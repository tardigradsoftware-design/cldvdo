#!/usr/bin/env python3
"""TOKMAK VİDEO ÜRETİCİ — senaryo CSV'sinden tek komutla video.

Kullanım:
  python3 tokmak.py --csv senaryolar.csv --id VID_001 --tur uzun            # plan + render + kalite kontrol
  python3 tokmak.py --csv senaryolar.csv --id VID_001 --tur shorts
  python3 tokmak.py --csv senaryolar.csv --id VID_001 --tur uzun --plan-yaz # sadece planı yaz (düzenlemek için)
  python3 tokmak.py --plan out/VID_001_uzun_plan.json                        # düzenlenmiş planı render et
  python3 tokmak.py ... --onizleme                                           # render yerine kare tabakası
  python3 tokmak.py ... --ses ses.mp3                                        # seslendirmeyi ekle (süreyi sese uydurur)
  python3 tokmak.py --csv senaryolar.csv --hepsi --tur shorts                # tüm satırlar (toplu üretim)
"""
import argparse
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from engine import audio, director, scenes            # noqa: E402
from engine.core import render                          # noqa: E402
from engine.voice import duration as voice_duration     # noqa: E402

COLS = {"uzun": ("uzun video tts", "uzun video başlığı", "uzun video etiketler", "uzun video hastaglar"),
        "shorts": ("shorts video tts", "shorts video başlığı", "shorts etiketler", "shorts hastaglar")}


def load_rows(path):
    with open(path, encoding="utf-8-sig") as f:
        return {r["video id"]: r for r in csv.DictReader(f)}


def make_plan(row, tur):
    tts, title, _, _ = COLS[tur]
    p = director.plan_long(row[tts], row[title]) if tur == "uzun" else director.plan_short(row[tts], row[title])
    p["id"] = row["video id"]
    return p


def write_meta(row, tur, out):
    _, title, tags, hashtags = COLS[tur]
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"BAŞLIK:\n{row[title]}\n\nETİKETLER:\n{row[tags]}\n\nHASHTAG:\n{row[hashtags]}\n\nMETİN (TTS):\n{row[COLS[tur][0]]}\n")


def render_plan(plan, out_dir, voice=None, preview=False, stil="kayit"):
    vid, tur = plan.get("id", "video"), "uzun" if plan["type"] == "long" else "shorts"
    total = voice_duration(voice) if voice else None
    if plan["type"] == "long":
        from engine.screencast import build_screencast
        obj = build_screencast(plan, total=total) if stil == "kayit" else scenes.build_long(plan, total=total)
    else:
        obj = scenes.build_short(plan, total=total)
    size = (1920, 1080) if plan["type"] == "long" else (1080, 1920)
    base = os.path.join(out_dir, f"{vid}_{tur}")
    if preview:
        from PIL import Image
        ts = [obj.starts[i] + obj.segs[i].dur * f if plan["type"] == "long" else obj.starts[i] + obj.beats[i].dur * f
              for i in range(len(obj.starts)) for f in ((0.3, 0.8) if plan["type"] == "long" else (0.7,))]
        tw, th = (384, 216) if plan["type"] == "long" else (216, 384)
        cols = 5 if plan["type"] == "long" else 8
        ims = [obj.frame(x).convert("RGB").resize((tw, th)) for x in ts]
        sheet = Image.new("RGB", (tw * cols, th * ((len(ims) + cols - 1) // cols)), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * tw, (k // cols) * th))
        sheet.save(base + "_onizleme.jpg")
        print(f"önizleme: {base}_onizleme.jpg  (süre {obj.duration:.1f} sn)")
        return None
    print(f"[{vid} {tur}] süre {obj.duration:.1f} sn — render…")
    wav = audio.mix(obj.duration, obj.events(), base + "_ses.wav", voice_path=voice, voice_offset=0)
    render(obj.frame, obj.duration, size, base + ".mp4", wav)
    os.remove(base + "_ses.wav")
    subprocess.run([sys.executable, os.path.join(ROOT, "engine", "qc.py"), base + ".mp4"])
    return base + ".mp4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    ap.add_argument("--id")
    ap.add_argument("--tur", choices=["uzun", "shorts"], default="uzun")
    ap.add_argument("--plan", help="düzenlenmiş plan JSON dosyası")
    ap.add_argument("--plan-yaz", action="store_true")
    ap.add_argument("--onizleme", action="store_true")
    ap.add_argument("--ses")
    ap.add_argument("--hepsi", action="store_true")
    ap.add_argument("--cikti", default=os.path.join(ROOT, "out"))
    ap.add_argument("--stil", choices=["kayit", "cizgi"], default="kayit",
                    help="uzun video stili: kayit = gerçekçi ekran kaydı (varsayılan), cizgi = çizgi/kart stili")
    a = ap.parse_args()
    os.makedirs(a.cikti, exist_ok=True)
    if a.plan:
        plan = json.load(open(a.plan, encoding="utf-8"))
        render_plan(plan, a.cikti, a.ses, a.onizleme, a.stil)
        return
    rows = load_rows(a.csv)
    ids = list(rows) if a.hepsi else [a.id]
    for vid in ids:
        row = rows[vid]
        plan = make_plan(row, a.tur)
        pj = os.path.join(a.cikti, f"{vid}_{a.tur}_plan.json")
        json.dump(plan, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        write_meta(row, a.tur, os.path.join(a.cikti, f"{vid}_{a.tur}_bilgi.txt"))
        print(f"plan: {pj}")
        if not a.plan_yaz:
            render_plan(plan, a.cikti, a.ses, a.onizleme, a.stil)


if __name__ == "__main__":
    main()
