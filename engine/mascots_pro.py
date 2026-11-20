"""Profesyonel hukukçu maskotları. pro_mascot(kind, expr, size, blink) -> RGBA sprite.
kind: 'erkek' | 'kadin' | 'baykus'     expr: normal | happy | shock | angry | wink | point
Çizim alanı 300x380 birim; kalın siyah kontur + iki tonlu düz gölgeleme.
"""
from functools import lru_cache

from .core import INK, SS, canvas, finish, font

WHITE = (255, 255, 255, 255)
RED = (232, 52, 46, 255)
RED_D = (178, 30, 30, 255)
ROBE = (34, 36, 44, 255)
ROBE_D = (20, 21, 27, 255)
ROBE_L = (58, 61, 74, 255)
SKIN = (255, 213, 178, 255)
SKIN_D = (236, 178, 140, 255)
BLUSH = (255, 150, 140, 255)
HAIR_M = (58, 40, 30, 255)
HAIR_M_L = (96, 68, 50, 255)
HAIR_F = (36, 26, 24, 255)
HAIR_F_L = (78, 56, 48, 255)
GOLD = (246, 190, 46, 255)
GOLD_D = (200, 140, 20, 255)
BOOK = (150, 28, 34, 255)
BOOK_D = (110, 18, 24, 255)
FOLDER = (38, 92, 230, 255)
PAPER = (250, 247, 238, 255)
OWL = (140, 104, 74, 255)
OWL_D = (104, 74, 52, 255)
OWL_L = (232, 214, 186, 255)
BEAK = (250, 176, 40, 255)


class P:
    """Kontur genişliği sabit, birim → piksel ölçekli çizim yardımcısı."""

    def __init__(self, d, s, ox=0, oy=0):
        self.d, self.s, self.ox, self.oy = d, s, ox, oy
        self.ow = max(1, int(6 * s))

    def _p(self, pts):
        return [((x + self.ox) * self.s, (y + self.oy) * self.s) for x, y in pts]

    def _b(self, b):
        x0, y0, x1, y1 = b
        return [(x0 + self.ox) * self.s, (y0 + self.oy) * self.s, (x1 + self.ox) * self.s, (y1 + self.oy) * self.s]

    def ell(self, b, fill, ol=True, w=None):
        self.d.ellipse(self._b(b), fill=fill, outline=INK if ol else None, width=(w or self.ow) if ol else 0)

    def rr(self, b, r, fill, ol=True, w=None):
        self.d.rounded_rectangle(self._b(b), radius=r * self.s, fill=fill, outline=INK if ol else None,
                                 width=(w or self.ow) if ol else 0)

    def poly(self, pts, fill, ol=True, w=None):
        p = self._p(pts)
        self.d.polygon(p, fill=fill)
        if ol:
            self.d.line(p + [p[0]], fill=INK, width=w or self.ow, joint="curve")

    def line(self, pts, fill=INK, w=None):
        self.d.line(self._p(pts), fill=fill, width=int((w or 6) * self.s), joint="curve")

    def arc(self, b, a0, a1, fill=INK, w=None):
        self.d.arc(self._b(b), a0, a1, fill=fill, width=int((w or 6) * self.s))

    def chord(self, b, a0, a1, fill, ol=True):
        self.d.chord(self._b(b), a0, a1, fill=fill, outline=INK if ol else None, width=self.ow if ol else 0)

    def pie(self, b, a0, a1, fill):
        self.d.pieslice(self._b(b), a0, a1, fill=fill)


# ---------------------------------------------------------------- ortak parçalar
def robe(p, cx=150, top=196, bottom=342, half_top=70, half_bot=96):
    # gövde
    p.poly([(cx - half_top, top), (cx + half_top, top), (cx + half_bot, bottom), (cx - half_bot, bottom)], ROBE)
    # sağ taraf gölgesi + kıvrımlar
    p.poly([(cx + 26, top + 6), (cx + half_top - 4, top + 4), (cx + half_bot - 6, bottom - 4), (cx + 40, bottom - 4)], ROBE_D, ol=False)
    p.line([(cx - 40, top + 70), (cx - 50, bottom - 6)], ROBE_L, 4)
    p.line([(cx + 44, top + 80), (cx + 52, bottom - 6)], ROBE_L, 3)
    # gömlek V
    p.poly([(cx - 22, top), (cx + 22, top), (cx, top + 44)], WHITE)
    # kırmızı yakalar
    p.poly([(cx - 22, top - 2), (cx - 46, top + 2), (cx - 4, top + 86)], RED)
    p.poly([(cx + 22, top - 2), (cx + 46, top + 2), (cx + 4, top + 86)], RED)
    p.poly([(cx + 22, top + 2), (cx + 46, top + 4), (cx + 30, top + 30)], RED_D, ol=False)
    # beyaz avukat yakalığı (bant)
    p.poly([(cx - 9, top + 10), (cx + 9, top + 10), (cx + 6, top + 46), (cx - 6, top + 46)], WHITE, w=int(4 * p.s))
    p.line([(cx, top + 12), (cx, top + 44)], INK, 3)


