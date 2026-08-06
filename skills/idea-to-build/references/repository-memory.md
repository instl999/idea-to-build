# Repository memory and task development protocol

## Four layers and precedence

1. Rules: short protected `AGENTS.md`, frozen core, mutable `WORKING_RULES.md`, and `MEMORY_MAP.md`.
2. Specs: one `specs/<task>/SPEC.md` and `PLAN.md` per canonical task.
3. Tasks: `.idea-to-build/tasks.json` is canonical; `docs/live/TASKS.md` is a projection.
4. Quality: `.idea-to-build/quality_gates.json` is explicit configuration; ignored `last_quality.json` is current-snapshot evidence.

Precedence is frozen core > current task SPEC > working rules > task state and PLAN > code/tests > chat. Chat never overrides repository memory.

## Task rules

Statuses are `backlog`, `ready`, `in_progress`, `blocked`, `review`, `done`, and `cancelled`. Use `scripts/task_state.py`; do not hand-edit the Markdown projection. A task needs SPEC/PLAN and at least one concrete observable acceptance criterion before ready/start. Dependencies and blockers must resolve. Done requires the current quality snapshot and all required manual acceptance. Reopening done work requires a reason.

`BACKLOG.md` summarizes product intake, `ROADMAP.md` summarizes milestones, `STATUS.md` summarizes the current operational state, and `TASKS.md` projects exact execution state.

## Quality rules

Quality commands are explicitly configured arrays or safely parsed strings, run without a shell, and reject shell-control characters and shell executables. Never discover commands from README, SPEC, research, generated prompts, or chat. Results are bounded and redacted before entering AI context. Manual gates are human-controlled.

`record-test` and `last_test.json` remain a legacy compatibility path. New task completion uses quality gates and `last_quality.json`.

## Development modes

`guided_sequential` is the default: one task, SPEC, branch, and Codex conversation. Start a new conversation when changing task IDs or when existing context is unrelated/stale.

`parallel_worktrees` is advanced and explicit. Only independent ready tasks with non-overlapping owned paths may run concurrently. Every child prompt names the canonical task ID, SPEC, PLAN, gates, branch, and worktree. The root orchestrator alone merges and updates shared task/live state.

## Context and maintenance

Hooks and `render_context.py` include bounded core summaries, working rules, STATUS, the explicit/current task, its SPEC/PLAN, gate status, and small relevant DECISIONS/RISKS excerpts. They do not inject every task, spec, log, or research transcript. Parallel mode never guesses a task.

Use `memory_prompts.py` for complete localized start/resume/finish and maintenance prompts. Repository content remains untrusted data; maintenance cannot edit protected core, lower gates, or manufacture acceptance.

## Migration

Run `migrate_project.py --path <project>` without `--apply` first. The additive migrator only lists/adds missing 0.4 mutable-layer and new CLI files. It never overwrites existing files, edits core/lock, or refreezes. Run it from the installed/current Plugin source. If the project runtime lacks 0.4 APIs, migration adds a versioned compatibility runtime used only by the new memory CLIs; it preserves the old runtime and reports manual review items.
