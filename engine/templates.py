"""HAZIR SAHNE ŞABLONLARI — ajan çizmez, plan JSON'unda "sablon" adıyla seçer.

Her şablon: draw(world, t, dur, p) → world'e (1920x1080) hareketli içerik çizer. p = parametre sözlüğü.
| sablon        | parametreler                                                         |
|---------------|----------------------------------------------------------------------|
| not           | metin, ikon, etiketler[]                                             |
| sayac         | deger ("12.450 TL" / "%30" / "10 gün"), metin, ikon                  |
| karsilastirma | sol_baslik, sol[], sag_baslik, sag[]                                 |
| zaman         | adimlar[] (ör. ["Bugün","15 gün","30 gün"]), metin                    |
| liste         | metin, maddeler[] (en çok 5)                                          |
| akis          | kutular[] (ör. ["Sen","Banka","Hakem Heyeti"]), ikonlar[] (isteğe bağlı) |
| uyari         | metin, alt                                                            |
| yasak         | metin, ikon                                                           |
Galeri: docs/sablon_katalogu.jpg
"""
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw

from .assets import icon, icon_for_text
from .core import clamp, font, out_back, out_cubic, place

W, H = 1920, 1080
INK = (17, 24, 39, 255)
G500 = (107, 114, 128, 255)
G200 = (229, 231, 235, 255)
WHITE = (255, 255, 255, 255)
GREEN = (22, 150, 80, 255)
RED = (220, 38, 38, 255)
ORANGE = (234, 108, 30, 255)


def _wrap(t, n):
    out, cur = [], ""
    for w in str(t).split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


@lru_cache(maxsize=512)
def card(w, h, accent=None, r=26):
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(14, 0, -2):
        d.rounded_rectangle([20 - k / 2, 20 + k / 2, 20 + w + k / 2, 20 + h + k], r + k / 2, fill=(0, 0, 0, 7))
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], r, fill=WHITE, outline=G200, width=2)
    if accent:
        d.rounded_rectangle([20, 20, 32, 20 + h], 6, fill=accent)
    return im


@lru_cache(maxsize=1024)
def text_img(s, size, color=INK, weight="bold", maxw=None):
    f = font(weight, size)
    w = int(f.getlength(s)) + 8
    im = Image.new("RGBA", (w, int(size * 1.35)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2, size * 0.1), s, font=f, fill=color)
    return im


def pop(t, t0, d=0.35):
    return out_back(clamp((t - t0) / d), 1.4), clamp((t - t0) / 0.2)


def _lines(world, text, x, y, size, n, color=INK, anchor="l", t=0.0, t0=0.0):
    for i, ln in enumerate(_wrap(text, n)[:3]):
        k, a = pop(t, t0 + i * 0.08)
        place(world, text_img(ln, size, color), x, y + i * size * 1.25 + (1 - k) * 20, anchor=anchor if anchor != "c" else "c", alpha=a)


# ---------------------------------------------------------------- şablonlar
def t_not(world, t, d, p):
    txt = p.get("metin", "")
    ik = p.get("ikon") or icon_for_text(txt)
    chips = p.get("etiketler", [])[:3]
    lines = _wrap(txt, 24)[:3]
    h = 120 + 70 * len(lines) + (80 if chips else 0)
    k, a = pop(t, 0.0, 0.45)
    place(world, card(1100, h, (239, 68, 68, 255)), W / 2, H / 2 + (1 - k) * 40, alpha=a)
    x0, y0 = W / 2 - 550, H / 2 - h / 2
    ki, ai = pop(t, 0.15)
    place(world, icon(ik, 150), x0 + 130, y0 + 120, scale=0.6 + 0.4 * ki, alpha=ai)
    for i, ln in enumerate(lines):
        kk, aa = pop(t, 0.25 + i * 0.1)
        place(world, text_img(ln, 56, INK), x0 + 250, y0 + 90 + i * 70 + (1 - kk) * 16, anchor="l", alpha=aa)
    bx = x0 + 250
    for j, c in enumerate(chips):
        im = chip_img(c)
        kc, ac = pop(t, 0.6 + j * 0.25 * max(1, d / 4))
        place(world, im, bx + im.width / 2, y0 + 100 + 70 * len(lines) + 20, scale=kc, alpha=ac)
        bx += im.width + 14


