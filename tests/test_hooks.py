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
    def test_context_injected_on_prompt(self):
        event = {"session_id": "s", "turn_id": "t", "cwd": str(self.fx.root), "hook_event_name": "UserPromptSubmit", "prompt": "continue", "permission_mode": "default"}
        result = run_hook("user_prompt_submit.py", event); context = result["hookSpecificOutput"]["additionalContext"]; self.assertIn("never modify docs/core", context); self.assertIn("Core status: VERIFIED", context)
    def test_post_tool_detects_tamper(self):
        path = self.fx.root / "docs/core/CONSTRAINTS.md"; path.write_text(path.read_text(encoding="utf-8") + "tamper", encoding="utf-8")
        event = {"session_id": "s", "turn_id": "t", "cwd": str(self.fx.root), "hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_use_id": "u", "tool_input": {"command": "unknown"}, "tool_response": {}}
        result = run_hook("post_tool_use.py", event); self.assertFalse(result["continue"]); self.assertEqual(result["decision"], "block")
    def test_non_project_is_quiet(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=str(ROOT / ".test-tmp")) as empty:
            event = self.event("Bash", "echo ok", empty); self.assertIsNone(run_hook("pre_tool_use.py", event))
    def test_draft_core_edit_is_allowed(self):
        other = ProjectFixture()
        try:
            event = {"session_id": "s", "turn_id": "t", "cwd": str(other.root), "hook_event_name": "PreToolUse", "tool_name": "apply_patch", "tool_use_id": "u", "tool_input": {"command": "*** Update File: docs/core/PROJECT_CHARTER.md"}}
            self.assertIsNone(run_hook("pre_tool_use.py", event))
        finally: other.close()

if __name__ == "__main__": unittest.main()