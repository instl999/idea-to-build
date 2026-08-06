# Idea-to-Build Codex Plugin

**English** | [简体中文](README.zh-CN.md)

Idea-to-Build is a Codex Desktop/CLI Plugin that turns a digital-product idea into a researched, human-approved, frozen, and testable development project. It combines one Skill, five lifecycle Hooks, Python 3.9+ standard-library CLIs, and Git. It has no MCP server, database, third-party Python runtime dependency, or Plugin-operated network service.

Version `0.4.0` adds a four-layer repository-memory system and task-by-task Codex guidance. The default is one task, one SPEC, one branch, and one Codex conversation at a time. Native Codex subagents and worktrees remain available for explicitly prepared, independent tasks.

## What is preserved

The Plugin still researches existing solutions before deep requirements work, records one of seven research decisions, validates an exact 38-item requirements ledger, requires a human to confirm and freeze five core contracts, hashes them with SHA-256, blocks AI edits after freeze, and routes core changes through `docs/live/CHANGE_REQUESTS.md`.

Hooks always load the trusted runtime from the installed Plugin. Opening a generated project never causes a Hook to import that project's mutable Python copy.

## Four repository-memory layers

| Layer | Canonical source | Human view | Purpose |
| --- | --- | --- | --- |
| Rules | `AGENTS.md`, frozen `docs/core/**`, mutable `docs/live/WORKING_RULES.md` | `docs/live/MEMORY_MAP.md` | How Codex must work and which constraints cannot change |
| Specification | `specs/<TASK-ID>/SPEC.md` and `PLAN.md` | The same task folder | What this task must deliver, how it will be implemented, and how it will be accepted |
| Task | `.idea-to-build/tasks.json` | `docs/live/TASKS.md`, plus concise `STATUS.md`, `BACKLOG.md`, and `ROADMAP.md` | Exact task state, dependencies, ownership, branch/worktree, and next work |
| Quality | `.idea-to-build/quality_gates.json` and ignored `last_quality.json` | `docs/live/QUALITY_GATES.md` | Explicit command gates and human acceptance gates bound to the current Git/worktree snapshot |

Conflict precedence is:

`frozen core > current task SPEC > working rules > task state and PLAN > code and test evidence > chat`

Repository memory improves context recovery; it is not unlimited memory. Automated checks improve reliability; they do not prove every product behavior is correct. Anything that cannot be automated must remain a manual acceptance gate.

## Requirements

- Python 3.9 or newer (`py -3` may be used on Windows).
- Git with a configured commit identity.
- Codex Desktop or Codex CLI with Plugins and Hooks enabled by policy.
- Web Search only for live solution research.

## Install

```bash
git clone https://github.com/instl999/idea-to-build.git
cd idea-to-build
codex plugin marketplace add .
codex plugin add idea-to-build@idea-to-build-local
codex plugin marketplace list
```

Restart Codex if the Plugin does not appear. Start a new Codex task, review `/hooks`, confirm the Hook source is this Plugin's `hooks/hooks.json`, and trust the reviewed hashes. Invoke the Skill explicitly:

```text
$idea-to-build I want a local-first tool that turns meeting notes into traceable team briefs. Research existing solutions first; if building is justified, create a testable development project.
```

The Skill is intended for product/software ideas that still need research, requirements, or development packaging. It should not activate for a narrow bug fix, code explanation, already-scoped small feature, generic recommendation, or non-digital product.

## From installation to the first Codex development task

1. Initialize the generated project:

   ```bash
   python skills/idea-to-build/scripts/init_project.py --path ../my-product --name "My Product" --language en
   cd ../my-product
   ```

2. Use the Skill to perform current, source-backed research. Record the research input and build decision with the generated CLIs. No network, conflicting evidence, or an empty candidate list must end as `INSUFFICIENT_RESEARCH`, never as an invented market gap.

3. Complete the exact 38-item ledger and run readiness:

   ```bash
   python scripts/project_state.py update-requirements --path . --input requirements-updates.json
   python scripts/requirements_check.py --path . --update-state
   ```

