from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_validator_round2.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "tools/validate_project.py"
    text = path.read_text(encoding="utf-8")
    replacements = {
        'require("ExpansionTile(" not in expenses, "Gider ekranındaki gri blok riski kaldırılmadı", failures)':
            'require_all(expenses, ["enum _ExpenseView", "_PaymentExpenseGroups", "Bütün harcamalar"], "Gider ekranı üçlü görünümü eksik", failures)',
        'require_all(reports + "\\n" + report_service, ["Rapor kapsamı", "Günlük", "Haftalık", "Aylık", "Yıllık", "Tüm zamanlar", "Gelir ve net durum", "Gelir ayrıntıları", "Ödemeler sonrası kalan", "Ödeme ve gider sonrası net", "Gerçekleşen ödemelerin dağılımı", "Bugün ve bu ay gider özeti", "toplam gider", "Kalan ödeme yükünün dağılımı", "Gider dağılımı", "Kalan taksit sayıları", "PDF indir", "PDF paylaş", "Tüm kişileri kapsa"], "Ayrıntılı rapor/PDF ekranı eksik", failures)':
            'require_all(reports + "\\n" + report_service, ["Rapor kapsamı", "Günlük", "Haftalık", "Aylık", "Yıllık", "Tüm zamanlar", "Gelir ve net durum", "Gelir ayrıntıları", "Ödemeler sonrası kalan", "Ödeme ve gider sonrası net", "Gerçekleşen ödemelerin dağılımı", "Seçili dönem gider özeti", "Bütün harcamalar", "Kalan ödeme yükünün dağılımı", "Gider dağılımı", "Kişi bazında güncel kalan borç", "PDF indir", "PDF paylaş", "Tüm kişileri kapsa"], "Ayrıntılı rapor/PDF ekranı eksik", failures)',
        'require("ExpansionTile(" not in reports, "Rapor ekranındaki gri blok riski kaldırılmadı", failures)':
            'require_all(reports, ["expandedDays", "report-person-", "ExpansionTile("], "Rapor açılır-kapanır ayrıntıları eksik", failures)',
        'require_all(reports, ["Bugün ve bu ay gider özeti", "Bugünkü toplam gider", "Bu ay ödemelere yapılan gider"], "Rapor güncel gider özeti eksik", failures)':
            'require_all(reports, ["Seçili dönem gider özeti", "Normal giderler", "Ödemeler", "Bütün harcamalar"], "Rapor filtreyle uyumlu gider özeti eksik", failures)',
    }
    for old, new in replacements.items():
        if old not in text:
            raise SystemExit(f"Doğrulayıcı alanı bulunamadı: {old[:80]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print("İkinci gözlem turu yapısal doğrulayıcısı güncellendi.")


if __name__ == "__main__":
    main()
