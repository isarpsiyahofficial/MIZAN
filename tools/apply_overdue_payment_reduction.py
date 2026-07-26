from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PATCH_SHA256 = "bcee7f6589753d1cae50d73fb1903a6032baf62e0b379670ffb01e045a8f408d"
PATCH_ZLIB_BASE64 = "eNqNVMFy2jAQvfsrNpeMPcbGUKAzOITQobdO02lzZ4S1Bs3INiPJadOGf4+EbGxDAvXFSN59u+/tWyhLUwiCDVNA+pyt+1lBkct+xv6SfGUPISVCwfriZ4flFP9AStNknSRh+HkyHEeTIQyiaDIaOUEQXMF3fN+/VuPhAYLRcNIbROCb93AA+irhREpY4lr9EAUtEwX/HDCPQFWKXL9kyVVs7vYOOD7Akih8YhnOYYMKMpKXhD8+o6Al/kKkyxJNhIbxDUzKcsKBkhcJs27wUt/F7SCSJ9tCnIb9xKQQFOlCVcEsBdfizSAvOYfXV4t/N4PIHGoc+9mrmZhDBVHdrKhu9DHnL65N8UJZrpUgiXKXpSCKFfmh0vSA73mH7L3jGzG+ManuainuYUU4r5jLp60oys3Wrb/qcikKzBP0uqpYnka0U9ItIWM7Dpthp6Gjm9LVuADCMJTJFmnJj7nHVpoOwozs3CNxr9fKpqjNIJDW86kwFupSum/TzVBadG6q0dze1gHmuWkEb2K9kMlFqlA0sK16ntcAvJtdEdiHqjAjcTei+E3WHKeQEi7Ri2s3G+FCWQjlNncdh5v9GH8a9wZD8MejSW9ycT0M4TLfEUZ1/98L9TXbqRcPjtM4s1hLQ6r/NuzvFucKLGVCKk+Lktv9sOyc4NQ1yw83KujO4xDYzKOdfg+R6TgAeGcJT9U+W0eYz1vOjrswyMlOHnx9TYF69WrCQUe/Vrc+uDWqbhzmxxpTTaPK27eXBXWNRLHn2sm6mdOrjrfjZrItp56mGL9+wbQQ+IFh69ajrs3+3wlnFRtx3gAzWRYh"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: apply_overdue_payment_reduction.py <kaynak-kökü>")
    root = Path(sys.argv[1]).resolve()
    patch = zlib.decompress(base64.b64decode(PATCH_ZLIB_BASE64))
    actual = hashlib.sha256(patch).hexdigest()
    if actual != PATCH_SHA256:
        raise SystemExit(f"Patch SHA uyuşmuyor: {actual}")
    with tempfile.NamedTemporaryFile(suffix=".patch", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        subprocess.run(
            ["patch", "-p1", "--forward", "--batch", "--reject-file=-"],
            cwd=root,
            stdin=patch_path.open("rb"),
            check=True,
        )
    finally:
        patch_path.unlink(missing_ok=True)
    print(f"Ödeme sonrası gecikme düşürme patch uygulandı: {actual}")


if __name__ == "__main__":
    main()
