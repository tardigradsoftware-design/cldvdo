# 🎬 VİDEO KURGU AJANI — EVRENSEL REHBER

> Bu rehber, **herhangi bir konudaki** seslendirmeyi (TTS) alıp onu viral potansiyeli yüksek bir videoya **kurgulamayı** öğretir.
> Senaryo ve seslendirme kullanıcıdan gelir. Ajanın işi: **sesi sahnelere bölmek, her sahneye uygun görseli çizmek, hareket, altyazı ve efektlerle sesi görselleştirmek.**
> **Arka plan müziği YOK.** Ses = seslendirme + çok hafif efektler.
> Motor kodu: GitHub `tardigradsoftware-design/cldvdo` (dal `ccr-411bd5c8-aqf2b8`) → `engine/` klasörü. `projects/elektrik/short.py` EN GÜNCEL ÖRNEKTİR (dikey); `projects/hat_sorgulama/` yatay örnek içerir.

---

## 0. TEMEL İLKELER

1. **Video kodla üretilir.** Python (Pillow) ile her kare çizilir, ffmpeg ile MP4 yapılır. Montaj programı, stok görüntü ve AI video kullanılmaz.
2. **Ses patrondur.** Görsel her zaman sese kilitlenir. Konuşmacı bir şeyi söylerken o şey ekranda belirir.
3. **Her şey çizimdir.** Kartlar, ikonlar, maskot ve arayüz taklitleri kodla çizilir. Tutarlıdır ve telif sorunu yoktur.
4. **Önce önizleme, sonra render.** Taşma ve çakışma kontak tabakada yakalanır.
5. **Her 2–3 saniyede yeni bir görsel olay olur** (izleyici tutma).
6. **Doğruluk:** senaryoda olmayan bilgi ekrana yazılmaz. Örnek kişisel veriler maskelenir (A**** Y*****, 1•••••••••8).

---

## 1. GİRDİ: KULLANICIDAN NE GELİR?

| Girdi | Biçim |
|---|---|
| **Seslendirme** | `dikey.mp3` ve/veya `yatay.mp3`. **Her bölüm arasında ~1 sn sessizlik**, bölüm içinde 0.5 sn'den uzun sessizlik yok. |
| **Senaryo metni** | Numaralı bölümler (1, 2, 3…). Her bölüm = 1 sahne (dikey) veya 1 segment (yatay). |
| (ops.) Referans video | Stil örneği |

**Ses eşleme kuralı:** sesteki bölüm sayısı, senaryodaki bölüm sayısına **eşit olmalıdır**. Değilse motor hata verir. Bu durumda `split_segments(min_silence=…, noise_db=…)` ayarlanır veya kullanıcıya sorulur.

---

## 2. ARAÇLAR

| Araç | Görev |
|---|---|
| Python 3 + **Pillow** | Kare çizimi |
| **numpy** | Vinyet, SFX sentezi, ses miksi |
| **ffmpeg / ffprobe** | Encode, `silencedetect` (ses bölme), `loudnorm`, `ebur128`, QC kareleri |
| multiprocessing | 4 çekirdekte paralel kare üretimi |
| Fontlar | Inter Display Black/ExtraBold (başlık), Inter Bold/SemiBold (gövde), DejaVu Sans Mono |
| Google Drive | Girdi alma, çıktı teslim (**dosya başına ~3 MB sınırı**) |

---

## 3. MOTOR (engine/) — NE NEREDE

| Dosya | İçerik |
|---|---|
| `core.py` | Renkler, fontlar, easing, `place()` / `place_anim()`, sprite önbelleği, `punch_zoom`, `render()` |
| `components.py` | Maskot, `Captions` (karaoke altyazı), imleç, tuş görselleştirici, ✓ ✗ ⚠ ikonları, mühür |
| `voice.py` | **`split_segments()`**: TTS'i sessizliklerden böler · **`fit_durations()`**: sahne sürelerini sese kilitler |
| `audio.py` | SFX sentezi + `mix(voice_path=…)` → −14 LUFS. **Müzik varsayılan olarak kapalı.** |
| `shorts.py` | **Dikey şablon:** `Short(beats, voice=...)` |
| `tutorial.py` | **Yatay şablon:** `Tutorial(segs, voice=...)`, tarayıcı/arayüz simülasyonu, kamera |

