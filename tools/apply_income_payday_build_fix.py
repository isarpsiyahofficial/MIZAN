from __future__ import annotations

import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: beklenen 1 eşleşme, bulunan {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_income_payday_build_fix.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "pubspec.yaml").is_file():
        raise SystemExit(f"Flutter kaynak kökü bulunamadı: {root}")

    configure = root / "tools/configure_android.py"
    replace_once(
        configure,
        """text = text.replace('android:launchMode=\"singleTop\"', 'android:launchMode=\"singleTop\"\\n            android:showWhenLocked=\"true\"\\n            android:turnScreenOn=\"true\"')""",
        """if 'android:showWhenLocked=\"true\"' not in text:
    text = text.replace(
        'android:launchMode=\"singleTop\"',
        'android:launchMode=\"singleTop\"\\n            android:showWhenLocked=\"true\"',
        1,
    )
if 'android:turnScreenOn=\"true\"' not in text:
    text = text.replace(
        'android:showWhenLocked=\"true\"',
        'android:showWhenLocked=\"true\"\\n            android:turnScreenOn=\"true\"',
        1,
    )""",
    )

    validator = root / "tools/validate_project.py"
    text = validator.read_text(encoding="utf-8")
    if 'currentSchemaVersion = 8' not in text:
        raise SystemExit("Eski şema doğrulaması bulunamadı.")
    validator.write_text(
        text.replace('currentSchemaVersion = 8', 'currentSchemaVersion = 9'),
        encoding="utf-8",
    )

    configure_text = configure.read_text(encoding="utf-8")
    if configure_text.count("android:showWhenLocked") != 2:
        raise SystemExit("Android kilit ekranı koruması beklenen idempotent yapıda değil.")
    if configure_text.count("android:turnScreenOn") != 2:
        raise SystemExit("Android ekran açma koruması beklenen idempotent yapıda değil.")
    if "currentSchemaVersion = 9" not in validator.read_text(encoding="utf-8"):
        raise SystemExit("Şema 9 doğrulaması uygulanmadı.")

    print("Gelir sürümü Android ve şema build korumaları uygulandı.")


if __name__ == "__main__":
    main()
