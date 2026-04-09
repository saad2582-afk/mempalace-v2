from mempalace_v2.integration.openclaw_flow import OpenClawFlow


def test_openclaw_flow_ingest_and_prepare_context(tmp_path):
    sample = tmp_path / "session.json"
    sample.write_text(
        '{"session_id":"oc1","timestamp":"2026-04-09T12:00:00Z","source":"test","messages":[{"role":"user","text":"My project is MemPalace v2. Remind me to renew the domain."}]}'
    )

    flow = OpenClawFlow(tmp_path)
    ingest = flow.ingest_session_end(sample)
    assert ingest["result"]["episodic_written"] == 1

    prepared = flow.prepare_pre_response_context("What do you know about my project and tasks?", limit=5)
    assert prepared["mode"] == "pre-response"
    assert "project" in prepared["context"].lower()
    assert "task" in prepared["context"].lower() or "renew the domain" in prepared["context"].lower()
