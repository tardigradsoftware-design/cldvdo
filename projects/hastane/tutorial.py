"""Senaryo: Özel hastane acil servis ücreti iadesi — YATAY adım adım anlatım.
Ekranlar: belge seti, e-Nabız (telefon), e-Devlet→CİMER, SABİM 184, e-Devlet→Tüketici Hakem Heyeti. Maskot: Tokmak."""
import importlib.util
import math
import os
import sys
from functools import lru_cache

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT)

from PIL import Image, ImageDraw

from engine.core import (BLUE, GREEN, INK, RED, SS, WHITE, YELLOW, canvas, card_base, clamp, dtext, finish, font,
                         out_back, out_cubic, path, pill, place, place_anim, prog, render, text_sprite)
from engine.components import draw_cursor, icon_check, icon_x, icon_warn, stamp
from engine.tutorial import CH, CW, H, W, Seg, Tutorial, cam_path, draw_browser, page_to_world
from engine import audio

# elektrik yatay projesindeki ortak ekran parçalarını yeniden kullan
_spec = importlib.util.spec_from_file_location("el_tut", os.path.join(ROOT, "projects", "elektrik", "tutorial.py"))
el = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(el)
el.UPNAMES = ["Fatura.pdf", "Dekont.pdf", "Epikriz_raporu.pdf"]

OUT = os.environ.get("OUT_DIR", "out")
VOICE = os.environ.get("VOICE")
GREYT = (110, 110, 110, 255)
LINE = (215, 215, 215, 255)
TEAL = (20, 150, 160, 255)
DRED = (190, 30, 40, 255)


def S(v):
    return int(v * SS)


typing, keys_for, key_sfx, overlay_rect, cw, browser_in = el.typing, el.keys_for, el.key_sfx, el.overlay_rect, el.cw, el.browser_in


def ctimes(caps, dur):
    """Tutorial altyazı dağılımıyla aynı: her altyazı parçasının başlangıç zamanı."""
    wc = [len(c.split()) + 1 for c in caps]
    tot = sum(wc)
    out, acc = [], 0.0
    for n in wc:
        out.append(acc)
        acc += dur * n / tot
    return out


def dur_for(caps, minimum=0.0, wps=2.7):
    words = sum(len(c.split()) for c in caps)
    return max(minimum, words / wps + 0.8)


# ================================================================ kartlar
@lru_cache(maxsize=8)
def receipt(n):
    w, h = 640, 560
    im, d = card_base(w, h, header=DRED, header_h=84)
    dtext(d, (30, 18), "ÖZEL ••• HASTANESİ", "black", 30, WHITE)
    dtext(d, (30, 52), "ACİL SERVİS · HİZMET FATURASI", "bold", 20, (255, 210, 210, 255))
    rows = [("Muayene", "1.250 TL"), ("Tahlil", "980 TL"), ("Röntgen", "870 TL"), ("Serum", "650 TL")]
    for k, (a, b) in enumerate(rows[:n]):
        dtext(d, (40, 120 + k * 64), a, "bold", 32, GREYT)
        dtext(d, (w - 40, 120 + k * 64), b, "black", 34, INK, "ra")
    if n >= 4:
        d.line([S(40), S(392), S(w - 40), S(392)], fill=INK, width=S(4))
        dtext(d, (40, 420), "TOPLAM", "black", 38)
        dtext(d, (w - 40, 414), "3.750 TL", "black", 48, RED, "ra")
    return finish(im)


@lru_cache(maxsize=1)
def acil_sign():
    w, h = 420, 300
    im, d = card_base(w, h, fill=DRED, radius=26)
    d.rounded_rectangle([S(170), S(40), S(250), S(200)], S(10), fill=WHITE)
    d.rounded_rectangle([S(130), S(80), S(290), S(160)], S(10), fill=WHITE)
    dtext(d, (w / 2, 250), "ACİL", "black", 54, WHITE, "mm")
    return finish(im)


@lru_cache(maxsize=4)
def sut_card(hl):
    w, h = 900, 520
    im, d = card_base(w, h, header=(30, 50, 100, 255), header_h=84)
    dtext(d, (34, 22), "SAĞLIK UYGULAMA TEBLİĞİ (SUT)", "black", 36, WHITE)
    for k in range(3):
        d.rounded_rectangle([S(40), S(120 + k * 36), S(40 + [780, 720, 600][k]), S(138 + k * 36)], S(8), fill=(225, 225, 225, 255))
    if hl:
        d.rounded_rectangle([S(34), S(240), S(866), S(360)], S(12), fill=(255, 236, 150, 255))
    dtext(d, (50, 250), "Acil hallerde özel sağlık kuruluşları", "black", 36, INK)
    dtext(d, (50, 300), "kişilerden ilave ücret talep edemez.", "black", 36, RED)
    for k in range(2):
        d.rounded_rectangle([S(40), S(400 + k * 36), S(40 + [700, 500][k]), S(418 + k * 36)], S(8), fill=(225, 225, 225, 255))
    return finish(im)


STEPS5 = [("Belgeleri al", "fatura · dekont · epikriz"), ("e-Nabız kontrol", "Acil Servis mi?"), ("CİMER şikâyeti", "SGK'ya, e-Devlet'ten"),
          ("SABİM 184", "paralel kayıt"), ("B planı", "Hakem Heyeti")]


@lru_cache(maxsize=8)
def step5_card(k):
    im, d = card_base(330, 230)
    d.ellipse([S(24), S(24), S(90), S(90)], fill=RED, outline=INK, width=S(4))
    dtext(d, (57, 57), str(k + 1), "black", 38, WHITE, "mm")
    dtext(d, (24, 122), STEPS5[k][0], "black", 32, INK)
    dtext(d, (24, 170), STEPS5[k][1], "semi", 22, GREYT)
    return finish(im)


@lru_cache(maxsize=1)
def slip_card():
    w, h = 300, 420
    im, d = card_base(w, h, fill=(252, 252, 248, 255))
    dtext(d, (w / 2, 40), "POS SLİBİ", "black", 30, INK, "mt")
    for k in range(6):
        d.line([S(36), S(110 + k * 34), S(w - 36 - (k % 3) * 30), S(110 + k * 34)], fill=(200, 200, 200, 255), width=S(5))
    dtext(d, (w / 2, 340), "3.750 TL", "black", 40, INK, "mm")
    return finish(im)


@lru_cache(maxsize=8)
def doc_card(title, sub, color):
    w, h = 420, 250
    im, d = card_base(w, h, header=color, header_h=64)
    dtext(d, (24, 16), title, "black", 28, WHITE)
    dtext(d, (24, 90), sub, "bold", 24, GREYT)
    for k in range(3):
        d.rounded_rectangle([S(24), S(140 + k * 30), S(24 + [360, 320, 240][k]), S(154 + k * 30)], S(7), fill=(225, 225, 225, 255))
    return finish(im)


