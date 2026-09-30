"""Scenes 4-6: lungs, heart and blood, digestion."""

import math

import cairo

import gfx as G
import maya as M
import organs as O
import scenes_a as A
from gfx import ease, ramp, window, lerp, clamp
from timeline import breath_phase_lungs, heart_phase, heart_bpm

BLOOD_LEGEND = [(G.BLOOD_RICH, "blood with more oxygen"), (G.BLOOD_POOR, "blood with less oxygen")]


# Scene 4: lungs -----------------------------------------------------------
LCX = 700  # body centre x in the lung view
AIRWAY = [(LCX, 214), (LCX, 250), (LCX, 300), (LCX, 440)]
BRONCHI = [[(LCX, 440), (LCX - 50, 480), (LCX - 95, 540)], [(LCX, 440), (LCX + 50, 480), (LCX + 90, 540)]]


def lungs_body(ctx, t, c, alpha):
    ph = breath_phase_lungs(t, c)
    depth = 0.55 + 0.45 * ramp(t, c["faster"], 3.0)
    s = math.sin(2 * math.pi * ph)
    fill = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    M.body_outline(ctx, LCX, 40, 1.2, alpha)
    expand = 1 + 0.08 * depth * fill
    for left in (False, True):
        cx = LCX + (95 if left else -100)
        ctx.save()
        ctx.translate(cx, 560)
        ctx.scale(expand, expand)
        O.lung_shape(ctx, 0, 0, 140 if left else 150, 300, left)
        G.rgba(ctx, O.LUNG, alpha)
        ctx.fill_preserve()
        G.rgba(ctx, O.LUNG_LINE, alpha)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.restore()
    # airway tube
    pts = AIRWAY
    G.Path(pts).stroke(ctx, G.hexc("7FB8D6"), 40, alpha)
    G.Path(pts).stroke(ctx, G.WHITE, 30, alpha)
    for b in BRONCHI:
        G.Path(b).stroke(ctx, G.hexc("7FB8D6"), 30, alpha)
        G.Path(b).stroke(ctx, G.WHITE, 20, alpha)
    for y in range(310, 430, 22):
        ctx.move_to(LCX - 11, y)
        ctx.line_to(LCX + 11, y)
        G.rgba(ctx, G.hexc("9CCBE3"), alpha)
        ctx.set_line_width(3)
        ctx.stroke()
    # airflow chevrons
    a_in = max(0.0, s) * alpha
    a_out = max(0.0, -s) * alpha
    for b in BRONCHI:
        path = AIRWAY + b[1:]
        G.flow_arrows(ctx, path, G.hexc("1E9BE8"), t, speed=0.5, spacing=0.25, size=30, alpha=a_in)
        G.flow_arrows(ctx, path[::-1], G.hexc("8C6FD9"), t, speed=0.5, spacing=0.25, size=30, alpha=a_out)
    # air entering / leaving at the nose and mouth
    for (x0, x1, y) in ((LCX - 140, LCX - 40, 190), (LCX + 140, LCX + 40, 220)):
        G.arrow(ctx, [(x0, y), (x1, y)], G.hexc("1E9BE8"), 9, a_in)
        G.arrow(ctx, [(x1, y), (x0, y)], G.hexc("8C6FD9"), 9, a_out)
    return s


