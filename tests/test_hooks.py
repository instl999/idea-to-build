import os, unittest
from _support import ProjectFixture, ROOT, run_hook

class HookTests(unittest.TestCase):
    def setUp(self): self.fx = ProjectFixture(); self.fx.freeze()
    def tearDown(self): self.fx.close()
    def event(self, tool, command, cwd=None):
        return {"session_id": "s", "turn_id": "t", "cwd": str(cwd or self.fx.root), "hook_event_name": "PreToolUse", "tool_name": tool, "tool_use_id": "u", "tool_input": {"command": command}, "permission_mode": "default"}
    def assert_blocked(self, tool, command, cwd=None):
        result = run_hook("pre_tool_use.py", self.event(tool, command, cwd)); self.assertIsNotNone(result); self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
    def test_apply_patch_core_blocked(self): self.assert_blocked("apply_patch", "*** Begin Patch\n*** Update File: docs/core/PROJECT_CHARTER.md\n+x\n*** End Patch")
    def test_shell_redirection_core_blocked(self): self.assert_blocked("Bash", "echo changed > docs/core/PROJECT_CHARTER.md")
    def test_move_remove_and_git_restore_blocked(self):
        for command in ("mv docs/core/PROJECT_CHARTER.md old.md", "rm docs/core/PROJECT_CHARTER.md", "git restore docs/core/PROJECT_CHARTER.md"):
            with self.subTest(command=command): self.assert_blocked("Bash", command)
    def test_windows_path_and_traversal_blocked(self):
        windows_path = str(self.fx.root / "docs/core/CONSTRAINTS.md").replace("/", "\\"); self.assert_blocked("Bash", 'Set-Content "' + windows_path + '" changed')
        sub = self.fx.root / "src"; sub.mkdir(); self.assert_blocked("Bash", "Set-Content ../docs/core/CONSTRAINTS.md changed", sub)
    def test_active_document_allowed(self):
        result = run_hook("pre_tool_use.py", self.event("Bash", "Set-Content docs/live/STATUS.md updated")); self.assertIsNone(result)
    def test_human_only_freeze_blocked(self): self.assert_blocked("Bash", "python scripts/freeze_core.py --path .")
    def test_dispatch_adapter_is_protected(self):
        self.assert_blocked("apply_patch", "*** Begin Patch\n*** Update File: scripts/codex_dispatch.py\n+x\n*** End Patch")
    def test_protected_runtime_execution_is_allowed(self):
        for command in (
            "python scripts/verify_core.py --path .",
            "python scripts/codex_dispatch.py preview --path .",
            "python scripts/codex_dispatch.py merge-result --path . --task-id task-01-app --commit " + "a" * 40 + " --base-commit " + "b" * 40,
        ):
            with self.subTest(command=command):
                self.assertIsNone(run_hook("pre_tool_use.py", self.event("Bash", command)))
    def test_context_injected_on_prompt(self):
        event = {"session_id": "s", "turn_id": "t", "cwd": str(self.fx.root), "hook_event_name": "UserPromptSubmit", "prompt": "continue", "permission_mode": "default"}
        result = run_hook("user_prompt_submit.py", event); context = result["hookSpecificOutput"]["additionalContext"]; self.assertIn("never modify docs/core", context); self.assertIn("Core status: VERIFIED", context)
    def test_post_tool_detects_tamper(self):
        path = self.fx.root / "docs/core/CONSTRAINTS.md"; path.write_text(path.read_text(encoding="utf-8") + "tamper", encoding="utf-8")
        event = {"session_id": "s", "turn_id": "t", "cwd": str(self.fx.root), "hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_use_id": "u", "tool_input": {"command": "unknown"}, "tool_response": {}}
        result = run_hook("post_tool_use.py", event); self.assertFalse(result["continue"]); self.assertEqual(result["decision"], "block")
    def test_non_project_is_quiet(self):
        import shutil, uuid
        empty = ROOT / ".test-tmp" / ("empty-" + uuid.uuid4().hex); empty.mkdir()
        try:
            event = self.event("Bash", "echo ok", empty); self.assertIsNone(run_hook("pre_tool_use.py", event))
        finally: shutil.rmtree(empty, ignore_errors=True)
    def test_project_runtime_is_never_imported(self):
        marker = self.fx.root / "project-runtime-executed"
        runtime = self.fx.root / "scripts" / "idea_to_build_lib.py"
        runtime.write_text("from pathlib import Path\nPath(%r).write_text('executed')\nraise RuntimeError('untrusted project runtime executed')\n" % str(marker), encoding="utf-8")
        event = {"session_id": "s", "turn_id": "t", "cwd": str(self.fx.root), "hook_event_name": "UserPromptSubmit", "prompt": "continue", "permission_mode": "default"}
        result = run_hook("user_prompt_submit.py", event)
        self.assertFalse(marker.exists())
        self.assertIn("Core status: VERIFIED", result["hookSpecificOutput"]["additionalContext"])
    def test_draft_core_edit_is_allowed(self):
        other = ProjectFixture()
        try:
            event = {"session_id": "s", "turn_id": "t", "cwd": str(other.root), "hook_event_name": "PreToolUse", "tool_name": "apply_patch", "tool_use_id": "u", "tool_input": {"command": "*** Update File: docs/core/PROJECT_CHARTER.md"}}
            self.assertIsNone(run_hook("pre_tool_use.py", event))
        finally: other.close()

    def test_structured_dotted_protected_paths_are_blocked(self):
        for path in (".idea-to-build/core.lock.json", ".codex/hooks/guard.py"):
            event = self.event("write", ""); event["tool_input"] = {"path": path, "content": "tamper"}
            result = run_hook("pre_tool_use.py", event)
            self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
    def test_state_flag_cannot_unfreeze_core(self):
        state_path = self.fx.root / ".idea-to-build/project_state.json"
        import json
        state = json.loads(state_path.read_text(encoding="utf-8")); state["core_frozen"] = False
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_blocked("apply_patch", "*** Update File: docs/core/PROJECT_CHARTER.md")
    def test_opaque_git_mutations_are_blocked_when_frozen(self):
        for command in ("git apply update.patch", "git merge topic", "git cherry-pick HEAD~1"):
            with self.subTest(command=command): self.assert_blocked("Bash", command)
    def test_session_start_verifies_and_injects_context(self):
        event = {"cwd": str(self.fx.root), "hook_event_name": "SessionStart"}
        result = run_hook("session_start.py", event)
        self.assertIn("Core status: VERIFIED", result["hookSpecificOutput"]["additionalContext"])
if __name__ == "__main__": unittest.main()