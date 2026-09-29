"""Render the video frames with pycairo and encode them with FFmpeg.

Usage:
  python src/render.py                 # full render -> build/video.mp4 (no audio)
  python src/render.py --preview T...  # write PNG frames at global times T (seconds)
  python src/render.py --scene-frames  # PNG contact frames for every scene
"""

import argparse
import json
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).parent))
import gfx as G  # noqa: E402
import timeline as TL  # noqa: E402
import scenes_a  # noqa: E402
import scenes_b  # noqa: E402
import scenes_c  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
FADE = 0.5

DRAW = {
    "intro": scenes_a.intro, "eyes": scenes_a.eyes, "muscles": scenes_a.muscles,
    "lungs": scenes_b.lungs, "heart": scenes_b.heart, "digestion": scenes_b.digestion,
    "kidneys": scenes_c.kidneys, "recovery": scenes_c.recovery, "recap": scenes_c.recap,
}


class Renderer:
    def __init__(self):
        self.scenes = TL.scenes()
        self.cues = [TL.CUE_FUNCS[s.id](s) for s in self.scenes]
        self.duration = TL.load()["duration"]
        cap_file = BUILD / "captions.json"
        self.captions = json.loads(cap_file.read_text()) if cap_file.exists() else []
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, G.W, G.H)
        self.ctx = cairo.Context(self.surface)

    def scene_index(self, t):
        for i, s in enumerate(self.scenes):
            if t < s.end:
                return i
        return len(self.scenes) - 1

    def draw_scene(self, ctx, i, t):
        s = self.scenes[i]
        ctx.save()
        DRAW[s.id](ctx, t - s.start, s, self.cues[i])
        ctx.restore()

    def caption_at(self, t):
        for c in self.captions:
            if c["start"] <= t < c["end"]:
                a = min(1.0, (t - c["start"]) / 0.12, (c["end"] - t) / 0.12)
                return c["text"], a
        return None, 0

    def frame(self, t):
        ctx = self.ctx
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        i = self.scene_index(t)
        s = self.scenes[i]
        if i > 0 and t - s.start < FADE:
            self.draw_scene(ctx, i - 1, t)
            ctx.push_group()
            self.draw_scene(ctx, i, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(G.ease((t - s.start) / FADE))
        else:
            self.draw_scene(ctx, i, t)
        text, a = self.caption_at(t)
        if text:
            G.caption(ctx, text, a)
        end_fade = G.ease((t - (self.duration - 1.2)) / 1.2)
        if end_fade > 0:
            ctx.set_source_rgba(0, 0, 0, end_fade)
            ctx.paint()
        self.surface.flush()
        return self.surface


def render_chunk(args):
    idx, f0, f1 = args
    r = Renderer()
    out = BUILD / "chunks" / f"chunk_{idx:02d}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0",
           "-s", f"{G.W}x{G.H}", "-r", str(G.FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
           "-g", str(G.FPS * 2), str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        surf = r.frame(f / G.FPS)
        proc.stdin.write(bytes(surf.get_data()))
        if (f - f0) % 300 == 0:
            print(f"chunk {idx}: frame {f - f0}/{f1 - f0}", flush=True)
    proc.stdin.close()
    proc.wait()
    return str(out)


def full_render(workers):
    r = Renderer()
    total = int(round(r.duration * G.FPS))
    (BUILD / "chunks").mkdir(parents=True, exist_ok=True)
    n = workers * 2
    bounds = [round(total * k / n) for k in range(n + 1)]
    jobs = [(k, bounds[k], bounds[k + 1]) for k in range(n)]
    with Pool(workers) as pool:
        outs = pool.map(render_chunk, jobs)
    lst = BUILD / "chunks" / "list.txt"
    lst.write_text("".join(f"file '{Path(o).name}'\n" for o in outs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(BUILD / "video.mp4")], check=True)
    print("frames", total, "->", BUILD / "video.mp4")


def preview(times, outdir):
    r = Renderer()
    outdir.mkdir(parents=True, exist_ok=True)
    for t in times:
        r.frame(t).write_to_png(str(outdir / f"t{t:07.2f}.png"))
    print("wrote", len(times), "frames to", outdir)


def scene_frames(outdir):
    r = Renderer()
    times = []
    for s in r.scenes:
        for l in s.scene["lines"]:
            times.append(round((l["start"] + l["end"]) / 2, 2))
    preview(times, outdir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", nargs="*", type=float)
    ap.add_argument("--scene-frames", action="store_true")
    ap.add_argument("--out", default=str(BUILD / "preview"))
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.preview:
        preview(a.preview, Path(a.out))
    elif a.scene_frames:
        scene_frames(Path(a.out))
    else:
        full_render(a.workers)
