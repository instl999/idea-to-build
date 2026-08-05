#!/usr/bin/env python3
"""Validate the plugin source package or a generated project package."""
import argparse, ast, json, re, sys
from pathlib import Path
from idea_to_build_lib import IdeaToBuildError, load_json, validate_project_package

PLUGIN_REQUIRED = (
    ".codex-plugin/plugin.json", "skills/idea-to-build/SKILL.md", "skills/idea-to-build/agents/openai.yaml",
    "skills/idea-to-build/references/workflow.md", "skills/idea-to-build/references/solution-research.md",
    "skills/idea-to-build/references/requirements-readiness.md", "skills/idea-to-build/references/document-contracts.md",
    "skills/idea-to-build/references/codex-orchestration.md", "skills/idea-to-build/references/git-policy.md",
    "skills/idea-to-build/references/security-policy.md", "skills/idea-to-build/assets/project-template/AGENTS.md",
    "hooks/hooks.json", "hooks/session_start.py", "hooks/user_prompt_submit.py", "hooks/pre_tool_use.py",
    "hooks/post_tool_use.py", "hooks/stop_check.py", "README.md", "CHANGELOG.md", "LICENSE", "pyproject.toml",
)

def validate_plugin(root):
    errors = ["Missing required plugin file: %s" % item for item in PLUGIN_REQUIRED if not (root / item).is_file()]
    try:
        manifest = load_json(root / ".codex-plugin" / "plugin.json")
        if manifest.get("name") != root.name: errors.append("Plugin name must match root directory name")
        if manifest.get("skills") != "./skills/": errors.append("Manifest skills path must be ./skills/")
        if "hooks" in manifest: errors.append("Default hooks/hooks.json discovery should be used; omit manifest hooks for validator compatibility")
    except IdeaToBuildError as exc: errors.append(str(exc))
    skill_path = root / "skills" / "idea-to-build" / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        if not text.startswith("---\n"): errors.append("SKILL.md must start with YAML frontmatter")
        if "name: idea-to-build" not in text[:300]: errors.append("SKILL.md name is missing or incorrect")
        if "description:" not in text[:1200]: errors.append("SKILL.md description is missing")
        if "Do not use" not in text[:1800]: errors.append("SKILL.md description must state negative activation boundaries")
    yaml_path = root / "skills" / "idea-to-build" / "agents" / "openai.yaml"
    if yaml_path.is_file():
        yaml_text = yaml_path.read_text(encoding="utf-8")
        for token in ("interface:", "display_name:", "short_description:", "policy:", "allow_implicit_invocation:"):
            if token not in yaml_text: errors.append("openai.yaml missing %s" % token)
    hooks_path = root / "hooks" / "hooks.json"
    if hooks_path.is_file():
        try:
            hooks = load_json(hooks_path).get("hooks", {})
            for event in ("SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"):
                if event not in hooks: errors.append("hooks.json missing %s" % event)
        except IdeaToBuildError as exc: errors.append(str(exc))
    for path in root.rglob("*.py"):
        if ".git" in path.parts: continue
        try: ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc: errors.append("Invalid Python %s: %s" % (path.relative_to(root), exc))
    private_patterns = (re.compile(re.escape("C:" + chr(92) + "Users" + chr(92)), re.I), re.compile("/" + "Users" + r"/[^/<]+/"), re.compile("/" + "home" + r"/[^/<]+/"))
    secret_pattern = re.compile(r"(?i)(api[_-]?key|secret|token)\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}")
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() in {".pyc", ".png", ".jpg"}: continue
        try: text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        if ("[" + "TODO:") in text: errors.append("Unresolved placeholder in %s" % path.relative_to(root))
        if any(pattern.search(text) for pattern in private_patterns): errors.append("Private absolute path in %s" % path.relative_to(root))
        if secret_pattern.search(text): errors.append("Possible secret in %s" % path.relative_to(root))
    return {"schema_version": 1, "kind": "plugin", "ok": not errors, "errors": errors}

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--path", help="Plugin or generated project root"); args = parser.parse_args()
    script_path = Path(__file__).resolve()
    default_root = Path.cwd().resolve()
    for candidate in (script_path.parent,) + tuple(script_path.parents):
        if (candidate / ".codex-plugin" / "plugin.json").is_file() or (candidate / ".idea-to-build" / "project_state.json").is_file():
            default_root = candidate
            break
    root = Path(args.path).expanduser().resolve() if args.path else default_root
    result = validate_plugin(root) if (root / ".codex-plugin" / "plugin.json").is_file() else validate_project_package(root)
    print(json.dumps(result, ensure_ascii=False)); raise SystemExit(0 if result["ok"] else 4)

if __name__ == "__main__":
    try: main()
    except IdeaToBuildError as exc: print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr); raise SystemExit(2)