**Çalıştırma:**
```bash
VOICE=dikey.mp3 OUT_DIR=out python3 projects/<konu>/short.py       # dikey
VOICE=yatay.mp3 OUT_DIR=out python3 projects/<konu>/tutorial.py    # yatay
VOICE=dikey.mp3 python3 projects/<konu>/short.py preview           # kontak tabaka
```

**Performans sırrı:** her öğe bir kez çizilip `@lru_cache` ile saklanır (2 kat süper örnekleme ile). Karede yalnızca ölçek, döndürme, saydamlık ve konum değiştirilir. Değişen içerik (daktilo, sayaç) duruma göre önbelleğe alınır.

---

## 4. SES → SAHNE SENKRONU (en kritik bölüm)

```
TTS.mp3 → silencedetect (≥0.7 sn sessizlik, -35 dB) → [(konuşma_başı, konuşma_sonu), ...]
  → sahne_i başlangıcı = konuşma_i başlangıcı
  → sahne_i süresi    = konuşma_(i+1) başı − konuşma_i başı   (sessizlik sahnenin sonuna dahil)
  → son sahne         = konuşma sonu + 0.4 sn
  → altyazı kelimeleri yalnızca KONUŞMA süresine yayılır (sessizliğe taşmaz)
```

- Kelime zamanlaması (ASR olmadan): kelimeler konuşma süresine **harf sayısına göre ağırlıklı** dağıtılır (`0.55 + 0.06 × harf`). Türkçe TTS'te hata payı ±0.2 sn civarıdır.
- **Görsel olaylar konuşmaya göre zamanlanır.** Bir kelime söylenirken ilgili kart veya mühür belirir: `t_in ≈ (kelime_sırası / kelime_sayısı) × konuşma_süresi`.
- Yatay videoda daktilo ve tıklama gibi animasyonlar sabit saniyelerle çalışır. Ses kısaysa animasyon sığmayabilir. Bu durumda animasyonu hızlandır (cps artır) veya o bölümün metnini uzatmasını kullanıcıdan iste.

---

## 5. GÖRSEL STİL KİTABI

