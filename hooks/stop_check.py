#!/usr/bin/env python3
"""Stop: enforce completion checks only for substantive development work."""
import json
from pathlib import Path
from _hooklib import block_payload, emit, find_root, git_changes, handle_error, load_runtime, read_event

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
        if not changes: return
        issues = []
        record = runtime.safe_project_path(root, ".idea-to-build/last_test.json")
        if not record.is_file(): issues.append("No test result is recorded; run the project tests and record the result")
        else:
            try:
                payload = json.loads(record.read_text(encoding="utf-8"))
                if payload.get("status") != "passed" or payload.get("exit_code") != 0: issues.append("The latest recorded test result is not passing")
                elif payload.get("git") != runtime.git_snapshot(root): issues.append("The passing test record is stale for the current Git/worktree snapshot")
            except (OSError, json.JSONDecodeError): issues.append("The recorded test result is unreadable")
        normalized = [line[3:].replace("\\", "/") if len(line) > 3 else line for line in changes]
        if "docs/live/STATUS.md" not in normalized: issues.append("docs/live/STATUS.md is not updated for the substantive changes")
        if issues: emit({"decision": "block", "reason": "Idea-to-Build completion check: " + "; ".join(issues)})
        else: emit({"continue": True, "systemMessage": "Idea-to-Build check passed. Review decisions, risks, architecture drift, ExecPlan status, and whether stable changes should be committed before finalizing."})
    except Exception as exc:
        payload = handle_error("Stop", root, exc)
        if payload: emit(payload)
if __name__ == "__main__": main()