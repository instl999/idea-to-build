"""Standard-library runtime for the Idea-to-Build Codex plugin."""
from __future__ import print_function
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

SCHEMA_VERSION = 1
PHASES = (
    "IDEA_RECEIVED", "SEARCH_REQUIRED", "SEARCH_IN_PROGRESS", "SOLUTION_FOUND",
    "BUILD_DECISION_REQUIRED", "REQUIREMENTS_GATHERING", "REQUIREMENTS_CONFLICT",
    "REQUIREMENTS_READY", "CORE_REVIEW", "CORE_FROZEN", "DOCUMENTS_GENERATED",
    "CODEX_HANDOFF_READY", "DEVELOPMENT_ACTIVE", "CHANGE_REQUESTED", "RELEASE_READY", "ARCHIVED",
)
TRANSITIONS = {
    "IDEA_RECEIVED": {"SEARCH_REQUIRED"}, "SEARCH_REQUIRED": {"SEARCH_IN_PROGRESS"},
    "SEARCH_IN_PROGRESS": {"SOLUTION_FOUND", "BUILD_DECISION_REQUIRED"},
    "SOLUTION_FOUND": {"BUILD_DECISION_REQUIRED", "ARCHIVED"},
    "BUILD_DECISION_REQUIRED": {"REQUIREMENTS_GATHERING", "ARCHIVED"},
    "REQUIREMENTS_GATHERING": {"REQUIREMENTS_CONFLICT", "REQUIREMENTS_READY"},
    "REQUIREMENTS_CONFLICT": {"REQUIREMENTS_GATHERING", "REQUIREMENTS_READY"},
    "REQUIREMENTS_READY": {"CORE_REVIEW"}, "CORE_REVIEW": {"REQUIREMENTS_GATHERING", "CORE_FROZEN"},
    "CORE_FROZEN": {"DOCUMENTS_GENERATED", "CHANGE_REQUESTED"},
    "DOCUMENTS_GENERATED": {"CODEX_HANDOFF_READY", "CHANGE_REQUESTED"},
    "CODEX_HANDOFF_READY": {"DEVELOPMENT_ACTIVE", "CHANGE_REQUESTED"},
    "DEVELOPMENT_ACTIVE": {"CHANGE_REQUESTED", "RELEASE_READY"},
    "CHANGE_REQUESTED": {"DEVELOPMENT_ACTIVE", "ARCHIVED"},
    "RELEASE_READY": {"DEVELOPMENT_ACTIVE", "ARCHIVED"}, "ARCHIVED": set(),
}
RESEARCH_DECISIONS = {"ADOPT_DIRECTLY", "ADOPT_WITH_CONFIGURATION", "COMBINE_EXISTING_TOOLS", "EXTEND_OPEN_SOURCE", "BUILD_CUSTOM", "INSUFFICIENT_RESEARCH", "NOT_RECOMMENDED"}
BUILDABLE_DECISIONS = {"ADOPT_WITH_CONFIGURATION", "COMBINE_EXISTING_TOOLS", "EXTEND_OPEN_SOURCE", "BUILD_CUSTOM"}
CORE_FILES = (
    "docs/core/PROJECT_CHARTER.md", "docs/core/PRODUCT_CONTRACT.md",
    "docs/core/ARCHITECTURE_CONTRACT.md", "docs/core/CONSTRAINTS.md",
    "docs/core/ACCEPTANCE_BASELINE.md",
)
REQUIREMENT_STATUSES = {"confirmed", "assumed", "open", "conflicting", "deferred", "out_of_scope"}
REQUIREMENT_SPECS = (
    ("problem_definition", "Problem definition", "P0", False, True),
    ("target_users", "Target users", "P0", False, True),
    ("trigger_scenarios", "Use trigger scenarios", "P1", True, False),
    ("current_alternatives", "Current alternatives", "P1", True, False),
    ("painful_steps", "Most painful steps", "P1", True, False),
    ("core_value", "Core value", "P0", False, False),
    ("success_outcome", "User success outcome", "P0", False, False),
    ("product_shape", "Product shape", "P0", False, True),
    ("primary_workflow", "Primary user workflow", "P0", False, True),
    ("inputs", "Inputs", "P0", False, True), ("outputs", "Outputs", "P0", False, True),
    ("must_have_features", "Must-have features", "P0", False, True),
    ("optional_features", "Optional features", "P2", True, False),
    ("non_goals", "Explicit non-goals", "P0", False, True),
    ("user_accounts", "User accounts", "P1", True, False),
    ("roles_permissions", "Roles and permissions", "P1", False, False),
    ("data_sources", "Data sources", "P0", False, True),
    ("external_integrations", "External integrations or none", "P0", False, True),
    ("privacy", "Privacy level and handling", "P0", False, True),
    ("security", "Security level and controls", "P0", False, True),
    ("compliance", "Compliance requirements or none", "P1", False, False),
    ("region_language", "Regions and languages", "P1", True, False),
    ("performance", "Performance requirements", "P1", True, False),
    ("usability", "Usability and accessibility", "P1", True, False),
    ("scale", "Expected scale", "P1", True, False),
    ("deployment", "Deployment boundary", "P0", False, True),
    ("budget", "Budget", "P1", False, False),
    ("team_capability", "Development team capability", "P1", True, False),
    ("time_constraints", "Time constraints", "P1", False, False),
    ("operations", "Operations and maintenance", "P1", True, False),
    ("business_model", "Business model", "P2", True, False),
    ("success_metrics", "Success metrics", "P1", True, False),
    ("acceptance_criteria", "End-to-end acceptance criteria", "P0", False, True),
    ("edge_cases", "Edge cases", "P1", True, False),
    ("failure_handling", "Failure handling", "P1", True, False),
    ("examples", "Example inputs and outputs", "P1", True, False),
    ("technical_constraints", "Technical constraints", "P1", False, False),
    ("immutable_constraints", "User-declared immutable constraints", "P0", False, True),
)
NULLABLE_OUT_OF_SCOPE = {"external_integrations", "compliance", "user_accounts"}
SCORE_FIELDS = ("functional_fit", "workflow_fit", "user_fit", "data_integration_fit", "privacy_security_fit", "deployment_fit", "customizability", "cost_fit", "maintenance", "license_fit", "lock_in_fit", "implementation_speed")
SCORE_WEIGHTS = {"functional_fit": .16, "workflow_fit": .12, "user_fit": .08, "data_integration_fit": .09, "privacy_security_fit": .12, "deployment_fit": .08, "customizability": .07, "cost_fit": .07, "maintenance": .06, "license_fit": .05, "lock_in_fit": .05, "implementation_speed": .05}
DESIGN_DOCS = {
    "PRODUCT_REQUIREMENTS.md": ("Product Requirements", ("Problem and users", "Scope", "Requirements", "Acceptance")),
    "USER_STORIES.md": ("User Stories", ("Actors", "Stories", "Acceptance links")),
    "USER_FLOWS.md": ("User Flows", ("Primary flow", "Alternative flows", "Failure flows")),
    "FEATURES.md": ("Feature Inventory", ("Must have", "Optional", "Non-goals")),
    "NON_FUNCTIONAL_REQUIREMENTS.md": ("Non-functional Requirements", ("Performance", "Reliability", "Usability", "Scale")),
    "DATA_MODEL.md": ("Data Model", ("Entities", "Ownership", "Lifecycle", "Retention")),
    "API_CONTRACT.md": ("API Contract", ("Interfaces", "Requests", "Responses", "Errors", "Versioning")),
    "SYSTEM_CONTEXT.md": ("System Context", ("Actors", "System boundary", "External systems", "Trust boundaries")),
    "COMPONENT_ARCHITECTURE.md": ("Component Architecture", ("Components", "Responsibilities", "Data flow", "Runtime boundaries")),
    "MODULE_BOUNDARIES.md": ("Module Boundaries", ("Ownership", "Public interfaces", "Forbidden coupling")),
    "EXTERNAL_DEPENDENCIES.md": ("External Dependencies", ("Required dependencies", "Alternatives", "Replaceability")),
    "SECURITY_PRIVACY.md": ("Security and Privacy", ("Threats", "Controls", "Data handling", "Verification")),
    "PERMISSIONS.md": ("Permission Model", ("Roles", "Capabilities", "Authorization checks", "Audit")),
    "ERROR_HANDLING.md": ("Error Handling", ("Error taxonomy", "User behavior", "Recovery", "Escalation")),
    "OBSERVABILITY.md": ("Observability", ("Logs", "Metrics", "Traces", "Alerts", "Sensitive-data rules")),
    "TEST_STRATEGY.md": ("Test Strategy", ("Unit", "Integration", "End-to-end", "Security", "Regression")),
    "DEPLOYMENT_ROLLBACK.md": ("Deployment and Rollback", ("Environments", "Release", "Migration", "Rollback")),
    "MVP_ROADMAP.md": ("MVP Roadmap", ("Milestones", "Dependencies", "Deliverables", "Acceptance")),
    "RISK_REGISTER.md": ("Risk Register", ("Product risks", "Technical risks", "Security risks", "Mitigations")),
    "REUSE_MATRIX.md": ("Reuse Matrix", ("Products", "Open source", "Skills and MCP", "SDKs and APIs", "Decision")),
    "CODEX_ORCHESTRATION.md": ("Codex Orchestration", ("Dependency graph", "Thread boundaries", "Merge sequence", "Quality gates")),
}

