# DÜZELTME TALİMATI — "Videon slayt gibi, video gibi değil"

Bu talimat, ürettiğin `acil_yatay_5adim.mp4` videosunun ölçülmüş sorunlarını ve nasıl düzelteceğini anlatır.
Önce bu dosyayı, sonra BASLA_YATAY.md'yi oku; `docs__hastane_kareler.jpg` hedef görünümdür.

## 1. ÖLÇÜM (senin videon vs hedef)

| Ölçüt | Senin videon | Hedef video | Kural |
|---|---|---|---|
| Donuk (hareketsiz) süre | **130 sn / 159 sn (%82)** | **1,7 sn / 152 sn (%1)** | %5'ten az olmalı |
| En uzun donma | **29,9 sn** | 1,7 sn | 2 sn'den uzun donma YOK |
| Sahne değişimi | ~22 | 150+ görsel olay | her 1,5–2,5 sn'de 1 olay |
| Altyazı | yok (sadece köşede küçük etiket) | kelime kelime, büyük, vurgulu | zorunlu |
| Maskot | yok | Tokmak, her sahnede ifade değişir | zorunlu |
| Yazı boyutu | çoğu 14–20 px (okunmaz) | en az 28 px, başlıklar 60–140 px | telefonda okunmalı |
| Kamera | hep sabit, tam ekran tarayıcı | işlem yapılan alana 1,3–1,5x zoom | zorunlu |
| Efekt sesi | — | tık, tuş, ding, impact, whoosh | her olayda |
| Ekranın kullanımı | içerik küçük, %60'ı boş | içerik büyük, merkezde | boş alan az |

Kendin ölç (render sonrası ZORUNLU):
```bash
ffmpeg -i video.mp4 -vf "freezedetect=n=0.003:d=1.5" -map 0:v -f null - 2>&1 | grep freeze_duration
```
Toplam donma süresi videonun %5'ini geçiyorsa video REDDEDİLİR, düzelt ve tekrar render al.

## 2. HAREKET KURALLARI (en önemli kısım)

1. **Ekranda hiçbir an tamamen durmaz.** Her karede en az biri hareket eder: imleç, yazılan metin, beliren kart,
   kamera kayması, maskot (nefes alır, göz kırpar), altyazı kelimesi.
2. **Her 1,5–2,5 saniyede yeni bir görsel olay** olur: kart düşer/pop olur, mühür basılır, tik çıkar, sayaç artar,
   alan dolar, kamera yakınlaşır/uzaklaşır, sahne değişir.
3. **Görsel olay = konuşulan kelime.** Seslendirmede "fatura" denince fatura kartı o anda ekrana gelir
   (`ctimes()` ile cümle başlangıçlarını hesapla, olayları oraya kilitle).
4. **Kamera canlıdır:** işlem yapılan alana 1,3–1,5x yakınlaş (`cam_path`), işlem bitince 1,0'a dön.
   Bekleme anlarında bile kamera çok yavaş kaysın (1,00 → 1,03 zoom drift).
5. **Giriş/çıkış animasyonu olmadan hiçbir öğe ekrana gelmez**: `place_anim(..., "pop" | "drop" | "up" | "stamp")`.
6. **Yazma animasyonu gerçek hızda:** 10–17 karakter/sn, her tuşta `key` sesi ve sol altta tuş göstergesi.
7. **Mühürler** ("ÜCRETSİZ", "SAKLA", "TUZAK!") önemli cümlelerde basılır, `impact` sesiyle.
8. **Sahne başına en fazla 6–8 saniye aynı ekran düzeni.** Uzun cümlelerde aynı sahnede yeni kartlar ekle.

## 3. GÖRÜNÜM KURALLARI

- Arka plan: açık gri vinyet (koyu lacivert değil). Tarayıcı penceresi kalın siyah çerçeve + gölge.
- Altyazı ekranın altında, kelime kelime: aktif kelime kırmızı kutu, okunanlar beyaz kutu, gelecekler gri.
- Sol üstte "ADIM n/5 · başlık" etiketi (pill).
- Sağ altta maskot Tokmak; ifadesi cümleye göre: risk → saskin, haksızlık → kizgin, kural → ciddi:isaret,
  çözüm → mutlu, başarı → heyecanli:kutlama.
- Rakamlar (3.750 TL) sayaç gibi artarak gelir.

## 4. YASAL / MARKA KURALI (senin videonda ihlal var)

- **"T.C." başlığı, gerçek alan adları (enabiz.gov.tr, saglik.gov.tr), resmî kurum logosu kullanma.**
  Sahte resmî site izlenimi verir. Stilize çiz: "e-Nabız" yazısı serbest ama "T.C. …" başlığı ve gerçek
  domain yok; URL çubuğunda genel/kurgusal adres kullan. Kişisel veriler maskeli (A**** Y*****, TR•• •••• 4821).

## 5. ÇALIŞMA DÖNGÜSÜ (her video için)

1. Metni adımlara ve cümlelere böl (`CAP_*` listeleri).
2. Her cümle için "ekranda ne hareket edecek?" sorusunu yanıtla — yanıt yoksa yeni görsel olay ekle.
3. `preview` ile her segmentin %20/%50/%80 karelerini üret, `docs__hastane_kareler.jpg` ile karşılaştır.
4. Render → `freezedetect` ölçümü → %5 üstü ise düzelt.
5. Örnek kodu (`projects__hastane__tutorial.py`) şablon olarak KULLAN; sıfırdan yazma.
