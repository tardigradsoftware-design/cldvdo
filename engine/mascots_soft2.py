"""Premium yumuşak-3D seri 2: sevimli (chibi) hukuk karakterleri. soft2(kind, expr, size)."""
import math
from functools import lru_cache

from .soft3d import Soft, glossy_eye, smile

BLACK_F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NAVY = (38, 50, 92)
ROBE = (40, 42, 56)
RED = (226, 54, 50)
GOLD = (240, 186, 60)
CREAM = (248, 236, 216)
WHITE = (252, 252, 252)
BLUSH = (255, 128, 128)
GREEN = (46, 170, 100)


def limb(s, a, b, w, col, hand=None, hr=13):
    s.paint(s.line([a, b], w), col, bevel=6, outline=0.35)
    if hand:
        s.paint(s.ell((b[0] - hr, b[1] - hr, b[0] + hr, b[1] + hr)), hand, bevel=6, spec=(b[0] - hr + 3, b[1] - hr + 2, b[0], b[1] - 2))


def feet(s, col, y=328, gap=30, w=24):
    for x in (150 - gap, 150 + gap):
        s.paint(s.ell((x - w, y - 6, x + w, y + 22)), col, bevel=8, spec=(x - w + 6, y - 4, x, y + 4))


def cheeks(s, lx, rx, y, a=0.5):
    s.soft_spot((lx - 12, y - 7, lx + 12, y + 7), BLUSH, 4, a)
    s.soft_spot((rx - 12, y - 7, rx + 12, y + 7), BLUSH, 4, a)


def suit(s, col=NAVY, tie=RED, top=200, bot=322):
    s.paint(s.rr((92, top, 208, bot), 46), col, bevel=22, spec=(100, top + 10, 130, top + 70), spec_a=0.22)
    s.paint(s.poly([(150, top + 2), (126, top + 2), (150, top + 54)]), WHITE, bevel=4, outline=0.3)
    s.paint(s.poly([(150, top + 2), (174, top + 2), (150, top + 54)]), WHITE, bevel=4, outline=0.3)
    s.paint(s.poly([(145, top + 8), (155, top + 8), (160, top + 42), (150, top + 56), (140, top + 42)]), tie, bevel=3, outline=0.4)


def robe(s, top=200, bot=324):
    s.paint(s.poly([(98, top), (202, top), (222, bot), (78, bot)]), ROBE, bevel=22, spec=(100, top + 10, 128, top + 80), spec_a=0.18)
    s.paint(s.poly([(150, top), (130, top), (150, top + 46)]), WHITE, bevel=3, outline=0.3)
    s.paint(s.poly([(150, top), (170, top), (150, top + 46)]), WHITE, bevel=3, outline=0.3)
    s.paint(s.poly([(132, top - 2), (112, top + 2), (146, top + 70)]), RED, bevel=4, outline=0.4)
    s.paint(s.poly([(168, top - 2), (188, top + 2), (154, top + 70)]), RED, bevel=4, outline=0.4)


def gavel(s, x, y, ang=-40):
    a = math.radians(ang)
    hx, hy = x + 46 * math.cos(a), y + 46 * math.sin(a)
    s.paint(s.line([(x, y), (hx, hy)], 8), (150, 92, 50), bevel=3)
    px, py = -math.sin(a), math.cos(a)
    L, Wd = 22, 12
    pts = [(hx + px * L + math.cos(a) * Wd, hy + py * L + math.sin(a) * Wd), (hx + px * L - math.cos(a) * Wd, hy + py * L - math.sin(a) * Wd),
           (hx - px * L - math.cos(a) * Wd, hy - py * L - math.sin(a) * Wd), (hx - px * L + math.cos(a) * Wd, hy - py * L + math.sin(a) * Wd)]
    s.paint(s.poly(pts), (150, 92, 50), bevel=5)


