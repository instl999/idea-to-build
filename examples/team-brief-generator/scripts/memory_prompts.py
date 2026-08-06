#!/usr/bin/env python3
"""List or render complete localized Codex repository-memory prompts."""
import argparse, json, sys
from _memory_runtime import runtime


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list"); listing.add_argument("--path", required=True)
    show = sub.add_parser("show"); show.add_argument("--path", required=True); show.add_argument("--kind", required=True, choices=runtime.PROMPT_KINDS); show.add_argument("--task")
    args = parser.parse_args()
    if args.command == "list": print(json.dumps({"schema_version": 1, "kinds": list(runtime.PROMPT_KINDS)}, ensure_ascii=False))
    else: print(runtime.memory_prompt(args.path, args.kind, args.task), end="")


if __name__ == "__main__":
    try: main()
    except runtime.IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)