"""HAZIR GÖRSEL KÜTÜPHANESİ — ajan ÇİZMEZ, sadece ADIYLA SEÇER.

    from engine.assets import icon, ICONS, icon_for_text
    img = icon("tapu", 160)          # renkli karo + beyaz piktogram (RGBA)
    icon_for_text("Tapu müdürlüğüne git")  -> "tapu"

Tüm ikonlar aynı stil: yuvarlatılmış kare, dikey gradyan, yumuşak gölge, beyaz sembol.
Galeri: docs/ikon_kutuphanesi.jpg   ·   Yeni ikon: ICONS sözlüğüne 1 satır ekle.
"""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DJR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

RED, ORANGE, AMBER, GREEN, TEAL, BLUE, INDIGO, PURPLE, PINK, SLATE, BROWN = (
    (226, 54, 50), (234, 108, 30), (217, 150, 20), (22, 150, 80), (14, 150, 160), (37, 99, 235), (67, 56, 202),
    (126, 58, 220), (219, 39, 119), (71, 85, 105), (150, 95, 50))

# ---------------------------------------------------------------- çizim yardımcıları (100x100 birim)
WH = (255, 255, 255, 255)


def _poly(d, s, pts, **kw):
    d.polygon([(x * s, y * s) for x, y in pts], **kw)


def _r(d, s, b, r, **kw):
    d.rounded_rectangle([b[0] * s, b[1] * s, b[2] * s, b[3] * s], radius=r * s, **kw)


def _e(d, s, b, **kw):
    d.ellipse([b[0] * s, b[1] * s, b[2] * s, b[3] * s], **kw)


def _l(d, s, pts, w):
    d.line([(x * s, y * s) for x, y in pts], fill=WH, width=int(w * s), joint="curve")


def _t(d, s, xy, txt, size, path=INTER, fill=WH):
    d.text((xy[0] * s, xy[1] * s), txt, font=ImageFont.truetype(path, int(size * s)), fill=fill, anchor="mm")


# ---- özel çizimler (beyaz, ~20..80 alanında)
def p_ev(d, s, c):
    _poly(d, s, [(50, 18), (82, 46), (74, 46), (74, 80), (26, 80), (26, 46), (18, 46)], fill=WH)
    _r(d, s, (43, 58, 57, 80), 2, fill=c)


def p_araba(d, s, c):
    _r(d, s, (16, 46, 84, 70), 8, fill=WH)
    _poly(d, s, [(28, 46), (36, 30), (64, 30), (72, 46)], fill=WH)
    _poly(d, s, [(34, 44), (40, 34), (60, 34), (66, 44)], fill=c)
    for x in (32, 68):
        _e(d, s, (x - 8, 62, x + 8, 78), fill=WH)
        _e(d, s, (x - 4, 66, x + 4, 74), fill=c)


def p_kart(d, s, c):
    _r(d, s, (16, 28, 84, 72), 7, fill=WH)
    d.rectangle([16 * s, 36 * s, 84 * s, 45 * s], fill=c)
    _r(d, s, (24, 54, 44, 62), 2, fill=c)


def p_kimlik(d, s, c):
    _r(d, s, (14, 26, 86, 74), 7, fill=WH)
    _e(d, s, (22, 36, 42, 56), fill=c)
    _r(d, s, (20, 56, 44, 66), 5, fill=c)
    for i, w in enumerate((30, 24, 28)):
        _r(d, s, (50, 36 + i * 11, 50 + w, 41 + i * 11), 2, fill=c)


def p_belge(d, s, c):
    _poly(d, s, [(28, 16), (60, 16), (74, 30), (74, 84), (28, 84)], fill=WH)
    _poly(d, s, [(60, 16), (60, 30), (74, 30)], fill=(220, 220, 220, 255))
    for i, w in enumerate((32, 36, 26, 34)):
        _r(d, s, (35, 40 + i * 10, 35 + w, 44 + i * 10), 2, fill=c)


def p_telefon(d, s, c):
    _r(d, s, (32, 14, 68, 86), 9, fill=WH)
    _r(d, s, (37, 22, 63, 74), 3, fill=c)
    _e(d, s, (46, 77, 54, 83), fill=c)


def p_banka(d, s, c):
    _poly(d, s, [(50, 14), (86, 34), (14, 34)], fill=WH)
    for x in (22, 38, 54, 70):
        d.rectangle([x * s, 40 * s, (x + 8) * s, 72 * s], fill=WH)
    _r(d, s, (14, 74, 86, 84), 2, fill=WH)


