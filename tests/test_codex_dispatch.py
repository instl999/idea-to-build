import json
import subprocess
import unittest
from pathlib import Path

from _support import ProjectFixture, itb


def git(root, *args, check=True):
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=check)


class CodexDispatchTests(unittest.TestCase):
    def setUp(self):
        self.fx = ProjectFixture("Dispatch Product")

    def tearDown(self):
        if (self.fx.root / ".git").exists():
            listed = git(self.fx.root, "worktree", "list", "--porcelain", check=False)
            paths = [Path(line.partition(" ")[2]) for line in listed.stdout.splitlines() if line.startswith("worktree ")]
            for path in paths:
                if path.resolve() != self.fx.root.resolve():
                    git(self.fx.root, "worktree", "remove", "--force", str(path), check=False)
            git(self.fx.root, "worktree", "prune", check=False)
        self.fx.close()

    def prepare(self, workstreams=None):
        self.fx.make_ready()
        state = itb.load_state(self.fx.root)
        state["current_phase"] = "REQUIREMENTS_READY"
        state["workstreams"] = workstreams or [{"name": "Application", "goal": "Build the application", "files": ["src"]}, {"name": "Tooling", "goal": "Build supporting tooling", "files": ["tools"]}]
        state["development_mode"] = "parallel_worktrees" if len(state["workstreams"]) > 1 else "guided_sequential"
        itb.save_state(self.fx.root, state)
        first = itb.get_task(self.fx.root, "TASK-0001"); spec = self.fx.root / first["spec_path"]
        spec.write_text(spec.read_text(encoding="utf-8").replace("The user can replace this example with one observable criterion and `task_state.py ready` accepts the reviewed SPEC.", "The first workstream produces its documented output and its verification command exits zero."), encoding="utf-8")
        tasks = itb.load_tasks(self.fx.root); tasks["tasks"][0]["owned_paths"] = state["workstreams"][0]["files"]; itb.save_tasks(self.fx.root, tasks); prepared = [first]
        for index, stream in enumerate(state["workstreams"][1:], start=2):
            task = itb.create_task(self.fx.root, "TASK-%04d" % index, stream["name"], owned_paths=stream["files"]); task_spec = self.fx.root / task["spec_path"]
            task_spec.write_text(task_spec.read_text(encoding="utf-8").replace("Replace this line with a concrete, observable acceptance result before marking the task ready.", "This workstream produces its documented output and its verification command exits zero."), encoding="utf-8"); prepared.append(task)
        for task in prepared: itb.transition_task(self.fx.root, task["id"], "ready")
        itb.confirm_core(self.fx.root, "I confirm and freeze this core preview")
        itb.freeze_core(self.fx.root, commit=False, readonly=False)
        generated = itb.generate_handoff(self.fx.root)
        git(self.fx.root, "init", "-b", "main")
        git(self.fx.root, "config", "user.name", "Dispatch Test")
        git(self.fx.root, "config", "user.email", "dispatch@example.invalid")
        git(self.fx.root, "add", "--all")
        git(self.fx.root, "commit", "-m", "test: prepare dispatch fixture")
        return generated

    def test_frozen_core_and_user_development_plan_are_dispatch_ready(self):
        generated = self.prepare()
        self.assertTrue(generated["subagents_recommended"])
        manifest = json.loads((self.fx.root / "codex" / "dispatch.json").read_text(encoding="utf-8"))
        self.assertIn("after core freeze", manifest["activation_policy"])
        preview = itb.preview_codex_dispatch(self.fx.root)
        self.assertEqual(preview["status"], "READY")
        self.assertEqual(preview["required_host_tools"], ["spawn_agent", "wait_agent"])

    def test_dispatch_rejects_non_human_frozen_confirmation(self):
        self.prepare()
        path = self.fx.root / ".idea-to-build" / "core.lock.json"
        lock = json.loads(path.read_text(encoding="utf-8"))
        lock["confirmation"]["actor"] = "ai"
        path.write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "explicit human"):
            itb.preview_codex_dispatch(self.fx.root)
    def test_manifest_builds_dependency_waves(self):
        generated = self.prepare(workstreams=[
            {"name": "Backend", "goal": "Build backend", "files": ["server"]},
            {"name": "Frontend", "goal": "Build frontend", "files": ["web"]},
        ])
        preview = itb.preview_codex_dispatch(self.fx.root)
        self.assertEqual([len(wave["task_ids"]) for wave in preview["waves"]], [2])
        self.assertEqual(preview["max_parallel"], 2)
        manifest = json.loads((self.fx.root / "codex" / "dispatch.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_sha256"], itb._json_digest(manifest))

    def test_dirty_integration_tree_blocks_dispatch(self):
        self.prepare()
        (self.fx.root / "unexpected.txt").write_text("dirty", encoding="utf-8")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "clean integration worktree"):
            itb.preview_codex_dispatch(self.fx.root)

    def test_start_enters_development_and_commits_state(self):
        self.prepare()
        before = git(self.fx.root, "rev-parse", "HEAD").stdout.strip()
        started = itb.start_codex_dispatch(self.fx.root)
        after = git(self.fx.root, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(before, after)
        self.assertEqual(started["status"], "ACTIVE")
        state = itb.load_state(self.fx.root)
        self.assertEqual(state["current_phase"], "DEVELOPMENT_ACTIVE")
        self.assertEqual(state["codex_dispatch_status"], "ACTIVE")
        self.assertFalse(git(self.fx.root, "status", "--porcelain").stdout.strip())

    def test_materialize_verify_ownership_and_retire_wave(self):
        self.prepare()
        started = itb.start_codex_dispatch(self.fx.root)
        materialized = itb.materialize_codex_wave(self.fx.root, 1, started["base_commit"])
        self.assertEqual(len(materialized["worktrees"]), 2)
        item = next(value for value in materialized["worktrees"] if value["canonical_task_id"] == "TASK-0001")
        worktree = Path(item["worktree"])
        self.assertTrue(worktree.is_dir())
        (worktree / "src").mkdir(exist_ok=True)
        (worktree / "src" / "feature.txt").write_text("implemented\n", encoding="utf-8")
        git(worktree, "add", "src/feature.txt")
        git(worktree, "commit", "-m", "feat: implement application")
        valid_commit = git(worktree, "rev-parse", "HEAD").stdout.strip()
        verified = itb.verify_codex_task_result(self.fx.root, item["task_id"], valid_commit, started["base_commit"])
        self.assertEqual(verified["changed_files"], ["src/feature.txt"])

        (worktree / "docs" / "live" / "STATUS.md").write_text("outside ownership\n", encoding="utf-8")
        git(worktree, "add", "docs/live/STATUS.md")
        git(worktree, "commit", "-m", "test: violate ownership")
        bad_commit = git(worktree, "rev-parse", "HEAD").stdout.strip()
        with self.assertRaisesRegex(itb.IdeaToBuildError, "outside ownership"):
            itb.verify_codex_task_result(self.fx.root, item["task_id"], bad_commit, started["base_commit"])
        retired = itb.retire_codex_wave(self.fx.root, 1)
        self.assertEqual(len(retired["removed"]), 2)
        self.assertFalse(worktree.exists())
        self.assertEqual(git(self.fx.root, "show-ref", "--verify", "--quiet", "refs/heads/" + item["branch"], check=False).returncode, 0)

    def test_merge_result_integrates_only_verified_task_commit(self):
        self.prepare()
        started = itb.start_codex_dispatch(self.fx.root)
        materialized = itb.materialize_codex_wave(self.fx.root, 1, started["base_commit"])
        item = next(value for value in materialized["worktrees"] if value["canonical_task_id"] == "TASK-0001")
        worktree = Path(item["worktree"])
        (worktree / "src").mkdir(exist_ok=True)
        (worktree / "src" / "merged.txt").write_text("verified merge" + chr(10), encoding="utf-8")
        git(worktree, "add", "src/merged.txt")
        git(worktree, "commit", "-m", "feat: add verified merge fixture")
        commit = git(worktree, "rev-parse", "HEAD").stdout.strip()
        before = git(self.fx.root, "rev-parse", "HEAD").stdout.strip()
        merged = itb.merge_codex_task_result(self.fx.root, item["task_id"], commit, started["base_commit"])
        self.assertEqual(merged["status"], "MERGED")
        self.assertNotEqual(before, merged["integration_commit"])
        self.assertEqual((self.fx.root / "src" / "merged.txt").read_text(encoding="utf-8"), "verified merge" + chr(10))
        self.assertTrue(itb.verify_core(self.fx.root)["ok"])
        retired = itb.retire_codex_wave(self.fx.root, 1)
        self.assertEqual(len(retired["removed"]), 2)
    def test_merge_conflict_is_aborted_and_branch_retained(self):
        self.prepare()
        started = itb.start_codex_dispatch(self.fx.root)
        materialized = itb.materialize_codex_wave(self.fx.root, 1, started["base_commit"])
        item = next(value for value in materialized["worktrees"] if value["canonical_task_id"] == "TASK-0001")
        worktree = Path(item["worktree"])
        (worktree / "src").mkdir(exist_ok=True)
        (worktree / "src" / "conflict.txt").write_text("child" + chr(10), encoding="utf-8")
        git(worktree, "add", "src/conflict.txt")
        git(worktree, "commit", "-m", "feat: child conflict fixture")
        child_commit = git(worktree, "rev-parse", "HEAD").stdout.strip()

        (self.fx.root / "src").mkdir(exist_ok=True)
        (self.fx.root / "src" / "conflict.txt").write_text("root" + chr(10), encoding="utf-8")
        git(self.fx.root, "add", "src/conflict.txt")
        git(self.fx.root, "commit", "-m", "test: root conflict fixture")
        before = git(self.fx.root, "rev-parse", "HEAD").stdout.strip()

        with self.assertRaisesRegex(itb.IdeaToBuildError, "conflicted and was aborted"):
            itb.merge_codex_task_result(self.fx.root, item["task_id"], child_commit, started["base_commit"])
        self.assertEqual(git(self.fx.root, "rev-parse", "HEAD").stdout.strip(), before)
        self.assertFalse(git(self.fx.root, "status", "--porcelain").stdout.strip())
        self.assertEqual((self.fx.root / "src" / "conflict.txt").read_text(encoding="utf-8"), "root" + chr(10))
        self.assertEqual(git(self.fx.root, "show-ref", "--verify", "--quiet", "refs/heads/" + item["branch"], check=False).returncode, 0)
        retired = itb.retire_codex_wave(self.fx.root, 1)
        self.assertEqual(len(retired["removed"]), 2)
    def test_single_workstream_guides_root_agent_without_subagents(self):
        generated = self.prepare(workstreams=[{"name": "Application", "goal": "Build the application", "files": ["src"]}])
        self.assertFalse(generated["subagents_recommended"])
        manifest = json.loads((self.fx.root / "codex" / "dispatch.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["orchestration_mode"], "SINGLE_AGENT")
        self.assertEqual(manifest["tasks"], [])
        with self.assertRaisesRegex(itb.IdeaToBuildError, "not recommended"):
            itb.preview_codex_dispatch(self.fx.root)

    def test_prompt_tampering_breaks_manifest_binding(self):
        self.prepare()
        manifest = json.loads((self.fx.root / "codex" / "dispatch.json").read_text(encoding="utf-8"))
        prompt = self.fx.root / manifest["tasks"][0]["prompt"]
        prompt.write_text(prompt.read_text(encoding="utf-8") + chr(10) + "tampered" + chr(10), encoding="utf-8")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "prompt hash mismatch"):
            itb.load_codex_dispatch(self.fx.root)

    def test_start_commit_failure_restores_state_and_index(self):
        self.prepare()
        hook = self.fx.root / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh" + chr(10) + "exit 1" + chr(10), encoding="utf-8")
        hook.chmod(0o755)
        with self.assertRaises(itb.IdeaToBuildError):
            itb.start_codex_dispatch(self.fx.root)
        state = itb.load_state(self.fx.root)
        self.assertEqual(state["current_phase"], "CODEX_HANDOFF_READY")
        self.assertEqual(state["codex_dispatch_status"], "READY")
        self.assertFalse(git(self.fx.root, "status", "--porcelain").stdout.strip())
    def test_manifest_tampering_fails_closed(self):
        self.prepare()
        path = self.fx.root / "codex" / "dispatch.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["tasks"][0]["ownership"] = ["docs/core"]
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(itb.IdeaToBuildError, "hash mismatch"):
            itb.load_codex_dispatch(self.fx.root)


if __name__ == "__main__":
    unittest.main()