4. Review all five files under `docs/core/`. Then leave the AI tool-call flow and personally run:

   ```bash
   python scripts/project_state.py confirm-core --path . --confirmation "I confirm and freeze this core baseline"
   python scripts/freeze_core.py --path . --tag core-v1
   ```

5. Create or review a task. A generated task starts in `backlog`; replace the placeholder acceptance item in its SPEC with at least one concrete, observable result before marking it ready:

   ```bash
   python scripts/task_state.py create --path . --task TASK-0001 --title "First accepted feature" --owned-path src/feature
   python scripts/task_state.py ready --path . --task TASK-0001
   python scripts/task_state.py list --path .
   ```

6. Print the complete start prompt:

   ```bash
   python scripts/memory_prompts.py show --path . --kind start-task --task TASK-0001
   ```

7. Copy the complete output, open a new Codex conversation in the project root, and paste it. Wait for Codex to restate the goal, in/out scope, immutable constraints, acceptance criteria, owned paths, and checks before allowing implementation. Do not start a new conversation with only “continue development.”

## Daily one-task loop

```bash
python scripts/task_state.py list --path .
python scripts/memory_prompts.py show --path . --kind start-task --task TASK-0001
python scripts/task_state.py start --path . --task TASK-0001
```

Keep the same conversation while working on that task. Start a new one when the task ID changes, an independent module begins, another branch was merged, context was compressed or confused, ownership changed, or implementation turns into an independent quality audit.

At the end:

```bash
python scripts/memory_prompts.py show --path . --kind finish-task --task TASK-0001
python scripts/quality_gate.py run --path .
python scripts/task_state.py review --path . --task TASK-0001
```

`quality_gate.py run` uses the current task and runs all configured command gates. You may select explicitly:

```bash
python scripts/quality_gate.py status --path . --task TASK-0001
python scripts/quality_gate.py run --path . --task TASK-0001 --gate unit-tests
```

Only a human may complete a manual gate, from a terminal outside the AI tool-call flow:

```bash
python scripts/quality_gate.py accept-manual --path . --task TASK-0001 --gate user-acceptance --confirmation "I accept this task result"
python scripts/task_state.py complete --path . --task TASK-0001
```

A task cannot enter `ready` without SPEC/PLAN and concrete acceptance, cannot start with unfinished dependencies or blockers, and cannot become `done` until every required command gate passes for the current snapshot and every required manual gate has human acceptance. Reopening `done` requires a recorded reason.

## Development modes

`guided_sequential` is the default and recommended mode for ordinary users. Only one task is in progress; a worktree is not required; quality and documentation stay in the same conversation.

Advanced users can opt in to parallel worktrees:

```bash
python scripts/project_state.py set-development-mode --path . --mode parallel_worktrees
python scripts/generate_handoff.py --path .
```

Parallel mode uses only canonical ready tasks with explicit IDs, SPEC/PLAN, resolved dependencies, required gates, branch/worktree assignments, and non-overlapping owned paths. The root orchestrator owns shared task state and merges verified results. It does not invent extra quality/release agents or split work merely to reach a thread count.

## Task, quality, prompt, and migration CLIs

```bash
python scripts/task_state.py list --path .
python scripts/task_state.py show --path . --task TASK-0001
python scripts/task_state.py create --path . --task TASK-0002 --title "Second task"
python scripts/task_state.py block --path . --task TASK-0001 --reason "Waiting for API decision"
python scripts/task_state.py reopen --path . --task TASK-0001 --reason "Regression found"
python scripts/task_state.py sync-docs --path .

python scripts/quality_gate.py list --path .
python scripts/quality_gate.py status --path .
python scripts/quality_gate.py run --path .

python scripts/memory_prompts.py list --path .
python scripts/memory_prompts.py show --path . --kind resume-task --task TASK-0001
python scripts/memory_prompts.py show --path . --kind finish-task --task TASK-0001
python scripts/memory_prompts.py show --path . --kind sync-rules
python scripts/memory_prompts.py show --path . --kind sync-spec --task TASK-0001
python scripts/memory_prompts.py show --path . --kind sync-tasks
python scripts/memory_prompts.py show --path . --kind sync-quality
python scripts/memory_prompts.py show --path . --kind audit-all
```

