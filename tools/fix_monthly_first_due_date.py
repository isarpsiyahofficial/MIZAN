from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_monthly_first_due_date.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    models = root / "lib/models/mizan_models.dart"
    text = models.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """  DateTime get firstScheduledDueDate => dueMode == DebtDueMode.monthlyDay
      ? _dayOfMonth(dueDate, dueDayOfMonth ?? dueDate.day)
      : _dateOnly(dueDate);""",
        """  DateTime get firstScheduledDueDate {
    if (dueMode != DebtDueMode.monthlyDay) return _dateOnly(dueDate);
    final candidate = _dayOfMonth(dueDate, dueDayOfMonth ?? dueDate.day);
    if (!candidate.isBefore(_dateOnly(dueDate))) return candidate;
    return dueDateForMonth(DateTime(dueDate.year, dueDate.month + 1));
  }""",
        "Borç ilk aylık vadesi",
    )
    text = replace_once(
        text,
        """  DateTime get firstScheduledDueDate => isMonthly
      ? _dayOfMonth(
          DateTime(dueDate.year, dueDate.month),
          paymentDay ?? dueDate.day,
        )
      : _dateOnly(dueDate);""",
        """  DateTime get firstScheduledDueDate {
    if (!isMonthly) return _dateOnly(dueDate);
    final candidate = _dayOfMonth(
      DateTime(dueDate.year, dueDate.month),
      paymentDay ?? dueDate.day,
    );
    if (!candidate.isBefore(_dateOnly(dueDate))) return candidate;
    return dueDateForMonth(DateTime(dueDate.year, dueDate.month + 1));
  }""",
        "Fatura ilk aylık vadesi",
    )
    text = replace_once(
        text,
        """  DateTime get firstScheduledDueDate => isMonthlySchedule
      ? _dayOfMonth(DateTime(dueDate.year, dueDate.month), paymentDay)
      : _dateOnly(dueDate);""",
        """  DateTime get firstScheduledDueDate {
    if (!isMonthlySchedule) return _dateOnly(dueDate);
    final candidate = _dayOfMonth(
      DateTime(dueDate.year, dueDate.month),
      paymentDay,
    );
    if (!candidate.isBefore(_dateOnly(dueDate))) return candidate;
    return dueDateForMonth(DateTime(dueDate.year, dueDate.month + 1));
  }""",
        "Kira/taksit ilk aylık vadesi",
    )
    models.write_text(text, encoding="utf-8")

    test = root / "test/monthly_first_due_date_regression_test.dart"
    test.write_text(
        """import 'package:flutter_test/flutter_test.dart';
import 'package:lefferion_prime_mizan/models/mizan_models.dart';

void main() {
  test('ayın ödeme günü başlangıç tarihinden önceyse sonraki aya geçilir', () {
    final debt = DebtProduct(
      id: 'debt',
      kind: DebtKind.credit,
      title: 'Kredi',
      totalAmount: 12000,
      monthlyPayment: 1000,
      dueDate: DateTime(2026, 7, 26),
      dueMode: DebtDueMode.monthlyDay,
      dueDayOfMonth: 5,
    );
    final bill = BillEntry(
      id: 'bill',
      kind: BillKind.electricity,
      institutionName: 'Elektrik',
      amount: 700,
      dueDate: DateTime(2026, 7, 26),
      scheduleMode: BillScheduleMode.monthly,
      paymentDay: 5,
    );
    final rent = RentEntry(
      id: 'rent',
      kind: RentEntryKind.productInstallment,
      title: 'Ürün taksiti',
      amount: 24000,
      paymentDay: 5,
      receiverName: 'Mağaza',
      dueDate: DateTime(2026, 7, 26),
      installmentCount: 12,
      currentInstallment: 1,
      payments: [
        PaymentRecord(
          id: 'previous',
          amount: 2000,
          paidAt: DateTime(2026, 7, 5),
          entryType: PaymentEntryType.installment,
        ),
      ],
    );

    expect(debt.firstScheduledDueDate, DateTime(2026, 8, 5));
    expect(bill.firstScheduledDueDate, DateTime(2026, 8, 5));
    expect(rent.firstScheduledDueDate, DateTime(2026, 8, 5));
    expect(rent.dueAmountAt(DateTime(2026, 7, 21)), closeTo(2200, 0.001));
    expect(rent.statusAt(DateTime(2026, 7, 21)), isNot(PaymentStatus.overdue));
  });

  test('ayın ödeme günü başlangıç tarihiyle aynı veya sonraysa aynı ay korunur', () {
    final rent = RentEntry(
      id: 'same-month',
      kind: RentEntryKind.homeRent,
      title: 'Ev kirası',
      amount: 15000,
      paymentDay: 20,
      receiverName: 'Ev sahibi',
      dueDate: DateTime(2026, 7, 15),
      recurringMonthly: true,
    );
    expect(rent.firstScheduledDueDate, DateTime(2026, 7, 20));
  });
}
""",
        encoding="utf-8",
    )

    verified = models.read_text(encoding="utf-8")
    if verified.count("candidate.isBefore(_dateOnly(dueDate))") < 3:
        raise SystemExit("İlk aylık vade düzeltmesi eksik uygulandı.")
    print("Borç, fatura ve kira/taksit ilk aylık vade başlangıçları düzeltildi.")


if __name__ == "__main__":
    main()
