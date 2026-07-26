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
    path = root / "lib/screens/settings_screen.dart"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        """    required this.ready,
    this.neutral = false,
  });""",
        """    required this.ready,
  });""",
        "Bildirim sistem durumu kurucusu",
    )
    text = replace_once(
        text,
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
    path.write_text(text, encoding="utf-8")
    if "this.neutral" in path.read_text(encoding="utf-8"):
        raise SystemExit("Kullanılmayan neutral parametresi kaldı.")
    print("Bildirim ayarları kullanılmayan parametre uyarısı giderildi.")


if __name__ == "__main__":
    main()
