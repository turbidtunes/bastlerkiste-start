"""medwalls.py – garden-wall runs, piers and gates of the Mediterranean village (Worker WZ, S25), shared by
geo_medhouse.py (photo types 17+) and geo_medwall.py (stand-alone wall pieces). Photos refs/photos/med_houses/:
cast vase-baluster walls on a rendered base (corner_balustrade, two_storey_balustrade), baluster panel fences between
marès piers (street_bungalow_poles), dry-laid limestone with a coping slab (stonewall_porch, street_bougainvillea),
marès ashlar (villa_arcade), rendered walls with pilasters (corner_bungalow_wall), breeze-block screens
(pink_arcade_balustrade). Plan convention: a run q0 -> q1 has the street on its right.
init(ctx, C_EXT, C_STONE, C_TRIM, rng, crazy_paving) first; crazy_paving(org, u, n, a, b, z0, z1) is the caller's
limestone facing (geo_medhouse's)."""
import math
import numpy as np
import bldlib as B
from bldlib import srgb
import hlib as H
from hlib import cbox
import civlib as C
CL_ = C
PIERS = []


def init(ctx_, c_ext, c_stone, c_trim, rng, crazy):
    global ctx, C_EXT, C_STONE, C_TRIM, wrng, crazy_paving
    ctx, C_EXT, C_STONE, C_TRIM, wrng, crazy_paving = ctx_, c_ext, c_stone, c_trim, rng, crazy
    PIERS.clear()


def obox(mb, p0, p1, n0, n1, z0, z1, col, ucx=True, A=0.0):
    """box along p0 -> p1 (plan, any direction), from n0 to n1 on its left normal, z0..z1"""
    p0 = np.array([p0[0], p0[1], 0.]); p1 = np.array([p1[0], p1[1], 0.]); L = np.linalg.norm(p1 - p0)
    if L < 1e-3 or z1 - z0 < 1e-3: return
    d = (p1 - p0) / L; nn = np.array([-d[1], d[0], 0.])
    V, F, uv, cc = H._box_dir((p0 + p1) / 2 + nn * (n0 + n1) / 2 + [0, 0, (z0 + z1) / 2], d, nn, L, z1 - z0, n1 - n0, (*col, A))
    mb.add(V, F, uv, cc)
    if ucx: ctx.hull(V)


def pier(x, y, s, h, stone=True, cap=True):
    """square gate / wall pier, marès ashlar (course lines) or rendered, with a moulded cap"""
    if any(abs(x - a_) < .3 and abs(y - b_) < .3 for a_, b_ in PIERS): return
    PIERS.append((x, y)); mb, col = (ctx.stone, C_STONE) if stone else (ctx.plaster, C_EXT)
    if stone:
        for k, z in enumerate(np.arange(0, h, .3)):
            cbox(mb, (x - s / 2, y - s / 2, z), (x + s / 2, y + s / 2, min(h, z + .29)), {"all": tuple(np.array(col) * wrng.uniform(.9, 1.04))}, A=.15)
    else: cbox(mb, (x - s / 2, y - s / 2, 0), (x + s / 2, y + s / 2, h), {"all": col}, damp_z=0, damp_amt=.3)
    if cap: cbox(ctx.stone, (x - s / 2 - .04, y - s / 2 - .04, h), (x + s / 2 + .04, y + s / 2 + .04, h + .07), {"all": C_STONE}, A=.15)
    ctx.ucxb((x - s / 2, y - s / 2, 0), (x + s / 2, y + s / 2, h + .07))


VASE = [(.6, 0), (.85, .05), (.55, .16), (.75, .3), (1.0, .5), (.8, .7), (.45, .8), (.85, .9), (.65, 1.0)]   # vase baluster, r / rmax over t = 0..1


