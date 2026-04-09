from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from mempalace_v2.integration.openclaw_flow import OpenClawFlow
from mempalace_v2.utils import now_iso, stable_id


class HookRunner:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.flow = OpenClawFlow(self.base_dir)

    def run_session_end(self, payload: dict[str, Any]) -> dict[str, Any]:
        session_path = payload.get("session_path")
        if session_path:
            return self.flow.ingest_session_end(session_path)

        session_data = payload.get("session")
        if session_data:
            temp_path = self.base_dir / "data" / f"hook-session-{stable_id(now_iso())}.json"
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_text(json.dumps(session_data, ensure_ascii=False, indent=2), encoding="utf-8")
            result = self.flow.ingest_session_end(temp_path)
            result["generated_session_path"] = str(temp_path)
            return result

        raise ValueError("session-end hook requires session_path or session payload")

    def run_pre_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = payload.get("prompt") or payload.get("user_prompt")
        if not prompt:
            raise ValueError("pre-response hook requires prompt")
        limit = int(payload.get("limit", 5))
        return self.flow.prepare_pre_response_context(prompt, limit=limit)


def load_payload(path: str | None = None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("No hook payload provided")
    return json.loads(raw)