def shoes(p, cx=150, y=334):
    p.rr((cx - 44, y, cx - 6, y + 22), 10, INK, ol=False)
    p.rr((cx + 6, y, cx + 44, y + 22), 10, INK, ol=False)


def shadow(p, cx=150, y=362, w=78):
    p.ell((cx - w, y, cx + w, y + 14), (0, 0, 0, 38), ol=False)


def eye(p, x, y, expr, blink, r=9, look=(0, 0), lash=False):
    if blink and expr in ("normal", "shock", "angry", "point"):
        p.line([(x - 11, y + 2), (x + 11, y + 2)], INK, 6)
        return
    if expr in ("happy",) or (expr == "wink" and x > 150):
        p.arc((x - 13, y - 8, x + 13, y + 16), 200, 340, INK, 6)
        return
    rr = r * (1.35 if expr == "shock" else 1.0)
    p.ell((x - rr * .85, y - rr * 1.2, x + rr * .85, y + rr * 1.2), INK, ol=False)
    p.ell((x - rr * .2 + look[0] + 2, y - rr * .75, x + rr * .35 + look[0] + 2, y - rr * .2), WHITE, ol=False)
    if lash:
        p.line([(x - rr * 1.0, y - rr * 0.9), (x - rr * 1.5, y - rr * 1.4)], INK, 4)


def brows(p, lx, rx, y, expr, col=INK):
    if expr == "angry":
        p.line([(lx - 14, y - 6), (lx + 12, y + 4)], col, 7)
        p.line([(rx + 14, y - 6), (rx - 12, y + 4)], col, 7)
    elif expr == "shock":
        p.arc((lx - 14, y - 16, lx + 14, y + 4), 200, 340, col, 6)
        p.arc((rx - 14, y - 16, rx + 14, y + 4), 200, 340, col, 6)
    else:
        p.line([(lx - 13, y), (lx + 11, y - 3)], col, 6)
        p.line([(rx - 11, y - 3), (rx + 13, y)], col, 6)


def mouth(p, x, y, expr, lip=None):
    if expr in ("happy", "wink", "point"):
        p.chord((x - 18, y - 12, x + 18, y + 14), 0, 180, WHITE if expr != "point" else (120, 30, 30, 255))
        if expr != "point":
            p.chord((x - 10, y + 2, x + 10, y + 14), 0, 180, (230, 110, 110, 255), ol=False)
    elif expr == "shock":
        p.ell((x - 9, y - 6, x + 9, y + 14), (120, 30, 30, 255))
    elif expr == "angry":
        p.arc((x - 14, y, x + 14, y + 20), 200, 340, INK, 6)
    else:
        p.arc((x - 14, y - 10, x + 14, y + 8), 30, 150, lip or INK, 6)


def hand(p, x, y, r=15):
    p.ell((x - r, y - r, x + r, y + r), SKIN)


def law_book(p, x, y, w=62, h=76, label="KANUN"):
    p.rr((x + 6, y + 4, x + w + 6, y + h + 4), 6, PAPER)
    p.rr((x, y, x + w, y + h), 6, BOOK)
    p.rr((x, y, x + 12, y + h), 4, BOOK_D, ol=False)
    p.line([(x + 12, y + 2), (x + 12, y + h - 2)], INK, 4)
    p.rr((x + 18, y + h / 2 - 12, x + w - 6, y + h / 2 + 12), 4, GOLD, w=int(3 * p.s))
    p.d.text(((x + 12 + w / 2 + p.ox) * p.s - 2 * p.s, (y + h / 2 + p.oy) * p.s), "§", font=font("black", int(20 * p.s)),
             fill=INK, anchor="mm")


