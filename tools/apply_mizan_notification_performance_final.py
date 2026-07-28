from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "5ec622ed24bd3aff6d6cd3aeedc17dbec1acfb0a490c8043ac4812e2c4016d15"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Kullanım: apply_mizan_notification_performance_final.py <source-root>"
        )
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"MİZAN kaynak kökü bulunamadı: {root}")

    chunk_dir = Path(__file__).resolve().parent / "notification_performance_patch_chunks"
    chunks = sorted(chunk_dir.glob("chunk_*.txt"))
    if len(chunks) != 11:
        raise SystemExit(f"Bildirim-performans final patch parçaları eksik: {chunks}")
    encoded = "".join(chunk.read_text(encoding="utf-8").strip() for chunk in chunks)
    patch = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Bildirim-performans final patch SHA uyuşmuyor: {actual}")

    with tempfile.NamedTemporaryFile(suffix=".patch") as handle:
        handle.write(patch)
        handle.flush()
        subprocess.run(
            ["patch", "--batch", "--forward", "-p1", "-i", handle.name],
            cwd=root,
            check=True,
        )

    required = {
        "lib/screens/settings_screen.dart": [
            "Bildirim sistemi",
            "Dakik bildirim izni",
        ],
        "lib/services/notification_service.dart": [
            "_scheduledSignatures",
            "AndroidNotificationDetails",
            "exactAllowWhileIdle",
        ],
        "lib/services/reminder_engine.dart": [
            "safeMaximumConcurrentNotifications",
            "repeatsDaily",
        ],
        "lib/screens/dashboard_screen.dart": [
            "Bu Ayın Ödeme Durumu",
            "Açık planlanan ödemeler",
            "Bu ay yapılan ödemeler",
            "_dashboardDataCache",
        ],
        "lib/services/report_service.dart": [
            "realizedDistribution",
            "combinedOutflowDistribution",
            "upcomingDetails",
        ],
        "lib/screens/reports_screen.dart": [
            "Önümüzdeki 7 gün",
            "_reportNavigationCache",
            "childrenBuilder",
        ],
        "lib/services/pdf_report_service.dart": [
            "GÜN BAŞLIĞI",
            "_dayHeader",
        ],
        "test/notification_performance_report_final_test.dart": [
            "unitPrice: 27800",
            "['day-7']",
        ],
    }
    forbidden = {
        "lib/screens/settings_screen.dart": [
            "Planlanan bildirim",
            "Alarm sesi",
            "Alarm tekrar",
        ],
        "lib/services/notification_service.dart": [
            "fullScreenIntent: true",
            "AudioAttributesUsage.alarm",
            "ongoing: true",
        ],
        "lib/models/mizan_models.dart": [
            "enum NotificationPresentationMode",
            "enum AlarmRepeatMode",
        ],
    }
    problems: list[str] = []
    for relative, tokens in required.items():
        source = (root / relative).read_text(encoding="utf-8")
        for token in tokens:
            if token not in source:
                problems.append(f"{relative}: eksik {token}")
    for relative, tokens in forbidden.items():
        source = (root / relative).read_text(encoding="utf-8")
        for token in tokens:
            if token in source:
                problems.append(f"{relative}: yasak kalıntı {token}")
    if (root / "test/alarm_regression_test.dart").exists():
        problems.append("test/alarm_regression_test.dart kaldırılmamış")
    if problems:
        raise SystemExit(f"Bildirim-performans final kapsamı eksik: {problems}")
    print("MİZAN bildirim, performans, aylık ödeme, rapor ve PDF final yaması uygulandı.")


if __name__ == "__main__":
    main()
