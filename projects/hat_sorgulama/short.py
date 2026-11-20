"""Senaryo: 'Adına gizli hat açılmış mı?' — DİKEY kısa video (Shorts/Reels/TikTok)."""
import math
import os
import sys
from functools import lru_cache

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from engine.core import (BLUE, GREEN, GREY, INK, RED, SS, WHITE, YELLOW, card_base, dtext, finish, font, out_back,
                         out_cubic, pill, place, place_anim, prog, render, text_sprite, canvas, clamp, path)
from engine.components import (cursor_sprite, draw_cursor, icon_check, icon_warn, sim_card, stamp)
from engine.shorts import Beat, Short, W, H
from engine import audio

OUT = os.environ.get("OUT_DIR", "out")
VOICE = os.environ.get("VOICE")  # TTS dosyası (bölümler arası ~1 sn sessizlik)


def S(v):
    return v * SS


# ================================================================ görseller
def v_hook(img, t, dur, cx, cy):
    for k, (col, dx, rot) in enumerate([(RED, -230, 14), (BLUE, 0, 0), (GREEN, 230, -14)]):
        place_anim(img, sim_card(190, col), cx + dx, cy - 20 + abs(dx) * 0.15, t, dur, "drop", -1 + 0 * k, 0.3, rot)
    for k, dx in enumerate((-230, 0, 230)):
        place_anim(img, text_sprite("?", "black", 130, WHITE, 6, INK), cx + dx, cy - 250, t, dur, "pop", -1 if k == 0 else 0.15 * k, 0.3)
    place_anim(img, stamp("SENİN Mİ?", 72), cx, cy + 230, t, dur, "stamp", 0.8, 0.25, -6)


@lru_cache(maxsize=1)
def id_card():
    w, h = 700, 430
    im, d = card_base(w, h, header=BLUE, header_h=78)
    dtext(d, (34, 22), "KİMLİK BİLGİLERİ", "black", 36, WHITE)
    d.rounded_rectangle([S(40), S(115), S(220), S(355)], S(16), fill=(225, 230, 240, 255), outline=INK, width=S(4))
    d.ellipse([S(90), S(150), S(170), S(230)], fill=(150, 160, 180, 255))
    d.rounded_rectangle([S(70), S(240), S(190), S(340)], S(40), fill=(150, 160, 180, 255))
    rows = [("AD SOYAD", "A**** Y*****"), ("KİMLİK NO", "1•••••••••8"), ("DOĞUM", "••.••.19••")]
    for k, (a, b) in enumerate(rows):
        dtext(d, (260, 125 + k * 82), a, "bold", 24, (120, 120, 120, 255))
        dtext(d, (260, 155 + k * 82), b, "black", 38, INK)
    return finish(im)


def v_id(img, t, dur, cx, cy):
    place_anim(img, id_card(), cx, cy, t, dur, "pop", 0.05, 0.4)
    for k in range(3):
        p = prog(t, 0.9 + k * 0.18, 0.6)
        if p > 0:
            place(img, text_sprite("•", "black", 90, RED), cx - 120 + k * 120, cy + 230 + out_cubic(p) * 120, alpha=1 - p)
    place_anim(img, stamp("SIZDI", 84), cx + 170, cy - 170, t, dur, "stamp", 0.75, 0.22, -12)


@lru_cache(maxsize=1)
def phone_body(w=470, h=720):
    im, d = canvas(w + 14, h + 14)
    d.rounded_rectangle([S(14), S(14), S(w + 14), S(h + 14)], S(64), fill=INK)
    d.rounded_rectangle([0, 0, S(w), S(h)], S(64), fill=INK)
    d.rounded_rectangle([S(14), S(14), S(w - 14), S(h - 14)], S(52), fill=(246, 246, 246, 255))
    d.rounded_rectangle([S(w / 2 - 60), S(30), S(w / 2 + 60), S(58)], S(14), fill=INK)
    return finish(im)