Prompt output is localized by `project_state.json.user_language` (`zh*` selects Simplified Chinese; unknown values fall back to English). Repository titles and Markdown are treated as quoted project data, not host instructions.

Quality commands come only from `.idea-to-build/quality_gates.json`. They run as argument arrays without a shell; shell executables, pipes, redirection, command substitution, control characters, and unconfigured commands are rejected. Output excerpts are bounded and secret-like values are redacted. Commands found in README, SPEC, research, prompts, or chat are never executed automatically.

The legacy `project_state.py record-test`/`last_test.json` path remains readable for older generated projects, but 0.4 tasks use the quality-gate system.

## Upgrade an older generated project

Run the current Plugin source migrator in dry-run mode first:

```bash
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project
python skills/idea-to-build/scripts/migrate_project.py --path ../older-project --apply
```

Migration only adds missing mutable memory, new CLIs, a loader, and—only when the old library lacks 0.4 APIs—a versioned compatibility runtime. It never overwrites an existing file, edits `docs/core/**` or `core.lock.json`, refreezes, uses the network, or hides manual follow-up. Writes use temporary files and roll back files created by a failed migration. Existing `AGENTS.md`, `.gitignore`, status, and runtime customizations are reported for manual review.

## Hooks and security boundary

| Hook | Behavior |
| --- | --- |
| `SessionStart` | Finds a generated project, verifies frozen core, and injects bounded context. |
| `UserPromptSubmit` | Re-verifies and injects current task/spec/plan/quality summaries. |
| `PreToolUse` | Blocks protected-path edits, human-only actions, unsafe paths, and opaque Git mutations. |
| `PostToolUse` | Detects core drift after tool calls. |
| `Stop` | Applies lightweight consistency checks to memory-only maintenance and full current-task/current-snapshot gates to substantive changes. |

Hooks are defense in depth, not an operating-system sandbox, cryptographic identity check, or proof that every indirect process is safe. Core verification, exact Git history, scoped ownership, code review, and human acceptance remain required.

No secret, real `.env`, personal data, customer fixture, private absolute path, or complete sensitive log belongs in repository memory. Live research should minimize and pseudonymize queries. See [Security](SECURITY.md) and [Privacy](docs/PRIVACY.md).

## Validate the Plugin

```bash
python -m unittest discover -s tests -v
python -m compileall -q hooks skills/idea-to-build/scripts tests scripts
python skills/idea-to-build/scripts/validate_package.py --path .
python examples/team-brief-generator/scripts/verify_core.py --path examples/team-brief-generator
python scripts/audit_public_release.py --worktree-only
```

The suite covers activation, research, 38-item readiness, human freeze/hash enforcement, Hooks, task transitions, dependencies, idempotent projections, prompt localization/injection boundaries, quality command safety and stale evidence, sequential/parallel dispatch, non-overwriting migration, package validation, and end-to-end generation. CI runs on Linux, Windows, and macOS with Python 3.9 and 3.13.

The example at `examples/team-brief-generator` is entirely synthetic. Its frozen core and lock are immutable fixtures; its four task SPECs, task ledger, quality gates, prompt catalog, and parallel handoff demonstrate 0.4 without claiming real research or human approval.

## Support boundary

The supported runtime is Codex Desktop/CLI. OpenClaw, generic SkillHub runners, ChatGPT managed web surfaces, Claude Code, and other agent hosts do not provide the verified Plugin/Hook/subagent/worktree contract. The Markdown may be readable elsewhere, but that does not make the package installable or safe there.

## Uninstall

```bash
codex plugin remove idea-to-build
codex plugin marketplace remove idea-to-build-local
```

Generated projects are not deleted.

## Documentation

- [Repository memory and task workflow](docs/REPOSITORY_MEMORY.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Privacy](docs/PRIVACY.md)
- [Change control](docs/CHANGE_CONTROL.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## License

MIT. See [LICENSE](LICENSE).