def balustrade(q0, q1, z0, hb, rmax=.05, step=.17, dies=0):
    """cast balustrade between two piers: plinth rail, vase balusters scaled to the clear height, coping rail
    (cast marès colour); dies = panelled solid blocks every n balusters (photo corner_balustrade)"""
    q0 = np.asarray(q0, float); q1 = np.asarray(q1, float); L = np.linalg.norm(q1 - q0); d = (q1 - q0) / L
    rb, rt = .08, .08; zc = z0 + rb + hb
    obox(ctx.stone, q0, q1, -.11, .11, z0, z0 + rb, C_STONE, ucx=False, A=.15)
    obox(ctx.stone, q0, q1, -.13, .13, zc, zc + rt, C_STONE, ucx=False, A=.15)
    n_ = max(1, int(L / step)); col = (*C_STONE, .15)
    for k in range(n_):
        c = q0 + d * (k + .5) * L / n_
        if dies and k % (dies + 1) == dies:                                       # solid die with a sunk panel
            obox(ctx.stone, c - d * .09, c + d * .09, -.1, .1, z0 + rb, zc, C_STONE, ucx=False, A=.15)
            obox(ctx.stone, c - d * .06, c + d * .06, -.105, .105, z0 + rb + .08, zc - .08, tuple(np.array(C_STONE) * .93), ucx=False, A=.2)
            continue
        rings = [[[c[0] + r * rmax * math.cos(t), c[1] + r * rmax * math.sin(t), z0 + rb + hb * z] for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)] for r, z in VASE]
        ctx.conc.grid(np.array(rings), col=col, close_v=True)
    ctx.hull([[*(q0 + np.array([-d[1], d[0]]) * e), z] for e in (-.13, .13) for z in (z0, zc + rt)] + [[*(q1 + np.array([-d[1], d[0]]) * e), z] for e in (-.13, .13) for z in (z0, zc + rt)])


def _bar(mb, p0, p1, n3, w, t, col):
    """straight bar in a vertical plane (p0, p1 3D in the plane, n3 = plane normal): width w in the plane, depth t"""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float); a = (p1 - p0) / np.linalg.norm(p1 - p0); s_ = np.cross(n3, a)
    V = [p + s_ * i * w / 2 + n3 * j * t / 2 for p in (p0, p1) for i in (-1, 1) for j in (-1, 1)]
    mb.add(V, [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]], [(float(np.dot(v, a)), float(np.dot(v, s_))) for v in V], col)


def _ring(mb, c, d3, n3, outer, inner, t, col):
    """closed ring prism in a vertical plane: outer / inner polygons as (u, v) around c, depth t along n3; every face
    wound outwards (front, back, outer and inner sides)"""
    up = np.array([0, 0, 1.]); P = lambda q, e: c + d3 * q[0] + up * q[1] + n3 * e
    k = len(outer); cc = c + d3 * np.mean([q[0] for q in outer]) + up * np.mean([q[1] for q in outer])
    def quad(V, want):
        nrm = np.cross(V[1] - V[0], V[3] - V[0])
        mb.add(V, [[0, 1, 2, 3] if np.dot(nrm, want) > 0 else [3, 2, 1, 0]], [(float(np.dot(v, d3)), float(v[2])) for v in V], col)
    for i in range(k):
        j = (i + 1) % k
        for e in (t / 2, -t / 2): quad([P(outer[i], e), P(outer[j], e), P(inner[j], e), P(inner[i], e)], n3 * np.sign(e))
        m_o = (P(outer[i], 0) + P(outer[j], 0)) / 2; m_i = (P(inner[i], 0) + P(inner[j], 0)) / 2
        quad([P(outer[i], t / 2), P(outer[j], t / 2), P(outer[j], -t / 2), P(outer[i], -t / 2)], m_o - cc)
        quad([P(inner[i], t / 2), P(inner[j], t / 2), P(inner[j], -t / 2), P(inner[i], -t / 2)], cc - m_i)


