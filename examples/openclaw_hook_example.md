# OpenClaw Hook Flow Example

## Session-end ingestion

```bash
PYTHONPATH=src python3 -m mempalace_v2.cli --base-dir . openclaw-session-end examples/sample_session.json
```

## Pre-response context assembly

```bash
PYTHONPATH=src python3 -m mempalace_v2.cli --base-dir . openclaw-pre-response "What do you know about my project and tasks?"
```

## Hook-style automation

### Session-end hook payload from file

```bash
PYTHONPATH=src python3 -m mempalace_v2.cli --base-dir . hook-session-end --payload examples/session_end_hook_payload.json
```

### Pre-response hook payload from file

```bash
PYTHONPATH=src python3 -m mempalace_v2.cli --base-dir . hook-pre-response --payload examples/pre_response_hook_payload.json
```

### Pre-response hook payload from stdin

```bash
cat examples/pre_response_hook_payload.json | \
  PYTHONPATH=src python3 -m mempalace_v2.cli --base-dir . hook-pre-response
```

## Intended integration shape

- session end or checkpoint -> ingest session
- next user prompt -> assemble memory context
- inject context into reply planning
- use file or stdin JSON payloads to match hook runner expectations
