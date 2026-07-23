from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "f4cc34beca0e60f1abe37fc8786cc8bab294806c2bfc04b914ee0c7dc7bec0e6"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_automatic_notification_sync.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")

    parts_dir = Path(__file__).resolve().parents[1] / ".patch_parts" / "auto_notification"
    part_paths = sorted(parts_dir.glob("part*.txt"))
    if len(part_paths) != 9:
        raise SystemExit(f"Beklenen 9 patch parçası bulunamadı: {part_paths}")
    encoded = "".join(path.read_text(encoding="utf-8").strip() for path in part_paths)
    patch = zlib.decompress(base64.b64decode(encoded))
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

    test_path = root / "test/automatic_notification_sync_test.dart"
    test_text = test_path.read_text(encoding="utf-8")
    old_test = """    await controller.load();
    scheduler.permissionRequestCount = 0;
    scheduler.rescheduleCount = 0;

    await controller.setNotificationsEnabled(true);
"""
    new_test = """    await controller.load();
    scheduler.permissionGranted = false;
    scheduler.exactAlarmGranted = false;
    scheduler.permissionRequestCount = 0;
    scheduler.rescheduleCount = 0;

    await controller.setNotificationsEnabled(true);
"""
    if test_text.count(old_test) != 1:
        raise SystemExit("Otomatik izin test düzeltmesi için beklenen blok bulunamadı.")
    test_path.write_text(test_text.replace(old_test, new_test, 1), encoding="utf-8")

    controller = (root / "lib/controllers/mizan_controller.dart").read_text(encoding="utf-8")
    main_dart = (root / "lib/main.dart").read_text(encoding="utf-8")
    settings = (root / "lib/screens/settings_screen.dart").read_text(encoding="utf-8")
    notifications = (root / "lib/services/notification_service.dart").read_text(encoding="utf-8")
    tests = test_path.read_text(encoding="utf-8")

    required = [
        "_notificationSyncQueue",
        "requestMissingNotificationPermissions",
        "synchronizeNotificationsAfterSystemResume",
        "WidgetsBindingObserver",
        "AppLifecycleState.resumed",
        "Otomatik senkronizasyon",
        "AndroidScheduleMode.exactAllowWhileIdle",
        "ödeme saati kaydedilince plan ek onay olmadan otomatik yenilenir",
        "uygulama resumed olduğunda manuel butonsuz otomatik planlama yapar",
        "scheduler.permissionGranted = false",
        "scheduler.exactAlarmGranted = false",
    ]
    combined = controller + main_dart + settings + notifications + tests
    missing = [item for item in required if item not in combined]
    if missing:
        raise SystemExit(f"Otomatik bildirim senkronizasyonu eksik: {missing}")

    forbidden = [
        "Bildirimleri yeniden planla",
        "Bildirim izinlerini aç",
        "Dakik alarm iznini aç",
    ]
    present = [item for item in forbidden if item in settings]
    if present:
        raise SystemExit(f"Manuel onay/yenileme kontrolleri kaldırılmadı: {present}")

    print(f"Otomatik bildirim senkronizasyon patch uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
