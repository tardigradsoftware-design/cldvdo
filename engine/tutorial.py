"""Yatay (16:9) adım adım anlatım şablonu: tarayıcı simülasyonu, kamera zoom, imleç, tuş görselleştirici."""
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable, List, Optional, Tuple

from PIL import Image, ImageDraw

from .core import (INK, RED, WHITE, SS, canvas, clamp, dtext, finish, font, in_out_cubic, lerp, out_back,
                   pill, place, prog, vignette_bg)
from .components import Captions, draw_mascot, keycap

W, H = 1920, 1080

# tarayıcı penceresi (dünya koordinatı)
BX, BY, BW, BH = 80, 118, 1760, 812
TOP = 84                       # sekme + adres çubuğu yüksekliği
CX0, CY0 = BX + 6, BY + TOP    # sayfa içeriğinin dünya ofseti
CW, CH = BW - 12, BH - TOP - 6


def page_to_world(px, py):
    return CX0 + px, CY0 + py


@lru_cache(maxsize=64)
def browser_chrome(url, focus, tab_title):
    im, d = canvas(BW + 14, BH + 14)
    S = SS
    d.rounded_rectangle([14 * S, 14 * S, (BW + 14) * S, (BH + 14) * S], 22 * S, fill=INK)
    d.rounded_rectangle([0, 0, BW * S, BH * S], 22 * S, fill=INK)
    d.rounded_rectangle([5 * S, 5 * S, (BW - 5) * S, (BH - 5) * S], 18 * S, fill=(232, 232, 232, 255))
    for k, c in enumerate([(255, 95, 86, 255), (255, 189, 46, 255), (39, 201, 63, 255)]):
        d.ellipse([(28 + k * 30) * S, 18 * S, (46 + k * 30) * S, 36 * S], fill=c)
    # sekme
    d.rounded_rectangle([140 * S, 10 * S, 470 * S, 44 * S], 10 * S, fill=WHITE)
    dtext(d, (160, 16), tab_title, "semi", 20, (60, 60, 60, 255))
    # adres çubuğu
    d.rounded_rectangle([20 * S, 48 * S, (BW - 20) * S, 78 * S], 10 * S, fill=WHITE,
                        outline=RED if focus else (210, 210, 210, 255), width=(3 if focus else 2) * S)
    d.ellipse([34 * S, 56 * S, 48 * S, 70 * S], outline=(120, 120, 120, 255), width=2 * S)
    dtext(d, (62, 51), url if url else "Ara veya adres yaz", "semi", 21, (40, 40, 40, 255) if url else (160, 160, 160, 255))
    if focus:
        x = 62 + font("semi", 21 * SS).getlength(url) / SS + 2
        d.rectangle([x * S, 52 * S, (x + 2) * S, 74 * S], fill=INK)
    d.rectangle([6 * S, TOP * S, (BW - 6) * S, (BH - 6) * S], fill=WHITE)
    return finish(im)


def draw_browser(world, url, page_spr, focus=False, tab="e-Devlet Kapısı", scale=1.0, alpha=1.0):
    chrome = browser_chrome(url, focus, tab)
    if scale >= 0.999 and alpha >= 0.999:
        world.alpha_composite(chrome, (BX, BY))
        if page_spr is not None:
            world.alpha_composite(page_spr, (CX0, CY0))
    else:
        tmp = chrome.copy()
        if page_spr is not None:
            tmp.alpha_composite(page_spr, (6, TOP))
        place(world, tmp, BX + BW / 2, BY + BH / 2, scale=scale, alpha=alpha)


def camera(img, z, cx, cy):
    if z <= 1.001:
        return img
    cw, ch = W / z, H / z
    x0 = clamp(cx - cw / 2, 0, W - cw)
    y0 = clamp(cy - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def cam_path(t, keys):
    """keys: [(t, z, cx, cy)] yumuşak geçiş."""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            k = in_out_cubic((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(lerp(x, y, k) for x, y in zip(a[1:], b[1:]))
    return keys[-1][1:]


@dataclass
class Seg:
    dur: float
    draw: Callable                         # draw(world, t, dur) -> dict(cam=(z,cx,cy), keys=[(t,label)], mascot=expr)
    captions: List[str] = field(default_factory=list)
    chapter: Optional[Tuple[str, str]] = None   # ("ADIM 1/4", "e-Devlet'e gir")
    sfx: List[Tuple[float, str]] = field(default_factory=list)
    mascot: str = "normal"


class Tutorial:
    def __init__(self, segs):
        self.segs = segs
        self.starts = []
        acc = 0.0
        for s in segs:
            self.starts.append(acc)
            acc += s.dur
        self.duration = acc
        # altyazılar: segment içine eşit dağıt (kelime sayısına göre ağırlıklı)
        self.caps = []
        for s in segs:
            caps = []
            if s.captions:
                wc = [len(c.split()) + 1 for c in s.captions]
                tot = sum(wc)
                acc = 0.0
                for c, n in zip(s.captions, wc):
                    d = s.dur * n / tot
                    caps.append(Captions(c, acc, d, lead=0.05, tail=0.12, max_chars=26, max_words=4))
                    acc += d
            self.caps.append(caps)
        self._keylog = {}

    def events(self):
        ev = []
        for i, (s, st) in enumerate(zip(self.segs, self.starts)):
            if i > 0:
                ev.append((st - 0.08, "whoosh", 0.8))
            for ts, name in s.sfx:
                ev.append((st + ts, name, 1.0))
        return ev

    def frame(self, t):
        i = max(k for k, s in enumerate(self.starts) if s <= t)
        seg, st = self.segs[i], self.starts[i]
        lt = t - st
        world = vignette_bg(W, H).copy()
        info = seg.draw(world, lt, seg.dur) or {}
        z, cx, cy = info.get("cam", (1.0, W / 2, H / 2))
        img = camera(world, z, cx, cy)

        # tuş görselleştirici
        keys = info.get("keys", [])
        recent = [(kt, lab) for kt, lab in keys if 0 <= lt - kt < 0.6]
        if recent:
            x = 110
            for kt, lab in recent[-5:]:
                cap = keycap(lab, 34)
                a = 1 - clamp((lt - kt - 0.4) / 0.2)
                sc = out_back(clamp((lt - kt) / 0.12)) if lt - kt < 0.12 else 1.0
                place(img, cap, x + cap.width / 2, 905, scale=sc, alpha=a)
                x += cap.width + 8

        # bölüm etiketi
        if seg.chapter:
            a, b = seg.chapter
            p1 = pill(a, "black", 30, WHITE, RED, pad=(18, 9), shadow=4)
            p2 = pill(b, "black", 30, INK, WHITE, border=3, pad=(18, 9), shadow=4)
            k = out_back(clamp(lt / 0.35)) if (i == 0 or self.segs[i - 1].chapter != seg.chapter) else 1.0
            place(img, p1, 80 + p1.width / 2, 58, scale=k)
            place(img, p2, 80 + p1.width + 10 + p2.width / 2, 58, scale=k)

        # altyazı
        for c in self.caps[i]:
            c.draw(img, W / 2, 1012, lt, size=46)

        # maskot
        draw_mascot(img, 1810, 960, t, info.get("mascot", seg.mascot), 150)

        # ilerleme
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 8], fill=(0, 0, 0, 25))
        d.rectangle([0, 0, int(W * t / self.duration), 8], fill=RED)
        return img
