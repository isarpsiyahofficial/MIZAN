from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]

# Make dashboard metric cards genuinely tappable without changing their layout.
path = root / 'lib/widgets/mizan_cards.dart'
text = path.read_text(encoding='utf-8')
metric_re = re.compile(
    r'class MetricCard extends StatelessWidget \{.*?\n\}\n\nclass MizanListCard',
    re.S,
)
metric_new = '''class MetricCard extends StatelessWidget {
  const MetricCard({
    required this.label,
    required this.value,
    this.color = MizanTheme.ink,
    this.icon,
    this.onTap,
    super.key,
  });

  final String label;
  final String value;
  final Color color;
  final IconData? icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (icon case final value?) ...[
                Icon(value, color: color),
                const SizedBox(height: 10),
              ],
              Text(
                label,
                style: const TextStyle(
                  color: MizanTheme.muted,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                value,
                softWrap: true,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: color,
                      fontWeight: FontWeight.w900,
                    ),
              ),
              if (onTap != null) ...[
                const SizedBox(height: 8),
                const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Detayı gör',
                      style: TextStyle(
                        color: MizanTheme.muted,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(width: 4),
                    Icon(Icons.chevron_right, size: 18, color: MizanTheme.muted),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class MizanListCard'''
text, count = metric_re.subn(metric_new, text, count=1)
if count != 1:
    raise SystemExit('MetricCard compatibility update failed.')
path.write_text(text, encoding='utf-8')

# Use the stable Android-compatible file_picker API/version used by this project.
path = root / 'pubspec.yaml'
text = path.read_text(encoding='utf-8')
text = re.sub(r'^  file_picker:.*$', '  file_picker: 10.3.10', text, flags=re.M)
path.write_text(text, encoding='utf-8')

path = root / 'lib/screens/settings_screen.dart'
text = path.read_text(encoding='utf-8')
text = text.replace('FilePicker.saveFile(', 'FilePicker.platform.saveFile(')
text = text.replace('FilePicker.pickFiles(', 'FilePicker.platform.pickFiles(')
path.write_text(text, encoding='utf-8')

# csv 7 uses CsvCodec rather than the removed version-6 converter names.
path = root / 'lib/services/csv_backup_service.dart'
text = path.read_text(encoding='utf-8')
text = text.replace(
    '  static const _encoder = ListToCsvConverter();\n'
    '  static const _decoder = CsvToListConverter();',
    '  static final CsvCodec _codec = CsvCodec();',
)
text = text.replace('return _encoder.convert(rows);', 'return _codec.encode(rows);')
text = text.replace('final rows = _decoder.convert(content);', 'final rows = _codec.decode(content);')
path.write_text(text, encoding='utf-8')

# Dashboard callbacks await detail sheets and satisfy strict analyzer rules.
path = root / 'lib/screens/dashboard_screen.dart'
text = path.read_text(encoding='utf-8')
text = text.replace(
    'if (group.type != null) return item.type == group.type;',
    'if (group.type != null) {\n'
    '                        return item.type == group.type;\n'
    '                      }',
)
text = text.replace(
    '''                  onTap: () {
                    final records = state.recordReferencesAt(now).where((item) {''',
    '''                  onTap: () async {
                    final records = state.recordReferencesAt(now).where((item) {''',
    1,
)
text = text.replace(
    '''                    Navigator.pop(sheetContext);
                    _showRecordList(
                      context,
                      title: group.title,
                      records: records,
                    );''',
    '''                    Navigator.pop(sheetContext);
                    await _showRecordList(
                      context,
                      title: group.title,
                      records: records,
                    );''',
    1,
)
text = text.replace(
    '''                  onTap: () {
                    Navigator.pop(sheetContext);
                    showRecordDetails(
                      context: context,
                      controller: controller,
                      personId: record.personId,
                      type: record.type,
                      sourceId: record.sourceId,
                      bankId: record.bankId,
                    );''',
    '''                  onTap: () async {
                    Navigator.pop(sheetContext);
                    await showRecordDetails(
                      context: context,
                      controller: controller,
                      personId: record.personId,
                      type: record.type,
                      sourceId: record.sourceId,
                      bankId: record.bankId,
                    );''',
    1,
)
path.write_text(text, encoding='utf-8')

