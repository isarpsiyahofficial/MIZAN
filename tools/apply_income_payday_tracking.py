from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "cf055454ed6c088ca7fc1c9e61c2681b4e04ba3c0f43f2393b168ed2f17d3505"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_income_payday_tracking.py <kaynak-kökü>")
    repository_root = Path(__file__).resolve().parents[1]
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")

    chunk_dir = repository_root / "income_payday_patch_chunks"
    encoded = "".join(
        path.read_text(encoding="utf-8").strip()
        for path in sorted(chunk_dir.glob("chunk*.txt"))
    )
    if not encoded:
        raise SystemExit("Gelir yatış günü patch parçaları bulunamadı.")
    patch = zlib.decompress(base64.b64decode(encoded))
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
        "lib/services/csv_backup_service.dart": ["_mergeIncome", "receipts"],
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
