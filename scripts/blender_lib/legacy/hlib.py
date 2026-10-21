"""hlib.py – building blocks for the Mauritian village houses (Session G): walls with openings, louvre / shutter /
slider windows, burglar grilles, doors, railings (steel bars or precast balusters), external stairs, flat slabs with
rebar stubs, corrugated-iron roofs (gable, hip, lean-to), water tank, solar heater, garden wall + gate.
All functions draw into the mesh builders of a Ctx; units metres, Z up, facades described by (org, u, n):
org = left end of the facade seen from outside at ground level of the block, u = along the facade, n = outward."""
import math
import numpy as np
import bldlib as B
from bldlib import MB, srgb


class Ctx:
    def __init__(self, rng):
        self.rng = rng
        for k in ("plaster", "raw", "tile", "conc", "rebar", "steel", "alu", "glass", "timber", "corr", "tank", "door",
                  "paintwood", "pvc"):
            setattr(self, k, MB())
        self.ucx = []; self.hulls = []
        self.C_GRILLE = srgb("#1c1c1c")

    def hull(self, pts):
        self.hulls.append(np.asarray(pts, float))

    def ucxb(self, lo, hi):
        lo, hi = np.asarray(lo, float), np.asarray(hi, float)
        if np.all(hi - lo > .01): self.ucx.append(((lo + hi) / 2, hi - lo))


def damp(z, z0, amount=.45): return float(np.clip(1 - (z - z0) / .55, 0, 1) * amount)


def cbox(mb, lo, hi, cols, damp_z=None, damp_amt=.45, A=0.0):
    """axis box lo..hi, per-face colour (keys px nx py ny pz nz, 'all'); A = rising damp above damp_z (or constant)"""
    lo, hi = np.asarray(lo, float), np.asarray(hi, float); lo, hi = np.minimum(lo, hi), np.maximum(lo, hi)   # (S32: hi was taken after lo was overwritten -> reversed corners gave a flat box)
    F = {"pz": ([(lo[0], lo[1], hi[2]), (hi[0], lo[1], hi[2]), (hi[0], hi[1], hi[2]), (lo[0], hi[1], hi[2])], (0, 1)),
         "nz": ([(lo[0], hi[1], lo[2]), (hi[0], hi[1], lo[2]), (hi[0], lo[1], lo[2]), (lo[0], lo[1], lo[2])], (0, 1)),
         "px": ([(hi[0], lo[1], lo[2]), (hi[0], hi[1], lo[2]), (hi[0], hi[1], hi[2]), (hi[0], lo[1], hi[2])], (1, 2)),
         "nx": ([(lo[0], hi[1], lo[2]), (lo[0], lo[1], lo[2]), (lo[0], lo[1], hi[2]), (lo[0], hi[1], hi[2])], (1, 2)),
         "py": ([(hi[0], hi[1], lo[2]), (lo[0], hi[1], lo[2]), (lo[0], hi[1], hi[2]), (hi[0], hi[1], hi[2])], (0, 2)),
         "ny": ([(lo[0], lo[1], lo[2]), (hi[0], lo[1], lo[2]), (hi[0], lo[1], hi[2]), (lo[0], lo[1], hi[2])], (0, 2))}
    for k, (V, ax) in F.items():
        c = cols.get(k, cols.get("all", (1, 1, 1)))
        if c is None: continue
        As = [max(A, damp(v[2], damp_z, damp_amt)) if damp_z is not None and k not in ("pz", "nz") else A for v in V]
        mb.add(V, [[0, 1, 2, 3]], [(v[ax[0]], v[ax[1]]) for v in V], [(*c, al) for al in As])


FACES = {"front": (np.array([0, -1., 0]), np.array([1., 0, 0])), "right": (np.array([1., 0, 0]), np.array([0, 1., 0])),
         "back": (np.array([0, 1., 0]), np.array([-1., 0, 0])), "left": (np.array([-1., 0, 0]), np.array([0, -1., 0]))}


def facade(rect, key):
    """(org, u, n, length) of a facade of rect (x0, x1, y0, y1)"""
    x0, x1, y0, y1 = rect; n, u = FACES[key]
    org = {"front": (x0, y0), "right": (x1, y0), "back": (x1, y1), "left": (x0, y1)}[key]
    L = x1 - x0 if key in ("front", "back") else y1 - y0
    return np.array([*org, 0.0]), u, n, L


def wall(ctx, rect, key, z0, z1, t, ops, c_ext, c_int, mb=None, damp_z=None, broken=None, damp_amt=.45, ucx=True):
    """exterior wall of a block facade: outer face on the block edge, openings ops = [(u0, u1, v0, v1, kind)] in facade
    metres (u from the facade's left end, v above z0). Front/back walls run the full length, sides fit between them.
    broken(u) -> metres lost at the top (ruins)."""
    mb = mb or ctx.plaster
    org, u, n, L = facade(rect, key)
    ua0, ua1 = (0.0, L) if key in ("front", "back") else (t, L - t)
    cuts_u = sorted({ua0, ua1, *[min(max(o[0], ua0), ua1) for o in ops], *[min(max(o[1], ua0), ua1) for o in ops]})
    if broken is not None:
        cuts_u = sorted(set(cuts_u) | set(np.arange(ua0, ua1, .4).tolist()))     # one block (400 mm) per step
    H = z1 - z0
    for ua, ub in zip(cuts_u[:-1], cuts_u[1:]):
        if ub - ua < 1e-4: continue
        um = (ua + ub) / 2; top = H - (broken(um) if broken else 0.0)
        blocked = sorted([(o[2], o[3]) for o in ops if o[0] < um < o[1]])
        iv, cur = [], 0.0
        for v0, v1 in blocked:
            if v0 > cur: iv.append((cur, min(v0, top)))
            cur = max(cur, v1)
        if cur < top and not (broken is not None and blocked): iv.append((cur, top))   # ruins: lintels fell, openings run to the break
        for va, vb in iv:
            if vb - va < .01: continue
            cutv = [v for v in ((damp_z + .6 - z0) if damp_z is not None else None,) if v is not None and va + .05 < v < vb - .05]
            for vva, vvb in zip([va] + cutv, cutv + [vb]):
                p_a = org + u * ua; p_b = org + u * ub
                lo = np.minimum(p_a, p_b) - np.abs(n) * 0; hi = np.maximum(p_a, p_b)
                inner = -n * t
                lo = np.minimum(lo, np.minimum(p_a + inner, p_b + inner)); hi = np.maximum(hi, np.maximum(p_a + inner, p_b + inner))
                lo[2], hi[2] = z0 + vva, z0 + vvb
                k_out = ("px" if n[0] > 0 else "nx") if abs(n[0]) > .5 else ("py" if n[1] > 0 else "ny")
                k_in = {"px": "nx", "nx": "px", "py": "ny", "ny": "py"}[k_out]
                cbox(mb, lo, hi, {"all": c_ext, k_out: c_ext, k_in: c_int}, damp_z, damp_amt)
                if ucx: ctx.ucxb(lo, hi)


