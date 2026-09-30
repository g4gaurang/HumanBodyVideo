"""Scenes 1-3: intro, eyes/brain/nerves, muscles and bones."""

import math

import cairo

import gfx as G
import maya as M
import organs as O
from gfx import ease, ramp, window, lerp, clamp
from timeline import RUN_CADENCE

GROUND = 800
SUN = (330, 130)


# Shared park backdrop ---------------------------------------------------
def cloud(ctx, x, y, s, alpha=1.0):
    for dx, dy, r in ((0, 0, 50), (50, -20, 60), (105, 0, 48), (55, 18, 50)):
        G.circle(ctx, x + dx * s, y + dy * s, r * s)
    ctx.set_source_rgba(1, 1, 1, 0.92 * alpha)
    ctx.fill()


def tree(ctx, x, ground, s=1.0):
    ctx.rectangle(x - 22 * s, ground - 230 * s, 44 * s, 235 * s)
    G.fill_stroke(ctx, G.hexc("9C6B43"), G.INK, 4)
    for dx, dy, r in ((0, -300, 120), (-90, -250, 85), (90, -250, 90), (0, -390, 90)):
        G.circle(ctx, x + dx * s, ground + dy * s, r * s)
        G.fill_stroke(ctx, G.hexc("4FB26A"), G.INK, 4)
    for dx, dy, r in ((-40, -330, 14), (50, -290, 12), (10, -250, 13)):
        G.circle(ctx, x + dx * s, ground + dy * s, r * s)
        G.rgba(ctx, G.CORAL)
        ctx.fill()


def park(ctx, t, cam=0.0, ground=GROUND, sun=True):
    G.gradient_bg(ctx, G.SKY_TOP, G.SKY_BOT)
    if sun:
        g = cairo.RadialGradient(SUN[0], SUN[1], 30, SUN[0], SUN[1], 200)
        g.add_color_stop_rgba(0, 1, 0.93, 0.5, 0.8)
        g.add_color_stop_rgba(1, 1, 0.93, 0.5, 0)
        ctx.set_source(g)
        ctx.paint()
        G.circle(ctx, SUN[0], SUN[1], 72)
        G.rgba(ctx, G.YELLOW)
        ctx.fill()
    for i, (bx, by, s) in enumerate(((200, 170, 1.0), (900, 110, 0.8), (1300, 250, 0.7))):
        x = (bx + t * (10 + i * 4) - cam * 0.15) % (G.W + 400) - 200
        cloud(ctx, x, by, s)
    # far hills
    for i in range(4):
        x = (i * 700 - cam * 0.3) % (G.W + 1400) - 700
        ctx.save()
        ctx.translate(x + 350, ground + 20)
        ctx.scale(1, 0.32)
        G.circle(ctx, 0, 0, 480)
        ctx.restore()
        G.rgba(ctx, G.hexc("A8DE8F"))
        ctx.fill()
    ctx.rectangle(0, ground - 20, G.W, G.H - ground + 20)
    G.rgba(ctx, G.GRASS)
    ctx.fill()
    ctx.move_to(0, ground - 20)
    ctx.line_to(G.W, ground - 20)
    G.rgba(ctx, G.GRASS_DARK)
    ctx.set_line_width(6)
    ctx.stroke()
    tx = (530 - cam * 0.7) % (G.W + 900) - 300
    tree(ctx, tx, ground - 10)
    for i in range(14):
        fx = (i * 173 - cam) % (G.W + 100) - 50
        fy = ground + 30 + (i * 53) % 180
        G.circle(ctx, fx, fy, 8)
        G.rgba(ctx, (G.YELLOW, G.WHITE, G.CORAL)[i % 3])
        ctx.fill()


def maya_points(pose, x, ground, scale):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
    return M.draw(cairo.Context(s), x, ground, scale, pose)


# Scene 1: intro ---------------------------------------------------------
INTRO_MAYA_X = 600


def intro_ball_pos(t, c):
    launch, freeze = c["ball_launch"], c["freeze"]
    if t < launch:
        return None
    dt = min(t, freeze) - launch
    u = 0.5 * (1 - math.exp(-dt / 1.1))
    if t >= freeze:
        u = 0.5 * (1 - math.exp(-(freeze - launch) / 1.1))
    x = lerp(2050, 760, u)
    y = 620 - 4 * 300 * u * (1 - u) + (400 - 620) * u
    return x, y, u


