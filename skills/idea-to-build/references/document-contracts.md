# Document contracts

## Epistemic labels

Every generated design document distinguishes:

- **User-confirmed fact**
- **AI recommendation**
- **Reversible default**
- **Unverified assumption**
- **Immutable constraint**

## Frozen core

- `docs/core/PROJECT_CHARTER.md`: problem, users, outcomes, scope, non-goals.
- `docs/core/PRODUCT_CONTRACT.md`: workflows, behaviors, inputs/outputs, permissions, acceptance.
- `docs/core/ARCHITECTURE_CONTRACT.md`: boundaries, data ownership, integrations, deployment, irreversible choices.
- `docs/core/CONSTRAINTS.md`: security, privacy, compliance, budget, schedule, technology, operations.
- `docs/core/ACCEPTANCE_BASELINE.md`: end-to-end and non-functional acceptance criteria.

Before freeze, show a preview and keep `core_frozen: false`. After a human-confirmed freeze, these files and `.idea-to-build/core.lock.json` are immutable to AI development conversations.

## Live documents

`STATUS`, `ROADMAP`, `BACKLOG`, `DECISIONS`, `RISKS`, `RESEARCH`, `RELEASES`, and `CHANGE_REQUESTS` are mutable operational records. A live decision cannot override a frozen contract. Core changes are proposed only through `CHANGE_REQUESTS.md` and completed by a human-managed review and refreeze process.

## Development set

Generate a product requirements document, user stories, flows, features, non-functional requirements, data model, API contract, system context, component boundaries, dependencies, security/privacy/permissions, error handling, observability, testing, deployment, rollback, MVP roadmap, risks, reuse matrix, and Codex handoff.

Also generate a conditional MCP integration guide. It records one post-readiness recommendation, including `MCP_NOT_APPLICABLE` when no server belongs in the design.
