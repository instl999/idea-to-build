# Workflow and state machine

Idea-to-Build is a gated workflow, not a one-shot document generator.

## Phases

1. `IDEA_RECEIVED`
2. `SEARCH_REQUIRED`
3. `SEARCH_IN_PROGRESS`
4. `SOLUTION_FOUND`
5. `BUILD_DECISION_REQUIRED`
6. `REQUIREMENTS_GATHERING`
7. `REQUIREMENTS_CONFLICT`
8. `REQUIREMENTS_READY`
9. `CORE_REVIEW`
10. `CORE_FROZEN`
11. `DOCUMENTS_GENERATED`
12. `CODEX_HANDOFF_READY`
13. `DEVELOPMENT_ACTIVE`
14. `CHANGE_REQUESTED`
15. `RELEASE_READY`
16. `ARCHIVED`

Use the state CLI for explicit transitions. It rejects unsupported jumps and newer schemas it cannot safely interpret.

## Gates

- Research gate: no current-solution conclusion without live evidence.
- Build gate: requirements gathering follows a user decision to configure, combine, extend, or build.
- Readiness gate: all blocking readiness checks pass.
- Freeze gate: readiness passes and a human records explicit confirmation.
- Development gate: core hashes verify and the handoff contains non-overlapping file ownership.
- Release gate: tests, documentation, risks, decisions, core verification, and Git status are reviewed.

## Question strategy

Ask 3-7 related questions per turn. Explain why the batch matters. Offer reversible defaults, allow “unknown,” and stop to resolve conflicting P0 requirements.

## Recovery

Never repair core drift by updating hashes. Stop, preserve evidence, record a change request, and use the documented human change-management procedure.