from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "feedback_round_2026_07"
EXPECTED_COMPRESSED_SHA = "6aa04d966e2796f10325834423ba067ae5a141530e8369670c4c2e895339f820"
EXPECTED_PATCH_SHA = "993f2f54ca73f73c3b4b00ea9022b443a1da14bcd3f35445f753d42a7d57159e"

pieces = sorted(CHUNKS.glob("chunk*.txt"))
if len(pieces) != 1:
    raise SystemExit(f"Beklenen tek kullanıcı geri bildirim parçası bulunamadı: {pieces}")

encoded = "".join(path.read_text(encoding="utf-8").strip() for path in pieces)
compressed = base64.b64decode(encoded, validate=True)
compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        f"Geri bildirim paketi SHA uyuşmuyor: {compressed_sha} != {EXPECTED_COMPRESSED_SHA}"
    )

patch = lzma.decompress(compressed)
patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(
        f"Geri bildirim yaması SHA uyuşmuyor: {patch_sha} != {EXPECTED_PATCH_SHA}"
    )

patch_path = ROOT / ".mizan_user_feedback.patch"
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
    "lib/screens/people_screen.dart": [
        "Kişi detayları",
        "Kişinin kayıtları",
        "_showPersonDetails",
    ],
    "lib/screens/expenses_screen.dart": [
        "Tarih aralığı",
        "for (final item in _ExpensePeriod.values)",
    ],
    "lib/screens/reports_screen.dart": [
        "Bu ay gerçekleşen ödemeler",
        "Ödeme + gider toplamı",
        "paymentTotals",
    ],
    "lib/models/mizan_models.dart": [
        "scheduledAmountAt",
        "effectiveDueDateAt",
        "monthlyDueDay",
    ],
    "lib/screens/record_form_dialogs.dart": [
        "Her ayın belirli günü",
        "Her ayın ödeme günü (1-31)",
    ],
}
for relative, tokens in required.items():
    content = (ROOT / relative).read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in content]
    if missing:
        raise SystemExit(f"Kullanıcı geri bildirimi eksik uygulandı: {relative}: {missing}")

print(
    "Kullanıcı geri bildirim turu uygulandı: "
    f"{len(patch)} bayt, SHA-256 {patch_sha}."
)
