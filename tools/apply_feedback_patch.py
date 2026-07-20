from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "feedback_patch_chunks_v3"
EXPECTED_COMPRESSED_SHA = (
    "8c546e74a304f8b4a334ba1a1abfeea8e43f0acf587fb04b7067551f27a18ef0"
)
EXPECTED_PATCH_SHA = (
    "99594d859172330cc834c3ef9c0a909db6da8c0215d5719569641623714f4de2"
)
EXPECTED_CHUNK_COUNT = 6

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

format_result = subprocess.run(
    ["dart", "format", "lib", "test"],
    cwd=ROOT,
    check=False,
)
if format_result.returncode != 0:
    raise SystemExit(
        f"Phone feedback Dart format failed with code {format_result.returncode}."
    )
