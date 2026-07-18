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

Future<void> _pumpApp(
  WidgetTester tester, {
  Size size = const Size(412, 915),
}) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final controller = MizanController(_MemoryStore(MizanState.seed()));
  await controller.load();
  await tester.pumpWidget(MizanApp(controller: controller));
  await tester.pumpAndSettle();
  expect(tester.takeException(), isNull);
}

Future<void> _tapNavigation(WidgetTester tester, IconData icon) async {
  final navigationBar = find.byType(NavigationBar);
  final navigationRail = find.byType(NavigationRail);
  final root = navigationBar.evaluate().isNotEmpty ? navigationBar : navigationRail;
  final target = find.descendant(of: root, matching: find.byIcon(icon));
  expect(target, findsOneWidget);
  await tester.tap(target);
  await tester.pumpAndSettle();
  expect(tester.takeException(), isNull);
}

Future<void> _scrollToTextAndTap(
  WidgetTester tester,
  String text, {
  Finder? scrollable,
}) async {
  final target = find.text(text);
  expect(target, findsOneWidget);
  await tester.scrollUntilVisible(
    target,
    240,
    scrollable: scrollable ?? find.byType(Scrollable).first,
  );
  await tester.pumpAndSettle();
  await tester.tap(target);
  await tester.pumpAndSettle();
  expect(tester.takeException(), isNull);
}

Future<void> _capture(
  WidgetTester tester,
  String filename, {
  Finder? target,
}) async {
  await tester.pumpAndSettle();
  expect(tester.takeException(), isNull);
  await expectLater(
    target ?? find.byType(Scaffold).first,
    matchesGoldenFile('goldens/$filename.png'),
  );
}

void main() {
  testWidgets('ana sayfa telefon görseli', (tester) async {
    await _pumpApp(tester);
    await _capture(tester, '01-dashboard-phone');
  });

  testWidgets('kişiler telefon görseli', (tester) async {
    await _pumpApp(tester);
    await _tapNavigation(tester, Icons.people_alt_outlined);
    await _capture(tester, '02-people-phone');
  });

  testWidgets('borç detay görseli', (tester) async {
    await _pumpApp(tester);
    await _tapNavigation(tester, Icons.people_alt_outlined);
    final peopleList = find.byType(ListView).first;
    await _scrollToTextAndTap(
      tester,
      'Kullanıcının yazdığı banka adı',
      scrollable: peopleList,
    );
    await _scrollToTextAndTap(
      tester,
      'Kredi kartı borcu',
      scrollable: peopleList,
    );
    expect(find.byType(BottomSheet), findsOneWidget);
    await _capture(
      tester,
      '03-debt-detail-phone',
      target: find.byType(Overlay).first,
    );
  });

  testWidgets('giderler telefon görseli', (tester) async {
    await _pumpApp(tester);
    await _tapNavigation(tester, Icons.shopping_bag_outlined);
    await _scrollToTextAndTap(
      tester,
      'Market',
      scrollable: find.byType(ListView).first,
    );
    await _capture(tester, '04-expenses-phone');
  });

  testWidgets('raporlar telefon görseli', (tester) async {
    await _pumpApp(tester);
    await _tapNavigation(tester, Icons.bar_chart_outlined);
    await _capture(tester, '05-reports-phone');
  });

  testWidgets('ayarlar telefon görseli', (tester) async {
    await _pumpApp(tester);
    await _tapNavigation(tester, Icons.settings_outlined);
    await _capture(tester, '06-settings-phone');
  });

  testWidgets('ana sayfa tablet görseli', (tester) async {
    await _pumpApp(tester, size: const Size(1180, 820));
    await _capture(tester, '07-dashboard-tablet');
  });
}