@lru_cache(maxsize=16)
def notif(app, msg, color):
    w, h = 410, 130
    im, d = card_base(w, h, border=4, radius=24, shadow=6)
    d.rounded_rectangle([S(20), S(22), S(70), S(72)], S(12), fill=color, outline=INK, width=S(3))
    dtext(d, (86, 22), app, "black", 22, (110, 110, 110, 255))
    dtext(d, (370, 24), "şimdi", "med", 18, (140, 140, 140, 255), "ra")
    y = 54
    line = ""
    for word in msg.split():
        test = (line + " " + word).strip()
        if font("bold", 25 * SS).getlength(test) / SS > 300:
            dtext(d, (86, y), line, "bold", 25)
            y += 32
            line = word
        else:
            line = test
    dtext(d, (86, y), line, "bold", 25)
    return finish(im)


def v_phone(img, t, dur, cx, cy):
    place_anim(img, phone_body(), cx, cy - 10, t, dur, "up", 0.0, 0.35)
    items = [("OPERATÖR", "Yeni hattınız aktifleştirildi.", GREEN),
             ("BANKA", "Kredi başvurunuz alındı.", BLUE),
             ("SMS", "Doğrulama kodunuz: 4821", RED)]
    for k, (a, m, c) in enumerate(items):
        place_anim(img, notif(a, m, c), cx, cy - 220 + k * 160, t, dur, "drop", 0.35 + k * 0.6, 0.35)


def v_invoice(img, t, dur, cx, cy):
    w, h = 660, 560
    base, d = card_base(w, h, header=RED, header_h=80)
    dtext(d, (34, 22), "BORÇ BİLDİRİMİ", "black", 38, WHITE)
    rows = [("Hat", "05** *** ** 17"), ("Abone", "SEN"), ("Durum", "Ödenmedi")]
    for k, (a, b) in enumerate(rows):
        dtext(d, (40, 120 + k * 70), a, "bold", 30, (120, 120, 120, 255))
        dtext(d, (w - 40, 120 + k * 70), b, "black", 34, RED if k == 2 else INK, "ra")
    d.line([S(40), S(340), S(w - 40), S(340)], fill=INK, width=S(4))
    dtext(d, (40, 372), "TOPLAM", "black", 34)
    card = finish(base)
    place_anim(img, card, cx, cy, t, dur, "pop", 0.0, 0.38)
    if t > 0.3:
        v = int(48750 * out_cubic(prog(t, 0.35, 1.3)))
        s = f"{v:,}".replace(",", ".") + " TL"
        place(img, text_sprite(s, "black", 92, RED), cx, cy + 190)
    place_anim(img, stamp("SENİN ADINA", 62, INK), cx + 170, cy - 345, t, dur, "stamp", 1.4, 0.22, 8)


def v_stopwatch(img, t, dur, cx, cy):
    im, d = canvas(460, 520)
    d.rounded_rectangle([S(200), 0, S(260), S(50)], S(8), fill=INK)
    d.ellipse([S(14), S(74), S(454), S(514)], fill=INK)
    d.ellipse([0, S(60), S(440), S(500)], fill=WHITE, outline=INK, width=S(10))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        r0, r1 = 180, 200
        d.line([S(220 + r0 * math.sin(a)), S(280 - r0 * math.cos(a)), S(220 + r1 * math.sin(a)), S(280 - r1 * math.cos(a))], fill=INK, width=S(7))
    face = finish(im)
    place_anim(img, face, cx, cy - 30, t, dur, "pop", 0.0, 0.35)
    if t > 0.2:
        p = prog(t, 0.25, dur - 0.75)
        a = p * math.pi * 1.0
        from PIL import ImageDraw
        dd = ImageDraw.Draw(img)
        ox, oy = cx, cy - 30 + 25
        dd.pieslice([ox - 170, oy - 170, ox + 170, oy + 170], -90, -90 + math.degrees(a), fill=(232, 52, 46, 90))
        dd.line([ox, oy, ox + 170 * math.sin(a), oy - 170 * math.cos(a)], fill=RED, width=12)
        dd.ellipse([ox - 16, oy - 16, ox + 16, oy + 16], fill=INK)
        sec = int(30 * p)
        place(img, pill(f"{sec:02d} sn", "black", 58, WHITE, INK, pad=(22, 10)), cx, cy + 300)


