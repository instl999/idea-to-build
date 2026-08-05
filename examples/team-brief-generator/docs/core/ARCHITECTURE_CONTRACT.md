# Team Brief Generator - Architecture Contract

## Boundaries

- `src/intake`: validated file and paste ingestion.
- `src/generation`: deterministic extraction, source-span model, and editable brief state.
- `src/export`: local persistence, deletion, backup/restore, and Markdown serialization.
- `ui`: accessible review workflow.

## Data flow

User input is validated, normalized in memory, parsed into typed items with source offsets, reviewed, then persisted or exported locally.

## Required properties

- TypeScript implementation with no runtime network dependency.
- Storage is behind an adapter and does not log note content.
- Untrusted note content and generated Markdown are escaped at rendering boundaries.
- Golden fixtures and property tests cover offsets and serializer round trips.

## Replaceable choices

Packaging framework, UI component library, and local database may change if the contract and acceptance baseline remain intact.
