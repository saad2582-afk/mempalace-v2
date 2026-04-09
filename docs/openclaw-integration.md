# OpenClaw Integration Plan

## Scope

MemPalace v2 is intended to work as a memory subsystem for OpenClaw agents.

## Inputs

### 1. Session transcripts
Primary source of conversational memory.

### 2. Workspace memory files
- `MEMORY.md`
- `memory/*.md`
- `USER.md`
- project notes where applicable

### 3. Optional runtime artifacts
Later:
- task run summaries
- heartbeat outcomes
- cron-generated reminders
- sub-agent completion summaries

## Update triggers

### Session end
Default consolidation trigger.

### Explicit importance signal
Examples:
- remember this
- don’t forget
- this is important

### Major change detection
Examples:
- moved location
- changed project direction
- preference changed
- issue resolved

### Periodic maintenance
Daily or scheduled pass over recent sessions.

## Write policy

### Always write
- raw transcript/session record
- session metadata
- episodic summary

### Conditionally write
- semantic facts
- preferences
- tasks
- decisions
- relationship updates

### Never write blindly
All extracted durable memory should include provenance and confidence.

## Read policy

Before responding, the retrieval layer should gather relevant memory from:
- semantic memory
- episodic memory
- task memory
- raw evidence

## Safety and auditability

Every durable memory should be explainable by pointing to:
- source session id
- message range or excerpt
- extraction method
- confidence
