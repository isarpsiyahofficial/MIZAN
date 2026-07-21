from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]

# Controller load separation and storage recovery.
path = root / 'lib/controllers/mizan_controller.dart'
text = path.read_text(encoding='utf-8')
load_re = re.compile(r"  Future<void> load\(\) async \{.*?\n  \}\n\n  Future<void> _commit\(", re.S)
load_new = '''  Future<void> load() async {
    _isBusy = true;
    notifyListeners();

    String? notificationWarning;
    try {
      await _scheduler.initialize();
      _notificationHealth = await _scheduler.requestPermissions();
    } on Object catch (error) {
      notificationWarning =
          'Bildirim izni veya zamanlama servisi açılamadı: ${_friendlyError(error)}';
    }

    try {
      final result = await _store.load();
      _state = result.state;
      _storageReady = true;
      _loadMessage = result.message;
      _lastError = notificationWarning;

      try {
        await _scheduler.reschedule(_state);
        _notificationHealth = await _scheduler.health();
      } on Object catch (error) {
        _lastError =
            'Kayıtlar açıldı ancak bildirimler planlanamadı: ${_friendlyError(error)}';
      }
    } on Object catch (error) {
      _storageReady = false;
      _state = MizanState.empty();
      _lastError =
          '${_friendlyError(error)} Mevcut kayıt dosyaları korunuyor; CSV yedeği geri yüklenmeden yeni kayıt yazılmayacak.';
    } finally {
      _isBusy = false;
      _isReady = true;
      notifyListeners();
    }
  }

  Future<void> _commit('''
text, count = load_re.subn(load_new, text, count=1)
assert count == 1, 'controller load replacement failed'

if 'Future<void> restoreFromBackup(MizanState restored)' not in text:
    anchor = '  Future<void> setNotificationsEnabled(bool enabled) async {'
    method = '''  Future<void> restoreFromBackup(MizanState restored) async {
    await _commit(
      restored.copyWith(schemaVersion: currentSchemaVersion),
      allowStorageRecovery: true,
    );
    _loadMessage = 'CSV yedeği doğrulandı ve geri yüklendi.';
    notifyListeners();
  }

'''
    assert anchor in text
    text = text.replace(anchor, method + anchor, 1)
path.write_text(text, encoding='utf-8')

# Model enums required by separated record groups.
path = root / 'lib/models/mizan_models.dart'
text = path.read_text(encoding='utf-8')
enum_re = re.compile(r"enum BillKind \{.*?\n\}\n\nenum RecordType \{.*?\n\}", re.S)
enum_new = '''enum BillKind {
  electricity('Elektrik'),
  water('Su'),
  phone('Telefon'),
  internet('İnternet'),
  naturalGas('Doğalgaz'),
  custom('Özel fatura');

  const BillKind(this.label);
  final String label;
}

enum CreditorType {
  person('Kişi'),
  companyInstitution('Şirket / Kurum'),
  cheque('Çek'),
  promissoryNote('Senet'),
  merchantBusiness('Esnaf / İşletme'),
  familyRelative('Aile / Yakın'),
  other('Diğer');

  const CreditorType(this.label);
  final String label;
}

enum PaymentFrequency {
  oneTime('Tek ödeme'),
  weekly('Haftalık'),
  biweekly('İki haftada bir'),
  monthly('Aylık'),
  quarterly('Üç aylık'),
  yearly('Yıllık'),
  custom('Özel aralık');

  const PaymentFrequency(this.label);
  final String label;
}

enum SubscriptionKind {
  digitalService('Dijital hizmet'),
  membership('Üyelik'),
  insurance('Sigorta'),
  education('Eğitim'),
  maintenance('Bakım / servis'),
  custom('Diğer abonelik');

  const SubscriptionKind(this.label);
  final String label;
}

enum RecordType {
  debt('Banka borcu'),
  personalDebt('Kişisel / kurumsal borç'),
  bill('Fatura'),
  subscription('Abonelik'),
  rent('Kira / taksit');

  const RecordType(this.label);
  final String label;
}'''
text, count = enum_re.subn(enum_new, text, count=1)
assert count == 1, 'model enum replacement failed'
path.write_text(text, encoding='utf-8')