def intro(ctx, t, S, c):
    zoom = ease((t - c["zoom"]) / 1.4)
    pose = M.stand(t)
    if t > c["ball_launch"]:
        pose["head"] = -8 * ramp(t, c["ball_launch"], 0.5)
    eye = maya_points(pose, INTRO_MAYA_X, GROUND, 1.0)["eye"]
    ctx.save()
    if zoom > 0:
        k = 1 + 3.5 * zoom
        ctx.translate(lerp(eye[0], 960, zoom), lerp(eye[1], 540, zoom))
        ctx.scale(k, k)
        ctx.translate(-eye[0], -eye[1])
    park(ctx, t)
    a_maya = ramp(t, c["maya_in"], 0.6)
    M.draw(ctx, INTRO_MAYA_X, GROUND, 1.0, pose, alpha=a_maya)
    ball = intro_ball_pos(t, c)
    if ball:
        bx, by, u = ball
        frozen = t >= c["freeze"]
        if not frozen:
            for k in range(1, 4):
                ctx.move_to(bx + 60 + k * 26, by - 30 + k * 18)
                ctx.line_to(bx + 110 + k * 26, by - 30 + k * 18)
                ctx.set_source_rgba(1, 1, 1, 0.6 - k * 0.15)
                ctx.set_line_width(6)
                ctx.stroke()
        M.draw_ball(ctx, bx, by, 46, spin=u * 9)
    ctx.restore()

    # freeze overlay
    fa = ramp(t, c["freeze"], 0.3) * (1 - zoom)
    if fa > 0:
        ctx.set_source_rgba(0.55, 0.75, 1.0, 0.18 * fa)
        ctx.paint()
        cx, cy = 960, 110
        G.panel(ctx, cx - 190, cy - 50, 380, 100, fa, r=50)
        for dx in (-160, -134):
            G.rounded_rect(ctx, cx + dx, cy - 24, 16, 48, 5)
            G.rgba(ctx, G.INK, fa)
            ctx.fill()
        G.draw_text(ctx, "slow motion", cx + 36, cy + 14, 42, alpha=fa)

    ta = window(t, c["tag"], S.ls("intro_3") + 0.3)
    G.label(ctx, "Maya, 11", INTRO_MAYA_X + 30, GROUND - 640, ta, size=44, bg=G.hexc("FFF1C9"))

    # title card
    tc = 1 - ramp(t, 3.6, 0.6)
    if tc > 0:
        ctx.set_source_rgba(1, 1, 1, 0.35 * tc)
        ctx.paint()
        pop = G.back_out(clamp(t / 0.8))
        ctx.save()
        ctx.translate(960, 440)
        ctx.scale(pop, pop)
        G.panel(ctx, -640, -190, 1280, 380, tc, fill=G.CREAM, r=60)
        G.draw_text(ctx, "How Your Body Works", 0, 10, 112, G.INK, alpha=tc)
        G.draw_text(ctx, "One catch. A lot of teamwork.", 0, 100, 46, G.hexc("E0702A"), alpha=tc)
        ctx.restore()
    if zoom > 0.6:
        ctx.set_source_rgba(1, 1, 1, (zoom - 0.6) / 0.4)
        ctx.paint()


# Scene 2: eyes, brain, nerves ------------------------------------------
EYE_C = (1000, 430)
EYE_R = 100
BALL_C = (250, 440)
OPTIC = [(1098, 436), (1140, 452), (1200, 456), (1250, 436), (1300, 400), (1360, 360), (1400, 330)]
BRAIN_C = (1290, 280)


HEAD_C = (1170, 420)
HEAD_R = 335


