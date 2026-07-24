from __future__ import annotations

import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Beklenen tek eşleşme bulunamadı: {path}: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_manual_overdue_test_fixes.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()

    replace_once(
        root / "lib/screens/record_form_dialogs.dart",
        "        TextFormField(\n          controller: manualOverdueDays,",
        "        TextFormField(\n          key: const Key('manual-overdue-days-field'),\n          controller: manualOverdueDays,",
    )
    replace_once(
        root / "test/overdue_calendar_tracking_test.dart",
        "    final today = dateOnly(DateTime.now());",
        "    final now = DateTime.now();\n    final today = DateTime(now.year, now.month, now.day);",
    )
    replace_once(
        root / "test/manual_overdue_edit_confirmation_test.dart",
        "    final manualField = find.byWidgetPredicate(\n      (widget) =>\n          widget is TextFormField &&\n          widget.decoration?.labelText == 'Yeni manuel gecikme günü (opsiyonel)',\n    );",
        "    final manualField = find.byKey(const Key('manual-overdue-days-field'));",
    )

    print("Manuel gecikme test seçicileri ve tarih normalizasyonu düzeltildi.")


if __name__ == "__main__":
    main()
