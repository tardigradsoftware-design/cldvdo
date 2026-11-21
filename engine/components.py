"""Ortak görsel bileşenler: maskot, karaoke altyazı, imleç, ikonlar, kartlar."""
import math
from functools import lru_cache

from PIL import Image

from .core import (BLUE, GREEN, GREY, INK, RED, SS, WHITE, YELLOW, canvas, card_base, dtext, finish, font,
                   pill, place, text_size, upper_tr)


# ---------------------------------------------------------------- maskot "HAKKO"
@lru_cache(maxsize=64)
def mascot(expr="normal", size=220, blink=False):
    W = size
    im, d = canvas(W, W * 1.12)
    S = SS * W / 220.0

    def R(x0, y0, x1, y1):
        return [x0 * S, y0 * S, x1 * S, y1 * S]

    # gölge
    d.ellipse(R(55, 228, 165, 242), fill=(0, 0, 0, 40))
    # anten
    d.line([110 * S, 40 * S, 110 * S, 14 * S], fill=INK, width=int(7 * S))
    d.ellipse(R(98, 2, 122, 26), fill=YELLOW, outline=INK, width=int(5 * S))
    # kollar
    d.ellipse(R(6, 120, 46, 160), fill=RED, outline=INK, width=int(6 * S))
    d.ellipse(R(174, 120, 214, 160), fill=RED, outline=INK, width=int(6 * S))
    # gövde/kafa
    d.rounded_rectangle(R(28, 36, 192, 196), radius=int(54 * S), fill=RED, outline=INK, width=int(7 * S))
    # ekran
    d.rounded_rectangle(R(50, 66, 170, 140), radius=int(28 * S), fill=INK)
    # yanak
    d.ellipse(R(52, 146, 72, 158), fill=(255, 140, 130, 255))
    d.ellipse(R(148, 146, 168, 158), fill=(255, 140, 130, 255))
    # ayak
    d.rounded_rectangle(R(62, 190, 98, 214), radius=int(10 * S), fill=INK)
    d.rounded_rectangle(R(122, 190, 158, 214), radius=int(10 * S), fill=INK)
    # rozet (kalkan)
    cx, cy = 110, 170
    pts = [(cx - 15, cy - 14), (cx + 15, cy - 14), (cx + 15, cy + 2), (cx, cy + 16), (cx - 15, cy + 2)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=WHITE, outline=INK)
    d.line([((cx - 7) * S, (cy - 1) * S), ((cx - 1) * S, (cy + 5) * S), ((cx + 8) * S, (cy - 7) * S)],
           fill=GREEN, width=int(5 * S))
    # gözler
    ew = int(7 * S)
    if blink and expr in ("normal", "shock", "angry"):
        d.line(R(72, 104, 96, 104), fill=WHITE, width=ew)
        d.line(R(124, 104, 148, 104), fill=WHITE, width=ew)
    elif expr == "happy":
        d.arc(R(70, 92, 98, 120), 200, 340, fill=WHITE, width=ew)
        d.arc(R(122, 92, 150, 120), 200, 340, fill=WHITE, width=ew)
        d.arc(R(96, 112, 124, 132), 20, 160, fill=WHITE, width=int(5 * S))
    elif expr == "shock":
        d.ellipse(R(68, 84, 98, 118), outline=WHITE, width=ew)
        d.ellipse(R(122, 84, 152, 118), outline=WHITE, width=ew)
        d.ellipse(R(103, 121, 117, 135), fill=WHITE)
    elif expr == "angry":
        d.line(R(70, 88, 98, 98), fill=WHITE, width=ew)
        d.line(R(150, 88, 122, 98), fill=WHITE, width=ew)
        d.ellipse(R(78, 100, 92, 116), fill=WHITE)
        d.ellipse(R(128, 100, 142, 116), fill=WHITE)
    elif expr == "wink":
        d.ellipse(R(74, 90, 92, 116), fill=WHITE)
        d.arc(R(122, 92, 150, 120), 200, 340, fill=WHITE, width=ew)
        d.arc(R(96, 112, 124, 132), 20, 160, fill=WHITE, width=int(5 * S))
    else:
        d.ellipse(R(74, 88, 92, 118), fill=WHITE)
        d.ellipse(R(128, 88, 146, 118), fill=WHITE)
    return finish(im)


# Varsayılan maskot: TOKMAK (maskot/tokmak_maskot.py). Diğerleri: ("pro", "baykus"), ("robot", None)
MASCOT = ("tokmak", "selam")
_TOKMAK_MAP = {"happy": "mutlu", "shock": "saskin", "angry": "kizgin", "wink": "goz_kirp", "point": "ciddi"}


