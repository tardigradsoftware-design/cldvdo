"""Senaryo: Voltaj hasarı tazminatı — YATAY adım adım anlatım (telefon, servis raporu, dağıtım şirketi
online başvuru, e-Devlet Tüketici Hakem Heyeti). Maskot: Tokmak. Müzik yok."""
import math
import os
import sys
from functools import lru_cache

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw

from engine.core import (BLUE, GREEN, INK, RED, SS, WHITE, YELLOW, canvas, card_base, clamp, dtext, finish, font,
                         out_back, out_cubic, path, pill, place, place_anim, prog, render, text_sprite)
from engine.components import draw_cursor, icon_check, icon_x, stamp
from engine.tutorial import (CH, CW, CX0, CY0, H, W, Seg, Tutorial, cam_path, draw_browser, page_to_world)
from engine import audio
from short import appliance, bolt, coin, smoke

OUT = os.environ.get("OUT_DIR", "out")
VOICE = os.environ.get("VOICE")
GREYT = (110, 110, 110, 255)
LINE = (215, 215, 215, 255)
DBLUE = (24, 70, 160, 255)


def S(v):
    return int(v * SS)


def typing(t, t0, text, cps=12):
    return text[: int(clamp((t - t0) * cps, 0, len(text)))]


def keys_for(t0, text, cps=12, label=None):
    return [(t0 + k / cps, label or (c.upper() if c != " " else "Space")) for k, c in enumerate(text)]


def key_sfx(t0, text, cps=12):
    return [(t0 + k / cps, "key") for k in range(len(text))]


def overlay_rect(world, box, rgba):
    x0, y0, x1, y1 = [int(v) for v in box]
    world.alpha_composite(Image.new("RGBA", (x1 - x0, y1 - y0), rgba), (x0, y0))


def browser_in(world, t, url, page, tab):
    if t < 0.4:
        k = out_back(t / 0.4, 1.5)
        draw_browser(world, url, page, tab=tab, scale=0.86 + 0.14 * k, alpha=clamp(t / 0.25))
    else:
        draw_browser(world, url, page, tab=tab)


def cw(box):
    x0, y0, x1, y1 = box
    return page_to_world((x0 + x1) / 2, (y0 + y1) / 2)


# ================================================================ ortak form çizimi
def field(d, box, label, value, focus, mono=False):
    x0, y0, x1, y1 = box
    dtext(d, (x0, y0 - 34), label, "bold", 22, (70, 70, 70, 255))
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(10), fill=WHITE, outline=RED if focus else (190, 190, 190, 255),
                        width=S(4 if focus else 2))
    dtext(d, (x0 + 20, (y0 + y1) / 2), value, "bold", 28, INK, "lm")
    if focus:
        cx = x0 + 20 + font("bold", 28 * SS).getlength(value) / SS + 3
        d.rectangle([S(cx), S(y0 + 14), S(cx + 3), S(y1 - 14)], fill=INK)


def upload_row(d, box, name, prog_v):
    x0, y0, x1, y1 = box
    done = prog_v >= 1
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=(240, 250, 244, 255) if done else (248, 248, 248, 255),
                        outline=GREEN if done else LINE, width=S(3))
    d.rounded_rectangle([S(x0 + 18), S(y0 + 16), S(x0 + 62), S(y1 - 16)], S(6), fill=RED if name.endswith("pdf") else BLUE)
    dtext(d, (x0 + 40, (y0 + y1) / 2), "PDF" if name.endswith("pdf") else "JPG", "black", 13, WHITE, "mm")
    dtext(d, (x0 + 80, y0 + 14), name, "bold", 24, INK)
    if prog_v <= 0:
        d.rounded_rectangle([S(x1 - 150), S(y0 + 18), S(x1 - 18), S(y1 - 18)], S(10), fill=DBLUE)
        dtext(d, (x1 - 84, (y0 + y1) / 2), "Yükle", "black", 22, WHITE, "mm")
    else:
        bx0, bx1 = x0 + 80, x1 - 80
        d.rounded_rectangle([S(bx0), S(y1 - 26), S(bx1), S(y1 - 16)], S(5), fill=(225, 225, 225, 255))
        d.rounded_rectangle([S(bx0), S(y1 - 26), S(bx0 + (bx1 - bx0) * min(1, prog_v)), S(y1 - 16)], S(5), fill=GREEN)
        if done:
            ck = icon_check(40)
            d._image.alpha_composite(ck.resize((ck.width * SS, ck.height * SS)), (S(x1 - 60), S((y0 + y1) / 2 - 20)))


# ================================================================ dağıtım şirketi sayfaları (stilize, kurgusal)
def dist_header(d):
    d.rectangle([0, 0, S(CW), S(92)], fill=DBLUE)
    d.rounded_rectangle([S(36), S(18), S(92), S(74)], S(12), fill=YELLOW)
    pts = [(66, 22), (50, 50), (62, 50), (56, 70), (78, 42), (66, 42), (72, 22)]
    d.polygon([(S(x), S(y)) for x, y in pts], fill=INK)
    dtext(d, (110, 46), "Dağıtım Şirketiniz", "black", 32, WHITE, "lm")
    dtext(d, (1700, 46), "Online İşlemler", "bold", 24, (200, 215, 255, 255), "rm")


TILES = ["Fatura Sorgula", "Kesinti Bildir", "Sayaç Okuma", "Tazminat Başvurusu", "Abonelik İşlemleri", "İletişim"]


def tile_box(k):
    c, r = k % 3, k // 3
    x0, y0 = 60 + c * 552, 190 + r * 240
    return (x0, y0, x0 + 520, y0 + 210)


