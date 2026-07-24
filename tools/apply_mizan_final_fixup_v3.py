from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from apply_mizan_final_fixup_v2 import main as apply_v2

PATCH_SHA256 = "dff3287404e628b0c90b26402cba23a5a9b80a025a7603d97dbe3b31345b7f64"
PATCH_BASE64 = """
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
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
            "hasSearchQuery",
            "visibleGroups.skip(1)",
            "isExpanded: true",
        ),
        "lib/screens/record_form_dialogs.dart": (
            "rent-entry-kind",
            "bill-schedule-mode",
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
    print("MİZAN final UI katmanı: gider araması, ilk gün görünürlüğü ve fatura/kira form taşma koruması uygulandı.")


if __name__ == "__main__":
    main()
