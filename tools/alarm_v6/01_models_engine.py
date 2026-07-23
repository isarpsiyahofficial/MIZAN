from pathlib import Path
import re, wave, math, struct
root=Path.cwd()

# Sound resources
raw=root/'android/app/src/main/res/raw'; raw.mkdir(parents=True,exist_ok=True)
def write_tone(path, notes, volume):
    rate=44100; frames=[]
    for frequency, duration in notes:
        count=int(rate*duration)
        for i in range(count):
            envelope=max(0.0,min(1.0,i/(rate*.015),(count-i)/(rate*.04)))
            frames.append(struct.pack('<h',int(32767*volume*envelope*math.sin(2*math.pi*frequency*i/rate))))
    with wave.open(str(path),'wb') as output:
        output.setnchannels(1); output.setsampwidth(2); output.setframerate(rate); output.writeframes(b''.join(frames))
write_tone(raw/'mizan_soft.wav',[(659.25,.18),(783.99,.22)],.20)
write_tone(raw/'mizan_alert.wav',[(880,.18),(.01,.06),(880,.18),(1046.5,.25)],.55)

# Models
p=root/'lib/models/mizan_models.dart'; s=p.read_text()
s=s.replace('const int currentSchemaVersion = 7;', 'const int currentSchemaVersion = 8;',1)
old="""enum NotificationSoundMode {
  system('Cihazın varsayılan sesi'),
  silent('Sessiz');

  const NotificationSoundMode(this.label);
  final String label;
}
"""
new="""enum NotificationSoundMode {
  system('Cihazın varsayılan sesi'),
  soft('Yumuşak MİZAN sesi'),
  alert('Belirgin MİZAN sesi'),
  silent('Sessiz');

  const NotificationSoundMode(this.label);
  final String label;
}

enum NotificationDeliveryMode {
  standard('Normal bildirim'),
  alarm('Alarm tipi hatırlatma');

  const NotificationDeliveryMode(this.label);
  final String label;
}
"""
assert old in s; s=s.replace(old,new,1)
s=s.replace("""    required this.message,
    this.enabled = true,
  });
""","""    required this.message,
    this.enabled = true,
    this.deliveryMode = NotificationDeliveryMode.standard,
  });
""",1)
s=s.replace("""  final String message;
  final bool enabled;

  NotificationSlot copyWith({
""","""  final String message;
  final bool enabled;
  final NotificationDeliveryMode deliveryMode;

  NotificationSlot copyWith({
""",1)
s=s.replace("""    String? message,
    bool? enabled,
  }) {
""","""    String? message,
    bool? enabled,
    NotificationDeliveryMode? deliveryMode,
  }) {
""",1)
s=s.replace("""      message: message ?? this.message,
      enabled: enabled ?? this.enabled,
    );
""","""      message: message ?? this.message,
      enabled: enabled ?? this.enabled,
      deliveryMode: deliveryMode ?? this.deliveryMode,
    );
""",1)
s=s.replace("""    'message': message,
    'enabled': enabled,
  };
""","""    'message': message,
    'enabled': enabled,
    'deliveryMode': deliveryMode.name,
  };
""",1)
s=s.replace("""      message: _string(json['message']),
      enabled: json['enabled'] as bool? ?? true,
    );
""","""      message: _string(json['message']),
      enabled: json['enabled'] as bool? ?? true,
      deliveryMode: NotificationDeliveryMode.values.firstWhere(
        (item) => item.name == _string(json['deliveryMode']),
        orElse: () => NotificationDeliveryMode.standard,
      ),
    );
""",1)
p.write_text(s)

# Reminder engine
p=root/'lib/services/reminder_engine.dart'; s=p.read_text()
s=s.replace("""    this.repeatsDaily = false,
  });
""","""    this.repeatsDaily = false,
    this.deliveryMode = NotificationDeliveryMode.standard,
  });
""",1)
s=s.replace("""  final bool repeatsDaily;
}
""","""  final bool repeatsDaily;
  final NotificationDeliveryMode deliveryMode;
}
""",1)
s=s.replace("""            repeatsDaily: true,
          ),
""","""            repeatsDaily: true,
            deliveryMode: slot.deliveryMode,
          ),
""",1)
s=s.replace("""              scheduledAt: scheduledAt,
            ),
""","""              scheduledAt: scheduledAt,
              deliveryMode: slot.deliveryMode,
            ),
""",1)
p.write_text(s)
