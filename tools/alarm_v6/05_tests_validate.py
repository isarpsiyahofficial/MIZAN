from pathlib import Path
import re
root=Path.cwd()
p=root/'test/test_support.dart'; s=p.read_text()
if 'showTestNotification' not in s:
    needle="""  @override
  Future<void> reschedule(MizanState state) async {
    rescheduleCount++;
    lastScheduledState = MizanState.fromJson(state.toJson());
  }
}
"""
    repl="""  @override
  Future<void> reschedule(MizanState state) async {
    rescheduleCount++;
    lastScheduledState = MizanState.fromJson(state.toJson());
  }

  @override
  Future<void> showTestNotification({
    required NotificationSoundMode soundMode,
    required NotificationDeliveryMode deliveryMode,
  }) async {}
}
"""
    assert needle in s; s=s.replace(needle,repl,1)
p.write_text(s)
p=root/'test/reminder_engine_test.dart'; s=p.read_text()
if 'alarm tipi ödeme ve gider slotları' not in s:
    insert="""

  test('alarm tipi ödeme ve gider slotları plana taşınır', () {
    final state = comprehensiveState(reference: DateTime(2026, 7, 19, 8)).copyWith(
      notificationSlots: const [
        NotificationSlot(
          id: 'expense-alarm',
          label: 'Gider alarmı',
          hour: 9,
          minute: 0,
          message: 'Giderleri kontrol et',
          deliveryMode: NotificationDeliveryMode.alarm,
        ),
      ],
      paymentNotificationSlots: const [
        NotificationSlot(
          id: 'payment-alarm',
          label: 'Ödeme alarmı',
          hour: 10,
          minute: 0,
          message: 'Ödemeleri kontrol et',
          deliveryMode: NotificationDeliveryMode.alarm,
        ),
      ],
    );
    final plan = const ReminderPlanBuilder().build(
      state: state,
      now: DateTime(2026, 7, 19, 8),
    );
    expect(plan, isNotEmpty);
    expect(
      plan.where((item) => item.deliveryMode == NotificationDeliveryMode.alarm),
      isNotEmpty,
    );
  });

  test('plan ödeme bildirimlerini cihaz alarm sınırının altında tutar', () {
    final state = comprehensiveState(reference: DateTime(2026, 7, 19, 8)).copyWith(
      paymentNotificationSlots: List.generate(
        10,
        (index) => NotificationSlot(
          id: 'slot-$index',
          label: 'Saat $index',
          hour: index,
          minute: 0,
          message: 'Kontrol et',
        ),
      ),
    );
    final plan = const ReminderPlanBuilder().build(
      state: state,
      now: DateTime(2026, 7, 19, 8),
    );
    expect(
      plan.where((item) => item.kind == ReminderKind.payment).length,
      lessThanOrEqualTo(450),
    );
  });
"""
    pos=s.rfind('}'); s=s[:pos]+insert+s[pos:]
p.write_text(s)
p=root/'test/model_test.dart'; s=p.read_text()
if 'alarm tipi bildirim ayarı JSON' not in s:
    insert="""

  test('alarm tipi bildirim ayarı JSON dönüşümünde korunur', () {
    const slot = NotificationSlot(
      id: 'alarm',
      label: 'Kritik ödeme',
      hour: 8,
      minute: 15,
      message: 'Ödemeyi kontrol et',
      deliveryMode: NotificationDeliveryMode.alarm,
    );
    final restored = NotificationSlot.fromJson(slot.toJson());
    expect(restored.deliveryMode, NotificationDeliveryMode.alarm);
  });
"""
    pos=s.rfind('}'); s=s[:pos]+insert+s[pos:]
p.write_text(s)
p=root/'docs/REQUIREMENTS_250_PLUS.md'; s=p.read_text()
if 'Alarm tipi hatırlatma yüksek önem' not in s:
    nums=[int(x) for x in re.findall(r'^(\d+)\.',s,re.M)]
    n=max(nums)+1
    items=['Normal bildirim ve alarm tipi hatırlatmalar ayrı seçilebilmelidir.','Alarm tipi hatırlatma yüksek önem, alarm ses kullanımı ve titreşimle oluşturulmalıdır.','Bildirim sesi sistem, yumuşak, belirgin veya sessiz olarak seçilebilmelidir.','Normal bildirim ve alarm tipi bildirim uygulama içinden anında test edilebilmelidir.','Bildirim planlamasında tek bir kayıt hatası diğer bildirimlerin kurulmasını durdurmamalıdır.','Planlanan ödeme bildirimleri Android cihaz alarm sınırının altında tutulmalıdır.','Cihaz yeniden başlatıldığında planlanmış bildirimler boot receiver ile korunmalıdır.']
    s+='\n'+''.join(f'{n+i}. {v}\n' for i,v in enumerate(items))
p.write_text(s)
p=root/'tools/validate_project.py'; s=p.read_text()
s=s.replace('currentSchemaVersion = 7','currentSchemaVersion = 8')
if 'NotificationDeliveryMode.alarm' not in s:
    s=s.replace('"TZDateTime",', '"TZDateTime", "NotificationDeliveryMode.alarm", "AudioAttributesUsage.alarm", "showTestNotification",')
if 'Alarm tipini test et' not in s:
    s=s.replace('"Bildirim sesi",', '"Bildirim sesi", "Normal bildirimi test et", "Alarm tipini test et",')
p.write_text(s)
