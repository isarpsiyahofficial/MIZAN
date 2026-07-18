import 'package:flutter/material.dart';

import '../core/theme.dart';

class MizanDestination {
  const MizanDestination({required this.icon, required this.label});
  final IconData icon;
  final String label;
}

class ResponsiveScaffold extends StatelessWidget {
  const ResponsiveScaffold({
    required this.selectedIndex,
    required this.onSelected,
    required this.destinations,
    required this.child,
    super.key,
  });

  final int selectedIndex;
  final ValueChanged<int> onSelected;
  final List<MizanDestination> destinations;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final wide = constraints.maxWidth >= 840;
        final extended = constraints.maxWidth >= 1120;
        final compactNavigation = constraints.maxWidth < 430;
        final content = SafeArea(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 160),
            child: KeyedSubtree(key: ValueKey(selectedIndex), child: child),
          ),
        );
        if (!wide) {
          return Scaffold(
            body: content,
            bottomNavigationBar: NavigationBar(
              selectedIndex: selectedIndex,
              onDestinationSelected: onSelected,
              labelBehavior: compactNavigation
                  ? NavigationDestinationLabelBehavior.onlyShowSelected
                  : NavigationDestinationLabelBehavior.alwaysShow,
              destinations: [
                for (final destination in destinations)
                  NavigationDestination(
                    icon: Icon(destination.icon),
                    label: destination.label,
                  ),
              ],
            ),
          );
        }
        return Scaffold(
          body: Row(
            children: [
              NavigationRail(
                selectedIndex: selectedIndex,
                onDestinationSelected: onSelected,
                extended: extended,
                minExtendedWidth: 210,
                backgroundColor: Colors.white,
                groupAlignment: -0.8,
                leading: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  child: Image.asset(
                    'assets/brand/lefferion-prime-logo.png',
                    width: extended ? 58 : 44,
                    height: extended ? 58 : 44,
                    fit: BoxFit.contain,
                  ),
                ),
                destinations: [
                  for (final destination in destinations)
                    NavigationRailDestination(
                      icon: Icon(destination.icon),
                      selectedIcon: Icon(
                        destination.icon,
                        color: MizanTheme.ink,
                      ),
                      label: Text(destination.label),
                    ),
                ],
              ),
              const VerticalDivider(width: 1),
              Expanded(child: content),
            ],
          ),
        );
      },
    );
  }
}
