"""30 hukuk/hak temalı maskot. m30(kind, expr, size, blink) -> RGBA sprite. Çizim alanı 300x380."""
import math
from functools import lru_cache

from .core import INK, SS, canvas, finish, font
from .mascots_pro import P, eye, mouth, brows

W_ = (255, 255, 255, 255)
RED = (232, 52, 46, 255)
RED_D = (176, 30, 30, 255)
NAVY = (34, 56, 120, 255)
NAVY_L = (60, 92, 170, 255)
BLUE = (60, 120, 235, 255)
GLASS = (200, 232, 250, 255)
TEAL = (20, 170, 150, 255)
GREEN = (40, 170, 90, 255)
GREEN_L = (150, 210, 120, 255)
GOLD = (246, 190, 46, 255)
GOLD_D = (205, 145, 20, 255)
YELLOW = (255, 214, 60, 255)
ORANGE = (250, 140, 40, 255)
WOOD = (166, 104, 56, 255)
WOOD_D = (122, 74, 38, 255)
CARD = (205, 160, 110, 255)
CARD_D = (170, 126, 82, 255)
PAPER = (252, 250, 244, 255)
CREAM = (252, 236, 210, 255)
GREY = (150, 156, 168, 255)
GREY_L = (205, 210, 220, 255)
PURPLE = (120, 72, 220, 255)
PINK = (255, 172, 190, 255)
PINK_D = (235, 130, 155, 255)
SKIN = (255, 213, 178, 255)
ELE = (165, 176, 198, 255)
ELE_L = (210, 190, 205, 255)
BLUSH = (255, 150, 140, 255)


# ---------------------------------------------------------------- ortak
def legs(p, cx=150, top=300, bot=338, gap=24):
    p.line([(cx - gap, top), (cx - gap, bot)], INK, 9)
    p.line([(cx + gap, top), (cx + gap, bot)], INK, 9)
    p.rr((cx - gap - 22, bot - 4, cx - gap + 12, bot + 14), 8, INK, ol=False)
    p.rr((cx + gap - 12, bot - 4, cx + gap + 22, bot + 14), 8, INK, ol=False)


def arm(p, x0, y0, x1, y1, hand=W_):
    p.line([(x0, y0), (x1, y1)], INK, 9)
    p.ell((x1 - 12, y1 - 12, x1 + 12, y1 + 12), hand)


def arms(p, y, xl, xr, hand=W_, wave=True):
    arm(p, xl, y, xl - 34, y + 40, hand)
    arm(p, xr, y, xr + 34, y - 36 if wave else y + 40, hand)


def face(p, cx, cy, expr, blink, gap=24, blush=True):
    brows(p, cx - gap, cx + gap, cy - 26, expr)
    eye(p, cx - gap, cy, expr, blink)
    eye(p, cx + gap, cy, expr, blink)
    if blush:
        p.ell((cx - gap - 20, cy + 16, cx - gap - 4, cy + 26), BLUSH, ol=False)
        p.ell((cx + gap + 4, cy + 16, cx + gap + 20, cy + 26), BLUSH, ol=False)
    mouth(p, cx, cy + 34, expr)


def txt(p, x, y, s, size, col=INK, f="black"):
    p.d.text(((x + p.ox) * p.s, (y + p.oy) * p.s), s, font=font(f, int(size * p.s)), fill=col, anchor="mm")


def shadow(p, cx=150, y=354, w=80):
    p.ell((cx - w, y, cx + w, y + 14), (0, 0, 0, 38), ol=False)


def ell_band(cx, cy, rx, ry, y1, y2, n=16):
    """Elips içinde y1–y2 arası yatay şerit poligonu."""
    pts_r, pts_l = [], []
    for k in range(n + 1):
        y = y1 + (y2 - y1) * k / n
        dx = rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2))
        pts_r.append((cx + dx, y))
        pts_l.append((cx - dx, y))
    return pts_r + pts_l[::-1]


