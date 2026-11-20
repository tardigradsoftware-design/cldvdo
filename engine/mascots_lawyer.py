"""Avukat maskot adayları. Hepsi aynı imza: lawyer(kind, expr, size, blink) -> RGBA sprite.
kind: 'robot' | 'terazi' | 'insan' | 'kitap'   expr: normal | happy | shock | angry | wink
"""
from functools import lru_cache

from .core import INK, RED, WHITE, YELLOW, GREEN, SS, canvas, finish

ROBE = (28, 28, 34, 255)
SKIN = (255, 214, 176, 255)
HAIR = (60, 42, 32, 255)
GOLD = (245, 186, 40, 255)
BOOK = (176, 30, 36, 255)
PAPER = (250, 246, 236, 255)


def _eyes(d, R, S, expr, blink, lx, rx, y, col=WHITE, r=10, mouth_y=None, mouth_col=None):
    ew = int(6 * S)
    mc = mouth_col or col
    my = mouth_y if mouth_y is not None else y + 26
    if blink and expr in ("normal", "shock", "angry"):
        d.line(R(lx - 11, y, lx + 11, y), fill=col, width=ew)
        d.line(R(rx - 11, y, rx + 11, y), fill=col, width=ew)
    elif expr in ("happy", "wink"):
        if expr == "wink":
            d.ellipse(R(lx - r * .8, y - r * 1.3, lx + r * .8, y + r * 1.3), fill=col)
        else:
            d.arc(R(lx - 13, y - 10, lx + 13, y + 14), 200, 340, fill=col, width=ew)
        d.arc(R(rx - 13, y - 10, rx + 13, y + 14), 200, 340, fill=col, width=ew)
        d.arc(R((lx + rx) / 2 - 14, my - 12, (lx + rx) / 2 + 14, my + 8), 20, 160, fill=mc, width=int(5 * S))
    elif expr == "shock":
        d.ellipse(R(lx - 14, y - 16, lx + 14, y + 16), outline=col, width=ew)
        d.ellipse(R(rx - 14, y - 16, rx + 14, y + 16), outline=col, width=ew)
        d.ellipse(R((lx + rx) / 2 - 7, my - 6, (lx + rx) / 2 + 7, my + 10), fill=mc)
    elif expr == "angry":
        d.line(R(lx - 14, y - 16, lx + 12, y - 8), fill=col, width=ew)
        d.line(R(rx + 14, y - 16, rx - 12, y - 8), fill=col, width=ew)
        d.ellipse(R(lx - 7, y - 4, lx + 7, y + 12), fill=col)
        d.ellipse(R(rx - 7, y - 4, rx + 7, y + 12), fill=col)
        d.line(R((lx + rx) / 2 - 12, my + 2, (lx + rx) / 2 + 12, my + 2), fill=mc, width=int(5 * S))
    else:
        d.ellipse(R(lx - r * .8, y - r * 1.3, lx + r * .8, y + r * 1.3), fill=col)
        d.ellipse(R(rx - r * .8, y - r * 1.3, rx + r * .8, y + r * 1.3), fill=col)


def _gavel(d, R, S, x, y, rot_left=True):
    """Küçük tokmak (x,y = sap ucu)."""
    w = int(5 * S)
    d.line(R(x, y, x + 34, y - 30), fill=INK, width=int(11 * S))
    d.line(R(x, y, x + 34, y - 30), fill=(150, 90, 45, 255), width=int(6 * S))
    pts = [(x + 18, y - 52), (x + 60, y - 16), (x + 46, y - 2), (x + 4, y - 38)]
    d.polygon([(px * S, py * S) for px, py in pts], fill=(150, 90, 45, 255), outline=INK)
    d.line([(px * S, py * S) for px, py in pts + [pts[0]]], fill=INK, width=w)


def _jabot(d, R, S, cx, top):
    """Beyaz yaka/kravat (avukat yakalığı)."""
    d.polygon([(S * (cx - 18), S * top), (S * (cx + 18), S * top), (S * (cx + 10), S * (top + 34)), (S * (cx - 10), S * (top + 34))],
              fill=WHITE, outline=INK)
    d.line([(S * (cx - 18), S * top), (S * (cx - 10), S * (top + 34)), (S * (cx + 10), S * (top + 34)), (S * (cx + 18), S * top)],
           fill=INK, width=int(4 * S))
    d.line(R(cx, top + 4, cx, top + 32), fill=INK, width=int(3 * S))


