from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from apply_mizan_final_fixup_v2 import main as apply_v2

PATCH_SHA256 = "bb1a1fd6162b983ec96e3602fb33287d7af4a4af64d27403ad25702d2a8a1c55"
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
            "Arama sonucu",
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