# ---------------------------------------------------------------- 30 karakter
def tokmak(p, e, b):
    shadow(p); legs(p, top=292, gap=18)
    p.rr((138, 186, 162, 300), 10, WOOD)
    arms(p, 140, 52, 248, WOOD)
    p.rr((46, 88, 254, 192), 34, WOOD)
    p.rr((46, 96, 254, 120), 10, (196, 130, 76, 255), ol=False)
    for x in (82, 218):
        p.line([(x, 92), (x, 188)], GOLD, 8)
    p.rr((36, 82, 70, 198), 14, WOOD_D); p.rr((230, 82, 264, 198), 14, WOOD_D)
    face(p, 150, 132, e, b, 24)


def acik_kitap(p, e, b):
    shadow(p); legs(p, top=306)
    arms(p, 200, 34, 266)
    p.poly([(26, 120), (150, 146), (274, 120), (274, 296), (150, 318), (26, 296)], RED)
    p.poly([(40, 112), (150, 136), (150, 304), (40, 282)], PAPER)
    p.poly([(150, 136), (260, 112), (260, 282), (150, 304)], PAPER)
    for k in range(4):
        p.line([(56, 240 + k * 12), (130, 254 + k * 12)], GREY_L, 4)
        p.line([(170, 254 + k * 12), (244, 240 + k * 12)], GREY_L, 4)
    txt(p, 95, 150, "MADDE", 16, RED); txt(p, 205, 150, "§ 1", 18, RED)
    face(p, 150, 196, e, b, 40)


def kum_saati(p, e, b):
    shadow(p); legs(p, top=314, gap=30)
    arms(p, 180, 80, 220, WOOD)
    p.poly([(92, 64), (208, 64), (160, 176), (140, 176)], GLASS)
    p.poly([(140, 176), (160, 176), (208, 288), (92, 288)], GLASS)
    p.poly([(116, 100), (184, 100), (152, 168), (148, 168)], GOLD, ol=False)
    p.poly([(104, 288), (196, 288), (150, 236)], GOLD, ol=False)
    p.line([(150, 170), (150, 236)], GOLD, 4)
    for x in (80, 220):
        p.line([(x, 60), (x, 292)], WOOD, 12)
    p.rr((62, 38, 238, 66), 10, WOOD); p.rr((62, 286, 238, 314), 10, WOOD)
    p.rr((100, 196, 200, 276), 24, W_, w=int(4 * p.s))
    face(p, 150, 226, e, b, 20, blush=False)


def takvim(p, e, b):
    shadow(p); legs(p, top=298)
    arms(p, 200, 62, 238)
    p.rr((60, 70, 240, 300), 18, W_)
    p.rr((60, 70, 240, 134), 18, RED); p.rr((62, 112, 238, 134), 0, RED, ol=False)
    p.line([(62, 134), (238, 134)], INK, 6)
    txt(p, 150, 104, "SON GÜN", 28, W_)
    for x in (100, 200):
        p.rr((x - 9, 50, x + 9, 88), 8, INK, ol=False)
    face(p, 150, 206, e, b, 30)


def zarf(p, e, b):
    shadow(p); legs(p, top=268)
    arms(p, 190, 40, 260)
    p.rr((36, 108, 264, 272), 14, CREAM)
    p.line([(40, 112), (150, 196), (260, 112)], INK, 6)
    p.rr((206, 120, 248, 162), 4, RED, w=int(4 * p.s)); txt(p, 227, 141, "PTT", 12, W_)
    p.ell((104, 172, 196, 262), W_, w=int(4 * p.s))
    face(p, 150, 212, e, b, 20, blush=False)
    p.rr((70, 234, 128, 256), 6, RED, w=int(3 * p.s)); txt(p, 99, 245, "TEBLİĞ", 11, W_)


def dilekce(p, e, b):
    shadow(p); legs(p, top=318)
    arm(p, 72, 200, 38, 240); arm(p, 238, 200, 274, 160)
    p.line([(274, 160), (292, 104)], NAVY, 9); p.poly([(286, 102), (298, 106), (294, 88)], GOLD, w=int(3 * p.s))
    p.poly([(70, 40), (200, 40), (240, 80), (240, 320), (70, 320)], PAPER)
    p.poly([(200, 40), (200, 80), (240, 80)], GREY_L)
    txt(p, 150, 70, "DİLEKÇE", 24, NAVY)
    for k in range(4):
        p.line([(92, 248 + k * 16), (218 - k * 14, 248 + k * 16)], GREY_L, 5)
    face(p, 155, 160, e, b, 28)


