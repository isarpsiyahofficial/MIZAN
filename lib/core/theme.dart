import 'package:flutter/material.dart';

class MizanTheme {
  static const ink = Color(0xFF172033);
  static const muted = Color(0xFF667085);
  static const surface = Color(0xFFF6F8FC);
  static const line = Color(0xFFDCE3EC);
  static const green = Color(0xFF18794E);
  static const red = Color(0xFFB42318);
  static const orange = Color(0xFFB54708);
  static const blue = Color(0xFF175CD3);
  static const purple = Color(0xFF6938EF);

  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(
      seedColor: ink,
      brightness: Brightness.light,
      primary: ink,
      secondary: green,
      surface: surface,
      error: red,
    );

    final border = OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: line),
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: surface,
      visualDensity: VisualDensity.standard,
      appBarTheme: const AppBarTheme(
        backgroundColor: surface,
        foregroundColor: ink,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardTheme(
        color: Colors.white,
        elevation: 0,
        margin: EdgeInsets.zero,
        clipBehavior: Clip.antiAlias,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: const BorderSide(color: line),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: border,
        enabledBorder: border,
        focusedBorder: border.copyWith(
          borderSide: const BorderSide(color: ink, width: 1.5),
        ),
        errorMaxLines: 3,
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(44, 46),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(44, 46),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(minimumSize: const Size(44, 44)),
      ),
      navigationBarTheme: const NavigationBarThemeData(
        height: 70,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      ),
      dividerTheme: const DividerThemeData(color: line, thickness: 1),
    );
  }
}
