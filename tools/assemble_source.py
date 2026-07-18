from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / ".source_parts"
FILES = {
    '.github/workflows/android-release.yml': '_github__workflows__android-release_yml',
    'docs/BATCH_PLAN.md': 'docs__BATCH_PLAN_md',
    'docs/QUALITY_CHECKLIST.md': 'docs__QUALITY_CHECKLIST_md',
    'docs/REQUIREMENTS_250_PLUS.md': 'docs__REQUIREMENTS_250_PLUS_md',
    'lib/controllers/mizan_controller.dart': 'lib__controllers__mizan_controller_dart',
    'lib/models/mizan_models.dart': 'lib__models__mizan_models_dart',
    'lib/screens/dashboard_screen.dart': 'lib__screens__dashboard_screen_dart',
    'lib/screens/expenses_screen.dart': 'lib__screens__expenses_screen_dart',
    'lib/screens/people_screen.dart': 'lib__screens__people_screen_dart',
    'lib/screens/record_form_dialogs.dart': 'lib__screens__record_form_dialogs_dart',
    'lib/screens/reports_screen.dart': 'lib__screens__reports_screen_dart',
    'lib/screens/settings_screen.dart': 'lib__screens__settings_screen_dart',
    'lib/services/local_store.dart': 'lib__services__local_store_dart',
    'lib/services/notification_service.dart': 'lib__services__notification_service_dart',
    'lib/services/reminder_engine.dart': 'lib__services__reminder_engine_dart',
    'lib/widgets/mizan_cards.dart': 'lib__widgets__mizan_cards_dart',
    'lib/widgets/record_notes_panel.dart': 'lib__widgets__record_notes_panel_dart',
    'test/controller_test.dart': 'test__controller_test_dart',
    'test/formatters_test.dart': 'test__formatters_test_dart',
    'test/local_store_test.dart': 'test__local_store_test_dart',
    'test/model_test.dart': 'test__model_test_dart',
    'test/reminder_engine_test.dart': 'test__reminder_engine_test_dart',
    'test/responsive_test.dart': 'test__responsive_test_dart',
    'tools/validate_project.py': 'tools__validate_project_py',
}

for target, prefix in FILES.items():
    pieces = sorted(PARTS.glob(f"{prefix}.part*"))
    if not pieces:
        raise RuntimeError(f"Eksik kaynak parçaları: {target}")
    destination = ROOT / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(piece.read_text(encoding="utf-8") for piece in pieces), encoding="utf-8")

shutil.rmtree(PARTS)
(ROOT / ".github/workflows/assemble-source.yml").unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
print(f"{len(FILES)} kaynak dosyası birleştirildi.")
