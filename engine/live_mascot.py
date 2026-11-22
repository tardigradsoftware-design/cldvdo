"""CANLI MASKOT — Tokmak konuşur (dudak senkronu), duygusu cümleye göre değişir, ekranda yer değiştirir.

Kullanım:
    lm = LiveMascot(voice_path, cues, spots, size)
    lm.draw(img, t)
cues  = [(başlangıç_sn, "ifade[:poz]"), ...]   (cümle başına; plan JSON'undaki "mascot" alanlarından gelir)
spots = [(x, y), ...]  maskotun gezineceği noktalar (ekran koordinatı)
Ses yoksa ağız hece ritmiyle (cümle sürelerine göre) yapay olarak oynar.
"""
import math

from .components import _TOKMAK_MAP
from .core import clamp, out_back, place

TEXT_EXTRAS = {"saskin", "dusunceli", "uykulu"}      # yansıtılınca bozulan "!" "?" "z" içeren ifadeler

SPOTS_LONG = [(1755, 850), (165, 810)]
SPOTS_SHORT = [(540, 1615), (200, 1600), (880, 1600), (870, 1060), (210, 1060)]


def _sprite(expr, poz, size, blink, talk):
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "maskot"))
    from tokmak_maskot import tokmak
    return tokmak(_TOKMAK_MAP.get(expr, expr), poz, int(size), blink, talk)


class LiveMascot:
    def __init__(self, cues, spots, size=220, voice=None, duration=None, center_x=None, hop=0.55):
        self.cues = sorted(cues) or [(0.0, "normal")]
        self.spots = spots
        self.size = size
        self.hop = hop
        self.cx = center_x if center_x is not None else sum(x for x, _ in spots) / len(spots)
        self.env = None
        if voice:
            from .voice import envelope
            self.env = envelope(voice)
        self.duration = duration
        # her cue'da yeni nokta (aynı nokta iki kez üst üste gelmez)
        self.pos = []
        for i in range(len(self.cues)):
            self.pos.append(self.spots[i % len(self.spots)])

    # -------------------------------------------------------------- yardımcılar
    def _cue(self, t):
        i = 0
        for k, (s, _) in enumerate(self.cues):
            if s <= t:
                i = k
        return i

    def _talk(self, t, i):
        if self.env is not None:
            k = int(t * 100)
            if k < 0 or k >= len(self.env):
                return 0, 0.0
            e = float(self.env[max(0, k - 2):k + 3].max())
            lvl = 0 if e < 0.18 else 1 if e < 0.42 else 2 if e < 0.65 else 3
            return lvl, e
        # ses yok: hece ritmi (4.5 hece/sn) — cümle başında konuşur, sonuna doğru susar
        s = self.cues[i][0]
        nxt = self.cues[i + 1][0] if i + 1 < len(self.cues) else (self.duration or s + 3)
        if t > nxt - 0.35:
            return 0, 0.0
        ph = math.sin((t - s) * 2 * math.pi * 4.5)
        lvl = 0 if ph < -0.3 else 1 if ph < 0.3 else 2
        return lvl, max(0.0, ph)

    # -------------------------------------------------------------- çizim
    def draw(self, img, t, alpha=1.0):
        if t < 0:
            return
        i = self._cue(t)
        s0, raw = self.cues[i]
        expr, poz = (raw.split(":", 1) + ["selam"])[:2] if ":" in raw else (raw, None)
        x1, y1 = self.pos[i]
        x0, y0 = self.pos[i - 1] if i > 0 else (x1, y1 + 300)
        lt = t - s0
        # yer değiştirme: yay çizerek zıpla
        k = clamp(lt / self.hop)
        e = 0.5 - 0.5 * math.cos(math.pi * k)
        x = x0 + (x1 - x0) * e
        y = y0 + (y1 - y0) * e - math.sin(math.pi * k) * (160 if (x0, y0) != (x1, y1) else 50)
        moving = k < 1
        # ekranın sağındaysa içeriğe (merkeze) dönsün
        right = x > self.cx + 40
        if poz is None:
            poz = "isaret" if (lt < 1.6 and i > 0) else "selam" if lt < 1.2 else "duz"
            if moving:
                poz = "kutlama"
        flip = right and expr not in TEXT_EXTRAS and poz == "isaret"
        if right and expr in TEXT_EXTRAS and poz == "isaret":
            poz = "selam"
        blink = (t % 3.3) < 0.11 or (1.7 < t % 5.9 < 1.8)
        lvl, en = (0, 0.0) if moving else self._talk(t, i)
        spr = _sprite(expr, poz, self.size, blink, lvl)
        if flip:
            from PIL import ImageOps
            spr = ImageOps.mirror(spr)
        # canlılık: nefes, konuşurken baş sallama, duygu değişiminde 'pop'
        bob = math.sin(t * 3.0) * 5 + (en * 6 if lvl else 0)
        sway = math.sin(t * 1.7) * 3 + (math.sin(t * 9) * 2 * en if lvl else 0)
        pop = 1 + 0.14 * (1 - out_back(clamp((lt - self.hop * 0.85) / 0.35), 2.0)) if i > 0 else out_back(clamp(t / 0.5), 1.6)
        sq = 1.0
        if 0.9 < k < 1.0 or (k >= 1 and lt - self.hop < 0.12):
            sq = 0.94     # iniş esnemesi
        if moving:
            sway += (x1 - x0) / 60 * math.sin(math.pi * k)
        place(img, spr, x, y + bob, scale=pop * sq, alpha=alpha, rot=-sway)


def cues_from_times(starts, exprs):
    return [(float(s), e or "normal") for s, e in zip(starts, exprs)]
