# Develop this project with Codex

The default is guided sequential development: one task, one SPEC, one branch, and one Codex conversation. Use parallel worktrees only after independent tasks, dependencies, gates, and non-overlapping owned paths are explicit.

## Start the first task

```text
python scripts/task_state.py list --path .
python scripts/memory_prompts.py show --path . --kind start-task --task TASK-0001
```

Copy the complete second command output into a new Codex conversation and say that the referenced SPEC controls scope. Do not say only “continue”. Stay in the same conversation while implementing that task; start another conversation when switching task IDs, recovering from unrelated context, or delegating an independent parallel task.

Before finishing, run:

```text
python scripts/memory_prompts.py show --path . --kind finish-task --task TASK-0001
```

The task reaches `done` only after current-snapshot command gates pass and the user completes all required manual acceptance.
