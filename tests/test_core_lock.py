import json, unittest
from _support import ProjectFixture, itb

class CoreLockTests(unittest.TestCase):
    def setUp(self): self.fx = ProjectFixture()
    def tearDown(self): self.fx.close()
    def test_explicit_confirmation_then_freeze(self):
        result = self.fx.freeze(); self.assertTrue(result["ok"]); self.assertEqual(len(result["files"]), 5)
        state = itb.load_state(self.fx.root); self.assertTrue(state["core_frozen"]); self.assertEqual(state["current_phase"], "CORE_FROZEN")
    def test_verify_success_and_normalized_newlines(self):
        self.fx.freeze(); self.assertTrue(itb.verify_core(self.fx.root)["ok"])
        path = self.fx.root / "docs/core/PROJECT_CHARTER.md"; text = path.read_text(encoding="utf-8"); path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        self.assertTrue(itb.verify_core(self.fx.root)["ok"])
    def test_modified_core_fails(self):
        self.fx.freeze(); path = self.fx.root / "docs/core/PRODUCT_CONTRACT.md"; path.write_text(path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        result = itb.verify_core(self.fx.root); self.assertFalse(result["ok"]); self.assertTrue(any("PRODUCT_CONTRACT" in item for item in result["mismatches"]))
    def test_confirmation_must_be_explicit(self):
        self.fx.make_ready(); state = itb.load_state(self.fx.root); state["current_phase"] = "REQUIREMENTS_READY"; itb.save_state(self.fx.root, state)
        with self.assertRaises(itb.IdeaToBuildError): itb.confirm_core(self.fx.root, "looks fine")
    def test_freeze_requires_human_actor(self):
        self.fx.make_ready(); state = itb.load_state(self.fx.root); state["current_phase"] = "CORE_REVIEW"; state["core_confirmation"] = {"confirmed": True, "actor": "ai"}; itb.save_state(self.fx.root, state)
        with self.assertRaisesRegex(itb.IdeaToBuildError, "human"): itb.freeze_core(self.fx.root, commit=False, readonly=False)

if __name__ == "__main__": unittest.main()