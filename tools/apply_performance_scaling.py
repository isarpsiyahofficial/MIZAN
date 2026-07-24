from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "cf915fb2439be6134bfb7f72e9a0d9876f6170c81d1ec79a8e8abcd0f034b4eb"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_performance_scaling.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")

    repository_root = Path(__file__).resolve().parents[1]
    part_dir = repository_root / ".performance_patch_parts"
    parts = sorted(part_dir.glob("part*"))
    if len(parts) != 4:
        raise SystemExit(f"Beklenen 4 patch parçası bulunamadı: {parts}")

    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    compressed = base64.b64decode(encoded, validate=True)
    patch = zlib.decompress(compressed)
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Patch SHA uyuşmuyor: {actual} != {PATCH_SHA256}")

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    with tempfile.NamedTemporaryFile(suffix=".patch", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        subprocess.run(
            ["git", "apply", "--whitespace=nowarn", str(patch_path)],
            cwd=root,
            check=True,
        )
    finally:
        patch_path.unlink(missing_ok=True)

    required = {
        "lib/services/local_store.dart": ["Isolate.run", "jsonEncode(envelope)"],
        "lib/controllers/mizan_controller.dart": [
            "_notificationSnapshot",
            "reschedule: false",
        ],
        "lib/screens/people_screen.dart": ["Tümünü aç", "_showAllRecordCards"],
        "lib/screens/expenses_screen.dart": ["expenses-load-more", "categoryTotals"],
        "test/performance_scaling_test.dart": [
            "10 bin kayıt",
            "10 bin gider",
            "bildirim planını boş yere kurmaz",
        ],
    }
    for relative, needles in required.items():
        text = (root / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise SystemExit(f"Eksik performans kapsamı: {relative}: {needle}")

    print(
        "Performans ölçekleme patch'i uygulandı: "
        f"{len(parts)} parça, SHA-256 {actual}"
    )


if __name__ == "__main__":
    main()
