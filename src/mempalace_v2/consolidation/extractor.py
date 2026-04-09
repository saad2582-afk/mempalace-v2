from __future__ import annotations

import re
from typing import Any

from mempalace_v2.models import SessionRecord
from mempalace_v2.utils import first_sentence, stable_id, tokenize_topics

PREFERENCE_PATTERNS = [
    re.compile(r"\bI prefer (?P<value>[^.\n]+)", re.IGNORECASE),
    re.compile(r"\bI like (?P<value>[^.\n]+)", re.IGNORECASE),
    re.compile(r"\bI use (?P<value>[^.\n]+)", re.IGNORECASE),
    re.compile(r"\bI switched to (?P<value>[^.\n]+)", re.IGNORECASE),
]

DECISION_PATTERNS = [
    re.compile(r"\bwe decided to (?P<value>[^.\n]+)", re.IGNORECASE),
    re.compile(r"\bwe will (?P<value>[^.\n]+)", re.IGNORECASE),
]

TASK_PATTERNS = [
    re.compile(r"\b(remind me to|todo:|to do:|follow up on) (?P<value>[^.\n]+)", re.IGNORECASE),
]


def extract_session_memory(session: SessionRecord) -> dict[str, Any]:
    transcript = "\n".join(f"{m.role}: {m.text}" for m in session.messages if m.text)
    summary = _build_summary(session)
    topics = tokenize_topics(transcript)
    evidence = [first_sentence(m.text, 160) for m in session.messages[:5] if m.text]

    semantic = []
    tasks = []
    events = []

    for message in session.messages:
        if message.role != "user":
            continue
        semantic.extend(_extract_preferences(message.text, session))
        semantic.extend(_extract_decisions(message.text, session))
        tasks.extend(_extract_tasks(message.text, session))

    if summary:
        events.append(summary)

    return {
        "episodic": {
            "id": stable_id("episodic", session.session_id, session.timestamp),
            "session_id": session.session_id,
            "timestamp": session.timestamp,
            "summary": summary,
            "topics": topics,
            "events": events,
            "evidence": evidence,
            "confidence": 0.6,
        },
        "semantic": semantic,
        "tasks": tasks,
    }


def _build_summary(session: SessionRecord) -> str:
    user_messages = [m.text for m in session.messages if m.role == "user" and m.text]
    assistant_messages = [m.text for m in session.messages if m.role == "assistant" and m.text]
    user_part = first_sentence(user_messages[0], 140) if user_messages else "No user prompt captured"
    assistant_part = first_sentence(assistant_messages[0], 140) if assistant_messages else "No assistant reply captured"
    return f"User discussed: {user_part} Assistant responded: {assistant_part}"


def _extract_preferences(text: str, session: SessionRecord) -> list[dict[str, Any]]:
    results = []
    for pattern in PREFERENCE_PATTERNS:
        for match in pattern.finditer(text):
            value = _clean_value(match.group("value"))
            results.append({
                "id": stable_id("semantic", session.session_id, "preference", value),
                "memory_type": "preference",
                "subject": "user",
                "predicate": "prefers",
                "value": value,
                "timestamp": session.timestamp,
                "valid_from": session.timestamp,
                "valid_to": None,
                "source_session": session.session_id,
                "source_excerpt": first_sentence(text, 180),
                "confidence": 0.7,
                "status": "active",
            })
    return results


def _extract_decisions(text: str, session: SessionRecord) -> list[dict[str, Any]]:
    results = []
    for pattern in DECISION_PATTERNS:
        for match in pattern.finditer(text):
            value = _clean_value(match.group("value"))
            results.append({
                "id": stable_id("semantic", session.session_id, "decision", value),
                "memory_type": "decision",
                "subject": "project",
                "predicate": "decided",
                "value": value,
                "timestamp": session.timestamp,
                "valid_from": session.timestamp,
                "valid_to": None,
                "source_session": session.session_id,
                "source_excerpt": first_sentence(text, 180),
                "confidence": 0.75,
                "status": "active",
            })
    return results


def _extract_tasks(text: str, session: SessionRecord) -> list[dict[str, Any]]:
    results = []
    for pattern in TASK_PATTERNS:
        for match in pattern.finditer(text):
            value = _clean_value(match.group("value"))
            results.append({
                "id": stable_id("task", session.session_id, value),
                "title": value,
                "details": first_sentence(text, 200),
                "status": "open",
                "priority": "normal",
                "timestamp": session.timestamp,
                "source_session": session.session_id,
                "source_excerpt": first_sentence(text, 180),
            })
    return results


def _clean_value(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" .,!?:;\t")
    for suffix in [" now", " please", " thanks"]:
        if value.lower().endswith(suffix):
            value = value[: -len(suffix)].rstrip()
    return value
