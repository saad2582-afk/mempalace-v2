from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteMemoryStore:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                valid_from TEXT,
                valid_to TEXT,
                source_session TEXT,
                source_excerpt TEXT,
                confidence REAL,
                status TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS task_memory (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL,
                priority TEXT,
                timestamp TEXT NOT NULL,
                source_session TEXT,
                source_excerpt TEXT,
                metadata_json TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS profile_memory (
                id TEXT PRIMARY KEY,
                profile_type TEXT NOT NULL,
                subject TEXT NOT NULL,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source_session TEXT,
                source_excerpt TEXT,
                confidence REAL,
                metadata_json TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source_session TEXT,
                source_excerpt TEXT,
                confidence REAL,
                metadata_json TEXT DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_semantic_lookup ON semantic_memory(memory_type, subject, predicate, status);
            CREATE INDEX IF NOT EXISTS idx_task_status ON task_memory(status);
            CREATE INDEX IF NOT EXISTS idx_profile_subject ON profile_memory(subject, profile_type);
            CREATE INDEX IF NOT EXISTS idx_relationship_subject ON relationships(subject, predicate);
            """
        )
        conn.commit()
        conn.close()

    def replace_semantic_memory(self, rows: list[dict[str, Any]]) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM semantic_memory")
        conn.executemany(
            """
            INSERT INTO semantic_memory (
                id, memory_type, subject, predicate, value, timestamp, valid_from, valid_to,
                source_session, source_excerpt, confidence, status, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(
                row.get("id"), row.get("memory_type"), row.get("subject"), row.get("predicate"), row.get("value"),
                row.get("timestamp"), row.get("valid_from"), row.get("valid_to"), row.get("source_session"),
                row.get("source_excerpt"), row.get("confidence"), row.get("status"), json.dumps(row.get("metadata", {}), ensure_ascii=False)
            ) for row in rows],
        )
        conn.commit()
        conn.close()

    def replace_task_memory(self, rows: list[dict[str, Any]]) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM task_memory")
        conn.executemany(
            """
            INSERT INTO task_memory (
                id, title, details, status, priority, timestamp, source_session, source_excerpt, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(
                row.get("id"), row.get("title"), row.get("details"), row.get("status"), row.get("priority"),
                row.get("timestamp"), row.get("source_session"), row.get("source_excerpt"), json.dumps(row.get("metadata", {}), ensure_ascii=False)
            ) for row in rows],
        )
        conn.commit()
        conn.close()

    def upsert_profiles(self, rows: list[dict[str, Any]]) -> int:
        conn = self._connect()
        count = 0
        for row in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO profile_memory (
                    id, profile_type, subject, value, timestamp, source_session, source_excerpt, confidence, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("id"), row.get("profile_type"), row.get("subject"), row.get("value"), row.get("timestamp"),
                    row.get("source_session"), row.get("source_excerpt"), row.get("confidence"), json.dumps(row.get("metadata", {}), ensure_ascii=False)
                ),
            )
            count += 1
        conn.commit()
        conn.close()
        return count

    def upsert_relationships(self, rows: list[dict[str, Any]]) -> int:
        conn = self._connect()
        count = 0
        for row in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO relationships (
                    id, subject, predicate, object, timestamp, source_session, source_excerpt, confidence, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("id"), row.get("subject"), row.get("predicate"), row.get("object"), row.get("timestamp"),
                    row.get("source_session"), row.get("source_excerpt"), row.get("confidence"), json.dumps(row.get("metadata", {}), ensure_ascii=False)
                ),
            )
            count += 1
        conn.commit()
        conn.close()
        return count

    def counts(self) -> dict[str, int]:
        conn = self._connect()
        tables = ["semantic_memory", "task_memory", "profile_memory", "relationships"]
        result = {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}
        conn.close()
        return result
