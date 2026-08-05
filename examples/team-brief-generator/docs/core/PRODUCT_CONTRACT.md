# Team Brief Generator - Product Contract

## Actors

- One local operator: a product lead or engineering manager.

## Primary workflow

1. Paste text or select a UTF-8 text/Markdown file up to 200 KB.
2. Generate a deterministic draft containing summary, decisions, actions, risks, and open questions.
3. Review each item beside its source span; edit or remove it.
4. Save locally or export the reviewed brief as Markdown.

## Must-have behavior

- No network request is made during processing.
- Missing owners or dates stay explicitly unknown; the product never invents them.
- Invalid input produces an actionable error without destroying the previous draft.
- Delete-all removes saved briefs after explicit confirmation.

## Acceptance

- The golden note produces all expected sections and source spans.
- Export matches the reviewed state byte-for-byte after newline normalization.
- Keyboard-only review and WCAG 2.2 AA contrast checks pass.
