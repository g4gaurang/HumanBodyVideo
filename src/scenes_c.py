"""Scenes 7-9: kidneys, recovery, recap and question."""

import math

import cairo

import gfx as G
import maya as M
import organs as O
import scenes_a as A
import scenes_b as B
from gfx import ease, ramp, window, lerp, clamp
from timeline import recovery_rates, recovery_heart_phase, recovery_breath_phase

URINE = G.hexc("F4D35E")
WATER = G.hexc("62B6FF")
WASTE = G.hexc("B5A33A")


# Scene 7: kidneys ---------------------------------------------------------
KB = (620, 0, 1.1)  # back-view body: centre x, top, scale


def _kx(x):
    return KB[0] + x * KB[2]


def _ky(y):
    return KB[1] + y * KB[2]


K_LEFT = (_kx(-82), _ky(390))   # Maya's left kidney (viewer's left in a back view)
K_RIGHT = (_kx(82), _ky(402))
AORTA_X = _kx(-12)
IVC_X = _kx(12)
BLADDER = (_kx(0), _ky(528))


def kidney_body(ctx, t, c, alpha, urine_rate=1.0):
    M.body_outline(ctx, KB[0], KB[1], KB[2], alpha, back=True)
    top, bot = _ky(260), _ky(500)
    B.vessel(ctx, [(AORTA_X, top), (AORTA_X, bot)], G.BLOOD_RICH, alpha, 14)
    B.vessel(ctx, [(IVC_X, top), (IVC_X, bot)], G.BLOOD_POOR, alpha, 14)
    for (kx, ky), flip in ((K_LEFT, False), (K_RIGHT, True)):
        hil = kx + (22 if not flip else -22)
        B.vessel(ctx, [(AORTA_X, ky - 12), (hil, ky - 12)], G.BLOOD_RICH, alpha, 9)
        B.vessel(ctx, [(hil, ky + 6), (IVC_X, ky + 6)], G.BLOOD_POOR, alpha, 9)
    for (kx, ky), flip in ((K_LEFT, False), (K_RIGHT, True)):
        O.kidney(ctx, kx, ky, 0.5 * KB[2], alpha, flip=not flip)
    ureters = []
    for (kx, ky), flip in ((K_LEFT, False), (K_RIGHT, True)):
        hil = kx + (18 if not flip else -18)
        pts = G.smooth_path([(hil, ky + 22), (hil + (8 if not flip else -8), ky + 70),
                             (BLADDER[0] + (-18 if not flip else 18), BLADDER[1] - 30)], 10)
        ureters.append(pts)
        G.Path(pts).stroke(ctx, G.INK, 11, alpha)
        G.Path(pts).stroke(ctx, URINE, 6, alpha)
    ctx.save()
    ctx.translate(*BLADDER)
    ctx.scale(1.2, 0.9)
    G.circle(ctx, 0, 0, 34)
    ctx.restore()
    G.fill_stroke(ctx, G.hexc("FFF0B8"), G.INK, 4, alpha)
    ft = t
    for (kx, ky), flip in ((K_LEFT, False), (K_RIGHT, True)):
        hil = kx + (22 if not flip else -22)
        G.dots_along(ctx, [(AORTA_X, ky - 12), (hil, ky - 12)], G.WHITE, ft, speed=0.8, count=2, r=4, alpha=alpha)
    ua = ramp(t, c["urine"], 0.4) * alpha
    if ua > 0:
        for pts in ureters:
            G.dots_along(ctx, pts, URINE, ft, speed=0.35, count=max(1, int(3 * urine_rate)), r=6, alpha=ua)


