from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "feedback_patch_chunks"
EXPECTED_COMPRESSED_SHA = (
    "f06a7017bd209a2d40e04c0ab1043adbb5effac2b70b05cde9b898852bc3cb86"
)
EXPECTED_PATCH_SHA = (
    "5b2765f3efdcbc5c3654a15018c460d524bc98360b4369f7d35287aaea88c987"
)
EXPECTED_CHUNK_COUNT = 1

pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != EXPECTED_CHUNK_COUNT:
    raise SystemExit(
        f"Phone feedback patch chunk count mismatch: "
        f"{len(pieces)} != {EXPECTED_CHUNK_COUNT}"
    )

encoded = "".join(path.read_text(encoding="utf-8").strip() for path in pieces)
try:
    compressed = base64.b64decode(encoded, validate=True)
except Exception as error:
    raise SystemExit(f"Phone feedback patch base64 is invalid: {error}") from error

compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        "Phone feedback compressed SHA mismatch: "
        f"{compressed_sha} != {EXPECTED_COMPRESSED_SHA}"
    )

try:
    patch = lzma.decompress(compressed)
except Exception as error:
    raise SystemExit(f"Phone feedback patch cannot be decompressed: {error}") from error

patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(
        f"Phone feedback patch SHA mismatch: {patch_sha} != {EXPECTED_PATCH_SHA}"
    )

patch_path = ROOT / ".mizan_feedback.patch"
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
    "Phone feedback patch applied and verified: "
    f"{len(patch)} bytes, SHA-256 {patch_sha}."
)
