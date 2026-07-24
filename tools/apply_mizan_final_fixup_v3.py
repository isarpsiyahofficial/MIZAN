from __future__ import annotations

import sys
from pathlib import Path

from apply_mizan_final_fixup_v2 import main as apply_v2


def _replace_once(text: str, old: str, new: str, message: str) -> str:
    if old not in text:
        raise SystemExit(message)
    return text.replace(old, new, 1)


def main() -> None:
    apply_v2()
    root = Path(sys.argv[1]).resolve()

    expense_path = root / "lib/screens/expenses_screen.dart"
    expense_text = expense_path.read_text(encoding="utf-8")
    expense_text = _replace_once(
        expense_text,
        "import 'package:flutter/material.dart';\n",
        "import 'package:flutter/material.dart';\n"
        "import 'package:flutter/rendering.dart' show ScrollCacheExtent;\n",
        "Flutter gider ekranı import alanı bulunamadı.",
    )
    expense_text = _replace_once(
        expense_text,
        """    return ListView(
      key: const PageStorageKey('expenses'),
      padding: EdgeInsets.fromLTRB(padding, 18, padding, 110),""",
        """    return ListView(
      key: const PageStorageKey('expenses'),
      scrollCacheExtent: const ScrollCacheExtent.pixels(2400),
      padding: EdgeInsets.fromLTRB(padding, 18, padding, 110),""",
        "Gider listesi bulunamadı.",
    )
    expense_text = _replace_once(
        expense_text,
        """                DropdownButtonFormField<ExpenseDaySort>(
                  key: const ValueKey('expense-day-sort'),
                  initialValue: daySort,""",
        """                DropdownButtonFormField<ExpenseDaySort>(
                  key: const ValueKey('expense-day-sort'),
                  isExpanded: true,
                  initialValue: daySort,""",
        "Gider sıralama seçicisi bulunamadı.",
    )
    expense_text = _replace_once(
        expense_text,
        """                    for (final item in ExpenseDaySort.values)
                      DropdownMenuItem(value: item, child: Text(item.label)),""",
        """                    for (final item in ExpenseDaySort.values)
                      DropdownMenuItem(
                        value: item,
                        child: Text(
                          item.label,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),""",
        "Gider sıralama seçenekleri bulunamadı.",
    )
    expense_path.write_text(expense_text, encoding="utf-8")

    forms_path = root / "lib/screens/record_form_dialogs.dart"
    forms_text = forms_path.read_text(encoding="utf-8")
    forms_text = _replace_once(
        forms_text,
        """  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
    onPressed: onTap,
    icon: const Icon(Icons.calendar_month_outlined),
    label: Align(
      alignment: Alignment.centerLeft,
      child: Text('$label: ${monthLabel(value)}'),
    ),
  );""",
        """  @override
  Widget build(BuildContext context) => OutlinedButton(
    onPressed: onTap,
    style: OutlinedButton.styleFrom(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      alignment: Alignment.centerLeft,
    ),
    child: Row(
      children: [
        const Icon(Icons.calendar_month_outlined),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.labelMedium,
              ),
              const SizedBox(height: 2),
              Text(
                monthLabel(value),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
            ],
          ),
        ),
      ],
    ),
  );""",
        "Aylık dönem seçicisi bulunamadı.",
    )
    forms_path.write_text(forms_text, encoding="utf-8")

    checks = {
        expense_path: (
            "show ScrollCacheExtent",
            "scrollCacheExtent: const ScrollCacheExtent.pixels(2400)",
            "isExpanded: true",
            "overflow: TextOverflow.ellipsis",
        ),
        forms_path: (
            "Text(\n                label,",
            "Expanded(\n          child: Column(",
            "monthLabel(value)",
        ),
    }
    missing = []
    for path, tokens in checks.items():
        verified = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in verified:
                missing.append(f"{path.name}:{token}")
    if missing:
        raise SystemExit(f"Final responsive kapsam eksik: {missing}")
    print("MİZAN final fixup v3 gider görünürlüğü ve aylık alan taşma korumasıyla uygulandı.")


if __name__ == "__main__":
    main()