@lru_cache(maxsize=8)
def page_dist_home(hover=False):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=(246, 248, 252, 255))
    dist_header(d)
    dtext(d, (60, 122), "Online İşlemler", "black", 40, INK)
    for k, name in enumerate(TILES):
        x0, y0, x1, y1 = tile_box(k)
        hl = (k == 3 and hover)
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(18), fill=(255, 238, 236, 255) if hl else WHITE,
                            outline=RED if hl else LINE, width=S(4 if hl else 2))
        d.rounded_rectangle([S(x0 + 30), S(y0 + 34), S(x0 + 100), S(y0 + 104)], S(16), fill=RED if k == 3 else (220, 228, 244, 255))
        if k == 3:
            dtext(d, (x0 + 65, y0 + 69), "₺", "black", 38, WHITE, "mm")
        dtext(d, (x0 + 30, y0 + 140), name, "black", 32, INK)
    return finish(im)


F_TES = (60, 200, 800, 264)
F_KAY = (60, 330, 800, 394)
F_IBAN = (60, 460, 800, 524)
UP = [(900, 190, 1688, 270), (900, 290, 1688, 370), (900, 390, 1688, 470)]
SEND = (900, 540, 1688, 612)
UPNAMES = ["Servis_raporu.pdf", "Tamir_faturasi.pdf", "Cihaz_fotograflari.jpg"]
V_TES, V_KAY, V_IBAN = "40••••••21", "4471829", "TR12 •••• •••• •••• 1234"


@lru_cache(maxsize=512)
def page_dist_form(tes, kay, iban, focus, p1, p2, p3, pressed):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=WHITE)
    dist_header(d)
    dtext(d, (60, 112), "Hasar Tazminat Başvurusu", "black", 36, INK)
    field(d, F_TES, "Tesisat / Abone No", tes, focus == "tes")
    field(d, F_KAY, "Arıza Kayıt No", kay, focus == "kay")
    field(d, F_IBAN, "IBAN", iban, focus == "iban")
    dtext(d, (900, 140), "Belgeler", "bold", 22, (70, 70, 70, 255))
    for box, nm, pv in zip(UP, UPNAMES, (p1, p2, p3)):
        upload_row(d, box, nm, pv / 10)
    x0, y0, x1, y1 = SEND
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=(180, 30, 26, 255) if pressed else RED)
    dtext(d, ((x0 + x1) / 2, (y0 + y1) / 2), "Başvuruyu Gönder", "black", 30, WHITE, "mm")
    return finish(im)


@lru_cache(maxsize=2)
def success_modal(title, no):
    w, h = 760, 380
    im, d = card_base(w, h, radius=26)
    ck = icon_check(110)
    im.alpha_composite(ck.resize((ck.width * SS, ck.height * SS)), (S(w / 2 - 55), S(34)))
    dtext(d, (w / 2, 190), title, "black", 44, GREEN, "mm")
    dtext(d, (w / 2, 260), no, "bold", 30, GREYT, "mm")
    return finish(im)


# ================================================================ e-Devlet sayfaları (stilize)
def ed_header(d):
    d.rectangle([0, 0, S(CW), S(92)], fill=WHITE)
    d.line([0, S(92), S(CW), S(92)], fill=LINE, width=S(2))
    d.rounded_rectangle([S(40), S(18), S(96), S(74)], S(14), fill=RED)
    dtext(d, (68, 46), "e", "black", 40, WHITE, "mm")
    dtext(d, (112, 46), "e-Devlet Kapısı", "black", 32, INK, "lm")
    d.ellipse([S(1500), S(24), S(1544), S(68)], fill=(200, 200, 200, 255))
    dtext(d, (1560, 46), "A**** Y*****  ▾", "bold", 24, INK, "lm")


SEARCH = (324, 210, 1300, 290)
SUG_ROW = 76


@lru_cache(maxsize=128)
def page_ed_home(typed="", focus=False, sugg=False, hover=False):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=WHITE)
    d.rectangle([0, S(92), S(CW), S(400)], fill=(253, 241, 240, 255))
    ed_header(d)
    dtext(d, (874, 150), "Size nasıl yardımcı olabilirim?", "black", 44, INK, "mm")
    x0, y0, x1, y1 = SEARCH
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=WHITE, outline=RED if focus else (190, 190, 190, 255), width=S(4 if focus else 3))
    dtext(d, (x0 + 28, (y0 + y1) / 2), typed or "Hizmet, kurum veya belge ara", "semi", 32, INK if typed else (165, 165, 165, 255), "lm")
    if focus:
        cx = x0 + 28 + font("semi", 32 * SS).getlength(typed) / SS + 3
        d.rectangle([S(cx), S(y0 + 22), S(cx + 3), S(y1 - 22)], fill=INK)
    d.rounded_rectangle([S(1310), S(y0), S(1424), S(y1)], S(12), fill=RED)
    dtext(d, (1367, (y0 + y1) / 2), "Ara", "black", 30, WHITE, "mm")
    for k, lab in enumerate(["Kurumlar", "Belediyeler", "Firmalar", "Popüler Hizmetler"]):
        tx = 110 + k * 392
        d.rounded_rectangle([S(tx), S(450), S(tx + 360), S(640)], S(18), fill=(247, 247, 247, 255), outline=LINE, width=S(2))
        dtext(d, (tx + 28, 580), lab, "bold", 28, (80, 80, 80, 255))
    if sugg:
        top = y1 - 4
        d.rounded_rectangle([S(x0), S(top), S(x1), S(top + SUG_ROW * 3 + 10)], S(12), fill=WHITE, outline=(190, 190, 190, 255), width=S(3))
        for r in range(3):
            ry = top + 6 + r * SUG_ROW
            if r == 0:
                if hover:
                    d.rectangle([S(x0 + 4), S(ry), S(x1 - 4), S(ry + SUG_ROW)], fill=(255, 236, 235, 255))
                d.rounded_rectangle([S(x0 + 22), S(ry + 14), S(x0 + 70), S(ry + 62)], S(10), fill=DBLUE)
                dtext(d, (x0 + 46, ry + 38), "TB", "black", 16, WHITE, "mm")
                dtext(d, (x0 + 88, ry + 12), "Tüketici Hakem Heyeti Başvurusu", "black", 28, INK)
                dtext(d, (x0 + 88, ry + 46), "Ticaret Bakanlığı", "semi", 20, GREYT)
            else:
                d.rounded_rectangle([S(x0 + 22), S(ry + 14), S(x0 + 70), S(ry + 62)], S(10), fill=(228, 228, 228, 255))
                d.rounded_rectangle([S(x0 + 88), S(ry + 18), S(x0 + 88 + 380 - r * 60), S(ry + 38)], S(8), fill=(228, 228, 228, 255))
    return finish(im)


