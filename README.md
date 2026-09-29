# HumanBodyVideo

Source for **"How Your Body Works"**, a four-minute animated explainer for an
11-year-old. Maya sees a ball, runs to catch it, and rests afterward; the video
uses that one moment to show how the eyes, brain and nerves, muscles and bones,
lungs, heart and blood, digestion, and kidneys work together, and how breathing
and heart rate slow during recovery.

The finished MP4 is published as a GitHub Release asset, not stored in Git.

## What is in the repository

| Path | Contents |
|---|---|
| `src/script_data.py` | The narration script (single source of truth for voice, captions and cue timing) |
| `script/storyboard.md` | Scene-by-scene storyboard and visual rules (colour key, labels, character) |
| `script/timed_script.md` | Script with start times, generated from the narration timeline |
| `src/narrate.py` | Narration with the open-weight Kokoro-82M voice model (runs locally) |
| `src/timeline.py` | Scene timing and shared cue definitions for visuals and sound effects |
| `src/maya.py` | Maya, drawn as one jointed vector puppet so she looks the same in every scene |
| `src/organs.py` | Simple organ shapes used in the diagrams |
| `src/scenes_a.py`, `scenes_b.py`, `scenes_c.py` | The nine scenes |
| `src/captions.py` | Caption timing from word timestamps, SRT export, timed script |
| `src/audio.py` | Synthesized background music and sound effects, ducking and mix |
| `src/render.py` | Frame renderer (pycairo) and FFmpeg encoding |
| `assets/reference/` | Character sheet and diagram colour key |
| `assets/fonts/` | Nunito font (SIL Open Font License) |
| `build.sh` | One-command build |

## Build

Tested on Ubuntu 24.04 with Python 3.12 and FFmpeg 6.

```bash
sudo apt-get install -y ffmpeg libcairo2-dev pkg-config python3-dev python3-venv espeak-ng
python3 -m venv .venv
.venv/bin/pip install torch==2.14.0 --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install -r requirements.txt
./build.sh --narrate
```

The first narration run downloads the Kokoro model from Hugging Face. Later
builds reuse `build/timeline.json` and `build/narration.wav`; run
`./build.sh --narrate` after editing the script.

Output: `output/how-your-body-works.mp4` (1920x1080, 30 fps, H.264 + AAC) and
`output/how-your-body-works.srt`.

## Editing tips

- Change wording in `src/script_data.py`, then rebuild with `--narrate`. Visual
  cues are tied to words (for example the "retina" label appears when the word
  is spoken), so if you remove a cue word, update the matching function in
  `src/timeline.py`.
- Preview single frames without a full render:
  `.venv/bin/python src/render.py --preview 30 95 150` writes PNGs to `build/preview/`.