# Remove all embedded demo records. Keep the compatibility factory but make it empty.
path = root / 'lib/models/mizan_models.dart'
text = path.read_text(encoding='utf-8')
seed_start = text.find('  factory MizanState.seed()')
if seed_start >= 0:
    seed_end = text.find('\n}\n\nconst List<NotificationSlot>', seed_start)
    if seed_end < 0:
        raise SystemExit('MizanState.seed block boundary was not found')
    text = (
        text[:seed_start]
        + '  factory MizanState.seed() => MizanState.empty();\n'
        + text[seed_end:]
    )
path.write_text(text, encoding='utf-8')

# Local store: never seed examples and never overwrite two corrupt files.
path = root / 'lib/services/local_store.dart'
text = path.read_text(encoding='utf-8')
load_re = re.compile(r"  @override\n  Future<StoreLoadResult> load\(\) async \{.*?\n  \}\n\n  Future<MizanState\?> _tryRead", re.S)
load_new = '''  @override
  Future<StoreLoadResult> load() async {
    final primary = await _file(_primaryFileName);
    final backup = await _file(_backupFileName);
    final primaryExists = await primary.exists();
    final backupExists = await backup.exists();

    final primaryResult = await _tryRead(primary);
    if (primaryResult != null) {
      return StoreLoadResult(
        state: primaryResult,
        source: StoreLoadSource.primary,
      );
    }

    final backupResult = await _tryRead(backup);
    if (backupResult != null) {
      final temporary = await _file(_temporaryFileName);
      await backup.copy(temporary.path);
      final verified = await _tryRead(temporary);
      if (verified == null) {
        throw const FileSystemException('Yedek kayıt doğrulanamadı.');
      }
      if (await primary.exists()) {
        await primary.delete();
      }
      try {
        await temporary.rename(primary.path);
      } on FileSystemException {
        await temporary.copy(primary.path);
        await temporary.delete();
      }
      return StoreLoadResult(
        state: backupResult,
        source: StoreLoadSource.backup,
        message: 'Ana kayıt okunamadı; son sağlam yedek geri yüklendi.',
      );
    }

    if (primaryExists || backupExists) {
      throw const FileSystemException(
        'Ana ve yedek kayıt dosyaları okunamadı. Dosyalar korunuyor.',
      );
    }

    final empty = MizanState.empty();
    await save(empty);
    return StoreLoadResult(
      state: empty,
      source: StoreLoadSource.fresh,
      message: 'MİZAN kullanıma hazır. İlk kişi veya kaydı ekleyebilirsin.',
    );
  }

  Future<MizanState?> _tryRead'''
text, count = load_re.subn(load_new, text, count=1)
assert count == 1, 'local store load replacement failed'
path.write_text(text, encoding='utf-8')

# Dependencies for CSV import/export; remove battery-settings intent dependency.
path = root / 'pubspec.yaml'
text = path.read_text(encoding='utf-8')
text = text.replace('  android_intent_plus: ^5.3.1\n', '')
if '  csv:' not in text:
    text = text.replace(
        '  path_provider: ^2.1.6\n',
        '  path_provider: ^2.1.6\n  csv: ^7.1.0\n  file_picker: ^11.0.2\n',
    )
else:
    text = re.sub(r'^  file_picker:.*$', '  file_picker: ^11.0.2', text, flags=re.M)
path.write_text(text, encoding='utf-8')

