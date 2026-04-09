# Architecture — MemPalace v2 for OpenClaw

## Purpose

MemPalace v2 is a persistent memory subsystem for OpenClaw.
It is designed to give agents strong cross-session continuity instead of simple transcript search.

## Problem statement

Most agent memory systems fail in one of two ways:
- they only store raw history and depend on search alone
- they over-compress memory into shallow facts and lose reasoning context

MemPalace v2 uses both raw evidence and curated structured memory.

## Goals

- preserve exact session evidence
- extract durable memories after sessions
- track changes in truth over time
- support open-loop and task continuity
- support retrieval across all sessions
- remain auditable and local-first
- integrate naturally with OpenClaw sessions and workspace memory files

## Non-goals

- replace OpenClaw itself
- depend on cloud-only infrastructure
- fully automate every memory write without provenance

## Memory layers

### 1. Raw Memory
Stores exact transcripts, excerpts, and source artifacts.
This is the evidence layer.

Examples:
- session transcript chunks
- memory file snapshots
- quoted evidence snippets

### 2. Episodic Memory
Stores what happened in a session.
This is the event/history layer.

Examples:
- session summary
- changes made
- decisions taken
- notable events
- topics discussed

### 3. Semantic Memory
Stores relatively stable truths and recurring knowledge.
This is the durable facts layer.

Examples:
- user preferences
- project facts
- stable environment details
- recurring patterns
- durable decisions

### 4. Task / Open-Loop Memory
Stores active obligations and unresolved threads.
This is the continuity layer.

Examples:
- todos
- reminders
- blocked issues
- pending follow-ups
- unresolved user requests

### 5. Versioning / Invalidation Layer
Tracks when memory changed and why.
This is the temporal truth layer.

Examples:
- previous city invalidated by move event
- old project decision superseded by new decision
- stale preference downgraded after contradiction

## Core pipeline

### Step 1 — Capture
At the end of a session or checkpoint:
- ingest transcript
- chunk raw evidence
- store session metadata
- identify participants, topics, and project scope

### Step 2 — Consolidate
Run a consolidation pass to extract candidate memories:
- facts
- preferences
- decisions
- tasks
- unresolved threads
- session events

### Step 3 — Compare
Compare candidate memories against existing memory:
- duplicate
- stronger restatement
- contradiction
- superseding update
- uncertain inference

### Step 4 — Apply
Apply writes to structured stores:
- add raw evidence
- add episodic records
- add semantic records
- add/update tasks
- invalidate stale facts when appropriate

### Step 5 — Link provenance
Every durable memory must point to:
- source session
- timestamp
- evidence excerpt
- extraction method
- confidence

## Storage model

Initial implementation uses file-based JSONL and JSON stores for simplicity and auditability.
A later version may add SQLite or a vector store.

### Planned stores

- `data/raw_sessions.jsonl`
- `data/raw_chunks.jsonl`
- `data/episodic_memory.jsonl`
- `data/semantic_memory.jsonl`
- `data/task_memory.jsonl`
- `data/invalidation_log.jsonl`
- `data/entities.json`

## OpenClaw integration points

### Ingestion inputs
- OpenClaw session transcripts
- `MEMORY.md`
- `memory/*.md`
- workspace notes and structured memory files

### Triggers
- session end
- compaction/precompact
- explicit "remember this"
- major state changes
- periodic maintenance

## Retrieval model

Retrieval should be memory-type aware.
It should not rely on a single nearest-neighbor lookup.

Planned retrieval sequence:
1. user profile / semantic memory
2. recent related episodic memory
3. task/open-loop memory
4. raw evidence snippets
5. uncertainty/conflict notes

## First implementation scope

Phase 1 focuses on:
- OpenClaw transcript ingestion
- basic session consolidation
- JSON schemas and storage
- first-pass extraction heuristics
- provenance-preserving writes

## Future work

- fact version graphs
- salience scoring
- retrieval planner
- entity resolution improvements
- vector retrieval over raw evidence
- evaluation suite for OpenClaw continuity tasks
