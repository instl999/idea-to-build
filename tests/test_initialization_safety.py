import os, shutil, unittest, uuid
from _support import ROOT, TEST_TEMP, itb

class InitializationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = TEST_TEMP / ("init-" + uuid.uuid4().hex); self.temp.mkdir()
        self.target = self.temp / "project"
    def tearDown(self): shutil.rmtree(self.temp, ignore_errors=True)
    def init(self, **kwargs):
        return itb.initialize_project(ROOT / "skills/idea-to-build/assets/project-template", ROOT / "skills/idea-to-build/scripts", self.target, kwargs.pop("name", "Safe Project"), "en", kwargs.pop("force", False), False, False)
    def test_runtime_conflict_is_detected_before_any_template_write(self):
        conflict = self.target / "scripts/idea_to_build_lib.py"; conflict.parent.mkdir(parents=True); conflict.write_text("preserve", encoding="utf-8")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "Refusing to overwrite"): self.init()
        self.assertEqual(conflict.read_text(encoding="utf-8"), "preserve")
        self.assertFalse((self.target / "AGENTS.md").exists())
    def test_multiline_project_name_is_rejected(self):
        with self.assertRaises(itb.IdeaToBuildError): self.init(name="Bad\nProject")
    def test_linked_output_ancestor_is_rejected(self):
        self.target.mkdir(); outside = self.temp / "outside"; outside.mkdir()
        try: os.symlink(str(outside), str(self.target / "scripts"), target_is_directory=True)
        except (OSError, NotImplementedError): self.skipTest("directory symlinks are unavailable")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "link or junction"): self.init()
        self.assertEqual(list(outside.iterdir()), [])

if __name__ == "__main__": unittest.main()