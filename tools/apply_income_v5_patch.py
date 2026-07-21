from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "income_v5_patch_chunks"
EXPECTED_COMPRESSED_SHA = "06b15e1008ea0edc7d424bbb29f73f31bdada04af5e40a18e062ff4807c6fe43"
EXPECTED_PATCH_SHA = "5f36a41436cb52395f07675338a2639dcfa5ac8fc2f06275a3b44c99ffad7d76"
EXPECTED_CHUNK_COUNT = 7
FIX_COMPRESSED_SHA = "62ce95c327b4a7d2786e12193047eebce4955a819a8b6536b377a11a0d3513f5"
FIX_PATCH_SHA = "6bf1366587a6410085b3f7daab1de0a957a4d6222bd54a77b83e4b1bd1bea28c"


def decode_payload(paths: list[Path], compressed_sha: str, patch_sha: str) -> bytes:
    encoded = "".join(path.read_text(encoding="utf-8").strip() for path in paths)
    compressed = base64.b64decode(encoded, validate=True)
    actual_compressed = hashlib.sha256(compressed).hexdigest()
    if actual_compressed != compressed_sha:
        raise SystemExit(
            f"Payload compressed SHA mismatch: {actual_compressed} != {compressed_sha}"
        )
    patch = lzma.decompress(compressed)
    actual_patch = hashlib.sha256(patch).hexdigest()
    if actual_patch != patch_sha:
        raise SystemExit(f"Payload patch SHA mismatch: {actual_patch} != {patch_sha}")
    return patch


def apply_patch(patch: bytes, name: str) -> None:
    path = ROOT / f".{name}.patch"
    path.write_bytes(patch)
    try:
        subprocess.run(
            ["git", "apply", "--binary", "--whitespace=nowarn", str(path)],
            cwd=ROOT,
            check=True,
        )
    finally:
        path.unlink(missing_ok=True)


pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != EXPECTED_CHUNK_COUNT:
    raise SystemExit(
        f"Income v5 patch chunk count mismatch: {len(pieces)} != {EXPECTED_CHUNK_COUNT}"
    )
main_patch = decode_payload(pieces, EXPECTED_COMPRESSED_SHA, EXPECTED_PATCH_SHA)
apply_patch(main_patch, "mizan_income_v5")

fix_paths = sorted(CHUNKS.glob("fix*.txt"))
if len(fix_paths) != 1:
    raise SystemExit(f"Income v5 correction chunk count mismatch: {len(fix_paths)} != 1")
fix_patch = decode_payload(fix_paths, FIX_COMPRESSED_SHA, FIX_PATCH_SHA)
apply_patch(fix_patch, "mizan_income_v5_fix")

required = {
    "lib/models/mizan_models.dart": [
        "currentSchemaVersion = 7",
        "class IncomeEntry",
        "paymentNotificationSlots",
        "availableReportMonths",
        "unpaidDueDatesAt",
    ],
    "lib/controllers/mizan_controller.dart": [
        "_nextMonthlyDueDate",
        "addPaymentNotificationSlot",
        "addIncome",
    ],
    "lib/services/reminder_engine.dart": [
        "final overdue = dueDay.isBefore(today)",
    ],
    "test/income_monthly_due_notification_v5_test.dart": [
        "yeni aylık banka borcunun ilk vadesi",
        "gelir sıklıkları",
    ],
}
for relative, tokens in required.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise SystemExit(f"Income v5 validation failed for {relative}: {missing}")

print(
    "MIZAN income v5 main and correction patches applied: "
    f"main {len(main_patch)} bytes, correction {len(fix_patch)} bytes."
)
