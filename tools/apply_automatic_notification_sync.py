from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "f4cc34beca0e60f1abe37fc8786cc8bab294806c2bfc04b914ee0c7dc7bec0e6"
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
