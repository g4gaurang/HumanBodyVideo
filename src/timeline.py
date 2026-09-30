"""Scene timing helpers shared by the renderer, captions and audio mixer."""

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load():
    return json.loads((BUILD / "timeline.json").read_text())


class SceneTime:
    """Cue lookups relative to the start of one scene."""

    def __init__(self, scene):
        self.scene = scene
        self.id = scene["id"]
        self.start = scene["start"]
        self.end = scene["end"]
        self.dur = self.end - self.start
        self.lines = {l["id"]: l for l in scene["lines"]}

    def line(self, line_id):
        l = self.lines[line_id]
        return l["start"] - self.start, l["end"] - self.start

    def ls(self, line_id):
        return self.line(line_id)[0]

    def le(self, line_id):
        return self.line(line_id)[1]

    def word(self, line_id, word, occurrence=0, end=False):
        target = norm(word)
        seen = 0
        for w in self.lines[line_id]["words"]:
            if norm(w["w"]).startswith(target):
                if seen == occurrence:
                    return (w["e"] if end else w["s"]) - self.start
                seen += 1
        raise KeyError(f"{word!r} not found in {line_id}")


def scenes():
    return [SceneTime(s) for s in load()["scenes"]]


def phase_linear(t, t0, t1, r0, r1):
    """Integral of a rate (cycles/s) that ramps linearly from r0 at t0 to r1 at t1."""
    if t <= t0:
        return r0 * t
    base = r0 * t0
    if t <= t1:
        d = t - t0
        k = (r1 - r0) / (t1 - t0)
        return base + r0 * d + 0.5 * k * d * d
    return base + 0.5 * (r0 + r1) * (t1 - t0) + r1 * (t - t1)


def phase_decay(t, t0, r_hi, r_lo, tau):
    """Integral of a rate that decays exponentially from r_hi to r_lo after t0."""
    if t <= t0:
        return r_hi * t
    d = t - t0
    return r_hi * t0 + r_lo * d + (r_hi - r_lo) * tau * (1 - math.exp(-d / tau))


# Shared cue definitions -------------------------------------------------
# Both the renderer and the sound-effects mixer call these so that sounds line
# up with the animation.

RUN_CADENCE = 2.6  # steps per second while running


def intro_cues(S):
    return {
        "maya_in": 3.4,
        "tag": S.word("intro_2", "Maya"),
        "ball_launch": S.word("intro_2", "flying") - 0.3,
        "freeze": S.word("intro_4", "slow"),
        "zoom": S.le("intro_4") - 0.2,
    }


def eyes_cues(S):
    return {
        "rays": S.ls("eyes_1") + 0.6,
        "retina": S.word("eyes_2", "retina"),
        "signals": S.word("eyes_3", "electrical"),
        "optic": S.word("eyes_3", "optic"),
        "brain": S.word("eyes_3", "brain"),
        "nerve_card": S.ls("eyes_4") - 0.2,
        "neurons": S.word("eyes_4", "neurons"),
        "process": S.ls("eyes_5") - 0.3,
        "body": S.ls("eyes_6") - 0.3,
        "spinal": S.word("eyes_6", "spinal"),
        "nerves": S.word("eyes_6", "nerves"),
    }


def muscle_cues(S):
    return {
        "pull": S.word("mus_1", "pull"),
        "push": S.word("mus_1", "push"),
        "contract": S.word("mus_2", "contracts"),
        "tendons": S.word("mus_3", "tendons"),
        "bones": S.word("mus_3", "bones"),
        "joint": S.word("mus_3", "joint"),
        "front": S.word("mus_4", "front"),
        "back": S.word("mus_4", "back"),
        "turns": S.word("mus_5", "turns"),
        "run": S.word("mus_5", "Maya") - 0.3,
        "lift": S.word("mus_6", "lift"),
        "catch": S.ls("mus_7") - 0.12,
    }


def run_footsteps(t0, t1):
    """Footstep times for a run starting at t0 (scene time)."""
    out, k = [], 0
    while True:
        t = t0 + (0.5 + k) / RUN_CADENCE
        if t > t1:
            return out
        out.append(t)
        k += 1


