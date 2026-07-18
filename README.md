# LEFFERION PRIME - MIZAN

Mizan, kişi bazlı borç, fatura, kira, taksit ve gider takibi için hazırlanan Flutter APK projesidir.

## Temel hedef

- Banka marka adı veya banka logosu hazır gelmez; banka adını kullanıcı kendisi yazar.
- Veriler cihaz içinde local saklanır.
- Uygulama telefon, tablet, yatay ve dikey ekranda taşmasız çalışacak şekilde kart tabanlı tasarlanır.
- Ödeme geçmişi, bildirim ve hesaplamalar kaynak kayda bağlı kalır.
- Giderler kullanıcı tanımlı kategorilerle tutulur; kategori detayında o kategoriye ait harcamalar görünür.

## Batch akışı

1. Veri modeli, local kayıt ve hesaplama motoru.
2. Responsive ekranlar ve kullanıcı akışları.
3. Bildirim motoru, raporlar, arama ve filtreleme.
4. Android build, GitHub Actions ve APK çıktısı.

## GitHub Actions APK

Workflow `.github/workflows/android-release.yml` içinde Flutter SDK kurar, Android platform dosyalarını üretir, launcher iconları hazırlar, testleri çalıştırır ve imzasız release APK üretir.

Kaynak bütünlüğü ve CI doğrulaması 18 Temmuz 2026 tarihinde yeniden başlatıldı.

Son doğrulama; sıfır analyzer sorunu, 260 maddelik yapısal kontrol, 25 birim ve etkileşim testi, dar ekran taşma kontrolleri ve release APK üretimini birlikte zorunlu tutar. Başarılı sonuçtan sonra doğrulanmış normal Flutter kaynakları PR dalına fast-forward commit olarak yazılır.
