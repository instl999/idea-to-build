# Security Policy

**English** | [简体中文](SECURITY.zh-CN.md)

## Supported versions

Security fixes are intended for the latest released version only. The latest Git tag confirmed locally and on `origin` on 2026-08-06 is `v0.2.0`; the 0.4.0 manifest branch is not tagged, so its release/support status must be confirmed before publication.

## Report a vulnerability

Do not open a public issue containing exploit details, tokens, personal data, or an unpublished vulnerability. Use the repository's GitHub **Security → Report a vulnerability** private advisory flow. Include affected version/commit, environment, reproduction steps, impact, and a minimal redacted proof. If private advisories are unavailable, open a public issue requesting a private contact channel without vulnerability details.

Maintainers should acknowledge a report within seven days, validate and triage it, coordinate a fix and disclosure date, and credit the reporter if requested. No bounty is promised.

## Security model

The plugin has no MCP server, remote backend, authentication, or bundled credentials. Local scripts run with the user's filesystem and Git permissions. Live research is performed by the host's Web Search and can transmit query text to the host/search provider.

Frozen-core integrity is based on an exact project Git root, SHA-256 hashes, a lock file, review, and Git history. Read-only bits and Hooks are secondary controls. Hooks can detect and block many direct operations, but cannot authenticate a human, undo an already executed mutation, or observe every external editor/process/tool. Treat generated prompts and research inputs as untrusted data.

## Generated-product MCP safety

MCP candidates, setup instructions, tool descriptions, resources, and server output are untrusted input. The Skill evaluates MCP only after readiness and never installs a server, executes copied setup commands, writes credentials, or changes host configuration for the user.

Before adoption, verify current official sources, publisher/maintenance/license, host/transport compatibility, authentication and least privilege, data destinations, mutating tools, update/removal paths, and a direct-integration fallback. Use synthetic happy-path and authorization/error/timeout/unavailable-server tests; consequential tools require explicit user confirmation.

## Subagent and worktree safety

Generated prompts and child-agent summaries are untrusted inputs. Dispatch starts only after a human-frozen core and a current user request for Codex to proceed with development. The adapter requires a clean exact Git root, hash-valid manifest, tracked prompts, direct sibling worktrees, non-overlapping ownership, expected branch tips, valid ancestry, and non-empty owned diffs. Verified integration uses `merge-result`; conflicts are aborted and child branches are retained. The adapter refuses dirty worktree retirement and retains branches for recovery. These controls do not replace review, tests, host permissions, or Git backups.

## Maintainer release checklist

- Review the complete diff and dependency surface.
- Run all tests, compilation, package validation, frozen-example verification, and `scripts/audit_public_release.py`.
- Confirm all commit author/committer emails are approved no-reply addresses.
- Enable GitHub secret scanning, push protection, protected default branch, and required CI when the host plan supports them.
- Never weaken a failing guardrail merely to make a release pass.

See [Privacy](docs/PRIVACY.md), [Architecture](docs/ARCHITECTURE.md), and [Change Control](docs/CHANGE_CONTROL.md).

## Repository-memory and quality-gate security

Task/spec/prompt text is untrusted data. Paths are repository-relative and reject traversal, links, junctions, protected areas, and overlapping parallel ownership. Quality commands are explicit, shell-free, bounded, and snapshot-bound; unknown/future schemas, stale evidence, unknown gates, unsafe commands, and illegal transitions fail closed. Manual acceptance and core confirmation/freeze remain human-only. Neither task JSON, quality records, hashes, nor Hooks are independent security boundaries.