def partition(ctx, p0, p1, z0, z1, t, doors=(), col=(1, 1, 1), mb=None):
    """interior wall (axis aligned) with doorways [(u0, u1)] 2.1 m high"""
    mb = mb or ctx.plaster
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float); L = np.linalg.norm(p1 - p0); d = (p1 - p0) / L
    nrm = np.array([-d[1], d[0], 0])
    cuts = sorted({0.0, L, *[c for dd in doors for c in dd]})
    for ua, ub in zip(cuts[:-1], cuts[1:]):
        um = (ua + ub) / 2; z_lo = z0
        if any(a <= um <= b for a, b in doors): z_lo = z0 + 2.1
        if z1 - z_lo < .01: continue
        a = np.array([*(p0 + d * ua)[:2], z_lo]) - nrm * t / 2; b = np.array([*(p0 + d * ub)[:2], z1]) + nrm * t / 2
        cbox(mb, np.minimum(a, b), np.maximum(a, b), {"all": col}); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


# ------------------------------------------------------------------ windows + doors
def louvre(ctx, c, u, w, h, n):
    """aluminium louvre window (glass jalousie blades tilted open) centred on c = sill centre in the wall"""
    def P(du, dz, dn=0): return c + u * du + np.array([0, 0, dz]) + n * dn
    for a_, b_ in (((-w / 2, 0), (w / 2, 0)), ((-w / 2, h), (w / 2, h)), ((-w / 2, 0), (-w / 2, h)), ((w / 2, 0), (w / 2, h))):
        B.sweep(ctx.alu, np.array([P(*a_), P(*b_)]), B.rect(.035, .06), (.78, .79, .8, 0), up=tuple(n))
    nbl = max(3, int(h / .135))
    for k in range(nbl):
        z = .07 + (h - .1) * (k + .5) / nbl; ang = math.radians(32); dz, dn = .065 * math.sin(ang), .065 * math.cos(ang)
        q = [P(-w / 2 + .03, z - dz, -dn), P(w / 2 - .03, z - dz, -dn), P(w / 2 - .03, z + dz, dn), P(-w / 2 + .03, z + dz, dn)]
        ctx.glass.add(q + [p + np.array([0, 0, .005]) for p in q], [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]],
                      [(i * .1, 0) for i in range(8)], (.75, .85, .82, 0))


def slider(ctx, c, u, w, h, n):
    """aluminium sliding window, two panes, one pushed half open"""
    def P(du, dz, dn=0): return c + u * du + np.array([0, 0, dz]) + n * dn
    for a_, b_ in (((-w / 2, 0), (w / 2, 0)), ((-w / 2, h), (w / 2, h)), ((-w / 2, 0), (-w / 2, h)), ((w / 2, 0), (w / 2, h))):
        B.sweep(ctx.alu, np.array([P(*a_), P(*b_)]), B.rect(.04, .07), (.85, .86, .86, 0), up=tuple(n))
    for k, (ua, ub, dn) in enumerate(((-w / 2 + .03, .04, .012), (-w / 2 + w * .3, w / 2 - .03, -.012))):
        for a_, b_ in (((ua, .03), (ub, .03)), ((ua, h - .03), (ub, h - .03)), ((ua, .03), (ua, h - .03)), ((ub, .03), (ub, h - .03))):
            B.sweep(ctx.alu, np.array([P(a_[0], a_[1], dn), P(b_[0], b_[1], dn)]), B.rect(.03, .02), (.85, .86, .86, 0), up=tuple(n))
        q = [P(ua + .015, .045, dn), P(ub - .015, .045, dn), P(ub - .015, h - .045, dn), P(ua + .015, h - .045, dn)]
        ctx.glass.add(q, [[0, 1, 2, 3]], [(0, 0)] * 4, (.7, .8, .8, 0))


def shutters(ctx, c, u, w, h, n, col, open_=True):
    """pair of timber louvred shutters (persiennes) hinged on the outer face, folded back against the wall"""
    leaf = w / 2
    for s_ in (-1, 1):
        hinge = c + u * s_ * w / 2 + n * .02
        d = u * s_ if open_ else -u * s_                           # open: lies flat on the wall beside the opening
        if open_: d = u * s_
        def P(a, z, dn=0): return hinge + d * a + np.array([0, 0, z]) + n * dn
        for a_, b_ in (((0, 0), (leaf, 0)), ((0, h), (leaf, h)), ((0, 0), (0, h)), ((leaf, 0), (leaf, h)), ((0, h / 2), (leaf, h / 2))):
            B.sweep(ctx.paintwood, np.array([P(*a_, .02), P(*b_, .02)]), B.rect(.06, .03), (*col, .1), up=tuple(n))
        for z in np.arange(.08, h - .05, .055):
            if abs(z - h / 2) < .05: continue
            q = [P(.03, z - .02, .008), P(leaf - .03, z - .02, .008), P(leaf - .03, z + .02, .03), P(.03, z + .02, .03)]
            ctx.paintwood.add(q, [[0, 1, 2, 3]], [(p[0] + p[1], p[2]) for p in q], (*col, .1))
        for k in (.2, h - .25):
            B.box(ctx.steel, P(0, k, .02), (.05, .05, .05), col=(.3, .3, .3, .4))


