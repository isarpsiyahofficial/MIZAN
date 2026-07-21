from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_git_file(spec: str) -> str:
    result = subprocess.run(
        ["git", "show", spec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        raise SystemExit(f"Git source is empty: {spec}")
    return result.stdout


def _execute_source(source: str, virtual_name: str) -> None:
    namespace = {
        "__name__": "__main__",
        "__file__": str(ROOT / virtual_name),
        "__package__": None,
    }
    exec(compile(source, virtual_name, "exec"), namespace, namespace)


# The immediate parent contains the already-reviewed full Round 3 applier.
# Keeping it in Git history avoids duplicating or silently rewriting that layer.
original_applier = _read_git_file("HEAD^:tools/apply_round3_patch.py")
_execute_source(original_applier, "tools/apply_round3_patch_reviewed.py")

# The current head contains the narrowly scoped responsive/PDF output fixes.
final_fixes = _read_git_file("HEAD:tools/apply_round3_final_fixes.py")
_execute_source(final_fixes, "tools/apply_round3_final_fixes.py")

print("Reviewed Round 3 and final responsive/PDF fixes applied in order.")