def p_takvim(d, s, c):
    _r(d, s, (18, 22, 82, 84), 8, fill=WH)
    d.rectangle([18 * s, 30 * s, 82 * s, 40 * s], fill=(255, 255, 255, 120))
    for x in (32, 68):
        _r(d, s, (x - 4, 14, x + 4, 30), 3, fill=WH)
    for i in range(3):
        for j in range(4):
            _r(d, s, (26 + j * 13, 46 + i * 12, 34 + j * 13, 53 + i * 12), 2, fill=c)


def p_kalkan(d, s, c):
    _poly(d, s, [(50, 14), (82, 26), (78, 58), (50, 86), (22, 58), (18, 26)], fill=WH)
    _l(d, s, [(36, 50), (47, 61), (66, 40)], 7)
    d.line([(36 * s, 50 * s), (47 * s, 61 * s), (66 * s, 40 * s)], fill=c, width=int(7 * s), joint="curve")


def p_kilit(d, s, c):
    d.arc([30 * s, 16 * s, 70 * s, 56 * s], 180, 360, fill=WH, width=int(8 * s))
    d.line([(34 * s, 36 * s), (34 * s, 46 * s)], fill=WH, width=int(8 * s))
    d.line([(66 * s, 36 * s), (66 * s, 46 * s)], fill=WH, width=int(8 * s))
    _r(d, s, (22, 44, 78, 84), 8, fill=WH)
    _e(d, s, (45, 56, 55, 66), fill=c)
    d.rectangle([48 * s, 62 * s, 52 * s, 74 * s], fill=c)


def p_anahtar(d, s, c):
    _e(d, s, (16, 30, 46, 60), fill=WH)
    _e(d, s, (25, 39, 37, 51), fill=c)
    _r(d, s, (42, 41, 86, 49), 3, fill=WH)
    _r(d, s, (70, 45, 76, 60), 2, fill=WH)
    _r(d, s, (78, 45, 84, 56), 2, fill=WH)


def p_para(d, s, c):
    _e(d, s, (18, 18, 82, 82), fill=WH)
    _e(d, s, (24, 24, 76, 76), outline=c, width=int(3 * s))
    _t(d, s, (50, 52), "₺", 40, INTER, c)


def p_fis(d, s, c):
    pts = [(26, 14), (74, 14), (74, 82)]
    for k in range(6):
        x = 74 - (k + 0.5) * 8
        pts += [(x, 88 if k % 2 == 0 else 82)]
    pts += [(26, 82)]
    _poly(d, s, pts, fill=WH)
    for i, w in enumerate((36, 30, 36, 22)):
        _r(d, s, (33, 24 + i * 11, 33 + w, 28 + i * 11), 2, fill=c)
    _r(d, s, (33, 70, 67, 74), 2, fill=c)


def p_koli(d, s, c):
    _poly(d, s, [(50, 14), (84, 30), (84, 70), (50, 86), (16, 70), (16, 30)], fill=WH)
    d.line([(16 * s, 30 * s), (50 * s, 46 * s), (84 * s, 30 * s)], fill=c, width=int(3 * s))
    d.line([(50 * s, 46 * s), (50 * s, 86 * s)], fill=c, width=int(3 * s))
    _poly(d, s, [(33, 22), (67, 38), (67, 48), (33, 32)], fill=(255, 255, 255, 150))


def p_kisi(d, s, c):
    _e(d, s, (36, 16, 64, 44), fill=WH)
    _r(d, s, (22, 50, 78, 86), 18, fill=WH)


def p_aile(d, s, c):
    _e(d, s, (18, 22, 40, 44), fill=WH)
    _r(d, s, (12, 48, 46, 80), 12, fill=WH)
    _e(d, s, (60, 22, 82, 44), fill=WH)
    _r(d, s, (54, 48, 88, 80), 12, fill=WH)
    _e(d, s, (42, 44, 58, 60), fill=WH)
    _r(d, s, (38, 62, 62, 84), 9, fill=WH)


def p_sirket(d, s, c):
    _r(d, s, (20, 22, 56, 86), 3, fill=WH)
    _r(d, s, (56, 40, 82, 86), 3, fill=WH)
    for i in range(4):
        for j in range(2):
            _r(d, s, (26 + j * 15, 30 + i * 13, 33 + j * 15, 37 + i * 13), 1, fill=c)
    for i in range(3):
        _r(d, s, (63, 48 + i * 12, 75, 54 + i * 12), 1, fill=c)