T_TUR = (60, 220, 800, 284)
T_KARSI = (60, 350, 800, 414)
T_TUTAR = (60, 480, 800, 544)
T_UP = [(900, 200, 1688, 270), (900, 284, 1688, 354), (900, 368, 1688, 438)]
T_SEND = (900, 560, 1688, 632)


@lru_cache(maxsize=512)
def page_thh(tur, karsi, tutar, focus, upv, free, pressed):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=WHITE)
    ed_header(d)
    dtext(d, (60, 112), "Ticaret Bakanlığı   ›   Tüketici Hakem Heyeti Başvurusu", "semi", 22, GREYT)
    dtext(d, (60, 150), "Tüketici Hakem Heyeti Başvurusu", "black", 34, INK)
    field(d, T_TUR, "Başvuru Konusu", tur, focus == "tur")
    if tur:
        dtext(d, (770, 252), "▾", "black", 24, GREYT, "rm")
    field(d, T_KARSI, "Karşı Taraf", karsi, focus == "karsi")
    field(d, T_TUTAR, "Uyuşmazlık Tutarı", tutar, focus == "tutar")
    dtext(d, (900, 160), "Belgeler (şirkete gönderdiklerinin aynısı)", "bold", 22, (70, 70, 70, 255))
    for box, nm in zip(T_UP, UPNAMES):
        upload_row(d, box, nm, upv / 10)
    if free:
        d.rounded_rectangle([S(900), S(460), S(1300), S(530)], S(12), fill=(236, 248, 241, 255), outline=GREEN, width=S(3))
        dtext(d, (1100, 495), "Başvuru ücreti: ÜCRETSİZ", "black", 26, GREEN, "mm")
    x0, y0, x1, y1 = T_SEND
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=(180, 30, 26, 255) if pressed else RED)
    dtext(d, ((x0 + x1) / 2, (y0 + y1) / 2), "Başvuruyu Gönder", "black", 30, WHITE, "mm")
    return finish(im)


# ================================================================ diğer görseller
@lru_cache(maxsize=1)
def phone_frame():
    w, h = 470, 860
    im, d = canvas(w + 14, h + 14)
    d.rounded_rectangle([S(14), S(14), S(w + 14), S(h + 14)], S(66), fill=INK)
    d.rounded_rectangle([0, 0, S(w), S(h)], S(66), fill=INK)
    d.rounded_rectangle([S(16), S(16), S(w - 16), S(h - 16)], S(52), fill=(248, 248, 250, 255))
    d.rounded_rectangle([S(w / 2 - 60), S(30), S(w / 2 + 60), S(58)], S(14), fill=INK)
    return finish(im)


PH_X, PH_Y = 640, 520  # telefon merkezi (dünya)
KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]


def key_pos(k):
    i = KEYS.index(k)
    c, r = i % 3, i // 3
    return PH_X - 130 + c * 130, PH_Y - 70 + r * 108


@lru_cache(maxsize=64)
def keypad_sprite(pressed):
    im, d = canvas(470, 860)
    for k in KEYS:
        x, y = key_pos(k)
        x, y = x - PH_X + 235, y - PH_Y + 430
        on = k == pressed
        d.ellipse([S(x - 44), S(y - 44), S(x + 44), S(y + 44)], fill=(200, 205, 215, 255) if on else (232, 234, 238, 255))
        dtext(d, (x, y), k, "semi", 40, INK, "mm")
    x, y = 235, 430 + 4 * 108 - 70 + 30
    d.ellipse([S(x - 46), S(y - 46), S(x + 46), S(y + 46)], fill=GREEN)
    dtext(d, (x, y), "ARA", "black", 26, WHITE, "mm")
    return finish(im)


@lru_cache(maxsize=1)
def note_card_base():
    w, h = 640, 400
    im, d = card_base(w, h, fill=(255, 250, 225, 255), header=YELLOW, header_h=70)
    dtext(d, (30, 18), "NOTLAR", "black", 32, INK)
    dtext(d, (40, 110), "Dağıtım şirketi arıza hattı", "bold", 28, GREYT)
    dtext(d, (40, 190), "ARIZA KAYIT NO:", "black", 34, INK)
    return finish(im)


