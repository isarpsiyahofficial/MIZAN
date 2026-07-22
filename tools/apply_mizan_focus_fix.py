from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "9500c8568174712087c19419f79572eb09c2b3cf77cf9fe8af5aab9807cedee0"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_mizan_focus_fix.py <kaynak-kökü>")
    repository_root = Path(__file__).resolve().parents[1]
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")
    chunk_dir = repository_root / "mizan_focus_fix_chunks"
    encoded = "".join(
        path.read_text(encoding="utf-8").strip()
        for path in sorted(chunk_dir.glob("chunk*.txt"))
    )
    if not encoded:
        raise SystemExit("Patch parçaları bulunamadı.")
    patch = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Patch SHA uyuşmuyor: {actual} != {PATCH_SHA256}")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    with tempfile.NamedTemporaryFile(suffix=".patch", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        subprocess.run(["git", "apply", "--check", str(patch_path)], cwd=root, check=True)
        subprocess.run(["git", "apply", "--whitespace=nowarn", str(patch_path)], cwd=root, check=True)
    finally:
        patch_path.unlink(missing_ok=True)
    required = {
        "lib/services/notification_service.dart": ["AndroidScheduleMode.exactAllowWhileIdle", "Yaklaşık zamanlama kullanılmadı", "scheduleTestNotification"],
        "lib/screens/settings_screen.dart": ["Hatırlatma ayrıntısı", "1 dakika sonra test et", "CSV yedeğini mevcut verilerle birleştir"],
        "lib/services/csv_backup_service.dart": ["class CsvMergeResult", "mergeStates", "categoryIdMap"],
        "lib/screens/reports_screen.dart": ["ReportPeriod.monthly", "ReportPeriod.yearly", "_selectRecordedYear"],
        "tools/configure_android.py": ["SCHEDULE_EXACT_ALARM", "USE_FULL_SCREEN_INTENT", "showWhenLocked", "turnScreenOn"],
    }
    for relative, needles in required.items():
        text = (root / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise SystemExit(f"Zorunlu odak düzeltmesi eksik: {relative}: {needle}")
    print(f"MİZAN odak düzeltmesi uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
