# GÖRSEL KONTROL (göz testi) — her videoda, render ÖNCESİ

Sen görselleri görebiliyorsun. `--onizleme` ile üretilen `out/VID_xxx_<tur>_onizleme.jpg` dosyasına BAK ve aşağıdaki
listeyi puanla. Her madde 0 (kötü) / 1 (idare eder) / 2 (iyi). Toplam 16 üzerinden **13 altıysa** plan JSON'unu düzelt
ve önizlemeyi BİR KEZ daha al. Sonra render'a geç. (Kendini sonsuz düzeltme döngüsüne sokma.)

## Uzun video (gerçekçi ekran kaydı — varsayılan stil)
| # | Soru | Nasıl düzeltilir (plan JSON) |
|---|---|---|
| 1 | Doğru kurumun portalı mı görünüyor? (e-Devlet, banka, CİMER…) | sahnenin `"theme"` alanını değiştir |
| 2 | Arama kutusuna yazılan hizmet adı metinle aynı mı? | `actions` içindeki `{"do":"search","text":...}` |
| 3 | Sonuç tablosundaki satırlar anlamlı mı? (cümle parçası değil, kayıt adı) | `{"do":"result","rows":[["Kayıt adı","Tutar/Durum"],...]}` |
| 4 | Form alanlarının etiketleri doğru mu? (IBAN, T.C. Kimlik, Açıklama…) | `{"do":"field","label":...}` |
| 5 | Metinde "uygulama/telefondan" geçiyorsa telefon ekranı mı kullanılmış? | `"device": "mobile"` |
| 6 | Bilgi notu kartlarındaki cümleler kısa ve anlamlı mı? (yarım kelime yok) | ilgili `card` sahnesinin `cards[i].title` alanı |
| 7 | Adım etiketleri ("ADIM 2/4 · …") doğru ve okunaklı mı? | `"chapter": ["ADIM 2/4", "Kısa başlık"]` |
| 8 | Hiçbir karede taşan / üst üste binen yazı yok mu? | başlığı kısalt (≤ 30 karakter) |

## Shorts
| # | Soru | Düzeltme |
|---|---|---|
| 1 | İlk karede güçlü bir soru/şok başlığı var mı? | ilk beat `title` |
| 2 | Başlık iki satırı anlamlı mı? (kelime ortasından kesilmemiş) | `title: ["SİYAH SATIR", "KIRMIZI SATIR"]` (her biri ≤ 18 karakter) |
| 3 | Her sahnede en az bir hareketli öğe var mı? (ikon, etiket, mühür, sayaç) | `chips`, `stamp`, `icon` ekle |
| 4 | Yorum sahnesinde doğru kelime mi yazılıyor? | comment beat `word` |
| 5 | Maskot ifadesi cümlenin duygusuna uyuyor mu? | `mascot` |
| 6 | Ekranda yazım hatası / anlamsız ifade yok mu? | ilgili `title`/`chips` |
| 7 | Görsel her 2–3 sn'de değişiyor mu? | uzun beat'i ikiye böl (aynı `sentence`'ı iki parçaya ayır) |
| 8 | Renkler ve stil hedef görsellerle (`docs__elektrik_kareler.jpg`) uyumlu mu? | — |

## Render sonrası (otomatik)
`engine/qc.py` raporu GEÇTİ olmalı. Ayrıca `_kareler.jpg` dosyasına bir kez bak: siyah/boş kare, bozuk yazı var mı?

## Kesin yasaklar (görürsen düzelt)
- "T.C." başlığı, gerçek kurum logosu, gerçek alan adı (…gov.tr) → YASAK
- Maskelenmemiş kişisel veri (gerçek isim, TC, IBAN) → YASAK

## Görsel zayıfsa ne yaparım?
Çizim kodu YAZMA. Plan JSON'unda sadece ikon/şablon adını değiştir (bkz. `docs__ikon_kutuphanesi.jpg`, `docs__sablon_katalogu.jpg`).
Örn. araba konusu ama ikon "onay" → `"icon": "araba"`; tutar geçen cümle "not" ise → `"sablon": "sayac"`.