@lru_cache(maxsize=1)
def report_base():
    w, h = 820, 620
    im, d = card_base(w, h, header=INK, header_h=84)
    dtext(d, (34, 22), "YETKİLİ SERVİS RAPORU", "black", 36, WHITE)
    rows = [("Cihaz", "Kombi"), ("Marka / Model", "•••••• / •••"), ("Tarih", "21.11.2026")]
    for k, (a, b) in enumerate(rows):
        dtext(d, (40, 120 + k * 56), a, "bold", 28, GREYT)
        dtext(d, (300, 120 + k * 56), b, "black", 30, INK)
    dtext(d, (40, 310), "Arıza nedeni:", "bold", 28, GREYT)
    d.rounded_rectangle([S(40), S(350), S(780), S(470)], S(12), outline=LINE, width=S(3))
    d.line([S(460), S(560), S(760), S(560)], fill=INK, width=S(3))
    dtext(d, (610, 572), "Servis kaşe / imza", "semi", 22, GREYT, "mt")
    return finish(im)


REPORT_TXT1 = "Voltaj dalgalanması nedeniyle"
REPORT_TXT2 = "anakart arızalanmıştır."


@lru_cache(maxsize=1)
def invoice_card():
    w, h = 520, 440
    im, d = card_base(w, h, header=RED, header_h=72)
    dtext(d, (28, 18), "TAMİR FATURASI", "black", 32, WHITE)
    for k, (a, b) in enumerate([("Anakart", "9.800 TL"), ("İşçilik", "2.650 TL")]):
        dtext(d, (34, 110 + k * 56), a, "bold", 28, GREYT)
        dtext(d, (w - 34, 110 + k * 56), b, "black", 30, INK, "ra")
    d.line([S(34), S(240), S(w - 34), S(240)], fill=INK, width=S(4))
    dtext(d, (34, 262), "TOPLAM", "black", 34)
    dtext(d, (w - 34, 258), "12.450 TL", "black", 42, RED, "ra")
    return finish(im)


@lru_cache(maxsize=16)
def calendar(day):
    w, h = 560, 480
    im, d = card_base(w, h, header=RED, header_h=80)
    dtext(d, (w / 2, 40), "İŞ GÜNÜ SAYACI", "black", 34, WHITE, "mm")
    for k in range(10):
        c, r = k % 5, k // 5
        x, y = 50 + c * 94, 130 + r * 120
        done = k < day
        d.rounded_rectangle([S(x), S(y), S(x + 78), S(y + 96)], S(12), fill=(250, 250, 250, 255), outline=INK, width=S(3))
        dtext(d, (x + 39, y + 48), str(k + 1), "black", 34, GREYT if done else INK, "mm")
        if done:
            d.line([S(x + 12), S(y + 12), S(x + 66), S(y + 84)], fill=RED, width=S(6))
    dtext(d, (w / 2, 410), f"{min(day, 10)} / 10", "black", 40, RED if day >= 10 else INK, "mm")
    return finish(im)


@lru_cache(maxsize=4)
def bank_notif(amount):
    w, h = 720, 170
    im, d = card_base(w, h, radius=30, shadow=8)
    d.rounded_rectangle([S(30), S(40), S(120), S(130)], S(20), fill=GREEN, outline=INK, width=S(3))
    dtext(d, (75, 85), "₺", "black", 50, WHITE, "mm")
    dtext(d, (150, 36), "BANKA · şimdi", "bold", 24, GREYT)
    dtext(d, (150, 74), f"Hesabınıza {amount} yatırıldı", "black", 34, INK)
    dtext(d, (150, 120), "Açıklama: Tazminat ödemesi", "semi", 24, GREYT)
    return finish(im)


@lru_cache(maxsize=4)
def step_card(k):
    names = [("186'yı ara", "kayıt numarası al"), ("Servis raporu", "voltaj yazdır"), ("Online başvuru", "belgeleri yükle"),
             ("Hakem Heyeti", "e-Devlet, ücretsiz")]
    im, d = card_base(390, 240)
    d.ellipse([S(28), S(28), S(98), S(98)], fill=RED, outline=INK, width=S(4))
    dtext(d, (63, 63), str(k + 1), "black", 40, WHITE, "mm")
    dtext(d, (28, 130), names[k][0], "black", 36, INK)
    dtext(d, (28, 180), names[k][1], "semi", 26, GREYT)
    return finish(im)


@lru_cache(maxsize=2)
def sub_button(state):
    if state == 0:
        return pill("ABONE OL", "black", 64, WHITE, RED, border=5, pad=(44, 22), shadow=8)
    return pill("ABONE OLUNDU ✓", "black", 64, INK, (225, 225, 225, 255), border=5, pad=(44, 22), shadow=8)


# ================================================================ segmentler
def s_hook(world, t, dur):
    l1 = text_sprite("BEYAZ EŞYAN YA DA KOMBİN", "black", 66, INK)
    l2 = text_sprite("ELEKTRİKTEN Mİ", "black", 120, RED)
    l3 = text_sprite("BOZULDU?", "black", 120, RED)
    y = 250
    for spr in (l1, l2, l3):
        place(world, spr, 90, y, anchor="tl")
        y += spr.height + 6
    for k, (kind, dx, dy) in enumerate((("kombi", -190, 0), ("buzdolabi", 40, -40))):
        sp = appliance(kind, 240)
        place_anim(world, sp, 1420 + dx, 470 + dy, t, dur, "drop", -1, 0.3)
        smoke(world, 1420 + dx, 470 + dy - sp.height / 2, t, 0.3)
    place_anim(world, bolt(170), 1700, 330, t, dur, "pop", -1, 0.3, -12)
    place_anim(world, stamp("TÜM MASRAF GERİ ✓", 60, GREEN), 1400, 790, t, dur, "stamp", 4.2, 0.25, -5)
    z = 1 + 0.06 * (1 - out_cubic(prog(t, 0, 0.4)))
    return {"cam": (z, W / 2, H / 2), "mascot": "saskin" if t < 4.2 else "mutlu"}