def lungs_cues(S):
    return {
        "energy": S.ls("lung_1"),
        "faster": S.ls("lung_2"),
        "faster_end": S.le("lung_2") + 1.0,
        "windpipe": S.word("lung_3", "windpipe"),
        "lungs": S.word("lung_3", "lungs"),
        "zoom": S.ls("lung_4") - 0.3,
        "alveoli": S.word("lung_4", "alveoli"),
        "oxygen": S.word("lung_5", "oxygen"),
        "co2": S.word("lung_6", "carbon"),
        "out": S.word("lung_6", "breathed"),
    }


def breath_phase_lungs(t, c):
    return phase_linear(t, c["faster"], c["faster_end"], 0.28, 0.6)


def heart_cues(S):
    return {
        "heart": S.word("heart_1", "heart"),
        "vessels": S.word("heart_1", "vessels"),
        "right": S.ls("heart_2"),
        "left": S.ls("heart_3"),
        "nutrients": S.word("heart_4", "nutrients"),
        "co2": S.word("heart_4", "carbon"),
        "faster": S.word("heart_5", "faster"),
    }


def heart_phase(t, c):
    """Heartbeats (cycles) in the heart scene: ~85 bpm rising to ~150 bpm."""
    return phase_linear(t, c["faster"], c["faster"] + 4.0, 85 / 60, 150 / 60)


def heart_bpm(t, c):
    k = min(1.0, max(0.0, (t - c["faster"]) / 4.0))
    return 85 + (150 - 85) * k


def digestion_cues(S):
    return {
        "plate": S.ls("dig_1") - 0.2,
        "body": S.ls("dig_2") - 0.2,
        "teeth": S.word("dig_3", "teeth"),
        "crush": S.word("dig_3", "crush"),
        "stomach": S.word("dig_4", "stomach"),
        "enzymes": S.word("dig_4", "enzymes"),
        "intestine": S.word("dig_5", "small"),
        "nutrients": S.word("dig_5", "nutrients"),
        "blood": S.word("dig_5", "blood"),
    }


def kidney_cues(S):
    return {
        "kidneys": S.word("kid_1", "kidneys"),
        "filter": S.word("kid_2", "filter"),
        "waste": S.word("kid_2", "waste"),
        "urine": S.word("kid_2", "urine"),
        "balance": S.ls("kid_3") - 0.2,
        "sweat": S.ls("kid_4") - 0.2,
        "return": S.word("kid_4", "return"),
        "less": S.word("kid_4", "less"),
    }


def recovery_cues(S):
    return {
        "sit": S.ls("rec_1") - 0.4,
        "slow": S.ls("rec_2"),
        "minutes": S.word("rec_3", "few"),
        "rest": S.ls("rec_4"),
    }


def recovery_rates(t, c):
    """Heart rate and breathing rate curves; returns (bpm, breaths/min, progress 0..1)."""
    t0 = c["slow"]
    span = max(1.0, (c["rest"] + 2.0) - t0)
    u = min(1.0, max(0.0, (t - t0) / span))
    minutes = u * 5.0
    bpm = 88 + (150 - 88) * math.exp(-minutes / 1.3)
    br = 20 + (40 - 20) * math.exp(-minutes / 1.2)
    return bpm, br, u


def recovery_heart_phase(t, c):
    return phase_decay(t, c["slow"], 150 / 60, 88 / 60, 5.0)


def recovery_breath_phase(t, c):
    return phase_decay(t, c["slow"], 0.66, 0.33, 5.0)


def recap_cues(S):
    return {
        "cards": S.ls("cap_1") - 0.2,
        "eyes": S.ls("cap_2"),
        "muscles": S.ls("cap_3"),
        "lungs": S.ls("cap_4"),
        "heart": S.word("cap_4", "heart"),
        "digestion": S.ls("cap_5"),
        "kidneys": S.word("cap_5", "kidneys"),
        "question": S.ls("cap_6") - 0.4,
        "question_card": S.le("cap_6") + 0.3,
    }


CUE_FUNCS = {
    "intro": intro_cues, "eyes": eyes_cues, "muscles": muscle_cues, "lungs": lungs_cues,
    "heart": heart_cues, "digestion": digestion_cues, "kidneys": kidney_cues,
    "recovery": recovery_cues, "recap": recap_cues,
}


def clamp01(x):
    return max(0.0, min(1.0, x))
