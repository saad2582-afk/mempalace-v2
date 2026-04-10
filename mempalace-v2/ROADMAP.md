# MemPalace v2 Pause and Resume Roadmap

_Last updated: 2026-04-10 UTC_

## Current state

There is an early project skeleton with a working CLI entrypoint and core ingestion/consolidation modules.

### Implemented so far

- CLI commands:
  - `ingest-session`
  - `ingest-memory-files`
  - `status`
- Session ingestion supports:
  - `.json`
  - `.jsonl`
  - `.md`
  - `.txt`
- Workspace memory ingestion supports:
  - `MEMORY.md`
  - `USER.md`
  - `memory/*.md`
- Consolidation pipeline writes to structured stores for:
  - raw sessions
  - episodic memory
  - semantic memory
  - task memory
  - invalidation log
  - entities index
- Basic extraction logic exists for:
  - preferences
  - project decisions
  - simple task capture
  - session summary generation

## What is missing

The project is not yet complete enough for production use. Several referenced modules and product layers still need to be built or verified.

### Immediate gaps

- Missing package pieces referenced by imports, including likely:
  - `mempalace_v2.models`
  - `mempalace_v2.storage`
  - `mempalace_v2.utils`
- No packaging metadata yet (`pyproject.toml` or equivalent not present)
- No tests
- No README or usage docs
- No sample data or fixtures
- No persistence schema documentation
- No retrieval/query layer yet
- No integration path back into OpenClaw runtime yet

## Recommended next milestones

### Milestone 1, make the code runnable end-to-end

Goal: get the current CLI working without missing imports.

Tasks:

- Add the missing foundational modules:
  - `models.py`
  - `storage.py`
  - `utils.py`
- Add package init files where needed
- Add packaging config (`pyproject.toml`)
- Verify `python -m mempalace_v2.cli status` works
- Verify ingest commands run on sample files

Definition of done:

- Fresh checkout can install and run the CLI successfully
- Sample ingestion produces output files in a data directory

### Milestone 2, stabilize data model and storage

Goal: lock down what gets written and how it evolves.

Tasks:

- Define schemas for:
  - session records
  - episodic memories
  - semantic memories
  - tasks
  - entity index
  - invalidation records
- Document file layout and retention assumptions
- Decide on append-only versus compaction strategy
- Add basic validation on write/read paths

Definition of done:

- Data files are documented and consistent
- Broken input fails clearly instead of corrupting output

### Milestone 3, improve extraction quality

Goal: move beyond simple regex capture.

Tasks:

- Refine preference detection to reduce false positives
- Tighten decision extraction so routine future-tense text is not over-captured
- Improve task extraction with due dates, priorities, and completion handling
- Add tests for representative transcripts
- Add confidence thresholds and maybe source categories

Definition of done:

- Extraction quality is measurably better on a small benchmark set
- Tests cover common and tricky examples

### Milestone 4, add retrieval and recall

Goal: make stored memory usable, not just collected.

Tasks:

- Add query commands for semantic, episodic, and task memory
- Support filtering by subject, topic, recency, and status
- Add a simple relevance ranking strategy
- Decide whether embeddings are needed now or later

Definition of done:

- A user can ask for recent decisions, active tasks, or known preferences and get useful results

### Milestone 5, integrate with OpenClaw workflows

Goal: connect this project to real assistant memory operations.

Tasks:

- Define where session exports come from
- Define when ingestion should happen
- Define how recall is surfaced to the assistant
- Add one practical integration path, for example a cron job or a direct command workflow

Definition of done:

- At least one real OpenClaw memory flow works end-to-end

## Suggested resume order

If we come back later, the best order is:

1. Finish missing core modules
2. Add packaging and runnable setup
3. Add tests and sample fixtures
4. Write a README with quickstart steps
5. Improve extraction quality
6. Add retrieval
7. Integrate with OpenClaw

## First tasks to do when resuming

- Inspect imports and create the missing modules
- Add a minimal `pyproject.toml`
- Add a tiny sample session fixture
- Run the CLI against the fixture
- Save example outputs for regression testing

## Notes for future us

- Keep the storage format simple first. JSON/JSONL is good enough for the early phase.
- Do not overbuild embeddings or vector search before the core pipeline is trustworthy.
- The current extractor is a prototype, not a final memory model.
- The highest leverage next step is making the existing code runnable and testable.
