#!/usr/bin/env python3
"""Run explicitly configured task quality gates without a shell."""
import argparse, json, sys
from _memory_runtime import runtime


def selected_task(path, task_id):
    if task_id:
        return task_id
    current = runtime.load_state(path).get("current_task_id")
    if not current:
        raise runtime.IdeaToBuildError("Select --task or start a task before running task quality gates")
    return current


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list"); listing.add_argument("--path", required=True)
    status = sub.add_parser("status"); status.add_argument("--path", required=True); status.add_argument("--task")
    run = sub.add_parser("run"); run.add_argument("--path", required=True); run.add_argument("--task"); run.add_argument("--gate")
    all_gates = sub.add_parser("all"); all_gates.add_argument("--path", required=True); all_gates.add_argument("--task")
    manual = sub.add_parser("accept-manual"); manual.add_argument("--path", required=True); manual.add_argument("--task"); manual.add_argument("--gate", required=True); manual.add_argument("--confirmation", required=True); manual.add_argument("--note")
    args = parser.parse_args()
    if args.command == "list": result = runtime.load_quality_gates(args.path)["gates"]
    else:
        task_id = selected_task(args.path, args.task)
        if args.command == "status": result = runtime.quality_status(args.path, task_id)
        elif args.command == "run": result = runtime.run_quality_gate(args.path, task_id, args.gate) if args.gate else runtime.run_all_quality_gates(args.path, task_id)
        elif args.command == "all": result = runtime.run_all_quality_gates(args.path, task_id)
        else: result = runtime.accept_manual_quality_gate(args.path, task_id, args.gate, args.confirmation, args.note)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try: main()
    except runtime.IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)