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
    "scripts/verify_core.py", "scripts/idea_to_build_lib.py", "scripts/codex_dispatch.py",
}
PROTECTED_PREFIXES = ("docs/core/", "hooks/", ".codex/hooks/")
MUTATING_TOOL = re.compile(r"(?i)(apply_patch|edit|write|delete|remove|move|rename|replace|create)")
MUTATING_COMMAND = re.compile(
    r"(?ix)(^|[;&|]\s*)(rm|mv|cp|chmod|sed|perl|python(?:3)?|truncate|dd|install|tar|unzip|7z|robocopy|xcopy|"
    r"git\s+(restore|checkout|reset|clean|mv|rm|apply|am|merge|cherry-pick|rebase|revert|switch|stash|read-tree|update-index)|"
    r"set-content|add-content|clear-content|out-file|remove-item|move-item|copy-item|rename-item|new-item|tee)\b|"
    r"(?:system\.io\.file|\[io\.file\])::(?:write|append|delete|move|copy)|(?<![<>=])>{1,2}(?![=>])"
)
PROTECTED_FRAGMENT = re.compile(
    r"(?i)(?:[A-Za-z]:)?[^\s'\"]*(?:docs[\\/]core(?:[\\/][^\s'\"]*)?|\.idea-to-build[\\/]core\.lock\.json|"
    r"AGENTS\.md|(?:\.codex[\\/])?hooks[\\/][^\s'\"]*|scripts[\\/](?:freeze_core|verify_core|idea_to_build_lib|codex_dispatch)\.py)"
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
    # An opened repository is untrusted. Import only the runtime shipped with
    # this installed plugin; project-controlled Python must never execute just
    # because lifecycle hooks inspect a generated project.
    runtime_path = Path(__file__).resolve().parents[1] / "skills" / "idea-to-build" / "scripts" / "idea_to_build_lib.py"
    if not runtime_path.is_file(): raise RuntimeError("Trusted Idea-to-Build plugin runtime is missing")
    spec = importlib.util.spec_from_file_location("idea_to_build_trusted_plugin_runtime", str(runtime_path))
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
    relative = relative.lower()
    if relative.startswith("./"): relative = relative[2:]
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

def protected_script_execution_allowed(root, cwd, command):
    if not command or re.search(r"[;&|`$<>\r\n]", command): return False
    try: tokens = shlex.split(command, posix=os.name != "nt")
    except ValueError: return False
    if not tokens: return False
    executable = Path(tokens[0].strip("'`")).name.lower()
    if executable not in ("python", "python.exe", "python3", "python3.exe", "py", "py.exe"): return False
    index = 1
    if executable in ("py", "py.exe") and len(tokens) > index and tokens[index] == "-3": index += 1
    if len(tokens) <= index: return False
    script = relative_if_inside(root, cwd, tokens[index])
    if script not in {"scripts/verify_core.py", "scripts/codex_dispatch.py"}: return False
    arguments = tokens[index + 1:]
    if arguments.count("--path") != 1: return False
    path_index = arguments.index("--path")
    if len(arguments) <= path_index + 1: return False
    raw_target = str(arguments[path_index + 1]).strip("'`")
    try:
        candidate = Path(raw_target)
        resolved_target = candidate.resolve() if candidate.is_absolute() else (Path(cwd) / candidate).resolve()
    except OSError:
        return False
    if resolved_target != Path(root).resolve(): return False
    if script == "scripts/verify_core.py": return arguments[0] == "--path" and len(arguments) == 2
    return bool(arguments and arguments[0] in ("preview", "start", "materialize-wave", "verify-result", "merge-result", "retire-wave"))

def forbidden_request(event, root):
    tool_name = str(event.get("tool_name", "")); tool_input = event.get("tool_input") or {}
    if not isinstance(tool_input, dict): tool_input = {"value": tool_input}
    command = str(tool_input.get("command", ""))
    runtime = load_runtime(root)
    lock_path = root / ".idea-to-build" / "core.lock.json"
    frozen = False
    if lock_path.is_file():
        try:
            lock = runtime.load_json(lock_path)
            frozen = not bool(lock.get("template_only"))
        except Exception:
            # A malformed lock is still evidence of an attempted frozen
            # baseline. Fail closed and let verification explain the damage.
            frozen = True
    if re.search(r"(?i)(?:^|[\\/])freeze_core\.py\b", command): return "freeze_core.py is human-controlled and cannot be run by an AI tool call"
    if re.search(r"(?i)project_state\.py\s+confirm-core\b", command): return "core confirmation is human-controlled"
    cwd = Path(event.get("cwd") or root).expanduser().resolve()
    if protected_script_execution_allowed(root, cwd, command): return None
    if not command_is_mutating(tool_name, tool_input): return None
    if frozen and re.search(r"(?i)\bgit\s+(?:apply|am|merge|cherry-pick|rebase|revert|read-tree)\b", command): return "opaque Git operation is blocked while a frozen core is present"
    for leaf in string_leaves(tool_input):
        for token in candidate_tokens(leaf):
            relative = relative_if_inside(root, cwd, token)
            if relative and is_protected(relative):
                core_only = relative.startswith("docs/core/") or relative == ".idea-to-build/core.lock.json"
                if frozen or not core_only: return "protected path targeted: %s" % relative
    normalized_command = command.replace("\\", "/").lower()
    always_pattern = r"(?:^|[\s'\"])(?:\.\./)*(?:agents\.md|hooks/|\.codex/hooks/|scripts/(?:freeze_core|verify_core|idea_to_build_lib|codex_dispatch)\.py)"
    core_pattern = r"(?:^|[\s'\"])(?:\.\./)*(?:docs/core|\.idea-to-build/core\.lock\.json)"
    if re.search(always_pattern, normalized_command) or (frozen and re.search(core_pattern, normalized_command)):
        return "a protected path is targeted by a mutating command"
    return None

def verify_or_reason(root):
    runtime = load_runtime(root)
    lock_path = root / ".idea-to-build" / "core.lock.json"
    if not lock_path.is_file(): return None, runtime.render_context(root)
    try:
        lock = runtime.load_json(lock_path)
    except Exception as exc:
        return "core.lock.json is unreadable: %s" % exc, runtime.render_context(root)
    if lock.get("template_only"): return None, runtime.render_context(root)
    result = runtime.verify_core(root)
    return (None if result["ok"] else "; ".join(result["mismatches"])), runtime.render_context(root)

def git_changes(root):
    result = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], text=True, capture_output=True)
    return result.stdout.splitlines() if result.returncode == 0 else None

def append_guardrail_event(root, message):
    runtime = load_runtime(root)
    path = runtime.safe_project_path(root, ".idea-to-build/guardrail.log")
    with path.open("a", encoding="utf-8") as handle: handle.write(message.replace("\n", " ")[:1000] + "\n")
