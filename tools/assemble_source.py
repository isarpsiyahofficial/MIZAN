from pathlib import Path
import re
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


def wrap_single_line_ifs(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if not stripped.startswith("if ("):
            output.append(line)
            continue
        depth = 0
        closing = -1
        for index, char in enumerate(stripped[3:], start=3):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    closing = index
                    break
        if closing < 0:
            output.append(line)
            continue
        condition = stripped[: closing + 1]
        body = stripped[closing + 1 :].strip()
        if (
            not body
            or body.startswith("{")
            or not body.endswith(";")
            or body.count(";") != 1
        ):
            output.append(line)
            continue
        output.extend(
            [
                f"{indent}{condition} {{",
                f"{indent}  {body}",
                f"{indent}}}",
            ]
        )
    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def delay_local_controller_disposal(text: str) -> str:
    patterns = [
        (
            r"finally\s*\{\s*name\.dispose\(\);\s*\}",
            "finally {\n      await Future<void>.delayed(kThemeAnimationDuration);\n      name.dispose();\n    }",
        ),
        (
            r"finally\s*\{\s*confirmation\.dispose\(\);\s*\}",
            "finally {\n      await Future<void>.delayed(kThemeAnimationDuration);\n      confirmation.dispose();\n    }",
        ),
        (
            r"finally\s*\{\s*name\.dispose\(\);\s*quantity\.dispose\(\);\s*unitPrice\.dispose\(\);\s*note\.dispose\(\);\s*\}",
            "finally {\n      await Future<void>.delayed(kThemeAnimationDuration);\n      name.dispose();\n      quantity.dispose();\n      unitPrice.dispose();\n      note.dispose();\n    }",
        ),
        (
            r"finally\s*\{\s*text\.dispose\(\);\s*\}",
            "finally {\n      await Future<void>.delayed(kThemeAnimationDuration);\n      text.dispose();\n    }",
        ),
        (
            r"finally\s*\{\s*message\.dispose\(\);\s*\}",
            "finally {\n      await Future<void>.delayed(kThemeAnimationDuration);\n      message.dispose();\n    }",
        ),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return text


for target, prefix in FILES.items():
    pieces = sorted(PARTS.glob(f"{prefix}.part*"))
    if not pieces:
        raise RuntimeError(f"Eksik kaynak parçaları: {target}")
    destination = ROOT / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "".join(piece.read_text(encoding="utf-8") for piece in pieces),
        encoding="utf-8",
    )

people_path = ROOT / "lib/screens/people_screen.dart"
people = people_path.read_text(encoding="utf-8")
if not people.startswith("import 'dart:async';"):
    people = "import 'dart:async';\n\n" + people
people = people.replace("builder: (sheetContext, __)", "builder: (sheetContext, _)")
people = people.replace("void _showDebtDetail(", "Future<void> _showDebtDetail(")
people = people.replace("void _showBillDetail(", "Future<void> _showBillDetail(")
people = people.replace("void _showRentDetail(", "Future<void> _showRentDetail(")
people = people.replace(
    "Future<void> _showDebtDetail(BuildContext context, MizanController controller, String personId, String bankId, String debtId) {\n  showModalBottomSheet<void>(",
    "Future<void> _showDebtDetail(BuildContext context, MizanController controller, String personId, String bankId, String debtId) {\n  return showModalBottomSheet<void>(",
)
people = people.replace(
    "Future<void> _showBillDetail(BuildContext context, MizanController controller, String personId, String billId) {\n  showModalBottomSheet<void>(",
    "Future<void> _showBillDetail(BuildContext context, MizanController controller, String personId, String billId) {\n  return showModalBottomSheet<void>(",
)
people = people.replace(
    "Future<void> _showRentDetail(BuildContext context, MizanController controller, String personId, String rentId) {\n  showModalBottomSheet<void>(",
    "Future<void> _showRentDetail(BuildContext context, MizanController controller, String personId, String rentId) {\n  return showModalBottomSheet<void>(",
)
people = re.sub(
    r"onTap: \(\) => (_show(?:Debt|Bill|Rent)Detail\([^\n]+\)),",
    r"onTap: () { unawaited(\1); },",
    people,
)
people = people.replace(
    "if (value == 'edit') await onEditPayment(payment);\n                      if (value == 'delete') await _confirmAction(context, title: 'Ödemeyi sil', message: '${money(payment.amount)} tutarındaki ödeme kaydı silinsin mi?', confirmLabel: 'Ödemeyi sil', action: () => onDeletePayment(payment));",
    "if (value == 'edit') {\n                        await onEditPayment(payment);\n                      } else if (value == 'delete') {\n                        await _confirmAction(context, title: 'Ödemeyi sil', message: '${money(payment.amount)} tutarındaki ödeme kaydı silinsin mi?', confirmLabel: 'Ödemeyi sil', action: () => onDeletePayment(payment));\n                      }",
)
people_path.write_text(people, encoding="utf-8")

expenses_path = ROOT / "lib/screens/expenses_screen.dart"
expenses = expenses_path.read_text(encoding="utf-8")
expenses = expenses.replace(
    "if (parseMoney(value ?? '') < 0) return 'Birim fiyat negatif olamaz.';",
    "if (parseMoney(value ?? '') < 0) { return 'Birim fiyat negatif olamaz.'; }",
)
expenses_path.write_text(delay_local_controller_disposal(expenses), encoding="utf-8")

settings_path = ROOT / "lib/screens/settings_screen.dart"
settings_path.write_text(
    delay_local_controller_disposal(settings_path.read_text(encoding="utf-8")),
    encoding="utf-8",
)

notes_path = ROOT / "lib/widgets/record_notes_panel.dart"
notes_path.write_text(
    delay_local_controller_disposal(notes_path.read_text(encoding="utf-8")),
    encoding="utf-8",
)

cards_path = ROOT / "lib/widgets/mizan_cards.dart"
cards = cards_path.read_text(encoding="utf-8")
cards = re.sub(
    r"if \(subtitle != null\)\s+Text\(subtitle!,",
    "if (subtitle case final value?) Text(value,",
    cards,
)
cards = re.sub(
    r"if \(action != null\)\s+action!,",
    "if (action case final value?) value,",
    cards,
)
cards = re.sub(
    r"if \(action != null\)\s+\.\.\.\[const SizedBox\(height: 14\), action!\],",
    "if (action case final value?) ...[const SizedBox(height: 14), value],",
    cards,
)
cards = re.sub(
    r"if \(trailing != null\)\s+\.\.\.\[const SizedBox\(width: 10\), Flexible\(child: trailing!\)\],",
    "if (trailing case final value?) ...[const SizedBox(width: 10), Flexible(child: value)],",
    cards,
)
cards_path.write_text(cards, encoding="utf-8")

for dart_file in (ROOT / "lib").rglob("*.dart"):
    dart_file.write_text(
        wrap_single_line_ifs(dart_file.read_text(encoding="utf-8")),
        encoding="utf-8",
    )

shutil.rmtree(PARTS)
(ROOT / ".github/workflows/assemble-source.yml").unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
print(f"{len(FILES)} kaynak dosyası birleştirildi; dialog ve analyzer güvenlik düzeltmeleri uygulandı.")
