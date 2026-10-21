"""civplan.py – plan helper for the W2 buildings: rooms + openings in world coordinates, assigned automatically to
the rooms (interior.py schema) and to the exterior facades (hlib.wall ops), with the standard fittings:
louvre windows + grilles + drip sills + painted surrounds + streaks, timber shutters (old buildings), breeze-block
vents, single / double doors with steel frames, security gates, worn threshold steps, partition hatches with a
timber ledge + sliding glass, interior doors with linings, loot sockets.

  P = Plan(ctx, rng, FL=.45, WT=.2)
  P.room("hall", "hall", (x0, x1, y0, y1), h=4.2)                  # rect = inner faces, h = clear height
  P.op(("y", -6.0), a, b, z0, z1, "window", ext=True, fit="louvre") # line ("y", c) = wall along x at y = c
  P.assign()                                                       # openings -> rooms
  P.walls(rect, ("front", "back", "left"), z_top, col_ext, col_int, mb=ctx.plaster)
  P.part(p0, p1, z_top, col_l, col_r)                              # partition with the openings on its line
  P.fit_exterior(blocks, ...); P.fit_interior(); P.loot(room, pts); P.write(path, extra)
"""
import math, os
import numpy as np
import bpy
import bldlib as B
from bldlib import srgb
import hlib as H
from hlib import cbox
import interior as IN
import civlib as C


