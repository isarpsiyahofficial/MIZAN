from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "payment_notification_round2_chunks"
EXPECTED_COMPRESSED_SHA = "8c007224fe341efe200428425a27bb571d1b7d62816fb05913caa85448b44f38"
EXPECTED_PATCH_SHA = "9298cc00370a6ce12b0b34e891af7dcee5c48aee9f25f793c4dedd8c3c83ec94"
EXPECTED_CHUNK_COUNT = 2

pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != EXPECTED_CHUNK_COUNT:
    raise SystemExit(
        f"Payment/notification patch chunk count mismatch: "
        f"{len(pieces)} != {EXPECTED_CHUNK_COUNT}"
    )

encoded = "".join(path.read_text(encoding="utf-8").strip() for path in pieces)
compressed = base64.b64decode(encoded, validate=True)
compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        f"Payment/notification compressed SHA mismatch: "
        f"{compressed_sha} != {EXPECTED_COMPRESSED_SHA}"
    )
patch = lzma.decompress(compressed)
patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(
        f"Payment/notification patch SHA mismatch: "
        f"{patch_sha} != {EXPECTED_PATCH_SHA}"
    )

patch_path = ROOT / ".mizan_payment_notification_round2.patch"
patch_path.write_bytes(patch)
try:
    subprocess.run(
        [
            "git",
            "apply",
            "--binary",
            "--whitespace=nowarn",
            str(patch_path),
        ],
        cwd=ROOT,
        check=True,
    )
finally:
    patch_path.unlink(missing_ok=True)

print(
    "Payment type, installment tracking and notification settings patch applied: "
    f"{len(patch)} bytes, SHA-256 {patch_sha}."
)
