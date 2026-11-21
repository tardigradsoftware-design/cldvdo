---
name: tokmak-video-uretici
description: Hak/hukuk rehberi TTS metinlerinden (senaryolar.csv) kodla yüksek tempolu SHORTS (9:16) ve UZUN ADIM ADIM ANLATIM (16:9) videoları üretir. Sanal portal ekranları (e-Devlet, CİMER, e-Nabız, banka, SGK, Hakem Heyeti… web + mobil), mouse/klavye simülasyonu, kelime kelime altyazı, Tokmak maskotu ve otomatik kalite kontrolü içerir. Kullanıcı "VID_xxx videosunu üret", "şu metinden video yap", "shorts/uzun video" dediğinde kullan.
---

# TOKMAK VİDEO ÜRETİCİ — SKILL

## 0) Altın kurallar (asla çiğneme)
1. **Video sıfırdan yazılmaz.** Önce `tokmak.py` ile otomatik üret; sadece gerekirse plan JSON'unu düzenle.
2. **Hareketsiz an yok.** Kalite kontrolü (`engine/qc.py`) GEÇTİ demeden video teslim edilmez (donma ≤ %5, en uzun donma ≤ 2 sn).
3. **Gerçek kurum kimliği yok.** "T.C." başlığı, gerçek logo, gerçek alan adı (….gov.tr) kullanılmaz. Portallar stilize/kurgusaldır.
   Kişisel veriler maskeli (A**** Y*****, TR•• •••• 4821, 1•••••••••8).
4. **Metin değiştirilmez.** TTS metni olduğu gibi altyazı olur; görseller metne uyar.
5. **Müzik yok.** Ses = seslendirme (varsa) + hafif efektler.
6. **Zaman bütçesi:** bir video için en fazla 1 önizleme + 1 render + 1 düzeltme turu.

## 1) Kurulum (bir kez)
```bash
pip install pillow numpy          # sistemde ffmpeg olmalı
# klasör yapısı:  tokmak.py, engine/*.py, maskot/tokmak_maskot.py, senaryolar.csv
```

## 1b) Stil
- **Uzun video varsayılan stili: `kayit` (gerçekçi ekran kaydı).** Tam ekran tarayıcı, gerçekçi portal arayüzü, imleci takip
  eden otomatik yakınlaşma, köşede küçük adım etiketi, gerekince bilgi notu kartı. **Karaoke altyazı ve büyük maskot YOK**
  — zamanın çoğu portal ekranında geçer (verimli anlatım). Hedef görünüm: `docs__ornek_kayit_VID_001.jpg`.
- Eski çizgi/kart stili gerekirse: `--stil cizgi`.
- Shorts her zaman çizgi/kart stilindedir (hızlı tempo, altyazılı, maskotlu).

## 1c) Görsel kontrol
Sen görselleri görebiliyorsun: her videoda önce **GORSEL_KONTROL.md**'deki puanlama listesini uygula.

## 2) Tek komutla üretim (90% durumda yeterli)
```bash
python3 tokmak.py --csv senaryolar.csv --id VID_001 --tur uzun     # uzun anlatım videosu
python3 tokmak.py --csv senaryolar.csv --id VID_001 --tur shorts   # dikey shorts
# isteğe bağlı:  --ses ses.mp3   (seslendirme eklenir, süre sese uydurulur)
#                --onizleme      (render yerine kare tabakası; saniyeler sürer)
#                --hepsi         (CSV'deki tüm satırlar)
```
Çıktılar `out/` içinde:
- `VID_001_uzun.mp4` — video
- `VID_001_uzun_kareler.jpg` — kalite kontrol kare tabakası
- `VID_001_uzun_plan.json` — DÜZENLENEBİLİR sahne planı
- `VID_001_uzun_bilgi.txt` — başlık, etiketler, hashtag'ler (yayın için)
Komut sonunda kalite raporu yazılır: `SONUÇ: GEÇTİ ✅` veya `KALDI ❌`.

## 3) Çalışma döngüsü (her video)
1. `--onizleme` çalıştır → `*_onizleme.jpg`'e bak. Sorular:
   - Portal sahnesi doğru kurumu mu gösteriyor? (tema)
   - Arama kutusuna doğru hizmet adı mı yazılıyor?
   - Büyük başlıklar anlamlı mı? Boş/anlamsız kart var mı?
2. Sorun varsa `out/VID_xxx_uzun_plan.json` dosyasını düzenle (bkz. §4), sonra:
   `python3 tokmak.py --plan out/VID_xxx_uzun_plan.json --onizleme` → tamamsa `--onizleme`siz çalıştır.