class IdeaToBuildError(RuntimeError):
    """Expected workflow or validation failure."""

def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path, payload):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(str(temporary), str(path))

def load_json(path):
    path = Path(path)
    try: payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc: raise IdeaToBuildError("Required JSON file is missing: %s" % path) from exc
    except (OSError, json.JSONDecodeError) as exc: raise IdeaToBuildError("Cannot read JSON file %s: %s" % (path, exc)) from exc
    if not isinstance(payload, dict): raise IdeaToBuildError("JSON root must be an object: %s" % path)
    return payload

def ensure_supported_schema(payload, label):
    raw = payload.get("schema_version", 0)
    if not isinstance(raw, int) or raw < 0: raise IdeaToBuildError("%s has an invalid schema_version" % label)
    if raw > SCHEMA_VERSION: raise IdeaToBuildError("%s schema_version %s is newer than supported version %s" % (label, raw, SCHEMA_VERSION))
    payload["schema_version"] = SCHEMA_VERSION
    return payload

def state_defaults(project_name="Unconfirmed"):
    now = utc_now()
    return {"schema_version": 1, "project_id": str(uuid.uuid4()), "project_name": project_name, "current_phase": "IDEA_RECEIVED", "created_at": now, "updated_at": now, "user_language": "en", "search_status": "NOT_STARTED", "research_decision": None, "build_decision": None, "requirements_readiness": "NOT_READY", "core_frozen": False, "core_hash": None, "core_confirmation": None, "unresolved_questions": [], "accepted_assumptions": [], "generated_documents": [], "planned_codex_threads": 0, "current_milestone": "Validate", "last_verified_commit": None, "workstreams": [], "test_commands": []}