def s_overview(world, t, dur):
    t1 = text_sprite("4 NET ADIM", "black", 110, RED)
    place_anim(world, t1, 90 + t1.width / 2, 250, t, dur, "left", 0.0)
    for k in range(4):
        place_anim(world, step_card(k), 280 + k * 450, 640, t, dur, "pop", 0.4 + k * 0.4, 0.35, [-3, 2, -2, 3][k])
    return {"mascot": "ciddi:isaret"}


def s_phone(world, t, dur):
    place_anim(world, phone_frame(), PH_X, PH_Y, t, dur, "up", 0.0, 0.35)
    if t < 0.35:
        return {"mascot": "ciddi:isaret"}
    taps = [(1.0, "1"), (1.45, "8"), (1.9, "6")]
    pressed = next((k for tt, k in taps if 0 <= t - tt < 0.18), None)
    calling = t > 2.6
    if not calling:
        place(world, keypad_sprite(pressed), PH_X, PH_Y + 7)
        num = "".join(k for tt, k in taps if t >= tt)
        place(world, text_sprite(num or " ", "semi", 70, INK), PH_X, PH_Y - 280)
        x, y = path(t, [(0, PH_X + 300, PH_Y + 300), (0.8, *key_pos("1")), (1.3, *key_pos("1")), (1.4, *key_pos("8")),
                        (1.8, *key_pos("8")), (1.85, *key_pos("6")), (2.25, *key_pos("6")), (2.45, PH_X, PH_Y + 392)])
        draw_cursor(world, x, y, t, tuple(tt for tt, _ in taps) + (2.5,), 44)
    else:
        place(world, text_sprite("186", "black", 96, INK), PH_X, PH_Y - 250)
        place(world, text_sprite("Elektrik Arıza Hattı", "semi", 34, GREYT), PH_X, PH_Y - 175)
        secs = int(max(0, t - 2.6) * 6)
        place(world, text_sprite(f"00:{secs:02d}", "bold", 40, GREEN), PH_X, PH_Y - 110)
        for k in range(3):
            r = 60 + ((t * 70 + k * 40) % 120)
            ring = Image.new("RGBA", (int(2 * r + 8), int(2 * r + 8)), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse([4, 4, 2 * r + 4, 2 * r + 4], outline=(24, 160, 88, int(200 * (1 - (r - 60) / 120))), width=6)
            world.alpha_composite(ring, (int(PH_X - r - 4), int(PH_Y + 80 - r - 4)))
        place(world, pill("ARANIYOR", "black", 34, WHITE, GREEN, pad=(22, 12)), PH_X, PH_Y + 80)
    if t > 4.0:
        place_anim(world, note_card_base(), 1380, 420, t, dur, "right", 4.0, 0.4)
        typed = typing(t, 4.5, "4471829", 9)
        if typed:
            place(world, text_sprite(typed, "black", 72, RED), 1380 - 270, 420 + 80, anchor="l")
        place_anim(world, stamp("NUMARAYI NOT ET!", 48), 1400, 700, t, dur, "stamp", 5.6, 0.22, -5)
    cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (0.6, 1.25, PH_X + 60, PH_Y), (3.6, 1.25, PH_X + 60, PH_Y), (4.2, 1.0, W / 2, H / 2)])
    return {"cam": cam, "keys": [(tt, k) for tt, k in taps], "mascot": "ciddi:isaret"}


def s_report(world, t, dur):
    place_anim(world, report_base(), 560, 520, t, dur, "drop", 0.0, 0.4, -2)
    rx0, ry0 = 560 - 410, 520 - 310
    l1 = typing(t, 1.0, REPORT_TXT1, 14)
    l2 = typing(t, 1.0 + len(REPORT_TXT1) / 14, REPORT_TXT2, 14)
    t_done = 1.0 + (len(REPORT_TXT1) + len(REPORT_TXT2)) / 14
    if t > t_done + 0.2:
        k = out_cubic(prog(t, t_done + 0.2, 0.5))
        overlay_rect(world, (rx0 + 48, ry0 + 358, rx0 + 48 + 540 * k, ry0 + 400), (255, 220, 60, 170))
    if l1:
        place(world, text_sprite(l1, "bold", 34, INK), rx0 + 56, ry0 + 380, anchor="l")
    if l2:
        place(world, text_sprite(l2, "bold", 34, INK), rx0 + 56, ry0 + 428, anchor="l")
    place_anim(world, stamp("MUTLAKA YAZDIR", 52), 560, 880, t, dur, "stamp", t_done + 0.6, 0.22, -4)
    place_anim(world, invoice_card(), 1450, 470, t, dur, "right", 5.6, 0.4, 3)
    place_anim(world, stamp("SAKLA", 64, GREEN), 1560, 760, t, dur, "stamp", 6.6, 0.22, -10)
    x, y = path(t, [(0, 1100, 900), (0.8, rx0 + 60, ry0 + 380), (t_done, rx0 + 600, ry0 + 430), (t_done + 1.2, rx0 + 600, ry0 + 430)])
    if t < 5.4:
        draw_cursor(world, x, y, t, (0.9,), 40)
    cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (0.6, 1.35, rx0 + 400, ry0 + 430), (t_done + 1.0, 1.35, rx0 + 400, ry0 + 430),
                       (t_done + 1.6, 1.0, W / 2, H / 2)])
    keys = keys_for(1.0, REPORT_TXT1 + REPORT_TXT2, 14)
    return {"cam": cam, "keys": keys, "mascot": "ciddi:isaret" if t < 5.6 else "goz_kirp"}


