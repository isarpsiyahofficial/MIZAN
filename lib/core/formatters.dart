import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/mizan_models.dart';

DateTime dateOnly(DateTime value) => DateTime(value.year, value.month, value.day);

bool isSameDay(DateTime a, DateTime b) =>
    a.year == b.year && a.month == b.month && a.day == b.day;

bool isSameMonth(DateTime value, DateTime month) =>
    value.year == month.year && value.month == month.month;

int calendarDaysBetween(DateTime from, DateTime to) =>
    dateOnly(to).difference(dateOnly(from)).inDays;

String money(num value) {
  final safe = value.isFinite ? value.toDouble() : 0.0;
  final negative = safe < 0;
  final absolute = safe.abs();
  final fixed = absolute.toStringAsFixed(2);
  final parts = fixed.split('.');
  final integerPart = parts.first;
  final decimalPart = parts.last;
  final grouped = StringBuffer();
  for (var index = 0; index < integerPart.length; index++) {
    grouped.write(integerPart[index]);
    final remaining = integerPart.length - index - 1;
    if (remaining > 0 && remaining % 3 == 0) {
      grouped.write('.');
    }
  }
  return '${negative ? '-' : ''}${grouped.toString()},$decimalPart TL';
}

String decimalText(num value) {
  final rounded = value.toStringAsFixed(2);
  return rounded.endsWith('.00')
      ? rounded.substring(0, rounded.length - 3)
      : rounded.replaceAll('.', ',');
}

double parseMoney(String input) {
  var clean = input
      .trim()
      .toLowerCase()
      .replaceAll('₺', '')
      .replaceAll('tl', '')
      .replaceAll(RegExp(r'\s+'), '');
  if (clean.isEmpty) {
    throw const FormatException('Tutar boş bırakılamaz.');
  }
  final negative = clean.startsWith('-');
  clean = clean.replaceAll('-', '');
  if (!RegExp(r'^\d+[\d.,]*$').hasMatch(clean)) {
    throw const FormatException('Geçerli bir para tutarı girin.');
  }

  final commaCount = ','.allMatches(clean).length;
  final dotCount = '.'.allMatches(clean).length;
  String normalized;

  if (commaCount > 0 && dotCount > 0) {
    final lastComma = clean.lastIndexOf(',');
    final lastDot = clean.lastIndexOf('.');
    final decimalSeparator = lastComma > lastDot ? ',' : '.';
    final thousandsSeparator = decimalSeparator == ',' ? '.' : ',';
    normalized = clean.replaceAll(thousandsSeparator, '');
    normalized = normalized.replaceAll(decimalSeparator, '.');
  } else if (commaCount + dotCount == 0) {
    normalized = clean;
  } else {
    final separator = commaCount > 0 ? ',' : '.';
    final count = commaCount + dotCount;
    if (count > 1) {
      final segments = clean.split(separator);
      final allThousands = segments.skip(1).every((part) => part.length == 3);
      if (!allThousands) {
        throw const FormatException('Tutar biçimi anlaşılamadı.');
      }
      normalized = segments.join();
    } else {
      final separatorIndex = clean.indexOf(separator);
      final decimals = clean.length - separatorIndex - 1;
      if (decimals == 0) {
        normalized = clean.substring(0, separatorIndex);
      } else if (decimals <= 2) {
        normalized = clean.replaceAll(separator, '.');
      } else if (decimals == 3 && separatorIndex > 0) {
        normalized = clean.replaceAll(separator, '');
      } else {
        throw const FormatException('En fazla iki kuruş hanesi girilebilir.');
      }
    }
  }

  final parsed = double.tryParse(normalized);
  if (parsed == null || !parsed.isFinite) {
    throw const FormatException('Geçerli bir para tutarı girin.');
  }
  final result = negative ? -parsed : parsed;
  return double.parse(result.toStringAsFixed(2));
}

double parsePositiveDecimal(String input, {String fieldName = 'Değer'}) {
  final normalized = input.trim().replaceAll(',', '.');
  final value = double.tryParse(normalized);
  if (value == null || !value.isFinite || value <= 0) {
    throw FormatException('$fieldName sıfırdan büyük olmalı.');
  }
  return value;
}

int? parseOptionalPositiveInt(String input, {String fieldName = 'Değer'}) {
  final clean = input.trim();
  if (clean.isEmpty) {
    return null;
  }
  final value = int.tryParse(clean);
  if (value == null || value <= 0) {
    throw FormatException('$fieldName pozitif tam sayı olmalı.');
  }
  return value;
}

String shortDate(DateTime value) {
  const months = [
    'Oca',
    'Şub',
    'Mar',
    'Nis',
    'May',
    'Haz',
    'Tem',
    'Ağu',
    'Eyl',
    'Eki',
    'Kas',
    'Ara',
  ];
  return '${value.day} ${months[value.month - 1]} ${value.year}';
}

String monthLabel(DateTime value) {
  const months = [
    'Ocak',
    'Şubat',
    'Mart',
    'Nisan',
    'Mayıs',
    'Haziran',
    'Temmuz',
    'Ağustos',
    'Eylül',
    'Ekim',
    'Kasım',
    'Aralık',
  ];
  return '${months[value.month - 1]} ${value.year}';
}

String timeLabel(int hour, int minute) =>
    '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';

String newId(String prefix) {
  final random = math.Random().nextInt(1 << 32).toRadixString(16);
  return '$prefix-${DateTime.now().microsecondsSinceEpoch}-$random';
}

int stableNotificationId(String value) {
  var hash = 0x811c9dc5;
  for (final unit in value.codeUnits) {
    hash ^= unit;
    hash = (hash * 0x01000193) & 0x7fffffff;
  }
  return hash == 0 ? 1 : hash;
}

Color statusColor(PaymentStatus status) {
  switch (status) {
    case PaymentStatus.active:
      return const Color(0xFF1F7A5A);
    case PaymentStatus.upcoming:
      return const Color(0xFFD88218);
    case PaymentStatus.overdue:
      return const Color(0xFFC33A3A);
    case PaymentStatus.completed:
      return const Color(0xFF325DDE);
    case PaymentStatus.passive:
      return const Color(0xFF6D7889);
  }
}
