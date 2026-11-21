# BAŞLA — Video Kurgu Ajanı Paketi

Bu paket, kodla dikey/yatay sosyal medya videosu üretmeyi öğretir.

## Okuma sırası
1. **AJAN-REHBERI.md** → kurallar, stil, zamanlama, kalite kontrol (önce bunu oku).
2. **docs/elektrik_kareler.jpg** → hedef görünüm: örnek videonun saniye saniye kareleri (soldan sağa, yukarıdan aşağı).
3. **projects/elektrik/short.py** → aynı videonun KODU. Bir TTS metninin sahnelere nasıl bölündüğünü, her cümlenin hangi görsele çevrildiğini gösterir. Yeni videolar bu dosya şablon alınarak yazılır.
4. **maskot/tokmak_maskot.py** → kanal maskotu (12 ifade × 4 poz).
5. **engine/** → motor (core, components, shorts, tutorial, audio, voice).

## Kurulum ve çalıştırma
```bash
pip install pillow numpy        # + sistemde ffmpeg
OUT_DIR=out python3 projects/elektrik/short.py preview   # hızlı kare önizleme
OUT_DIR=out python3 projects/elektrik/short.py           # tam render -> out/elektrik_dikey.mp4
VOICE=ses.mp3 OUT_DIR=out python3 projects/<konu>/short.py   # seslendirmeli (bölümler arası ~1 sn sessizlik)
```

## Yeni video üretme
`projects/elektrik/` klasörünü kopyala → `build()` içindeki Beat listesini yeni metne göre yeniden yaz
(her cümle = 1 Beat: başlık 2 satır, altyazı *vurgulu*, görsel fonksiyonu, maskot ifadesi, efektler).
Arka plan müziği kullanılmaz.
