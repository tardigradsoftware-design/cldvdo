"""Hızlı video kalite kontrolü (≈10 sn). Kullanım:
    python3 engine/qc.py video.mp4            -> GEÇTİ/KALDI raporu + video_kareler.jpg
Kontroller: çözünürlük, piksel formatı, donma oranı, en uzun donma, ses seviyesi, kare tabakası.
"""
import json
import re
import subprocess
import sys


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main(path):
    info = json.loads(sh(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,pix_fmt:format=duration",
                          "-of", "json", path]).stdout)
    dur = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])

    err = sh(["ffmpeg", "-i", path, "-vf", "freezedetect=n=0.003:d=1.5", "-map", "0:v", "-f", "null", "-"]).stderr
    fr = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", err)]
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
    if len(starts) > len(fr):  # video donuk bitiyorsa
        fr.append(dur - starts[-1])
    frozen = sum(fr)
    longest = max(fr) if fr else 0.0

    lufs = None
    if has_audio:
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", sh(["ffmpeg", "-i", path, "-af", "ebur128", "-f", "null", "-"]).stderr)
        lufs = float(m[-1]) if m else None

    sheet = path.rsplit(".", 1)[0] + "_kareler.jpg"
    n = 30
    sh(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"fps={n}/{dur},scale=320:-1,tile=6x5:padding=4:color=white",
        "-frames:v", "1", sheet])

    checks = [
        ("Çözünürlük", f"{v['width']}x{v['height']}", (v["width"], v["height"]) in ((1920, 1080), (1080, 1920))),
        ("Piksel formatı", v.get("pix_fmt"), v.get("pix_fmt") == "yuv420p"),
        ("Donuk süre oranı", f"%{100 * frozen / dur:.1f}  (sınır %5)", frozen / dur <= 0.05),
        ("En uzun donma", f"{longest:.1f} sn  (sınır 2 sn)", longest <= 2.0),
        ("Ses seviyesi", f"{lufs} LUFS  (hedef -18…-12)" if lufs is not None else "ses yok", lufs is not None and -18 <= lufs <= -12),
    ]
    print(f"\nVİDEO: {path}  ({dur:.1f} sn)")
    ok = True
    for name, val, good in checks:
        ok &= good
        print(f"  {'✓' if good else '✗'} {name:<18} {val}")
    if fr:
        worst = sorted(zip(starts, fr), key=lambda x: -x[1])[:3]
        print("  En uzun donmalar: " + ", ".join(f"{s:.0f}. sn ({d:.1f} sn)" for s, d in worst))
    print(f"  Kare tabakası: {sheet}  → hedef görünümle karşılaştır")
    print(f"\nSONUÇ: {'GEÇTİ ✅' if ok else 'KALDI ❌  — ✗ olan maddeleri düzelt, sadece ilgili sahneleri değiştir, tekrar render al'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