@lru_cache(maxsize=64)
def search_card(typed, focus):
    w, h = 820, 330
    im, d = card_base(w, h, header=(235, 235, 235, 255), header_h=62)
    for k, c in enumerate([(255, 95, 86, 255), (255, 189, 46, 255), (39, 201, 63, 255)]):
        d.ellipse([S(28 + k * 30), S(24), S(48 + k * 30), S(44)], fill=c)
    d.rounded_rectangle([S(140), S(16), S(780), S(50)], S(10), fill=WHITE)
    dtext(d, (160, 21), "turkiye.gov.tr", "semi", 22, (90, 90, 90, 255))
    dtext(d, (44, 100), "Size nasıl yardımcı olabilirim?", "bold", 30, (90, 90, 90, 255))
    d.rounded_rectangle([S(40), S(160), S(640), S(250)], S(14), fill=WHITE, outline=RED if focus else INK, width=S(5))
    shown = typed if typed else "Hizmet ara..."
    dtext(d, (66, 186), shown, "bold", 36, INK if typed else (170, 170, 170, 255))
    if focus:
        x = 66 + font("bold", 36 * SS).getlength(typed) / SS + 4
        d.rectangle([S(x), S(182), S(x + 4), S(228)], fill=INK)
    d.rounded_rectangle([S(660), S(160), S(780), S(250)], S(14), fill=RED, outline=INK, width=S(5))
    dtext(d, (720, 205), "ARA", "black", 32, WHITE, "mm")
    return finish(im)


QUERY = "mobil hat sorgulama"


def typing(t, t0, text, cps=13):
    n = int(clamp((t - t0) * cps, 0, len(text)))
    return text[:n]


def v_search(img, t, dur, cx, cy):
    typed = typing(t, 0.6, QUERY)
    place_anim(img, search_card(typed, t > 0.4), cx, cy, t, dur, "pop", 0.0, 0.35)
    # imleç: alana gelir, sonra ARA'ya
    x, y = path(t, [(0, cx + 300, cy + 380), (0.35, cx - 120, cy + 60), (2.4, cx - 120, cy + 60), (2.8, cx + 300, cy + 60)])
    draw_cursor(img, x, y, t, (0.4, 2.85), 60)


@lru_cache(maxsize=8)
def results_card(hl):
    w, h = 840, 560
    im, d = card_base(w, h)
    dtext(d, (40, 34), "Arama sonuçları: “mobil hat sorgulama”", "bold", 28, (110, 110, 110, 255))
    y = 96
    for k in range(3):
        top = y + k * 145
        fill = (255, 236, 235, 255) if (hl and k == 0) else (248, 248, 248, 255)
        d.rounded_rectangle([S(30), S(top), S(810), S(top + 125)], S(16), fill=fill,
                            outline=RED if (hl and k == 0) else (210, 210, 210, 255), width=S(4))
        if k == 0:
            d.rounded_rectangle([S(54), S(top + 28), S(124), S(top + 98)], S(14), fill=BLUE, outline=INK, width=S(3))
            dtext(d, (89, top + 63), "BTK", "black", 22, WHITE, "mm")
            dtext(d, (148, top + 26), "Mobil Hat Sorgulama", "black", 38)
            dtext(d, (148, top + 76), "Bilgi Teknolojileri ve İletişim Kurumu", "semi", 24, (110, 110, 110, 255))
        else:
            d.rounded_rectangle([S(54), S(top + 28), S(124), S(top + 98)], S(14), fill=(220, 220, 220, 255))
            d.rounded_rectangle([S(148), S(top + 34), S(148 + 420 - k * 60), S(top + 60)], S(8), fill=(220, 220, 220, 255))
            d.rounded_rectangle([S(148), S(top + 76), S(148 + 300), S(top + 96)], S(8), fill=(232, 232, 232, 255))
    return finish(im)


def v_results(img, t, dur, cx, cy):
    place_anim(img, results_card(t > 1.55), cx, cy, t, dur, "up", 0.0, 0.35)
    x, y = path(t, [(0, cx + 330, cy + 360), (0.5, cx + 330, cy + 300), (1.45, cx - 60, cy - 110)])
    draw_cursor(img, x, y, t, (1.55,), 60)