# ---------------------------------------------------------------- 1) Penguen Avukat
def penguen(s, e):
    s.ground_shadow(150, 352, 80)
    feet(s, (248, 160, 50), 330, 30)
    s.paint(s.ell((66, 120, 234, 346)), (36, 40, 56), bevel=30, spec=(80, 140, 120, 240), spec_a=0.2)
    s.paint(s.ell((100, 176, 200, 338)), WHITE, bevel=16, outline=0.2)
    limb(s, (74, 210), (46, 270), 24, (36, 40, 56))
    limb(s, (226, 210), (258, 160), 24, (36, 40, 56))
    s.paint(s.rr((236, 120, 286, 168), 6), CREAM, bevel=6, spec=(240, 122, 260, 132))
    s.paint(s.rr((236, 128, 286, 136), 0), RED, flat=True, outline=0)
    s.paint(s.ell((60, 34, 240, 204)), (36, 40, 56), bevel=34, spec=(86, 44, 150, 96), spec_a=0.4)
    s.paint(s.union(s.ell((88, 84, 156, 184)), s.ell((144, 84, 212, 184))), WHITE, bevel=14, outline=0.2)
    glossy_eye(s, 122, 128, 18, 21, (60, 90, 150), e)
    glossy_eye(s, 178, 128, 18, 21, (60, 90, 150), e)
    s.paint(s.poly([(136, 160), (164, 160), (150, 182)]), (248, 160, 50), bevel=5, spec=(138, 160, 150, 168))
    cheeks(s, 100, 200, 166)
    s.paint(s.union(s.poly([(150, 206), (122, 194), (122, 220)]), s.poly([(150, 206), (178, 194), (178, 220)])), RED, bevel=5)
    s.paint(s.ell((143, 199, 157, 213)), (190, 36, 36), bevel=3)


# ---------------------------------------------------------------- 2) Aslan Hakim
def aslan(s, e):
    s.ground_shadow(150, 354, 84)
    feet(s, (60, 46, 40), 330, 32)
    robe(s)
    limb(s, (96, 224), (64, 280), 22, ROBE, (232, 170, 80))
    mane = []
    for k in range(14):
        a = 2 * math.pi * k / 14
        cx, cy = 150 + 92 * math.cos(a), 122 + 86 * math.sin(a)
        mane.append(s.ell((cx - 30, cy - 30, cx + 30, cy + 30)))
    s.paint(s.union(*mane), (196, 100, 40), bevel=24, spec=(80, 40, 150, 90), spec_a=0.25)
    s.paint(s.ell((76, 52, 104, 80)), (226, 150, 70), bevel=6)
    s.paint(s.ell((196, 52, 224, 80)), (226, 150, 70), bevel=6)
    s.paint(s.ell((70, 52, 230, 200)), (238, 172, 84), bevel=30, spec=(92, 60, 150, 100), spec_a=0.35)
    s.paint(s.union(s.ell((112, 140, 156, 190)), s.ell((144, 140, 188, 190))), CREAM, bevel=12, outline=0.2)
    glossy_eye(s, 120, 118, 17, 20, (150, 100, 30), e)
    glossy_eye(s, 180, 118, 17, 20, (150, 100, 30), e)
    s.paint(s.poly([(136, 144), (164, 144), (150, 160)]), (90, 50, 40), bevel=4, spec=(140, 144, 150, 150))
    smile(s, 150, 172, 24, e)
    cheeks(s, 98, 202, 150, 0.45)
    limb(s, (204, 236), (244, 262), 22, ROBE, (232, 170, 80))
    gavel(s, 244, 262, -75)


