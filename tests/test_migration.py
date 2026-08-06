import subprocess, unittest
from _support import ProjectFixture, ROOT, itb


class MigrationTests(unittest.TestCase):
    def setUp(self): self.fx = ProjectFixture("Legacy Project"); self.fx.freeze()
    def tearDown(self): self.fx.close()

    def test_dry_run_and_apply_only_add_missing_files(self):
        core_lock = (self.fx.root / ".idea-to-build/core.lock.json").read_bytes()
        status = self.fx.root / "docs/live/STATUS.md"; status.write_text("# Custom legacy status\n", encoding="utf-8")
        missing = (".idea-to-build/tasks.json", ".idea-to-build/quality_gates.json", "docs/live/MEMORY_MAP.md", "scripts/task_state.py")
        for relative in missing: (self.fx.root / relative).unlink()
        dry = itb.migrate_project(ROOT / "skills/idea-to-build/assets/project-template", ROOT / "skills/idea-to-build/scripts", self.fx.root, False)
        self.assertTrue(dry["dry_run"]); self.assertEqual(set(dry["would_add"]), set(missing)); self.assertFalse((self.fx.root / missing[0]).exists())
        applied = itb.migrate_project(ROOT / "skills/idea-to-build/assets/project-template", ROOT / "skills/idea-to-build/scripts", self.fx.root, True)
        self.assertEqual(set(applied["added"]), set(missing))
        self.assertEqual((self.fx.root / ".idea-to-build/core.lock.json").read_bytes(), core_lock)
        self.assertEqual(status.read_text(encoding="utf-8"), "# Custom legacy status\n")

    def test_migration_never_overwrites_existing_variable_file(self):
        rules = self.fx.root / "docs/live/WORKING_RULES.md"; rules.write_text("custom rules\n", encoding="utf-8")
        result = itb.migrate_project(ROOT / "skills/idea-to-build/assets/project-template", ROOT / "skills/idea-to-build/scripts", self.fx.root, True)
        self.assertNotIn("docs/live/WORKING_RULES.md", result["added"]); self.assertEqual(rules.read_text(encoding="utf-8"), "custom rules\n")

    def test_legacy_runtime_gets_non_overwriting_compatibility_fallback(self):
        legacy = self.fx.root / "scripts/idea_to_build_lib.py"
        legacy.write_text("LEGACY_MARKER = True\n", encoding="utf-8")
        for name in ("task_state.py", "quality_gate.py", "memory_prompts.py", "migrate_project.py", "_memory_runtime.py"):
            (self.fx.root / "scripts" / name).unlink()
        result = itb.migrate_project(ROOT / "skills/idea-to-build/assets/project-template", ROOT / "skills/idea-to-build/scripts", self.fx.root, True)
        self.assertIn("scripts/idea_to_build_memory_runtime.py", result["added"])
        self.assertEqual(legacy.read_text(encoding="utf-8"), "LEGACY_MARKER = True\n")
        completed = subprocess.run(["python", str(self.fx.root / "scripts/task_state.py"), "list", "--path", str(self.fx.root)], text=True, capture_output=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("TASK-0001", completed.stdout)

if __name__ == "__main__": unittest.main()
