#!/usr/bin/env python3
"""Verify frozen core SHA-256 hashes."""
import argparse, json, sys
from idea_to_build_lib import IdeaToBuildError, verify_core

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--path", required=True); args = parser.parse_args(); result = verify_core(args.path); print(json.dumps(result, ensure_ascii=False)); raise SystemExit(0 if result["ok"] else 3)
if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)