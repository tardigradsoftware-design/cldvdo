# cldvdo — Kodla Video Motoru

Python (Pillow + numpy) ile kare kare çizim → ffmpeg ile MP4. Telifsiz sentez müzik + SFX, −14 LUFS.

## Yapı
- `engine/core.py` — easing, sprite önbelleği, animasyon, çok çekirdekli render
- `engine/components.py` — maskot, karaoke altyazı, imleç, tuş görselleştirici, ikonlar
- `engine/audio.py` — müzik yatağı, SFX sentezi, miks + loudnorm
- `engine/shorts.py` — dikey (9:16) şablon
- `engine/tutorial.py` — yatay (16:9) adım adım anlatım şablonu (tarayıcı, kamera zoom)
- `projects/<senaryo>/` — senaryo + sahne görselleri

## Çalıştırma
```bash
OUT_DIR=out python3 projects/hat_sorgulama/short.py      # dikey
OUT_DIR=out python3 projects/hat_sorgulama/tutorial.py   # yatay
python3 projects/hat_sorgulama/short.py preview          # hızlı kare önizleme
```
