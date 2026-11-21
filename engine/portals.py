"""Portal sahne kütüphanesi — düzenlenebilir, WEB (tarayıcı) ve MOBİL (telefon) uyumlu.

Bir portal sayfası = tema + widget listesi + widget durumları. Aynı sayfa hem web hem mobil düzende çizilir.
Tüm portallar STİLİZE ve kurgusaldır: gerçek logo, "T.C." başlığı ve gerçek alan adı KULLANILMAZ.

Yeni portal eklemek için THEMES sözlüğüne bir satır eklemen yeterli.
"""
from functools import lru_cache

from PIL import Image

from .core import GREEN, INK, RED, SS, WHITE, canvas, card_base, dtext, finish, font
from .components import icon_check

GREYT = (110, 110, 110, 255)
LINE = (214, 214, 214, 255)

# ---------------------------------------------------------------- TEMALAR (düzenlenebilir)
# key: (görünen ad, ana renk, logo harfi, adres çubuğu metni, anahtar kelimeler)
THEMES = {
    "edevlet":  ("e-Devlet Kapısı", (214, 40, 40), "e", "edevlet-portali / hizmetler", ["e-devlet", "edevlet"]),
    "cimer":    ("CİMER · İletişim Merkezi", (190, 24, 40), "C", "cimer-basvuru", ["cimer", "cumhurbaşkanlığı iletişim"]),
    "enabiz":   ("e-Nabız", (20, 150, 160), "+", "enabiz-uygulama", ["e-nabız", "enabiz"]),
    "sgk":      ("Sosyal Güvenlik Kurumu", (20, 90, 170), "S", "sgk-online", ["sgk", "sosyal güvenlik"]),
    "banka":    ("Bankan · Mobil Şube", (16, 120, 90), "₺", "bankan-internet-subesi", ["banka", "mobil bankacılık", "internet şubesi", "kredi kartı", "hesabına"]),
    "hakem":    ("Tüketici Hakem Heyeti", (30, 70, 150), "T", "tuketici-basvuru", ["hakem heyeti", "tübis", "tüketici"]),
    "uyap":     ("UYAP Vatandaş", (40, 50, 90), "U", "uyap-vatandas", ["uyap", "dava", "icra", "mahkeme"]),
    "vergi":    ("Vergi Dairesi Online", (110, 40, 140), "V", "vergi-online", ["vergi", "gib", "beyanname"]),
    "tapu":     ("Tapu Online", (150, 90, 30), "T", "tapu-online", ["tapu", "web tapu"]),
    "ptt":      ("PTT Online", (230, 180, 20), "P", "ptt-online", ["ptt"]),
    "operator": ("Operatörüm", (40, 90, 200), "O", "operatorum-app", ["operatör", "hat", "fatura itiraz", "gsm"]),
    "kargo":    ("Kargom", (240, 120, 20), "K", "kargom-takip", ["kargo", "gönderi"]),
    "eticaret": ("Alışveriş Sitesi", (240, 100, 30), "A", "alisveris-sitesi / siparislerim", ["sipariş", "e-ticaret", "iade talebi", "satıcı"]),
    "ilan":     ("İlan Sitesi", (240, 190, 0), "İ", "ilan-sitesi", ["sahibinden", "ilan"]),
    "kvkk":     ("KVK Kurumu · Başvuru", (60, 60, 70), "K", "kvkk-basvuru", ["kvkk", "kişisel veri"]),
    "isverenlik": ("İŞKUR Online", (200, 60, 30), "İ", "iskur-online", ["işkur", "işsizlik"]),
    "eposta":   ("E-Posta", (60, 110, 230), "@", "eposta", ["e-posta", "mail"]),
    "sabim":    ("Sağlık Şikâyet Hattı", (190, 30, 40), "S", "saglik-sikayet", ["sabim", "sağlık bakanlığı"]),
}


def theme_for(text, default="edevlet"):
    t = text.lower()
    best, score = default, 0
    for k, (_, _, _, _, kws) in THEMES.items():
        s = sum(t.count(w) for w in kws)
        if s > score:
            best, score = k, s
    return best


def rgba(c, a=255):
    return (c[0], c[1], c[2], a)


# ---------------------------------------------------------------- WIDGET'LAR
# Widget = dict(id, kind, label, value, options...). Durum = dict(id -> durum).
#   kind: "search" | "field" | "radio" | "select" | "textarea" | "upload" | "table" | "button" | "info" | "list"
#   durum: field/search/textarea -> (yazılan_karakter_sayısı, odak)  ; radio/select -> seçili mi (bool)
#          upload -> ilerleme 0..10 ; table/list -> vurgulu satır (int|-1) ; button -> basılı (bool)

