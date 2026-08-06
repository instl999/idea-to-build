#!/usr/bin/env python3
"""Inspect and update Idea-to-Build project state."""
import argparse, json, os, shlex, subprocess, sys
from pathlib import Path
from idea_to_build_lib import (BUILDABLE_DECISIONS, IdeaToBuildError, RESEARCH_DECISIONS, TEST_RECORD_RUNNER, confirm_core, git_snapshot, load_json, load_state, safe_project_path, save_state, validate_single_line, transition_state, update_requirements, utc_now, write_json)

def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status"); status.add_argument("--path", required=True)
    transition = sub.add_parser("transition"); transition.add_argument("--path", required=True); transition.add_argument("--phase", required=True); transition.add_argument("--reason")
    decision = sub.add_parser("set-decision"); decision.add_argument("--path", required=True); decision.add_argument("--research", choices=sorted(RESEARCH_DECISIONS)); decision.add_argument("--build", choices=sorted(BUILDABLE_DECISIONS))
    update = sub.add_parser("update-requirements"); update.add_argument("--path", required=True); update.add_argument("--input", required=True)
    confirmation = sub.add_parser("confirm-core"); confirmation.add_argument("--path", required=True); confirmation.add_argument("--confirmation", required=True)
    test = sub.add_parser("record-test"); test.add_argument("--path", required=True); test.add_argument("--test-command", required=True)
    args = parser.parse_args()
    if args.command == "status": result = load_state(args.path)
    elif args.command == "transition": result = transition_state(args.path, args.phase, args.reason)
    elif args.command == "set-decision":
        if not args.research and not args.build: raise IdeaToBuildError("Provide --research or --build")
        result = load_state(args.path)
        if args.research: result["research_decision"] = args.research
        if args.build: result["build_decision"] = args.build
        save_state(args.path, result)
    elif args.command == "update-requirements":
        payload = load_json(Path(args.input).expanduser().resolve()); updates = payload.get("updates")
        if not isinstance(updates, list): raise IdeaToBuildError("Input must contain an updates array")
        result = update_requirements(args.path, updates)
    elif args.command == "confirm-core": result = confirm_core(args.path, args.confirmation)
    else:
        root = Path(args.path).expanduser().resolve(); state = load_state(root)
        allowed = [validate_single_line("test command", value, 500) for value in state.get("test_commands", [])]
        if args.test_command not in allowed: raise IdeaToBuildError("Test command must exactly match a command declared in project_state.json")
        command = shlex.split(args.test_command, posix=os.name != "nt")
        if not command: raise IdeaToBuildError("Test command is empty")
        try: completed = subprocess.run(command, cwd=str(root), check=False)
        except OSError as exc: raise IdeaToBuildError("Cannot run declared test command: %s" % exc) from exc
        snapshot = git_snapshot(root)
        result = {"schema_version": 1, "project_id": state["project_id"], "runner": TEST_RECORD_RUNNER, "command": args.test_command, "status": "passed" if completed.returncode == 0 else "failed", "exit_code": completed.returncode, "recorded_at": utc_now(), "git": snapshot}
        write_json(safe_project_path(root, ".idea-to-build/last_test.json"), result)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)