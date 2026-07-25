from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "44abb8c88ec8cf51af735ab6236e05e037df4c9844da2a1873aab4150e4f69ce"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_mizan_audit_correctness_final.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"MİZAN kaynak kökü bulunamadı: {root}")

    chunk_dir = Path(__file__).resolve().parent / "mizan_audit_patch_chunks"
    chunks = sorted(chunk_dir.glob("*.txt"))
    if not chunks:
        raise SystemExit("Nihai denetim patch parçaları bulunamadı.")
    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in chunks)
    patch = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Nihai denetim patch SHA uyuşmuyor: {actual}")

    with tempfile.NamedTemporaryFile(suffix=".patch") as handle:
        handle.write(patch)
        handle.flush()
        subprocess.run(
            ["patch", "--batch", "--forward", "-p1", "-i", handle.name],
            cwd=root,
            check=True,
        )

    required = {
        "lib/services/csv_backup_service.dart": ["countDuplicates: false", "if (countDuplicates) tracker.duplicate++"],
        "lib/controllers/mizan_controller.dart": ["duplicateCount > 0"],
        "lib/screens/people_screen.dart": ["Kalan toplam ayrıntıları", "Bu ay planlanan ayrıntıları", "Gecikmiş kayıt ayrıntıları", "subscription.outstandingAmountAt(now)"],
        "lib/services/outflow_service.dart": ["enum OutflowView", "class OutflowPaymentDetail"],
        "lib/screens/expenses_screen.dart": ["Günlük harcamalar", "Ödemeler", "Bütün harcamalar", "expandedDays.remove(key)"],
        "lib/services/report_service.dart": ["referenceDate", "overdueLoad", "subscription.outstandingAmountAt(reference)"],
        "lib/screens/reports_screen.dart": ["_SelectedExpenseOverview", "_showRemainingDetails", "Kişi bazında güncel kalan borç", "_ReportOutflowGroups"],
        "lib/services/pdf_report_service.dart": ["HSLColor.fromAHSL", "_dayHeader", "Bütün harcama ayrıntıları"],
        "lib/models/mizan_models.dart": ["missedDuePeriodsAt", "rent.overdueAmountAt(reference)", "subscription.overdueAmountAt(reference)", "subscription.outstandingAmountAt(reference)", "double outstandingAmountAt(DateTime reference)", "DateTime effectiveDueDateAt(DateTime reference)", "overdueDueDatesAt(DateTime reference)", "amountForMonth(DateTime month)", "final value = amount - paidAmount;"],
        "test/audit_correctness_final_test.dart": ["closeTo(23622", "bütün gecikmiş aylık dönemler ödendiğinde manuel gecikme yeniden açılmaz"],
        "test/calculation_engine_audit_test.dart": ["aynı ödeme kayıtlarını bir kez sayar", "abonelikte bütün geçmiş açık dönemler", "abonelik gecikme toplamı rapor ve kişi özetine kümülatif yansır", "outstandingAmountAt(reference)"],
        "test/audit_ui_final_test.dart": ["tüm zamanlardan aylığa dönüş"],
        "tools/validate_audit_correctness_final.py": ["MİZAN nihai denetim doğrulaması geçti"],
        "docs/REQUIREMENTS_250_PLUS.md": ["402."],
    }
    missing: list[str] = []
    for relative, tokens in required.items():
        path = root / relative
        if not path.is_file():
            missing.append(f"{relative}:dosya yok")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                missing.append(f"{relative}:{token}")

    forbidden = {
        "lib/screens/people_screen.dart": ["Ödenmeyen dönemler:", "Ödenmeyen aylar:"],
        "lib/screens/reports_screen.dart": ["Kalan taksit sayıları"],
    }
    for relative, tokens in forbidden.items():
        text = (root / relative).read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                missing.append(f"{relative}:yasak metin {token}")

    if missing:
        raise SystemExit(f"Nihai denetim kapsamı eksik: {missing}")
    print("MİZAN hesaplama, rapor, gider, CSV ve PDF nihai denetim patch'i uygulandı.")


if __name__ == "__main__":
    main()
