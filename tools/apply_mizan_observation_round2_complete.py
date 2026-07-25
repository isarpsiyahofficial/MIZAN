from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "3ee2d9327304ef44507061d7650b2dd17d857aea6192d66542d2e355e15ba744"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Kullanım: apply_mizan_observation_round2_complete.py <source-root>"
        )
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"MİZAN kaynak kökü bulunamadı: {root}")

    chunk_dir = Path(__file__).resolve().parent / "round2_patch_chunks"
    chunks = sorted(chunk_dir.glob("chunk_*.txt"))
    if len(chunks) != 5:
        raise SystemExit(f"Tam patch parçaları eksik: {chunks}")
    encoded = "".join(chunk.read_text(encoding="utf-8").strip() for chunk in chunks)
    patch = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"İkinci gözlem tam patch SHA uyuşmuyor: {actual}")

    with tempfile.NamedTemporaryFile(suffix=".patch") as handle:
        handle.write(patch)
        handle.flush()
        subprocess.run(
            ["patch", "--batch", "--forward", "-p1", "-i", handle.name],
            cwd=root,
            check=True,
        )

    required = {
        "lib/services/csv_backup_service.dart": [
            "duplicateCheckpoint",
            "duplicateCount: userDuplicateCount",
        ],
        "lib/models/mizan_models.dart": [
            "missedDuePeriodsAt",
            "byMonth",
        ],
        "lib/screens/people_screen.dart": [
            "_PersonMetricDetailSheet",
            "Detayı gör",
        ],
        "lib/screens/expenses_screen.dart": [
            "enum _ExpenseView",
            "_PaymentExpenseGroups",
            "Bütün harcamalar",
        ],
        "lib/screens/reports_screen.dart": [
            "_ReportMetricDetailSheet",
            "_ReportOutflowGroups",
            "Bütün harcama ayrıntıları",
        ],
        "lib/services/pdf_report_service.dart": [
            "_stableTone",
            "_dayHeader",
            "Günlük harcamalar",
        ],
        "test/report_service_test.dart": [
            "gecikmiş aylık taksitler bütün açık dönemleriyle toplanır",
        ],
    }
    missing: list[str] = []
    for relative, tokens in required.items():
        source = (root / relative).read_text(encoding="utf-8")
        for token in tokens:
            if token not in source:
                missing.append(f"{relative}:{token}")
    if missing:
        raise SystemExit(f"İkinci gözlem tam kapsamı eksik: {missing}")
    print("MİZAN ikinci gözlem turu tam patch'i uygulandı.")


if __name__ == "__main__":
    main()