3. Render sonu raporu oku. KALDI ise rapordaki donma saniyelerindeki sahneye eylem/kart ekle, bir kez daha render al.
4. Teslim: mp4 + bilgi.txt. Raporu kullanıcıya aynen ilet.

## 4) Plan JSON'u (düzenleme rehberi)

### Uzun video: `scenes` listesi — her sahne bir dict
| kind | ne gösterir | düzenlenebilir alanlar |
|---|---|---|
| `hook` | dev başlık + yan etiketler + "HAKKINI AL" mührü | `title`, `sentences` |
| `overview` | "N NET ADIM" + adım kartları | `steps` (kısa adım adları) |
| `portal` | tarayıcıda (web) ya da telefonda (mobil) portal + mouse + klavye | `theme`, `device`, `actions` |
| `phone` | telefonda numara tuşlama + arama | `number`, `note` |
| `document` | dilekçe/ihtarname/e-posta yazılması + mühür | `doc_title`, `lines`, `stamp` |
| `money` | banka bildirimi + para sayacı + yağan paralar | `amount` |
| `card` | her cümle için büyük ifade + ikon + etiketler + mühür | `cards[i].title/chips/stamp/icon` |
| `outro` | abone ol butonu tıklanır | — |
Ortak alanlar: `sentences` (altyazı = TTS cümleleri, DEĞİŞTİRME), `chapter` (["ADIM 2/4","Başlık"]), `mascot` (cümle başına ifade).

**`theme` değerleri:** edevlet, cimer, enabiz, sgk, banka, hakem, uyap, vergi, tapu, ptt, operator, kargo, eticaret, ilan, kvkk,
isverenlik, eposta, sabim. Görünüm: `docs/portal_katalogu.jpg`. Yeni portal: `engine/portals.py` → `THEMES` sözlüğüne 1 satır.

**`device`:** `"web"` (tarayıcı penceresi) veya `"mobile"` (telefon ekranı). Metinde "uygulama/mobil/telefonundan" geçerse mobil seç.

