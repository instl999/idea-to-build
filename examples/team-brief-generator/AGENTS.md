# Idea-to-Build project rules

Before any work, read all files in `docs/core/`, plus `docs/live/STATUS.md`, `ROADMAP.md`, `DECISIONS.md`, `RISKS.md`, and the relevant ExecPlan under `plans/`. Run `python scripts/verify_core.py --path .` and briefly state the controlling constraints before editing.

- Never modify `docs/core/**` or `.idea-to-build/core.lock.json`. Propose core changes only in `docs/live/CHANGE_REQUESTS.md`.
- Never run `freeze_core.py`, record core confirmation, unlock core files, update core hashes, weaken protection, or lower acceptance criteria.
- Use an ExecPlan for complex features or major refactors.
- Run the documented tests after code changes and update the relevant live documents.
- Commit each stable tested feature. Create a branch or separate worktree before major or parallel work.
- Parallel threads must have non-overlapping writable file ownership; the orchestrator merges shared files.
- Never commit keys, tokens, `.env` files, personal data, or secret-bearing output.
- Do not use destructive reset, force push, or history rewriting to hide failures or unknown changes.