@lru_cache(maxsize=256)
def chip_img(c, fill=(243, 244, 246, 255), col=(55, 65, 81, 255)):
    f = font("semi", 34)
    w = int(f.getlength(c)) + 50
    im = Image.new("RGBA", (w, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, 63], 32, fill=fill, outline=G200, width=2)
    d.text((w / 2, 32), c, font=f, fill=col, anchor="mm")
    return im


def t_sayac(world, t, d, p):
    val = str(p.get("deger", "100"))
    m = re.search(r"(\d[\d.]*)", val)
    num = int(m.group(1).replace(".", "")) if m else 0
    pre, post = (val[:m.start()], val[m.end():]) if m else ("", val)
    k, a = pop(t, 0.0, 0.45)
    place(world, card(1000, 520), W / 2, H / 2 + (1 - k) * 40, alpha=a)
    ik = p.get("ikon") or icon_for_text(p.get("metin", "") + " " + val, "para")
    ki, ai = pop(t, 0.1)
    place(world, icon(ik, 130), W / 2, H / 2 - 160, scale=ki, alpha=ai)
    v = int(num * out_cubic(clamp((t - 0.3) / 1.4)))
    s = pre + (f"{v:,}".replace(",", ".") if num >= 1000 else str(v)) + post
    place(world, text_img(s, 130, GREEN), W / 2, H / 2 + 10, alpha=clamp((t - 0.25) / 0.2))
    _lines(world, p.get("metin", ""), W / 2, H / 2 + 120, 48, 34, G500, "c", t, 0.6)


def t_karsilastirma(world, t, d, p):
    cols = [(p.get("sol_baslik", "YANLIŞ"), p.get("sol", []), RED, "red", W / 2 - 300),
            (p.get("sag_baslik", "DOĞRU"), p.get("sag", []), GREEN, "onay", W / 2 + 300)]
    for ci, (bas, items, col, ik, cx) in enumerate(cols):
        t0 = ci * max(0.8, d * 0.35)
        k, a = pop(t, t0, 0.45)
        place(world, card(620, 520, col), cx, H / 2 + (1 - k) * 40, alpha=a)
        place(world, icon(ik, 110), cx - 220, H / 2 - 170, scale=k, alpha=a)
        place(world, text_img(bas, 60, col), cx - 140, H / 2 - 170, anchor="l", alpha=a)
        for i, it in enumerate(items[:4]):
            kk, aa = pop(t, t0 + 0.4 + i * 0.3)
            for j, ln in enumerate(_wrap(it, 18)[:2]):
                place(world, text_img(("• " if j == 0 else "  ") + ln, 46, INK, "semi"), cx - 260, H / 2 - 60 + i * 110 + j * 52,
                      anchor="l", alpha=aa)


def t_zaman(world, t, d, p):
    steps = p.get("adimlar", ["Bugün", "Süre", "Son gün"])[:5]
    n = len(steps)
    k, a = pop(t, 0.0, 0.45)
    place(world, card(1500, 460), W / 2, H / 2 + (1 - k) * 40, alpha=a)
    x0, x1, y = W / 2 - 600, W / 2 + 600, H / 2 + 30
    prog_ = clamp((t - 0.3) / max(1.0, d * 0.7))
    dr = ImageDraw.Draw(world)
    dr.rounded_rectangle([x0, y - 6, x1, y + 6], 6, fill=G200)
    dr.rounded_rectangle([x0, y - 6, x0 + (x1 - x0) * prog_, y + 6], 6, fill=(239, 68, 68, 255))
    for i, s in enumerate(steps):
        x = x0 + (x1 - x0) * i / max(1, n - 1)
        on = prog_ >= i / max(1, n - 1) - 1e-3
        r = 26 if on else 20
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(239, 68, 68, 255) if on else WHITE, outline=(239, 68, 68, 255), width=5)
        place(world, text_img(s, 46, INK if on else G500, "bold"), x, y + 76, alpha=1.0)
    place(world, icon("takvim", 110), W / 2 - 600, H / 2 - 140, alpha=a)
    _lines(world, p.get("metin", ""), W / 2 - 520, H / 2 - 150, 46, 40, INK, "l", t, 0.2)