def p_tokmak(d, s, c):
    _r(d, s, (24, 20, 70, 42), 8, fill=WH)
    _r(d, s, (20, 18, 30, 44), 4, fill=WH)
    _r(d, s, (64, 18, 74, 44), 4, fill=WH)
    d.line([(47 * s, 42 * s), (47 * s, 70 * s)], fill=WH, width=int(8 * s))
    _r(d, s, (24, 72, 76, 84), 4, fill=WH)


def p_grafik(d, s, c):
    for i, h in enumerate((22, 38, 30, 52)):
        _r(d, s, (20 + i * 16, 80 - h, 31 + i * 16, 80), 2, fill=WH)
    d.line([(16 * s, 84 * s), (84 * s, 84 * s)], fill=WH, width=int(4 * s))


def p_saat(d, s, c):
    _e(d, s, (16, 16, 84, 84), fill=WH)
    d.line([(50 * s, 50 * s), (50 * s, 28 * s)], fill=c, width=int(6 * s))
    d.line([(50 * s, 50 * s), (66 * s, 58 * s)], fill=c, width=int(6 * s))
    _e(d, s, (45, 45, 55, 55), fill=c)


def p_buyutec(d, s, c):
    _e(d, s, (16, 16, 64, 64), outline=WH, width=int(9 * s))
    d.line([(58 * s, 58 * s), (82 * s, 82 * s)], fill=WH, width=int(12 * s))


def p_sms(d, s, c):
    _r(d, s, (14, 20, 86, 68), 14, fill=WH)
    _poly(d, s, [(28, 64), (26, 84), (44, 66)], fill=WH)
    for x in (34, 50, 66):
        _e(d, s, (x - 5, 39, x + 5, 49), fill=c)


def p_kamera(d, s, c):
    _r(d, s, (14, 30, 86, 78), 10, fill=WH)
    _r(d, s, (34, 22, 58, 32), 3, fill=WH)
    _e(d, s, (34, 38, 66, 70), fill=c)
    _e(d, s, (41, 45, 59, 63), fill=WH)


def p_megafon(d, s, c):
    _poly(d, s, [(20, 40), (40, 40), (74, 22), (74, 78), (40, 60), (20, 60)], fill=WH)
    _r(d, s, (28, 58, 40, 80), 3, fill=WH)
    d.arc([70 * s, 34 * s, 92 * s, 66 * s], 300, 60, fill=WH, width=int(5 * s))


def p_kum_saati(d, s, c):
    _r(d, s, (24, 14, 76, 22), 3, fill=WH)
    _r(d, s, (24, 78, 76, 86), 3, fill=WH)
    _poly(d, s, [(30, 22), (70, 22), (54, 50), (70, 78), (30, 78), (46, 50)], fill=WH)
    _poly(d, s, [(38, 70), (62, 70), (50, 58)], fill=c)


def p_konum(d, s, c):
    _e(d, s, (26, 12, 74, 60), fill=WH)
    _poly(d, s, [(30, 46), (70, 46), (50, 86)], fill=WH)
    _e(d, s, (40, 26, 60, 46), fill=c)


def p_kamyon(d, s, c):
    _r(d, s, (12, 30, 60, 68), 4, fill=WH)
    _poly(d, s, [(62, 40), (78, 40), (88, 54), (88, 68), (62, 68)], fill=WH)
    for x in (28, 74):
        _e(d, s, (x - 9, 62, x + 9, 80), fill=WH)
        _e(d, s, (x - 4, 67, x + 4, 75), fill=c)


def p_damla(d, s, c):
    _poly(d, s, [(50, 12), (72, 50), (28, 50)], fill=WH)
    _e(d, s, (26, 36, 74, 84), fill=WH)


def p_alev(d, s, c):
    _poly(d, s, [(50, 12), (70, 40), (74, 62), (62, 84), (38, 84), (26, 62), (32, 44), (42, 52)], fill=WH)
    _poly(d, s, [(50, 50), (60, 64), (56, 80), (44, 80), (40, 66)], fill=c)


