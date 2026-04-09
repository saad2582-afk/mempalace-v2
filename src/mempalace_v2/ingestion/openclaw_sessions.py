from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mempalace_v2.models import Message, SessionRecord
from mempalace_v2.utils import now_iso, stable_id


SUPPORTED_EXTENSIONS = {".json", ".jsonl", ".md", ".txt"}


def load_session(path: str | Path) -> SessionRecord:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported session file type: {ext}")

    if ext == ".json":
        return _load_json_session(file_path)
    if ext == ".jsonl":
        return _load_jsonl_session(file_path)
    return _load_text_session(file_path)


def _load_json_session(path: Path) -> SessionRecord:
    data = json.loads(path.read_text(encoding="utf-8"))
    session_id = data.get("session_id") or data.get("id") or stable_id(str(path))
    timestamp = data.get("timestamp") or now_iso()
    source = data.get("source") or "openclaw-session-json"
    channel = data.get("channel")
    messages = [_coerce_message(m) for m in data.get("messages", [])]
    metadata = data.get("metadata", {})
    return SessionRecord(
        session_id=session_id,
        timestamp=timestamp,
        source=source,
        channel=channel,
        messages=messages,
        metadata=metadata,
    )


def _load_jsonl_session(path: Path) -> SessionRecord:
    messages: list[Message] = []
    metadata: dict[str, Any] = {}
    timestamp = now_iso()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if item.get("type") == "metadata":
            metadata.update(item)
            timestamp = item.get("timestamp", timestamp)
            continue
        if "role" in item and "text" in item:
            messages.append(_coerce_message(item))
    return SessionRecord(
        session_id=metadata.get("session_id") or stable_id(str(path)),
        timestamp=timestamp,
        source=metadata.get("source") or "openclaw-session-jsonl",
        channel=metadata.get("channel"),
        messages=messages,
        metadata=metadata,
    )


def _load_text_session(path: Path) -> SessionRecord:
    messages: list[Message] = []
    current_role = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer, current_role
        if current_role and buffer:
            messages.append(Message(role=current_role, text="\n".join(buffer).strip()))
        buffer = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        lowered = line.lower()
        if lowered.startswith("user:"):
            flush()
            current_role = "user"
            buffer.append(line.split(":", 1)[1].strip())
        elif lowered.startswith("assistant:"):
            flush()
            current_role = "assistant"
            buffer.append(line.split(":", 1)[1].strip())
        elif lowered.startswith("system:"):
            flush()
            current_role = "system"
            buffer.append(line.split(":", 1)[1].strip())
        else:
            buffer.append(line)
    flush()

    return SessionRecord(
        session_id=stable_id(str(path)),
        timestamp=now_iso(),
        source="openclaw-session-text",
        channel=None,
        messages=messages,
        metadata={"path": str(path)},
    )


def _coerce_message(item: dict[str, Any]) -> Message:
    return Message(
        role=item.get("role", "unknown"),
        text=item.get("text", "").strip(),
        timestamp=item.get("timestamp"),
    )