@lru_cache(maxsize=1)
def law_badge():
    w, h = 760, 150
    im, d = card_base(w, h, fill=(236, 243, 255, 255), radius=22)
    dtext(d, (30, 26), "HASTA HAKLARI YÖNETMELİĞİ", "black", 32, (30, 50, 100, 255))
    dtext(d, (30, 82), "Tıbbi kayıtlarının örneğini almak yasal hakkın.", "bold", 28, INK)
    return finish(im)


# ---------------------------------------------------------------- e-Nabız telefon ekranları (stilize)
PX, PY = 560, 540
SW, SHH = 438, 800
SX0, SY0 = PX - SW / 2, PY - 404


def to_w(sx, sy):
    return SX0 + sx, SY0 + sy


@lru_cache(maxsize=16)
def enabiz_screen(state, hl=False):
    im, d = canvas(SW, SHH)
    d.rounded_rectangle([0, 0, S(SW), S(SHH)], S(40), fill=(246, 248, 250, 255))
    d.rounded_rectangle([0, 0, S(SW), S(150)], S(40), fill=TEAL)
    d.rectangle([0, S(100), S(SW), S(150)], fill=TEAL)
    dtext(d, (SW / 2, 100), "e-Nabız", "black", 40, WHITE, "mm")
    for k in range(3):
        d.rounded_rectangle([S(26), S(84 + k * 12), S(62), S(90 + k * 12)], S(3), fill=WHITE)
    if state == "home":
        for k, lab in enumerate(["Randevularım", "Tahlillerim", "Reçetelerim", "Raporlarım"]):
            c, r = k % 2, k // 2
            x0, y0 = 24 + c * 200, 190 + r * 200
            d.rounded_rectangle([S(x0), S(y0), S(x0 + 186), S(y0 + 180)], S(20), fill=WHITE, outline=LINE, width=S(2))
            d.ellipse([S(x0 + 60), S(y0 + 30), S(x0 + 126), S(y0 + 96)], fill=(210, 236, 238, 255))
            dtext(d, (x0 + 93, y0 + 136), lab, "bold", 22, INK, "mm")
    elif state == "menu":
        d.rectangle([0, S(150), S(SW), S(SHH)], fill=(120, 120, 120, 255))
        d.rectangle([0, S(150), S(320), S(SHH)], fill=WHITE)
        for k, lab in enumerate(["Ana Sayfa", "Ziyaretlerim", "Reçetelerim", "Tahlillerim", "Raporlarım", "Ayarlar"]):
            y = 180 + k * 86
            if k == 1 and hl:
                d.rectangle([0, S(y - 10), S(320), S(y + 60)], fill=(220, 242, 244, 255))
            dtext(d, (30, y + 10), lab, "black" if k == 1 else "semi", 30, TEAL if k == 1 else INK)
    elif state == "list":
        dtext(d, (26, 180), "Ziyaretlerim", "black", 34, INK)
        rows = [("21.11.2026", "Özel ••• Hastanesi"), ("03.09.2026", "••• Devlet Hastanesi"), ("14.05.2026", "Aile Hekimliği")]
        for k, (a, b) in enumerate(rows):
            y = 250 + k * 130
            sel = k == 0 and hl
            d.rounded_rectangle([S(20), S(y), S(SW - 20), S(y + 112)], S(16), fill=(220, 242, 244, 255) if sel else WHITE,
                                outline=TEAL if sel else LINE, width=S(3 if sel else 2))
            dtext(d, (40, y + 18), a, "bold", 22, GREYT)
            dtext(d, (40, y + 56), b, "black", 28, INK)
    elif state == "detail":
        dtext(d, (26, 180), "Ziyaret Detayı", "black", 34, INK)
        dtext(d, (26, 236), "Özel ••• Hastanesi · 21.11.2026", "semi", 22, GREYT)
        d.rounded_rectangle([S(20), S(280), S(SW - 20), S(380)], S(16), fill=(236, 248, 241, 255), outline=GREEN, width=S(4))
        dtext(d, (40, 296), "Bölüm", "bold", 22, GREYT)
        dtext(d, (40, 330), "ACİL SERVİS", "black", 34, GREEN)
        d.rounded_rectangle([S(20), S(400), S(SW - 20), S(500)], S(16), fill=WHITE, outline=LINE, width=S(2))
        dtext(d, (40, 416), "Tanı kodu", "bold", 22, GREYT)
        dtext(d, (40, 450), "R10.4 · Karın ağrısı", "black", 30, INK)
        for k in range(3):
            d.rounded_rectangle([S(20), S(530 + k * 60), S(SW - 20 - k * 60), S(560 + k * 60)], S(8), fill=(228, 228, 228, 255))
    return finish(im)


# ---------------------------------------------------------------- CİMER (stilize)
C_RADIO = [(60 + k * 235, 150, 60 + k * 235 + 220, 200) for k in range(4)]
C_RADIO_LAB = ["Bilgi Edinme", "Şikayet", "Öneri", "İhbar"]
C_TEXT = (60, 250, 1000, 460)
C_IBAN = (60, 530, 1000, 590)
C_ADD = (1080, 150, 1688, 200)
C_UP = [(1080, 215 + k * 68, 1688, 275 + k * 68) for k in range(4)]
C_UPN = ["Fatura.pdf", "Dekont.pdf", "Epikriz_raporu.pdf", "eNabiz_ekran.jpg"]
C_KURUM = (1080, 530, 1688, 590)
C_OK = (1080, 620, 1688, 684)
C_LINES = ["21.11.2026 tarihinde Özel ••• Hastanesi acil servisine",
           "başvurdum. SUT'a aykırı olarak 3.750 TL ilave ücret",
           "tahsil edilmiştir. Tutarın hesabıma iadesini ve",
           "hastaneye yaptırım uygulanmasını talep ederim."]
C_TXT = "\n".join(C_LINES)
V_IBAN = "IBAN: TR•• •••• •••• •••• 4821"


def cimer_header(d):
    d.rectangle([0, 0, S(CW), S(92)], fill=(200, 24, 40, 255))
    d.ellipse([S(36), S(18), S(92), S(74)], fill=WHITE)
    dtext(d, (64, 46), "C", "black", 34, (200, 24, 40, 255), "mm")
    dtext(d, (110, 46), "CİMER · Cumhurbaşkanlığı İletişim Merkezi", "black", 30, WHITE, "lm")


