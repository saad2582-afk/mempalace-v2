# MemPalace v2 for OpenClaw

MemPalace v2 is an OpenClaw-focused persistent memory subsystem.

The goal is not just searchable transcript recall.
The goal is cross-session continuity for agents:
- durable user and project memory
- episodic session memory
- fact versioning and invalidation
- task/open-loop tracking
- retrieval-ready memory assembly
- raw evidence preserved for auditability

## Status

Early scaffold.

## Core idea

A sharp memory system needs multiple layers:
- raw memory: exact transcripts and evidence
- episodic memory: what happened in a session
- semantic memory: stable facts, preferences, decisions
- task memory: open loops, reminders, unresolved work
- provenance: every durable memory links back to source evidence

## Initial components

- `docs/architecture-v2.md` — architecture and update flow
- `docs/openclaw-integration.md` — OpenClaw-specific integration plan
- `schemas/` — memory schemas
- `src/mempalace_v2/ingestion/` — transcript and file ingestion
- `src/mempalace_v2/consolidation/` — first-pass memory consolidation

## Design principles

1. Keep raw evidence
2. Consolidate after sessions
3. Version facts instead of overwriting blindly
4. Separate memory types
5. Be auditable and local-first

## Current prototype capabilities

- ingest OpenClaw-style session files
- consolidate sessions into episodic, semantic, task, profile, and relationship memory
- persist structured memory in SQLite
- retrieve memory relevant to a prompt
- assemble compact memory context for use before a reply
- simulate OpenClaw session-end and pre-response flows from the CLI

## Near-term roadmap

1. OpenClaw transcript ingestion
2. Session consolidation
3. Structured semantic/task memory extraction
4. Fact invalidation and versioning
5. Retrieval planning and memory assembly
6. OpenClaw flow integration and hook wiring
