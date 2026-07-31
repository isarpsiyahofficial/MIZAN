from __future__ import annotations

import base64
import hashlib
import lzma
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / 'round4_patch_chunks'
EXPECTED_CHUNK_COUNT = 5
EXPECTED_COMPRESSED_SHA = '9b05c7d856651d82f72a2c9c2d59e60514229a784bdfef6ec6148d2c57c39f9e'
EXPECTED_PATCH_SHA = 'b6c3b65cd7ed5cb3b3380ddc4ac910216edc4765d2cb6ed7190eeaaab3f5a3af'

pieces = [CHUNKS / f'chunk{index:02d}.txt' for index in range(EXPECTED_CHUNK_COUNT)]
missing = [str(path) for path in pieces if not path.is_file()]
if missing:
    raise SystemExit(f'Round 4 patch parçaları eksik: {missing}')
encoded = ''.join(path.read_text(encoding='utf-8').strip() for path in pieces)
compressed = base64.b64decode(encoded, validate=True)
compressed_sha = hashlib.sha256(compressed).hexdigest()
if compressed_sha != EXPECTED_COMPRESSED_SHA:
    raise SystemExit(
        f'Round 4 sıkıştırılmış SHA uyuşmuyor: {compressed_sha} != {EXPECTED_COMPRESSED_SHA}'
    )
patch = lzma.decompress(compressed)
patch_sha = hashlib.sha256(patch).hexdigest()
if patch_sha != EXPECTED_PATCH_SHA:
    raise SystemExit(f'Round 4 yama SHA uyuşmuyor: {patch_sha} != {EXPECTED_PATCH_SHA}')
patch_path = ROOT / '.mizan_round4.patch'
patch_path.write_bytes(patch)
try:
    subprocess.run(
        ['git', 'apply', '--binary', '--whitespace=nowarn', str(patch_path)],
        cwd=ROOT,
        check=True,
    )
finally:
    patch_path.unlink(missing_ok=True)

validator_path = ROOT / 'tools/validate_project.py'
validator_text = validator_path.read_text(encoding='utf-8')
old_validator_token = '"AlarmRepeatMode", "Tekrarlı alarm"'
new_validator_token = '"alarmRepeatMode.minutes", "Tekrarlı alarm"'
if old_validator_token in validator_text:
    validator_text = validator_text.replace(
        old_validator_token,
        new_validator_token,
        1,
    )
elif new_validator_token not in validator_text:
    raise SystemExit('Round 4 bildirim planı doğrulama hedefi bulunamadı.')
validator_path.write_text(validator_text, encoding='utf-8')

configure_path = ROOT / 'tools/configure_android.py'
configure_text = configure_path.read_text(encoding='utf-8')
old_permission_block = '''if "android.permission.POST_NOTIFICATIONS" not in text:
    text = text.replace("<manifest xmlns:android=\\"http://schemas.android.com/apk/res/android\\">", "<manifest xmlns:android=\\"http://schemas.android.com/apk/res/android\\">\\n" + permissions)'''
new_permission_block = '''manifest_tag = "<manifest xmlns:android=\\"http://schemas.android.com/apk/res/android\\">"
for permission_name in (
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.SCHEDULE_EXACT_ALARM",
    "android.permission.USE_FULL_SCREEN_INTENT",
    "android.permission.VIBRATE",
):
    if permission_name not in text:
        permission_line = (
            f'    <uses-permission android:name="{permission_name}" />\\n'
        )
        text = text.replace(manifest_tag, manifest_tag + "\\n" + permission_line, 1)'''
if old_permission_block in configure_text:
    configure_text = configure_text.replace(
        old_permission_block,
        new_permission_block,
        1,
    )
elif 'for permission_name in (' not in configure_text:
    raise SystemExit('Android izin ekleme bloğu bulunamadı.')
configure_path.write_text(configure_text, encoding='utf-8')

required = {
    'lib/models/mizan_models.dart': [
        'const int currentSchemaVersion = 7;',
        'manualOverdueDays',
        'missedDuePeriodsAt',
        'enum NotificationPresentationMode',
        'enum AlarmRepeatMode',
    ],
    'lib/services/notification_service.dart': [
        'requestFullScreenIntentPermission',
        'fullScreenIntent: alarmStyle',
        'AudioAttributesUsage.alarm',
    ],
    'lib/services/pdf_report_service.dart': [
        "await _newPage();",
        'Future<void> _notice',
    ],
    'lib/screens/record_form_dialogs.dart': ['Manuel gecikme günü (opsiyonel)'],
    'tools/validate_project.py': ['alarmRepeatMode.minutes'],
    'tools/configure_android.py': [
        'for permission_name in (',
        'android.permission.USE_FULL_SCREEN_INTENT',
        'android.permission.VIBRATE',
    ],
}
for relative, tokens in required.items():
    text = (ROOT / relative).read_text(encoding='utf-8')
    absent = [token for token in tokens if token not in text]
    if absent:
        raise SystemExit(f'Round 4 doğrulaması başarısız: {relative}: {absent}')
print(f'Round 4 yaması uygulandı: {len(patch)} bayt, SHA-256 {patch_sha}.')
