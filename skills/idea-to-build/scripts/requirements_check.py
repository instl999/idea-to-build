#!/usr/bin/env python3
"""Evaluate requirements readiness using explicit gates."""
import argparse, json, sys
from idea_to_build_lib import IdeaToBuildError, check_readiness, load_state, save_state

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--path", required=True); parser.add_argument("--update-state", action="store_true"); args = parser.parse_args()
    result = check_readiness(args.path)
    if args.update_state:
        state = load_state(args.path); state["requirements_readiness"] = result["status"]
        state["current_phase"] = "REQUIREMENTS_READY" if result["ready"] else ("REQUIREMENTS_CONFLICT" if any("conflict" in item.lower() for item in result["blockers"]) else "REQUIREMENTS_GATHERING")
        state["unresolved_questions"] = result["blockers"]; save_state(args.path, state)
    print(json.dumps(result, ensure_ascii=False)); raise SystemExit(0 if result["ready"] else 3)

if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)