def energy_panel(ctx, t, c, alpha):
    if alpha <= 0:
        return
    x0, y0 = 1180, 190
    G.panel(ctx, x0, y0, 620, 250, alpha)
    G.draw_text(ctx, "Inside working muscle cells", x0 + 310, y0 + 55, 34, alpha=alpha)
    # apple
    ax, ay = x0 + 90, y0 + 150
    G.circle(ctx, ax, ay, 40)
    G.fill_stroke(ctx, G.hexc("FF5A5F"), G.INK, 4, alpha)
    ctx.move_to(ax, ay - 38)
    ctx.line_to(ax + 6, ay - 58)
    G.rgba(ctx, G.INK, alpha)
    ctx.set_line_width(5)
    ctx.stroke()
    G.draw_text(ctx, "food", ax, ay + 76, 28, alpha=alpha)
    G.draw_text(ctx, "+", x0 + 175, ay + 14, 54, alpha=alpha)
    G.circle(ctx, x0 + 260, ay, 36)
    G.fill_stroke(ctx, G.O2, G.INK, 4, alpha)
    G.draw_text(ctx, "O2", x0 + 260, ay + 12, 32, G.WHITE, alpha=alpha)
    G.draw_text(ctx, "oxygen", x0 + 260, ay + 76, 28, alpha=alpha)
    G.arrow(ctx, [(x0 + 330, ay), (x0 + 440, ay)], G.INK, 8, alpha)
    # lightning bolt
    bx, by = x0 + 520, ay
    ctx.move_to(bx + 10, by - 55)
    ctx.line_to(bx - 25, by + 8)
    ctx.line_to(bx + 2, by + 8)
    ctx.line_to(bx - 12, by + 58)
    ctx.line_to(bx + 30, by - 10)
    ctx.line_to(bx + 2, by - 10)
    ctx.close_path()
    G.fill_stroke(ctx, G.YELLOW, G.INK, 4, alpha)
    G.draw_text(ctx, "energy", bx, ay + 76, 28, alpha=alpha)


ALV_C = (1180, 430)
ALV_R = 200
CAP_R = 245


