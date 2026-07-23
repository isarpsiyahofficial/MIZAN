from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import zlib
from pathlib import Path

from apply_overdue_calendar_fix import PATCH_SHA256, PATCH_ZLIB_BASE64


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_overdue_calendar_fix_v2.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")

    patch = zlib.decompress(base64.b64decode(PATCH_ZLIB_BASE64))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Patch SHA uyuşmuyor: {actual} != {PATCH_SHA256}")

    subprocess.run(
        ["patch", "-p1", "--forward", "--batch", "--reject-file=-"],
        cwd=root,
        input=patch,
        check=True,
    )
    print(f"Gecikme takvim patch uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