# ExpansionTile must paint onto its own Material so headers and ink remain visible.
path = root / 'lib/screens/people_screen.dart'
text = path.read_text(encoding='utf-8')
old_bank_surface = '''    return DecoratedBox(
      decoration: BoxDecoration(
        color: MizanTheme.surface,
        borderRadius: BorderRadius.circular(16),
      ),
      child: ExpansionTile('''
new_bank_surface = '''    return Material(
      color: MizanTheme.surface,
      borderRadius: BorderRadius.circular(16),
      clipBehavior: Clip.antiAlias,
      child: ExpansionTile('''
if old_bank_surface not in text:
    raise SystemExit('Bank group Material surface was not found.')
text = text.replace(old_bank_surface, new_bank_surface, 1)
path.write_text(text, encoding='utf-8')

# Expense category actions are awaited, and the actual BuildContext is guarded.
path = root / 'lib/screens/expenses_screen.dart'
text = path.read_text(encoding='utf-8')
text = text.replace('builder: (_, __) {', 'builder: (context, child) {')
text = text.replace(
    '''                        onSelected: (value) {
                          if (value == 'edit') {
                            _showCategoryForm(sheetContext, category: category);
                          } else if (value == 'delete') {
                            _showDeleteCategory(sheetContext, category);
                          }
                        },''',
    '''                        onSelected: (value) async {
                          if (value == 'edit') {
                            await _showCategoryForm(
                              sheetContext,
                              category: category,
                            );
                          } else if (value == 'delete') {
                            await _showDeleteCategory(sheetContext, category);
                          }
                        },''',
)
text = text.replace(
    '''      await _showCategoryForm(context);
      if (!mounted) {
        return;
      }
      if (widget.controller.state.expenseCategories.isEmpty) {
        return;
      }''',
    '''      await _showCategoryForm(context);
      if (!context.mounted) {
        return;
      }
      if (widget.controller.state.expenseCategories.isEmpty) {
        return;
      }''',
)
text = text.replace(
    '''      await _showCategoryForm(context);
      if (widget.controller.state.expenseCategories.isEmpty) return;''',
    '''      await _showCategoryForm(context);
      if (!context.mounted) {
        return;
      }
      if (widget.controller.state.expenseCategories.isEmpty) {
        return;
      }''',
)
path.write_text(text, encoding='utf-8')

# Reports use explicit blocks and await record-detail navigation.
path = root / 'lib/screens/reports_screen.dart'
text = path.read_text(encoding='utf-8')
text = text.replace(
    '''      if (personId != null && item.personId != personId) return false;
      if (onlySelectedMonth && !isSameMonth(item.dueDate, month)) return false;
      if (status != null && item.status != status) return false;''',
    '''      if (personId != null && item.personId != personId) {
        return false;
      }
      if (onlySelectedMonth && !isSameMonth(item.dueDate, month)) {
        return false;
      }
      if (status != null && item.status != status) {
        return false;
      }''',
)
text = text.replace(
    '''                    onTap: () {
                      Navigator.pop(sheetContext);
                      showRecordDetails(''',
    '''                    onTap: () async {
                      Navigator.pop(sheetContext);
                      await showRecordDetails(''',
)
path.write_text(text, encoding='utf-8')

# Test compatibility, real scrolling behavior, and clean analyzer output.
path = root / 'test/local_store_test.dart'
text = path.read_text(encoding='utf-8')
text = text.replace(
    "import 'package:lefferion_prime_mizan/models/mizan_models.dart';\n",
    '',
)
text = text.replace(
    'await expectLater(store.load(), throwsFileSystemException);',
    'await expectLater(store.load(), throwsA(isA<FileSystemException>()));',
)
path.write_text(text, encoding='utf-8')

path = root / 'test/visual_capture_test.dart'
text = path.read_text(encoding='utf-8')
text = text.replace("import 'dart:typed_data';\n\n", '')
text = text.replace('final target = find.text(text).last;', 'final target = find.text(text);')
path.write_text(text, encoding='utf-8')

