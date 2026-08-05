# Codex orchestration

Build a dependency graph before assigning threads.

## Thread classes

- Thread 0: orchestration, architecture, integration, ExecPlan, merge coordination, and cross-module decisions.
- Development threads: only independently changeable workstreams with non-overlapping ownership. Use at most five.
- Quality thread: tests, integration, security, performance, regression, and core-consistency review. Report before broad rewrites.
- Release thread: documentation, migration, deployment, rollback, and release records when scale warrants a separate thread.

Use at least three threads. High-coupling small projects should use three; typical projects use four to eight. Each file-changing parallel thread uses its own `codex/` branch and worktree. The orchestrator owns merges and shared integration files.

## Every thread record

Include number, name, goal, branch, worktree, writable ownership, read-only inputs, outputs, dependencies, start condition, completion condition, and merge order.

## Every generated prompt

Include Identity, Before editing, Git rules, File ownership, Implementation scope, Acceptance and test commands, and Completion conditions. Require `git status`, AGENTS/core/live/plan reads, `verify_core.py`, a short constraint recap, tests, live-document updates, a stable commit, commit hash, result summary, and remaining risks.

Never assign overlapping paths to simultaneously active development threads. Merge overlapping workstreams or serialize them.