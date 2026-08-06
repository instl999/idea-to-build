# Codex Development Handoff

Development mode: `parallel_worktrees`.
Recommended Codex execution: **root orchestrator plus 4 scoped tasks**.

Parallel worktrees are selected because explicitly prepared tasks have independent non-overlapping ownership.
Frozen core hash: `409bf7fe207f8da0d0e50eff1f0c2ff16b1eb70720b89cfdabd2e742281e7b73`

## Beginner next step

Current task: `TASK-0001`.
Run: `python scripts/memory_prompts.py show --path . --kind start-task --task TASK-0001`.
Copy the complete output into a new Codex conversation and restate that the task SPEC controls scope. Do not paste only the word continue.
Finish with: `python scripts/memory_prompts.py show --path . --kind finish-task --task TASK-0001`.

## Advanced parallel mode

Use this section only when `development_mode` is `parallel_worktrees`. Each child must name its canonical task, SPEC, PLAN, gates, branch, worktree, and owned paths. The orchestrator alone updates canonical task state and shared live documents.

Codex activation policy: **start after freeze when the user asks to proceed with development**.
Dispatch manifest: `codex/dispatch.json`.

## Merge sequence

1. Thread 0 validates task SPECs, plans, gates, dependencies, and ownership.
2. Independent task branches merge in declared order after verification.
3. The orchestrator re-runs current-snapshot quality gates and updates task/live status.

## Thread 0 — Orchestrator, architecture, and integration

- Goal: Maintain canonical task state, coordinate ownership, integrate branches, and resolve cross-module decisions
- Canonical task: `orchestrator`
- SPEC / PLAN: `select explicitly` / `select explicitly`
- Quality gates: select from canonical task
- Branch: `current integration branch`
- Worktree: `.`
- Writable ownership: `plans`, `.idea-to-build/tasks.json`, `.idea-to-build/quality_gates.json`, `docs/live/DECISIONS.md`, `docs/live/RISKS.md`, `docs/live/TASKS.md`, `docs/live/STATUS.md`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: None
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 0

## Thread 1 — Canonical TASK-0001

- Goal: Implement TASK-0001 under specs/TASK-0001/SPEC.md
- Canonical task: `TASK-0001`
- SPEC / PLAN: `specs/TASK-0001/SPEC.md` / `specs/TASK-0001/PLAN.md`
- Quality gates: `verify-core`, `user-acceptance`
- Branch: `codex/01-task-0001`
- Worktree: `../team-brief-generator-01-task-0001`
- Writable ownership: `src/intake`, `src/shared`, `package.json`, `package-lock.json`, `tsconfig.json`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: None
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 1

## Thread 2 — Canonical TASK-0002

- Goal: Implement TASK-0002 under specs/TASK-0002/SPEC.md
- Canonical task: `TASK-0002`
- SPEC / PLAN: `specs/TASK-0002/SPEC.md` / `specs/TASK-0002/PLAN.md`
- Quality gates: `verify-core`, `user-acceptance`
- Branch: `codex/02-task-0002`
- Worktree: `../team-brief-generator-02-task-0002`
- Writable ownership: `src/generation`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: TASK-0001
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 2

## Thread 3 — Canonical TASK-0003

- Goal: Implement TASK-0003 under specs/TASK-0003/SPEC.md
- Canonical task: `TASK-0003`
- SPEC / PLAN: `specs/TASK-0003/SPEC.md` / `specs/TASK-0003/PLAN.md`
- Quality gates: `verify-core`, `user-acceptance`
- Branch: `codex/03-task-0003`
- Worktree: `../team-brief-generator-03-task-0003`
- Writable ownership: `src/export`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: TASK-0001
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 3

## Thread 4 — Canonical TASK-0004

- Goal: Implement TASK-0004 under specs/TASK-0004/SPEC.md
- Canonical task: `TASK-0004`
- SPEC / PLAN: `specs/TASK-0004/SPEC.md` / `specs/TASK-0004/PLAN.md`
- Quality gates: `verify-core`, `user-acceptance`
- Branch: `codex/04-task-0004`
- Worktree: `../team-brief-generator-04-task-0004`
- Writable ownership: `ui`
- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan
- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary
- Dependencies: TASK-0001
- Start condition: core verification passes and dependencies are available
- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed
- Merge order: 4
