# Repository Memory Map

## Precedence

1. Frozen `docs/core/**` and `.idea-to-build/core.lock.json`.
2. The current task `SPEC.md`.
3. `docs/live/WORKING_RULES.md`.
4. `.idea-to-build/tasks.json` and the current task `PLAN.md`.
5. Current code and test evidence.
6. Chat context.

Chat never overrides repository memory. Resolve a conflict at the highest layer; put core-affecting proposals in `docs/live/CHANGE_REQUESTS.md`.

## Sources, editors, and update triggers

| Layer / information | Canonical source | Human view | Who may edit | Update trigger | New Codex conversation reads |
| --- | --- | --- | --- | --- | --- |
| Immutable product/architecture/acceptance | `docs/core/**` + core lock | Same files | Human freeze/change-control flow only after freeze | New approved baseline | Bounded verified core summary |
| Stable Codex entry rules | `AGENTS.md` | Same file | Maintainer/human review; protected from ordinary Codex | Plugin/project rule contract changes | First |
| Mutable implementation conventions | `docs/live/WORKING_RULES.md` | Same file | Codex or human with code/config/test evidence | Verified convention changes | After core |
| One task's accepted behavior | `specs/<TASK-ID>/SPEC.md` | Same file | Codex/human before and during task, subject to frozen core | Scope/acceptance evidence changes | Selected task only |
| One task's implementation record | `specs/<TASK-ID>/PLAN.md` | Same file | Current task owner | Progress, discoveries, decisions, close-out | Selected task only |
| Exact task status/ownership/dependencies | `.idea-to-build/tasks.json` | Generated `docs/live/TASKS.md` | `task_state.py`/root orchestrator | Every legal task transition | Selected/current task record |
| Current operational summary | `docs/live/STATUS.md` | Same file | Current task/root orchestrator | Phase, task, blocker, next step, or verification changes | Always |
| Quality configuration | `.idea-to-build/quality_gates.json` | `docs/live/QUALITY_GATES.md` | Reviewed maintainer/task setup | Real check commands or acceptance needs change | Selected task gates |
| Current quality evidence | Ignored `.idea-to-build/last_quality.json` | `quality_gate.py status` | Quality runner; manual entries only by user | Gate run or manual acceptance | Status/issues summary only |
| Product intake and milestones | `BACKLOG.md`, `ROADMAP.md` | Same files | Product/task planning flow | Priority or milestone changes | Only when relevant |
| Core change proposals | `CHANGE_REQUESTS.md` | Same file | Codex/human may propose; human decides | Current work conflicts with frozen core | Only when relevant |

## Bounded reading rule

Do not load all tasks, specs, test logs, archives, or external research. Read only the selected task plus relevant decisions/risks. In parallel mode, require an explicit task ID when no canonical current task is selected.