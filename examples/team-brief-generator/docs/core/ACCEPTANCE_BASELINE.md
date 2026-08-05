# Team Brief Generator - Acceptance Baseline

## Functional

- Golden note produces the expected summary, decisions, action items, risks, and open questions.
- Each item maps to the exact source span; unknown owner and date fields remain unknown.
- Review edits persist and Markdown export matches the reviewed content.
- Delete-all requires confirmation and removes all saved briefs.

## Non-functional

- A 50 KB note yields a first draft within two seconds on the reference laptop.
- Processing succeeds with networking disabled and emits zero network requests.
- Keyboard operation, focus visibility, semantic labels, and WCAG 2.2 AA contrast pass.
- Empty, oversized, unsupported, duplicate, malformed, and hostile inputs fail safely.

## Release evidence

- Unit, integration, end-to-end, security, accessibility, offline, performance, backup/restore, and core-hash checks pass.
- Known risks and rollback steps are recorded in `docs/live/RISKS.md` and `docs/live/RELEASES.md`.
