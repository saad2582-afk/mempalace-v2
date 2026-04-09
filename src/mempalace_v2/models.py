from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Message:
    role: str
    text: str
    timestamp: str | None = None


@dataclass
class SessionRecord:
    session_id: str
    timestamp: str
    source: str
    channel: str | None = None
    messages: list[Message] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["messages"] = [asdict(m) for m in self.messages]
        return data
