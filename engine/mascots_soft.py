"""Premium yumuşak-3D hukuk maskotları. soft_mascot(kind, expr, size) -> RGBA."""
from functools import lru_cache

from .soft3d import Soft, glossy_eye, smile

BLACK_F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"

NAVY = (38, 46, 78)
ROBE = (40, 42, 56)
RED = (226, 54, 50)
GOLD = (240, 186, 60)
CREAM = (246, 234, 214)
WHITE = (252, 252, 252)
BLUSH = (255, 130, 130)


def robe_front(s, cx, top, bot, half_t, half_b, lapel=RED):
    s.paint(s.poly([(cx - half_t, top), (cx + half_t, top), (cx + half_b, bot), (cx - half_b, bot)]), ROBE, bevel=22,
            spec=(cx - half_t + 6, top + 10, cx - half_t + 40, top + 90), spec_a=0.18)
    s.paint(s.poly([(cx - 18, top - 2), (cx + 18, top - 2), (cx, top + 40)]), WHITE, bevel=6, outline=0.3)
    s.paint(s.poly([(cx - 18, top - 4), (cx - 40, top), (cx - 4, top + 78)]), lapel, bevel=6, outline=0.4)
    s.paint(s.poly([(cx + 18, top - 4), (cx + 40, top), (cx + 4, top + 78)]), lapel, bevel=6, outline=0.4)
    s.paint(s.rr((cx - 7, top + 6, cx + 7, top + 44), 3), WHITE, bevel=3, outline=0.35)


# ---------------------------------------------------------------- 1) Baykuş
def baykus(s, e):
    s.ground_shadow(150, 352, 86)
    for x in (122, 178):
        s.paint(s.ell((x - 20, 326, x + 20, 352)), (244, 160, 50), bevel=6)
    body = (64, 118, 236, 346)
    s.paint(s.ell(body), (150, 108, 78), bevel=30, spec=(90, 140, 140, 220), spec_a=0.25)
    s.paint(s.ell((104, 196, 196, 338)), CREAM, bevel=14, outline=0.25)
    for r in range(3):
        for c in range(3 - (r == 2)):
            x = 124 + c * 26 + (13 if r == 2 else 0); y = 222 + r * 30
            s.paint(s.arc((x - 11, y - 8, x + 11, y + 10), 20, 160, 3), (205, 180, 150), flat=True, outline=0)
    # cübbe kanatları
    s.paint(s.poly([(66, 196), (110, 186), (124, 334), (84, 312), (60, 260)]), ROBE, bevel=18)
    s.paint(s.poly([(234, 196), (190, 186), (176, 334), (216, 312), (240, 260)]), ROBE, bevel=18)
    s.paint(s.poly([(110, 186), (126, 186), (134, 250)]), RED, bevel=4, outline=0.4)
    s.paint(s.poly([(190, 186), (174, 186), (166, 250)]), RED, bevel=4, outline=0.4)
    # tokmak
    s.paint(s.line([(214, 286), (250, 248)], 9), (150, 92, 50), bevel=4)
    s.paint(s.poly([(236, 222), (272, 256), (258, 270), (222, 236)]), (150, 92, 50), bevel=6)
    s.paint(s.poly([(244, 230), (252, 238), (238, 252), (230, 244)]), GOLD, bevel=3, outline=0.3)
    # kulak tüyleri
    s.paint(s.poly([(78, 92), (62, 30), (112, 66)]), (128, 90, 64), bevel=8)
    s.paint(s.poly([(222, 92), (238, 30), (188, 66)]), (128, 90, 64), bevel=8)
    # kafa
    s.paint(s.ell((56, 40, 244, 214)), (156, 114, 82), bevel=34, spec=(84, 52, 150, 100), spec_a=0.35)
    s.paint(s.ell((78, 70, 222, 204)), (238, 222, 196), bevel=18, outline=0.25)
    glossy_eye(s, 120, 128, 27, 29, (214, 140, 40), e)
    glossy_eye(s, 180, 128, 27, 29, (214, 140, 40), e)
    s.paint(s.ring((88, 94, 152, 162), 5), GOLD, bevel=3, outline=0.35, spec=(92, 96, 120, 112))
    s.paint(s.ring((148, 94, 212, 162), 5), GOLD, bevel=3, outline=0.35, spec=(152, 96, 180, 112))
    s.paint(s.line([(150, 126), (150, 126)], 6), GOLD, bevel=2)
    s.paint(s.poly([(138, 158), (162, 158), (150, 184)]), (246, 170, 50), bevel=5, spec=(140, 158, 152, 168))
    s.soft_spot((88, 160, 112, 176), BLUSH, 4, 0.5)
    s.soft_spot((188, 160, 212, 176), BLUSH, 4, 0.5)