def kalem(p, e, b):
    shadow(p, w=50)
    arms(p, 210, 118, 182, NAVY_L)
    p.poly([(124, 268), (176, 268), (150, 336)], GOLD)
    p.line([(150, 290), (150, 330)], INK, 4)
    p.ell((144, 340, 156, 356), NAVY, ol=False)
    p.rr((118, 138, 182, 274), 16, NAVY_L)
    p.rr((114, 28, 186, 152), 20, NAVY)
    p.rr((170, 40, 180, 120), 4, GOLD, w=int(3 * p.s))
    p.rr((114, 132, 186, 150), 0, GOLD, w=int(3 * p.s))
    p.rr((122, 160, 178, 252), 18, W_, w=int(4 * p.s))
    face(p, 150, 196, e, b, 14, blush=False)


def anahtar(p, e, b):
    shadow(p, w=50)
    arms(p, 120, 72, 228, GOLD)
    p.rr((138, 170, 162, 330), 8, GOLD)
    p.rr((160, 270, 194, 290), 4, GOLD); p.rr((160, 300, 186, 320), 4, GOLD)
    p.ell((70, 30, 230, 190), GOLD)
    p.ell((84, 44, 216, 176), (255, 222, 120, 255), ol=False)
    face(p, 150, 104, e, b, 28)


def kilit(p, e, b):
    shadow(p); legs(p, top=288)
    p.arc((92, 24, 208, 160), 180, 360, INK, 30)
    p.arc((92, 24, 208, 160), 180, 360, GREY, 18)
    p.line([(98, 92), (98, 110)], GREY, 18); p.line([(202, 92), (202, 110)], GREY, 18)
    arms(p, 200, 70, 230, GOLD)
    p.rr((64, 100, 236, 292), 26, GOLD)
    p.rr((64, 100, 236, 128), 14, GOLD_D, ol=False)
    p.ell((138, 236, 162, 260), INK, ol=False); p.poly([(144, 252), (156, 252), (160, 280), (140, 280)], INK, ol=False)
    face(p, 150, 172, e, b, 30)


def buyutec(p, e, b):
    shadow(p, w=60)
    p.poly([(186, 196), (206, 180), (276, 300), (254, 316)], WOOD)
    arm(p, 64, 140, 30, 180)
    p.ell((54, 34, 246, 226), NAVY)
    p.ell((74, 54, 226, 206), GLASS, ol=False)
    p.arc((90, 70, 160, 140), 200, 260, W_, 8)
    face(p, 150, 128, e, b, 28)


def kamera(p, e, b):
    shadow(p, w=60)
    p.rr((96, 310, 176, 330), 6, GREY)
    p.line([(136, 196), (136, 312)], GREY, 14); p.line([(136, 196), (136, 312)], INK, 3)
    arm(p, 70, 160, 36, 200)
    p.rr((56, 96, 222, 200), 20, W_)
    p.ell((72, 110, 90, 128), RED, ol=False)
    p.ell((196, 94, 266, 204), INK); p.ell((212, 112, 250, 186), BLUE, ol=False); p.ell((220, 122, 234, 136), W_, ol=False)
    face(p, 136, 146, e, b, 24, blush=False)


def telefon(p, e, b):
    shadow(p); legs(p, top=318)
    arms(p, 200, 86, 214)
    p.rr((84, 30, 216, 324), 28, INK)
    p.rr((96, 56, 204, 300), 14, GLASS, ol=False)
    p.rr((132, 40, 168, 50), 5, (60, 60, 60, 255), ol=False)
    p.rr((110, 226, 190, 262), 10, RED, ol=False); txt(p, 150, 244, "SMS", 18, W_)
    face(p, 150, 160, e, b, 24)