@lru_cache(maxsize=1024)
def page_cimer(radio, text_n, iban, focus, ups, kurum, pressed):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=WHITE)
    cimer_header(d)
    dtext(d, (60, 116), "Başvuru Türü", "bold", 22, (70, 70, 70, 255))
    for k, (box, lab) in enumerate(zip(C_RADIO, C_RADIO_LAB)):
        x0, y0, x1, y1 = box
        sel = radio == k
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(10), fill=(255, 236, 236, 255) if sel else WHITE,
                            outline=RED if sel else LINE, width=S(3))
        d.ellipse([S(x0 + 14), S(y0 + 14), S(x0 + 36), S(y0 + 36)], outline=INK, width=S(3), fill=RED if sel else WHITE)
        dtext(d, (x0 + 48, (y0 + y1) / 2), lab, "bold", 22, INK, "lm")
    dtext(d, (60, 216), "Başvuru Metni", "bold", 22, (70, 70, 70, 255))
    x0, y0, x1, y1 = C_TEXT
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(10), fill=WHITE, outline=RED if focus == "text" else (190, 190, 190, 255),
                        width=S(4 if focus == "text" else 2))
    shown = C_TXT[:text_n].split("\n")
    for k, ln in enumerate(shown):
        dtext(d, (x0 + 18, y0 + 18 + k * 46), ln, "semi", 25, INK)
    el.field(d, C_IBAN, "IBAN (kendi adına kayıtlı)", iban, focus == "iban")
    dtext(d, (1080, 116), "Belgeler", "bold", 22, (70, 70, 70, 255))
    bx0, by0, bx1, by1 = C_ADD
    d.rounded_rectangle([S(bx0), S(by0), S(bx1), S(by1)], S(10), fill=(30, 50, 100, 255))
    dtext(d, ((bx0 + bx1) / 2, (by0 + by1) / 2), "+ Belge Ekle", "black", 24, WHITE, "mm")
    for k in range(ups):
        x0, y0, x1, y1 = C_UP[k]
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(10), fill=(240, 250, 244, 255), outline=GREEN, width=S(3))
        nm = C_UPN[k]
        d.rounded_rectangle([S(x0 + 14), S(y0 + 10), S(x0 + 54), S(y1 - 10)], S(6), fill=RED if nm.endswith("pdf") else BLUE)
        dtext(d, (x0 + 70, (y0 + y1) / 2), nm, "bold", 24, INK, "lm")
        ck = icon_check(34)
        d._image.alpha_composite(ck.resize((ck.width * SS, ck.height * SS)), (S(x1 - 50), S((y0 + y1) / 2 - 17)))
    el.field(d, C_KURUM, "İlgili Kurum", kurum, focus == "kurum")
    if kurum:
        dtext(d, (1660, 560), "▾", "black", 24, GREYT, "rm")
    x0, y0, x1, y1 = C_OK
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=(170, 20, 30, 255) if pressed else (200, 24, 40, 255))
    dtext(d, ((x0 + x1) / 2, (y0 + y1) / 2), "Başvuruyu Onayla", "black", 30, WHITE, "mm")
    return finish(im)


@lru_cache(maxsize=64)
def page_ed_search(typed, focus, sugg, hover):
    """e-Devlet ana sayfa, CİMER önerili."""
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=WHITE)
    d.rectangle([0, S(92), S(CW), S(400)], fill=(253, 241, 240, 255))
    el.ed_header(d)
    dtext(d, (874, 150), "Size nasıl yardımcı olabilirim?", "black", 44, INK, "mm")
    x0, y0, x1, y1 = el.SEARCH
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=WHITE, outline=RED if focus else (190, 190, 190, 255), width=S(4 if focus else 3))
    dtext(d, (x0 + 28, (y0 + y1) / 2), typed or "Hizmet, kurum veya belge ara", "semi", 32, INK if typed else (165, 165, 165, 255), "lm")
    if focus:
        cx = x0 + 28 + font("semi", 32 * SS).getlength(typed) / SS + 3
        d.rectangle([S(cx), S(y0 + 22), S(cx + 3), S(y1 - 22)], fill=INK)
    d.rounded_rectangle([S(1310), S(y0), S(1424), S(y1)], S(12), fill=RED)
    dtext(d, (1367, (y0 + y1) / 2), "Ara", "black", 30, WHITE, "mm")
    if sugg:
        top = y1 - 4
        d.rounded_rectangle([S(x0), S(top), S(x1), S(top + 86)], S(12), fill=WHITE, outline=(190, 190, 190, 255), width=S(3))
        if hover:
            d.rectangle([S(x0 + 4), S(top + 4), S(x1 - 4), S(top + 82)], fill=(255, 236, 235, 255))
        d.rounded_rectangle([S(x0 + 22), S(top + 18), S(x0 + 70), S(top + 66)], S(10), fill=(200, 24, 40, 255))
        dtext(d, (x0 + 46, top + 42), "C", "black", 22, WHITE, "mm")
        dtext(d, (x0 + 88, top + 14), "Cumhurbaşkanlığı İletişim Merkezi (CİMER)", "black", 28, INK)
        dtext(d, (x0 + 88, top + 50), "Başvuru yap", "semi", 20, GREYT)
    return finish(im)


# ---------------------------------------------------------------- SABİM
@lru_cache(maxsize=8)
def sabim_form(n):
    w, h = 760, 500
    im, d = card_base(w, h, header=(30, 50, 100, 255), header_h=80)
    dtext(d, (30, 20), "SAĞLIK BAKANLIĞI · ŞİKÂYET", "black", 32, WHITE)
    rows = [("Konu", "Haksız acil servis ücreti"), ("Hastane", "Özel ••• Hastanesi"), ("Fatura No", "AS-2026-00418"),
            ("Tarih", "21.11.2026")]
    for k, (a, b) in enumerate(rows[:n]):
        y = 112 + k * 88
        dtext(d, (36, y), a, "bold", 24, GREYT)
        d.rounded_rectangle([S(36), S(y + 32), S(w - 36), S(y + 76)], S(8), fill=(248, 248, 248, 255), outline=LINE, width=S(2))
        dtext(d, (52, y + 54), b, "black", 26, INK, "lm")
    return finish(im)


@lru_cache(maxsize=2)
def inst_badge(label, color):
    return pill(label, "black", 40, WHITE, color, border=4, pad=(28, 16), shadow=6)


@lru_cache(maxsize=1)
def incoming_call():
    w, h = 680, 200
    im, d = card_base(w, h, radius=34, fill=(30, 34, 44, 255))
    d.ellipse([S(30), S(50), S(130), S(150)], fill=(90, 100, 120, 255))
    dtext(d, (80, 100), "H", "black", 50, WHITE, "mm")
    dtext(d, (160, 46), "Özel ••• Hastanesi arıyor…", "black", 32, WHITE)
    dtext(d, (160, 100), "“Uzlaşalım, iadenizi hemen yapalım.”", "semi", 26, (200, 220, 255, 255))
    d.ellipse([S(w - 120), S(60), S(w - 40), S(140)], fill=GREEN)
    return finish(im)


