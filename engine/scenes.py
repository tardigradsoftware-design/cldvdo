"""Plan → video. Otomatik yönetmenin çıkardığı (ve istenirse elle düzenlenen) planı Tutorial/Short'a çevirir.
Her sahne hareketlidir: kamera her zaman çok hafif kayar (donma olmaz), olaylar cümle başlarına kilitlenir."""
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw

from .core import (BLUE, GREEN, INK, RED, SS, WHITE, YELLOW, canvas, card_base, clamp, dtext, finish, font, lerp,
                   out_back, out_cubic, path, pill, place, place_anim, prog, text_sprite, upper_tr)
from .components import draw_cursor, icon_check, icon_warn, icon_x, stamp
from .tutorial import CX0, CY0, H, W, Seg, Tutorial, draw_browser
from . import portals as P
from .director import WPS, emphasize, key_phrase, kw_chips, wrap, words

GREYT = (110, 110, 110, 255)


def S(v):
    return int(v * SS)


def sdur(s):
    return words(s) / WPS + 0.35


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def drift(t, base=(1.0, W / 2, H / 2)):
    z, cx, cy = base
    return (z * (1.018 + 0.014 * math.sin(t * 0.7)), cx + 14 * math.sin(t * 0.45), cy + 8 * math.cos(t * 0.5))


def overlay(img, rgba, box=None):
    x0, y0, x1, y1 = box or (0, 0, img.width, img.height)
    img.alpha_composite(Image.new("RGBA", (int(x1 - x0), int(y1 - y0)), rgba), (int(x0), int(y0)))


def typing(t, t0, text, cps):
    return int(clamp((t - t0) * cps, 0, len(text)))


# ================================================================ ortak çizimler
@lru_cache(maxsize=1)
def phone_frame():
    w, h = 470, 860
    im, d = canvas(w + 14, h + 14)
    d.rounded_rectangle([S(14), S(14), S(w + 14), S(h + 14)], S(66), fill=INK)
    d.rounded_rectangle([0, 0, S(w), S(h)], S(66), fill=INK)
    d.rounded_rectangle([S(16), S(16), S(w - 16), S(h - 16)], S(52), fill=(248, 248, 250, 255))
    d.rounded_rectangle([S(w / 2 - 60), S(30), S(w / 2 + 60), S(58)], S(14), fill=INK)
    return finish(im)


KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]


