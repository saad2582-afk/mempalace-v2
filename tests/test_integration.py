import json

from mempalace_v2.integration.hook_runner import HookRunner
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


def test_hook_runner_with_inline_session_payload(tmp_path):
    runner = HookRunner(tmp_path)
    payload = {
        "session": {
            "session_id": "hook-sample-001",
            "timestamp": "2026-04-09T14:00:00Z",
            "source": "openclaw-hook",
            "messages": [
                {"role": "user", "text": "My project is MemPalace v2. Remind me to renew the domain."}
            ],
        }
    }
    result = runner.run_session_end(payload)
    assert result["mode"] == "session-end"
    assert result["result"]["episodic_written"] == 1
    assert "generated_session_path" in result


def test_hook_runner_pre_response_payload(tmp_path):
    sample = tmp_path / "session.json"
    sample.write_text(
        json.dumps({
            "session_id": "oc1",
            "timestamp": "2026-04-09T12:00:00Z",
            "source": "test",
            "messages": [{"role": "user", "text": "My project is MemPalace v2. Remind me to renew the domain."}],
        })
    )

    flow = OpenClawFlow(tmp_path)
    flow.ingest_session_end(sample)

    runner = HookRunner(tmp_path)
    result = runner.run_pre_response({"prompt": "What do you know about my project and tasks?", "limit": 5})
    assert result["mode"] == "pre-response"
    assert "project" in result["context"].lower()
