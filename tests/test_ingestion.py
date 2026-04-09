from pathlib import Path

from mempalace_v2.ingestion.openclaw_sessions import load_session
from mempalace_v2.ingestion.memory_files import ingest_workspace_memory


def test_load_json_session():
    path = Path(__file__).resolve().parents[1] / "examples" / "sample_session.json"
    session = load_session(path)
    assert session.session_id == "sample-openclaw-session-001"
    assert len(session.messages) == 2
    assert session.messages[0].role == "user"


def test_ingest_workspace_memory(tmp_path):
    (tmp_path / "USER.md").write_text("# USER\nName: Saad\n", encoding="utf-8")
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    (memory_dir / "2026-04-09.md").write_text("Remember this note", encoding="utf-8")

    records = ingest_workspace_memory(tmp_path)
    assert len(records) == 2
    assert {r["category"] for r in records} == {"workspace-memory", "daily-memory"}