def p_ilac(d, s, c):
    d.line([(30 * s, 70 * s), (70 * s, 30 * s)], fill=WH, width=int(26 * s))
    _e(d, s, (17, 57, 43, 83), fill=WH)
    _e(d, s, (57, 17, 83, 43), fill=WH)
    d.line([(42 * s, 42 * s), (58 * s, 58 * s)], fill=c, width=int(3 * s))


def p_hastane(d, s, c):
    _r(d, s, (16, 16, 84, 84), 12, fill=WH)
    _r(d, s, (42, 26, 58, 74), 3, fill=c)
    _r(d, s, (26, 42, 74, 58), 3, fill=c)


def p_okul(d, s, c):
    _poly(d, s, [(50, 18), (90, 36), (50, 54), (10, 36)], fill=WH)
    _poly(d, s, [(28, 46), (72, 46), (72, 66), (50, 76), (28, 66)], fill=WH)
    d.line([(84 * s, 38 * s), (84 * s, 64 * s)], fill=WH, width=int(4 * s))


def p_canta(d, s, c):
    _r(d, s, (14, 32, 86, 80), 9, fill=WH)
    _r(d, s, (36, 20, 64, 34), 5, outline=WH, width=int(6 * s))
    d.rectangle([14 * s, 50 * s, 86 * s, 54 * s], fill=c)


def p_sepet(d, s, c):
    _poly(d, s, [(14, 26), (26, 26), (34, 62), (76, 62), (84, 36), (30, 36)], fill=WH)
    _e(d, s, (32, 68, 44, 80), fill=WH)
    _e(d, s, (64, 68, 76, 80), fill=WH)


def p_etiket(d, s, c):
    _poly(d, s, [(16, 20), (52, 20), (86, 54), (54, 86), (16, 50)], fill=WH)
    _e(d, s, (26, 30, 38, 42), fill=c)


def p_yuzde(d, s, c):
    _t(d, s, (50, 52), "%", 62, INTER)


def p_imza(d, s, c):
    d.line([(16 * s, 72 * s), (30 * s, 52 * s), (40 * s, 70 * s), (54 * s, 44 * s), (62 * s, 68 * s), (84 * s, 60 * s)],
           fill=WH, width=int(6 * s), joint="curve")
    d.line([(16 * s, 84 * s), (84 * s, 84 * s)], fill=WH, width=int(3 * s))


def p_yasak(d, s, c):
    _e(d, s, (16, 16, 84, 84), outline=WH, width=int(10 * s))
    d.line([(28 * s, 72 * s), (72 * s, 28 * s)], fill=WH, width=int(10 * s))


def p_elektrik(d, s, c):
    _poly(d, s, [(58, 10), (24, 56), (46, 56), (38, 90), (76, 40), (54, 40), (64, 10)], fill=WH)


def p_uyari(d, s, c):
    _poly(d, s, [(50, 14), (88, 80), (12, 80)], fill=WH)
    _r(d, s, (46, 36, 54, 62), 3, fill=c)
    _e(d, s, (45, 66, 55, 76), fill=c)


def g(ch, path=DJ, size=58):
    def f(d, s, c):
        _t(d, s, (50, 54), ch, size, path)
    return f


