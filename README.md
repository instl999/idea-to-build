# Idea-to-Build Codex Plugin

**English** | [简体中文](README.zh-CN.md)

Idea-to-Build is an installable Codex Plugin made of one Skill plus lifecycle Hooks (no MCP server). It researches existing solutions before detailed discovery, turns an approved digital-product idea into a strict 38-item requirements ledger, freezes five human-approved core contracts with SHA-256, and creates a bounded multi-task Codex handoff.

Version: `0.2.0`. The local runtime uses only Python 3.9+ standard-library modules and Git. It needs no plugin API key, third-party Python package, or plugin-operated network service. Live solution research still requires the host's Web Search and network access.

## What it does

The plugin implements a gated 16-phase workflow from `IDEA_RECEIVED` through research, requirements, core review/freeze, document generation, Codex handoff, development, release, and archive.

Its important guarantees are:

- Research direct products, composable alternatives, and reusable open-source/Skill/MCP/SDK/template options before deep requirements work.
- Return only one declared research decision: `ADOPT_DIRECTLY`, `ADOPT_WITH_CONFIGURATION`, `COMBINE_EXISTING_TOOLS`, `EXTEND_OPEN_SOURCE`, `BUILD_CUSTOM`, `INSUFFICIENT_RESEARCH`, or `NOT_RECOMMENDED`.
- Fail closed when live evidence is unavailable, conflicting, or contains no verifiable candidates.
- Require the exact 38-item ledger schema; missing IDs or altered gate metadata cannot bypass readiness.
- Block freeze while required facts, P0 conflicts, irreversible choices, privacy, security, deployment, or acceptance details remain unresolved.
- Require an explicit human terminal action for confirmation and freeze. An AI task must never approve, unlock, or refreeze the core.
- Verify frozen `docs/core/**` against `.idea-to-build/core.lock.json` and route later product changes through change control.
- Generate non-overlapping file ownership, dependencies, branches, worktrees, tests, and merge order for Codex tasks.

## Package layout

```text
idea-to-build/
├── .agents/plugins/marketplace.json     # repository-local marketplace
├── .codex-plugin/plugin.json            # plugin manifest
├── hooks/                               # lifecycle Hooks and trusted guardrail runtime loader
├── skills/idea-to-build/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   ├── assets/project-template/
│   └── scripts/
├── examples/team-brief-generator/       # frozen synthetic fixture
├── scripts/audit_public_release.py      # worktree and Git-history privacy audit
└── tests/
```

A generated project contains `AGENTS.md`, five core contracts, eight live documents, an ExecPlan directory, design scaffolds, Codex handoff prompts, state/requirements files, and project-local runtime scripts.

## Requirements

- Python 3.9 or newer (`py -3` may be used on Windows).
- Git available with a commit identity configured.
- A current Codex/ChatGPT host that supports Plugins and Hooks. Organization policy can disable either capability.
- Web Search only when performing live solution research.

## Install

Clone the repository:

```bash
git clone https://github.com/instl999/idea-to-build.git
cd idea-to-build
```

Register its repository-local marketplace and install the plugin:

```bash
codex plugin marketplace add .
codex plugin add idea-to-build@idea-to-build-local
codex plugin list --json
```

In Codex Desktop, restart if needed, open Plugins, and select the `Idea-to-Build Local` source. In a new task, run `/hooks`, verify the source is this plugin's `hooks/hooks.json`, review the commands and hashes, then trust and enable `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`.

To update:

```bash
git pull
codex plugin remove idea-to-build@idea-to-build-local
codex plugin add idea-to-build@idea-to-build-local
```

Review new Hook hashes and use a new task so the updated Skill context is loaded.

## Invoke

Explicit invocation is the most predictable:

```text
$idea-to-build I want a local-first tool that turns meeting notes into traceable team briefs. Research current alternatives first; if continuing is justified, turn it into an implementable and testable Codex project.
```

The Skill may also activate implicitly for a digital product/software idea when the user asks to validate, research, clarify requirements, or prepare Codex development. It should not activate for a narrow bug fix, code explanation, already-scoped small feature, generic software recommendation, casual brainstorming without validation/build intent, or a non-digital product.

## Workflow

### 1. Initialize a generated project

```bash
python skills/idea-to-build/scripts/init_project.py --path ../my-product --name "My Product"
cd ../my-product
python scripts/project_state.py status --path .
```

Initialization preflights every output before writing, refuses links/junctions and existing files unless `--force` is explicit, initializes an exact project Git root, and normally creates the skeleton commit. `--skip-initial-commit` is intended for CI/fixtures.

### 2. Research and record a build decision

Use live Web Search across all three solution layers. Minimize and pseudonymize query data; do not send secrets, personal records, or proprietary text. Save dated official sources, evidence, inferences, conflicts, and stale/unverified fields, then run:

```bash
python scripts/research_report.py --path . --input research-input.json
python scripts/project_state.py set-decision --path . --build BUILD_CUSTOM
```

No network, conflicting evidence, or an empty candidate set produces `INSUFFICIENT_RESEARCH`; “not found” is never presented as proof of a market opportunity.

### 3. Complete requirements and readiness

```bash
python scripts/project_state.py update-requirements --path . --input requirements-updates.json
python scripts/requirements_check.py --path . --update-state
```

