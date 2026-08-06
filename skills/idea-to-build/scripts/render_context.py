#!/usr/bin/env python3
"""Render bounded core and live project context."""
import argparse, json, sys
from idea_to_build_lib import IdeaToBuildError, render_context

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--path", required=True); parser.add_argument("--task"); parser.add_argument("--format", choices=("json", "text"), default="json"); args = parser.parse_args(); result = render_context(args.path, args.task)
    print(json.dumps(result, ensure_ascii=False) if args.format == "json" else result["additional_context"]); raise SystemExit(0 if result["ok"] else 3)
if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)