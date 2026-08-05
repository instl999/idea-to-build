#!/usr/bin/env python3
"""Inspect and update Idea-to-Build project state."""
import argparse, json, sys
from pathlib import Path
from idea_to_build_lib import (BUILDABLE_DECISIONS, IdeaToBuildError, RESEARCH_DECISIONS, confirm_core, load_json, load_state, save_state, transition_state, update_requirements, utc_now, write_json)

def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status"); status.add_argument("--path", required=True)
    transition = sub.add_parser("transition"); transition.add_argument("--path", required=True); transition.add_argument("--phase", required=True); transition.add_argument("--reason")
    decision = sub.add_parser("set-decision"); decision.add_argument("--path", required=True); decision.add_argument("--research", choices=sorted(RESEARCH_DECISIONS)); decision.add_argument("--build", choices=sorted(BUILDABLE_DECISIONS))
    update = sub.add_parser("update-requirements"); update.add_argument("--path", required=True); update.add_argument("--input", required=True)
    confirmation = sub.add_parser("confirm-core"); confirmation.add_argument("--path", required=True); confirmation.add_argument("--confirmation", required=True)
    test = sub.add_parser("record-test"); test.add_argument("--path", required=True); test.add_argument("--test-command", required=True); test.add_argument("--status", choices=("passed", "failed"), required=True)
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
        result = {"schema_version": 1, "command": args.test_command, "status": args.status, "recorded_at": utc_now()}
        write_json(Path(args.path).expanduser().resolve() / ".idea-to-build" / "last_test.json", result)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)