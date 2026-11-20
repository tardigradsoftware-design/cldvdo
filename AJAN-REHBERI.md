# 🎬 VİDEO ÜRETİM AJANI — TAM DEVİR REHBERİ

> Bu belge, "kodla video üretim" sisteminin **nasıl düşündüğünü, hangi araçları kullandığını ve adım adım nasıl ürettiğini** anlatır. Bunu alan ajan aynı kaliteyle ve aynı mantıkla üretebilmelidir.
> Kod: GitHub `tardigradsoftware-design/cldvdo`, dal `ccr-411bd5c8-aqf2b8`

---

## 0. TEMEL FELSEFE

1. **Video bir montaj programında değil, KODLA üretilir.** Her kare Python ile çizilir ve ffmpeg ile MP4'e dönüştürülür. Zaman çizelgeli bir montaj programı, stok görüntü veya AI video modeli kullanılmaz.
2. **Her şey vektör tarzı ve düz tasarım:** kartlar, ikonlar, maskot ve UI taklitleri kodla çizilir. Dışarıdan görsel gerekmez, bu yüzden tutarlılık %100 olur ve telif sorunu çıkmaz.
3. **Önce ÖNİZLEME, sonra RENDER.** Kareler önce düşük çözünürlükte bir temas sayfasına (kontak tabaka) dökülüp gözle kontrol edilir: taşma, çakışma ve okunabilirlik burada yakalanır. Ancak sonra tam render alınır.
4. **İzleyici tutma (retention) mühendisliği:** her saniye bir şey olmalı. İlk kare güçlü olmalı, sonda kesin bir çağrı (CTA) olmalı.
5. **Bilgi doğruluğu:** hukuki ve resmî işlemlerde yalnızca emin olunan bilgi yazılır. Gerçek kişi verisi gösterilmez; örnek veriler maskelenir (A**** Y*****, 1•••••••••8).

---

## 1. KULLANILAN ARAÇLAR / ORTAM

| Araç | Ne için |
|---|---|
| **Python 3** | Tüm motor |
| **Pillow (PIL)** | Kare kare çizim: metin, şekil, kart, maskot, UI |
| **numpy** | Arka plan vinyeti, **müzik ve ses efekti sentezi** |
| **ffmpeg / ffprobe** | Encode (H.264), ses miks, loudnorm, kalite kontrol, kare çıkarma |
| **multiprocessing (fork)** | Kareleri 4 çekirdekte paralel çizme |
| **Fontlar** | Inter Display Black/ExtraBold (başlıklar), Inter Bold/SemiBold (gövde), DejaVu Sans Mono (kod). Türkçe karakter desteği tam. |
| **Google Drive bağlayıcısı** | Referans videoları indirme, çıktıları yükleme |
| **Git/GitHub** | Kodu saklama |

**Ortam gerçekleri (bu oturumda öğrenilenler):**
- Dışarıya erişim kısıtlı: GitHub raw, HuggingFace ve Microsoft TTS kapalı. Font ve ses modeli indirilemiyor, bu yüzden her şey yerelde sentezleniyor.
- **Bu ortamda TTS yok.** Seslendirme dışarıda üretilip dosya olarak veriliyor.
- **Drive yükleme sınırı: dosya başına yaklaşık 3,1 MB.** Daha büyük videolar 2 geçişli encode ile küçültülüyor (aşağıda).
- Makine: 4 çekirdek ve 16 GB RAM. 37 sn dikey video yaklaşık 25 sn'de, 75 sn yatay video yaklaşık 60 sn'de render oluyor.

---

## 2. MİMARİ (dosya yapısı)

```
engine/
  core.py        → renkler, fontlar, easing, sprite önbelleği, place/place_anim, kamera zoom, render()
  components.py  → maskot, karaoke altyazı, imleç, klavye tuşu, ikonlar (✓ ✗ ⚠), SIM kart, mühür
  audio.py       → müzik yatağı (sentez), SFX sentezi, miks, ducking, -14 LUFS
  shorts.py      → DİKEY şablon (Beat listesi → video)
  tutorial.py    → YATAY şablon (Seg listesi + tarayıcı simülasyonu + kamera)
projects/<konu>/
  short.py       → o konunun dikey senaryosu + sahne görselleri
  tutorial.py    → o konunun yatay senaryosu + sayfa taklitleri
```

