# Frozen-Core Change Control

**English** | [简体中文](CHANGE_CONTROL.zh-CN.md)

## Principle

A frozen core is immutable in normal development. Version 0.3.0 intentionally has no unlock, rehash, or in-place refreeze command. Hooks, Skills, and AI tasks must not edit the lock/core or manufacture human approval. Updating a hash to match an unexplained change destroys the evidence and is never an acceptable repair.

Root-agent versus subagent execution is a reversible Codex development choice and is deliberately excluded from the frozen product lock. Switching execution strategy does not require a core change while ownership, acceptance, architecture, privacy, security, and deployment contracts remain unchanged.

## Non-core changes

Implementation details that remain within the contracts belong in design/live documents and code. Record decisions and risks, run the frozen-core verifier, execute required tests, update STATUS, and commit normally.

## Core-affecting request

1. Stop implementation that depends on the disputed contract.
2. Record the proposal in `docs/live/CHANGE_REQUESTS.md`: requester, date, reason, affected requirements/core files, privacy/security/deployment impact, migration/rollback, alternatives, and acceptance changes.
3. Preserve evidence: current core hash, tag/commit, working-tree status, verifier output, and relevant decisions. Do not edit the frozen files.
4. Obtain explicit product/security/technical review. Reject changes that only lower acceptance to hide a failure.
5. For an approved new baseline, create a fresh generated project or separately initialized exact Git repository/branch under human control. Copy only reviewed mutable facts/decisions, draft a new set of five core contracts, and rerun the complete research/readiness process.
6. A human reviews the full new preview and runs the exact confirmation and freeze commands. Keep the old baseline/tag available for rollback/audit.
7. Migrate implementation through a reviewed plan; verify both old and new references, tests, data migration, rollback, and release notes.

Do not silently replace the old lock in the original frozen project. If organizational policy requires in-place baselines, build and audit a dedicated human-authorized migration tool before use; this release does not provide one.

## Emergency integrity failure

If verification fails without an approved request, treat it as potential corruption: stop, preserve copies/logs/Git status, identify the writer and scope, rotate any possibly exposed credential, restore from a known good commit in a recovery branch, and investigate. Never “fix” the incident by recomputing hashes over unknown content.