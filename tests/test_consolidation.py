import json

from mempalace_v2.consolidation.pipeline import MemoryPipeline
from mempalace_v2.ingestion.openclaw_sessions import load_session


def test_pipeline_writes_memory(tmp_path):
    sample = tmp_path / "session.json"
    sample.write_text(
        '{"session_id":"s1","timestamp":"2026-04-09T12:00:00Z","source":"test","messages":[{"role":"user","text":"I prefer PostgreSQL. Remind me to renew domain."},{"role":"assistant","text":"Noted."}]}'
    )

    pipeline = MemoryPipeline(tmp_path)
    result = pipeline.process_session(load_session(sample))

    assert result["raw_written"] == 1
    assert result["episodic_written"] == 1
    assert result["semantic_written"] >= 1
    assert result["task_written"] == 1
    assert (tmp_path / "data" / "semantic_memory.jsonl").exists()


def test_preference_supersession(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        '{"session_id":"s1","timestamp":"2026-04-09T12:00:00Z","source":"test","messages":[{"role":"user","text":"I prefer PostgreSQL."}]}'
    )
    second.write_text(
        '{"session_id":"s2","timestamp":"2026-04-10T12:00:00Z","source":"test","messages":[{"role":"user","text":"I switched to SQLite now."}]}'
    )

    pipeline = MemoryPipeline(tmp_path)
    pipeline.process_session(load_session(first))
    result = pipeline.process_session(load_session(second))

    semantic_lines = (tmp_path / "data" / "semantic_memory.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in semantic_lines]
    assert len(rows) == 2
    assert result["invalidations"] == 1
    assert any(row["status"] == "superseded" for row in rows)
    assert any(row["status"] == "active" and row["value"] == "SQLite" for row in rows)


def test_task_merge_updates_existing_open_task(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        '{"session_id":"s1","timestamp":"2026-04-09T12:00:00Z","source":"test","messages":[{"role":"user","text":"Remind me to renew the domain."}]}'
    )
    second.write_text(
        '{"session_id":"s2","timestamp":"2026-04-10T12:00:00Z","source":"test","messages":[{"role":"user","text":"Remind me to renew the domain."}]}'
    )

    pipeline = MemoryPipeline(tmp_path)
    pipeline.process_session(load_session(first))
    result = pipeline.process_session(load_session(second))

    task_lines = (tmp_path / "data" / "task_memory.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in task_lines]
    assert len(rows) == 1
    assert result["task_updated"] == 1
