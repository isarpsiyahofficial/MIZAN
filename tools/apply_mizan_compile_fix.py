from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_mizan_compile_fix.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/services/notification_service.dart"
    text = path.read_text(encoding="utf-8")
    import_line = "import '../core/formatters.dart';\n"
    if import_line not in text:
        anchor = "import '../models/mizan_models.dart';\n"
        if anchor not in text:
            raise SystemExit("Bildirim servisi import noktası bulunamadı.")
        text = text.replace(anchor, import_line + anchor, 1)
        path.write_text(text, encoding="utf-8")
    if "stableNotificationId('mizan-exact-test-" not in path.read_text(encoding="utf-8"):
        raise SystemExit("Dakik test bildirim kimliği bulunamadı.")
    print("Bildirim kimliği yardımcı import'u doğrulandı.")


if __name__ == "__main__":
    main()
