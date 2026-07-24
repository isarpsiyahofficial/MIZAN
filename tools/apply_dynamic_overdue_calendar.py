from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "90fd058ddea3d2379e7a5735964b6797251f9e0891746332aa5266bb8ced0c4a"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_dynamic_overdue_calendar.py <kaynak-kökü>")

    source_root = Path(sys.argv[1]).resolve()
    if not (source_root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {source_root}")

    repository_root = Path(__file__).resolve().parents[1]
    part_dir = repository_root / ".overdue_patch_parts"
    parts = sorted(part_dir.glob("part*"))
    if len(parts) != 5:
        raise SystemExit(f"Beklenen 5 patch parçası bulunamadı: {parts}")

    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    patch = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Patch SHA uyuşmuyor: {actual} != {PATCH_SHA256}")

    subprocess.run(["git", "init", "-q"], cwd=source_root, check=True)
    with tempfile.NamedTemporaryFile(suffix=".patch", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        subprocess.run(
            ["git", "apply", "--whitespace=nowarn", str(patch_path)],
            cwd=source_root,
            check=True,
        )
    finally:
        patch_path.unlink(missing_ok=True)

    required = {
        "lib/models/mizan_models.dart": [
            "currentSchemaVersion = 10",
            "manualOverdueSince",
            "manualOverduePeriods",
            "overdueDays",
        ],
        "lib/services/csv_backup_service.dart": [
            "hydrateLegacyOverdueAnchors",
            "manualOverduePeriods",
        ],
        "lib/services/local_store.dart": ["hydrateLegacyOverdueAnchors"],
        "lib/screens/record_form_dialogs.dart": [
            "Gecikmiş aylar (opsiyonel)",
            "İlk geçerli vade",
        ],
        "test/overdue_calendar_tracking_test.dart": [
            "10 günlük eski CSV",
            "ödeme ile azalır",
        ],
    }
    for relative, needles in required.items():
        text = (source_root / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise SystemExit(f"Eksik kapsam: {relative}: {needle}")

    print(f"Dinamik gecikme/takvim patch uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