def fis(p, e, b):
    shadow(p); legs(p, top=310)
    arms(p, 170, 80, 220)
    pts = [(80, 40), (220, 40), (220, 296)]
    for k in range(8):
        x = 220 - (k + 1) * 17.5
        pts.append((x + 8.75, 310 if k % 2 == 0 else 296))
        pts.append((x, 296))
    pts.append((80, 296))
    p.poly(pts, PAPER)
    for k in range(3):
        p.line([(100, 196 + k * 18), (200 - k * 20, 196 + k * 18)], GREY_L, 5)
    p.line([(100, 252), (200, 252)], INK, 3)
    txt(p, 120, 272, "TOPLAM", 14); txt(p, 182, 272, "₺?", 16, RED)
    face(p, 150, 120, e, b, 26)


def kredi_karti(p, e, b):
    shadow(p); legs(p, top=252)
    arms(p, 180, 40, 260, PURPLE)
    p.rr((34, 108, 266, 256), 20, PURPLE)
    p.rr((34, 128, 266, 150), 0, INK, ol=False)
    p.rr((56, 170, 100, 204), 6, GOLD, w=int(3 * p.s))
    txt(p, 92, 232, "•••• 4821", 16, W_)
    p.ell((134, 156, 244, 254), W_, w=int(4 * p.s))
    face(p, 189, 196, e, b, 22, blush=False)


def ev(p, e, b):
    shadow(p); legs(p, top=300)
    arms(p, 210, 66, 234, CREAM)
    p.rr((188, 62, 214, 120), 4, RED_D)
    p.rr((64, 134, 236, 302), 8, CREAM)
    p.poly([(36, 146), (150, 46), (264, 146)], RED)
    p.rr((132, 236, 168, 302), 6, WOOD)
    p.ell((158, 266, 164, 272), GOLD, ol=False)
    face(p, 150, 184, e, b, 32)


def araba(p, e, b):
    shadow(p, y=300, w=120)
    p.poly([(78, 156), (110, 98), (196, 98), (230, 156)], BLUE)
    p.poly([(94, 152), (118, 108), (188, 108), (214, 152)], GLASS, ol=False)
    p.rr((26, 148, 274, 252), 36, BLUE)
    p.rr((246, 176, 270, 196), 6, YELLOW, w=int(3 * p.s)); p.rr((30, 176, 52, 196), 6, RED, w=int(3 * p.s))
    for x in (90, 210):
        p.ell((x - 32, 222, x + 32, 286), INK, ol=False); p.ell((x - 14, 240, x + 14, 268), GREY, ol=False)
    face(p, 154, 146, e, b, 32, blush=False)


def koli(p, e, b):
    shadow(p); legs(p, top=300)
    arms(p, 200, 60, 240, CARD)
    p.poly([(60, 118), (30, 88), (130, 88), (150, 118)], CARD_D)
    p.poly([(240, 118), (270, 88), (170, 88), (150, 118)], CARD_D)
    p.rr((60, 116, 240, 302), 6, CARD)
    p.rr((138, 116, 162, 170), 0, CREAM, ol=False)
    p.rr((180, 252, 228, 290), 4, W_, w=int(3 * p.s)); txt(p, 204, 271, "İADE", 11, RED)
    face(p, 150, 204, e, b, 30)


def poset(p, e, b):
    shadow(p); legs(p, top=300)
    p.arc((92, 60, 142, 150), 180, 360, INK, 10); p.arc((158, 60, 208, 150), 180, 360, INK, 10)
    arms(p, 200, 64, 236, TEAL)
    p.poly([(68, 112), (232, 112), (252, 302), (48, 302)], TEAL)
    p.poly([(190, 112), (232, 112), (252, 302), (212, 302)], (12, 140, 122, 255), ol=False)
    p.ell((98, 146, 202, 250), W_, w=int(4 * p.s))
    face(p, 150, 192, e, b, 22, blush=False)
    txt(p, 150, 278, "TÜKETİCİ", 18, W_)


