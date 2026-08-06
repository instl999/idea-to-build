# TASK-0001: Implementation plan

## Progress and implementation steps

- [ ] Re-read frozen core, this SPEC, working rules, and current status.
- [ ] Confirm dependency results and exact ownership.
- [ ] Implement only the accepted outcome and failure behavior.
- [ ] Add focused tests and run required quality gates.
- [ ] Update PLAN/status and move to review for human acceptance.

## Modules and paths

- Owned paths: `src/intake, src/shared, package.json, package-lock.json, tsconfig.json`.

## File ownership

- This task writes only its canonical owned paths; shared task/live state remains with the root orchestrator.

## Dependencies

- None

## Data migration

- No stored-data migration; this task defines the first internal record shape.

## Test plan

- Add focused success/failure regression tests for the acceptance criterion.
- Run `python scripts/quality_gate.py all --path . --task TASK-0001`.

## Risks

- Contract drift between dependencies; mitigate by testing exact internal inputs/outputs before merge.
- Partial local writes; mitigate with validation and atomic replacement where persistence applies.

## Rollback

- Revert or fix forward from the task commit while retaining the task branch and evidence; do not rewrite history.

## Progress discoveries

- None recorded yet.

## Important decisions

- Frozen constraints control; route any core conflict to `docs/live/CHANGE_REQUESTS.md`.

## Final result and remaining issues

- Pending implementation and quality evidence.