# ---------------------------------------------------------------- 2) Tilki avukat
def tilki(s, e):
    s.ground_shadow(150, 354, 80)
    s.paint(s.poly([(214, 300), (286, 236), (270, 300), (236, 330)]), (240, 128, 50), bevel=16)
    s.paint(s.poly([(270, 250), (286, 236), (278, 268)]), WHITE, bevel=4)
    for x in (124, 176):
        s.paint(s.rr((x - 20, 316, x + 20, 352), 12), (50, 40, 40), bevel=6)
    s.paint(s.rr((84, 196, 216, 330), 44), NAVY, bevel=24, spec=(92, 206, 126, 280), spec_a=0.2)
    s.paint(s.poly([(150, 200), (124, 200), (150, 262)]), WHITE, bevel=4, outline=0.3)
    s.paint(s.poly([(150, 200), (176, 200), (150, 262)]), WHITE, bevel=4, outline=0.3)
    s.paint(s.poly([(144, 208), (156, 208), (162, 250), (150, 266), (138, 250)]), RED, bevel=4, outline=0.4)
    # çanta
    s.paint(s.rr((44, 262, 98, 306), 8), (120, 70, 40), bevel=8, spec=(48, 266, 70, 278))
    s.paint(s.arc((58, 248, 84, 274), 180, 360, 4), (80, 46, 26), flat=True, outline=0)
    s.paint(s.rr((66, 280, 76, 288), 2), GOLD, bevel=2)
    # kulaklar
    s.paint(s.poly([(70, 108), (68, 28), (128, 72)]), (236, 120, 44), bevel=10)
    s.paint(s.poly([(230, 108), (232, 28), (172, 72)]), (236, 120, 44), bevel=10)
    s.paint(s.poly([(80, 92), (78, 46), (114, 74)]), (60, 40, 40), bevel=5, outline=0)
    s.paint(s.poly([(220, 92), (222, 46), (186, 74)]), (60, 40, 40), bevel=5, outline=0)
    # kafa
    s.paint(s.ell((58, 56, 242, 214)), (244, 128, 48), bevel=32, spec=(86, 66, 150, 110), spec_a=0.35)
    s.paint(s.poly([(64, 150), (150, 130), (236, 150), (150, 222)]), WHITE, bevel=16, outline=0.15)
    glossy_eye(s, 116, 128, 22, 25, (70, 120, 60), e)
    glossy_eye(s, 184, 128, 22, 25, (70, 120, 60), e)
    s.paint(s.ell((138, 158, 162, 176)), (40, 30, 30), bevel=4, spec=(142, 160, 152, 166))
    smile(s, 150, 186, 30, e if e != "normal" else "normal")
    s.soft_spot((84, 158, 106, 172), BLUSH, 4, 0.45)
    s.soft_spot((194, 158, 216, 172), BLUSH, 4, 0.45)