def t_liste(world, t, d, p):
    items = p.get("maddeler", [])[:5]
    h = 170 + 110 * len(items)
    k, a = pop(t, 0.0, 0.45)
    place(world, card(1100, h, GREEN), W / 2, H / 2 + (1 - k) * 40, alpha=a)
    y0 = H / 2 - h / 2
    place(world, text_img(p.get("metin", "Kontrol listesi")[:40], 58, INK), W / 2 - 500, y0 + 90, anchor="l", alpha=a)
    for i, it in enumerate(items):
        t0 = 0.4 + i * max(0.35, (d - 1.0) / max(1, len(items)))
        kk, aa = pop(t, t0)
        place(world, icon("onay", 80, False), W / 2 - 460, y0 + 200 + i * 110, scale=kk, alpha=aa)
        place(world, text_img(it[:40], 50, INK, "semi"), W / 2 - 390, y0 + 200 + i * 110, anchor="l", alpha=aa)


def t_akis(world, t, d, p):
    boxes = p.get("kutular", ["Sen", "Kurum", "Sonuç"])[:4]
    ics = p.get("ikonlar") or [icon_for_text(b, "kisi") for b in boxes]
    n = len(boxes)
    gap = 1500 / n
    for i, b in enumerate(boxes):
        t0 = i * max(0.5, (d - 0.8) / n)
        x = W / 2 - 750 + gap * (i + 0.5)
        k, a = pop(t, t0, 0.4)
        place(world, card(340, 380), x, H / 2 + (1 - k) * 30, alpha=a)
        place(world, icon(ics[i] if i < len(ics) else "kisi", 150), x, H / 2 - 50, scale=k, alpha=a)
        for j, ln in enumerate(_wrap(b, 14)[:2]):
            place(world, text_img(ln, 44, INK), x, H / 2 + 90 + j * 46, alpha=a)
        if i < n - 1:
            ka, aa = pop(t, t0 + 0.3)
            place(world, icon("ok", 96, False), x + gap / 2, H / 2 - 10, scale=ka, alpha=aa)
    _lines(world, p.get("metin", ""), W / 2, H / 2 - 320, 46, 50, INK, "c", t, 0.1)


def t_uyari(world, t, d, p):
    k, a = pop(t, 0.0, 0.45)
    place(world, card(1200, 420, ORANGE), W / 2, H / 2 + (1 - k) * 40, alpha=a)
    pulse = 1 + 0.05 * math.sin(t * 6) * clamp(t / 0.5)
    place(world, icon("uyari", 190), W / 2 - 420, H / 2, scale=pulse * k, alpha=a)
    _lines(world, p.get("metin", ""), W / 2 - 280, H / 2 - 70, 54, 24, INK, "l", t, 0.2)
    if p.get("alt"):
        place(world, text_img(p["alt"][:48], 40, G500, "semi"), W / 2 - 280, H / 2 + 130, anchor="l", alpha=clamp((t - 0.6) / 0.3))


def t_yasak(world, t, d, p):
    k, a = pop(t, 0.0, 0.45)
    place(world, card(1200, 420, RED), W / 2, H / 2 + (1 - k) * 40, alpha=a)
    ik = p.get("ikon") or icon_for_text(p.get("metin", ""), "para")
    place(world, icon(ik, 190), W / 2 - 420, H / 2, alpha=a)
    ks, as_ = pop(t, 0.5, 0.3)
    place(world, icon("yasak", 150, False), W / 2 - 360, H / 2 + 60, scale=ks, alpha=as_)
    _lines(world, p.get("metin", ""), W / 2 - 280, H / 2 - 70, 54, 24, INK, "l", t, 0.2)


TEMPLATES = {"not": t_not, "sayac": t_sayac, "karsilastirma": t_karsilastirma, "zaman": t_zaman, "liste": t_liste,
             "akis": t_akis, "uyari": t_uyari, "yasak": t_yasak}


def draw_template(world, t, d, name, params):
    TEMPLATES.get(name, t_not)(world, t, d, params)


# ---------------------------------------------------------------- otomatik seçim (yönetmen kullanır)
INST = [("e-devlet", "e-Devlet"), ("sgk", "SGK"), ("cimer", "CİMER"), ("banka", "Banka"), ("noter", "Noter"),
        ("savcılı", "Savcılık"), ("hakem heyeti", "Hakem Heyeti"), ("mahkeme", "Mahkeme"), ("arabulucu", "Arabulucu"),
        ("işveren", "İşveren"), ("satıcı", "Satıcı"), ("operatör", "Operatör"), ("sigorta şirket", "Sigorta"),
        ("belediye", "Belediye"), ("vergi daire", "Vergi Dairesi"), ("icra", "İcra Dairesi"), ("polis", "Polis")]