# ---------------------------------------------------------------- 3) Kedi Avukat
def kedi(s, e):
    s.ground_shadow(150, 352, 80)
    G = (156, 160, 172)
    s.paint(s.line([(196, 306), (248, 300), (268, 248), (256, 222)], 16), G, bevel=6)
    feet(s, (70, 70, 80), 330, 30)
    suit(s, (60, 40, 100), GOLD)
    limb(s, (96, 224), (70, 282), 22, (60, 40, 100), G)
    limb(s, (204, 224), (232, 270), 22, (60, 40, 100), G)
    s.paint(s.rr((206, 246, 262, 292), 6), (40, 110, 220), bevel=6, spec=(210, 248, 232, 258))
    s.paint(s.poly([(74, 100), (78, 26), (136, 66)]), G, bevel=10)
    s.paint(s.poly([(226, 100), (222, 26), (164, 66)]), G, bevel=10)
    s.paint(s.poly([(86, 86), (88, 44), (122, 68)]), (240, 170, 180), bevel=5, outline=0.2)
    s.paint(s.poly([(214, 86), (212, 44), (178, 68)]), (240, 170, 180), bevel=5, outline=0.2)
    s.paint(s.ell((62, 50, 238, 212)), G, bevel=32, spec=(88, 58, 150, 100), spec_a=0.35)
    s.paint(s.ell((108, 140, 192, 204)), (236, 236, 240), bevel=12, outline=0.15)
    glossy_eye(s, 118, 124, 19, 22, (90, 170, 80), e)
    glossy_eye(s, 182, 124, 19, 22, (90, 170, 80), e)
    s.paint(s.ring((92, 98, 146, 152), 4), (40, 40, 50), bevel=2, outline=0)
    s.paint(s.ring((154, 98, 208, 152), 4), (40, 40, 50), bevel=2, outline=0)
    s.paint(s.line([(146, 124), (154, 124)], 4), (40, 40, 50), flat=True, outline=0)
    s.paint(s.poly([(142, 156), (158, 156), (150, 166)]), (230, 120, 140), bevel=3)
    smile(s, 150, 176, 22, e)
    for sy in (-1, 1):
        for d in (0, 10):
            s.paint(s.line([(96, 168 + d), (62, 162 + d * 1.6)], 2), (90, 90, 100), flat=True, outline=0)
            s.paint(s.line([(204, 168 + d), (238, 162 + d * 1.6)], 2), (90, 90, 100), flat=True, outline=0)
    cheeks(s, 100, 200, 160)


# ---------------------------------------------------------------- 4) Panda Arabulucu
def panda(s, e):
    s.ground_shadow(150, 354, 86)
    K = (40, 40, 48)
    feet(s, K, 330, 34, 26)
    s.paint(s.rr((84, 190, 216, 326), 56), WHITE, bevel=26, spec=(94, 200, 130, 260), spec_a=0.3)
    limb(s, (92, 230), (60, 270), 28, K, K, 16)
    limb(s, (208, 230), (244, 196), 28, K, K, 16)
    s.paint(s.line([(244, 196), (276, 150)], 4), (90, 140, 60), flat=True, outline=0)
    for (x, y, a) in ((262, 168, 30), (272, 152, -20), (254, 182, -30), (280, 140, 20)):
        s.paint(s.ell((x - 10, y - 5, x + 10, y + 5)), (120, 190, 80), bevel=3, outline=0.3)
    s.paint(s.ell((60, 30, 108, 78)), K, bevel=10)
    s.paint(s.ell((192, 30, 240, 78)), K, bevel=10)
    s.paint(s.ell((62, 44, 238, 210)), WHITE, bevel=30, spec=(86, 52, 150, 96), spec_a=0.4)
    s.paint(s.ell((92, 96, 146, 158)), K, bevel=10, outline=0)
    s.paint(s.ell((154, 96, 208, 158)), K, bevel=10, outline=0)
    glossy_eye(s, 121, 128, 14, 16, (90, 60, 40), e)
    glossy_eye(s, 179, 128, 14, 16, (90, 60, 40), e)
    s.paint(s.ell((138, 152, 162, 168)), K, bevel=4, spec=(142, 153, 152, 158))
    smile(s, 150, 180, 24, e)
    cheeks(s, 96, 204, 166)


