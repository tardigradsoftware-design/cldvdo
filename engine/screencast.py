"""GERÇEKÇİ EKRAN KAYDI modu (uzun videolar için).

Tam ekran tarayıcı + gerçekçi (stilize) portal arayüzü + otomatik yakınlaşan kamera (imleci takip eder)
+ minimal adım etiketi + bilgi notu. Karaoke altyazı ve büyük maskot YOK. Aynı plan JSON'unu kullanır.
"""
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from .core import SS, canvas, finish, clamp, font, lerp, out_back, out_cubic, path, place, prog, text_sprite, upper_tr
from .tutorial import H, W, Seg, Tutorial
from . import portals as P
from .director import key_phrase, kw_chips, wrap, words, amount_in

INK = (17, 24, 39, 255)
G700 = (55, 65, 81, 255)
G500 = (107, 114, 128, 255)
G300 = (209, 213, 219, 255)
G200 = (229, 231, 235, 255)
G100 = (243, 244, 246, 255)
G50 = (249, 250, 251, 255)
WHITE = (255, 255, 255, 255)
GREEN = (22, 163, 74, 255)
GREEN_BG = (220, 252, 231, 255)
CHROME_H = 86
PAGE_W, PAGE_H = W, H - CHROME_H


def S(v):
    return int(v * SS)


def tc(theme, a=255):
    c = P.THEMES[theme][1]
    return (c[0], c[1], c[2], a)


def tint(theme, k=0.9):
    c = P.THEMES[theme][1]
    return tuple(int(v + (255 - v) * k) for v in c) + (255,)


def txt(d, xy, s, f, size, fill=INK, anchor="la"):
    d.text((xy[0] * SS, xy[1] * SS), s, font=font(f, size * SS), fill=fill, anchor=anchor)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def shadow_box(d, box, r=12, fill=WHITE, border=G200, sh=6):
    x0, y0, x1, y1 = box
    for k in range(sh, 0, -2):
        a = int(10 * (sh - k + 2) / sh)
        d.rounded_rectangle([S(x0 - k / 2), S(y0 + k / 2), S(x1 + k / 2), S(y1 + k)], S(r + k / 2), fill=(0, 0, 0, a))
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(r), fill=fill, outline=border, width=S(1.5))


# ================================================================ tarayıcı penceresi (tam ekran)
@lru_cache(maxsize=32)
def chrome(theme, url, tab):
    im, d = canvas(W, CHROME_H)
    d.rectangle([0, 0, S(W), S(40)], fill=(222, 225, 230, 255))
    for k, c in enumerate([(255, 95, 86, 255), (255, 189, 46, 255), (39, 201, 63, 255)]):
        d.ellipse([S(18 + k * 22), S(14), S(30 + k * 22), S(26)], fill=c)
    d.rounded_rectangle([S(100), S(6), S(420), S(46)], S(10), fill=WHITE)
    d.rounded_rectangle([S(116), S(16), S(132), S(32)], S(4), fill=tc(theme))
    txt(d, (142, 15), tab[:30], "med", 15, G700)
    txt(d, (400, 13), "×", "reg", 18, G500)
    d.rectangle([0, S(40), S(W), S(CHROME_H)], fill=WHITE)
    for k, g in enumerate(["‹", "›", "↻"]):
        txt(d, (24 + k * 34, 63), g, "semi", 24, G500, "mm")
    d.rounded_rectangle([S(130), S(48), S(1700), S(78)], S(15), fill=G100)
    d.rounded_rectangle([S(146), S(57), S(158), S(69)], S(3), outline=G500, width=S(2))
    txt(d, (170, 63), url, "reg", 17, G700, "lm")
    d.ellipse([S(1850), S(50), S(1878), S(78)], fill=tc(theme))
    d.line([0, S(CHROME_H - 1), S(W), S(CHROME_H - 1)], fill=G200, width=S(1))
    return finish(im)


# ================================================================ gerçekçi sayfa
SIDEBAR = ["Ana Sayfa", "Hizmetler", "Başvurularım", "Belgelerim", "Ödemelerim", "Bildirimler", "Ayarlar"]
CX0, CY0 = 320, 230            # içerik kartının başlangıcı (sayfa koordinatı)
CARD_W = 980
FORM_X0, FORM_X1 = CX0 + 32, CX0 + CARD_W - 32


def _wh(k):
    return {"field": 96, "select": 96, "radio": 92, "textarea": 210, "upload": 66, "table": 0, "button": 56,
            "list": 0, "info": 64, "search": 64}[k]


def real_layout(widgets, top=CY0 + 32):
    boxes, y = {}, top
    for w in widgets:
        k = w["kind"]
        h = _wh(k)
        if k == "table":
            h = 40 + 48 + 56 * len(w.get("rows", []))
        if k == "list":
            h = 36 + 56 * len(w.get("rows", []))
        boxes[w["id"]] = (FORM_X0, y, FORM_X1, y + h)
        y += h + (22 if k != "upload" else 10)
    return boxes, y


def split_screens(widgets):
    screens, cur = [], []
    for w in widgets:
        _, bottom = real_layout(cur + [w])
        if cur and bottom > PAGE_H - 40:
            screens.append(cur)
            cur = [w]
        else:
            cur = cur + [w]
    screens.append(cur)
    return screens


