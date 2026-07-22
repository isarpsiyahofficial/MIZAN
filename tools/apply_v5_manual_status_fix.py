from __future__ import annotations

import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: beklenen 1 eşleşme, bulunan {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_v5_manual_status_fix.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    replace_once(
        root / "lib/models/mizan_models.dart",
        """  PaymentStatus statusAt(DateTime reference) {
    if (isArchived) return PaymentStatus.passive;
    if (remainingAmount <= 0) return PaymentStatus.completed;
    final days = _daysUntil(effectiveDueDateAt(reference), reference);
    if (days < 0) return PaymentStatus.overdue;
    if (days <= 5) return PaymentStatus.upcoming;
    return PaymentStatus.active;
  }""",
        """  PaymentStatus statusAt(DateTime reference) {
    if (isArchived) return PaymentStatus.passive;
    if (remainingAmount <= 0) return PaymentStatus.completed;
    if (overdueDaysAt(reference) > 0) return PaymentStatus.overdue;
    final days = _daysUntil(effectiveDueDateAt(reference), reference);
    if (days <= 5) return PaymentStatus.upcoming;
    return PaymentStatus.active;
  }""",
    )
    replace_once(
        root / "test/alarm_regression_test.dart",
        """    expect(debt.overdueDaysAt(reference), 46);
    expect(
      DebtProduct.fromJson(debt.toJson()).manualOverdueDays,
      46,
    );""",
        """    expect(debt.overdueDaysAt(reference), 46);
    expect(debt.statusAt(reference), PaymentStatus.overdue);
    expect(
      DebtProduct.fromJson(debt.toJson()).manualOverdueDays,
      46,
    );""",
    )
    print("Manuel gecikme durumu V5 hesaplamasına bağlandı.")


if __name__ == "__main__":
    main()