# ---------------------------------------------------------------- 5) Ayı Koruyucu
def ayi(s, e):
    s.ground_shadow(150, 354, 88)
    B = (150, 96, 60)
    feet(s, (110, 68, 40), 330, 34, 26)
    s.paint(s.rr((84, 192, 216, 326), 56), B, bevel=26, spec=(94, 200, 130, 260), spec_a=0.25)
    s.paint(s.ell((110, 226, 190, 318)), (220, 180, 130), bevel=14, outline=0.2)
    limb(s, (210, 232), (240, 274), 26, B, B, 15)
    # kalkan
    pts = [(24, 206), (80, 190), (136, 206), (130, 270), (80, 320), (30, 270)]
    s.paint(s.poly(pts), (50, 110, 220), bevel=18, spec=(36, 206, 80, 240))
    s.paint(s.poly([(34, 214), (80, 200), (126, 214), (121, 266), (80, 308), (39, 266)]), (70, 140, 240), bevel=10, outline=0.2)
    s.paint(s.line([(56, 252), (74, 272), (106, 232)], 10), WHITE, bevel=3, outline=0.3)
    s.paint(s.ell((64, 34, 112, 82)), B, bevel=10)
    s.paint(s.ell((188, 34, 236, 82)), B, bevel=10)
    s.paint(s.ell((76, 46, 100, 70)), (220, 160, 130), bevel=4, outline=0)
    s.paint(s.ell((200, 46, 224, 70)), (220, 160, 130), bevel=4, outline=0)
    s.paint(s.ell((62, 44, 238, 210)), B, bevel=30, spec=(86, 52, 150, 96), spec_a=0.35)
    s.paint(s.ell((110, 136, 190, 198)), (232, 196, 150), bevel=12, outline=0.15)
    glossy_eye(s, 116, 118, 16, 19, (70, 40, 20), e)
    glossy_eye(s, 184, 118, 16, 19, (70, 40, 20), e)
    s.paint(s.ell((136, 142, 164, 162)), (50, 30, 26), bevel=4, spec=(140, 143, 152, 150))
    smile(s, 150, 176, 22, e)
    cheeks(s, 96, 204, 150)


# ---------------------------------------------------------------- 6) Tavşan Stajyer
def tavsan(s, e):
    s.ground_shadow(150, 354, 78)
    W_ = (246, 244, 248)
    feet(s, W_, 332, 30, 26)
    suit(s, (46, 140, 110), RED, 204, 324)
    s.paint(s.rr((140, 226, 160, 250), 4), GOLD, bevel=3)
    limb(s, (98, 226), (72, 284), 22, (46, 140, 110), W_)
    limb(s, (202, 226), (236, 262), 22, (46, 140, 110), W_)
    s.paint(s.rr((214, 230, 268, 300), 6), (150, 100, 60), bevel=6)
    s.paint(s.rr((220, 242, 262, 296), 3), WHITE, bevel=3, outline=0.2)
    for y in (254, 266, 278):
        s.paint(s.line([(226, y), (256, y)], 2.4), (170, 170, 180), flat=True, outline=0)
    s.paint(s.rr((230, 224, 246, 236), 3), (120, 120, 130), bevel=2)
    s.paint(s.ell((84, 4, 132, 130)), W_, bevel=14)
    s.paint(s.ell((98, 20, 120, 116)), (250, 180, 196), bevel=6, outline=0.15)
    s.paint(s.ell((168, 4, 216, 130)), W_, bevel=14)
    s.paint(s.ell((180, 20, 202, 116)), (250, 180, 196), bevel=6, outline=0.15)
    s.paint(s.ell((64, 56, 236, 216)), W_, bevel=30, spec=(88, 64, 150, 104), spec_a=0.4)
    glossy_eye(s, 120, 132, 18, 21, (200, 80, 110), e)
    glossy_eye(s, 180, 132, 18, 21, (200, 80, 110), e)
    s.paint(s.poly([(142, 160), (158, 160), (150, 170)]), (240, 130, 150), bevel=3)
    smile(s, 150, 182, 22, e)
    s.paint(s.rr((140, 190, 160, 200), 3), WHITE, bevel=2, outline=0.3)
    cheeks(s, 98, 202, 168, 0.6)