def grille(ctx, c, u, w, h, n, col, style=0):
    """burglar grille on the outer face: frame, vertical bars every 0.12, rails; style 1 adds a scroll band,
    style 2 a diamond lattice"""
    cc = (*col, .1)
    def P(du, dz): return c + u * du + np.array([0, 0, dz]) + n * .025
    W2, H2 = w / 2 + .06, h + .06
    for a_, b_ in (((-W2, -.06), (W2, -.06)), ((-W2, H2), (W2, H2)), ((-W2, -.06), (-W2, H2)), ((W2, -.06), (W2, H2))):
        B.sweep(ctx.steel, np.array([P(*a_), P(*b_)]), B.rect(.025, .025), cc, up=tuple(n))
    if style == 2:
        m = max(2, int(2 * W2 / .2))
        for k in range(-m, 2 * m):
            x0 = -W2 + k * .2
            for sgn in (1, -1):
                pa, pb = (x0, -.06), (x0 + sgn * (H2 + .06), H2)
                # clip to the frame
                t0, t1 = 0, 1
                for t_ in np.linspace(0, 1, 41):
                    pass
                xa, xb = pa[0], pb[0]
                if max(xa, xb) < -W2 or min(xa, xb) > W2: continue
                def cl(x, z):
                    return max(-W2, min(W2, x)), z
                ts = np.linspace(0, 1, 2)
                A_ = np.array(pa); B_ = np.array(pb); dv = B_ - A_
                tl = [0, 1]
                for lim in (-W2, W2):
                    if abs(dv[0]) > 1e-6:
                        tt = (lim - A_[0]) / dv[0]
                        if 0 < tt < 1: tl.append(tt)
                tl = sorted(tl); seg = [(ta, tb) for ta, tb in zip(tl[:-1], tl[1:]) if -W2 - 1e-6 <= (A_ + dv * (ta + tb) / 2)[0] <= W2 + 1e-6]
                for ta, tb in seg:
                    qa, qb = A_ + dv * ta, A_ + dv * tb
                    B.sweep(ctx.steel, np.array([P(*qa), P(*qb)]), B.rect(.012, .012), cc, up=tuple(n))
        return
    for z in (h * .33, h * .66):
        B.sweep(ctx.steel, np.array([P(-W2, z), P(W2, z)]), B.rect(.02, .02), cc, up=tuple(n))
    nbar = int(2 * W2 / .12)
    for k in range(1, nbar):
        du = -W2 + 2 * W2 * k / nbar
        B.sweep(ctx.steel, np.array([P(du, -.06), P(du, H2)]), B.rect(.012, .012), cc, up=tuple(n))
    if style == 1:
        for k in range(int(2 * W2 / .24)):
            du = -W2 + .12 + .24 * k
            B.tube_path(ctx.steel, [P(du + .05 * math.cos(t), h * .5 + .05 * math.sin(t)) for t in np.linspace(.5, 5.8, 9)], .006, 6, cc, up=tuple(n))


def door_leaf(ctx, hinge, u, n_in, col, open_deg=88, w=.86, h=2.06, glazed=False, working=True):
    """panelled timber door hinged at 'hinge' (bottom, inner face), opening towards n_in. working (user 18.10.: "Türen
    müssen funktionieren"): the leaf is drawn CLOSED into builders of its own (MB.leaves of ctx.door / glass / steel ->
    objects DoorLeaf_<nn>_<mat> with the hinge frame); export_bld.py exports them as SM_<mesh>_Door_<nn> + doors.json
    and ABKDoor swings them in the game – open_deg only applies to working=False (a leaf that stays part of the mesh)."""
    h0 = np.asarray(hinge, float); cc = (*col, .0)
    dst = {"door": ctx.door, "glass": ctx.glass, "steel": ctx.steel}
    if working:
        n_ = getattr(ctx, "_nleaf", 0) + 1; ctx._nleaf = n_; open_deg = 0
        meta = dict(n=n_, hinge=[round(float(x), 4) for x in h0], u=[round(float(x), 5) for x in u],
                    n_in=[round(float(x), 5) for x in n_in], w=round(float(w), 3), h=round(float(h), 3))
        for k in dst:
            m = MB(); dst[k].leaves.append((f"DoorLeaf_{n_:02d}", m, meta)); dst[k] = m
    a_ = math.radians(open_deg); d = u * math.cos(a_) + n_in * math.sin(a_); side = np.cross(np.array([0, 0, 1.0]), d)
    def bx(cen_u, cen_z, du, dz, th):
        dst["door"].add(*_box_dir(h0 + d * cen_u + [0, 0, cen_z], d, side, du, dz, th, cc))
    bx(.05, h / 2, .1, h - .01, .042); bx(w - .05, h / 2, .1, h - .02, .042)
    for z0_, z1_ in ((.01, .12), (h - .12, h), (.95, 1.07)): bx(w / 2, (z0_ + z1_) / 2, w - .2, z1_ - z0_, .04)
    for z0_, z1_ in ((.12, .95), (1.07, h - .12)):
        if glazed and z0_ > 1: dst["glass"].add(*_box_dir(h0 + d * (w / 2) + [0, 0, (z0_ + z1_) / 2], d, side, w - .2, z1_ - z0_, .006, (.7, .8, .8, 0)))
        else: bx(w / 2, (z0_ + z1_) / 2, w - .2, z1_ - z0_, .024)
    for sd in ((1, -1) if working else (1,)):           # lever handle (both faces on a working leaf)
        B.box(dst["steel"], h0 + d * (w - .1) + side * .04 * sd + [0, 0, 1.0], (.03, .03, .12), col=(.6, .55, .4, .3))


def _box_dir(c, d, side, du, dz, th, col):
    """oriented box (d = length axis, side = thickness axis) -> (verts, faces, uv, col) for MB.add"""
    V = [c + d * a * du / 2 + side * b * th / 2 + np.array([0, 0, e * dz / 2]) for a in (-1, 1) for b in (-1, 1) for e in (-1, 1)]
    F = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    uv = [(float(np.dot(v, d)), float(v[2])) for v in V]
    return V, F, uv, col


