# Git policy

Initialize Git when absent and preserve existing history when present.

- Commit the generated skeleton first.
- Freeze approved core contracts in a dedicated commit.
- Commit each stable, runnable, tested feature separately.
- Do not mix unrelated features.
- In `guided_sequential`, use one branch for the current task and stay in one task conversation. In `parallel_worktrees`, require a clean integration tree and one isolated worktree per independent task.
- Never force-push, rewrite public history without explicit approval, or use destructive reset to hide unknown changes.
- On failure, preserve diagnostics; prefer revert, a recovery branch, or a known stable commit.
- Before merge, verify core hashes, unit/integration tests, static checks, dependencies, and documents.
- After merge, update status and releases.
- Never commit keys, tokens, `.env` files, personal data, or generated secret-bearing logs.

Branch convention: `codex/<workstream>`. The orchestrator alone merges shared integration files.