| Öğe | Kural |
|---|---|
| Zemin | Açık gri, radyal vinyet (#FAFAFA ortası → #DEDEDE kenarları) |
| Renkler | Mürekkep #111 · **Kırmızı #E8342E** (ana vurgu/tehlike) · Yeşil #18A058 (doğru/✓) · Mavi #265CE6 (kurum/bilgi) · Sarı #FFCC29 (uyarı) |
| Başlık | Sol üstte 2 satır: 1. satır siyah 92px, **2. satır kırmızı ve büyük** (112px). Sığmazsa otomatik küçülür. |
| Kart | 5px siyah çerçeve, **sağ alta 10px sert siyah gölge**, 18px köşe. İsteğe bağlı renkli başlık şeridi. |
| Pill | Tam yuvarlak etiket. Vurgu pill'i kırmızı zemin + beyaz yazı. |
| Mühür | Eğik (−12°…+8°) kalın etiket. 2.2 kat büyükten "basılır". |
| Altyazı | Kelime kelime: **aktif kelime = kırmızı pill**, söylenmişler = beyaz pill + siyah yazı, sıradakiler = soluk gri. Grup başına en fazla 3–4 kelime. |
| Maskot | **TOKMAK** (`maskot/tokmak_maskot.py`, kanalın resmî maskotu). Varsayılan `components.MASCOT = ("tokmak", "selam")`. Beat maskot alanına ifade yazılır; poz için `"ifade:poz"` (ör. `"ciddi:isaret"`, `"heyecanli:kutlama"`). İfadeler: normal, mutlu, kahkaha, saskin, kizgin, uzgun, goz_kirp, dusunceli, ciddi, endiseli, heyecanli, uykulu. Pozlar: selam, isaret, kutlama, duz. **Duyguya göre:** risk→saskin/endiseli, haksızlık→kizgin, çözüm→mutlu/heyecanli:kutlama, kural/adım→ciddi:isaret, soru→dusunceli, CTA→goz_kirp. |
| İlerleme | En üstte ince kırmızı çubuk |
| Sayaç pill'i (ops.) | Üstte sabit merak sayacı. Değeri video ilerledikçe açılır (ör. "?" → "3"). |

**Yerleşim, dikey (1080×1920):** sayaç y=120 · başlık y=250 · **orta görsel y≈900 (y=420–1300 arası)** · altyazı y=1365 · maskot y=1610 · alt 300px boş (platform arayüzü).
**Yerleşim, yatay (1920×1080):** bölüm pill'i sol üstte · içerik/tarayıcı alanı (80,118 → 1840,930) · tuş görselleştirici sol alt · altyazı y=1012 · maskot sağ alt.

---

## 6. HAREKET DİLİ

| Animasyon | Ne zaman |
|---|---|
| `pop` (0→1.1→1) | Kart, ikon, rakam girişi |
| `left` / `right` | Başlık 1. satırı, yan bilgi kartları |
| `up` | Liste, arayüz kartı |
| `drop` (+dönme) | Belge, fiziksel nesne |
| `stamp` | Hüküm cümlesi ("SENİN DEĞİL!", "ÜCRETSİZ", "HAZIR") |
| Çıkış | Sahnenin son 0.18 sn'sinde küçülerek kaybolur |
| Punch zoom + sarsıntı | **Sadece** hook ve şok anı. En fazla 1.06 kat. |
| Gecikmeli giriş | Öğeler 0.1–0.45 sn arayla, konuşmayla birlikte gelir |
| Daktilo | 11–13 karakter/sn, yanıp sönen imleç |
| Sayaç | Rakam 0'dan hedefe out_cubic ile artar |
| İmleç | in_out_cubic ile hareket, tıkta küçülür ve kırmızı halka yayılır |
| Kamera (yatay) | İşlem yapılan alana 1.3–1.7 kat yakınlaşır. Geniş tablolarda en fazla 1.12. İşlem bitince 1.0'a döner. |

---

## 7. CÜMLE → GÖRSEL ÇEVİRİ SÖZLÜĞÜ (evrensel)

Her senaryo cümlesini şu kalıplardan birine çevir:

| Cümle türü | Görsel kalıp |
|---|---|
| Soru / şok hook | Büyük başlık + 3'lü nesne + soru işaretleri + mühür ("SENİN Mİ?") |
| "…olabilir / risk" | İlgili nesne kartı + kırmızı mühür (SIZDI, GECİKTİ, REDDEDİLDİ) |
| "Sana bildirim/mesaj gelir" | Telefon çerçevesi + yukarıdan düşen bildirim kartları (ding) |
| Para / ceza / borç | Fatura/makbuz kartı + sayaçla artan tutar + mühür |
| "Sadece X saniye/dakika" | Kronometre + sayaç pill'i |
| "Şuraya gir, şunu yaz" | Tarayıcı/arama kartı + daktilo + imleç + tık |
| "Şuna tıkla" | Sonuç listesi + hover vurgusu + tık halkası |
| "Listeye/sonuca bak" | Tablo kartı + satır vurgusu (✓ yeşil / ⚠ kırmızı) + çizilerek beliren daire |
| "Şunları yap" (aksiyon) | Numaralı/tikli liste. Maddeler konuşmayla tek tek eklenir. |
| Yasal dayanak / hak | Belge kartı + madde etiketi + "HAKKIN" mührü |
| Önce / sonra karşılaştırma | İkiye bölünmüş ekran: sol kırmızı ✗, sağ yeşil ✓ |
| Rakam / istatistik | Dev rakam (sayaçla) + kısa açıklama pill'i |
| Değer teklifi ("şablonu hazırladım") | Belge + "HAZIR ŞABLON" / "ÜCRETSİZ" mührü |
| CTA "yoruma X yaz" | Yorum arayüzü: kelime yazılır → gönder → "DM'de ✓" yanıtı |
| "Kaydet / paylaş" | Kaydet + paylaş ikonları, pop |
| Abone ol | Buton tıklanır → "ABONE OLUNDU ✓" |

**Başlık (2 satır) kuralı:** cümlenin özü ekranda en fazla 6 kelime olur. 1. satır bağlam (siyah), 2. satır vurucu kısım (kırmızı). Örn: "FATURASI / SANA GELİR".
**Altyazı kuralı:** TTS metninin tamamı kelime kelime gösterilir. Her cümlede 1–2 kelime `*YILDIZ*` ile vurgulanır (rakamlar, fiil, "SEN", hüküm kelimesi).

---

## 8. KURGU KALIPLARI

### A) DİKEY (Shorts/Reels/TikTok), 30–50 sn, 10–14 sahne
1. **Hook (ilk 2–3 sn):** soru veya şok. **İlk karede başlık, görsel ve altyazı GÖRÜNÜR olmalı** (boş kare yasak). Punch zoom + impact.
2. **Problem büyütme (2–4 sahne):** nasıl olur → sonucu ne → sana zararı.
3. **Rahatlatma:** "Çözümü basit / X saniye".
4. **Adımlar (2–4 sahne):** "1. …", "2. …". Arayüz taklidi + imleç.
5. **Kriz planı:** aksiyon listesi.
6. **Değer teklifi:** şablon/rehber hazır.
7. **CTA:** "Yoruma [KELİME] yaz, [X]'i göndereyim" + yorum arayüzü.
8. **Paylaş/kaydet:** son sahne, ilk kareye benzer bitiş (döngü hissi).

### B) YATAY ANLATIM, 1–5 dk
1. **Hook (3–5 sn):** büyük 3 satır başlık + görsel + mühür.
2. **Yol haritası:** "X dakikada adım adım" + numaralı bölüm kartları.
3. **Açık döngü:** "Videonun sonunda [hediye]" (izleyiciyi sonuna kadar tutar).
4. **Adımlar:** sol üstte sürekli "ADIM n/N · başlık" pill'i. Ekran simülasyonu:
   - URL daktilo → Enter → yükleme çubuğu → sayfa
   - Form alanları **maskeli** doldurulur, tuşlar sol altta görünür
   - Arama → öneri listesi → üzerine gelme → tık
   - Sonuç: yükleme göstergesi → tablo → satır satır vurgu + açıklama etiketleri
   - Kamera işlem yapılan yere yakınlaşır
5. **Ne yapmalı:** arka plan kararır, ortada aksiyon kartı açılır, maddeler tek tek eklenir.
6. **Bonus ipuçları.**
7. **CTA:** yorum + abone butonu tıklanır.

**Arayüz taklidi kuralı:** kurumların veya uygulamaların arayüzü **stilize** çizilir. Logo ve birebir tasarım kopyalanmaz. Amaç eğitimdir, sahte site üretmek değil.

---

## 9. SES TASARIMI (MÜZİK YOK)

- **Seslendirme:** tepe değeri 0.8'e normalize edilir, öndedir.
- **SFX (numpy sentezi):** `whoosh` (sahne geçişi) · `pop` (giriş) · `impact` (hook/şok/mühür) · `ding` (olumlu/madde) · `error` (tehlike) · `key` (tuş) · `click` (tık) · `riser`.
- Konuşma varken SFX kazancı ×0.6 olur. Altyazı `tick` sesleri **kapalıdır** (konuşmayla çakışmasın).
- Son çıkış: `loudnorm=I=-14:TP=-1.5:LRA=11` → hedef **−14 LUFS ±1**.

---

## 10. ÜRETİM PROSEDÜRÜ (her yeni video)

1. Ses dosyasını al → `split_segments()` ile bölüm sayısını kontrol et (senaryoyla eşit mi?).
2. `projects/<konu>/` klasörü aç, örnek projeyi şablon olarak kopyala.
3. Her bölüm için `Beat` (dikey) / `Seg` (yatay) yaz: başlık, altyazı (TTS metni + *vurgu*), görsel fonksiyonu (§7 sözlüğünden), maskot ifadesi, SFX.
4. **Önizleme** kontak tabakasını üret → taşma, çakışma ve okunabilirlik kontrolü → düzelt.
5. **Render:** `VOICE=… OUT_DIR=out python3 …`
6. **Kalite kontrol:**
   - `ffprobe`: 1080×1920 / 1920×1080, yuv420p, süre ≈ ses süresi
   - `ebur128`: −14 LUFS ±1
   - 1.6–3 sn arayla kare tabakası çıkar → gözle kontrol
   - İlk kareyi ayrıca kontrol et
   - Rastgele 3 noktada ses–görsel senkronunu kontrol et (kelime söylenirken kart ekranda mı?)
7. **Teslim (Drive ~3 MB sınırı):**
   - Dikey: `-b:v 520k -maxrate 900k` 2 geçiş, AAC 96k
   - Yatay: `scale=1280:720`, `-b:v 200k -maxrate 550k` 2 geçiş, AAC 64k
   - Uzun yatay videolarda bitrate'i (3 MB × 8 / süre) formülüyle hesapla; gerekirse parçala veya kullanıcıya sor.
8. Drive'da klasör aç → yükle (`sha256:<hash>:<yol>` dosya referansıyla) → linkleri ver.

---

## 11. BİLİNEN TUZAKLAR

| Tuzak | Çözüm |
|---|---|
| `ImageDraw.Draw(rgba, "RGBA")` yarı saydam dolguyu **karıştırmaz, üzerine yazar** | Ayrı `Image.new("RGBA")` katmanı oluştur → `alpha_composite` |
| Python `upper()` Türkçede yanlış (i→I) | `upper_tr()` kullan (i→İ, ı→I) |
| Emoji kare içinde çıkmıyor | Kullanma; ✓ ▾ › gibi basit glifler kullanılabilir |
| Uzun başlık taşıyor | Otomatik küçültme (genişlik > 970px ise) |
| Punch zoom başlığı kırpıyor | En fazla 1.06 kat |
| İlk kare boş | İlk sahnede öğeler `t_in=-1` ile baştan görünür |
| Geniş tabloda zoom kolonları kesiyor | En fazla 1.12 kat |
| Orta görsel altyazıyla çakışıyor | Görsel y=1300'ü geçmez |
| Mühür kart başlığını kapatıyor | Mührü köşeye veya kart dışına taşı |
| Ses bölüm sayısı tutmuyor | `min_silence` / `noise_db` ayarla veya kullanıcıdan sessizlikleri düzeltmesini iste |
| Drive yüklemesi reddedildi (>3 MB) | 2 geçişli küçültme |

---

## 12. SINIRLAR
- TTS bu ajanda yok; ses kullanıcıdan gelir.
- Arka plan müziği kullanılmaz.
- AI video ve stok görüntü yok; hareket programatik çizimle sağlanır.
- Gerçek logo, birebir resmî site ve gerçek kişisel veri kullanılmaz.
- Platformlara otomatik yayın yapılmaz.

---

## 13. AJANA VERİLECEK BAŞLANGIÇ PROMPT'U

```
Sen bir video KURGU ajanısın. Konu ve seslendirme sana verilecek; senin işin sesi görselleştirip kurgulamak.
1) GitHub cldvdo reposunu (dal: ccr-411bd5c8-aqf2b8) klonla ve AJAN-REHBERI.md'yi baştan sona oku. Stil, hareket, senkron, QC kurallarına aynen uy.
2) Sana verilen TTS dosyasını engine/voice.py ile bölümlere ayır; bölüm sayısı senaryoyla eşleşmeli.
3) projects/hat_sorgulama/ örneğini şablon alıp projects/<konu>/ altında dikey (short.py) ve/veya yatay (tutorial.py) kurguyu yaz. Her cümleyi §7 sözlüğüne göre bir görsele çevir; görseller konuşmayla eş zamanlı belirsin.
4) Arka plan müziği kullanma. Sadece seslendirme + hafif SFX.
5) Önce önizleme tabakası üret ve kontrol et, sonra render al, QC yap (ffprobe, -14 LUFS, kare tabakası, ilk kare, senkron).
6) Videoları 3 MB altına küçültüp Drive'da konu klasörüne yükle, linkleri ver.
```
