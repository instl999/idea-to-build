import json, unittest
from _support import ProjectFixture, itb

class StateMachineTests(unittest.TestCase):
    def setUp(self): self.fx = ProjectFixture()
    def tearDown(self): self.fx.close()
    def test_initial_state_has_required_fields(self):
        state = itb.load_state(self.fx.root)
        for key in ("schema_version", "project_id", "project_name", "current_phase", "created_at", "updated_at", "user_language", "search_status", "requirements_readiness", "core_frozen", "core_hash", "unresolved_questions", "accepted_assumptions", "generated_documents", "planned_codex_threads", "current_milestone", "last_verified_commit"):
            self.assertIn(key, state)
        self.assertEqual(state["current_phase"], "IDEA_RECEIVED")
        self.assertEqual(state["codex_dispatch_status"], "NOT_PLANNED")
        self.assertIsNone(state["codex_dispatch_started_at"])
    def test_supported_transition(self):
        state = itb.transition_state(self.fx.root, "SEARCH_REQUIRED", "Idea recorded")
        self.assertEqual(state["current_phase"], "SEARCH_REQUIRED")
    def test_unsupported_transition_fails(self):
        with self.assertRaises(itb.IdeaToBuildError): itb.transition_state(self.fx.root, "CORE_FROZEN")
    def test_old_schema_is_migrated(self):
        path = self.fx.root / ".idea-to-build" / "project_state.json"; payload = json.loads(path.read_text(encoding="utf-8")); payload.pop("schema_version"); payload.pop("workstreams"); path.write_text(json.dumps(payload), encoding="utf-8")
        state = itb.load_state(self.fx.root); self.assertEqual(state["schema_version"], 1); self.assertEqual(state["workstreams"], [])
    def test_newer_schema_fails_explicitly(self):
        path = self.fx.root / ".idea-to-build" / "project_state.json"; payload = json.loads(path.read_text(encoding="utf-8")); payload["schema_version"] = 999; path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "newer"): itb.load_state(self.fx.root)

    def test_every_declared_transition_is_accepted(self):
        for source, targets in itb.TRANSITIONS.items():
            for target in targets:
                with self.subTest(source=source, target=target):
                    state = itb.load_state(self.fx.root); state["current_phase"] = source; itb.save_state(self.fx.root, state)
                    self.assertEqual(itb.transition_state(self.fx.root, target)["current_phase"], target)
if __name__ == "__main__": unittest.main()