def kumbara(p, e, b):
    shadow(p, w=100)
    for x in (82, 122, 176, 214):
        p.rr((x - 12, 250, x + 12, 300), 8, PINK_D)
    p.arc((26, 150, 66, 196), 90, 330, PINK_D, 7)
    p.poly([(100, 98), (116, 58), (138, 96)], PINK_D)
    p.ell((50, 90, 250, 270), PINK)
    p.rr((126, 92, 176, 104), 5, INK, ol=False)
    p.ell((208, 154, 268, 212), PINK_D)
    p.ell((222, 172, 232, 188), INK, ol=False); p.ell((244, 172, 254, 188), INK, ol=False)
    p.ell((136, 24, 172, 60), GOLD); txt(p, 154, 42, "₺", 18, GOLD_D)
    face(p, 150, 160, e, b, 24)


def ilk_yardim(p, e, b):
    shadow(p); legs(p, top=292)
    p.rr((112, 64, 188, 104), 14, None, w=int(10 * p.s))
    arms(p, 200, 50, 250, W_)
    p.rr((48, 92, 252, 294), 22, W_)
    p.rr((48, 92, 252, 120), 14, RED, ol=False)
    p.rr((134, 136, 166, 196), 4, RED, ol=False); p.rr((120, 150, 180, 182), 4, RED, ol=False)
    face(p, 150, 236, e, b, 34, blush=False)


def baret(p, e, b):
    shadow(p); legs(p, top=312)
    arms(p, 268, 96, 204, SKIN)
    p.rr((92, 250, 208, 316), 18, ORANGE)
    p.rr((92, 274, 208, 286), 0, (230, 240, 240, 255), ol=False)
    p.ell((78, 104, 222, 252), SKIN)
    p.chord((70, 40, 230, 196), 180, 360, YELLOW)
    p.rr((46, 110, 254, 132), 10, YELLOW)
    p.rr((140, 44, 160, 118), 6, GOLD_D, ol=False)
    face(p, 150, 180, e, b, 28)


def kep(p, e, b):
    shadow(p); legs(p, top=300)
    arms(p, 210, 88, 212, PAPER)
    p.rr((86, 120, 214, 304), 30, PAPER)
    p.rr((86, 248, 214, 272), 0, RED, ol=False)
    p.ell((138, 250, 162, 270), GOLD, w=int(3 * p.s))
    p.rr((94, 82, 206, 132), 10, INK)
    p.poly([(40, 86), (150, 42), (260, 86), (150, 128)], INK)
    p.line([(150, 84), (246, 96), (246, 150)], GOLD, 5); p.ell((236, 146, 256, 170), GOLD)
    face(p, 150, 182, e, b, 28)


def ampul(p, e, b):
    shadow(p); legs(p, top=252, bot=332)
    for a in range(-150, -20, 26):
        r = math.radians(a)
        p.line([(150 + 100 * math.cos(r), 110 + 100 * math.sin(r)), (150 + 128 * math.cos(r), 110 + 128 * math.sin(r))], GOLD, 7)
    arms(p, 150, 74, 226, YELLOW)
    p.poly([(112, 170), (188, 170), (180, 212), (120, 212)], YELLOW)
    p.rr((116, 206, 184, 252), 10, GREY)
    for y in (220, 236):
        p.line([(118, y), (182, y)], INK, 4)
    p.ell((70, 30, 230, 190), YELLOW)
    p.arc((92, 52, 150, 110), 190, 250, W_, 8)
    face(p, 150, 110, e, b, 28)


def adliye(p, e, b):
    shadow(p, w=120); legs(p, top=306, gap=40)
    p.rr((40, 266, 260, 288), 4, CREAM); p.rr((28, 286, 272, 308), 4, CREAM)
    for x in (58, 92, 194, 228):
        p.rr((x - 12, 130, x + 12, 268), 4, CREAM)
        p.line([(x, 136), (x, 262)], GREY_L, 3)
    p.rr((114, 132, 186, 266), 14, W_)
    p.rr((40, 112, 260, 134), 4, CREAM)
    p.poly([(30, 114), (150, 44), (270, 114)], CREAM)
    txt(p, 150, 92, "⚖", 30, NAVY, "bold") if False else txt(p, 150, 94, "ADALET", 16, NAVY)
    face(p, 150, 190, e, b, 18, blush=False)


