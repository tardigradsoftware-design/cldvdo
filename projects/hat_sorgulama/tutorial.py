"""Senaryo: 'Adına gizli hat açılmış mı?' — YATAY adım adım anlatım (e-Devlet simülasyonu)."""
import math
import os
import sys
from functools import lru_cache

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from PIL import ImageDraw

from engine.core import (BLUE, GREEN, INK, RED, SS, WHITE, YELLOW, canvas, card_base, clamp, dtext, finish, font,
                         in_out_cubic, out_back, out_cubic, path, pill, place, place_anim, prog, render, text_sprite)
from engine.components import draw_cursor, icon_check, icon_warn, sim_card, stamp
from engine.tutorial import (BH, BW, BX, BY, CH, CW, CX0, CY0, H, W, Seg, Tutorial, cam_path, draw_browser,
                             page_to_world)
from engine import audio
from short import comment_ui, doc_card

OUT = os.environ.get("OUT_DIR", "out")
GREYT = (110, 110, 110, 255)
LINE = (215, 215, 215, 255)


def S(v):
    return int(v * SS)


def typing(t, t0, text, cps=12):
    return text[: int(clamp((t - t0) * cps, 0, len(text)))]


def key_events(t0, text, cps=12, label=None):
    out = []
    for k, ch in enumerate(text):
        lab = label or (ch.upper() if ch != " " else "Space")
        out.append((t0 + k / cps, lab))
    return out


# ================================================================ e-Devlet benzeri sayfalar (stilize)
def header(d, user=False, login_btn=True):
    d.rectangle([0, 0, S(CW), S(92)], fill=WHITE)
    d.line([0, S(92), S(CW), S(92)], fill=LINE, width=S(2))
    d.rounded_rectangle([S(40), S(18), S(96), S(74)], S(14), fill=RED)
    dtext(d, (68, 46), "e", "black", 40, WHITE, "mm")
    dtext(d, (112, 46), "e-Devlet Kapısı", "black", 32, INK, "lm")
    if user:
        d.ellipse([S(1500), S(24), S(1544), S(68)], fill=(200, 200, 200, 255))
        dtext(d, (1560, 46), "A**** Y*****  ▾", "bold", 24, INK, "lm")
    elif login_btn:
        d.rounded_rectangle([S(1530), S(22), S(1708), S(70)], S(10), fill=RED)
        dtext(d, (1619, 46), "Giriş Yap", "black", 24, WHITE, "mm")


# sayfa içi düzen sabitleri
SEARCH = (324, 210, 1300, 290)
ARA_BTN = (1310, 210, 1424, 290)
SUG_ROW = 76
LOGIN_CARD = (474, 120, 1274, 690)
TC_IN = (524, 300, 1224, 366)
PW_IN = (524, 420, 1224, 486)
LOGIN_BTN = (524, 526, 1224, 594)
TABLE = (60, 360, 1688, 360 + 64 + 3 * 92)


