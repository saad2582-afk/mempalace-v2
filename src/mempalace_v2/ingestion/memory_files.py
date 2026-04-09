from __future__ import annotations

from pathlib import Path

from mempalace_v2.utils import now_iso, stable_id


DEFAULT_FILES = ["MEMORY.md", "USER.md"]


def ingest_workspace_memory(workspace_dir: str | Path) -> list[dict]:
    root = Path(workspace_dir)
    records: list[dict] = []

    for name in DEFAULT_FILES:
        file_path = root / name
        if file_path.exists():
            records.append(_make_record(file_path, category="workspace-memory"))

    memory_dir = root / "memory"
    if memory_dir.exists() and memory_dir.is_dir():
        for file_path in sorted(memory_dir.glob("*.md")):
            records.append(_make_record(file_path, category="daily-memory"))

    return records


def _make_record(path: Path, category: str) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "id": stable_id(category, str(path)),
        "category": category,
        "path": str(path),
        "timestamp": now_iso(),
        "text": text,
    }
