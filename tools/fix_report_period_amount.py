from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_report_period_amount.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/models/mizan_models.dart"
    text = path.read_text(encoding="utf-8")
    old = """            amount: rent.dueAmountAt(reference),
            dueDate: rent.effectiveDueDateAt(reference),"""
    new = """            amount: rent.plannedCycleAmount,
            dueDate: rent.effectiveDueDateAt(reference),"""
    if old not in text:
        raise SystemExit("Kira/taksit dönem tutarı kayıt referansı bulunamadı.")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    if "amount: rent.plannedCycleAmount" not in path.read_text(encoding="utf-8"):
        raise SystemExit("Kira/taksit dönem tutarı düzeltmesi doğrulanamadı.")
    print("Kira/taksit rapor yükü kalan toplam yerine güncel dönem tutarını kullanıyor.")


if __name__ == "__main__":
    main()