def grille_door(ctx, hinge, u, n_out, col, open_deg=100, w=.86, h=2.06):
    """steel security gate in front of a door, swung outwards"""
    a_ = math.radians(open_deg); d = u * math.cos(a_) + n_out * math.sin(a_); cc = (*col, .15)
    def P(a, z): return hinge + d * a + np.array([0, 0, z])
    for (a0, z0), (a1, z1) in (((0, 0), (w, 0)), ((0, h), (w, h)), ((0, 0), (0, h)), ((w, 0), (w, h)), ((0, h * .45), (w, h * .45))):
        B.sweep(ctx.steel, np.array([P(a0, z0), P(a1, z1)]), B.rect(.03, .03), cc, up=(0, 0, 1) if z0 == z1 else tuple(np.cross([0, 0, 1], d)))
    for a in np.arange(.1, w - .05, .1):
        B.sweep(ctx.steel, np.array([P(a, 0), P(a, h)]), B.rect(.014, .014), cc, up=tuple(np.cross([0, 0, 1], d)))


# ------------------------------------------------------------------ railings, stairs
def railing(ctx, pts, z0, col, style="bars", h=.95, posts=1.5, conc_col=(.9, .9, .88)):
    """steel bar railing or precast concrete balustrade (vase balusters between a plinth and a coping rail)"""
    P = [np.array([p[0], p[1], 0.0]) for p in pts]
    if style == "baluster":
        for pa, pb in zip(P[:-1], P[1:]):
            L = np.linalg.norm(pb - pa); d = (pb - pa) / L; side = np.array([-d[1], d[0], 0])
            for zc, hh, ww in ((z0 + .06, .12, .16), (z0 + h - .04, .08, .2)):
                V, F, uv, c = _box_dir(np.array([*((pa + pb) / 2)[:2], zc]), np.array([*d[:2], 0]), side, L, hh, ww, (*conc_col, .2))
                ctx.conc.add(V, F, uv, c)
            nb = max(1, int(L / .2))
            for k in range(nb):
                q = pa + d * (k + .5) * L / nb
                prof = [(.035, 0), (.045, .03), (.03, .1), (.055, .35), (.04, .55), (.025, .6), (.045, .66), (.035, h - .2 - .08)]
                rings = [[[q[0] + r * math.cos(t), q[1] + r * math.sin(t), z0 + .12 + z] for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)] for r, z in prof]
                ctx.conc.grid(np.array(rings), col=(*conc_col, .2), close_v=True)
            for q in ((pa, pb) if pb is P[-1] else (pa,)):        # one pier per corner (duplicates flip normals)
                cbox(ctx.conc, (q[0] - .11, q[1] - .11, z0), (q[0] + .11, q[1] + .11, z0 + h + .02), {"all": conc_col})
            ctx.ucxb(np.minimum(pa, pb) - [.1, .1, 0] + [0, 0, z0], np.maximum(pa, pb) + [.1, .1, z0 + h])
        return
    cc = (*col, .15)
    for pa, pb in zip(P[:-1], P[1:]):
        L = np.linalg.norm(pb - pa); n_ = max(1, int(round(L / posts)))
        for k in range(n_ + 1):
            q = pa + (pb - pa) * k / n_
            B.sweep(ctx.steel, np.array([[q[0], q[1], z0], [q[0], q[1], z0 + h]]), B.rect(.04, .04), cc, up=(1, 0, 0))
        for zz, w_ in ((z0 + h, .04), (z0 + .45, .02), (z0 + .08, .02)):
            B.sweep(ctx.steel, np.array([[pa[0], pa[1], zz], [pb[0], pb[1], zz]]), B.rect(w_, .02), cc, up=(0, 0, 1))
        for k in range(1, int(L / .12)):
            q = pa + (pb - pa) * k / int(L / .12)
            B.sweep(ctx.steel, np.array([[q[0], q[1], z0 + .08], [q[0], q[1], z0 + h]]), B.rect(.014, .014), cc, up=(1, 0, 0))
        ctx.ucxb(np.minimum(pa, pb) + [-.03, -.03, z0], np.maximum(pa, pb) + [.03, .03, z0 + h])


def stair(ctx, p0, d, side_out, z0, z1, width, col_trim, col_tread, rail_col, rail_style="bars", land=1.0):
    """straight cast stair (waist slab + treads) from p0 (bottom, inner edge against the wall) along d, rising to z1;
    side_out = horizontal unit vector away from the wall (open side gets the railing); landing of 'land' metres at the
    top. Returns the top landing rectangle (lo, hi) in xy and z1."""
    p0 = np.asarray(p0, float); d = np.asarray(d, float); so = np.asarray(side_out, float)
    nr = max(2, int(round((z1 - z0) / .18))); rise = (z1 - z0) / nr; run = .25; m_ = rise / run
    for k in range(nr - 1):
        a = p0 + d * run * k; b = a + d * run + so * width
        lo = np.minimum(a, b); hi = np.maximum(a, b); lo[2] = z0 + max(0, rise * k - .03); hi[2] = z0 + rise * (k + 1)
        cbox(ctx.conc, lo + [.001, .001, 0], hi - [.001, .001, 0], {"all": col_trim, "pz": col_tread})
    L = run * (nr - 1)
    P = np.array([p0 + so * width / 2 - d * .25 + [0, 0, z0 - .25 * m_], p0 + so * width / 2 + d * L + [0, 0, z0 + L * m_]])
    B.sweep(ctx.conc, P, B.rect(width, .15, 0, -.075), (*col_trim, 0), up=(0, 0, 1))
    la = p0 + d * L; lb = la + d * land + so * width
    lo = np.minimum(la, lb); hi = np.maximum(la, lb); lo[2] = z1 - .15; hi[2] = z1
    cbox(ctx.conc, lo, hi, {"all": col_trim, "pz": col_tread})
    post = la + d * (land - .125) + so * (width - .125)
    if z1 - .15 > .3:
        cbox(ctx.plaster, (post[0] - .125, post[1] - .125, 0), (post[0] + .125, post[1] + .125, z1 - .15), {"all": col_trim}, damp_z=0)
        ctx.ucxb((post[0] - .125, post[1] - .125, 0), (post[0] + .125, post[1] + .125, z1 - .15))
    # sloped railing on the open side
    xr = so * (width - .05); cc = (*rail_col, .15)
    for k in list(range(0, nr - 1, 3)) + [nr - 2]:
        q = p0 + xr + d * (run * k + run / 2); zt = z0 + rise * (k + 1)
        B.sweep(ctx.steel, np.array([[q[0], q[1], zt], [q[0], q[1], zt + .9]]), B.rect(.04, .04), cc, up=(1, 0, 0))
    for dz in (.9, .45):
        qa = p0 + xr + d * (run / 2); qb = p0 + xr + d * (run * (nr - 1.5))
        B.sweep(ctx.steel, np.array([[qa[0], qa[1], z0 + rise + dz], [qb[0], qb[1], z0 + rise * (nr - 1) + dz]]), B.rect(.04 if dz > .5 else .02, .02), cc, up=(0, 0, 1))
    railing(ctx, [la + xr + d * .05, la + xr + d * (land - .05)], z1, rail_col, "bars", posts=5)
    lo_s = np.minimum(p0, la + so * width); hi_s = np.maximum(p0, la + so * width)
    ctx.ucxb([lo_s[0], lo_s[1], z0], [hi_s[0], hi_s[1], z0 + (z1 - z0) * .5])
    return (np.minimum(la, lb)[:2], np.maximum(la, lb)[:2], z1)


