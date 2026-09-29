"""Synthesize background music and sound effects, then mix them with the narration.

Everything is generated here with numpy, so there are no licensing questions.
Sound-effect times come from the same cue functions the renderer uses.

Writes build/music.wav, build/sfx.wav and build/mix.wav (48 kHz stereo).
"""

import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, lfilter

sys.path.insert(0, str(Path(__file__).parent))
import timeline as TL  # noqa: E402

SR = 48000
RNG = np.random.default_rng(7)

MUSIC_GAIN_DB = -23.0     # music level before ducking, relative to full scale
DUCK_DB = -7.0            # extra reduction while the narrator speaks
SFX_GAIN_DB = -10.0


def db(x):
    return 10 ** (x / 20)


def note_hz(n):
    """MIDI note number to Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, r, sr=SR):
    e = np.ones(n)
    na, nr = int(a * sr), int(r * sr)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    return lfilter([1 - a], [1, -a], x)


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


# Music -------------------------------------------------------------------
BPM = 84
BEAT = 60 / BPM
# F major: F - C - Dm - Bb, two bars each
CHORDS = [(53, [65, 69, 72]), (48, [64, 67, 72]), (50, [62, 65, 69]), (46, [62, 65, 70])]


def pad_voice(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.003 * t)
         + 0.5 * np.sin(2 * np.pi * freq * 0.998 * t))
    return x * env_adsr(n, 1.2, 1.4)


def pluck(freq, dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * 5.0)
    return x * env_adsr(n, 0.004, 0.05)


def music(total, sections):
    """sections: list of (start, end, intensity 0..1) controlling the arpeggio."""
    n = int(total * SR) + SR
    L, R = np.zeros(n), np.zeros(n)
    chord_len = 8 * BEAT
    k = 0
    while k * chord_len < total + chord_len:
        t0 = k * chord_len
        root, tones = CHORDS[k % 4]
        s0 = int(t0 * SR)
        if s0 >= n:
            break
        for i, tn in enumerate(tones):
            v = pad_voice(note_hz(tn - 12), chord_len + 1.4) * 0.16
            e = min(n, s0 + len(v))
            pan = 0.35 + 0.15 * i
            L[s0:e] += v[:e - s0] * (1 - pan)
            R[s0:e] += v[:e - s0] * pan
        b = pad_voice(note_hz(root - 12), chord_len + 1.0) * 0.22
        e = min(n, s0 + len(b))
        L[s0:e] += b[:e - s0]
        R[s0:e] += b[:e - s0]
        # arpeggio on eighth notes, level set by the section intensity
        pattern = [0, 1, 2, 1, 2, 0, 1, 2]
        for step in range(16):
            ts = t0 + step * BEAT / 2
            inten = intensity_at(ts, sections)
            if inten <= 0.01:
                continue
            tn = tones[pattern[step % 8]] + (12 if step % 8 in (2, 6) else 0)
            v = pluck(note_hz(tn)) * 0.10 * inten
            si = int(ts * SR)
            e = min(n, si + len(v))
            pan = 0.3 if step % 2 else 0.7
            L[si:e] += v[:e - si] * (1 - pan)
            R[si:e] += v[:e - si] * pan
        k += 1
    x = np.stack([L, R], 1)[: int(total * SR)]
    x = lowpass(x.T, 5000).T
    fade = np.ones(len(x))
    fi, fo = int(2.0 * SR), int(3.0 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    return x * fade[:, None]


def intensity_at(t, sections):
    v = 0.0
    for s, e, inten in sections:
        if s <= t < e:
            v = inten
    return v


# Sound effects -------------------------------------------------------------
def noise(n):
    return RNG.standard_normal(n)


def sfx_whoosh(dur=0.7, lo=300, hi=2500):
    n = int(dur * SR)
    x = noise(n)
    out = np.zeros(n)
    cut = np.linspace(lo, hi, n) ** 1.0
    y = 0.0
    for i in range(n):
        a = math.exp(-2 * math.pi * cut[i] / SR)
        y = (1 - a) * x[i] + a * y
        out[i] = y
    out = highpass(out, 150)
    return out * np.sin(np.linspace(0, np.pi, n)) ** 2 * 1.4


def sfx_chime(base=880.0, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * base * m * t) * np.exp(-t * d)
            for m, a, d in ((1, 1.0, 3.0), (2.0, 0.35, 5.0), (2.76, 0.25, 7.0), (5.4, 0.08, 9.0)))
    return x * env_adsr(n, 0.003, 0.2) * 0.5


def sfx_pop(freq=700.0):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * t / 0.09)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) * 0.5


def sfx_tick():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120) + 0.3 * noise(n) * np.exp(-t * 200)) * 0.6


def sfx_thump():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 6) + 45
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    slap = lowpass(noise(n), 2500) * np.exp(-t * 60) * 1.5
    return (body + slap) * 0.9


def sfx_step():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    x = lowpass(noise(n), 900) * np.exp(-t * 55)
    return highpass(x, 80) * 1.6


def sfx_heartbeat():
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for t0, f, a in ((0.0, 58, 1.0), (0.26, 70, 0.7)):
        tt = np.clip(t - t0, 0, None)
        g = (t >= t0) * np.exp(-tt * 22) * (1 - np.exp(-tt * 400))
        out += a * np.sin(2 * np.pi * f * tt) * g
    return lowpass(out, 300) * 1.8


def sfx_breath(dur, inhale=True):
    n = int(dur * SR)
    x = lowpass(highpass(noise(n), 500), 2500 if inhale else 1800)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return x * env * 0.12


def sfx_crunch():
    n = int(0.5 * SR)
    out = np.zeros(n)
    for k in range(6):
        s = int((0.03 + k * 0.075 + RNG.uniform(0, 0.02)) * SR)
        m = int(0.04 * SR)
        t = np.arange(m) / SR
        out[s:s + m] += highpass(noise(m), 1200) * np.exp(-t * 90) * RNG.uniform(0.5, 1.0)
    return out * 0.7


def sfx_gurgle(dur=1.2):
    n = int(dur * SR)
    out = np.zeros(n)
    for k in range(7):
        s = int(RNG.uniform(0, dur - 0.15) * SR)
        m = int(0.12 * SR)
        t = np.arange(m) / SR
        f = RNG.uniform(160, 320) * (1 + 1.5 * t / 0.12)
        out[s:s + m] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.linspace(0, np.pi, m)) * 0.5
    return lowpass(out, 900)


def sfx_drip():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    f = 700 + 1400 * (1 - np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) * 0.45


def sfx_sparkle():
    n = int(0.9 * SR)
    out = np.zeros(n)
    for k, f in enumerate((1568, 1976, 2349, 3136)):
        s = int(k * 0.08 * SR)
        m = n - s
        t = np.arange(m) / SR
        out[s:] += np.sin(2 * np.pi * f * t) * np.exp(-t * 9) * 0.25
    return out


def phase_crossings(fn, t0, t1, offset=0.0, step=0.005):
    """Times in [t0, t1) where fn(t) crosses integer + offset."""
    out = []
    prev = fn(t0) - offset
    t = t0 + step
    while t < t1:
        cur = fn(t) - offset
        if math.floor(cur) > math.floor(prev):
            out.append(t)
        prev = cur
        t += step
    return out


def events():
    """List of (global_time, sound_array, gain_db, pan)."""
    ev = []
    scenes = TL.scenes()
    S = {s.id: s for s in scenes}
    C = {s.id: TL.CUE_FUNCS[s.id](s) for s in scenes}

    def add(scene, t, snd, gain=0.0, pan=0.5):
        ev.append((S[scene].start + t, snd, gain, pan))

    whoosh = sfx_whoosh()
    for s in scenes[1:]:
        ev.append((s.start - 0.35, whoosh, -14, 0.5))
    c = C["intro"]
    add("intro", 0.25, sfx_chime(659.3), -6)
    add("intro", 0.55, sfx_chime(987.8), -9)
    add("intro", c["tag"], sfx_pop(650), -12)
    add("intro", c["ball_launch"], sfx_whoosh(1.1, 400, 1800), -8, 0.8)
    add("intro", c["freeze"], sfx_tick(), -8)
    add("intro", c["zoom"], sfx_whoosh(1.3, 200, 3000), -10)
    c = C["eyes"]
    add("eyes", c["signals"], sfx_sparkle(), -12)
    add("eyes", c["body"] + 0.6, sfx_sparkle(), -12)
    for k in ("retina", "optic", "brain", "neurons", "spinal", "nerves"):
        add("eyes", c[k], sfx_pop(620), -16)
    c = C["muscles"]
    for k in ("pull", "push", "contract", "tendons", "bones", "joint", "front", "back"):
        add("muscles", c[k], sfx_pop(560), -16)
    for i, t in enumerate(TL.run_footsteps(c["run"] + 0.2, c["lift"] + 0.3)):
        add("muscles", t, sfx_step(), -10, 0.4 + 0.2 * (i % 2))
    add("muscles", c["catch"] - 2.0, sfx_whoosh(1.6, 300, 2200), -12, 0.8)
    add("muscles", c["catch"], sfx_thump(), -4)
    add("muscles", c["catch"] + 0.08, sfx_chime(784.0), -10)
    c = C["lungs"]
    ph = lambda t: TL.breath_phase_lungs(t, c)  # noqa: E731
    starts = phase_crossings(ph, 0.2, c["zoom"])
    for t in starts:
        period = 1.0 / (0.28 + (0.6 - 0.28) * TL.clamp01((t - c["faster"]) / (c["faster_end"] - c["faster"])))
        add("lungs", t, sfx_breath(period * 0.45, True), -6)
        add("lungs", t + period * 0.5, sfx_breath(period * 0.45, False), -8)
    for k in ("windpipe", "lungs", "alveoli", "oxygen", "co2"):
        add("lungs", c[k], sfx_pop(620), -16)
    c = C["heart"]
    hp = lambda t: TL.heart_phase(t, c)  # noqa: E731
    beat = sfx_heartbeat()
    for t in phase_crossings(hp, 0.0, S["heart"].dur - 0.3):
        add("heart", t, beat, -6)
    for k in ("heart", "vessels"):
        add("heart", c[k], sfx_pop(620), -16)
    c = C["digestion"]
    add("digestion", c["plate"], sfx_pop(520), -12)
    add("digestion", c["crush"], sfx_crunch(), -6)
    add("digestion", c["crush"] + 0.45, sfx_crunch(), -8)
    add("digestion", c["stomach"] + 0.4, sfx_gurgle(), -6)
    for k in ("intestine", "nutrients", "blood"):
        add("digestion", c[k], sfx_pop(620), -16)
    c = C["kidneys"]
    for k in ("kidneys", "filter", "balance"):
        add("kidneys", c[k], sfx_pop(620), -16)
    for i in range(3):
        add("kidneys", c["urine"] + i * 0.35, sfx_drip(), -12)
    for i in range(2):
        add("kidneys", c["sweat"] + 0.6 + i * 0.5, sfx_drip(), -14)
    c = C["recovery"]
    rp = lambda t: TL.recovery_heart_phase(t, c)  # noqa: E731
    for t in phase_crossings(rp, c["slow"] - 1.5, S["recovery"].dur - 0.5):
        add("recovery", t, beat, -14)
    c = C["recap"]
    notes = [523.3, 587.3, 659.3, 698.5, 784.0, 880.0]
    for i, k in enumerate(("eyes", "muscles", "lungs", "heart", "digestion", "kidneys")):
        add("recap", c[k], sfx_chime(notes[i], 1.2), -14)
    add("recap", c["question"] + 0.6, sfx_chime(523.3, 2.5), -10)
    add("recap", c["question"] + 0.9, sfx_chime(784.0, 2.5), -12)
    return ev


def place(buf, t, snd, gain_db, pan):
    s = int(t * SR)
    if s < 0:
        snd = snd[-s:]
        s = 0
    e = min(len(buf), s + len(snd))
    if e <= s:
        return
    g = db(gain_db)
    buf[s:e, 0] += snd[:e - s] * g * math.cos(pan * math.pi / 2) * 1.41
    buf[s:e, 1] += snd[:e - s] * g * math.sin(pan * math.pi / 2) * 1.41


def speech_envelope(voice, attack=0.05, release=0.6):
    x = np.abs(voice)
    win = int(0.03 * SR)
    x = np.convolve(x, np.ones(win) / win, mode="same")
    active = (x > 0.01).astype(float)
    # hold, then smooth with attack/release
    env = np.zeros_like(active)
    a_c = math.exp(-1 / (attack * SR))
    r_c = math.exp(-1 / (release * SR))
    y = 0.0
    for i, v in enumerate(active):
        c = a_c if v > y else r_c
        y = c * y + (1 - c) * v
        env[i] = y
    return env


def main():
    tl = TL.load()
    total = tl["duration"]
    voice24, sr = sf.read(TL.BUILD / "narration.wav")
    assert sr == 24000
    voice = resample_poly(voice24, 2, 1)
    n = int(total * SR)
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    voice = voice / np.max(np.abs(voice)) * db(-3)

    scenes = {s.id: s for s in TL.scenes()}
    sections = [
        (0, scenes["eyes"].start, 1.0),
        (scenes["eyes"].start, scenes["muscles"].start, 0.6),
        (scenes["muscles"].start, scenes["lungs"].start, 1.0),
        (scenes["lungs"].start, scenes["recovery"].start, 0.7),
        (scenes["recovery"].start, scenes["recap"].start, 0.3),
        (scenes["recap"].start, scenes["recap"].start + TL.recap_cues(scenes["recap"])["question"], 0.9),
    ]
    mus = music(total, sections)
    env = speech_envelope(voice)
    duck = db(DUCK_DB) ** env
    mus = mus * db(MUSIC_GAIN_DB) / np.max(np.abs(mus)) * duck[:, None]

    fx = np.zeros((n, 2))
    evs = events()
    for t, snd, g, pan in evs:
        place(fx, t, snd, g, pan)
    fx *= db(SFX_GAIN_DB)

    mix = mus + fx + voice[:, None]
    peak = np.max(np.abs(mix))
    if peak > 0.98:
        mix *= 0.98 / peak
    sf.write(TL.BUILD / "music.wav", mus.astype(np.float32), SR)
    sf.write(TL.BUILD / "sfx.wav", fx.astype(np.float32), SR)
    sf.write(TL.BUILD / "voice48.wav", voice.astype(np.float32), SR)
    sf.write(TL.BUILD / "mix.wav", mix.astype(np.float32), SR)
    print(f"mix {total:.2f}s, peak {peak:.2f}, events {len(evs)}")


if __name__ == "__main__":
    main()