class Plan:
    def __init__(self, ctx, rng, FL=.45, WT=.2, bounds=None):
        self.ctx, self.rng, self.FL, self.WT = ctx, rng, FL, WT
        self.rooms, self.ops, self.R, self.LOOT = [], [], {}, []

    def room(self, id_, typ, rect, h, z=None, **kw):
        r = {"id": id_, "type": typ, "storey": kw.pop("storey", 0), "rect": rect, "z": (self.FL + .012) if z is None else z,
             "h": h, "openings": [], **kw}
        self.rooms.append(r); self.R[id_] = r; return r

    def op(self, line, a, b, z0, z1, kind, ext=False, fit=None, **kw):
        o = {"line": line, "a": a, "b": b, "z0": z0, "z1": z1, "kind": kind, "ext": ext, "fit": fit, **kw}
        self.ops.append(o); return o

    def on(self, line, lo, hi):
        return [o for o in self.ops if o["line"] == line and o["b"] > lo and o["a"] < hi]

    def assign(self, tol=.3):
        for r in self.rooms:
            x0, x1, y0, y1 = r["rect"]
            for o in self.ops:
                ax, c = o["line"]
                for side, (lax, lc, lo_, hi_) in {"s": ("y", y0, x0, x1), "n": ("y", y1, x0, x1), "w": ("x", x0, y0, y1), "e": ("x", x1, y0, y1)}.items():
                    if ax == lax and abs(c - lc) <= tol and o["a"] < hi_ - .05 and o["b"] > lo_ + .05 and (o.get("z_room") is None or abs(o["z_room"] - r["z"]) < .5):
                        kind = {"vent": "embrasure", "bars": "opening"}.get(o["kind"], o["kind"])
                        r["openings"].append({"side": side, "a": round(max(o["a"], lo_), 3), "b": round(min(o["b"], hi_), 3), "z0": o["z0"], "z1": o["z1"],
                                              "kind": kind, "to": o.get("to") or ("outside" if o["ext"] else "?")})
        opp = {"s": "n", "n": "s", "w": "e", "e": "w"}
        for r in self.rooms:
            for o in r["openings"]:
                if o["to"] != "?": continue
                for r2 in self.rooms:
                    if r2 is r: continue
                    if any(o2["kind"] == o["kind"] and abs(o2["a"] - o["a"]) < .06 and abs(o2["b"] - o["b"]) < .06 and o2["side"] == opp[o["side"]] for o2 in r2["openings"]):
                        o["to"] = r2["id"]
                if o["to"] == "?": o["to"] = "corridor"

    # ---------------------------------------------------------------- shell
    def facade_ops(self, rect, key, line=None):
        x0, x1, y0, y1 = rect
        line = line or {"front": ("y", y0), "back": ("y", y1), "left": ("x", x0), "right": ("x", x1)}[key]
        lo_, hi_ = (x0, x1) if key in ("front", "back") else (y0, y1)
        out = []
        for o in self.on(line, lo_, hi_):
            if not o["ext"]: continue
            if key == "front": u0, u1 = o["a"] - x0, o["b"] - x0
            elif key == "back": u0, u1 = x1 - o["b"], x1 - o["a"]
            elif key == "right": u0, u1 = o["a"] - y0, o["b"] - y0
            else: u0, u1 = y1 - o["b"], y1 - o["a"]
            zb = o.get("zbase", self.FL)
            out.append((u0, u1, zb + o["z0"], zb + o["z1"], o["kind"], o))
        return out

    def walls(self, rect, keys, z_top, c_ext, c_int, mb=None, z0=0.0, damp=True, t=None):
        t = t or self.WT
        for key in keys:
            H.wall(self.ctx, rect, key, z0, z_top, t, [(o[0], o[1], o[2] - z0, o[3] - z0, o[4]) for o in self.facade_ops(rect, key)], c_ext, c_int,
                   mb=mb, damp_z=z0 if damp else None, damp_amt=.4)

    def part(self, p0, p1, z_top, col_l, col_r, t=None, mb=None, z0=None):
        line = ("y", p0[1]) if abs(p0[1] - p1[1]) < 1e-6 else ("x", p0[0])
        ax = 0 if line[0] == "y" else 1; lo_, hi_ = min(p0[ax], p1[ax]), max(p0[ax], p1[ax])
        z0 = self.FL - .02 if z0 is None else z0
        ops = [(o["a"] - lo_, o["b"] - lo_, o["z0"] + (self.FL - z0) * 0 + (o.get("zbase", self.FL) - z0), o["z1"] + (o.get("zbase", self.FL) - z0)) for o in self.on(line, lo_, hi_) if not o["ext"] and o["kind"] != "bars"]
        if p0[ax] > p1[ax]: ops = [(hi_ - lo_ - b, hi_ - lo_ - a, v0, v1) for a, b, v0, v1 in ops]
        C.pwall(self.ctx, p0, p1, z0, z_top, t or self.WT, ops, col_l, col_r, mb=mb)

    def floors(self, col=(1, 1, 1), mb=None, skip=()):
        for r in self.rooms:
            if r["id"] in skip: continue
            x0, x1, y0, y1 = r["rect"]
            cbox(mb or self.ctx.tile, (x0, y0, r["z"] - .032), (x1, y1, r["z"]), {"all": col})

    # ---------------------------------------------------------------- exterior fittings
    def fit_exterior(self, blocks, c_ext, c_trim, c_grille, c_door, c_plinth=None, c_old=None, shutters=None, plinth_top=None, wear=True):
        """blocks = [(rect, keys, z_top)]. Windows: fit 'louvre' (alu louvres), 'tall', 'small', 'shutter' (timber
        persiennes + casement), 'sash' (old: shutters closed half), 'case' (casement + grille, no persiennes). Doors: 'single' | 'double' | 'steel'."""
        ctx, rng, WT = self.ctx, self.rng, self.WT
        for rect, keys, top in blocks:
            for key in keys:
                org, u, n, L = H.facade(rect, key)
                fops = self.facade_ops(rect, key)
                if wear:
                    if c_plinth is not None:
                        dr = [o for o in fops if o[4] == "door"]; cuts = [0.0] + [v for o in dr for v in (o[0], o[1])] + [L]
                        for ua, ub in zip(cuts[0::2], cuts[1::2]):
                            if ub - ua > .02: C.wbox(ctx.plaster, org, u, n, ua, ub, 0, plinth_top or self.FL + .15, 0, .006, c_plinth, .5)
                    if c_old is not None: C.paint_chips(ctx, org, u, n, L, self.FL + .3, top - .3, c_old, rng, rng.randint(4, 9))
                    C.crack_line(ctx, org, u, n, L, top - .25, rng)
                    for k in range(rng.randint(3, 6)):
                        s = rng.uniform(.4, L - .4)
                        if any(o[0] - .2 < s < o[1] + .2 for o in fops): continue
                        C.streak(ctx, org + u * s + [0, 0, top - .02], u, n, rng.uniform(.3, .8), rng.uniform(.6, 1.6), c_ext, rng)
                for u0, u1, v0, v1, kind, oo in fops:
                    w, h = u1 - u0, v1 - v0
                    t_ = oo.get("t", WT)
                    c_in = org + u * (u0 + u1) / 2 - n * t_ / 2 + [0, 0, v0]; c_out = org + u * (u0 + u1) / 2 + [0, 0, v0]
                    if kind == "window":
                        fit = oo["fit"] or "louvre"
                        if fit in ("shutter", "sash", "case", "hatch"):
                            # glazed casement pair in the reveal + louvred timber persiennes on the outer face;
                            # hatch = serving window: one closed leaf behind a half grille, the other half open
                            for s_ in ((-1,) if fit == "hatch" else (-1, 1)):
                                hc = c_in + u * s_ * w / 2
                                for (a_, b_) in (((0, 0), (w / 2, 0)), ((0, h), (w / 2, h)), ((0, 0), (0, h)), ((w / 2, 0), (w / 2, h)), ((0, h * .5), (w / 2, h * .5))):
                                    pa = hc - u * s_ * a_[0] + [0, 0, a_[1]]; pb = hc - u * s_ * b_[0] + [0, 0, b_[1]]
                                    B.sweep(ctx.paintwood, np.array([pa, pb]), B.rect(.05, .05), (*c_trim, .1), up=tuple(n))
                                q = [hc - u * s_ * .03 + [0, 0, .03], hc - u * s_ * (w / 2 - .03) + [0, 0, .03], hc - u * s_ * (w / 2 - .03) + [0, 0, h - .03], hc - u * s_ * .03 + [0, 0, h - .03]]
                                ctx.glass.add(q, [[0, 1, 2, 3], [3, 2, 1, 0]], [(0, 0)] * 4, (.7, .8, .8, 0))
                            if fit not in ("case", "hatch"): H.shutters(ctx, c_out, u, w, h, n, shutters or srgb("#2f6b45"), open_=True)
                            if fit == "hatch": H.grille(ctx, c_out + u * w / 4, u, w / 2, h, n, c_grille, 0)
                            elif oo.get("grille", True): H.grille(ctx, c_out, u, w, h, n, c_grille, 0)
                        elif fit == "arch":
                            pass                                          # glazing by the caller (coloured glass + bars)
                        else:
                            H.louvre(ctx, c_in, u, w, h, n)
                            if oo.get("grille", True): H.grille(ctx, c_out, u, w, h, n, c_grille, 2 if fit == "tall" else 0)
                        C.sill_drip(ctx, c_out, u, n, w, c_trim)
                        if oo.get("surround", fit != "arch"):
                            for (a_, b_) in (((-w / 2 - .1, h), (w / 2 + .1, h + .1)), ((-w / 2 - .1, 0), (-w / 2, h)), ((w / 2, 0), (w / 2 + .1, h))):
                                lo = c_out + u * a_[0] + [0, 0, a_[1]]; hi = c_out + u * b_[0] + [0, 0, b_[1]] + n * .012
                                cbox(oo.get("surround_mb") or ctx.plaster, np.minimum(lo, hi), np.maximum(lo, hi), {"all": c_trim})
                        if wear: C.streak(ctx, c_out + n * .012 - [0, 0, .08], u, n, w * .8, rng.uniform(.4, .9), c_ext, rng)
                        cbox(ctx.tile, np.minimum(c_in - u * w / 2 - n * t_ / 2, c_in + u * w / 2 + n * .1) - [0, 0, .01], np.maximum(c_in - u * w / 2 - n * t_ / 2, c_in + u * w / 2 + n * .1), {"all": (.9, .9, .88)})
                    elif kind == "bars":                                     # cell window: bars set in the reveal, no glass
                        for k in range(1, int(w / .11)):
                            q = c_in + u * (-w / 2 + k * w / int(w / .11))
                            B.tube_path(ctx.steel, [q, q + [0, 0, h]], .011, 6, (*c_grille, .3))
                        for z_ in (.02, h - .02): C.wbox(ctx.steel, c_in, u, n, -w / 2, w / 2, z_ - .02, z_ + .02, -.04, .04, c_grille)
                        C.sill_drip(ctx, c_out, u, n, w, c_trim)
                    elif kind == "vent":
                        C.breeze_block(ctx, org + u * (u0 + u1) / 2 - n * t_ / 2 + [0, 0, v0], u, n, w, h, t_, c_ext)
                    elif kind == "door":
                        fit = oo["fit"] or "single"
                        if fit == "double":
                            for s_, hu in ((1, u0 + .02), (-1, u1 - .02)):
                                H.door_leaf(ctx, org + u * hu - n * t_, u * s_, -n, c_door, open_deg=oo.get("open", rng.choice([10, 80, 95])), w=w / 2 - .03, h=oo.get("leaf_h", h - .03), glazed=oo.get("glazed", True))
                            if oo.get("gate", True):
                                for s_, hu in ((1, u0 + .05), (-1, u1 - .05)):
                                    for k in range(5):
                                        q = org + u * (hu + s_ * k * .045) + n * (.06 + (.03 if k % 2 else 0))
                                        B.sweep(ctx.steel, np.array([q + [0, 0, .02], q + [0, 0, h - .02]]), B.rect(.016, .03), (*c_grille, .2), up=tuple(n))
                                cbox(ctx.steel, org + u * u0 + n * .03 + [0, 0, v1], org + u * u1 + n * .1 + [0, 0, v1 + .06], {"all": c_grille})
                        else:
                            H.door_leaf(ctx, org + u * (u0 + .02) - n * t_, u, -n, c_door if fit != "steel" else (.45, .48, .5), open_deg=oo.get("open", rng.choice([0, 30, 85])), w=w - .04, h=h - .03)
                            if oo.get("gate", rng.random() < .6): H.grille_door(ctx, org + u * (u1 + .02) + n * .03, -u, n, c_grille, 172, w=w - .04)
                        fc = oo.get("frame_col", (.55, .58, .6))
                        for s0, s1 in ((u0 - .06, u0), (u1, u1 + .06)):
                            lo = org + u * s0 + n * .01 + [0, 0, v0]; hi = org + u * s1 - n * (t_ + .01) + [0, 0, v1 + .06]
                            cbox(ctx.steel, np.minimum(lo, hi), np.maximum(lo, hi), {"all": fc})
                        lo = org + u * (u0 - .06) + n * .01 + [0, 0, v1]; hi = org + u * (u1 + .06) - n * (t_ + .01) + [0, 0, v1 + .06]
                        cbox(ctx.steel, np.minimum(lo, hi), np.maximum(lo, hi), {"all": fc})
                        st = oo.get("steps", "auto")
                        if st and v0 > .1 and st != "none":
                            q0 = org + u * (u0 - .3); q1 = org + u * (u1 + .3) + n * .45 + [0, 0, v0]
                            nst = max(1, int(round(v0 / .16)))
                            for k in range(nst):
                                a_ = q0 + n * (k * .3); b_ = q1 + n * (k * .3) - [0, 0, v0 * k / nst]
                                C.worn_step(ctx, np.minimum(a_, b_), np.maximum(a_, b_), (.72, .71, .68), rng)
                            self.ctx.ucxb(np.minimum(q0, q1 + n * .3 * (nst - 1)), np.maximum(q0, q1 + n * .3 * (nst - 1)) - [0, 0, v0 * .3])

    # ---------------------------------------------------------------- interior fittings
    def fit_interior(self, c_door, frame_col=(.92, .9, .85)):
        ctx, rng = self.ctx, self.rng
        for o in self.ops:
            if o["ext"]: continue
            ax, c = o["line"]; a_, b_ = o["a"], o["b"]; zb = o.get("zbase", self.FL); z0, z1 = zb + o["z0"], zb + o["z1"]
            if o["kind"] == "counter":
                if ax == "y":
                    cbox(ctx.timber, (a_ - .05, c - .3, z0 - .04), (b_ + .05, c + .3, z0), {"all": (.7, .55, .38)}); ctx.ucxb((a_ - .05, c - .3, z0 - .04), (b_ + .05, c + .3, z0))
                    m = (a_ + b_) / 2
                    ctx.glass.add([(a_, c + .05, z0 + .02), (m + .05, c + .05, z0 + .02), (m + .05, c + .05, z1 - .02), (a_, c + .05, z1 - .02)], [[0, 1, 2, 3], [3, 2, 1, 0]], [(0, 0)] * 4, (.75, .85, .85, 0))
                    cbox(ctx.alu, (a_, c + .03, z0), (b_, c + .07, z0 + .02), {"all": (.78, .79, .8)}); cbox(ctx.alu, (a_, c + .03, z1 - .02), (b_, c + .07, z1), {"all": (.78, .79, .8)})
                else:
                    cbox(ctx.timber, (c - .3, a_ - .05, z0 - .04), (c + .3, b_ + .05, z0), {"all": (.7, .55, .38)}); ctx.ucxb((c - .3, a_ - .05, z0 - .04), (c + .3, b_ + .05, z0))
                    m = (a_ + b_) / 2
                    ctx.glass.add([(c + .05, a_, z0 + .02), (c + .05, m + .05, z0 + .02), (c + .05, m + .05, z1 - .02), (c + .05, a_, z1 - .02)], [[0, 1, 2, 3], [3, 2, 1, 0]], [(0, 0)] * 4, (.75, .85, .85, 0))
                    cbox(ctx.alu, (c + .03, a_, z0), (c + .07, b_, z0 + .02), {"all": (.78, .79, .8)}); cbox(ctx.alu, (c + .03, a_, z1 - .02), (c + .07, b_, z1), {"all": (.78, .79, .8)})
            elif o["kind"] == "idoor" and o["fit"] in ("door", "door2"):
                t = o.get("t", self.WT); side = o.get("swing", 1)                # swing +1 = into +x / +y
                if ax == "y":
                    u = np.array([1., 0, 0]); n_in = np.array([0, side * 1., 0]); hinge = np.array([a_ + .02, c + side * t / 2, zb])
                else:
                    u = np.array([0, 1., 0]); n_in = np.array([side * 1., 0, 0]); hinge = np.array([c + side * t / 2, a_ + .02, zb])
                if o["fit"] == "door":
                    C.idoor(ctx, hinge, u, n_in, o.get("col", c_door), open_deg=o.get("open", rng.choice([15, 60, 90])), w=b_ - a_ - .04, h=o["z1"] - .04, frame_col=frame_col, t=t)
                else:
                    wl = (b_ - a_) / 2 - .03
                    H.door_leaf(ctx, hinge, u, n_in, o.get("col", c_door), open_deg=90, w=wl, h=o["z1"] - .04)
                    H.door_leaf(ctx, hinge + u * (b_ - a_ - .04), -u, n_in, o.get("col", c_door), open_deg=85, w=wl, h=o["z1"] - .04)

    def loot(self, r, pts):
        if isinstance(r, str): r = self.R[r]
        for k, p in enumerate(pts):
            s = bpy.data.objects.new(f"SOCKET_Loot_{r['id']}_{k}", None); bpy.context.scene.collection.objects.link(s); s.location = tuple(p)
            self.LOOT.append({"name": s.name, "room": r["id"], "loc": [round(float(v), 3) for v in p]})

    def lights(self, r, kind):
        if isinstance(r, str): r = self.R[r]
        x0, x1, y0, y1 = r["rect"]; z = r["z"] + r["h"]
        if kind == "fan":
            nx = max(1, int((x1 - x0) / 3.8)); ny = max(1, int((y1 - y0) / 3.8))
            for i in range(nx):
                for j in range(ny): C.ceiling_fan(self.ctx, (x0 + (i + .5) * (x1 - x0) / nx, y0 + (j + .5) * (y1 - y0) / ny, z), self.rng)
        nx = max(1, int((x1 - x0) / 3.0)); ny = max(1, int((y1 - y0) / 3.0))
        for i in range(nx):
            for j in range(ny):
                off = .9 if kind == "fan" else 0
                C.tube_light(self.ctx, (x0 + (i + .5) * (x1 - x0) / nx + off * (1 if (i + j) % 2 else -1) * .5, y0 + (j + .5) * (y1 - y0) / ny + off, z))

    def dado(self, r, col, h=1.2, mb=None):
        if isinstance(r, str): r = self.R[r]
        for side in "snwe":
            for a_, b_ in IN.free_spans(r, side, 0, h, .02):
                IN.wall_box(mb or self.ctx.plaster, r, side, a_, b_, .1, h, 0, .002, col)
                IN.wall_box(self.ctx.paintwood, r, side, a_, b_, h, h + .03, 0, .012, tuple(np.array(col) * .8))

    def write(self, path, extra):
        IN.write_rooms(path, self.rooms, {**extra, "loot_sockets": self.LOOT})