def _wh(kind, mobile):
    if mobile:
        return {"search": 70, "field": 104, "radio": 70, "select": 104, "textarea": 230, "upload": 64, "table": 280,
                "button": 76, "info": 100, "list": 300}[kind]
    return {"search": 80, "field": 110, "radio": 80, "select": 110, "textarea": 230, "upload": 70, "table": 300,
            "button": 76, "info": 80, "list": 320}[kind]


def layout(widgets, mobile, W, top):
    """Widget kutularını hesaplar. Web: iki sütun (sol: giriş alanları/tablo, sağ: yükleme+buton). Mobil: tek sütun."""
    boxes = {}
    if mobile:
        y = top
        for w in widgets:
            h = _wh(w["kind"], True)
            boxes[w["id"]] = (20, y, W - 20, y + h)
            y += h + 14
        return boxes
    lx0, lx1, rx0, rx1 = 60, 1000, 1080, W - 60
    yl = yr = top
    right_kinds = ("upload", "button")
    for w in widgets:
        h = _wh(w["kind"], False)
        if w["kind"] == "search":
            boxes[w["id"]] = (324, top + 20, 1300, top + 20 + h)
            yl = yr = top + 20 + h + 30
        elif w["kind"] in right_kinds:
            boxes[w["id"]] = (rx0, yr, rx1, yr + h)
            yr += h + 14
        else:
            boxes[w["id"]] = (lx0, yl, lx1, yl + h)
            yl += h + 16
    return boxes


def _field(d, box, label, shown, focus, mobile, select=False):
    x0, y0, x1, y1 = box
    fs = 22 if mobile else 22
    dtext(d, (x0, y0 + 2), label, "bold", fs, (70, 70, 70, 255))
    iy0 = y0 + 36
    d.rounded_rectangle([x0 * SS, iy0 * SS, x1 * SS, y1 * SS], 10 * SS, fill=WHITE,
                        outline=RED if focus else (190, 190, 190, 255), width=(4 if focus else 2) * SS)
    tsz = 28 if not mobile else 26
    dtext(d, (x0 + 18, (iy0 + y1) / 2), shown, "bold", tsz, INK, "lm")
    if select:
        dtext(d, (x1 - 20, (iy0 + y1) / 2), "▾", "black", 24, GREYT, "rm")
    if focus:
        cx = x0 + 18 + font("bold", tsz * SS).getlength(shown) / SS + 3
        d.rectangle([cx * SS, (iy0 + 14) * SS, (cx + 3) * SS, (y1 - 14) * SS], fill=INK)


