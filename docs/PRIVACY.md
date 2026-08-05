# Privacy and Data Handling

**English** | [简体中文](PRIVACY.zh-CN.md)

## Data processed

The plugin can process product ideas, research queries/results, requirements, assumptions, core/design/live documents, generated prompts, local paths relative to a project, Git metadata, test commands/results, and guardrail messages. It does not require an account, API key, remote plugin backend, or telemetry.

Most processing is local. Live research uses the host's Web Search, so query text and normal provider metadata may be processed outside the repository under the host/provider policies. GitHub receives anything you publish.

## Rules before input or search

- Do not paste secrets, credentials, private keys, `.env` contents, health/financial/government identifiers, raw customer records, or confidential source text.
- Minimize queries to the smallest facts needed. Replace names, emails, organizations, repository names, domains, and exact numbers with stable pseudonyms when identity is unnecessary.
- Obtain authorization before processing data belonging to another person or organization.
- Prefer aggregate/example data and official public sources. Record only the evidence needed for the decision.
- Review generated prompts: requirements embedded in them may be repeated across tasks.

## Subagent prompt minimization

Before generating or sending a child-agent prompt, include only the frozen constraints and scoped context needed for that workstream. Do not duplicate raw research transcripts, credentials, personal records, proprietary source excerpts, or unrelated organization details. Subagent/worktree execution uses the host and local Git permissions; any remote model processing follows the host's data policy, not a separate plugin backend.

## Storage and retention

Generated projects store data as ordinary local UTF-8/JSON/Markdown files and Git history. `.idea-to-build/guardrail.log` and `last_test.json` are ignored by this repository template but may remain locally. Deleting working files does not remove them from Git history, backups, worktrees, remote forks, Web Search provider logs, or already shared prompts.

Choose retention and access controls appropriate to the data. Use repository permissions, encrypted storage where required, short-lived worktrees, and secure deletion/rotation procedures managed by your organization. Never use core hashing as encryption or confidentiality.

## Public-release desensitization

Use synthetic fixtures. Inspect the complete Git history, not only the current tree. Configure a no-reply commit email, remove private paths and personal addresses, rotate any exposed credential instead of merely deleting it, and run:

```bash
python scripts/audit_public_release.py
```

The audit is heuristic. Also enable host secret scanning/push protection and conduct human review. If sensitive data reaches GitHub, revoke/rotate it immediately, follow the host removal procedure for Git objects/caches/forks, and notify affected parties according to policy/law.