def head_side(ctx, alpha=1.0):
    """Large side view of Maya's head facing left, as a pale outline."""
    hx, hy = HEAD_C
    ctx.new_path()
    ctx.rectangle(hx - 110, hy + 200, 230, 700)
    G.rgba(ctx, G.BODY_FILL, alpha)
    ctx.fill_preserve()
    G.rgba(ctx, G.BODY_LINE, alpha)
    ctx.set_line_width(7)
    ctx.stroke()
    G.circle(ctx, hx, hy, HEAD_R)
    # nose
    ctx.move_to(hx - HEAD_R + 30, hy + 70)
    ctx.curve_to(hx - HEAD_R - 20, hy + 120, hx - HEAD_R - 30, hy + 150, hx - HEAD_R + 22, hy + 160)
    ctx.close_path()
    G.rgba(ctx, G.BODY_FILL, alpha)
    ctx.fill()
    G.circle(ctx, hx, hy, HEAD_R)
    G.rgba(ctx, G.BODY_LINE, alpha)
    ctx.set_line_width(7)
    ctx.stroke()
    ctx.move_to(hx - HEAD_R + 22, hy + 60)
    ctx.curve_to(hx - HEAD_R - 20, hy + 120, hx - HEAD_R - 30, hy + 150, hx - HEAD_R + 22, hy + 160)
    ctx.stroke()
    # hair on the back and top of the head
    ctx.new_path()
    ctx.arc(hx, hy, HEAD_R + 4, math.pi * 1.25, math.pi * 2.3)
    ctx.arc_negative(hx, hy, HEAD_R - 22, math.pi * 2.3, math.pi * 1.25)
    ctx.close_path()
    G.rgba(ctx, M.HAIR, alpha * 0.85)
    ctx.fill()


def eye_diagram(ctx, alpha=1.0, retina_glow=0.0):
    x, y = EYE_C
    G.circle(ctx, x, y, EYE_R)
    G.fill_stroke(ctx, O.EYE_WHITE, G.INK, 5, alpha)
    # cornea bulge at the front (left)
    ctx.new_path()
    ctx.arc(x - EYE_R + 8, y, 44, math.pi * 0.62, math.pi * 1.38)
    G.rgba(ctx, G.hexc("D8F1FF"), alpha)
    ctx.fill_preserve()
    G.rgba(ctx, G.INK, alpha)
    ctx.set_line_width(4)
    ctx.stroke()
    # iris seen edge-on
    for sgn in (-1, 1):
        ctx.rectangle(x - EYE_R + 20, y + sgn * 22 - (8 if sgn < 0 else -8) - 10, 10, 30 * sgn)
    G.rgba(ctx, O.IRIS, alpha)
    ctx.fill()
    # lens
    ctx.save()
    ctx.translate(x - EYE_R + 40, y)
    ctx.scale(0.45, 1)
    G.circle(ctx, 0, 0, 38)
    ctx.restore()
    G.fill_stroke(ctx, G.hexc("CDEBFF"), G.INK, 3, alpha)
    # retina on the back wall
    ctx.new_path()
    ctx.arc(x, y, EYE_R - 9, -math.pi * 0.36, math.pi * 0.36)
    G.rgba(ctx, O.RETINA, alpha)
    ctx.set_line_width(14)
    ctx.stroke()
    if retina_glow > 0:
        ctx.new_path()
        ctx.arc(x, y, EYE_R - 9, -math.pi * 0.36, math.pi * 0.36)
        ctx.set_source_rgba(1, 0.85, 0.3, 0.6 * retina_glow * alpha)
        ctx.set_line_width(30)
        ctx.stroke()


def light_rays(ctx, t0, t, alpha=1.0):
    k = ease((t - t0) / 1.4)
    if k <= 0:
        return
    lens = (EYE_C[0] - EYE_R + 40, EYE_C[1])
    rt = EYE_C[0] + EYE_R - 12
    rays = [
        [(BALL_C[0] + 20, BALL_C[1] - 50), (lens[0], lens[1] - 14), (rt - 6, EYE_C[1] + 42)],
        [(BALL_C[0] + 20, BALL_C[1] + 50), (lens[0], lens[1] + 14), (rt - 6, EYE_C[1] - 42)],
    ]
    for pts in rays:
        G.arrow(ctx, pts, G.hexc("FFC93C"), 8, alpha, upto=k)


def signals(ctx, pts, t, t0, alpha=1.0, speed=0.55, count=4):
    a = ramp(t, t0, 0.4) * alpha
    if a <= 0:
        return
    G.Path(pts).stroke(ctx, G.hexc("F2C94C"), 16, a * 0.9)
    G.Path(pts).stroke(ctx, G.hexc("FFF3B0"), 7, a)
    G.dots_along(ctx, pts, G.SIGNAL, t - t0, speed=speed, count=count, r=11, alpha=a, glow=True)


