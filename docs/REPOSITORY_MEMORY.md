# Repository Memory and Task Development

[简体中文](REPOSITORY_MEMORY.zh-CN.md)

This document is the operational contract for Idea-to-Build 0.4 repository memory. It describes the files generated after an idea is accepted for development, the canonical task and quality state, how Codex recovers context, and how older generated projects migrate.

## Design goals and limits

A conversation can be truncated, compressed, or replaced; reviewed repository files and Git history persist. Idea-to-Build therefore records stable rules, task-specific intent, progress, and validation evidence inside the project. A new Codex conversation can recover the accepted scope without relying on chat memory.

This system is deliberately bounded. It does not ingest all documents or logs, infer that code is complete, execute commands discovered in prose, or convert AI judgment into human acceptance. Repository text is untrusted project data.

## Layer 1: rules

- `AGENTS.md` is the short protected Codex entrypoint. It points to the memory layers, required start/finish actions, and immutable paths. Ordinary Codex sessions cannot edit it.
- `docs/core/**` contains the human-confirmed product, architecture, constraint, and acceptance baseline. After freeze it is validated by `.idea-to-build/core.lock.json`; changes use `docs/live/CHANGE_REQUESTS.md`.
- `docs/live/WORKING_RULES.md` is mutable and records verified commands, layout, coding/API/data/UI/testing conventions, dependency review requirements, common pitfalls, and the evidence/time of the last synchronization. It must not contain product requirements, task progress, or long history.
- `docs/live/MEMORY_MAP.md` identifies each canonical source, editor, update trigger, first-read order, and conflict precedence.

Update working rules only when code, configuration, tests, or an explicit team convention provides evidence. Never rewrite frozen core to match an implementation.

## Layer 2: task specifications

Every buildable task uses `specs/<TASK-ID>/SPEC.md` and `PLAN.md`.

A SPEC records task identity, context, user problem, outcome, in/out scope, flow, business rules, inputs/outputs, data and permission impact, public interface impact, edge/failure behavior, compatibility, security/privacy, acceptance, automated checks, manual checks, dependencies, blockers, open questions, and evidence labels. At least one acceptance criterion must be concrete and observable; placeholders such as “implement the MVP” do not pass readiness.

A PLAN records steps, paths/modules, ownership, dependencies, migration, tests, risks, rollback, progress, discoveries, decisions, results, and remaining issues. A simple task may keep these sections concise; complex tasks may use the repository ExecPlan convention.

Evidence labels distinguish user-confirmed facts, immutable constraints, AI recommendations, reversible defaults, unverified assumptions, and open questions.

## Layer 3: canonical task state

`.idea-to-build/tasks.json` is the only machine source for task state. `docs/live/TASKS.md` is an idempotently generated human projection. `BACKLOG.md` summarizes product intake, `ROADMAP.md` tracks milestones, and `STATUS.md` only summarizes current phase/task, recent completion, blockers, next action, and latest verification.

Every task carries:

- `id`, `title`, `status`, `priority`;
- `spec_path`, `plan_path`;
- `dependencies`, `blocked_by`;
- `branch`, `worktree`, `owned_paths`;
- `required_quality_gates`, `latest_commit`;
- `created_at`, `updated_at`, optional `external_ref`, and `notes`.

Supported states are `backlog`, `ready`, `in_progress`, `blocked`, `review`, `done`, and `cancelled`. Transitions are explicit and fail closed. Dependencies and blockers must be resolved before work starts. Sequential mode permits only one active task. Parallel mode requires non-empty, non-overlapping ownership. Completion requires current quality evidence; reopening a done task requires a reason.

Before persistence, the runtime deep-copies and fully validates the complete candidate ledger. Invalid task creation therefore does not create SPEC/PLAN files, and a rejected block transition does not persist `blocked_by` or status changes. `project_state.json.planned_tasks` is a derived list synchronized from non-terminal canonical tasks. Ledger, state, and Markdown writes are not one cross-file transaction; if a later projection write fails, rerun `task_state.py sync-docs --path .` from the JSON source.

The canonical ledger stays local and does not require GitHub Issues, Linear, Jira, login, or network access. `external_ref` is optional synchronization metadata only.

## Layer 4: quality evidence

