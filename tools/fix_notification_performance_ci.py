from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label} bulunamadı; kaynak beklenenden farklı.")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_notification_performance_ci.py <source-root>")
    root = Path(sys.argv[1]).resolve()

    settings_path = root / "lib/screens/settings_screen.dart"
    settings = settings_path.read_text(encoding="utf-8")
    settings = replace_once(
        settings,
        """    required this.ready,
    this.neutral = false,
  });""",
        """    required this.ready,
  });""",
        "Bildirim sistem durumu kurucusu",
    )
    settings = replace_once(
        settings,
        """  final bool ready;
  final bool neutral;

  @override
  Widget build(BuildContext context) {
    final color = neutral
        ? MizanTheme.blue
        : ready
        ? MizanTheme.green
        : MizanTheme.red;""",
        """  final bool ready;

  @override
  Widget build(BuildContext context) {
    final color = ready ? MizanTheme.green : MizanTheme.red;""",
        "Bildirim sistem durumu renk hesabı",
    )
    settings_path.write_text(settings, encoding="utf-8")

    reminder_engine_path = root / "lib/services/reminder_engine.dart"
    reminder_engine = reminder_engine_path.read_text(encoding="utf-8")
    reminder_engine = replace_once(
        reminder_engine,
        """        reminders.add(
          ScheduledReminder(
            id: stableNotificationId(key),
            sourceId: record.sourceId,
            kind: ReminderKind.payment,
            title: '${record.type.label}: ${record.title}',
            message:
                '${slot.message.trim()} Son ödeme ${shortDate(dueDay)}. Kalan tutar ${money(record.amount)}.'
                    .trim(),
            scheduledAt: scheduledAt,
            repeatsDaily: true,
          ),
        );""",
        """        final timing = record.overdueDays > 0
            ? 'Ödeme ${record.overdueDays} gün gecikti.'
            : 'Son ödeme ${shortDate(dueDay)}.';
        reminders.add(
          ScheduledReminder(
            id: stableNotificationId(key),
            sourceId: record.sourceId,
            kind: ReminderKind.payment,
            title: '${record.type.label}: ${record.title}',
            message:
                '${slot.message.trim()} $timing Kalan tutar ${money(record.amount)}.'
                    .trim(),
            scheduledAt: scheduledAt,
            repeatsDaily: true,
          ),
        );""",
        "Gecikmiş ödeme bildiriminde yalnız gün sayısı",
    )
    reminder_engine_path.write_text(reminder_engine, encoding="utf-8")

    reminder_test_path = root / "test/reminder_engine_test.dart"
    reminder_test = reminder_test_path.read_text(encoding="utf-8")
    reminder_test = replace_once(
        reminder_test,
        "item.scheduledAt.day == 5 &&",
        "item.scheduledAt.day == 1 &&",
        "Aylık ödeme bildiriminin sıradaki dakik çalışma günü",
    )
    reminder_test = replace_once(
        reminder_test,
        """    expect(reminders.first.message, contains('2.500,00 TL'));""",
        """    expect(reminders.first.message, contains('5 Tem 2026'));
    expect(reminders.first.message, contains('2.500,00 TL'));""",
        "Aylık ödeme bildirimi vade metni",
    )
    reminder_test_path.write_text(reminder_test, encoding="utf-8")

    final_test_path = root / "test/notification_performance_report_final_test.dart"
    final_test = final_test_path.read_text(encoding="utf-8")
    final_test = replace_once(
        final_test,
        """    expect(find.text('Açık planlanan ödemeler'), findsOneWidget);
    expect(find.textContaining('7 açık kayıt'), findsOneWidget);
    expect(find.text('Bu ay yapılan ödemeler'), findsOneWidget);
    expect(find.textContaining('1 ödeme'), findsOneWidget);""",
        """    expect(find.text('Açık planlanan ödemeler'), findsOneWidget);
    expect(find.textContaining('7 açık kayıt'), findsOneWidget);
    final paidSection = find.text('Bu ay yapılan ödemeler');
    await tester.scrollUntilVisible(
      paidSection,
      300,
      scrollable: find.byType(Scrollable).last,
    );
    expect(paidSection, findsOneWidget);
    expect(find.textContaining('1 ödeme'), findsOneWidget);""",
        "Aylık ödeme modalı yapılan ödemeler bölümü testi",
    )
    final_test_path.write_text(final_test, encoding="utf-8")

    responsive_test_path = root / "test/responsive_test.dart"
    responsive_test = responsive_test_path.read_text(encoding="utf-8")
    responsive_test = replace_once(
        responsive_test,
        "expect(find.text('Bildirim türü'), findsOneWidget);",
        "expect(find.text('Durum ve saat'), findsOneWidget);",
        "Alarm türü kaldırılan bildirim ayrıntısı responsive testi",
    )
    responsive_test_path.write_text(responsive_test, encoding="utf-8")

    checks = {
        settings_path: ["final color = ready ? MizanTheme.green : MizanTheme.red;"],
        reminder_engine_path: [
            "? 'Ödeme ${record.overdueDays} gün gecikti.'",
            "'$timing Kalan tutar",
        ],
        reminder_test_path: [
            "item.scheduledAt.day == 1",
            "contains('5 Tem 2026')",
        ],
        final_test_path: [
            "final paidSection = find.text('Bu ay yapılan ödemeler')",
            "scrollUntilVisible",
        ],
        responsive_test_path: ["expect(find.text('Durum ve saat'), findsOneWidget);"],
    }
    problems: list[str] = []
    for path, tokens in checks.items():
        source = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in source:
                problems.append(f"{path.name}: {token}")
    if "this.neutral" in settings_path.read_text(encoding="utf-8"):
        problems.append("settings_screen.dart: kullanılmayan neutral parametresi kaldı")
    if problems:
        raise SystemExit(f"Bildirim-performans CI düzeltmeleri eksik: {problems}")
    print("Bildirim ayarları, gecikme günleri, davranış ve responsive testleri güncel sisteme uyumlandı.")


if __name__ == "__main__":
    main()
