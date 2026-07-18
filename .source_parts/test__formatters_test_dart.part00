import 'package:flutter_test/flutter_test.dart';
import 'package:lefferion_prime_mizan/core/formatters.dart';

void main() {
  group('para biçimi', () {
    test('Türkçe ve uluslararası girişleri güvenli çözümler', () {
      expect(parseMoney('1.234,56 TL'), 1234.56);
      expect(parseMoney('1.000,50'), 1000.50);
      expect(parseMoney('1,234.56'), 1234.56);
      expect(parseMoney('100,50'), 100.50);
      expect(parseMoney('100.50'), 100.50);
      expect(parseMoney('10.050'), 10050);
    });

    test('kuruş kaybetmeden gösterir', () {
      expect(money(1234.5), '1.234,50 TL');
      expect(money(0), '0,00 TL');
    });

    test('geçersiz tutarı reddeder', () {
      expect(() => parseMoney('abc'), throwsFormatException);
      expect(() => parseMoney('12,3456'), throwsFormatException);
    });
  });
}