def nerve_card(ctx, t, c, alpha):
    if alpha <= 0:
        return
    ctx.set_source_rgba(0.96, 0.97, 1, 0.75 * alpha)
    ctx.paint()
    G.panel(ctx, 260, 150, 1400, 600, alpha)
    # the nerve: a cable with fibres inside
    ctx.rectangle(420, 390, 640, 120)
    G.fill_stroke(ctx, G.hexc("FFF4C7"), G.INK, 4, alpha)
    ctx.save()
    ctx.translate(420, 450)
    ctx.scale(0.45, 1)
    G.circle(ctx, 0, 0, 60)
    ctx.restore()
    G.fill_stroke(ctx, G.hexc("FFE9A8"), G.INK, 4, alpha)
    for i in range(9):
        ang = i * 2 * math.pi / 9
        fx, fy = 420 + 17 * math.cos(ang), 450 + 40 * math.sin(ang)
        G.circle(ctx, fx, fy, 8)
        G.fill_stroke(ctx, G.hexc("F2C94C"), G.INK, 2, alpha)
    for k in range(5):
        y = 405 + k * 22
        ctx.move_to(430, y)
        ctx.line_to(1060, y)
        G.rgba(ctx, G.hexc("E8C66A"), alpha * 0.7)
        ctx.set_line_width(4)
        ctx.stroke()
    # one neuron whose fibre joins the cable
    cb = (1400, 330)
    fibre = [cb, (1330, 380), (1220, 430), (1100, 449), (1060, 449), (430, 449)]
    G.Path(fibre[:5]).stroke(ctx, G.INK, 14, alpha)
    G.Path(fibre).stroke(ctx, G.hexc("FFD84D"), 8, alpha)
    for ang in range(0, 360, 60):
        r = math.radians(ang + 20)
        ctx.move_to(*cb)
        ctx.line_to(cb[0] + 95 * math.cos(r), cb[1] + 85 * math.sin(r))
        ctx.line_to(cb[0] + 120 * math.cos(r + 0.25), cb[1] + 105 * math.sin(r + 0.25))
        G.rgba(ctx, G.INK, alpha)
        ctx.set_line_width(12)
        ctx.stroke()
        ctx.move_to(*cb)
        ctx.line_to(cb[0] + 95 * math.cos(r), cb[1] + 85 * math.sin(r))
        ctx.line_to(cb[0] + 120 * math.cos(r + 0.25), cb[1] + 105 * math.sin(r + 0.25))
        G.rgba(ctx, G.hexc("FFD84D"), alpha)
        ctx.set_line_width(6)
        ctx.stroke()
    G.circle(ctx, cb[0], cb[1], 48)
    G.fill_stroke(ctx, G.hexc("FFD84D"), G.INK, 5, alpha)
    G.circle(ctx, cb[0], cb[1], 18)
    G.rgba(ctx, G.hexc("C99A1E"), alpha)
    ctx.fill()
    G.dots_along(ctx, fibre, G.SIGNAL, t, speed=0.45, count=3, r=10, alpha=alpha, glow=True)
    G.label(ctx, "nerve", 620, 600, alpha * ramp(t, c["nerve_card"] + 0.4), anchor=(620, 510))
    G.label(ctx, "neuron", 1400, 560, alpha * ramp(t, c["neurons"]), anchor=(1400, 380))


LIMB_NERVES = [
    [(960, 200), (960, 240), (960, 300), (905, 300), (872, 360), (850, 450), (838, 530)],
    [(960, 200), (960, 240), (960, 300), (1015, 300), (1048, 360), (1070, 450), (1082, 530)],
    [(960, 200), (960, 240), (960, 470), (930, 540), (918, 640), (908, 760), (900, 820)],
    [(960, 200), (960, 240), (960, 470), (990, 540), (1002, 640), (1012, 760), (1020, 820)],
]


