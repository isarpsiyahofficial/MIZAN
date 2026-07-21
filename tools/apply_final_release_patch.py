from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "release_round_2026_07_21"
EXPECTED_COMPRESSED_SHA = "7bf1d1d5417632271439fc64a9c471b90c0afb88f13d4f3d0120b450f6c4aeec"
EXPECTED_PATCH_SHA = "0bbd52e3a3375292858e634a71bcf87cc40774a1add94ceea01ba970a07a0674"
EXPECTED_CHUNK_COUNT = 8

pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != EXPECTED_CHUNK_COUNT:
    raise SystemExit(
        f"Final release patch chunk count mismatch: {len(pieces)} != {EXPECTED_CHUNK_COUNT}"
    )
encoded = "".join(path.read_text(encoding="utf-8").strip() for path in pieces)
compressed = base64.b64decode(encoded, validate=True)
compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        f"Final release compressed SHA mismatch: {compressed_sha} != {EXPECTED_COMPRESSED_SHA}"
    )
patch = lzma.decompress(compressed)
patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(f"Final release patch SHA mismatch: {patch_sha} != {EXPECTED_PATCH_SHA}")
patch_path = ROOT / ".mizan_final_release.patch"
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
    "lib/screens/record_form_dialogs.dart": [
        "Taksit ödemesi",
        "Borcu / kaydı kapat",
        "Kısmi ödeme",
        "Ödenen taksit sayısı",
    ],
    "lib/screens/settings_screen.dart": [
        "Bildirim sesi",
        "Ödeme bildirimi sıklığı",
        "Hatırlatmaya başlama",
    ],
    "lib/screens/reports_screen.dart": [
        "PDF indir",
        "PDF paylaş",
        "Rapor dönemi",
        "Kişi bazında kalan borç",
    ],
    "lib/services/report_service.dart": [
        "ReportPeriod.allTime",
        "realizedGrandTotal",
        "personRemainingTotals",
    ],
    "lib/services/report_pdf_service.dart": [
        "PdfPageFormat.a4",
        "Gerçekleşen ödeme ayrıntıları",
        "Kalan ödeme yükü ayrıntıları",
    ],
}
for relative, tokens in required.items():
    content = (ROOT / relative).read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in content]
    if missing:
        raise SystemExit(f"Final release validation failed for {relative}: {missing}")

print(
    "Final MIZAN payment, notification and PDF revision applied: "
    f"{len(patch)} bytes, SHA-256 {patch_sha}."
)
