from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_chunk(directory: str, index: int) -> str:
    name = f"chunk{index:02d}.txt"
    path = ROOT / directory / name
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    result = subprocess.run(
        ["git", "show", f"HEAD:{directory}/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def decode_patch(
    *,
    label: str,
    directory: str,
    chunk_count: int,
    compressed_sha_expected: str,
    patch_sha_expected: str,
) -> bytes:
    pieces = [read_chunk(directory, index) for index in range(chunk_count)]
    if any(not piece for piece in pieces):
        raise SystemExit(f"{label} contains an empty chunk.")

    encoded = "".join(pieces)
    try:
        compressed = base64.b64decode(encoded, validate=True)
    except Exception as error:
        raise SystemExit(f"{label} base64 is invalid: {error}") from error

    compressed_sha = hashlib.sha256(compressed).hexdigest()
    if compressed_sha != compressed_sha_expected:
        raise SystemExit(
            f"{label} compressed SHA mismatch: "
            f"{compressed_sha} != {compressed_sha_expected}"
        )

    try:
        patch = lzma.decompress(compressed)
    except Exception as error:
        raise SystemExit(f"{label} cannot be decompressed: {error}") from error

    patch_sha = hashlib.sha256(patch).hexdigest()
    if patch_sha != patch_sha_expected:
        raise SystemExit(
            f"{label} patch SHA mismatch: {patch_sha} != {patch_sha_expected}"
        )
    print(
        f"{label} decoded: {len(patch)} bytes, "
        f"compressed SHA-256 {compressed_sha}, patch SHA-256 {patch_sha}."
    )
    return patch


def apply_patch(label: str, filename: str, patch: bytes) -> None:
    patch_path = ROOT / filename
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
    print(f"{label} applied successfully.")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            return
        raise SystemExit(f"Round 3 compatibility target not found: {label}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


main_patch = decode_patch(
    label="MIZAN round 3 main patch",
    directory="round3_patch_chunks_v2",
    chunk_count=9,
    compressed_sha_expected=(
        "e524b6dbaa37c730e751dcab80e19a412af6c155b84a0de2fb4f556b47170fb1"
    ),
    patch_sha_expected=(
        "111b63c5e5edd7e0746719865ee0a615c4fbb5a07fcee24483048e95514168e5"
    ),
)
new_files_patch = decode_patch(
    label="MIZAN round 3 report and PDF files patch",
    directory="round3_newfiles_chunks",
    chunk_count=4,
    compressed_sha_expected=(
        "b9f8a7b7eb92d6a1ee692a6ad3b7a41b98432ba6b0e0a50302950a131e3ceb14"
    ),
    patch_sha_expected=(
        "a97901123ac1b34406f358f6c45d5893fd6d2896660e30e71d0b5aa710dbbcb1"
    ),
)

apply_patch("MIZAN round 3 main patch", ".mizan_round3.patch", main_patch)
apply_patch(
    "MIZAN round 3 report and PDF files patch",
    ".mizan_round3_newfiles.patch",
    new_files_patch,
)

replace_once(
    ROOT / "test/controller_test.dart",
    "expect(updated.payments.last.entryType, PaymentEntryType.installment);",
    "expect(updated.payments.first.entryType, PaymentEntryType.installment);",
    "new payment order assertion",
)
replace_once(
    ROOT / "test/controller_test.dart",
    "expect(updated.paidInstallmentCount, greaterThanOrEqualTo(1));",
    "expect(updated.remainingAmount, 7000);",
    "controller payment balance assertion",
)
replace_once(
    ROOT / "lib/screens/reports_screen.dart",
    "    var working = {...selectedPersonIds};",
    "    final working = {...selectedPersonIds};",
    "final report person selection",
)
replace_once(
    ROOT / "lib/screens/settings_screen.dart",
    """                    : (value) {
                        if (value != null) {
                          controller.setPaymentReminderFrequency(value);
                        }
                      },""",
    """                    : (value) async {
                        if (value != null) {
                          await controller.setPaymentReminderFrequency(value);
                        }
                      },""",
    "await reminder frequency update",
)
replace_once(
    ROOT / "lib/screens/settings_screen.dart",
    """                    : (value) {
                        if (value != null) {
                          controller.setNotificationSoundMode(value);
                        }
                      },""",
    """                    : (value) async {
                        if (value != null) {
                          await controller.setNotificationSoundMode(value);
                        }
                      },""",
    "await notification sound update",
)
replace_once(
    ROOT / "lib/services/pdf_report_service.dart",
    "const Rect.fromLTWH(0, 0, pageWidth.toDouble(), pageHeight.toDouble())",
    "Rect.fromLTWH(0, 0, pageWidth.toDouble(), pageHeight.toDouble())",
    "non-constant PDF canvas rectangle",
)

report_test = ROOT / "test/report_service_test.dart"
report_test_text = report_test.read_text(encoding="utf-8")
report_test_text = report_test_text.replace(
    "const MizanReportService().build(",
    "MizanReportService().build(",
)
report_test_text = report_test_text.replace(
    "const ReportFilter(",
    "ReportFilter(",
)
if "const MizanReportService().build(" in report_test_text:
    raise SystemExit("Const report-service invocation remains in tests.")
report_test.write_text(report_test_text, encoding="utf-8")

required = [
    ROOT / "lib/services/report_service.dart",
    ROOT / "lib/services/pdf_report_service.dart",
    ROOT / "test/report_service_test.dart",
    ROOT / "test/pdf_report_test.dart",
]
missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
if missing:
    raise SystemExit(f"Round 3 new files are missing after patch application: {missing}")

print("MIZAN round 3 complete revision and compatibility fixes applied.")
