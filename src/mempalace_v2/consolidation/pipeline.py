from __future__ import annotations

from pathlib import Path
from typing import Any

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
        for memory in extracted["semantic"]:
            invalidation = self._invalidate_conflicts(memory, existing_semantic)
            if invalidation:
                invalidations.append(invalidation)
                self.invalidations.append(invalidation)
            self.semantic.append(memory)
            semantic_written += 1

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
        if new_memory.get("memory_type") != "preference":
            return None
        for old in reversed(existing):
            if old.get("memory_type") == new_memory.get("memory_type") and old.get("subject") == new_memory.get("subject") and old.get("status") == "active" and old.get("value") != new_memory.get("value"):
                old["status"] = "superseded"
                old["valid_to"] = new_memory["timestamp"]
                return {
                    "id": stable_id("invalidate", old["id"], new_memory["id"]),
                    "old_memory_id": old["id"],
                    "new_memory_id": new_memory["id"],
                    "reason": "new preference superseded active preference",
                    "timestamp": now_iso(),
                }
        return None

    def _update_entities(self, session: SessionRecord) -> None:
        data = self.entities.read()
        session_count = int(data.get("session_count", 0)) + 1
        data["session_count"] = session_count
        data.setdefault("sources", []).append({
            "session_id": session.session_id,
            "timestamp": session.timestamp,
        })
        self.entities.write(data)
