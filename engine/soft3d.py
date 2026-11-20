"""Yumuşak 3D (clay/vinyl) görünüm motoru: hacim gölgesi, kenar ışığı, parlama, renkli kontur, zemin gölgesi.
Kullanım:
    s = Soft(300, 380)
    m = s.ell((70, 110, 230, 350)); s.paint(m, (150,110,80))
    img = s.image(size=260)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _shift(a, dx, dy):
    h, w = a.shape
    out = np.zeros_like(a)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = a[ys0:ys1, xs0:xs1]
    return out


class Soft:
    def __init__(self, w, h, k=3):
        self.k = k
        self.W, self.H = int(w * k), int(h * k)
        self.rgb = np.zeros((self.H, self.W, 3), np.float32)
        self.a = np.zeros((self.H, self.W), np.float32)
        self.ground = None

    # ------------------------------------------------------------ maskeler
    def _new(self):
        m = Image.new("L", (self.W, self.H), 0)
        return m, ImageDraw.Draw(m)

    def _b(self, b):
        return [v * self.k for v in b]

    def ell(self, b):
        m, d = self._new(); d.ellipse(self._b(b), fill=255); return m

    def rr(self, b, r):
        m, d = self._new(); d.rounded_rectangle(self._b(b), radius=r * self.k, fill=255); return m

    def poly(self, pts):
        m, d = self._new(); d.polygon([(x * self.k, y * self.k) for x, y in pts], fill=255); return m

    def line(self, pts, w):
        m, d = self._new()
        d.line([(x * self.k, y * self.k) for x, y in pts], fill=255, width=int(w * self.k), joint="curve")
        r = w * self.k / 2
        for x, y in (pts[0], pts[-1]):
            d.ellipse([x * self.k - r, y * self.k - r, x * self.k + r, y * self.k + r], fill=255)
        return m

    def arc(self, b, a0, a1, w):
        m, d = self._new(); d.arc(self._b(b), a0, a1, fill=255, width=int(w * self.k)); return m

    def chord(self, b, a0, a1):
        m, d = self._new(); d.chord(self._b(b), a0, a1, fill=255); return m

    def ring(self, b, w):
        m, d = self._new(); d.ellipse(self._b(b), outline=255, width=int(w * self.k)); return m

    def text(self, xy, s, fnt_path, size, anchor="mm"):
        from PIL import ImageFont
        m, d = self._new()
        d.text((xy[0] * self.k, xy[1] * self.k), s, font=ImageFont.truetype(fnt_path, int(size * self.k)), fill=255, anchor=anchor)
        return m

    @staticmethod
    def union(*ms):
        out = ms[0].copy()
        for m in ms[1:]:
            out = Image.fromarray(np.maximum(np.asarray(out), np.asarray(m)))
        return out

    @staticmethod
    def cut(m, by):
        return Image.fromarray(np.clip(np.asarray(m, np.int16) - np.asarray(by, np.int16), 0, 255).astype(np.uint8))

    @staticmethod
    def inter(m, by):
        return Image.fromarray(np.minimum(np.asarray(m), np.asarray(by)))

    # ------------------------------------------------------------ boyama
    def paint(self, m, color, shade=0.38, hi=0.32, bevel=16, spec=None, spec_a=0.55, outline=0.5, ow=2.2,
              grad=0.12, alpha=1.0, flat=False):
        """m: maske. color: RGB. spec: (x0,y0,x1,y1) parlama elipsi (birim). outline: kontur koyuluğu (0=yok)."""
        k = self.k
        M = np.asarray(m, np.float32) / 255.0
        if M.max() == 0:
            return
        base = np.array(color[:3], np.float32) / 255.0
        col = np.broadcast_to(base, M.shape + (3,)).copy()
        if not flat:
            r = bevel * k
            B = np.asarray(m.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0
            off = int(r * 0.55)
            dark = np.clip(1 - _shift(B, -off, -off), 0, 1) * M      # sağ-alt kenarlar
            light = np.clip(1 - _shift(B, off, off), 0, 1) * M       # sol-üst kenarlar
            ys = np.nonzero(M.max(1))[0]
            y0, y1 = ys.min(), ys.max() + 1
            g = np.zeros(M.shape, np.float32)
            g[y0:y1] = np.linspace(-1, 1, y1 - y0)[:, None]
            col = col * (1 - shade * dark[..., None]) * (1 - grad * g[..., None])
            col = col + (1 - col) * (hi * light[..., None])
        if spec is not None:
            sm = self.ell(spec).filter(ImageFilter.GaussianBlur(4 * k))
            S = np.asarray(sm, np.float32) / 255.0 * M * spec_a
            col = col + (1 - col) * S[..., None]
        if outline > 0:
            er = m.filter(ImageFilter.MinFilter(int(ow * k) * 2 + 1))
            E = np.clip(M - np.asarray(er, np.float32) / 255.0, 0, 1)
            col = col * (1 - outline * E[..., None])
        A = M * alpha
        self.rgb = col * A[..., None] + self.rgb * (1 - A[..., None])
        self.a = A + self.a * (1 - A)

    def soft_spot(self, b, color, blur=6, alpha=0.6, clip=None):
        """Yanak pembesi, ışıltı gibi bulanık lekeler."""
        m = self.ell(b).filter(ImageFilter.GaussianBlur(blur * self.k))
        M = np.asarray(m, np.float32) / 255.0 * alpha
        if clip is not None:
            M *= np.asarray(clip, np.float32) / 255.0
        c = np.array(color[:3], np.float32) / 255.0
        self.rgb = c * M[..., None] + self.rgb * (1 - M[..., None])
        self.a = np.maximum(self.a, M * (self.a > 0))

    def ground_shadow(self, cx, y, w, h=16, alpha=0.28):
        self.ground = (cx, y, w, h, alpha)

    # ------------------------------------------------------------ çıktı
    def image(self, size=None):
        H, W = self.H, self.W
        out = np.zeros((H, W, 4), np.float32)
        if self.ground:
            cx, y, w, h, al = self.ground
            gm = self.ell((cx - w, y - h / 2, cx + w, y + h / 2)).filter(ImageFilter.GaussianBlur(6 * self.k))
            G = np.asarray(gm, np.float32) / 255.0 * al
            out[..., 3] = G
        A = self.a
        out[..., :3] = self.rgb
        out[..., 3] = A + out[..., 3] * (1 - A)
        img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")
        w = self.W // self.k if size is None else size
        h = int(self.H * w / self.W)
        return img.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- yüz yardımcıları
def glossy_eye(s, cx, cy, rx, ry, iris=(120, 80, 40), expr="normal", look=(0, 0)):
    if expr == "happy":
        s.paint(s.arc((cx - rx, cy - ry * 0.4, cx + rx, cy + ry * 1.3), 200, 340, rx * 0.32), (40, 30, 30), flat=True, outline=0)
        return
    sc = 1.15 if expr == "shock" else 1.0
    rx, ry = rx * sc, ry * sc
    s.paint(s.ell((cx - rx, cy - ry, cx + rx, cy + ry)), (255, 255, 255), shade=0.18, hi=0.0, bevel=6, outline=0.35, ow=1.6)
    ir = rx * (0.55 if expr == "shock" else 0.78)
    ix, iy = cx + look[0], cy + ry * 0.12 + look[1]
    s.paint(s.ell((ix - ir, iy - ir * 1.12, ix + ir, iy + ir * 1.12)), iris, shade=0.45, hi=0.15, bevel=5, outline=0.3, ow=1)
    pr = ir * 0.55
    s.paint(s.ell((ix - pr, iy - pr * 1.1, ix + pr, iy + pr * 1.1)), (20, 16, 20), flat=True, outline=0)
    s.paint(s.ell((ix - ir * 0.55, iy - ir * 0.8, ix - ir * 0.05, iy - ir * 0.3)), (255, 255, 255), flat=True, outline=0)
    s.paint(s.ell((ix + ir * 0.25, iy + ir * 0.25, ix + ir * 0.5, iy + ir * 0.5)), (255, 255, 255), flat=True, outline=0, alpha=0.8)


def smile(s, cx, cy, w, expr="normal"):
    if expr == "shock":
        s.paint(s.ell((cx - w * 0.22, cy - w * 0.1, cx + w * 0.22, cy + w * 0.42)), (110, 30, 40), shade=0.3, bevel=4, outline=0.3, ow=1)
        return
    if expr == "happy" or expr == "open":
        m = s.chord((cx - w / 2, cy - w * 0.45, cx + w / 2, cy + w * 0.45), 0, 180)
        s.paint(m, (120, 32, 44), shade=0.3, bevel=4, outline=0.3, ow=1)
        t = s.inter(s.ell((cx - w * 0.28, cy + w * 0.05, cx + w * 0.28, cy + w * 0.6)), m)
        s.paint(t, (240, 110, 120), flat=True, outline=0)
        return
    s.paint(s.arc((cx - w / 2, cy - w * 0.5, cx + w / 2, cy + w * 0.3), 25, 155, max(2.6, w * 0.11)), (60, 30, 30), flat=True, outline=0)