@lru_cache(maxsize=8)
def table_card(stage):
    w, h = 840, 600
    im, d = card_base(w, h, header=INK, header_h=84)
    dtext(d, (36, 22), "ADINIZA KAYITLI HATLAR", "black", 36, WHITE)
    dtext(d, (40, 112), "Operatör", "bold", 26, (120, 120, 120, 255))
    dtext(d, (800, 112), "Hat sayısı", "bold", 26, (120, 120, 120, 255), "ra")
    rows = [("Turkcell", "1"), ("Vodafone", "2"), ("Türk Telekom", "0")]
    for k, (a, b) in enumerate(rows):
        top = 160 + k * 135
        bad = stage >= 1 and k == 1
        d.rounded_rectangle([S(28), S(top), S(812), S(top + 115)], S(16),
                            fill=(255, 232, 230, 255) if bad else (247, 247, 247, 255),
                            outline=RED if bad else (215, 215, 215, 255), width=S(5 if bad else 3))
        dtext(d, (60, top + 34), a, "black", 42)
        dtext(d, (780, top + 26), b, "black", 56, RED if bad else INK, "ra")
    return finish(im)


def v_table(img, t, dur, cx, cy):
    place_anim(img, table_card(1 if t > 1.3 else 0), cx, cy, t, dur, "pop", 0.0, 0.38)
    place_anim(img, stamp("1 TANESİ SENİN DEĞİL!", 50), cx + 40, cy + 330, t, dur, "stamp", 1.4, 0.22, -5)
    place_anim(img, icon_warn(110), cx + 400, cy - 130, t, dur, "pop", 1.3, 0.3)


@lru_cache(maxsize=8)
def checklist(n):
    w, h = 860, 560
    im, d = card_base(w, h)
    dtext(d, (40, 34), "HEMEN YAP:", "black", 40, RED)
    items = [("Operatöre başvur,", "hattı kapattır"), ("Savcılığa", "suç duyurusu yap"), ("Belgeleri", "sakla (ekran görüntüsü)")]
    for k, (a, b) in enumerate(items[:n]):
        top = 120 + k * 145
        d.rounded_rectangle([S(30), S(top), S(830), S(top + 122)], S(18), fill=(244, 252, 247, 255), outline=INK, width=S(4))
        ck = icon_check(64)
        dtext(d, (150, top + 20), a, "black", 38)
        dtext(d, (150, top + 66), b, "semi", 32, (90, 90, 90, 255))
        im.alpha_composite(ck.resize((ck.width * SS, ck.height * SS)), (S(54), S(top + 28)))
    return finish(im)


def v_checklist(img, t, dur, cx, cy):
    n = 1 + int(t > 0.95) + int(t > 1.9)
    place_anim(img, checklist(n), cx, cy, t, dur, "pop", 0.0, 0.38)


@lru_cache(maxsize=1)
def doc_card():
    w, h = 620, 700
    im, d = card_base(w, h)
    dtext(d, (w / 2, 60), "CUMHURİYET BAŞSAVCILIĞINA", "black", 30, INK, "mt")
    dtext(d, (w / 2, 108), "Suç Duyurusu Dilekçesi", "bold", 28, RED, "mt")
    for k in range(10):
        ww = [500, 520, 470, 540, 380, 510, 530, 300, 0, 260][k]
        if ww:
            d.rounded_rectangle([S(50), S(190 + k * 44), S(50 + ww), S(208 + k * 44)], S(8), fill=(222, 222, 222, 255))
    d.rounded_rectangle([S(380), S(600), S(570), S(650)], S(10), outline=INK, width=S(4))
    dtext(d, (475, 625), "İmza", "semi", 24, (120, 120, 120, 255), "mm")
    return finish(im)


def v_doc(img, t, dur, cx, cy):
    place_anim(img, doc_card(), cx, cy, t, dur, "drop", 0.0, 0.4, 4)
    place_anim(img, stamp("HAZIR ŞABLON", 66, GREEN), cx + 60, cy + 250, t, dur, "stamp", 0.8, 0.22, -8)