@lru_cache(maxsize=2)
def end_card():
    return pill("ABONE OL", "black", 64, WHITE, RED, border=5, pad=(44, 22), shadow=8)


# ================================================================ segmentler
CAP_HOOK = ["özel hastanenin *ACİL SERVİSİNE* başvurduğunda", "senden *MUAYENE* tahlil röntgen veya serum",
            "adı altında ücret alındıysa", "ödediğin parayı *KURUŞU KURUŞUNA* geri alabilirsin"]
CAP_LAW = ["*SAĞLIK UYGULAMA TEBLİĞİ'NE* göre", "hastanenin *SGK ANLAŞMASI* olsun ya da olmasın",
           "acil hallerde hiçbir özel hastane", "vatandaştan *TEK KURUŞ* ilave ücret alamaz"]
CAP_OVR = ["şimdi hastanelerin en sık kullandığı *TUZAKLARA* düşmeden", "paranı nasıl geri alacağını *BEŞ NET ADIMDA* anlatıyorum"]
CAP_S1 = ["birinci adım çıkışta *BELGELERİ* eksiksiz almak",
          "acil anda tartışmak istemeyip ödemeyi yaptıysan bile",
          "hastaneden asla *SADECE KREDİ KARTI SLİBİYLE* ayrılma",
          "bankodan mutlaka şu *ÜÇ BELGEYİ* iste",
          "yapılan tüm işlemlerin kalem kalem yazılı olduğu *DETAYLI HİZMET FATURASI*",
          "*ÖDEME DEKONTU*",
          "ve doktorun acil müdahaleyi yazdığı *ACİL SERVİS EPİKRİZ RAPORU*",
          "epikriz raporunu vermekten kaçınırlarsa",
          "*HASTA HAKLARI YÖNETMELİĞİ* gereği",
          "tıbbi kayıt örneğini almanın *YASAL HAKKIN* olduğunu hatırlat"]
CAP_S2 = ["ikinci adım en sık yapılan *YEŞİL ALAN VE POLİKLİNİK* tuzağını kontrol etmek",
          "bazı özel hastaneler ücret alabilmek için",
          "sisteme girişini acil servis yerine *NORMAL POLİKLİNİK*",
          "veya acil olmayan *YEŞİL ALAN* olarak işler",
          "telefonundan *e-NABIZ* uygulamasına gir",
          "sol menüden *ZİYARETLERİM* sekmesine tıkla",
          "ve ilgili hastane kaydını aç",
          "burada bölüm adının *ACİL SERVİS* göründüğünü",
          "ve tanı kodlarını kontrol edip *EKRAN GÖRÜNTÜSÜ* al",
          "eğer acil bir durumla gittiğin halde girişin *POLİKLİNİK* gösterildiyse",
          "şikayet metninde bunu *ÖZELLİKLE BELİRT*"]
CAP_S3 = ["üçüncü adım e-Devlet üzerinden resmi *SGK ŞİKAYETİNİ* açmak",
          "e-Devlet'e giriş yap ve arama çubuğuna *CİMER* yazıp",
          "Cumhurbaşkanlığı İletişim Merkezi uygulamasına git",
          "başvuru türü olarak mutlaka *ŞİKAYET* seçeneğini işaretle",
          "metin kutusuna olayı *KISA VE NET* yaz",
          "şu tarihte şu özel hastanenin acil servisine başvurduğunu",
          "*SUT'A AYKIRI* olarak şu tutarda haksız ilave ücret tahsil edildiğini",
          "ve tutarın *İADESİ* ile hastaneye yaptırım uygulanmasını talep ettiğini belirt",
          "alt satıra kendi adına kayıtlı *IBAN* numaranı ekle",
          "belge ekle butonundan *FATURANI DEKONTUNU*",
          "epikriz raporunu ve *e-NABIZ* ekran görüntünü yükle",
          "kurum seçiminde *SOSYAL GÜVENLİK KURUMU'NU* işaretleyip",
          "başvuruyu *ONAYLA*"]
CAP_S4 = ["dördüncü adım *SAĞLIK BAKANLIĞI* hattından paralel kayıt açmak",
          "süreci hızlandırmak için *184 NUMARALI SABİM* hattını ara",
          "veya Sağlık Bakanlığı online şikayet sistemine gir",
          "aynı hastane adı *FATURA NUMARASI* ve tarihle",
          "*HAKSIZ ACİL SERVİS ÜCRETİ* bildirimi oluştur",
          "iki kurumdan birden *DENETİM* açıldığında",
          "hastane genellikle seni arayıp *UZLAŞMA VE HIZLI İADE* teklif eder"]
CAP_S5 = ["beşinci adım *B PLANI*",
          "hastane iadeyi geciktirir veya SGK incelemesi uzarsa",
          "elindeki aynı belgelerle *e-DEVLET* üzerinden",
          "*TÜKETİCİ HAKEM HEYETLERİNE BAŞVURU* ekranına girip",
          "doğrudan *BEDEL İADESİ* talebi açabilirsin",
          "*ÜCRETSİZ* olan bu başvuruyla karar çıktığında",
          "paran yasal olarak *HESABINA YATIRILIR*",
          "ayrıca hastaneye SGK tarafından", "yüksek oranda *İDARİ PARA CEZASI* kesilir"]


def seg_hook(dur):
    tt = ctimes(CAP_HOOK, dur)

    def f(world, t, d):
        place_anim(world, acil_sign(), 420, 380, t, d, "pop", -1, 0.3, -4)
        l1 = text_sprite("ACİL SERVİSTE", "black", 64, INK)
        l2 = text_sprite("PARA MI ÖDEDİN?", "black", 78, RED)
        place(world, l1, 420, 650)
        place(world, l2, 420, 740)
        n = 0 if t < tt[1] else min(4, 1 + int((t - tt[1]) / ((tt[2] - tt[1]) / 3.2)))
        place_anim(world, receipt(max(n, 0)), 1300, 470, t, d, "drop", -1, 0.3, 2)
        place_anim(world, stamp("KURUŞU KURUŞUNA GERİ ✓", 56, GREEN), 1300, 830, t, d, "stamp", tt[3] + 0.4, 0.25, -5)
        z = 1 + 0.06 * (1 - out_cubic(prog(t, 0, 0.4)))
        return {"cam": (z, W / 2, H / 2), "mascot": "saskin" if t < tt[3] else "mutlu"}
    sfx = [(0, "impact")] + [(tt[1] + k * (tt[2] - tt[1]) / 3.2, "pop") for k in range(4)] + [(tt[3] + 0.4, "impact")]
    return f, sfx


