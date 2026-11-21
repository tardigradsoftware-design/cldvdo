"""Senaryo: Voltaj dalgalanmasında yanan cihazın parası — DİKEY kısa video. Maskot: Tokmak. Müzik yok."""
import math
import os
import sys
from functools import lru_cache

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from PIL import Image

from engine.core import (BLUE, GREEN, INK, RED, SS, WHITE, YELLOW, canvas, card_base, clamp, dtext, finish, font,
                         out_cubic, path, pill, place, place_anim, prog, render, text_sprite, out_back)
from engine.components import draw_cursor, icon_check, icon_x, stamp
from engine.shorts import Beat, Short, W, H
from engine import audio

OUT = os.environ.get("OUT_DIR", "out")
VOICE = os.environ.get("VOICE")
GREYT = (120, 120, 120, 255)
SMOKE = (150, 150, 150, 255)


def S(v):
    return int(v * SS)


def overlay(img, rgba):
    img.alpha_composite(Image.new("RGBA", img.size, rgba))


def typing(t, t0, text, cps=10):
    return text[: int(clamp((t - t0) * cps, 0, len(text)))]


# ================================================================ çizimler
@lru_cache(maxsize=4)
def bolt(size=260, color=YELLOW):
    im, d = canvas(size, size * 1.3)
    s = SS * size / 100
    pts = [(58, 0), (14, 70), (46, 70), (30, 130), (86, 50), (52, 50), (74, 0)]
    d.polygon([(x * s + 6 * SS, y * s + 6 * SS) for x, y in pts], fill=INK)
    d.polygon([(x * s, y * s) for x, y in pts], fill=color)
    d.line([(x * s, y * s) for x, y in pts + [pts[0]]], fill=INK, width=S(6), joint="curve")
    return finish(im)


@lru_cache(maxsize=8)
def bulb(on=True, size=220):
    im, d = canvas(size, size * 1.35)
    s = SS * size / 100
    col = (255, 226, 90, 255) if on else (205, 205, 205, 255)
    d.ellipse([10 * s, 0, 90 * s, 80 * s], fill=col, outline=INK, width=S(6))
    d.rectangle([32 * s, 74 * s, 68 * s, 104 * s], fill=(150, 156, 168, 255), outline=INK, width=S(5))
    for y in (84, 94):
        d.line([32 * s, y * s, 68 * s, y * s], fill=INK, width=S(4))
    d.line([(40 * s, 70 * s), (46 * s, 40 * s), (54 * s, 52 * s), (60 * s, 40 * s)], fill=INK, width=S(4))
    return finish(im)


@lru_cache(maxsize=8)
def appliance(kind, size=250):
    w, h = size, int(size * (1.5 if kind == "buzdolabi" else 1.0 if kind == "tv" else 1.25))
    im, d = card_base(w, h, fill=WHITE if kind != "tv" else INK, radius=16)
    if kind == "kombi":
        d.rounded_rectangle([S(w * .25), S(h * .14), S(w * .75), S(h * .34)], S(8), fill=(40, 60, 90, 255))
        dtext(d, (w * .5, h * .24), "88°", "black", int(size * .11), (120, 230, 255, 255), "mm")
        for k in range(3):
            d.ellipse([S(w * (.26 + k * .18)), S(h * .45), S(w * (.36 + k * .18)), S(h * .53)], fill=(200, 200, 200, 255), outline=INK, width=S(3))
        for k in range(4):
            x = w * (.22 + k * .18)
            d.rectangle([S(x), S(h * .82), S(x + w * .06), S(h * .98)], fill=(170, 170, 170, 255), outline=INK, width=S(3))
        dtext(d, (w * .5, h * .67), "KOMBİ", "black", int(size * .1), GREYT, "mm")
    elif kind == "tv":
        d.rounded_rectangle([S(w * .07), S(h * .08), S(w * .93), S(h * .8)], S(6), fill=(40, 46, 60, 255))
        d.line([S(w * .2), S(h * .2), S(w * .45), S(h * .55)], fill=(90, 100, 120, 255), width=S(5))
        dtext(d, (w * .5, h * .9), "TV", "black", int(size * .09), WHITE, "mm")
    else:
        d.line([S(8), S(h * .38), S(w - 8), S(h * .38)], fill=INK, width=S(5))
        d.rounded_rectangle([S(w * .78), S(h * .12), S(w * .86), S(h * .3)], S(4), fill=(170, 170, 170, 255), outline=INK, width=S(3))
        d.rounded_rectangle([S(w * .78), S(h * .46), S(w * .86), S(h * .7)], S(4), fill=(170, 170, 170, 255), outline=INK, width=S(3))
        dtext(d, (w * .4, h * .85), "BUZDOLABI", "black", int(size * .085), GREYT, "mm")
    return finish(im)