@lru_cache(maxsize=64)
def comment_ui(typed, sent, replied):
    w, h = 860, 640
    im, d = card_base(w, h, radius=30)
    dtext(d, (40, 30), "Yorumlar", "black", 38)
    dtext(d, (820, 36), "1.284", "bold", 30, (130, 130, 130, 255), "ra")
    y = 110
    rows = [("ayse.k", "Annemin adına 2 hat çıktı 😳" if False else "Annemin adına 2 hat çıktı!"),
            ("mert_34", "Hemen kontrol ettim, teşekkürler")]
    if sent:
        rows.append(("sen", "HAT"))
    for k, (u, m) in enumerate(rows):
        me = u == "sen"
        d.ellipse([S(40), S(y), S(104), S(y + 64)], fill=RED if me else (200, 200, 200, 255), outline=INK, width=S(3))
        dtext(d, (124, y + 2), u, "bold", 26, (110, 110, 110, 255))
        dtext(d, (124, y + 34), m, "black" if me else "semi", 32 if me else 30, RED if me else INK)
        y += 108
    if replied:
        d.rounded_rectangle([S(124), S(y - 6), S(820), S(y + 66)], S(18), fill=(236, 248, 241, 255), outline=GREEN, width=S(4))
        dtext(d, (146, y + 14), "↳ Dilekçe + rehber DM'de ✓", "black", 30, GREEN)
    d.rounded_rectangle([S(30), S(520), S(690), S(608)], S(44), fill=(244, 244, 244, 255), outline=INK, width=S(4))
    dtext(d, (64, 545), typed if typed else "Yorum ekle...", "black" if typed else "semi", 34,
          INK if typed else (160, 160, 160, 255))
    d.ellipse([S(710), S(520), S(800), S(610)], fill=RED, outline=INK, width=S(4))
    d.polygon([(S(738), S(545)), (S(782), S(565)), (S(738), S(585))], fill=WHITE)
    return finish(im)


def v_comment(img, t, dur, cx, cy):
    typed = typing(t, 0.5, "HAT", 6)
    sent = t > 1.45
    place_anim(img, comment_ui("" if sent else typed, sent, t > 2.2), cx, cy, t, dur, "pop", 0.0, 0.38)
    x, y = path(t, [(0, cx + 300, cy + 420), (1.0, cx + 300, cy + 420), (1.35, cx + 330, cy + 250)])
    draw_cursor(img, x, y, t, (1.4,), 60)


@lru_cache(maxsize=4)
def big_icon(kind):
    im, d = canvas(260, 260)
    d.rounded_rectangle([S(10), S(10), S(260), S(260)], S(40), fill=INK)
    d.rounded_rectangle([0, 0, S(250), S(250)], S(40), fill=WHITE, outline=INK, width=S(8))
    if kind == "save":
        d.polygon([(S(80), S(50)), (S(170), S(50)), (S(170), S(200)), (S(125), S(160)), (S(80), S(200))], fill=RED, outline=INK)
    else:
        d.polygon([(S(60), S(170)), (S(60), S(130)), (S(140), S(130)), (S(140), S(90)), (S(200), S(150)), (S(140), S(210)), (S(140), S(170))],
                  fill=GREEN, outline=INK)
    return finish(im)


def v_save(img, t, dur, cx, cy):
    place_anim(img, big_icon("save"), cx - 170, cy - 40, t, dur, "pop", 0.05, 0.35, -6)
    place_anim(img, big_icon("share"), cx + 170, cy - 40, t, dur, "pop", 0.25, 0.35, 6)
    place_anim(img, pill("KAYDET", "black", 54, WHITE, RED, pad=(26, 12), shadow=6), cx - 170, cy + 160, t, dur, "up", 0.35)
    place_anim(img, pill("PAYLAŞ", "black", 54, WHITE, GREEN, pad=(26, 12), shadow=6), cx + 170, cy + 160, t, dur, "up", 0.5)


# ================================================================ üst sayaç
REVEAL_T = None