# ------------------------------------------------------------------ roofs
def slab(ctx, rect, z, ov, col_edge, col_top, col_under, upstand=True, front_extra=0.0, sides=(0, 0)):
    """flat RC slab (150 mm) with drip overhang, optional 100 mm upstand, PVC spouts at the back"""
    x0, x1, y0, y1 = rect
    lo = (x0 - ov - sides[0], y0 - ov - front_extra, z); hi = (x1 + ov + sides[1], y1 + ov, z + .15)
    cbox(ctx.conc, lo, hi, {"all": col_edge, "pz": col_top, "nz": col_under}); ctx.ucxb(lo, hi)
    if upstand:
        e = .1; zt = z + .25; X0, Y0, X1, Y1 = lo[0], lo[1], hi[0], hi[1]
        for a, b in (((X0, Y0), (X1, Y0 + e)), ((X0, Y1 - e), (X1, Y1)), ((X0, Y0 + e), (X0 + e, Y1 - e)), ((X1 - e, Y0 + e), (X1, Y1 - e))):
            cbox(ctx.conc, (a[0], a[1], z + .15), (b[0], b[1], zt), {"all": col_edge, "pz": col_top})
        for xs in (X0 + .6, X1 - .6):
            B.tube_path(ctx.pvc, [[xs, Y1 - .05, z + .19], [xs, Y1 + .28, z + .17]], .037, 10, (.86, .86, .83, .2))
    return hi[2]


def corr_face(ctx, O, uax, vax, U, V, vmin=lambda u: 0.0, col=(1, 1, 1), rust=.3, sheet=.762, sag=0.0):
    """corrugated sheets on a sloped roof plane: O = eave-left corner, uax along the eave, vax up the slope (unit,
    3D), extents U × V; vmin(u) trims the lower/hip edge (hip faces). Corrugations run up the slope, 76 mm pitch,
    18 mm deep, sheets overlap one corrugation. Single-sided (Unreal: two-sided material)."""
    O = np.asarray(O, float); uax = np.asarray(uax, float); vax = np.asarray(vax, float)
    nrm = np.cross(uax, vax); nrm /= np.linalg.norm(nrm)
    ns = int(math.ceil(U / sheet))
    for k in range(ns):
        ua = k * sheet; ub = min(U, ua + sheet + .076)
        us = np.linspace(ua, ub, max(3, int((ub - ua) / .076 * 4)))
        rows = []
        for f in np.linspace(0, 1, 4):
            row = []
            for u in us:
                vm = vmin(u); v = vm + (V - vm) * f
                off = .009 * math.sin((u - ua) / .076 * 2 * math.pi) + .0015 * k - sag * math.sin(math.pi * f) ** 2
                row.append(O + uax * u + vax * v + nrm * off)
            rows.append(row)
        G = np.array(rows)
        uv = np.stack(np.broadcast_arrays(us[None, :], np.linspace(0, V, 4)[:, None]), -1)
        ctx.corr.grid(G, uv, (*col, ctx.rng.uniform(rust * .5, rust * 1.5)))