def smoke(img, x, y, t, t0):
    for k in range(4):
        p = ((t - t0) * 0.8 + k * 0.25) % 1.0
        if t < t0:
            return
        r = 18 + 30 * p
        a = int(170 * (1 - p))
        im, d = canvas(r * 2 + 4, r * 2 + 4)
        d.ellipse([0, 0, S(r * 2), S(r * 2)], fill=(120, 120, 120, a))
        place(img, finish(im), x + math.sin(k * 2 + t * 2) * 14, y - p * 130)


@lru_cache(maxsize=8)
def bill_card(crossed):
    w, h = 640, 420
    im, d = card_base(w, h, header=RED, header_h=78)
    dtext(d, (34, 20), "TAMİR FATURASI", "black", 38, WHITE)
    rows = [("Kombi kartı", "4.200 TL"), ("TV paneli", "6.900 TL"), ("İşçilik", "1.350 TL")]
    for k, (a, b) in enumerate(rows):
        dtext(d, (40, 112 + k * 62), a, "bold", 32, GREYT)
        dtext(d, (w - 40, 112 + k * 62), b, "black", 34, INK, "ra")
    d.line([S(40), S(312), S(w - 40), S(312)], fill=INK, width=S(4))
    dtext(d, (40, 334), "TOPLAM", "black", 38)
    dtext(d, (w - 40, 330), "12.450 TL", "black", 46, RED, "ra")
    return finish(im)