def oct_screen(c, d3, n3, w, h, t=.1, cell=.3, col=None):
    """cast concrete screen of octagon rings linked by short bars (the octagon breeze-block lattice of photo
    pink_arcade_balustrade): rings and the frame are closed prisms, links reach 10 mm into them (no butting faces);
    depth t; c = bottom centre"""
    col = (*(col or C_TRIM), .15); c = np.asarray(c, float); up = np.array([0, 0, 1.]); bw = .035
    nu = max(1, int(round(w / cell))); nv = max(1, int(round(h / cell))); cu, cv = w / nu, h / nv; R = min(cu, cv) * .36
    _ring(ctx.plaster, c, d3, n3, [(-w / 2, 0), (w / 2, 0), (w / 2, h), (-w / 2, h)], [(-w / 2 + bw, bw), (w / 2 - bw, bw), (w / 2 - bw, h - bw), (-w / 2 + bw, h - bw)], t, col)
    sc = 1 / math.cos(math.radians(22.5))
    for i in range(nu):
        for j in range(nv):
            uc, vc = -w / 2 + (i + .5) * cu, (j + .5) * cv
            ro, ri = (R + bw / 2) * sc, (R - bw / 2) * sc                       # vertex radii for apothems R +- bw/2
            ang = [math.radians(22.5 + 45 * k) for k in range(8)]
            _ring(ctx.plaster, np.array([0., 0, 0]) + c, d3, n3, [(uc + ro * math.cos(a_), vc + ro * math.sin(a_)) for a_ in ang],
                  [(uc + ri * math.cos(a_), vc + ri * math.sin(a_)) for a_ in ang], t * .96, col)
            a_o = R + bw / 2 - .01                                              # links start 10 mm inside the ring
            u_end = uc + cu - a_o if i < nu - 1 else w / 2 - bw + .01
            _bar(ctx.plaster, c + d3 * (uc + a_o) + up * vc, c + d3 * u_end + up * vc, n3, bw, t * .9, col)
            if i == 0: _bar(ctx.plaster, c + d3 * (-w / 2 + bw - .01) + up * vc, c + d3 * (uc - a_o) + up * vc, n3, bw, t * .9, col)
            v_end = vc + cv - a_o if j < nv - 1 else h - bw + .01
            _bar(ctx.plaster, c + d3 * uc + up * (vc + a_o), c + d3 * uc + up * v_end, n3, bw, t * .9, col)
            if j == 0: _bar(ctx.plaster, c + d3 * uc + up * (bw - .01), c + d3 * uc + up * (vc - a_o), n3, bw, t * .9, col)


def wall_run(style, q0, q1, h):
    """one straight run of a garden wall between two piers / gate edges (q = plan points on the wall centre line;
    the street is on the right of q0 -> q1)"""
    q0 = np.asarray(q0, float); q1 = np.asarray(q1, float); L = np.linalg.norm(q1 - q0)
    if L < .1: return
    d = (q1 - q0) / L; nn = np.array([-d[1], d[0]]); d3 = np.array([*d, 0.]); n3 = np.array([*nn, 0.])
    if style in ("baluster", "balpanel"):                                         # cast vase balusters on a rendered base, marès band + piers
        hb, hp, ps = (.6, .62, .44) if style == "baluster" else (.45, .5, .4)     # piers wider than base + band (no coplanar faces)
        obox(ctx.plaster, q0, q1, -.15, .15, 0, hb, C_EXT)
        obox(ctx.stone, q0, q1, -.18, .18, hb, hb + .06, C_STONE, ucx=False, A=.15)
        k = max(1, int(round(L / 2.4))); xs = np.linspace(0, L, k + 1)
        for a_, b_ in zip(xs[:-1], xs[1:]):
            if b_ - a_ - ps > .3:                                               # (short stub between two piers: no balusters)
                balustrade(q0 + d * (a_ + ps / 2), q0 + d * (b_ - ps / 2), hb + .06, hp - .16, rmax=.05 if style == "baluster" else .04,
                           step=.17 if style == "baluster" else .14, dies=5 if style == "baluster" else 0)
        for x_ in xs: p_ = q0 + d * x_; pier(p_[0], p_[1], ps, hb + hp + .14, stone=True)
    elif style == "rubble":                                                        # dry-laid limestone face both sides, marès coping slab
        obox(ctx.plaster, q0, q1, -.17, .17, 0, h, C_EXT)
        crazy_paving(np.array([*(q0 - nn * .17), 0.]), d3, -n3, 0, L, 0, h)
        crazy_paving(np.array([*(q1 + nn * .17), 0.]), -d3, n3, 0, L, 0, h)
        obox(ctx.stone, q0, q1, -.22, .22, h, h + .08, C_STONE, ucx=False, A=.2)
    elif style == "ashlar":                                                        # marès ashlar blocks (street face), rendered back, coping
        obox(ctx.plaster, q0, q1, -.15, .15, 0, h, C_EXT)
        org = np.array([*(q0 - nn * .15), 0.])
        for r_, z in enumerate(np.arange(0, h - .01, .3)):
            for x_ in np.arange(-.3 * (r_ % 2), L, .6):
                a_, b_ = max(0, x_), min(L, x_ + .58)
                if b_ - a_ > .05: C.wbox(ctx.stone, org, d3, -n3, a_, b_, z + .005, min(h, z + .295), 0, .02, tuple(np.array(C_STONE) * wrng.uniform(.86, 1.05)), .2)
        obox(ctx.stone, q0, q1, -.2, .2, h, h + .07, C_STONE, ucx=False, A=.15)
    elif style in ("render_high", "render_low"):                                  # rendered wall, pilasters every 2.4 m (high), coping
        t_ = .25 if style == "render_high" else .2
        obox(ctx.plaster, q0, q1, -t_ / 2, t_ / 2, 0, h, C_EXT)
        if style == "render_high":
            for x_ in np.linspace(0, L, max(1, int(round(L / 2.4))) + 1)[1:-1]:
                p_ = q0 + d * x_; obox(ctx.plaster, p_ - d * .15, p_ + d * .15, -t_ / 2 - .04, t_ / 2 + .04, 0, h + .05, C_EXT, ucx=False)
        obox(ctx.plaster, q0, q1, -t_ / 2 - .03, t_ / 2 + .03, h, h + .05, C_TRIM, ucx=False)
    elif style == "breeze":                                                        # cast breeze-block screen on a rendered base, marès coping
        obox(ctx.plaster, q0, q1, -.1, .1, 0, .4, C_EXT)
        k = max(1, int(round(L / 2.4))); xs = np.linspace(0, L, k + 1)
        for a_, b_ in zip(xs[:-1], xs[1:]):
            w_ = round(int((b_ - a_ - .32) / .3) * .3, 3)
            if w_ > .19:
                c_ = q0 + d * (a_ + b_) / 2; oct_screen(np.array([*c_, .4]), d3, n3, w_, .6, t=.1)
                for s0, s1 in ((a_ + .15, (a_ + b_) / 2 - w_ / 2), ((a_ + b_) / 2 + w_ / 2, b_ - .15)):
                    if s1 - s0 > .005: obox(ctx.plaster, q0 + d * s0, q0 + d * s1, -.1, .1, .4, 1.0, C_EXT, ucx=False)
            ctx.hull([[*(q0 + d * a_ + nn * e), z] for e in (-.1, .1) for z in (0, 1.0)] + [[*(q0 + d * b_ + nn * e), z] for e in (-.1, .1) for z in (0, 1.0)])
        obox(ctx.stone, q0, q1, -.14, .14, 1.0, 1.06, C_STONE, ucx=False, A=.15)
        for x_ in xs: p_ = q0 + d * x_; pier(p_[0], p_[1], .3, 1.06, stone=False)


