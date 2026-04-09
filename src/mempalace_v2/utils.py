from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone


TOPIC_STOPWORDS = {
    "the", "and", "that", "this", "with", "from", "have", "will", "about", "what", "your", "just", "they", "them", "then", "into", "want", "need"
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(*parts: str) -> str:
    joined = "::".join(parts)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()[:16]


def tokenize_topics(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
    seen: list[str] = []
    for word in words:
        if word in TOPIC_STOPWORDS:
            continue
        if word not in seen:
            seen.append(word)
        if len(seen) >= limit:
            break
    return seen


def first_sentence(text: str, max_len: int = 220) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
