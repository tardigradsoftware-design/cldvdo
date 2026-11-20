"""Çekirdek: font, easing, sprite önbelleği, dönüşümlü yapıştırma ve ffmpeg render."""
import math
import os
import subprocess
from functools import lru_cache
from multiprocessing import get_context

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 30
SS = 2  # sprite süper örnekleme (kenar yumuşatma)

# ---------------------------------------------------------------- renkler
INK = (17, 17, 17, 255)
WHITE = (255, 255, 255, 255)
RED = (232, 52, 46, 255)
GREEN = (24, 160, 88, 255)
BLUE = (38, 92, 230, 255)
YELLOW = (255, 204, 41, 255)
GREY = (165, 165, 165, 255)
LIGHT = (244, 244, 244, 255)
SOFT = (226, 226, 226, 255)

# ---------------------------------------------------------------- fontlar
_FONT_DIR = "/usr/share/fonts/opentype/inter"
FONTS = {
    "black": f"{_FONT_DIR}/InterDisplay-Black.otf",
    "xbold": f"{_FONT_DIR}/InterDisplay-ExtraBold.otf",
    "bold": f"{_FONT_DIR}/Inter-Bold.otf",
    "semi": f"{_FONT_DIR}/Inter-SemiBold.otf",
    "med": f"{_FONT_DIR}/Inter-Medium.otf",
    "reg": f"{_FONT_DIR}/Inter-Regular.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
}


@lru_cache(maxsize=256)
def font(name, size):
    return ImageFont.truetype(FONTS[name], int(size))


