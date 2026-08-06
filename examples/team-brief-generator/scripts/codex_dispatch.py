#!/usr/bin/env python3
"""Prepare and operate the Codex-native subagent/worktree adapter."""
import argparse
import json
import sys

from idea_to_build_lib import (
    IdeaToBuildError,
    materialize_codex_wave,
    merge_codex_task_result,
    preview_codex_dispatch,
    retire_codex_wave,
    start_codex_dispatch,
    verify_codex_task_result,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    preview = sub.add_parser("preview", help="Validate gates and print a side-effect-free dispatch plan")
    preview.add_argument("--path", required=True)
    preview.add_argument("--max-parallel", type=int, default=3)

    start = sub.add_parser("start", help="Enter DEVELOPMENT_ACTIVE and commit managed dispatch state")
    start.add_argument("--path", required=True)
    start.add_argument("--max-parallel", type=int, default=3)

    materialize = sub.add_parser("materialize-wave", help="Create or reuse isolated worktrees for one dependency wave")
    materialize.add_argument("--path", required=True)
    materialize.add_argument("--wave", type=int, required=True)
    materialize.add_argument("--base-commit", required=True)

    verify = sub.add_parser("verify-result", help="Verify a task branch tip and file ownership before merge")
    verify.add_argument("--path", required=True)
    verify.add_argument("--task-id", required=True)
    verify.add_argument("--commit", required=True)
    verify.add_argument("--base-commit", required=True)

    merge = sub.add_parser("merge-result", help="Verify and merge one task result into the clean integration branch")
    merge.add_argument("--path", required=True)
    merge.add_argument("--task-id", required=True)
    merge.add_argument("--commit", required=True)
    merge.add_argument("--base-commit", required=True)
    retire = sub.add_parser("retire-wave", help="Remove clean worktrees after integration while retaining branches")
    retire.add_argument("--path", required=True)
    retire.add_argument("--wave", type=int, required=True)

    args = parser.parse_args()
    if args.command == "preview":
        result = preview_codex_dispatch(args.path, max_parallel=args.max_parallel)
    elif args.command == "start":
        result = start_codex_dispatch(args.path, max_parallel=args.max_parallel)
    elif args.command == "materialize-wave":
        result = materialize_codex_wave(args.path, args.wave, args.base_commit)
    elif args.command == "verify-result":
        result = verify_codex_task_result(args.path, args.task_id, args.commit, args.base_commit)
    elif args.command == "merge-result":
        result = merge_codex_task_result(args.path, args.task_id, args.commit, args.base_commit)
    else:
        result = retire_codex_wave(args.path, args.wave)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except IdeaToBuildError as exc:
        print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
