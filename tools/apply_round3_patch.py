from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "agent/mizan-safe-clear-ui-v2"
REVIEWED_APPLIER_COMMIT = "f59a39ae303acc1da22f58250066dda1c5aadf68"


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


# Pull-request checkouts are shallow. Fetch only enough branch history to read
# the immutable reviewed Round 3 applier commit.
subprocess.run(
    ["git", "fetch", "--deepen=4", "origin", BRANCH],
    cwd=ROOT,
    check=True,
)

original_applier = _read_git_file(
    f"{REVIEWED_APPLIER_COMMIT}:tools/apply_round3_patch.py"
)
_execute_source(original_applier, "tools/apply_round3_patch_reviewed.py")

final_fixes = _read_git_file("HEAD:tools/apply_round3_final_fixes.py")
_execute_source(final_fixes, "tools/apply_round3_final_fixes.py")

print("Reviewed Round 3 and final responsive/PDF fixes applied in order.")
