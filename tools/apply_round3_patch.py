from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "round3_patch_chunks"
EXPECTED_COMPRESSED_SHA = (
    "e524b6dbaa37c730e751dcab80e19a412af6c155b84a0de2fb4f556b47170fb1"
)
EXPECTED_PATCH_SHA = (
    "111b63c5e5edd7e0746719865ee0a615c4fbb5a07fcee24483048e95514168e5"
)
EXPECTED_CHUNK_COUNT = 1

pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != EXPECTED_CHUNK_COUNT:
    raise SystemExit(
        f"Round 3 patch chunk count mismatch: {len(pieces)} != {EXPECTED_CHUNK_COUNT}"
    )

encoded = "".join(path.read_text(encoding="utf-8").strip() for path in pieces)
try:
    compressed = base64.b64decode(encoded, validate=True)
except Exception as error:
    raise SystemExit(f"Round 3 patch base64 is invalid: {error}") from error

compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        "Round 3 compressed SHA mismatch: "
        f"{compressed_sha} != {EXPECTED_COMPRESSED_SHA}"
    )

try:
    patch = lzma.decompress(compressed)
except Exception as error:
    raise SystemExit(f"Round 3 patch cannot be decompressed: {error}") from error

patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(
        f"Round 3 patch SHA mismatch: {patch_sha} != {EXPECTED_PATCH_SHA}"
    )

patch_path = ROOT / ".mizan_round3.patch"
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
    "MIZAN round 3 patch applied and verified: "
    f"{len(patch)} bytes, SHA-256 {patch_sha}."
)