def draw_widget(d, w, st, box, color, mobile):
    k = w["kind"]
    x0, y0, x1, y1 = box
    if k in ("field", "select"):
        n, focus = st if st else (0, False)
        val = w.get("value", "")
        shown = val[:n] if k == "field" else (val if n else "")
        _field(d, box, w.get("label", ""), shown, focus, mobile, select=(k == "select"))
    elif k == "search":
        n, focus = st if st else (0, False)
        val = w.get("value", "")
        d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], 12 * SS, fill=WHITE,
                            outline=RED if focus else (190, 190, 190, 255), width=(4 if focus else 3) * SS)
        shown = val[:n]
        dtext(d, (x0 + 24, (y0 + y1) / 2), shown or "Hizmet ara…", "semi", 30 if not mobile else 26,
              INK if shown else (165, 165, 165, 255), "lm")
        if focus:
            cx = x0 + 24 + font("semi", (30 if not mobile else 26) * SS).getlength(shown) / SS + 3
            d.rectangle([cx * SS, (y0 + 18) * SS, (cx + 3) * SS, (y1 - 18) * SS], fill=INK)
    elif k == "radio":
        sel = bool(st)
        opts = w.get("options", ["Seçenek"])
        n = len(opts)
        bw = (x1 - x0 - (n - 1) * 12) / n
        for i, o in enumerate(opts):
            bx0 = x0 + i * (bw + 12)
            on = sel and i == w.get("pick", 0)
            d.rounded_rectangle([bx0 * SS, (y0 + 10) * SS, (bx0 + bw) * SS, (y1 - 10) * SS], 10 * SS,
                                fill=(255, 236, 236, 255) if on else WHITE, outline=RED if on else LINE, width=3 * SS)
            d.ellipse([(bx0 + 12) * SS, ((y0 + y1) / 2 - 10) * SS, (bx0 + 32) * SS, ((y0 + y1) / 2 + 10) * SS],
                      outline=INK, width=3 * SS, fill=RED if on else WHITE)
            dtext(d, (bx0 + 42, (y0 + y1) / 2), o, "bold", 20 if mobile else 22, INK, "lm")
    elif k == "textarea":
        n, focus = st if st else (0, False)
        dtext(d, (x0, y0 + 2), w.get("label", "Metin"), "bold", 22, (70, 70, 70, 255))
        d.rounded_rectangle([x0 * SS, (y0 + 36) * SS, x1 * SS, y1 * SS], 10 * SS, fill=WHITE,
                            outline=RED if focus else (190, 190, 190, 255), width=(4 if focus else 2) * SS)
        lines = w.get("lines", [])
        left = n
        for i, ln in enumerate(lines):
            if left <= 0:
                break
            dtext(d, (x0 + 16, y0 + 50 + i * 40), ln[:left], "semi", 22 if mobile else 25, INK)
            left -= len(ln)
    elif k == "upload":
        p = (st or 0) / 10
        done = p >= 1
        d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], 12 * SS, fill=(240, 250, 244, 255) if done else (248, 248, 248, 255),
                            outline=GREEN if done else LINE, width=3 * SS)
        nm = w.get("value", "Belge.pdf")
        d.rounded_rectangle([(x0 + 14) * SS, (y0 + 12) * SS, (x0 + 54) * SS, (y1 - 12) * SS], 6 * SS,
                            fill=RED if nm.endswith("pdf") else (40, 90, 220, 255))
        dtext(d, (x0 + 70, y0 + 10), nm, "bold", 22, INK)
        if p <= 0:
            d.rounded_rectangle([(x1 - 130) * SS, (y0 + 14) * SS, (x1 - 14) * SS, (y1 - 14) * SS], 10 * SS, fill=rgba(color))
            dtext(d, (x1 - 72, (y0 + y1) / 2), "Yükle", "black", 20, WHITE, "mm")
        else:
            bx0, bx1 = x0 + 70, x1 - 70
            d.rounded_rectangle([bx0 * SS, (y1 - 22) * SS, bx1 * SS, (y1 - 12) * SS], 5 * SS, fill=(225, 225, 225, 255))
            d.rounded_rectangle([bx0 * SS, (y1 - 22) * SS, (bx0 + (bx1 - bx0) * min(1, p)) * SS, (y1 - 12) * SS], 5 * SS, fill=GREEN)
            if done:
                ck = icon_check(36)
                d._image.alpha_composite(ck.resize((ck.width * SS, ck.height * SS)), (int((x1 - 52) * SS), int(((y0 + y1) / 2 - 18) * SS)))
    elif k in ("table", "list"):
        hl = st if st is not None else -1
        rows = w.get("rows", [])
        dtext(d, (x0, y0 + 2), w.get("label", ""), "black", 26 if not mobile else 24, INK)
        rh = (y1 - y0 - 44) / max(1, len(rows))
        for i, r in enumerate(rows):
            ry = y0 + 40 + i * rh
            on = i == hl
            d.rounded_rectangle([x0 * SS, ry * SS, x1 * SS, (ry + rh - 8) * SS], 12 * SS,
                                fill=(236, 248, 241, 255) if on else (248, 248, 248, 255), outline=GREEN if on else LINE,
                                width=(4 if on else 2) * SS)
            a, b = (r + ("",))[:2] if isinstance(r, tuple) else (r, "")
            dtext(d, (x0 + 20, ry + (rh - 8) / 2), a, "bold", 24 if not mobile else 22, INK, "lm")
            if b:
                dtext(d, (x1 - 20, ry + (rh - 8) / 2), b, "black", 26 if not mobile else 22, GREEN if on else INK, "rm")
    elif k == "button":
        pressed = bool(st)
        c = color if not pressed else tuple(max(0, v - 40) for v in color)
        d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], 12 * SS, fill=rgba(c))
        dtext(d, ((x0 + x1) / 2, (y0 + y1) / 2), w.get("label", "Gönder"), "black", 28, WHITE, "mm")
    elif k == "info":
        d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], 12 * SS, fill=(236, 243, 255, 255), outline=(190, 210, 245, 255), width=2 * SS)
        dtext(d, (x0 + 20, (y0 + y1) / 2), w.get("value", ""), "semi", 22 if mobile else 24, (40, 60, 110, 255), "lm")