@lru_cache(maxsize=256)
def page_home(user=False, typed="", focus=False, sugg=False, hover=False):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=WHITE)
    d.rectangle([0, S(92), S(CW), S(400)], fill=(253, 241, 240, 255))
    header(d, user=user)
    dtext(d, (874, 150), "Size nasıl yardımcı olabilirim?", "black", 44, INK, "mm")
    x0, y0, x1, y1 = SEARCH
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=WHITE, outline=RED if focus else (190, 190, 190, 255), width=S(4 if focus else 3))
    dtext(d, (x0 + 28, (y0 + y1) / 2), typed if typed else "Hizmet, kurum veya belge ara", "semi", 32,
          INK if typed else (165, 165, 165, 255), "lm")
    if focus:
        cx = x0 + 28 + font("semi", 32 * SS).getlength(typed) / SS + 3
        d.rectangle([S(cx), S(y0 + 22), S(cx + 3), S(y1 - 22)], fill=INK)
    a0, b0, a1, b1 = ARA_BTN
    d.rounded_rectangle([S(a0), S(b0), S(a1), S(b1)], S(12), fill=RED)
    dtext(d, ((a0 + a1) / 2, (b0 + b1) / 2), "Ara", "black", 30, WHITE, "mm")
    # kutucuklar
    labels = ["Kurumlar", "Belediyeler", "Firmalar", "Popüler Hizmetler"]
    for k, lab in enumerate(labels):
        tx = 110 + k * 392
        d.rounded_rectangle([S(tx), S(450), S(tx + 360), S(640)], S(18), fill=(247, 247, 247, 255), outline=LINE, width=S(2))
        d.rounded_rectangle([S(tx + 28), S(480), S(tx + 92), S(544)], S(14), fill=(225, 225, 225, 255))
        dtext(d, (tx + 28, 580), lab, "bold", 28, (80, 80, 80, 255))
    if sugg:
        top = y1 - 4
        d.rounded_rectangle([S(x0), S(top), S(x1), S(top + SUG_ROW * 3 + 10)], S(12), fill=WHITE, outline=(190, 190, 190, 255), width=S(3))
        for r in range(3):
            ry = top + 6 + r * SUG_ROW
            if r == 0:
                if hover:
                    d.rectangle([S(x0 + 4), S(ry), S(x1 - 4), S(ry + SUG_ROW)], fill=(255, 236, 235, 255))
                d.rounded_rectangle([S(x0 + 22), S(ry + 14), S(x0 + 70), S(ry + 62)], S(10), fill=BLUE)
                dtext(d, (x0 + 46, ry + 38), "BTK", "black", 15, WHITE, "mm")
                dtext(d, (x0 + 88, ry + 12), "Mobil Hat Sorgulama", "black", 28, INK)
                dtext(d, (x0 + 88, ry + 46), "Bilgi Teknolojileri ve İletişim Kurumu", "semi", 20, GREYT)
            else:
                d.rounded_rectangle([S(x0 + 22), S(ry + 14), S(x0 + 70), S(ry + 62)], S(10), fill=(228, 228, 228, 255))
                d.rounded_rectangle([S(x0 + 88), S(ry + 18), S(x0 + 88 + 380 - r * 60), S(ry + 38)], S(8), fill=(228, 228, 228, 255))
                d.rounded_rectangle([S(x0 + 88), S(ry + 48), S(x0 + 88 + 260), S(ry + 62)], S(7), fill=(238, 238, 238, 255))
    return finish(im)


@lru_cache(maxsize=256)
def page_login(tc="", pw="", focus=None, pressed=False):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=(246, 246, 246, 255))
    header(d, login_btn=False)
    x0, y0, x1, y1 = LOGIN_CARD
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(18), fill=WHITE, outline=LINE, width=S(2))
    dtext(d, ((x0 + x1) / 2, y0 + 36), "Kimlik Doğrulama Sistemi", "black", 32, INK, "mm")
    tabs = ["e-Devlet Şifresi", "Mobil İmza", "e-İmza", "İnternet Bankacılığı"]
    tx = x0 + 30
    for k, tb in enumerate(tabs):
        f = font("bold", 19 * SS)
        wd = f.getlength(tb) / SS
        dtext(d, (tx, y0 + 82), tb, "bold", 19, RED if k == 0 else GREYT)
        if k == 0:
            d.rectangle([S(tx), S(y0 + 112), S(tx + wd), S(y0 + 116)], fill=RED)
        tx += wd + 34
    d.line([S(x0 + 20), S(y0 + 118), S(x1 - 20), S(y0 + 118)], fill=LINE, width=S(2))
    for (lab, box, val, key) in (("T.C. Kimlik No", TC_IN, tc, "tc"), ("e-Devlet Şifresi", PW_IN, pw, "pw")):
        a0, b0, a1, b1 = box
        dtext(d, (a0, b0 - 34), lab, "bold", 22, (70, 70, 70, 255))
        foc = focus == key
        d.rounded_rectangle([S(a0), S(b0), S(a1), S(b1)], S(10), fill=WHITE, outline=RED if foc else (190, 190, 190, 255), width=S(4 if foc else 2))
        dtext(d, (a0 + 22, (b0 + b1) / 2), val, "bold", 30, INK, "lm")
        if foc:
            cx = a0 + 22 + font("bold", 30 * SS).getlength(val) / SS + 3
            d.rectangle([S(cx), S(b0 + 16), S(cx + 3), S(b1 - 16)], fill=INK)
    a0, b0, a1, b1 = LOGIN_BTN
    d.rounded_rectangle([S(a0), S(b0), S(a1), S(b1)], S(12), fill=(190, 35, 30, 255) if pressed else RED)
    dtext(d, ((a0 + a1) / 2, (b0 + b1) / 2), "Giriş Yap", "black", 28, WHITE, "mm")
    dtext(d, (a1, b1 + 34), "Şifremi Unuttum", "semi", 20, BLUE, "rm")
    return finish(im)


