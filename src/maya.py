"""Maya, the one character in the video, drawn as a jointed vector puppet.

Side view, facing right. Angles are in degrees measured from straight down;
positive values swing a limb forward (toward +x). Proportions are fixed here so
she looks the same in every scene.
"""

import math

import cairo

from gfx import INK, circle, hexc, lerp, rgba

SKIN = hexc("A8693F")
SKIN_FAR = hexc("925932")
HAIR = hexc("3B2416")
SHIRT = hexc("FF8A3D")
SHIRT_FAR = hexc("E6732A")
SHORTS = hexc("2EC4B6")
SHORTS_FAR = hexc("22A597")
SHOE = hexc("FFFFFF")
SHOE_STRIPE = hexc("FF6B6B")
SOCK = hexc("F5F5F5")
CHEEK = hexc("E8876A")

HEAD_R = 58
NECK = 18
TORSO = 165
UPPER_ARM = 92
FOREARM = 86
THIGH = 122
SHIN = 122
LIMB_W = 30
OUT = 4.5

BASE = {
    "lean": 0.0, "head": 0.0, "hip_y": -(THIGH + SHIN + 14), "hip_x": 0.0,
    "n_hip": 3.0, "n_knee": 4.0, "f_hip": -3.0, "f_knee": 4.0,
    "n_sh": 8.0, "n_el": 12.0, "f_sh": -6.0, "f_el": 12.0,
    "tail": 0.0, "eyes": 1.0, "mouth": 0.0, "breath": 0.0, "rot": 0.0,
}