### Render hattı
```
senaryo (Beat/Seg listesi)
  → olay listesi (SFX zamanları) → audio.mix() → WAV (-14 LUFS)
  → frame(t) fonksiyonu → Pillow RGBA kare → rgb24 raw → ffmpeg stdin
  → libx264 CRF19, yuv420p, high profile, +faststart, AAC 192k 48kHz → MP4
```

### Performansın sırrı: SPRITE ÖNBELLEĞİ
- Her görsel öğe (kart, yazı, pill, maskot ifadesi) **bir kez** çizilir ve `@lru_cache` ile saklanır.
- Karede yalnızca **dönüşüm** uygulanır: ölçek, döndürme, saydamlık, konum.
- Değişen içerikler (daktilo yazısı, sayaç) **duruma göre** önbelleğe alınır, örneğin `search_card(typed="mobil h", focus=True)`.
- **Süper örnekleme:** sprite 2 kat boyutta çizilip LANCZOS ile küçültülür, böylece kenarlar pürüzsüz olur.

---

## 3. GÖRSEL STİL KİTABI (referans videolardan çıkarıldı)

| Öğe | Kural |
|---|---|
| Zemin | Açık gri, ortası açık ve kenarları koyu radyal vinyet (#FAFAFA → #DEDEDE) |
| Renkler | Mürekkep #111, Kırmızı #E8342E (ana vurgu), Yeşil #18A058 (olumlu/✓), Mavi #265CE6, Sarı #FFCC29 (uyarı) |
| Başlık | Sol üstte 2 satır. 1. satır siyah (92px), 2. satır **kırmızı ve daha büyük** (112px). Sığmazsa otomatik küçülür. |
| Kartlar | **5px kalın siyah çerçeve + sağ alta 10px sert siyah gölge** + 18px köşe yuvarlaklığı. Renkli başlık şeridi opsiyonel. |
| Pill / etiket | Tam yuvarlak, beyaz veya kırmızı zemin. Önemli olanlar gölgeli. |
| Mühür (stamp) | Eğik (-12°…+8°), kalın çerçeveli, büyükten küçülerek "basılır" |
| Altyazı | Kelime kelime: **aktif kelime kırmızı pill**, geçmiş kelimeler beyaz pill ve siyah yazı, gelecek kelimeler soluk gri. Grup başına en fazla 3-4 kelime. |
| Maskot | Kırmızı robot, siyah ekran yüzlü, sarı antenli, göğsünde yeşil tikli kalkan rozeti. İfadeler: normal / happy / shock / angry / wink. Nefes alır, 3 sn'de bir göz kırpar, sahne başında zıplar. |
| İlerleme | En üstte ince kırmızı çubuk (dikeyde 12px, yatayda 8px) |
| Sayaç | Dikeyde üstte sabit pill (ör. "ADINA KAYITLI HAT [?]" → sonradan "[3]"). Merak döngüsü yaratır. |

**Yerleşim, dikey (1080×1920):** sayaç y=120 · başlık y=250 · görsel merkezi y=900 · altyazı y=1365 · maskot y=1610. Alt 300px'te platform arayüzü olduğu için orası boş bırakılır.
**Yerleşim, yatay (1920×1080):** bölüm pill'i sol üstte y=58 · tarayıcı penceresi (80,118, 1760×812) · tuş görselleştirici sol altta y=905 · altyazı y=1012 · maskot sağ altta.

---

## 4. HAREKET DİLİ

| Animasyon | Kullanım |
|---|---|
| `pop` | Ölçek 0 → 1.1 → 1 (out_back). Kartlar ve ikonlar için. |
| `left` / `right` | Yandan kayarak gelir. Başlık 1. satır için. |
| `up` | Aşağıdan yukarı. Listeler ve UI kartları için. |
| `drop` | Yukarıdan düşer ve döner. Belge ve SIM kart için. |
| `stamp` | 2.2 katından 1'e iner. Mühürler için. |
| Çıkış | Her öğe sahnenin son 0,18 sn'sinde küçülerek kaybolur. |
| Punch zoom | Açılış sahnesinde kare 1.06 katından 1'e iner + sarsıntı. |
| Gecikmeli giriş | Öğeler 0,1–0,45 sn arayla tek tek gelir. Ekran asla bir anda dolmaz. |
| Daktilo | Yazı karakter karakter yazılır (11–13 karakter/sn) ve imleç yanıp söner. |
| Sayaç | Rakamlar 0'dan hedefe out_cubic ile artar (ör. 48.750 TL). |
| İmleç | Kolay hareket (in_out_cubic) eden ok. Tıklamada küçülür ve kırmızı halka yayılır. |
| Kamera (yatay) | İşlem yapılan alana 1.3–1.7 kat yakınlaşır, işlem bitince 1.0'a döner. Tablo gibi geniş alanlarda en fazla 1.12 (kenarlar kesilmesin). |

Easing fonksiyonları: `out_cubic`, `in_out_cubic`, `out_back(s=2.2)`, `in_cubic`.

---

## 5. SES TASARIMI (dışarıdan dosya kullanılmaz, hepsi sentez)

**Müzik yatağı (numpy):** 104 BPM. Akorlar C–G–Am–F; pad + 8'lik pluck arpej + bas + kick (1-3) + clap (2-4) + hi-hat 8'lik. Başta 0,3 sn fade-in, sonda 1,2 sn fade-out. Telifsiz, çünkü tamamen sentez.

**SFX (numpy):**
| SFX | Ne zaman |
|---|---|
| `whoosh` | Her sahne geçişinde (0,08 sn önce) |
| `pop` | Öğe girişi |
| `tick` | Altyazıda her kelime (kısık) |
| `impact` | Açılış, şok anı, mühür |
| `ding` | Olumlu bilgi, liste maddesi, bildirim |
| `error` | Tehlike veya kötü haber |
| `key` | Her klavye vuruşu (rastgele tonlu) |
| `click` | Mouse tıklaması |
| `riser` | Gerilim yükseltme |

**Miks:** müzik ×0,45–0,55 · SFX kazanç tablosu (ör. impact 0,6, tick 0,25) · `tanh` yumuşak limit · ffmpeg `loudnorm=I=-14:TP=-1.5:LRA=11`.
**Seslendirme gelince:** sahne süreleri ses klibinin süresine göre ayarlanır (klip + 0,2–0,4 sn). Konuşma sırasında müzik ×0,35'e kısılır (ducking).

---

## 6. VİDEO TÜRLERİ VE SENARYO KURALLARI

### A) DİKEY KISA VİDEO (Shorts/Reels/TikTok), 30–45 sn, 11–13 sahne
Her sahne 2,4–4,2 sn sürer. Yapı:
1. **Hook (0–2,6 sn):** soru veya şok ("ADINA GİZLİ HAT VAR MI?"). İlk karede başlık, görsel ve altyazı **görünür** olmalı; boş kare olmaz. Punch zoom + impact.
2. **Problem büyütme (3 sahne):** nasıl olur → ne yapılabilir → sana zararı ("FATURASI SANA GELİR").
3. **Rahatlatma:** "Kontrolü 30 saniye".
4. **Adımlar (3 sahne):** "1. …", "2. …", "3. …". UI taklidi + imleç.
5. **Kriz planı:** "Tanımadığın hat varsa": tikli liste.
6. **Değer teklifi:** "Dilekçesi hazır". Belge + "HAZIR ŞABLON" mührü.
7. **CTA (zorunlu):** "YORUMA **[ANAHTAR KELİME]** YAZ, [X]'İ GÖNDEREYİM". Yorum arayüzü taklidi: kelime yazılır → gönderilir → "DM'de ✓" yanıtı gelir.
8. **Paylaşım:** "Kaydet, ailene gönder" (kaydet ve paylaş ikonları).

### B) YATAY ANLATIM VİDEOSU, 1–3 dk, adım adım
1. **Hook (3–4 sn):** büyük 3 satır başlık + görsel + mühür.
2. **Yol haritası (4–5 sn):** "2 dakikada adım adım" + 4 bölüm kartı.
3. **Açık döngü (4 sn):** "Videonun sonunda DİLEKÇE ŞABLONU" + "ÜCRETSİZ". İzleyiciyi sona kadar tutar.
4. **Adımlar:** tarayıcı simülasyonu.
   - Adres çubuğuna URL daktilo ile yazılır → Enter tuşu → sayfa yüklenme çubuğu → sayfa açılır.
   - Giriş: T.C. Kimlik No ve şifre alanları **maskeli** doldurulur; tuşlar sol altta tuş görselleştiricide görünür.
   - Arama kutusuna sorgu yazılır → öneri listesi açılır → üzerine gelinince renk değişir → tıklanır.
   - Sonuç sayfası: önce dönen yükleme göstergesi, sonra tablo. Satırlar tek tek vurgulanır (✓ yeşil, ⚠ kırmızı), çizilerek beliren daire ve açıklama etiketleri eklenir.
   - Sol üstte sürekli **"ADIM n/4 · başlık"** pill'i görünür.
5. **Ne yapmalı:** arka plan kararır, ortada numaralı aksiyon kartı açılır ve maddeler tek tek eklenir.
6. **Bonus (koruma ipuçları).**
7. **CTA:** yorum arayüzü + "ABONE OL" butonu. İmleç tıklar → "ABONE OLUNDU ✓" + ding.

**Kurumsal sayfa taklidi kuralı:** gerçek siteye *benzeyen* ama birebir kopyalamayan, stilize bir arayüz çizilir (logo kopyalanmaz; "e" harfli kırmızı kare + "e-Devlet Kapısı" yazısı). Amaç eğitim, sahte site yapmak değil.

### Altyazı / metin yazım kuralları
- Altyazı metni sahne başına tek cümle. Vurgulanan kelime `*YILDIZ*` arasına yazılır.
- Ekranda kare başına en fazla 8 kelime. Hook en fazla 6 kelime.
- Türkçe büyük harf dönüşümü `upper_tr()` ile yapılır (i→İ, ı→I). Python'un `upper()` fonksiyonu Türkçede yanlış sonuç verir!
- Emoji kare içine yazılmaz (font desteklemiyor); ✓ ▾ › gibi basit glifler kullanılabilir.

---

## 7. KONU HAVUZU VE CTA MANTIĞI
10 kategori: Tüketici · Çalışma hayatı · Kira/Mülk · Banka/Borç · e-Devlet/Bürokrasi · Siber güvenlik · Ulaşım · Sağlık · Sosyal haklar · Günlük hukuk.
- Her kısa videonun bir **yorum anahtar kelimesi** olur (HAT, AİDAT, DEPOZİTO, İADE…) ve karşılığında **somut bir şey** verilir: dilekçe şablonu, kontrol listesi, adım adım rehber.
- Aynı senaryodan 1 dikey + 1 yatay video çıkar. Dikey video, yatay videonun "fragmanı" gibidir.

---

## 8. ADIM ADIM ÜRETİM PROSEDÜRÜ

1. **Senaryo:** dikey için Beat listesi (süre, başlık 2 satır, altyazı, görsel fonksiyonu, maskot ifadesi, SFX), yatay için Seg listesi.
2. **Görsel fonksiyonları:** `v_xxx(img, t, dur, cx, cy)`. Sprite'lar `@lru_cache` ile çizilir, `place_anim` ile yerleştirilir.
3. **Önizleme:** `python3 projects/X/short.py preview` her sahnenin %75 anından kontak tabaka üretir. **Bakılıp düzeltilir.**
4. **Render:** `OUT_DIR=out python3 projects/X/short.py` ve `.../tutorial.py`
5. **Kalite kontrol (her video):**
   - `ffprobe` ile çözünürlük, yuv420p ve süre kontrolü
   - `ffmpeg -af ebur128` ile hedef −14 LUFS ±1
   - Videodan her 1,6–3,2 sn'de bir kare alınıp tabaka yapılır ve **gözle kontrol edilir**
   - İlk kare ayrıca kontrol edilir (kapak/hook)
6. **Teslim için küçültme (Drive sınırı ~3 MB):**
   - Dikey: 2 geçiş, `-b:v 520k -maxrate 900k`, AAC 96k
   - Yatay: `scale=1280:720`, 2 geçiş, `-b:v 200k -maxrate 550k`, AAC 64k
   - Dosya 3,0 MB'ın altında kalmalı.
7. **Drive:** konu adıyla klasör açılır → MP4'ler yüklenir (dosya referansıyla `sha256:<hash>:<yol>`) → linkler verilir.
8. **Git:** kod commit edilir ve push edilir.

---

## 9. ÖĞRENİLEN HATALAR (tekrarlanmasın)

| Hata | Çözüm |
|---|---|
| `ImageDraw.Draw(rgba_img, "RGBA")` yarı saydam dolguyu **karıştırmaz, üzerine yazar**; satır tamamen kırmızıya boyandı | Yarı saydam katmanı ayrı bir `Image.new("RGBA")` olarak oluşturup `alpha_composite` ile ekle |
| Uzun kırmızı başlık sağdan taştı | Genişlik > 970px ise font boyutunu 6'şar 6'şar küçült |
| Punch zoom başlığı kırptı | Zoom en fazla 1.06, merkez ekranın ortası |
| İlk kare boştu (öğeler pop ile geliyordu) | İlk sahnede öğeler t_in=-1 ile baştan görünür, altyazı lead=0 |
| Tabloya 1.3 kat zoom kolonları kesti | Geniş içerikte en fazla 1.12 kat |
| Telefon görseli altyazıyla çakıştı | Orta görsel en fazla y≈1300'e kadar uzanmalı |
| Kart üstündeki mühür başlık şeridini kapattı | Mühür kartın dışına veya köşesine taşınır |
| SIM kartlar başlığın üstüne bindi (yatay) | Başlık sol kolonda (x<1050), görseller sağ kolonda |
| Drive yüklemesi 4,2 MB'ta reddedildi | 2 geçişli küçültme ve 3 MB altı |

---

## 10. YAPILAMAYANLAR / SINIRLAR
- Bu ortamda TTS yok; seslendirme dışarıdan gelir.
- AI video veya stok görüntü yok; hareket tamamen programatik çizimle sağlanır.
- Gerçek marka logoları ve resmî site birebir kopyalanmaz; stilize taklit yapılır.
- Gerçek kişisel veri gösterilmez.
- Platformlara otomatik yayın yapılmaz.

---

## 11. DEVİR ALAN AJANA HAZIR PROMPT

```
Sen kodla video üreten bir ajansın. Python (Pillow + numpy) ile kare kare çizip ffmpeg ile MP4 üretirsin.
GitHub'daki cldvdo reposunu (dal: ccr-411bd5c8-aqf2b8) klonla ve AJAN-REHBERI.md'yi baştan sona oku; tüm stil, hareket, ses ve kalite kontrol kurallarına aynen uy.
Yeni konu için projects/hat_sorgulama/ klasörünü örnek alarak projects/<konu>/ altında short.py (dikey, 11-13 sahne, 30-45 sn) ve tutorial.py (yatay, adım adım tarayıcı simülasyonu, 1-3 dk) yaz.
Her videoda: güçlü ilk kare, kelime kelime altyazı, maskot, sahne geçiş SFX'leri, sonda "Yoruma [KELİME] yaz, [ŞABLON]'u göndereyim" CTA'sı olsun.
Render öncesi önizleme kontak tabakası üret ve kontrol et; render sonrası ffprobe + ebur128 (-14 LUFS) + kare tabakası ile QC yap.
Teslimde videoları 3 MB altına küçült, Drive'da konu klasörüne yükle, linkleri ver.
Hukuki bilgilerde yalnızca emin olduğun bilgiyi yaz; örnek kişisel verileri maskele.
```