def _arc_pts(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def alveoli_view(ctx, t, c, alpha):
    if alpha <= 0:
        return
    # left: airway ending in a cluster of air sacs
    tree = [[(140, 200), (330, 380)], [(330, 380), (420, 440)], [(330, 380), (360, 510)], [(330, 380), (440, 360)]]
    for seg in tree:
        G.Path(seg).stroke(ctx, G.hexc("7FB8D6"), 30, alpha)
        G.Path(seg).stroke(ctx, G.hexc("D6F0FF"), 20, alpha)
    clusters = [(460, 470), (380, 560), (480, 340)]
    for (x, y) in clusters:
        for k in range(6):
            a = k * math.pi / 3
            G.circle(ctx, x + 38 * math.cos(a), y + 38 * math.sin(a), 30)
            G.fill_stroke(ctx, G.hexc("FBD3DC"), O.LUNG_LINE, 4, alpha)
        G.circle(ctx, x, y, 30)
        G.fill_stroke(ctx, G.hexc("FBD3DC"), O.LUNG_LINE, 4, alpha)
    G.label(ctx, "alveoli (air sacs)", 400, 720, alpha * ramp(t, c["alveoli"]), anchor=(400, 610))
    # magnifier lines
    mx, my = 498, 470
    G.circle(ctx, mx, my, 44)
    G.rgba(ctx, G.INK, alpha)
    ctx.set_line_width(4)
    ctx.stroke()
    for sgn in (-1, 1):
        ctx.move_to(mx + 10, my + sgn * 43)
        ctx.line_to(ALV_C[0] - 250, ALV_C[1] + sgn * 300)
    ctx.set_source_rgba(0.2, 0.2, 0.3, 0.35 * alpha)
    ctx.set_line_width(3)
    ctx.stroke()
    # right: one air sac and a tiny blood vessel wrapped around it
    ctx.save()
    G.circle(ctx, ALV_C[0], ALV_C[1] + 30, 400)
    G.fill_stroke(ctx, G.WHITE, G.INK, 5, alpha)
    G.circle(ctx, ALV_C[0], ALV_C[1] + 30, 397)
    ctx.clip()
    stem = [(ALV_C[0], ALV_C[1] - ALV_R + 10), (ALV_C[0], ALV_C[1] - 420)]
    G.Path(stem).stroke(ctx, O.LUNG_LINE, 110, alpha)
    G.Path(stem).stroke(ctx, G.hexc("E6F6FF"), 96, alpha)
    G.circle(ctx, ALV_C[0], ALV_C[1], ALV_R)
    G.fill_stroke(ctx, G.hexc("E6F6FF"), O.LUNG_LINE, 14, alpha)
    G.Path([(ALV_C[0], ALV_C[1] - ALV_R + 4), (ALV_C[0], ALV_C[1] - 420)]).stroke(ctx, G.hexc("E6F6FF"), 84, alpha)
    # capillary: blood arrives with less oxygen (left) and leaves with more (right)
    lower = [(ALV_C[0] - 430, ALV_C[1] + 40)] + [
        (ALV_C[0] + CAP_R * math.cos(math.radians(170 - k * 4)),
         ALV_C[1] + CAP_R * math.sin(math.radians(170 - k * 4))) for k in range(41)
    ] + [(ALV_C[0] + 430, ALV_C[1] + 40)]
    n = len(lower)
    for i in range(n - 1):
        k = i / (n - 1)
        col = G.mix(G.BLOOD_POOR, G.BLOOD_RICH, clamp((k - 0.25) / 0.5))
        G.Path(lower[i:i + 2]).stroke(ctx, col, 52, alpha)
    G.dots_along(ctx, lower, G.hexc("FFFFFF"), t, speed=0.12, count=10, r=7, alpha=alpha * 0.8)
    G.flow_arrows(ctx, lower, G.WHITE, t, speed=0.12, spacing=0.34, size=22, alpha=alpha * 0.9)
    # oxygen: from air in the sac into the blood
    oa = ramp(t, c["oxygen"], 0.5) * alpha
    if oa > 0:
        for i in range(6):
            ang = math.radians(60 + i * 12)
            start = (ALV_C[0] + 90 * math.cos(ang) - 20, ALV_C[1] + 60 * math.sin(ang) - 40)
            mid = (ALV_C[0] + (CAP_R) * math.cos(ang), ALV_C[1] + CAP_R * math.sin(ang))
            path = [start, mid]
            u = ((t - c["oxygen"]) * 0.45 + i / 6) % 1.0
            x, y, _ = G.Path(path).at(ease(u))
            fade = min(1, u / 0.1, (1 - u) / 0.1)
            G.circle(ctx, x, y, 17)
            G.fill_stroke(ctx, G.O2, G.INK, 3, oa * fade)
            G.draw_text(ctx, "O2", x, y + 7, 18, G.WHITE, alpha=oa * fade)
    ca = ramp(t, c["co2"], 0.5) * alpha
    if ca > 0:
        exhale = ramp(t, c["out"] - 0.4, 0.6)
        for i in range(5):
            ang = math.radians(130 + i * 9)
            start = (ALV_C[0] + CAP_R * math.cos(ang), ALV_C[1] + CAP_R * math.sin(ang))
            mid = (ALV_C[0] - 40 + i * 20, ALV_C[1] - 20)
            top = (ALV_C[0] - 20 + i * 10, ALV_C[1] - 420)
            path = [start, mid, top] if exhale > 0.5 else [start, mid]
            u = ((t - c["co2"]) * 0.35 + i / 5) % 1.0
            x, y, _ = G.Path(path).at(ease(u))
            fade = min(1, u / 0.1, (1 - u) / 0.1)
            G.circle(ctx, x, y, 17)
            G.fill_stroke(ctx, G.CO2, G.INK, 3, ca * fade)
            G.draw_text(ctx, "CO2", x, y + 6, 14, G.WHITE, alpha=ca * fade)
        if exhale > 0:
            G.arrow(ctx, [(ALV_C[0] + 70, ALV_C[1] - 150), (ALV_C[0] + 70, ALV_C[1] - 330)], G.AIR_OUT, 14, alpha * exhale)
    ctx.restore()
    G.label(ctx, "air sac", ALV_C[0] - 70, ALV_C[1] - 110, alpha * ramp(t, c["alveoli"] + 0.4), size=34)
    G.label(ctx, "blood vessel", 1640, 720, alpha * ramp(t, c["oxygen"] - 0.6), anchor=(1480, 610))
    G.label(ctx, "oxygen", 1690, 330, oa, anchor=(1330, 560), bg=G.hexc("DDEBFF"))
    G.label(ctx, "carbon dioxide", 700, 820, ca, anchor=(940, 560), bg=G.hexc("ECEFF3"))
    G.legend(ctx, BLOOD_LEGEND, 40, 40, alpha)


def lungs(ctx, t, S, c):
    G.soft_bg(ctx, G.hexc("EAF7FF"), t)
    body_a = 1 - ramp(t, c["zoom"], 0.6)
    if body_a > 0:
        lungs_body(ctx, t, c, body_a)
        energy_panel(ctx, t, c, body_a * window(t, c["energy"], c["windpipe"] - 0.4, 0.5))
        G.label(ctx, "breathing faster and deeper", 1440, 520,
                body_a * window(t, c["faster"] + 0.3, c["windpipe"] - 0.3), size=40, bg=G.hexc("E4F6FF"))
        G.label(ctx, "windpipe", 1000, 330, body_a * ramp(t, c["windpipe"]), anchor=(LCX + 16, 360))
        G.label(ctx, "lungs", 1060, 600, body_a * ramp(t, c["lungs"]), anchor=(LCX + 150, 600))
    alveoli_view(ctx, t, c, ramp(t, c["zoom"], 0.6))
    G.scene_title(ctx, "Lungs", t)


# Scene 5: heart and blood ----------------------------------------------
HC = (960, 470)
PULM_OUT = [(915, 400), (840, 360), (800, 300), (815, 215)]
THRU_LUNG = [(815, 215), (880, 180), (960, 170), (1040, 180), (1105, 215)]
PULM_IN = [(1105, 215), (1120, 300), (1080, 360), (1005, 400)]
AORTA = [(1010, 540), (1100, 580), (1340, 580), (1340, 740), (1120, 740)]
THRU_MUSCLE = [(1120, 740), (960, 755), (800, 740)]
VENA = [(800, 740), (580, 740), (580, 580), (820, 580), (910, 540)]


def vessel(ctx, pts, color, alpha, width=30):
    G.Path(pts).stroke(ctx, G.INK, width + 8, alpha)
    G.Path(pts).stroke(ctx, color, width, alpha)


def vessel_grad(ctx, pts, c0, c1, alpha, width=30):
    G.Path(pts).stroke(ctx, G.INK, width + 8, alpha)
    n = len(pts)
    for i in range(n - 1):
        G.Path(pts[i:i + 2]).stroke(ctx, G.mix(c0, c1, i / (n - 2)), width, alpha)


def lungs_icon(ctx, x, y, s, alpha):
    for left in (False, True):
        ctx.save()
        ctx.translate(x + (80 if left else -85) * s, y)
        O.lung_shape(ctx, 0, 0, 110 * s, 190 * s, left)
        G.rgba(ctx, O.LUNG, alpha)
        ctx.fill_preserve()
        G.rgba(ctx, O.LUNG_LINE, alpha)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.restore()


def heart(ctx, t, S, c):
    G.soft_bg(ctx, G.hexc("FFF0F3"), t)
    ph = heart_phase(t, c)
    frac = ph % 1.0
    beat = math.exp(-frac * 9) + 0.6 * math.exp(-max(0, frac - 0.18) * 9) * (frac > 0.18)
    speed = heart_bpm(t, c) / 85
    pa = ramp(t, c["right"], 0.6)
    ba = ramp(t, c["left"], 0.6)
    va = ramp(t, c["vessels"] - 0.3, 0.5)
    # lungs and muscle at the two ends of the loops
    la = max(pa, 0.25 * va)
    lungs_icon(ctx, 960, 210, 1.0, max(la, 0.35))
    ma = max(ba, 0.35)
    O.muscle_spindle(ctx, 780, 780, 1140, 780, 110, O.MUSCLE_ICON, ma)
    # vessels
    base = 0.3 * va
    vessel(ctx, PULM_OUT, G.BLOOD_POOR, max(base, pa))
    vessel_grad(ctx, THRU_LUNG, G.BLOOD_POOR, G.BLOOD_RICH, max(base, pa), 22)
    vessel(ctx, PULM_IN, G.BLOOD_RICH, max(base, pa))
    vessel(ctx, AORTA, G.BLOOD_RICH, max(base, ba))
    vessel_grad(ctx, THRU_MUSCLE, G.BLOOD_RICH, G.BLOOD_POOR, max(base, ba), 22)
    vessel(ctx, VENA, G.BLOOD_POOR, max(base, ba))
    flow_t = t * speed
    if pa > 0:
        G.flow_arrows(ctx, PULM_OUT + THRU_LUNG[1:] + PULM_IN[1:], G.WHITE, flow_t, speed=0.18, spacing=0.14, size=22, alpha=pa)
        G.dots_along(ctx, THRU_LUNG, G.O2, flow_t, speed=0.5, count=4, r=8, alpha=pa * 0.9)
    if ba > 0:
        G.flow_arrows(ctx, AORTA + THRU_MUSCLE[1:] + VENA[1:], G.WHITE, flow_t, speed=0.12, spacing=0.09, size=22, alpha=ba)
    na = ramp(t, c["nutrients"], 0.5)
    if na > 0:
        G.dots_along(ctx, AORTA, G.NUTRIENT, flow_t, speed=0.3, count=5, r=10, alpha=na)
    ca = ramp(t, c["co2"], 0.5)
    if ca > 0:
        G.dots_along(ctx, VENA + PULM_OUT[1:], G.CO2, flow_t, speed=0.22, count=6, r=10, alpha=ca)
    O.heart(ctx, HC[0], HC[1], 1.0, 1.0, beat)
    # labels
    G.label(ctx, "heart", 1250, 470, window(t, c["heart"], c["right"]), anchor=(1060, 470))
    G.label(ctx, "blood vessels", 1600, 660, window(t, c["vessels"], c["left"]), anchor=(1348, 660))
    G.label(ctx, "right side", 720, 470, ramp(t, c["right"]), size=34, anchor=(900, 470))
    G.label(ctx, "left side", 1210, 470, ramp(t, c["left"]), size=34, anchor=(1020, 470))
    G.label(ctx, "lungs", 1300, 170, ramp(t, c["right"] + 0.8), size=34, anchor=(1130, 190))
    G.label(ctx, "leg muscles", 1510, 800, ramp(t, c["left"] + 2.0), size=34, anchor=(1150, 790))
    G.label(ctx, "nutrients", 1560, 520, window(t, c["nutrients"], c["faster"] - 0.3), size=34, anchor=(1340, 600), bg=G.hexc("FFF1C9"))
    G.label(ctx, "carbon dioxide", 380, 480, window(t, c["co2"], c["faster"] - 0.3), size=34, anchor=(580, 640), bg=G.hexc("ECEFF3"))
    if pa > 0:
        G.draw_text(ctx, "(shown as if you are facing Maya)", HC[0], 640, 26, G.hexc("6B7080"), alpha=pa)
    G.legend(ctx, BLOOD_LEGEND, 1420, 40, ramp(t, c["right"] + 0.5))
    # heart-rate meter and running inset
    fa = ramp(t, c["faster"] - 0.6, 0.5)
    if fa > 0:
        G.panel(ctx, 1500, 330, 330, 190, fa)
        G.draw_text(ctx, "heart rate", 1665, 380, 32, alpha=fa)
        G.draw_text(ctx, f"{int(round(heart_bpm(t, c)))}", 1665, 460, 72, G.hexc("E63946"), alpha=fa)
        G.draw_text(ctx, "beats per minute", 1665, 500, 24, G.hexc("6B7080"), alpha=fa)
        ctx.save()
        G.circle(ctx, 240, 300, 160)
        G.fill_stroke(ctx, G.SKY_BOT, G.INK, 5, fa)
        G.circle(ctx, 240, 300, 156)
        ctx.clip()
        ctx.push_group()
        ctx.rectangle(0, 330, 500, 200)
        G.rgba(ctx, G.GRASS)
        ctx.fill()
        M.draw(ctx, 240, 400, 0.42, M.run(t))
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(fa)
        ctx.restore()
    G.scene_title(ctx, "Heart and blood", t)


# Scene 6: digestion -----------------------------------------------------
DB = (1180, 30, 1.05)  # body outline: centre x, top, scale


def _bx(x):
    return DB[0] + x * DB[2]


def _by(y):
    return DB[1] + y * DB[2]


MOUTH = (_bx(0), _by(140))
ESO = [MOUTH, (_bx(0), _by(200)), (_bx(2), _by(300)), (_bx(18), _by(385)), (_bx(42), _by(410))]
STOM_C = (_bx(58), _by(440))
PYLORUS = (_bx(20), _by(488))


def intestine_path():
    pts = [PYLORUS, (_bx(-10), _by(500))]
    rows = 5
    for r in range(rows):
        y = _by(515 + r * 26)
        xs = (_bx(-70), _bx(70)) if r % 2 == 0 else (_bx(70), _bx(-70))
        pts += [(xs[0], y), (xs[1], y)]
    pts.append((_bx(0), _by(660)))
    return G.smooth_path(pts, 8)


INTESTINE = intestine_path()
DIG_VESSEL = [(_bx(-95), _by(640)), (_bx(-95), _by(520)), (_bx(-85), _by(420)), (_bx(-40), _by(330)), (_bx(-12), _by(290))]


def plate(ctx, x, y, s, alpha, bite=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.save()
    ctx.scale(1, 0.42)
    G.circle(ctx, 0, 0, 230)
    ctx.restore()
    G.fill_stroke(ctx, G.WHITE, G.INK, 5, alpha)
    ctx.save()
    ctx.scale(1, 0.42)
    G.circle(ctx, 0, 0, 170)
    ctx.restore()
    G.rgba(ctx, G.hexc("EEF2F7"), alpha)
    ctx.fill()
    # sandwich
    ctx.move_to(-150, 20)
    ctx.line_to(-20, 20)
    ctx.line_to(-85, -110)
    ctx.close_path()
    G.fill_stroke(ctx, G.hexc("F2C779"), G.INK, 5, alpha)
    ctx.move_to(-140, 12)
    ctx.line_to(-30, 12)
    G.rgba(ctx, G.hexc("7CCB6B"), alpha)
    ctx.set_line_width(8)
    ctx.stroke()
    # apple
    G.circle(ctx, 80, -20, 58)
    G.fill_stroke(ctx, G.hexc("FF5A5F"), G.INK, 5, alpha)
    ctx.move_to(80, -76)
    ctx.line_to(88, -100)
    G.rgba(ctx, G.INK, alpha)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.move_to(90, -92)
    ctx.curve_to(110, -110, 130, -100, 120, -86)
    ctx.close_path()
    G.fill_stroke(ctx, G.hexc("5DB35A"), G.INK, 3, alpha)
    ctx.restore()


def pieces_diagram(ctx, x, y, alpha):
    if alpha <= 0:
        return
    ctx.rectangle(x - 190, y - 40, 80, 80)
    G.fill_stroke(ctx, G.hexc("F2C779"), G.INK, 4, alpha)
    G.arrow(ctx, [(x - 95, y), (x - 40, y)], G.INK, 6, alpha)
    for i in range(4):
        ctx.rectangle(x - 25 + (i % 2) * 42, y - 38 + (i // 2) * 42, 34, 34)
        G.fill_stroke(ctx, G.hexc("F2C779"), G.INK, 3, alpha)
    G.arrow(ctx, [(x + 75, y), (x + 130, y)], G.INK, 6, alpha)
    for i in range(12):
        G.circle(ctx, x + 150 + (i % 4) * 20, y - 25 + (i // 4) * 24, 7)
        G.fill_stroke(ctx, G.NUTRIENT, G.INK, 2, alpha)


def teeth_inset(ctx, t, c, alpha):
    if alpha <= 0:
        return
    x, y, r = 780, 230, 130
    ctx.move_to(x + r * 0.9, y + 20)
    ctx.line_to(MOUTH[0] - 30, MOUTH[1])
    G.rgba(ctx, G.INK, alpha * 0.5)
    ctx.set_line_width(3)
    ctx.stroke()
    G.circle(ctx, x, y, r)
    G.fill_stroke(ctx, G.hexc("FFD9DE"), G.INK, 5, alpha)
    chomp = 0.5 + 0.5 * math.cos((t - c["teeth"]) * 2 * math.pi * 2.2)
    gap = 10 + 34 * chomp
    for row, sgn in ((-1, -1), (1, 1)):
        for i in range(5):
            tx = x - 90 + i * 38
            ty = y + sgn * gap
            G.rounded_rect(ctx, tx, ty if sgn > 0 else ty - 34, 32, 34, 8)
            G.fill_stroke(ctx, G.WHITE, G.INK, 3, alpha)
    crush = clamp((t - c["crush"]) / 1.2)
    n = 1 + int(crush * 7)
    for i in range(n):
        s = 26 / math.sqrt(n)
        px = x - 10 + (i % 3 - 1) * 26 * crush
        py = y + (i // 3 - 1) * 12 * crush
        ctx.rectangle(px - s / 2, py - s / 2, s, s)
        G.fill_stroke(ctx, G.hexc("F2C779"), G.INK, 2, alpha)


def digestion(ctx, t, S, c):
    G.soft_bg(ctx, G.hexc("FFF6E5"), t)
    ba = ramp(t, c["body"], 0.6)
    move = ease((t - c["body"]) / 0.9)
    pl_x, pl_y, pl_s = lerp(960, 380, move), lerp(470, 330, move), lerp(1.3, 0.8, move)
    plate(ctx, pl_x, pl_y, pl_s, ramp(t, c["plate"], 0.5))
    pieces_diagram(ctx, 380, 600, window(t, c["body"] + 0.8, c["stomach"], 0.4))
    if ba > 0:
        M.body_outline(ctx, DB[0], DB[1], DB[2], ba)
        # large intestine, faint and unlabelled
        li = G.smooth_path([(_bx(-80), _by(700)), (_bx(-110), _by(640)), (_bx(-110), _by(505)),
                            (_bx(0), _by(495)), (_bx(110), _by(505)), (_bx(110), _by(640)), (_bx(60), _by(700))], 8)
        G.Path(li).stroke(ctx, G.hexc("F3D3B5"), 34, ba * 0.7)
        G.Path(ESO).stroke(ctx, G.hexc("E7A77F"), 22, ba)
        G.Path(ESO).stroke(ctx, G.hexc("F7C9A0"), 14, ba)
        sq = math.sin((t - c["stomach"]) * 5) * window(t, c["stomach"], c["intestine"], 0.3)
        O.stomach(ctx, STOM_C[0], STOM_C[1], 0.9 * DB[2], sq, ba)
        G.Path(INTESTINE).stroke(ctx, G.hexc("D99A6C"), 24, ba)
        G.Path(INTESTINE).stroke(ctx, O.INTESTINE, 16, ba)
        vb = ramp(t, c["nutrients"] - 0.3, 0.5)
        vessel(ctx, DIG_VESSEL, G.BLOOD_RICH, ba * vb, 16)
        if vb > 0:
            G.flow_arrows(ctx, DIG_VESSEL, G.WHITE, t, speed=0.4, spacing=0.3, size=16, alpha=vb)
    # food travelling: mouth -> stomach -> small intestine
    fs = c["teeth"] - 1.0
    if fs < t < c["teeth"]:
        u = ease((t - fs) / 1.0)
        fx = lerp(pl_x - 60, MOUTH[0], u)
        fy = lerp(pl_y - 20, MOUTH[1], u) - 120 * math.sin(math.pi * u)
        ctx.rectangle(fx - 16, fy - 16, 32, 32)
        G.fill_stroke(ctx, G.hexc("F2C779"), G.INK, 3)
    down = c["stomach"] - 0.9
    if down < t < c["stomach"] + 0.4:
        u = ease((t - down) / 1.3)
        for i in range(4):
            x, y, _ = G.Path(ESO).at(clamp(u - i * 0.06))
            G.circle(ctx, x, y, 7)
            G.fill_stroke(ctx, G.hexc("F2C779"), G.INK, 2)
    if c["stomach"] + 0.3 < t < c["intestine"] + 0.4:
        shrink = clamp((t - c["enzymes"]) / 2.0)
        for i in range(9):
            a = i * 0.7 + t * 1.5
            r = 22 + 10 * math.sin(t * 3 + i)
            x = STOM_C[0] + r * math.cos(a)
            y = STOM_C[1] + 8 + r * 0.6 * math.sin(a)
            G.circle(ctx, x, y, lerp(8, 4, shrink))
            G.fill_stroke(ctx, G.hexc("F2C779"), G.INK, 1.5)
        ea = ramp(t, c["enzymes"], 0.4)
        if ea > 0 and t < c["intestine"]:
            for i in range(5):
                a = -i * 1.2 + t * 2.0
                x = STOM_C[0] + 34 * math.cos(a)
                y = STOM_C[1] + 6 + 20 * math.sin(a)
                ctx.move_to(x, y)
                ctx.arc(x, y, 7, 0.5, 2 * math.pi - 0.5)
                ctx.close_path()
                G.rgba(ctx, G.hexc("4CC38A"), ea)
                ctx.fill()
    if t > c["intestine"]:
        ia = ramp(t, c["intestine"], 0.4)
        G.dots_along(ctx, INTESTINE, G.hexc("F2C779"), t - c["intestine"], speed=0.15, count=10, r=5, alpha=ia)
        na = ramp(t, c["nutrients"], 0.4)
        if na > 0:
            for i in range(6):
                u = ((t - c["nutrients"]) * 0.5 + i / 6) % 1.0
                sx, sy, _ = G.Path(INTESTINE).at(0.3 + i * 0.1)
                vx, vy, _ = G.Path(DIG_VESSEL).at(0.1 + i * 0.08)
                if u < 0.5:
                    x, y = lerp(sx, vx, ease(u * 2)), lerp(sy, vy, ease(u * 2))
                else:
                    x, y, _ = G.Path(DIG_VESSEL).at(0.1 + i * 0.08 + (u - 0.5) * 1.6)
                fade = min(1, u / 0.1, (1 - u) / 0.1)
                G.circle(ctx, x, y, 8)
                G.fill_stroke(ctx, G.NUTRIENT, G.INK, 2, na * fade)
    teeth_inset(ctx, t, c, window(t, c["teeth"] - 0.3, c["stomach"] - 0.3, 0.3))
    G.label(ctx, "teeth", 780, 410, window(t, c["teeth"], c["stomach"] - 0.3))
    G.label(ctx, "stomach", 1560, 430, window(t, c["stomach"], c["intestine"]), anchor=(STOM_C[0] + 50, STOM_C[1]))
    G.label(ctx, "enzymes", 1560, 530, window(t, c["enzymes"], c["intestine"]), anchor=(STOM_C[0] + 30, STOM_C[1] + 20), bg=G.hexc("DDF6EA"))
    G.label(ctx, "small intestine", 1580, 620, ramp(t, c["intestine"]), anchor=(_bx(70), _by(560)))
    G.label(ctx, "nutrients", 760, 560, ramp(t, c["nutrients"]), anchor=(_bx(-60), _by(540)), bg=G.hexc("FFF1C9"))
    G.label(ctx, "blood", 760, 420, ramp(t, c["blood"]), anchor=(_bx(-88), _by(430)))
    G.scene_title(ctx, "Digestion", t)
