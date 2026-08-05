# Team Brief Generator - Project Charter

Status: Human-approved and frozen

## User-confirmed facts

- Product leads and engineering managers need a faster way to turn meeting notes into consistent, reviewable briefs.
- Source notes may contain private company information and must remain on the device.
- A useful brief is produced and reviewed in under two minutes.

## Immutable constraints

- Local-only processing; no runtime network calls.
- Every generated item retains a source span.
- No accounts or autonomous actions in MVP.

## Scope

- In scope: note input, deterministic extraction, review/edit, local persistence, deletion, Markdown export.
- Non-goals: recording, transcription, cloud sync, collaboration, calendar bots, automatic task assignment.

## Success boundary

- Golden-flow acceptance passes, offline behavior is verified, and 80% of test users finish without help.
