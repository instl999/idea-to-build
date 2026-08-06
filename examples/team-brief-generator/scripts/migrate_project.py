#!/usr/bin/env python3
"""Add missing 0.4 repository-memory files to an older project without overwriting it."""
import argparse, json, sys
from pathlib import Path
from _memory_runtime import runtime


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--path", required=True); parser.add_argument("--apply", action="store_true"); args = parser.parse_args(); here = Path(__file__).resolve().parent
    print(json.dumps(runtime.migrate_project(here.parent / "assets" / "project-template", here, args.path, args.apply), ensure_ascii=False))


if __name__ == "__main__":
    try: main()
    except runtime.IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)