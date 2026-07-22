from pathlib import Path
root=Path.cwd()
# Notification service
p=root/'lib/services/notification_service.dart'; s=p.read_text()
s=s.replace("""  Future<NotificationHealth> requestPermissions();
  Future<void> reschedule(MizanState state);
}
""","""  Future<NotificationHealth> requestPermissions();
  Future<void> reschedule(MizanState state);
  Future<void> showTestNotification({
    required NotificationSoundMode soundMode,
    required NotificationDeliveryMode deliveryMode,
  });
}
""",1)
s=s.replace("""  @override
  Future<void> reschedule(MizanState state) async {}
}
""","""  @override
  Future<void> reschedule(MizanState state) async {}

  @override
  Future<void> showTestNotification({
    required NotificationSoundMode soundMode,
    required NotificationDeliveryMode deliveryMode,
  }) async {}
}
""",1)
start=s.index('  NotificationDetails _detailsFor(')
end=s.index('\n\n  final FlutterLocalNotificationsPlugin', start)
new_func="""  NotificationDetails _detailsFor(
    ReminderKind kind,
    NotificationSoundMode soundMode,
    NotificationDeliveryMode deliveryMode,
  ) {
    final silent = soundMode == NotificationSoundMode.silent;
    final isAlarm = deliveryMode == NotificationDeliveryMode.alarm;
    final soundName = switch (soundMode) {
      NotificationSoundMode.system => 'system',
      NotificationSoundMode.soft => 'soft',
      NotificationSoundMode.alert => 'alert',
      NotificationSoundMode.silent => 'silent',
    };
    final androidSound = switch (soundMode) {
      NotificationSoundMode.soft =>
        const RawResourceAndroidNotificationSound('mizan_soft'),
      NotificationSoundMode.alert =>
        const RawResourceAndroidNotificationSound('mizan_alert'),
      _ => null,
    };
    final base = isAlarm
        ? 'alarm'
        : (kind == ReminderKind.expense ? 'expense' : 'payment');
    return NotificationDetails(
      android: AndroidNotificationDetails(
        'mizan_${base}_${soundName}_v6',
        isAlarm
            ? 'Alarm tipi hatırlatmalar'
            : (kind == ReminderKind.expense
                  ? 'Gider hatırlatmaları'
                  : 'Ödeme hatırlatmaları'),
        channelDescription: isAlarm
            ? 'Yüksek öncelikli alarm tipi MİZAN hatırlatmaları'
            : (kind == ReminderKind.expense
                  ? 'Günlük gider kaydı hatırlatmaları'
                  : 'Tüm kayıt türlerinin son ödeme hatırlatmaları'),
        importance: isAlarm
            ? Importance.max
            : (kind == ReminderKind.expense
                  ? Importance.defaultImportance
                  : Importance.high),
        priority: isAlarm
            ? Priority.max
            : (kind == ReminderKind.expense
                  ? Priority.defaultPriority
                  : Priority.high),
        category: isAlarm ? AndroidNotificationCategory.alarm : null,
        audioAttributesUsage: isAlarm
            ? AudioAttributesUsage.alarm
            : AudioAttributesUsage.notification,
        visibility: isAlarm ? NotificationVisibility.public : null,
        playSound: !silent,
        enableVibration: !silent && isAlarm,
        sound: androidSound,
      ),
    );
  }
"""
s=s[:start]+new_func+s[end:]
old_loop="""    for (final reminder in plan) {
      final local = reminder.scheduledAt;
      final scheduled = tz.TZDateTime(
        tz.local,
        local.year,
        local.month,
        local.day,
        local.hour,
        local.minute,
      );
      await _plugin.zonedSchedule(
        id: reminder.id,
        title: reminder.title,
        body: reminder.message,
        scheduledDate: scheduled,
        notificationDetails: _detailsFor(
          reminder.kind,
          state.notificationSoundMode,
        ),
        androidScheduleMode: mode,
        payload: '${reminder.kind.name}:${reminder.sourceId}',
        matchDateTimeComponents: reminder.repeatsDaily
            ? DateTimeComponents.time
            : null,
      );
    }
  }
}
"""
new_loop="""    var scheduledCount = 0;
    Object? lastError;
    for (final reminder in plan) {
      final local = reminder.scheduledAt;
      final scheduled = tz.TZDateTime(
        tz.local,
        local.year,
        local.month,
        local.day,
        local.hour,
        local.minute,
      );
      try {
        await _plugin.zonedSchedule(
          id: reminder.id,
          title: reminder.title,
          body: reminder.message,
          scheduledDate: scheduled,
          notificationDetails: _detailsFor(
            reminder.kind,
            state.notificationSoundMode,
            reminder.deliveryMode,
          ),
          androidScheduleMode: mode,
          payload: '${reminder.kind.name}:${reminder.sourceId}',
          matchDateTimeComponents: reminder.repeatsDaily
              ? DateTimeComponents.time
              : null,
        );
        scheduledCount += 1;
      } on Object catch (error) {
        lastError = error;
      }
    }
    if (plan.isNotEmpty && scheduledCount == 0) {
      throw StateError('Hiçbir bildirim planlanamadı: $lastError');
    }
  }

  @override
  Future<void> showTestNotification({
    required NotificationSoundMode soundMode,
    required NotificationDeliveryMode deliveryMode,
  }) async {
    if (!Platform.isAndroid) return;
    await initialize();
    await _plugin.show(
      id: stableNotificationId('mizan-test-${deliveryMode.name}'),
      title: deliveryMode == NotificationDeliveryMode.alarm
          ? 'MİZAN alarm testi'
          : 'MİZAN bildirim testi',
      body: 'Bildirim sistemi çalışıyor.',
      notificationDetails: _detailsFor(
        ReminderKind.payment,
        soundMode,
        deliveryMode,
      ),
      payload: 'test:${deliveryMode.name}',
    );
  }
}
"""
assert old_loop in s; s=s.replace(old_loop,new_loop,1)
p.write_text(s)
