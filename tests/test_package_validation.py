import importlib.util, sys, unittest
from _support import ROOT

sys.path.insert(0, str(ROOT / "skills/idea-to-build/scripts"))
spec = importlib.util.spec_from_file_location("package_validator", str(ROOT / "skills/idea-to-build/scripts/validate_package.py")); validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)

class PackageValidationTests(unittest.TestCase):
    def test_plugin_package_is_valid(self):
        result = validator.validate_plugin(ROOT)
        self.assertEqual(result["errors"], [])
    def test_manifest_name_matches_skill_directory(self):
        result = validator.validate_plugin(ROOT); self.assertFalse(any("name must match" in item for item in result["errors"]))

if __name__ == "__main__": unittest.main()