def pose(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def blend(a, b, k):
    return {key: lerp(a[key], b[key], k) for key in a}


def stand(t=0.0):
    b = math.sin(t * 2.2)
    return pose(breath=b, tail=3 * math.sin(t * 1.3), n_sh=8 + 1.5 * b, f_sh=-6 - 1.5 * b)


def run(t, cadence=2.6):
    p = 2 * math.pi * cadence * t / 2
    s, c = math.sin(p), math.cos(p)
    sf, cf = math.sin(p + math.pi), math.cos(p + math.pi)
    bob = -10 * abs(math.cos(p))
    return pose(
        lean=12, head=-6, hip_y=BASE["hip_y"] + 12 + bob,
        n_hip=42 * s, n_knee=14 + 80 * max(0.0, c),
        f_hip=42 * sf, f_knee=14 + 80 * max(0.0, cf),
        n_sh=-40 * s, n_el=85, f_sh=-40 * sf, f_el=85,
        tail=-18 + 10 * math.sin(p * 2), mouth=0.5,
    )


def reach(t=0.0):
    """Arms raised forward to catch."""
    return pose(lean=4, head=-10, n_sh=128, n_el=22, f_sh=118, f_el=26,
                n_hip=10, n_knee=12, f_hip=-14, f_knee=8, mouth=0.6, tail=-6)


def hold(t=0.0):
    """Holding the ball against the chest."""
    b = math.sin(t * 2.2)
    return pose(n_sh=40, n_el=100, f_sh=36, f_el=104, breath=b, mouth=0.3)


def sit(t, breath_rate=0.5):
    b = math.sin(2 * math.pi * breath_rate * t)
    return pose(hip_y=-34, lean=-6, n_hip=135, n_knee=120, f_hip=94, f_knee=2,
                n_sh=34, n_el=95, f_sh=-24, f_el=10, breath=b, head=-4)


def sleep(t):
    b = math.sin(2 * math.pi * 0.22 * t)
    return pose(rot=-90, eyes=0.0, breath=b, n_sh=10, n_el=40, f_sh=0, f_el=30,
                n_hip=18, n_knee=30, f_hip=12, f_knee=24, mouth=0.0)


def _dir(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


def _pt(x, y, a, length):
    dx, dy = _dir(a)
    return x + dx * length, y + dy * length


def _limb(ctx, pts, width, color, alpha):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for pass_color, w in ((INK, width + OUT * 2), (color, width)):
        rgba(ctx, pass_color, alpha)
        ctx.set_line_width(w)
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.stroke()


def _leg(ctx, hx, hy, hip, knee, far, alpha):
    kx, ky = _pt(hx, hy, hip, THIGH)
    shin_a = hip - knee
    ax, ay = _pt(kx, ky, shin_a, SHIN)
    skin = SKIN_FAR if far else SKIN
    _limb(ctx, [(kx, ky), (ax, ay)], LIMB_W - 2, skin, alpha)
    # sock
    sx, sy = _pt(ax, ay, shin_a + 180, 18)
    _limb(ctx, [(sx, sy), (ax, ay)], LIMB_W - 3, SOCK, alpha)
    # shoe: rounded wedge pointing forward from the ankle
    ctx.save()
    ctx.translate(ax, ay)
    ctx.rotate(-math.radians(shin_a))
    ctx.move_to(-16, -6)
    ctx.line_to(-18, 14)
    ctx.curve_to(-18, 24, 46, 26, 52, 16)
    ctx.curve_to(56, 6, 30, -2, 12, -8)
    ctx.close_path()
    rgba(ctx, SHOE if not far else hexc("E4E8EE"), alpha)
    ctx.fill_preserve()
    rgba(ctx, INK, alpha)
    ctx.set_line_width(OUT)
    ctx.stroke()
    ctx.move_to(-4, 4)
    ctx.line_to(30, 10)
    rgba(ctx, SHOE_STRIPE, alpha)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()
    # thigh with shorts over the top part
    _limb(ctx, [(hx, hy), (kx, ky)], LIMB_W, skin, alpha)
    mx, my = _pt(hx, hy, hip, THIGH * 0.55)
    _limb(ctx, [(hx, hy), (mx, my)], LIMB_W + 12, SHORTS_FAR if far else SHORTS, alpha)
    return (kx, ky), (ax, ay)


def _arm(ctx, sx, sy, sh, el, far, alpha, lean):
    ex, ey = _pt(sx, sy, sh + lean, UPPER_ARM)
    wx, wy = _pt(ex, ey, sh + lean + el, FOREARM)
    skin = SKIN_FAR if far else SKIN
    _limb(ctx, [(sx, sy), (ex, ey), (wx, wy)], LIMB_W - 6, skin, alpha)
    hx, hy = _pt(wx, wy, sh + lean + el, 12)
    circle(ctx, hx, hy, 15)
    rgba(ctx, INK, alpha)
    ctx.fill()
    circle(ctx, hx, hy, 15 - OUT)
    rgba(ctx, skin, alpha)
    ctx.fill()
    # sleeve
    mx, my = _pt(sx, sy, sh + lean, UPPER_ARM * 0.42)
    _limb(ctx, [(sx, sy), (mx, my)], LIMB_W + 8, SHIRT_FAR if far else SHIRT, alpha)
    return (hx, hy)


def _head(ctx, x, y, p, alpha, ear=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(p["head"]))
    # ponytail
    ta = math.radians(p["tail"])
    ctx.save()
    ctx.translate(-HEAD_R * 0.62, -HEAD_R * 0.62)
    ctx.rotate(ta)
    ctx.move_to(0, -8)
    ctx.curve_to(-40, -20, -70, 10, -60, 60)
    ctx.curve_to(-50, 40, -30, 20, 8, 14)
    ctx.close_path()
    rgba(ctx, HAIR, alpha)
    ctx.fill_preserve()
    rgba(ctx, INK, alpha)
    ctx.set_line_width(OUT)
    ctx.stroke()
    circle(ctx, 0, 2, 10)
    rgba(ctx, SHIRT, alpha)
    ctx.fill()
    ctx.restore()
    # face
    circle(ctx, 0, 0, HEAD_R)
    rgba(ctx, SKIN, alpha)
    ctx.fill_preserve()
    rgba(ctx, INK, alpha)
    ctx.set_line_width(OUT)
    ctx.stroke()
    # hair cap
    ctx.new_path()
    ctx.arc(0, 0, HEAD_R + 2, math.radians(160), math.radians(335))
    ctx.curve_to(40, -40, 16, -30, 4, -34)
    ctx.curve_to(-14, -18, -34, -6, -HEAD_R * 0.9, 16)
    ctx.close_path()
    rgba(ctx, HAIR, alpha)
    ctx.fill_preserve()
    rgba(ctx, INK, alpha)
    ctx.set_line_width(OUT)
    ctx.stroke()
    if ear:
        circle(ctx, -8, 6, 11)
        rgba(ctx, SKIN_FAR, alpha)
        ctx.fill_preserve()
        rgba(ctx, INK, alpha)
        ctx.set_line_width(3)
        ctx.stroke()
    # eye
    if p["eyes"] > 0.5:
        circle(ctx, 32, -6, 7.5)
        rgba(ctx, INK, alpha)
        ctx.fill()
        circle(ctx, 34, -8, 2.5)
        ctx.set_source_rgba(1, 1, 1, alpha)
        ctx.fill()
    else:
        ctx.new_path()
        ctx.arc(32, -8, 8, math.radians(20), math.radians(160))
        rgba(ctx, INK, alpha)
        ctx.set_line_width(3.5)
        ctx.stroke()
    # eyebrow
    ctx.move_to(22, -24)
    ctx.curve_to(28, -28, 36, -28, 42, -24)
    rgba(ctx, HAIR, alpha)
    ctx.set_line_width(4.5)
    ctx.stroke()
    # cheek
    circle(ctx, 30, 16, 9)
    rgba(ctx, CHEEK, 0.55 * alpha)
    ctx.fill()
    # mouth
    m = p["mouth"]
    if m > 0.2:
        ctx.save()
        ctx.translate(46, 26)
        ctx.scale(1, 0.6 + m * 0.8)
        circle(ctx, 0, 0, 6)
        ctx.restore()
        rgba(ctx, hexc("6B2E2E"), alpha)
        ctx.fill()
    else:
        ctx.new_path()
        ctx.arc(38, 18, 12, math.radians(30), math.radians(95))
        rgba(ctx, INK, alpha)
        ctx.set_line_width(3.5)
        ctx.stroke()
    ctx.restore()


def draw(ctx, x, ground_y, scale, p, alpha=1.0, flip=False):
    """Draw Maya with feet on ground_y. Returns key points in screen space."""
    ctx.save()
    ctx.translate(x, ground_y)
    ctx.scale(-scale if flip else scale, scale)
    if p["rot"]:
        ctx.rotate(math.radians(p["rot"]))
    hx, hy = p["hip_x"], p["hip_y"]
    lean = p["lean"]
    breath = p["breath"]
    sx, sy = _pt(hx, hy, 180 + lean, TORSO - 12)
    neck_top = _pt(hx, hy, 180 + lean, TORSO + NECK)

    far_hand = _arm(ctx, sx - 6, sy, p["f_sh"], p["f_el"], True, alpha, lean)
    _leg(ctx, hx - 4, hy, p["f_hip"], p["f_knee"], True, alpha)

    # torso (T-shirt), widens slightly with each breath
    ctx.save()
    ctx.translate(hx, hy)
    ctx.rotate(-math.radians(lean))
    chest = 1 + 0.035 * breath
    ctx.move_to(-34, 6)
    ctx.curve_to(-40, -60, -44 * chest, -120, -32, -TORSO + 8)
    ctx.curve_to(-10, -TORSO - 4, 18, -TORSO - 4, 34 * chest, -TORSO + 14)
    ctx.curve_to(44 * chest, -110, 40, -50, 36, 6)
    ctx.close_path()
    rgba(ctx, SHIRT, alpha)
    ctx.fill_preserve()
    rgba(ctx, INK, alpha)
    ctx.set_line_width(OUT)
    ctx.stroke()
    # shorts waistband
    ctx.move_to(-35, 0)
    ctx.line_to(37, 0)
    ctx.line_to(38, 22)
    ctx.line_to(-36, 22)
    ctx.close_path()
    rgba(ctx, SHORTS, alpha)
    ctx.fill_preserve()
    rgba(ctx, INK, alpha)
    ctx.stroke()
    ctx.restore()

    # neck + head
    nx, ny = _pt(hx, hy, 180 + lean, TORSO - 6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    rgba(ctx, INK, alpha)
    ctx.set_line_width(26 + OUT * 2)
    ctx.move_to(nx, ny)
    ctx.line_to(*neck_top)
    ctx.stroke()
    rgba(ctx, SKIN, alpha)
    ctx.set_line_width(26)
    ctx.move_to(nx, ny)
    ctx.line_to(*neck_top)
    ctx.stroke()
    head_c = _pt(*neck_top, 180 + lean, HEAD_R - 8)
    _head(ctx, head_c[0], head_c[1], p, alpha)

    near_knee, near_ankle = _leg(ctx, hx + 4, hy, p["n_hip"], p["n_knee"], False, alpha)
    near_hand = _arm(ctx, sx + 6, sy, p["n_sh"], p["n_el"], False, alpha, lean)

    def to_screen(pt):
        return ctx.user_to_device(*pt)

    pts = {
        "near_hand": to_screen(near_hand), "far_hand": to_screen(far_hand),
        "head": to_screen(head_c), "eye": to_screen((head_c[0] + 32, head_c[1] - 6)),
        "hip": to_screen((hx, hy)), "chest": to_screen(_pt(hx, hy, 180 + lean, TORSO * 0.6)),
        "knee": to_screen(near_knee),
    }
    ctx.restore()
    return pts


def draw_ball(ctx, x, y, r, spin=0.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(spin)
    colors = [hexc("FF4F4F"), hexc("FFD23F"), hexc("3A86FF"), hexc("FFFFFF")]
    for i in range(6):
        ctx.move_to(0, 0)
        ctx.arc(0, 0, r, i * math.pi / 3, (i + 1) * math.pi / 3)
        ctx.close_path()
        rgba(ctx, colors[i % 4] if i < 4 else colors[(i + 1) % 4], alpha)
        ctx.fill()
    circle(ctx, 0, 0, r)
    rgba(ctx, INK, alpha)
    ctx.set_line_width(4)
    ctx.stroke()
    circle(ctx, 0, 0, r * 0.18)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.fill()
    ctx.restore()
    circle(ctx, x - r * 0.35, y - r * 0.4, r * 0.22)
    ctx.set_source_rgba(1, 1, 1, 0.45 * alpha)
    ctx.fill()


def body_outline(ctx, cx, top, s, alpha=1.0, fill=None, line=None, back=False):
    """Front (or back) silhouette of Maya used as the frame for body diagrams.

    cx: centre x, top: y of the top of the head, s: scale (1.0 = 900 px tall).
    """
    from gfx import BODY_FILL, BODY_LINE
    fill = fill or BODY_FILL
    line = line or BODY_LINE
    ctx.save()
    ctx.translate(cx, top)
    ctx.scale(s, s)
    # ponytail visible behind the head in back view, to the side in front view
    ctx.move_to(40, 40)
    ctx.curve_to(120, 20, 130, 120, 100, 190)
    ctx.curve_to(90, 130, 70, 90, 40, 80)
    ctx.close_path()
    rgba(ctx, HAIR, alpha * 0.9)
    ctx.fill()
    ctx.move_to(-22, 175)
    ctx.line_to(-22, 205)
    ctx.curve_to(-60, 212, -120, 215, -140, 250)
    # left arm (viewer's left)
    ctx.curve_to(-160, 300, -175, 420, -185, 520)
    ctx.curve_to(-190, 560, -150, 565, -148, 525)
    ctx.curve_to(-140, 440, -130, 360, -120, 320)
    ctx.curve_to(-115, 400, -112, 450, -118, 520)
    # left leg
    ctx.curve_to(-122, 640, -110, 760, -100, 880)
    ctx.curve_to(-98, 905, -30, 905, -28, 880)
    ctx.curve_to(-22, 760, -12, 640, 0, 560)
    ctx.curve_to(12, 640, 22, 760, 28, 880)
    ctx.curve_to(30, 905, 98, 905, 100, 880)
    ctx.curve_to(110, 760, 122, 640, 118, 520)
    ctx.curve_to(112, 450, 115, 400, 120, 320)
    ctx.curve_to(130, 360, 140, 440, 148, 525)
    ctx.curve_to(150, 565, 190, 560, 185, 520)
    ctx.curve_to(175, 420, 160, 300, 140, 250)
    ctx.curve_to(120, 215, 60, 212, 22, 205)
    ctx.line_to(22, 175)
    ctx.close_path()
    rgba(ctx, fill, alpha)
    ctx.fill_preserve()
    rgba(ctx, line, alpha)
    ctx.set_line_width(6 / s * 0.6)
    ctx.stroke()
    circle(ctx, 0, 100, 82)
    rgba(ctx, fill, alpha)
    ctx.fill_preserve()
    rgba(ctx, line, alpha)
    ctx.stroke()
    ctx.new_path()
    if back:
        ctx.arc(0, 100, 84, math.radians(180), math.radians(360))
        ctx.curve_to(84, 140, 60, 175, 0, 178)
        ctx.curve_to(-60, 175, -84, 140, -84, 100)
    else:
        ctx.arc(0, 100, 84, math.radians(190), math.radians(350))
        ctx.curve_to(40, 40, -40, 40, -83, 86)
    ctx.close_path()
    rgba(ctx, HAIR, alpha * 0.9)
    ctx.fill()
    if not back:
        for ex in (-30, 30):
            circle(ctx, ex, 112, 7)
            rgba(ctx, line, alpha)
            ctx.fill()
        ctx.new_path()
        ctx.arc(0, 128, 26, math.radians(35), math.radians(145))
        rgba(ctx, line, alpha)
        ctx.set_line_width(5)
        ctx.stroke()
    ctx.restore()
