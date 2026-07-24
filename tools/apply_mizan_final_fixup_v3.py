from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from apply_mizan_final_fixup_v2 import main as apply_v2

PATCH_SHA256 = "f7865407affbc950e9ed9f0699e6ebc06eb37f2ed5751ba34c3d03c9fad3578c"
PATCH_BASE64 = """
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
P17hSg4=
"""


def main() -> None:
    apply_v2()
    root = Path(sys.argv[1]).resolve()
    patch = zlib.decompress(base64.b64decode("".join(PATCH_BASE64.split())))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Final UI fixup SHA uyuşmuyor: {actual}")

    with tempfile.NamedTemporaryFile(suffix=".patch") as temp:
        temp.write(patch)
        temp.flush()
        subprocess.run(
            ["git", "apply", "--whitespace=nowarn", temp.name],
            cwd=root,
            check=True,
        )

    required = {
        "lib/screens/expenses_screen.dart": (
            "Günlük harcamalar",
            "firstVisibleGroup",
            "visibleGroups.skip(1)",
            "isExpanded: true",
        ),
        "lib/screens/record_form_dialogs.dart": (
            "rent-entry-kind",
            "isExpanded: true",
            "monthLabel(value)",
            "overflow: TextOverflow.ellipsis",
        ),
    }
    missing = []
    for relative, tokens in required.items():
        path = root / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        for token in tokens:
            if token not in text:
                missing.append(f"{relative}:{token}")
    expense_text = (root / "lib/screens/expenses_screen.dart").read_text(encoding="utf-8")
    for forbidden in ("ScrollCacheExtent", "scrollCacheExtent:"):
        if forbidden in expense_text:
            missing.append(f"lib/screens/expenses_screen.dart:forbidden={forbidden}")
    if missing:
        raise SystemExit(f"Final responsive kapsam eksik: {missing}")
    print("MİZAN final UI katmanı: gider başlığı/ilk gün görünürlüğü, arama ve form taşma koruması uygulandı.")


if __name__ == "__main__":
    main()
