"""Drawing helpers shared by every scene (pycairo)."""

import math

import cairo

W, H = 1920, 1080
FPS = 30
FONT = "Nunito"


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


# Palette ---------------------------------------------------------------
NAVY = hexc("2B2D42")
INK = hexc("33364D")
WHITE = hexc("FFFFFF")
CREAM = hexc("FFF8EC")
SKY_TOP = hexc("8FD3FF")
SKY_BOT = hexc("DDF3FF")
GRASS = hexc("7CCB6B")
GRASS_DARK = hexc("5DB35A")
ORANGE = hexc("FF8A3D")
CORAL = hexc("FF6B6B")
TEAL = hexc("2EC4B6")
YELLOW = hexc("FFD23F")
SIGNAL = hexc("FFE14D")
AIR_IN = hexc("5CC8FF")
AIR_OUT = hexc("B9A7E6")
BLOOD_RICH = hexc("E63946")
BLOOD_POOR = hexc("7B5CC4")
O2 = hexc("3A86FF")
CO2 = hexc("8D99AE")
NUTRIENT = hexc("FFB703")
MUSCLE = hexc("F2727F")
MUSCLE_ACTIVE = hexc("FF4D5E")
TENDON = hexc("F4E9D8")
BONE = hexc("FBF3E4")
BODY_FILL = hexc("FFE9DA")
BODY_LINE = hexc("E7B99E")
PANEL = hexc("F4F7FB")


def rgba(ctx, c, alpha=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], c[3] * alpha)


def mix(c1, c2, t):
    return tuple(a + (b - a) * t for a, b in zip(c1, c2))


# Timing ----------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def back_out(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ramp(t, start, dur=0.4):
    """0 before start, eased to 1 over dur."""
    return ease((t - start) / dur) if dur > 0 else float(t >= start)


def window(t, start, end, fade=0.35):
    """Fade in at start, fade out at end."""
    return min(ramp(t, start, fade), 1 - ramp(t, end - fade, fade))


def lerp(a, b, t):
    return a + (b - a) * t


# Shapes ----------------------------------------------------------------
def rounded_rect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def circle(ctx, x, y, r):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)


def fill_stroke(ctx, fill, stroke=None, width=4, alpha=1.0):
    if fill is not None:
        rgba(ctx, fill, alpha)
        if stroke is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke is not None:
        rgba(ctx, stroke, alpha)
        ctx.set_line_width(width)
        ctx.stroke()


def capsule(ctx, x1, y1, x2, y2, width, color, alpha=1.0, outline=None, ow=3):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if outline is not None:
        rgba(ctx, outline, alpha)
        ctx.set_line_width(width + ow * 2)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()
    rgba(ctx, color, alpha)
    ctx.set_line_width(width)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()


def glow_dot(ctx, x, y, r, color, alpha=1.0):
    g = cairo.RadialGradient(x, y, 0, x, y, r * 2.6)
    g.add_color_stop_rgba(0, color[0], color[1], color[2], 0.55 * alpha)
    g.add_color_stop_rgba(1, color[0], color[1], color[2], 0)
    ctx.set_source(g)
    circle(ctx, x, y, r * 2.6)
    ctx.fill()
    circle(ctx, x, y, r)
    rgba(ctx, color, alpha)
    ctx.fill()
    circle(ctx, x - r * 0.3, y - r * 0.3, r * 0.35)
    ctx.set_source_rgba(1, 1, 1, 0.7 * alpha)
    ctx.fill()


# Paths -----------------------------------------------------------------
class Path:
    """Polyline with arc-length lookup, for flows and signals."""

    def __init__(self, pts):
        self.pts = pts
        self.cum = [0.0]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(x2 - x1, y2 - y1))
        self.length = self.cum[-1]

    def at(self, u):
        """Point and tangent angle at fraction u of the length."""
        d = clamp(u) * self.length
        for i in range(1, len(self.cum)):
            if self.cum[i] >= d:
                seg = self.cum[i] - self.cum[i - 1] or 1
                f = (d - self.cum[i - 1]) / seg
                (x1, y1), (x2, y2) = self.pts[i - 1], self.pts[i]
                return x1 + (x2 - x1) * f, y1 + (y2 - y1) * f, math.atan2(y2 - y1, x2 - x1)
        x1, y1 = self.pts[-2]
        x2, y2 = self.pts[-1]
        return x2, y2, math.atan2(y2 - y1, x2 - x1)

    def stroke(self, ctx, color, width, alpha=1.0, upto=1.0):
        if upto <= 0:
            return
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        rgba(ctx, color, alpha)
        ctx.set_line_width(width)
        ctx.move_to(*self.pts[0])
        target = upto * self.length
        for i in range(1, len(self.pts)):
            if self.cum[i] <= target:
                ctx.line_to(*self.pts[i])
            else:
                x, y, _ = self.at(upto)
                ctx.line_to(x, y)
                break
        ctx.stroke()


