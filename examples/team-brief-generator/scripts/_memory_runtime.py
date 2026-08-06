"""Load repository-memory APIs from the canonical runtime or a migration fallback."""
from __future__ import print_function
import importlib.util
from pathlib import Path

_REQUIRED = (
    "load_tasks", "load_quality_gates", "memory_prompt", "migrate_project",
    "quality_status", "run_quality_gate", "transition_task",
)


def _load_runtime():
    import idea_to_build_lib as candidate
    if all(hasattr(candidate, name) for name in _REQUIRED):
        return candidate
    fallback = Path(__file__).resolve().with_name("idea_to_build_memory_runtime.py")
    if not fallback.is_file() or fallback.is_symlink():
        raise ImportError(
            "This project has a legacy Idea-to-Build runtime. Run the current Plugin "
            "migrate_project.py with --apply to add the non-overwriting compatibility runtime."
        )
    spec = importlib.util.spec_from_file_location("idea_to_build_memory_runtime", str(fallback))
    if spec is None or spec.loader is None:
        raise ImportError("Cannot load the Idea-to-Build repository-memory compatibility runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not all(hasattr(module, name) for name in _REQUIRED):
        raise ImportError("The Idea-to-Build compatibility runtime is incomplete")
    return module


runtime = _load_runtime()