def migrate_state(payload):
    ensure_supported_schema(payload, "project state")
    result = state_defaults(str(payload.get("project_name") or "Unconfirmed")); result.update(payload)
    if result.get("current_phase") not in PHASES: raise IdeaToBuildError("Unknown project phase: %s" % result.get("current_phase"))
    for key in ("unresolved_questions", "accepted_assumptions", "generated_documents", "workstreams", "test_commands"):
        if not isinstance(result.get(key), list): raise IdeaToBuildError("project state field %s must be a list" % key)
    result["schema_version"] = SCHEMA_VERSION
    return result

def project_root(path): return Path(path).expanduser().resolve()

def find_project_root(start):
    current = project_root(start); current = current.parent if current.is_file() else current
    for candidate in (current,) + tuple(current.parents):
        if (candidate / ".idea-to-build" / "project_state.json").is_file(): return candidate
    return None

def load_state(root): return migrate_state(load_json(project_root(root) / ".idea-to-build" / "project_state.json"))

def save_state(root, state):
    state = migrate_state(dict(state)); state["updated_at"] = utc_now()
    write_json(project_root(root) / ".idea-to-build" / "project_state.json", state)

def transition_state(root, target, reason=None):
    if target not in PHASES: raise IdeaToBuildError("Unknown target phase: %s" % target)
    state = load_state(root); current = state["current_phase"]
    if target != current and target not in TRANSITIONS[current]: raise IdeaToBuildError("Unsupported phase transition: %s -> %s" % (current, target))
    state["current_phase"] = target
    if reason: state.setdefault("phase_history", []).append({"from": current, "to": target, "reason": reason, "at": utc_now()})
    save_state(root, state); return state
def new_requirements_ledger():
    return {"schema_version": 1, "updated_at": utc_now(), "requirements": [
        {"id": item_id, "category": label, "priority": priority, "reversible": reversible,
         "required_for_readiness": required, "status": "open", "value": None,
         "accepted": False, "notes": ""}
        for item_id, label, priority, reversible, required in REQUIREMENT_SPECS]}

def load_ledger(root):
    ledger = ensure_supported_schema(load_json(project_root(root) / ".idea-to-build" / "requirements_ledger.json"), "requirements ledger")
    requirements = ledger.get("requirements")
    if not isinstance(requirements, list): raise IdeaToBuildError("requirements ledger must contain a requirements array")
    seen = set()
    for item in requirements:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str): raise IdeaToBuildError("Every requirement must have a string id")
        if item["id"] in seen: raise IdeaToBuildError("Duplicate requirement id: %s" % item["id"])
        seen.add(item["id"])
        if item.get("status") not in REQUIREMENT_STATUSES: raise IdeaToBuildError("Invalid requirement status for %s" % item["id"])
    return ledger

def save_ledger(root, ledger):
    ensure_supported_schema(ledger, "requirements ledger"); ledger["updated_at"] = utc_now()
    write_json(project_root(root) / ".idea-to-build" / "requirements_ledger.json", ledger)

def update_requirements(root, updates):
    ledger = load_ledger(root); by_id = {item["id"]: item for item in ledger["requirements"]}
    for update in updates:
        item_id = update.get("id")
        if item_id not in by_id: raise IdeaToBuildError("Unknown requirement id: %s" % item_id)
        status_value = update.get("status", by_id[item_id]["status"])
        if status_value not in REQUIREMENT_STATUSES: raise IdeaToBuildError("Invalid requirement status: %s" % status_value)
        for key in ("status", "value", "accepted", "notes"):
            if key in update: by_id[item_id][key] = update[key]
    save_ledger(root, ledger); return ledger

def check_readiness(root):
    ledger, state = load_ledger(root), load_state(root)
    blockers, confirmed, assumptions, unresolved, non_blocking = [], [], [], [], []
    for item in ledger["requirements"]:
        status_value = item["status"]; label = "%s (%s)" % (item["category"], item["id"])
        if status_value == "confirmed": confirmed.append(label)
        elif status_value == "assumed": assumptions.append(label)
        elif status_value in ("open", "conflicting"): unresolved.append(label)
        else: non_blocking.append(label)
        if status_value == "conflicting" and item.get("priority") == "P0": blockers.append("P0 conflict: %s" % label)
        if item.get("required_for_readiness"):
            permitted_out = item["id"] in NULLABLE_OUT_OF_SCOPE and status_value == "out_of_scope"
            if status_value != "confirmed" and not permitted_out: blockers.append("Required item is not confirmed: %s" % label)
        if not item.get("reversible", True) and status_value == "assumed": blockers.append("Irreversible item cannot remain assumed: %s" % label)
        if item.get("priority") == "P0" and status_value == "assumed" and not item.get("accepted"): blockers.append("P0 assumption is not accepted: %s" % label)
    if state.get("build_decision") not in BUILDABLE_DECISIONS: blockers.append("A build/configure/combine/extend decision is not recorded")
    blockers = list(dict.fromkeys(blockers))
    required_total = sum(1 for item in ledger["requirements"] if item.get("required_for_readiness")) + 1
    ratio = round((required_total - min(required_total, len(blockers))) / float(required_total), 3)
    return {"schema_version": 1, "ready": not blockers, "status": "READY" if not blockers else "NOT_READY", "completion_ratio": ratio, "confirmed": confirmed, "assumptions": assumptions, "unresolved": unresolved, "non_blocking": non_blocking, "blockers": blockers}

def score_candidate(candidate):
    total = 0.0
    for field in SCORE_FIELDS:
        value = candidate.get(field, 0.0)
        if not isinstance(value, (int, float)) or value < 0 or value > 1: raise IdeaToBuildError("Candidate score %s must be between 0 and 1" % field)
        total += float(value) * SCORE_WEIGHTS[field]
    return round(total, 3)

