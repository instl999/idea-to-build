# TASK-0001: Input and parsing

Evidence labels: User-confirmed fact, Immutable constraint, AI recommendation, Reversible default, Unverified assumption, or Open question.

## Background

- **User-confirmed fact:** This is a synthetic workstream derived from the frozen Team Brief Generator fixture.

## User problem

- **User-confirmed fact:** A local user needs malformed meeting-note input rejected before it can affect brief generation.

## Outcome

- **User-confirmed fact:** Normalize valid synthetic notes deterministically and return a documented validation error for malformed input.

## Scope

- In scope: Only `src/intake, src/shared, package.json, package-lock.json, tsconfig.json` and the behavior stated below.
- Out of scope: Other workstreams, frozen core changes, network services, and real customer data.

## User flow

1. The user supplies synthetic notes; the parser validates and normalizes them; downstream code receives a stable record or a typed error.

## Business rules

- Preserve deterministic, local-first behavior and frozen acceptance precedence.
- Reject invalid input before later state is changed.

## Inputs and outputs

- Inputs: Synthetic fixtures and completed dependency outputs.
- Outputs: A tested implementation commit, typed success/failure behavior, and review evidence.

## Data and permissions impact

- Synthetic local data only; no credentials, telemetry, remote transfer, or new privilege boundary.

## API, database, and public type impact

- Defines the internal normalized input record and validation error consumed by later tasks.
- No database or public network endpoint is introduced.

## Edge cases and failure behavior

- Reject malformed or unauthorized input without corrupting previously valid local data.
- Preserve a recoverable error and do not claim partial output as success.

## Compatibility

- Python 3.9+ standard library and the fixture's existing cross-platform boundary remain required.

## Security and privacy

- Use only synthetic data; do not add credentials, telemetry, unreviewed dependencies, or remote transfer.

## Acceptance criteria

- [ ] Valid synthetic meeting notes produce a deterministic normalized record, while malformed input returns a documented validation error without persistence.

## Automated acceptance

- Run the configured `verify-core` command gate and focused task tests when implemented.

## Manual acceptance

- The user reviews this synthetic outcome against the criterion above.

## Dependencies and blockers

- Dependencies: None
- Blockers: None recorded.

## Quality gates

- `verify-core`
- `user-acceptance`

## Open questions

- None for this synthetic fixture.