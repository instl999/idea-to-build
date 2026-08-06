# Codex Prompt Catalog

Use `python scripts/memory_prompts.py list --path .` to list prompt kinds and `show` to render a complete project-language prompt.

| Kind | When to use | New conversation? |
| --- | --- | --- |
| `start-task` | Start one ready task from its SPEC | Yes, normally |
| `resume-task` | Resume the same task after interruption | No, unless context is unrelated or stale |
| `finish-task` | Review, test, update status, and request manual acceptance | Same task conversation |
| `sync-rules` | Reconcile mutable working rules and memory map | Maintenance conversation |
| `sync-spec` | Strengthen one mutable task SPEC/PLAN | Task planning conversation |
| `sync-tasks` | Validate ledger and regenerate TASKS.md | Maintenance conversation |
| `sync-quality` | Validate explicit gate configuration and documentation | Maintenance conversation |
| `audit-all` | Audit all four memory layers without widening product scope | Maintenance/review conversation |