def seg_law(dur):
    tt = ctimes(CAP_LAW, dur)

    def f(world, t, d):
        place_anim(world, sut_card(t > tt[2]), 700, 470, t, d, "pop", 0.0, 0.35)
        place_anim(world, pill("SGK anlaşmalı ✓", "black", 36, WHITE, GREEN, border=4, pad=(22, 12), shadow=5), 1490, 330, t, d, "right", tt[1] + 0.3)
        place_anim(world, pill("SGK anlaşmasız ✓", "black", 36, WHITE, GREEN, border=4, pad=(22, 12), shadow=5), 1490, 430, t, d, "right", tt[1] + 0.9)
        place_anim(world, text_sprite("İLAVE ÜCRET", "black", 54, INK), 1490, 590, t, d, "up", tt[3])
        place_anim(world, text_sprite("0 TL", "black", 150, RED, 6, WHITE), 1490, 720, t, d, "stamp", tt[3] + 0.3, 0.25)
        return {"mascot": "ciddi:isaret"}
    return f, [(tt[1] + 0.3, "ding"), (tt[1] + 0.9, "ding"), (tt[2], "whoosh"), (tt[3] + 0.3, "impact")]


def seg_overview(dur):
    tt = ctimes(CAP_OVR, dur)

    def f(world, t, d):
        place_anim(world, stamp("TUZAK!", 70), 1600, 200, t, d, "stamp", 0.3, 0.25, 8)
        t1 = text_sprite("5 NET ADIM", "black", 110, RED)
        place_anim(world, t1, 90 + t1.width / 2, 230, t, d, "left", tt[1])
        for k in range(5):
            place_anim(world, step5_card(k), 200 + k * 380, 640, t, d, "pop", tt[1] + 0.3 + k * 0.35, 0.35, [-3, 2, -2, 3, -2][k])
        return {"mascot": "ciddi:isaret"}
    return f, [(0.3, "impact")] + [(tt[1] + 0.3 + k * 0.35, "pop") for k in range(5)]


def seg_s1(dur):
    tt = ctimes(CAP_S1, dur)

    def f(world, t, d):
        if t < tt[3]:
            place_anim(world, slip_card(), 960, 500, t, tt[3] + 0.2, "drop", 0.2, 0.35, -3)
            if t > tt[2]:
                place_anim(world, icon_x(160), 960, 500, t, tt[3] + 0.2, "stamp", tt[2] + 0.3, 0.25)
                place_anim(world, stamp("SADECE SLİP YETMEZ", 52), 960, 820, t, tt[3] + 0.2, "stamp", tt[2] + 0.5, 0.25, -4)
            return {"mascot": "kizgin" if t > tt[2] else "ciddi"}
        docs = [("DETAYLI FATURA", "kalem kalem tüm işlemler", (30, 50, 100, 255), tt[4]),
                ("ÖDEME DEKONTU", "ödediğin tutar", (24, 140, 90, 255), tt[5]),
                ("EPİKRİZ RAPORU", "acil müdahale kaydı", DRED, tt[6])]
        place_anim(world, text_sprite("BANKODAN 3 BELGE İSTE", "black", 70, INK), W / 2, 200, t, d, "up", tt[3])
        for k, (a, b, c, t0) in enumerate(docs):
            x = 380 + k * 580
            place_anim(world, doc_card(a, b, c), x, 470, t, d, "drop", t0, 0.4, [-3, 2, -2][k])
            place_anim(world, icon_check(76), x + 180, 350, t, d, "pop", t0 + 0.6, 0.3)
        if t > tt[7]:
            place_anim(world, law_badge(), W / 2, 760, t, d, "up", tt[7] + 0.4, 0.4)
        return {"mascot": "goz_kirp" if t > tt[9] else "ciddi:isaret"}
    sfx = [(0.2, "pop"), (tt[2] + 0.3, "error"), (tt[2] + 0.5, "impact"), (tt[3], "whoosh")] + \
          [(x, "pop") for x in (tt[4], tt[5], tt[6])] + [(x + 0.6, "ding") for x in (tt[4], tt[5], tt[6])] + [(tt[7] + 0.4, "ding")]
    return f, sfx


def seg_s2(dur):
    tt = ctimes(CAP_S2, dur)
    T_APP, T_MENU, T_ZIY, T_REC = tt[4], tt[5], tt[5] + (tt[6] - tt[5]) * 0.6, tt[6]
    T_SHOT = tt[8] + (tt[9] - tt[8]) * 0.5

    def f(world, t, d):
        if t < T_APP:
            # tuzak açıklaması: Acil Servis yerine Poliklinik / Yeşil Alan
            place_anim(world, text_sprite("HASTANE KAYDI NASIL GİRİLDİ?", "black", 60, INK), W / 2, 220, t, T_APP + 0.2, "up", 0.0)
            place_anim(world, pill("ACİL SERVİS ✓", "black", 54, WHITE, GREEN, border=5, pad=(30, 18), shadow=6), 560, 520, t, T_APP + 0.2, "pop", 0.6)
            place_anim(world, pill("POLİKLİNİK ✗", "black", 54, WHITE, RED, border=5, pad=(30, 18), shadow=6), 1360, 460, t, T_APP + 0.2, "pop", tt[2])
            place_anim(world, pill("YEŞİL ALAN ✗", "black", 54, WHITE, RED, border=5, pad=(30, 18), shadow=6), 1360, 600, t, T_APP + 0.2, "pop", tt[3])
            place_anim(world, stamp("ÜCRET ALMAK İÇİN!", 50, INK), 1360, 780, t, T_APP + 0.2, "stamp", tt[3] + 0.8, 0.25, -6)
            return {"mascot": "kizgin" if t > tt[2] else "dusunceli"}
        place_anim(world, el.phone_frame(), PX, PY, t, d, "up", T_APP, 0.35)
        if t < T_MENU:
            scr = enabiz_screen("home")
        elif t < T_ZIY + 0.2:
            scr = enabiz_screen("menu", t > T_ZIY - 0.4)
        elif t < T_REC + 0.3:
            scr = enabiz_screen("list", t > T_REC - 0.3)
        else:
            scr = enabiz_screen("detail")
        if t > T_APP + 0.3:
            place(world, scr, PX, SY0 + SHH / 2)
        ham = to_w(44, 96)
        ziy = to_w(120, 296)
        rec = to_w(220, 306)
        x, y = path(t, [(T_APP, 1100, 900), (T_MENU - 0.4, *ham), (T_MENU + 0.3, *ham), (T_ZIY - 0.4, *ziy), (T_ZIY + 0.3, *ziy),
                        (T_REC - 0.4, *rec), (T_REC + 0.5, *rec), (T_REC + 1.2, 1100, 900)])
        if t < T_REC + 1.2:
            draw_cursor(world, x, y, t, (T_MENU, T_ZIY, T_REC), 44)
        if t > T_REC + 0.3:
            a = to_w(SW / 2, 330)
            place_anim(world, pill("BÖLÜM: ACİL SERVİS ✓", "black", 40, WHITE, GREEN, border=4, pad=(24, 14), shadow=6),
                       1300, 360, t, d, "right", tt[7], 0.4)
            place_anim(world, pill("Tanı kodunu da kontrol et", "black", 34, INK, WHITE, border=4, pad=(22, 12), shadow=5),
                       1300, 470, t, d, "right", tt[8], 0.4)
        if T_SHOT <= t < T_SHOT + 0.25:
            overlay_rect(world, (int(SX0), int(SY0), int(SX0 + SW), int(SY0 + SHH)), (255, 255, 255, int(220 * (1 - (t - T_SHOT) / 0.25))))
        place_anim(world, pill("EKRAN GÖRÜNTÜSÜ ALINDI ✓", "black", 34, WHITE, INK, pad=(22, 12)), PX, PY + 470, t, d, "pop", T_SHOT + 0.1)
        if t > tt[9]:
            place_anim(world, icon_warn(100), 1060, 660, t, d, "pop", tt[9], 0.3)
            place_anim(world, pill("Poliklinik yazıyorsa", "black", 36, WHITE, RED, border=4, pad=(22, 12), shadow=5), 1380, 640, t, d, "right", tt[9] + 0.2)
            place_anim(world, stamp("ŞİKAYETTE BELİRT!", 50), 1380, 760, t, d, "stamp", tt[10], 0.25, -5)
        cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (T_APP + 0.4, 1.0, W / 2, H / 2), (T_MENU - 0.3, 1.3, PX + 120, PY - 60),
                           (T_REC + 0.8, 1.3, PX + 120, PY - 60), (T_REC + 1.4, 1.0, W / 2, H / 2)])
        return {"cam": cam, "mascot": "saskin" if t > tt[9] else "ciddi"}
    sfx = [(0.6, "pop"), (tt[2], "error"), (tt[3], "error"), (tt[3] + 0.8, "impact"), (T_APP, "whoosh"),
           (T_MENU, "click"), (T_ZIY, "click"), (T_REC, "click"), (tt[7], "ding"), (T_SHOT, "tick"), (T_SHOT + 0.1, "ding"),
           (tt[9], "error"), (tt[10], "impact")]
    return f, sfx


