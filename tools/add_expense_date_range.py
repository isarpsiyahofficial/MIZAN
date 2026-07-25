from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: add_expense_date_range.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/screens/expenses_screen.dart"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "enum _ExpensePeriod { thisMonth, days30, days90, all }",
        "enum _ExpensePeriod { thisMonth, days30, days90, custom, all }",
        "Gider dönem seçenekleri",
    )
    text = replace_once(
        text,
        """    _ExpensePeriod.days90 => 'Son 90 gün',
    _ExpensePeriod.all => 'Tümü',""",
        """    _ExpensePeriod.days90 => 'Son 90 gün',
    _ExpensePeriod.custom => 'Tarih aralığı',
    _ExpensePeriod.all => 'Tümü',""",
        "Gider dönem etiketleri",
    )
    text = replace_once(
        text,
        """  _ExpensePeriod period = _ExpensePeriod.thisMonth;
  ExpenseDaySort daySort = ExpenseDaySort.newest;""",
        """  _ExpensePeriod period = _ExpensePeriod.thisMonth;
  DateTime? customStart;
  DateTime? customEnd;
  ExpenseDaySort daySort = ExpenseDaySort.newest;""",
        "Özel tarih aralığı durumu",
    )
    text = replace_once(
        text,
        """    _ExpensePeriod.days90 => (
      start: dateOnly(now).subtract(const Duration(days: 89)),
      end: dateOnly(now),
    ),
    _ExpensePeriod.all => (start: null, end: null),""",
        """    _ExpensePeriod.days90 => (
      start: dateOnly(now).subtract(const Duration(days: 89)),
      end: dateOnly(now),
    ),
    _ExpensePeriod.custom => (
      start: customStart ?? DateTime(now.year, now.month),
      end: customEnd ?? dateOnly(now),
    ),
    _ExpensePeriod.all => (start: null, end: null),""",
        "Özel tarih aralığı hesabı",
    )
    text = replace_once(
        text,
        """                    for (final item in _ExpensePeriod.values)
                      ChoiceChip(
                        selected: period == item,
                        label: Text(item.label),
                        onSelected: (_) => setState(() {
                          period = item;
                          visibleGroupLimit = _pageSize;
                          expandedDays.clear();
                        }),
                      ),""",
        """                    for (final item in _ExpensePeriod.values)
                      ChoiceChip(
                        selected: period == item,
                        label: Text(item.label),
                        onSelected: (_) async {
                          if (item == _ExpensePeriod.custom) {
                            await _selectCustomRange(context);
                            return;
                          }
                          setState(() {
                            period = item;
                            visibleGroupLimit = _pageSize;
                            expandedDays.clear();
                            autoExpandTopDay = true;
                          });
                        },
                      ),""",
        "Gider dönem seçicileri",
    )
    marker = """  Future<void> _showCategoryManager(BuildContext context) async {"""
    method = """  Future<void> _selectCustomRange(BuildContext context) async {
    final today = dateOnly(DateTime.now());
    final initialStart = customStart ?? today.subtract(const Duration(days: 29));
    final initialEnd = customEnd ?? today;
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(today.year - 20),
      lastDate: DateTime(today.year + 20, 12, 31),
      initialDateRange: DateTimeRange(start: initialStart, end: initialEnd),
      helpText: 'Tarih aralığı seçin',
      cancelText: 'Vazgeç',
      confirmText: 'Uygula',
      saveText: 'Uygula',
    );
    if (!mounted || picked == null) return;
    setState(() {
      customStart = dateOnly(picked.start);
      customEnd = dateOnly(picked.end);
      period = _ExpensePeriod.custom;
      visibleGroupLimit = _pageSize;
      expandedDays.clear();
      autoExpandTopDay = true;
    });
  }

"""
    text = replace_once(text, marker, method + marker, "Tarih aralığı seçme metodu")
    path.write_text(text, encoding="utf-8")

    verified = path.read_text(encoding="utf-8")
    for token in (
        "_ExpensePeriod.custom",
        "Tarih aralığı",
        "showDateRangePicker",
        "customStart",
        "customEnd",
    ):
        if token not in verified:
            raise SystemExit(f"Gider tarih aralığı kapsamı eksik: {token}")
    print("Giderler ekranına güvenli özel tarih aralığı filtresi eklendi.")


if __name__ == "__main__":
    main()
