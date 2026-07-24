from __future__ import annotations

import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: beklenen 1 eşleşme, bulunan {count}: {old[:80]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_dynamic_overdue_compile_fixes.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()

    replace_once(
        root / "lib/models/mizan_models.dart",
        "      anchor = dueDateForMonth(DateTime(anchor.year, anchor.month + 1));",
        """      final currentAnchor = anchor!;
      anchor = dueDateForMonth(
        DateTime(currentAnchor.year, currentAnchor.month + 1),
      );""",
    )

    replace_once(
        root / "lib/screens/record_form_dialogs.dart",
        "import '../core/formatters.dart';\n",
        "import '../core/formatters.dart';\nimport '../core/theme.dart';\n",
    )

    replace_once(
        root / "lib/screens/reports_screen.dart",
        "        _PersonDebtSection(details: report.personDebtDetails),",
        """        _PersonDebtSection(
          details: report.personDebtDetails,
          referenceDate: report.generatedAt,
        ),""",
    )
    replace_once(
        root / "lib/screens/reports_screen.dart",
        """class _PersonDebtSection extends StatelessWidget {
  const _PersonDebtSection({required this.details});
  final List<ReportPersonDebtDetail> details;""",
        """class _PersonDebtSection extends StatelessWidget {
  const _PersonDebtSection({
    required this.details,
    required this.referenceDate,
  });
  final List<ReportPersonDebtDetail> details;
  final DateTime referenceDate;""",
    )
    replace_once(
        root / "lib/screens/reports_screen.dart",
        """'• ${record.title} · ${shortDate(record.dueDate)} · ${recordTimingLabel(record, report.generatedAt)} · ${money(record.amount)}',""",
        """'• ${record.title} · ${shortDate(record.dueDate)} · ${recordTimingLabel(record, referenceDate)} · ${money(record.amount)}',""",
    )

    test_path = root / "test/overdue_calendar_tracking_test.dart"
    text = test_path.read_text(encoding="utf-8")
    text = text.replace("const CsvCodec()", "CsvCodec()")
    test_path.write_text(text, encoding="utf-8")

    print("Dinamik gecikme derleme düzeltmeleri uygulandı.")


if __name__ == "__main__":
    main()