@lru_cache(maxsize=2)
def people(n_know):
    w, h = 720, 520
    im, d = card_base(w, h)
    dtext(d, (w / 2, 40), "10 KİŞİDEN KAÇI BİLİYOR?", "black", 38, INK, "mt")
    for k in range(10):
        cx = 100 + (k % 5) * 130
        cy = 200 + (k // 5) * 170
        col = GREEN if k < n_know else (190, 190, 190, 255)
        d.ellipse([S(cx - 26), S(cy - 70), S(cx + 26), S(cy - 18)], fill=col, outline=INK, width=S(4))
        d.rounded_rectangle([S(cx - 42), S(cy - 10), S(cx + 42), S(cy + 62)], S(30), fill=col, outline=INK, width=S(4))
    return finish(im)


@lru_cache(maxsize=1)
def volt_frame():
    w, h = 820, 520
    im, d = card_base(w, h, header=INK, header_h=80)
    dtext(d, (36, 20), "ŞEBEKE VOLTAJI", "black", 38, WHITE)
    for k, v in enumerate(("380V", "220V", "0V")):
        y = 150 + k * 140
        d.line([S(110), S(y), S(w - 40), S(y)], fill=(225, 225, 225, 255), width=S(3))
        dtext(d, (40, y - 18), v, "bold", 28, GREYT)
    return finish(im)


def volt_curve(x):
    """0-1 arası x için voltaj (px y ofseti). Ortada büyük sıçrama + düşüş."""
    base = math.sin(x * 40) * 10
    spike = 0
    if 0.45 < x < 0.62:
        q = (x - 0.45) / 0.17
        spike = -150 * math.sin(q * math.pi) if q < 0.5 else 0
        if q >= 0.5:
            spike = 150 * math.sin((q - 0.5) * 2 * math.pi) * 0.9
    return base + spike


@lru_cache(maxsize=2)
def tazminat_card():
    w, h = 700, 560
    im, d = card_base(w, h, header=BLUE, header_h=84)
    dtext(d, (34, 22), "ELEKTRİK DAĞITIM ŞİRKETİ", "black", 34, WHITE)
    dtext(d, (40, 122), "Voltaj dalgalanması nedeniyle", "semi", 30, GREYT)
    dtext(d, (40, 162), "oluşan cihaz hasarı", "semi", 30, GREYT)
    d.rounded_rectangle([S(40), S(230), S(w - 40), S(330)], S(16), fill=(236, 248, 241, 255), outline=GREEN, width=S(5))
    dtext(d, (w / 2, 280), "TAZMİN EDİLİR", "black", 50, GREEN, "mm")
    for k in range(4):
        d.rounded_rectangle([S(40), S(370 + k * 40), S(40 + [560, 600, 480, 300][k]), S(388 + k * 40)], S(8), fill=(225, 225, 225, 255))
    return finish(im)


@lru_cache(maxsize=2)
def coin(size=110):
    im, d = canvas(size + 8, size + 8)
    d.ellipse([S(6), S(6), S(size + 6), S(size + 6)], fill=INK)
    d.ellipse([0, 0, S(size), S(size)], fill=(250, 200, 50, 255), outline=INK, width=S(5))
    d.ellipse([S(14), S(14), S(size - 14), S(size - 14)], outline=(210, 150, 20, 255), width=S(4))
    d.text((S(size / 2), S(size / 2)), "₺", font=font("black", S(size * .5)), fill=(170, 110, 10, 255), anchor="mm")
    return finish(im)


@lru_cache(maxsize=32)
def comment_ui(typed, sent, replied):
    w, h = 860, 640
    im, d = card_base(w, h, radius=30)
    dtext(d, (40, 30), "Yorumlar", "black", 38)
    dtext(d, (820, 36), "2.318", "bold", 30, (130, 130, 130, 255), "ra")
    y = 110
    rows = [("emre.k", "Geçen ay kombim yanmıştı!"), ("zeynep_34", "Bunu bilmiyordum, teşekkürler")]
    if sent:
        rows.append(("sen", "ELEKTRİK"))
    for u, m in rows:
        me = u == "sen"
        d.ellipse([S(40), S(y), S(104), S(y + 64)], fill=RED if me else (200, 200, 200, 255), outline=INK, width=S(3))
        dtext(d, (124, y + 2), u, "bold", 26, (110, 110, 110, 255))
        dtext(d, (124, y + 34), m, "black" if me else "semi", 32 if me else 30, RED if me else INK)
        y += 108
    if replied:
        d.rounded_rectangle([S(124), S(y - 6), S(820), S(y + 66)], S(18), fill=(236, 248, 241, 255), outline=GREEN, width=S(4))
        dtext(d, (146, y + 14), "↳ Adım adım rehber DM'de ✓", "black", 30, GREEN)
    d.rounded_rectangle([S(30), S(520), S(690), S(608)], S(44), fill=(244, 244, 244, 255), outline=INK, width=S(4))
    dtext(d, (64, 545), typed if typed else "Yorum ekle...", "black" if typed else "semi", 34, INK if typed else (160, 160, 160, 255))
    d.ellipse([S(710), S(520), S(800), S(610)], fill=RED, outline=INK, width=S(4))
    d.polygon([(S(738), S(545)), (S(782), S(565)), (S(738), S(585))], fill=WHITE)
    return finish(im)


@lru_cache(maxsize=4)
def guide_card(n):
    w, h = 820, 600
    im, d = card_base(w, h, header=INK, header_h=84)
    dtext(d, (36, 22), "ADIM ADIM REHBER", "black", 38, WHITE)
    steps = [("Hasarı belgele", "fotoğraf + servis raporu"), ("Dağıtım şirketine başvur", "yazılı dilekçe ile"),
             ("Tazminatını al", "onarım ya da bedel")]
    for k, (a, b) in enumerate(steps[:n]):
        top = 118 + k * 152
        d.rounded_rectangle([S(30), S(top), S(790), S(top + 130)], S(18), fill=(246, 252, 248, 255), outline=INK, width=S(4))
        d.ellipse([S(54), S(top + 28), S(128), S(top + 102)], fill=RED, outline=INK, width=S(4))
        dtext(d, (91, top + 65), str(k + 1), "black", 40, WHITE, "mm")
        dtext(d, (156, top + 24), a, "black", 38)
        dtext(d, (156, top + 76), b, "semi", 30, (90, 90, 90, 255))
    return finish(im)


# ================================================================ sahne görselleri
def v_hook(img, t, dur, cx, cy):
    # elektrik gidip gelir: karanlık / aydınlık titreme
    flick = [(0.18, 0.3), (0.42, 0.54), (0.66, 0.72)]
    dark = any(a <= t < b for a, b in flick)
    place(img, bulb(not dark, 240), cx - 170, cy - 40)
    place_anim(img, bolt(240), cx + 170, cy - 40, t, dur, "pop", -1, 0.3, -10)
    place_anim(img, stamp("CİHAZIN YANDI MI?", 58), cx, cy + 250, t, dur, "stamp", 0.7, 0.22, -5)
    if dark:
        overlay(img, (10, 10, 20, 150))


def v_appliances(img, t, dur, cx, cy):
    for k, (kind, dx, dy) in enumerate((("kombi", -280, -20), ("tv", 0, 40), ("buzdolabi", 280, -40))):
        sp = appliance(kind, 220)
        place_anim(img, sp, cx + dx, cy + dy, t, dur, "drop", 0.05 + k * 0.35, 0.35)
        if t > 0.5 + k * 0.35:
            smoke(img, cx + dx, cy + dy - sp.height / 2, t, 0.5 + k * 0.35)
            place_anim(img, icon_x(70), cx + dx + 80, cy + dy - sp.height / 2 + 10, t, dur, "pop", 0.55 + k * 0.35, 0.25)


def v_bill(img, t, dur, cx, cy):
    place_anim(img, bill_card(False), cx, cy, t, dur, "pop", 0.0, 0.35)
    if t > 0.9:
        k = out_cubic(prog(t, 0.9, 0.3))
        from PIL import ImageDraw
        dd = ImageDraw.Draw(img)
        x0, y0 = cx - 300, cy - 190
        dd.line([x0, y0, x0 + 600 * k, y0 + 380 * k], fill=RED, width=16)
    place_anim(img, stamp("SEN ÖDEMİYORSUN", 62, GREEN), cx, cy + 290, t, dur, "stamp", 1.25, 0.22, -6)


def v_people(img, t, dur, cx, cy):
    place_anim(img, people(1 if t > 1.0 else 0), cx, cy, t, dur, "pop", 0.0, 0.35)
    place_anim(img, text_sprite("?", "black", 120, RED, 6, WHITE), cx + 330, cy - 240, t, dur, "pop", 0.6, 0.3, 12)


def v_volt(img, t, dur, cx, cy):
    fr = volt_frame()
    place_anim(img, fr, cx, cy, t, dur, "up", 0.0, 0.35)
    if t < 0.3:
        return
    from PIL import ImageDraw
    dd = ImageDraw.Draw(img)
    x0, x1 = cx - fr.width / 2 + 120, cx + fr.width / 2 - 50
    ymid = cy - fr.height / 2 + 290
    p = prog(t, 0.3, 1.4)
    pts = []
    for k in range(int(220 * p) + 1):
        x = k / 220
        pts.append((x0 + (x1 - x0) * x, ymid + volt_curve(x)))
    if len(pts) > 1:
        bad = [q for q in pts if abs(q[1] - ymid) > 40]
        dd.line(pts, fill=BLUE, width=10, joint="curve")
        if bad:
            dd.line(bad, fill=RED, width=12, joint="curve") if len(bad) > 1 else None
    if p > 0.6:
        place_anim(img, stamp("DALGALANMA!", 56), cx + 120, cy - 330, t, dur, "stamp", 0.3 + 1.4 * 0.6, 0.22, 6)


def v_company(img, t, dur, cx, cy):
    place_anim(img, tazminat_card(), cx, cy, t, dur, "pop", 0.0, 0.38)
    place_anim(img, stamp("ZORUNLU", 64, INK), cx + 220, cy + 300, t, dur, "stamp", 1.0, 0.22, -10)


def v_coins(img, t, dur, cx, cy):
    for k in range(9):
        t0 = 0.1 + k * 0.12
        if t < t0:
            continue
        x = cx - 240 + (k % 5) * 120 + (k // 5) * 60
        yt = cy + 120 - (k // 5) * 90
        y = min(yt, cy - 500 + (t - t0) * 2200)
        place(img, coin(120), x, y)
    v = int(12450 * out_cubic(prog(t, 0.2, 1.4)))
    place(img, text_sprite(f"{v:,}".replace(",", ".") + " TL", "black", 110, GREEN, 6, WHITE), cx, cy - 210)
    place_anim(img, pill("GERİ ALIRSIN ✓", "black", 50, WHITE, GREEN, border=4, pad=(26, 12), shadow=6), cx, cy + 300, t, dur, "pop", 1.5, 0.3)


def v_comment(img, t, dur, cx, cy):
    word = "ELEKTRİK"
    typed = typing(t, 0.4, word, 11)
    sent = t > 1.45
    place_anim(img, comment_ui("" if sent else typed, sent, t > 2.1), cx, cy, t, dur, "pop", 0.0, 0.35)
    x, y = path(t, [(0, cx + 300, cy + 420), (1.0, cx + 300, cy + 420), (1.35, cx + 330, cy + 250)])
    draw_cursor(img, x, y, t, (1.4,), 60)


def v_guide(img, t, dur, cx, cy):
    n = 1 + int(t > 0.6) + int(t > 1.2)
    place_anim(img, guide_card(n), cx, cy, t, dur, "pop", 0.0, 0.35)
    place_anim(img, stamp("DM'DE GÖNDERİYORUM", 50, GREEN), cx, cy + 340, t, dur, "stamp", 1.6, 0.22, -4)


# ================================================================ üst sayaç
REVEAL_T = None


def top_counter(img, t):
    val = "?" if (REVEAL_T is None or t < REVEAL_T) else "0 TL"
    col = INK if val == "?" else GREEN
    lab = pill("SENİN ÖDEYECEĞİN", "black", 34, INK, WHITE, border=4, pad=(20, 10), shadow=5)
    num = pill(val, "black", 34, WHITE, col, border=4, pad=(18, 10), shadow=5)
    x0 = 540 - (lab.width + num.width + 8) / 2
    place(img, lab, x0, 120, anchor="l")
    sc = out_back((t - REVEAL_T) / 0.3) if (REVEAL_T and 0 <= t - REVEAL_T < 0.3) else 1.0
    place(img, num, x0 + lab.width + 8 + num.width / 2, 120, scale=sc)


# ================================================================ senaryo (TTS metniyle birebir)
def build():
    global REVEAL_T
    keys = [(0.4 + k / 11, "key") for k in range(8)]
    beats = [
        Beat(2.4, ("ELEKTRİK", "GİDİP GELDİ"), "elektrik gidip *GELDİĞİNDE*", v_hook, "saskin",
             [(0.0, "impact"), (0.18, "click"), (0.42, "click"), (0.7, "impact")], punch=True),
        Beat(3.2, ("KOMBİ, TV,", "BUZDOLABI YANDI"), "kombin televizyonun veya *BUZDOLABIN* yandıysa", v_appliances, "endiseli",
             [(0.5, "error"), (0.85, "error"), (1.2, "error")]),
        Beat(3.2, ("TAMİR PARASI", "SENDEN ÇIKMAZ"), "tamir parasını *CEBİNDEN* ödemek zorunda değilsin", v_bill, "ciddi:isaret",
             [(0.9, "whoosh"), (1.25, "impact")]),
        Beat(2.0, ("ÇOĞU KİŞİ", "BİLMEZ"), "çoğu kişi *BİLMEZ* ama", v_people, "dusunceli", [(0.6, "pop")]),
        Beat(3.0, ("VOLTAJ", "DALGALANMASI"), "voltaj *DALGALANMASINDAN* doğan cihaz hasarını", v_volt, "saskin",
             [(0.3, "riser"), (1.15, "error"), (1.15, "impact")]),
        Beat(2.8, ("DAĞITIM ŞİRKETİ", "ÖDEMEK ZORUNDA"), "elektrik *DAĞITIM ŞİRKETİ*", v_company, "ciddi:isaret",
             [(0.1, "ding"), (1.0, "impact")]),
        Beat(2.8, ("KURUŞU", "KURUŞUNA"), "*KURUŞU KURUŞUNA* karşılamak zorunda", v_coins, "heyecanli:kutlama",
             [(0.1 + k * 0.12 + 0.2, "tick") for k in range(9)] + [(1.5, "ding")]),
        Beat(3.6, ("YORUMA", "ELEKTRİK YAZ"), "yorumlara *ELEKTRİK* yaz", v_comment, "goz_kirp",
             keys + [(1.4, "click"), (2.1, "ding")]),
        Beat(3.4, ("ADIM ADIM", "REHBER HAZIR"), "adım adım rehberi hemen *GÖNDEREYİM*", v_guide, "mutlu:kutlama",
             [(0.0, "ding"), (0.6, "ding"), (1.2, "ding"), (1.6, "impact")]),
    ]
    sh = Short(beats, top=top_counter, voice=VOICE)
    REVEAL_T = sh.starts[6] + 1.5
    return sh


def main():
    os.makedirs(OUT, exist_ok=True)
    sh = build()
    print(f"süre: {sh.duration:.1f} sn")
    wav = audio.mix(sh.duration, sh.events(), os.path.join(OUT, "elektrik_audio.wav"), voice_path=VOICE,
                    voice_offset=sh.voice_offset)
    render(sh.frame, sh.duration, (W, H), os.path.join(OUT, "elektrik_dikey.mp4"), wav)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        sh = build()
        ts = [float(x) for x in sys.argv[2:]] or [s + b.dur * 0.8 for s, b in zip(sh.starts, sh.beats)]
        ims = [sh.frame(x).convert("RGB").resize((270, 480)) for x in ts]
        cols = 5
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (270 * cols, 480 * rows), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * 270, (k // cols) * 480))
        os.makedirs(OUT, exist_ok=True)
        sheet.save(os.path.join(OUT, "preview_elektrik.jpg"))
    else:
        main()
