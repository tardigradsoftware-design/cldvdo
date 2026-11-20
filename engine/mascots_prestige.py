"""Prestijli / güvenilir hukuk maskotları (büst portre). prestige(kind, expr, size) -> RGBA. Alan 300x320."""
import math
from functools import lru_cache

from .soft3d import Soft

NAVY = (24, 38, 72)
NAVY_L = (40, 60, 108)
GOLD = (201, 162, 74)
GOLD_L = (232, 200, 120)
IVORY = (244, 238, 226)
BURG = (120, 28, 40)
ROBE = (26, 28, 36)
WHITE = (250, 250, 248)
INKC = (28, 24, 26)


def calm_eye(s, cx, cy, rx, ry, iris, expr="normal", lid=(60, 40, 30)):
    if expr == "happy":
        s.paint(s.arc((cx - rx, cy - ry * 0.5, cx + rx, cy + ry * 1.1), 205, 335, max(3, rx * 0.22)), lid, flat=True, outline=0)
        return
    s.paint(s.ell((cx - rx, cy - ry, cx + rx, cy + ry)), (248, 246, 240), shade=0.15, hi=0, bevel=4, outline=0.25, ow=1)
    ir = rx * 0.66
    s.paint(s.ell((cx - ir, cy - ir * 1.05 + ry * 0.1, cx + ir, cy + ir * 1.05 + ry * 0.1)), iris, shade=0.5, hi=0.1, bevel=4, outline=0.3, ow=1)
    pr = ir * 0.5
    s.paint(s.ell((cx - pr, cy - pr + ry * 0.1, cx + pr, cy + pr + ry * 0.1)), (16, 12, 14), flat=True, outline=0)
    s.paint(s.ell((cx - ir * 0.5, cy - ir * 0.6, cx - ir * 0.1, cy - ir * 0.2)), WHITE, flat=True, outline=0)
    # üst göz kapağı (ciddi bakış)
    s.paint(s.chord((cx - rx - 1, cy - ry - 4, cx + rx + 1, cy + ry * 0.55), 180, 360), lid, bevel=3, outline=0, alpha=0.9)
    s.paint(s.arc((cx - rx - 2, cy - ry * 0.75, cx + rx + 2, cy + ry * 0.95), 195, 345, 2.6), (30, 20, 20), flat=True, outline=0)


def calm_mouth(s, cx, cy, w, col=(110, 50, 50), expr="normal"):
    if expr == "happy":
        s.paint(s.arc((cx - w / 2, cy - w * 0.45, cx + w / 2, cy + w * 0.3), 25, 155, 3.2), col, flat=True, outline=0)
    else:
        s.paint(s.arc((cx - w / 2, cy - w * 0.25, cx + w / 2, cy + w * 0.18), 30, 150, 3), col, flat=True, outline=0)


def shoulders_robe(s, lapel=BURG):
    s.paint(s.poly([(20, 320), (40, 236), (110, 206), (190, 206), (260, 236), (280, 320)]), ROBE, bevel=26, spec=(48, 226, 110, 260), spec_a=0.15)
    s.paint(s.poly([(124, 206), (176, 206), (150, 262)]), WHITE, bevel=5, outline=0.3)
    s.paint(s.poly([(122, 204), (96, 212), (144, 300)]), lapel, bevel=6, outline=0.35)
    s.paint(s.poly([(178, 204), (204, 212), (156, 300)]), lapel, bevel=6, outline=0.35)
    s.paint(s.rr((142, 212, 158, 256), 3), WHITE, bevel=3, outline=0.3)


def shoulders_suit(s, tie=BURG, shirt=WHITE, col=NAVY):
    s.paint(s.poly([(20, 320), (38, 240), (110, 208), (190, 208), (262, 240), (280, 320)]), col, bevel=26, spec=(48, 226, 110, 262), spec_a=0.18)
    s.paint(s.poly([(118, 208), (182, 208), (150, 290)]), shirt, bevel=6, outline=0.3)
    s.paint(s.poly([(116, 206), (92, 218), (138, 300), (146, 270)]), NAVY_L if col == NAVY else col, bevel=8, outline=0.35)
    s.paint(s.poly([(184, 206), (208, 218), (162, 300), (154, 270)]), NAVY_L if col == NAVY else col, bevel=8, outline=0.35)
    if tie:
        s.paint(s.poly([(143, 214), (157, 214), (162, 270), (150, 290), (138, 270)]), tie, bevel=4, outline=0.35, spec=(144, 216, 150, 236))