def filter_panel(ctx, t, c, alpha):
    if alpha <= 0:
        return
    x0, y0, w, h = 1080, 130, 760, 660
    G.panel(ctx, x0, y0, w, h, alpha)
    G.draw_text(ctx, "Inside a kidney", x0 + w / 2, y0 + 60, 38, alpha=alpha)
    kx, ky = x0 + 470, y0 + 360
    O.kidney(ctx, kx, ky, 2.3, alpha, fill=G.hexc("E7A0A8"))
    # filter: a mesh of tiny tubes
    for i in range(7):
        for j in range(4):
            G.circle(ctx, kx + 10 + j * 30, ky - 100 + i * 32, 10)
            G.fill_stroke(ctx, G.hexc("F7D3D8"), O.KIDNEY_LINE, 2, alpha)
    blood_in = [(x0 + 30, y0 + 190), (x0 + 250, y0 + 190), (kx - 40, ky - 110), (kx + 40, ky - 90)]
    blood_out = [(kx + 30, ky + 30), (kx - 40, ky + 10), (x0 + 250, y0 + 380), (x0 + 30, y0 + 380)]
    ureter = [(kx + 40, ky + 60), (kx - 40, ky + 120), (x0 + 300, y0 + 560), (x0 + 300, y0 + 650)]
    B.vessel(ctx, blood_in[:2] + [(kx - 40, ky - 110)], G.BLOOD_RICH, alpha, 34)
    B.vessel(ctx, [(kx - 40, ky + 10)] + blood_out[2:], G.BLOOD_POOR, alpha, 34)
    G.Path([(kx - 40, ky + 120)] + ureter[2:]).stroke(ctx, G.INK, 30, alpha)
    G.Path([(kx - 40, ky + 120)] + ureter[2:]).stroke(ctx, URINE, 22, alpha)
    ft = t - c["kidneys"]
    G.dots_along(ctx, blood_in, G.WHITE, ft, speed=0.25, count=5, r=7, alpha=alpha)
    G.dots_along(ctx, blood_out, G.WHITE, ft, speed=0.25, count=5, r=7, alpha=alpha)
    wa = ramp(t, c["waste"], 0.4) * alpha
    if wa > 0:
        G.dots_along(ctx, blood_in, WASTE, ft, speed=0.25, count=3, r=10, alpha=wa, phase=0.08)
        path = blood_in[:3] + [(kx + 20, ky)] + ureter[1:]
        for i in range(4):
            u = ((t - c["waste"]) * 0.18 + i / 4) % 1.0
            x, y, _ = G.Path(path).at(u)
            fade = min(1, u / 0.08, (1 - u) / 0.08)
            if i % 2:
                O.water_drop(ctx, x, y, 9, WATER, wa * fade)
            else:
                G.circle(ctx, x, y, 10)
                G.fill_stroke(ctx, WASTE, G.INK, 2, wa * fade)
    G.label(ctx, "filter", kx + 190, ky - 180, window(t, c["filter"], c["balance"]) * alpha, anchor=(kx + 60, ky - 80))
    G.label(ctx, "waste + extra water", x0 + 330, y0 + 130, window(t, c["waste"], c["balance"]) * alpha, size=32, bg=G.hexc("FFF6D6"))
    G.label(ctx, "urine", x0 + 440, y0 + 600, window(t, c["urine"], c["balance"]) * alpha, anchor=(x0 + 318, y0 + 600), bg=G.hexc("FFF6D6"))
    G.label(ctx, "cleaned blood", x0 + 180, y0 + 440, window(t, c["urine"] - 1.0, c["balance"]) * alpha, size=30)


def balance_panel(ctx, t, c, alpha):
    if alpha <= 0:
        return
    x0, y0, w, h = 1080, 130, 760, 660
    G.panel(ctx, x0, y0, w, h, alpha)
    G.draw_text(ctx, "Keeping a balance", x0 + w / 2, y0 + 60, 38, alpha=alpha)
    cx, cy = x0 + w / 2, y0 + 250
    tilt = 0.18 * math.sin((t - c["balance"]) * 2.5) * math.exp(-(t - c["balance"]) * 0.9)
    ctx.move_to(cx, cy)
    ctx.line_to(cx - 60, y0 + 560)
    ctx.line_to(cx + 60, y0 + 560)
    ctx.close_path()
    G.fill_stroke(ctx, G.hexc("C9D3E0"), G.INK, 4, alpha)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(tilt)
    ctx.rectangle(-260, -10, 520, 20)
    G.fill_stroke(ctx, G.hexc("A9B6C8"), G.INK, 4, alpha)
    ends = [ctx.user_to_device(-240, 0), ctx.user_to_device(240, 0)]
    ctx.restore()
    for i, (ex, ey) in enumerate(ends):
        ctx.move_to(ex, ey)
        ctx.line_to(ex - 70, ey + 130)
        ctx.move_to(ex, ey)
        ctx.line_to(ex + 70, ey + 130)
        G.rgba(ctx, G.INK, alpha)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.save()
        ctx.translate(ex, ey + 140)
        ctx.scale(1, 0.3)
        G.circle(ctx, 0, 0, 90)
        ctx.restore()
        G.fill_stroke(ctx, G.hexc("E2E8F0"), G.INK, 4, alpha)
        if i == 0:
            for k in range(3):
                O.water_drop(ctx, ex - 40 + k * 40, ey + 110, 14, WATER, alpha)
            G.draw_text(ctx, "water", ex, ey + 220, 36, alpha=alpha)
        else:
            for k in range(4):
                G.rounded_rect(ctx, ex - 55 + k * 28, ey + 100 - (k % 2) * 16, 24, 24, 4)
                G.fill_stroke(ctx, G.WHITE, G.INK, 3, alpha)
            G.draw_text(ctx, "salts", ex, ey + 220, 36, alpha=alpha)