# isim: (çizim, renk, Türkçe ad, anahtar kelimeler)
ICONS = {
    "ev": (p_ev, ORANGE, "Ev / Kira", ["kira", "ev ", "konut", "daire", "ev sahibi", "kiracı"]),
    "tapu": (p_belge, BROWN, "Tapu", ["tapu"]),
    "araba": (p_araba, BLUE, "Araç / Trafik", ["araç", "araba", "trafik", "otopark", "hgs", "plaka", "sürücü"]),
    "kart": (p_kart, INDIGO, "Kredi kartı", ["kredi kart", "kart ", "aidat", "çekim", "pos"]),
    "kimlik": (p_kimlik, SLATE, "Kimlik", ["kimlik", "nüfus", "tc kimlik"]),
    "belge": (p_belge, SLATE, "Belge / Dilekçe", ["dilekçe", "belge", "evrak", "rapor", "ihtarname", "sözleşme"]),
    "telefon": (p_telefon, TEAL, "Telefon / Uygulama", ["telefon", "uygulama", "mobil", "hat"]),
    "banka": (p_banka, GREEN, "Banka", ["banka", "mevduat", "kredi", "faiz"]),
    "takvim": (p_takvim, RED, "Takvim / Süre", ["gün içinde", "süre", "tarih", "yıl", "ay içinde"]),
    "kalkan": (p_kalkan, GREEN, "Koruma / Güvenlik", ["koru", "güvenlik", "dolandır", "sigorta"]),
    "kilit": (p_kilit, SLATE, "Gizlilik / KVKK", ["kvkk", "kişisel veri", "gizli", "şifre", "kilit"]),
    "anahtar": (p_anahtar, AMBER, "Anahtar / Erişim", ["anahtar", "giriş"]),
    "para": (p_para, GREEN, "Para / İade", ["para", "iade", "ödeme", "tazminat", "ücret", "tl"]),
    "fis": (p_fis, AMBER, "Fiş / Fatura", ["fatura", "fiş", "dekont", "makbuz"]),
    "koli": (p_koli, BROWN, "Kargo / Ürün", ["kargo", "ürün", "sipariş", "paket", "koli"]),
    "kisi": (p_kisi, BLUE, "Kişi", ["kişi", "vatandaş", "kullanıcı"]),
    "aile": (p_aile, PINK, "Aile", ["aile", "çocuk", "eş ", "anne", "baba", "nafaka", "miras"]),
    "sirket": (p_sirket, SLATE, "Şirket / İşveren", ["şirket", "işveren", "firma", "işyeri", "satıcı"]),
    "tokmak": (p_tokmak, BROWN, "Mahkeme / Dava", ["mahkeme", "dava", "hakim", "icra", "yargıtay", "avukat"]),
    "grafik": (p_grafik, INDIGO, "Artış / Oran", ["artış", "oran", "zam", "enflasyon"]),
    "saat": (p_saat, ORANGE, "Saat / Mesai", ["saat", "mesai", "fazla çalışma"]),
    "buyutec": (p_buyutec, BLUE, "Sorgula / İncele", ["sorgula", "kontrol et", "incele", "araştır"]),
    "sms": (p_sms, TEAL, "Mesaj / SMS", ["sms", "mesaj", "whatsapp", "bildirim"]),
    "kamera": (p_kamera, SLATE, "Fotoğraf / Delil", ["fotoğraf", "ekran görüntüsü", "kamera", "video", "delil"]),
    "megafon": (p_megafon, RED, "Şikayet / Duyuru", ["şikayet", "şikâyet", "cimer", "ihbar"]),
    "kum_saati": (p_kum_saati, PURPLE, "Zamanaşımı", ["zamanaşımı", "bekle", "gecik"]),
    "konum": (p_konum, RED, "Adres / Konum", ["adres", "konum", "şube"]),
    "kamyon": (p_kamyon, ORANGE, "Taşıma / Nakliye", ["nakliye", "taşıma", "teslimat"]),
    "damla": (p_damla, BLUE, "Su", ["su faturası", "su "]),
    "alev": (p_alev, ORANGE, "Doğalgaz / Isınma", ["doğalgaz", "kombi", "ısınma"]),
    "elektrik": (p_elektrik, AMBER, "Elektrik", ["elektrik", "voltaj", "elektrik kesinti", "tedaş", "trafo"]),
    "ilac": (p_ilac, PINK, "İlaç", ["ilaç", "reçete", "eczane"]),
    "hastane": (p_hastane, RED, "Hastane / Sağlık", ["hastane", "acil", "sağlık", "e-nabız", "doktor"]),
    "okul": (p_okul, INDIGO, "Okul / Eğitim", ["okul", "öğrenci", "burs", "kyk", "üniversite", "eğitim"]),
    "canta": (p_canta, SLATE, "İş / Çalışma", ["iş ", "çalışan", "maaş", "işçi", "kıdem", "ihbar tazminat"]),
    "sepet": (p_sepet, GREEN, "Alışveriş", ["alışveriş", "market", "sepet", "e-ticaret"]),
    "etiket": (p_etiket, ORANGE, "Fiyat / Etiket", ["fiyat", "etiket", "indirim", "kampanya"]),
    "yuzde": (p_yuzde, PURPLE, "Yüzde", ["yüzde", "%"]),
    "imza": (p_imza, INDIGO, "İmza / Onay", ["imza", "onayla", "noter"]),
    "yasak": (p_yasak, RED, "Yasak", ["yasak", "asla", "alamaz", "yapamaz"]),
    "uyari": (p_uyari, ORANGE, "Uyarı / Dikkat", ["dikkat", "tuzak", "uyarı", "risk"]),
    "onay": (g("✔", DJ, 62), GREEN, "Onay / Doğru", ["doğru", "onaylandı", "tamam", "hakkın"]),
    "red": (g("✖", DJ, 58), RED, "Red / Yanlış", ["red", "reddedil", "yanlış", "iptal"]),
    "yildiz": (g("★", DJ, 64), AMBER, "Önemli", ["önemli", "ipucu", "püf"]),
    "kalp": (g("❤", DJ, 58), PINK, "Sağlık / Bakım", ["bakım", "engelli", "yaşlı"]),
    "eposta": (g("✉", DJ, 66), BLUE, "E-posta", ["e-posta", "mail", "eposta"]),
    "ucak": (g("✈", DJ, 62), TEAL, "Uçuş / Seyahat", ["uçuş", "uçak", "seyahat", "bagaj", "tatil"]),
    "engelli": (g("♿", DJ, 62), BLUE, "Engelli hakları", ["engelli"]),
    "terazi": (g("⚖", DJ, 62), INDIGO, "Hak / Hukuk", ["hukuk", "kanun", "yasal", "hak", "adalet", "yönetmelik"]),
    "ayar": (g("⚙", DJ, 62), SLATE, "Ayarlar", ["ayar", "tanımla"]),
    "kalem": (g("✎", DJ, 62), BLUE, "Yaz / Doldur", ["yaz", "doldur", "form"]),
    "bayrak": (g("⚑", DJ, 62), RED, "Resmî kurum", ["e-devlet", "bakanlık", "kurum", "devlet", "belediye"]),
    "ok": (g("➜", DJ, 60), BLUE, "Sonraki adım", ["sonra", "ardından"]),
}


