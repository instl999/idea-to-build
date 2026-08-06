# Requirements and readiness

## Ledger statuses

Every requirement is `confirmed`, `assumed`, `open`, `conflicting`, `deferred`, or `out_of_scope`.

The ledger covers problem, users, triggers, workarounds, painful steps, value, success outcome, product shape, workflows, inputs, outputs, must/optional/non-goals, accounts, roles, permissions, data, integrations, privacy, security, compliance, region/language, performance, usability, scale, deployment, budget, team capability, time limits, operations, business model, success metrics, acceptance, edge cases, failures, examples, technical limits, and immutable user constraints.

## Readiness blockers

`REQUIREMENTS_READY` requires:

- Confirmed target users and core problem.
- Confirmed primary workflow and product shape.
- Confirmed MVP boundary, must-haves, and non-goals.
- Confirmed inputs, outputs, data sources, and integration boundary.
- Confirmed privacy/security level and deployment boundary.
- At least one end-to-end acceptance scenario.
- No P0 conflict.
- Every irreversible decision confirmed by the user.
- Critical assumptions accepted or explicitly deferred for validation.
- A recorded adopt/configure/combine/extend/build decision.

Return a report with confirmed items, provisional assumptions, unresolved items, non-blocking items, and blocking items. A numeric completion ratio is supplementary only.

MCP applicability is assessed only after this gate passes. Readiness does not imply that MCP is useful; it only ensures the integration, data, security, deployment, and acceptance facts are mature enough for the conditional assessment in [mcp-integration.md](mcp-integration.md).