def get_mascot(expr, size, blink):
    kind, name = MASCOT
    if kind == "tokmak":
        import os, sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "maskot"))
        from tokmak_maskot import tokmak
        poz = "selam"
        if ":" in expr:
            expr, poz = expr.split(":", 1)
        return tokmak(_TOKMAK_MAP.get(expr, expr), poz, int(size * 1.15), blink)
    if kind == "pro":
        from .mascots_pro import pro_mascot
        return pro_mascot(name, expr, int(size * 1.05), blink)
    return mascot(expr, size, blink)


def draw_mascot(base, x, y, t, expr="normal", size=220, hop_t=None):
    """Nefes alma + göz kırpma + isteğe bağlı zıplama."""
    blink = (t % 3.1) < 0.12
    bob = math.sin(t * 3.2) * 6
    sq = 1.0
    if hop_t is not None and 0 <= t - hop_t < 0.45:
        k = (t - hop_t) / 0.45
        bob -= math.sin(k * math.pi) * 38
        sq = 1 + 0.06 * math.sin(k * math.pi * 2)
    spr = get_mascot(expr, size, blink)
    place(base, spr, x, y + bob, scale=sq)


# ---------------------------------------------------------------- karaoke altyazı
def caption_words(text):
    """'ADINA *HAT* açılmış' -> [(KELİME, vurgu)]"""
    out = []
    for w in text.split():
        emph = w.startswith("*") and w.endswith("*")
        out.append((upper_tr(w.strip("*")), emph))
    return out


def caption_groups(words, max_chars=16, max_words=3):
    groups, cur = [], []
    for i, (w, e) in enumerate(words):
        if cur and (len(" ".join(words[j][0] for j in cur + [i])) > max_chars or len(cur) >= max_words):
            groups.append(cur)
            cur = []
        cur.append(i)
    if cur:
        groups.append(cur)
    return groups