# ---------------------------------------------------------------- 1) Aslan
def aslan(s, e):
    shoulders_robe(s)
    mane = []
    for k in range(18):
        a = 2 * math.pi * k / 18 - math.pi / 2
        cx, cy = 150 + 96 * math.cos(a), 126 + 92 * math.sin(a) * (0.95 if math.sin(a) < 0 else 1.05)
        mane.append(s.ell((cx - 30, cy - 34, cx + 30, cy + 34)))
    s.paint(s.union(*mane), (150, 96, 44), bevel=26, spec=(70, 40, 150, 90), spec_a=0.2, outline=0.4)
    s.paint(s.ell((72, 56, 228, 214)), (206, 150, 76), bevel=30, spec=(96, 64, 150, 104), spec_a=0.25)
    s.paint(s.union(s.ell((114, 148, 156, 196)), s.ell((144, 148, 186, 196))), (238, 220, 190), bevel=12, outline=0.2)
    s.paint(s.ell((128, 186, 172, 210)), (228, 206, 176), bevel=8, outline=0.15)
    calm_eye(s, 120, 122, 15, 12, (170, 110, 30), e, (150, 96, 44))
    calm_eye(s, 180, 122, 15, 12, (170, 110, 30), e, (150, 96, 44))
    s.paint(s.line([(100, 104), (136, 108)], 5), (130, 80, 36), flat=True, outline=0)
    s.paint(s.line([(200, 104), (164, 108)], 5), (130, 80, 36), flat=True, outline=0)
    s.paint(s.poly([(136, 152), (164, 152), (150, 170)]), (70, 40, 36), bevel=4, spec=(140, 152, 150, 158))
    calm_mouth(s, 150, 182, 26, (90, 50, 40), e)


# ---------------------------------------------------------------- 2) Baykuş
def baykus(s, e):
    s.paint(s.rr((30, 268, 270, 316), 10), BURG, bevel=12, spec=(40, 270, 120, 280))
    s.paint(s.rr((30, 300, 270, 316), 4), IVORY, bevel=3, outline=0.25)
    s.paint(s.rr((120, 278, 180, 294), 4), GOLD, bevel=4)
    B = (104, 90, 80)
    s.paint(s.ell((66, 110, 234, 290)), B, bevel=28, spec=(80, 120, 130, 180), spec_a=0.15)
    s.paint(s.ell((108, 170, 192, 286)), (226, 214, 196), bevel=12, outline=0.2)
    for r in range(3):
        for c in range(3):
            x, y = 126 + c * 24, 196 + r * 26
            s.paint(s.arc((x - 9, y - 6, x + 9, y + 8), 20, 160, 2.4), (180, 164, 144), flat=True, outline=0)
    s.paint(s.poly([(66, 170), (104, 160), (112, 280), (76, 266)]), (80, 68, 60), bevel=14)
    s.paint(s.poly([(234, 170), (196, 160), (188, 280), (224, 266)]), (80, 68, 60), bevel=14)
    s.paint(s.poly([(84, 66), (70, 20), (116, 50)]), (90, 76, 66), bevel=8)
    s.paint(s.poly([(216, 66), (230, 20), (184, 50)]), (90, 76, 66), bevel=8)
    s.paint(s.ell((60, 30, 240, 190)), B, bevel=30, spec=(86, 36, 150, 80), spec_a=0.25)
    s.paint(s.ell((80, 56, 220, 184)), (236, 226, 210), bevel=18, outline=0.2)
    calm_eye(s, 120, 114, 22, 22, (196, 130, 30), e, (96, 82, 72))
    calm_eye(s, 180, 114, 22, 22, (196, 130, 30), e, (96, 82, 72))
    s.paint(s.ring((92, 86, 148, 142), 4), GOLD, bevel=2, outline=0.3, spec=(96, 88, 120, 100))
    s.paint(s.ring((152, 86, 208, 142), 4), GOLD, bevel=2, outline=0.3, spec=(156, 88, 180, 100))
    s.paint(s.line([(148, 112), (152, 112)], 4), GOLD, flat=True, outline=0)
    s.paint(s.poly([(140, 140), (160, 140), (150, 164)]), (214, 160, 60), bevel=5)


