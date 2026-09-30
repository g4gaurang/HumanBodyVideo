# Plan: "How Your Body Works" (four-minute video)

## Tool check (verified in the build environment)
- Available: FFmpeg 6 (libx264, AAC, drawtext, libass), Python 3.12, Node 22, Chrome.
- Not installed / not configured: Manim, Remotion, Motion Canvas, paid TTS or
  image APIs. No API keys present.
- Chosen stack:
  - Visuals: Python + pycairo, fully procedural vector drawing (controllable
    diagrams, consistent character).
  - Narration: Kokoro-82M open-weight TTS (local CPU, Apache-2.0), voice `af_heart`.
  - Music and sound effects: synthesized with numpy (no licensing questions).
  - Captions: burned in from Kokoro word timestamps, plus an `.srt` sidecar.
  - Assembly: FFmpeg.

## Steps
- [x] Inspect repository (only a README existed)
- [x] Write script in `src/script_data.py` (544 words), accuracy review
- [x] Storyboard `script/storyboard.md`
- [x] Narration + timeline (`src/narrate.py`)
- [ ] Character reference sheet and diagram style (`src/render.py`)
- [ ] Scene renderer for the 9 scenes
- [ ] Music and sound effects (`src/audio.py`)
- [ ] Captions (`src/captions.py`) and timed script
- [ ] Assemble `output/how-your-body-works.mp4` (`build.sh`)
- [ ] QA: duration, frames from every scene, loudness, caption vs. speech (ASR)
- [ ] Commit sources, `.gitignore` MP4 and build files
- [ ] GitHub Release with the MP4 asset, verify download checksum

## Review
(filled in after QA)