# Complete CSV service. Snapshot is authoritative; detail rows make the backup readable.
csv_service = r'''import 'dart:convert';

import 'package:csv/csv.dart';

import '../models/mizan_models.dart';

class CsvBackupService {
  const CsvBackupService();

  static const formatName = 'MIZAN_CSV_BACKUP';
  static const _encoder = ListToCsvConverter();
  static const _decoder = CsvToListConverter();

  String exportState(MizanState state) {
    final safeState = state.copyWith(schemaVersion: currentSchemaVersion);
    final rows = <List<dynamic>>[
      const [
        'format',
        'schema_version',
        'entity_type',
        'entity_id',
        'person_id',
        'bank_id',
        'record_type',
        'record_id',
        'name',
        'amount',
        'date',
        'data_json',
      ],
      [
        formatName,
        currentSchemaVersion,
        'snapshot',
        'state',
        '',
        '',
        '',
        '',
        'MİZAN tam yedek',
        '',
        DateTime.now().toUtc().toIso8601String(),
        jsonEncode(safeState.toJson()),
      ],
    ];

    for (final person in safeState.people) {
      rows.add(_row('person', person.id, person.name, person.toJson(), personId: person.id));
      for (final bank in person.banks) {
        rows.add(_row('bank_group', bank.id, bank.userWrittenName, bank.toJson(), personId: person.id, bankId: bank.id, amount: bank.totalDebt));
        for (final debt in bank.products) {
          rows.add(_row('bank_debt', debt.id, debt.title, debt.toJson(), personId: person.id, bankId: bank.id, recordType: RecordType.debt.name, recordId: debt.id, amount: debt.remainingAmount, date: debt.dueDate));
          _children(rows, person.id, bank.id, RecordType.debt.name, debt.id, debt.payments, debt.notes);
        }
      }
      for (final debt in person.personalDebts) {
        rows.add(_row('personal_corporate_debt', debt.id, debt.title, debt.toJson(), personId: person.id, recordType: RecordType.personalDebt.name, recordId: debt.id, amount: debt.remainingAmount, date: debt.effectiveDueDate));
        _children(rows, person.id, '', RecordType.personalDebt.name, debt.id, debt.payments, debt.notes);
      }
      for (final bill in person.bills) {
        rows.add(_row('bill', bill.id, '${bill.kind.label} - ${bill.institutionName}', bill.toJson(), personId: person.id, recordType: RecordType.bill.name, recordId: bill.id, amount: bill.remainingAmount, date: bill.dueDate));
        _children(rows, person.id, '', RecordType.bill.name, bill.id, bill.payments, bill.notes);
      }
      for (final subscription in person.subscriptions) {
        rows.add(_row('subscription', subscription.id, subscription.title, subscription.toJson(), personId: person.id, recordType: RecordType.subscription.name, recordId: subscription.id, amount: subscription.remainingAmount, date: subscription.nextDueDate));
        _children(rows, person.id, '', RecordType.subscription.name, subscription.id, subscription.payments, subscription.notes);
      }
      for (final rent in person.rents) {
        rows.add(_row('rent_installment', rent.id, rent.title, rent.toJson(), personId: person.id, recordType: RecordType.rent.name, recordId: rent.id, amount: rent.remainingAmount, date: rent.dueDate));
        _children(rows, person.id, '', RecordType.rent.name, rent.id, rent.payments, rent.notes);
      }
    }
    for (final category in safeState.expenseCategories) {
      rows.add(_row('expense_category', category.id, category.name, category.toJson()));
    }
    for (final expense in safeState.expenses) {
      rows.add(_row('expense', expense.id, expense.name, expense.toJson(), recordId: expense.categoryId, amount: expense.totalAmount, date: expense.spentAt));
    }
    return _encoder.convert(rows);
  }

  MizanState importState(String content) {
    final rows = _decoder.convert(content);
    if (rows.length < 2) {
      throw const FormatException('CSV yedeği boş veya eksik.');
    }
    final header = rows.first.map((value) => value.toString()).toList();
    final formatIndex = header.indexOf('format');
    final typeIndex = header.indexOf('entity_type');
    final dataIndex = header.indexOf('data_json');
    if (formatIndex < 0 || typeIndex < 0 || dataIndex < 0) {
      throw const FormatException('Bu dosya MİZAN CSV yedeği değil.');
    }
    for (final row in rows.skip(1)) {
      if (row.length <= dataIndex) {
        continue;
      }
      if (row[formatIndex].toString() != formatName ||
          row[typeIndex].toString() != 'snapshot') {
        continue;
      }
      final decoded = jsonDecode(row[dataIndex].toString());
      if (decoded is! Map) {
        throw const FormatException('CSV tam yedek verisi geçersiz.');
      }
      return MizanState.fromJson(Map<String, dynamic>.from(decoded));
    }
    throw const FormatException('CSV içinde tam MİZAN yedeği bulunamadı.');
  }

  void _children(
    List<List<dynamic>> rows,
    String personId,
    String bankId,
    String type,
    String sourceId,
    List<PaymentRecord> payments,
    List<RecordNote> notes,
  ) {
    for (final payment in payments) {
      rows.add(_row('payment', payment.id, payment.method.isEmpty ? 'Ödeme' : payment.method, payment.toJson(), personId: personId, bankId: bankId, recordType: type, recordId: sourceId, amount: payment.amount, date: payment.paidAt));
    }
    for (final note in notes) {
      rows.add(_row('note', note.id, note.text, note.toJson(), personId: personId, bankId: bankId, recordType: type, recordId: sourceId, date: note.createdAt));
    }
  }

  List<dynamic> _row(
    String type,
    String id,
    String name,
    Map<String, dynamic> data, {
    String personId = '',
    String bankId = '',
    String recordType = '',
    String recordId = '',
    double? amount,
    DateTime? date,
  }) => [
    formatName,
    currentSchemaVersion,
    type,
    id,
    personId,
    bankId,
    recordType,
    recordId,
    name,
    amount ?? '',
    date?.toIso8601String() ?? '',
    jsonEncode(data),
  ];
}
'''
(root / 'lib/services/csv_backup_service.dart').write_text(csv_service, encoding='utf-8')

