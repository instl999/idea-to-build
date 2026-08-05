# Codex Development Handoff

This project should use exactly **7 Codex threads**.

Frozen core hash: `409bf7fe207f8da0d0e50eff1f0c2ff16b1eb70720b89cfdabd2e742281e7b73`

## Merge sequence

1. Thread 0 validates plans and ownership.
2. Independent development branches merge in numeric order after their checks pass.
3. Quality validates the integrated tree and reports findings.
4. Release work merges last when present.

## Thread 0 — Orchestrator, architecture, and integration

- Goal: Maintain the ExecPlan, coordinate ownership, integrate branches, and resolve cross-module decisions
- Branch: `codex/00-orchestrator-architecture-and-integratio`
- Worktree: `../team-brief-generator-00-orchestrator-architecture-and-integratio`
- Writable ownership: `plans`, `docs/live/DECISIONS.md`, `docs/live/RISKS.md`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: None
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 0

## Thread 1 — Input and parsing

- Goal: Implement validated note ingestion and deterministic parsing
- Branch: `codex/01-input-and-parsing`
- Worktree: `../team-brief-generator-01-input-and-parsing`
- Writable ownership: `src/intake`, `src/shared`, `package.json`, `package-lock.json`, `tsconfig.json`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: None
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 1

## Thread 2 — Brief generation

- Goal: Build traceable brief generation and editing state
- Branch: `codex/02-brief-generation`
- Worktree: `../team-brief-generator-02-brief-generation`
- Writable ownership: `src/generation`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: Input and parsing
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 2

## Thread 3 — Export and persistence

- Goal: Implement local persistence, deletion, and Markdown export
- Branch: `codex/03-export-and-persistence`
- Worktree: `../team-brief-generator-03-export-and-persistence`
- Writable ownership: `src/export`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: Input and parsing
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 3

## Thread 4 — Review interface

- Goal: Build the accessible review workflow
- Branch: `codex/04-review-interface`
- Worktree: `../team-brief-generator-04-review-interface`
- Writable ownership: `ui`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: Input and parsing
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 4

## Thread 5 — Quality engineering

- Goal: Report test, integration, security, performance, regression, and core-consistency findings
- Branch: `codex/05-quality-engineering`
- Worktree: `../team-brief-generator-05-quality-engineering`
- Writable ownership: `tests`, `quality`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: Input and parsing, Brief generation, Export and persistence, Review interface
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 5

## Thread 6 — Release and operations

- Goal: Complete release checks, documentation, migration, deployment, rollback, and release records
- Branch: `codex/06-release-and-operations`
- Worktree: `../team-brief-generator-06-release-and-operations`
- Writable ownership: `docs/live/STATUS.md`, `docs/live/RELEASES.md`, `deploy`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: Quality engineering
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 6
