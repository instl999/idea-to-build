import unittest
from _support import ProjectFixture, itb

class RequirementsReadinessTests(unittest.TestCase):
    def setUp(self): self.fx = ProjectFixture()
    def tearDown(self): self.fx.close()
    def test_vague_idea_is_not_ready(self):
        report = itb.check_readiness(self.fx.root); self.assertFalse(report["ready"]); self.assertGreater(len(report["blockers"]), 5)
    def test_multiround_updates_persist(self):
        itb.update_requirements(self.fx.root, [{"id": "problem_definition", "status": "confirmed", "value": "Round one"}])
        itb.update_requirements(self.fx.root, [{"id": "target_users", "status": "confirmed", "value": "Round two"}])
        by_id = {item["id"]: item for item in itb.load_ledger(self.fx.root)["requirements"]}
        self.assertEqual(by_id["problem_definition"]["value"], "Round one"); self.assertEqual(by_id["target_users"]["value"], "Round two")
    def test_p0_conflict_blocks(self):
        itb.update_requirements(self.fx.root, [{"id": "problem_definition", "status": "conflicting", "value": "Two incompatible problems"}])
        self.assertTrue(any("P0 conflict" in item for item in itb.check_readiness(self.fx.root)["blockers"]))
    def test_reversible_default_can_remain_assumed_if_nonblocking(self):
        self.fx.make_ready(); itb.update_requirements(self.fx.root, [{"id": "optional_features", "status": "assumed", "value": "Dark mode", "accepted": True}])
        self.assertTrue(itb.check_readiness(self.fx.root)["ready"])
    def test_irreversible_item_cannot_be_assumed(self):
        self.fx.make_ready(); itb.update_requirements(self.fx.root, [{"id": "deployment", "status": "assumed", "value": "Public cloud", "accepted": True}])
        report = itb.check_readiness(self.fx.root); self.assertFalse(report["ready"]); self.assertTrue(any("Irreversible" in item for item in report["blockers"]))
    def test_complete_information_is_ready(self):
        self.assertTrue(self.fx.make_ready()["ready"])
    def test_not_ready_cannot_freeze(self):
        state = itb.load_state(self.fx.root); state["current_phase"] = "CORE_REVIEW"; state["core_confirmation"] = {"confirmed": True, "actor": "human"}; itb.save_state(self.fx.root, state)
        with self.assertRaisesRegex(itb.IdeaToBuildError, "not ready"): itb.freeze_core(self.fx.root, commit=False, readonly=False)

    def test_missing_requirement_cannot_bypass_gate(self):
        ledger = itb.load_ledger(self.fx.root); ledger["requirements"].pop(); itb.save_ledger(self.fx.root, ledger)
        with self.assertRaisesRegex(itb.IdeaToBuildError, "Missing requirement"): itb.check_readiness(self.fx.root)
    def test_protected_requirement_metadata_cannot_be_changed(self):
        ledger = itb.load_ledger(self.fx.root); ledger["requirements"][0]["required_for_readiness"] = False
        itb.write_json(self.fx.root / ".idea-to-build/requirements_ledger.json", ledger)
        with self.assertRaisesRegex(itb.IdeaToBuildError, "protected metadata"): itb.load_ledger(self.fx.root)
    def test_confirmed_requirement_needs_value(self):
        ledger = itb.load_ledger(self.fx.root); ledger["requirements"][0].update({"status": "confirmed", "value": ""})
        itb.write_json(self.fx.root / ".idea-to-build/requirements_ledger.json", ledger)
        with self.assertRaisesRegex(itb.IdeaToBuildError, "must have a value"): itb.load_ledger(self.fx.root)
if __name__ == "__main__": unittest.main()