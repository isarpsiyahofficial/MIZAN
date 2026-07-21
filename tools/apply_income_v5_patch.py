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

pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != EXPECTED_CHUNK_COUNT:
    raise SystemExit(
        f"Income v5 patch chunk count mismatch: {len(pieces)} != {EXPECTED_CHUNK_COUNT}"
    )

encoded = "".join(path.read_text(encoding="utf-8").strip() for path in pieces)
compressed = base64.b64decode(encoded, validate=True)
compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        f"Income v5 compressed SHA mismatch: {compressed_sha} != {EXPECTED_COMPRESSED_SHA}"
    )

patch = lzma.decompress(compressed)
patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(
        f"Income v5 patch SHA mismatch: {patch_sha} != {EXPECTED_PATCH_SHA}"
    )

patch_path = ROOT / ".mizan_income_v5.patch"
patch_path.write_bytes(patch)
try:
    subprocess.run(
        ["git", "apply", "--binary", "--whitespace=nowarn", str(patch_path)],
        cwd=ROOT,
        check=True,
    )
finally:
    patch_path.unlink(missing_ok=True)

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
    "MIZAN income v5 patch applied and verified: "
    f"{len(patch)} bytes, SHA-256 {patch_sha}."
)