@lru_cache(maxsize=32)
def page_service(loading=False, spin=0):
    im, d = canvas(CW, CH)
    d.rectangle([0, 0, S(CW), S(CH)], fill=WHITE)
    header(d, user=True)
    dtext(d, (60, 118), "Bilgi Teknolojileri ve İletişim Kurumu   ›   Mobil Hat Sorgulama", "semi", 22, GREYT)
    d.rounded_rectangle([S(60), S(160), S(120), S(220)], S(12), fill=BLUE)
    dtext(d, (90, 190), "BTK", "black", 18, WHITE, "mm")
    dtext(d, (140, 190), "Mobil Hat Sorgulama", "black", 46, INK, "lm")
    d.rounded_rectangle([S(60), S(250), S(1688), S(320)], S(12), fill=(236, 243, 255, 255), outline=(190, 210, 245, 255), width=S(2))
    dtext(d, (90, 285), "Bu hizmet ile adınıza kayıtlı mobil hatları operatör bazında görüntüleyebilirsiniz.", "semi", 24, (40, 60, 110, 255), "lm")
    x0, y0, x1, y1 = TABLE
    if loading:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for k in range(8):
            a = (k + spin) / 8 * 2 * math.pi
            c = int(80 + 150 * k / 8)
            d.ellipse([S(cx + 46 * math.cos(a) - 9), S(cy + 46 * math.sin(a) - 9), S(cx + 46 * math.cos(a) + 9), S(cy + 46 * math.sin(a) + 9)],
                      fill=(c, c, c, 255))
        return finish(im)
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(12), fill=WHITE, outline=LINE, width=S(2))
    d.rectangle([S(x0 + 2), S(y0 + 2), S(x1 - 2), S(y0 + 64)], fill=(245, 245, 245, 255))
    dtext(d, (x0 + 40, y0 + 32), "Operatör", "black", 24, (80, 80, 80, 255), "lm")
    dtext(d, (x1 - 40, y0 + 32), "Hat Sayısı", "black", 24, (80, 80, 80, 255), "rm")
    for k, (op, n) in enumerate(ROWS):
        ry = y0 + 64 + k * 92
        if k:
            d.line([S(x0 + 20), S(ry), S(x1 - 20), S(ry)], fill=LINE, width=S(2))
        dtext(d, (x0 + 40, ry + 46), op, "bold", 32, INK, "lm")
        dtext(d, (x1 - 60, ry + 46), n, "black", 40, INK, "rm")
    return finish(im)


ROWS = [("Turkcell", "1"), ("Vodafone", "2"), ("Türk Telekom", "0")]


def row_world(k):
    x0, y0, x1, y1 = TABLE
    ry = y0 + 64 + k * 92
    return page_to_world(x0, ry)[0], page_to_world(x0, ry)[1], page_to_world(x1, ry + 92)[0], page_to_world(x1, ry + 92)[1]


def center_world(box):
    x0, y0, x1, y1 = box
    return page_to_world((x0 + x1) / 2, (y0 + y1) / 2)


# ================================================================ segmentler
def s_hook(world, t, dur):
    l1 = text_sprite("ADINA HABERİN OLMADAN", "black", 76, INK)
    l2 = text_sprite("HAT AÇILMIŞ", "black", 140, RED)
    l3 = text_sprite("OLABİLİR!", "black", 140, RED)
    y = 230
    for spr in (l1, l2, l3):
        place(world, spr, 100, y, anchor="tl")
        y += spr.height + 4
    for k, (col, dx, rot) in enumerate([(RED, -190, 14), (BLUE, 0, 0), (GREEN, 190, -14)]):
        place_anim(world, sim_card(170, col), 1480 + dx, 430 + abs(dx) * 0.12, t, dur, "drop", -1, 0.3, rot)
    place_anim(world, stamp("SENİN Mİ?", 70), 1480, 720, t, dur, "stamp", 0.7, 0.22, -6)
    z = 1 + 0.06 * (1 - out_cubic(prog(t, 0, 0.4)))
    return {"cam": (z, W / 2, H / 2), "mascot": "shock"}


