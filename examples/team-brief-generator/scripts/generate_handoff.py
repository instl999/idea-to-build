#!/usr/bin/env python3
"""Generate design documents and an exact Codex thread/worktree handoff."""
import argparse, json, sys
from pathlib import Path
from idea_to_build_lib import IdeaToBuildError, generate_handoff, load_json

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--path", required=True); parser.add_argument("--workstreams", help="JSON file containing a workstreams array"); args = parser.parse_args(); streams = None
    if args.workstreams:
        payload = load_json(Path(args.workstreams).expanduser().resolve()); streams = payload.get("workstreams")
        if not isinstance(streams, list): raise IdeaToBuildError("Workstream input must contain a workstreams array")
    print(json.dumps(generate_handoff(args.path, streams), ensure_ascii=False))
if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)