from pathlib import Path
root=Path.cwd()
# Controller
p=root/'lib/controllers/mizan_controller.dart'; s=p.read_text()
s=s.replace("""  Future<void> updatePaymentNotificationSlot({
    required String slotId,
    int? hour,
    int? minute,
    String? message,
    bool? enabled,
  }) async {
""","""  Future<void> updatePaymentNotificationSlot({
    required String slotId,
    int? hour,
    int? minute,
    String? message,
    bool? enabled,
    NotificationDeliveryMode? deliveryMode,
  }) async {
""",1)
s=s.replace("""                      message: cleanMessage,
                      enabled: enabled,
                    )
""","""                      message: cleanMessage,
                      enabled: enabled,
                      deliveryMode: deliveryMode,
                    )
""",1)
s=s.replace("""  Future<void> updateNotificationSlot({
    required String slotId,
    int? hour,
    int? minute,
    String? message,
    bool? enabled,
  }) async {
""","""  Future<void> updateNotificationSlot({
    required String slotId,
    int? hour,
    int? minute,
    String? message,
    bool? enabled,
    NotificationDeliveryMode? deliveryMode,
  }) async {
""",1)
idx=s.index('Future<void> updateNotificationSlot')
pos=s.index('message: cleanMessage,',idx)
insert=s.index('enabled: enabled,',pos)+len('enabled: enabled,')
s=s[:insert]+"\n                      deliveryMode: deliveryMode,"+s[insert:]
anchor='  Future<void> refreshNotificationHealth() async {'
method="""  Future<void> showTestNotification({required bool alarm}) async {
    _isBusy = true;
    notifyListeners();
    try {
      if (!_notificationHealth.permissionGranted) {
        _notificationHealth = await _scheduler.requestPermissions();
      }
      if (!_notificationHealth.permissionGranted) {
        throw StateError('Bildirim izni verilmedi.');
      }
      await _scheduler.showTestNotification(
        soundMode: _state.notificationSoundMode,
        deliveryMode: alarm
            ? NotificationDeliveryMode.alarm
            : NotificationDeliveryMode.standard,
      );
      _notificationHealth = await _scheduler.health();
      _lastError = null;
    } on Object catch (error) {
      _lastError = _friendlyError(error);
    } finally {
      _isBusy = false;
      notifyListeners();
    }
  }

"""
assert anchor in s; s=s.replace(anchor,method+anchor,1)
p.write_text(s)
