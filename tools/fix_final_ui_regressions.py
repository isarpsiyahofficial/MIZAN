from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_final_ui_regressions.py <source-root>")
    root = Path(sys.argv[1]).resolve()

    expenses_path = root / "lib/screens/expenses_screen.dart"
    expenses = expenses_path.read_text(encoding="utf-8")
    expenses = replace_once(
        expenses,
        "import 'package:flutter/material.dart';",
        "import 'package:flutter/material.dart';\nimport 'package:flutter/rendering.dart';",
        "ScrollCacheExtent içe aktarımı",
    )
    expenses = replace_once(
        expenses,
        """    return ListView(
      key: const PageStorageKey('expenses'),
      padding: EdgeInsets.fromLTRB(padding, 18, padding, 110),""",
        """    return ListView(
      key: const PageStorageKey('expenses'),
      scrollCacheExtent: const ScrollCacheExtent.pixels(2400),
      padding: EdgeInsets.fromLTRB(padding, 18, padding, 110),""",
        "Giderler liste önbelleği",
    )
    expenses_path.write_text(expenses, encoding="utf-8")

    reports_path = root / "lib/screens/reports_screen.dart"
    reports = reports_path.read_text(encoding="utf-8")
    old_reports = """        const SizedBox(height: 18),
        _CurrentExpenseOverview(state: state, now: DateTime.now()),
        const SizedBox(height: 18),
        _ReportFilters(
          state: state,
          period: period,
          anchorDate: effectiveAnchor,
          availableMonths: availableMonths,
          availableYears: availableYears,
          selectedPersonIds: validPersonIds,
          status: status,
          onPeriodChanged: (value) => setState(() {
            period = value;
            if (value == ReportPeriod.monthly && availableMonths.isNotEmpty) {
              anchorDate = availableMonths.first;
            } else if (value == ReportPeriod.yearly &&
                availableYears.isNotEmpty) {
              anchorDate = DateTime(availableYears.first);
            }
          }),
          onAnchorChanged: (value) => setState(() => anchorDate = value),
          onPeoplePressed: () => _selectPeople(state),
          onStatusChanged: (value) => setState(() => status = value),
        ),
        const SizedBox(height: 12),"""
    new_reports = """        const SizedBox(height: 18),
        _ReportFilters(
          state: state,
          period: period,
          anchorDate: effectiveAnchor,
          availableMonths: availableMonths,
          availableYears: availableYears,
          selectedPersonIds: validPersonIds,
          status: status,
          onPeriodChanged: (value) => setState(() {
            period = value;
            if (value == ReportPeriod.monthly && availableMonths.isNotEmpty) {
              anchorDate = availableMonths.first;
            } else if (value == ReportPeriod.yearly &&
                availableYears.isNotEmpty) {
              anchorDate = DateTime(availableYears.first);
            }
          }),
          onAnchorChanged: (value) => setState(() => anchorDate = value),
          onPeoplePressed: () => _selectPeople(state),
          onStatusChanged: (value) => setState(() => status = value),
        ),
        const SizedBox(height: 12),
        _CurrentExpenseOverview(state: state, now: DateTime.now()),
        const SizedBox(height: 12),"""
    reports = replace_once(
        reports,
        old_reports,
        new_reports,
        "Rapor filtre ve güncel gider sırası",
    )
    reports_path.write_text(reports, encoding="utf-8")

    settings_path = root / "lib/screens/settings_screen.dart"
    settings = settings_path.read_text(encoding="utf-8")
    settings = replace_once(
        settings,
        "title: 'Etkin bildirim planı',",
        "title: 'Planlanan bildirim',",
        "Bildirim planı başlığı",
    )
    settings_path.write_text(settings, encoding="utf-8")

    forms_path = root / "lib/screens/record_form_dialogs.dart"
    forms = forms_path.read_text(encoding="utf-8")
    dropdowns = (
        (
            """        DropdownButtonFormField<BillKind>(
          initialValue: kind,
          decoration: const InputDecoration(labelText: 'Fatura türü'),""",
            """        DropdownButtonFormField<BillKind>(
          initialValue: kind,
          isExpanded: true,
          decoration: const InputDecoration(labelText: 'Fatura türü'),""",
            "Fatura türü seçicisi",
        ),
        (
            """        DropdownButtonFormField<BillScheduleMode>(
          key: const ValueKey('bill-schedule-mode'),
          initialValue: scheduleMode,
          decoration: const InputDecoration(labelText: 'Fatura düzeni'),""",
            """        DropdownButtonFormField<BillScheduleMode>(
          key: const ValueKey('bill-schedule-mode'),
          initialValue: scheduleMode,
          isExpanded: true,
          decoration: const InputDecoration(labelText: 'Fatura düzeni'),""",
            "Fatura düzeni seçicisi",
        ),
        (
            """        DropdownButtonFormField<RentEntryKind>(
          key: const ValueKey('rent-entry-kind'),
          initialValue: kind,
          decoration: const InputDecoration(labelText: 'Kayıt türü'),""",
            """        DropdownButtonFormField<RentEntryKind>(
          key: const ValueKey('rent-entry-kind'),
          initialValue: kind,
          isExpanded: true,
          decoration: const InputDecoration(labelText: 'Kayıt türü'),""",
            "Kira/taksit türü seçicisi",
        ),
    )
    for old, new, label in dropdowns:
        forms = replace_once(forms, old, new, label)

    forms = forms.replace(
        "DropdownMenuItem(value: item, child: Text(item.label)),",
        """DropdownMenuItem(
                value: item,
                child: Text(
                  item.label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),""",
    )
    forms_path.write_text(forms, encoding="utf-8")

    checks = {
        expenses_path: (
            "scrollCacheExtent: const ScrollCacheExtent.pixels(2400)",
        ),
        reports_path: ("_ReportFilters(", "_CurrentExpenseOverview("),
        settings_path: ("title: 'Planlanan bildirim'",),
        forms_path: ("DropdownButtonFormField<RentEntryKind>(", "isExpanded: true"),
    }
    missing: list[str] = []
    for path, tokens in checks.items():
        verified = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in verified:
                missing.append(f"{path.name}:{token}")
    if missing:
        raise SystemExit(f"Final UI koruma kapsamı eksik: {missing}")
    print("Gider, rapor, bildirim ve form responsive regresyonları düzeltildi.")


if __name__ == "__main__":
    main()