**`actions` (portal eylemleri)** — `s` = eylemin bağlı olduğu cümle sırası (0'dan başlar; o cümle okunurken olur):
```json
{"s": 1, "do": "search",   "text": "Şahıs Ödemeleri Sorgulama"}     // arama kutusuna yaz + öneriye tıkla
{"s": 1, "do": "login"}                                              // T.C. kimlik + şifre maskeli doldurulur
{"s": 2, "do": "menu",     "text": "Kart Ayarları"}                  // menü/sekme listesinde seç
{"s": 2, "do": "select",   "text": "Şikayet"}                        // seçenek işaretle
{"s": 3, "do": "field",    "label": "IBAN", "text": "TR•• •••• •••• 4821"}
{"s": 3, "do": "textarea", "lines": ["satır 1", "satır 2"]}          // metin kutusuna yazma
{"s": 4, "do": "upload",   "files": ["Fatura.pdf", "Dekont.pdf"]}    // belge yükleme
{"s": 4, "do": "result",   "rows": [["Bekleyen ödeme", "1.250 TL"], ["Diğer", "—"]]}  // sonuç tablosu, ilk satır vurgulu
{"s": 5, "do": "screenshot"}                                         // ekran görüntüsü flaşı
{"s": 5, "do": "submit",   "label": "Başvuruyu Gönder"}              // butona bas + "İşleminiz alındı" penceresi
```
Bir cümleye birden fazla eylem bağlanabilir (cümle süresine bölünür). Kamera her eylemde ilgili alana otomatik yakınlaşır.

### Hazır görsel kütüphanesi — ÇİZİM YAPMA, ADIYLA SEÇ
Asla yeni çizim/şekil kodu yazma. Görsel gerekiyorsa kütüphaneden adını yaz:
- **İkonlar (53 adet):** `docs__ikon_kutuphanesi.jpg` → ev, tapu, araba, kart, kimlik, belge, telefon, banka, takvim, kalkan,
  kilit, para, fis, koli, kisi, aile, sirket, tokmak, saat, sms, hastane, okul, sepet, imza, yasak, uyari, onay, red, terazi …
  Kullanım: shorts beat'inde `"icon": "araba"`, not şablonlarında `"ikon": "araba"`.
- **Sahne şablonları (8 adet, uzun video):** `docs__sablon_katalogu.jpg`. Portal dışındaki bilgi notu ekranlarında
  her cümle için `notlar` listesinde bir öğe bulunur; otomatik seçilir, beğenmezsen sadece adını/parametresini değiştir:
```json
"notlar": [
 {"sablon": "not",           "metin": "Bankalar 10 yıl sonra parayı devlete aktarır", "ikon": "banka", "etiketler": ["10 yıl"]},
 {"sablon": "sayac",         "deger": "12.450 TL", "metin": "Ortalama alacak"},
 {"sablon": "karsilastirma", "sol_baslik": "YANLIŞ", "sol": ["Sözlü şikâyet"], "sag_baslik": "DOĞRU", "sag": ["Yazılı başvuru"]},
 {"sablon": "zaman",         "adimlar": ["Bugün", "15 gün", "30 gün"], "metin": "Cevap süresi"},
 {"sablon": "liste",         "metin": "Hazırlaman gerekenler", "maddeler": ["Kimlik", "Fatura", "Dekont"]},
 {"sablon": "akis",          "kutular": ["Sen", "Satıcı", "Hakem Heyeti"], "metin": "Başvuru sırası"},
 {"sablon": "uyari",         "metin": "Süreyi kaçırırsan hakkın düşer", "alt": "Zamanaşımı 2 yıl"},
 {"sablon": "yasak",         "metin": "İşveren maaşından kesinti yapamaz", "ikon": "para"}
]
```
Seçim kuralı: tutar/yüzde → sayac · süre/gün → zaman · 3+ belge/madde → liste · kurumlar arası süreç → akis ·
"yapamaz/asla" → yasak · risk/ceza → uyari · "X yerine Y" → karsilastirma · diğer → not.
Metinler kısa olsun (not/uyari/yasak ≤ 8 kelime, madde ≤ 4 kelime).

### Shorts: `beats` listesi — her beat bir dict
`kind`: hook | card | money | phone | document | portal | comment ;
alanlar: `sentence` (altyazı), `title` ([siyah satır, kırmızı satır] — EN ÇOK düzenlenen alan), `chips`, `stamp`, `icon`
(warn/money/calendar/doc/law/check **veya kütüphaneden herhangi bir ikon adı**), `mascot`, `word` (comment için yorum kelimesi), `query`/`theme` (portal için), `amount`, `number`.

### Maskot ifadeleri (Tokmak)
normal, mutlu, kahkaha, saskin, kizgin, uzgun, goz_kirp, dusunceli, ciddi, endiseli, heyecanli, uykulu ; poz eki `:selam|:isaret|:kutlama|:duz`
Duyguya göre: risk → saskin/endiseli, haksızlık → kizgin, kural/adım → ciddi:isaret, çözüm → mutlu, başarı → heyecanli:kutlama, CTA → goz_kirp:selam.

## 5) Seslendirme
TTS dosyası varsa `--ses dosya.mp3` ver. Video süresi sese ölçeklenir. Cümleler arasında ~0,5 sn, paragraflar arasında ~1 sn
sessizlik olması senkronu iyileştirir. Ses yoksa video altyazıyla, 2,6 kelime/sn hızında üretilir.

## 6) Kalite kontrolü
`python3 engine/qc.py out/VID_001_uzun.mp4` → çözünürlük, yuv420p, donma oranı ≤ %5, en uzun donma ≤ 2 sn, ses −18…−12 LUFS.
Ayrıca `*_kareler.jpg`'i hedef görünümlerle karşılaştır: `docs/hastane_kareler.jpg` (uzun), `docs/elektrik_kareler.jpg` (shorts).

## 7) Dosya haritası
| dosya | görev |
|---|---|
| `tokmak.py` | komut satırı: CSV → plan → render → QC |
| `engine/director.py` | metni çözümler, sahne planı çıkarır (kurallar burada) |
| `engine/scenes.py` | plan → hareketli sahneler (portal, telefon, belge, para, kart…) |
| `engine/portals.py` | portal temaları + widget'lar (web/mobil) — shorts/çizgi stili |
| `engine/screencast.py` | GERÇEKÇİ EKRAN KAYDI modu (uzun videolar, varsayılan) |
| `engine/tutorial.py`, `engine/shorts.py` | yatay/dikey şablon (altyazı, bölüm etiketi, kamera, maskot) |
| `engine/core.py`, `components.py`, `audio.py`, `voice.py` | motor |
| `engine/assets.py` | ikon kütüphanesi (`python3 -m engine.assets` → katalog) |
| `engine/templates.py` | sahne şablonları (`python3 -m engine.templates` → katalog) |
| `engine/qc.py` | kalite kontrol |
| `maskot/tokmak_maskot.py` | maskot (12 ifade × 4 poz) |