def upper_tr(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def in_cubic(t):
    t = clamp(t)
    return t ** 3


def in_out_cubic(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def out_back(t, s=2.2):
    t = clamp(t)
    c3 = s + 1
    return 1 + c3 * (t - 1) ** 3 + s * (t - 1) ** 2


def prog(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def path(t, keys, ease=in_out_cubic):
    """keys: [(t, x, y), ...] -> (x, y) yumuşak interpolasyon."""
    if t <= keys[0][0]:
        return keys[0][1], keys[0][2]
    for (t0, x0, y0), (t1, x1, y1) in zip(keys, keys[1:]):
        if t <= t1:
            k = ease((t - t0) / max(1e-6, t1 - t0))
            return lerp(x0, x1, k), lerp(y0, y1, k)
    return keys[-1][1], keys[-1][2]


# ---------------------------------------------------------------- giriş/çıkış animasyonları
def enter_exit(t, dur, kind="pop", t_in=0.0, d_in=0.35, d_out=0.18):
    """(scale, dx, dy, alpha, rot) döndürür. t: sahne-yerel zaman."""
    p = prog(t, t_in, d_in)
    q = prog(t, dur - d_out, d_out)
    scale, dx, dy, alpha, rot = 1.0, 0.0, 0.0, 1.0, 0.0
    if kind == "pop":
        scale = out_back(p) if p < 1 else 1.0
        alpha = clamp(p * 4)
    elif kind == "up":
        dy = (1 - out_cubic(p)) * 80
        alpha = clamp(p * 2.5)
    elif kind == "left":
        dx = (1 - out_back(p, 1.4)) * -160
        alpha = clamp(p * 3)
    elif kind == "right":
        dx = (1 - out_back(p, 1.4)) * 160
        alpha = clamp(p * 3)
    elif kind == "drop":
        dy = (1 - out_back(p, 1.6)) * -140
        rot = (1 - out_cubic(p)) * -8
        alpha = clamp(p * 3)
    elif kind == "stamp":
        scale = lerp(2.2, 1.0, out_cubic(p))
        alpha = clamp(p * 3)
    elif kind == "fade":
        alpha = p
    if q > 0:
        scale *= 1 - 0.35 * in_cubic(q)
        alpha *= 1 - q
    return max(scale, 0.01), dx, dy, alpha, rot


# ---------------------------------------------------------------- sprite yardımcıları
def canvas(w, h):
    """Süper örneklenmiş boş RGBA tuval + çizim nesnesi."""
    im = Image.new("RGBA", (int(w * SS), int(h * SS)), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def finish(im):
    return im.resize((im.width // SS, im.height // SS), Image.LANCZOS)


def place(base, spr, cx, cy, scale=1.0, alpha=1.0, rot=0.0, anchor="c"):
    """Sprite'ı dönüştürüp base üstüne yapıştır. (cx, cy) anchor noktası."""
    if spr is None or alpha <= 0.01 or scale <= 0.01:
        return
    s = spr
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BICUBIC)
    if abs(rot) > 0.05:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = s.getchannel("A").point(lambda v: int(v * alpha))
        s = s.copy()
        s.putalpha(a)
    if anchor == "c":
        x, y = cx - s.width / 2, cy - s.height / 2
    elif anchor == "tl":
        x, y = cx, cy
    elif anchor == "tc":
        x, y = cx - s.width / 2, cy
    elif anchor == "l":
        x, y = cx, cy - s.height / 2
    else:
        x, y = cx, cy
    base.alpha_composite(s, (int(round(x)), int(round(y)))) if x >= 0 and y >= 0 else _paste_clip(base, s, int(round(x)), int(round(y)))


def _paste_clip(base, s, x, y):
    x0, y0 = max(0, -x), max(0, -y)
    if x0 >= s.width or y0 >= s.height:
        return
    s = s.crop((x0, y0, s.width, s.height))
    base.alpha_composite(s, (max(0, x), max(0, y)))


def place_anim(base, spr, cx, cy, t, dur, kind="pop", t_in=0.0, d_in=0.35, rot=0.0, d_out=0.18, scale=1.0, anchor="c"):
    if t < t_in:
        return
    sc, dx, dy, a, r = enter_exit(t, dur, kind, t_in, d_in, d_out)
    place(base, spr, cx + dx, cy + dy, sc * scale, a, rot + r, anchor)


def text_size(txt, f):
    b = f.getbbox(txt)
    return b[2] - b[0], b[3] - b[1], b


# ---------------------------------------------------------------- bileşenler (önbellekli)
@lru_cache(maxsize=2048)
def text_sprite(txt, fname, size, color=INK, stroke=0, stroke_color=WHITE):
    f = font(fname, size * SS)
    w, h, b = text_size(txt, f)
    pad = (stroke + 4) * SS
    im, d = canvas((w + 2 * pad) / SS + 1, (h + 2 * pad) / SS + 1)
    d.text((pad - b[0], pad - b[1]), txt, font=f, fill=color, stroke_width=stroke * SS, stroke_fill=stroke_color)
    return finish(im)


@lru_cache(maxsize=1024)
def pill(txt, fname="black", size=46, fg=WHITE, bg=RED, border=0, pad=(22, 10), radius=None, shadow=0, bc=INK):
    f = font(fname, size * SS)
    w, h, b = text_size(txt, f)
    pw, ph = w / SS + pad[0] * 2, size * 0.78 + pad[1] * 2
    r = ph / 2 if radius is None else radius
    sh = shadow
    im, d = canvas(pw + border * 2 + sh + 2, ph + border * 2 + sh + 2)
    o = border
    if sh:
        d.rounded_rectangle([(o + sh) * SS, (o + sh) * SS, (o + sh + pw) * SS, (o + sh + ph) * SS], r * SS, fill=INK)
    if border:
        d.rounded_rectangle([0, 0, (pw + 2 * o) * SS, (ph + 2 * o) * SS], (r + o) * SS, fill=bc)
    d.rounded_rectangle([o * SS, o * SS, (o + pw) * SS, (o + ph) * SS], r * SS, fill=bg)
    tx = (o + pad[0]) * SS - b[0]
    ty = (o + ph / 2) * SS - (b[1] + b[3]) / 2
    d.text((tx, ty), txt, font=f, fill=fg)
    return finish(im)


def card_base(w, h, fill=WHITE, border=5, radius=18, shadow=10, header=None, header_h=0):
    """Kalın siyah çerçeve + sert gölgeli kart. (im, d, ox, oy) döner: içerik çizimi için."""
    im, d = canvas(w + shadow + 2, h + shadow + 2)
    S = SS
    d.rounded_rectangle([shadow * S, shadow * S, (w + shadow) * S, (h + shadow) * S], radius * S, fill=INK)
    d.rounded_rectangle([0, 0, w * S, h * S], radius * S, fill=INK)
    d.rounded_rectangle([border * S, border * S, (w - border) * S, (h - border) * S], (radius - border) * S, fill=fill)
    if header is not None and header_h:
        d.rounded_rectangle([border * S, border * S, (w - border) * S, (border + header_h) * S], (radius - border) * S, fill=header)
        d.rectangle([border * S, (border + header_h / 2) * S, (w - border) * S, (border + header_h) * S], fill=header)
        d.line([border * S, (border + header_h) * S, (w - border) * S, (border + header_h) * S], fill=INK, width=border * S)
    return im, d


def dtext(d, xy, txt, fname, size, fill=INK, anchor="la"):
    d.text((xy[0] * SS, xy[1] * SS), txt, font=font(fname, size * SS), fill=fill, anchor=anchor)


def rich_line(d, x, y, segments, fname, size, anchor_baseline=False):
    """segments: [(metin, renk), ...] tek satır yan yana. Genişlik döner."""
    f = font(fname, size * SS)
    cx = x * SS
    for txt, col in segments:
        d.text((cx, y * SS), txt, font=f, fill=col)
        cx += f.getlength(txt)
    return (cx / SS) - x


@lru_cache(maxsize=64)
def vignette_bg(w, h, c_center=(250, 250, 250), c_edge=(222, 222, 222)):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (xx - w / 2) / (w / 2)
    dy = (yy - h / 2) / (h / 2)
    r = np.clip(np.sqrt(dx * dx * 0.9 + dy * dy * 0.6), 0, 1.4) / 1.4
    r = r ** 1.6
    out = np.zeros((h, w, 4), np.uint8)
    for i in range(3):
        out[..., i] = (c_center[i] * (1 - r) + c_edge[i] * r).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, "RGBA")


def shake(t, t0, dur=0.25, amp=14):
    p = prog(t, t0, dur)
    if p <= 0 or p >= 1:
        return 0, 0
    k = (1 - p) * amp
    return math.sin(t * 90) * k, math.cos(t * 77) * k


def punch_zoom(img, z, cx=None, cy=None):
    """Tüm kareye zoom (1.0 = yok)."""
    if z <= 1.001:
        return img
    w, h = img.size
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    cw, ch = w / z, h / z
    x0 = clamp(cx - cw / 2, 0, w - cw)
    y0 = clamp(cy - ch / 2, 0, h - ch)
    return img.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


# ---------------------------------------------------------------- render
_RENDER_FN = None


def _frame_bytes(i):
    img = _RENDER_FN(i / FPS)
    return img.convert("RGB").tobytes()


def render(frame_fn, duration, size, out_path, audio_path=None, workers=4, crf=19):
    """frame_fn(t)->PIL.Image ; çok çekirdekli kare üretip ffmpeg'e akıtır."""
    global _RENDER_FN
    _RENDER_FN = frame_fn
    n = int(round(duration * FPS))
    w, h = size
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(FPS), "-i", "-"]
    if audio_path:
        cmd += ["-i", audio_path]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-movflags", "+faststart"]
    if audio_path:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest"]
    cmd += [out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ctx = get_context("fork")
    with ctx.Pool(workers) as pool:
        for k, fb in enumerate(pool.imap(_frame_bytes, range(n), chunksize=4)):
            p.stdin.write(fb)
            if k % (FPS * 5) == 0:
                print(f"  kare {k}/{n}", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg hata verdi")
    return out_path
