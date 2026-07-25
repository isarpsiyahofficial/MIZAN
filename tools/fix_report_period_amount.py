from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_report_period_amount.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/models/mizan_models.dart"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """  DateTime get firstScheduledDueDate => dueMode == DebtDueMode.monthlyDay
      ? _dayOfMonth(dueDate, dueDayOfMonth ?? dueDate.day)
      : _dateOnly(dueDate);""",
        """  DateTime get firstScheduledDueDate => _dateOnly(dueDate);""",
        "Banka borcu ilk aylık vadesi",
    )
    text = replace_once(
        text,
        """  DateTime get firstScheduledDueDate => isMonthly
      ? _dayOfMonth(
          DateTime(dueDate.year, dueDate.month),
          paymentDay ?? dueDate.day,
        )
      : _dateOnly(dueDate);""",
        """  DateTime get firstScheduledDueDate => _dateOnly(dueDate);""",
        "Fatura ilk aylık vadesi",
    )
    text = replace_once(
        text,
        """  DateTime get firstScheduledDueDate => isMonthlySchedule
      ? _dayOfMonth(DateTime(dueDate.year, dueDate.month), paymentDay)
      : _dateOnly(dueDate);""",
        """  DateTime get firstScheduledDueDate => _dateOnly(dueDate);""",
        "Kira/taksit ilk aylık vadesi",
    )
    text = replace_once(
        text,
        """  double get remainingAmount => outstandingAmountAt(DateTime.now());
  double get scheduledPaymentAmount => dueAmountAt(DateTime.now());""",
        """  double get remainingAmount {
    if (kind == RentEntryKind.homeRent ||
        (kind == RentEntryKind.custom &&
            recurringMonthly &&
            installmentCount == null)) {
      return amount;
    }
    final value = amount - paidAmount;
    return value <= 0 ? 0 : double.parse(value.toStringAsFixed(2));
  }

  double get scheduledPaymentAmount => dueAmountAt(DateTime.now());""",
        "Kira/taksit gerçek kalan toplamı",
    )
    text = replace_once(
        text,
        """  bool isDueInMonth(DateTime month) {
    if (!isMonthlySchedule) {
      return dueDate.year == month.year && dueDate.month == month.month;
    }
    final due = dueDateForMonth(month);""",
        """  bool isDueInMonth(DateTime month) {
    if (!isMonthlySchedule) {
      return dueDate.year == month.year && dueDate.month == month.month;
    }
    final first = firstScheduledDueDate;
    if (first.year == month.year && first.month == month.month) return true;
    final due = dueDateForMonth(month);""",
        "Kira/taksit ilk ay dönem yükü",
    )

    if "amount: rent.plannedCycleAmount" in text:
        text = text.replace(
            "amount: rent.plannedCycleAmount",
            "amount: rent.dueAmountAt(reference)",
            1,
        )
    if "amount: rent.dueAmountAt(reference)" not in text:
        raise SystemExit("Kira/taksit dönem tutarı kayıt referansı doğrulanamadı.")

    path.write_text(text, encoding="utf-8")
    verified = path.read_text(encoding="utf-8")
    required = (
        "DateTime get firstScheduledDueDate => _dateOnly(dueDate);",
        "final value = amount - paidAmount;",
        "if (first.year == month.year && first.month == month.month) return true;",
        "amount: rent.dueAmountAt(reference)",
    )
    for token in required:
        if token not in verified:
            raise SystemExit(f"Kira/taksit dönem düzeltmesi eksik: {token}")
    print("İlk ödeme tarihi korunuyor; ilk ay dönem yüküne katılıyor, sonraki aylar ödeme gününe göre ilerliyor ve kalan toplam dönem tutarından ayrılıyor.")


if __name__ == "__main__":
    main()
