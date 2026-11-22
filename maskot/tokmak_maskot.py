"""
TOKMAK — kanal maskotu (bağımsız dosya, sadece Pillow gerekir: pip install pillow)

Kullanım:
    from tokmak_maskot import tokmak, IFADELER, POZLAR
    img = tokmak("mutlu", poz="selam", boyut=300)       # PIL RGBA görsel (şeffaf arka plan)
    img.save("tokmak_mutlu.png")

    # Göz kırpma animasyonu için: tokmak("normal", kirp=True)
    # Tüm ifadeleri PNG olarak dışa aktar:
    #   python3 tokmak_maskot.py cikti_klasoru

İfadeler (IFADELER): normal, mutlu, kahkaha, saskin, kizgin, uzgun, goz_kirp,
                     dusunceli, ciddi, endiseli, heyecanli, uykulu
Pozlar   (POZLAR)  : selam (sağ kol yukarıda), isaret (sağa gösterir),
                     kutlama (iki kol yukarıda), duz (kollar aşağıda)

Önerilen kullanım (videoda duyguya göre):
    risk / tehlike  -> saskin, endiseli      haksızlık   -> kizgin
    çözüm / müjde   -> mutlu, kahkaha        kural / adım -> ciddi + isaret
    soru            -> dusunceli             kötü haber  -> uzgun
    "yoruma yaz"    -> goz_kirp + selam      başarı      -> heyecanli + kutlama
"""
import math
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

SS = 2  # süper örnekleme (pürüzsüz kenar)

INK = (17, 17, 17, 255)
WHITE = (255, 255, 255, 255)
WOOD = (166, 104, 56, 255)
WOOD_L = (196, 130, 76, 255)
WOOD_D = (122, 74, 38, 255)
GOLD = (246, 190, 46, 255)
BLUSH = (255, 150, 140, 255)
MOUTH = (120, 30, 30, 255)
TONGUE = (235, 110, 120, 255)
TEAR = (90, 170, 245, 255)
RED = (232, 52, 46, 255)

IFADELER = ["normal", "mutlu", "kahkaha", "saskin", "kizgin", "uzgun", "goz_kirp",
            "dusunceli", "ciddi", "endiseli", "heyecanli", "uykulu"]
POZLAR = ["selam", "isaret", "kutlama", "duz"]

_FONT_ADAYLARI = [
    "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf",
]


def _font(size):
    for f in _FONT_ADAYLARI:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


class _P:
    """300x380 birimlik çizim alanını piksele çeviren yardımcı."""

    def __init__(self, d, s):
        self.d, self.s = d, s
        self.ow = max(1, int(6 * s))

    def _p(self, pts):
        return [(x * self.s, y * self.s) for x, y in pts]

    def _b(self, b):
        return [v * self.s for v in b]

    def ell(self, b, fill, ol=True, w=None):
        self.d.ellipse(self._b(b), fill=fill, outline=INK if ol else None, width=(w or self.ow) if ol else 0)

    def rr(self, b, r, fill, ol=True):
        self.d.rounded_rectangle(self._b(b), radius=r * self.s, fill=fill, outline=INK if ol else None,
                                 width=self.ow if ol else 0)

    def poly(self, pts, fill, ol=True):
        p = self._p(pts)
        self.d.polygon(p, fill=fill)
        if ol:
            self.d.line(p + [p[0]], fill=INK, width=self.ow, joint="curve")

    def line(self, pts, fill=INK, w=6):
        self.d.line(self._p(pts), fill=fill, width=int(w * self.s), joint="curve")

    def arc(self, b, a0, a1, fill=INK, w=6):
        self.d.arc(self._b(b), a0, a1, fill=fill, width=int(w * self.s))

    def chord(self, b, a0, a1, fill, ol=True):
        self.d.chord(self._b(b), a0, a1, fill=fill, outline=INK if ol else None, width=self.ow if ol else 0)

    def text(self, xy, s, size, fill=INK):
        self.d.text((xy[0] * self.s, xy[1] * self.s), s, font=_font(int(size * self.s)), fill=fill, anchor="mm")