def top_counter(img, t):
    val = "?" if (REVEAL_T is None or t < REVEAL_T) else "3"
    col = INK if val == "?" else RED
    lab = pill("ADINA KAYITLI HAT", "black", 34, INK, WHITE, border=4, pad=(20, 10), shadow=5)
    num = pill(val, "black", 34, WHITE, col, border=4, pad=(18, 10), shadow=5)
    total = lab.width + num.width + 8
    x0 = 540 - total / 2
    place(img, lab, x0, 120, anchor="l")
    sc = 1.0
    if REVEAL_T and 0 <= t - REVEAL_T < 0.3:
        sc = out_back((t - REVEAL_T) / 0.3)
    place(img, num, x0 + lab.width + 8 + num.width / 2, 120, scale=sc)


# ================================================================ senaryo
def build():
    global REVEAL_T
    beats = [
        Beat(2.6, ("ADINA", "GİZLİ HAT VAR MI?"), "çoğu kişi *BİLMİYOR*", v_hook, "shock", [(0.8, "impact")], punch=True),
        Beat(3.0, ("KİMLİK BİLGİN", "SIZDIYSA"), "bilgilerin bir yerde *SIZDIYSA*", v_id, "angry", [(0.75, "error")]),
        Beat(3.4, ("O HATLA", "NELER YAPILIR?"), "senin adına *KREDİ* başvurusu", v_phone, "shock",
             [(0.35, "ding"), (0.95, "ding"), (1.55, "ding")]),
        Beat(3.0, ("FATURASI", "SANA GELİR"), "borç *SENİN* adına çıkar", v_invoice, "angry", [(1.4, "impact")]),
        Beat(2.4, ("KONTROLÜ", "30 SANİYE"), "kontrol etmek sadece *30 SANİYE*", v_stopwatch, "happy", [(0.3, "riser")]),
        Beat(3.4, ("1. E-DEVLET'E GİR", "ARAMAYA YAZ"), "e-devlet'te *HAT SORGULAMA* yaz", v_search, "normal",
             [(0.6 + k / 13, "key") for k in range(len(QUERY))] + [(2.85, "click")]),
        Beat(2.8, ("2. BUNA", "TIKLA"), "*MOBİL HAT SORGULAMA* hizmetine gir", v_results, "normal", [(1.55, "click")]),
        Beat(3.6, ("3. LİSTEYİ", "KONTROL ET"), "tanımadığın hat *VAR MI?*", v_table, "shock", [(1.4, "error"), (1.3, "impact")]),
        Beat(3.6, ("TANIMADIĞIN", "HAT VARSA"), "operatöre başvur *SAVCILIĞA* bildir", v_checklist, "normal",
             [(0.1, "ding"), (0.95, "ding"), (1.9, "ding")]),
        Beat(2.8, ("DİLEKÇESİ", "HAZIR"), "suç duyurusu dilekçesi *HAZIR*", v_doc, "happy", [(0.8, "impact")]),
        Beat(4.2, ("YORUMA", "HAT YAZ"), "yoruma *HAT* yaz dilekçeyi *GÖNDEREYİM*", v_comment, "wink",
             [(0.5 + k / 6, "key") for k in range(3)] + [(1.4, "click"), (2.2, "ding")]),
        Beat(2.6, ("KAYDET,", "AİLENE GÖNDER"), "annene babana da *GÖNDER*", v_save, "happy", [(0.05, "pop2"), (0.25, "pop2")]),
    ]
    sh = Short(beats, top=top_counter, voice=VOICE)
    REVEAL_T = sh.starts[7] + 1.3
    return sh


def main():
    os.makedirs(OUT, exist_ok=True)
    sh = build()
    print(f"süre: {sh.duration:.1f} sn")
    wav = audio.mix(sh.duration, sh.events(), os.path.join(OUT, "short_audio.wav"), voice_path=VOICE, voice_offset=sh.voice_offset)
    render(sh.frame, sh.duration, (W, H), os.path.join(OUT, "dikey_hat_sorgulama.mp4"), wav)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        sh = build()
        from PIL import Image
        ts = [float(x) for x in sys.argv[2:]] or [s + b.dur * 0.75 for s, b in zip(sh.starts, sh.beats)]
        ims = [sh.frame(x).convert("RGB").resize((270, 480)) for x in ts]
        cols = 6
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (270 * cols, 480 * rows), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * 270, (k // cols) * 480))
        sheet.save(os.path.join(OUT, "preview_short.jpg"))
    else:
        main()
