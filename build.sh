#!/usr/bin/env bash
# Build output/how-your-body-works.mp4 from source.
#
#   ./build.sh            full build (reuses existing narration if present)
#   ./build.sh --narrate  regenerate the narration audio first
#
# Needs: Python venv at .venv (see README), FFmpeg with libx264, and system
# packages libcairo2-dev and espeak-ng.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv/bin/python}
mkdir -p build output

# The renderer selects the Nunito font through fontconfig.
if ! fc-list | grep -qi nunito; then
  mkdir -p ~/.local/share/fonts
  cp assets/fonts/Nunito.ttf ~/.local/share/fonts/
  fc-cache -f >/dev/null
fi

if [[ "${1:-}" == "--narrate" || ! -f build/timeline.json ]]; then
  echo "== narration"
  $PY src/narrate.py
fi

echo "== reference sheets"
$PY src/reference_sheet.py

echo "== captions"
$PY src/captions.py

echo "== music, sound effects and mix"
$PY src/audio.py

echo "== frames"
$PY src/render.py --workers "${WORKERS:-4}"

echo "== final mux"
ffmpeg -nostdin -y -loglevel error -i build/video.mp4 -i build/mix.wav \
  -map 0:v -map 1:a -c:v copy \
  -af "acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest \
  output/how-your-body-works.mp4

ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate \
  -of default=nw=1 output/how-your-body-works.mp4
echo "done: output/how-your-body-works.mp4"
