import json, subprocess, unittest
from _support import ProjectFixture, itb


def git(root, *args): return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=True)


class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.fx = ProjectFixture("Quality Product"); self.fx.freeze()
        task = itb.get_task(self.fx.root, "TASK-0001"); spec = self.fx.root / task["spec_path"]
        text = spec.read_text(encoding="utf-8").replace("- [ ] The user can replace this example with one observable criterion and `task_state.py ready` accepts the reviewed SPEC.", "- [ ] The verified command exits zero and the user confirms the observable task result.")
        spec.write_text(text, encoding="utf-8")
        payload = itb.load_tasks(self.fx.root); payload["tasks"][0]["owned_paths"] = ["src"]; itb.save_tasks(self.fx.root, payload)
        itb.transition_task(self.fx.root, "TASK-0001", "ready"); itb.transition_task(self.fx.root, "TASK-0001", "in_progress")
        git(self.fx.root, "init", "-q"); git(self.fx.root, "config", "user.name", "Quality Test"); git(self.fx.root, "config", "user.email", "quality@example.invalid"); git(self.fx.root, "add", "."); git(self.fx.root, "commit", "-qm", "fixture")
    def tearDown(self): self.fx.close()

    def test_command_pass_manual_pending_then_human_acceptance_allows_done(self):
        result = itb.run_all_quality_gates(self.fx.root, "TASK-0001")
        self.assertEqual(result["results"][0]["status"], "passed")
        self.assertEqual(result["skipped"][0]["gate_id"], "user-acceptance")
        self.assertIn("Manual acceptance", result["skipped"][0]["reason"])
        self.assertIn("user-acceptance", result["status"]["issues"][0])
        itb.transition_task(self.fx.root, "TASK-0001", "review")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "cannot be done"): itb.transition_task(self.fx.root, "TASK-0001", "done")
        itb.accept_manual_quality_gate(self.fx.root, "TASK-0001", "user-acceptance", "I accept this task result")
        self.assertEqual(itb.transition_task(self.fx.root, "TASK-0001", "done")["status"], "done")

    def test_snapshot_becomes_stale_after_code_change(self):
        itb.run_all_quality_gates(self.fx.root, "TASK-0001")
        (self.fx.root / "src").mkdir(); (self.fx.root / "src/change.txt").write_text("changed", encoding="utf-8")
        status = itb.quality_status(self.fx.root, "TASK-0001")
        self.assertFalse(status["ok"]); self.assertTrue(any("stale" in item for item in status["issues"]))

    def test_shell_controls_and_shell_executables_are_rejected(self):
        for command in (["python", "-c", "print(1); print(2)"], ["cmd.exe", "/c", "echo ok"]):
            payload = itb.new_quality_gates(); payload["gates"][0]["command"] = command; itb.write_json(self.fx.root / itb.QUALITY_GATES_FILE, payload)
            with self.subTest(command=command), self.assertRaises(itb.IdeaToBuildError): itb.load_quality_gates(self.fx.root)

    def test_output_is_redacted_and_bounded(self):
        gates = itb.new_quality_gates(); now = itb.utc_now(); gates["gates"].append({"id": "safe-output", "name": "Safe output", "kind": "command", "command": ["python", "-c", "print('token=abcdefghijklmnop\\n' + 'x'*6000)"], "instructions": None, "required": True, "scope": "all", "configured": True, "source": "test", "updated_at": now})
        itb.write_json(self.fx.root / itb.QUALITY_GATES_FILE, gates)
        tasks = itb.load_tasks(self.fx.root); tasks["tasks"][0]["required_quality_gates"] = ["safe-output"]; itb.save_tasks(self.fx.root, tasks)
        result = itb.run_quality_gate(self.fx.root, "TASK-0001", "safe-output")
        self.assertIn("[REDACTED]", result["output_excerpt"]); self.assertLessEqual(len(result["output_excerpt"]), 4020); self.assertNotIn("abcdefghijklmnop", result["output_excerpt"])

    def test_future_quality_schema_fails_closed(self):
        payload = itb.new_quality_gates(); payload["schema_version"] = 99; itb.write_json(self.fx.root / itb.QUALITY_GATES_FILE, payload)
        with self.assertRaisesRegex(itb.IdeaToBuildError, "newer"): itb.load_quality_gates(self.fx.root)

    def test_cli_uses_current_task_and_run_without_gate_runs_all_commands(self):
        script = self.fx.root / "scripts/quality_gate.py"
        status = subprocess.run(["python", str(script), "status", "--path", str(self.fx.root)], text=True, capture_output=True, timeout=30)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("No quality result exists", status.stdout)
        run = subprocess.run(["python", str(script), "run", "--path", str(self.fx.root)], text=True, capture_output=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["results"][0]["status"], "passed")

if __name__ == "__main__": unittest.main()
