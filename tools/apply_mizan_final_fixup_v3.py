from __future__ import annotations

import sys
from pathlib import Path

from apply_mizan_final_fixup_v2 import main as apply_v2


def main() -> None:
    apply_v2()
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/screens/expenses_screen.dart"
    text = path.read_text(encoding="utf-8")

    dropdown_old = """                DropdownButtonFormField<ExpenseDaySort>(
                  key: const ValueKey('expense-day-sort'),
                  initialValue: daySort,"""
    dropdown_new = """                DropdownButtonFormField<ExpenseDaySort>(
                  key: const ValueKey('expense-day-sort'),
                  isExpanded: true,
                  initialValue: daySort,"""
    if dropdown_old not in text:
        raise SystemExit("Gider sıralama seçicisi bulunamadı.")
    text = text.replace(dropdown_old, dropdown_new, 1)

    item_old = """                    for (final item in ExpenseDaySort.values)
                      DropdownMenuItem(value: item, child: Text(item.label)),"""
    item_new = """                    for (final item in ExpenseDaySort.values)
                      DropdownMenuItem(
                        value: item,
                        child: Text(
                          item.label,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),"""
    if item_old not in text:
        raise SystemExit("Gider sıralama seçenekleri bulunamadı.")
    text = text.replace(item_old, item_new, 1)
    path.write_text(text, encoding="utf-8")

    verified = path.read_text(encoding="utf-8")
    for token in ("isExpanded: true", "overflow: TextOverflow.ellipsis"):
        if token not in verified:
            raise SystemExit(f"Responsive gider seçicisi eksik: {token}")
    print("MİZAN final fixup v3 responsive katmanı uygulandı.")


if __name__ == "__main__":
    main()
