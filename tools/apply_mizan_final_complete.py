from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "a9e19466204a2f0882b176e3c297be76a04f0e46daed3f87c8c8e3657a088516"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_mizan_final_complete.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")
    part_dir = Path(__file__).with_name("mizan_final_complete_parts")
    parts = sorted(part_dir.glob("part*.txt"))
    if len(parts) != 6:
        raise SystemExit(f"Beklenen 6 patch parçası bulunamadı: {len(parts)}")
    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    patch = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Final patch SHA uyuşmuyor: {actual} != {PATCH_SHA256}")
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
        "lib/services/expense_browser_service.dart": "ExpenseBrowserService",
        "lib/models/mizan_models.dart": "BillPeriodAmount",
        "lib/screens/record_form_dialogs.dart": "RentEntryKind.productInstallment",
        "lib/screens/reports_screen.dart": "_ReportExpenseGroups",
        "test/performance_scaling_test.dart": "10 bin gider ve 10 bin ödeme",
    }
    missing = []
    for relative, token in required.items():
        path = root / relative
        if not path.is_file() or token not in path.read_text(encoding="utf-8"):
            missing.append(f"{relative}:{token}")
    if missing:
        raise SystemExit(f"Final kapsam eksik: {missing}")
    print(f"Final kapsam patch uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