# ---------------------------------------------------------------- A) Robot Avukat
def _robot(d, R, S, expr, blink):
    d.ellipse(R(55, 228, 165, 242), fill=(0, 0, 0, 40))
    # cübbe gövde
    d.rounded_rectangle(R(40, 120, 180, 218), radius=int(26 * S), fill=ROBE, outline=INK, width=int(7 * S))
    d.polygon([(S * 110, S * 128), (S * 84, S * 128), (S * 110, S * 190)], fill=RED)
    d.polygon([(S * 110, S * 128), (S * 136, S * 128), (S * 110, S * 190)], fill=RED)
    _jabot(d, R, S, 110, 126)
    # kollar + tokmak
    d.ellipse(R(18, 150, 54, 186), fill=ROBE, outline=INK, width=int(6 * S))
    d.ellipse(R(166, 150, 202, 186), fill=ROBE, outline=INK, width=int(6 * S))
    _gavel(d, R, S, 176, 166)
    # kafa
    d.line(R(110, 22, 110, 6), fill=INK, width=int(7 * S))
    d.ellipse(R(100, -2, 120, 18), fill=YELLOW, outline=INK, width=int(4 * S))
    d.rounded_rectangle(R(44, 18, 176, 130), radius=int(44 * S), fill=RED, outline=INK, width=int(7 * S))
    d.rounded_rectangle(R(62, 40, 158, 104), radius=int(24 * S), fill=INK)
    _eyes(d, R, S, expr, blink, 90, 130, 68, WHITE, mouth_y=92)
    # ayak
    d.rounded_rectangle(R(66, 210, 100, 228), radius=int(8 * S), fill=INK)
    d.rounded_rectangle(R(120, 210, 154, 228), radius=int(8 * S), fill=INK)


# ---------------------------------------------------------------- B) Terazi
def _terazi(d, R, S, expr, blink):
    d.ellipse(R(50, 228, 170, 242), fill=(0, 0, 0, 40))
    # kaide
    d.polygon([(S * 70, S * 232), (S * 150, S * 232), (S * 130, S * 205), (S * 90, S * 205)], fill=GOLD, outline=INK)
    d.line([(S * 70, S * 232), (S * 90, S * 205), (S * 130, S * 205), (S * 150, S * 232), (S * 70, S * 232)], fill=INK, width=int(6 * S))
    # direk
    d.rectangle(R(102, 120, 118, 208), fill=GOLD, outline=INK, width=int(5 * S))
    # kol
    d.rounded_rectangle(R(14, 54, 206, 68), radius=int(7 * S), fill=GOLD, outline=INK, width=int(5 * S))
    # kefeler
    for cx in (34, 186):
        d.line(R(cx, 62, cx - 18, 128), fill=INK, width=int(3 * S))
        d.line(R(cx, 62, cx + 18, 128), fill=INK, width=int(3 * S))
        d.chord(R(cx - 30, 110, cx + 30, 150), 0, 180, fill=GOLD, outline=INK, width=int(5 * S))
        d.line(R(cx - 30, 130, cx + 30, 130), fill=INK, width=int(5 * S))
    # yüz (orta yuvarlak)
    d.ellipse(R(62, 28, 158, 124), fill=RED, outline=INK, width=int(7 * S))
    d.ellipse(R(102, 6, 118, 22), fill=GOLD, outline=INK, width=int(4 * S))
    _eyes(d, R, S, expr, blink, 92, 128, 70, WHITE, mouth_y=96)
    d.ellipse(R(70, 88, 84, 98), fill=(255, 140, 130, 255))
    d.ellipse(R(136, 88, 150, 98), fill=(255, 140, 130, 255))


