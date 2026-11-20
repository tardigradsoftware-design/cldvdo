"""Ses: numpy ile telifsiz müzik yatağı + SFX sentezi, miks ve -14 LUFS normalizasyonu."""
import subprocess
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=0.1, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4) * (curve / 4))
    return e


# ---------------------------------------------------------------- SFX
def sfx_pop(f=900):
    t = _t(0.09)
    fr = f * (1 + 1.2 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 45) * 0.6


def sfx_click():
    n = int(0.03 * SR)
    x = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 260)
    t = np.arange(n) / SR
    return (x * 0.5 + np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 300) * 0.5) * 0.7


def sfx_key():
    n = int(0.045 * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    x = np.convolve(x, np.ones(6) / 6, "same")
    f = rng.uniform(1500, 2600)
    return (x * 0.6 + np.sin(2 * np.pi * f * t) * 0.3) * np.exp(-t * 140) * 0.45


def sfx_whoosh(d=0.35, up=True):
    n = int(d * SR)
    x = rng.normal(0, 1, n)
    out = np.zeros(n)
    # zamanla değişen basit tek kutuplu alçak geçiren
    fc = np.linspace(0.02, 0.35, n) if up else np.linspace(0.35, 0.02, n)
    y = 0.0
    for i in range(n):
        y += fc[i] * (x[i] - y)
        out[i] = y
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return out * env * 1.6


def sfx_impact():
    t = _t(0.6)
    f = 55 + 90 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    n = rng.normal(0, 1, len(t)) * np.exp(-t * 30) * 0.4
    return np.tanh((body + n) * 1.8) * 0.8


def sfx_ding():
    t = _t(0.7)
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((1318, 0.5), (1976, 0.3), (2637, 0.15)))
    return x * np.exp(-t * 5) * 0.5


def sfx_error():
    t = _t(0.32)
    sq = np.sign(np.sin(2 * np.pi * 220 * t)) * 0.3 + np.sin(2 * np.pi * 233 * t) * 0.3
    return sq * np.exp(-t * 7) * 0.5


def sfx_tick():
    t = _t(0.05)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 120) * 0.35


def sfx_riser(d=1.0):
    t = _t(d)
    f = 200 + 900 * (t / d) ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + rng.normal(0, 1, len(t)) * 0.08
    return x * (t / d) ** 2


SFX = {
    "pop": lambda: sfx_pop(900), "pop2": lambda: sfx_pop(1300), "click": sfx_click, "key": sfx_key,
    "whoosh": lambda: sfx_whoosh(0.32, True), "whoosh_down": lambda: sfx_whoosh(0.32, False),
    "impact": sfx_impact, "ding": sfx_ding, "error": sfx_error, "tick": sfx_tick, "riser": sfx_riser,
}
SFX_GAIN = {"pop": 0.35, "pop2": 0.3, "click": 0.5, "key": 0.32, "whoosh": 0.22, "whoosh_down": 0.2,
            "impact": 0.6, "ding": 0.35, "error": 0.35, "tick": 0.25, "riser": 0.3}


# ---------------------------------------------------------------- müzik
def _note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music_bed(duration, bpm=104, seed=3):
    """Hafif, pozitif lo-fi/pop yatak: kick + clap + hat + bas + pad. Telifsiz (sentez)."""
    r = np.random.default_rng(seed)
    n = int(duration * SR) + SR
    out = np.zeros(n)
    beat = 60 / bpm
    # akorlar: C - G - Am - F (MIDI kök + üçlü)
    prog = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [60, 64, 69]), (41, [60, 65, 69])]
    bar = beat * 4
    t_bar = np.arange(int(bar * SR)) / SR
    k = 0
    tpos = 0.0
    while tpos < duration + bar:
        root, chord = prog[k % 4]
        i0 = int(tpos * SR)
        seg = np.zeros(len(t_bar))
        # pad (yumuşak üçgen benzeri)
        for m in chord:
            f = _note(m)
            seg += (np.sin(2 * np.pi * f * t_bar) + 0.25 * np.sin(2 * np.pi * 2 * f * t_bar)) * 0.06
        seg *= np.minimum(1, t_bar / 0.08) * np.minimum(1, (bar - t_bar) / 0.1)
        # pluck arpej 8'lik
        for s in range(8):
            m = chord[[0, 1, 2, 1, 0, 2, 1, 2][s]] + 12
            ts = s * beat / 2
            j = int(ts * SR)
            tt = np.arange(int(beat / 2 * SR)) / SR
            pl = np.sin(2 * np.pi * _note(m) * tt) * np.exp(-tt * 9) * 0.05
            seg[j:j + len(pl)] += pl[: len(seg) - j]
        # bas
        for s in range(4):
            j = int(s * beat * SR)
            tt = np.arange(int(beat * 0.9 * SR)) / SR
            b = np.sin(2 * np.pi * _note(root) * tt) * np.exp(-tt * 3) * 0.22
            seg[j:j + len(b)] += b[: len(seg) - j]
        # davul
        for s in range(4):
            j = int(s * beat * SR)
            if s in (0, 2):
                tt = np.arange(int(0.25 * SR)) / SR
                kick = np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 12) * 0.5
                seg[j:j + len(kick)] += kick[: len(seg) - j]
            else:
                tt = np.arange(int(0.18 * SR)) / SR
                clap = r.normal(0, 1, len(tt)) * np.exp(-tt * 28) * 0.13
                seg[j:j + len(clap)] += clap[: len(seg) - j]
            for hh in (0, 0.5):
                jj = int((s + hh) * beat * SR)
                tt = np.arange(int(0.05 * SR)) / SR
                hat = np.diff(r.normal(0, 1, len(tt) + 1)) * np.exp(-tt * 90) * 0.035
                seg[jj:jj + len(hat)] += hat[: len(seg) - jj]
        e = min(len(seg), n - i0)
        if e > 0:
            out[i0:i0 + e] += seg[:e]
        tpos += bar
        k += 1
    out = out[: int(duration * SR)]
    fade = int(1.2 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    return out


# ---------------------------------------------------------------- miks
def mix(duration, events, out_wav, music_gain=0.55, voice_path=None, duck=None):
    """events: [(t, sfx_adı, kazanç_çarpanı)] ; duck: [(t0, t1)] müziğin kısılacağı aralıklar."""
    n = int(duration * SR)
    mus = music_bed(duration) * music_gain
    if duck:
        g = np.ones(n)
        for a, b in duck:
            i, j = int(a * SR), int(b * SR)
            g[i:j] = 0.35
        g = np.convolve(g, np.ones(int(0.15 * SR)) / int(0.15 * SR), "same")
        mus *= g
    fx = np.zeros(n)
    cache = {}
    for t, name, gmul in events:
        x = SFX[name]() if name in ("key", "whoosh", "whoosh_down") else cache.setdefault(name, SFX[name]())
        i = int(t * SR)
        if i >= n:
            continue
        e = min(len(x), n - i)
        fx[i:i + e] += x[:e] * SFX_GAIN[name] * gmul
    mixed = mus + fx
    mixed = np.tanh(mixed * 1.1) * 0.9
    st = np.stack([mixed, mixed], 1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    raw = out_wav + ".raw.wav"
    with wave.open(raw, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    # platform standardı: -14 LUFS, TP -1.5
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", str(SR), out_wav], check=True)
    return out_wav