# --- dağıtım şirketi online başvuru zamanlaması
D_CLICK_TILE = 1.9
D_TES0, D_KAY0, D_IBAN0 = 2.6, 4.1, 5.3
D_UP = [7.4, 8.6, 9.8]
D_SEND = 11.2
URL_DIST = "dagitimsirketiniz.com.tr/online-islemler"


def s_dist(world, t, dur):
    if t < D_CLICK_TILE + 0.25:
        page = page_dist_home(hover=t > 1.5)
    else:
        tes = typing(t, D_TES0, V_TES, 10)
        kay = typing(t, D_KAY0, V_KAY, 10)
        iban = typing(t, D_IBAN0, V_IBAN, 15)
        focus = "tes" if D_TES0 - 0.2 < t < D_KAY0 - 0.2 else "kay" if t < D_IBAN0 - 0.2 else "iban" if t < D_UP[0] - 0.3 else None
        pv = [int(clamp((t - u - 0.1) / 0.8, 0, 1) * 10) for u in D_UP]
        page = page_dist_form(tes, kay, iban, focus if t > D_TES0 - 0.2 else None, *pv, D_SEND < t < D_SEND + 0.2)
    browser_in(world, t, URL_DIST, page, "Online İşlemler")
    tile = cw(tile_box(3))
    pts = [(0, 1100, 900), (1.4, tile[0], tile[1]), (D_CLICK_TILE + 0.2, tile[0], tile[1])]
    for f, t0 in ((F_TES, D_TES0), (F_KAY, D_KAY0), (F_IBAN, D_IBAN0)):
        c = cw(f)
        pts += [(t0 - 0.4, c[0] - 200, c[1]), (t0 + 0.6, c[0] - 200, c[1])]
    for box, u in zip(UP, D_UP):
        c = cw((box[2] - 150, box[1], box[2] - 18, box[3]))
        pts += [(u - 0.3, c[0], c[1]), (u + 0.5, c[0], c[1])]
    s = cw(SEND)
    pts += [(D_SEND - 0.3, s[0], s[1]), (dur, s[0], s[1])]
    x, y = path(t, pts)
    clicks = (D_CLICK_TILE, D_TES0 - 0.2, D_KAY0 - 0.2, D_IBAN0 - 0.2) + tuple(D_UP) + (D_SEND,)
    draw_cursor(world, x, y, t, clicks, 40)
    if t > D_SEND + 0.3:
        overlay_rect(world, (0, 0, W, H), (20, 20, 20, int(120 * clamp((t - D_SEND - 0.3) / 0.3))))
        place_anim(world, success_modal("Başvurunuz alındı", "Başvuru No: TZ-2026-0815"), W / 2, H / 2, t, dur, "pop", D_SEND + 0.35, 0.35)
    left = cw((60, 200, 800, 524))
    right = cw((900, 190, 1688, 470))
    cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (D_CLICK_TILE + 0.2, 1.0, W / 2, H / 2), (D_TES0 - 0.2, 1.3, left[0] + 60, left[1]),
                       (D_UP[0] - 0.5, 1.3, left[0] + 60, left[1]), (D_UP[0] - 0.1, 1.3, right[0], right[1]),
                       (D_SEND - 0.6, 1.3, right[0], right[1]), (D_SEND - 0.1, 1.0, W / 2, H / 2)])
    keys = keys_for(D_TES0, "40••••••21", 10, None) + keys_for(D_KAY0, V_KAY, 10) + keys_for(D_IBAN0, V_IBAN, 15)
    keys = [(kt, "•" if lab == "•" else lab) for kt, lab in keys]
    return {"cam": cam, "keys": keys, "mascot": "mutlu" if t > D_SEND + 0.4 else "ciddi"}


def s_wait(world, t, dur):
    day = int(clamp((t - 0.6) / 2.2, 0, 1) * 10)
    place_anim(world, calendar(day), 620, 520, t, dur, "pop", 0.0, 0.35)
    place_anim(world, stamp("ÖDEME YAPILMADI ✗", 60), 1330, 420, t, dur, "stamp", 3.0, 0.25, -6)
    nx = text_sprite("SIRADAKİ: e-DEVLET", "black", 56, DBLUE)
    place_anim(world, nx, 1330, 640, t, dur, "up", 3.4, 0.35)
    return {"mascot": "kizgin" if t > 3.0 else "dusunceli"}


E_Q = "tüketici hakem heyeti"
E_Q0, E_CPS = 1.3, 12
E_SUG = E_Q0 + 6 / E_CPS
E_CLICK = 4.2
E_TUR, E_KARSI0, E_TUTAR0 = 5.0, 6.2, 8.0
E_UP0 = 9.2
E_FREE = 10.9
E_SEND = 12.0
V_KARSI = "Elektrik Dağıtım Şirketi"


