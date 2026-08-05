import json, unittest
from _support import ROOT, itb

class ActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.cases = json.loads((ROOT / "tests/fixtures/activation_cases.json").read_text(encoding="utf-8"))
    def test_positive_cases_match(self):
        for prompt in self.cases["positive"]:
            with self.subTest(prompt=prompt): self.assertTrue(itb.should_activate(prompt))
    def test_negative_cases_do_not_match(self):
        for prompt in self.cases["negative"]:
            with self.subTest(prompt=prompt): self.assertFalse(itb.should_activate(prompt))
    def test_skill_description_has_positive_and_negative_boundaries(self):
        text = (ROOT / "skills/idea-to-build/SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        self.assertIn("I have an app idea", text); self.assertIn("Do not use", text); self.assertIn("narrow bug fix", text)

if __name__ == "__main__": unittest.main()