def seg_s3(dur):
    tt = ctimes(CAP_S3, dur)
    Q = "cimer"
    Q0 = tt[1] + 0.4
    SUG = Q0 + 3 / 10
    CLK = tt[2] + 0.5
    RAD = tt[3] + 0.6
    TX0 = tt[4] + 0.2
    TX_CPS = len(C_TXT) / max(3.0, (tt[8] - TX0 - 0.3))
    IB0 = tt[8] + 0.3
    UP0 = [tt[9] + 0.2, tt[9] + 0.9, tt[10] + 0.2, tt[10] + 0.9]
    KUR = tt[11] + 0.3
    OK = tt[12] + 0.2

    def f(world, t, d):
        if t < CLK + 0.3:
            typed = typing(t, Q0, Q.upper(), 8)
            page = page_ed_search(typed, t > Q0 - 0.3, t > SUG, t > CLK - 0.6)
            url = "www.turkiye.gov.tr"
        else:
            tn = int(clamp((t - TX0) * TX_CPS, 0, len(C_TXT)))
            iban = typing(t, IB0, V_IBAN, 16)
            ups = sum(1 for u in UP0 if t > u + 0.2)
            focus = "text" if TX0 - 0.2 < t < IB0 - 0.2 else "iban" if IB0 - 0.2 <= t < UP0[0] - 0.3 else \
                "kurum" if KUR - 0.1 < t < OK - 0.3 else None
            page = page_cimer(1 if t > RAD else -1, tn, iban, focus, ups, "Sosyal Güvenlik Kurumu" if t > KUR + 0.3 else "",
                              OK < t < OK + 0.2)
            url = "www.turkiye.gov.tr/cimer"
        browser_in(world, t, url, page, "e-Devlet · CİMER")
        sw = cw(el.SEARCH)
        sug = page_to_world(el.SEARCH[0] + 320, el.SEARCH[3] + 40)
        pts = [(0, 1100, 900), (Q0 - 0.4, sw[0] - 150, sw[1]), (SUG + 0.6, sw[0] - 150, sw[1]), (CLK - 0.3, *sug), (CLK + 0.3, *sug)]
        r = cw(C_RADIO[1])
        pts += [(RAD - 0.4, *r), (RAD + 0.3, *r)]
        tx = cw(C_TEXT)
        pts += [(TX0 - 0.4, tx[0] + 300, tx[1] + 80), (IB0 - 0.6, tx[0] + 300, tx[1] + 80)]
        ib = cw(C_IBAN)
        pts += [(IB0 - 0.3, ib[0] + 200, ib[1]), (UP0[0] - 0.6, ib[0] + 200, ib[1])]
        ad = cw(C_ADD)
        for u in UP0:
            pts += [(u - 0.3, *ad), (u + 0.3, *ad)]
        ku = cw(C_KURUM)
        pts += [(KUR - 0.3, *ku), (KUR + 0.5, *ku)]
        ok = cw(C_OK)
        pts += [(OK - 0.3, *ok), (d, *ok)]
        x, y = path(t, pts)
        draw_cursor(world, x, y, t, (Q0 - 0.3, CLK, RAD, TX0 - 0.2, IB0 - 0.2) + tuple(UP0) + (KUR, OK), 40)
        if t > OK + 0.3:
            overlay_rect(world, (0, 0, W, H), (20, 20, 20, int(120 * clamp((t - OK - 0.3) / 0.3))))
            place_anim(world, el.success_modal("Başvurunuz alındı", "SGK'ya iletildi"), W / 2, H / 2, t, d, "pop", OK + 0.35, 0.35)
        left = cw((60, 150, 1000, 590))
        right = cw((1080, 150, 1688, 684))
        cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (Q0 - 0.3, 1.5, sw[0], sw[1] + 80), (CLK + 0.1, 1.5, sw[0], sw[1] + 80),
                           (CLK + 0.6, 1.0, W / 2, H / 2), (RAD - 0.4, 1.3, left[0] + 80, left[1] - 40), (UP0[0] - 0.6, 1.3, left[0] + 80, left[1] - 40),
                           (UP0[0] - 0.2, 1.3, right[0] - 60, right[1]), (OK - 0.6, 1.3, right[0] - 60, right[1]), (OK, 1.0, W / 2, H / 2)])
        keys = keys_for(Q0, Q.upper(), 8) + [(TX0 + k / TX_CPS, (c.upper() if c not in " \n" else "Space")) for k, c in enumerate(C_TXT)][::2] + \
            keys_for(IB0, V_IBAN, 16)
        return {"cam": cam, "keys": keys, "mascot": "mutlu" if t > OK + 0.4 else "ciddi"}
    sfx = [(Q0 - 0.3, "click"), (CLK, "click"), (RAD, "click"), (TX0 - 0.2, "click"), (IB0 - 0.2, "click"), (KUR, "click"),
           (OK, "click"), (OK + 0.35, "ding")] + key_sfx(Q0, Q, 8) + [(TX0 + k / TX_CPS, "key") for k in range(0, len(C_TXT), 2)] + \
        key_sfx(IB0, V_IBAN, 16) + [(u, "click") for u in UP0] + [(u + 0.2, "ding") for u in UP0]
    return f, sfx


