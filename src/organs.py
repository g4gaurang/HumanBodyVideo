"""Simple, friendly organ shapes. Each takes a centre and a scale."""

import math

from gfx import INK, circle, hexc, rgba

BRAIN = hexc("F7B2C4")
BRAIN_LINE = hexc("D9809B")
LUNG = hexc("F9A8B8")
LUNG_LINE = hexc("D46A84")
HEART_R = hexc("9B7BD6")  # right side, receives oxygen-poor blood
HEART_L = hexc("F0616D")  # left side, oxygen-rich blood
STOMACH = hexc("F6B58A")
STOMACH_LINE = hexc("D98A5A")
INTESTINE = hexc("F7C9A0")
KIDNEY = hexc("C8505E")
KIDNEY_LINE = hexc("8E2F3C")
EYE_WHITE = hexc("FFFFFF")
IRIS = hexc("6B4A2B")
RETINA = hexc("FF9F6B")
MUSCLE_ICON = hexc("F2727F")


def _stroke(ctx, color, width, alpha):
    rgba(ctx, color, alpha)
    ctx.set_line_width(width)
    ctx.stroke()


def brain(ctx, x, y, s, alpha=1.0, glow=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if glow > 0:
        import cairo
        g = cairo.RadialGradient(0, 0, 40, 0, 0, 180)
        g.add_color_stop_rgba(0, 1, 0.9, 0.3, 0.5 * glow * alpha)
        g.add_color_stop_rgba(1, 1, 0.9, 0.3, 0)
        ctx.set_source(g)
        circle(ctx, 0, 0, 180)
        ctx.fill()
    ctx.move_to(-95, 30)
    ctx.curve_to(-120, -10, -100, -70, -50, -80)
    ctx.curve_to(-20, -100, 30, -100, 60, -80)
    ctx.curve_to(110, -70, 125, -10, 100, 30)
    ctx.curve_to(90, 60, 40, 70, 10, 60)
    ctx.curve_to(-20, 72, -80, 65, -95, 30)
    ctx.close_path()
    rgba(ctx, BRAIN, alpha)
    ctx.fill_preserve()
    _stroke(ctx, BRAIN_LINE, 5, alpha)
    for (a, b, c, d) in [(-70, -20, -40, -50), (-30, 10, 0, -30), (10, -50, 40, -20),
                         (40, 20, 80, -10), (-60, 30, -20, 20), (20, 40, 60, 40)]:
        ctx.move_to(a, b)
        ctx.curve_to(a + 10, b - 20, c - 10, d + 20, c, d)
        _stroke(ctx, BRAIN_LINE, 4, alpha * 0.8)
    ctx.restore()


def lung_shape(ctx, x, y, w, h, left_side=False):
    """One lung. left_side=True draws the body's left lung (viewer's right)."""
    sx = 1 if left_side else -1
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sx * w / 100, h / 200)
    # inner edge near the midline is at x=-50 (after flipping, faces centre)
    ctx.move_to(-40, -95)
    ctx.curve_to(-10, -110, 30, -60, 45, 0)
    ctx.curve_to(55, 50, 60, 90, 40, 100)
    ctx.curve_to(10, 108, -30, 104, -48, 96)
    if left_side:
        ctx.curve_to(-50, 60, -30, 40, -45, 10)
    ctx.curve_to(-55, -30, -55, -80, -40, -95)
    ctx.close_path()
    ctx.restore()


def lungs(ctx, x, y, s, expand=1.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for left in (False, True):
        cx = 58 if left else -58
        ctx.save()
        ctx.translate(cx, 10)
        ctx.scale(expand, expand)
        lung_shape(ctx, 0, 0, 92 if left else 100, 200, left)
        rgba(ctx, LUNG, alpha)
        ctx.fill_preserve()
        _stroke(ctx, LUNG_LINE, 5, alpha)
        ctx.restore()
    # windpipe and bronchi
    rgba(ctx, hexc("BFE6F7"), alpha)
    ctx.set_line_width(16)
    ctx.move_to(0, -140)
    ctx.line_to(0, -60)
    ctx.stroke()
    ctx.move_to(0, -60)
    ctx.line_to(-40, -20)
    ctx.move_to(0, -60)
    ctx.line_to(40, -20)
    ctx.stroke()
    ctx.restore()


def heart_path(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, -40)
    ctx.curve_to(-20, -95, -110, -85, -105, -15)
    ctx.curve_to(-100, 40, -40, 80, 0, 110)
    ctx.curve_to(40, 80, 100, 40, 105, -15)
    ctx.curve_to(110, -85, 20, -95, 0, -40)
    ctx.close_path()
    ctx.restore()


def heart(ctx, x, y, s, alpha=1.0, beat=0.0, split=True):
    k = 1 + 0.07 * beat
    import cairo
    ctx.save()
    heart_path(ctx, x, y, s * k)
    ctx.clip()
    if split:
        rgba(ctx, HEART_R, alpha)
        ctx.rectangle(x - 200 * s, y - 200 * s, 200 * s, 400 * s)
        ctx.fill()
        rgba(ctx, HEART_L, alpha)
        ctx.rectangle(x, y - 200 * s, 200 * s, 400 * s)
        ctx.fill()
    else:
        rgba(ctx, HEART_L, alpha)
        ctx.paint_with_alpha(alpha)
    g = cairo.LinearGradient(x, y - 100 * s, x, y + 110 * s)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.25 * alpha)
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()
    if split:
        ctx.move_to(x, y - 35 * s * k)
        ctx.line_to(x, y + 100 * s * k)
        rgba(ctx, WHITE_A, alpha * 0.9)
        ctx.set_line_width(6 * s)
        ctx.stroke()
    heart_path(ctx, x, y, s * k)
    _stroke(ctx, INK, 5, alpha)


