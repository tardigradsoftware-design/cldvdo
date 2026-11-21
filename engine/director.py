"""OTOMATİK YÖNETMEN — TTS metninden sahne planı (JSON) çıkarır ve videoyu kurar.

Akış:  metin  →  plan_long()/plan_short()  →  plan (dict, JSON'a yazılıp DÜZENLENEBİLİR)  →  build_long()/build_short()
Sahne türleri (uzun):  hook, overview, portal, phone, document, money, card, outro
Sahne türleri (shorts): hook, card, money, phone, document, portal, comment, save
"""
import math
import re

from PIL import Image, ImageDraw

from .core import (BLUE, GREEN, INK, RED, SS, WHITE, YELLOW, canvas, card_base, clamp, dtext, finish, font, in_out_cubic,
                   lerp, out_back, out_cubic, path, pill, place, place_anim, prog, text_sprite, upper_tr)
from .components import draw_cursor, icon_check, icon_warn, icon_x, stamp
from . import portals as P

WPS = 2.6  # okuma/konuşma hızı (kelime/sn)
_FULL = ""
GREYT = (110, 110, 110, 255)
ORD = ["Birinci", "İkinci", "Üçüncü", "Dördüncü", "Beşinci", "Altıncı", "Yedinci"]

EMPH = {"ücretsiz", "mutlaka", "asla", "iade", "hakkın", "zamanaşımı", "iban", "şikayet", "şikâyet", "tazminat", "yasal",
        "kuruşu", "geri", "dikkat", "tuzak", "ceza", "faiz", "hemen", "noter", "dilekçe", "e-devlet", "e-devlet'e",
        "e-devlet'te", "e-devlet'ten", "cimer", "sgk", "banka", "kanun", "zorunda", "hesabına", "bedava", "yüzde"}
RISK = ["dikkat", "tuzak", "asla", "ceza", "kaybed", "zamanaşımı", "haksız", "dolandır", "yanma", "gecik", "hacz", "icra"]
GOOD = ["alabilirsin", "iade", "ücretsiz", "hakkın", "geri", "yatar", "yatırılır", "kazan", "karşılan", "silinir", "düşer"]


# ================================================================ metin yardımcıları
def sentences(text):
    text = re.sub(r"\s+", " ", text.replace("​", " ")).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ0-9e])", text)
    return [p.strip() for p in parts if p.strip()]


def words(s):
    return len(s.split())


def emphasize(s, maxn=2):
    ws = s.split()
    picks = []
    for i, w in enumerate(ws):
        core = re.sub(r"[^\wçğıöşüÇĞİÖŞÜ'\-]", "", w).lower()
        score = 0
        if re.search(r"\d", w):
            score = 3
        elif core in EMPH:
            score = 2
        elif i > 0 and w[:1].isupper() and len(core) > 3:
            score = 1
        if score:
            picks.append((score, i))
    picks = sorted(picks, reverse=True)[:maxn]
    for _, i in picks:
        ws[i] = "*" + ws[i].strip(",.;:") + "*" + ("" if ws[i][-1:] not in ",.;:" else "")
    return " ".join(ws)


def mascot_for(s, default="ciddi"):
    t = s.lower()
    if "yorum" in t and "yaz" in t:
        return "goz_kirp:selam"
    if "abone" in t:
        return "kahkaha:kutlama"
    if any(k in t for k in RISK):
        return "saskin" if any(k in t for k in ("dikkat", "tuzak", "zamanaşımı")) else "kizgin"
    if any(k in t for k in GOOD):
        return "mutlu"
    if "adım" in t:
        return "ciddi:isaret"
    return default


def amount_in(s):
    m = re.search(r"(\d{1,3}(?:[.\s]\d{3})+|\d+)\s*(?:TL|lira|₺)", s)
    return m.group(1).replace(" ", ".") + " TL" if m else None


def phone_in(s):
    m = re.search(r"\b(1\d{2}|444\s?\d\s?\d{3})\b", s)
    if m and re.search(r"\bara|hattı|hattını|numaralı", s.lower()):
        return m.group(1)
    return None