def gate_leaves(hp, dd, lw, h, kind):
    """one leaf from hinge point hp along dd (plan), width lw: timber planks with a curved top, or a steel bar gate"""
    hp = np.asarray(hp, float); dd = np.asarray(dd, float)
    if kind == "steel":
        col = (*srgb(wrng.choice(["#9aa0a0", "#2a2a28", "#d8d8d4"])), .2)
        for (a_, za), (b_, zb) in (((0, .05), (lw, .05)), ((0, h), (lw, h)), ((0, .05), (0, h)), ((lw, .05), (lw, h)), ((0, h * .4), (lw, h * .4))):
            B.sweep(ctx.steel, np.array([[*(hp + dd * a_), za], [*(hp + dd * b_), zb]]), B.rect(.04, .04), col, up=(0, 0, 1) if za == zb else (*dd, 0))
        C.wbox(ctx.steel, np.array([*hp, 0.]), np.array([*dd, 0.]), np.array([-dd[1], dd[0], 0.]), .03, lw - .03, .07, h * .4, -.005, .005, col[:3], .2)    # lower sheet
        for k in range(1, int(lw / .11)):
            q = hp + dd * k * .11; B.sweep(ctx.steel, np.array([[*q, h * .4], [*q, h + .08]]), B.rect(.016, .016), col, up=(*dd, 0))
    else:
        col = (*srgb(wrng.choice(["#6b4528", "#5a3a24", "#a0582c"])), .2)
        for zz in (.15, h - .1): B.sweep(ctx.timber, np.array([[*hp, zz], [*(hp + dd * lw), zz]]), B.rect(.07, .03), col, up=(0, 0, 1))
        for k in range(int(lw / .1)):
            q = hp + dd * (.05 + k * .1); top = h + .12 * math.sin(math.pi * min(1, (k * .1 + .05) / lw))
            B.sweep(ctx.timber, np.array([[*q, .05], [*q, top]]), B.rect(.08, .025), col, up=(0, 0, 1))


