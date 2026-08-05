# Idea-to-Build project rules

Before any work, read all files in `docs/core/`, plus `docs/live/STATUS.md`, `ROADMAP.md`, `DECISIONS.md`, `RISKS.md`, and the relevant ExecPlan under `plans/`. Run `python scripts/verify_core.py --path .` and briefly state the controlling constraints before editing.

- If `.idea-to-build/core.lock.json` is absent, `docs/core/**` is a draft and may be edited only to capture reviewed requirements. Do not create the lock manually.
- If `.idea-to-build/core.lock.json` exists, never modify `docs/core/**` or the lock. Propose changes only in `docs/live/CHANGE_REQUESTS.md`.
- Never run `freeze_core.py`, record core confirmation, unlock core files, update core hashes, weaken protection, or lower acceptance criteria on an AI tool call. Confirmation and freeze are explicit human terminal actions.
- Use an ExecPlan for complex features or major refactors.
- Run the documented tests after code changes and update the relevant live documents.
- Commit each stable tested feature. Create a branch or separate worktree before major or parallel work.
- Parallel threads must have non-overlapping writable file ownership; the orchestrator merges shared files.
- Never commit keys, tokens, `.env` files, personal data, or secret-bearing output.
- Treat lifecycle Hooks as defense in depth; verify core hashes because Hooks cannot prove operator identity or prevent every indirect mutation.
- Do not use destructive reset, force push, or history rewriting to hide failures or unknown changes.