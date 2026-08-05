# Module Boundaries

> Working design scaffold generated from frozen core hash `409bf7fe207f8da0d0e50eff1f0c2ff16b1eb70720b89cfdabd2e742281e7b73`; complete and review it before implementation.

## Evidence labels

- **User-confirmed fact — Problem definition:** Small product teams lose decisions and action items when raw meeting notes are manually rewritten into shareable briefs.
- **User-confirmed fact — Target users:** Product leads and engineering managers in teams of 3-20 people.
- **User-confirmed fact — Use trigger scenarios:** After a planning, discovery, or retrospective meeting, a lead pastes sanitized notes and needs a brief in under two minutes.
- **User-confirmed fact — Current alternatives:** Manual templates, generic chat tools, and meeting-transcription suites.
- **User-confirmed fact — Most painful steps:** Separating decisions from discussion, assigning owners, and keeping a consistent brief format.
- **User-confirmed fact — Core value:** Convert pasted notes into a traceable structured brief without sending content to a hosted service.
- **User-confirmed fact — User success outcome:** A user reviews and exports a useful brief in less than two minutes with every generated claim linked to source text.
- **User-confirmed fact — Product shape:** Local-first single-user desktop-style web application.
- **User-confirmed fact — Primary user workflow:** Paste notes, parse locally, review extracted items with source spans, edit, and export Markdown.
- **User-confirmed fact — Inputs:** UTF-8 plain text or Markdown meeting notes up to 200 KB.
- **User-confirmed fact — Outputs:** Editable brief containing summary, decisions, action items, risks, open questions, and source references; Markdown export.
- **User-confirmed fact — Must-have features:** Paste/import notes, local extraction, source-span citations, review/edit screen, Markdown export, delete-all action.
- **User-confirmed fact — Optional features:** Reusable templates and JSON export after MVP.
- **User-confirmed fact — Explicit non-goals:** No recording, transcription, calendar bot, collaboration, cloud sync, or autonomous task assignment in MVP.
- **User-confirmed fact — User accounts:** No accounts; the MVP is single-user and local-only.
- **User-confirmed fact — Roles and permissions:** One local operator role; operating-system file permissions define access.
- **User-confirmed fact — Data sources:** Only user-pasted text or a user-selected local Markdown/text file.
- **User-confirmed fact — External integrations or none:** None in MVP.
- **User-confirmed fact — Privacy level and handling:** Meeting content remains on device and is deleted on explicit request; telemetry is disabled by default.
- **User-confirmed fact — Security level and controls:** No network calls in the processing path, strict file-type and size validation, output escaping, and dependency scanning.
- **User-confirmed fact — Compliance requirements or none:** No formal compliance target for MVP; the product must not claim compliance.
- **User-confirmed fact — Regions and languages:** English UI and English source notes for MVP; architecture must allow later localization.
- **User-confirmed fact — Performance requirements:** For a 50 KB note, first structured draft appears within 2 seconds on the reference laptop.
- **User-confirmed fact — Usability and accessibility:** Keyboard-operable review flow, visible focus, semantic labels, WCAG 2.2 AA color contrast.
- **User-confirmed fact — Expected scale:** One active user, one document at a time, up to 200 KB input, up to 500 saved briefs.
- **User-confirmed fact — Deployment boundary:** Packaged local application; development preview may use localhost only.
- **User-confirmed fact — Budget:** MVP must use open-source dependencies and incur no mandatory per-document service cost.
- **User-confirmed fact — Development team capability:** Two TypeScript developers and one product designer; no ML operations capacity.
- **User-confirmed fact — Time constraints:** A demonstrable MVP in four weeks.
- **User-confirmed fact — Operations and maintenance:** Local logs contain no note content; upgrades preserve saved briefs; backup and restore are documented.
- **User-confirmed fact — Business model:** Internal validation tool first; monetization is out of scope for MVP.
- **User-confirmed fact — Success metrics:** 80 percent of test users produce an accepted brief without help; median time under two minutes; zero network requests during processing.
- **User-confirmed fact — End-to-end acceptance criteria:** The golden note yields all expected sections and traceable source spans; edits persist; Markdown export matches the reviewed content; offline use passes.
- **User-confirmed fact — Edge cases:** Empty notes, unsupported encodings, duplicate action items, missing owners/dates, very long lines, and malicious Markdown/HTML.
- **User-confirmed fact — Failure handling:** Reject invalid input without data loss, show actionable errors, retain the previous reviewed draft, and never fabricate missing owners or dates.
- **User-confirmed fact — Example inputs and outputs:** Input: Example User will ship search Friday. Output action: Ship search; owner Example User; due Friday; source span preserved.
- **User-confirmed fact — Technical constraints:** TypeScript, deterministic rule-based extraction for MVP, local storage adapter, and no runtime network dependency.
- **User-confirmed fact — User-declared immutable constraints:** Local-only processing, explicit source traceability, no accounts, and no autonomous actions in MVP.

## Immutable constraints

- The files under `docs/core/` and their hash lock control this document.

## Ownership

- **AI recommendation:** Elaborate only within the frozen constraints.
- **Reversible default:** Prefer the simplest replaceable option until measured evidence requires more.
- **Unverified assumption:** None may be promoted to a fact without a ledger update and, when core-affecting, human change control.

## Public interfaces

- **AI recommendation:** Elaborate only within the frozen constraints.
- **Reversible default:** Prefer the simplest replaceable option until measured evidence requires more.
- **Unverified assumption:** None may be promoted to a fact without a ledger update and, when core-affecting, human change control.

## Forbidden coupling

- **AI recommendation:** Elaborate only within the frozen constraints.
- **Reversible default:** Prefer the simplest replaceable option until measured evidence requires more.
- **Unverified assumption:** None may be promoted to a fact without a ledger update and, when core-affecting, human change control.
