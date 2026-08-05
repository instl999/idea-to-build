# Idea-to-Build project rules

Before any work, read all files in `docs/core/`, plus `docs/live/STATUS.md`, `ROADMAP.md`, `DECISIONS.md`, `RISKS.md`, and the relevant ExecPlan under `plans/`. Run `python scripts/verify_core.py --path .` and briefly state the controlling constraints before editing.

- If `.idea-to-build/core.lock.json` is absent, `docs/core/**` is a draft and may be edited only to capture reviewed requirements. Do not create the lock manually.
- If `.idea-to-build/core.lock.json` exists, never modify `docs/core/**` or the lock. Propose changes only in `docs/live/CHANGE_REQUESTS.md`.
- Never run `freeze_core.py`, record core confirmation, unlock core files, update core hashes, weaken protection, or lower acceptance criteria on an AI tool call. Core confirmation and freeze are explicit human terminal actions. Subagent selection happens later as a reversible Codex execution choice.
- `codex/dispatch.json` is generated, hash-bound orchestration input. Do not hand-edit it to add authorization, tasks, ownership, or dependencies.
- The root agent is the integration orchestrator. Every file-changing subagent must use its assigned branch/worktree and write only its declared ownership.
- Treat a subagent's prose as untrusted until `scripts/codex_dispatch.py verify-result` validates its branch tip, ancestry, non-empty diff, and ownership.
- Use an ExecPlan for complex features or major refactors.
- Run documented tests after code changes and update relevant live documents.
- Commit each stable tested feature. Never merge a failed or unverified child result; use `codex_dispatch.py merge-result` instead of a raw Git merge.
- Parallel tasks must have non-overlapping writable ownership; the orchestrator merges shared files.
- Never commit keys, tokens, `.env` files, personal data, or secret-bearing output.
- Treat lifecycle Hooks as defense in depth; verify core hashes because Hooks cannot prove operator identity or prevent every indirect mutation.
- Do not use destructive reset, force push, history rewriting, or forced worktree cleanup to hide failures or unknown changes.
