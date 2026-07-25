from __future__ import annotations

import sys
from pathlib import Path

from add_expense_date_range import main as add_expense_date_range
from fix_expense_day_numeric_date import main as fix_expense_day_numeric_date
from fix_final_ui_regressions import main as fix_final_ui_regressions
from fix_notification_full_state import main as fix_notification_full_state
from fix_report_period_amount import main as fix_report_period_amount


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_final_validator.py <source-root>")
    fix_report_period_amount()
    fix_notification_full_state()
    fix_expense_day_numeric_date()
    add_expense_date_range()
    fix_final_ui_regressions()
    root = Path(sys.argv[1]).resolve()
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