def sweat_panel(ctx, t, c, alpha):
    if alpha <= 0:
        return
    x0, y0, w, h = 1080, 130, 760, 660
    G.panel(ctx, x0, y0, w, h, alpha)
    ctx.save()
    G.rounded_rect(ctx, x0 + 30, y0 + 30, 330, 600, 30)
    ctx.clip()
    G.gradient_bg(ctx, G.hexc("FFD27A"), G.hexc("FFF1C9"))
    G.circle(ctx, x0 + 90, y0 + 90, 45)
    G.rgba(ctx, G.YELLOW)
    ctx.fill()
    ctx.rectangle(x0 + 30, y0 + 520, 330, 120)
    G.rgba(ctx, G.GRASS)
    ctx.fill()
    pts = M.draw(ctx, x0 + 190, y0 + 540, 0.72, M.stand(t))
    hx, hy = pts["head"]
    for i in range(3):
        u = ((t - c["sweat"]) * 0.7 + i / 3) % 1.0
        O.water_drop(ctx, hx - 50 + i * 14, hy - 20 + u * 70, 8, WATER, min(1, (1 - u) * 3))
    ctx.restore()
    G.rounded_rect(ctx, x0 + 30, y0 + 30, 330, 600, 30)
    G.rgba(ctx, G.INK, alpha)
    ctx.set_line_width(4)
    ctx.stroke()
    # bars
    k1 = ease((t - c["return"]) / 1.2)
    k2 = ease((t - c["less"]) / 1.0)
    bx = x0 + 420
    bars = [("water back to blood", WATER, lerp(0.5, 0.9, k1)), ("urine", URINE, lerp(0.5, 0.2, k2))]
    for i, (name, col, v) in enumerate(bars):
        by = y0 + 120 + i * 260
        G.draw_text(ctx, name, bx, by, 32, align="left", alpha=alpha)
        G.rounded_rect(ctx, bx, by + 30, 300, 60, 30)
        G.fill_stroke(ctx, G.hexc("EEF2F7"), G.INK, 4, alpha)
        G.rounded_rect(ctx, bx + 6, by + 36, 288 * v, 48, 24)
        G.rgba(ctx, col, alpha)
        ctx.fill()
        if i == 0 and k1 > 0.05:
            G.arrow(ctx, [(bx + 150, by + 170), (bx + 150, by + 110)], G.hexc("2BA84A"), 10, alpha * k1)
        if i == 1 and k2 > 0.05:
            G.arrow(ctx, [(bx + 150, by + 110), (bx + 150, by + 170)], G.CORAL, 10, alpha * k2)


def kidneys(ctx, t, S, c):
    G.soft_bg(ctx, G.hexc("F1F8EC"), t)
    rate = lerp(1.0, 0.34, ease((t - c["less"]) / 1.0))
    kidney_body(ctx, t, c, 1.0, rate)
    G.label(ctx, "kidneys", 330, 360, ramp(t, c["kidneys"]), anchor=(K_LEFT[0] - 30, K_LEFT[1]))
    G.label(ctx, "bladder", 330, 620, ramp(t, c["urine"]), anchor=(BLADDER[0] - 40, BLADDER[1]), size=34)
    G.draw_text(ctx, "back view", KB[0] - 330, 230, 30, G.hexc("6B7080"), alpha=ramp(t, 0.5))
    filter_panel(ctx, t, c, window(t, c["kidneys"] + 0.4, c["balance"] + 0.3, 0.5))
    balance_panel(ctx, t, c, window(t, c["balance"] + 0.3, c["sweat"] + 0.3, 0.5))
    sweat_panel(ctx, t, c, ramp(t, c["sweat"] + 0.3, 0.5))
    G.scene_title(ctx, "Kidneys", t)


