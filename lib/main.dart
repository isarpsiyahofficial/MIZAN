import 'package:flutter/material.dart';

import 'controllers/mizan_controller.dart';
import 'core/theme.dart';
import 'screens/dashboard_screen.dart';
import 'screens/expenses_screen.dart';
import 'screens/people_screen.dart';
import 'screens/reports_screen.dart';
import 'screens/settings_screen.dart';
import 'services/local_store.dart';
import 'services/notification_service.dart';
import 'widgets/responsive_scaffold.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final controller = MizanController(
    LocalStore(),
    scheduler: LocalNotificationService(),
  );
  await controller.load();
  runApp(MizanApp(controller: controller));
}

class MizanApp extends StatelessWidget {
  const MizanApp({required this.controller, super.key});
  final MizanController controller;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LEFFERION PRIME - MIZAN',
      debugShowCheckedModeBanner: false,
      theme: MizanTheme.light(),
      home: MizanHome(controller: controller),
    );
  }
}

class MizanHome extends StatefulWidget {
  const MizanHome({required this.controller, super.key});
  final MizanController controller;
  @override
  State<MizanHome> createState() => _MizanHomeState();
}

class _MizanHomeState extends State<MizanHome> {
  int selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, _) {
        final pages = [
          DashboardScreen(controller: widget.controller),
          PeopleScreen(controller: widget.controller),
          ExpensesScreen(controller: widget.controller),
          ReportsScreen(controller: widget.controller),
          SettingsScreen(controller: widget.controller),
        ];
        return Stack(
          children: [
            ResponsiveScaffold(
              selectedIndex: selectedIndex,
              onSelected: (value) => setState(() => selectedIndex = value),
              destinations: const [
                MizanDestination(icon: Icons.space_dashboard_outlined, label: 'Ana sayfa'),
                MizanDestination(icon: Icons.people_alt_outlined, label: 'Kişiler'),
                MizanDestination(icon: Icons.shopping_bag_outlined, label: 'Giderler'),
                MizanDestination(icon: Icons.bar_chart_outlined, label: 'Raporlar'),
                MizanDestination(icon: Icons.settings_outlined, label: 'Ayarlar'),
              ],
              child: pages[selectedIndex],
            ),
            if (widget.controller.isBusy)
              const Positioned(left: 0, right: 0, top: 0, child: LinearProgressIndicator(minHeight: 3)),
            if (widget.controller.lastError != null || widget.controller.loadMessage != null)
              Positioned(
                left: 12,
                right: 12,
                top: MediaQuery.paddingOf(context).top + 8,
                child: Material(
                  elevation: 4,
                  borderRadius: BorderRadius.circular(14),
                  color: widget.controller.lastError != null
                      ? Theme.of(context).colorScheme.errorContainer
                      : Theme.of(context).colorScheme.secondaryContainer,
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(14, 10, 6, 10),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            widget.controller.lastError ?? widget.controller.loadMessage!,
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                        ),
                        IconButton(
                          tooltip: 'Kapat',
                          onPressed: widget.controller.clearMessages,
                          icon: const Icon(Icons.close),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        );
      },
    );
  }
}
