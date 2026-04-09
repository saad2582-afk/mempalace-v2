from __future__ import annotations

import argparse
import json
from pathlib import Path

from mempalace_v2.consolidation.pipeline import MemoryPipeline
from mempalace_v2.ingestion.memory_files import ingest_workspace_memory
from mempalace_v2.ingestion.openclaw_sessions import load_session
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

    p_debug = sub.add_parser("debug-dump", help="Dump one internal store")
    p_debug.add_argument("store", choices=["raw_sessions", "episodic_memory", "semantic_memory", "task_memory", "invalidations"])
    p_debug.add_argument("--limit", type=int, default=0)
    p_debug.set_defaults(func=cmd_debug_dump)
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
