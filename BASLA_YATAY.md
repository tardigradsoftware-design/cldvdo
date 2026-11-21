# BAŞLA — YATAY ADIM ADIM ANLATIM VİDEOSU (örnek: Hastane acil servis ücreti iadesi)

Bu paket, bir TTS metnini **bilgisayar ekranında gösteriyormuş gibi** yatay (16:9) videoya dönüştürmeyi öğretir:
sanal tarayıcı + sanal e-Devlet/CİMER/e-Nabız ekranları + mouse hareketi + tıklama halkası + klavyeyle yazma + tuş göstergesi
+ kamera yakınlaşması + kelime kelime altyazı + maskot (Tokmak). Arka plan müziği YOK.

## Dosya adları
Bu klasör düzdür. Dosya adındaki `__` klasör ayracıdır: `engine__core.py` = `engine/core.py`,
`projects__hastane__tutorial.py` = `projects/hastane/tutorial.py`. Çalıştırmak için bu yollarla klasör yapısını kur.
(TUM_PAKET_YATAY.txt aynı dosyaların hepsini tek metinde, gerçek yollarıyla içerir.)

## Okuma sırası
1. **AJAN-REHBERI.md** → genel kurallar, stil, kalite kontrol.
2. **docs__hastane_kareler.jpg** → HEDEF GÖRÜNÜM: örnek videodan her 3 saniyede bir kare (soldan sağa, yukarıdan aşağı).
3. **projects__hastane__tutorial.py** → bu videonun KODU (asıl örnek). İncele:
   - `CAP_*` listeleri: TTS metni cümle cümle altyazıya bölünmüş (*VURGU* yıldızla).
   - `ctimes()` + `dur_for()`: segment süresi kelime sayısından hesaplanır; görsel olaylar ilgili cümlenin başladığı ana kilitlenir.
   - `seg_s2` → telefonda uygulama (e-Nabız) gezintisi; `seg_s3` → e-Devlet arama + CİMER formu doldurma;
     `seg_s4` → telefonda numara tuşlama; `seg_s5` → e-Devlet Tüketici Hakem Heyeti formu.
   - Her segment `{"cam": kamera, "keys": tuşlar, "mascot": ifade}` döndürür.
4. **projects__elektrik__tutorial.py** → ortak ekran parçaları (form alanı, dosya yükleme satırı, başarı penceresi, e-Devlet
   başlığı/arama, Hakem Heyeti formu, telefon tuş takımı, banka bildirimi). Hastane kodu bunları `el.` ile kullanır.
5. **engine__tutorial.py** → yatay şablon: tarayıcı penceresi, kamera, bölüm etiketi (ADIM n/N), tuş göstergesi, altyazı.
6. **engine__core.py / engine__components.py / engine__audio.py / engine__voice.py** → motor.
7. **maskot__tokmak_maskot.py** → maskot (ifade:poz, ör. "ciddi:isaret").

## Çalıştırma
```bash
pip install pillow numpy   # + ffmpeg
OUT_DIR=out python3 projects/hastane/tutorial.py preview   # kare önizleme
OUT_DIR=out python3 projects/hastane/tutorial.py           # tam render (~2.5 dk video)
```

## Yeni yatay video üretme
1. TTS metnini adımlara böl → her bölüm bir `CAP_` listesi (cümleler/yan cümleler).
2. Metinde geçen her ekran için sanal sayfa çiz (`page_xxx(...)` + `@lru_cache`), stilize: gerçek logo/birebir tasarım YOK.
3. Mouse yolunu `path(t, [(zaman, x, y), ...])`, tıklamaları `draw_cursor(..., click_times)`, yazmayı `typing()` ile kur.
4. Kamerayı işlem yapılan alana yakınlaştır (1.3–1.5x), işlem bitince 1.0'a dön.
5. Önizle → düzelt → render → QC (ffprobe, -14/-16 LUFS, kare tabakası).