CHAPTERS = ["e-Devlet'e gir", "Hizmeti bul", "Listeyi oku", "Ne yapmalı?"]


@lru_cache(maxsize=8)
def chapter_card(k):
    im, d = card_base(380, 230)
    d.ellipse([S(30), S(30), S(100), S(100)], fill=RED, outline=INK, width=S(4))
    dtext(d, (65, 65), str(k + 1), "black", 40, WHITE, "mm")
    dtext(d, (30, 140), CHAPTERS[k], "black", 36, INK)
    return finish(im)


def s_overview(world, t, dur):
    t1 = text_sprite("2 DAKİKADA", "black", 96, RED)
    t2 = text_sprite("ADIM ADIM KONTROL EDELİM", "black", 72, INK)
    place_anim(world, t1, 110 + t1.width / 2, 250, t, dur, "left", 0.0)
    place_anim(world, t2, 110 + t2.width / 2, 250 + t1.height + 10, t, dur, "left", 0.1)
    for k in range(4):
        place_anim(world, chapter_card(k), 300 + k * 440, 640, t, dur, "pop", 0.5 + k * 0.45, 0.35, [-3, 2, -2, 3][k])
    return {"mascot": "happy"}


def s_teaser(world, t, dur):
    place_anim(world, doc_card(), 1350, 520, t, dur, "drop", 0.1, 0.4, 4)
    t1 = text_sprite("VİDEONUN SONUNDA", "black", 70, INK)
    t2 = text_sprite("DİLEKÇE ŞABLONU", "black", 96, RED)
    place_anim(world, t1, 110 + t1.width / 2, 400, t, dur, "left", 0.0)
    place_anim(world, t2, 110 + t2.width / 2, 400 + t1.height + 14, t, dur, "pop", 0.15)
    place_anim(world, stamp("ÜCRETSİZ", 56, GREEN), 1560, 820, t, dur, "stamp", 0.9, 0.22, -8)
    return {"mascot": "wink"}


def browser_in(world, t, url, page, focus=False):
    if t < 0.4:
        k = out_back(t / 0.4, 1.5)
        draw_browser(world, url, page, focus, scale=0.85 + 0.15 * k, alpha=clamp(t / 0.25))
    else:
        draw_browser(world, url, page, focus)


URL = "turkiye.gov.tr"
URL_T0, URL_CPS = 0.7, 11
ENTER_T = URL_T0 + len(URL) / URL_CPS + 0.25


def s_url(world, t, dur):
    typed = typing(t, URL_T0, URL, URL_CPS)
    loaded = t > ENTER_T + 0.25
    page = page_home() if loaded else None
    browser_in(world, t, typed if not loaded else "https://" + URL, page, focus=(0.5 < t < ENTER_T + 0.1))
    if ENTER_T < t < ENTER_T + 0.35:
        d = ImageDraw.Draw(world)
        d.rectangle([CX0, CY0, CX0 + int(CW * (t - ENTER_T) / 0.3), CY0 + 5], fill=RED)
    btn = page_to_world(1619, 46)
    x, y = path(t, [(0, 1100, 760), (ENTER_T + 0.3, 1100, 760), (ENTER_T + 1.3, btn[0], btn[1])])
    draw_cursor(world, x, y, t, (ENTER_T + 1.5,), 40)
    cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (0.6, 1.7, 520, 230), (ENTER_T + 0.2, 1.7, 520, 230),
                       (ENTER_T + 0.8, 1.0, W / 2, H / 2), (ENTER_T + 1.1, 1.0, W / 2, H / 2), (ENTER_T + 1.5, 1.35, 1500, 330)])
    keys = key_events(URL_T0, URL, URL_CPS, None) + [(ENTER_T, "Enter")]
    return {"cam": cam, "keys": keys}