# Scene 8: recovery ------------------------------------------------------
def chart(ctx, x, y, w, h, title, unit, values, color, lo_hi, rest, alpha, u, icon):
    G.panel(ctx, x, y, w, h, alpha, r=30)
    G.draw_text(ctx, title, x + 90, y + 55, 36, align="left", alpha=alpha)
    current = values(u)
    G.draw_text(ctx, f"{int(round(current))}", x + w - 40, y + 60, 56, color, align="right", alpha=alpha)
    G.draw_text(ctx, unit, x + w - 40, y + 92, 22, G.hexc("6B7080"), align="right", alpha=alpha)
    icon(x + 50, y + 45)
    gx, gy, gw, gh = x + 60, y + 115, w - 120, h - 175
    lo, hi = lo_hi
    ctx.move_to(gx, gy)
    ctx.line_to(gx, gy + gh)
    ctx.line_to(gx + gw, gy + gh)
    G.rgba(ctx, G.INK, alpha)
    ctx.set_line_width(3)
    ctx.stroke()
    ry = gy + gh - (rest - lo) / (hi - lo) * gh
    ctx.set_dash([12, 10])
    ctx.move_to(gx, ry)
    ctx.line_to(gx + gw, ry)
    G.rgba(ctx, G.hexc("8D99AE"), alpha)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.set_dash([])
    G.draw_text(ctx, "resting", gx + gw - 6, ry - 10, 22, G.hexc("6B7080"), align="right", alpha=alpha)
    pts = []
    n = 60
    for i in range(n + 1):
        uu = i / n * u
        v = values(uu)
        pts.append((gx + uu * gw, gy + gh - (v - lo) / (hi - lo) * gh))
    if len(pts) > 1:
        G.Path(pts).stroke(ctx, color, 7, alpha)
        G.circle(ctx, pts[-1][0], pts[-1][1], 10)
        G.rgba(ctx, color, alpha)
        ctx.fill()
    for m in range(6):
        G.draw_text(ctx, str(m), gx + m * gw / 5, gy + gh + 30, 22, G.hexc("6B7080"), alpha=alpha)


def recovery(ctx, t, S, c):
    A.park(ctx, t)
    bph = recovery_breath_phase(t, c)
    p = M.sit(0)
    p["breath"] = math.sin(2 * math.pi * bph) * 2.0
    p["mouth"] = 0.6 * (1 - ramp(t, c["minutes"] + 2.0, 2.0))
    x = 470
    M.draw(ctx, x, A.GROUND, 1.0, p, alpha=ramp(t, c["sit"], 0.5))
    M.draw_ball(ctx, x + 330, A.GROUND - 34, 38, 0.6)
    bpm, br, u = recovery_rates(t, c)
    ca = ramp(t, c["slow"] - 0.5, 0.6)
    if ca > 0:
        hph = recovery_heart_phase(t, c)
        frac = hph % 1.0
        beat = math.exp(-frac * 9)

        def heart_icon(ix, iy):
            O.heart(ctx, ix, iy, 0.22, ca, beat, split=False)

        def lung_icon(ix, iy):
            B.lungs_icon(ctx, ix, iy + 4, 0.28 + 0.02 * math.sin(2 * math.pi * bph), ca)

        def hr(uu):
            return 88 + (150 - 88) * math.exp(-uu * 5 / 1.3)

        def brf(uu):
            return 20 + (40 - 20) * math.exp(-uu * 5 / 1.2)

        chart(ctx, 1020, 110, 820, 340, "heart rate", "beats per minute", hr, G.BLOOD_RICH, (70, 160), 88, ca, u, heart_icon)
        chart(ctx, 1020, 480, 820, 340, "breathing", "breaths per minute", brf, G.hexc("1E9BE8"), (10, 45), 20, ca, u, lung_icon)
        G.draw_text(ctx, "minutes of rest", 1430, 855, 26, G.INK, alpha=ca)
    G.scene_title(ctx, "Recovery", t)


