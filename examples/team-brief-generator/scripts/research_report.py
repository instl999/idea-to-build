#!/usr/bin/env python3
"""Render a source-recorded solution research report."""
import argparse, json, sys
from pathlib import Path
from idea_to_build_lib import IdeaToBuildError, load_json, load_state, render_research_report, save_state

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--path", required=True); parser.add_argument("--input", required=True); args = parser.parse_args()
    root = Path(args.path).expanduser().resolve(); payload = load_json(Path(args.input).expanduser().resolve()); report, result = render_research_report(payload)
    output = root / "docs" / "live" / "RESEARCH.md"; output.parent.mkdir(parents=True, exist_ok=True); output.write_text(report, encoding="utf-8")
    state = load_state(root); state["search_status"] = "INSUFFICIENT" if result["decision"] == "INSUFFICIENT_RESEARCH" else "COMPLETE"; state["research_decision"] = result["decision"]; state["current_phase"] = "SOLUTION_FOUND" if result["decision"] == "ADOPT_DIRECTLY" else "BUILD_DECISION_REQUIRED"; save_state(root, state)
    print(json.dumps({"schema_version": 1, "ok": True, "report": "docs/live/RESEARCH.md", **result}, ensure_ascii=False))

if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)