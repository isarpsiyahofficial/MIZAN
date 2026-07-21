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
    compressed = base64.b64decode(encoded, validate=True)
    compressed_sha = hashlib.sha256(compressed).hexdigest()
    if compressed_sha != compressed_sha_expected:
        raise SystemExit(
            f"{label} compressed SHA mismatch: "
            f"{compressed_sha} != {compressed_sha_expected}"
        )

    patch = lzma.decompress(compressed)
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
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return
    if new in text:
        return
    raise SystemExit(f"Round 3 compatibility target not found: {label}")


def ensure_async_value_callback(path: Path, call: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    call_pos = text.find(call)
    if call_pos < 0:
        raise SystemExit(f"Notification callback call not found: {label}")

    awaited_call = f"await {call}"
    if awaited_call not in text:
        text = text.replace(call, awaited_call, 1)
        call_pos = text.find(awaited_call)
    else:
        call_pos = text.find(awaited_call)

    async_marker = ": (value) async {"
    plain_marker = ": (value) {"
    async_pos = text.rfind(async_marker, 0, call_pos)
    plain_pos = text.rfind(plain_marker, 0, call_pos)
    if async_pos < plain_pos:
        if plain_pos < 0 or call_pos - plain_pos > 500:
            raise SystemExit(f"Notification callback declaration not found: {label}")
        text = text[:plain_pos] + async_marker + text[plain_pos + len(plain_marker) :]

    path.write_text(text, encoding="utf-8")


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

settings_path = ROOT / "lib/screens/settings_screen.dart"
ensure_async_value_callback(
    settings_path,
    "controller.setPaymentReminderFrequency(value);",
    "payment reminder frequency",
)
ensure_async_value_callback(
    settings_path,
    "controller.setNotificationSoundMode(value);",
    "notification sound mode",
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
report_test_text = report_test_text.replace("const ReportFilter(", "ReportFilter(")
if "const MizanReportService().build(" in report_test_text:
    raise SystemExit("Const report-service invocation remains in tests.")
report_test.write_text(report_test_text, encoding="utf-8")

pdf_test = ROOT / "test/pdf_report_test.dart"
pdf_test_text = pdf_test.read_text(encoding="utf-8")
pdf_test_text = pdf_test_text.replace(
    "testWidgets('PDF raporu geçerli PDF üretir ve ayrıntılarda taşmaz', (tester) async {",
    "test('PDF raporu geçerli PDF üretir ve ayrıntılarda taşmaz', () async {",
)
if "testWidgets('PDF raporu" in pdf_test_text:
    raise SystemExit("PDF test still runs in fake widget time.")
pdf_test.write_text(pdf_test_text, encoding="utf-8")

model_path = ROOT / "lib/models/mizan_models.dart"
replace_once(
    model_path,
    """            amount: rent.remainingAmount,
            dueDate: rent.dueDate,""",
    """            amount: rent.scheduledPaymentAmount,
            dueDate: rent.dueDate,""",
    "upcoming rent and installment period amount",
)
replace_once(
    model_path,
    """              rent.isDueInMonth(month),
        )
        .fold<double>(0.0, (sum, rent) => sum + rent.remainingAmount);""",
    """              rent.isDueInMonth(month),
        )
        .fold<double>(
          0.0,
          (sum, rent) => sum + rent.scheduledPaymentAmount,
        );""",
    "monthly rent and installment period amount",
)

final_installment_test = ROOT / "test/final_installment_period_test.dart"
final_installment_test.write_text(
    """import 'package:flutter_test/flutter_test.dart';
import 'package:lefferion_prime_mizan/models/mizan_models.dart';

void main() {
  test('kira ve taksit aylık yükü kalan bakiye yerine dönem tutarıdır', () {
    final rent = RentEntry(
      id: 'rent-final',
      title: 'Ürün taksiti',
      amount: 24000,
      paymentDay: 5,
      receiverName: 'İşletme',
      dueDate: DateTime(2026, 7, 26),
      installmentCount: 12,
      currentInstallment: 1,
      payments: [
        PaymentRecord(
          id: 'rent-payment',
          amount: 2000,
          paidAt: DateTime(2026, 7, 5),
          entryType: PaymentEntryType.installment,
        ),
      ],
    );
    final person = PersonAccount(
      id: 'person-final',
      name: 'Test',
      rents: [rent],
    );
    final state = MizanState(
      people: [person],
      expenseCategories: const [],
      expenses: const [],
      notificationSlots: defaultNotificationSlots,
    );

    expect(rent.remainingAmount, 22000);
    expect(rent.scheduledPaymentAmount, closeTo(2200, 0.001));
    expect(person.monthlyLoadFor(DateTime(2026, 7)), closeTo(2200, 0.001));
    final reference = state
        .recordReferencesAt(DateTime(2026, 7, 21))
        .singleWhere((item) => item.type == RecordType.rent);
    expect(reference.amount, closeTo(2200, 0.001));
    expect(reference.amount, isNot(22000));
  });
}
""",
    encoding="utf-8",
)

required = [
    ROOT / "lib/services/report_service.dart",
    ROOT / "lib/services/pdf_report_service.dart",
    ROOT / "test/report_service_test.dart",
    ROOT / "test/pdf_report_test.dart",
    ROOT / "test/final_installment_period_test.dart",
]
missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
if missing:
    raise SystemExit(f"Round 3 new files are missing after patch application: {missing}")

print("MIZAN round 3 complete revision and final compatibility fixes applied.")
