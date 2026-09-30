"""QA: transcribe the finished MP4 and compare speech with the captions.

Reports overall word error rate against the script and, for each caption,
how well the words heard during that caption's time window match its text.
Usage: python src/qa_captions.py [path/to/video.mp4]
"""

import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import timeline as TL  # noqa: E402

NUMBERS = {"11": "eleven"}


def words(s):
    out = []
    for w in s.replace("-", " ").split():
        n = TL.norm(w)
        n = NUMBERS.get(n, n)
        if n:
            out.append(n)
    return out


def wer(ref, hyp):
    d = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
    for i in range(len(ref) + 1):
        d[i][0] = i
    for j in range(len(hyp) + 1):
        d[0][j] = j
    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1,
                          d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]))
    return d[-1][-1] / max(1, len(ref))


def main():
    from faster_whisper import WhisperModel

    video = sys.argv[1] if len(sys.argv) > 1 else str(TL.ROOT / "output" / "how-your-body-works.mp4")
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    import subprocess
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", video, "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segments, _ = model.transcribe(audio, word_timestamps=True, beam_size=5, vad_filter=False)
    heard = []
    for seg in segments:
        for w in seg.words:
            heard.append((w.word, w.start, w.end))
    caps = json.loads((TL.BUILD / "captions.json").read_text())
    ref = [w for c in caps for w in words(c["text"])]
    hyp = [w for h in heard for w in words(h[0])]
    overall = wer(ref, hyp)
    print(f"words in captions: {len(ref)}, words heard: {len(hyp)}, WER: {overall:.3f}")
    worst = []
    for c in caps:
        inside = [h for h in heard if c["start"] - 0.25 <= (h[1] + h[2]) / 2 <= c["end"] + 0.25]
        hw = [w for h in inside for w in words(h[0])]
        cw = words(c["text"])
        ratio = difflib.SequenceMatcher(None, cw, hw).ratio()
        worst.append((ratio, c["start"], c["text"], " ".join(hw)))
    worst.sort()
    print("lowest per-caption match (caption text vs words heard in its time window):")
    for r, s, t, h in worst[:8]:
        print(f"  {r:.2f} @{s:6.1f}s  caption: {t}\n{'':18}heard:   {h}")
    ok = sum(1 for r, *_ in worst if r >= 0.85)
    print(f"captions with match >= 0.85: {ok}/{len(worst)}")
    (TL.BUILD / "qa_transcript.json").write_text(json.dumps(heard, indent=1))


if __name__ == "__main__":
    main()