def _header(d, theme, W, mobile):
    name, col, logo, _, _ = THEMES[theme]
    h = 150 if mobile else 92
    if mobile:
        d.rounded_rectangle([0, 0, W * SS, h * SS], 40 * SS, fill=rgba(col))
        d.rectangle([0, 100 * SS, W * SS, h * SS], fill=rgba(col))
        for k in range(3):
            d.rounded_rectangle([26 * SS, (84 + k * 12) * SS, 62 * SS, (90 + k * 12) * SS], 3 * SS, fill=WHITE)
        dtext(d, (W / 2, 104), name if len(name) < 22 else name.split("·")[0].strip(), "black", 30, WHITE, "mm")
    else:
        d.rectangle([0, 0, W * SS, h * SS], fill=rgba(col))
        d.rounded_rectangle([36 * SS, 18 * SS, 92 * SS, 74 * SS], 14 * SS, fill=WHITE)
        dtext(d, (64, 46), logo, "black", 34, rgba(col), "mm")
        dtext(d, (110, 46), name, "black", 30, WHITE, "lm")
        d.ellipse([(W - 260) * SS, 26 * SS, (W - 220) * SS, 66 * SS], fill=(255, 255, 255, 120))
        dtext(d, (W - 206, 46), "A**** Y*****", "bold", 22, WHITE, "lm")
    return h


def page_size(mobile):
    return (438, 800) if mobile else (1748, 722)


def render_page(theme, title, widgets, states, mobile, suggestions=None):
    """Bir portal sayfasını çizer. states: dict id->durum. suggestions: (metin, alt_metin, hover) arama önerisi."""
    def fz(v):
        return tuple(fz(x) for x in v) if isinstance(v, (list, tuple)) else v
    return _render_cached(theme, title, tuple(tuple(sorted((k, fz(v)) for k, v in w.items())) for w in widgets),
                          tuple(sorted(states.items())), mobile, suggestions)


@lru_cache(maxsize=4096)
def _render_cached(theme, title, widgets_t, states_t, mobile, suggestions):
    widgets = [dict(w) for w in widgets_t]
    states = dict(states_t)
    W, H = page_size(mobile)
    im, d = canvas(W, H)
    if mobile:
        d.rounded_rectangle([0, 0, W * SS, H * SS], 40 * SS, fill=(246, 248, 250, 255))
    else:
        d.rectangle([0, 0, W * SS, H * SS], fill=WHITE)
    col = THEMES[theme][1]
    top = _header(d, theme, W, mobile)
    if title:
        dtext(d, (24 if mobile else 60, top + 20), title, "black", 28 if mobile else 36, INK)
        top += 70 if mobile else 80
    boxes = layout(widgets, mobile, W, top)
    for w in widgets:
        draw_widget(d, w, states.get(w["id"]), boxes[w["id"]], col, mobile)
    if suggestions:
        sw = next((w for w in widgets if w["kind"] == "search"), None)
        if sw:
            x0, y0, x1, y1 = boxes[sw["id"]]
            text, sub, hover = suggestions
            d.rounded_rectangle([x0 * SS, (y1 - 4) * SS, x1 * SS, (y1 + 90) * SS], 12 * SS, fill=WHITE, outline=(190, 190, 190, 255), width=3 * SS)
            if hover:
                d.rectangle([(x0 + 4) * SS, y1 * SS, (x1 - 4) * SS, (y1 + 86) * SS], fill=(255, 236, 235, 255))
            d.rounded_rectangle([(x0 + 18) * SS, (y1 + 18) * SS, (x0 + 66) * SS, (y1 + 66) * SS], 10 * SS, fill=rgba(col))
            dtext(d, (x0 + 84, y1 + 14), text[:40], "black", 26 if not mobile else 20, INK)
            dtext(d, (x0 + 84, y1 + 52), sub[:44], "semi", 20 if not mobile else 16, GREYT)
    return finish(im)


def widget_boxes(widgets, mobile, title=True):
    W, H = page_size(mobile)
    top = (150 if mobile else 92) + ((70 if mobile else 80) if title else 0)
    return layout(widgets, mobile, W, top)


@lru_cache(maxsize=16)
def success_modal(title, sub, w=760, h=360):
    im, d = card_base(w, h, radius=26)
    ck = icon_check(110)
    im.alpha_composite(ck.resize((ck.width * SS, ck.height * SS)), (int((w / 2 - 55) * SS), 34 * SS))
    dtext(d, (w / 2, 186), title, "black", 42, GREEN, "mm")
    dtext(d, (w / 2, 250), sub, "bold", 28, GREYT, "mm")
    return finish(im)
