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


# ---------------------------------------------------------------- dudak senkronu + cümle hizalama
def _pcm(path, sr=16000):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def envelope(path, fps=100):
    """Ses gücü eğrisi (0..1), saniyede `fps` örnek."""
    import numpy as np
    x = _pcm(path)
    hop = 16000 // fps
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-9)
    db = 20 * np.log10(rms)
    return np.clip((db + 45) / 30, 0, 1)


def align(path, units, weight=None):
    """Metin birimlerini (cümle/beat) sese hizalar → her birimin başlangıç saniyesi.
    Yöntem: konuşma süresi harf sayısına göre bölünür, her sınır ±0,8 sn içindeki en sessiz ana kaydırılır."""
    import numpy as np
    env = envelope(path)
    fps = 100
    sm = np.convolve(env, np.ones(9) / 9, mode="same")
    talk = sm > 0.12
    idx = np.where(talk)[0]
    if not len(idx):
        return [0.0] * len(units)
    s0, s1 = idx[0] / fps, idx[-1] / fps
    # konuşma zamanı ekseni (uzun sessizlikler sayılmaz)
    cum = np.cumsum(talk) / fps
    w = [max(1, len(u.replace(" ", ""))) for u in units] if weight is None else weight
    tot = sum(w)
    starts, acc = [s0], 0
    for k in range(len(units) - 1):
        acc += w[k]
        target = acc / tot * cum[-1]
        t_est = int(np.searchsorted(cum, target))
        lo, hi = max(t_est - 80, int(starts[-1] * fps) + 30), min(t_est + 80, len(sm) - 1)
        if hi <= lo:
            starts.append(t_est / fps)
            continue
        j = lo + int(np.argmin(sm[lo:hi] + np.abs(np.arange(lo, hi) - t_est) / 80 * 0.15))
        # sessizliğin sonuna (bir sonraki konuşmanın başına) kaydır
        while j < len(sm) - 1 and sm[j] < 0.12 and j < hi + 40:
            j += 1
        starts.append(j / fps)
    return starts
