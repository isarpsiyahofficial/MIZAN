import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lefferion_prime_mizan/controllers/mizan_controller.dart';
import 'package:lefferion_prime_mizan/main.dart';
import 'package:lefferion_prime_mizan/models/mizan_models.dart';
import 'package:lefferion_prime_mizan/services/local_store.dart';

class _DiagnosticStore implements MizanStore {
  _DiagnosticStore(this.state);
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

void main() {
  testWidgets('rapor ekranındaki taşan render zincirini yazdırır', (tester) async {
    tester.view.physicalSize = const Size(412, 915);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final controller = MizanController(_DiagnosticStore(MizanState.seed()));
    await controller.load();
    await tester.pumpWidget(MizanApp(controller: controller));
    await tester.pumpAndSettle();

    final reportIcon = find.descendant(
      of: find.byType(NavigationBar),
      matching: find.byIcon(Icons.bar_chart_outlined),
    );
    await tester.tap(reportIcon);
    await tester.pumpAndSettle();

    final error = tester.takeException();
    if (error != null) {
      debugPrint('REPORT_OVERFLOW_ERROR: $error');
      debugDumpRenderTree();
    }
    expect(error, isNull);
  });
}