def tin_roof(ctx, rect, z, kind, pitch_deg, ov, col_sheet, col_fascia, rust, gable_col=None, t=.2, gable_mb=None, ridge=None):
    """corrugated-iron roof on timber rafters + purlins over rect, wall top at z: kind 'gable' (ridge along the long
    side, plastered gable triangles on the end walls), 'hip' (45° hips), 'lean' (one slope rising to +y).
    Collision: one convex hull of the roof volume. Returns the ridge height."""
    x0, x1, y0, y1 = rect; W, D = x1 - x0, y1 - y0; p = math.radians(pitch_deg); tp = math.tan(p)
    rcol = (1, .9, .8, .3)
    if kind == "lean":
        zl = z; O = np.array([x0 - ov, y0 - ov, zl - ov * tp]); vv = np.array([0, math.cos(p), math.sin(p)])
        corr_face(ctx, O, np.array([1., 0, 0]), vv, W + 2 * ov, (D + 2 * ov) / math.cos(p), col=col_sheet, rust=rust)
        if getattr(ctx, "nails", None) is not None:
            import detail as DT
            DT.nail_rust(ctx, O, np.array([1., 0, 0]), vv, W + 2 * ov, [(y - (y0 - ov)) / math.cos(p) for y in np.linspace(y0 - ov + .3, y1 + ov - .3, 4)], ctx.nails, col_sheet, p=getattr(ctx, "nails_p", .55))
        for y in np.linspace(y0 - ov + .3, y1 + ov - .3, 4):
            B.box(ctx.timber, ((x0 + x1) / 2, y, zl + (y - y0) * tp - .03), (W + 2 * ov, .05, .05), col=rcol)
        ctx.hull([[x, y, zl + (y - y0) * tp + dz] for x in (x0 - ov, x1 + ov) for y in (y0 - ov, y1 + ov) for dz in (-.05, .03)])
        return zl + (D + ov) * tp
    along_x = (W >= D) if ridge is None else (ridge == "x")
    Lr, Dr = (W, D) if along_x else (D, W)
    half = Dr / 2 + ov; h = (Dr / 2) * tp; zr = z + h; ze = z - ov * tp; sl = half / math.cos(p)
    def P(a, b, zz):
        return np.array([x0 + a, (y0 + y1) / 2 + b, zz]) if along_x else np.array([(x0 + x1) / 2 + b, y0 + a, zz])
    A = P(1, 0, 0) - P(0, 0, 0); Bv = P(0, 1, 0) - P(0, 0, 0); Z = np.array([0, 0, 1.0])
    U = Lr + 2 * ov
    for s in (-1, 1):                                       # the two long faces
        vax = -s * Bv * math.cos(p) + Z * math.sin(p)
        O, uax = (P(-ov, s * half, ze), A) if s < 0 else (P(Lr + ov, s * half, ze), -A)
        if kind == "hip": corr_face_trap(ctx, O, uax, vax, U, lambda u, U=U: min(sl, min(u, U - u) * sl / half), col_sheet, rust)
        else: corr_face(ctx, O, uax, vax, U, sl, col=col_sheet, rust=rust)
        if getattr(ctx, "nails", None) is not None:          # detail pass: rusty nail heads on the purlin lines
            import detail as DT
            DT.nail_rust(ctx, O, uax, vax, U, [half * f / math.cos(p) for f in np.linspace(.08, .95, 4)], ctx.nails, col_sheet, p=getattr(ctx, "nails_p", .55),
                         vmax=(lambda u, U=U: min(sl, min(u, U - u) * sl / half)) if kind == "hip" else None)
        B.sweep(ctx.paintwood, np.array([O - Z * .1, O - Z * .1 + uax * U]), B.rect(.025, .18), (*col_fascia, .2), up=(0, 0, 1))
    if kind == "hip":
        for e in (-1, 1):                                   # the two hip ends
            ax_in = A * (1 if e < 0 else -1); a_e = -ov if e < 0 else Lr + ov
            O = P(a_e, -half * (1 if e < 0 else -1), ze); uax = Bv * (1 if e < 0 else -1)
            vax = ax_in * math.cos(p) + Z * math.sin(p); U2 = 2 * half
            corr_face_trap(ctx, O, uax, vax, U2, lambda u, U2=U2: min(sl, min(u, U2 - u) * sl / half), col_sheet, rust)
            B.sweep(ctx.paintwood, np.array([O - Z * .1, O - Z * .1 + uax * U2]), B.rect(.025, .18), (*col_fascia, .2), up=(0, 0, 1))
        r0, r1 = Dr / 2, Lr - Dr / 2
        for (a0, b0), a1 in (((-ov, -half), r0), ((-ov, half), r0), ((Lr + ov, -half), r1), ((Lr + ov, half), r1)):
            B.sweep(ctx.corr, np.array([P(a0, b0, ze + .03), P(a1, 0, zr + .03)]), B.rect(.12, .03), (*col_sheet, rust), up=(0, 0, 1))
        ra, rb = r0, r1; rafters = np.arange(r0, r1 + .01, .9) if r1 > r0 else []
    else:
        ra, rb = -ov, Lr + ov; rafters = list(np.arange(t + .1, Lr - t - .05, .9)) + [-ov + .03, Lr + ov - .03]
        for a_e, th in ((0.0, t), (Lr, -t)):                # plastered gable triangles on the end walls
            tri = [(-Dr / 2, 0), (Dr / 2, 0), (0, h - .06)]
            V = [P(a_e, b, z + zz) for b, zz in tri] + [P(a_e + th, b, z + zz) for b, zz in tri]
            (gable_mb or ctx.plaster).add(V, [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]], [(b, zz) for b, zz in tri] * 2, (*(gable_col or (1, 1, 1)), .3 if gable_mb is not None else 0))
    if rb > ra:
        B.sweep(ctx.corr, np.array([P(ra, 0, zr + .04), P(rb, 0, zr + .04)]), [(-.15, -.02), (0, .03), (.15, -.02), (0, .0)], (*col_sheet, rust), up=(0, 0, 1))
    for a in rafters:
        for s in (-1, 1):
            B.sweep(ctx.timber, np.array([P(a, s * (half - .02), ze - .06), P(a, 0, zr - .06)]), B.rect(.05, .1, 0, -.05), rcol, up=(0, 0, 1))
    for s in (-1, 1):
        for f in np.linspace(.08, .95, 4):
            bb = s * half * (1 - f); zz = zr - (half * (1 - f)) * tp - .02
            a0, a1 = (-ov, Lr + ov) if kind == "gable" else (-ov + half * f, Lr + ov - half * f)
            if a1 > a0: B.sweep(ctx.timber, np.array([P(a0, bb, zz), P(a1, bb, zz)]), B.rect(.05, .05), rcol, up=(0, 0, 1))
    ctx.hull([P(a, b, ze) for a in (-ov, Lr + ov) for b in (-half, half)] + [P(ra, 0, zr + .05), P(rb, 0, zr + .05)])
    return zr


def corr_face_trap(ctx, O, uax, vax, U, vmax, col, rust):
    """corrugated face whose top edge is trimmed by vmax(u) (hip roofs)"""
    O = np.asarray(O, float); nrm = np.cross(uax, vax); nrm /= np.linalg.norm(nrm)
    sheet = .762
    for k in range(int(math.ceil(U / sheet))):
        ua = k * sheet; ub = min(U, ua + sheet + .076)
        us = np.linspace(ua, ub, max(3, int((ub - ua) / .076 * 4)))
        rows = []
        for f in np.linspace(0, 1, 4):
            rows.append([O + uax * u + vax * (vmax(u) * f) + nrm * (.009 * math.sin((u - ua) / .076 * 2 * math.pi) + .0015 * k) for u in us])
        G = np.array(rows)
        if np.ptp(G[:, :, 2]) < 1e-4: continue
        uv = np.stack(np.broadcast_arrays(us[None, :], np.linspace(0, 1, 4)[:, None]), -1)
        ctx.corr.grid(G, uv, (*col, ctx.rng.uniform(rust * .5, rust * 1.5)))