# Scene 9: recap and question ---------------------------------------------
CARDS = [
    ("eyes, brain, nerves", "eyes"), ("muscles + bones", "muscles"), ("lungs", "lungs"),
    ("heart", "heart"), ("digestion", "digestion"), ("kidneys", "kidneys"),
]


def card_icon(ctx, kind, x, y, a, t):
    if kind == "eyes":
        O.eye_icon(ctx, x - 50, y + 10, 34, a)
        O.brain(ctx, x + 40, y, 0.42, a)
    elif kind == "muscles":
        O.bone(ctx, x - 70, y + 40, x + 70, y - 40, 18, a)
        O.muscle_spindle(ctx, x - 60, y + 5, x + 60, y - 65, 40, O.MUSCLE_ICON, a)
    elif kind == "lungs":
        B.lungs_icon(ctx, x, y + 5, 0.55, a)
    elif kind == "heart":
        O.heart(ctx, x, y, 0.55, a, max(0, math.sin(t * 7)) ** 4)
    elif kind == "digestion":
        O.stomach(ctx, x, y, 0.75, 0, a)
    elif kind == "kidneys":
        O.kidney(ctx, x - 40, y, 0.42, a, flip=True)
        O.kidney(ctx, x + 40, y, 0.42, a)


def recap_cards(ctx, t, c, alpha):
    order = ["eyes", "muscles", "lungs", "heart", "digestion", "kidneys"]
    cw, ch = 330, 290
    for i, (title, key) in enumerate(CARDS):
        col, row = i % 3, i // 3
        x = 700 + col * (cw + 40)
        y = 140 + row * (ch + 40)
        appear = ramp(t, c["cards"] + i * 0.15, 0.4) * alpha
        if appear <= 0:
            continue
        lit = ramp(t, c[key], 0.3)
        active = window(t, c[key], c[order[i + 1]] if i + 1 < len(order) else c["question"], 0.3)
        sc = 1 + 0.06 * active
        ctx.save()
        ctx.translate(x + cw / 2, y + ch / 2)
        ctx.scale(sc, sc)
        ctx.translate(-(x + cw / 2), -(y + ch / 2))
        G.rounded_rect(ctx, x + 6, y + 10, cw, ch, 30)
        ctx.set_source_rgba(0, 0, 0, 0.1 * appear)
        ctx.fill()
        G.rounded_rect(ctx, x, y, cw, ch, 30)
        G.fill_stroke(ctx, G.WHITE if lit > 0.5 else G.hexc("F3F4F8"),
                      G.ORANGE if active > 0.5 else G.INK, 7 if active > 0.5 else 4, appear)
        card_icon(ctx, key, x + cw / 2, y + 120, appear * (0.35 + 0.65 * lit), t)
        G.draw_text(ctx, title, x + cw / 2, y + ch - 36, 34, alpha=appear * (0.5 + 0.5 * lit))
        ctx.restore()


