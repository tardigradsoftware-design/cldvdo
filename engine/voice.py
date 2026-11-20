"""Seslendirme (TTS) dosyasından sahne zamanlaması çıkarma.

Kural: TTS dosyasında her sahne/bölüm arasında ~1 sn sessizlik olmalı.
split_segments() konuşma bloklarını bulur; fit_durations() sahne sürelerini sese kilitler.
"""
import re
import subprocess


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def split_segments(path, min_silence=0.7, noise_db=-35):
    """[(konuşma_başı, konuşma_sonu), ...] döndürür (saniye)."""
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af",
                          f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duration(path)
    segs, cur = [], 0.0
    for s0, s1 in zip(starts, ends + [total] * (len(starts) - len(ends))):
        if s0 - cur > 0.15:
            segs.append((cur, s0))
        cur = s1
    if total - cur > 0.15:
        segs.append((cur, total))
    return segs


def fit_durations(segs, total, pad_end=0.4):
    """Her sahne, kendi konuşmasının başladığı anda başlar; bir sonrakinin başına kadar sürer.
    Döner: (sahne_süreleri, ses_ofseti). İlk sahne t=0'da başlasın diye ses ilk konuşmaya hizalanır."""
    offset = -segs[0][0]
    starts = [a + offset for a, _ in segs]
    durs = [starts[k + 1] - starts[k] for k in range(len(starts) - 1)]
    durs.append(segs[-1][1] + offset - starts[-1] + pad_end)
    return durs, offset


def speech_spans(segs, offset):
    """Sahne-yerel konuşma aralıkları: altyazıyı konuşmaya yaymak için."""
    out = []
    for k, (a, b) in enumerate(segs):
        out.append((0.0, b - a))
    return out
