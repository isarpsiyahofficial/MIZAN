import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lefferion_prime_mizan/controllers/mizan_controller.dart';
import 'package:lefferion_prime_mizan/main.dart';
import 'package:lefferion_prime_mizan/models/mizan_models.dart';
import 'package:lefferion_prime_mizan/services/local_store.dart';

class _MemoryStore implements MizanStore {
  _MemoryStore(this.state);

  MizanState state;

  @override
  Future<StoreLoadResult> load() async => StoreLoadResult(
        state: state,
        source: StoreLoadSource.primary,
      );

  @override
  Future<void> reset(MizanState value) async => state = value;

  @override
  Future<void> save(MizanState value) async => state = value;
}

Future<MizanController> _pumpApp(
  WidgetTester tester,
  MizanState state,
) async {
  tester.view.physicalSize = const Size(412, 915);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final controller = MizanController(_MemoryStore(state));
  await controller.load();
  await tester.pumpWidget(MizanApp(controller: controller));
  await tester.pumpAndSettle();
  expect(tester.takeException(), isNull);
  return controller;
}

Future<void> _tapText(WidgetTester tester, String text) async {
  final finder = find.text(text).last;
  await tester.ensureVisible(finder);
  await tester.tap(finder);
  await tester.pumpAndSettle();
}

Finder _dialogFields() => find.descendant(
      of: find.byType(AlertDialog),
      matching: find.byType(TextFormField),
    );

Future<void> _addPerson(
  WidgetTester tester,
  MizanController controller,
) async {
  await _tapText(tester, 'Kişiler');
  await _tapText(tester, 'Kişi ekle');
  await tester.enterText(_dialogFields().single, 'Test Kişi');
  await _tapText(tester, 'Kaydet');
  expect(controller.state.people.single.name, 'Test Kişi');
}

