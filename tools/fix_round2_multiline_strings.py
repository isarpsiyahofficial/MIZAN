from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; ikinci tur kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_round2_multiline_strings.py <source-root>")
    root = Path(sys.argv[1]).resolve()

    expenses_path = root / "lib/screens/expenses_screen.dart"
    expenses = expenses_path.read_text(encoding="utf-8")
    expenses = replace_once(
        expenses,
        """                    subtitle:
                        '${_paymentRecordLabel(detail.type)} · ${detail.recordSubtitle}${detail.payment.note.trim().isEmpty ? '' : '
${detail.payment.note.trim()}'}',""",
        """                    subtitle:
                        '${_paymentRecordLabel(detail.type)} · ${detail.recordSubtitle}${detail.payment.note.trim().isEmpty ? '' : '\\n${detail.payment.note.trim()}'}',""",
        "Gider ödeme açıklaması",
    )
    expenses_path.write_text(expenses, encoding="utf-8")

    reports_path = root / "lib/screens/reports_screen.dart"
    reports = reports_path.read_text(encoding="utf-8")
    reports = replace_once(
        reports,
        """                                subtitle:
                                    '${record.subtitle}
${shortDate(record.dueDate)} · ${recordTimingLabel(record, referenceDate)}',""",
        """                                subtitle:
                                    '${record.subtitle}\\n${shortDate(record.dueDate)} · ${recordTimingLabel(record, referenceDate)}',""",
        "Rapor kayıt açıklaması",
    )
    reports_path.write_text(reports, encoding="utf-8")

    pdf_path = root / "lib/services/pdf_report_service.dart"
    pdf = pdf_path.read_text(encoding="utf-8")
    pdf = replace_once(
        pdf,
        """            subtitle:
                '${decimalText(detail.expense.quantity)} × ${money(detail.expense.unitPrice)}${note == null ? '' : '
Not: $note'}',""",
        """            subtitle:
                '${decimalText(detail.expense.quantity)} × ${money(detail.expense.unitPrice)}${note == null ? '' : '\\nNot: $note'}',""",
        "PDF günlük gider notu",
    )
    pdf = replace_once(
        pdf,
        """          await _keyValue(
            '${detail.personName} · ${_typeLabel(detail.type)}
${detail.recordTitle}',""",
        """          await _keyValue(
            '${detail.personName} · ${_typeLabel(detail.type)}\\n${detail.recordTitle}',""",
        "PDF ödeme başlığı",
    )
    pdf = replace_once(
        pdf,
        """            subtitle:
                '${detail.payment.entryType.label}$method · ${detail.recordSubtitle}${note == null ? '' : '
Not: $note'}',""",
        """            subtitle:
                '${detail.payment.entryType.label}$method · ${detail.recordSubtitle}${note == null ? '' : '\\nNot: $note'}',""",
        "PDF ödeme notu",
    )
    pdf_path.write_text(pdf, encoding="utf-8")

    checks = {
        expenses_path: ["\\n${detail.payment.note.trim()}"],
        reports_path: ["${record.subtitle}\\n${shortDate(record.dueDate)}"],
        pdf_path: [
            "\\nNot: $note",
            "${_typeLabel(detail.type)}\\n${detail.recordTitle}",
        ],
    }
    missing: list[str] = []
    for path, tokens in checks.items():
        source = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in source:
                missing.append(f"{path.name}:{token}")
    if missing:
        raise SystemExit(f"İkinci tur çok satırlı metin düzeltmesi eksik: {missing}")
    print("İkinci tur Dart çok satırlı metinleri güvenli kaçışlarla düzeltildi.")


if __name__ == "__main__":
    main()