# ---------------------------------------------------------------- 3) Kartal
def kartal(s, e):
    shoulders_suit(s)
    s.paint(s.poly([(96, 210), (110, 170), (190, 170), (204, 210), (150, 236)]), (110, 72, 44), bevel=12)
    feathers = [s.ell((66, 40, 234, 200))]
    for k in range(7):
        x = 84 + k * 22
        feathers.append(s.poly([(x - 14, 180), (x + 14, 180), (x, 214)]))
    s.paint(s.union(*feathers), (242, 240, 234), bevel=26, spec=(90, 50, 160, 96), spec_a=0.2, outline=0.35)
    # gaga
    s.paint(s.poly([(146, 124), (200, 128), (214, 150), (198, 148), (188, 162), (146, 158)]), (232, 176, 40), bevel=10, spec=(152, 126, 190, 136))
    s.paint(s.line([(156, 150), (200, 150)], 2.2), (160, 110, 20), flat=True, outline=0)
    calm_eye(s, 132, 108, 14, 11, (190, 130, 20), e, (200, 196, 186))
    s.paint(s.poly([(108, 92), (156, 90), (152, 100), (112, 102)]), (196, 192, 182), bevel=4, outline=0.3)


# ---------------------------------------------------------------- 4) Avukat Bey
def avukat_bey(s, e):
    shoulders_suit(s)
    SK = (236, 196, 164)
    s.paint(s.rr((128, 170, 172, 214), 12), (214, 172, 140), bevel=6, outline=0.2)
    s.paint(s.ell((72, 86, 96, 132)), SK, bevel=6); s.paint(s.ell((204, 86, 228, 132)), SK, bevel=6)
    s.paint(s.ell((84, 30, 216, 194)), SK, bevel=26, spec=(100, 44, 150, 90), spec_a=0.25)
    HAIR = (48, 40, 36)
    s.paint(s.union(s.chord((80, 18, 220, 120), 180, 360), s.poly([(80, 70), (86, 46), (150, 30), (212, 46), (220, 74), (196, 56), (110, 54)])), HAIR,
            bevel=12, spec=(110, 24, 170, 40), spec_a=0.25)
    s.paint(s.poly([(82, 70), (90, 70), (92, 104), (84, 100)]), (150, 146, 142), bevel=3, outline=0)
    s.paint(s.poly([(218, 70), (210, 70), (208, 104), (216, 100)]), (150, 146, 142), bevel=3, outline=0)
    calm_eye(s, 124, 108, 11, 8, (80, 60, 44), e, SK)
    calm_eye(s, 176, 108, 11, 8, (80, 60, 44), e, SK)
    s.paint(s.line([(108, 92), (138, 90)], 4), HAIR, flat=True, outline=0)
    s.paint(s.line([(162, 90), (192, 92)], 4), HAIR, flat=True, outline=0)
    s.paint(s.rr((104, 96, 144, 122), 6), (0, 0, 0), flat=True, outline=0, alpha=0.0)
    s.paint(s.union(s.cut(s.rr((102, 94, 146, 124), 7), s.rr((106, 98, 142, 120), 5)),
                    s.cut(s.rr((154, 94, 198, 124), 7), s.rr((158, 98, 194, 120), 5)),
                    s.line([(146, 106), (154, 106)], 3)), (40, 36, 40), flat=True, outline=0)
    s.paint(s.poly([(146, 118), (154, 118), (158, 140), (142, 140)]), (222, 180, 148), bevel=4, outline=0)
    calm_mouth(s, 150, 158, 30, (150, 80, 70), e)


# ---------------------------------------------------------------- 5) Avukat Hanım
def avukat_hanim(s, e):
    SK = (240, 204, 176)
    HAIR = (60, 40, 34)
    s.paint(s.rr((80, 70, 220, 214), 50), HAIR, bevel=16)
    shoulders_suit(s, tie=None, shirt=IVORY)
    s.paint(s.ell((176, 236, 196, 256)), GOLD, bevel=4, spec=(178, 238, 186, 244))
    s.paint(s.rr((130, 170, 170, 214), 12), (220, 180, 150), bevel=6, outline=0.2)
    s.paint(s.ell((86, 34, 214, 192)), SK, bevel=26, spec=(100, 44, 150, 90), spec_a=0.25)
    s.paint(s.ell((122, 0, 178, 50)), HAIR, bevel=12, spec=(130, 6, 150, 18))
    s.paint(s.union(s.chord((82, 22, 218, 130), 180, 360), s.poly([(84, 92), (96, 50), (150, 34), (204, 50), (216, 92), (198, 66), (150, 58), (100, 72)])), HAIR,
            bevel=12, spec=(110, 28, 170, 44), spec_a=0.25)
    s.paint(s.ell((80, 124, 94, 138)), WHITE, bevel=4, spec=(82, 125, 88, 130))
    s.paint(s.ell((206, 124, 220, 138)), WHITE, bevel=4, spec=(208, 125, 214, 130))
    calm_eye(s, 124, 112, 11, 8, (90, 60, 40), e, SK)
    calm_eye(s, 176, 112, 11, 8, (90, 60, 40), e, SK)
    s.paint(s.line([(110, 96), (138, 94)], 3.4), HAIR, flat=True, outline=0)
    s.paint(s.line([(162, 94), (190, 96)], 3.4), HAIR, flat=True, outline=0)
    s.paint(s.poly([(146, 122), (154, 122), (157, 142), (143, 142)]), (226, 186, 156), bevel=4, outline=0)
    calm_mouth(s, 150, 160, 28, (176, 70, 76), e)
    s.soft_spot((100, 132, 120, 144), (240, 150, 140), 4, 0.25)
    s.soft_spot((180, 132, 200, 144), (240, 150, 140), 4, 0.25)