TC_MASK = "1•••••••••8"
PW_MASK = "••••••••"
TC_T0, PW_T0, LOGIN_T = 1.0, 2.9, 4.4


def s_login(world, t, dur):
    tc = typing(t, TC_T0, TC_MASK, 10)
    pw = typing(t, PW_T0, PW_MASK, 10)
    focus = "tc" if 0.8 < t < 2.6 else ("pw" if 2.6 <= t < LOGIN_T else None)
    page = page_login(tc, pw, focus, LOGIN_T < t < LOGIN_T + 0.2)
    draw_browser(world, "https://giris.turkiye.gov.tr", page)
    tcw, pww, lbw = center_world(TC_IN), center_world(PW_IN), center_world(LOGIN_BTN)
    x, y = path(t, [(0, 1500, 330), (0.7, tcw[0] - 200, tcw[1]), (2.4, tcw[0] - 200, tcw[1]),
                    (2.7, pww[0] - 200, pww[1]), (4.0, pww[0] - 200, pww[1]), (4.3, lbw[0], lbw[1])])
    draw_cursor(world, x, y, t, (0.8, 2.7, LOGIN_T), 40)
    # ipucu kartı
    if t > 5.0:
        tip = tip_card()
        place_anim(world, tip, 1560, 560, t, dur, "right", 5.0, 0.4)
    cc = center_world(LOGIN_CARD)
    cam = cam_path(t, [(0, 1.35, 1500, 330), (0.6, 1.4, cc[0], cc[1] + 20), (4.6, 1.4, cc[0], cc[1] + 20), (5.2, 1.0, W / 2, H / 2)])
    keys = key_events(TC_T0, "12345678901", 10) + key_events(PW_T0, "********", 10, "•") + [(LOGIN_T - 0.05, "Enter")]
    return {"cam": cam, "keys": keys}


@lru_cache(maxsize=1)
def tip_card():
    w, h = 520, 330
    im, d = card_base(w, h, fill=(255, 250, 225, 255))
    ic = icon_warn(70)
    im.alpha_composite(ic.resize((ic.width * SS, ic.height * SS)), (S(26), S(24)))
    dtext(d, (112, 40), "Şifren yok mu?", "black", 34)
    dtext(d, (30, 130), "• PTT şubesinden al", "bold", 30)
    dtext(d, (30, 185), "• ya da İnternet Bankacılığı", "bold", 30)
    dtext(d, (52, 225), "ile giriş yap", "bold", 30)
    return finish(im)


Q = "mobil hat sorgulama"
Q_T0, Q_CPS = 1.4, 11
SUG_T = Q_T0 + 6 / Q_CPS
CLICK_SUG = 5.0


def s_search(world, t, dur):
    typed = typing(t, Q_T0, Q, Q_CPS)
    hover = t > CLICK_SUG - 0.6
    page = page_home(True, typed, focus=t > 1.0, sugg=t > SUG_T, hover=hover)
    draw_browser(world, "https://www.turkiye.gov.tr", page)
    sw = center_world(SEARCH)
    row = page_to_world(SEARCH[0] + 300, SEARCH[3] + 2 + SUG_ROW / 2)
    x, y = path(t, [(0, 1100, 760), (0.9, sw[0] - 150, sw[1]), (3.6, sw[0] - 150, sw[1]), (4.4, row[0], row[1])])
    draw_cursor(world, x, y, t, (1.0, CLICK_SUG), 40)
    cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (1.0, 1.55, sw[0], sw[1] + 80), (5.2, 1.55, sw[0], sw[1] + 80), (5.8, 1.0, W / 2, H / 2)])
    return {"cam": cam, "keys": key_events(Q_T0, Q, Q_CPS)}


def overlay_rect(world, box, rgba):
    from PIL import Image
    x0, y0, x1, y1 = [int(v) for v in box]
    world.alpha_composite(Image.new("RGBA", (x1 - x0, y1 - y0), rgba), (x0, y0))


def callout(txt, color, size=34):
    return pill(txt, "black", size, WHITE, color, border=4, pad=(20, 12), shadow=6)


