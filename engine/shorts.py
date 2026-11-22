"""Dikey (9:16) kısa video şablonu: başlık + orta görsel + karaoke altyazı + maskot + üst sayaç."""
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from .core import (INK, RED, WHITE, FPS, out_back, out_cubic, place, place_anim, prog, punch_zoom, shake,
                   text_sprite, upper_tr, vignette_bg)
from .components import Captions, draw_mascot

W, H = 1080, 1920


@dataclass
class Beat:
    dur: float
    title: Tuple[str, str]               # (siyah satır, kırmızı satır)
    caption: str                         # *vurgu* destekli
    visual: Optional[Callable] = None    # visual(base, t, dur, cx, cy)
    mascot: str = "normal"
    sfx: List[Tuple[float, str]] = field(default_factory=list)  # sahne-yerel
    punch: bool = False                  # girişte zoom + sarsıntı
    top: Optional[Callable] = None       # üst sayaç pill çizimi: top(base, t_global)


class Short:
    def __init__(self, beats, top=None, voice=None):
        """voice: TTS dosyası (sahneler arası ~1 sn sessizlikli). Verilirse sahne süreleri sese kilitlenir."""
        self.voice, self.voice_offset = voice, 0.0
        spans = None
        if voice:
            from .voice import split_segments, fit_durations
            segs = split_segments(voice)
            if len(segs) != len(beats):
                raise ValueError(f"Seste {len(segs)} bölüm bulundu, senaryoda {len(beats)} sahne var")
            durs, self.voice_offset = fit_durations(segs, None)
            for b, d in zip(beats, durs):
                b.dur = d
            spans = [b_ - a_ for a_, b_ in segs]
        self.beats = beats
        self.top = top
        self.starts = []
        acc = 0.0
        for b in beats:
            self.starts.append(acc)
            acc += b.dur
        self.duration = acc
        # altyazı: ses varsa konuşma süresine, yoksa sahne süresine yayılır
        self.caps = []
        for k, b in enumerate(beats):
            if spans:
                self.caps.append(Captions(b.caption, 0, spans[k] + 0.15, lead=0.0, tail=0.0, max_chars=19))
            else:
                self.caps.append(Captions(b.caption, 0, b.dur, lead=0.0 if k == 0 else 0.1, max_chars=19))

    # ---------------------------------------------------------- ses olayları
    def events(self):
        ev = []
        for i, (b, s) in enumerate(zip(self.beats, self.starts)):
            if i > 0:
                ev.append((s - 0.08, "whoosh", 1.0))
            if b.punch:
                ev.append((s, "impact", 1.0))
            ev.append((s + 0.02, "pop", 0.8))
            for ts in self.caps[i].word_starts():
                if not self.voice:
                    ev.append((s + ts, "tick", 0.5))
            for ts, name in b.sfx:
                ev.append((s + ts, name, 1.0))
        return ev

    # ---------------------------------------------------------- kare
    def frame(self, t):
        i = max(k for k, s in enumerate(self.starts) if s <= t) if t >= 0 else 0
        b, s = self.beats[i], self.starts[i]
        lt = t - s
        img = vignette_bg(W, H).copy()
        first = i == 0

        # başlık
        l1, l2 = b.title
        sz1 = 92
        while True:
            t1 = text_sprite(upper_tr(l1), "black", sz1, INK)
            if t1.width <= W - 110 or sz1 <= 50:
                break
            sz1 -= 6
        t2 = None
        if l2:
            sz = 112
            while sz > 48:
                t2 = text_sprite(upper_tr(l2), "black", sz, RED)
                if t2.width <= W - 110:
                    break
                sz -= 6
        x0, y0 = 62, 250
        if first and lt < 0.4:
            place(img, t1, x0, y0, anchor="tl")
            if t2:
                place(img, t2, x0, y0 + t1.height + 4, anchor="tl")
        else:
            place_anim(img, t1, x0 + t1.width / 2, y0 + t1.height / 2, lt, b.dur, "left", 0.0, 0.32)
            if t2:
                place_anim(img, t2, x0 + t2.width / 2, y0 + t1.height + 4 + t2.height / 2, lt, b.dur, "pop", 0.08, 0.38)

        # görsel
        if b.visual:
            b.visual(img, lt, b.dur, 540, 900)

        # altyazı
        self.caps[i].draw(img, 540, 1365, lt, size=60)

        # maskot
        if getattr(self, "live", None):
            self.live.draw(img, t)          # canlı maskot: konuşur, yer değiştirir
        else:
            draw_mascot(img, 540, 1610, t, b.mascot, 210, hop_t=0.0 if lt < 0.5 else None)

        # üst sayaç
        if self.top:
            self.top(img, t)

        # ilerleme çubuğu
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 12], fill=(0, 0, 0, 25))
        d.rectangle([0, 0, int(W * t / self.duration), 12], fill=RED)

        # vuruş efekti
        if b.punch:
            z = 1 + 0.06 * (1 - out_cubic(prog(lt, 0, 0.35)))
            dx, dy = shake(lt, 0.0, 0.3, 16)
            img = punch_zoom(img, z, 540 + dx, 960 + dy)
        return img