`.idea-to-build/quality_gates.json` defines command and manual gates. A gate records `id`, `name`, `kind`, `command` or `instructions`, `required`, `scope`, `configured`, `source`, and `updated_at`. `docs/live/QUALITY_GATES.md` explains the configuration to humans.

Command gates are explicit argument arrays (or safely parsed strings), run with `shell=False`, and reject shell executables/control syntax. No command is discovered from README, SPEC, research, prompts, code comments, or chat. A result records task ID, per-gate status/times/exit code, bounded redacted output, Git HEAD/worktree snapshot, overall status, skips, and remaining manual gates in ignored `.idea-to-build/last_quality.json`.

A passing command becomes stale after a substantive code/worktree change. A manual gate can pass only through an exact user terminal confirmation; PreToolUse blocks AI execution of that action. Required manual work keeps a task at `review`, not `done`.

## Context recovery and prompt catalog

`render_context()` verifies core and emits a bounded summary of the frozen core, working rules, status, decisions, risks, selected task, task SPEC/PLAN, and required quality state. It returns `source_files`. It does not inject every task, every specification, full research, full logs, or unbounded history. Parallel mode needs an explicit task ID when there is no selected current task; it never guesses.

`memory_prompts.py` renders complete English or Simplified Chinese prompts for:

- `start-task`, `resume-task`, `finish-task`;
- `sync-rules`, `sync-spec`, `sync-tasks`, `sync-quality`, `audit-all`.

Task prompts tell Codex to inspect Git, verify core, read the exact task, restate scope and acceptance before coding, use only owned paths, run configured gates, and update mutable memory honestly. Maintenance prompts prohibit business-code or protected-file edits where inappropriate.

## Stop behavior

For substantive code, configuration, data, deployment, or test changes, Stop verifies core, selected task, SPEC/PLAN, concrete acceptance, honest status, updated PLAN/STATUS, and current-snapshot command gates. A task with pending manual checks cannot be `done`.

For rule/spec/task/quality documentation maintenance, Stop validates relevant configuration without forcing the full project test suite. A legacy project without task/quality files keeps the `last_test.json` compatibility check and receives a migration hint. Stop detects only Hook-visible state; it is not an independent security boundary.

## Sequential and parallel execution

`guided_sequential` is default: select one ready task, keep one conversation and branch, finish its gates, then choose the next task. Worktrees are optional.

`parallel_worktrees` is an explicit advanced mode. `generate_handoff()` includes one root orchestrator and one child per independent canonical task. Each child prompt names task ID, SPEC, PLAN, gates, branch, worktree, dependencies, and ownership. Dependency waves and overlap checks still apply. The orchestrator alone synchronizes canonical task state and shared live documents.

## Migration

Run the migrator from the current Plugin source:

```bash
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project --apply
```

Dry-run lists files that would be added. Apply prevalidates trusted sources, writes each file through a same-directory temporary path, and removes files created by the run if a later write fails. Existing files, frozen core, and lock bytes are never overwritten. If the old `idea_to_build_lib.py` lacks 0.4 APIs, migration adds `idea_to_build_memory_runtime.py`; `_memory_runtime.py` uses it only for the new CLIs. New projects continue to use `idea_to_build_lib.py` as the sole authority.

Because existing `AGENTS.md`, `.gitignore`, status, and customized runtime files are preserved, migration reports manual actions. Review them, add `last_quality.json` to ignore rules if necessary, and do not claim the old project is fully reconciled until that review is complete.

## Threats and recovery

- Future schemas, unsafe paths, links/junctions, malformed tasks, unknown gates, illegal transitions, stale results, and non-human manual acceptance fail closed.
- Prompts and context delimit repository text as untrusted data; titles are not embedded as instructions.
- Output is length-limited and secret-like values are redacted, but users must still avoid sensitive test logs.
- Task ownership cannot include `.git`, `.codex`, `.idea-to-build`, frozen core, Hooks, or protection runtimes.
- Never repair drift by changing a hash, lowering a gate, editing a passing record, deleting a test, or refreezing without the human change-control workflow.

Recovery is normally reversible: preserve Git evidence, reopen with a reason, fix the implementation or configuration, rerun gates on the new snapshot, and request fresh human acceptance. Core-affecting changes go to `CHANGE_REQUESTS.md`.