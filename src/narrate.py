"""Generate narration audio and the master timeline.

Uses the open-weight Kokoro-82M text-to-speech model (runs locally on CPU).
Writes:
  build/narration.wav   full narration track (24 kHz mono)
  build/timeline.json   scene and line timings, with per-word timestamps
"""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import script_data as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SR = 24000
VOICE = "af_heart"
SPEED = 0.88


def synth_line(pipeline, text):
    chunks, words, offset = [], [], 0.0
    for result in pipeline(text, voice=VOICE, speed=SPEED):
        audio = result.audio.numpy() if hasattr(result.audio, "numpy") else np.asarray(result.audio)
        for tok in result.tokens or []:
            if tok.start_ts is None or not tok.text.strip():
                continue
            if all(not c.isalnum() for c in tok.text):
                continue
            words.append({"w": tok.text, "s": offset + tok.start_ts, "e": offset + tok.end_ts})
        chunks.append(audio)
        offset += len(audio) / SR
    audio = np.concatenate(chunks)
    # Trim leading/trailing near-silence so line timing is tight.
    thresh = 0.01 * np.max(np.abs(audio))
    idx = np.nonzero(np.abs(audio) > thresh)[0]
    lead = max(0, idx[0] - int(0.03 * SR))
    tail = min(len(audio), idx[-1] + int(0.08 * SR))
    audio = audio[lead:tail]
    shift = lead / SR
    for w in words:
        w["s"] = max(0.0, w["s"] - shift)
        w["e"] = max(w["s"], w["e"] - shift)
    return audio, words


def main():
    from kokoro import KPipeline

    BUILD.mkdir(exist_ok=True)
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    t = 0.0
    pieces = []
    timeline = {"voice": VOICE, "speed": SPEED, "scenes": []}
    for scene in S.SCENES:
        sc = {"id": scene["id"], "title": scene["title"], "start": t, "lines": []}
        lead = scene.get("lead", S.SCENE_LEAD)
        pieces.append(np.zeros(int(lead * SR)))
        t += lead
        for entry in scene["lines"]:
            line_id, text = entry[0], entry[1]
            gap = entry[2] if len(entry) > 2 else S.DEFAULT_GAP
            audio, words = synth_line(pipeline, text)
            dur = len(audio) / SR
            for w in words:
                w["s"] = round(w["s"] + t, 3)
                w["e"] = round(w["e"] + t, 3)
            sc["lines"].append({"id": line_id, "text": text, "start": round(t, 3),
                                "end": round(t + dur, 3), "words": words})
            print(f"{line_id:8s} {t:7.2f}s  {dur:5.2f}s  {text[:60]}")
            pieces.append(audio)
            pieces.append(np.zeros(int(gap * SR)))
            t += dur + gap
        tail = scene.get("tail", S.SCENE_TAIL)
        pieces.append(np.zeros(int(tail * SR)))
        t += tail
        sc["end"] = round(t, 3)
        timeline["scenes"].append(sc)
    track = np.concatenate(pieces).astype(np.float32)
    total = len(track) / SR
    timeline["duration"] = round(total, 3)
    sf.write(BUILD / "narration.wav", track, SR)
    (BUILD / "timeline.json").write_text(json.dumps(timeline, indent=1))
    print(f"total {total:.2f}s  words {S.word_count()}")


if __name__ == "__main__":
    main()