# ---------------------------------------------------------------- 6) Adalet Amblemi
def _leaf(cx, cy, ang, L=20, W=8):
    pts = []
    for k in range(14):
        t = 2 * math.pi * k / 14
        x, y = L * math.cos(t), W * math.sin(t)
        pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
    return pts


def amblem(s, e):
    R, C = 122, (150, 150)
    leaves = []
    for side in (-1, 1):
        for k in range(9):
            a = math.radians(95 + k * 15) if side < 0 else math.radians(85 - k * 15)
            x, y = C[0] + R * math.cos(a), C[1] + R * math.sin(a)
            tang = a + (math.pi / 2 if side > 0 else -math.pi / 2)
            off = 0.5 if k % 2 else -0.5
            leaves.append(s.poly(_leaf(x + 10 * math.cos(a) * off, y + 10 * math.sin(a) * off, tang + off * 0.6)))
    s.paint(s.union(*leaves), GOLD, bevel=5, outline=0.35, spec=(40, 120, 100, 200), spec_a=0.2)
    s.paint(s.poly([(70, 50), (150, 22), (230, 50), (222, 170), (150, 262), (78, 170)]), NAVY, bevel=24, spec=(84, 50, 150, 110), spec_a=0.25)
    s.paint(s.poly([(84, 60), (150, 36), (216, 60), (209, 166), (150, 246), (91, 166)]), NAVY_L, bevel=14, outline=0.2)
    s.paint(s.rr((146, 70, 154, 204), 3), GOLD_L, bevel=3)
    s.paint(s.rr((96, 84, 204, 92), 3), GOLD_L, bevel=3)
    s.paint(s.ell((142, 60, 158, 76)), GOLD_L, bevel=3)
    for cx in (106, 194):
        s.paint(s.line([(cx, 90), (cx - 18, 140)], 1.6), GOLD_L, flat=True, outline=0)
        s.paint(s.line([(cx, 90), (cx + 18, 140)], 1.6), GOLD_L, flat=True, outline=0)
        s.paint(s.chord((cx - 26, 124, cx + 26, 156), 0, 180), GOLD_L, bevel=6)
    s.paint(s.poly([(126, 206), (174, 206), (164, 196), (136, 196)]), GOLD_L, bevel=3)


KINDS = {"aslan": ("Adalet Aslanı", aslan), "baykus": ("Bilge Baykuş", baykus), "kartal": ("Hukuk Kartalı", kartal),
         "bey": ("Avukat Bey", avukat_bey), "hanim": ("Avukat Hanım", avukat_hanim), "amblem": ("Adalet Amblemi", amblem)}


@lru_cache(maxsize=64)
def prestige(kind, expr="normal", size=300):
    s = Soft(300, 320, k=3)
    KINDS[kind][1](s, expr)
    return s.image(size)


def badge(kind, size=420, expr="normal"):
    """Lacivert zemin + altın halkalı rozet içinde portre."""
    from PIL import Image, ImageDraw
    s = Soft(340, 340, k=3)
    s.paint(s.ell((10, 10, 330, 330)), GOLD, bevel=14, spec=(40, 20, 170, 80), spec_a=0.35)
    s.paint(s.ell((24, 24, 316, 316)), NAVY, bevel=24, outline=0.3)
    s.paint(s.ring((34, 34, 306, 306), 2), GOLD_L, flat=True, outline=0)
    bg = s.image(size)
    por = prestige(kind, expr, int(size * 0.74))
    mask = Image.new("L", bg.size, 0)
    ImageDraw.Draw(mask).ellipse([size * 24 / 340 + 2, size * 24 / 340 + 2, size * 316 / 340 - 2, size * 316 / 340 - 2], fill=255)
    layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    layer.alpha_composite(por, ((size - por.width) // 2, int(size * 0.92) - por.height))
    a = Image.fromarray(__import__("numpy").minimum(__import__("numpy").asarray(layer.getchannel("A")), __import__("numpy").asarray(mask)))
    layer.putalpha(a)
    bg.alpha_composite(layer)
    return bg
