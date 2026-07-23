from pathlib import Path
import re
root=Path.cwd()

p=root/'lib/screens/settings_screen.dart'; s=p.read_text()
needle="""                  OutlinedButton.icon(
                    onPressed: controller.isBusy
                        ? null
                        : controller.rescheduleNotifications,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Planlamayı yenile'),
                  ),
"""
if 'Alarm tipini test et' not in s:
    repl=needle+"""                  OutlinedButton.icon(
                    onPressed: controller.isBusy
                        ? null
                        : () => controller.showTestNotification(alarm: false),
                    icon: const Icon(Icons.notifications_active_outlined),
                    label: const Text('Normal bildirimi test et'),
                  ),
                  OutlinedButton.icon(
                    onPressed: controller.isBusy
                        ? null
                        : () => controller.showTestNotification(alarm: true),
                    icon: const Icon(Icons.alarm_on_outlined),
                    label: const Text('Alarm tipini test et'),
                  ),
"""
    assert needle in s; s=s.replace(needle,repl,1)
s=s.replace('                  subtitle: slot.message,', "                  subtitle: '${slot.deliveryMode.label} · ${slot.message}',",1)
s=s.replace('            subtitle: slot.message,', "            subtitle: '${slot.deliveryMode.label} · ${slot.message}',",1)
s=s.replace("""    var time = TimeOfDay(hour: slot.hour, minute: slot.minute);
    final message = TextEditingController(text: slot.message);
""","""    var time = TimeOfDay(hour: slot.hour, minute: slot.minute);
    var deliveryMode = slot.deliveryMode;
    final message = TextEditingController(text: slot.message);
""",1)
idx=s.index('Future<void> _editPaymentSlot')
pos=s.index('                    OutlinedButton.icon(',idx)
drop="""                    DropdownButtonFormField<NotificationDeliveryMode>(
                      initialValue: deliveryMode,
                      isExpanded: true,
                      decoration: const InputDecoration(
                        labelText: 'Hatırlatma tipi',
                      ),
                      items: [
                        for (final item in NotificationDeliveryMode.values)
                          DropdownMenuItem(
                            value: item,
                            child: Text(item.label),
                          ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setDialogState(() => deliveryMode = value);
                        }
                      },
                    ),
                    const SizedBox(height: 12),
"""
if 'NotificationDeliveryMode>' not in s[idx:s.index('Future<void> _editSlot',idx)]:
    s=s[:pos]+drop+s[pos:]
idx=s.index('updatePaymentNotificationSlot(',s.index('Future<void> _editPaymentSlot'))
pos=s.index('message: message.text,',idx)+len('message: message.text,')
if 'deliveryMode:' not in s[idx:s.index(');',pos)]:
    s=s[:pos]+"\n                    deliveryMode: deliveryMode,"+s[pos:]
idx=s.index('Future<void> _editSlot')
old="""    var time = TimeOfDay(hour: slot.hour, minute: slot.minute);
    final message = TextEditingController(text: slot.message);
"""
assert old in s[idx:]
s=s[:idx]+s[idx:].replace(old,"""    var time = TimeOfDay(hour: slot.hour, minute: slot.minute);
    var deliveryMode = slot.deliveryMode;
    final message = TextEditingController(text: slot.message);
""",1)
idx=s.index('Future<void> _editSlot')
pos=s.index('                      OutlinedButton.icon(',idx)
exp_drop=drop.replace('                    Dropdown','                      Dropdown').replace('\n                      initialValue','\n                        initialValue').replace('\n                      isExpanded','\n                        isExpanded').replace('\n                      decoration','\n                        decoration').replace('\n                        labelText', '\n                          labelText').replace('\n                      ),','\n                        ),').replace('\n                      items','\n                        items').replace('\n                        for', '\n                          for').replace('\n                          DropdownMenuItem', '\n                            DropdownMenuItem').replace('\n                            value', '\n                              value').replace('\n                            child', '\n                              child').replace('\n                          ),','\n                            ),').replace('\n                      ],','\n                        ],').replace('\n                      onChanged','\n                        onChanged').replace('\n                        if', '\n                          if').replace('\n                          setDialogState', '\n                            setDialogState').replace('\n                        }','\n                          }').replace('\n                      },','\n                        },').replace('\n                    ),','\n                      ),').replace('\n                    const SizedBox','\n                      const SizedBox')
if 'NotificationDeliveryMode>' not in s[idx:s.index('Future<void> _exportCsv',idx)]:
    s=s[:pos]+exp_drop+s[pos:]
idx=s.index('updateNotificationSlot(',s.index('Future<void> _editSlot'))
pos=s.index('message: message.text,',idx)+len('message: message.text,')
if 'deliveryMode:' not in s[idx:s.index(');',pos)]:
    s=s[:pos]+"\n                    deliveryMode: deliveryMode,"+s[pos:]
p.write_text(s)