def draw_real_widget(d, w, st, box, theme):
    k = w["kind"]
    x0, y0, x1, y1 = box
    acc = tc(theme)
    if k in ("field", "select", "search"):
        n, focus = st if st else (0, False)
        val = w.get("value", "")
        shown = val[:n] if k != "select" else (val if n else "")
        iy0 = y0 + (34 if k != "search" else 0)
        if k != "search":
            txt(d, (x0, y0 + 4), w.get("label", ""), "med", 19, G700)
        if focus:
            d.rounded_rectangle([S(x0 - 4), S(iy0 - 4), S(x1 + 4), S(y1 + 4)], S(12), fill=tint(theme, 0.82))
        d.rounded_rectangle([S(x0), S(iy0), S(x1), S(y1)], S(9), fill=WHITE, outline=acc if focus else G300, width=S(2 if focus else 1.5))
        ph = {"select": "Seçiniz", "search": "Hizmet, kurum veya belge ara"}.get(k, "")
        txt(d, (x0 + 18, (iy0 + y1) / 2), shown or ph, "reg", 21, INK if shown else (156, 163, 175, 255), "lm")
        if k == "select":
            txt(d, (x1 - 22, (iy0 + y1) / 2), "⌄", "semi", 22, G500, "mm")
        if focus and k != "select":
            cx = x0 + 18 + font("reg", 21 * SS).getlength(shown) / SS + 2
            d.rectangle([S(cx), S(iy0 + 14), S(cx + 2), S(y1 - 14)], fill=INK)
    elif k == "radio":
        sel = bool(st)
        txt(d, (x0, y0 + 4), w.get("label", "Başvuru türü"), "med", 19, G700)
        opts = w.get("options", [])
        bx = x0
        for i, o in enumerate(opts):
            on = sel and i == w.get("pick", 0)
            tw = font("med", 19 * SS).getlength(o) / SS + 64
            d.rounded_rectangle([S(bx), S(y0 + 36), S(bx + tw), S(y1)], S(9), fill=tint(theme, 0.9) if on else WHITE,
                                outline=acc if on else G300, width=S(2 if on else 1.5))
            d.ellipse([S(bx + 16), S((y0 + 36 + y1) / 2 - 9), S(bx + 34), S((y0 + 36 + y1) / 2 + 9)], outline=acc if on else G500, width=S(2))
            if on:
                d.ellipse([S(bx + 20), S((y0 + 36 + y1) / 2 - 5), S(bx + 30), S((y0 + 36 + y1) / 2 + 5)], fill=acc)
            txt(d, (bx + 44, (y0 + 36 + y1) / 2), o, "med", 19, INK, "lm")
            bx += tw + 12
    elif k == "textarea":
        n, focus = st if st else (0, False)
        txt(d, (x0, y0 + 4), w.get("label", "Açıklama"), "med", 19, G700)
        d.rounded_rectangle([S(x0), S(y0 + 34), S(x1), S(y1)], S(9), fill=WHITE, outline=acc if focus else G300, width=S(2 if focus else 1.5))
        left = n
        for i, ln in enumerate(w.get("lines", [])):
            if left <= 0:
                break
            txt(d, (x0 + 18, y0 + 50 + i * 34), ln[:left], "reg", 20, INK)
            left -= len(ln)
    elif k == "upload":
        p_ = (st or 0) / 10
        nm = w.get("value", "Belge.pdf")
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(9), fill=G50 if p_ < 1 else (240, 253, 244, 255),
                            outline=G300 if p_ < 1 else (134, 239, 172, 255), width=S(1.5))
        d.rounded_rectangle([S(x0 + 14), S(y0 + 13), S(x0 + 52), S(y1 - 13)], S(6), fill=(220, 38, 38, 255) if nm.endswith("pdf") else (37, 99, 235, 255))
        txt(d, (x0 + 33, (y0 + y1) / 2), "PDF" if nm.endswith("pdf") else "JPG", "bold", 11, WHITE, "mm")
        txt(d, (x0 + 66, y0 + 12), nm, "med", 19, INK)
        if p_ <= 0:
            d.rounded_rectangle([S(x1 - 150), S(y0 + 14), S(x1 - 14), S(y1 - 14)], S(8), fill=WHITE, outline=G300, width=S(1.5))
            txt(d, (x1 - 82, (y0 + y1) / 2), "Dosya Seç", "med", 17, G700, "mm")
        else:
            txt(d, (x0 + 66, y1 - 22), f"{int(240 * min(1, p_))} KB / 240 KB", "reg", 14, G500)
            bx0, bx1 = x0 + 260, x1 - 70
            d.rounded_rectangle([S(bx0), S(y1 - 22), S(bx1), S(y1 - 16)], S(3), fill=G200)
            d.rounded_rectangle([S(bx0), S(y1 - 22), S(bx0 + (bx1 - bx0) * min(1, p_)), S(y1 - 16)], S(3), fill=GREEN if p_ >= 1 else acc)
            if p_ >= 1:
                d.ellipse([S(x1 - 50), S((y0 + y1) / 2 - 14), S(x1 - 22), S((y0 + y1) / 2 + 14)], fill=GREEN)
                d.line([(S(x1 - 43), S((y0 + y1) / 2)), (S(x1 - 37), S((y0 + y1) / 2 + 6)), (S(x1 - 28), S((y0 + y1) / 2 - 6))], fill=WHITE, width=S(3))
    elif k == "table":
        hl = st if st is not None else -1
        txt(d, (x0, y0 + 4), w.get("label", "Sonuçlar"), "semi", 21, INK)
        d.rounded_rectangle([S(x0), S(y0 + 40), S(x1), S(y1)], S(9), fill=WHITE, outline=G200, width=S(1.5))
        d.rounded_rectangle([S(x0 + 1), S(y0 + 41), S(x1 - 1), S(y0 + 88)], S(9), fill=G50)
        txt(d, (x0 + 20, y0 + 64), "Kayıt", "semi", 16, G500, "lm")
        txt(d, (x1 - 20, y0 + 64), "Durum / Tutar", "semi", 16, G500, "rm")
        for i, r in enumerate(w.get("rows", [])):
            ry = y0 + 88 + i * 56
            a, b = (tuple(r) + ("",))[:2] if isinstance(r, (tuple, list)) else (r, "")
            if i == hl:
                d.rectangle([S(x0 + 1), S(ry), S(x1 - 1), S(ry + 56)], fill=tint(theme, 0.92))
                d.rectangle([S(x0 + 1), S(ry), S(x0 + 5), S(ry + 56)], fill=tc(theme))
            d.line([S(x0), S(ry), S(x1), S(ry)], fill=G200, width=S(1))
            txt(d, (x0 + 20, ry + 28), a, "med", 19, INK, "lm")
            if b:
                bw = font("semi", 16 * SS).getlength(b) / SS + 28
                good = i == hl
                d.rounded_rectangle([S(x1 - 20 - bw), S(ry + 14), S(x1 - 20), S(ry + 42)], S(14), fill=GREEN_BG if good else G100)
                txt(d, (x1 - 20 - bw / 2, ry + 28), b, "semi", 16, (21, 128, 61, 255) if good else G700, "mm")
    elif k == "list":
        hl = st if st is not None else -1
        txt(d, (x0, y0 + 4), w.get("label", "İşlemler"), "semi", 21, INK)
        for i, r in enumerate(w.get("rows", [])):
            ry = y0 + 36 + i * 56
            on = i == hl
            d.rounded_rectangle([S(x0), S(ry + 4), S(x1), S(ry + 52)], S(9), fill=tint(theme, 0.9) if on else WHITE,
                                outline=tc(theme) if on else G200, width=S(1.5))
            txt(d, (x0 + 20, ry + 28), str(r), "med" if not on else "semi", 19, INK, "lm")
            txt(d, (x1 - 20, ry + 28), "›", "semi", 24, G500, "rm")
    elif k == "button":
        pressed = bool(st)
        done = st == "done"
        c = GREEN if done else (tuple(max(0, v - 30) for v in acc[:3]) + (255,) if pressed else acc)
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(9), fill=c)
        txt(d, ((x0 + x1) / 2, (y0 + y1) / 2), "Gönderildi ✓" if done else w.get("label", "Gönder"), "semi", 21, WHITE, "mm")
    elif k == "info":
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(9), fill=(239, 246, 255, 255), outline=(191, 219, 254, 255), width=S(1.5))
        txt(d, (x0 + 18, (y0 + y1) / 2), w.get("value", "")[:70], "reg", 19, (30, 64, 175, 255), "lm")


