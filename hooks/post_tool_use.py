#!/usr/bin/env python3
"""PostToolUse: detect any core drift after a supported tool call."""
from _hooklib import append_guardrail_event, block_payload, emit, find_root, handle_error, read_event, verify_or_reason

def main():
    event = read_event(); root = find_root(event.get("cwd"))
    if root is None: return
    try:
        reason, context = verify_or_reason(root)
        if reason:
            append_guardrail_event(root, "core mismatch after %s: %s" % (event.get("tool_name"), reason))
            emit(block_payload("PostToolUse", reason))
    except Exception as exc:
        payload = handle_error("PostToolUse", root, exc)
        if payload: emit(payload)
if __name__ == "__main__": main()