def zil(p, e, b):
    shadow(p); legs(p, top=290)
    for sx in (1, -1):
        p.arc((150 + sx * 90 - 30, 110, 150 + sx * 90 + 30, 210), 300 if sx > 0 else 120, 60 if sx > 0 else 240, RED, 6)
    p.ell((136, 254, 164, 284), INK, ol=False)
    arms(p, 210, 60, 240, GOLD)
    p.ell((136, 30, 164, 58), GOLD)
    p.chord((74, 50, 226, 230), 180, 360, GOLD)
    p.poly([(74, 140), (226, 140), (248, 258), (52, 258)], GOLD, ol=False)
    p.line([(76, 140), (52, 258), (248, 258), (224, 140)], INK, 6)
    p.rr((46, 250, 254, 268), 8, GOLD_D)
    face(p, 150, 172, e, b, 28)


def muhur_mumu(p, e, b):
    shadow(p, w=70)
    p.poly([(120, 250), (96, 336), (122, 318), (142, 340), (150, 250)], NAVY)
    p.poly([(180, 250), (204, 336), (178, 318), (158, 340), (150, 250)], RED_D)
    pts = []
    for k in range(32):
        a = 2 * math.pi * k / 32
        r = 100 + (8 if k % 2 else -2)
        pts.append((150 + r * math.cos(a), 160 + r * math.sin(a)))
    p.poly(pts, RED_D)
    p.ell((78, 88, 222, 232), RED)
    p.ell((90, 100, 210, 220), (240, 90, 80, 255), ol=False)
    p.ell((98, 108, 202, 212), W_, w=int(4 * p.s))
    face(p, 150, 156, e, b, 24, blush=False)


def guvercin(p, e, b):
    shadow(p, w=70)
    for x in (128, 160):
        p.line([(x, 250), (x - 6, 300)], ORANGE, 7); p.line([(x - 6, 300), (x + 8, 300)], ORANGE, 7)
    p.poly([(70, 176), (20, 150), (30, 226)], GREY_L)
    p.ell((54, 120, 232, 262), W_)
    p.poly([(96, 160), (186, 150), (160, 238), (110, 222)], GREY_L)
    p.ell((150, 66, 244, 160), W_)
    p.poly([(240, 104), (276, 114), (240, 126)], ORANGE)
    p.line([(262, 118), (290, 150)], GREEN, 5)
    for (x, y) in ((272, 132), (284, 146)):
        p.ell((x - 9, y - 5, x + 9, y + 5), GREEN_L, w=int(3 * p.s))
    blink = b
    eye(p, 206, 104, e, blink, r=8)
    p.ell((214, 124, 226, 132), BLUSH, ol=False)


def fil(p, e, b):
    shadow(p, w=90)
    p.rr((96, 290, 130, 330), 10, ELE); p.rr((170, 290, 204, 330), 10, ELE)
    p.rr((86, 196, 214, 312), 40, ELE)
    p.poly([(150, 210), (140, 222), (150, 260), (160, 222)], RED, w=int(3 * p.s))
    p.ell((14, 60, 116, 200), ELE); p.ell((30, 78, 102, 184), ELE_L, ol=False)
    p.ell((184, 60, 286, 200), ELE); p.ell((198, 78, 270, 184), ELE_L, ol=False)
    p.ell((70, 40, 230, 206), ELE)
    p.line([(150, 160), (150, 236), (172, 254)], INK, 34); p.line([(150, 160), (150, 236), (172, 254)], ELE, 22)
    p.poly([(118, 176), (126, 172), (112, 216)], W_, w=int(3 * p.s)); p.poly([(182, 176), (174, 172), (188, 216)], W_, w=int(3 * p.s))
    brows(p, 120, 180, 92, e)
    eye(p, 120, 116, e, b); eye(p, 180, 116, e, b)
    p.ell((92, 136, 108, 146), BLUSH, ol=False); p.ell((192, 136, 208, 146), BLUSH, ol=False)


