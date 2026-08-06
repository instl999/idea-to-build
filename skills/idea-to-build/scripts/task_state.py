#!/usr/bin/env python3
"""Manage the canonical Idea-to-Build task ledger."""
import argparse, json, sys
from _memory_runtime import runtime


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list"); listing.add_argument("--path", required=True); listing.add_argument("--status")
    show = sub.add_parser("show"); show.add_argument("--path", required=True); show.add_argument("--task", required=True)
    create = sub.add_parser("create"); create.add_argument("--path", required=True); create.add_argument("--task", required=True); create.add_argument("--title", required=True); create.add_argument("--priority", choices=("P0", "P1", "P2", "P3"), default="P1"); create.add_argument("--owned-path", action="append", default=[]); create.add_argument("--depends-on", action="append", default=[]); create.add_argument("--quality-gate", action="append")
    for name in ("ready", "start", "review", "complete", "cancel"):
        item = sub.add_parser(name); item.add_argument("--path", required=True); item.add_argument("--task", required=True); item.add_argument("--reason")
    blocked = sub.add_parser("block"); blocked.add_argument("--path", required=True); blocked.add_argument("--task", required=True); blocked.add_argument("--blocked-by", action="append", default=[]); blocked.add_argument("--reason", required=True)
    reopen = sub.add_parser("reopen"); reopen.add_argument("--path", required=True); reopen.add_argument("--task", required=True); reopen.add_argument("--reason", required=True)
    sync = sub.add_parser("sync-docs"); sync.add_argument("--path", required=True)
    args = parser.parse_args()
    if args.command == "list":
        tasks = runtime.load_tasks(args.path)["tasks"]; result = [item for item in tasks if not args.status or item["status"] == args.status]
    elif args.command == "show": result = runtime.get_task(args.path, args.task)
    elif args.command == "create": result = runtime.create_task(args.path, args.task, args.title, args.priority, args.owned_path, args.depends_on, args.quality_gate)
    elif args.command == "block": result = runtime.block_task(args.path, args.task, args.blocked_by, args.reason)
    elif args.command == "reopen": result = runtime.reopen_task(args.path, args.task, args.reason)
    elif args.command == "sync-docs": result = {"path": str(runtime.sync_tasks_document(args.path))}
    else:
        target = {"ready": "ready", "start": "in_progress", "review": "review", "complete": "done", "cancel": "cancelled"}[args.command]
        result = runtime.transition_task(args.path, args.task, target, args.reason)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try: main()
    except runtime.IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)