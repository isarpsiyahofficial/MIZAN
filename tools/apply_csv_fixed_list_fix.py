from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "1513c7bdc2ae231f9ab5e914f36b3096d85f08c51d213fd2e7ac135a1d799972"
PATCH_ZLIB_BASE64 = "eNqtVFtum0AU/fcq7h8gA7GJX3HaKm2aj1RJWymRqiqqrDFck1FgcGcGNyTKWryG7iHZV4eXDRS3VlVLCHznnPs8cz26WIBl+VQCOQjo/EAgX1EXxYErVrM5ce/i5ayw2R7hEuZ7wTqUeXgPQzLEYd+17dF4MZhMJtDv9UaDQceyrD3jdbrd7r4xT07AciZH5hi66esIlMENiBBwKlbvMsJVjofHDqQ/47gD+deCMhKASyT6EU/OvUuyhNfw6kpyynwT8vebx6fjjlWBx5wjk6c5i6JQlFlIlkIvTj6IiN1oeL9EJnAL076pwN19/OQogL/5M3OgYSuWPnODiKGqwLBldEGF1H0e/SDzAKcgeYxp1VnwiIOeZ0DDZcQleoXPBCgrMihPdpdilN0syykp515ah8R7qTf932jUy7rQSvxIQkypLOIhCegDtvCZwmQevKqEJQpZ1Uf6v9TtzrNCrB5xyGAxsm0yPhwfDvp1se5m5wrdfZ7Kst8/MkfQTV/KsbKsIupBSCjTjaoYAZ4yTapppg6K+Wvz6GUNd0XTIVAjRUEZQoKMbu0rBJ96yAHvAmQ4pwHlWqGMLEwppogJCcXVUX1u3g69VGdDnwp6SR8Iu5Iqoo3hUia6YbvRMvlC5e1GqwC/qWRaxLwphVpBtR02EyjH/x8y2GIAzmqoRKfeVPU6a4WVtlYzIZWZMn6tNlozKlW0V9QW5lxiqFftAM2AVjY/zayjtlupmV4dV8211dH3mDBJZTKFfuMkZlR+5mr2U3CGvcahUOnLt3IK71Ui1zRE3ek5IxPGJjiOUQO3dyYdZ32gqlPlQMsVnpuyyW6ue1MHXN2JiNdoOTSnlV5baHEgK6QQuY8ZZ7OqzY3zarbpRF2p5w5skcuuqS0Tbom4QOYrCfaNbfA/kP+JY6s77wdob/Vg1vWwyw3xPLU6ozit0ueo6Pz6lrBP/EwpIriOdGeTwVM2tKwFUO6gzKOWr5byDggK6gkDBHxZB+qhPN0/yUZ74EXPax5vCAnCnDyvA8Kef6bChM1W+gVqRqsc"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_csv_fixed_list_fix.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")

    patch = zlib.decompress(base64.b64decode(PATCH_ZLIB_BASE64))
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

    service = (root / "lib/services/csv_backup_service.dart").read_text(encoding="utf-8")
    test = (root / "test/csv_backup_test.dart").read_text(encoding="utf-8")
    required = [
        ".map(_cloneMap).toList(growable: true)",
        "boş kategori listesine yeni kategori ve gider eklenebilir",
        "final restored = service.importState(exported);",
    ]
    combined = service + test
    missing = [needle for needle in required if needle not in combined]
    if missing:
        raise SystemExit(f"CSV sabit liste düzeltmesi eksik: {missing}")

    print(f"CSV sabit uzunluklu liste düzeltmesi uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