# ---------------------------------------------------------------- yüz parçaları
def _goz(p, x, y, tip, kirp):
    if kirp and tip not in ("kapali_mutlu", "yildiz"):
        p.line([(x - 11, y + 2), (x + 11, y + 2)], INK, 6)
        return
    if tip == "kapali_mutlu":
        p.arc((x - 13, y - 8, x + 13, y + 16), 200, 340, INK, 6)
    elif tip == "buyuk":
        p.ell((x - 12, y - 16, x + 12, y + 16), WHITE, w=int(5 * p.s))
        p.ell((x - 6, y - 7, x + 6, y + 7), INK, ol=False)
        p.ell((x - 3, y - 6, x + 1, y - 2), WHITE, ol=False)
    elif tip == "yildiz":
        pts = []
        for k in range(10):
            r = 14 if k % 2 == 0 else 6
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        p.poly(pts, GOLD)
    elif tip == "yarim":
        p.ell((x - 8, y - 9, x + 8, y + 11), INK, ol=False)
        p.chord((x - 12, y - 14, x + 12, y + 8), 180, 360, WOOD, ol=False)
        p.line([(x - 12, y - 1), (x + 12, y - 1)], INK, 5)
    elif tip == "yukari":
        p.ell((x - 8, y - 11, x + 8, y + 11), INK, ol=False)
        p.ell((x - 1, y - 9, x + 4, y - 4), WHITE, ol=False)
    elif tip == "asagi":
        p.ell((x - 8, y - 9, x + 8, y + 13), INK, ol=False)
        p.ell((x - 2, y - 2, x + 3, y + 3), WHITE, ol=False)
    else:  # normal
        p.ell((x - 8, y - 11, x + 8, y + 11), INK, ol=False)
        p.ell((x - 2, y - 7, x + 3, y - 2), WHITE, ol=False)


def _kas(p, lx, rx, y, tip):
    if tip == "kizgin":
        p.line([(lx - 14, y - 6), (lx + 12, y + 4)], INK, 7)
        p.line([(rx + 14, y - 6), (rx - 12, y + 4)], INK, 7)
    elif tip == "uzgun":
        p.line([(lx - 13, y + 2), (lx + 11, y - 6)], INK, 6)
        p.line([(rx + 13, y + 2), (rx - 11, y - 6)], INK, 6)
    elif tip == "kalkik":
        p.arc((lx - 14, y - 16, lx + 14, y + 4), 200, 340, INK, 6)
        p.arc((rx - 14, y - 16, rx + 14, y + 4), 200, 340, INK, 6)
    elif tip == "tek_kalkik":
        p.line([(lx - 13, y), (lx + 11, y - 1)], INK, 6)
        p.arc((rx - 14, y - 18, rx + 14, y + 2), 200, 340, INK, 6)
    elif tip == "duz":
        p.line([(lx - 13, y - 2), (lx + 12, y - 2)], INK, 7)
        p.line([(rx - 12, y - 2), (rx + 13, y - 2)], INK, 7)
    else:
        p.line([(lx - 13, y), (lx + 11, y - 3)], INK, 6)
        p.line([(rx - 11, y - 3), (rx + 13, y)], INK, 6)


def _konus(p, x, y, seviye, ifade):
    """Konuşurken ağız: seviye 1..3 (sesin gücüne göre açıklık). Duyguya göre biçim değişir."""
    h = (4, 9, 15)[seviye - 1]
    if ifade in ("mutlu", "kahkaha", "heyecanli", "goz_kirp"):
        w = 16 + seviye * 2
        p.chord((x - w, y - 8, x + w, y + 4 + h * 0.95), 0, 180, MOUTH)
        if seviye > 1:
            p.chord((x - w * 0.55, y + h * 0.3, x + w * 0.55, y + 2 + h * 0.95), 0, 180, TONGUE, ol=False)
    elif ifade == "kizgin":
        w = 17
        p.rr((x - w, y - 4, x + w, y + 6 + h), 5, MOUTH)
        p.rr((x - w + 3, y - 2, x + w - 3, y + 4), 2, WHITE, ol=False)
    elif ifade in ("uzgun", "endiseli"):
        w = 9 + seviye * 2
        p.ell((x - w, y - 2, x + w, y + 4 + h), MOUTH)
    else:
        w = 11 + seviye * 3
        p.ell((x - w, y - 4, x + w, y + 2 + h), MOUTH)
        if seviye > 1:
            p.chord((x - w * 0.6, y + h * 0.35, x + w * 0.6, y + 2 + h), 0, 180, TONGUE, ol=False)