def body_nerves(ctx, t, c, alpha):
    if alpha <= 0:
        return
    M.body_outline(ctx, 960, 60, 0.8, alpha)
    O.brain(ctx, 960, 125, 0.42, alpha, glow=0.5 + 0.5 * math.sin(t * 4))
    # spinal cord and nerves (static)
    for pts in LIMB_NERVES:
        G.Path(pts[1:]).stroke(ctx, G.hexc("F2C94C"), 9, alpha * 0.9)
    G.Path([(960, 160), (960, 470)]).stroke(ctx, G.hexc("F2C94C"), 16, alpha)
    ts = c["body"] + 0.6
    for i, pts in enumerate(LIMB_NERVES):
        if t > ts:
            G.dots_along(ctx, pts, G.SIGNAL, t - ts, speed=0.42, count=3, r=10,
                         alpha=alpha, phase=i * 0.08, glow=True)
    # muscles light up as signals arrive
    glow = ramp(t, ts + 1.2, 0.5) * (0.6 + 0.4 * math.sin(t * 6))
    for (x, y, rx, ry) in ((840, 380, 22, 50), (1080, 380, 22, 50), (918, 640, 34, 80), (1002, 640, 34, 80)):
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(rx, ry)
        G.circle(ctx, 0, 0, 1)
        ctx.restore()
        G.rgba(ctx, G.MUSCLE, alpha * (0.35 + 0.5 * glow))
        ctx.fill()
    G.label(ctx, "brain", 1180, 130, alpha * ramp(t, c["body"] + 0.4), anchor=(1010, 125))
    G.label(ctx, "spinal cord", 1260, 330, alpha * ramp(t, c["spinal"]), anchor=(965, 360))
    G.label(ctx, "nerves", 1240, 680, alpha * ramp(t, c["nerves"]), anchor=(1008, 700))


def eyes(ctx, t, S, c):
    G.soft_bg(ctx, G.hexc("EAF0FF"), t)
    pa = 1 - ramp(t, c["body"], 0.6)
    if pa > 0:
        head_side(ctx, pa)
        O.brain(ctx, BRAIN_C[0], BRAIN_C[1], 1.1, pa,
                glow=window(t, c["process"], c["body"], 0.5) * (0.6 + 0.4 * math.sin(t * 5)))
        eye_diagram(ctx, pa, window(t, c["retina"], c["retina"] + 3.0, 0.4))
        M.draw_ball(ctx, BALL_C[0], BALL_C[1], 60, 0.3, pa)
        light_rays(ctx, c["rays"], t, pa)
        signals(ctx, OPTIC, t, c["signals"], pa)
        # prediction arc while the brain processes the signals
        pr = ramp(t, c["process"] + 1.0, 1.2) * pa
        if pr > 0:
            pts = G.bezier_pts((BALL_C[0] + 70, BALL_C[1] - 40), (420, 220), (620, 200), (760, 330), 40)
            p = G.Path(pts)
            n = 14
            for i in range(n):
                if i / n > pr:
                    break
                x, y, _ = p.at(i / n)
                G.circle(ctx, x, y, 7)
                G.rgba(ctx, G.hexc("3A86FF"), pa)
                ctx.fill()
            if pr > 0.95:
                x, y, a = p.at(1.0)
                G.arrow_head(ctx, x, y, a, 30, G.hexc("3A86FF"), pa)
        lab_end = c["nerve_card"]
        G.label(ctx, "retina", 1080, 640, pa * window(t, c["retina"], lab_end),
                anchor=(EYE_C[0] + EYE_R - 12, EYE_C[1] + 40))
        G.label(ctx, "optic nerve", 1440, 580, pa * window(t, c["optic"], lab_end),
                anchor=(1200, 456))
        G.label(ctx, "brain", 1640, 150, pa * window(t, c["brain"], lab_end),
                anchor=(1420, 230))
    nerve_card(ctx, t, c, window(t, c["nerve_card"], c["process"], 0.45))
    body_nerves(ctx, t, c, ramp(t, c["body"], 0.6))
    G.scene_title(ctx, "Eyes, brain and nerves", t)


# Scene 3: muscles and bones --------------------------------------------
HIP = (880, 190)
FEMUR = 280
TIBIA = 280


def _rot(v, th):
    return (v[0] * math.cos(th) - v[1] * math.sin(th), v[0] * math.sin(th) + v[1] * math.cos(th))


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def leg_geometry(theta_deg):
    th = math.radians(theta_deg)
    K = (HIP[0], HIP[1] + FEMUR)
    A = _add(K, _rot((0, TIBIA), th))
    toe = _add(A, _rot((115, 0), th))
    P = _add(K, _rot((40, -6), th / 2))
    Oq = _add(HIP, (38, 20))
    Iq = _add(K, _rot((26, 55), th))
    Oh = _add(HIP, (-44, 24))
    Wh = _add(K, _rot((-38, -14), th / 2))
    Ih = _add(K, _rot((-24, 52), th))
    return dict(K=K, A=A, toe=toe, P=P, Oq=Oq, Iq=Iq, Oh=Oh, Wh=Wh, Ih=Ih)