# ---------------------------------------------------------------- 3) Kalkan
def kalkan(s, e):
    s.ground_shadow(150, 352, 70)
    for x in (126, 174):
        s.paint(s.rr((x - 9, 280, x + 9, 334), 8), (40, 40, 50), bevel=4)
        s.paint(s.rr((x - 20, 324, x + 18, 350), 12), (40, 40, 50), bevel=6)
    s.paint(s.line([(66, 170), (34, 216)], 12), (40, 40, 50), bevel=5)
    s.paint(s.ell((20, 204, 46, 230)), WHITE, bevel=6)
    s.paint(s.line([(234, 160), (262, 112)], 12), (40, 40, 50), bevel=5)
    s.paint(s.ell((250, 96, 276, 122)), WHITE, bevel=6)
    outer = [(56, 76), (150, 40), (244, 76), (238, 196), (150, 312), (62, 196)]
    inner = [(76, 92), (150, 62), (224, 92), (218, 192), (150, 286), (82, 192)]
    s.paint(s.poly(outer), GOLD, bevel=12, spec=(70, 70, 120, 110))
    s.paint(s.poly(inner), RED, bevel=26, spec=(88, 92, 150, 150), spec_a=0.4)
    s.paint(s.ell((98, 106, 202, 214)), WHITE, bevel=14, outline=0.25)
    glossy_eye(s, 128, 150, 15, 18, (40, 80, 160), e)
    glossy_eye(s, 172, 150, 15, 18, (40, 80, 160), e)
    smile(s, 150, 184, 30, e)
    s.soft_spot((106, 170, 124, 182), BLUSH, 3, 0.5)
    s.soft_spot((176, 170, 194, 182), BLUSH, 3, 0.5)
    s.paint(s.text((150, 246), "★", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40), GOLD, bevel=4, outline=0.3)


# ---------------------------------------------------------------- 4) Kanun kitabı
def kitap(s, e):
    s.ground_shadow(150, 354, 84)
    for x in (122, 178):
        s.paint(s.rr((x - 20, 322, x + 20, 350), 12), (50, 40, 40), bevel=6)
    s.paint(s.rr((70, 52, 248, 326), 18), CREAM, bevel=10)
    for y in range(70, 320, 12):
        s.paint(s.line([(238, y), (246, y)], 1.5), (210, 196, 170), flat=True, outline=0)
    s.paint(s.rr((52, 40, 232, 316), 20), (170, 32, 40), bevel=30, spec=(66, 52, 120, 140), spec_a=0.3)
    s.paint(s.rr((52, 40, 78, 316), 12), (130, 22, 30), bevel=8, outline=0.3)
    for (x, y) in ((214, 56), (214, 300)):
        s.paint(s.ell((x - 12, y - 12, x + 12, y + 12)), GOLD, bevel=4)
    s.paint(s.rr((96, 236, 210, 282), 10), GOLD, bevel=8, spec=(100, 238, 150, 250))
    s.paint(s.text((153, 259), "KANUN", BLACK_F, 26), (120, 24, 30), flat=True, outline=0)
    s.paint(s.poly([(186, 310), (200, 310), (200, 356), (193, 346), (186, 356)]), (40, 90, 200), bevel=3)
    s.paint(s.line([(56, 180), (22, 220)], 12), (130, 22, 30), bevel=5)
    s.paint(s.ell((10, 208, 36, 234)), WHITE, bevel=6)
    s.paint(s.line([(232, 170), (264, 130)], 12), (130, 22, 30), bevel=5)
    s.paint(s.ell((252, 114, 278, 140)), WHITE, bevel=6)
    s.paint(s.rr((88, 82, 212, 212), 30), (250, 244, 232), bevel=14, outline=0.25)
    glossy_eye(s, 126, 136, 16, 19, (90, 60, 40), e)
    glossy_eye(s, 174, 136, 16, 19, (90, 60, 40), e)
    s.paint(s.ring((102, 112, 150, 160), 4), (40, 40, 50), bevel=2, outline=0)
    s.paint(s.ring((150, 112, 198, 160), 4), (40, 40, 50), bevel=2, outline=0)
    smile(s, 150, 182, 30, e)
    s.soft_spot((96, 166, 114, 178), BLUSH, 3, 0.5)
    s.soft_spot((186, 166, 204, 178), BLUSH, 3, 0.5)