def ring(world, box, p, color=RED, width=8):
    """Kutunun etrafına çizilerek beliren elips."""
    if p <= 0:
        return
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(world)
    d.arc([x0, y0, x1, y1], -90, -90 + 360 * out_cubic(p), fill=color, width=width)


T_ROW1, T_ROW2, T_ROW3, T_SUM = 2.6, 5.0, 8.6, 10.6


def s_table(world, t, dur):
    loading = t < 0.9
    page = page_service(loading, int(t * 12) % 8)
    draw_browser(world, "https://www.turkiye.gov.tr/btk-mobil-hat-sorgulama", page)
    r1, r2, r3 = row_world(0), row_world(1), row_world(2)
    d = ImageDraw.Draw(world, "RGBA")
    if t > T_ROW1:
        d.rectangle([r1[0] + 4, r1[1] + 4, r1[2] - 4, r1[3] - 4], outline=GREEN, width=5)
        place_anim(world, callout("Senin hattın ✓", GREEN), r1[2] - 420, r1[1] + 46, t, 99, "pop", T_ROW1)
    if t > T_ROW2:
        overlay_rect(world, (r2[0] + 4, r2[1] + 4, r2[2] - 4, r2[3] - 4), (232, 52, 46, 40))
        d.rectangle([r2[0] + 4, r2[1] + 4, r2[2] - 4, r2[3] - 4], outline=RED, width=5)
        nx = r2[2] - 60
        ring(world, (nx - 70, r2[1] - 6, nx + 40, r2[3] + 6), prog(t, T_ROW2 + 0.2, 0.5))
        place_anim(world, callout("Sen 1 hat kullanıyorsan?!", RED), r2[2] - 520, r2[1] + 46, t, 99, "pop", T_ROW2 + 0.5)
        place_anim(world, icon_warn(90), r2[0] + 380, r2[1] + 46, t, 99, "pop", T_ROW2 + 0.6)
    if t > T_ROW3:
        place_anim(world, callout("Hat yok ✓", GREEN), r3[2] - 360, r3[1] + 46, t, 99, "pop", T_ROW3)
    if t > T_SUM:
        place_anim(world, stamp("1 HAT SENİN DEĞİL!", 60), 960, 470, t, dur, "stamp", T_SUM, 0.25, -4)
    tc = ((r1[0] + r1[2]) / 2, (r1[1] + r3[3]) / 2)
    cam = cam_path(t, [(0, 1.0, W / 2, H / 2), (1.2, 1.0, W / 2, H / 2), (1.9, 1.12, tc[0], tc[1] - 40),
                       (T_SUM - 0.3, 1.12, tc[0], tc[1] - 40), (T_SUM + 0.2, 1.0, W / 2, H / 2)])
    mascot = "shock" if T_ROW2 < t < T_ROW3 or t > T_SUM else "normal"
    return {"cam": cam, "mascot": mascot}


STEPS = [("Ekran görüntüsü al", "Listeyi kanıt olarak sakla"),
         ("Operatöre başvur", "Hattın sana ait olmadığını bildir, iptal ettir"),
         ("Savcılığa suç duyurusu", "Cumhuriyet Başsavcılığına dilekçe ver"),
         ("Banka ve kredi kayıtlarını kontrol et", "Adına kredi / kart başvurusu var mı bak")]
STEP_T = [0.6, 3.8, 7.6, 11.6]


@lru_cache(maxsize=8)
def steps_card(n):
    w, h = 1240, 740
    im, d = card_base(w, h)
    dtext(d, (50, 40), "TANIMADIĞIN HAT VARSA — HEMEN YAP:", "black", 44, RED)
    for k, (a, b) in enumerate(STEPS[:n]):
        top = 130 + k * 148
        d.rounded_rectangle([S(40), S(top), S(1200), S(top + 128)], S(18), fill=(246, 252, 248, 255), outline=INK, width=S(4))
        d.ellipse([S(66), S(top + 26), S(142), S(top + 102)], fill=RED, outline=INK, width=S(4))
        dtext(d, (104, top + 64), str(k + 1), "black", 40, WHITE, "mm")
        dtext(d, (176, top + 22), a, "black", 40)
        dtext(d, (176, top + 76), b, "semi", 30, (90, 90, 90, 255))
    return finish(im)


