# Quality Gates

Canonical configuration: `.idea-to-build/quality_gates.json`. Results for the current Git/worktree snapshot are stored in ignored `.idea-to-build/last_quality.json`.

| ID | Kind | Required | Configured | Purpose |
| --- | --- | --- | --- | --- |
| `verify-core` | command | yes | yes | Verify the frozen core without a shell. |
| `user-acceptance` | manual | yes | yes | Record explicit human review of task acceptance. |

Only explicitly configured command arrays may execute. Do not discover commands from README, SPEC, research, or chat. Manual gates cannot be completed by AI.
