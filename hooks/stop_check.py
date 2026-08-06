#!/usr/bin/env python3
"""Stop: enforce task-aware completion checks for substantive development work."""
import json
from _hooklib import block_payload, emit, find_root, git_changes, handle_error, load_runtime, read_event

MAINTENANCE_PREFIXES = ("docs/live/", "specs/", "codex/prompts/", "codex/README.md", "codex/PROMPT_CATALOG.md")
MAINTENANCE_EXACT = {".idea-to-build/tasks.json", ".idea-to-build/quality_gates.json", ".idea-to-build/project_state.json"}
TRANSIENT = {".idea-to-build/last_test.json", ".idea-to-build/last_quality.json", ".idea-to-build/guardrail.log"}

def _paths(changes):
    result = []
    for line in changes:
        raw = line[3:] if len(line) > 3 else line
        if " -> " in raw: raw = raw.split(" -> ", 1)[1]
        result.append(raw.strip('"').replace("\\", "/"))
    return result

def _legacy_issues(runtime, root, state, paths):
    issues = []
    record = runtime.safe_project_path(root, ".idea-to-build/last_test.json")
    if not record.is_file(): issues.append("No test result is recorded (legacy compatibility path)")
    else:
        try:
            payload = json.loads(record.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or payload.get("schema_version") != 1: issues.append("The legacy test record is invalid")
            elif payload.get("project_id") != state.get("project_id"): issues.append("The test result belongs to a different project")
            elif payload.get("runner") != runtime.TEST_RECORD_RUNNER: issues.append("The legacy test record runner is invalid")
            elif payload.get("command") not in state.get("test_commands", []): issues.append("The legacy test command is no longer declared")
            elif payload.get("status") != "passed" or payload.get("exit_code") != 0: issues.append("The legacy test did not pass")
            elif payload.get("git") != runtime.git_snapshot(root): issues.append("The legacy passing test is stale")
        except (OSError, json.JSONDecodeError): issues.append("The legacy test result is unreadable")
    if "docs/live/STATUS.md" not in paths: issues.append("docs/live/STATUS.md is not updated")
    return issues

def main():
    event = read_event(); root = find_root(event.get("cwd"))
    if root is None or event.get("stop_hook_active"): return
    try:
        runtime = load_runtime(root); state = runtime.load_state(root)
        lock_path = runtime.safe_project_path(root, ".idea-to-build/core.lock.json")
        if lock_path.is_file():
            verification = runtime.verify_core(root)
            if not verification["ok"]: emit(block_payload("Stop", "; ".join(verification["mismatches"]))); return
        if state.get("current_phase") not in ("CODEX_HANDOFF_READY", "DEVELOPMENT_ACTIVE", "RELEASE_READY", "CHANGE_REQUESTED"): return
        changes = git_changes(root)
        if changes is None: emit(block_payload("Stop", "Git status failed; completion cannot be verified")); return
        paths = [path for path in _paths(changes) if path not in TRANSIENT]
        if not paths: return
        memory_only = all(path in MAINTENANCE_EXACT or path.startswith(MAINTENANCE_PREFIXES) for path in paths)
        try:
            runtime.load_tasks(root); runtime.load_quality_gates(root)
        except runtime.IdeaToBuildError:
            issues = _legacy_issues(runtime, root, state, paths)
            if issues: emit({"decision": "block", "reason": "Idea-to-Build legacy completion check: " + "; ".join(issues)})
            else: emit({"continue": True, "systemMessage": "Legacy test evidence passed. Repository-memory migration is recommended: run the current installed Plugin migrator in dry-run mode."})
            return
        if memory_only:
            emit({"continue": True, "systemMessage": "Idea-to-Build memory-maintenance check passed: task and quality configuration are internally valid; no full code-test gate was required."}); return
        issues = []; task_id = state.get("current_task_id")
        if not task_id: issues.append("Substantive changes require an explicit current_task_id")
        else:
            try:
                task = runtime.get_task(root, task_id)
                if not runtime.task_acceptance_items(root, task): issues.append("The current task SPEC has no concrete acceptance criterion")
                if task["status"] not in ("review", "done"): issues.append("The current task status must honestly be review or done before stopping")
                if task["plan_path"] not in paths: issues.append("The current task PLAN is not updated")
                status = runtime.quality_status(root, task_id); record = status.get("record", {}); results = record.get("results", {}) if isinstance(record, dict) else {}; gates = {gate["id"]: gate for gate in runtime.load_quality_gates(root)["gates"]}
                if record.get("git") != runtime.git_snapshot(root): issues.append("The quality result is stale for the current Git/worktree snapshot")
                for gate_id in task["required_quality_gates"]:
                    gate = gates.get(gate_id); result = results.get(gate_id)
                    if not gate or not gate.get("configured"): issues.append("Required quality gate is not configured: %s" % gate_id)
                    elif gate["kind"] == "command" and (not isinstance(result, dict) or result.get("status") != "passed"): issues.append("Required command quality gate has not passed: %s" % gate_id)
                    elif gate["kind"] == "manual" and (not isinstance(result, dict) or result.get("status") != "passed" or result.get("actor") != "human") and task["status"] == "done": issues.append("A done task requires human manual acceptance: %s" % gate_id)
                if task["status"] == "done" and not status.get("ok"): issues.extend(status.get("issues", []))
            except runtime.IdeaToBuildError as exc: issues.append(str(exc))
        if "docs/live/STATUS.md" not in paths: issues.append("docs/live/STATUS.md is not updated for substantive changes")
        if issues: emit({"decision": "block", "reason": "Idea-to-Build task completion check: " + "; ".join(dict.fromkeys(issues))})
        else: emit({"continue": True, "systemMessage": "Idea-to-Build task check passed. Report acceptance, quality results, manual gates, task status, commit state, and remaining risks accurately."})
    except Exception as exc:
        payload = handle_error("Stop", root, exc)
        if payload: emit(payload)

if __name__ == "__main__": main()