def _agiz(p, x, y, tip):
    if tip == "gulumse":
        p.arc((x - 14, y - 10, x + 14, y + 8), 30, 150, INK, 6)
    elif tip == "acik_gul":
        p.chord((x - 18, y - 12, x + 18, y + 14), 0, 180, MOUTH)
        p.chord((x - 10, y + 2, x + 10, y + 14), 0, 180, TONGUE, ol=False)
    elif tip == "kahkaha":
        p.chord((x - 24, y - 16, x + 24, y + 22), 0, 180, MOUTH)
        p.chord((x - 14, y + 4, x + 14, y + 22), 0, 180, TONGUE, ol=False)
        p.rr((x - 16, y - 2, x + 16, y + 4), 2, WHITE, ol=False)
    elif tip == "o":
        p.ell((x - 9, y - 6, x + 9, y + 14), MOUTH)
    elif tip == "duz":
        p.line([(x - 12, y + 2), (x + 12, y + 2)], INK, 6)
    elif tip == "uzgun":
        p.arc((x - 14, y, x + 14, y + 20), 200, 340, INK, 6)
    elif tip == "kizgin":
        p.rr((x - 16, y - 4, x + 16, y + 10), 4, WHITE)
        p.line([(x - 16, y + 3), (x + 16, y + 3)], INK, 3)
    elif tip == "dalgali":
        p.line([(x - 15, y + 4), (x - 8, y - 1), (x, y + 4), (x + 8, y - 1), (x + 15, y + 4)], INK, 5)
    elif tip == "yamuk":
        p.arc((x - 6, y - 8, x + 18, y + 8), 30, 150, INK, 6)


# ifade -> (sol göz, sağ göz, kaş, ağız, ekstra)
_IFADE = {
    "normal": ("normal", "normal", "normal", "gulumse", None),
    "mutlu": ("kapali_mutlu", "kapali_mutlu", "normal", "acik_gul", None),
    "kahkaha": ("kapali_mutlu", "kapali_mutlu", "kalkik", "kahkaha", "parilti"),
    "saskin": ("buyuk", "buyuk", "kalkik", "o", "unlem"),
    "kizgin": ("normal", "normal", "kizgin", "kizgin", "ofke"),
    "uzgun": ("asagi", "asagi", "uzgun", "uzgun", "gozyasi"),
    "goz_kirp": ("normal", "kapali_mutlu", "normal", "acik_gul", None),
    "dusunceli": ("yukari", "yukari", "tek_kalkik", "yamuk", "soru"),
    "ciddi": ("normal", "normal", "duz", "duz", None),
    "endiseli": ("buyuk", "buyuk", "uzgun", "dalgali", "ter"),
    "heyecanli": ("yildiz", "yildiz", "kalkik", "kahkaha", "parilti"),
    "uykulu": ("yarim", "yarim", "duz", "duz", "zzz"),
}


def _ekstra(p, tip):
    if tip == "unlem":
        p.text((272, 54), "!", 54, RED)
    elif tip == "soru":
        p.text((270, 56), "?", 54, INK)
    elif tip == "ofke":
        for a in (0, 90, 180, 270):
            r = math.radians(a + 45)
            p.line([(262 + 6 * math.cos(r), 58 + 6 * math.sin(r)), (262 + 18 * math.cos(r), 58 + 18 * math.sin(r))], RED, 6)
    elif tip == "gozyasi":
        p.poly([(126, 146), (120, 162), (126, 170), (132, 162)], TEAR, ol=False)
        p.ell((119, 158, 133, 172), TEAR, ol=False)
    elif tip == "ter":
        p.poly([(232, 70), (224, 88), (232, 96), (240, 88)], TEAR, ol=True)
        p.ell((224, 82, 240, 98), TEAR, ol=False)
    elif tip == "parilti":
        for (x, y, r) in ((40, 58, 12), (262, 50, 10), (24, 110, 7)):
            p.poly([(x, y - r), (x + r * .3, y - r * .3), (x + r, y), (x + r * .3, y + r * .3), (x, y + r),
                    (x - r * .3, y + r * .3), (x - r, y), (x - r * .3, y - r * .3)], GOLD, ol=False)
    elif tip == "zzz":
        p.text((246, 62), "z", 26, (80, 80, 100, 255))
        p.text((266, 40), "Z", 34, (80, 80, 100, 255))


