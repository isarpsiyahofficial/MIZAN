from __future__ import annotations

import sys
from pathlib import Path

from add_expense_date_range import main as add_expense_date_range
from fix_monthly_first_due_date import main as fix_monthly_first_due_date


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_final_validator.py <source-root>")
    fix_monthly_first_due_date()
    root = Path(sys.argv[1]).resolve()

    regression_test = root / "test/monthly_first_due_date_regression_test.dart"
    test_text = regression_test.read_text(encoding="utf-8")
    replacements = {
        "DebtKind.credit": "DebtKind.loan",
        "monthlyPayment: 1000": "monthlyAmount: 1000",
    }
    for old, new in replacements.items():
        if old not in test_text:
            raise SystemExit(f"Aylık ilk vade testi düzeltme alanı bulunamadı: {old}")
        test_text = test_text.replace(old, new, 1)
    regression_test.write_text(test_text, encoding="utf-8")

    add_expense_date_range()
    path = root / "tools/validate_project.py"
    text = path.read_text(encoding="utf-8")
    old = 'require_all(reminder_engine, ["safeMaximumConcurrentAlarms = 120", "putIfAbsent"], "Güvenli ve kararlı alarm planı eksik", failures)'
    new = 'require_all(reminders, ["safeMaximumConcurrentAlarms = 120", "putIfAbsent"], "Güvenli ve kararlı alarm planı eksik", failures)'
    if old not in text:
        raise SystemExit("Final doğrulayıcıdaki bildirim değişkeni bulunamadı.")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    if "require_all(reminders," not in path.read_text(encoding="utf-8"):
        raise SystemExit("Final doğrulayıcı düzeltmesi doğrulanamadı.")
    print("Final yapısal doğrulayıcı bildirim değişkeni düzeltildi.")


if __name__ == "__main__":
    main()