def search_query(s):
    m = re.search(r"arama (?:çubuğuna|kutusuna|alanına|motoruna)\s+(.+?)\s+(?:yaz|yazıp|yazarak|yazın)\b", s, re.I)
    return m.group(1).strip(" '\"“”") if m else None


def key_phrase(s, maxw=5):
    """Cümleden ekranda büyük yazılacak kısa ifade."""
    s = re.sub(r"^(Birinci|İkinci|Üçüncü|Dördüncü|Beşinci|Altıncı|Yedinci) adım,?\s*", "", s)
    clauses = [c.strip() for c in re.split(r"[,;:]| ve | veya | ama ", s) if words(c) >= 2]
    if not clauses:
        clauses = [s]

    def sc(c):
        return sum(2 if re.sub(r"\W", "", w.lower()) in EMPH else 0 for w in c.split()) + (3 if re.search(r"\d", c) else 0) - abs(words(c) - 4) * 0.3
    best = max(clauses, key=sc)
    return " ".join(best.rstrip(".!?").split()[:maxw])


def kw_chips(s, n=3):
    """Özel isim grupları ve sayılı ifadelerden kısa etiketler (ör. 'Kart Ayarları', '30 gün')."""
    out = []
    for m in re.finditer(r"\b\d+[\d.,]*\s+(?:gün|yıl|ay|saat|TL|lira|iş günü|kat)\b", s):
        out.append(m.group(0))
    body = s.split(" ", 1)[1] if " " in s else s
    for m in re.finditer(r"(?:[A-ZÇĞİÖŞÜ0-9][\wçğıöşü'’/-]*)(?:\s+[A-ZÇĞİÖŞÜ0-9][\wçğıöşü'’/-]*){0,3}", body):
        g = m.group(0).strip(" '’")
        if len(g) > 3 and g not in out:
            out.append(g)
    for w in s.split():
        c = re.sub(r"[^\wçğıöşü'-]", "", w.lower())
        if c in EMPH and c not in [o.lower() for o in out]:
            out.append(c)
    return [o[:26] for o in out][:n]


def chunks(s, lo=4, hi=9):
    """Uzun cümleyi doğal yerlerden (virgül, ve/veya/ama) kısa parçalara böler (shorts temposu için)."""
    if words(s) <= hi:
        return [s]
    parts = re.split(r"(?<=,)\s+|(?<=[sy][ea])\s+(?=[a-zçğıöşü])|\s+(?=(?:veya|ama|ancak|ve|çünkü|böylece|yoksa)\s)", s)
    out, cur = [], ""
    for p in parts:
        if cur and words(cur) >= lo and words(cur) + words(p) > hi:
            out.append(cur.strip())
            cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur:
        if out and words(cur) < lo:
            out[-1] += " " + cur
        else:
            out.append(cur.strip())
    return out


def chips_in(s):
    """Virgül/veya ile sayılan öğeler (ör. 'rapor parası, emzirme ödeneği, yol veya cenaze yardımı')."""
    if s.count(",") + s.count(" veya ") + s.count(" ya da ") + s.count(" ve ") < 2:
        return []
    m = re.split(r",| veya | ya da | ve ", s)
    items = [" ".join(x.strip(" .").split()[-3:]) for x in m if 1 <= words(x) <= 6]
    return items[:4] if len(items) >= 3 else []


DOC_TYPES = [("ihtarname", "İHTARNAME"), ("noter", "NOTER İHTARNAMESİ"), ("e-posta", "E-POSTA"), ("mail", "E-POSTA"),
             ("dilekçe", "DİLEKÇE"), ("tutanak", "TUTANAK"), ("itiraz", "İTİRAZ DİLEKÇESİ"), ("sözleşme", "SÖZLEŞME")]
PORTAL_VERBS = ["arama çubuğuna", "arama kutusuna", "ekranına gir", "menüsünden", "sekmesine", "butonuna", "uygulamasına gir",
                "e-devlet'e gir", "e-devlet’e gir", "giriş yap", "bölümüne gir", "bölümünden", "sayfasına gir", "online",
                "ekranına", "uygulamasından", "internet şubesi", "mobil bankacılık"]


