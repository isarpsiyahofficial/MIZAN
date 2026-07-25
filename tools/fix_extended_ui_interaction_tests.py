from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; test kaynağı beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_extended_ui_interaction_tests.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "test/ui_interaction_test.dart"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        """    expect(find.text('Günlük harcamalar'), findsOneWidget);
    expect(find.byType(ExpansionTile), findsNothing);""",
        """    final dailyExpenses = find.text('Günlük harcamalar');
    await tester.scrollUntilVisible(
      dailyExpenses,
      180,
      scrollable: find.byType(Scrollable).first,
    );
    expect(dailyExpenses, findsOneWidget);
    expect(find.byType(ExpansionTile), findsNothing);""",
        "Uzatılmış gider ekranı başlık kontrolü",
    )
    text = replace_once(
        text,
        """    final combinedReport = find.textContaining(
      'gerçekleşen toplam ödeme-gider raporu',
    );""",
        """    final combinedReport = find.textContaining(
      'Normal giderler ile banka, şahıs, fatura, abonelik, kira ve taksit',
    );""",
        "Yeni toplam gider açıklaması kontrolü",
    )
    text = replace_once(
        text,
        """    expect(find.text('24.07.2026 Cuma'), findsOneWidget);
    await tester.tap(find.text('24.07.2026 Cuma'));
    await tester.pumpAndSettle();""",
        """    final matchingDay = find.text('24.07.2026 Cuma');
    final expenseScrollable = find.byType(Scrollable).first;
    await tester.scrollUntilVisible(
      matchingDay,
      180,
      scrollable: expenseScrollable,
    );
    await tester.drag(expenseScrollable, const Offset(0, -180));
    await tester.pumpAndSettle();
    expect(matchingDay, findsOneWidget);
    final matchingDayHeader = find.ancestor(
      of: matchingDay,
      matching: find.byType(InkWell),
    );
    expect(matchingDayHeader, findsOneWidget);
    await tester.tap(matchingDayHeader);
    await tester.pumpAndSettle();""",
        "Uzatılmış gider arama sonucu kontrolü",
    )
    path.write_text(text, encoding="utf-8")
    verified = path.read_text(encoding="utf-8")
    for token in (
        "final dailyExpenses",
        "Normal giderler ile banka, şahıs",
        "final matchingDayHeader",
    ):
        if token not in verified:
            raise SystemExit(f"Uzatılmış ekran etkileşim testi eksik: {token}")
    print("Gider ve rapor etkileşim testleri uzatılmış güvenli düzeni kaydırarak doğruluyor.")


if __name__ == "__main__":
    main()