@lru_cache(maxsize=512)
def icon(name, size=160, shadow=True):
    """Hazır ikon. Bilinmeyen isim → 'yildiz'."""
    draw, col, _, _ = ICONS.get(name, ICONS["yildiz"])
    S = 4
    n = size * S
    pad = int(n * 0.08)
    im = Image.new("RGBA", (n + pad * 2, n + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + n * 0.05, pad + n, pad + n * 1.03], radius=n * 0.24, fill=(0, 0, 0, 60))
        from PIL import ImageFilter
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(n * 0.04)))
    # gradyan karo
    top = np.array([min(255, v + 40) for v in col], np.float32)
    bot = np.array(col, np.float32) * 0.85
    k = np.linspace(0, 1, n)[:, None, None]
    grad = (top * (1 - k) + bot * k).repeat(n, axis=1)
    tile = Image.fromarray(np.dstack([grad, np.full((n, n), 255, np.float32)]).astype(np.uint8), "RGBA")
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, n - 1, n - 1], radius=n * 0.24, fill=255)
    tile.putalpha(mask)
    hl = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle([n * 0.04, n * 0.03, n * 0.96, n * 0.45], radius=n * 0.2, fill=(255, 255, 255, 34))
    tile.alpha_composite(hl)
    d = ImageDraw.Draw(tile)
    draw(d, n / 100, col + (255,))
    im.alpha_composite(tile, (pad, pad))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


def icon_for_text(text, default="terazi"):
    t = " " + text.lower() + " "
    best, score = default, 0
    for name, (_, _, _, kws) in ICONS.items():
        sc = sum(len(k) for k in kws if k in t)
        if sc > score:
            best, score = name, sc
    return best


def gallery(path="docs/ikon_kutuphanesi.jpg", cols=9):
    names = list(ICONS)
    cw, ch = 220, 250
    rows = (len(names) + cols - 1) // cols
    im = Image.new("RGB", (cols * cw + 40, rows * ch + 120), (246, 247, 249))
    d = ImageDraw.Draw(im)
    d.text((30, 30), f"İKON KÜTÜPHANESİ · {len(names)} ikon · plan JSON'unda adıyla kullan (\"ikon\": \"ad\")",
           font=ImageFont.truetype(INTER, 34), fill=(17, 24, 39))
    for i, n in enumerate(names):
        x, y = 20 + (i % cols) * cw, 100 + (i // cols) * ch
        ic = icon(n, 140)
        im.paste(ic, (x + (cw - ic.width) // 2, y), ic)
        d.text((x + cw / 2, y + 178), n, font=ImageFont.truetype(INTER, 24), fill=(17, 24, 39), anchor="mm")
        d.text((x + cw / 2, y + 208), ICONS[n][2], font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 18),
               fill=(107, 114, 128), anchor="mm")
    im.save(path, quality=90)
    return path
