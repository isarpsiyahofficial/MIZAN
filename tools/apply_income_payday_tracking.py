from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "cf055454ed6c088ca7fc1c9e61c2681b4e04ba3c0f43f2393b168ed2f17d3505"
PATCH_ZLIB_BASE64 = "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"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_income_payday_tracking.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")

    patch = zlib.decompress(base64.b64decode(PATCH_ZLIB_BASE64))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Patch SHA uyuşmuyor: {actual} != {PATCH_SHA256}")

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    with tempfile.NamedTemporaryFile(suffix=".patch", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        subprocess.run(["git", "apply", "--check", str(patch_path)], cwd=root, check=True)
        subprocess.run(
            ["git", "apply", "--whitespace=nowarn", str(patch_path)],
            cwd=root,
            check=True,
        )
    finally:
        patch_path.unlink(missing_ok=True)

    required = {
        "lib/models/mizan_models.dart": [
            "class IncomeReceipt",
            "scheduleTrackingEnabled",
            "trackedOccurrenceAt",
            "daysUntilTrackedOccurrence",
        ],
        "lib/controllers/mizan_controller.dart": [
            "markIncomeReceived",
            "undoLatestIncomeReceipt",
            "_validateIncomeTracking",
        ],
        "lib/screens/dashboard_screen.dart": [
            "Yatış gününü takip et",
            "Her ayın kaçında yatıyor?",
            "Haftanın hangi günü yatıyor?",
            "Gelir yattı",
            "Sabit yatış günü değişmedi",
        ],
        "lib/services/csv_backup_service.dart": [
            "_mergeIncome",
            "receipts",
        ],
        "test/income_payday_tracking_test.dart": [
            "geç alınan maaş gerçek tarihi kaydeder ancak sabit günü değiştirmez",
            "CSV birleştirme gelir alınma geçmişini çoğaltmadan korur",
        ],
    }
    for relative, needles in required.items():
        text = (root / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise SystemExit(f"Zorunlu gelir takibi öğesi eksik: {relative}: {needle}")

    print(f"Gelir yatış günü takibi uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
