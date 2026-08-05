#!/usr/bin/env python3
"""UserPromptSubmit: verify core and inject bounded context on every prompt."""
from _hooklib import block_payload, emit, find_root, handle_error, read_event, verify_or_reason

def main():
    event = read_event(); root = find_root(event.get("cwd"))
    if root is None: return
    try:
        reason, context = verify_or_reason(root)
        if reason: emit(block_payload("UserPromptSubmit", reason)); return
        emit({"continue": True, "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context["additional_context"]}})
    except Exception as exc:
        payload = handle_error("UserPromptSubmit", root, exc)
        if payload: emit(payload)
if __name__ == "__main__": main()