# ---------------------------------------------------------------- C) İnsan avukat (chibi)
def _insan(d, R, S, expr, blink):
    d.ellipse(R(55, 228, 165, 242), fill=(0, 0, 0, 40))
    # cübbe
    d.polygon([(S * 50, S * 222), (S * 70, S * 128), (S * 150, S * 128), (S * 170, S * 222)], fill=ROBE, outline=INK)
    d.line([(S * 50, S * 222), (S * 70, S * 128), (S * 150, S * 128), (S * 170, S * 222), (S * 50, S * 222)], fill=INK, width=int(7 * S))
    d.polygon([(S * 110, S * 130), (S * 88, S * 130), (S * 110, S * 200)], fill=RED)
    d.polygon([(S * 110, S * 130), (S * 132, S * 130), (S * 110, S * 200)], fill=RED)
    _jabot(d, R, S, 110, 128)
    # kol + dosya
    d.rounded_rectangle(R(140, 150, 196, 196), radius=int(6 * S), fill=PAPER, outline=INK, width=int(5 * S))
    d.line(R(150, 164, 186, 164), fill=(170, 170, 170, 255), width=int(4 * S))
    d.line(R(150, 176, 180, 176), fill=(170, 170, 170, 255), width=int(4 * S))
    d.ellipse(R(132, 164, 156, 188), fill=SKIN, outline=INK, width=int(5 * S))
    # baş
    d.ellipse(R(52, 18, 168, 134), fill=SKIN, outline=INK, width=int(7 * S))
    # saç
    d.chord(R(52, 14, 168, 100), 180, 360, fill=HAIR, outline=INK, width=int(6 * S))
    d.pieslice(R(48, 30, 100, 90), 180, 300, fill=HAIR)
    # gözlük
    for cx in (88, 132):
        d.ellipse(R(cx - 20, 66, cx + 20, 102), fill=WHITE, outline=INK, width=int(5 * S))
    d.line(R(108, 82, 112, 82), fill=INK, width=int(5 * S))
    _eyes(d, R, S, expr, blink, 88, 132, 84, INK, r=7, mouth_y=116, mouth_col=INK)
    d.ellipse(R(62, 104, 76, 114), fill=(255, 150, 140, 255))
    d.ellipse(R(144, 104, 158, 114), fill=(255, 150, 140, 255))
    # ayak
    d.rounded_rectangle(R(72, 216, 104, 232), radius=int(8 * S), fill=INK)
    d.rounded_rectangle(R(116, 216, 148, 232), radius=int(8 * S), fill=INK)


# ---------------------------------------------------------------- D) Kanun kitabı
def _kitap(d, R, S, expr, blink):
    d.ellipse(R(50, 228, 170, 242), fill=(0, 0, 0, 40))
    # sayfalar (arka)
    d.rounded_rectangle(R(46, 26, 186, 214), radius=int(14 * S), fill=PAPER, outline=INK, width=int(7 * S))
    for y in (60, 100, 140, 180):
        d.line(R(176, y, 184, y), fill=INK, width=int(3 * S))
    # kapak
    d.rounded_rectangle(R(34, 16, 172, 206), radius=int(14 * S), fill=BOOK, outline=INK, width=int(7 * S))
    d.rectangle(R(34, 26, 52, 196), fill=(140, 20, 26, 255))
    d.line(R(52, 20, 52, 202), fill=INK, width=int(5 * S))
    # altın şerit + § işareti
    d.rounded_rectangle(R(66, 150, 158, 188), radius=int(8 * S), fill=GOLD, outline=INK, width=int(4 * S))
    from .core import font
    d.text((112 * S, 170 * S), "§ KANUN", font=font("black", int(17 * S)), fill=INK, anchor="mm")
    # yüz
    d.rounded_rectangle(R(66, 44, 158, 132), radius=int(20 * S), fill=PAPER, outline=INK, width=int(5 * S))
    _eyes(d, R, S, expr, blink, 94, 130, 78, INK, r=8, mouth_y=106, mouth_col=INK)
    # papyon
    d.polygon([(S * 112, S * 140), (S * 90, S * 130), (S * 90, S * 150)], fill=INK)
    d.polygon([(S * 112, S * 140), (S * 134, S * 130), (S * 134, S * 150)], fill=INK)
    # kollar + tokmak
    d.ellipse(R(14, 120, 46, 152), fill=BOOK, outline=INK, width=int(6 * S))
    d.ellipse(R(170, 120, 202, 152), fill=BOOK, outline=INK, width=int(6 * S))
    _gavel(d, R, S, 180, 132)
    # ayak
    d.rounded_rectangle(R(66, 204, 98, 222), radius=int(8 * S), fill=INK)
    d.rounded_rectangle(R(116, 204, 148, 222), radius=int(8 * S), fill=INK)


KINDS = {"robot": _robot, "terazi": _terazi, "insan": _insan, "kitap": _kitap}


@lru_cache(maxsize=128)
def lawyer(kind="robot", expr="normal", size=220, blink=False):
    W = size
    im, d = canvas(W * 1.16, W * 1.12)
    S = SS * W / 220.0

    def R(x0, y0, x1, y1):
        return [(x0 + 6) * S, (y0 + 6) * S, (x1 + 6) * S, (y1 + 6) * S]

    KINDS[kind](d, R, S, expr, blink)
    return finish(im)