for reject in root.rglob('*.rej'):
    reject.unlink()

required_tokens = {
    'lib/controllers/mizan_controller.dart': [
        'bool get storageReady',
        'Future<void> restoreFromBackup',
        'await _scheduler.requestPermissions()',
    ],
    'lib/models/mizan_models.dart': [
        'enum CreditorType',
        'enum SubscriptionKind',
        'factory MizanState.seed() => MizanState.empty();',
    ],
    'lib/services/local_store.dart': [
        'StoreLoadSource.fresh',
        'final empty = MizanState.empty();',
        'Ana ve yedek kayıt dosyaları okunamadı',
    ],
    'lib/services/csv_backup_service.dart': [
        "static const formatName = 'MIZAN_CSV_BACKUP'",
        "'personal_corporate_debt'",
        "'subscription'",
    ],
    'pubspec.yaml': ['csv: ^7.1.0', 'file_picker: ^11.0.2'],
}
for relative, tokens in required_tokens.items():
    content = (root / relative).read_text(encoding='utf-8')
    missing = [token for token in tokens if token not in content]
    if missing:
        raise SystemExit(f'Revision prerequisite resolution failed for {relative}: {missing}')

for forbidden in ('Örnek kişi', 'Kredi kartı borcu', 'android_intent_plus'):
    matches = []
    for relative in ('lib/models/mizan_models.dart', 'pubspec.yaml'):
        if forbidden in (root / relative).read_text(encoding='utf-8'):
            matches.append(relative)
    if matches:
        raise SystemExit(f'Forbidden demo or removed dependency remains: {forbidden} in {matches}')

print('MIZAN v2 intermediate prerequisites and rejected hunks resolved.')
