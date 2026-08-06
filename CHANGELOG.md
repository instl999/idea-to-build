# Changelog

## 0.4.0 - 2026-08-06

- Added four-layer repository memory: mutable working rules/map, per-task SPEC/PLAN, canonical task ledger/projection, and explicit command/manual quality gates.
- Added task, quality, localized prompt, development-mode, bounded-context, task-aware Stop, and non-overwriting migration CLIs.
- Made guided sequential development the default while retaining canonical task-bound Codex subagent/worktree orchestration for advanced parallel work.
- Added an old-runtime compatibility loader, migration rollback, current-snapshot evidence, output bounds/redaction, path/ownership checks, and human-only acceptance enforcement.
- Updated the synthetic frozen example without changing its frozen core or lock; added bilingual repository-memory, architecture, privacy, security, change-control, contribution, and usage documentation.
- Expanded regression coverage for task readiness/state/dependencies, prompt recovery, quality safety/staleness/manual gates, Hook completion, modes, migration, and package integrity.

## 0.3.0 - 2026-08-05

- Added on-demand development orchestration: one effective workstream stays with the root agent, while independent workstreams receive scoped subagent prompts and dependency waves.
- Added a hash-bound Codex dispatch manifest and Codex-native adapter flow for clean worktree creation, result verification, and safe retirement.
- Narrowed the Skill to Codex: after the human freezes the product core, a user request to proceed activates native root-agent or subagent execution without polluting the immutable contract with a reversible orchestration choice.
- Added branch-tip, ancestry, non-empty diff, and file-ownership verification before child commits can be merged.
- Expanded English and Chinese architecture, privacy, security, change-control, usage, and compatibility documentation.
- Added a post-readiness MCP applicability gate, four explicit recommendations, existing-versus-custom server review guidance, and a generated MCP integration guide without adding a server or dependency to the Plugin.
- Hardened Stop evidence with project/runner/declared-command validation, protected Hook-visible record writes, and pass/block/forgery regression tests.
- Added generated-project ignore rules for local test/guardrail artifacts, environments, caches, and `.env*`, while preserving `.env.example`.
- Completed Plugin and generated-project required-file validation, synchronized the 0.3.0 project version, and added version/cachebuster regression coverage.

## 0.2.0 - 2026-08-05

- Hardened Hooks so they load only the installed runtime and derive freeze state from the core lock.
- Added link/junction-safe repository paths, exact Git-root checks, initialization preflight, and freeze rollback.
- Made the 38-item requirements schema fail closed and tightened research decisions and workstream inputs.
- Bound recorded tests to an actually executed command and the current Git/worktree snapshot.
- Added bilingual user, architecture, privacy, security, change-control, and contribution documentation.
- Added cross-platform CI and a tracked-content/Git-history release privacy audit.

## 0.1.0 - 2026-08-05

- Initial installable Codex plugin.
- Evidence-gated idea and solution research workflow.
- Persistent requirements state, readiness gates, core freeze, and SHA-256 verification.
- Codex lifecycle hooks for context loading and protected-file guardrails.
- Deterministic thread/worktree handoff generation and standard-library CLIs.
- Unit, integration, activation-boundary, hook, and end-to-end tests.