@lru_cache(maxsize=4096)
def caption_sprite(group_words, active, size=58, gap=10):
    """group_words: ((kelime, vurgu),...) ; active: aktif kelime indeksi (grup içi)."""
    parts = []
    for k, (w, e) in enumerate(group_words):
        if k == active:
            parts.append(pill(w, "black", size, WHITE, RED, border=0, pad=(16, 10), radius=10, shadow=6))
        elif k < active:
            parts.append(pill(w, "black", size, INK, WHITE, border=0, pad=(12, 10), radius=10, shadow=0))
        else:
            parts.append(pill(w, "black", size, (190, 190, 190, 255), WHITE, border=0, pad=(12, 10), radius=10))
    wsum = sum(p.width for p in parts) + gap * (len(parts) - 1)
    h = max(p.height for p in parts)
    im = Image.new("RGBA", (wsum, h), (0, 0, 0, 0))
    x = 0
    for p in parts:
        im.alpha_composite(p, (x, (h - p.height) // 2))
        x += p.width + gap
    return im


class Captions:
    """Sahne süresine yayılmış kelime kelime altyazı."""

    def __init__(self, text, start, dur, lead=0.1, tail=0.25, max_chars=16, max_words=3):
        self.words = caption_words(text)
        self.groups = caption_groups(self.words, max_chars, max_words)
        n = len(self.words)
        span = max(0.3, dur - lead - tail)
        weights = [0.55 + 0.06 * len(w) for w, _ in self.words]
        tot = sum(weights)
        self.times = []
        acc = start + lead
        for wgt in weights:
            self.times.append(acc)
            acc += span * wgt / tot
        self.end = start + dur

    def word_starts(self):
        return list(self.times)

    def draw(self, base, x, y, t, size=58):
        if t < self.times[0] or t >= self.end:
            return
        idx = max(i for i, ts in enumerate(self.times) if ts <= t)
        gi = next(g for g in self.groups if idx in g)
        rel = gi.index(idx)
        spr = caption_sprite(tuple(self.words[i] for i in gi), rel, size)
        k = (t - self.times[idx]) / 0.12
        sc = 1.0 + (0.08 * (1 - k) if k < 1 else 0)
        place(base, spr, x, y, scale=sc)


# ---------------------------------------------------------------- imleç
@lru_cache(maxsize=8)
def cursor_sprite(size=44):
    im, d = canvas(size, size * 1.4)
    s = SS * size / 44.0
    pts = [(2, 2), (2, 46), (13, 35), (21, 54), (29, 50), (21, 32), (36, 32)]
    d.polygon([(x * s, y * s) for x, y in pts], fill=WHITE)
    d.line([(x * s, y * s) for x, y in pts + [pts[0]]], fill=INK, width=int(3.2 * s), joint="curve")
    return finish(im)


def draw_cursor(base, x, y, t=0.0, click_times=(), size=44):
    for ct in click_times:
        dt = t - ct
        if 0 <= dt < 0.45:
            k = dt / 0.45
            r = 14 + 46 * k
            ring = Image.new("RGBA", (int(2 * r + 8), int(2 * r + 8)), (0, 0, 0, 0))
            from PIL import ImageDraw
            dd = ImageDraw.Draw(ring)
            a = int(200 * (1 - k))
            dd.ellipse([4, 4, 2 * r + 4, 2 * r + 4], outline=(232, 52, 46, a), width=6)
            base.alpha_composite(ring, (int(x - r - 4), int(y - r - 4)))
    sc = 1.0
    for ct in click_times:
        if 0 <= t - ct < 0.15:
            sc = 0.85
    place(base, cursor_sprite(size), x - 2, y - 2, scale=sc, anchor="tl")


# ---------------------------------------------------------------- tuş görselleştirici
@lru_cache(maxsize=256)
def keycap(label, size=44):
    f = font("bold", size * SS)
    w, h, b = text_size(label, f)
    kw = max(size * 1.5, w / SS + 34)
    kh = size * 1.6
    im, d = canvas(kw + 6, kh + 10)
    d.rounded_rectangle([0, 8 * SS, kw * SS, (kh + 8) * SS], 12 * SS, fill=INK)
    d.rounded_rectangle([0, 0, kw * SS, kh * SS], 12 * SS, fill=WHITE, outline=INK, width=4 * SS)
    d.text((kw * SS / 2, kh * SS / 2), label, font=f, fill=INK, anchor="mm")
    return finish(im)


# ---------------------------------------------------------------- küçük ikonlar
@lru_cache(maxsize=64)
def icon_check(size=48, color=GREEN):
    im, d = canvas(size, size)
    d.ellipse([0, 0, size * SS, size * SS], fill=color)
    s = size * SS
    d.line([(s * .27, s * .52), (s * .44, s * .68), (s * .74, s * .34)], fill=WHITE, width=int(s * .12), joint="curve")
    return finish(im)


@lru_cache(maxsize=64)
def icon_x(size=48, color=RED):
    im, d = canvas(size, size)
    d.ellipse([0, 0, size * SS, size * SS], fill=color)
    s = size * SS
    w = int(s * .12)
    d.line([(s * .32, s * .32), (s * .68, s * .68)], fill=WHITE, width=w)
    d.line([(s * .68, s * .32), (s * .32, s * .68)], fill=WHITE, width=w)
    return finish(im)


@lru_cache(maxsize=16)
def icon_warn(size=80):
    im, d = canvas(size, size)
    s = size * SS
    d.polygon([(s / 2, s * .06), (s * .96, s * .9), (s * .04, s * .9)], fill=YELLOW, outline=INK)
    d.line([(s / 2, s * .06), (s * .96, s * .9), (s * .04, s * .9), (s / 2, s * .06)], fill=INK, width=int(s * .06), joint="curve")
    d.text((s / 2, s * .6), "!", font=font("black", int(s * .5)), fill=INK, anchor="mm")
    return finish(im)


@lru_cache(maxsize=32)
def sim_card(size=120, color=RED, label=""):
    im, d = canvas(size, size * 1.3)
    s = SS * size / 120
    d.polygon([(0, 0), (85 * s, 0), (120 * s, 35 * s), (120 * s, 156 * s), (0, 156 * s)], fill=INK)
    d.polygon([(6 * s, 6 * s), (82 * s, 6 * s), (114 * s, 38 * s), (114 * s, 150 * s), (6 * s, 150 * s)], fill=color)
    d.rounded_rectangle([30 * s, 55 * s, 90 * s, 115 * s], 10 * s, fill=YELLOW, outline=INK, width=int(4 * s))
    for y in (75, 95):
        d.line([30 * s, y * s, 90 * s, y * s], fill=INK, width=int(3 * s))
    d.line([60 * s, 55 * s, 60 * s, 115 * s], fill=INK, width=int(3 * s))
    if label:
        d.text((60 * s, 135 * s), label, font=font("black", int(16 * s)), fill=WHITE, anchor="mm")
    return finish(im)


def stamp(txt, size=64, color=RED):
    """Eğik mühür etiketi."""
    return pill(txt, "black", size, WHITE, color, border=5, pad=(24, 14), radius=10, shadow=8)
