# TASK-0002: Brief generation

Evidence labels: User-confirmed fact, Immutable constraint, AI recommendation, Reversible default, Unverified assumption, or Open question.

## Background

- **User-confirmed fact:** This is a synthetic workstream derived from the frozen Team Brief Generator fixture.

## User problem

- **User-confirmed fact:** A local user needs a concise team brief generated from an already validated normalized record.

## Outcome

- **User-confirmed fact:** Generate a deterministic brief containing the frozen required sections without network access.

## Scope

- In scope: Only `src/generation` and the behavior stated below.
- Out of scope: Other workstreams, frozen core changes, network services, and real customer data.

## User flow

1. The generator receives a normalized record, applies frozen rules, and returns a reviewable brief or a typed generation error.

## Business rules

- Preserve deterministic, local-first behavior and frozen acceptance precedence.
- Reject invalid input before later state is changed.

## Inputs and outputs

- Inputs: Synthetic fixtures and completed dependency outputs.
- Outputs: A tested implementation commit, typed success/failure behavior, and review evidence.

## Data and permissions impact

- Synthetic local data only; no credentials, telemetry, remote transfer, or new privilege boundary.

## API, database, and public type impact

- Consumes the TASK-0001 normalized record and defines the brief result used by export and review.
- No database or public network endpoint is introduced.

## Edge cases and failure behavior

- Reject malformed or unauthorized input without corrupting previously valid local data.
- Preserve a recoverable error and do not claim partial output as success.

## Compatibility

- Python 3.9+ standard library and the fixture's existing cross-platform boundary remain required.

## Security and privacy

- Use only synthetic data; do not add credentials, telemetry, unreviewed dependencies, or remote transfer.

## Acceptance criteria

- [ ] A normalized synthetic meeting record produces a deterministic brief with every frozen required section, and missing required content produces a documented error.

## Automated acceptance

- Run the configured `verify-core` command gate and focused task tests when implemented.

## Manual acceptance

- The user reviews this synthetic outcome against the criterion above.

## Dependencies and blockers

- Dependencies: TASK-0001
- Blockers: None recorded.

## Quality gates

- `verify-core`
- `user-acceptance`

## Open questions

- None for this synthetic fixture.