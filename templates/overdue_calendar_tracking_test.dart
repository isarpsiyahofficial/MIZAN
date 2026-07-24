import 'dart:convert';

import 'package:csv/csv.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lefferion_prime_mizan/controllers/mizan_controller.dart';
import 'package:lefferion_prime_mizan/models/mizan_models.dart';
import 'package:lefferion_prime_mizan/services/csv_backup_service.dart';
import 'package:lefferion_prime_mizan/services/reminder_engine.dart';

import 'test_support.dart';

void main() {
  DebtProduct monthlyDebt({
    int? manualDays,
    DateTime? recordedAt,
    DateTime? since,
    List<DateTime> periods = const [],
    List<PaymentRecord> payments = const [],
  }) => DebtProduct(
    id: 'debt',
    kind: DebtKind.loan,
    title: 'Aylık kredi',
    totalAmount: 12000,
    monthlyAmount: 1000,
    dueDate: DateTime(2026, 8, 5),
    dueMode: DebtDueMode.monthlyDay,
    dueDayOfMonth: 5,
    manualOverdueDays: manualDays,
    manualOverdueRecordedAt: recordedAt,
    manualOverdueSince: since,
    manualOverduePeriods: periods,
    payments: payments,
  );

  MizanState stateWithDebt(DebtProduct debt) => MizanState(
    people: [
      PersonAccount(
        id: 'person',
        name: 'Kişi',
        banks: [
          BankGroup(
            id: 'bank',
            userWrittenName: 'Banka',
            products: [debt],
          ),
        ],
      ),
    ],
    expenseCategories: const [],
    expenses: const [],
    notificationSlots: const [],
    paymentNotificationSlots: const [
      NotificationSlot(
        id: 'morning',
        label: 'Sabah',
        hour: 9,
        minute: 0,
        message: 'Ödemeyi kontrol et.',
      ),
    ],
  );

  test('manuel gecikme günü takvimle her gün bir artar', () {
    final debt = monthlyDebt(
      manualDays: 46,
      recordedAt: DateTime(2026, 7, 21),
      since: DateTime(2026, 6, 5),
    );

    expect(debt.overdueDaysAt(DateTime(2026, 7, 21)), 46);
    expect(debt.overdueDaysAt(DateTime(2026, 7, 22)), 47);
    expect(debt.overdueDaysAt(DateTime(2026, 7, 24)), 49);
  });

  test('10 günlük eski CSV yedeğindeki 13 gün gecikme 23 güne çıkar', () {
    const service = CsvBackupService();
    final backupDay = DateTime(2026, 7, 14);
    final reference = DateTime(2026, 7, 24);
    final original = stateWithDebt(monthlyDebt(manualDays: 13));
    final rows = const CsvCodec().decode(service.exportState(original));
    final header = rows.first.map((value) => value.toString()).toList();
    final dateIndex = header.indexOf('date');
    final dataIndex = header.indexOf('data_json');
    final snapshot = rows[1];
    snapshot[dateIndex] = backupDay.toUtc().toIso8601String();
    final json = Map<String, dynamic>.from(
      jsonDecode(snapshot[dataIndex].toString()) as Map,
    );
    final debtJson = ((json['people'] as List).first as Map)['banks'] as List;
    final product = (((debtJson.first as Map)['products'] as List).first as Map);
    product.remove('manualOverdueRecordedAt');
    product.remove('manualOverdueSince');
    snapshot[dataIndex] = jsonEncode(json);

    final imported = service.importState(const CsvCodec().encode(rows));
    final debt = imported.people.single.banks.single.products.single;
    expect(debt.manualOverdueRecordedAt, backupDay);
    expect(debt.overdueDaysAt(reference), 23);
  });

  test('seçilen gecikmiş aylar doğru hesaplanır ve ödeme ile azalır', () {
    final reference = DateTime(2026, 7, 24);
    final debt = monthlyDebt(
      periods: [DateTime(2026, 5), DateTime(2026, 6)],
    );

    expect(debt.unpaidDueDatesAt(reference), [
      DateTime(2026, 5, 5),
      DateTime(2026, 6, 5),
    ]);
    expect(debt.overdueDaysAt(reference), 80);
    expect(debt.dueAmountAt(reference), 2000);

    final mayPaid = debt.copyWith(
      payments: [
        PaymentRecord(
          id: 'payment',
          amount: 1000,
          paidAt: DateTime(2026, 7, 24),
          entryType: PaymentEntryType.installment,
          appliesToDueDate: DateTime(2026, 5, 5),
        ),
      ],
    );
    expect(mayPaid.unpaidDueDatesAt(reference), [DateTime(2026, 6, 5)]);
    expect(mayPaid.overdueDaysAt(reference), 49);
    expect(mayPaid.dueAmountAt(reference), 1000);
  });

  test('gecikme bildirimi seçilen en eski ödenmeyen dönemi kullanır', () {
    final now = DateTime(2026, 7, 24, 8);
    final state = stateWithDebt(
      monthlyDebt(periods: [DateTime(2026, 5), DateTime(2026, 6)]),
    );

    final reminders = const ReminderPlanBuilder().build(state: state, now: now);
    final payment = reminders.firstWhere(
      (item) => item.kind == ReminderKind.payment,
    );
    expect(payment.message, contains('Ödeme 80 gün gecikti.'));
  });

  test('her ayın 5i yeni kayıtta bütün aylarda sonraki takvim ayına geçer', () async {
    final store = MemoryStore(
      const MizanState(
        people: [
          PersonAccount(
            id: 'person',
            name: 'Kişi',
            banks: [BankGroup(id: 'bank', userWrittenName: 'Banka')],
          ),
        ],
        expenseCategories: [],
        expenses: [],
        notificationSlots: [],
      ),
    );
    final controller = MizanController(store, scheduler: SpyScheduler());
    await controller.load();
    final createdAt = DateTime.now();

    await controller.addDebtProduct(
      personId: 'person',
      bankId: 'bank',
      kind: DebtKind.loan,
      title: 'Takvim kredisi',
      totalAmount: 12000,
      monthlyAmount: 1000,
      dueDate: createdAt,
      dueMode: DebtDueMode.monthlyDay,
      dueDayOfMonth: 5,
    );

    final due = controller.state.people.single.banks.single.products.single.dueDate;
    final expected = DateTime(createdAt.year, createdAt.month + 1, 5);
    expect(due, expected);
  });
}