def bedroom(ctx, t, c, alpha):
    if alpha <= 0:
        return
    ctx.push_group()
    G.gradient_bg(ctx, G.hexc("1F2A55"), G.hexc("3A4A80"))
    # window with moon and stars
    wx, wy, ww, wh = 1250, 120, 520, 380
    G.rounded_rect(ctx, wx, wy, ww, wh, 20)
    G.fill_stroke(ctx, G.hexc("0F1838"), G.hexc("C9D3E0"), 14)
    G.circle(ctx, wx + 380, wy + 120, 55)
    G.rgba(ctx, G.hexc("FFF3B0"))
    ctx.fill()
    G.circle(ctx, wx + 405, wy + 105, 50)
    G.rgba(ctx, G.hexc("0F1838"))
    ctx.fill()
    for i in range(12):
        sx = wx + 40 + (i * 97) % (ww - 80)
        sy = wy + 40 + (i * 61) % (wh - 80)
        tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        G.circle(ctx, sx, sy, 3 + 2 * tw)
        ctx.set_source_rgba(1, 1, 0.85, 0.5 + 0.5 * tw)
        ctx.fill()
    ctx.move_to(wx + ww / 2, wy)
    ctx.line_to(wx + ww / 2, wy + wh)
    ctx.move_to(wx, wy + wh / 2)
    ctx.line_to(wx + ww, wy + wh / 2)
    G.rgba(ctx, G.hexc("C9D3E0"))
    ctx.set_line_width(10)
    ctx.stroke()
    # floor and bed
    ctx.rectangle(0, 800, G.W, 280)
    G.rgba(ctx, G.hexc("2A3566"))
    ctx.fill()
    G.rounded_rect(ctx, 380, 640, 900, 120, 24)
    G.fill_stroke(ctx, G.hexc("8C6BB1"), G.INK, 5)
    ctx.rectangle(390, 750, 30, 90)
    ctx.rectangle(1240, 750, 30, 90)
    G.rgba(ctx, G.hexc("5B4A7A"))
    ctx.fill()
    G.rounded_rect(ctx, 410, 565, 250, 90, 40)
    G.fill_stroke(ctx, G.WHITE, G.INK, 5)
    # Maya asleep: head on the pillow, the rest of her under the blanket
    ctx.save()
    ctx.translate(560, 560)
    ctx.scale(0.95, 0.95)
    ctx.rotate(math.radians(-62))
    M._head(ctx, 0, 0, M.pose(eyes=0.0, mouth=0.0, tail=40), 1.0, ear=False)
    ctx.restore()
    rise = 7 * math.sin(2 * math.pi * 0.22 * t)
    ctx.move_to(610, 655)
    ctx.curve_to(640, 560 - rise, 820, 545 - rise, 940, 575)
    ctx.curve_to(1040, 600, 1150, 590, 1200, 570)
    ctx.curve_to(1240, 560, 1270, 600, 1275, 655)
    ctx.close_path()
    G.fill_stroke(ctx, G.hexc("FF8A3D"), G.INK, 5)
    for i in range(5):
        x = 720 + i * 110
        ctx.move_to(x, 600 - rise * 0.5 + (10 if i > 1 else 0))
        ctx.line_to(x, 652)
        G.rgba(ctx, G.hexc("E0702A"))
        ctx.set_line_width(4)
        ctx.stroke()
    # thought bubble with a question mark
    for (bx, by, r) in ((600, 470, 14), (640, 420, 22)):
        G.circle(ctx, bx, by, r)
        G.fill_stroke(ctx, G.WHITE, G.INK, 3)
    G.circle(ctx, 760, 300, 110)
    G.fill_stroke(ctx, G.WHITE, G.INK, 4)
    O.heart(ctx, 710, 300, 0.32, 1.0, max(0, math.sin(t * 4)) ** 4, split=False)
    B.lungs_icon(ctx, 805, 300, 0.32, 1.0)
    G.draw_text(ctx, "?", 760, 385, 50, G.hexc("E0702A"))
    zz = (t * 0.6) % 1.0
    G.draw_text(ctx, "z", 470 + zz * 40, 500 - zz * 60, 40 + zz * 20, G.WHITE, alpha=1 - zz)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)


def recap(ctx, t, S, c):
    G.soft_bg(ctx, G.CREAM, t)
    qa = ramp(t, c["question"], 0.8)
    if qa < 1:
        pts_pose = M.hold(t)
        pts = M.draw(ctx, 360, 820, 1.05, pts_pose)
        hx = (pts["near_hand"][0] + pts["far_hand"][0]) / 2 + 30
        hy = (pts["near_hand"][1] + pts["far_hand"][1]) / 2 - 5
        M.draw_ball(ctx, hx, hy, 44)
        recap_cards(ctx, t, c, 1.0)
        G.draw_text(ctx, "One catch, a whole team", 1235, 95, 48, G.hexc("E0702A"), alpha=ramp(t, c["cards"]))
    bedroom(ctx, t, c, qa)
    if qa > 0:
        pa = ramp(t, c["question"] + 0.6, 0.6)
        G.panel(ctx, 160, 40, 1600, 64 + 2 * 64, pa, fill=G.CREAM, r=40)
        G.draw_text(ctx, "Something to think about:", 960, 110, 44, G.hexc("E0702A"), alpha=pa)
        G.draw_text(ctx, "When you're asleep, what happens to your breathing and heartbeat? Why?",
                    960, 175, 42, alpha=pa)