The ledger loader requires all 38 stable IDs and their code-defined category, priority, reversibility, and readiness metadata. A confirmed item must carry a value.

### 4. Human confirmation and freeze

Have Codex draft and present the five core contracts. After reviewing them, leave the AI tool-call flow and run these yourself in a terminal:

```bash
python scripts/project_state.py confirm-core --path . --confirmation "I confirm and freeze this core baseline"
python scripts/freeze_core.py --path . --tag core-v1
```

Freeze requires the project directory to be the exact Git top-level, creates normalized per-file and aggregate SHA-256 hashes, writes the lock and state, applies read-only bits as a secondary guardrail, and commits the baseline. Failures before commit restore state, lock, permissions, and managed staging. A tag failure after a successful commit is reported as partial success and requires human handling.

### 5. Generate the Codex handoff

```bash
python scripts/generate_handoff.py --path . --workstreams workstreams.json
python scripts/render_context.py --path .
python scripts/verify_core.py --path .
```

Workstream names, goals, dependencies, tests, and paths must be bounded single-line data. Ownership must be repository-relative and cannot include the repository root, `.git`, `.codex`, `.idea-to-build`, Hooks, core files, or protection scripts. Shared foundation files such as package manifests, lockfiles, configuration, and public interfaces need an explicit owner.

Generated design documents are review-required working scaffolds, not completed specifications.

### 6. Record a real test result

Declare exact commands in `project_state.json` under `test_commands`, then run one of them through the recorder:

```bash
python scripts/project_state.py record-test --path . --test-command "python -m unittest discover -s tests -v"
```

The recorder executes the command without a shell, derives pass/fail from its exit code, and binds the result to the current Git HEAD and worktree digest. The Stop Hook rejects a stale or self-declared result.

## Hook behavior and boundary

| Event | Behavior |
| --- | --- |
| `SessionStart` | Finds a generated project, verifies a frozen core, and injects bounded core/live context. |
| `UserPromptSubmit` | Re-verifies and injects phase-specific draft or frozen rules. |
| `PreToolUse` | Blocks direct protected-path edits, human-only commands, path traversal, and opaque Git mutations while frozen. |
| `PostToolUse` | Recomputes hashes after tool calls and stops on drift. |
| `Stop` | During development phases, requires valid core, current real test evidence, and a STATUS update. |

Hooks are defense in depth, not an operating-system sandbox and not a cryptographic human-identity mechanism. A process, external editor, indirect program, unsupported tool event, or user with filesystem rights can bypass prevention. Hash verification, exact Git history, review, and human process remain authoritative. Never rely on Hooks alone to protect sensitive data or frozen contracts.

## Test and validate

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests scripts
python skills/idea-to-build/scripts/validate_package.py --path .
python examples/team-brief-generator/scripts/verify_core.py --path examples/team-brief-generator
python scripts/audit_public_release.py --worktree-only
```

The current suite contains 65 unit/integration scenarios covering activation boundaries, schema/state handling, research decisions, exact requirements gates, confirmation/freeze/hash behavior, Hooks, path and prompt hardening, task planning, package validation, and end-to-end generation. CI runs the suite on Linux, Windows, and macOS with Python 3.9 and 3.13.

Before a public push, run `python scripts/audit_public_release.py` after sanitizing commit metadata. The audit examines tracked text, symbolic links, common secret/private-path patterns, email addresses, and author/committer emails across all refs. It is an additional heuristic control, not a substitute for repository-host secret scanning.

The example under `examples/team-brief-generator` is entirely synthetic: names, approval metadata, timestamps, decisions, candidate data, and requirements are fixtures, not real market evidence or a claim that a human approved a real product.

## Compatibility

- Codex Desktop/CLI are the recommended end-to-end surfaces because they can access local projects, Git, Hooks, and worktrees.
- ChatGPT Work may use the Skill for research and discovery, but a managed web environment must not be assumed to access local Git, permissions, or Hooks.
- Availability depends on host version, rollout, plan, workspace policy, and Hook trust.

## Uninstall

```bash
codex plugin remove idea-to-build@idea-to-build-local
codex plugin marketplace remove idea-to-build-local
codex plugin list --json
```

Generated projects are not deleted.

## Troubleshooting

- Plugin missing: inspect `codex plugin marketplace list --json`, confirm the local marketplace, and restart the host.
- Skill not invoked: start a new task and use `$idea-to-build` explicitly.
- Hook skipped: use `/hooks`, review/trust the current hash, and confirm Hooks are enabled by policy/configuration.
- Research remains insufficient: enable Web Search or provide current, dated official evidence; never edit the conclusion optimistically.
- Readiness fails: inspect the JSON blockers and resolve missing/altered requirements, P0 conflicts, irreversible assumptions, and the build decision.
- Freeze fails: confirm exact Git root, identity, clean managed staging, readiness, and exact human confirmation.
- Core verification fails: stop, preserve evidence, and file a change request; never update hashes to hide drift.
- Stop repeats: record an allowed real test command after the latest changes and update `docs/live/STATUS.md`.

## Further documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Privacy and data handling](docs/PRIVACY.md)
- [Frozen-core change control](docs/CHANGE_CONTROL.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## License

MIT. See [LICENSE](LICENSE).