def classify(s):
    t = s.lower()
    if phone_in(s):
        return "phone"
    if search_query(s) or any(v in t for v in PORTAL_VERBS):
        return "portal"
    if any(k in t for k, _ in DOC_TYPES) and re.search(r"yaz|gönder|hazırla|çek|ilet|iste", t):
        return "document"
    if amount_in(s) or re.search(r"yatırıl|hesabına yat|geri öden|iade edil", t):
        return "money"
    return "card"


# ================================================================ PLAN (uzun)
def plan_long(text, title="", tags=""):
    global _FULL
    _FULL = text.lower()
    ss = sentences(text)
    plan = {"type": "long", "title": title, "scenes": []}
    i_over = next((i for i, s in enumerate(ss) if re.search(r"adımda", s)), None)
    i_steps = [i for i, s in enumerate(ss) if re.match(r"(%s) adım" % "|".join(ORD), s)]
    i_out = next((i for i, s in enumerate(ss) if "abone" in s.lower()), len(ss))
    first_step = i_steps[0] if i_steps else (i_over + 1 if i_over is not None else 1)
    intro = ss[: (i_over if i_over is not None else first_step)]
    plan["scenes"].append({"kind": "hook", "sentences": intro or ss[:1], "title": title})
    step_titles = []
    for k, i in enumerate(i_steps):
        t = re.sub(r"^(%s) adım,?\s*" % "|".join(ORD), "", ss[i]).rstrip(".")
        step_titles.append(t)
    if i_over is not None:
        plan["scenes"].append({"kind": "overview", "sentences": [ss[i_over]], "steps": [short_title(t) for t in step_titles]})
    n = len(i_steps)
    for k, i in enumerate(i_steps):
        end = i_steps[k + 1] if k + 1 < n else i_out
        chap = [f"ADIM {k + 1}/{n}", short_title(step_titles[k], 30)]
        body = ss[i + 1:end]
        groups = []
        for s in body:
            kind = classify(s)
            if groups and groups[-1]["kind"] == kind and kind in ("portal", "document"):
                groups[-1]["sentences"].append(s)
            else:
                groups.append({"kind": kind, "sentences": [s]})
        if not groups:
            groups = [{"kind": "card", "sentences": []}]
        groups[0]["sentences"].insert(0, ss[i])  # adım başlığı cümlesi ilk sahnede okunur
        for g in groups:
            g["chapter"] = chap
            g["context"] = step_titles[k]
            plan["scenes"].append(g)
    if i_out < len(ss):
        plan["scenes"].append({"kind": "outro", "sentences": ss[i_out:]})
    for sc in plan["scenes"]:
        enrich(sc)
    return plan


def short_title(t, n=26):
    t = t.strip().rstrip(".")
    if len(t) <= n:
        return t[:1].upper() + t[1:]
    ws, out = t.split(), ""
    for w in ws:
        if len(out) + len(w) + 1 > n:
            break
        out = (out + " " + w).strip()
    return out[:1].upper() + out[1:]


def enrich(sc):
    """Sahne parametrelerini metinden otomatik doldurur (JSON'da düzenlenebilir)."""
    txt = " ".join(sc.get("sentences", []))
    k = sc["kind"]
    sc.setdefault("mascot", [mascot_for(s) for s in sc.get("sentences", [])])
    if k == "portal":
        th = P.theme_for(txt + " " + sc.get("context", ""))
        if (search_query(txt) or "e-devlet" in txt.lower()) and "e-devlet" in _FULL and th in ("banka", "sgk", "edevlet") \
                and not re.search(r"mobil bankacılık|internet şubesi|banka(?:nın)? uygulama", txt.lower()):
            th = "edevlet"
        sc.setdefault("theme", th)
        sc.setdefault("device", "mobile" if re.search(r"uygulama|mobil|telefonundan", txt.lower()) else "web")
        sc.setdefault("actions", portal_actions(sc["sentences"]))
    elif k == "phone":
        sc.setdefault("number", next((phone_in(s) for s in sc["sentences"] if phone_in(s)), "184"))
        sc.setdefault("note", key_phrase(txt, 5))
    elif k == "document":
        t = txt.lower()
        sc.setdefault("doc_title", next((v for kw, v in DOC_TYPES if kw in t), "DİLEKÇE"))
        body = re.sub(r"^(%s) adım,?\s*" % "|".join(ORD), "", " ".join(sc["sentences"][1:] or sc["sentences"]))
        sc.setdefault("lines", wrap(body, 42)[:5])
        sc.setdefault("stamp", "NOTER ONAYLI" if "noter" in t else "GÖNDERİLDİ" if "e-posta" in t or "mail" in t else "HAZIR")
    elif k == "money":
        sc.setdefault("amount", amount_in(txt) or "")
    elif k in ("card",):
        sc.setdefault("cards", [{"title": key_phrase(s), "chips": chips_in(s) or kw_chips(s), "stamp": stamp_for(s), "icon": icon_for(s)}
                                for s in sc["sentences"]])