def _towards(a, b, d):
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    return (b[0] - (b[0] - a[0]) / L * d, b[1] - (b[1] - a[1]) / L * d)


def leg_diagram(ctx, theta, quad_on, ham_on, alpha=1.0):
    g = leg_geometry(theta)
    K, A = g["K"], g["A"]
    # faint leg silhouette
    th = math.radians(theta)
    for (p1, p2, w) in ((HIP, K, 170), (K, A, 120)):
        G.capsule(ctx, p1[0], p1[1], p2[0], p2[1], w, G.BODY_FILL, alpha * 0.9)
    # pelvis
    px, py = HIP
    ctx.move_to(px - 70, py + 30)
    ctx.curve_to(px - 110, py - 20, px - 90, py - 110, px - 20, py - 120)
    ctx.curve_to(px + 40, py - 125, px + 80, py - 90, px + 70, py - 50)
    ctx.curve_to(px + 60, py - 20, px + 40, py - 10, px + 30, py + 10)
    ctx.curve_to(px + 10, py + 40, px - 40, py + 50, px - 70, py + 30)
    ctx.close_path()
    G.fill_stroke(ctx, G.BONE, G.INK, 4, alpha)
    G.circle(ctx, px, py, 34)
    G.fill_stroke(ctx, G.hexc("EFE3CC"), G.INK, 3, alpha)
    O.bone(ctx, HIP[0], HIP[1], K[0], K[1] - 6, 40, alpha)
    O.bone(ctx, K[0], K[1] + 8, A[0], A[1], 36, alpha)
    # foot
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    G.capsule(ctx, A[0], A[1], g["toe"][0], g["toe"][1], 30, G.BONE, alpha, G.INK, 4)
    # hamstrings (back)
    hb_end = _towards(g["Oh"], g["Wh"], 40)
    Lh = math.hypot(hb_end[0] - g["Oh"][0], hb_end[1] - g["Oh"][1])
    wh = 58 * (190 / Lh) ** 2.2 + 8 * ham_on
    col = G.mix(G.MUSCLE, G.MUSCLE_ACTIVE, ham_on)
    tend = [hb_end, g["Wh"], g["Ih"]]
    G.Path(tend).stroke(ctx, G.INK, 14, alpha)
    G.Path(tend).stroke(ctx, G.TENDON, 8, alpha)
    if ham_on > 0.05:
        O.muscle_spindle(ctx, g["Oh"][0], g["Oh"][1], hb_end[0], hb_end[1], wh + 22,
                         G.hexc("FFD23F"), alpha * ham_on * 0.7, outline=G.hexc("FFD23F"))
    O.muscle_spindle(ctx, g["Oh"][0], g["Oh"][1], hb_end[0], hb_end[1], wh, col, alpha)
    # quadriceps (front)
    qb_end = _towards(g["Oq"], g["P"], 55)
    Lq = math.hypot(qb_end[0] - g["Oq"][0], qb_end[1] - g["Oq"][1])
    wq = 66 * (205 / Lq) ** 2.2 + 8 * quad_on
    col = G.mix(G.MUSCLE, G.MUSCLE_ACTIVE, quad_on)
    tend = [qb_end, g["P"], g["Iq"]]
    G.Path(tend).stroke(ctx, G.INK, 14, alpha)
    G.Path(tend).stroke(ctx, G.TENDON, 8, alpha)
    if quad_on > 0.05:
        O.muscle_spindle(ctx, g["Oq"][0], g["Oq"][1], qb_end[0], qb_end[1], wq + 22,
                         G.hexc("FFD23F"), alpha * quad_on * 0.7, outline=G.hexc("FFD23F"))
    O.muscle_spindle(ctx, g["Oq"][0], g["Oq"][1], qb_end[0], qb_end[1], wq, col, alpha)
    # kneecap
    ctx.save()
    ctx.translate(*g["P"])
    ctx.rotate(th / 2)
    ctx.scale(0.75, 1)
    G.circle(ctx, 0, 0, 20)
    ctx.restore()
    G.fill_stroke(ctx, G.BONE, G.INK, 4, alpha)
    # pull arrows: along the active muscle, toward the hip end it pulls from
    for on, o, e, side in ((quad_on, g["Oq"], qb_end, 1), (ham_on, g["Oh"], hb_end, -1)):
        if on > 0.05:
            dx, dy = o[0] - e[0], o[1] - e[1]
            L = math.hypot(dx, dy)
            nx, ny = -dy / L * side * 85, dx / L * side * 85
            a0 = (e[0] + nx + dx * 0.05, e[1] + ny + dy * 0.05)
            a1 = (e[0] + nx + dx * 0.75, e[1] + ny + dy * 0.75)
            G.arrow(ctx, [a0, a1], G.ORANGE, 16, alpha * on)
    return g