def seg_s4(dur):
    tt = ctimes(CAP_S4, dur)
    taps = [(tt[1] + 0.6, "1"), (tt[1] + 1.0, "8"), (tt[1] + 1.4, "4")]
    CALL = tt[1] + 2.0

    def f(world, t, d):
        if t < tt[2] + 0.5:
            place_anim(world, el.phone_frame(), el.PH_X, el.PH_Y, t, tt[2] + 0.7, "up", 0.0, 0.35)
            if t > 0.35:
                if t < CALL:
                    pressed = next((k for tt_, k in taps if 0 <= t - tt_ < 0.18), None)
                    place(world, el.keypad_sprite(pressed), el.PH_X, el.PH_Y + 7)
                    num = "".join(k for tt_, k in taps if t >= tt_)
                    place(world, text_sprite(num or " ", "semi", 70, INK), el.PH_X, el.PH_Y - 280)
                    x, y = path(t, [(0, 1100, 900), (taps[0][0] - 0.3, *el.key_pos("1")), (taps[1][0] - 0.1, *el.key_pos("1")),
                                    (taps[1][0], *el.key_pos("8")), (taps[2][0] - 0.1, *el.key_pos("8")), (taps[2][0], *el.key_pos("4")),
                                    (CALL - 0.2, el.PH_X, el.PH_Y + 392)])
                    draw_cursor(world, x, y, t, tuple(a for a, _ in taps) + (CALL - 0.1,), 44)
                else:
                    place(world, text_sprite("184", "black", 96, INK), el.PH_X, el.PH_Y - 250)
                    place(world, text_sprite("SABİM · Sağlık Bakanlığı", "semi", 30, GREYT), el.PH_X, el.PH_Y - 175)
                    place(world, pill("ARANIYOR", "black", 34, WHITE, GREEN, pad=(22, 12)), el.PH_X, el.PH_Y + 80)
            place_anim(world, pill("veya online şikâyet sistemi", "black", 36, INK, WHITE, border=4, pad=(22, 12), shadow=5),
                       1350, 520, t, tt[2] + 0.7, "right", tt[2], 0.35)
            return {"keys": [(a, k) for a, k in taps], "mascot": "ciddi:isaret"}
        n = 0 if t < tt[3] else min(4, 1 + int((t - tt[3]) / 0.6))
        if t < tt[5]:
            place_anim(world, sabim_form(n), 640, 520, t, tt[5] + 0.2, "pop", tt[2] + 0.5, 0.35)
            place_anim(world, stamp("BİLDİRİM OLUŞTUR", 50), 640, 860, t, tt[5] + 0.2, "stamp", tt[4], 0.25, -4)
            return {"mascot": "ciddi"}
        place_anim(world, inst_badge("SGK", (30, 50, 100, 255)), 560, 330, t, d, "drop", tt[5], 0.35)
        place_anim(world, inst_badge("SAĞLIK BAKANLIĞI", (190, 30, 40, 255)), 1300, 330, t, d, "drop", tt[5] + 0.3, 0.35)
        place_anim(world, stamp("ÇİFT DENETİM", 60, INK), 930, 470, t, d, "stamp", tt[5] + 0.8, 0.25, -4)
        place_anim(world, incoming_call(), 930, 720, t, d, "up", tt[6], 0.4)
        return {"mascot": "heyecanli:kutlama" if t > tt[6] + 0.5 else "ciddi"}
    sfx = [(a, "click") for a, _ in taps] + [(CALL - 0.1, "click"), (CALL, "ding"), (tt[2], "pop")] + \
          [(tt[3] + k * 0.6, "pop") for k in range(4)] + [(tt[4], "impact"), (tt[5], "pop"), (tt[5] + 0.3, "pop"),
                                                          (tt[5] + 0.8, "impact"), (tt[6], "ding")]
    return f, sfx


