from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "patch_chunks_v3"
EXPECTED_COMPRESSED_SHA = "aa80201c590c4f57177a3c453cadf0c5eecda4d929290d4ac465ca19429e28de"
EXPECTED_PATCH_SHA = "bada99cb6816c70ac9dd8504bf82a0209d109f6ff8ca8603d0c2d978f8763e28"
EXPECTED_CHUNK_COUNT = 18

pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != EXPECTED_CHUNK_COUNT:
    raise SystemExit(
        f"Revision patch chunk count mismatch: {len(pieces)} != {EXPECTED_CHUNK_COUNT}"
    )

encoded = "".join(path.read_text(encoding="utf-8").strip() for path in pieces)
try:
    compressed = base64.b64decode(encoded, validate=True)
except Exception as error:
    raise SystemExit(f"Revision patch base64 is invalid: {error}") from error

compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        "Revision patch compressed SHA mismatch: "
        f"{compressed_sha} != {EXPECTED_COMPRESSED_SHA}"
    )

try:
    patch = lzma.decompress(compressed)
except Exception as error:
    raise SystemExit(f"Revision patch cannot be decompressed: {error}") from error

patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(
        f"Revision patch SHA mismatch: {patch_sha} != {EXPECTED_PATCH_SHA}"
    )

patch_path = ROOT / ".mizan_revision.patch"
patch_path.write_bytes(patch)
try:
    subprocess.run(
        ["git", "apply", "--binary", "--whitespace=nowarn", str(patch_path)],
        cwd=ROOT,
        check=True,
    )
finally:
    patch_path.unlink(missing_ok=True)

print(
    "MIZAN v2 revision patch applied and verified: "
    f"{len(patch)} bytes, SHA-256 {patch_sha}."
)
