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

# file_picker 11 uses static methods directly on FilePicker.
path = root / 'lib/screens/settings_screen.dart'
text = path.read_text(encoding='utf-8').replace('FilePicker.platform.', 'FilePicker.')
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

# Expense category actions are awaited, and context is guarded after async work.
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
      if (widget.controller.state.expenseCategories.isEmpty) return;''',
    '''      await _showCategoryForm(context);
      if (!mounted) {
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

# Test compatibility and clean analyzer output.
path = root / 'test/local_store_test.dart'
text = path.read_text(encoding='utf-8').replace(
    'await expectLater(store.load(), throwsFileSystemException);',
    'await expectLater(store.load(), throwsA(isA<FileSystemException>()));',
)
path.write_text(text, encoding='utf-8')

path = root / 'test/visual_capture_test.dart'
text = path.read_text(encoding='utf-8').replace("import 'dart:typed_data';\n\n", '')
path.write_text(text, encoding='utf-8')

checks = {
    'lib/widgets/mizan_cards.dart': ['final VoidCallback? onTap;', "'Detayı gör'"],
    'lib/screens/settings_screen.dart': ['FilePicker.saveFile(', 'FilePicker.pickFiles('],
    'lib/services/csv_backup_service.dart': ['static final CsvCodec _codec', '_codec.encode(rows)', '_codec.decode(content)'],
    'test/local_store_test.dart': ['throwsA(isA<FileSystemException>())'],
}
for relative, tokens in checks.items():
    content = (root / relative).read_text(encoding='utf-8')
    missing = [token for token in tokens if token not in content]
    if missing:
        raise SystemExit(f'Post-revision validation failed for {relative}: {missing}')

for forbidden in (
    'FilePicker.platform.',
    'ListToCsvConverter',
    'CsvToListConverter',
    'throwsFileSystemException',
):
    found = []
    for relative in checks:
        if forbidden in (root / relative).read_text(encoding='utf-8'):
            found.append(relative)
    if found:
        raise SystemExit(f'Removed API remains: {forbidden} in {found}')

print('MIZAN v2 package API, tappable cards and strict analyzer fixes applied.')
