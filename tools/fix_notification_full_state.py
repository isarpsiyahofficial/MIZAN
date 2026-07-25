from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_notification_full_state.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/controllers/mizan_controller.dart"
    text = path.read_text(encoding="utf-8")
    start = text.index("  Future<void> _synchronizeNotifications(")
    end = text.index("  Future<void> synchronizeNotificationsAfterSystemResume()", start)
    block = text[start:end]
    old_block = block
    block = block.replace("    final snapshot = _notificationSnapshot(state);\n", "")
    block = block.replace("snapshot.notificationsEnabled", "state.notificationsEnabled")
    block = block.replace("_requiresAlarmPresentation(snapshot)", "_requiresAlarmPresentation(state)")
    block = block.replace("await _scheduler.reschedule(snapshot);", "await _scheduler.reschedule(state);")
    if block == old_block:
        raise SystemExit("Bildirim senkronizasyonunda tam state düzeltme alanı bulunamadı.")
    if "snapshot" in block:
        raise SystemExit("Bildirim senkronizasyonunda eksik snapshot kullanımı kaldı.")
    text = text[:start] + block + text[end:]
    path.write_text(text, encoding="utf-8")
    verified = path.read_text(encoding="utf-8")
    if "await _scheduler.reschedule(state);" not in verified:
        raise SystemExit("Bildirim planlayıcısına tam state gönderimi doğrulanamadı.")
    print("Bildirim karşılaştırma özeti korunurken planlayıcıya tam kayıt durumu gönderiliyor.")


if __name__ == "__main__":
    main()
