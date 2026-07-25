from __future__ import annotations

import re
import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_mizan_observation_round2.py <source-root>")
    root = Path(sys.argv[1]).resolve()

    csv_path = root / "lib/services/csv_backup_service.dart"
    text = csv_path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "    final tracker = _MergeTracker();\n    final currentJson",
        "    final tracker = _MergeTracker();\n    var userDuplicateCount = 0;\n    final currentJson",
        "CSV kullanıcı tekrar sayacı",
    )
    text = replace_once(
        text,
        "    final categoryIdMap = <String, String>{};",
        "    userDuplicateCount = tracker.duplicate;\n\n    final categoryIdMap = <String, String>{};",
        "CSV kişi/kayıt tekrar sayısı",
    )
    text = replace_once(
        text,
        "      merge: _mergeIncome,\n    );\n\n    currentJson['notificationSlots']",
        "      merge: _mergeIncome,\n    );\n    userDuplicateCount = tracker.duplicate;\n\n    currentJson['notificationSlots']",
        "CSV gelir sonrası kullanıcı tekrar sayısı",
    )
    text = replace_once(
        text,
        "      duplicateCount: tracker.duplicate,",
        "      duplicateCount: userDuplicateCount,",
        "CSV sonuç tekrar sayısı",
    )
    csv_path.write_text(text, encoding="utf-8")

    controller_path = root / "lib/controllers/mizan_controller.dart"
    text = controller_path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        """    _loadMessage =
        'CSV yedeği mevcut kayıtlarla birleştirildi: '
        '$addedCount yeni, $mergedCount ilişki güncellendi, '
        '$duplicateCount ortak kayıt atlandı.';""",
        """    final duplicatePart = duplicateCount > 0
        ? ', $duplicateCount gerçekten ortak kullanıcı kaydı atlandı'
        : '';
    _loadMessage =
        'CSV yedeği mevcut kayıtlarla birleştirildi: '
        '$addedCount yeni, $mergedCount ilişki güncellendi$duplicatePart.';""",
        "CSV birleştirme mesajı",
    )
    controller_path.write_text(text, encoding="utf-8")

    settings_path = root / "lib/screens/settings_screen.dart"
    text = settings_path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "Text('Ortak/tekrar kayıt atlanacak: ${result.duplicateCount}'),",
        """Text(
              result.duplicateCount == 0
                  ? 'Ortak kullanıcı kaydı: Yok'
                  : 'Ortak kullanıcı kaydı atlanacak: ${result.duplicateCount}',
            ),""",
        "CSV onay tekrar bilgisi",
    )
    settings_path.write_text(text, encoding="utf-8")

    people_path = root / "lib/screens/people_screen.dart"
    text = people_path.read_text(encoding="utf-8")
    text, count = re.subn(
        r"\n\s*if \(current\.unpaidDueDates\.isNotEmpty\) \.\.\.\[\n\s*const SizedBox\(height: 4\),\n\s*Text\(\n\s*'Ödenmeyen dönemler: \$\{current\.unpaidDueDates\.map\(monthLabel\)\.join\(', '\)\}',\n\s*style: const TextStyle\(fontWeight: FontWeight\.w700\),\n\s*\),\n\s*\],",
        "",
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit("Ödenmeyen dönemler metni bulunamadı.")
    people_path.write_text(text, encoding="utf-8")

    models_path = root / "lib/models/mizan_models.dart"
    text = models_path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "amount: bill.dueAmountAt(reference),",
        """amount: bill.statusAt(reference) == PaymentStatus.overdue
                ? bill.outstandingAmountAt(reference)
                : bill.dueAmountAt(reference),""",
        "Gecikmiş fatura toplamı",
    )
    text = replace_once(
        text,
        "amount: rent.dueAmountAt(reference),",
        """amount: rent.statusAt(reference) == PaymentStatus.overdue
                ? rent.outstandingAmountAt(reference)
                : rent.dueAmountAt(reference),""",
        "Gecikmiş kira/taksit toplamı",
    )
    models_path.write_text(text, encoding="utf-8")

    reports_path = root / "lib/screens/reports_screen.dart"
    text = reports_path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        """          onPeriodChanged: (value) => setState(() {
            period = value;
            if (value == ReportPeriod.monthly && availableMonths.isNotEmpty) {
              anchorDate = availableMonths.first;
            } else if (value == ReportPeriod.yearly &&
                availableYears.isNotEmpty) {
              anchorDate = DateTime(availableYears.first);
            }
          }),""",
        """          onPeriodChanged: (value) => setState(() {
            period = value;
            final now = DateTime.now();
            if (value == ReportPeriod.monthly) {
              anchorDate = DateTime(now.year, now.month);
            } else if (value == ReportPeriod.yearly) {
              anchorDate = DateTime(now.year);
            } else if (value == ReportPeriod.daily ||
                value == ReportPeriod.weekly) {
              anchorDate = dateOnly(now);
            }
          }),""",
        "Rapor dönem dönüşü",
    )
    text = replace_once(
        text,
        "_CurrentExpenseOverview(state: state, now: DateTime.now()),",
        "_CurrentExpenseOverview(report: report),",
        "Rapor özet filtresi",
    )
    section_start = text.find(
        "        _DetailedListSection(\n          title: 'Kalan taksit sayıları',"
    )
    if section_start < 0:
        raise SystemExit("Kalan taksit sayıları bölümü bulunamadı.")
    section_end = text.find("        _PersonDebtSection(", section_start)
    if section_end < 0:
        raise SystemExit("Kişi bazlı kalan borç bölümü bulunamadı.")
    text = text[:section_start] + text[section_end:]

    overview_start = text.index("class _CurrentExpenseOverview extends StatelessWidget")
    overview_end = text.index("class _RealizedTotalCard", overview_start)
    overview = """class _CurrentExpenseOverview extends StatelessWidget {
  const _CurrentExpenseOverview({required this.report});

  final MizanReport report;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      SectionTitle(
        'Seçili dönem gider özeti',
        subtitle:
            '${report.range.label} filtresine ait normal gider, ödeme ve birleşik toplamlar gösterilir.',
      ),
      const SizedBox(height: 10),
      AdaptiveGrid(
        minTileWidth: 175,
        children: [
          MetricCard(
            label: 'Normal giderler',
            value: money(report.totalExpenses),
            color: MizanTheme.green,
            icon: Icons.shopping_bag_outlined,
          ),
          MetricCard(
            label: 'Ödemeler',
            value: money(report.totalPayments),
            color: MizanTheme.blue,
            icon: Icons.payments_outlined,
          ),
          MetricCard(
            label: 'Bütün harcamalar',
            value: money(report.realizedGrandTotal),
            color: MizanTheme.orange,
            icon: Icons.account_balance_wallet_outlined,
          ),
        ],
      ),
      const SizedBox(height: 8),
      const Text(
        'Bütün harcamalar, normal giderler ile banka, şahıs, fatura, abonelik, kira ve taksit ödemelerinin toplamıdır.',
        style: TextStyle(
          color: MizanTheme.muted,
          fontWeight: FontWeight.w600,
        ),
      ),
    ],
  );
}

"""
    text = text[:overview_start] + overview + text[overview_end:]
    text = replace_once(
        text,
        "  int visibleDayLimit = _pageSize;\n",
        "  int visibleDayLimit = _pageSize;\n  final Set<int> expandedDays = <int>{};\n",
        "Rapor gider günü açılır durumu",
    )
    old_group = """        for (final entry in visible) ...[
          _ReportExpenseDayHeader(
            day: DateTime(
              entry.key ~/ 10000,
              (entry.key ~/ 100) % 100,
              entry.key % 100,
            ),
            count: entry.value.length,
            total: entry.value.fold<double>(
              0,
              (sum, item) => sum + item.expense.totalAmount,
            ),
            labelBuilder: _browser.dayLabel,
          ),
          const SizedBox(height: 8),
          for (final detail in entry.value)
            _ReportExpenseDetailCard(detail: detail),
          const SizedBox(height: 8),
        ],"""
    new_group = """        for (final entry in visible) ...[
          InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => setState(() {
              if (!expandedDays.add(entry.key)) expandedDays.remove(entry.key);
            }),
            child: _ReportExpenseDayHeader(
              day: DateTime(
                entry.key ~/ 10000,
                (entry.key ~/ 100) % 100,
                entry.key % 100,
              ),
              count: entry.value.length,
              total: entry.value.fold<double>(
                0,
                (sum, item) => sum + item.expense.totalAmount,
              ),
              labelBuilder: _browser.dayLabel,
            ),
          ),
          if (expandedDays.contains(entry.key)) ...[
            const SizedBox(height: 8),
            for (final detail in entry.value)
              _ReportExpenseDetailCard(detail: detail),
          ],
          const SizedBox(height: 8),
        ],"""
    text = replace_once(text, old_group, new_group, "Rapor gider günü açılır içeriği")

    person_start = text.index("class _PersonDebtSection extends StatelessWidget")
    person_end = text.index("String _anchorLabel", person_start)
    person_section = """class _PersonDebtSection extends StatelessWidget {
  const _PersonDebtSection({
    required this.details,
    required this.referenceDate,
  });

  final List<ReportPersonDebtDetail> details;
  final DateTime referenceDate;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionTitle(
            'Kişi bazında güncel kalan borç',
            subtitle:
                'Kişi ve kayıt türü başlıklarına dokunarak ayrıntıları açıp kapatabilirsiniz.',
          ),
          const SizedBox(height: 12),
          if (details.isEmpty)
            const Text(
              'Kişi kaydı bulunmuyor.',
              style: TextStyle(color: MizanTheme.muted),
            )
          else
            for (final person in details)
              Card(
                margin: const EdgeInsets.only(bottom: 10),
                child: ExpansionTile(
                  key: PageStorageKey('report-person-${person.personId}'),
                  title: Text(
                    person.personName,
                    style: const TextStyle(fontWeight: FontWeight.w900),
                  ),
                  subtitle: Text(
                    'Toplam kalan: ${money(person.totalRemaining)}',
                  ),
                  childrenPadding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                  children: [
                    for (final type in RecordType.values)
                      if ((person.byType[type] ?? 0) > 0)
                        ExpansionTile(
                          tilePadding: EdgeInsets.zero,
                          title: Text(
                            reportTypeLabel(type),
                            style: const TextStyle(
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          trailing: Text(
                            money(person.byType[type] ?? 0),
                            style: const TextStyle(
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                          children: [
                            for (final record in person.records.where(
                              (item) => item.type == type,
                            ))
                              ListTile(
                                dense: true,
                                contentPadding: EdgeInsets.zero,
                                title: Text(
                                  record.title,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                subtitle: Text(
                                  '${shortDate(record.dueDate)} · ${recordTimingLabel(record, referenceDate)}',
                                ),
                                trailing: Text(
                                  money(record.amount),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w900,
                                  ),
                                ),
                              ),
                          ],
                        ),
                  ],
                ),
              ),
        ],
      ),
    ),
  );
}

"""
    text = text[:person_start] + person_section + text[person_end:]
    text = text.replace(
        "'Giderler ödeme kayıtlarından ayrıdır ve kategori bazında hesaplanır.'",
        "'Normal giderler kategori bazında; ödemeler ise banka, şahıs, fatura, abonelik, kira ve taksit kayıtlarından ayrı hesaplanır.'",
        1,
    )
    reports_path.write_text(text, encoding="utf-8")

    expenses_path = root / "lib/screens/expenses_screen.dart"
    text = expenses_path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "import '../services/expense_browser_service.dart';",
        "import '../services/expense_browser_service.dart';\nimport '../services/report_service.dart';",
        "Gider ödeme raporu içe aktarımı",
    )
    text = replace_once(
        text,
        "enum _ExpensePeriod",
        """enum _ExpenseView { daily, payments, all }

extension on _ExpenseView {
  String get label => switch (this) {
    _ExpenseView.daily => 'Günlük harcamalar',
    _ExpenseView.payments => 'Ödemeler',
    _ExpenseView.all => 'Bütün harcamalar',
  };
}

enum _ExpensePeriod""",
        "Gider görünüm türleri",
    )
    text = replace_once(
        text,
        "  String? selectedCategoryId;",
        "  String? selectedCategoryId;\n  _ExpenseView expenseView = _ExpenseView.daily;",
        "Gider görünüm durumu",
    )
    category_block = """    final categoryById = <String, ExpenseCategory>{
      for (final category in state.expenseCategories) category.id: category,
    };"""
    payment_block = category_block + """
    final paymentReport = const MizanReportService().build(
      state: state,
      filter: ReportFilter(
        period: ReportPeriod.allTime,
        anchorDate: now,
      ),
    );
    final paymentDetails = paymentReport.paymentDetails.where((detail) {
      final day = dateOnly(detail.payment.paidAt);
      if (range.start != null && day.isBefore(dateOnly(range.start!))) {
        return false;
      }
      if (range.end != null && day.isAfter(dateOnly(range.end!))) {
        return false;
      }
      final query = searchController.text.trim().toLowerCase();
      if (query.isEmpty) return true;
      return '${detail.personName} ${detail.recordTitle} ${detail.recordSubtitle} ${detail.payment.note}'
          .toLowerCase()
          .contains(query);
    }).toList(growable: false);
    final paymentTotal = paymentDetails.fold<double>(
      0,
      (sum, item) => sum + item.payment.amount,
    );"""
    text = replace_once(text, category_block, payment_block, "Gider ödeme listesi")
    text = replace_once(
        text,
        """            MetricCard(
              label: '${period.label} görünümü',
              value: money(visibleTotal),
              icon: Icons.filter_alt_outlined,
            ),""",
        """            MetricCard(
              label: '${period.label} normal gider',
              value: money(visibleTotal),
              icon: Icons.shopping_bag_outlined,
            ),
            MetricCard(
              label: '${period.label} ödemeler',
              value: money(paymentTotal),
              color: MizanTheme.blue,
              icon: Icons.payments_outlined,
            ),
            MetricCard(
              label: '${period.label} bütün harcamalar',
              value: money(visibleTotal + paymentTotal),
              color: MizanTheme.orange,
              icon: Icons.account_balance_wallet_outlined,
            ),""",
        "Gider görünüm toplamları",
    )
    text = replace_once(
        text,
        """        const SizedBox(height: 16),
        SectionTitle(
          'Günlük harcamalar',""",
        """        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final item in _ExpenseView.values)
                  ChoiceChip(
                    selected: expenseView == item,
                    label: Text(item.label),
                    onSelected: (_) => setState(() => expenseView = item),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        if (expenseView == _ExpenseView.daily ||
            expenseView == _ExpenseView.all) ...[
          SectionTitle(
          'Günlük harcamalar',""",
        "Gider görünüm seçicileri",
    )
    text = replace_once(
        text,
        """        if (visibleGroups.length < groups.length)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: OutlinedButton.icon(
              key: const ValueKey('expenses-load-more'),
              onPressed: () => setState(() => visibleGroupLimit += _pageSize),
              icon: const Icon(Icons.expand_more),
              label: Text(
                'Daha fazla gün göster (${groups.length - visibleGroups.length} kaldı)',
              ),
            ),
          ),
      ],""",
        """        if (visibleGroups.length < groups.length)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: OutlinedButton.icon(
              key: const ValueKey('expenses-load-more'),
              onPressed: () => setState(() => visibleGroupLimit += _pageSize),
              icon: const Icon(Icons.expand_more),
              label: Text(
                'Daha fazla gün göster (${groups.length - visibleGroups.length} kaldı)',
              ),
            ),
          ),
        ],
        if (expenseView == _ExpenseView.payments ||
            expenseView == _ExpenseView.all) ...[
          if (expenseView == _ExpenseView.all) const SizedBox(height: 18),
          SectionTitle(
            'Ödemeler',
            subtitle: '${paymentDetails.length} ödeme · ${money(paymentTotal)}',
          ),
          const SizedBox(height: 10),
          _PaymentExpenseGroups(details: paymentDetails),
        ],
        if (expenseView == _ExpenseView.all) ...[
          const SizedBox(height: 18),
          const Text(
            'Bütün harcamalar görünümünde günlük harcamalar ve ödemeler ayrı başlıklar altında tutulur; yalnız toplamları birlikte hesaplanır.',
            style: TextStyle(
              color: MizanTheme.muted,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ],""",
        "Gider görünüm bölümleri",
    )
    marker = "class _ExpenseDayCard extends StatefulWidget"
    index = text.index(marker)
    payment_widgets = """String _paymentRecordLabel(RecordType type) => switch (type) {
  RecordType.debt => 'Banka / kredi',
  RecordType.personalDebt => 'Kişisel / kurumsal',
  RecordType.bill => 'Fatura',
  RecordType.subscription => 'Abonelik',
  RecordType.rent => 'Kira / taksit',
};

IconData _paymentRecordIcon(RecordType type) => switch (type) {
  RecordType.debt => Icons.account_balance_outlined,
  RecordType.personalDebt => Icons.handshake_outlined,
  RecordType.bill => Icons.receipt_long_outlined,
  RecordType.subscription => Icons.autorenew_outlined,
  RecordType.rent => Icons.home_work_outlined,
};

class _PaymentExpenseGroups extends StatelessWidget {
  const _PaymentExpenseGroups({required this.details});

  final List<ReportPaymentDetail> details;

  @override
  Widget build(BuildContext context) {
    final groups = <int, List<ReportPaymentDetail>>{};
    for (final detail in details) {
      final day = dateOnly(detail.payment.paidAt);
      final key = day.year * 10000 + day.month * 100 + day.day;
      groups.putIfAbsent(key, () => <ReportPaymentDetail>[]).add(detail);
    }
    final entries = groups.entries.toList()
      ..sort((a, b) => b.key.compareTo(a.key));
    if (entries.isEmpty) {
      return const EmptyState(
        title: 'Ödeme bulunamadı',
        message: 'Seçili filtrede kaydedilmiş ödeme yok.',
      );
    }
    return Column(
      children: [
        for (final entry in entries)
          Card(
            margin: const EdgeInsets.only(bottom: 10),
            child: ExpansionTile(
              key: PageStorageKey('payment-day-${entry.key}'),
              title: Text(
                '${(entry.key % 100).toString().padLeft(2, '0')}.${((entry.key ~/ 100) % 100).toString().padLeft(2, '0')}.${entry.key ~/ 10000}',
                style: const TextStyle(fontWeight: FontWeight.w900),
              ),
              subtitle: Text('${entry.value.length} ödeme kaydı'),
              trailing: Text(
                money(entry.value.fold<double>(
                  0,
                  (sum, item) => sum + item.payment.amount,
                )),
                style: const TextStyle(fontWeight: FontWeight.w900),
              ),
              children: [
                for (final detail in entry.value)
                  ListTile(
                    leading: Icon(
                      _paymentRecordIcon(detail.type),
                      color: MizanTheme.blue,
                    ),
                    title: Text(
                      '${detail.personName} · ${detail.recordTitle}',
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text(
                      '${_paymentRecordLabel(detail.type)}${detail.payment.note.isEmpty ? '' : ' · ${detail.payment.note}'}',
                    ),
                    trailing: Text(
                      money(detail.payment.amount),
                      style: const TextStyle(fontWeight: FontWeight.w900),
                    ),
                  ),
              ],
            ),
          ),
      ],
    );
  }
}

"""
    text = text[:index] + payment_widgets + text[index:]
    expenses_path.write_text(text, encoding="utf-8")

    checks = {
        "lib/services/csv_backup_service.dart": [
            "userDuplicateCount",
            "duplicateCount: userDuplicateCount",
        ],
        "lib/screens/expenses_screen.dart": [
            "enum _ExpenseView",
            "Bütün harcamalar",
            "_PaymentExpenseGroups",
        ],
        "lib/screens/reports_screen.dart": [
            "Seçili dönem gider özeti",
            "expandedDays",
            "report-person-",
        ],
        "lib/models/mizan_models.dart": [
            "bill.outstandingAmountAt(reference)",
            "rent.outstandingAmountAt(reference)",
        ],
    }
    missing: list[str] = []
    for relative, tokens in checks.items():
      source = (root / relative).read_text(encoding="utf-8")
      for token in tokens:
        if token not in source:
          missing.append(f"{relative}:{token}")
    if "Ödenmeyen dönemler:" in people_path.read_text(encoding="utf-8"):
        missing.append("Ödenmeyen dönemler kaldırılmadı")
    if "Kalan taksit sayıları" in reports_path.read_text(encoding="utf-8"):
        missing.append("Kalan taksit sayıları kaldırılmadı")
    if missing:
        raise SystemExit(f"İkinci gözlem turu kapsamı eksik: {missing}")
    print("MİZAN ikinci gözlem turu uygulandı.")


if __name__ == "__main__":
    main()