WHITE_A = hexc("FFFFFF")


def stomach(ctx, x, y, s, squeeze=0.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (1 - 0.06 * squeeze), s * (1 + 0.05 * squeeze))
    ctx.move_to(-30, -80)
    ctx.curve_to(-10, -95, 20, -90, 25, -70)
    ctx.curve_to(70, -60, 85, 10, 55, 55)
    ctx.curve_to(25, 95, -50, 90, -75, 60)
    ctx.curve_to(-85, 45, -80, 30, -65, 30)
    ctx.curve_to(-40, 45, -10, 40, 0, 10)
    ctx.curve_to(10, -20, -10, -50, -30, -60)
    ctx.close_path()
    rgba(ctx, STOMACH, alpha)
    ctx.fill_preserve()
    _stroke(ctx, STOMACH_LINE, 5, alpha)
    ctx.restore()


def kidney(ctx, x, y, s, alpha=1.0, flip=False, fill=None):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    ctx.move_to(0, -100)
    ctx.curve_to(55, -100, 70, -40, 65, 0)
    ctx.curve_to(60, 60, 40, 100, 0, 100)
    ctx.curve_to(-35, 100, -45, 60, -25, 30)
    ctx.curve_to(-15, 15, -15, -15, -25, -30)
    ctx.curve_to(-45, -60, -35, -100, 0, -100)
    ctx.close_path()
    rgba(ctx, fill or KIDNEY, alpha)
    ctx.fill_preserve()
    _stroke(ctx, KIDNEY_LINE, 5 / max(s, 0.3) * 0.5, alpha)
    ctx.restore()


def muscle_spindle(ctx, ax, ay, bx, by, width, color, alpha=1.0, outline=INK):
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length * width / 2, dx / length * width / 2
    ctx.move_to(ax, ay)
    ctx.curve_to(ax + dx * 0.2 + nx * 1.3, ay + dy * 0.2 + ny * 1.3,
                 ax + dx * 0.8 + nx * 1.3, ay + dy * 0.8 + ny * 1.3, bx, by)
    ctx.curve_to(ax + dx * 0.8 - nx * 1.3, ay + dy * 0.8 - ny * 1.3,
                 ax + dx * 0.2 - nx * 1.3, ay + dy * 0.2 - ny * 1.3, ax, ay)
    ctx.close_path()
    rgba(ctx, color, alpha)
    ctx.fill_preserve()
    _stroke(ctx, outline, 4, alpha)
    # fibre lines
    for f in (-0.35, 0.0, 0.35):
        ctx.move_to(ax + dx * 0.12 + nx * f, ay + dy * 0.12 + ny * f)
        ctx.curve_to(ax + dx * 0.35 + nx * f * 1.6, ay + dy * 0.35 + ny * f * 1.6,
                     ax + dx * 0.65 + nx * f * 1.6, ay + dy * 0.65 + ny * f * 1.6,
                     ax + dx * 0.88 + nx * f, ay + dy * 0.88 + ny * f)
        rgba(ctx, WHITE_A, alpha * 0.35)
        ctx.set_line_width(3)
        ctx.stroke()


def bone(ctx, ax, ay, bx, by, width, alpha=1.0):
    from gfx import BONE
    import cairo
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for color, w in ((INK, width + 8), (BONE, width)):
        rgba(ctx, color, alpha)
        ctx.set_line_width(w)
        ctx.move_to(ax, ay)
        ctx.line_to(bx, by)
        ctx.stroke()
    for px, py in ((ax, ay), (bx, by)):
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * width * 0.42, dx / L * width * 0.42
        for sgn in (-1, 1):
            circle(ctx, px + nx * sgn, py + ny * sgn, width * 0.52)
            rgba(ctx, INK, alpha)
            ctx.fill()
    for px, py in ((ax, ay), (bx, by)):
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * width * 0.42, dx / L * width * 0.42
        for sgn in (-1, 1):
            circle(ctx, px + nx * sgn, py + ny * sgn, width * 0.52 - 4)
            rgba(ctx, BONE, alpha)
            ctx.fill()
    rgba(ctx, BONE, alpha)
    ctx.set_line_width(width)
    ctx.move_to(ax, ay)
    ctx.line_to(bx, by)
    ctx.stroke()


def eye_icon(ctx, x, y, r, alpha=1.0):
    circle(ctx, x, y, r)
    rgba(ctx, EYE_WHITE, alpha)
    ctx.fill_preserve()
    _stroke(ctx, INK, 4, alpha)
    circle(ctx, x, y, r * 0.5)
    rgba(ctx, IRIS, alpha)
    ctx.fill()
    circle(ctx, x, y, r * 0.24)
    rgba(ctx, INK, alpha)
    ctx.fill()
    circle(ctx, x - r * 0.15, y - r * 0.15, r * 0.1)
    rgba(ctx, WHITE_A, alpha)
    ctx.fill()


def water_drop(ctx, x, y, r, color, alpha=1.0):
    ctx.move_to(x, y - r * 1.6)
    ctx.curve_to(x + r * 0.4, y - r * 0.8, x + r, y - r * 0.2, x + r, y + r * 0.3)
    ctx.arc(x, y + r * 0.3, r, 0, math.pi)
    ctx.curve_to(x - r, y - r * 0.2, x - r * 0.4, y - r * 0.8, x, y - r * 1.6)
    ctx.close_path()
    rgba(ctx, color, alpha)
    ctx.fill_preserve()
    _stroke(ctx, INK, 2.5, alpha)