# ---------------------------------------------------------------- 5) Tokmak
def tokmak(s, e):
    s.ground_shadow(150, 354, 96)
    s.paint(s.rr((60, 318, 240, 346), 12), (130, 80, 44), bevel=10, spec=(70, 320, 140, 330))
    s.paint(s.rr((138, 190, 162, 322), 10), (170, 106, 58), bevel=8, spec=(140, 196, 150, 300))
    s.paint(s.line([(56, 150), (24, 196)], 11), (110, 66, 36), bevel=5)
    s.paint(s.ell((12, 184, 38, 210)), (255, 214, 178), bevel=6)
    s.paint(s.line([(244, 150), (276, 106)], 11), (110, 66, 36), bevel=5)
    s.paint(s.ell((264, 92, 290, 118)), (255, 214, 178), bevel=6)
    s.paint(s.rr((40, 82, 260, 200), 46), (176, 110, 60), bevel=30, spec=(56, 90, 160, 120), spec_a=0.35)
    for x in (84, 216):
        s.paint(s.rr((x - 9, 84, x + 9, 198), 4), GOLD, bevel=5, outline=0.35)
    s.paint(s.rr((30, 78, 64, 204), 16), (140, 84, 46), bevel=10)
    s.paint(s.rr((236, 78, 270, 204), 16), (140, 84, 46), bevel=10)
    glossy_eye(s, 126, 132, 16, 19, (60, 40, 30), e)
    glossy_eye(s, 174, 132, 16, 19, (60, 40, 30), e)
    smile(s, 150, 168, 30, e)
    s.soft_spot((100, 154, 116, 166), BLUSH, 3, 0.5)
    s.soft_spot((184, 154, 200, 166), BLUSH, 3, 0.5)


# ---------------------------------------------------------------- 6) Fil
def fil(s, e):
    s.ground_shadow(150, 356, 92)
    G = (152, 168, 196)
    for x in (112, 188):
        s.paint(s.rr((x - 22, 290, x + 22, 350), 16), G, bevel=10)
    s.paint(s.rr((80, 196, 220, 320), 50), G, bevel=26)
    robe_front(s, 150, 206, 318, 46, 64)
    s.paint(s.ell((6, 58, 116, 210)), G, bevel=20)
    s.paint(s.ell((24, 80, 100, 190)), (236, 186, 200), bevel=12, outline=0.2)
    s.paint(s.ell((184, 58, 294, 210)), G, bevel=20)
    s.paint(s.ell((200, 80, 276, 190)), (236, 186, 200), bevel=12, outline=0.2)
    s.paint(s.ell((66, 34, 234, 214)), G, bevel=34, spec=(92, 46, 160, 100), spec_a=0.35)
    s.paint(s.line([(150, 150), (150, 196), (166, 214)], 26), G, bevel=12)
    s.paint(s.poly([(118, 176), (128, 172), (114, 206)]), WHITE, bevel=4)
    s.paint(s.poly([(182, 176), (172, 172), (186, 206)]), WHITE, bevel=4)
    glossy_eye(s, 118, 122, 17, 20, (60, 70, 110), e)
    glossy_eye(s, 182, 122, 17, 20, (60, 70, 110), e)
    s.soft_spot((88, 146, 108, 160), BLUSH, 4, 0.5)
    s.soft_spot((192, 146, 212, 160), BLUSH, 4, 0.5)


KINDS = {"baykus": ("Hakkı Baykuş", baykus), "tilki": ("Avukat Tilki", tilki), "kalkan": ("Kalkan", kalkan),
         "kitap": ("Kanun Kitabı", kitap), "tokmak": ("Tokmak", tokmak), "fil": ("Hafız Fil", fil)}


@lru_cache(maxsize=128)
def soft_mascot(kind, expr="normal", size=300):
    s = Soft(300, 380, k=3)
    KINDS[kind][1](s, expr)
    return s.image(size)
