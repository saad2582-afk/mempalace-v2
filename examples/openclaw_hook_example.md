# OpenClaw Hook Flow Example

## Session-end ingestion

```bash
PYTHONPATH=src python3 -m mempalace_v2.cli --base-dir . openclaw-session-end examples/sample_session.json
```

This ingests one OpenClaw-style session file at the end of a session.

## Pre-response context assembly

```bash
PYTHONPATH=src python3 -m mempalace_v2.cli --base-dir . openclaw-pre-response "What do you know about my project and tasks?"
```

This returns a structured payload with:
- retrieved memory
- a compact memory context block ready to inject before a reply

## Intended integration shape

- session end or checkpoint -> ingest session
- next user prompt -> assemble memory context
- inject context into reply planning
