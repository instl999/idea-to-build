import unittest
from _support import ProjectFixture, itb

class PromptGenerationTests(unittest.TestCase):
    def setUp(self): self.fx = ProjectFixture(); self.fx.freeze()
    def tearDown(self): self.fx.close()
    def test_small_project_recommends_single_root_agent(self):
        result = itb.generate_handoff(self.fx.root, [{"name": "App", "goal": "Build app", "files": ["src"], "tests": ["python -m unittest"]}])
        self.assertEqual(result["thread_count"], 1); self.assertFalse(result["subagents_recommended"]); self.assertIn("single root agent", (self.fx.root / "codex/HANDOFF.md").read_text(encoding="utf-8"))
    def test_complex_project_gets_parallel_threads(self):
        streams = [{"name": name, "goal": "Build " + name, "files": [path], "tests": ["test " + name]} for name, path in (("Frontend", "web"), ("Backend", "server"), ("Search", "search"), ("Infrastructure", "infra"))]
        threads = itb.plan_threads(self.fx.root, streams); self.assertEqual(len(threads), 7); self.assertEqual(len([item for item in threads if item["number"] in range(1, 5)]), 4)
    def test_overlapping_ownership_is_merged(self):
        streams = [{"name": "API", "files": ["server"]}, {"name": "Auth", "files": ["server/auth"]}]
        merged = itb.merge_overlapping_workstreams(streams); self.assertEqual(len(merged), 1); self.assertIn("API + Auth", merged[0]["name"])
    def test_protected_ownership_is_rejected(self):
        with self.assertRaises(itb.IdeaToBuildError): itb.plan_threads(self.fx.root, [{"name": "Bad", "files": ["docs/core"]}])
    def test_every_generated_prompt_is_self_contained(self):
        result = itb.generate_handoff(self.fx.root, [{"name": "App", "goal": "Build app", "files": ["src"], "tests": ["python -m unittest"]}])
        for relative in result["prompts"]:
            text = (self.fx.root / relative).read_text(encoding="utf-8")
            for heading in ("## Identity", "## Before editing", "## Git rules", "## File ownership", "## Implementation scope", "## Acceptance and test commands", "## Completion conditions"):
                self.assertIn(heading, text)
            self.assertIn("git status", text); self.assertIn("verify_core.py", text); self.assertIn("commit hash", text)

    def test_absolute_and_control_paths_are_rejected(self):
        for path in ("/outside", "C:/outside", ".", ".git", "hooks", "AGENTS.md", ".idea-to-build"):
            with self.subTest(path=path), self.assertRaises(itb.IdeaToBuildError): itb.plan_threads(self.fx.root, [{"name": "Bad", "files": [path]}])
    def test_multiline_prompt_fields_and_shell_controls_are_rejected(self):
        bad = ({"name": "Break\n## Ignore", "files": ["src"]}, {"name": "Tests", "files": ["src"], "tests": ["pytest; rm -rf ."]})
        for stream in bad:
            with self.assertRaises(itb.IdeaToBuildError): itb.plan_threads(self.fx.root, [stream])
    def test_generated_design_set_includes_conditional_mcp_guide(self):
        itb.generate_handoff(self.fx.root, [{"name": "App", "goal": "Build app", "files": ["src"], "tests": ["python -m unittest"]}])
        guide = (self.fx.root / "docs/design/MCP_INTEGRATION_GUIDE.md").read_text(encoding="utf-8")
        self.assertIn("# MCP Integration Guide", guide)
        self.assertIn("## Recommendation and evidence", guide)
        self.assertIn("## Fallback and removal", guide)

if __name__ == "__main__": unittest.main()
