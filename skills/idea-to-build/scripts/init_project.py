#!/usr/bin/env python3
"""Initialize an Idea-to-Build project package."""
import argparse, json, sys
from pathlib import Path
from idea_to_build_lib import IdeaToBuildError, initialize_project

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, help="Target project directory")
    parser.add_argument("--name", help="Project name; defaults to target directory name")
    parser.add_argument("--language", default="en", help="User language code")
    parser.add_argument("--force", action="store_true", help="Overwrite generated paths that already exist")
    parser.add_argument("--skip-initial-commit", action="store_true", help="Initialize Git but leave the skeleton uncommitted (CI and fixtures only)")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    result = initialize_project(here.parent / "assets" / "project-template", here, args.path, args.name or Path(args.path).expanduser().resolve().name, args.language, args.force, True, not args.skip_initial_commit)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)