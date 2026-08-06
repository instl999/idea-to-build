import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_public_release", str(ROOT / "scripts" / "audit_public_release.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load audit_public_release.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class ReleaseAuditTests(unittest.TestCase):
    def test_official_and_synthetic_no_reply_addresses_are_allowed(self):
        for value in (
            "noreply@github.com",
            "12345-user@users.noreply.github.com",
            "fixture@example.invalid",
        ):
            with self.subTest(value=value):
                self.assertTrue(audit.email_allowed(value))

    def test_personal_and_lookalike_addresses_are_rejected(self):
        for value in (
            "person" + "@example.com",
            "attacker" + "@noreply.github.com",
            "noreply" + "@github.com.example.org",
        ):
            with self.subTest(value=value):
                self.assertFalse(audit.email_allowed(value))