def _page_base(d, theme, active_menu):
    d.rectangle([0, 0, S(PAGE_W), S(PAGE_H)], fill=(246, 247, 249, 255))
    d.rectangle([0, 0, S(PAGE_W), S(64)], fill=WHITE)
    d.rectangle([0, 0, S(PAGE_W), S(4)], fill=tc(theme))
    d.line([0, S(64), S(PAGE_W), S(64)], fill=G200, width=S(1))
    name, _, logo, _, _ = P.THEMES[theme]
    d.rounded_rectangle([S(28), S(14), S(66), S(52)], S(9), fill=tc(theme))
    txt(d, (47, 33), logo, "bold", 22, WHITE, "mm")
    txt(d, (80, 33), name, "semi", 22, INK, "lm")
    d.rounded_rectangle([S(1240), S(14), S(1640), S(50)], S(18), fill=G100)
    txt(d, (1262, 32), "Ara…", "reg", 16, G500, "lm")
    d.ellipse([S(1800), S(16), S(1832), S(48)], fill=G200)
    txt(d, (1790, 32), "A**** Y*****", "med", 16, G700, "rm")
    d.rectangle([0, S(65), S(280), S(PAGE_H)], fill=WHITE)
    d.line([S(280), S(65), S(280), S(PAGE_H)], fill=G200, width=S(1))
    for i, m in enumerate(SIDEBAR):
        y = 88 + i * 50
        on = i == active_menu
        if on:
            d.rounded_rectangle([S(14), S(y), S(266), S(y + 42)], S(8), fill=tint(theme, 0.9))
            d.rectangle([S(14), S(y + 8), S(17), S(y + 34)], fill=tc(theme))
        d.rounded_rectangle([S(30), S(y + 13), S(46), S(y + 29)], S(4), fill=tc(theme) if on else G300)
        txt(d, (60, y + 21), m, "semi" if on else "med", 17, INK if on else G700, "lm")


@lru_cache(maxsize=2048)
def real_page(theme, title, crumb, widgets_t, states_t, done):
    widgets = [dict(w) for w in widgets_t]
    states = dict(states_t)
    im, d = canvas(PAGE_W, PAGE_H)
    _page_base(d, theme, 1)
    txt(d, (CX0, 92), f"Hizmetler  ›  {crumb}", "reg", 16, G500)
    txt(d, (CX0, 120), title[:60], "bold", 32, INK)
    txt(d, (CX0, 168), "İşlemi tamamlamak için aşağıdaki adımları izleyin.", "reg", 18, G500)
    boxes, bottom = real_layout(widgets)
    shadow_box(d, (CX0, CY0, CX0 + CARD_W, max(bottom + 20, CY0 + 200)))
    for w in widgets:
        draw_real_widget(d, w, states.get(w["id"]), boxes[w["id"]], theme)
    # sağ bilgi paneli
    shadow_box(d, (1340, CY0, 1880, CY0 + 300))
    txt(d, (1366, CY0 + 26), "Bilgilendirme", "semi", 20, INK)
    for i, ln in enumerate(["Başvurunuz kayıt altına alınır.", "Sonuç e-posta/SMS ile bildirilir.", "Belgelerinizi PDF/JPG yükleyin."]):
        d.ellipse([S(1368), S(CY0 + 80 + i * 44), S(1378), S(CY0 + 90 + i * 44)], fill=tc(theme))
        txt(d, (1392, CY0 + 85 + i * 44), ln, "reg", 17, G700, "lm")
    if done:
        d.rounded_rectangle([S(1340), S(CY0 + 330), S(1880), S(CY0 + 430)], S(12), fill=GREEN_BG, outline=(134, 239, 172, 255), width=S(1.5))
        d.ellipse([S(1364), S(CY0 + 358), S(1408), S(CY0 + 402)], fill=GREEN)
        txt(d, (1386, CY0 + 380), "✓", "bold", 24, WHITE, "mm")
        txt(d, (1424, CY0 + 360), "İşleminiz alındı", "semi", 20, (21, 128, 61, 255))
        txt(d, (1424, CY0 + 390), "Kayıt No: 2026-" + str(abs(hash(title)) % 900000 + 100000), "reg", 16, G700)
    return finish(im)


