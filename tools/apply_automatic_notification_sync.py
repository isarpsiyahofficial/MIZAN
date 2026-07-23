from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "1214cf21c40f38be65a0e1aab572f9abb82403e720f048def53f5510c2c2ea3e"
PATCH_ZLIB_BASE64 = "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"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_automatic_notification_sync.py <kaynak-kökü>")
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

    controller = (root / "lib/controllers/mizan_controller.dart").read_text(encoding="utf-8")
    main_dart = (root / "lib/main.dart").read_text(encoding="utf-8")
    settings = (root / "lib/screens/settings_screen.dart").read_text(encoding="utf-8")
    notifications = (root / "lib/services/notification_service.dart").read_text(encoding="utf-8")
    tests = (root / "test/automatic_notification_sync_test.dart").read_text(encoding="utf-8")

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
