# Thread 0: Orchestrator, architecture, and integration

## Identity

You own only this workstream: Maintain canonical task state, coordinate ownership, integrate branches, and resolve cross-module decisions

Canonical task: orchestrator (select an explicit task before implementation)
Task SPEC: select from .idea-to-build/tasks.json
Task PLAN: select from .idea-to-build/tasks.json
Required quality gates: select from the canonical task

## Before editing

1. Locate the Git root and run `git status`.
2. Confirm the worktree is clean enough for this scoped work.
3. Read `AGENTS.md`, `docs/live/MEMORY_MAP.md`, the frozen core summary, `WORKING_RULES.md`, `STATUS.md`, this task SPEC and PLAN, relevant decisions/risks, and no unrelated task archive.
4. Run `python scripts/verify_core.py --path .`.
5. Restate the controlling constraints in at most ten bullets.
6. Do not edit until these checks pass.

## Git rules

- Use branch `current integration branch` in worktree `.`.
- Initialize Git only if absent; never start major work in an unexplained dirty tree.
- Use a separate worktree for parallel changes and stay within the ownership below.
- Commit each runnable, tested stable feature with an accurate message.
- Create a new branch before major refactoring; milestone tags are optional and human-reviewed.
- Never force-push, rewrite public history without approval, or use destructive reset to erase unknown changes.
- Prefer revert, recovery branches, or a known stable commit after failure.
- Never commit secrets, tokens, `.env`, or personal data.
- Run tests and core verification immediately before commit.

## File ownership

Writable:
- `plans`
- `.idea-to-build/tasks.json`
- `.idea-to-build/quality_gates.json`
- `docs/live/DECISIONS.md`
- `docs/live/RISKS.md`
- `docs/live/TASKS.md`
- `docs/live/STATUS.md`

Read-only: `AGENTS.md`, live documents not assigned here, and other threads' owned paths.

Forbidden: `docs/core/**`, `.idea-to-build/core.lock.json`, protection hooks, and paths outside this repository.

Shared integration files must be proposed in the handoff and merged by Thread 0.

## Implementation scope

- Must complete: Maintain canonical task state, coordinate ownership, integrate branches, and resolve cross-module decisions
- Must not complete: unrelated workstreams or a core-contract change.
- Dependencies: None
- Before adding a production dependency, explain necessity, maintenance, license, security, privacy, deployment fit, lock-in, and replacement options.
- Preserve the API, open-source, and acceptance constraints in the frozen documents.

## Acceptance and test commands

- `python scripts/verify_core.py --path .`
- `python scripts/verify_core.py --path .`

## Completion conditions

- The scoped feature runs and all required tests pass.
- Core hashes remain valid.
- Relevant live updates are proposed to the orchestrator.
- The stable work is committed.
- Report the commit hash, change summary, test results, and remaining risks.
- Never automatically modify or refreeze core documents.