@lru_cache(maxsize=32)
def keypad(pressed):
    im, d = canvas(470, 860)
    for i, k in enumerate(KEYS):
        x, y = 105 + (i % 3) * 130, 360 + (i // 3) * 108
        d.ellipse([S(x - 44), S(y - 44), S(x + 44), S(y + 44)], fill=(200, 205, 215, 255) if k == pressed else (232, 234, 238, 255))
        dtext(d, (x, y), k, "semi", 40, INK, "mm")
    d.ellipse([S(235 - 46), S(792 - 46), S(235 + 46), S(792 + 46)], fill=GREEN)
    dtext(d, (235, 792), "ARA", "black", 26, WHITE, "mm")
    return finish(im)


def key_xy(px, py, k):
    i = KEYS.index(k)
    return px - 235 + 105 + (i % 3) * 130, py - 430 + 360 + (i // 3) * 108


@lru_cache(maxsize=64)
def icon_big(kind, size=260):
    im, d = canvas(size, size)
    s = size / 260
    if kind == "warn":
        return icon_warn(size)
    if kind == "check":
        return icon_check(size)
    if kind == "money":
        d.ellipse([S(14 * s), S(14 * s), S(size), S(size)], fill=INK)
        d.ellipse([0, 0, S(size - 14 * s), S(size - 14 * s)], fill=(250, 200, 50, 255), outline=INK, width=S(8 * s))
        dtext(d, ((size - 14 * s) / 2, (size - 14 * s) / 2), "₺", "black", int(130 * s), (170, 110, 10, 255), "mm")
    elif kind == "calendar":
        d.rounded_rectangle([S(10 * s), S(30 * s), S(size - 10 * s), S(size - 10 * s)], S(24 * s), fill=WHITE, outline=INK, width=S(8 * s))
        d.rectangle([S(14 * s), S(34 * s), S(size - 14 * s), S(90 * s)], fill=RED)
        for k in range(2):
            d.rounded_rectangle([S((70 + k * 110) * s), S(10 * s), S((90 + k * 110) * s), S(60 * s)], S(8 * s), fill=INK)
        dtext(d, (size / 2, 170 * s), "!", "black", int(110 * s), INK, "mm")
    elif kind == "doc":
        d.polygon([(S(40 * s), S(10 * s)), (S(180 * s), S(10 * s)), (S(230 * s), S(60 * s)), (S(230 * s), S(250 * s)), (S(40 * s), S(250 * s))],
                  fill=WHITE, outline=INK)
        d.line([(S(40 * s), S(10 * s)), (S(180 * s), S(10 * s)), (S(230 * s), S(60 * s)), (S(230 * s), S(250 * s)), (S(40 * s), S(250 * s)),
                (S(40 * s), S(10 * s))], fill=INK, width=S(8 * s), joint="curve")
        for k in range(5):
            d.line([S(70 * s), S((90 + k * 30) * s), S((200 - (k % 2) * 40) * s), S((90 + k * 30) * s)], fill=(190, 190, 190, 255), width=S(9 * s))
    elif kind == "law":
        d.rectangle([S(122 * s), S(40 * s), S(138 * s), S(230 * s)], fill=INK)
        d.rounded_rectangle([S(20 * s), S(60 * s), S(240 * s), S(76 * s)], S(8 * s), fill=INK)
        for cx in (50, 210):
            d.line([S(cx * s), S(70 * s), S((cx - 30) * s), S(150 * s)], fill=INK, width=S(4 * s))
            d.line([S(cx * s), S(70 * s), S((cx + 30) * s), S(150 * s)], fill=INK, width=S(4 * s))
            d.chord([S((cx - 42) * s), S(120 * s), S((cx + 42) * s), S(180 * s)], 0, 180, fill=YELLOW, outline=INK, width=S(6 * s))
        d.rounded_rectangle([S(70 * s), S(220 * s), S(190 * s), S(246 * s)], S(8 * s), fill=INK)
    return finish(im)


@lru_cache(maxsize=256)
def wrapped_title(text, size, color, maxch):
    lines = wrap(upper_tr(text), maxch)[:4]
    sprites = [text_sprite(l, "black", size, color) for l in lines]
    w = max(s.width for s in sprites)
    h = sum(s.height for s in sprites) - 10 * (len(sprites) - 1)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for s in sprites:
        im.alpha_composite(s, (0, y))
        y += s.height - 10
    return im


@lru_cache(maxsize=64)
def chip(text, color):
    return pill(text, "black", 34, WHITE, color, border=4, pad=(22, 12), shadow=5)


@lru_cache(maxsize=32)
def bigchip(text, color):
    return pill(text[:30], "black", 44, WHITE, color, border=5, pad=(26, 14), shadow=6)


@lru_cache(maxsize=16)
def doc_card(title, n_lines, lines, stamp_txt=""):
    w, h = 900, 560
    im, d = card_base(w, h, header=INK, header_h=80)
    dtext(d, (34, 20), title, "black", 36, WHITE)
    return finish(im)


@lru_cache(maxsize=8)
def bank_notif(amount):
    w, h = 720, 170
    im, d = card_base(w, h, radius=30, shadow=8)
    d.rounded_rectangle([S(30), S(40), S(120), S(130)], S(20), fill=GREEN, outline=INK, width=S(3))
    dtext(d, (75, 85), "₺", "black", 50, WHITE, "mm")
    dtext(d, (150, 36), "BANKA · şimdi", "bold", 24, GREYT)
    dtext(d, (150, 74), f"Hesabınıza {amount} yatırıldı" if amount else "Ödemeniz hesabınıza yatırıldı", "black", 32, INK)
    dtext(d, (150, 120), "Açıklama: İade / Tazminat", "semi", 24, GREYT)
    return finish(im)


@lru_cache(maxsize=4)
def coin(size=110):
    return icon_big("money", size)


@lru_cache(maxsize=16)
def step_card(i, title, w=360):
    im, d = card_base(w, 250)
    d.ellipse([S(24), S(24), S(94), S(94)], fill=RED, outline=INK, width=S(4))
    dtext(d, (59, 59), str(i + 1), "black", 40, WHITE, "mm")
    for k, ln in enumerate(wrap(title, 17)[:3]):
        dtext(d, (24, 116 + k * 40), ln, "black", 32, INK)
    return finish(im)


@lru_cache(maxsize=4)
def sub_button(state):
    if state == 0:
        return pill("ABONE OL", "black", 64, WHITE, RED, border=5, pad=(44, 22), shadow=8)
    return pill("ABONE OLUNDU ✓", "black", 64, INK, (225, 225, 225, 255), border=5, pad=(44, 22), shadow=8)


def sentence_times(sents, dur):
    est = [sdur(s) for s in sents] or [dur]
    k = dur / sum(est)
    ts, acc = [], 0.0
    for e in est:
        ts.append(acc)
        acc += e * k
    return ts, [e * k for e in est]


# ================================================================ UZUN sahneler
def scene_hook(sc, dur):
    title = sc.get("title") or key_phrase(" ".join(sc["sentences"]), 8)
    ts, ds = sentence_times(sc["sentences"], dur)
    chips_ = []
    for s in sc["sentences"]:
        chips_ += [key_phrase(s, 4)]
    chips_ = chips_[:3]

    n_lines = len(wrap(upper_tr(title), 20))
    tsz, tch = (84, 20) if n_lines <= 3 else (66, 26)

    def f(world, t, d):
        tt = wrapped_title(title, tsz, INK, tch)
        place(world, tt, 90, 200, anchor="tl")
        for i, c in enumerate(chips_):
            place_anim(world, bigchip(c, [RED, BLUE, GREEN][i % 3]), 1450, 330 + i * 140, t, d, "right", 0.4 + ts[min(i, len(ts) - 1)], 0.4, [-3, 2, -2][i])
        place_anim(world, stamp("HAKKINI AL ✓", 64, GREEN), 1400, 800, t, d, "stamp", max(1.5, d - 2.0), 0.25, -5)
        z = 1 + 0.06 * (1 - out_cubic(prog(t, 0, 0.4)))
        return {"cam": drift(t, (z, W / 2, H / 2)), "mascot": sc["mascot"][0] if sc.get("mascot") else "saskin"}
    sfx = [(0, "impact")] + [(0.4 + ts[min(i, len(ts) - 1)], "pop") for i in range(len(chips_))] + [(max(1.5, dur - 2.0), "impact")]
    return f, sfx


def scene_overview(sc, dur):
    steps = sc.get("steps", [])
    n = len(steps)
    cw = min(380, int(1700 / max(1, n)) - 20)

    def f(world, t, d):
        t1 = text_sprite(f"{n} NET ADIM", "black", 120, RED)
        place_anim(world, t1, 90 + t1.width / 2, 240, t, d, "left", 0.0)
        for i, s in enumerate(steps):
            x = 960 + (i - (n - 1) / 2) * (cw + 20)
            place_anim(world, step_card(i, s, cw), x, 640, t, d, "pop", 0.4 + i * 0.35, 0.35, [-3, 2, -2, 3, -2, 2][i % 6])
        return {"cam": drift(t), "mascot": "ciddi:isaret"}
    return f, [(0.4 + i * 0.35, "pop") for i in range(n)]


def scene_card(sc, dur):
    sents = sc["sentences"]
    ts, ds = sentence_times(sents, dur)
    cards = sc.get("cards") or [{"title": key_phrase(s), "chips": [], "stamp": "", "icon": "check"} for s in sents]

    def f(world, t, d):
        i = max(k for k in range(len(ts)) if ts[k] <= t) if t >= 0 else 0
        c = cards[min(i, len(cards) - 1)]
        lt, ld = t - ts[i], ds[i]
        place_anim(world, wrapped_title(c["title"], 86, INK, 18), 620, 400, lt, ld, "left", 0.0, 0.35)
        place_anim(world, icon_big(c.get("icon", "check"), 280), 1480, 420, lt, ld, "pop", 0.25, 0.35, -4)
        for j, ch in enumerate(c.get("chips", [])[:4]):
            place_anim(world, chip(ch, [RED, BLUE, GREEN, INK][j % 4]), 420 + (j % 2) * 560, 720 + (j // 2) * 110, lt, ld, "pop",
                       0.5 + j * 0.45 * min(1, ld / 3), 0.3)
        if c.get("stamp"):
            place_anim(world, stamp(c["stamp"], 64), 1480, 700, lt, ld, "stamp", min(ld * 0.55, 2.5), 0.25, -6)
        m = sc.get("mascot") or ["ciddi"]
        return {"cam": drift(t), "mascot": m[min(i, len(m) - 1)]}
    sfx = []
    for i, c in enumerate(cards[:len(ts)]):
        sfx += [(ts[i] + 0.25, "pop")]
        sfx += [(ts[i] + 0.5 + j * 0.45 * min(1, ds[i] / 3), "tick") for j in range(len(c.get("chips", [])[:4]))]
        if c.get("stamp"):
            sfx.append((ts[i] + min(ds[i] * 0.55, 2.5), "impact"))
    return f, sfx


def scene_phone(sc, dur):
    num = str(sc.get("number", "184"))
    PX, PY = 640, 520
    t_keys = [0.6 + i * 0.4 for i in range(len(num))]
    t_call = t_keys[-1] + 0.6

    def f(world, t, d):
        place_anim(world, phone_frame(), PX, PY, t, d, "up", 0.0, 0.35)
        if t > 0.35:
            if t < t_call:
                pressed = next((num[i] for i, tk in enumerate(t_keys) if 0 <= t - tk < 0.18 and num[i] in KEYS), None)
                place(world, keypad(pressed), PX, PY + 7)
                shown = "".join(num[i] for i, tk in enumerate(t_keys) if t >= tk)
                place(world, text_sprite(shown or " ", "semi", 70, INK), PX, PY - 280)
                pts = [(0, PX + 300, PY + 300)]
                for i, tk in enumerate(t_keys):
                    if num[i] in KEYS:
                        x, y = key_xy(PX, PY, num[i])
                        pts += [(tk - 0.15, x, y), (tk + 0.1, x, y)]
                pts.append((t_call - 0.1, PX, PY + 362))
                x, y = path(t, pts)
                draw_cursor(world, x, y, t, tuple(t_keys) + (t_call - 0.05,), 44)
            else:
                place(world, text_sprite(num, "black", 96, INK), PX, PY - 250)
                place(world, pill("ARANIYOR", "black", 34, WHITE, GREEN, pad=(22, 12)), PX, PY + 60)
                for k in range(3):
                    r = 60 + ((t * 70 + k * 40) % 120)
                    ring = Image.new("RGBA", (int(2 * r + 8), int(2 * r + 8)), (0, 0, 0, 0))
                    ImageDraw.Draw(ring).ellipse([4, 4, 2 * r + 4, 2 * r + 4], outline=(24, 160, 88, int(200 * (1 - (r - 60) / 120))), width=6)
                    world.alpha_composite(ring, (int(PX - r - 4), int(PY + 60 - r - 4)))
        note = sc.get("note", "")
        if note:
            place_anim(world, wrapped_title(note, 64, INK, 16), 1420, 420, t, d, "right", t_call + 0.3, 0.4)
            place_anim(world, stamp("HEMEN ARA", 56), 1420, 700, t, d, "stamp", t_call + 1.0, 0.25, -5)
        cam = drift(t, (1.15, PX + 120, PY)) if t < t_call + 0.2 else drift(t)
        m = sc.get("mascot") or ["ciddi:isaret"]
        return {"cam": cam, "keys": [(tk, num[i]) for i, tk in enumerate(t_keys)], "mascot": m[0]}
    sfx = [(tk, "click") for tk in t_keys] + [(t_call - 0.05, "click"), (t_call, "ding"), (t_call + 1.0, "impact")]
    return f, sfx


def scene_document(sc, dur):
    lines = sc.get("lines", [])[:5]
    total = sum(len(l) for l in lines) or 1
    t0, t1 = 0.8, max(1.6, dur - 1.6)
    cps = total / (t1 - t0)
    title = sc.get("doc_title", "DİLEKÇE")

    def f(world, t, d):
        base = doc_card(title, 0, ())
        place_anim(world, base, 760, 520, t, d, "drop", 0.0, 0.4, -2)
        x0, y0 = 760 - 450, 520 - 280
        n = typing(t, t0, "".join(lines), cps)
        for i, ln in enumerate(lines):
            before = sum(len(l) for l in lines[:i])
            k = clamp(n - before, 0, len(ln))
            if k > 0:
                place(world, text_sprite(ln[:int(k)], "bold", 32, INK), x0 + 40, y0 + 130 + i * 62, anchor="l")
        if sc.get("stamp"):
            place_anim(world, stamp(sc["stamp"], 60, GREEN), 1500, 760, t, d, "stamp", t1 + 0.2, 0.25, -8)
        place_anim(world, icon_big("doc", 220), 1520, 360, t, d, "pop", 0.3, 0.35, 6)
        cam = drift(t, (1.2, 760, 470)) if t < t1 else drift(t)
        m = sc.get("mascot") or ["ciddi"]
        return {"cam": cam, "mascot": m[0], "keys": [(t0 + j / cps, c.upper() if c != " " else "Space") for j, c in enumerate("".join(lines))][::3]}
    sfx = [(0.0, "whoosh")] + [(t0 + j / cps, "key") for j in range(0, total, 2)] + ([(t1 + 0.2, "impact")] if sc.get("stamp") else [])
    return f, sfx


def scene_money(sc, dur):
    amt = sc.get("amount", "")
    val = int(re.sub(r"\D", "", amt) or 0)

    def f(world, t, d):
        place_anim(world, bank_notif(amt), 640, 380, t, d, "drop", 0.2, 0.4)
        for k in range(10):
            tk = 0.6 + k * 0.1
            if t < tk:
                continue
            x = 1260 + (k % 5) * 110 + (k // 5) * 55
            place(world, coin(110), x, min(640 - (k // 5) * 80, 100 + (t - tk) * 2000))
        if val:
            v = int(val * out_cubic(prog(t, 0.5, 1.4)))
            place(world, text_sprite(f"+{v:,}".replace(",", ".") + " TL", "black", 100, GREEN, 6, WHITE), 640, 600)
        else:
            place_anim(world, wrapped_title(key_phrase(" ".join(sc["sentences"]), 5), 70, GREEN, 18), 640, 620, t, d, "up", 0.6)
        m = sc.get("mascot") or ["mutlu"]
        return {"cam": drift(t), "mascot": "heyecanli:kutlama" if "mutlu" in m[0] else m[0]}
    return f, [(0.2, "ding")] + [(0.85 + k * 0.1, "tick") for k in range(10)]


def scene_outro(sc, dur):
    def f(world, t, d):
        t1 = text_sprite("HAKLARINI KORUYAN", "black", 80, INK)
        t2 = text_sprite("NET REHBERLER", "black", 110, RED)
        place_anim(world, t1, W / 2, 300, t, d, "up", 0.0)
        place_anim(world, t2, W / 2, 410, t, d, "pop", 0.2)
        tc = min(2.9, d - 0.8)
        place_anim(world, sub_button(1 if t > tc + 0.05 else 0), W / 2, 640, t, d, "pop", 0.6, 0.35)
        x, y = path(t, [(0, 1400, 950), (tc - 1.0, 1400, 950), (tc - 0.1, W / 2 + 40, 650)])
        draw_cursor(world, x, y, t, (tc,), 48)
        return {"cam": drift(t), "mascot": "goz_kirp:selam" if t < tc else "kahkaha:kutlama"}
    tc = min(2.9, dur - 0.8)
    return f, [(0.6, "pop"), (tc, "click"), (tc + 0.05, "ding")]


# ---------------------------------------------------------------- PORTAL (web + mobil)
PHX, PHY = 600, 540


def compile_portal(sc, dur):
    """Eylemleri zamana yerleştirir; sayfa/widget/durum zaman çizelgesini kurar."""
    sents = sc["sentences"]
    ts, ds = sentence_times(sents, dur)
    mobile = sc.get("device") == "mobile"
    theme = sc.get("theme", "edevlet")
    acts = [dict(a) for a in sc.get("actions", [])]
    by_s = {}
    for a in acts:
        by_s.setdefault(min(a.get("s", 0), len(sents) - 1), []).append(a)
    timeline = []
    for si, al in sorted(by_s.items()):
        w0, w1 = ts[si] + 0.25, ts[si] + ds[si] - 0.15
        seg = (w1 - w0) / len(al)
        for j, a in enumerate(al):
            a["t0"], a["t1"] = w0 + j * seg, w0 + (j + 1) * seg
            timeline.append(a)
    # widget'ları oluştur
    service_title = None
    widgets, has_search = [], False
    for a in timeline:
        d = a["do"]
        if d == "search":
            has_search = True
            service_title = service_title or a["text"]
        elif d == "login":
            widgets += [{"id": "tc", "kind": "field", "label": "T.C. Kimlik No", "value": "1•••••••••8"},
                        {"id": "pw", "kind": "field", "label": "Şifre", "value": "••••••••"}]
            a["targets"] = ["tc", "pw"]
        elif d == "menu":
            wid = f"menu{len(widgets)}"
            widgets.append({"id": wid, "kind": "list", "label": "İşlemler", "rows": [a["text"], "Geçmiş işlemlerim", "Ayarlar"]})
            a["targets"] = [wid]
        elif d == "select":
            wid = f"sel{len(widgets)}"
            widgets.append({"id": wid, "kind": "radio", "options": ["Bilgi", a["text"][:16], "Diğer"], "pick": 1})
            a["targets"] = [wid]
        elif d == "field":
            wid = f"f{len(widgets)}"
            widgets.append({"id": wid, "kind": "field", "label": a.get("label", ""), "value": a["text"]})
            a["targets"] = [wid]
        elif d == "textarea":
            wid = f"ta{len(widgets)}"
            widgets.append({"id": wid, "kind": "textarea", "label": "Açıklama", "lines": a["lines"]})
            a["targets"] = [wid]
        elif d == "upload":
            ids = []
            for f_ in a["files"]:
                wid = f"up{len(widgets)}"
                widgets.append({"id": wid, "kind": "upload", "value": f_})
                ids.append(wid)
            a["targets"] = ids
        elif d == "result":
            wid = f"tb{len(widgets)}"
            widgets.append({"id": wid, "kind": "table", "label": "Sonuç", "rows": [tuple(r) for r in a["rows"]]})
            a["targets"] = [wid]
        elif d == "submit":
            wid = f"btn{len(widgets)}"
            widgets.append({"id": wid, "kind": "button", "label": a.get("label", "Gönder")})
            a["targets"] = [wid]
    if not widgets:
        widgets.append({"id": "info", "kind": "info", "value": key_phrase(" ".join(sents), 8)})
    title = (service_title or sc.get("context") or P.THEMES[theme][0])
    title = title[:1].upper() + title[1:]
    # ekranlara böl (taşma olmasın)
    screens, cur = [], []
    PW, PHh = P.page_size(mobile)
    for w in widgets:
        trial = cur + [w]
        bx = P.widget_boxes(trial, mobile)
        if cur and max(b[3] for b in bx.values()) > PHh - 16:
            screens.append(cur)
            cur = [w]
        else:
            cur = trial
    screens.append(cur)
    wscreen = {w["id"]: i for i, sc_ in enumerate(screens) for w in sc_}
    return dict(mobile=mobile, theme=theme, timeline=timeline, screens=screens, wscreen=wscreen, title=title,
                has_search=has_search, search=next((a for a in timeline if a["do"] == "search"), None))


def scene_portal(sc, dur):
    C = compile_portal(sc, dur)
    mobile, theme, tl = C["mobile"], C["theme"], C["timeline"]
    srch = C["search"]
    url = P.THEMES[theme][3]

    def state_at(t):
        """(sayfa_spr, ekran_no, widget_listesi, kutular, odak_widget, modal, flash)"""
        if srch and t < srch["t1"] - 0.05:
            q = srch["text"]
            ta, tb = srch["t0"], srch["t1"]
            cps = len(q) / max(0.6, (tb - ta) * 0.55)
            n = typing(t, ta + 0.25, q, cps)
            sugg = (q[:40], P.THEMES[theme][0], t > tb - 0.6) if n >= min(len(q), 4) else None
            wl = [{"id": "q", "kind": "search", "value": q}]
            st = {"q": (n, True)}
            spr = P.render_page(theme, "Size nasıl yardımcı olabilirim?", wl, st, mobile, sugg)
            return spr, wl, P.widget_boxes(wl, mobile), srch, False, None
        active = None
        states = {}
        for a in tl:
            if a["do"] == "search":
                continue
            prog_a = clamp((t - a["t0"]) / max(0.2, a["t1"] - a["t0"]))
            if a["t0"] - 0.3 <= t <= a["t1"] + 0.2:
                active = a
            if t < a["t0"]:
                continue
            tg = a.get("targets", [])
            if a["do"] == "login":
                for j, wid in enumerate(tg):
                    v = 11 if j == 0 else 8
                    pj = clamp(prog_a * 2 - j)
                    states[wid] = (int(v * pj), 0 < prog_a * 2 - j < 1)
            elif a["do"] in ("field",):
                v = len(a["text"])
                states[tg[0]] = (int(v * clamp(prog_a / 0.85)), prog_a < 1)
            elif a["do"] == "textarea":
                v = sum(len(l) for l in a["lines"])
                states[tg[0]] = (int(v * clamp(prog_a / 0.9)), prog_a < 1)
            elif a["do"] == "upload":
                for j, wid in enumerate(tg):
                    pj = clamp(prog_a * len(tg) - j)
                    states[wid] = int(pj * 10)
            elif a["do"] in ("menu", "result"):
                states[tg[0]] = 0 if prog_a > 0.4 else -1
            elif a["do"] == "select":
                states[tg[0]] = prog_a > 0.4
            elif a["do"] == "submit":
                states[tg[0]] = 0.35 < prog_a < 0.55
        # hangi ekran?
        scr = 0
        for a in tl:
            if a.get("targets") and t >= a["t0"] - 0.3:
                scr = C["wscreen"][a["targets"][0]]
        wl = C["screens"][scr]
        st = {k: v for k, v in states.items() if any(w["id"] == k for w in wl)}
        spr = P.render_page(theme, C["title"], wl, st, mobile)
        sub = next((a for a in tl if a["do"] == "submit" and a["t0"] + 0.55 * (a["t1"] - a["t0"]) <= t), None)
        modal = sub is not None and t < sub["t1"] + 2.2
        flash = next((a for a in tl if a["do"] == "screenshot" and 0 <= t - (a["t0"] + 0.3) < 0.25), None)
        return spr, wl, P.widget_boxes(wl, mobile), active, modal, flash

    def to_world(x, y):
        if mobile:
            return PHX - 219 + x, PHY - 412 + y
        return CX0 + x, CY0 + y

    def target_xy(a, boxes, t):
        if a is None:
            return None
        if a["do"] == "search":
            b = boxes.get("q")
            if not b:
                return None
            if t > a["t1"] - 0.7:
                return to_world(b[0] + 300, b[3] + 44)
            return to_world(b[0] + 180, (b[1] + b[3]) / 2)
        tg = a.get("targets") or []
        if not tg:
            return None
        k = min(len(tg) - 1, int(clamp((t - a["t0"]) / max(0.2, a["t1"] - a["t0"])) * len(tg)))
        b = boxes.get(tg[k])
        if not b:
            return None
        if a["do"] == "upload":
            return to_world(b[2] - 70, (b[1] + b[3]) / 2)
        return to_world((b[0] + b[2]) / 2 - (100 if a["do"] in ("field", "login", "textarea") else 0), (b[1] + b[3]) / 2 + 10)

    # imleç yolu: her eylemin başında hedefe gider (bir kez hesaplanır)
    def _cursor_pts():
        pts = [(0, 1100, 900)]
        for a in ([srch] if srch else []) + [x for x in tl if x["do"] != "search"]:
            _, _, boxes, _, _, _ = state_at(a["t0"] + 0.05)
            p0 = target_xy(a, boxes, a["t0"] + 0.05)
            if p0:
                pts += [(a["t0"] - 0.05, *p0), (a["t0"] + 0.35, *p0)]
            if a["do"] in ("upload", "login", "search"):
                p1 = target_xy(a, state_at(a["t1"] - 0.1)[2], a["t1"] - 0.1)
                if p1:
                    pts += [(a["t1"] - 0.35, *p1), (a["t1"] - 0.05, *p1)]
        pts.sort(key=lambda p: p[0])
        return pts

    CUR = _cursor_pts()

    def cursor_at(t):
        return path(t, CUR)

    clicks = []
    for a in ([srch] if srch else []) + [x for x in tl if x["do"] != "search"]:
        clicks.append(a["t0"] + 0.1)
        if a["do"] == "search":
            clicks.append(a["t1"] - 0.15)
        if a["do"] == "upload":
            n = len(a.get("targets", []))
            clicks += [a["t0"] + (a["t1"] - a["t0"]) * j / n + 0.05 for j in range(n)]
        if a["do"] == "submit":
            clicks.append(a["t0"] + 0.45 * (a["t1"] - a["t0"]))

    def f(world, t, d):
        spr, wl, boxes, active, modal, flash = state_at(t)
        if mobile:
            place_anim(world, phone_frame(), PHX, PHY, t, d, "up", 0.0, 0.35)
            if t > 0.3:
                place(world, spr, PHX - 219, PHY - 412, anchor="tl")
            # sağda: cümlenin ana fikri
            ts_, ds_ = sentence_times(sc["sentences"], d)
            i = max(k for k in range(len(ts_)) if ts_[k] <= t)
            place_anim(world, wrapped_title(key_phrase(sc["sentences"][i], 6), 54, INK, 14), 1430, 420, t - ts_[i], ds_[i], "right", 0.2, 0.4)
            for j, ch in enumerate(kw_chips(sc["sentences"][i])):
                place_anim(world, chip(ch, [RED, BLUE, GREEN][j % 3]), 1430, 640 + j * 100, t - ts_[i], ds_[i], "pop", 0.6 + j * 0.4, 0.3)
        else:
            if t < 0.4:
                k = out_back(t / 0.4, 1.5)
                draw_browser(world, url, spr, tab=P.THEMES[theme][0], scale=0.86 + 0.14 * k, alpha=clamp(t / 0.25))
            else:
                draw_browser(world, url, spr, tab=P.THEMES[theme][0])
        x, y = cursor_at(t)
        draw_cursor(world, x, y, t, tuple(clicks), 40 if not mobile else 46)
        if flash:
            overlay(world, (255, 255, 255, 200))
        if modal:
            overlay(world, (20, 20, 20, 110))
            place_anim(world, P.success_modal("İşleminiz alındı", P.THEMES[theme][0]), W / 2, H / 2, t, d, "pop",
                       next(a for a in tl if a["do"] == "submit")["t0"] + 0.6, 0.35)
        # kamera: aktif widget'a yakınlaş
        foc = None
        if active is not None:
            p = target_xy(active, boxes, t)
            if p:
                w_ = smooth((t - (active["t0"] - 0.5)) / 0.4) * smooth(((active["t1"] + 0.5) - t) / 0.4)
                zf = 1.18 if mobile else 1.32
                foc = (1 + (zf - 1) * w_, lerp(W / 2, p[0] + (120 if mobile else 0), w_), lerp(H / 2, p[1], w_))
        if srch and srch["t0"] - 0.3 <= t <= srch["t1"] + 0.3:
            b = boxes.get("q")
            if b:
                p = to_world((b[0] + b[2]) / 2, b[3] + 20)
                w_ = smooth((t - (srch["t0"] - 0.4)) / 0.4) * smooth(((srch["t1"] + 0.4) - t) / 0.4)
                foc = (1 + 0.45 * w_ if not mobile else 1 + 0.18 * w_, lerp(W / 2, p[0], w_), lerp(H / 2, p[1], w_))
        if modal:
            foc = None
        cam = drift(t, foc or (1.0, W / 2, H / 2))
        keys = []
        for a in tl:
            if a["do"] in ("search", "field"):
                txt = a["text"]
                cps = len(txt) / max(0.4, (a["t1"] - a["t0"]) * (0.55 if a["do"] == "search" else 0.85))
                base_t = a["t0"] + (0.25 if a["do"] == "search" else 0)
                keys += [(base_t + j / cps, c.upper() if c != " " else "Space") for j, c in enumerate(txt)]
        m = sc.get("mascot") or ["ciddi"]
        ts_, _ = sentence_times(sc["sentences"], d)
        i = max(k for k in range(len(ts_)) if ts_[k] <= t)
        return {"cam": cam, "keys": keys, "mascot": "mutlu" if modal else m[min(i, len(m) - 1)]}

    sfx = [(c, "click") for c in clicks]
    for a in tl:
        if a["do"] in ("search", "field", "textarea", "login"):
            n = len(a.get("text", "")) or sum(len(l) for l in a.get("lines", [])) or 19
            sfx += [(a["t0"] + 0.25 + (a["t1"] - a["t0"] - 0.4) * j / n, "key") for j in range(0, n, 2)]
        if a["do"] == "upload":
            n = len(a.get("targets", []))
            sfx += [(a["t0"] + (a["t1"] - a["t0"]) * (j + 1) / n, "ding") for j in range(n)]
        if a["do"] == "submit":
            sfx.append((a["t0"] + 0.6, "ding"))
        if a["do"] == "screenshot":
            sfx.append((a["t0"] + 0.3, "tick"))
    return f, sfx


LONG_SCENES = {"hook": scene_hook, "overview": scene_overview, "card": scene_card, "phone": scene_phone,
               "document": scene_document, "money": scene_money, "outro": scene_outro, "portal": scene_portal}

MIN_DUR = {"hook": 4.0, "overview": 3.0, "phone": 4.5, "document": 4.5, "money": 3.6, "outro": 4.2, "portal": 4.0, "card": 2.2}


def build_long(plan, voice=None, total=None):
    scenes = plan["scenes"]
    durs = []
    for sc in scenes:
        d = sum(sdur(s) for s in sc.get("sentences", [])) or 3.0
        durs.append(max(MIN_DUR.get(sc["kind"], 2.0), d))
    if total:  # seslendirme süresine ölçekle
        k = total / sum(durs)
        durs = [d * k for d in durs]
    segs = []
    for sc, d in zip(scenes, durs):
        f, sfx = LONG_SCENES[sc["kind"]](sc, d)
        caps = [emphasize(s) for s in sc.get("sentences", [])]
        segs.append(Seg(d, f, caps, tuple(sc["chapter"]) if sc.get("chapter") else None, sfx))
    return Tutorial(segs, voice=None)


# ================================================================ SHORTS
def build_short(plan, total=None):
    from .shorts import Beat, Short
    beats = []
    durs = [max(1.8, sdur(b["sentence"])) for b in plan["beats"]]
    if total:
        k = total / sum(durs)
        durs = [d * k for d in durs]
    for i, (b, d) in enumerate(zip(plan["beats"], durs)):
        vis, sfx = SHORT_VIS[b["kind"]](b, d)
        t1, t2 = (b.get("title") or ["", ""])[:2]
        beats.append(Beat(d, (t1, t2), emphasize(b["sentence"]), vis, b.get("mascot", "ciddi"), sfx, punch=(i == 0)))
    return Short(beats)


def sv_card(b, d):
    def v(img, t, dur, cx, cy):
        place_anim(img, icon_big(b.get("icon", "check"), 300), cx, cy - 120, t, dur, "pop", -1 if b["kind"] == "hook" else 0.0, 0.35, -4)
        chs = b.get("chips", [])[:4]
        for j, ch in enumerate(chs):
            place_anim(img, bigchip(ch, [RED, BLUE, GREEN, INK][j % 4]), cx, cy + 130 + j * 110, t, dur, "pop", dur * (0.12 + 0.6 * j / max(1, len(chs))), 0.3)
        if b.get("stamp"):
            place_anim(img, stamp(b["stamp"], 66), cx + 120, cy + 60, t, dur, "stamp", min(dur * 0.5, 1.6), 0.25, -8)
    nch = len(b.get("chips", [])[:4])
    sfx = [(0.0, "pop")] + [(d * (0.12 + 0.6 * j / max(1, nch)), "tick") for j in range(nch)] + \
          ([(min(d * 0.5, 1.6), "impact")] if b.get("stamp") else [])
    return v, sfx


def sv_money(b, d):
    val = int(re.sub(r"\D", "", b.get("amount", "")) or 0)

    def v(img, t, dur, cx, cy):
        for k in range(8):
            tk = 0.2 + k * 0.1
            if t >= tk:
                place(img, coin(130), cx - 260 + (k % 4) * 170, min(cy + 220 - (k // 4) * 100, cy - 500 + (t - tk) * 2400))
        if val:
            vv = int(val * out_cubic(prog(t, 0.2, 1.2)))
            place(img, text_sprite(f"{vv:,}".replace(",", ".") + " TL", "black", 120, GREEN, 6, WHITE), cx, cy - 220)
        place_anim(img, pill("GERİ ALIRSIN ✓", "black", 50, WHITE, GREEN, border=4, pad=(26, 12), shadow=6), cx, cy + 360, t, dur, "pop", 1.0, 0.3)
    return v, [(0.2 + k * 0.1 + 0.3, "tick") for k in range(8)] + [(1.0, "ding")]


def sv_phone(b, d):
    num = str(b.get("number", "184"))

    def v(img, t, dur, cx, cy):
        shown = num[:int(clamp((t - 0.3) / 0.3, 0, len(num)))]
        place_anim(img, card_phone(), cx, cy, t, dur, "up", 0.0, 0.35)
        place(img, text_sprite(shown or " ", "black", 150, INK), cx, cy - 60)
        if t > 0.3 + len(num) * 0.3:
            place(img, pill("ARANIYOR", "black", 48, WHITE, GREEN, pad=(28, 14)), cx, cy + 160)
    return v, [(0.3 + i * 0.3, "click") for i in range(len(num))] + [(0.4 + len(num) * 0.3, "ding")]


@lru_cache(maxsize=1)
def card_phone():
    im, d = card_base(560, 620, radius=60)
    return finish(im)


def sv_document(b, d):
    lines = b.get("lines", [])
    total = sum(len(l) for l in lines) or 1
    cps = total / max(1.0, d - 1.0)

    def v(img, t, dur, cx, cy):
        place_anim(img, doc_card(b.get("doc_title", "DİLEKÇE"), 0, ()), cx, cy, t, dur, "drop", 0.0, 0.35, -2)
        n = typing(t, 0.4, "".join(lines), cps)
        for i, ln in enumerate(lines):
            before = sum(len(l) for l in lines[:i])
            k = clamp(n - before, 0, len(ln))
            if k > 0:
                place(img, text_sprite(ln[:int(k)], "bold", 34, INK), cx - 410, cy - 150 + i * 60, anchor="l")
    return v, [(0.4 + j / cps, "key") for j in range(0, total, 2)]


def sv_portal(b, d):
    q = b.get("query") or key_phrase(b["sentence"], 4)
    theme = b.get("theme", "edevlet")

    def v(img, t, dur, cx, cy):
        n = typing(t, 0.5, q, 12)
        wl = [{"id": "q", "kind": "search", "value": q}]
        spr = P.render_page(theme, "", wl, {"q": (n, True)}, True, (q[:30], P.THEMES[theme][0], False) if n >= 4 else None)
        place_anim(img, phone_frame(), cx, cy, t, dur, "up", 0.0, 0.35)
        place(img, spr, cx - 219, cy - 412, anchor="tl")
    return v, [(0.5 + j / 12, "key") for j in range(0, len(q), 2)]


@lru_cache(maxsize=32)
def comment_ui(word, typed, sent, replied):
    w, h = 860, 640
    im, d = card_base(w, h, radius=30)
    dtext(d, (40, 30), "Yorumlar", "black", 38)
    dtext(d, (820, 36), "1.927", "bold", 30, (130, 130, 130, 255), "ra")
    y = 110
    rows = [("ayse.k", "Bunu hiç bilmiyordum!"), ("mert_34", "Hemen kontrol ettim, teşekkürler")]
    if sent:
        rows.append(("sen", word))
    for u, m in rows:
        me = u == "sen"
        d.ellipse([S(40), S(y), S(104), S(y + 64)], fill=RED if me else (200, 200, 200, 255), outline=INK, width=S(3))
        dtext(d, (124, y + 2), u, "bold", 26, (110, 110, 110, 255))
        dtext(d, (124, y + 34), m, "black" if me else "semi", 32 if me else 30, RED if me else INK)
        y += 108
    if replied:
        d.rounded_rectangle([S(124), S(y - 6), S(820), S(y + 66)], S(18), fill=(236, 248, 241, 255), outline=GREEN, width=S(4))
        dtext(d, (146, y + 14), "↳ Rehber DM'de ✓", "black", 30, GREEN)
    d.rounded_rectangle([S(30), S(520), S(690), S(608)], S(44), fill=(244, 244, 244, 255), outline=INK, width=S(4))
    dtext(d, (64, 545), typed if typed else "Yorum ekle...", "black" if typed else "semi", 34, INK if typed else (160, 160, 160, 255))
    d.ellipse([S(710), S(520), S(800), S(610)], fill=RED, outline=INK, width=S(4))
    d.polygon([(S(738), S(545)), (S(782), S(565)), (S(738), S(585))], fill=WHITE)
    return finish(im)


def sv_comment(b, d):
    word = b.get("word", "EVET")
    cps = 9
    t_send = 0.4 + len(word) / cps + 0.3

    def v(img, t, dur, cx, cy):
        n = typing(t, 0.4, word, cps)
        sent = t > t_send
        place_anim(img, comment_ui(word, "" if sent else word[:n], sent, t > t_send + 0.6), cx, cy, t, dur, "pop", 0.0, 0.35)
        x, y = path(t, [(0, cx + 300, cy + 420), (t_send - 0.4, cx + 300, cy + 420), (t_send - 0.05, cx + 330, cy + 250)])
        draw_cursor(img, x, y, t, (t_send,), 60)
    return v, [(0.4 + j / cps, "key") for j in range(len(word))] + [(t_send, "click"), (t_send + 0.6, "ding")]


SHORT_VIS = {"hook": sv_card, "card": sv_card, "money": sv_money, "phone": sv_phone, "document": sv_document,
             "portal": sv_portal, "comment": sv_comment, "save": sv_card}