def folder(p, x, y, w=70, h=56):
    p.rr((x + 8, y - 8, x + w - 8, y + h - 10), 4, PAPER)
    p.line([(x + 16, y + 4), (x + w - 18, y + 4)], (180, 180, 180, 255), 4)
    p.line([(x + 16, y + 14), (x + w - 26, y + 14)], (180, 180, 180, 255), 4)
    p.rr((x, y + 6, x + w, y + h), 6, FOLDER)
    p.rr((x + 6, y + 6, x + 30, y + 14), 3, (28, 70, 190, 255), ol=False)


def point_arm(p):
    """Yana (sağa) işaret eden kol: başparmak yukarıda, işaret parmağı yatay."""
    p.poly([(212, 206), (236, 214), (262, 200), (252, 178)], ROBE)
    p.ell((244, 172, 276, 204), SKIN)                 # yumruk
    p.rr((262, 176, 296, 190), 7, SKIN)               # işaret parmağı (yatay)
    p.ell((252, 160, 268, 180), SKIN)                 # başparmak
    p.arc((248, 182, 270, 202), 300, 60, SKIN_D, 4)


def gavel(p, x, y):
    p.line([(x, y), (x + 40, y - 34)], INK, 13)
    p.line([(x, y), (x + 40, y - 34)], (156, 96, 50, 255), 7)
    p.poly([(x + 22, y - 62), (x + 70, y - 20), (x + 54, y - 4), (x + 6, y - 46)], (156, 96, 50, 255))
    p.poly([(x + 30, y - 55), (x + 40, y - 46), (x + 24, y - 30), (x + 14, y - 39)], GOLD, ol=False)


# ---------------------------------------------------------------- 1) Erkek avukat
def erkek(p, expr, blink):
    shadow(p)
    shoes(p)
    robe(p)
    # kollar
    if expr == "point":
        point_arm(p)
    else:
        p.poly([(212, 206), (238, 214), (246, 276), (220, 282)], ROBE)
        law_book(p, 214, 236)
        hand(p, 222, 270, 14)
    p.poly([(88, 206), (62, 214), (56, 290), (82, 294)], ROBE)
    hand(p, 70, 298, 14)
    # boyun + kulaklar + kafa
    p.rr((132, 160, 168, 202), 8, SKIN_D, ol=False)
    p.ell((78, 100, 102, 136), SKIN)
    p.ell((198, 100, 222, 136), SKIN)
    p.ell((86, 34, 214, 176), SKIN)
    # saç (yan ayrık)
    p.chord((84, 26, 216, 120), 180, 360, HAIR_M)
    p.poly([(86, 76), (92, 44), (150, 28), (206, 44), (214, 78), (192, 62), (120, 56), (96, 80)], HAIR_M, ol=False)
    p.line([(88, 78), (100, 46), (150, 30), (204, 46), (214, 80)], INK, 6)
    p.line([(120, 40), (160, 36), (192, 46)], HAIR_M_L, 5)
    # yanak
    p.ell((100, 130, 118, 142), BLUSH, ol=False)
    p.ell((182, 130, 200, 142), BLUSH, ol=False)
    # gözlük + gözler + kaşlar
    brows(p, 124, 176, 92, expr)
    eye(p, 124, 114, expr, blink)
    eye(p, 176, 114, expr, blink)
    p.rr((100, 98, 146, 132), 12, None, w=int(5 * p.s))
    p.rr((154, 98, 200, 132), 12, None, w=int(5 * p.s))
    p.line([(146, 112), (154, 112)], INK, 5)
    mouth(p, 150, 150, expr)