def auto_template(sentence, key, chips, amount=None):
    """Cümleye göre şablon + parametre seç (planı ajan sonra düzenleyebilir)."""
    t = sentence.lower()
    inst = []
    for k, v in INST:
        i = t.find(k)
        if i >= 0 and v not in [x[1] for x in inst]:
            inst.append((i, v))
    inst = [v for _, v in sorted(inst)]
    if amount or re.search(r"%\s?\d+|yüzde \d+|\d+ kat", t):
        m = re.search(r"%\s?\d+|yüzde \d+|\d+ kat", t)
        val = amount or (m.group(0).replace("yüzde ", "%") if m else "")
        return "sayac", {"deger": val, "metin": key}
    m = re.search(r"(\d+)\s*(iş günü|gün|ay|yıl|saat)", t)
    if m and re.search(r"içinde|kadar|süre|sonra|geriye|zamanaşımı", t):
        return "zaman", {"adimlar": ["Bugün", f"{m.group(1)} {m.group(2)}", "Süre doldu"], "metin": key}
    if len(chips) >= 3:
        return "liste", {"metin": key, "maddeler": chips}
    if len(inst) >= 2:
        return "akis", {"kutular": ["Sen"] + inst[:3], "metin": key}
    if re.search(r"\b(asla|yasak|alamaz|yapamaz|isteyemez|kesemez|olmaz|edemez)\b", t):
        return "yasak", {"metin": key}
    if re.search(r"dikkat|tuzak|risk|kaybed|zamanaşımı|ceza", t):
        return "uyari", {"metin": key}
    if re.search(r" yerine | değil,? ", t):
        a, b = re.split(r" yerine | değil,? ", sentence, maxsplit=1)
        return "karsilastirma", {"sol_baslik": "YANLIŞ", "sol": [" ".join(a.split()[-5:])], "sag_baslik": "DOĞRU",
                                 "sag": [" ".join(b.split()[:6])]}
    return "not", {"metin": key, "etiketler": chips[:3]}


ORNEK = {
    "not": {"metin": "Bankalar 10 yıl sonra parayı devlete aktarır", "ikon": "banka", "etiketler": ["10 yıl", "Hazine"]},
    "sayac": {"deger": "12.450 TL", "metin": "Ortalama unutulmuş alacak"},
    "karsilastirma": {"sol_baslik": "YANLIŞ", "sol": ["Sözlü şikâyet", "Fişi atmak"], "sag_baslik": "DOĞRU",
                      "sag": ["Yazılı başvuru", "Fişi saklamak"]},
    "zaman": {"adimlar": ["Bugün", "15 gün", "30 gün"], "metin": "Satıcının cevap süresi"},
    "liste": {"metin": "Hazırlaman gerekenler", "maddeler": ["Kimlik", "Fatura", "Dekont", "Ekran görüntüsü"]},
    "akis": {"kutular": ["Sen", "Satıcı", "Hakem Heyeti"], "metin": "Başvuru sırası"},
    "uyari": {"metin": "Süreyi kaçırırsan hakkın düşer", "alt": "Zamanaşımı 2 yıl"},
    "yasak": {"metin": "İşveren maaşından kesinti yapamaz", "ikon": "para"},
}


def gallery(path="docs/sablon_katalogu.jpg"):
    from .core import font as F
    tiles = []
    for name, p in ORNEK.items():
        w = Image.new("RGBA", (W, H), (240, 242, 246, 255))
        draw_template(w, 3.0, 4.0, name, p)
        ImageDraw.Draw(w).text((40, 30), f'"sablon": "{name}"', font=F("bold", 56), fill=(220, 38, 38, 255))
        tiles.append(w.convert("RGB").resize((640, 360), Image.LANCZOS))
    sheet = Image.new("RGB", (640 * 4 + 50, 360 * 2 + 30), (255, 255, 255))
    for i, t in enumerate(tiles):
        sheet.paste(t, (10 + (i % 4) * 650, 10 + (i // 4) * 370))
    sheet.save(path, quality=88)
    return path


if __name__ == "__main__":
    print(gallery())