# ---------------------------------------------------------------- gövde
def _kol(p, x0, y0, x1, y1):
    p.line([(x0, y0), (x1, y1)], INK, 9)
    p.ell((x1 - 12, y1 - 12, x1 + 12, y1 + 12), WOOD)


def _ciz(p, ifade, poz, kirp, konus=0):
    # gölge
    p.ell((70, 354, 230, 368), (0, 0, 0, 38), ol=False)
    # bacaklar
    for x in (132, 168):
        p.line([(x, 292), (x, 338)], INK, 9)
    p.rr((132 - 22, 334, 132 + 12, 352), 8, INK, ol=False)
    p.rr((168 - 12, 334, 168 + 22, 352), 8, INK, ol=False)
    # sap
    p.rr((138, 186, 162, 300), 10, WOOD)
    # kollar
    if poz == "selam":
        _kol(p, 52, 140, 18, 180); _kol(p, 248, 140, 282, 104)
    elif poz == "isaret":
        _kol(p, 52, 140, 18, 180)
        p.line([(248, 140), (288, 140)], INK, 9)
        p.ell((276, 128, 300, 152), WOOD)
        p.rr((292, 134, 300, 146), 3, WOOD)
    elif poz == "kutlama":
        _kol(p, 52, 140, 16, 96); _kol(p, 248, 140, 284, 96)
    else:  # duz
        _kol(p, 52, 140, 22, 190); _kol(p, 248, 140, 278, 190)
    # baş
    p.rr((46, 88, 254, 192), 34, WOOD)
    p.rr((46, 96, 254, 120), 10, WOOD_L, ol=False)
    for x in (82, 218):
        p.line([(x, 92), (x, 188)], GOLD, 8)
    p.rr((36, 82, 70, 198), 14, WOOD_D)
    p.rr((230, 82, 264, 198), 14, WOOD_D)
    # yüz
    gl, gr, kas, agiz, ek = _IFADE[ifade]
    _kas(p, 126, 174, 106, kas)
    _goz(p, 126, 132, gl, kirp)
    _goz(p, 174, 132, gr, kirp)
    if ifade not in ("kizgin", "ciddi"):
        p.ell((86, 148, 102, 158), BLUSH, ol=False)
        p.ell((198, 148, 214, 158), BLUSH, ol=False)
    if konus:
        _konus(p, 150, 166, konus, ifade)
    else:
        _agiz(p, 150, 166, agiz)
    _ekstra(p, ek)


@lru_cache(maxsize=1024)
def tokmak(ifade="normal", poz="selam", boyut=300, kirp=False, konus=0):
    """Tokmak maskotunu şeffaf arka planlı RGBA görsel olarak döndürür.
    konus: 0 = ifadenin kendi ağzı, 1..3 = konuşma ağzı (dudak senkronu için)."""
    if ifade not in _IFADE:
        raise ValueError(f"Bilinmeyen ifade: {ifade}. Seçenekler: {IFADELER}")
    if poz not in POZLAR:
        raise ValueError(f"Bilinmeyen poz: {poz}. Seçenekler: {POZLAR}")
    sx = boyut / 300.0
    w, h = int(boyut * SS * 1.04), int(380 * sx * SS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    _ciz(_P(ImageDraw.Draw(im), SS * sx), ifade, poz, kirp, konus)
    return im.resize((w // SS, h // SS), Image.LANCZOS)


def disa_aktar(klasor="tokmak_png", boyut=600):
    import os
    os.makedirs(klasor, exist_ok=True)
    for i in IFADELER:
        for pz in POZLAR:
            tokmak(i, pz, boyut).save(os.path.join(klasor, f"tokmak_{i}_{pz}.png"))
        tokmak(i, "selam", boyut, kirp=True).save(os.path.join(klasor, f"tokmak_{i}_kirpik.png")) if i in ("normal", "ciddi", "kizgin") else None
    print(f"{klasor}/ klasörüne {len(IFADELER) * len(POZLAR)} PNG yazıldı.")


if __name__ == "__main__":
    disa_aktar(sys.argv[1] if len(sys.argv) > 1 else "tokmak_png")