def s_edevlet(world, t, dur):
    if t < E_CLICK + 0.3:
        typed = typing(t, E_Q0, E_Q, E_CPS)
        page = page_ed_home(typed, t > 1.0, t > E_SUG, t > E_CLICK - 0.6)
        url = "www.turkiye.gov.tr"
    else:
        tur = "Ayıplı Hizmet — Elektrik" if t > E_TUR + 0.3 else ""
        karsi = typing(t, E_KARSI0, V_KARSI, 17)
        tutar = typing(t, E_TUTAR0, "12.450 TL", 12)
        focus = "tur" if E_TUR - 0.1 < t < E_KARSI0 - 0.2 else "karsi" if E_KARSI0 - 0.2 <= t < E_TUTAR0 - 0.2 else \
            "tutar" if E_TUTAR0 - 0.2 <= t < E_UP0 - 0.3 else None
        upv = int(clamp((t - E_UP0) / 1.2, 0, 1) * 10)
        page = page_thh(tur, karsi, tutar, focus, upv, t > E_FREE, E_SEND < t < E_SEND + 0.2)
        url = "www.turkiye.gov.tr/ticaret-tuketici-hakem-heyeti"
    browser_in(world, t, url, page, "e-Devlet Kapısı")
    sw = cw(SEARCH)
    row = page_to_world(SEARCH[0] + 320, SEARCH[3] + 2 + SUG_ROW / 2)
    pts = [(0, 1100, 900), (0.9, sw[0] - 150, sw[1]), (3.4, sw[0] - 150, sw[1]), (E_CLICK - 0.3, row[0], row[1]),
           (E_CLICK + 0.3, row[0], row[1])]
    for box, t0 in ((T_TUR, E_TUR), (T_KARSI, E_KARSI0), (T_TUTAR, E_TUTAR0)):
        c = cw(box)
        pts += [(t0 - 0.4, c[0] - 150, c[1]), (t0 + 0.5, c[0] - 150, c[1])]
    up = cw((T_UP[0][2] - 150, T_UP[0][1], T_UP[0][2], T_UP[0][3]))
    pts += [(E_UP0 - 0.3, up[0], up[1]), (E_UP0 + 0.5, up[0], up[1])]
    s = cw(T_SEND)
    pts += [(E_SEND - 0.3, s[0], s[1]), (dur, s[0], s[1])]
    x, y = path(t, pts)
    draw_cursor(world, x, y, t, (1.0, E_CLICK, E_TUR, E_KARSI0 - 0.2, E_TUTAR0 - 0.2, E_UP0, E_SEND), 40)
    if E_FREE < t < E_SEND:
        place_anim(world, stamp("ÜCRETSİZ", 64, GREEN), cw((900, 460, 1300, 530))[0] + 380, cw((900, 460, 1300, 530))[1] - 40,
                   t, E_SEND - E_FREE + 0.2, "stamp", E_FREE, 0.22, -8)
    if t > E_SEND + 0.3:
        overlay_rect(world, (0, 0, W, H), (20, 20, 20, int(120 * clamp((t - E_SEND - 0.3) / 0.3))))
        place_anim(world, success_modal("Başvurunuz alındı", "Hakem heyeti kararını bekleyin"), W / 2, H / 2, t, dur, "pop",
                   E_SEND + 0.35, 0.35)
    left = cw((60, 220, 800, 544))
    cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (1.0, 1.5, sw[0], sw[1] + 80), (E_CLICK + 0.1, 1.5, sw[0], sw[1] + 80),
                       (E_CLICK + 0.6, 1.0, W / 2, H / 2), (E_TUR - 0.3, 1.3, left[0] + 60, left[1]),
                       (E_UP0 - 0.5, 1.3, left[0] + 60, left[1]), (E_UP0, 1.0, W / 2, H / 2)])
    keys = keys_for(E_Q0, E_Q, E_CPS) + keys_for(E_KARSI0, V_KARSI, 17) + keys_for(E_TUTAR0, "12.450 TL", 12)
    return {"cam": cam, "keys": keys, "mascot": "mutlu" if t > E_SEND + 0.4 else "ciddi"}


