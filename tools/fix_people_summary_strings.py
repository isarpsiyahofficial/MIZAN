from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_people_summary_strings.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/screens/people_screen.dart"
    text = path.read_text(encoding="utf-8")

    replacements = (
        (
            """      subtitle:
          '$schedule · Bu dönem ${money(currentDue)}
Ödenmemiş toplam ${money(outstanding)} · ${shortDate(due)} · ${paymentTimingLabel(status, due, now)}',""",
            """      subtitle:
          '$schedule · Bu dönem ${money(currentDue)}\\n'
          'Ödenmemiş toplam ${money(outstanding)} · ${shortDate(due)} · ${paymentTimingLabel(status, due, now)}',""",
            "fatura kişi özeti",
        ),
        (
            """      subtitle:
          '${rent.kind.label} · ${rent.receiverName}
$schedule · Bu dönem ${money(currentDue)} · Toplam ${money(outstanding)}
${shortDate(due)} · ${paymentTimingLabel(status, due, now)}',""",
            """      subtitle:
          '${rent.kind.label} · ${rent.receiverName}\\n'
          '$schedule · Bu dönem ${money(currentDue)} · Toplam ${money(outstanding)}\\n'
          '${shortDate(due)} · ${paymentTimingLabel(status, due, now)}',""",
            "kira kişi özeti",
        ),
    )
    for old, new, label in replacements:
        if old not in text:
            raise SystemExit(f"Bozuk {label} metni bulunamadı; kaynak beklenenden farklı.")
        text = text.replace(old, new, 1)

    path.write_text(text, encoding="utf-8")
    verified = path.read_text(encoding="utf-8")
    if "money(currentDue)}\\n'" not in verified:
        raise SystemExit("Kişiler ekranı satır sonu düzeltmesi doğrulanamadı.")
    print("Kişiler ekranındaki bozuk çok satırlı açıklamalar düzeltildi.")


if __name__ == "__main__":
    main()
