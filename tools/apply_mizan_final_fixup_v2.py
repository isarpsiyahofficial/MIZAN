from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from apply_mizan_final_fixup import PATCH_BASE64, PATCH_SHA256


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_mizan_final_fixup_v2.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"MİZAN kaynak kökü bulunamadı: {root}")

    patch = zlib.decompress(base64.b64decode("".join(PATCH_BASE64.split())))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Final fixup SHA uyuşmuyor: {actual}")

    with tempfile.NamedTemporaryFile(suffix=".patch") as temp:
        temp.write(patch)
        temp.flush()
        subprocess.run(
            ["git", "apply", "--whitespace=nowarn", temp.name],
            cwd=root,
            check=True,
        )

    required = {
        "lib/services/reminder_engine.dart": "safeMaximumPaymentReminders",
        "lib/services/notification_service.dart": "_isAlarmCapacityError",
        "lib/services/local_store.dart": "_atomicWrite",
        "lib/screens/expenses_screen.dart": "Tarih aralığı",
        "lib/screens/people_screen.dart": "Ödenmemiş toplam",
        "test/reminder_engine_test.dart": "alarm sınırını aşmadan",
    }
    missing = []
    for relative, token in required.items():
        path = root / relative
        if not path.is_file() or token not in path.read_text(encoding="utf-8"):
            missing.append(f"{relative}:{token}")
    if missing:
        raise SystemExit(f"Final fixup kapsamı eksik: {missing}")
    print("MİZAN final fixup v2 katmanı SHA doğrulamasıyla uygulandı.")


if __name__ == "__main__":
    main()
