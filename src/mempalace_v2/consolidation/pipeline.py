from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from mempalace_v2.consolidation.extractor import extract_session_memory
from mempalace_v2.models import SessionRecord
from mempalace_v2.storage import JsonStore, JsonlStore, ensure_data_dir
from mempalace_v2.utils import now_iso, stable_id


class MemoryPipeline:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.data_dir = ensure_data_dir(self.base_dir)
        self.raw_sessions = JsonlStore(self.data_dir / "raw_sessions.jsonl")
        self.episodic = JsonlStore(self.data_dir / "episodic_memory.jsonl")
        self.semantic = JsonlStore(self.data_dir / "semantic_memory.jsonl")
        self.tasks = JsonlStore(self.data_dir / "task_memory.jsonl")
        self.invalidations = JsonlStore(self.data_dir / "invalidation_log.jsonl")
        self.entities = JsonStore(self.data_dir / "entities.json")

    def process_session(self, session: SessionRecord) -> dict[str, Any]:
        self.raw_sessions.append(session.to_dict())
        extracted = extract_session_memory(session)
        self.episodic.append(extracted["episodic"])

        semantic_written = 0
        invalidations = []
        existing_semantic = self.semantic.read_all()
        updated_semantic = list(existing_semantic)
        for memory in extracted["semantic"]:
            invalidation = self._invalidate_conflicts(memory, updated_semantic)
            if invalidation:
                invalidations.append(invalidation)
                self.invalidations.append(invalidation)
            if not self._is_duplicate(memory, updated_semantic):
                updated_semantic.append(memory)
                semantic_written += 1

        self._rewrite_jsonl(self.semantic.path, updated_semantic)

        task_written = 0
        for task in extracted["tasks"]:
            self.tasks.append(task)
            task_written += 1

        self._update_entities(session)

        return {
            "session_id": session.session_id,
            "raw_written": 1,
            "episodic_written": 1,
            "semantic_written": semantic_written,
            "task_written": task_written,
            "invalidations": len(invalidations),
        }

    def _invalidate_conflicts(self, new_memory: dict[str, Any], existing: list[dict[str, Any]]) -> dict[str, Any] | None:
        memory_type = new_memory.get("memory_type")
        subject = new_memory.get("subject")
        predicate = new_memory.get("predicate")
        value = new_memory.get("value")
        if not memory_type or not subject or not predicate:
            return None

        for old in reversed(existing):
            if old.get("memory_type") != memory_type:
                continue
            if old.get("subject") != subject or old.get("predicate") != predicate:
                continue
            if old.get("status") != "active":
                continue
            if old.get("value") == value:
                return None

            old["status"] = "superseded"
            old["valid_to"] = new_memory["timestamp"]
            return {
                "id": stable_id("invalidate", old["id"], new_memory["id"]),
                "old_memory_id": old["id"],
                "new_memory_id": new_memory["id"],
                "reason": f"new {memory_type} superseded active memory",
                "timestamp": now_iso(),
            }
        return None

    def _is_duplicate(self, new_memory: dict[str, Any], existing: list[dict[str, Any]]) -> bool:
        for old in existing:
            if old.get("memory_type") == new_memory.get("memory_type") and old.get("subject") == new_memory.get("subject") and old.get("predicate") == new_memory.get("predicate") and old.get("value") == new_memory.get("value") and old.get("status") == "active":
                return True
        return False

    def _rewrite_jsonl(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _update_entities(self, session: SessionRecord) -> None:
        data = self.entities.read()
        session_count = int(data.get("session_count", 0)) + 1
        data["session_count"] = session_count
        data.setdefault("sources", []).append({
            "session_id": session.session_id,
            "timestamp": session.timestamp,
        })
        self.entities.write(data)
