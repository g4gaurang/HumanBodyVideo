"""Render the character and diagram reference sheets into assets/reference/."""

import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).parent))
import gfx as G  # noqa: E402
import maya as M  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets" / "reference"


def character_sheet():
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, G.W, G.H)
    ctx = cairo.Context(s)
    G.rgba(ctx, G.CREAM)
    ctx.paint()
    G.draw_text(ctx, "Maya, age 11: character reference", G.W / 2, 90, 56)
    poses = [("stand", M.stand(0)), ("run A", M.run(0.0)), ("run B", M.run(0.19)),
             ("reach", M.reach()), ("hold ball", M.hold()), ("sit", M.sit(0))]
    for i, (name, p) in enumerate(poses):
        x = 200 + i * 290
        ground = 720
        ctx.move_to(x - 120, ground + 12)
        ctx.line_to(x + 120, ground + 12)
        G.rgba(ctx, G.GRASS_DARK)
        ctx.set_line_width(6)
        ctx.stroke()
        pts = M.draw(ctx, x, ground, 0.95, p)
        if name == "hold ball":
            hx = (pts["near_hand"][0] + pts["far_hand"][0]) / 2 + 20
            hy = (pts["near_hand"][1] + pts["far_hand"][1]) / 2 - 10
            M.draw_ball(ctx, hx, hy, 34)
        G.draw_text(ctx, name, x, 790, 34)
    M.draw_ball(ctx, 1700, 950, 44, 0.4)
    G.draw_text(ctx, "ball", 1700, 1030, 30)
    M.body_outline(ctx, 330, 850, 0.22)
    G.draw_text(ctx, "diagram outline", 330, 1070, 26)
    palette = [(M.SKIN, "skin"), (M.HAIR, "hair"), (M.SHIRT, "shirt"), (M.SHORTS, "shorts"),
               (M.SHOE_STRIPE, "shoe stripe")]
    for i, (c, n) in enumerate(palette):
        x = 620 + i * 190
        G.circle(ctx, x, 920, 34)
        G.fill_stroke(ctx, c, G.INK, 4)
        G.draw_text(ctx, n, x, 990, 26)
    s.write_to_png(str(OUT / "maya_character_sheet.png"))


def diagram_key():
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, G.W, G.H)
    ctx = cairo.Context(s)
    G.rgba(ctx, G.CREAM)
    ctx.paint()
    G.draw_text(ctx, "Diagram colour and arrow key", G.W / 2, 90, 56)
    rows = [
        ("Nerve signal", G.SIGNAL, "signal"),
        ("Air in", G.AIR_IN, "arrow"),
        ("Air out", G.AIR_OUT, "arrow"),
        ("Blood with more oxygen", G.BLOOD_RICH, "flow"),
        ("Blood with less oxygen", G.BLOOD_POOR, "flow"),
        ("Oxygen (O2)", G.O2, "dot"),
        ("Carbon dioxide (CO2)", G.CO2, "dot"),
        ("Nutrients", G.NUTRIENT, "dot"),
        ("Muscle pull", G.ORANGE, "arrow"),
    ]
    for i, (name, c, kind) in enumerate(rows):
        y = 200 + i * 95
        pts = [(300, y), (700, y)]
        if kind == "arrow":
            G.arrow(ctx, pts, c, 14)
        elif kind == "flow":
            G.Path(pts).stroke(ctx, c, 26)
            G.flow_arrows(ctx, pts, G.WHITE, 0.0, size=20, spacing=0.3)
        elif kind == "signal":
            G.Path(pts).stroke(ctx, G.hexc("F2C94C"), 10, 0.5)
            G.dots_along(ctx, pts, c, 0.0, count=4, r=11, glow=True)
        else:
            for k in range(4):
                G.circle(ctx, 330 + k * 110, y, 16)
                G.fill_stroke(ctx, c, G.INK, 3)
        G.draw_text(ctx, name, 780, y + 14, 40, align="left")
    s.write_to_png(str(OUT / "diagram_key.png"))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    character_sheet()
    diagram_key()
    print("wrote", OUT)