@lru_cache(maxsize=512)
def real_home(theme, typed, focus, sugg, hover):
    im, d = canvas(PAGE_W, PAGE_H)
    _page_base(d, theme, 0)
    txt(d, (CX0 + 780, 200), "Size nasıl yardımcı olabiliriz?", "bold", 40, INK, "mm")
    txt(d, (CX0 + 780, 250), "Hizmet adını yazın, listeden seçin.", "reg", 19, G500, "mm")
    box = (CX0 + 330, 300, CX0 + 1230, 364)
    draw_real_widget(d, {"kind": "search", "value": typed}, (len(typed), focus), box, theme)
    txt(d, (CX0 + 330, 410), "Popüler hizmetler", "semi", 18, G700)
    bx = CX0 + 330
    for c in ["Belge Doğrulama", "Başvurularım", "Ödemeler", "Şikayet"]:
        tw = font("med", 17 * SS).getlength(c) / SS + 36
        d.rounded_rectangle([S(bx), S(440), S(bx + tw), S(480)], S(20), fill=WHITE, outline=G300, width=S(1.5))
        txt(d, (bx + tw / 2, 460), c, "med", 17, G700, "mm")
        bx += tw + 12
    if sugg:
        t1, t2 = sugg
        shadow_box(d, (box[0], box[3] + 8, box[2], box[3] + 8 + 3 * 66 + 12), r=10)
        for i in range(3):
            ry = box[3] + 14 + i * 66
            if i == 0 and hover:
                d.rounded_rectangle([S(box[0] + 6), S(ry), S(box[2] - 6), S(ry + 62)], S(8), fill=tint(theme, 0.9))
            d.rounded_rectangle([S(box[0] + 20), S(ry + 13), S(box[0] + 56), S(ry + 49)], S(8), fill=tc(theme) if i == 0 else G200)
            if i == 0:
                txt(d, (box[0] + 72, ry + 10), t1[:46], "semi", 20, INK)
                txt(d, (box[0] + 72, ry + 38), t2[:50], "reg", 15, G500)
            else:
                d.rounded_rectangle([S(box[0] + 72), S(ry + 16), S(box[0] + 72 + 300 - i * 60), S(ry + 30)], S(6), fill=G200)
                d.rounded_rectangle([S(box[0] + 72), S(ry + 38), S(box[0] + 72 + 180), S(ry + 48)], S(5), fill=G100)
    return finish(im), box


# ---------------------------------------------------------------- imleç (gerçekçi)
@lru_cache(maxsize=2)
def arrow(size=30):
    im, d = canvas(size + 6, size * 1.5 + 6)
    s = SS * size / 30
    pts = [(2, 2), (2, 34), (10, 26), (16, 40), (22, 37), (16, 24), (27, 24)]
    sh = [(x + 2, y + 3) for x, y in pts]
    d.polygon([(x * s, y * s) for x, y in sh], fill=(0, 0, 0, 70))
    d.polygon([(x * s, y * s) for x, y in pts], fill=(20, 20, 20, 255))
    inner = [(4.5, 7), (4.5, 29), (10.5, 23), (16.5, 36.5), (19.5, 35), (13.5, 21.5), (21.5, 21.5)]
    d.polygon([(x * s, y * s) for x, y in inner], fill=WHITE)
    return finish(im)


def draw_pointer(img, x, y, t, clicks, theme, touch=False):
    for ct in clicks:
        dt = t - ct
        if 0 <= dt < 0.45:
            k = dt / 0.45
            r = 10 + 34 * k
            ring = Image.new("RGBA", (int(2 * r + 8), int(2 * r + 8)), (0, 0, 0, 0))
            c = tc(theme)
            ImageDraw.Draw(ring).ellipse([4, 4, 2 * r + 4, 2 * r + 4], fill=(c[0], c[1], c[2], int(70 * (1 - k))),
                                         outline=(c[0], c[1], c[2], int(200 * (1 - k))), width=3)
            img.alpha_composite(ring, (int(x - r - 4), int(y - r - 4)))
    if touch:
        r = 22
        dot = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
        ImageDraw.Draw(dot).ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=(60, 60, 60, 90), outline=(255, 255, 255, 200), width=3)
        img.alpha_composite(dot, (int(x - r - 2), int(y - r - 2)))
    else:
        pressed = any(0 <= t - ct < 0.12 for ct in clicks)
        a = arrow(30)
        if pressed:
            a = a.resize((int(a.width * 0.88), int(a.height * 0.88)), Image.LANCZOS)
        img.alpha_composite(a, (int(x - 2), int(y - 2)))