# ------------------------------------------------------------------ roof furniture
def starter(ctx, x, y, z, rng):
    """RC column stub with 4 rusty starter bars + links (waiting for the next floor)"""
    cbox(ctx.conc, (x - .125, y - .125, z), (x + .125, y + .125, z + .12), {"all": (.82, .81, .78)})
    for dx in (-.07, .07):
        for dy in (-.07, .07):
            L_ = rng.uniform(.55, .95); top = [x + dx, y + dy, z + .12 + L_]
            pts = [[x + dx, y + dy, z + .12], top]
            if rng.random() < .25: pts.append([top[0] + .12 * np.sign(dx), top[1], top[2]])          # hooked over
            elif rng.random() < .12: pts.append([top[0] + .02, top[1] + .03, top[2] + .25])              # slightly bent
            B.tube_path(ctx.rebar, pts, .006, 6, (1, 1, 1, rng.uniform(.3, .9)))
    for k in range(3):
        zz = z + .2 + k * .15
        B.tube_path(ctx.rebar, [[x - .075, y - .075, zz], [x + .075, y - .075, zz], [x + .075, y + .075, zz], [x - .075, y + .075, zz], [x - .075, y - .075, zz]], .003, 4, (1, 1, 1, .7))


def column(ctx, x, y, z0, z1, col, raw=False, bars=False, rng=None):
    mb = ctx.raw if raw else ctx.plaster
    cbox(mb, (x - .125, y - .125, z0), (x + .125, y + .125, z1), {"all": col}, damp_z=z0 if z0 < .5 else None)
    ctx.ucxb((x - .125, y - .125, z0), (x + .125, y + .125, z1))
    if bars:
        for dx in (-.07, .07):
            for dy in (-.07, .07):
                L_ = rng.uniform(.5, .9)
                B.tube_path(ctx.rebar, [[x + dx, y + dy, z1], [x + dx, y + dy, z1 + L_]], .009, 6, (1, 1, 1, .8))


def water_tank(ctx, x, y, z, col):
    cbox(ctx.conc, (x - .65, y - .65, z), (x + .65, y + .65, z + .45), {"all": (.8, .79, .76)})
    rows = []
    for zz, rr in ((0, .52), (.04, .55), (1.1, .55), (1.18, .48), (1.24, .2), (1.26, .0)):
        rows.append([[x + rr * math.cos(t), y + rr * math.sin(t), z + .45 + zz] for t in np.linspace(0, 2 * math.pi, 28, endpoint=False)])
    o = ctx.tank.grid(np.array(rows), col=(*col, 0), close_v=True); ctx.tank.cap([o + j for j in range(28)], True)
    for k in range(5):
        zz = z + .65 + k * .18
        B.tube_path(ctx.tank, [[x + .556 * math.cos(t), y + .556 * math.sin(t), zz] for t in np.linspace(0, 2 * math.pi, 29)], .012, 6, (*col, 0))
    B.tube_path(ctx.tank, [[x, y, z + 1.70], [x, y, z + 1.78]], .11, 16, (*col, 0))
    B.tube_path(ctx.pvc, [[x - .5, y, z + .55], [x - .9, y, z + .55], [x - .9, y, z - .05]], .016, 8, (.86, .86, .83, .2))
    ctx.ucxb((x - .6, y - .6, z), (x + .6, y + .6, z + 1.75))


def solar_heater(ctx, x, y, z, face=-1):
    """thermosiphon solar water heater: tilted flat-plate collector + horizontal storage tank on a galvanised frame"""
    tilt = math.radians(25)
    c0 = np.array([x, y, z + .35])
    d = np.array([0, face * math.cos(tilt), math.sin(tilt)])            # up the collector
    for a in (-.95, .95):
        B.sweep(ctx.alu, np.array([c0 + [a, 0, -.35], c0 + [a, 0, 0], c0 + [a, 0, 0] + d * 2.0, c0 + [a, 0, -.35] + np.array([0, d[1] * 2.0, 0])]),
                B.rect(.04, .04), (.75, .76, .77, .2), up=(1, 0, 0))
    q = [c0 + [-1, 0, .02], c0 + [1, 0, .02], c0 + [1, 0, .02] + d * 2, c0 + [-1, 0, .02] + d * 2]
    ctx.glass.add(q, [[0, 1, 2, 3]], [(0, 0)] * 4, (.15, .2, .3, 0))
    nrm = np.cross(q[1] - q[0], q[3] - q[0]); nrm /= np.linalg.norm(nrm)
    for a_, b_ in ((q[0], q[1]), (q[1], q[2]), (q[2], q[3]), (q[3], q[0])):
        B.sweep(ctx.alu, np.array([a_, b_]), B.rect(.05, .06), (.78, .79, .8, 0), up=tuple(nrm))
    tk = c0 + d * 2.05 + np.array([0, 0, .25])
    B.tube_path(ctx.tank, [tk + [-1.0, 0, 0], tk + [1.0, 0, 0]], .25, 18, (.85, .86, .86, 0))
    for a in (-1.0, 1.0): B.superellipsoid(ctx.tank, tk + [a, 0, 0], (.03, .25, .25), (1, 1), 14, 6, (.6, .6, .6, 0))
    ctx.ucxb(c0 + [-1.05, min(0, d[1] * 2.3) - .3, -.35], c0 + [1.05, max(0, d[1] * 2.3) + .3, 1.4])


