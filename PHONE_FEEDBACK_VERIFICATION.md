# MİZAN Telefon Geri Bildirimi Doğrulaması

Son başarılı GitHub Actions koşusu: **#85** (`29764457976`)

Doğrulanan commit: `685d130062941b185a50ed59055b5ac66e9e9314`

## Sonuçlar

- Flutter analyzer: **0 sorun**
- Yapısal şartname doğrulaması: **300 gereksinim geçti**
- Birim, model, controller, veri güvenliği, CSV, bildirim, widget ve responsive testleri: **53/53 geçti**
- Arayüz render senaryoları: **12 yeni senaryo dahil bütün görseller üretildi**
- Release APK: **başarıyla üretildi — 55.559.211 bayt**
- APK SHA-256: `c0ba1491c098df1ebc55ee122b00e69aec25176f21b5ffa37ddd9b58d5bed010`
- Doğrulanmış kaynak ZIP: başarıyla üretildi

## Telefon geri bildiriminden uygulanan düzeltmeler

- Kişiyi düzenle ve sil işlemleri ana karttan kaldırılarak **Kişi detayları** alanına taşındı.
- Kişi detaylarında beş kayıt grubunun toplamları ve kişiye bağlı bütün açık kayıtlar gösteriliyor.
- Giderler ve raporlar ekranlarındaki fiziksel cihazda görülen büyük gri bloklara neden olan iç içe Material/açılır yapı kaldırıldı.
- Banka borcunda ödeme tarihi yöntemi **Son ödeme tarihi** veya **Her ayın belirli günü** olarak seçilebilir hale getirildi.
- Eski kayıtlar veri kaybı olmadan sabit tarih yöntemiyle taşınıyor.
- Raporlarda seçili ayda gerçekleşen ödemeler beş kayıt türüne göre ayrı toplamlanıyor:
  - Banka borçları
  - Kişisel ve kurumsal borçlar
  - Faturalar
  - Abonelikler
  - Kira ve taksitler
- Giderler borç ödemelerine karıştırılmadan ayrı gösteriliyor.
- **Bu ay gerçekleşen toplam ödeme-gider raporu**, gerçekleşen ödemeler ile Giderler modülünü birleştiriyor.
- **Önümüzdeki 7 gün** hesabı toplam kalan borcu değil, ilgili dönemde gerçekten ödenecek taksit/vade tutarını kullanıyor.
- Aynı dönem tutarı ana sayfa kritik ödemeler ve rapor kayıtlarında da kullanılıyor.

PR fiziksel Android cihazdaki son kullanıcı kontrolü tamamlanana kadar taslak tutulmaktadır.