def kaplumbaga(p, e, b):
    shadow(p, w=110)
    for x in (80, 130, 186, 226):
        p.ell((x - 18, 230, x + 18, 276), GREEN_L)
    p.ell((40, 196, 84, 222), GREEN_L)
    p.ell((190, 104, 278, 196), GREEN_L)
    p.chord((40, 100, 244, 300), 180, 360, GREEN)
    p.rr((34, 190, 250, 216), 12, (30, 130, 70, 255))
    for (x, y) in ((100, 150), (142, 128), (184, 150), (142, 172)):
        hex_ = [(x + 20 * math.cos(math.radians(a)), y + 20 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        p.poly(hex_, (60, 190, 110, 255), w=int(4 * p.s))
    eye(p, 244, 140, e, b, r=8)
    p.arc((228, 154, 262, 180), 20, 140, INK, 5)
    p.ell((252, 158, 266, 166), BLUSH, ol=False)


def ari(p, e, b):
    shadow(p, w=70); legs(p, top=262, bot=330, gap=26)
    p.ell((70, 40, 148, 130), (220, 240, 255, 255)); p.ell((152, 40, 230, 130), (220, 240, 255, 255))
    for sx in (-1, 1):
        p.line([(150 + sx * 20, 96), (150 + sx * 44, 40)], INK, 5); p.ell((150 + sx * 44 - 8, 32, 150 + sx * 44 + 8, 48), INK, ol=False)
    arms(p, 190, 72, 228, YELLOW)
    p.poly([(140, 268), (160, 268), (150, 296)], INK, ol=False)
    p.ell((66, 90, 234, 276), YELLOW)
    p.poly(ell_band(150, 183, 84, 93, 196, 216), INK, ol=False)
    p.poly(ell_band(150, 183, 84, 93, 236, 254), INK, ol=False)
    p.ell((66, 90, 234, 276), None)
    p.rr((182, 206, 210, 230), 4, W_, w=int(3 * p.s))
    face(p, 150, 148, e, b, 26)


KINDS = {
    "tokmak": ("Tokmak", tokmak), "acik_kitap": ("Açık Kanun", acik_kitap), "kum_saati": ("Zamanaşımı", kum_saati),
    "takvim": ("Son Gün", takvim), "zarf": ("Tebligat", zarf), "dilekce": ("Dilekçe", dilekce),
    "kalem": ("İmza Kalemi", kalem), "anahtar": ("Hak Anahtarı", anahtar), "kilit": ("KVKK Kilidi", kilit),
    "buyutec": ("Büyüteç", buyutec), "kamera": ("Delil Kamera", kamera), "telefon": ("SMS Telefon", telefon),
    "fis": ("Fiş", fis), "kredi_karti": ("Kredi Kartı", kredi_karti), "ev": ("Kiracı Ev", ev),
    "araba": ("Trafik Araba", araba), "koli": ("Kargo Koli", koli), "poset": ("Tüketici Poşet", poset),
    "kumbara": ("Kumbara", kumbara), "ilk_yardim": ("Hasta Hakkı", ilk_yardim), "baret": ("İşçi Baret", baret),
    "kep": ("Öğrenci Kep", kep), "ampul": ("Bilgi Ampul", ampul), "adliye": ("Adliye", adliye),
    "zil": ("Uyarı Zili", zil), "muhur_mumu": ("Mühür Mumu", muhur_mumu), "guvercin": ("Arabulucu Güvercin", guvercin),
    "fil": ("Hafız Fil", fil), "kaplumbaga": ("Kalkan Kaplumbağa", kaplumbaga), "ari": ("Emekçi Arı", ari),
}


@lru_cache(maxsize=512)
def m30(kind, expr="normal", size=260, blink=False):
    sx = size / 300.0
    im, d = canvas(size, 380 * sx)
    p = P(d, SS * sx)
    KINDS[kind][1](p, expr, blink)
    return finish(im)