def stamp_for(s):
    t = s.lower()
    for kw, st in (("ücretsiz", "ÜCRETSİZ"), ("zamanaşımı", "ZAMANAŞIMI!"), ("mutlaka", "MUTLAKA"), ("asla", "ASLA!"),
                   ("tuzak", "TUZAK!"), ("dikkat", "DİKKAT!"), ("sakla", "SAKLA"), ("hakkın", "HAKKIN"), ("iade", "İADE"),
                   ("yasal", "YASAL HAK"), ("ceza", "CEZA"), ("zorunda", "ZORUNLU")):
        if kw in t:
            return st
    return ""


def icon_for(s):
    t = s.lower()
    if any(k in t for k in RISK):
        return "warn"
    if amount_in(s) or any(k in t for k in ("para", "ödeme", "ücret", "tl")):
        return "money"
    if any(k in t for k in ("gün", "süre", "yıl", "ay içinde", "tarih")):
        return "calendar"
    if any(k in t for k in ("belge", "fatura", "rapor", "dekont", "sözleşme", "makbuz")):
        return "doc"
    if any(k in t for k in ("kanun", "yönetmelik", "tebliğ", "madde", "yargıtay", "mahkeme")):
        return "law"
    return "check"


def wrap(text, n):
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------- portal eylemleri
UPLOAD_KW = [("fatura", "Fatura.pdf"), ("dekont", "Dekont.pdf"), ("rapor", "Rapor.pdf"), ("sözleşme", "Sozlesme.pdf"),
             ("fotoğraf", "Fotograflar.jpg"), ("ekran görüntü", "Ekran_goruntusu.jpg"), ("makbuz", "Makbuz.pdf"),
             ("dilekçe", "Dilekce.pdf"), ("tutanak", "Tutanak.pdf"), ("kimlik", "Kimlik.pdf"), ("ihtarname", "Ihtarname.pdf")]


def portal_actions(sents):
    """Cümlelerden düzenlenebilir eylem listesi üretir. Her eylem bir cümleye bağlıdır (s = cümle sırası)."""
    acts = []
    for si, s in enumerate(sents):
        if re.match(r"(%s) adım" % "|".join(ORD), s):
            continue
        t = s.lower()
        q = search_query(s)
        if q:
            acts.append({"s": si, "do": "search", "text": q})
        if re.search(r"giriş yap|şifren|kimlik numara", t) and not q:
            acts.append({"s": si, "do": "login"})
        m = re.search(r"([A-ZÇĞİÖŞÜ][\wçğıöşü]+(?:\s[A-ZÇĞİÖŞÜa-zçğıöşü][\wçğıöşü]+){0,3})\s+(?:sekmesine|menüsüne|bölümüne|ekranına|butonuna|bölümünden|menüsünden|sekmesinden)", s)
        if m and not q:
            acts.append({"s": si, "do": "menu", "text": m.group(1)})
        m = re.search(r"([\wçğıöşüÇĞİÖŞÜ]+(?:\s[\wçğıöşüÇĞİÖŞÜ]+){0,2})\s+(?:seçeneğini|seçeneği|kategorisini|türünü)", s)
        if m:
            acts.append({"s": si, "do": "select", "text": m.group(1)[:1].upper() + m.group(1)[1:]})
        if "iban" in t:
            acts.append({"s": si, "do": "field", "label": "IBAN", "text": "TR•• •••• •••• •••• 4821"})
        if re.search(r"metin kutusuna|açıklama|şikayet metn|olayı .*yaz|kısa ve net", t):
            body = re.sub(r"^.*?(yaz|belirt)[:,]?\s*", "", s)
            acts.append({"s": si, "do": "textarea", "lines": wrap(body if words(body) > 4 else s, 52)[:4]})
        if re.search(r"yükle|belge ekle|ekle(?:yip|yerek)? ", t):
            files = [f for kw, f in UPLOAD_KW if kw in t][:4] or ["Belge.pdf", "Fatura.pdf"]
            acts.append({"s": si, "do": "upload", "files": files})
        if re.search(r"kontrol et|görürsün|görünür|bak\b|listele|sorgula|tara|gör\b|incele", t) and not q:
            acts.append({"s": si, "do": "result", "rows": result_rows(s)})
        if re.search(r"ekran görüntüsü", t):
            acts.append({"s": si, "do": "screenshot"})
        if re.search(r"gönder|onayla|başvur|kaydet|tamamla|oluştur|talep et", t):
            acts.append({"s": si, "do": "submit", "label": "Kaydet" if "kaydet" in t else "Başvuruyu Gönder"})
    if not acts:
        acts.append({"s": 0, "do": "result", "rows": result_rows(" ".join(sents))})
    if any(a["do"] == "search" for a in acts) and not any(a["do"] != "search" for a in acts):
        si = max(a["s"] for a in acts)
        acts.append({"s": min(si + 1, len(sents) - 1), "do": "result", "rows": result_rows(" ".join(sents[si:]))})
    return acts