# ---------------------------------------------------------------- ekran üstü öğeler
@lru_cache(maxsize=64)
def step_label(a, b):
    f1, f2 = font("bold", 22 * SS), font("med", 22 * SS)
    w1, w2 = f1.getlength(a) / SS, f2.getlength(b) / SS
    w = w1 + w2 + 64
    im, d = canvas(w, 52)
    d.rounded_rectangle([0, 0, S(w), S(52)], S(14), fill=(17, 24, 39, 225))
    d.rounded_rectangle([S(8), S(8), S(w1 + 32), S(44)], S(10), fill=(239, 68, 68, 255))
    txt(d, (20, 26), a, "bold", 22, WHITE, "lm")
    txt(d, (w1 + 44, 26), b, "med", 22, WHITE, "lm")
    return finish(im)


@lru_cache(maxsize=256)
def note_card(text, icon="i", accent=(239, 68, 68, 255), chips=()):
    lines = wrap(text, 26)[:3]
    h = 60 + 54 * len(lines) + (70 if chips else 0) + 30
    w = 820
    im, d = canvas(w + 20, h + 20)
    for k in range(10, 0, -2):
        d.rounded_rectangle([S(10 - k / 2), S(10 + k / 2), S(w + 10 + k / 2), S(h + 10 + k)], S(22), fill=(0, 0, 0, 8))
    d.rounded_rectangle([S(10), S(10), S(w + 10), S(h + 10)], S(20), fill=WHITE)
    d.rounded_rectangle([S(10), S(10), S(20), S(h + 10)], S(4), fill=accent)
    d.ellipse([S(44), S(40), S(104), S(100)], fill=accent)
    txt(d, (74, 70), icon, "bold", 30, WHITE, "mm")
    for i, ln in enumerate(lines):
        txt(d, (128, 40 + i * 54), ln, "bold", 36, INK)
    if chips:
        bx = 128
        y = 50 + 54 * len(lines)
        for c in chips:
            tw = font("semi", 20 * SS).getlength(c) / SS + 32
            if bx + tw > w:
                break
            d.rounded_rectangle([S(bx), S(y), S(bx + tw), S(y + 44)], S(22), fill=G100, outline=G300, width=S(1.5))
            txt(d, (bx + tw / 2, y + 22), c, "semi", 20, G700, "mm")
            bx += tw + 10
    return finish(im)


def good_chips(s):
    return tuple(c for c in kw_chips(s, 4) if c[:1].isupper() or c[:1].isdigit())[:3]


def icon_char(s):
    t = s.lower()
    if amount_in(s) or any(k in t for k in ("para", "ücret", "ödeme", " tl")):
        return "₺", (22, 163, 74, 255)
    if any(k in t for k in ("dikkat", "asla", "tuzak", "zamanaşımı", "ceza", "haksız")):
        return "!", (234, 88, 12, 255)
    if any(k in t for k in ("kanun", "yönetmelik", "tebliğ", "madde", "yargıtay")):
        return "§", (37, 99, 235, 255)
    if any(k in t for k in ("gün", "süre", "yıl", "tarih")):
        return "⏱", (124, 58, 237, 255)
    return "✓", (239, 68, 68, 255)