# ---------------------------------------------------------------- 2) Kadın avukat
def kadin(p, expr, blink):
    shadow(p)
    shoes(p)
    # arka saç
    p.rr((92, 70, 208, 196), 40, HAIR_F)
    robe(p)
    if expr == "point":
        point_arm(p)
    else:
        p.poly([(212, 206), (238, 214), (246, 276), (220, 282)], ROBE)
        folder(p, 206, 236)
        hand(p, 220, 280, 14)
    p.poly([(88, 206), (62, 214), (56, 290), (82, 294)], ROBE)
    hand(p, 70, 298, 14)
    p.rr((134, 160, 166, 202), 8, SKIN_D, ol=False)
    p.ell((86, 38, 214, 176), SKIN)
    # topuz
    p.ell((122, 0, 178, 48), HAIR_F)
    p.arc((132, 8, 168, 40), 200, 320, HAIR_F_L, 5)
    # perçem
    p.chord((84, 30, 216, 130), 180, 360, HAIR_F)
    p.poly([(86, 90), (96, 50), (150, 34), (204, 50), (214, 90), (200, 70), (156, 58), (110, 66), (94, 96)], HAIR_F, ol=False)
    p.line([(86, 92), (96, 50), (150, 34), (204, 50), (214, 92)], INK, 6)
    p.line([(110, 52), (150, 42), (180, 48)], HAIR_F_L, 5)
    # küpe
    p.ell((84, 128, 96, 140), GOLD, w=int(3 * p.s))
    p.ell((204, 128, 216, 140), GOLD, w=int(3 * p.s))
    p.ell((102, 128, 120, 140), BLUSH, ol=False)
    p.ell((180, 128, 198, 140), BLUSH, ol=False)
    brows(p, 124, 176, 92, expr)
    eye(p, 124, 112, expr, blink, lash=True)
    eye(p, 176, 112, expr, blink)
    if not blink and expr not in ("happy",) and not (expr == "wink"):
        p.line([(176 + 9, 112 - 10), (176 + 15, 112 - 16)], INK, 4)
    mouth(p, 150, 148, expr, lip=(200, 50, 60, 255))


# ---------------------------------------------------------------- 3) Baykuş hukukçu
def baykus(p, expr, blink):
    shadow(p)
    # ayaklar
    for x in (122, 166):
        p.line([(x, 336), (x - 8, 352)], BEAK, 7)
        p.line([(x, 336), (x, 354)], BEAK, 7)
        p.line([(x, 336), (x + 8, 352)], BEAK, 7)
    # gövde
    p.ell((70, 60, 230, 346), OWL)
    p.ell((104, 170, 196, 336), OWL_L, ol=False)
    for k in range(3):
        for j in range(3):
            p.arc((116 + j * 24, 200 + k * 30, 136 + j * 24, 216 + k * 30), 20, 160, OWL_D, 4)
    # kulak tüyleri
    for sx in (1, -1):
        bx = 150 - sx * 50
        p.poly([(bx - sx * 18, 84), (bx - sx * 30, 52), (bx - sx * 6, 66), (bx + sx * 8, 80)], OWL_D)
        p.line([(bx - sx * 26, 58), (bx - sx * 12, 76)], OWL, 3)
    # cübbe kanatları
    p.poly([(74, 170), (110, 168), (122, 330), (78, 300)], ROBE)
    p.poly([(226, 170), (190, 168), (178, 330), (222, 300)], ROBE)
    p.poly([(110, 168), (126, 168), (132, 230)], RED, w=int(4 * p.s))
    p.poly([(190, 168), (174, 168), (168, 230)], RED, w=int(4 * p.s))
    # yüz diski
    p.ell((86, 72, 214, 180), OWL_L)
    # büyük gözler + gözlük
    for x in (122, 178):
        p.ell((x - 26, 100, x + 26, 152), WHITE)
    eye(p, 122, 126, expr, blink, r=11)
    eye(p, 178, 126, expr, blink, r=11)
    p.ell((94, 98, 150, 154), None, w=int(6 * p.s))
    p.ell((150, 98, 206, 154), None, w=int(6 * p.s))
    brows(p, 122, 178, 92, expr, OWL_D)
    # gaga
    p.poly([(140, 150), (160, 150), (150, 172)], BEAK)
    if expr in ("shock",):
        p.ell((143, 168, 157, 182), (120, 30, 30, 255))
    # tokmak (sağ kanat)
    if expr == "point":
        p.poly([(214, 200), (250, 150), (236, 138), (206, 180)], ROBE)
        gavel(p, 232, 150)
    else:
        gavel(p, 210, 268)


KINDS = {"erkek": erkek, "kadin": kadin, "baykus": baykus}


@lru_cache(maxsize=256)
def pro_mascot(kind="erkek", expr="normal", size=260, blink=False):
    sx = size / 300.0
    im, d = canvas(size, 380 * sx)
    p = P(d, SS * sx)
    KINDS[kind](p, expr, blink)
    return finish(im)
