import unittest
from _support import ProjectFixture, itb

class EndToEndTests(unittest.TestCase):
    def test_init_ready_freeze_generate_verify(self):
        fx = ProjectFixture("Team Brief Generator")
        try:
            self.assertFalse((fx.root / ".idea-to-build/core.lock.json").exists())
            readiness = fx.make_ready(); self.assertTrue(readiness["ready"])
            state = itb.load_state(fx.root); state["current_phase"] = "REQUIREMENTS_READY"; state["workstreams"] = [{"name": "Application", "goal": "Build the brief generator", "files": ["src"]}]; itb.save_state(fx.root, state)
            itb.confirm_core(fx.root, "Approved: freeze and build this core")
            frozen = itb.freeze_core(fx.root, commit=False, readonly=False); self.assertTrue(frozen["ok"])
            handoff = itb.generate_handoff(fx.root); self.assertEqual(handoff["thread_count"], 3)
            self.assertTrue(itb.verify_core(fx.root)["ok"]); self.assertTrue(itb.render_context(fx.root)["ok"])
            package = itb.validate_project_package(fx.root); self.assertTrue(package["ok"], package["errors"])
            self.assertGreaterEqual(len(list((fx.root / "docs/design").glob("*.md"))), 21)
            prompt = (fx.root / handoff["prompts"][1]).read_text(encoding="utf-8"); self.assertIn("You own only this workstream", prompt)
        finally: fx.close()

if __name__ == "__main__": unittest.main()