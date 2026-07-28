from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "f04320adc91f3184eaefe1e79428a46c2e28f31f4aa4560e662ec697a963e87c"
EXPECTED_CHUNKS = 2


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Kullanım: apply_mizan_notification_reliability_final.py <source-root>"
        )
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"MİZAN kaynak kökü bulunamadı: {root}")

    chunk_dir = Path(__file__).resolve().parent / "notification_reliability_patch_chunks"
    chunks = sorted(chunk_dir.glob("chunk_*.txt"))
    if len(chunks) != EXPECTED_CHUNKS:
        raise SystemExit(f"Bildirim güvenilirlik patch parçaları eksik: {chunks}")
    encoded = "".join(chunk.read_text(encoding="utf-8").strip() for chunk in chunks)
    patch = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Bildirim güvenilirlik patch SHA uyuşmuyor: {actual}")

    with tempfile.NamedTemporaryFile(suffix=".patch") as handle:
        handle.write(patch)
        handle.flush()
        subprocess.run(
            ["patch", "--batch", "--forward", "-p1", "-i", handle.name],
            cwd=root,
            check=True,
        )

    required = {
        "lib/services/notification_service.dart": [
            "pendingNotificationRequests()",
            "desiredIds.difference(actualIds)",
            "_rescheduleTail",
        ],
        "lib/services/monthly_payment_status_service.dart": [
            "class MonthlyPaymentStatusService",
            "plannedAndPaidTotal",
        ],
        "lib/screens/dashboard_screen.dart": [
            "MonthlyPaymentStatusService",
            "Bu Ayın Ödeme Durumu",
        ],
        "android/app/src/main/AndroidManifest.xml": [
            "ExactAlarmPermissionReceiver",
            "SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED",
            "ScheduledNotificationBootReceiver",
        ],
        "android/app/src/main/java/com/dexterous/flutterlocalnotifications/ExactAlarmPermissionReceiver.java": [
            "canScheduleExactAlarms()",
            "rescheduleNotifications(context)",
        ],
        "test/notification_background_reliability_test.dart": [
            "37100",
            "hasLength(7)",
        ],
    }
    forbidden = {
        "lib/services/notification_service.dart": [
            "_scheduledSignatures",
            "_scheduleCachePrimed",
        ],
        "android/app/src/main/AndroidManifest.xml": [
            "android.permission.USE_FULL_SCREEN_INTENT",
            'android:showWhenLocked="true"',
            'android:turnScreenOn="true"',
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
    if problems:
        raise SystemExit(f"Bildirim güvenilirlik final kapsamı eksik: {problems}")
    print("MİZAN bildirim arka plan güvenilirliği ve Temmuz hesap denetimi yaması uygulandı.")


if __name__ == "__main__":
    main()
