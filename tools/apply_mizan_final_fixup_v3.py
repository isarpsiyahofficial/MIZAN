from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from apply_mizan_final_fixup_v2 import main as apply_v2

PATCH_SHA256 = "1f8a86f6c29155db9de3101a624e7afdb81a43916f5963ee6e00f8af10c276b5"
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
            "if (!hasSearchQuery)",
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
    print("MİZAN final UI katmanı: gider arama odağı, ilk gün görünürlüğü ve fatura/kira form taşma koruması uygulandı.")


if __name__ == "__main__":
    main()
