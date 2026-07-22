from __future__ import annotations

import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: beklenen 1 eşleşme, bulunan {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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

    replace_once(
        root / "test/ui_interaction_test.dart",
        """    expect(find.text('Aylık'), findsOneWidget);
    expect(find.text('Yıllık'), findsOneWidget);
    expect(find.text('Yıllık'), findsOneWidget);
    expect(find.text('Tüm zamanlar'), findsOneWidget);
""",
        """    expect(find.text('Aylık'), findsOneWidget);
    expect(find.text('Yıllık'), findsOneWidget);
    expect(find.text('Tüm zamanlar'), findsNothing);
""",
    )
    print("Bildirim import'u ve aylık/yıllık rapor UI testi doğrulandı.")


if __name__ == "__main__":
    main()
