from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from mempalace_v2.storage import ensure_data_dir
from mempalace_v2.utils import tokenize_topics


class MemoryRetriever:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.db_path = ensure_data_dir(self.base_dir) / "memory.db"

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def retrieve(self, prompt: str, limit: int = 5) -> dict[str, list[dict[str, Any]]]:
        tokens = tokenize_topics(prompt, limit=12)
        semantic = self._query_semantic(tokens, limit)
        tasks = self._query_tasks(tokens, limit)
        profiles = self._query_profiles(tokens, limit)
        relationships = self._query_relationships(tokens, limit)
        return {
            "tokens": [{"token": t} for t in tokens],
            "semantic": semantic,
            "tasks": tasks,
            "profiles": profiles,
            "relationships": relationships,
        }

    def _query_semantic(self, tokens: list[str], limit: int) -> list[dict[str, Any]]:
        if not tokens:
            return []
        clauses = " OR ".join(["LOWER(value) LIKE ? OR LOWER(source_excerpt) LIKE ?" for _ in tokens])
        params = []
        for token in tokens:
            like = f"%{token.lower()}%"
            params.extend([like, like])
        params.append(limit)
        sql = f"SELECT * FROM semantic_memory WHERE status = 'active' AND ({clauses}) ORDER BY timestamp DESC LIMIT ?"
        return self._run(sql, params)

    def _query_tasks(self, tokens: list[str], limit: int) -> list[dict[str, Any]]:
        if not tokens:
            return self._run("SELECT * FROM task_memory WHERE status IN ('open','in_progress','blocked') ORDER BY timestamp DESC LIMIT ?", [limit])
        clauses = " OR ".join(["LOWER(title) LIKE ? OR LOWER(details) LIKE ?" for _ in tokens])
        params = []
        for token in tokens:
            like = f"%{token.lower()}%"
            params.extend([like, like])
        params.append(limit)
        sql = f"SELECT * FROM task_memory WHERE status IN ('open','in_progress','blocked') AND ({clauses}) ORDER BY timestamp DESC LIMIT ?"
        return self._run(sql, params)

    def _query_profiles(self, tokens: list[str], limit: int) -> list[dict[str, Any]]:
        if not tokens:
            return self._run("SELECT * FROM profile_memory ORDER BY timestamp DESC LIMIT ?", [limit])
        clauses = " OR ".join(["LOWER(value) LIKE ? OR LOWER(profile_type) LIKE ?" for _ in tokens])
        params = []
        for token in tokens:
            like = f"%{token.lower()}%"
            params.extend([like, like])
        params.append(limit)
        sql = f"SELECT * FROM profile_memory WHERE ({clauses}) ORDER BY timestamp DESC LIMIT ?"
        return self._run(sql, params)

    def _query_relationships(self, tokens: list[str], limit: int) -> list[dict[str, Any]]:
        if not tokens:
            return self._run("SELECT * FROM relationships ORDER BY timestamp DESC LIMIT ?", [limit])
        clauses = " OR ".join(["LOWER(object) LIKE ? OR LOWER(predicate) LIKE ? OR LOWER(source_excerpt) LIKE ?" for _ in tokens])
        params = []
        for token in tokens:
            like = f"%{token.lower()}%"
            params.extend([like, like, like])
        params.append(limit)
        sql = f"SELECT * FROM relationships WHERE ({clauses}) ORDER BY timestamp DESC LIMIT ?"
        return self._run(sql, params)

    def _run(self, sql: str, params: list[Any]) -> list[dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]
