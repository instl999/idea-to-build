import importlib.util, sys, unittest
from unittest import mock
from _support import ROOT

sys.path.insert(0, str(ROOT / "skills/idea-to-build/scripts"))
spec = importlib.util.spec_from_file_location("package_validator", str(ROOT / "skills/idea-to-build/scripts/validate_package.py")); validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)

class PackageValidationTests(unittest.TestCase):
    def test_plugin_package_is_valid(self):
        result = validator.validate_plugin(ROOT)
        self.assertEqual(result["errors"], [])
    def test_manifest_name_matches_skill_directory(self):
        result = validator.validate_plugin(ROOT); self.assertFalse(any("name must match" in item for item in result["errors"]))
    def test_skill_places_mcp_assessment_after_readiness(self):
        text = (ROOT / "skills/idea-to-build/SKILL.md").read_text(encoding="utf-8")
        readiness = text.index("### 5. Check readiness")
        mcp = text.index("### 6. Assess MCP applicability when justified")
        core = text.index("### 7. Draft and review core contracts")
        self.assertLess(readiness, mcp)
        self.assertLess(mcp, core)
        for decision in ("MCP_NOT_APPLICABLE", "MCP_USE_EXISTING_SERVER", "MCP_BUILD_CUSTOM_SERVER", "MCP_DEFER"):
            self.assertIn(decision, text)

    def test_required_files_cover_operational_runtime_and_project_memory(self):
        required = set(validator.PLUGIN_REQUIRED)
        for path in (
            ".agents/plugins/marketplace.json",
            "hooks/_hooklib.py",
            "skills/idea-to-build/scripts/project_state.py",
            "scripts/audit_public_release.py",
            "AGENTS.md",
            "docs/INDEX.md",
        ):
            with self.subTest(path=path):
                self.assertIn(path, required)

    def test_version_contract_rejects_mismatch_and_accepts_cachebuster(self):
        pyproject = '[project]\nversion = "0.3.0"\n'
        self.assertEqual(validator._version_contract_errors({"version": "0.3.0+codex.123"}, pyproject), [])
        errors = validator._version_contract_errors({"version": "0.4.0"}, pyproject)
        self.assertIn("pyproject.toml project.version must match the base plugin manifest version", errors)

    def test_missing_operational_hook_helper_is_reported(self):
        original = type(ROOT).is_file
        def missing_hooklib(path):
            if path.as_posix().endswith("hooks/_hooklib.py"): return False
            return original(path)
        with mock.patch.object(type(ROOT), "is_file", missing_hooklib):
            result = validator.validate_plugin(ROOT)
        self.assertIn("Missing required plugin file: hooks/_hooklib.py", result["errors"])

    def test_missing_mcp_protocol_is_reported(self):
        original = type(ROOT).is_file
        def missing_mcp(path):
            if path.as_posix().endswith("skills/idea-to-build/references/mcp-integration.md"): return False
            return original(path)
        with mock.patch.object(type(ROOT), "is_file", missing_mcp):
            result = validator.validate_plugin(ROOT)
        self.assertIn("Missing required plugin file: skills/idea-to-build/references/mcp-integration.md", result["errors"])


if __name__ == "__main__": unittest.main()
