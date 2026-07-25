from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanım: fix_expense_card_trailing_overflow.py <source-root>")
    root = Path(sys.argv[1]).resolve()
    path = root / "lib/screens/expenses_screen.dart"
    text = path.read_text(encoding="utf-8")
    old = """    trailing: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          money(item.totalAmount),
          style: const TextStyle(fontWeight: FontWeight.w900),
        ),
        PopupMenuButton<String>(
          onSelected: (value) => value == 'edit' ? onEdit() : onDelete(),
          itemBuilder: (_) => const [
            PopupMenuItem(value: 'edit', child: Text('Düzenle')),
            PopupMenuItem(value: 'delete', child: Text('Sil')),
          ],
        ),
      ],
    ),"""
    new = """    trailing: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 132),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Flexible(
            child: Text(
              money(item.totalAmount),
              textAlign: TextAlign.right,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontWeight: FontWeight.w900),
            ),
          ),
          const SizedBox(width: 2),
          PopupMenuButton<String>(
            tooltip: 'Gider işlemleri',
            onSelected: (value) => value == 'edit' ? onEdit() : onDelete(),
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'edit', child: Text('Düzenle')),
              PopupMenuItem(value: 'delete', child: Text('Sil')),
            ],
          ),
        ],
      ),
    ),"""
    if old not in text:
        raise SystemExit("Gider kartı tutar ve işlem alanı bulunamadı.")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    verified = path.read_text(encoding="utf-8")
    for token in (
        "BoxConstraints(maxWidth: 132)",
        "tooltip: 'Gider işlemleri'",
        "overflow: TextOverflow.ellipsis",
    ):
        if token not in verified:
            raise SystemExit(f"Gider kartı taşma koruması eksik: {token}")
    print("Gider kartı tutar ve işlem alanı dar ekranlarda taşmayacak biçimde sınırlandı.")


if __name__ == "__main__":
    main()
