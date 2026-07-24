from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import traceback
import zlib
from pathlib import Path

PATCH_SHA256 = "90fd058ddea3d2379e7a5735964b6797251f9e0891746332aa5266bb8ced0c4a"


def apply_patch(source_root: Path) -> None:
    log_dir = source_root / "ci-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "apply-dynamic-overdue.log"

    def emit(message: object) -> None:
        text = str(message)
        print(text)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(text + "\n")

    repository_root = Path(__file__).resolve().parents[1]
    part_dir = repository_root / ".overdue_patch_parts"
    parts = sorted(part_dir.glob("part*"))
    emit(f"Patch parçaları: {[(part.name, part.stat().st_size) for part in parts]}")
    if len(parts) != 5:
        raise RuntimeError(f"Beklenen 5 patch parçası bulunamadı: {parts}")

    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    emit(f"Kodlanmış patch uzunluğu: {len(encoded)}")
    compressed = base64.b64decode(encoded, validate=True)
    emit(f"Sıkıştırılmış patch uzunluğu: {len(compressed)}")
    patch = zlib.decompress(compressed)
    actual = hashlib.sha256(patch).hexdigest()
    emit(f"Patch uzunluğu: {len(patch)}")
    emit(f"Patch SHA-256: {actual}")
    if actual != PATCH_SHA256:
        raise RuntimeError(f"Patch SHA uyuşmuyor: {actual} != {PATCH_SHA256}")

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
                raise RuntimeError(f"Eksik kapsam: {relative}: {needle}")

    emit(f"Dinamik gecikme/takvim patch uygulandı: SHA-256 {actual}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_dynamic_overdue_calendar.py <kaynak-kökü>")
    source_root = Path(sys.argv[1]).resolve()
    if not (source_root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {source_root}")
    try:
        apply_patch(source_root)
    except BaseException as exc:
        log_dir = source_root / "ci-logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "apply-dynamic-overdue.log").open("a", encoding="utf-8") as handle:
            handle.write(f"HATA: {type(exc).__name__}: {exc}\n")
            handle.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