def s_steps(world, t, dur):
    draw_browser(world, "https://www.turkiye.gov.tr/btk-mobil-hat-sorgulama", page_service())
    overlay_rect(world, (0, 0, W, H), (20, 20, 20, int(150 * clamp(t / 0.4))))
    n = sum(1 for st in STEP_T if t >= st)
    if n:
        place_anim(world, steps_card(n), 960, 520, t, dur, "pop", 0.0, 0.35)
    return {"mascot": "normal"}


@lru_cache(maxsize=4)
def info_card(kind):
    w, h = 720, 520
    im, d = card_base(w, h)
    if kind == 0:
        d.rounded_rectangle([S(250), S(50), S(470), S(270)], S(24), fill=WHITE, outline=INK, width=S(6))
        d.rectangle([S(253), S(53), S(467), S(110)], fill=RED)
        dtext(d, (360, 195), "6", "black", 110, INK, "mm")
        dtext(d, (360, 330), "6 AYDA BİR", "black", 54, RED, "mm")
        dtext(d, (360, 410), "kontrolü tekrarla", "bold", 36, INK, "mm")
    else:
        for k, (cx, col) in enumerate([(250, BLUE), (360, RED), (470, GREEN)]):
            d.ellipse([S(cx - 50), S(70), S(cx + 50), S(170)], fill=col, outline=INK, width=S(5))
            d.rounded_rectangle([S(cx - 70), S(180), S(cx + 70), S(280)], S(40), fill=col, outline=INK, width=S(5))
        dtext(d, (360, 350), "AİLENLE BİRLİKTE", "black", 50, RED, "mm")
        dtext(d, (360, 425), "onların hesabını da kontrol et", "bold", 32, INK, "mm")
    return finish(im)


def s_bonus(world, t, dur):
    place_anim(world, info_card(0), 540, 520, t, dur, "pop", 0.2, 0.35, -2)
    place_anim(world, info_card(1), 1380, 520, t, dur, "pop", 3.4, 0.35, 2)
    return {"mascot": "happy"}


@lru_cache(maxsize=4)
def sub_button(state):
    if state == 0:
        return pill("ABONE OL", "black", 52, WHITE, RED, border=5, pad=(36, 18), shadow=8)
    return pill("ABONE OLUNDU ✓", "black", 52, INK, (225, 225, 225, 255), border=5, pad=(36, 18), shadow=8)


def s_cta(world, t, dur):
    typed = typing(t, 0.5, "HAT", 6)
    sent = t > 1.45
    place_anim(world, comment_ui("" if sent else typed, sent, t > 2.2), 560, 500, t, dur, "pop", 0.0, 0.35)
    t1 = text_sprite("YORUMA", "black", 80, INK)
    t2 = text_sprite("HAT YAZ", "black", 120, RED)
    place_anim(world, t1, 1120 + t1.width / 2, 260, t, dur, "left", 0.1)
    place_anim(world, t2, 1120 + t2.width / 2, 260 + t1.height + 40, t, dur, "pop", 0.2)
    t3 = text_sprite("dilekçe şablonunu göndereyim", "bold", 40, INK)
    place_anim(world, t3, 1120 + t3.width / 2, 520, t, dur, "up", 0.4)
    sb = sub_button(1 if t > 5.6 else 0)
    place_anim(world, sb, 1120 + sb.width / 2, 700, t, dur, "pop", 3.6, 0.35)
    send = (560 + 330, 500 + 245)
    bx = (1120 + sub_button(0).width / 2, 700)
    x, y = path(t, [(0, 900, 900), (1.0, 900, 900), (1.35, send[0], send[1]), (4.4, send[0], send[1]), (5.4, bx[0], bx[1])])
    draw_cursor(world, x, y, t, (1.4, 5.55), 44)
    return {"mascot": "happy" if t > 5.6 else "wink"}