void main() {
  testWidgets('ana navigasyonun tüm sekmeleri doğru ekranı açar', (tester) async {
    await _pumpApp(tester, MizanState.seed());

    await _tapText(tester, 'Kişiler');
    expect(find.text('Kişiler ve ödemeler'), findsOneWidget);
    await _tapText(tester, 'Giderler');
    expect(find.text('Borç, fatura ve kiradan bağımsız kategori bazlı harcama takibi'), findsOneWidget);
    await _tapText(tester, 'Raporlar');
    expect(find.text('Kişi, ay, borç türü ve durum filtreleriyle hesaplanan ayrıntılı toplamlar'), findsOneWidget);
    await _tapText(tester, 'Ayarlar');
    expect(find.text('Gerçek Android bildirimleri, yerel kayıt sağlığı ve güvenli sıfırlama'), findsOneWidget);
    await _tapText(tester, 'Ana sayfa');
    expect(find.text('Kritik ödemeler'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('kişi banka borç ödeme ve not butonları kaynak kaydı günceller', (tester) async {
    final controller = await _pumpApp(tester, MizanState.empty());
    await _addPerson(tester, controller);

    await _tapText(tester, 'Banka ekle');
    await tester.enterText(_dialogFields().single, 'Test Banka');
    await _tapText(tester, 'Kaydet');
    expect(controller.state.people.single.banks.single.userWrittenName, 'Test Banka');

    await tester.tap(find.byTooltip('Banka grubu işlemleri'));
    await tester.pumpAndSettle();
    await _tapText(tester, 'Borç ürünü ekle');
    final debtFields = _dialogFields();
    await tester.enterText(debtFields.at(0), 'Test Kart');
    await tester.enterText(debtFields.at(1), '1000');
    await tester.enterText(debtFields.at(2), '250');
    await _tapText(tester, 'Kaydet');

    final debt = controller.state.people.single.banks.single.products.single;
    expect(debt.title, 'Test Kart');
    expect(debt.remainingAmount, 1000);

    await _tapText(tester, 'Test Banka');
    await _tapText(tester, 'Test Kart');
    await _tapText(tester, 'Ödeme ekle');
    await _tapText(tester, 'Kaydet');
    expect(
      controller.state.people.single.banks.single.products.single.remainingAmount,
      0,
    );

    final noteButton = find.text('Not ekle');
    await tester.scrollUntilVisible(
      noteButton,
      250,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.tap(noteButton);
    await tester.pumpAndSettle();
    await tester.enterText(_dialogFields().single, 'Kayda özel test notu');
    await _tapText(tester, 'Kaydet');
    expect(
      controller.state.people.single.banks.single.products.single.notes.single.text,
      'Kayda özel test notu',
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('fatura ve kira formları butonlardan açılır ve ayrı kaydedilir', (tester) async {
    final controller = await _pumpApp(tester, MizanState.empty());
    await _addPerson(tester, controller);

    await _tapText(tester, 'Fatura ekle');
    final billFields = _dialogFields();
    await tester.enterText(billFields.at(0), 'Test Kurum');
    await tester.enterText(billFields.at(1), '350,75');
    await _tapText(tester, 'Kaydet');
    expect(controller.state.people.single.bills.single.institutionName, 'Test Kurum');
    expect(controller.state.people.single.bills.single.amount, 350.75);

    await _tapText(tester, 'Kira / taksit ekle');
    final rentFields = _dialogFields();
    await tester.enterText(rentFields.at(0), 'Test Kira');
    await tester.enterText(rentFields.at(1), '15000');
    await tester.enterText(rentFields.at(3), 'Test Alıcı');
    await _tapText(tester, 'Kaydet');
    expect(controller.state.people.single.rents.single.title, 'Test Kira');
    expect(controller.state.people.single.rents.single.receiverName, 'Test Alıcı');
    expect(controller.state.people.single.bills, hasLength(1));
    expect(tester.takeException(), isNull);
  });

  testWidgets('gider kategori ekle düzenle harcama ekle ve onaylı sil akışı çalışır', (tester) async {
    final controller = await _pumpApp(tester, MizanState.empty());
    await _tapText(tester, 'Giderler');

    await _tapText(tester, 'Kategori');
    await tester.enterText(_dialogFields().single, 'Market Test');
    await _tapText(tester, 'Kaydet');
    expect(controller.state.expenseCategories.single.name, 'Market Test');

    await _tapText(tester, 'Harcama');
    final expenseFields = _dialogFields();
    await tester.enterText(expenseFields.at(0), 'Ekmek');
    await tester.enterText(expenseFields.at(2), '45,50');
    await _tapText(tester, 'Kaydet');
    expect(controller.state.expenses.single.name, 'Ekmek');
    expect(controller.state.expenses.single.totalAmount, 45.50);

    await tester.tap(find.byTooltip('Kategori işlemleri'));
    await tester.pumpAndSettle();
    await _tapText(tester, 'Kategoriyi düzenle');
    await tester.enterText(_dialogFields().single, 'Market Düzenli');
    await _tapText(tester, 'Kaydet');
    expect(controller.state.expenseCategories.single.name, 'Market Düzenli');

    await tester.tap(find.byTooltip('Kategori işlemleri'));
    await tester.pumpAndSettle();
    await _tapText(tester, 'Kategoriyi sil');
    final confirmation = find.descendant(
      of: find.byType(AlertDialog),
      matching: find.byType(TextField),
    );
    await tester.enterText(confirmation.single, 'ONAYLIYORUM');
    await _tapText(tester, 'Kategori ve harcamaları sil');
    expect(controller.state.expenseCategories, isEmpty);
    expect(controller.state.expenses, isEmpty);
    expect(tester.takeException(), isNull);
  });

  testWidgets('ayar butonları bildirim durumunu ve mesajı kaydeder, sıfırlama vazgeçilebilir', (tester) async {
    final controller = await _pumpApp(tester, MizanState.seed());
    await _tapText(tester, 'Ayarlar');

    await tester.tap(find.byType(Switch).first);
    await tester.pumpAndSettle();
    expect(controller.state.notificationsEnabled, isFalse);

    await _tapText(tester, 'Sabah gider · 07:00');
    await tester.enterText(_dialogFields().single, 'Yeni sabah mesajı');
    await _tapText(tester, 'Kaydet');
    expect(controller.state.notificationSlots.first.message, 'Yeni sabah mesajı');

    final personCount = controller.state.people.length;
    await _tapText(tester, 'Tüm veriyi örnek kayıtlarla sıfırla');
    await _tapText(tester, 'Vazgeç');
    expect(controller.state.people.length, personCount);
    expect(tester.takeException(), isNull);
  });
}