def seg_s5(dur):
    tt = ctimes(CAP_S5, dur)
    Q = "tüketici hakem heyeti"
    Q0 = tt[2] + 0.2
    SUG = Q0 + 6 / 14
    CLK = tt[3] + 0.6
    TUR, KAR0, TUT0 = tt[4] + 0.1, tt[4] + 0.8, tt[4] + 2.4
    UP0, FREE, SEND = tt[5] - 0.6, tt[5] + 0.1, tt[5] + 1.6
    V_KAR = "Özel ••• Hastanesi"

    def f(world, t, d):
        if t < tt[2]:
            place_anim(world, text_sprite("B PLANI", "black", 140, RED), W / 2, 380, t, tt[2] + 0.2, "stamp", 0.0, 0.3)
            place_anim(world, pill("İade gecikirse  ·  SGK incelemesi uzarsa", "black", 40, INK, WHITE, border=4, pad=(26, 14), shadow=5),
                       W / 2, 600, t, tt[2] + 0.2, "up", tt[1])
            return {"mascot": "dusunceli"}
        if t < tt[6]:
            lt = t
            if lt < CLK + 0.3:
                page = el.page_ed_home(typing(lt, Q0, Q, 14), lt > Q0 - 0.3, lt > SUG, lt > CLK - 0.6)
                url = "www.turkiye.gov.tr"
            else:
                tur = "Ayıplı Hizmet — Sağlık" if lt > TUR + 0.3 else ""
                kar = typing(lt, KAR0, V_KAR, 14)
                tut = typing(lt, TUT0, "3.750 TL", 12)
                focus = "tur" if TUR - 0.1 < lt < KAR0 - 0.2 else "karsi" if KAR0 - 0.2 <= lt < TUT0 - 0.2 else \
                    "tutar" if TUT0 - 0.2 <= lt < UP0 - 0.3 else None
                upv = int(clamp((lt - UP0) / 0.7, 0, 1) * 10)
                page = el.page_thh(tur, kar, tut, focus, upv, lt > FREE, SEND < lt < SEND + 0.2)
                url = "www.turkiye.gov.tr/ticaret-tuketici-hakem-heyeti"
            browser_in(world, lt - tt[2], url, page, "e-Devlet Kapısı")
            sw = cw(el.SEARCH)
            row = page_to_world(el.SEARCH[0] + 320, el.SEARCH[3] + 2 + el.SUG_ROW / 2)
            pts = [(tt[2], 1100, 900), (Q0 - 0.3, sw[0] - 150, sw[1]), (SUG + 0.8, sw[0] - 150, sw[1]), (CLK - 0.3, *row), (CLK + 0.3, *row)]
            for box, t0 in ((el.T_TUR, TUR), (el.T_KARSI, KAR0), (el.T_TUTAR, TUT0)):
                c = cw(box)
                pts += [(t0 - 0.3, c[0] - 150, c[1]), (t0 + 0.4, c[0] - 150, c[1])]
            up = cw((el.T_UP[0][2] - 150, el.T_UP[0][1], el.T_UP[0][2], el.T_UP[0][3]))
            pts += [(UP0 - 0.3, *up), (UP0 + 0.3, *up)]
            s = cw(el.T_SEND)
            pts += [(SEND - 0.3, *s), (tt[6], *s)]
            x, y = path(t, pts)
            draw_cursor(world, x, y, t, (Q0 - 0.3, CLK, TUR, KAR0 - 0.2, TUT0 - 0.2, UP0, SEND), 40)
            if FREE < t < SEND:
                c = cw((900, 460, 1300, 530))
                place_anim(world, stamp("ÜCRETSİZ", 64, GREEN), c[0] + 380, c[1] - 40, t, SEND - FREE + 0.2, "stamp", FREE, 0.22, -8)
            if t > SEND + 0.3:
                overlay_rect(world, (0, 0, W, H), (20, 20, 20, int(120 * clamp((t - SEND - 0.3) / 0.3))))
                place_anim(world, el.success_modal("Başvurunuz alındı", "Bedel iadesi talebi"), W / 2, H / 2, t, tt[6] + 0.2, "pop", SEND + 0.35, 0.35)
            left = cw((60, 220, 800, 544))
            cam = cam_path(t, [(tt[2], 1.0, W / 2, H / 2), (Q0 - 0.3, 1.5, sw[0], sw[1] + 80), (CLK + 0.1, 1.5, sw[0], sw[1] + 80),
                               (CLK + 0.5, 1.0, W / 2, H / 2), (TUR - 0.3, 1.3, left[0] + 60, left[1]), (UP0 - 0.4, 1.3, left[0] + 60, left[1]),
                               (UP0, 1.0, W / 2, H / 2)])
            keys = keys_for(Q0, Q, 14) + keys_for(KAR0, V_KAR, 14) + keys_for(TUT0, "3.750 TL", 12)
            return {"cam": cam, "keys": keys, "mascot": "ciddi"}
        place_anim(world, el.bank_notif("3.750 TL"), 640, 400, t, d, "drop", tt[6], 0.4)
        v = int(3750 * out_cubic(prog(t, tt[6] + 0.3, 1.2)))
        place(world, text_sprite(f"+{v:,}".replace(",", ".") + " TL", "black", 96, GREEN, 6, WHITE), 640, 620)
        place_anim(world, pill("ÖZEL ••• HASTANESİ", "black", 40, WHITE, (90, 90, 100, 255), border=4, pad=(26, 14), shadow=6), 1400, 380, t, d,
                   "pop", tt[7], 0.35)
        place_anim(world, stamp("İDARİ PARA CEZASI", 62), 1400, 520, t, d, "stamp", tt[8] + 0.3, 0.25, -6)
        return {"mascot": "heyecanli:kutlama"}
    sfx = [(0.0, "impact"), (tt[1], "pop"), (tt[2], "whoosh"), (Q0 - 0.3, "click"), (CLK, "click"), (TUR, "click"),
           (KAR0 - 0.2, "click"), (TUT0 - 0.2, "click"), (UP0, "click"), (UP0 + 0.7, "ding"), (FREE, "impact"), (SEND, "click"),
           (SEND + 0.35, "ding"), (tt[6], "ding"), (tt[8] + 0.3, "impact")] + key_sfx(Q0, Q, 14) + key_sfx(KAR0, V_KAR, 14) + \
        key_sfx(TUT0, "3.750 TL", 12)
    return f, sfx


def s_end(world, t, d):
    t1 = text_sprite("HAKLARINI KORU", "black", 110, RED)
    place_anim(world, t1, W / 2, 360, t, d, "pop", 0.0)
    sb = end_card() if t < 1.4 else el.sub_button(1)
    place_anim(world, sb, W / 2, 600, t, d, "pop", 0.3, 0.35)
    x, y = path(t, [(0, 1400, 950), (1.0, W / 2 + 40, 610)])
    draw_cursor(world, x, y, t, (1.3,), 48)
    return {"mascot": "kahkaha:kutlama" if t > 1.4 else "goz_kirp"}


# ================================================================ kurgu
def build():
    spec = [
        (CAP_HOOK, seg_hook, None, 0), (CAP_LAW, seg_law, None, 0), (CAP_OVR, seg_overview, None, 6.0),
        (CAP_S1, seg_s1, ("ADIM 1/5", "Belgeleri eksiksiz al"), 0),
        (CAP_S2, seg_s2, ("ADIM 2/5", "e-Nabız kontrolü"), 0),
        (CAP_S3, seg_s3, ("ADIM 3/5", "CİMER · SGK şikâyeti"), 0),
        (CAP_S4, seg_s4, ("ADIM 4/5", "SABİM 184"), 0),
        (CAP_S5, seg_s5, ("ADIM 5/5", "B planı · Hakem Heyeti"), 0),
    ]
    segs = []
    for caps, fn, chap, mn in spec:
        dur = dur_for(caps, mn)
        f, sfx = fn(dur)
        segs.append(Seg(dur, f, caps, chap, sfx))
    segs.append(Seg(3.2, s_end, [], None, [(0.3, "pop"), (1.3, "click"), (1.4, "ding")]))
    return Tutorial(segs, voice=None)


def main():
    os.makedirs(OUT, exist_ok=True)
    tu = build()
    print(f"süre: {tu.duration:.1f} sn")
    wav = audio.mix(tu.duration, tu.events(), os.path.join(OUT, "hastane_audio.wav"), voice_path=VOICE, voice_offset=0)
    render(tu.frame, tu.duration, (W, H), os.path.join(OUT, "hastane_yatay.mp4"), wav)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        tu = build()
        ts = [float(x) for x in sys.argv[2:]] or [s + g.dur * f for s, g in zip(tu.starts, tu.segs) for f in (0.2, 0.5, 0.8)]
        ims = [tu.frame(x).convert("RGB").resize((480, 270)) for x in ts]
        cols = 5
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (480 * cols, 270 * rows), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * 480, (k // cols) * 270))
        os.makedirs(OUT, exist_ok=True)
        sheet.save(os.path.join(OUT, "preview_hastane.jpg"))
        print(f"süre: {tu.duration:.1f} sn")
    else:
        main()
