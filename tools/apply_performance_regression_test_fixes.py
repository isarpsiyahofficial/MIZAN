from __future__ import annotations

import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Beklenen tek eşleşme bulunamadı: {path}: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Kullanım: apply_performance_regression_test_fixes.py <kaynak-kökü>"
        )
    root = Path(sys.argv[1]).resolve()
    replace_once(
        root / "test/performance_scaling_test.dart",
        "              amount: 100 + index,",
        "              amount: 100.0 + index,",
    )
    replace_once(
        root / "test/controller_test.dart",
        "    expect(scheduler.lastScheduledState?.toJson(), beforeJson);",
        "    expect(paymentCount(scheduler.lastScheduledState!), beforePayments);\n"
        "    expect(scheduler.lastScheduledState!.people, hasLength(1));\n"
        "    expect(scheduler.lastScheduledState!.expenses, isEmpty);\n"
        "    expect(scheduler.lastScheduledState!.expenseCategories, isEmpty);",
    )
    print("Performans testleri hafif bildirim veri sınırına uyarlandı.")


if __name__ == "__main__":
    main()
