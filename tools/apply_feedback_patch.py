from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "feedback_patch_chunks"
EXPECTED_COMPRESSED_SHA = (
    "1f610ff3090d8ef415d1cdd13751f66029b570239b9b4ff034448a08655eca0b"
)
EXPECTED_PATCH_SHA = (
    "13d6519749bd78b965943ded8ae8c751aed2cdc46e1b8531f58d87b1b78b6db4"
)
EXPECTED_CHUNK_COUNT = 5

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

interaction_test = ROOT / "test/ui_interaction_test.dart"
interaction_text = interaction_test.read_text(encoding="utf-8")

old_delete = "    expect(find.text('Kişiyi sil'), findsOneWidget);"
new_delete = """    final deletePerson = find.text('Kişiyi sil');
    await tester.scrollUntilVisible(
      deletePerson,
      120,
      scrollable: detailScrollable,
    );
    expect(deletePerson, findsOneWidget);"""
if old_delete not in interaction_text:
    raise SystemExit("Person delete visibility expectation was not found.")
interaction_text = interaction_text.replace(old_delete, new_delete, 1)

old_bank_flow = """    await tester.scrollUntilVisible(
      find.text('Kullanıcının bankası'),
      220,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.text('Kullanıcının bankası'));
    await tester.pumpAndSettle();
    final addDebt = find.text('Borç ürünü ekle');
    await tester.scrollUntilVisible(
      addDebt,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(addDebt);
    await tester.pumpAndSettle();"""
new_bank_flow = """    final bankTitle = find.text('Kullanıcının bankası');
    await tester.scrollUntilVisible(
      bankTitle,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    expect(bankTitle, findsOneWidget);
    final bankActions = find.byTooltip('Banka grubu işlemleri');
    await tester.ensureVisible(bankActions);
    await tester.tap(bankActions);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Borç ekle'));
    await tester.pumpAndSettle();
    expect(find.text('Borç ürünü ekle'), findsOneWidget);"""
if old_bank_flow not in interaction_text:
    raise SystemExit("Bank debt creation interaction flow was not found.")
interaction_text = interaction_text.replace(old_bank_flow, new_bank_flow, 1)
interaction_test.write_text(interaction_text, encoding="utf-8")

format_result = subprocess.run(
    ["dart", "format", "lib", "test"],
    cwd=ROOT,
    check=False,
)
if format_result.returncode != 0:
    raise SystemExit(
        f"Phone feedback Dart format failed with code {format_result.returncode}."
    )