# ================================================================ kurgu
def build():
    segs = [
        Seg(3.4, s_hook, ["adına haberin olmadan *HAT* açılmış olabilir"], None, [(0, "impact"), (0.7, "impact")], "shock"),
        Seg(4.8, s_overview, ["*2 DAKİKADA* adım adım kontrol edelim"], None,
            [(0.5 + k * 0.45, "pop") for k in range(4)], "happy"),
        Seg(4.0, s_teaser, ["sonunda *DİLEKÇE* şablonunu da vereceğim"], None, [(0.15, "whoosh_down"), (0.9, "impact")], "wink"),
        Seg(ENTER_T + 2.0, s_url, ["tarayıcıya *turkiye.gov.tr* yaz", "sağ üstten *GİRİŞ YAP* butonuna tıkla"],
            ("ADIM 1/4", "e-Devlet'e gir"),
            [(URL_T0 + k / URL_CPS, "key") for k in range(len(URL))] + [(ENTER_T, "click"), (ENTER_T + 1.5, "click")]),
        Seg(9.5, s_login, ["T.C. kimlik numaranı ve *e-Devlet şifreni* gir", "şifren yoksa *PTT'den* alabilirsin",
                           "ya da *İNTERNET BANKACILIĞI* ile girebilirsin"],
            ("ADIM 1/4", "e-Devlet'e gir"),
            [(0.8, "click"), (2.7, "click"), (LOGIN_T, "click"), (5.0, "pop")] +
            [(TC_T0 + k / 10, "key") for k in range(11)] + [(PW_T0 + k / 10, "key") for k in range(8)]),
        Seg(6.0, s_search, ["arama kutusuna *mobil hat sorgulama* yaz", "çıkan *BTK* hizmetine tıkla"],
            ("ADIM 2/4", "Hizmeti bul"),
            [(1.0, "click"), (CLICK_SUG, "click")] + [(Q_T0 + k / Q_CPS, "key") for k in range(len(Q))]),
        Seg(13.0, s_table, ["adına kayıtlı tüm hatlar *OPERATÖR* bazında listelenir", "her satırı tek tek *KONTROL ET*",
                            "kullanmadığın bir hat varsa *DİKKAT!*", "o hat *SENİN ADINA* dolandırıcılıkta kullanılabilir"],
            ("ADIM 3/4", "Listeyi oku"),
            [(T_ROW1, "ding"), (T_ROW2, "error"), (T_ROW2 + 0.5, "pop"), (T_ROW3, "ding"), (T_SUM, "impact")]),
        Seg(15.5, s_steps, ["önce listenin *EKRAN GÖRÜNTÜSÜNÜ* al", "operatöre başvur hattı *İPTAL* ettir",
                            "savcılığa *SUÇ DUYURUSUNDA* bulun", "bankadaki *KREDİ* kayıtlarını da kontrol et"],
            ("ADIM 4/4", "Tanımadığın hat varsa"), [(st, "ding") for st in STEP_T]),
        Seg(6.8, s_bonus, ["bu kontrolü *6 AYDA BİR* tekrarla", "anne babanla *BİRLİKTE* kontrol et"],
            ("BONUS", "Aileni koru"), [(0.2, "pop"), (3.4, "pop")], "happy"),
        Seg(8.0, s_cta, ["yoruma *HAT* yaz", "suç duyurusu *DİLEKÇESİNİ* göndereyim", "işine yaradıysa *ABONE OL*"],
            None, [(0.5 + k / 6, "key") for k in range(3)] + [(1.4, "click"), (2.2, "ding"), (5.55, "click"), (5.6, "ding")], "wink"),
    ]
    return Tutorial(segs)


def main():
    os.makedirs(OUT, exist_ok=True)
    tu = build()
    print(f"süre: {tu.duration:.1f} sn")
    wav = audio.mix(tu.duration, tu.events(), os.path.join(OUT, "tutorial_audio.wav"), music_gain=0.45)
    render(tu.frame, tu.duration, (W, H), os.path.join(OUT, "yatay_hat_sorgulama.mp4"), wav)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        tu = build()
        from PIL import Image
        ts = [float(x) for x in sys.argv[2:]] or [s + g.dur * f for s, g in zip(tu.starts, tu.segs) for f in (0.3, 0.8)]
        ims = [tu.frame(x).convert("RGB").resize((480, 270)) for x in ts]
        cols = 4
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (480 * cols, 270 * rows), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * 480, (k // cols) * 270))
        sheet.save(os.path.join(OUT, "preview_tutorial.jpg"))
    else:
        main()