def knee_arrow(ctx, g, direction, alpha):
    """Curved arrow near the ankle showing which way the shin swings."""
    if alpha <= 0.02:
        return
    K, A = g["K"], g["A"]
    ang = math.atan2(A[1] - K[1], A[0] - K[0])
    r = 330
    span = -0.45 * direction
    pts = [(K[0] + r * math.cos(ang + span * i / 20 - span * 0.2),
            K[1] + r * math.sin(ang + span * i / 20 - span * 0.2)) for i in range(21)]
    G.arrow(ctx, pts, G.ORANGE, 10, alpha)


def leg_keyframes(c):
    return [
        (0.0, 55.0), (c["contract"], 0.0), (c["joint"], 62.0), (c["front"], 0.0),
        (c["back"], 72.0), (c["turns"], 0.0), (c["turns"] + 0.8, 70.0), (c["turns"] + 1.6, 0.0),
    ]


def leg_state(t, c, move=1.0):
    """Knee angle, front/back muscle activity and swing direction at time t."""
    kf = leg_keyframes(c)
    theta, quad, ham, direction = kf[0][1], 0.0, 0.0, 0
    for i in range(1, len(kf)):
        t1, v1 = kf[i]
        v0 = kf[i - 1][1]
        d = move if i < 6 else 0.7
        if t < t1:
            break
        theta = lerp(v0, v1, ease((t - t1) / d))
        act = window(t, t1, t1 + d + 0.5, 0.2)
        if v1 < v0:
            quad, ham, direction = act, 0.0, 1
        else:
            quad, ham, direction = 0.0, act, -1
    return theta, quad, ham, direction


def muscles_leg(ctx, t, S, c, alpha):
    theta, quad, ham, direction = leg_state(t, c)
    g = leg_diagram(ctx, theta, quad, ham, alpha)
    knee_arrow(ctx, g, direction, alpha * max(quad, ham))
    # pull / push tags
    pa = window(t, c["pull"], c["contract"] - 0.2) * alpha
    if pa > 0:
        G.label(ctx, "pull", 380, 300, pa, size=50, bg=G.hexc("DFF7E3"))
        G.label(ctx, "push", 380, 420, ramp(t, c["push"]) * pa, size=50, bg=G.hexc("FFE1E1"))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(480, 300)
        ctx.line_to(500, 322)
        ctx.line_to(538, 276)
        G.rgba(ctx, G.hexc("2BA84A"), pa)
        ctx.set_line_width(10)
        ctx.stroke()
        ca = ramp(t, c["push"] + 0.2) * pa
        if ca > 0:
            ctx.move_to(482, 396)
            ctx.line_to(530, 444)
            ctx.move_to(530, 396)
            ctx.line_to(482, 444)
            G.rgba(ctx, G.CORAL, ca)
            ctx.set_line_width(10)
            ctx.stroke()
    qb_mid = ((g["Oq"][0] + g["P"][0]) / 2 + 30, (g["Oq"][1] + g["P"][1]) / 2)
    hb_mid = ((g["Oh"][0] + g["Wh"][0]) / 2 - 30, (g["Oh"][1] + g["Wh"][1]) / 2)
    G.label(ctx, "contracts = gets shorter", 1370, 300,
            alpha * window(t, c["contract"], c["tendons"] - 0.2), anchor=qb_mid)
    mus_w = S.word("mus_3", "muscles")
    end3 = S.ls("mus_4") - 0.1
    G.label(ctx, "muscle", 1260, 250, alpha * window(t, mus_w, end3), anchor=qb_mid)
    tq = _towards(g["Oq"], g["P"], 28)
    G.label(ctx, "tendon", 1260, 470, alpha * window(t, c["tendons"], end3), anchor=tq)
    G.label(ctx, "bone", 520, 330, alpha * window(t, c["bones"], end3), anchor=(HIP[0] - 12, 330))
    G.label(ctx, "joint", 520, 480, alpha * window(t, c["joint"], end3), anchor=(g["K"][0] - 20, g["K"][1]))
    G.label(ctx, "front thigh muscle", 1330, 300, alpha * window(t, c["front"], c["run"]), anchor=qb_mid)
    G.label(ctx, "back thigh muscle", 470, 300, alpha * window(t, c["back"], c["run"]), anchor=hb_mid)


