#!/usr/bin/env python3
"""PreToolUse: deny AI mutation of frozen contracts and protection controls."""
from _hooklib import block_payload, emit, find_root, forbidden_request, handle_error, read_event

def main():
    event = read_event(); root = find_root(event.get("cwd"))
    if root is None: return
    try:
        reason = forbidden_request(event, root)
        if reason: emit(block_payload("PreToolUse", reason))
    except Exception as exc:
        payload = handle_error("PreToolUse", root, exc)
        if payload: emit(payload)
if __name__ == "__main__": main()