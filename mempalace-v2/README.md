# MemPalace v2

MemPalace v2 is an early Python prototype for turning OpenClaw conversations and workspace memory files into structured memory artifacts.

Right now, the project focuses on a simple local pipeline:

- ingest session transcripts
- ingest workspace memory markdown files
- extract lightweight episodic, semantic, and task memory
- write structured JSON and JSONL outputs for later retrieval

## Status

This project is in an early scaffold stage.

What exists today:

- a CLI entrypoint
- session loaders for json, jsonl, markdown, and text inputs
- workspace memory file ingestion
- a consolidation pipeline
- prototype extraction for:
  - preferences
  - decisions
  - tasks
  - session summaries

What does not exist yet:

- missing foundational modules referenced by imports (`models`, `storage`, `utils`)
- packaging metadata
- tests
- fixtures
- retrieval/query commands
- OpenClaw integration wiring

See `ROADMAP.md` for the pause/resume plan.

## Project layout

```text
mempalace-v2/
├── README.md
├── ROADMAP.md
└── src/
    └── mempalace_v2/
        ├── cli.py
        ├── consolidation/
        │   ├── __init__.py
        │   ├── extractor.py
        │   └── pipeline.py
        └── ingestion/
            ├── memory_files.py
            └── openclaw_sessions.py
```

## Current CLI shape

The CLI currently exposes three commands:

- `ingest-session <path>`
- `ingest-memory-files <workspace>`
- `status`

Example intended usage once the missing base modules are added:

```bash
python -m mempalace_v2.cli --base-dir . status
python -m mempalace_v2.cli --base-dir . ingest-session sample-session.json
python -m mempalace_v2.cli --base-dir . ingest-memory-files /path/to/workspace
```

## Current behavior

### Session ingestion

`ingest-session` loads one conversation file and runs it through a memory pipeline.

Supported input formats:

- `.json`
- `.jsonl`
- `.md`
- `.txt`

The loader attempts to normalize the session into a common record structure with:

- session id
- timestamp
- source
- channel
- messages
- metadata

### Workspace memory ingestion

`ingest-memory-files` scans a workspace and writes raw memory file records.

Currently included:

- `MEMORY.md`
- `USER.md`
- `memory/*.md`

### Consolidation outputs

The pipeline is designed to write these stores in a local data directory:

- `raw_sessions.jsonl`
- `episodic_memory.jsonl`
- `semantic_memory.jsonl`
- `task_memory.jsonl`
- `invalidation_log.jsonl`
- `entities.json`

## Extraction rules, current prototype

The extractor is intentionally simple right now.

It looks for user messages that imply:

- preferences, such as "I prefer ..." or "I like ..."
- decisions, such as "we decided to ..." or "we will ..."
- tasks, such as "remind me to ..." or "todo: ..."

It also generates:

- a one-line session summary
- lightweight topics
- evidence snippets

This is a prototype extraction layer, not a finalized memory system.

## Known limitations

- The codebase is incomplete and will not run end-to-end yet
- Regex extraction is high-risk for false positives
- There is no test coverage yet
- Data schemas are implied by code, not formally documented
- Query and retrieval are not implemented

## Recommended next steps

1. Add the missing core modules
2. Add `pyproject.toml`
3. Add sample fixtures and tests
4. Make the CLI runnable end-to-end
5. Improve extraction quality
6. Add retrieval commands
7. Integrate with OpenClaw workflows

## Resume notes

If you are picking this project back up later:

- start with `ROADMAP.md`
- make the imports resolvable first
- keep the storage layer simple in the first pass
- avoid overbuilding retrieval before the ingestion pipeline is trustworthy

## License

No license has been added yet.
