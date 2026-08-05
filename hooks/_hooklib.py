"""Shared helpers for Idea-to-Build lifecycle hooks."""
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

PROTECTED_EXACT = {
    ".idea-to-build/core.lock.json", "agents.md", "scripts/freeze_core.py",
    "scripts/verify_core.py", "scripts/idea_to_build_lib.py",
}
PROTECTED_PREFIXES = ("docs/core/", "hooks/", ".codex/hooks/")
MUTATING_TOOL = re.compile(r"(?i)(apply_patch|edit|write|delete|remove|move|rename|replace|create)")
MUTATING_COMMAND = re.compile(
    r"(?ix)(^|[;&|]\s*)(rm|mv|cp|chmod|sed|perl|python(?:3)?|git\s+(restore|checkout|reset|clean|mv|rm)|"
    r"set-content|add-content|out-file|remove-item|move-item|copy-item|rename-item|new-item|tee)\b|(?<![<>=])>{1,2}(?![=>])"
)
PROTECTED_FRAGMENT = re.compile(
    r"(?i)(?:[A-Za-z]:)?[^\s'\"]*(?:docs[\\/]core(?:[\\/][^\s'\"]*)?|\.idea-to-build[\\/]core\.lock\.json|"
    r"AGENTS\.md|(?:\.codex[\\/])?hooks[\\/][^\s'\"]*|scripts[\\/](?:freeze_core|verify_core|idea_to_build_lib)\.py)"
)

def read_event():
    raw = sys.stdin.read()
    if not raw.strip(): return {}
    value = json.loads(raw)
    if not isinstance(value, dict): raise ValueError("Hook input must be a JSON object")
    return value

def emit(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")

def find_root(start):
    current = Path(start or os.getcwd()).expanduser().resolve()
    if current.is_file(): current = current.parent
    for candidate in (current,) + tuple(current.parents):
        if (candidate / ".idea-to-build" / "project_state.json").is_file(): return candidate
    return None

def load_runtime(root):
    runtime_path = root / "scripts" / "idea_to_build_lib.py"
    if not runtime_path.is_file(): raise RuntimeError("Idea-to-Build runtime is missing from generated project")
    spec = importlib.util.spec_from_file_location("idea_to_build_project_runtime", str(runtime_path))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def block_payload(event, reason, error=False):
    message = ("Idea-to-Build hook error: " if error else "Idea-to-Build blocked this operation: ") + reason
    if event == "PreToolUse":
        return {"systemMessage": message, "hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": message}}
    if event == "UserPromptSubmit": return {"decision": "block", "reason": message}
    if event == "PostToolUse": return {"continue": False, "stopReason": message, "systemMessage": message, "decision": "block", "reason": message, "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": message}}
    if event == "Stop": return {"decision": "block", "reason": message}
    return {"continue": False, "stopReason": message, "systemMessage": message}

def handle_error(event, root, exc):
    if root is None: return None
    return block_payload(event, str(exc), error=True)

def relative_if_inside(root, cwd, value):
    value = str(value).strip().strip("'\"")
    value = value.lstrip("+-").strip("()[]{};,:")
    if not value: return None
    value = value.replace("%CD%", str(cwd)).replace("$PWD", str(cwd)).replace("${PWD}", str(cwd))
    if value.startswith("a/") or value.startswith("b/"): value = value[2:]
    value = value.replace("\\", os.sep).replace("/", os.sep)
    candidate = Path(value)
    if not candidate.is_absolute(): candidate = Path(cwd) / candidate
    try: candidate = candidate.resolve(strict=False); relative = candidate.relative_to(root)
    except (OSError, ValueError): return None
    return relative.as_posix().lower()

def is_protected(relative):
    relative = relative.lower().lstrip("./")
    return relative in PROTECTED_EXACT or any(relative.startswith(prefix) for prefix in PROTECTED_PREFIXES)

def string_leaves(value):
    if isinstance(value, str): yield value
    elif isinstance(value, dict):
        for child in value.values():
            for item in string_leaves(child): yield item
    elif isinstance(value, list):
        for child in value:
            for item in string_leaves(child): yield item

def candidate_tokens(text):
    for match in re.finditer(r"^\*\*\*\s+(?:Update|Delete|Add)\s+File:\s*(.+)$", text, re.M): yield match.group(1).strip()
    for match in PROTECTED_FRAGMENT.finditer(text): yield match.group(0)
    try:
        for token in shlex.split(text, posix=False):
            if any(marker in token.lower() for marker in ("docs", "core", "agents", "hooks", "scripts", ".idea-to-build")): yield token
    except ValueError:
        pass

def command_is_mutating(tool_name, tool_input):
    if tool_name.lower() in ("apply_patch", "edit", "write"): return True
    if MUTATING_TOOL.search(tool_name) and not tool_name.lower().startswith(("read", "get", "list")): return True
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    return bool(MUTATING_COMMAND.search(str(command)))

def forbidden_request(event, root):
    tool_name = str(event.get("tool_name", "")); tool_input = event.get("tool_input") or {}
    if not isinstance(tool_input, dict): tool_input = {"value": tool_input}
    command = str(tool_input.get("command", ""))
    if re.search(r"(?i)(?:^|[\\/])freeze_core\.py\b", command): return "freeze_core.py is human-controlled and cannot be run by an AI tool call"
    if re.search(r"(?i)project_state\.py\s+confirm-core\b", command): return "core confirmation is human-controlled"
    if not command_is_mutating(tool_name, tool_input): return None
    cwd = Path(event.get("cwd") or root).expanduser().resolve()
    for leaf in string_leaves(tool_input):
        for token in candidate_tokens(leaf):
            relative = relative_if_inside(root, cwd, token)
            if relative and is_protected(relative): return "protected path targeted: %s" % relative
    normalized_command = command.replace("\\", "/").lower()
    if re.search(r"(?:^|[\s'\"])(?:\.\./)*(?:docs/core|\.idea-to-build/core\.lock\.json|agents\.md|hooks/|\.codex/hooks/|scripts/(?:freeze_core|verify_core|idea_to_build_lib)\.py)", normalized_command):
        return "a protected path is targeted by a mutating command"
    return None

def verify_or_reason(root):
    runtime = load_runtime(root); state = runtime.load_state(root)
    if not state.get("core_frozen"): return None, runtime.render_context(root)
    result = runtime.verify_core(root)
    return (None if result["ok"] else "; ".join(result["mismatches"])), runtime.render_context(root)

def git_changes(root):
    result = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], text=True, capture_output=True)
    return result.stdout.splitlines() if result.returncode == 0 else []

def append_guardrail_event(root, message):
    path = root / ".idea-to-build" / "guardrail.log"
    with path.open("a", encoding="utf-8") as handle: handle.write(message.replace("\n", " ")[:1000] + "\n")