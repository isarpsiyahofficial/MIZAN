from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "7164e9037c79f1c44460525a8b002563c729b7614a312c6acd74c8e6a6f9b884"
PATCH_ZLIB_BASE64 = "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"


def _replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Beklenen tek eşleşme bulunamadı: {path}: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_manual_overdue_sync_fix.py <kaynak-kökü>")
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

    _replace_once(
        root / "lib/screens/record_form_dialogs.dart",
        "        TextFormField(\n          controller: manualOverdueDays,",
        "        TextFormField(\n          key: const Key('manual-overdue-days-field'),\n          controller: manualOverdueDays,",
    )
    _replace_once(
        root / "test/overdue_calendar_tracking_test.dart",
        "    final today = dateOnly(DateTime.now());",
        "    final now = DateTime.now();\n    final today = DateTime(now.year, now.month, now.day);",
    )
    _replace_once(
        root / "test/manual_overdue_edit_confirmation_test.dart",
        "    final manualField = find.byWidgetPredicate(\n      (widget) =>\n          widget is TextFormField &&\n          widget.decoration?.labelText == 'Yeni manuel gecikme günü (opsiyonel)',\n    );",
        "    final manualField = find.byKey(const Key('manual-overdue-days-field'));",
    )

    required = {
        "lib/models/mizan_models.dart": [
            "_earliestOverdueAnchorAt",
            "currentManualOverdueDaysAt",
        ],
        "lib/controllers/mizan_controller.dart": [
            "replaceManualOverdueDays",
            "effectiveManualDays",
        ],
        "lib/screens/record_form_dialogs.dart": [
            "Gecikme gününü değiştir",
            "Gecikme hesabını yeniden kur",
            "Değişikliği onayla",
            "manual-overdue-days-field",
        ],
        "test/overdue_calendar_tracking_test.dart": [
            "manuel gecikme daha eskiyse",
            "ilgili olmayan düzenleme manuel gecikme referansını sıfırlamaz",
        ],
        "test/manual_overdue_edit_confirmation_test.dart": [
            "manuel gecikme değişikliği ayrı onay ister",
            "manual-overdue-days-field",
        ],
    }
    for relative, needles in required.items():
        text = (root / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise SystemExit(f"Eksik kapsam: {relative}: {needle}")

    print(f"Manuel gecikme senkronizasyon patch'i uygulandı: SHA-256 {actual}")


if __name__ == "__main__":
    main()
