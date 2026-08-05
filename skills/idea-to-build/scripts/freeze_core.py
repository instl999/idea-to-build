#!/usr/bin/env python3
"""Human-controlled freeze of approved core contracts."""
import argparse, json, sys
from idea_to_build_lib import IdeaToBuildError, freeze_core

def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog="AI development conversations must not run this command."); parser.add_argument("--path", required=True); parser.add_argument("--tag", help="Optional annotated baseline tag"); args = parser.parse_args()
    print(json.dumps(freeze_core(args.path, commit=True, tag=args.tag, readonly=True), ensure_ascii=False))

if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)