def result_rows(s):
    amt = amount_in(s)
    kp = key_phrase(s, 3)
    return [[kp[:28], amt or "✓ Var"], ["Diğer kayıtlar", "—"], ["Son güncelleme", "Bugün"]]


# ================================================================ PLAN (shorts)
def plan_short(text, title=""):
    ss = sentences(text)
    beats = []
    for i, s in enumerate(ss):
        t = s.lower()
        if "yorum" in t and "yaz" in t and "," in s:
            c = s.index(",")
            parts = [s[:c + 1], s[c + 1:].strip()]
        else:
            parts = chunks(s)
        for p in parts:
            pl = p.lower()
            if "yorum" in pl and "yaz" in pl and re.search(r"[Yy]orumlara\s+\S+\s+yaz", p):
                m = re.search(r"[Yy]orumlara\s+([\wÇĞİÖŞÜçğıöşü]+)\s+yaz", p)
                kind, extra = "comment", {"word": upper_tr(m.group(1)) if m else "EVET"}
            elif re.search(r"göndereyim|atayım|paylaşayım", pl):
                kind, extra = "card", {"stamp": "DM'DE ✓", "icon": "doc"}
            elif i == 0 and p is parts[0]:
                kind, extra = "hook", {"stamp": stamp_for(p) or "DİKKAT!"}
            else:
                kind = classify(p)
                kind = "card" if kind == "portal" and not search_query(p) else kind
                extra = {}
            b = {"kind": kind, "sentence": p, "mascot": mascot_for(p, "saskin" if kind == "hook" else "ciddi"), "title": short_head(p)}
            if kind == "card" or kind == "hook":
                b.update({"chips": chips_in(p) or kw_chips(p), "stamp": stamp_for(p) or ("DİKKAT!" if any(k in pl for k in RISK) else ""),
                          "icon": icon_for(p)})
            b.update(extra)
            if kind == "money":
                b["amount"] = amount_in(p) or ""
            if kind == "phone":
                b["number"] = phone_in(p) or "184"
            if kind == "document":
                b["doc_title"] = next((v for kw, v in DOC_TYPES if kw in pl), "DİLEKÇE")
                b["lines"] = wrap(p, 30)[:4]
            if kind == "portal":
                b["query"] = search_query(p)
                b["theme"] = P.theme_for(p)
            beats.append(b)
    return {"type": "short", "title": title, "beats": beats}


def short_head(s):
    kp = key_phrase(s, 5)
    ws = upper_tr(kp).split()
    if len(ws) <= 2:
        return [" ".join(ws), ""]
    cut = 2 if len(ws) >= 4 else 1
    return [" ".join(ws[:cut]), " ".join(ws[cut:])]