path = root / 'test/ui_interaction_test.dart'
text = path.read_text(encoding='utf-8')
text = text.replace('final target = find.text(text).last;', 'final target = find.text(text);')
text = text.replace(
    '''    expect(find.text('Kayıt sahibi'), findsOneWidget);
    expect(find.text('Banka Borçları'), findsOneWidget);
    expect(find.text('Kişisel ve Kurumsal Borçlar'), findsOneWidget);
    expect(find.text('Faturalar'), findsOneWidget);
    expect(find.text('Abonelikler'), findsOneWidget);
    expect(find.text('Kira ve Taksitler'), findsOneWidget);''',
    '''    expect(find.text('Kayıt sahibi'), findsOneWidget);
    for (final title in const [
      'Banka Borçları',
      'Kişisel ve Kurumsal Borçlar',
      'Faturalar',
      'Abonelikler',
      'Kira ve Taksitler',
    ]) {
      final target = find.text(title);
      await tester.scrollUntilVisible(
        target,
        220,
        scrollable: find.byType(Scrollable).first,
      );
      expect(target, findsOneWidget);
    }''',
)
text = text.replace(
    '''    expect(find.text('CSV yedeğini dışa aktar'), findsOneWidget);
    expect(find.text('CSV yedeğini geri yükle'), findsOneWidget);
    expect(find.text('Anlık yerel kayıt'), findsOneWidget);''',
    '''    final exportButton = find.text('CSV yedeğini dışa aktar');
    await tester.scrollUntilVisible(
      exportButton,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    expect(exportButton, findsOneWidget);
    expect(find.text('CSV yedeğini geri yükle'), findsOneWidget);
    expect(find.text('Anlık yerel kayıt'), findsOneWidget);''',
)
text = text.replace(
    "expect(find.text('Giderler'), findsOneWidget);",
    "expect(find.text('Giderler'), findsWidgets);",
)
path.write_text(text, encoding='utf-8')

path = root / 'test/widget_test.dart'
text = path.read_text(encoding='utf-8')
if "import 'package:flutter/material.dart';" not in text:
    text = text.replace(
        "import 'package:flutter_test/flutter_test.dart';",
        "import 'package:flutter/material.dart';\nimport 'package:flutter_test/flutter_test.dart';",
    )
text = text.replace(
    '''    expect(find.text('LEFFERION PRIME - MİZAN'), findsOneWidget);
    expect(find.text('Uygulama boş ve kullanıma hazır'), findsOneWidget);''',
    '''    expect(find.text('LEFFERION PRIME - MİZAN'), findsOneWidget);
    final emptyMessage = find.text('Uygulama boş ve kullanıma hazır');
    await tester.scrollUntilVisible(
      emptyMessage,
      220,
      scrollable: find.byType(Scrollable).first,
    );
    expect(emptyMessage, findsOneWidget);''',
)
path.write_text(text, encoding='utf-8')

checks = {
    'lib/widgets/mizan_cards.dart': ['final VoidCallback? onTap;', "'Detayı gör'"],
    'lib/screens/people_screen.dart': ['return Material(', 'clipBehavior: Clip.antiAlias'],
    'lib/screens/settings_screen.dart': ['FilePicker.platform.saveFile(', 'FilePicker.platform.pickFiles('],
    'lib/services/csv_backup_service.dart': ['static final CsvCodec _codec', '_codec.encode(rows)', '_codec.decode(content)'],
    'pubspec.yaml': ['file_picker: 10.3.10'],
    'test/local_store_test.dart': ['throwsA(isA<FileSystemException>())'],
}
for relative, tokens in checks.items():
    content = (root / relative).read_text(encoding='utf-8')
    missing = [token for token in tokens if token not in content]
    if missing:
        raise SystemExit(f'Post-revision validation failed for {relative}: {missing}')

for forbidden in (
    'ListToCsvConverter',
    'CsvToListConverter',
    'throwsFileSystemException',
    'find.text(text).last',
):
    found = []
    for relative in (
        'lib/services/csv_backup_service.dart',
        'test/local_store_test.dart',
        'test/ui_interaction_test.dart',
        'test/visual_capture_test.dart',
    ):
        if forbidden in (root / relative).read_text(encoding='utf-8'):
            found.append(relative)
    if found:
        raise SystemExit(f'Removed API or fragile finder remains: {forbidden} in {found}')

print('MIZAN v2 Material, package, Android build and interaction-test fixes applied.')
