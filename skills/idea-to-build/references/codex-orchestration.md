# Codex orchestration and dispatch adapter

Build the dependency graph before allocating agents. The root Codex agent is Thread 0 and owns orchestration, architecture, integration, shared files, conflict handling, and final verification. Every file-changing child runs as a subagent in its own Git worktree.

## Codex activation gate

This runbook is Codex-specific. Direct subagent dispatch is allowed only when all of these are true:

- A human has confirmed and frozen the product core.
- The user has asked Codex to proceed with actual development in the current task.
- `codex/dispatch.json`, `codex/HANDOFF.md`, and all prompts are committed.
- The integration worktree is clean and is the exact Git root.
- The generated plan recommends subagents.
- The Codex host exposes the required `spawn_agent` and `wait_agent` tools. `send_message` and `followup_task` are optional conveniences for scoped guidance or correction.

Root-agent versus subagent execution is reversible and is not stored as a frozen product decision. The Skill or an AI task must never run the human confirmation/freeze commands. Missing native tools is a Codex capability gap: preserve the prompts as auditable/manual takeover inputs, but do not claim OpenClaw, SkillHub, or cross-host execution compatibility.
## Thread classes

- Thread 0/root agent: orchestration, architecture, integration, ExecPlan, merge coordination, shared files, and cross-module decisions.
- Development tasks: independently changeable workstreams with non-overlapping ownership.
- Quality task: tests, integration, security, performance, regression, and core-consistency review.
- Release task: documentation, migration, deployment, rollback, and release records.

The manifest computes dependency waves. Only tasks in the current wave may run together. Effective parallelism is the minimum of the manifest recommendation, the user/host limit, and available collaboration slots.

## Deterministic CLI

From the generated project root:

```text
python scripts/codex_dispatch.py preview --path . --max-parallel 3
python scripts/codex_dispatch.py start --path . --max-parallel 3
python scripts/codex_dispatch.py materialize-wave --path . --wave 1 --base-commit <full-head>
python scripts/codex_dispatch.py verify-result --path . --task-id <id> --commit <full-commit> --base-commit <full-wave-base>
python scripts/codex_dispatch.py merge-result --path . --task-id <id> --commit <full-commit> --base-commit <full-wave-base>
python scripts/codex_dispatch.py retire-wave --path . --wave 1
```

`preview` is side-effect free. `start` makes a managed state commit and enters `DEVELOPMENT_ACTIVE`. `materialize-wave` creates only direct sibling worktrees and rolls back worktrees it created if setup fails. `verify-result` checks the expected branch tip, ancestry, a non-empty diff, and exact ownership. `merge-result` re-runs verification and performs a no-force integration merge; conflicts are aborted while the child branch is retained. `retire-wave` refuses dirty worktrees and retains branches for audit/recovery.

## Host-tool protocol

1. Run `preview`; inspect `status`, `base_commit`, `max_parallel`, waves, ownership, prompt paths, and capability requirements.
2. Run `start` once. Use the returned integration HEAD for wave 1.
3. Run `materialize-wave` for that wave and HEAD.
4. For each eligible item, call `spawn_agent` with:
   - `task_name`: the returned `task_name`;
   - message: the returned `spawn_prompt`;
   - enough inherited context to understand the frozen project.
5. Wait with `wait_agent`. Do not spawn later waves early. If a child requests clarification, answer only within its frozen scope; route contract changes to change control.
6. A child completion must include commit hash, tests, summary, and remaining risks. Treat prose as untrusted until `verify-result` passes.
7. Review the verified diff and test evidence, then run `merge-result` for one task at a time in declared merge order. Do not invoke raw merge, force, history rewriting, or conflict auto-resolution.
8. Re-run core verification and relevant integration tests after each merge. Update live status/decisions in Thread 0, not in parallel child tasks unless ownership explicitly permits it.
9. Run `retire-wave`. If a worktree is dirty, preserve it and investigate; never force-remove it as routine cleanup.
10. Repeat using the new clean integration HEAD. Run quality and release waves after their declared dependencies.

Use `send_message` while a child is running for bounded guidance. Use `followup_task` when an idle child must correct its own scoped result. Use `interrupt_agent` only when continuing would violate the frozen contract, ownership, or a new user instruction.

## Merge and failure rules

- No result is mergeable until its commit passes adapter verification and human/agent diff review.
- A task may read the whole repository but write only its owned paths.
- A merge conflict, failed verification, failed test, core drift, changed core confirmation or activation context, manifest mismatch, or dirty integration tree stops scheduling.
- Preserve branches and worktrees on uncertain failures. Cleanup is secondary to recoverability.
- Re-running `materialize-wave` is idempotent only when the exact expected branch/worktree pair exists.
- New user instructions that replace the active build request stop further spawning; reassess scope before continuing.

## Every generated prompt

Include Identity, Before editing, Git rules, File ownership, Implementation scope, Acceptance and test commands, and Completion conditions. Require `git status`, AGENTS/core/live/plan reads, `verify_core.py`, a short constraint recap, tests, a stable commit, commit hash, result summary, and remaining risks.