@lru_cache(maxsize=4)
def gradient_bg(theme):
    import numpy as np
    c = np.array(P.THEMES[theme][1], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    k = (xx / W * 0.5 + yy / H * 0.5)[..., None]
    a = np.array([245, 246, 250], np.float32)
    b = a * 0.86 + c * 0.14
    rgb = a * (1 - k) + b * k
    out = np.dstack([rgb, np.full((H, W), 255, np.float32)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def live(t, z=1.0, cx=W / 2, cy=H / 2):
    """Sürekli, yumuşak kamera kayması (iki farklı frekans → hiç durmaz)."""
    return (z * (1.02 + 0.014 * math.sin(t * 0.7)), cx + 16 * math.sin(t * 0.45), cy + 9 * math.cos(t * 0.53))


def cam_apply(img, z, cx, cy):
    if z <= 1.001:
        return img
    cw, ch = W / z, H / z
    x0 = clamp(cx - cw / 2, 0, W - cw)
    y0 = clamp(cy - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


# ================================================================ sahneler
def sent_times(sents, dur):
    from .scenes import sentence_times
    return sentence_times(sents, dur)


def make_portal(sc, dur):
    from .scenes import compile_portal
    C = compile_portal(sc, dur)
    theme = C["theme"]
    mobile = C["mobile"]
    tl = C["timeline"]
    srch = C["search"]
    title = C["title"]
    url = P.THEMES[theme][3].replace(" ", "")
    all_widgets = [w for s_ in C["screens"] for w in s_]
    screens = split_screens(all_widgets)
    wscreen = {w["id"]: i for i, s_ in enumerate(screens) for w in s_}
    submit = next((a for a in tl if a["do"] == "submit"), None)

    def fz(v):
        return tuple(fz(x) for x in v) if isinstance(v, (list, tuple)) else v

    def states_at(t):
        states, active = {}, None
        for a in tl:
            if a["do"] == "search":
                continue
            if a["t0"] - 0.35 <= t <= a["t1"] + 0.25:
                active = a
            if t < a["t0"]:
                continue
            pa = clamp((t - a["t0"]) / max(0.2, a["t1"] - a["t0"]))
            tg = a.get("targets", [])
            if a["do"] == "login":
                for j, wid in enumerate(tg):
                    pj = clamp(pa * 2 - j)
                    states[wid] = (int((11 if j == 0 else 8) * pj), 0 < pa * 2 - j < 1)
            elif a["do"] == "field":
                states[tg[0]] = (int(len(a["text"]) * clamp(pa / 0.85)), pa < 1)
            elif a["do"] == "textarea":
                states[tg[0]] = (int(sum(len(l) for l in a["lines"]) * clamp(pa / 0.9)), pa < 1)
            elif a["do"] == "upload":
                for j, wid in enumerate(tg):
                    states[wid] = int(clamp(pa * len(tg) - j) * 10)
            elif a["do"] in ("menu", "result"):
                states[tg[0]] = 0 if pa > 0.35 else -1
            elif a["do"] == "select":
                states[tg[0]] = pa > 0.4
            elif a["do"] == "submit":
                states[tg[0]] = "done" if pa > 0.6 else (0.3 < pa <= 0.6)
        return states, active

    def page_at(t):
        if srch and t < srch["t1"] - 0.05:
            q = srch["text"]
            cps = len(q) / max(0.6, (srch["t1"] - srch["t0"]) * 0.55)
            n = int(clamp((t - srch["t0"] - 0.25) * cps, 0, len(q)))
            spr, box = real_home(theme, q[:n], True, (q, P.THEMES[theme][0]) if n >= min(4, len(q)) else None, t > srch["t1"] - 0.6)
            return spr, {"q": box}, None, -1
        states, active = states_at(t)
        scr = 0
        for a in tl:
            if a.get("targets") and t >= a["t0"] - 0.35:
                scr = wscreen.get(a["targets"][0], scr)
        wl = screens[scr]
        st = {k: v for k, v in states.items() if any(w["id"] == k for w in wl)}
        done = submit is not None and t > submit["t0"] + 0.6 * (submit["t1"] - submit["t0"])
        spr = real_page(theme, title, P.THEMES[theme][0], tuple(tuple(sorted((k, fz(v)) for k, v in w.items())) for w in wl),
                        tuple(sorted(st.items())), done)
        boxes, _ = real_layout(wl)
        return spr, boxes, active, scr

    def target(a, boxes, t):
        if a is None:
            return None
        if a["do"] == "search":
            b = boxes.get("q")
            if not b:
                return None
            return (b[0] + 300, b[3] + 44) if t > a["t1"] - 0.7 else (b[0] + 200, (b[1] + b[3]) / 2)
        tg = a.get("targets") or []
        if not tg:
            return None
        k = min(len(tg) - 1, int(clamp((t - a["t0"]) / max(0.2, a["t1"] - a["t0"])) * len(tg)))
        b = boxes.get(tg[k])
        if not b:
            return None
        if a["do"] == "upload":
            return (b[2] - 82, (b[1] + b[3]) / 2)
        if a["do"] in ("field", "login", "textarea"):
            return (b[0] + 160, (b[1] + b[3]) / 2 + 14)
        if a["do"] == "list" or a["do"] == "menu" or a["do"] == "result":
            return (b[0] + 200, b[1] + 64)
        return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2 + 8)

    # imleç yolu (bir kez)
    order = ([srch] if srch else []) + [a for a in tl if a["do"] != "search"]
    pts = [(0, 1500, 900)]
    for a in order:
        _, boxes, _, _ = page_at(a["t0"] + 0.05)
        p0 = target(a, boxes, a["t0"] + 0.05)
        if p0:
            pts += [(a["t0"] - 0.05, *p0), (a["t0"] + 0.3, *p0)]
        if a["do"] in ("upload", "login", "search"):
            _, b2, _, _ = page_at(a["t1"] - 0.1)
            p1 = target(a, b2, a["t1"] - 0.1)
            if p1:
                pts += [(a["t1"] - 0.35, *p1), (a["t1"] - 0.05, *p1)]
    pts.sort(key=lambda p: p[0])
    clicks = []
    for a in order:
        clicks.append(a["t0"] + 0.1)
        if a["do"] == "search":
            clicks.append(a["t1"] - 0.15)
        if a["do"] == "upload":
            n = len(a.get("targets", []))
            clicks += [a["t0"] + (a["t1"] - a["t0"]) * j / n + 0.05 for j in range(n)]
        if a["do"] == "submit":
            clicks.append(a["t0"] + 0.4 * (a["t1"] - a["t0"]))
    ts, ds = sent_times(sc["sentences"], dur)

    def draw(world, t, d):
        spr, boxes, active, scr = page_at(t)
        if mobile:
            return draw_mobile(world, t, d, sc, spr, boxes, active, theme, title)
        world.alpha_composite(chrome(theme, url, P.THEMES[theme][0]), (0, 0))
        world.alpha_composite(spr, (0, CHROME_H))
        x, y = path(t, pts)
        y += CHROME_H
        idle = 1 - max([smooth(1 - abs(t - c) / 0.6) for c in clicks] + [0])
        x += idle * 7 * math.sin(t * 1.3)
        y += idle * 5 * math.cos(t * 1.1)
        draw_pointer(world, x, y, t, clicks, theme)
        # otomatik yakınlaşma: imleci izle
        act = active if active else (srch if srch and srch["t0"] - 0.4 <= t <= srch["t1"] + 0.4 else None)
        z, cx, cy = 1.0, W / 2, H / 2
        if act:
            a0, a1 = act["t0"], act["t1"]
            w_ = smooth((t - (a0 - 0.55)) / 0.5) * smooth(((a1 + 0.6) - t) / 0.5)
            zf = 1.7 if act["do"] in ("search", "field", "login", "upload") else 1.45
            z = 1 + (zf - 1) * w_
            cx, cy = lerp(W / 2, x, w_), lerp(H / 2, y, w_)
        return {"cam": live(t, z, cx, cy)}

    def keys():
        ks = []
        for a in tl:
            if a["do"] in ("search", "field"):
                txt_ = a["text"]
                cps = len(txt_) / max(0.4, (a["t1"] - a["t0"]) * (0.55 if a["do"] == "search" else 0.85))
                b = a["t0"] + (0.25 if a["do"] == "search" else 0)
                ks += [(b + j / cps, "key") for j in range(0, len(txt_), 2)]
            if a["do"] == "textarea":
                n = sum(len(l) for l in a["lines"])
                ks += [(a["t0"] + (a["t1"] - a["t0"]) * 0.9 * j / n, "key") for j in range(0, n, 2)]
            if a["do"] == "upload":
                n = len(a.get("targets", []))
                ks += [(a["t0"] + (a["t1"] - a["t0"]) * (j + 1) / n, "tick") for j in range(n)]
            if a["do"] == "submit":
                ks.append((a["t0"] + 0.6 * (a["t1"] - a["t0"]), "ding"))
        return ks
    sfx = [(c, "click") for c in clicks] + keys()
    return draw, sfx


@lru_cache(maxsize=4)
def phone_shell():
    w, h = 420, 860
    im, d = canvas(w + 30, h + 30)
    for k in range(14, 0, -2):
        d.rounded_rectangle([S(15 - k / 2), S(15 + k / 2), S(w + 15 + k / 2), S(h + 15 + k)], S(64), fill=(0, 0, 0, 9))
    d.rounded_rectangle([S(15), S(15), S(w + 15), S(h + 15)], S(62), fill=(28, 28, 32, 255))
    d.rounded_rectangle([S(25), S(25), S(w + 5), S(h + 5)], S(54), fill=WHITE)
    d.rounded_rectangle([S(w / 2 - 50), S(36), S(w / 2 + 80), S(66)], S(15), fill=(28, 28, 32, 255))
    txt(d, (70, 52), "9:41", "semi", 18, INK, "mm")
    d.rounded_rectangle([S(w - 70), S(45), S(w - 36), S(59)], S(4), outline=INK, width=S(2))
    d.rectangle([S(w - 67), S(48), S(w - 44), S(56)], fill=INK)
    return finish(im)


def draw_mobile(world, t, d, sc, spr, boxes, active, theme, title):
    world.alpha_composite(gradient_bg(theme), (0, 0))
    PX, PY = 700, 540
    shell = phone_shell()
    place(world, shell, PX, PY)
    # web sayfasını telefon ekranına "mobil" olarak yerleştir: içerik kartını kırp
    crop = spr.crop((CX0 - 10, 70, CX0 + CARD_W + 10, PAGE_H)).resize((380, int((PAGE_H - 70) * 380 / (CARD_W + 20))), Image.LANCZOS)
    hdr = Image.new("RGBA", (380, 92), tc(theme))
    ImageDraw.Draw(hdr).text((190, 56), P.THEMES[theme][0][:22], font=font("semi", 22), fill=WHITE, anchor="mm")
    x0, y0 = PX - 190, PY - 360
    world.alpha_composite(hdr, (x0, y0))
    world.alpha_composite(crop.crop((0, 0, 380, 690)), (x0, y0 + 92))
    ts, ds = sent_times(sc["sentences"], d)
    i = max(k for k in range(len(ts)) if ts[k] <= t)
    s = sc["sentences"][i]
    ic, col = icon_char(s)
    nc = note_card(key_phrase(s, 7), ic, col, good_chips(s))
    k = out_back(clamp((t - ts[i] - 0.15) / 0.4), 1.2)
    place(world, nc, 1360 + (1 - k) * 80, 520, alpha=clamp((t - ts[i]) / 0.3))
    # dokunma göstergesi
    if active is not None:
        p = None
        tg = active.get("targets") or []
        if tg and tg[0] in boxes:
            b = boxes[tg[0]]
            sx = (b[0] + b[2]) / 2 - (CX0 - 10)
            sy = (b[1] + b[3]) / 2 - 70
            p = (x0 + sx * 380 / (CARD_W + 20), y0 + 92 + sy * 380 / (CARD_W + 20))
        if p and p[1] < y0 + 780:
            draw_pointer(world, p[0], p[1], t, (active["t0"] + 0.1,), theme, touch=True)
    return {"cam": live(t, 1.0, W / 2 - 100, H / 2)}


def make_note(sc, dur, bg_fn=None):
    """Portal dışı cümleler: son ekranın bulanık görüntüsü üzerinde bilgi notu kartları."""
    sents = sc.get("sentences", [])
    ts, ds = sent_times(sents, dur)

    def draw(world, t, d):
        if bg_fn:
            world.alpha_composite(bg_fn(), (0, 0))
        else:
            world.alpha_composite(gradient_bg("edevlet"), (0, 0))
        i = max(k for k in range(len(ts)) if ts[k] <= t)
        s = sents[i]
        ic, col = icon_char(s)
        nc = note_card(key_phrase(s, 8), ic, col, good_chips(s))
        k = out_back(clamp((t - ts[i]) / 0.45), 1.3)
        place(world, nc, W / 2, H / 2 + (1 - k) * 60, scale=1.15 + 0.1 * k, alpha=clamp((t - ts[i]) / 0.3))
        return {"cam": live(t)}
    return draw, [(ts[i] + 0.05, "pop") for i in range(len(ts))]


def make_title(sc, dur, kind):
    title = sc.get("title") or key_phrase(" ".join(sc["sentences"]), 9)
    steps = sc.get("steps", [])

    def draw(world, t, d):
        world.alpha_composite(gradient_bg("uyap"), (0, 0))
        ImageDraw.Draw(world).rectangle([0, 0, W, H], fill=None)
        if kind == "hook":
            lines = wrap(title, 26)[:4]
            for i, ln in enumerate(lines):
                k = out_back(clamp((t - 0.1 - i * 0.12) / 0.45), 1.2)
                place(world, text_sprite(ln, "bold", 72, INK), 140, 300 + i * 92, anchor="l", alpha=clamp((t - i * 0.12) / 0.3))
            place(world, step_label("ADIM ADIM", "Rehber"), 140, 200, anchor="l", alpha=clamp(t / 0.3))
            if t > 0.8:
                nc = note_card(key_phrase(" ".join(sc["sentences"]), 7), *icon_char(" ".join(sc["sentences"])))
                place(world, nc, 1450, 640, alpha=clamp((t - 0.8) / 0.4))
        else:
            place(world, text_sprite(f"{len(steps)} adımda süreç", "bold", 64, INK), 140, 220, anchor="l", alpha=clamp(t / 0.3))
            for i, s in enumerate(steps):
                a = clamp((t - 0.4 - i * 0.4) / 0.35)
                if a <= 0:
                    continue
                y = 340 + i * 110
                row = Image.new("RGBA", (1100, 90), (0, 0, 0, 0))
                dr = ImageDraw.Draw(row)
                dr.rounded_rectangle([0, 0, 1099, 89], 16, fill=WHITE, outline=G200, width=2)
                dr.ellipse([22, 18, 76, 72], fill=(239, 68, 68, 255))
                dr.text((49, 45), str(i + 1), font=font("bold", 28), fill=WHITE, anchor="mm")
                dr.text((100, 45), s, font=font("semi", 32), fill=INK, anchor="lm")
                place(world, row, 140 + (1 - out_back(a)) * -60, y, anchor="l", alpha=a)
        return {"cam": live(t)}
    sfx = [(0.4 + i * 0.4, "pop") for i in range(len(steps))] if kind == "overview" else [(0.1, "whoosh")]
    return draw, sfx


def make_outro(sc, dur):
    def draw(world, t, d):
        world.alpha_composite(gradient_bg("uyap"), (0, 0))
        place(world, text_sprite("Haklarını koruyan net rehberler", "bold", 64, INK), W / 2, 380, alpha=clamp(t / 0.3))
        tc_ = min(2.6, d - 0.8)
        done = t > tc_ + 0.05
        b = Image.new("RGBA", (420, 96), (0, 0, 0, 0))
        dr = ImageDraw.Draw(b)
        dr.rounded_rectangle([0, 0, 419, 95], 48, fill=(60, 60, 60, 255) if done else (220, 38, 38, 255))
        dr.text((210, 48), "Abone olundu ✓" if done else "ABONE OL", font=font("bold", 38), fill=WHITE, anchor="mm")
        place(world, b, W / 2, 560, scale=out_back(clamp((t - 0.4) / 0.4)))
        x, y = path(t, [(0, 1500, 900), (tc_ - 0.9, 1500, 900), (tc_ - 0.1, W / 2 + 30, 575)])
        draw_pointer(world, x, y, t, (tc_,), "edevlet")
        return {"cam": live(t), "mascot": "kahkaha:kutlama" if done else "goz_kirp:selam"}
    tc_ = min(2.6, dur - 0.8)
    return draw, [(tc_, "click"), (tc_ + 0.05, "ding")]


def build_screencast(plan, total=None):
    """Plan → gerçekçi ekran kaydı tarzı Tutorial (altyazı yok, maskot sadece kapanışta)."""
    from .scenes import sdur, MIN_DUR
    scenes = plan["scenes"]
    durs = []
    for sc in scenes:
        d = sum(sdur(s) for s in sc.get("sentences", [])) or 3.0
        mn = {"hook": 3.6, "overview": 2.2 + 0.4 * len(sc.get("steps", [])), "portal": 4.0, "outro": 3.6}.get(sc["kind"], 2.0)
        durs.append(max(mn, d))
    if total:
        k = total / sum(durs)
        durs = [d * k for d in durs]
    segs, last_bg = [], [None]
    for sc, d in zip(scenes, durs):
        kind = sc["kind"]
        if kind == "portal":
            f, sfx = make_portal(sc, d)
            last_bg[0] = (f, d)
        elif kind in ("hook", "overview"):
            f, sfx = make_title(sc, d, kind)
        elif kind == "outro":
            f, sfx = make_outro(sc, d)
        else:
            bg = None
            if last_bg[0]:
                pf, pd = last_bg[0]

                @lru_cache(maxsize=1)
                def bg(pf=pf, pd=pd):
                    w = Image.new("RGBA", (W, H), (255, 255, 255, 255))
                    pf(w, pd - 0.05, pd)
                    w = w.filter(ImageFilter.GaussianBlur(8))
                    w.alpha_composite(Image.new("RGBA", (W, H), (240, 242, 246, 150)))
                    return w
            f, sfx = make_note(sc, d, bg)
        chap = sc.get("chapter")

        def wrapped(world, t, dd, f=f, chap=chap):
            info = f(world, t, dd) or {}
            return info
        seg = Seg(d, wrapped, [], None, sfx)
        seg.label = tuple(chap) if chap else None
        segs.append(seg)
    tu = Tutorial(segs, voice=None, mascot=False, captions=False, whoosh=0.25)
    base_frame = tu.frame

    def frame(t):
        img = base_frame(t)
        i = max(k for k, s in enumerate(tu.starts) if s <= t)
        lab = segs[i].label
        if lab:
            first = i == 0 or segs[i - 1].label != lab
            a = clamp((t - tu.starts[i]) / 0.35) if first else 1.0
            sl = step_label(*lab)
            place(img, sl, 32, H - 32 - sl.height + (1 - a) * 20, anchor="tl", alpha=a)
        return img
    tu.frame = frame
    return tu
