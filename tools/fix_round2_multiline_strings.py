from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; ikinci tur kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_round2_multiline_strings.py <source-root>")
    root = Path(sys.argv[1]).resolve()

    expenses_path = root / "lib/screens/expenses_screen.dart"
    expenses = expenses_path.read_text(encoding="utf-8")
    expenses = replace_once(
        expenses,
        """import '../widgets/mizan_cards.dart';""",
        """import '../widgets/mizan_cards.dart';
import 'people_screen.dart';""",
        "Gider kayıt ayrıntısı içe aktarımı",
    )
    expenses = replace_once(
        expenses,
        """                    subtitle:
                        '${_paymentRecordLabel(detail.type)} · ${detail.recordSubtitle}${detail.payment.note.trim().isEmpty ? '' : '
${detail.payment.note.trim()}'}',""",
        """                    subtitle:
                        '${_paymentRecordLabel(detail.type)} · ${detail.recordSubtitle}${detail.payment.note.trim().isEmpty ? '' : '\\n${detail.payment.note.trim()}'}',""",
        "Gider ödeme açıklaması",
    )
    expenses_path.write_text(expenses, encoding="utf-8")

    people_path = root / "lib/screens/people_screen.dart"
    people = people_path.read_text(encoding="utf-8")
    people = replace_once(
        people,
        "icon: recordIcon(row.type),",
        "icon: _recordTypeIcon(row.type),",
        "Kişi metrik ayrıntısı kayıt simgesi",
    )
    people_path.write_text(people, encoding="utf-8")

    reports_path = root / "lib/screens/reports_screen.dart"
    reports = reports_path.read_text(encoding="utf-8")
    reports = replace_once(
        reports,
        """                                subtitle:
                                    '${record.subtitle}
${shortDate(record.dueDate)} · ${recordTimingLabel(record, referenceDate)}',""",
        """                                subtitle:
                                    '${record.subtitle}\\n${shortDate(record.dueDate)} · ${recordTimingLabel(record, referenceDate)}',""",
        "Rapor kayıt açıklaması",
    )
    reports_path.write_text(reports, encoding="utf-8")

    pdf_path = root / "lib/services/pdf_report_service.dart"
    pdf = pdf_path.read_text(encoding="utf-8")
    pdf = replace_once(
        pdf,
        """            subtitle:
                '${decimalText(detail.expense.quantity)} × ${money(detail.expense.unitPrice)}${note == null ? '' : '
Not: $note'}',""",
        """            subtitle:
                '${decimalText(detail.expense.quantity)} × ${money(detail.expense.unitPrice)}${note == null ? '' : '\\nNot: $note'}',""",
        "PDF günlük gider notu",
    )
    pdf = replace_once(
        pdf,
        """          await _keyValue(
            '${detail.personName} · ${_typeLabel(detail.type)}
${detail.recordTitle}',""",
        """          await _keyValue(
            '${detail.personName} · ${_typeLabel(detail.type)}\\n${detail.recordTitle}',""",
        "PDF ödeme başlığı",
    )
    pdf = replace_once(
        pdf,
        """            subtitle:
                '${detail.payment.entryType.label}$method · ${detail.recordSubtitle}${note == null ? '' : '
Not: $note'}',""",
        """            subtitle:
                '${detail.payment.entryType.label}$method · ${detail.recordSubtitle}${note == null ? '' : '\\nNot: $note'}',""",
        "PDF ödeme notu",
    )
    pdf_path.write_text(pdf, encoding="utf-8")

    cards_path = root / "lib/widgets/mizan_cards.dart"
    cards = cards_path.read_text(encoding="utf-8")
    cards = replace_once(
        cards,
        """              if (onTap != null) ...[
                const SizedBox(height: 8),
                const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Detayı gör',
                      style: TextStyle(
                        color: MizanTheme.muted,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(width: 4),
                    Icon(
                      Icons.chevron_right,
                      size: 18,
                      color: MizanTheme.muted,
                    ),
                  ],
                ),
              ],""",
        """              if (onTap != null) ...[
                const SizedBox(height: 8),
                const SizedBox(
                  width: double.infinity,
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          'Detayı gör',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: MizanTheme.muted,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      SizedBox(width: 4),
                      Icon(
                        Icons.chevron_right,
                        size: 18,
                        color: MizanTheme.muted,
                      ),
                    ],
                  ),
                ),
              ],""",
        "Özet kartı detay bağlantısı responsive düzeni",
    )
    cards_path.write_text(cards, encoding="utf-8")

    pdf_test_path = root / "test/pdf_report_test.dart"
    pdf_test = pdf_test_path.read_text(encoding="utf-8")
    pdf_test = replace_once(
        pdf_test,
        """            quantity: 1 + (index % 3),
            unitPrice: 125 + index,""",
        """            quantity: 1.0 + (index % 3),
            unitPrice: 125.0 + index,""",
        "PDF uzun rapor sayısal test verileri",
    )
    pdf_test_path.write_text(pdf_test, encoding="utf-8")

    report_test_path = root / "test/report_service_test.dart"
    report_test = report_test_path.read_text(encoding="utf-8")
    marker = "test('gecikmiş aylık taksitler bütün açık dönemleriyle toplanır'"
    if marker not in report_test:
        raise SystemExit("Birikmiş gecikme regresyon testi bulunamadı.")
    before, after = report_test.split(marker, 1)
    after = replace_once(
        after,
        """      ],
      notificationSlots: defaultNotificationSlots,""",
        """      ],
      expenseCategories: const [],
      expenses: const [],
      notificationSlots: defaultNotificationSlots,""",
        "Birikmiş gecikme testinin zorunlu state alanları",
    )
    report_test_path.write_text(before + marker + after, encoding="utf-8")

    ui_test_path = root / "test/ui_interaction_test.dart"
    ui_test = ui_test_path.read_text(encoding="utf-8")
    ui_test = replace_once(
        ui_test,
        """    final remaining = find.text('Kalan ödeme yükü');
    await tester.scrollUntilVisible(
      remaining,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(remaining);
    await tester.pumpAndSettle();""",
        """    final remaining = find.text('Kalan ödeme yükü');
    await tester.scrollUntilVisible(
      remaining,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    final remainingCard = find.ancestor(
      of: remaining,
      matching: find.byType(InkWell),
    );
    await tester.ensureVisible(remainingCard);
    await tester.pumpAndSettle();
    await tester.tap(remainingCard);
    await tester.pumpAndSettle();""",
        "Rapor kalan yük kartı etkileşim testi",
    )
    ui_test = replace_once(
        ui_test,
        """    await tester.tap(find.text('Kişi detaylarını aç'));
    await tester.pumpAndSettle();""",
        """    final personDetailsButton = find.widgetWithText(
      FilledButton,
      'Kişi detaylarını aç',
    );
    await tester.scrollUntilVisible(
      personDetailsButton,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.ensureVisible(personDetailsButton);
    await tester.pumpAndSettle();
    await tester.tap(personDetailsButton);
    await tester.pumpAndSettle();""",
        "Kişi ayrıntısı düğmesi etkileşim testi",
    )
    ui_test = replace_once(
        ui_test,
        """    await _tapNavigation(tester, Icons.bar_chart_outlined);
    await tester.tap(find.text('Tüm kişiler'));
    await tester.pumpAndSettle();""",
        """    await _tapNavigation(tester, Icons.bar_chart_outlined);
    final peopleFilterButton = find.widgetWithText(
      OutlinedButton,
      'Tüm kişiler',
    );
    await tester.scrollUntilVisible(
      peopleFilterButton,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.ensureVisible(peopleFilterButton);
    await tester.pumpAndSettle();
    await tester.tap(peopleFilterButton);
    await tester.pumpAndSettle();""",
        "Rapor kişi filtresi etkileşim testi",
    )
    ui_test_path.write_text(ui_test, encoding="utf-8")

    checks = {
        expenses_path: [
            "import 'people_screen.dart';",
            "\\n${detail.payment.note.trim()}",
        ],
        people_path: ["icon: _recordTypeIcon(row.type)"],
        reports_path: ["${record.subtitle}\\n${shortDate(record.dueDate)}"],
        pdf_path: [
            "\\nNot: $note",
            "${_typeLabel(detail.type)}\\n${detail.recordTitle}",
        ],
        cards_path: [
            "width: double.infinity",
            "overflow: TextOverflow.ellipsis",
        ],
        pdf_test_path: ["quantity: 1.0 +", "unitPrice: 125.0 +"],
        report_test_path: [
            "expenseCategories: const []",
            "expenses: const []",
        ],
        ui_test_path: [
            "final remainingCard",
            "final personDetailsButton",
            "final peopleFilterButton",
        ],
    }
    missing: list[str] = []
    for path, tokens in checks.items():
        source = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in source:
                missing.append(f"{path.name}:{token}")
    if missing:
        raise SystemExit(f"İkinci tur derleme ve responsive düzeltmesi eksik: {missing}")
    print("İkinci tur derleme, responsive kart ve etkileşim test düzeltmeleri uygulandı.")


if __name__ == "__main__":
    main()
