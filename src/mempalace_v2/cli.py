from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3

from mempalace_v2.consolidation.pipeline import MemoryPipeline
from mempalace_v2.ingestion.memory_files import ingest_workspace_memory
from mempalace_v2.ingestion.openclaw_sessions import load_session
from mempalace_v2.integration.hook_runner import HookRunner, load_payload
from mempalace_v2.integration.openclaw_flow import OpenClawFlow
from mempalace_v2.retrieval.assembler import MemoryAssembler
from mempalace_v2.retrieval.query import MemoryRetriever
from mempalace_v2.storage import ensure_data_dir


def cmd_ingest_session(args: argparse.Namespace) -> None:
    base_dir = Path(args.base_dir).resolve()
    pipeline = MemoryPipeline(base_dir)
    session = load_session(args.path)
    result = pipeline.process_session(session)
    print(json.dumps(result, indent=2))


def cmd_ingest_memory_files(args: argparse.Namespace) -> None:
    base_dir = Path(args.base_dir).resolve()
    data_dir = ensure_data_dir(base_dir)
    records = ingest_workspace_memory(args.workspace)
    out = data_dir / "workspace_memory.jsonl"
    with out.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"written": len(records), "output": str(out)}, indent=2))


def cmd_status(args: argparse.Namespace) -> None:
    pipeline = MemoryPipeline(Path(args.base_dir).resolve())
    files = sorted(p.name for p in pipeline.data_dir.glob("*.json*") if p.is_file())
    print(json.dumps({
        "data_dir": str(pipeline.data_dir),
        "files": files,
        "summary": pipeline.status_summary(),
    }, indent=2))


def cmd_debug_dump(args: argparse.Namespace) -> None:
    pipeline = MemoryPipeline(Path(args.base_dir).resolve())
    rows = pipeline.debug_dump(args.store)
    if args.limit:
        rows = rows[: args.limit]
    print(json.dumps(rows, indent=2))


def cmd_sqlite_dump(args: argparse.Namespace) -> None:
    base_dir = Path(args.base_dir).resolve()
    db_path = ensure_data_dir(base_dir) / "memory.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM {args.table} LIMIT ?", (args.limit,)).fetchall()
    conn.close()
    print(json.dumps([dict(row) for row in rows], indent=2))


def cmd_retrieve(args: argparse.Namespace) -> None:
    retriever = MemoryRetriever(Path(args.base_dir).resolve())
    result = retriever.retrieve(args.prompt, limit=args.limit)
    print(json.dumps(result, indent=2))


def cmd_assemble_context(args: argparse.Namespace) -> None:
    assembler = MemoryAssembler(str(Path(args.base_dir).resolve()))
    result = assembler.assemble(args.prompt, limit=args.limit)
    print(json.dumps(result, indent=2))


def cmd_openclaw_session_end(args: argparse.Namespace) -> None:
    flow = OpenClawFlow(Path(args.base_dir).resolve())
    result = flow.ingest_session_end(args.path)
    print(json.dumps(result, indent=2))


def cmd_openclaw_pre_response(args: argparse.Namespace) -> None:
    flow = OpenClawFlow(Path(args.base_dir).resolve())
    result = flow.prepare_pre_response_context(args.prompt, limit=args.limit)
    print(json.dumps(result, indent=2))


def cmd_hook_session_end(args: argparse.Namespace) -> None:
    runner = HookRunner(Path(args.base_dir).resolve())
    payload = load_payload(args.payload)
    result = runner.run_session_end(payload)
    print(json.dumps(result, indent=2))


def cmd_hook_pre_response(args: argparse.Namespace) -> None:
    runner = HookRunner(Path(args.base_dir).resolve())
    payload = load_payload(args.payload)
    result = runner.run_pre_response(payload)
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MemPalace v2 for OpenClaw")
    parser.add_argument("--base-dir", default=".", help="Project base directory")
    sub = parser.add_subparsers(dest="command")

    p_ingest = sub.add_parser("ingest-session", help="Ingest and consolidate one session file")
    p_ingest.add_argument("path", help="Path to session file")
    p_ingest.set_defaults(func=cmd_ingest_session)

    p_memory = sub.add_parser("ingest-memory-files", help="Ingest workspace memory markdown files")
    p_memory.add_argument("workspace", help="Workspace directory")
    p_memory.set_defaults(func=cmd_ingest_memory_files)

    p_status = sub.add_parser("status", help="Show current data files and summary")
    p_status.set_defaults(func=cmd_status)

    p_debug = sub.add_parser("debug-dump", help="Dump one internal JSONL store")
    p_debug.add_argument("store", choices=["raw_sessions", "episodic_memory", "semantic_memory", "task_memory", "invalidations"])
    p_debug.add_argument("--limit", type=int, default=0)
    p_debug.set_defaults(func=cmd_debug_dump)

    p_sqlite = sub.add_parser("sqlite-dump", help="Dump one SQLite table")
    p_sqlite.add_argument("table", choices=["semantic_memory", "task_memory", "profile_memory", "relationships"])
    p_sqlite.add_argument("--limit", type=int, default=20)
    p_sqlite.set_defaults(func=cmd_sqlite_dump)

    p_retrieve = sub.add_parser("retrieve", help="Retrieve memory relevant to a prompt")
    p_retrieve.add_argument("prompt", help="Prompt to retrieve against")
    p_retrieve.add_argument("--limit", type=int, default=5)
    p_retrieve.set_defaults(func=cmd_retrieve)

    p_assemble = sub.add_parser("assemble-context", help="Assemble prompt-ready memory context")
    p_assemble.add_argument("prompt", help="Prompt to assemble context for")
    p_assemble.add_argument("--limit", type=int, default=5)
    p_assemble.set_defaults(func=cmd_assemble_context)

    p_oc_end = sub.add_parser("openclaw-session-end", help="OpenClaw-style session-end ingestion")
    p_oc_end.add_argument("path", help="Path to session file")
    p_oc_end.set_defaults(func=cmd_openclaw_session_end)

    p_oc_pre = sub.add_parser("openclaw-pre-response", help="OpenClaw-style pre-response context assembly")
    p_oc_pre.add_argument("prompt", help="Prompt to prepare context for")
    p_oc_pre.add_argument("--limit", type=int, default=5)
    p_oc_pre.set_defaults(func=cmd_openclaw_pre_response)

    p_hook_end = sub.add_parser("hook-session-end", help="Run session-end hook payload from file or stdin")
    p_hook_end.add_argument("--payload", default=None, help="Path to JSON payload file. If omitted, read stdin")
    p_hook_end.set_defaults(func=cmd_hook_session_end)

    p_hook_pre = sub.add_parser("hook-pre-response", help="Run pre-response hook payload from file or stdin")
    p_hook_pre.add_argument("--payload", default=None, help="Path to JSON payload file. If omitted, read stdin")
    p_hook_pre.set_defaults(func=cmd_hook_pre_response)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
