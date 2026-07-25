from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_expense_day_numeric_date.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/services/expense_browser_service.dart"
    text = path.read_text(encoding="utf-8")
    old = """  String dayLabel(DateTime value) =>
      '${shortDate(value)} ${weekdayLabel(value)}';"""
    new = """  String dayLabel(DateTime value) =>
      '${value.day.toString().padLeft(2, '0')}.${value.month.toString().padLeft(2, '0')}.${value.year} ${weekdayLabel(value)}';"""
    if old not in text:
        raise SystemExit("Gider gün başlığı tarih biçimi bulunamadı.")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    verified = path.read_text(encoding="utf-8")
    if ".${value.year} ${weekdayLabel(value)}" not in verified:
        raise SystemExit("Sayısal gider gün başlığı doğrulanamadı.")
    print("Gider gün başlığı gg.aa.yyyy ve Türkçe gün adı biçimine sabitlendi.")


if __name__ == "__main__":
    main()