def dish(ctx, x, y, z, ang):
    d = np.array([math.cos(ang), math.sin(ang), .35]); d /= np.linalg.norm(d)
    B.tube_path(ctx.alu, [[x, y, z], [x, y, z + .6]], .025, 8, (.7, .7, .7, .3))
    c = np.array([x, y, z + .65]) + d * .1
    rings = []
    for r, dz in ((.0, .0), (.15, .02), (.3, .07), (.38, .11)):
        side = np.cross(d, [0, 0, 1]); side /= np.linalg.norm(side); upv = np.cross(side, d)
        rings.append([c + d * dz + (side * math.cos(t) + upv * math.sin(t)) * r for t in np.linspace(0, 2 * math.pi, 18, endpoint=False)])
    ctx.alu.grid(np.array(rings), col=(.95, .95, .95, .1), close_v=True)
    B.tube_path(ctx.alu, [c + d * .1, c + d * .45], .01, 6, (.6, .6, .6, .2))


# ------------------------------------------------------------------ garden wall + gate
def garden_wall(ctx, x0, x1, y, h, col, gate_x, gate_w, gate_col, rng, returns=(), claustra=None):
    """front boundary wall (rendered blocks 150 mm) with pillars every ~2.5 m and a double steel gate; claustra = a
    random stream: then some runs get a breeze-block (claustra) band in the upper half"""
    t = .15
    def run(a, b):
        if b - a < .05: return
        if claustra is not None and h >= 1.0 and b - a > .9 and claustra.random() < .6:     # breeze-block band
            import civlib as CL
            zc0 = max(.5, h - .45); cbox(ctx.plaster, (a, y, 0), (b, y + t, .5), {"all": col}, damp_z=0, damp_amt=.4)
            cbox(ctx.plaster, (a, y, .5), (b, y + t, zc0), {"all": col}) if zc0 > .51 else None
            k_ = max(1, int((b - a - .1) / .2)); w_ = k_ * .2; a2 = (a + b) / 2 - w_ / 2
            for s0, s1 in ((a, a2), (a2 + w_, b)):
                if s1 - s0 > .005: cbox(ctx.plaster, (s0, y, zc0), (s1, y + t, h), {"all": col})
            CL.add_mbs(ctx); CL.breeze_block(ctx, np.array([(a + b) / 2, y + t / 2, zc0]), np.array([1., 0, 0]), np.array([0, -1., 0]), w_, h - zc0, t=t, col=col)
            ctx.ucxb((a, y, 0), (b, y + t, h))
        else:
            for za, zb in ((0, .5), (.5, h)):
                cbox(ctx.plaster, (a, y, za), (b, y + t, zb), {"all": col}, damp_z=0, damp_amt=.4)
        cbox(ctx.conc, (a, y - .03, h), (b, y + t + .03, h + .05), {"all": (.92, .91, .88)})
        ctx.ucxb((a, y, 0), (b, y + t, h + .05))
    def pil(x, s=.3, hh=None):
        hh = hh or h + .15
        cbox(ctx.plaster, (x - s / 2, y + t / 2 - s / 2, 0), (x + s / 2, y + t / 2 + s / 2, hh), {"all": col}, damp_z=0, damp_amt=.4)
        cbox(ctx.conc, (x - s / 2 - .04, y + t / 2 - s / 2 - .04, hh), (x + s / 2 + .04, y + t / 2 + s / 2 + .04, hh + .07), {"all": (.92, .91, .88)})
        ctx.ucxb((x - s / 2, y + t / 2 - s / 2, 0), (x + s / 2, y + t / 2 + s / 2, hh + .07))
    ga, gb = gate_x - gate_w / 2, gate_x + gate_w / 2
    for a, b in ((x0, ga - .2), (gb + .2, x1)):
        if b - a < .3: continue
        n_ = max(1, int(round((b - a) / 2.5))); xs = np.linspace(a, b, n_ + 1)
        for xa, xb in zip(xs[:-1], xs[1:]): run(xa + .15, xb - .15)
        for xx in xs: pil(xx, .3 if (abs(xx - (ga - .2)) > .01 and abs(xx - (gb + .2)) > .01) else .4, h + (.35 if abs(xx - ga + .2) < .01 or abs(xx - gb - .2) < .01 else .15))
    # gate leaves: one closed, one open
    cc = (*gate_col, .2)
    for side, hinge_x, open_deg in ((1, ga, 0), (-1, gb, rng.uniform(30, 80))):
        a_ = math.radians(open_deg); d = np.array([side * math.cos(a_), -math.sin(a_), 0]); w = gate_w / 2 - .02
        h0 = np.array([hinge_x, y + t / 2, .05])
        def P(u, v): return h0 + d * u + np.array([0, 0, v])
        for (ua, va), (ub, vb) in (((0, 0), (w, 0)), ((0, h), (w, h)), ((0, 0), (0, h)), ((w, 0), (w, h)), ((0, h * .5), (w, h * .5))):
            B.sweep(ctx.steel, np.array([P(ua, va), P(ub, vb)]), B.rect(.04, .04), cc, up=(0, 0, 1) if va == vb else tuple(d))
        for u in np.arange(.11, w - .05, .11):
            B.sweep(ctx.steel, np.array([P(u, .02), P(u, h + .08)]), B.rect(.016, .016), cc, up=tuple(d))
        for v in (.25, h - .2):                              # pin hinges on the pillar side + straps on the leaf
            B.tube_path(ctx.steel, [h0 + [0, 0, v - .07], h0 + [0, 0, v + .07]], .02, 8, (*gate_col, .5))
            B.sweep(ctx.steel, np.array([P(-.04, v), P(.25, v)]), B.rect(.045, .008), (*gate_col, .5), up=(0, 0, 1))
        if open_deg == 0:                                    # drop bolt into the drive at the free end of the closed leaf
            B.tube_path(ctx.steel, [P(w - .06, .45), P(w - .06, -.04)], .009, 6, (*gate_col, .4))
            B.box(ctx.steel, P(w - .06, .5), (.05, .05, .1), col=(*gate_col, .4))
    for (xa, ya), (xb, yb) in returns:
        for za, zb in ((0, .5), (.5, h)):
            cbox(ctx.plaster, (min(xa, xb), min(ya, yb), za), (max(xa, xb) + (t if xa == xb else 0), max(ya, yb), zb), {"all": col}, damp_z=0, damp_amt=.4)
        ctx.ucxb((min(xa, xb), min(ya, yb), 0), (max(xa, xb) + (t if xa == xb else 0), max(ya, yb), h))