def s_result(world, t, dur):
    place_anim(world, text_sprite("KARAR ÇIKTI", "black", 100, INK), 560, 260, t, dur, "left", 0.0)
    place_anim(world, bank_notif("12.450 TL"), 560, 470, t, dur, "drop", 0.6, 0.4)
    for k in range(10):
        t0 = 1.2 + k * 0.1
        if t < t0:
            continue
        x = 1260 + (k % 5) * 110 + (k // 5) * 55
        yt = 640 - (k // 5) * 80
        place(world, coin(110), x, min(yt, 100 + (t - t0) * 2000))
    v = int(12450 * out_cubic(prog(t, 1.0, 1.6)))
    place(world, text_sprite(f"+{v:,}".replace(",", ".") + " TL", "black", 96, GREEN, 6, WHITE), 1450, 330) if t > 1.0 else None
    place_anim(world, stamp("TAMİR BEDELİ HESABINDA ✓", 56, GREEN), 760, 760, t, dur, "stamp", 2.8, 0.25, -4)
    return {"mascot": "heyecanli:kutlama"}


def s_cta(world, t, dur):
    t1 = text_sprite("HAKLARINI KORUYAN", "black", 80, INK)
    t2 = text_sprite("NET REHBERLER", "black", 110, RED)
    place_anim(world, t1, W / 2, 300, t, dur, "up", 0.0)
    place_anim(world, t2, W / 2, 410, t, dur, "pop", 0.2)
    sb = sub_button(1 if t > 3.0 else 0)
    place_anim(world, sb, W / 2, 640, t, dur, "pop", 0.8, 0.35)
    x, y = path(t, [(0, 1400, 950), (1.8, 1400, 950), (2.8, W / 2 + 40, 650)])
    draw_cursor(world, x, y, t, (2.95,), 48)
    return {"mascot": "goz_kirp:selam" if t < 3.0 else "kahkaha:kutlama"}


# ================================================================ kurgu (TTS metniyle birebir)
def build():
    D_ED_DUR = E_SEND + 3.0
    segs = [
        Seg(7.0, s_hook, ["elektrik kesintisi veya voltaj dalgalanması yüzünden",
                          "evindeki beyaz eşya ya da kombi arızalandıysa",
                          "tüm masrafı dağıtım şirketinden *GERİ ALABİLİRSİN*"],
            None, [(0, "impact"), (0.3, "error"), (4.2, "impact")], "saskin"),
        Seg(3.6, s_overview, ["*DÖRT NET ADIMDA* süreci anlatıyorum"], None, [(0.4 + k * 0.4, "pop") for k in range(4)]),
        Seg(7.6, s_phone, ["birinci adım arızadan hemen sonra *DAĞITIM ŞİRKETİNİ* arayıp",
                           "kesinti veya arıza *KAYIT NUMARASI* al"],
            ("ADIM 1/4", "Arıza kaydı al"), [(1.0, "click"), (1.45, "click"), (1.9, "click"), (2.5, "click"), (2.6, "ding")] +
            key_sfx(4.5, "4471829", 9) + [(5.6, "impact")]),
        Seg(9.4, s_report, ["ikinci adım cihazı *YETKİLİ SERVİSE* göster",
                            "servis raporuna arızanın *VOLTAJ DALGALANMASINDAN* kaynaklandığını mutlaka yazdır",
                            "ve *FATURANI* sakla"],
            ("ADIM 2/4", "Servis raporu"), [(0.9, "click")] + key_sfx(1.0, REPORT_TXT1 + REPORT_TXT2, 14) +
            [(1.0 + (len(REPORT_TXT1) + len(REPORT_TXT2)) / 14 + 0.6, "impact"), (5.6, "whoosh"), (6.6, "impact")]),
        Seg(D_SEND + 3.0, s_dist, ["üçüncü adım dağıtım şirketinin *ONLINE İŞLEMLER* ekranına gir",
                                   "*TAZMİNAT BAŞVURUSU* bölümünden",
                                   "servis raporunu faturanı ve *IBAN* bilgini",
                                   "yükleyip *GÖNDER*"],
            ("ADIM 3/4", "Online tazminat başvurusu"),
            [(D_CLICK_TILE, "click"), (D_TES0 - 0.2, "click"), (D_KAY0 - 0.2, "click"), (D_IBAN0 - 0.2, "click")] +
            key_sfx(D_TES0, V_TES, 10) + key_sfx(D_KAY0, V_KAY, 10) + key_sfx(D_IBAN0, V_IBAN, 15) +
            [(u, "click") for u in D_UP] + [(u + 0.9, "ding") for u in D_UP] + [(D_SEND, "click"), (D_SEND + 0.35, "ding")]),
        Seg(4.6, s_wait, ["dördüncü adım şirket *10 İŞ GÜNÜ* içinde", "ödeme *YAPMAZSA*"],
            ("ADIM 4/4", "Tüketici Hakem Heyeti"), [(0.6 + k * 0.22, "tick") for k in range(10)] + [(3.0, "error"), (3.0, "impact")]),
        Seg(D_ED_DUR, s_edevlet, ["aynı belgelerle *e-DEVLET'TEN*", "*TÜKETİCİ HAKEM HEYETİ'NE*", "*ÜCRETSİZ* başvur"],
            ("ADIM 4/4", "Tüketici Hakem Heyeti"),
            [(1.0, "click"), (E_CLICK, "click"), (E_TUR, "click"), (E_KARSI0 - 0.2, "click"), (E_TUTAR0 - 0.2, "click"),
             (E_UP0, "click"), (E_UP0 + 1.2, "ding"), (E_FREE, "impact"), (E_SEND, "click"), (E_SEND + 0.35, "ding")] +
            key_sfx(E_Q0, E_Q, E_CPS) + key_sfx(E_KARSI0, V_KARSI, 17) + key_sfx(E_TUTAR0, "12.450 TL", 12)),
        Seg(5.4, s_result, ["karar çıktığında *TÜM TAMİR BEDELİ*", "hesabına *YATIRILIR*"], None,
            [(0.6, "ding")] + [(1.2 + k * 0.1 + 0.25, "tick") for k in range(10)] + [(2.8, "impact")]),
        Seg(5.0, s_cta, ["haklarını koruyan *NET REHBERLER* için", "*ABONE OLMAYI* unutma"], None,
            [(0.8, "pop"), (2.95, "click"), (3.0, "ding")]),
    ]
    return Tutorial(segs, voice=VOICE)


def main():
    os.makedirs(OUT, exist_ok=True)
    tu = build()
    print(f"süre: {tu.duration:.1f} sn")
    wav = audio.mix(tu.duration, tu.events(), os.path.join(OUT, "elektrik_yatay_audio.wav"), voice_path=VOICE,
                    voice_offset=tu.voice_offset)
    render(tu.frame, tu.duration, (W, H), os.path.join(OUT, "elektrik_yatay.mp4"), wav)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        tu = build()
        ts = [float(x) for x in sys.argv[2:]] or [s + g.dur * f for s, g in zip(tu.starts, tu.segs) for f in (0.35, 0.85)]
        ims = [tu.frame(x).convert("RGB").resize((480, 270)) for x in ts]
        cols = 4
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (480 * cols, 270 * rows), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * 480, (k // cols) * 270))
        os.makedirs(OUT, exist_ok=True)
        sheet.save(os.path.join(OUT, "preview_elektrik_yatay.jpg"))
    else:
        main()
