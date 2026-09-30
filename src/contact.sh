#!/usr/bin/env bash
# Tile PNG frames into 2x2 contact sheets: contact.sh <frames_dir> <out_dir>
set -e
in="$1"; out="$2"; mkdir -p "$out"
ls "$in"/*.png | sort > /tmp/frames.txt
i=0
while mapfile -t -n 4 group && ((${#group[@]})); do
  args=(); n=0; for f in "${group[@]}"; do args+=(-i "$f"); n=$((n+1)); done
  while ((n < 4)); do args+=(-f lavfi -i "color=white:s=1920x1080"); n=$((n+1)); done
  ffmpeg -nostdin -loglevel error -y "${args[@]}" -filter_complex "[0][1][2][3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0,scale=1920:-1" -frames:v 1 "$out/sheet_$(printf %02d $i).png"
  i=$((i+1))
done < /tmp/frames.txt
