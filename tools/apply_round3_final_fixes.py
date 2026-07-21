from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

settings = ROOT / 'lib/screens/settings_screen.dart'
text = settings.read_text(encoding='utf-8')
old = '''        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 18, color: color),
            const SizedBox(width: 7),
            Text(
              label,
              style: TextStyle(color: color, fontWeight: FontWeight.w800),
            ),
          ],
        ),'''
new = '''        child: Wrap(
          spacing: 7,
          runSpacing: 4,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Icon(icon, size: 18, color: color),
            Text(
              label,
              softWrap: true,
              style: TextStyle(color: color, fontWeight: FontWeight.w800),
            ),
          ],
        ),'''
if old not in text and new not in text:
    raise SystemExit('Settings status badge layout target was not found.')
text = text.replace(old, new, 1)
settings.write_text(text, encoding='utf-8')

reports = ROOT / 'lib/screens/reports_screen.dart'
text = reports.read_text(encoding='utf-8')
old = '''          return AlertDialog(
            title: const Text('Kişi kapsamı'),
            content: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520, maxHeight: 520),
              child: ListView(
                shrinkWrap: true,
                children: [
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: allSelected,
                    title: const Text('Tüm kişileri kapsa'),
                    subtitle: const Text(
                      'Bütün kişilerin ödeme ve borç kayıtları rapora alınır.',
                    ),
                    onChanged: (_) => setDialogState(working.clear),
                  ),
                  const Divider(),
                  for (final person in state.people)
                    CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      value: working.contains(person.id),
                      title: Text(person.name),
                      onChanged: (value) => setDialogState(() {
                        if (value == true) {
                          working.add(person.id);
                        } else {
                          working.remove(person.id);
                        }
                      }),
                    ),
                ],
              ),
            ),'''
new = '''          return AlertDialog(
            scrollable: true,
            title: const Text('Kişi kapsamı'),
            content: SizedBox(
              width: 520,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: allSelected,
                    title: const Text('Tüm kişileri kapsa'),
                    subtitle: const Text(
                      'Bütün kişilerin ödeme ve borç kayıtları rapora alınır.',
                    ),
                    onChanged: (_) => setDialogState(working.clear),
                  ),
                  const Divider(),
                  for (final person in state.people)
                    CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      value: working.contains(person.id),
                      title: Text(person.name),
                      onChanged: (value) => setDialogState(() {
                        if (value == true) {
                          working.add(person.id);
                        } else {
                          working.remove(person.id);
                        }
                      }),
                    ),
                ],
              ),
            ),'''
if old not in text and new not in text:
    raise SystemExit('Report person dialog layout target was not found.')
text = text.replace(old, new, 1)
reports.write_text(text, encoding='utf-8')

pdf_test = ROOT / 'test/pdf_report_test.dart'
text = pdf_test.read_text(encoding='utf-8')
if "import 'dart:io';" not in text:
    text = "import 'dart:io';\n\n" + text
old = """    expect(bytes.length, greaterThan(1000));
    expect(String.fromCharCodes(bytes.take(4)), '%PDF');"""
new = """    expect(bytes.length, greaterThan(1000));
    expect(String.fromCharCodes(bytes.take(4)), '%PDF');

    final outputDirectory = Directory('test/output');
    await outputDirectory.create(recursive: true);
    await File('${outputDirectory.path}/MIZAN-TUM-ZAMANLAR-RAPOR-ORNEGI.pdf')
        .writeAsBytes(bytes, flush: true);"""
if old not in text and new not in text:
    raise SystemExit('PDF sample output target was not found.')
text = text.replace(old, new, 1)
pdf_test.write_text(text, encoding='utf-8')

checks = {
    settings: ['Wrap(', 'WrapCrossAlignment.center', 'softWrap: true'],
    reports: ['scrollable: true', "title: const Text('Tüm kişileri kapsa')"],
    pdf_test: ["import 'dart:io';", 'MIZAN-TUM-ZAMANLAR-RAPOR-ORNEGI.pdf'],
}
for path, tokens in checks.items():
    content = path.read_text(encoding='utf-8')
    missing = [token for token in tokens if token not in content]
    if missing:
        raise SystemExit(f'Final responsive/PDF fix validation failed for {path}: {missing}')

print('Round 3 final responsive dialog and PDF sample fixes applied.')
