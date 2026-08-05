import importlib.util
import json
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP = ROOT / ".test-tmp"
TEST_TEMP.mkdir(exist_ok=True)
LIB_PATH = ROOT / "skills" / "idea-to-build" / "scripts" / "idea_to_build_lib.py"
_spec = importlib.util.spec_from_file_location("itb_test_runtime", str(LIB_PATH))
itb = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(itb)

class ProjectFixture:
    def __init__(self, name="Example Product"):
        self.temp = TEST_TEMP / ("case-" + uuid.uuid4().hex)
        self.temp.mkdir()
        self.root = self.temp / "project"
        itb.initialize_project(
            ROOT / "skills" / "idea-to-build" / "assets" / "project-template",
            ROOT / "skills" / "idea-to-build" / "scripts",
            self.root, name, "en", False, False, False,
        )
    def close(self):
        for path in self.temp.rglob("*"):
            try: path.chmod(0o700 if path.is_dir() else 0o600)
            except OSError: pass
        shutil.rmtree(self.temp, ignore_errors=True)
    def make_ready(self):
        ledger = itb.load_ledger(self.root)
        updates = []
        for item in ledger["requirements"]:
            if item.get("required_for_readiness"):
                updates.append({"id": item["id"], "status": "confirmed", "value": "Confirmed value for " + item["category"]})
            else:
                updates.append({"id": item["id"], "status": "deferred", "value": "Deferred without blocking MVP"})
        itb.update_requirements(self.root, updates)
        state = itb.load_state(self.root); state["build_decision"] = "BUILD_CUSTOM"; state["research_decision"] = "BUILD_CUSTOM"; state["current_phase"] = "REQUIREMENTS_GATHERING"; itb.save_state(self.root, state)
        return itb.check_readiness(self.root)
    def freeze(self):
        self.make_ready(); state = itb.load_state(self.root); state["current_phase"] = "REQUIREMENTS_READY"; itb.save_state(self.root, state)
        itb.confirm_core(self.root, "I confirm and freeze this core preview")
        return itb.freeze_core(self.root, commit=False, readonly=False)

def candidate(name="Candidate", score=.7, **extra):
    item = {field: score for field in itb.SCORE_FIELDS}; item.update({"name": name, "type": "product", "coverage": score, "official_source": "https://example.invalid/official", "license": "Verified in fixture", "recommendation": "Review"}); item.update(extra); return item

def run_hook(script_name, event):
    import subprocess, sys
    result = subprocess.run([sys.executable, str(ROOT / "hooks" / script_name)], input=json.dumps(event), text=True, capture_output=True, timeout=15)
    if result.returncode != 0: raise AssertionError("hook failed: %s" % result.stderr)
    return json.loads(result.stdout) if result.stdout.strip() else None