# ---------------------------------------------------------------- 7) Terazi
def terazi(s, e):
    s.ground_shadow(150, 356, 90)
    s.paint(s.poly([(96, 346), (204, 346), (182, 312), (118, 312)]), GOLD, bevel=12, spec=(104, 316, 140, 330))
    s.paint(s.rr((140, 190, 160, 316), 8), GOLD, bevel=8)
    s.paint(s.rr((14, 92, 286, 108), 8), GOLD, bevel=6, spec=(20, 92, 120, 98))
    for cx in (40, 260):
        s.paint(s.line([(cx, 100), (cx - 24, 186)], 2.5), (150, 110, 40), flat=True, outline=0)
        s.paint(s.line([(cx, 100), (cx + 24, 186)], 2.5), (150, 110, 40), flat=True, outline=0)
        s.paint(s.chord((cx - 40, 160, cx + 40, 212), 0, 180), GOLD, bevel=10, spec=(cx - 30, 186, cx, 196))
    s.paint(s.ell((136, 32, 164, 60)), GOLD, bevel=6)
    s.paint(s.ell((84, 60, 216, 192)), (232, 70, 60), bevel=30, spec=(104, 70, 150, 104), spec_a=0.4)
    s.paint(s.ell((100, 76, 200, 176)), WHITE, bevel=14, outline=0.2)
    glossy_eye(s, 130, 118, 13, 16, (60, 80, 150), e)
    glossy_eye(s, 170, 118, 13, 16, (60, 80, 150), e)
    smile(s, 150, 150, 22, e)
    cheeks(s, 112, 188, 140, 0.45)


# ---------------------------------------------------------------- 8) Kumbara Domuz
def domuz(s, e):
    s.ground_shadow(150, 352, 100)
    P_ = (250, 170, 190)
    PD = (230, 128, 156)
    for x in (88, 126, 174, 212):
        s.paint(s.rr((x - 16, 270, x + 16, 334), 12), PD, bevel=8)
    s.paint(s.arc((14, 170, 58, 214), 90, 340, 7), PD, bevel=3)
    s.paint(s.ell((40, 120, 260, 300)), P_, bevel=36, spec=(70, 132, 150, 190), spec_a=0.45)
    s.paint(s.ell((70, 104, 122, 150)), PD, bevel=10)
    s.paint(s.ell((178, 104, 230, 150)), PD, bevel=10)
    s.paint(s.rr((124, 126, 176, 138), 5), (120, 60, 80), bevel=3, outline=0)
    s.paint(s.ell((128, 60, 172, 104)), GOLD, bevel=10, spec=(134, 64, 150, 76))
    s.paint(s.text((150, 83), "₺", DEJAVU, 26), (200, 140, 30), flat=True, outline=0)
    glossy_eye(s, 116, 176, 15, 18, (90, 50, 60), e)
    glossy_eye(s, 184, 176, 15, 18, (90, 50, 60), e)
    s.paint(s.ell((122, 200, 178, 240)), PD, bevel=10, spec=(128, 202, 146, 212))
    s.paint(s.ell((136, 212, 146, 228)), (140, 70, 90), flat=True, outline=0)
    s.paint(s.ell((154, 212, 164, 228)), (140, 70, 90), flat=True, outline=0)
    smile(s, 150, 252, 22, e)
    cheeks(s, 92, 208, 210, 0.5)


KINDS = {"penguen": ("Penguen Avukat", penguen), "aslan": ("Aslan Hâkim", aslan), "kedi": ("Kedi Avukat", kedi),
         "panda": ("Panda Arabulucu", panda), "ayi": ("Koruyucu Ayı", ayi), "tavsan": ("Tavşan Stajyer", tavsan),
         "terazi": ("Terazi", terazi), "domuz": ("Tüketici Kumbara", domuz)}


@lru_cache(maxsize=128)
def soft2(kind, expr="normal", size=300):
    s = Soft(300, 380, k=3)
    KINDS[kind][1](s, expr)
    return s.image(size)
