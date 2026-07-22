from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "d93919662b63f3704899cea15017b58b1637ffd9daae1baa8b11de021333633e"
PATCH_ZLIB_BASE64 = "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"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_report_alltime_notification_ui.py <kaynak-kökü>")
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
        subprocess.run(
            ["git", "apply", "--whitespace=nowarn", str(patch_path)],
            cwd=root,
            check=True,
        )
    finally:
        patch_path.unlink(missing_ok=True)

    reports = (root / "lib/screens/reports_screen.dart").read_text(encoding="utf-8")
    settings = (root / "lib/screens/settings_screen.dart").read_text(encoding="utf-8")
    tests = "\n".join(
        (root / path).read_text(encoding="utf-8")
        for path in [
            "test/report_service_test.dart",
            "test/ui_interaction_test.dart",
            "test/responsive_test.dart",
        ]
    )
    required = [
        "ReportPeriod.allTime",
        "Tüm kayıt geçmişi",
        "Bildirim ve alarm sistemi",
        "Bildirim türü",
        "SegmentedButton<NotificationPresentationMode>",
        "1 dakika sonra test bildirimi",
        "tüm zamanlarda kişi ve kalan durum filtreleri birlikte çalışır",
        "320x568 bildirim ayrıntısı taşmasız açılır",
    ]
    combined = reports + settings + tests
    missing = [needle for needle in required if needle not in combined]
    if missing:
        raise SystemExit(f"Rapor/bildirim UI düzeltmesi eksik: {missing}")
    if "class _ModeChoice" in settings or "class _StatusBadge" in settings:
        raise SystemExit("Eski karmaşık bildirim seçim bileşenleri kaldırılmadı.")

    print(f"Rapor ve bildirim UI patch uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
