from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mempalace_v2.consolidation.pipeline import MemoryPipeline
from mempalace_v2.ingestion.openclaw_sessions import load_session
from mempalace_v2.retrieval.assembler import MemoryAssembler


class OpenClawFlow:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.pipeline = MemoryPipeline(self.base_dir)
        self.assembler = MemoryAssembler(str(self.base_dir))

    def ingest_session_end(self, session_path: str | Path) -> dict[str, Any]:
        session = load_session(session_path)
        result = self.pipeline.process_session(session)
        return {
            "mode": "session-end",
            "session_path": str(session_path),
            "result": result,
        }

    def prepare_pre_response_context(self, prompt: str, limit: int = 5) -> dict[str, Any]:
        assembled = self.assembler.assemble(prompt, limit=limit)
        return {
            "mode": "pre-response",
            "prompt": prompt,
            "context": assembled["context"],
            "retrieved": assembled["retrieved"],
        }

    def export_hook_payload(self, prompt: str, limit: int = 5) -> str:
        payload = self.prepare_pre_response_context(prompt, limit=limit)
        return json.dumps(payload, indent=2)