def decide_research(payload):
    if not payload.get("network_available", False): return {"decision": "INSUFFICIENT_RESEARCH", "candidate_gap": False, "reason": "Live research was unavailable.", "candidates": []}
    if payload.get("conflicting_evidence"): return {"decision": "INSUFFICIENT_RESEARCH", "candidate_gap": False, "reason": "Material evidence conflicts remain unresolved.", "candidates": []}
    candidates = payload.get("candidates", [])
    if not isinstance(candidates, list): raise IdeaToBuildError("candidates must be an array")
    scored = []
    for raw in candidates:
        if not isinstance(raw, dict): raise IdeaToBuildError("Each candidate must be an object")
        item = dict(raw); item["score"] = score_candidate(item); scored.append(item)
    scored.sort(key=lambda item: item["score"], reverse=True)
    viable = [item for item in scored if not item.get("disqualifying_risk")]
    if not viable: decision = "BUILD_CUSTOM"
    else:
        best = viable[0]
        if best["score"] >= .82 and best.get("coverage", best["score"]) >= .85: decision = "ADOPT_DIRECTLY"
        elif best["score"] >= .68 and best.get("configurable", False): decision = "ADOPT_WITH_CONFIGURATION"
        elif len(viable) >= 2 and payload.get("combination_required", False): decision = "COMBINE_EXISTING_TOOLS"
        elif best.get("open_source", False) and best["score"] >= .48: decision = "EXTEND_OPEN_SOURCE"
        elif best.get("not_recommended", False): decision = "NOT_RECOMMENDED"
        else: decision = "BUILD_CUSTOM"
    gap = decision == "BUILD_CUSTOM" and not any(item.get("coverage", item["score"]) >= .8 for item in viable)
    reason = "Compared %d candidate(s) using declared weighted criteria." % len(scored)
    if gap: reason += " No candidate highly covers the requirements; this is a candidate requirement gap, not a proven market opportunity."
    return {"decision": decision, "candidate_gap": gap, "reason": reason, "candidates": scored}

def render_research_report(payload):
    result = decide_research(payload)
    lines = ["# Solution Research", "", "Research date: %s" % payload.get("search_date", utc_now()[:10]), "", "## Conclusion", "", "`%s`" % result["decision"], "", result["reason"], "", "## Candidate matrix", "", "| Name | Type | Score | Coverage | Official source | License | Maintenance | Recommendation |", "| --- | --- | ---: | ---: | --- | --- | --- | --- |"]
    for item in result.get("candidates", []):
        lines.append("| %s | %s | %.3f | %s | %s | %s | %s | %s |" % (item.get("name", "Unnamed"), item.get("type", "Unspecified"), item["score"], item.get("coverage", "Unverified"), item.get("official_source", "Unverified"), item.get("license", "Unverified"), item.get("maintenance", "Unverified"), item.get("recommendation", "Review")))
    if not result.get("candidates"): lines.append("| None verified | — | — | — | — | — | — | Research required |")
    for title, key in (("Queries", "queries"), ("Evidence sources", "sources"), ("Inferences", "inferences"), ("Unverified or potentially stale information", "unverified"), ("User decisions required", "user_decisions")):
        lines += ["", "## " + title, ""] + ["- %s" % item for item in payload.get(key, [])]
    if result["decision"] == "INSUFFICIENT_RESEARCH": lines += ["", "Live evidence is insufficient. No claim that a solution or market gap does not exist is permitted."]
    return "\n".join(lines).rstrip() + "\n", result
def normalized_content(path):
    try: text = Path(path).read_text(encoding="utf-8")
    except OSError as exc: raise IdeaToBuildError("Cannot read core file %s: %s" % (path, exc)) from exc
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")

def hash_path(path): return hashlib.sha256(normalized_content(path)).hexdigest()