def bezier_pts(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0]
        y = mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]
        out.append((x, y))
    return out


def smooth_path(pts, n=12):
    """Catmull-Rom through pts."""
    if len(pts) < 3:
        return list(pts)
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def arrow_head(ctx, x, y, ang, size, color, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.move_to(size * 0.6, 0)
    ctx.line_to(-size * 0.6, -size * 0.6)
    ctx.line_to(-size * 0.3, 0)
    ctx.line_to(-size * 0.6, size * 0.6)
    ctx.close_path()
    rgba(ctx, color, alpha)
    ctx.fill()
    ctx.restore()


def arrow(ctx, pts, color, width=10, alpha=1.0, upto=1.0, head=None):
    """Arrow along a polyline; head drawn at the current tip."""
    if alpha <= 0 or upto <= 0.01:
        return
    p = Path(pts)
    p.stroke(ctx, color, width, alpha, upto * 0.97)
    x, y, a = p.at(upto)
    arrow_head(ctx, x, y, a, head or width * 2.6, color, alpha)


def flow_arrows(ctx, pts, color, t, speed=0.35, spacing=0.22, size=26, alpha=1.0):
    """Chevrons travelling along a path to show direction of flow."""
    if alpha <= 0:
        return
    p = Path(pts)
    n = max(1, int(1 / spacing))
    for i in range(n):
        u = ((t * speed) + i / n) % 1.0
        fade = min(1, u / 0.12, (1 - u) / 0.12)
        x, y, a = p.at(u)
        arrow_head(ctx, x, y, a, size, color, alpha * fade)


def dots_along(ctx, pts, color, t, speed=0.25, count=8, r=9, alpha=1.0, phase=0.0, glow=False):
    if alpha <= 0:
        return
    p = Path(pts)
    for i in range(count):
        u = ((t * speed) + i / count + phase) % 1.0
        fade = min(1, u / 0.06, (1 - u) / 0.06)
        x, y, _ = p.at(u)
        if glow:
            glow_dot(ctx, x, y, r, color, alpha * fade)
        else:
            circle(ctx, x, y, r)
            rgba(ctx, color, alpha * fade)
            ctx.fill()


# Text ------------------------------------------------------------------
def font(ctx, size, bold=True):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def text_width(ctx, s):
    return ctx.text_extents(s).x_advance


def chem_parts(s):
    """Split 'CO2' style text into (text, is_subscript) runs."""
    parts, buf = [], ""
    for i, ch in enumerate(s):
        is_sub = ch.isdigit() and i > 0 and s[i - 1] in "OC" and s.startswith(("O2", "CO2"))
        if is_sub:
            if buf:
                parts.append((buf, False))
                buf = ""
            parts.append((ch, True))
        else:
            buf += ch
    if buf:
        parts.append((buf, False))
    return parts


def draw_text(ctx, s, x, y, size, color=INK, align="center", bold=True, alpha=1.0,
              outline=None, ow=6):
    font(ctx, size, bold)
    parts = chem_parts(s)
    widths = []
    for txt, sub in parts:
        font(ctx, size * (0.65 if sub else 1), bold)
        widths.append(text_width(ctx, txt))
    total = sum(widths)
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    cx = x
    for (txt, sub), w in zip(parts, widths):
        font(ctx, size * (0.65 if sub else 1), bold)
        yy = y + (size * 0.18 if sub else 0)
        ctx.move_to(cx, yy)
        ctx.text_path(txt)
        if outline is not None:
            rgba(ctx, outline, alpha)
            ctx.set_line_width(ow)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke_preserve()
        rgba(ctx, color, alpha)
        ctx.fill()
        cx += w
    return total


def label(ctx, s, x, y, alpha, size=38, color=INK, bg=WHITE, anchor=None, pop=True,
          line_color=None):
    """Rounded tag with optional leader line to anchor (x, y) point."""
    if alpha <= 0.01:
        return
    font(ctx, size)
    w = sum(text_width(ctx, t) * (0.65 if sub else 1) for t, sub in chem_parts(s)) + size * 0.9
    h = size * 1.45
    if anchor is not None:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        rgba(ctx, line_color or INK, alpha * 0.8)
        ctx.set_line_width(4)
        ctx.move_to(x, y)
        ctx.line_to(*anchor)
        ctx.stroke()
        circle(ctx, anchor[0], anchor[1], 7)
        rgba(ctx, line_color or INK, alpha)
        ctx.fill()
    ctx.save()
    sc = back_out(alpha) if pop else 1
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    rounded_rect(ctx, -w / 2 + 3, -h / 2 + 5, w, h, h / 2)
    ctx.set_source_rgba(0, 0, 0, 0.12 * alpha)
    ctx.fill()
    rounded_rect(ctx, -w / 2, -h / 2, w, h, h / 2)
    fill_stroke(ctx, bg, INK, 3.5, alpha)
    draw_text(ctx, s, 0, size * 0.35, size, color, alpha=alpha)
    ctx.restore()


def wrap(ctx, text, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(ctx, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def balanced_wrap(ctx, text, max_w):
    """One line if it fits, otherwise two lines of similar width."""
    if text_width(ctx, text) <= max_w:
        return [text]
    words = text.split()
    best, best_w = None, None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        w = max(text_width(ctx, a), text_width(ctx, b))
        if best_w is None or w < best_w:
            best, best_w = [a, b], w
    if best_w is not None and best_w <= max_w:
        return best
    return wrap(ctx, text, max_w)


def caption(ctx, text, alpha=1.0):
    if not text or alpha <= 0:
        return
    size = 46
    font(ctx, size, bold=True)
    lines = balanced_wrap(ctx, text, 1500)
    lh = size * 1.28
    box_w = max(text_width(ctx, l) for l in lines) + 70
    box_h = lh * len(lines) + 36
    x = (W - box_w) / 2
    y = H - 50 - box_h
    rounded_rect(ctx, x, y, box_w, box_h, 26)
    ctx.set_source_rgba(0.1, 0.11, 0.18, 0.78 * alpha)
    ctx.fill()
    for i, l in enumerate(lines):
        draw_text(ctx, l, W / 2, y + 18 + lh * (i + 0.78), size, WHITE, alpha=alpha)


def panel(ctx, x, y, w, h, alpha=1.0, fill=WHITE, r=40):
    rounded_rect(ctx, x + 6, y + 10, w, h, r)
    ctx.set_source_rgba(0, 0, 0, 0.10 * alpha)
    ctx.fill()
    rounded_rect(ctx, x, y, w, h, r)
    fill_stroke(ctx, fill, INK, 4, alpha)


def scene_title(ctx, text, t, color=INK):
    a = window(t, 0.1, 3.2, 0.4)
    if a <= 0:
        return
    font(ctx, 40)
    w = text_width(ctx, text) + 60
    x = 60 - (1 - ease_out(a)) * 40
    rounded_rect(ctx, x, 44, w, 66, 33)
    fill_stroke(ctx, WHITE, INK, 3.5, a)
    draw_text(ctx, text, x + w / 2, 90, 40, color, alpha=a)


def legend(ctx, items, x, y, alpha=1.0):
    """items: list of (color, text)."""
    if alpha <= 0:
        return
    font(ctx, 28)
    w = max(text_width(ctx, t) for _, t in items) + 90
    h = 30 + 46 * len(items)
    panel(ctx, x, y, w, h, alpha, r=24)
    for i, (c, t) in enumerate(items):
        cy = y + 38 + i * 46
        circle(ctx, x + 36, cy, 13)
        rgba(ctx, c, alpha)
        ctx.fill()
        draw_text(ctx, t, x + 62, cy + 10, 28, INK, align="left", alpha=alpha)


def gradient_bg(ctx, top, bot):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *top)
    g.add_color_stop_rgba(1, *bot)
    ctx.set_source(g)
    ctx.paint()


def soft_bg(ctx, color, t=0.0):
    rgba(ctx, color)
    ctx.paint()
    # gentle drifting circles for depth
    for i in range(7):
        x = (i * 331 + t * 12 * (1 + i % 3)) % (W + 400) - 200
        y = 150 + (i * 197) % 800
        circle(ctx, x, y, 90 + (i % 4) * 40)
        ctx.set_source_rgba(1, 1, 1, 0.16)
        ctx.fill()
