"""Build caption chunks from the narration word timestamps.

Writes:
  build/captions.json              chunks used by the renderer (burned in)
  output/how-your-body-works.srt   sidecar subtitles
  script/timed_script.md           the script with start times per line
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import timeline as TL  # noqa: E402

ROOT = TL.ROOT
MAX_CHARS = 100
HOLD = 0.5


def align(line):
    """Return [(script_word, start, end)] by matching normalised characters."""
    chars = []
    for i, w in enumerate(line["words"]):
        chars += [(ch, i) for ch in TL.norm(w["w"])]
    out, pos = [], 0
    words = line["text"].split()
    for sw in words:
        n = TL.norm(sw)
        if not n:
            continue
        seg = chars[pos:pos + len(n)]
        if "".join(c for c, _ in seg) != n:
            return None
        ws, we = line["words"][seg[0][1]], line["words"][seg[-1][1]]
        out.append((sw, ws["s"], we["e"]))
        pos += len(n)
    return out


def proportional(line):
    words = line["text"].split()
    total = sum(len(w) for w in words)
    t, out = line["start"], []
    span = line["end"] - line["start"]
    for w in words:
        d = span * len(w) / total
        out.append((w, t, t + d))
        t += d
    return out


def chunk(aligned):
    """Keep a sentence together when it fits in two caption lines; otherwise split
    at the most balanced break, preferring punctuation."""
    text_len = len(" ".join(w[0] for w in aligned))
    if text_len <= MAX_CHARS or len(aligned) < 4:
        return [aligned]
    best, best_score = None, None
    for i in range(2, len(aligned) - 1):
        left = len(" ".join(w[0] for w in aligned[:i]))
        right = text_len - left - 1
        score = abs(left - right)
        prev = aligned[i - 1][0]
        if prev[-1] in ".?!:":
            score -= 70
        elif prev[-1] in ",;":
            score -= 22
        if best_score is None or score < best_score:
            best, best_score = i, score
    return chunk(aligned[:best]) + chunk(aligned[best:])


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    tl = TL.load()
    caps, fallbacks = [], []
    for scene in tl["scenes"]:
        for line in scene["lines"]:
            aligned = align(line)
            if aligned is None:
                fallbacks.append(line["id"])
                aligned = proportional(line)
            for ch in chunk(aligned):
                caps.append({"start": round(ch[0][1] - 0.05, 3), "end": round(ch[-1][2], 3),
                             "text": " ".join(w[0] for w in ch), "line": line["id"]})
    for i, c in enumerate(caps):
        nxt = caps[i + 1]["start"] if i + 1 < len(caps) else c["end"] + HOLD
        c["end"] = round(min(c["end"] + HOLD, nxt - 0.02), 3)
    (TL.BUILD / "captions.json").write_text(json.dumps(caps, indent=1))
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    srt = []
    for i, c in enumerate(caps, 1):
        srt.append(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n")
    (out / "how-your-body-works.srt").write_text("\n".join(srt))

    md = ["# How Your Body Works: timed script", "",
          f"Generated from `src/script_data.py` and the narration timeline "
          f"(voice `{tl['voice']}`, speed {tl['speed']}). Total runtime "
          f"{int(tl['duration'] // 60)}:{tl['duration'] % 60:04.1f}.", ""]
    words = 0
    for scene in tl["scenes"]:
        md.append(f"## {scene['title']} ({fmt(scene['start'])} to {fmt(scene['end'])})")
        md.append("")
        md.append("| Start | Line | Narration |")
        md.append("|---|---|---|")
        for line in scene["lines"]:
            words += len(line["text"].split())
            md.append(f"| {fmt(line['start'])} | `{line['id']}` | {line['text']} |")
        md.append("")
    md.append(f"Word count: {words}.")
    (ROOT / "script" / "timed_script.md").write_text("\n".join(md) + "\n")
    print(f"{len(caps)} captions, fallbacks: {fallbacks or 'none'}")


def fmt(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


if __name__ == "__main__":
    main()