def core_entries(root):
    base, entries = project_root(root), []
    for relative in CORE_FILES:
        path = base / relative
        if not path.is_file(): raise IdeaToBuildError("Core file is missing: %s" % relative)
        content = normalized_content(path)
        entries.append({"path": relative, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
    return entries

def aggregate_core_hash(entries):
    material = "".join("%s:%s\n" % (item["path"], item["sha256"]) for item in entries)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()

def verify_core(root):
    base = project_root(root); lock_path = base / ".idea-to-build" / "core.lock.json"
    if not lock_path.is_file(): return {"schema_version": 1, "ok": False, "status": "NOT_FROZEN", "mismatches": ["core.lock.json is missing"]}
    lock = ensure_supported_schema(load_json(lock_path), "core lock")
    if lock.get("template_only"): return {"schema_version": 1, "ok": False, "status": "NOT_FROZEN", "mismatches": ["core lock is a template marker"]}
    expected = lock.get("files")
    if not isinstance(expected, list): raise IdeaToBuildError("core lock files must be an array")
    mismatches, actual_entries = [], []
    for item in expected:
        relative = item.get("path") if isinstance(item, dict) else None
        if relative not in CORE_FILES: mismatches.append("Unexpected locked path: %s" % relative); continue
        path = base / str(relative)
        if not path.is_file(): mismatches.append("Missing: %s" % relative); continue
        actual_hash = hash_path(path); actual_entries.append({"path": relative, "sha256": actual_hash})
        if actual_hash != item.get("sha256"): mismatches.append("Hash mismatch: %s" % relative)
    if {item.get("path") for item in expected if isinstance(item, dict)} != set(CORE_FILES): mismatches.append("Locked core file set differs from the required set")
    aggregate = aggregate_core_hash(actual_entries) if len(actual_entries) == len(CORE_FILES) else None
    if aggregate != lock.get("core_hash"): mismatches.append("Aggregate core hash mismatch")
    mismatches = list(dict.fromkeys(mismatches))
    return {"schema_version": 1, "ok": not mismatches, "status": "VERIFIED" if not mismatches else "MISMATCH", "core_hash": aggregate, "mismatches": mismatches}

def _run_git(root, arguments, check=True):
    return subprocess.run(["git", "-C", str(root)] + list(arguments), text=True, capture_output=True, check=check)

def git_commit_paths(root, paths, message):
    base = project_root(root)
    try:
        _run_git(base, ["rev-parse", "--is-inside-work-tree"])
        _run_git(base, ["add", "--"] + list(paths))
        status_result = _run_git(base, ["diff", "--cached", "--quiet"], check=False)
        if status_result.returncode == 0:
            current = _run_git(base, ["rev-parse", "HEAD"], check=False)
            return current.stdout.strip() if current.returncode == 0 else "NO_CHANGES"
        commit = _run_git(base, ["commit", "-m", message], check=False)
        if commit.returncode != 0: raise IdeaToBuildError("Git commit failed: %s" % (commit.stderr.strip() or commit.stdout.strip()))
        return _run_git(base, ["rev-parse", "HEAD"]).stdout.strip()
    except FileNotFoundError as exc: raise IdeaToBuildError("Git is required but was not found") from exc
    except subprocess.CalledProcessError as exc: raise IdeaToBuildError("Git command failed: %s" % (exc.stderr.strip() or exc.stdout.strip())) from exc

def confirm_core(root, statement):
    normalized = statement.strip().lower()
    if not any(token in normalized for token in ("confirm", "freeze", "approved", "确认", "冻结", "按此开发")): raise IdeaToBuildError("Confirmation statement must explicitly approve or freeze the core preview")
    readiness = check_readiness(root)
    if not readiness["ready"]: raise IdeaToBuildError("Requirements are not ready: %s" % "; ".join(readiness["blockers"]))
    state = load_state(root)
    if state["current_phase"] not in ("REQUIREMENTS_READY", "CORE_REVIEW"): raise IdeaToBuildError("Core confirmation is allowed only during REQUIREMENTS_READY or CORE_REVIEW")
    state["current_phase"] = "CORE_REVIEW"
    state["core_confirmation"] = {"confirmed": True, "statement": statement.strip(), "confirmed_at": utc_now(), "actor": "human"}
    save_state(root, state); return state

def freeze_core(root, commit=True, tag=None, readonly=True):
    base, state = project_root(root), load_state(root)
    if state.get("core_frozen"): raise IdeaToBuildError("Core is already frozen; use the human change-request process")
    readiness = check_readiness(base)
    if not readiness["ready"]: raise IdeaToBuildError("Requirements are not ready: %s" % "; ".join(readiness["blockers"]))
    confirmation = state.get("core_confirmation")
    if not isinstance(confirmation, dict) or not confirmation.get("confirmed") or confirmation.get("actor") != "human": raise IdeaToBuildError("Explicit human confirmation is required before core freeze")
    entries = core_entries(base); aggregate = aggregate_core_hash(entries)
    try: previous_commit = _run_git(base, ["rev-parse", "HEAD"], check=False).stdout.strip() or None
    except FileNotFoundError: previous_commit = None
    lock = {"schema_version": 1, "frozen_at": utc_now(), "confirmation": confirmation, "normalization": "UTF-8 with CRLF and CR normalized to LF for hashing; source text is not rewritten", "hash_algorithm": "SHA-256", "files": entries, "core_hash": aggregate}
    write_json(base / ".idea-to-build" / "core.lock.json", lock)
    state.update({"core_frozen": True, "core_hash": aggregate, "current_phase": "CORE_FROZEN", "last_verified_commit": previous_commit}); save_state(base, state)
    if readonly:
        for relative in CORE_FILES:
            try: os.chmod(str(base / relative), stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
            except OSError as exc: raise IdeaToBuildError("Read-only protection failed for %s: %s" % (relative, exc)) from exc
    commit_hash = None
    if commit:
        commit_hash = git_commit_paths(base, list(CORE_FILES) + [".idea-to-build/core.lock.json", ".idea-to-build/project_state.json"], "chore(core): freeze approved baseline")
        if tag:
            tagged = _run_git(base, ["tag", "-a", tag, "-m", "Approved core baseline"], check=False)
            if tagged.returncode != 0: raise IdeaToBuildError("Core commit succeeded but tag failed: %s" % tagged.stderr.strip())
    return {"schema_version": 1, "ok": True, "core_hash": aggregate, "commit": commit_hash, "files": entries}

def summarize_markdown(path, limit=900):
    path = Path(path)
    if not path.is_file(): return "Missing: %s" % path.name
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped.startswith("#") or stripped.startswith("-") or (stripped and not lines): lines.append(stripped)
        if sum(len(item) for item in lines) >= limit: break
    return "\n".join(lines)[:limit]

def render_context(root):
    base, state = project_root(root), load_state(root)
    verification = verify_core(base) if state.get("core_frozen") else {"ok": True, "status": "DRAFT_NOT_FROZEN", "mismatches": []}
    live_files = ("docs/live/STATUS.md", "docs/live/ROADMAP.md", "docs/live/DECISIONS.md", "docs/live/RISKS.md")
    lines = ["Idea-to-Build project: %s" % state["project_name"], "Phase: %s" % state["current_phase"], "Milestone: %s" % state.get("current_milestone"), "Core status: %s" % verification["status"], "Immutable rule: never modify docs/core/** or .idea-to-build/core.lock.json; use docs/live/CHANGE_REQUESTS.md.", "Required reads: AGENTS.md, all docs/core files, STATUS, ROADMAP, DECISIONS, RISKS, and the relevant ExecPlan."]
    for relative in CORE_FILES: lines += ["", "[%s]" % relative, summarize_markdown(base / relative)]
    for relative in live_files: lines += ["", "[%s]" % relative, summarize_markdown(base / relative, 650)]
    return {"schema_version": 1, "ok": bool(verification["ok"]), "verification": verification, "project_name": state["project_name"], "phase": state["current_phase"], "core_hash": state.get("core_hash"), "additional_context": "\n".join(lines), "source_files": ["AGENTS.md"] + list(CORE_FILES) + list(live_files)}
def _confirmed_requirement_lines(root):
    lines = []
    for item in load_ledger(root)["requirements"]:
        if item["status"] in ("confirmed", "assumed") and item.get("value") not in (None, ""):
            label = "User-confirmed fact" if item["status"] == "confirmed" else "Unverified assumption"
            lines.append("- **%s — %s:** %s" % (label, item["category"], item["value"]))
    return lines or ["- No ledger facts were available; generation should not have passed readiness."]

def generate_design_documents(root):
    base, state = project_root(root), load_state(root)
    if not state.get("core_frozen"): raise IdeaToBuildError("Core must be frozen before design document generation")
    verified = verify_core(base)
    if not verified["ok"]: raise IdeaToBuildError("Core verification failed: %s" % "; ".join(verified["mismatches"]))
    facts, output = _confirmed_requirement_lines(base), []
    for filename, spec in DESIGN_DOCS.items():
        title, sections = spec
        lines = ["# %s" % title, "", "Generated from frozen core hash `%s`." % state.get("core_hash"), "", "## Evidence labels", ""] + facts
        lines += ["", "## Immutable constraints", "", "- The files under `docs/core/` and their hash lock control this document."]
        for section in sections:
            lines += ["", "## %s" % section, "", "- **AI recommendation:** Elaborate only within the frozen constraints.", "- **Reversible default:** Prefer the simplest replaceable option until measured evidence requires more.", "- **Unverified assumption:** None may be promoted to a fact without a ledger update and, when core-affecting, human change control."]
        path = base / "docs" / "design" / filename; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8"); output.append(path.relative_to(base).as_posix())
    state["generated_documents"] = sorted(set(state.get("generated_documents", []) + output))
    if state["current_phase"] == "CORE_FROZEN": state["current_phase"] = "DOCUMENTS_GENERATED"
    save_state(base, state); return output

def normalize_owner_path(value):
    value = value.strip().replace("\\", "/")
    while value.startswith("./"): value = value[2:]
    value = re.sub(r"/+", "/", value).rstrip("/"); value = re.sub(r"/\*\*?$", "", value)
    if not value or value.startswith("../") or "/../" in ("/" + value + "/"): raise IdeaToBuildError("Invalid ownership path: %s" % value)
    if value == "docs/core" or value.startswith("docs/core/") or value == ".idea-to-build/core.lock.json": raise IdeaToBuildError("A workstream cannot own frozen core paths: %s" % value)
    return value

def ownership_overlaps(first, second):
    left, right = normalize_owner_path(first), normalize_owner_path(second)
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")

def merge_overlapping_workstreams(raw_streams):
    streams = []
    for index, raw in enumerate(raw_streams):
        if not isinstance(raw, dict): raise IdeaToBuildError("Every workstream must be an object")
        files = [normalize_owner_path(str(item)) for item in raw.get("files", [])]
        if not files: raise IdeaToBuildError("Workstream %s has no file ownership" % raw.get("name", index))
        streams.append({"name": str(raw.get("name") or "Workstream %d" % (index + 1)), "goal": str(raw.get("goal") or "Implement the assigned workstream"), "files": list(dict.fromkeys(files)), "dependencies": list(raw.get("dependencies", [])), "tests": list(raw.get("tests", []))})
    changed = True
    while changed:
        changed = False
        for left_index in range(len(streams)):
            for right_index in range(left_index + 1, len(streams)):
                left, right = streams[left_index], streams[right_index]
                if any(ownership_overlaps(a, b) for a in left["files"] for b in right["files"]):
                    streams[left_index] = {"name": "%s + %s" % (left["name"], right["name"]), "goal": "%s; %s" % (left["goal"], right["goal"]), "files": list(dict.fromkeys(left["files"] + right["files"])), "dependencies": list(dict.fromkeys(left["dependencies"] + right["dependencies"])), "tests": list(dict.fromkeys(left["tests"] + right["tests"]))}
                    del streams[right_index]; changed = True; break
            if changed: break
    if len(streams) > 5:
        head, tail = streams[:4], streams[4:]
        streams = head + [{"name": "Integrated remaining workstreams", "goal": "; ".join(item["goal"] for item in tail), "files": list(dict.fromkeys(path for item in tail for path in item["files"])), "dependencies": list(dict.fromkeys(dep for item in tail for dep in item["dependencies"])), "tests": list(dict.fromkeys(test for item in tail for test in item["tests"]))}]
    return streams

def slugify(value): return (re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:40] or "workstream")

def _thread_prompt(number, thread):
    writable = "\n".join("- `%s`" % item for item in thread["files"]) or "- No implementation files; coordinate only."
    tests = "\n".join("- `%s`" % item for item in thread.get("tests", [])) or "- Run the commands in `docs/core/ACCEPTANCE_BASELINE.md`."
    dependencies = ", ".join(thread.get("dependencies", [])) or "None"
    return """# Thread {number}: {name}

## Identity

You own only this workstream: {goal}

## Before editing

1. Locate the Git root and run `git status`.
2. Confirm the worktree is clean enough for this scoped work.
3. Read `AGENTS.md`, every file in `docs/core/`, `docs/live/STATUS.md`, `ROADMAP.md`, `DECISIONS.md`, `RISKS.md`, and the relevant ExecPlan in `plans/`.
4. Run `python scripts/verify_core.py --path .`.
5. Restate the controlling constraints in at most ten bullets.
6. Do not edit until these checks pass.

## Git rules

- Use branch `{branch}` in worktree `{worktree}`.
- Initialize Git only if absent; never start major work in an unexplained dirty tree.
- Use a separate worktree for parallel changes and stay within the ownership below.
- Commit each runnable, tested stable feature with an accurate message.
- Create a new branch before major refactoring; milestone tags are optional and human-reviewed.
- Never force-push, rewrite public history without approval, or use destructive reset to erase unknown changes.
- Prefer revert, recovery branches, or a known stable commit after failure.
- Never commit secrets, tokens, `.env`, or personal data.
- Run tests and core verification immediately before commit.

## File ownership

Writable:
{writable}

Read-only: `AGENTS.md`, live documents not assigned here, and other threads' owned paths.

Forbidden: `docs/core/**`, `.idea-to-build/core.lock.json`, protection hooks, and paths outside this repository.

Shared integration files must be proposed in the handoff and merged by Thread 0.

## Implementation scope

- Must complete: {goal}
- Must not complete: unrelated workstreams or a core-contract change.
- Dependencies: {dependencies}
- Before adding a production dependency, explain necessity, maintenance, license, security, privacy, deployment fit, lock-in, and replacement options.
- Preserve the API, open-source, and acceptance constraints in the frozen documents.

## Acceptance and test commands

{tests}
- `python scripts/verify_core.py --path .`

## Completion conditions

- The scoped feature runs and all required tests pass.
- Core hashes remain valid.
- Relevant live updates are proposed to the orchestrator.
- The stable work is committed.
- Report the commit hash, change summary, test results, and remaining risks.
- Never automatically modify or refreeze core documents.
""".format(number=number, name=thread["name"], goal=thread["goal"], branch=thread["branch"], worktree=thread["worktree"], writable=writable, dependencies=dependencies, tests=tests)
def plan_threads(root, workstreams=None):
    state = load_state(root); raw = list(workstreams if workstreams is not None else state.get("workstreams", []))
    if not raw: raw = [{"name": "Product implementation", "goal": "Implement the MVP", "files": ["src"], "tests": ["python -m unittest discover -s tests -v"]}]
    development = merge_overlapping_workstreams(raw)
    threads = [{"number": 0, "name": "Orchestrator, architecture, and integration", "goal": "Maintain the ExecPlan, coordinate ownership, integrate branches, and resolve cross-module decisions", "files": ["plans", "docs/live/DECISIONS.md", "docs/live/RISKS.md"], "dependencies": [], "tests": ["python scripts/verify_core.py --path ."], "merge_order": 0}]
    for index, stream in enumerate(development, start=1):
        thread = dict(stream); thread.update({"number": index, "merge_order": index}); threads.append(thread)
    quality_number = len(threads)
    if len(development) == 1:
        threads.append({"number": quality_number, "name": "Quality and release", "goal": "Validate tests, security, performance, regression, documentation, release, and rollback", "files": ["tests", "docs/live/STATUS.md", "docs/live/RELEASES.md"], "dependencies": [development[0]["name"]], "tests": ["python -m unittest discover -s tests -v", "python scripts/verify_core.py --path ."], "merge_order": quality_number})
    else:
        threads.append({"number": quality_number, "name": "Quality engineering", "goal": "Report test, integration, security, performance, regression, and core-consistency findings", "files": ["tests", "quality"], "dependencies": [item["name"] for item in development], "tests": ["python -m unittest discover -s tests -v", "python scripts/verify_core.py --path ."], "merge_order": quality_number})
        release_number = quality_number + 1
        threads.append({"number": release_number, "name": "Release and operations", "goal": "Complete release checks, documentation, migration, deployment, rollback, and release records", "files": ["docs/live/STATUS.md", "docs/live/RELEASES.md", "deploy"], "dependencies": ["Quality engineering"], "tests": ["python scripts/verify_core.py --path ."], "merge_order": release_number})
    project_slug = slugify(state["project_name"])
    for thread in threads:
        slug = slugify(thread["name"]); thread["branch"] = "codex/%02d-%s" % (thread["number"], slug); thread["worktree"] = "../%s-%02d-%s" % (project_slug, thread["number"], slug)
    return threads

def generate_handoff(root, workstreams=None):
    base, state = project_root(root), load_state(root)
    if not state.get("core_frozen"): raise IdeaToBuildError("Core must be frozen before generating a Codex handoff")
    verified = verify_core(base)
    if not verified["ok"]: raise IdeaToBuildError("Core verification failed: %s" % "; ".join(verified["mismatches"]))
    generated = generate_design_documents(base); state = load_state(base); threads = plan_threads(base, workstreams)
    lines = ["# Codex Development Handoff", "", "This project should use exactly **%d Codex threads**." % len(threads), "", "Frozen core hash: `%s`" % state.get("core_hash"), "", "## Merge sequence", "", "1. Thread 0 validates plans and ownership.", "2. Independent development branches merge in numeric order after their checks pass.", "3. Quality validates the integrated tree and reports findings.", "4. Release work merges last when present.", ""]
    prompt_dir = base / "codex" / "prompts"; prompt_dir.mkdir(parents=True, exist_ok=True)
    for old in prompt_dir.glob("[0-9][0-9]-*.md"): old.unlink()
    prompt_paths = []
    for thread in threads:
        lines += ["## Thread %d — %s" % (thread["number"], thread["name"]), "", "- Goal: %s" % thread["goal"], "- Branch: `%s`" % thread["branch"], "- Worktree: `%s`" % thread["worktree"], "- Writable ownership: %s" % ", ".join("`%s`" % item for item in thread["files"]), "- Inputs: AGENTS.md, frozen core, live status, risks, decisions, relevant ExecPlan", "- Outputs: scoped implementation or review evidence, a stable commit, and handoff summary", "- Dependencies: %s" % (", ".join(thread["dependencies"]) or "None"), "- Start condition: core verification passes and dependencies are available", "- Completion condition: tests pass, core remains valid, live updates are handed to Thread 0, and work is committed", "- Merge order: %d" % thread["merge_order"], ""]
        filename = "%02d-%s.md" % (thread["number"], slugify(thread["name"])); (prompt_dir / filename).write_text(_thread_prompt(thread["number"], thread), encoding="utf-8"); prompt_paths.append("codex/prompts/" + filename)
    (base / "codex" / "HANDOFF.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    state["planned_codex_threads"] = len(threads); state["generated_documents"] = sorted(set(state.get("generated_documents", []) + generated + ["codex/HANDOFF.md"] + prompt_paths)); state["current_phase"] = "CODEX_HANDOFF_READY"; save_state(base, state)
    return {"schema_version": 1, "thread_count": len(threads), "threads": threads, "handoff": "codex/HANDOFF.md", "prompts": prompt_paths}

def should_activate(text):
    normalized = text.strip().lower()
    negative = (r"\bfix (this |a )?bug\b", r"\bexplain (this |the )?code\b", r"\bimplement (this |a )?small feature\b", r"\brecommend (some )?software\b", r"只.*修复.*bug", r"解释.*代码", r"只.*推荐.*软件", r"随便.*聊.*创意", r"不.*验证.*开发")
    if any(re.search(pattern, normalized) for pattern in negative): return False
    intent = any(token in normalized for token in ("app idea", "application idea", "product idea", "tool idea", "software idea", "has this been built", "already exists", "buildable project", "requirements analysis", "plan with codex", "existing solution", "我有一个应用想法", "软件想法", "产品想法", "有没有人做过", "整理成可开发", "需求分析", "交给 codex 开发", "规划用 codex", "搜索有没有现成产品", "软件需求"))
    build_or_validate = any(token in normalized for token in ("build", "develop", "validate", "research", "requirements", "codex", "开发", "验证", "检索", "搜索", "需求", "可开发"))
    return intent and build_or_validate

def initialize_project(template_dir, scripts_dir, target, name, language="en", force=False, initialize_git=True, initial_commit=True):
    template, scripts, destination = project_root(template_dir), project_root(scripts_dir), project_root(target)
    destination.mkdir(parents=True, exist_ok=True); project_id, created_at = str(uuid.uuid4()), utc_now()
    replacements = {"{{PROJECT_NAME}}": name, "{{PROJECT_ID}}": project_id, "{{CREATED_AT}}": created_at}; created = []
    for source in sorted(template.rglob("*")):
        if not source.is_file(): continue
        relative = source.relative_to(template)
        if relative.as_posix() == ".idea-to-build/core.lock.json": continue
        output = destination / relative
        if output.exists() and not force: raise IdeaToBuildError("Refusing to overwrite existing project file: %s" % output)
        text = source.read_text(encoding="utf-8")
        for old, new in replacements.items(): text = text.replace(old, new)
        output.parent.mkdir(parents=True, exist_ok=True); output.write_text(text, encoding="utf-8"); created.append(relative.as_posix())
    state = load_state(destination); state["user_language"] = language; save_state(destination, state)
    write_json(destination / ".idea-to-build" / "requirements_ledger.json", new_requirements_ledger()); created.append(".idea-to-build/requirements_ledger.json")
    runtime_names = ("idea_to_build_lib.py", "project_state.py", "research_report.py", "requirements_check.py", "freeze_core.py", "verify_core.py", "render_context.py", "generate_handoff.py", "validate_package.py")
    for name_value in runtime_names:
        source, output = scripts / name_value, destination / "scripts" / name_value
        output.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(str(source), str(output)); created.append("scripts/" + name_value)
    commit_hash = None
    if initialize_git:
        if not (destination / ".git").exists():
            try: subprocess.run(["git", "init", str(destination)], text=True, capture_output=True, check=True)
            except (FileNotFoundError, subprocess.CalledProcessError) as exc: raise IdeaToBuildError("Failed to initialize Git: %s" % exc) from exc
        if initial_commit: commit_hash = git_commit_paths(destination, sorted(set(created)), "chore: initialize Idea-to-Build project")
    return {"schema_version": 1, "project_id": project_id, "path": str(destination), "created_files": sorted(set(created)), "initial_commit": commit_hash}

def validate_project_package(root):
    base = project_root(root)
    required = ["AGENTS.md", ".idea-to-build/project_state.json", ".idea-to-build/requirements_ledger.json"] + list(CORE_FILES) + ["docs/live/STATUS.md", "docs/live/ROADMAP.md", "docs/live/BACKLOG.md", "docs/live/DECISIONS.md", "docs/live/RISKS.md", "docs/live/RESEARCH.md", "docs/live/RELEASES.md", "docs/live/CHANGE_REQUESTS.md", "codex/HANDOFF.md", "scripts/idea_to_build_lib.py", "scripts/verify_core.py"]
    errors = ["Missing required project file: %s" % item for item in required if not (base / item).is_file()]
    try:
        state = load_state(base); load_ledger(base)
        if state.get("core_frozen"):
            verification = verify_core(base)
            if not verification["ok"]: errors.extend(verification["mismatches"])
    except IdeaToBuildError as exc: errors.append(str(exc))
    return {"schema_version": 1, "ok": not errors, "errors": errors}