def run_x(t, c):
    t0, t1 = c["run"] + 0.2, c["catch"]
    k = clamp((t - t0) / (t1 - t0))
    return lerp(260, 760, 1 - (1 - k) ** 1.6)


def run_pose(t, c):
    t0 = c["run"] + 0.2
    run = M.run(t - t0, RUN_CADENCE)
    if t < c["lift"]:
        return run
    k = ease((t - c["lift"]) / 0.7)
    p = M.blend(run, M.reach(), k)
    if t >= c["catch"]:
        k2 = ease((t - c["catch"] - 0.4) / 0.6)
        p = M.blend(M.reach(), M.hold(t), k2)
    return p


def catch_point(c):
    x = run_x(c["catch"], c)
    pts = maya_points(M.reach(), x, GROUND, 1.0)
    hx = (pts["near_hand"][0] + pts["far_hand"][0]) / 2 + 30
    hy = (pts["near_hand"][1] + pts["far_hand"][1]) / 2 - 5
    return hx, hy


def muscles_run(ctx, t, S, c, alpha):
    if alpha <= 0:
        return
    cam = 700 * clamp((t - c["run"]) / (c["catch"] - c["run"]))
    ctx.push_group()
    park(ctx, t, cam=cam)
    x = run_x(t, c)
    p = run_pose(t, c)
    pts = M.draw(ctx, x, GROUND, 1.0, p)
    # ball flies in from the right and lands in her hands
    cx, cy = catch_point(c)
    tl = c["catch"] - 2.0
    if t < c["catch"]:
        u = clamp((t - tl) / 2.0)
        if u > 0:
            bx = lerp(2000, cx, u)
            by = lerp(120, cy, u) - 260 * math.sin(math.pi * u) * (1 - u)
            M.draw_ball(ctx, bx, by, 42, spin=u * 10)
    else:
        hx = (pts["near_hand"][0] + pts["far_hand"][0]) / 2 + 30
        hy = (pts["near_hand"][1] + pts["far_hand"][1]) / 2 - 5
        M.draw_ball(ctx, hx, hy, 42, spin=0)
        ga = window(t, c["catch"] + 0.05, c["catch"] + 3.0, 0.2)
        if ga > 0:
            sc = G.back_out(clamp((t - c["catch"]) / 0.4))
            ctx.save()
            ctx.translate(x + 470, 250)
            ctx.scale(sc, sc)
            for i in range(10):
                a = i * math.pi / 5
                ctx.move_to(0, 0)
                ctx.line_to(150 * math.cos(a), 150 * math.sin(a))
            G.rgba(ctx, G.YELLOW, ga * 0.6)
            ctx.set_line_width(14)
            ctx.stroke()
            G.draw_text(ctx, "Got it!", 0, 24, 84, G.hexc("E0702A"), alpha=ga, outline=G.WHITE, ow=14)
            ctx.restore()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)


def muscles(ctx, t, S, c):
    G.soft_bg(ctx, G.hexc("E6F2FF"), t)
    switch = c["run"] + 0.3
    la = 1 - ramp(t, switch, 0.6)
    if la > 0:
        muscles_leg(ctx, t, S, c, la)
    muscles_run(ctx, t, S, c, ramp(t, switch, 0.6))
    if t < switch:
        G.scene_title(ctx, "Muscles and bones", t)
