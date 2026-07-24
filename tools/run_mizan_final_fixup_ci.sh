#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="${SOURCE_ROOT:-workspace/LEFFERION-PRIME-MIZAN-MANUAL-OVERDUE-SYNC-FINAL}"

python3 - <<'PY'
from pathlib import Path
import hashlib, shutil, zipfile
archives = sorted(Path('.baseline-artifact').rglob('*.zip'))
if len(archives) != 1:
    raise SystemExit(f'Beklenen tek kaynak ZIP bulunamadı: {archives}')
archive = archives[0]
expected = 'c87d38b1a6d03ebef79d89df575bf7e4b0f4b8050256aac4532dd8646b8abe48'
actual = hashlib.sha256(archive.read_bytes()).hexdigest()
if actual != expected:
    raise SystemExit(f'Kaynak SHA uyuşmuyor: {actual}')
shutil.rmtree('workspace', ignore_errors=True)
Path('workspace').mkdir()
with zipfile.ZipFile(archive) as source_zip:
    source_zip.extractall('workspace')
PY

python3 tools/apply_mizan_final_complete.py "$SOURCE_ROOT"
python3 tools/apply_mizan_final_fixup.py "$SOURCE_ROOT"
test -f "$SOURCE_ROOT/pubspec.yaml"

mkdir -p "$SOURCE_ROOT/ci-logs"
exec > >(tee "$SOURCE_ROOT/ci-logs/final-verification.log") 2>&1

cd "$SOURCE_ROOT"
flutter create . --platforms=android --org com.lefferionprime --project-name lefferion_prime_mizan
python3 tools/configure_android.py
flutter pub get
dart format lib test
dart run flutter_launcher_icons
flutter analyze --fatal-warnings
python3 tools/validate_project.py
flutter test test/expense_browser_service_test.dart --reporter expanded
flutter test test/bill_rent_schedule_test.dart --reporter expanded
flutter test test/performance_scaling_test.dart --reporter expanded
flutter test test/overdue_calendar_tracking_test.dart test/manual_overdue_edit_confirmation_test.dart --reporter expanded
flutter test test/model_test.dart test/final_installment_period_test.dart --reporter expanded
flutter test test/local_store_test.dart test/controller_test.dart --reporter expanded
flutter test test/reminder_engine_test.dart test/alarm_regression_test.dart test/automatic_notification_sync_test.dart --reporter expanded
flutter test test/report_service_test.dart test/pdf_report_test.dart --reporter expanded
flutter test test/responsive_test.dart test/ui_interaction_test.dart --reporter expanded
flutter test test/visual_capture_test.dart --update-goldens
flutter test --reporter expanded
flutter build apk --release
unzip -t build/app/outputs/flutter-apk/app-release.apk
grep -q "safeMaximumPaymentReminders" lib/services/reminder_engine.dart
grep -q "_atomicWrite" lib/services/local_store.dart
grep -q "Tarih aralığı" lib/screens/expenses_screen.dart
cd ../..

python3 - <<'PY'
from pathlib import Path
import shutil, zipfile
root=Path('workspace/LEFFERION-PRIME-MIZAN-MANUAL-OVERDUE-SYNC-FINAL')
dist=Path('dist-final-fixup-pr')
stage=dist/'LEFFERION-PRIME-MIZAN-FINAL-FIXUP'
archive=dist/'LEFFERION-PRIME-MIZAN-FINAL-FIXUP-SOURCE.zip'
shutil.rmtree(dist,ignore_errors=True)
stage.mkdir(parents=True)
excluded_roots={'.git','.dart_tool','build','ci-logs','dist','.gradle'}
excluded_files={'.flutter-plugins','.flutter-plugins-dependencies','.packages','local.properties'}
for source in root.rglob('*'):
    relative=source.relative_to(root)
    if not relative.parts or any(part in excluded_roots for part in relative.parts) or source.name in excluded_files:
        continue
    target=stage/relative
    if source.is_dir(): target.mkdir(parents=True,exist_ok=True)
    elif source.is_file():
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as output:
    for source in stage.rglob('*'):
        if source.is_file(): output.write(source,source.relative_to(stage.parent))
with zipfile.ZipFile(archive) as check:
    bad=check.testzip()
    if bad: raise SystemExit(f'Kaynak ZIP bozuk: {bad}')
PY
