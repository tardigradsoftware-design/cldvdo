"""Yeni nesil maskot konseptleri (nesne-karakterler). new_mascot(kind, expr, size, blink).
kind: kalkan | muhur | megafon | bekci | paragraf | klasor
"""
from functools import lru_cache

from .core import INK, SS, canvas, finish, font
from .mascots_pro import P, eye, mouth, brows, shadow

WHITE = (255, 255, 255, 255)
RED = (232, 52, 46, 255)
RED_D = (180, 32, 30, 255)
NAVY = (30, 52, 110, 255)
NAVY_D = (20, 36, 80, 255)
TEAL = (20, 170, 150, 255)
TEAL_D = (12, 128, 112, 255)
GOLD = (246, 190, 46, 255)
GOLD_D = (205, 145, 20, 255)
WOOD = (166, 104, 56, 255)
WOOD_D = (122, 74, 38, 255)
MANILA = (247, 206, 110, 255)
MANILA_D = (222, 172, 70, 255)
PAPER = (252, 250, 244, 255)
DOG = (214, 168, 120, 255)
DOG_D = (176, 128, 84, 255)
DOG_L = (246, 228, 204, 255)
PURPLE = (120, 72, 220, 255)
PURPLE_D = (88, 48, 176, 255)
BLUSH = (255, 150, 140, 255)


def legs(p, cx=150, top=300, bot=338, gap=24, col=INK):
    p.line([(cx - gap, top), (cx - gap, bot)], col, 9)
    p.line([(cx + gap, top), (cx + gap, bot)], col, 9)
    p.rr((cx - gap - 22, bot - 4, cx - gap + 12, bot + 14), 8, INK, ol=False)
    p.rr((cx + gap - 12, bot - 4, cx + gap + 22, bot + 14), 8, INK, ol=False)


def arm(p, x0, y0, x1, y1, hand=WHITE):
    p.line([(x0, y0), (x1, y1)], INK, 9)
    p.ell((x1 - 13, y1 - 13, x1 + 13, y1 + 13), hand)


def face(p, cx, cy, expr, blink, gap=26, col_blush=True):
    brows(p, cx - gap, cx + gap, cy - 26, expr)
    eye(p, cx - gap, cy, expr, blink)
    eye(p, cx + gap, cy, expr, blink)
    if col_blush:
        p.ell((cx - gap - 22, cy + 16, cx - gap - 4, cy + 26), BLUSH, ol=False)
        p.ell((cx + gap + 4, cy + 16, cx + gap + 22, cy + 26), BLUSH, ol=False)
    mouth(p, cx, cy + 34, expr)


# ---------------------------------------------------------------- 1) Kalkan
def kalkan(p, expr, blink):
    shadow(p, y=354, w=70)
    legs(p, top=292, bot=338)
    arm(p, 70, 170, 34, 214)
    arm(p, 230, 170, 268, 128)
    # sağ elde küçük tik bayrağı
    p.line([(268, 128), (268, 70)], INK, 6)
    p.rr((268, 66, 312 - 20, 100), 4, (24, 160, 88, 255), w=int(4 * p.s))
    body = [(58, 82), (150, 52), (242, 82), (236, 200), (150, 312), (64, 200)]
    p.poly(body, RED)
    p.poly([(150, 60), (234, 88), (228, 198), (150, 300)], RED_D, ol=False)
    inner = [(82, 98), (150, 76), (218, 98), (212, 194), (150, 280), (88, 194)]
    p.line(inner + [inner[0]], WHITE, 6)
    p.ell((96, 112, 204, 220), WHITE)
    face(p, 150, 158, expr, blink, gap=24, col_blush=False)


# ---------------------------------------------------------------- 2) Mühür
def muhur(p, expr, blink):
    shadow(p, y=354, w=84)
    legs(p, top=318, bot=338, gap=40)
    p.ell((112, 18, 188, 94), WOOD)
    p.arc((124, 30, 160, 66), 200, 290, (210, 150, 100, 255), 6)
    p.rr((132, 86, 168, 142), 8, WOOD)
    p.rr((62, 136, 238, 290), 22, WOOD)
    p.rr((62, 136, 100, 290), 18, WOOD_D, ol=False)
    p.line([(100, 140), (100, 286)], INK, 4)
    p.rr((52, 282, 248, 322), 10, RED)
    p.d.text(((150 + p.ox) * p.s, (302 + p.oy) * p.s), "ONAYLI", font=font("black", int(24 * p.s)), fill=WHITE, anchor="mm")
    arm(p, 64, 220, 28, 250, WOOD)
    arm(p, 236, 220, 272, 186, WOOD)
    p.rr((114, 160, 226, 270), 26, PAPER, w=int(4 * p.s))
    face(p, 170, 204, expr, blink, gap=22)


# ---------------------------------------------------------------- 3) Megafon
def megafon(p, expr, blink):
    shadow(p, y=354, w=76)
    legs(p, top=286, bot=338, gap=30)
    # ses dalgaları
    for k, r in enumerate((26, 48)):
        p.arc((236 - r, 150 - r - 20, 236 + r + 20, 150 + r + 20), 300, 60, RED, 7)
    # sap
    p.rr((120, 222, 152, 296), 10, INK, ol=False)
    # gövde (koni)
    cone = [(44, 128), (96, 116), (232, 60), (246, 64), (246, 246), (232, 250), (96, 194), (44, 182)]
    p.poly(cone, TEAL)
    p.poly([(96, 160), (232, 168), (246, 168), (246, 246), (232, 250), (96, 194)], TEAL_D, ol=False)
    p.line(cone + [cone[0]], INK, 6)
    p.rr((26, 120, 58, 190), 10, WHITE)
    p.ell((226, 58, 262, 252), (230, 245, 242, 255))
    arm(p, 120, 196, 96, 250)
    p.ell((108, 116, 220, 214), WHITE)
    face(p, 164, 160, expr, blink, gap=24, col_blush=False)


# ---------------------------------------------------------------- 4) Bekçi (bulldog)
def bekci(p, expr, blink):
    shadow(p, y=356, w=80)
    # gövde (takım elbise)
    p.rr((80, 214, 220, 334), 34, NAVY)
    p.poly([(150, 218), (124, 218), (150, 280)], WHITE, ol=False)
    p.poly([(150, 218), (176, 218), (150, 280)], WHITE, ol=False)
    p.poly([(144, 224), (156, 224), (160, 268), (150, 282), (140, 268)], RED, w=int(4 * p.s))
    p.rr((170, 236, 200, 266), 6, GOLD, w=int(4 * p.s))
    p.d.text(((185 + p.ox) * p.s, (251 + p.oy) * p.s), "★", font=font("black", int(16 * p.s)) if False else font("black", int(16 * p.s)), fill=INK, anchor="mm")
    p.rr((96, 326, 136, 348), 10, INK, ol=False)
    p.rr((164, 326, 204, 348), 10, INK, ol=False)
    p.ell((62, 250, 96, 284), DOG)
    p.ell((204, 250, 238, 284), DOG)
    # kulaklar
    p.poly([(70, 72), (40, 50), (52, 120)], DOG_D)
    p.poly([(230, 72), (260, 50), (248, 120)], DOG_D)
    # kafa
    p.rr((58, 56, 242, 226), 70, DOG)
    p.ell((92, 132, 208, 226), DOG_L)
    # gözler
    brows(p, 118, 182, 98, expr)
    eye(p, 118, 120, expr, blink)
    eye(p, 182, 120, expr, blink)
    # burun + ağız
    p.rr((130, 140, 170, 164), 12, INK, ol=False)
    p.ell((138, 144, 148, 150), (120, 120, 120, 255), ol=False)
    if expr == "shock":
        p.ell((136, 182, 164, 212), (120, 30, 30, 255))
    elif expr in ("happy", "wink"):
        p.chord((118, 170, 182, 214), 0, 180, (120, 30, 30, 255))
        p.chord((136, 190, 164, 214), 0, 180, (240, 120, 130, 255), ol=False)
    else:
        p.arc((122, 162, 152, 190), 20, 160, INK, 5)
        p.arc((148, 162, 178, 190), 20, 160, INK, 5)
    # alt dişler
    p.poly([(128, 196), (134, 184), (140, 196)], WHITE, w=int(3 * p.s))
    p.poly([(160, 196), (166, 184), (172, 196)], WHITE, w=int(3 * p.s))


# ---------------------------------------------------------------- 5) Paragraf (§)
def paragraf(p, expr, blink):
    shadow(p, y=354, w=64)
    legs(p, top=300, bot=338, gap=22)
    f = font("black", int(330 * p.s))
    x, y = (150 + p.ox) * p.s, (176 + p.oy) * p.s
    p.d.text((x + 10 * p.s, y + 10 * p.s), "§", font=f, fill=INK, anchor="mm", stroke_width=int(8 * p.s), stroke_fill=INK)
    p.d.text((x, y), "§", font=f, fill=PURPLE, anchor="mm", stroke_width=int(8 * p.s), stroke_fill=INK)
    arm(p, 96, 180, 50, 214)
    arm(p, 204, 160, 252, 120)
    p.ell((98, 54, 202, 132), WHITE)
    face(p, 150, 88, expr, blink, gap=22, col_blush=False)


# ---------------------------------------------------------------- 6) Klasör
def klasor(p, expr, blink):
    shadow(p, y=354, w=84)
    legs(p, top=306, bot=338, gap=36)
    # kağıtlar (saç)
    for k, (x, rot) in enumerate([(90, -10), (130, 4), (168, -4)]):
        p.poly([(x, 92), (x + 6 + rot, 30), (x + 56 + rot, 34), (x + 50, 96)], PAPER, w=int(5 * p.s))
        p.line([(x + 14 + rot, 50), (x + 42 + rot, 52)], (180, 180, 180, 255), 4)
    # sekme + gövde
    p.rr((52, 66, 130, 104), 10, MANILA_D)
    p.rr((46, 86, 254, 312), 18, MANILA)
    p.rr((46, 86, 254, 120), 14, MANILA_D, ol=False)
    p.line([(50, 120), (250, 120)], INK, 5)
    # ataç
    p.rr((222, 70, 240, 140), 9, None, w=int(5 * p.s))
    p.rr((228, 82, 236, 128), 4, None, w=int(3 * p.s))
    # etiket
    p.rr((96, 250, 204, 286), 6, WHITE, w=int(4 * p.s))
    p.d.text(((150 + p.ox) * p.s, (268 + p.oy) * p.s), "DELİL", font=font("black", int(22 * p.s)), fill=RED, anchor="mm")
    arm(p, 50, 200, 20, 236, MANILA)
    arm(p, 250, 200, 282, 162, MANILA)
    face(p, 150, 178, expr, blink, gap=30)


KINDS = {"kalkan": kalkan, "muhur": muhur, "megafon": megafon, "bekci": bekci, "paragraf": paragraf, "klasor": klasor}


@lru_cache(maxsize=256)
def new_mascot(kind="kalkan", expr="normal", size=260, blink=False):
    sx = size / 300.0
    im, d = canvas(size * 1.05, 380 * sx)
    p = P(d, SS * sx)
    KINDS[kind](p, expr, blink)
    return finish(im)
