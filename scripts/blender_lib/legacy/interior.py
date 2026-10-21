"""interior.py – built-in interior finish + rooms.json for every Session G building (FREIGABE "LIVED-IN LOCATIONS").

A room is a dict:
  {"id": "s0_r1", "type": "living|kitchen|bedroom|bathroom|shop|store|office|workshop|hall|salon|dining|watch",
   "storey": 0, "rect": (x0, x1, y0, y1) = inner wall faces (m), "z": floor level, "h": clear height,
   "openings": [{"side": "s|n|w|e", "a": .., "b": .. (world coord along the side), "z0": .., "z1": .. (above floor),
                 "kind": "door|idoor|window|counter|opening", "to": "<room id>|outside"}],
   "finish": True}
Sides: s = wall at y0 (room interior towards +y), n = y1, w = x0, e = x1.

finish(rooms, M, rng) adds per room (M = mesh builders: plaster, tile, conc, steel, alu, glass, timber, paintwood,
pvc, ceramic, dark – any missing key falls back to plaster/pvc):
  skirting · door architraves (both faces) · inner window sills + frames · curtain rods · light switch beside each door +
  sockets, all on surface conduit (PVC) running up to the ceiling · ceiling fan (living/bedroom/salon) or a lamp ·
  kitchen: masonry counter with tiled top, steel sink + tap, splashback tiles, shelf · bathroom: WC + cistern, pedestal
  basin + mirror, shower corner (tray, mixer + head, curtain rail), electric water heater, wall tiles to 1.5 m ·
  shop: counter + wall shelving · fuse/meter board at the entrance · wear: scuffs, patched plaster, damp stains,
  chipped floor tiles, loose cable clips.
write_rooms(path, rooms, extra) writes rooms.json (+ cover-free zones 1.0 m deep in front of every opening).
"""
import json, math
import numpy as np
import bldlib as B

SIDES = {"s": (np.array([1., 0, 0]), np.array([0, 1., 0])), "n": (np.array([1., 0, 0]), np.array([0, -1., 0])),
         "w": (np.array([0, 1., 0]), np.array([1., 0, 0])), "e": (np.array([0, 1., 0]), np.array([-1., 0, 0]))}
C_WOOD = (.55, .38, .24); C_WHITE = (.93, .93, .9); C_TILE_W = (.9, .92, .93); C_STEELC = (.7, .72, .74)


def _mb(M, k, fb="plaster"): return M.get(k) or M.get(fb) or M["plaster"]


def box(mb, lo, hi, col, A=0.0):
    lo, hi = np.minimum(lo, hi), np.maximum(lo, hi); c = (lo + hi) / 2; s = hi - lo
    if np.any(s < 1e-4): return
    B.box(mb, c, s, col=(*col, A))


def side_geom(r, side):
    """(origin point at the side start, along-vector, inward normal, length, start coord)"""
    x0, x1, y0, y1 = r["rect"]; u, n = SIDES[side]
    if side == "s": o = np.array([x0, y0, r["z"]]); a0, L = x0, x1 - x0
    elif side == "n": o = np.array([x0, y1, r["z"]]); a0, L = x0, x1 - x0
    elif side == "w": o = np.array([x0, y0, r["z"]]); a0, L = y0, y1 - y0
    else: o = np.array([x1, y0, r["z"]]); a0, L = y0, y1 - y0
    return o, u, n, L, a0


def P(r, side, s, z, d=0.0):
    """point on a room side: s = world coord along the side, z above floor, d inward offset"""
    o, u, n, L, a0 = side_geom(r, side)
    return o + u * (s - a0) + n * d + np.array([0, 0, z])


def side_ops(r, side): return [o for o in r["openings"] if o["side"] == side]


def free_spans(r, side, zlo=0.0, zhi=2.2, margin=.12):
    """[(a, b)] stretches of a side not blocked by openings in the band zlo..zhi"""
    o, u, n, L, a0 = side_geom(r, side)
    cuts = [(op["a"] - margin, op["b"] + margin) for op in side_ops(r, side) if op["z0"] < zhi and op["z1"] > zlo]
    spans, cur = [], a0 + .02
    for a, b in sorted(cuts):
        if a > cur + .05: spans.append((cur, min(a, a0 + L - .02)))
        cur = max(cur, b)
    if a0 + L - .02 > cur + .05: spans.append((cur, a0 + L - .02))
    return [(a, b) for a, b in spans if b - a > .05]


def wall_box(mb, r, side, a, b, z0, z1, d0, d1, col, A=0.0):
    box(mb, P(r, side, a, z0, d0), P(r, side, b, z1, d1), col, A)


# ------------------------------------------------------------------ elements
def skirting(r, M, col):
    for side in "snwe":
        for a, b in free_spans(r, side, 0.0, .12, 0.0):
            wall_box(_mb(M, "paintwood"), r, side, a, b, 0, .1, 0, .014, col)


def architraves(r, M, col):
    for op in r["openings"]:
        side = op["side"]
        if op["kind"] in ("door", "idoor", "opening"):
            w = .07
            for s0, s1 in ((op["a"] - w, op["a"]), (op["b"], op["b"] + w)):
                wall_box(_mb(M, "paintwood"), r, side, s0, s1, 0, op["z1"] + w, -.002, .016, col)
            wall_box(_mb(M, "paintwood"), r, side, op["a"] - w, op["b"] + w, op["z1"], op["z1"] + w, -.002, .016, col)
        elif op["kind"] == "window":
            wall_box(_mb(M, "paintwood"), r, side, op["a"] - .05, op["b"] + .05, op["z0"] - .03, op["z0"], -.03, .06, col)       # inner sill
            for s0, s1 in ((op["a"] - .05, op["a"]), (op["b"], op["b"] + .05)):
                wall_box(_mb(M, "paintwood"), r, side, s0, s1, op["z0"], op["z1"] + .05, -.002, .014, col)
            wall_box(_mb(M, "paintwood"), r, side, op["a"] - .05, op["b"] + .05, op["z1"], op["z1"] + .05, -.002, .014, col)


def curtain_rod(r, M, op, rng):
    op["rod"] = True
    side = op["side"]; z = op["z1"] + .12
    a, b = op["a"] - .18, op["b"] + .18
    B.tube_path(_mb(M, "steel"), [P(r, side, a, z, .09), P(r, side, b, z, .09)], .01, 6, (*rng.choice([C_WOOD, (.75, .75, .72), (.2, .2, .2)]), .1))
    for s in (a + .05, b - .05):
        B.tube_path(_mb(M, "steel"), [P(r, side, s, z, .0), P(r, side, s, z, .09)], .006, 4, (.6, .6, .6, .1))


def conduit(r, M, side, s, z_from, h):
    """surface PVC conduit from a fitting straight up to the ceiling, with saddle clips"""
    p0, p1 = P(r, side, s, z_from, .018), P(r, side, s, h - .02, .018)
    B.tube_path(_mb(M, "pvc"), [p0, p1], .01, 6, (*C_WHITE, .15))
    for z in np.arange(z_from + .4, h - .1, .6):
        wall_box(_mb(M, "pvc"), r, side, s - .015, s + .015, z, z + .02, 0, .03, C_WHITE)


def switch(r, M, side, s, z, kind="switch"):
    w, hgt = (.08, .08) if kind == "switch" else (.08, .08)
    wall_box(_mb(M, "pvc"), r, side, s - w / 2, s + w / 2, z - hgt / 2, z + hgt / 2, 0, .035, C_WHITE)
    if kind == "socket":
        for ds in (-.012, .012): wall_box(_mb(M, "dark", "steel"), r, side, s + ds - .003, s + ds + .003, z - .008, z + .008, .035, .037, (.05, .05, .05))
    else:
        wall_box(_mb(M, "pvc"), r, side, s - .012, s + .012, z - .02, z + .02, .035, .045, (.95, .95, .93))


def lights(r, M, rng, fan):
    x0, x1, y0, y1 = r["rect"]; c = np.array([(x0 + x1) / 2, (y0 + y1) / 2, r["z"] + r["h"]])
    st = _mb(M, "steel")
    dr = max(.0, r["h"] - 3.1)                           # high ceilings: longer downrod / cord, fittings end up at ~2.7 m
    r["ceiling"] = "fan" if fan else ("batten" if r["type"] in ("kitchen", "shop", "store", "workshop", "office") and r["h"] <= 3.3 else "lamp")
    if fan:                                              # ceiling fan: canopy, downrod, motor, 3 blades
        B.tube_path(st, [c, c - [0, 0, .32 + dr]], .012, 6, (*C_WHITE, .1))
        B.superellipsoid(st, c - [0, 0, .02], (.07, .07, .03), (1, 1), 10, 4, (*C_WHITE, .1))
        c = c - [0, 0, dr]
        B.superellipsoid(st, c - [0, 0, .38], (.11, .11, .07), (1, .7), 14, 6, (*C_WHITE, .1))
        a0 = rng.uniform(0, 2); bcol = rng.choice([C_WHITE, C_WOOD])
        for k in range(3):
            t = a0 + 2 * math.pi * k / 3; d = np.array([math.cos(t), math.sin(t), 0]); s = np.array([-d[1], d[0], 0])
            p = c - [0, 0, .4] + d * .12; q = c - [0, 0, .41] + d * .68
            _mb(M, "paintwood").add([p - s * .05, p + s * .05, q + s * .065, q - s * .065], [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*bcol, .1))
            _mb(M, "paintwood").add([q - s * .065, q + s * .065, p + s * .05, p - s * .05], [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*bcol, .1))
    elif r["type"] in ("kitchen", "shop", "store", "workshop", "office") and r["h"] <= 3.3:     # fluorescent tube batten
        box(st, c + [-.62, -.04, -.06], c + [.62, .04, 0], C_WHITE, .1)
        B.tube_path(_mb(M, "ceramic", "pvc"), [c + [-.6, 0, -.075], c + [.6, 0, -.075]], .016, 8, (1, 1, .97, 0))
    else:                                                # lamp holder + bulb (+ simple shade)
        B.tube_path(_mb(M, "pvc"), [c, c - [0, 0, .25 + dr]], .006, 4, (*C_WHITE, .1))
        c = c - [0, 0, dr]
        B.superellipsoid(_mb(M, "ceramic", "pvc"), c - [0, 0, .3], (.03, .03, .045), (1, 1), 8, 6, (1, 1, .95, 0))
        if rng.random() < .6:
            prof = [(.04, -.24), (.16, -.33), (.17, -.34)]
            rings = [[c + [rr * math.cos(t), rr * math.sin(t), z] for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)] for rr, z in prof]
            _mb(M, "pvc").grid(np.array(rings), col=(*rng.choice([C_WHITE, (.85, .75, .5), (.6, .7, .8)]), .1), close_v=True)


def longest_free(r, sides, zhi=1.0):
    best = None
    for side in sides:
        for a, b in free_spans(r, side, 0, zhi):
            if best is None or b - a > best[2] - best[1]: best = (side, a, b)
    return best


def kitchen(r, M, rng, collide):
    sp = longest_free(r, "snwe", 1.6)
    if not sp: return
    side, a, b = sp; L = min(b - a, rng.choice([2.0, 2.4, 2.8])); a = a + .05; b = a + L
    base, tile = _mb(M, "plaster"), _mb(M, "tile", "conc")
    wall_box(base, r, side, a, b, 0, .86, 0, .6, (.9, .9, .86), .2)                              # masonry base
    for k, s0 in enumerate(np.arange(a + .05, b - .5, .62)):                                  # recess shelves behind curtains / doors
        wall_box(_mb(M, "paintwood"), r, side, s0, s0 + .55, .1, .76, .6, .615, (*np.array(rng.choice([(.45, .6, .7), (.75, .55, .35), (.9, .9, .88)])),))
    wall_box(tile, r, side, a - .02, b + .02, .86, .9, 0, .63, rng.choice([C_TILE_W, (.75, .85, .8), (.85, .8, .7)]))          # tiled top
    wall_box(tile, r, side, a, b, .9, 1.5, 0, .006, C_TILE_W)                                   # splashback
    sc = a + min(.7, L * .35)                                                                  # steel sink + tap
    wall_box(_mb(M, "alu", "steel"), r, side, sc - .3, sc + .3, .88, .905, .08, .55, C_STEELC)
    wall_box(_mb(M, "dark", "steel"), r, side, sc - .23, sc + .23, .905, .906, .13, .5, (.25, .26, .27))
    t0 = P(r, side, sc, .9, .06); t1 = P(r, side, sc, 1.12, .06); t2 = P(r, side, sc, 1.12, .2)
    B.tube_path(_mb(M, "alu", "steel"), [t0, t1, t2, t2 - [0, 0, .05]], .012, 6, (*C_STEELC, .1))
    wall_box(_mb(M, "paintwood"), r, side, a, min(b, a + 1.4), 1.75, 1.78, 0, .3, C_WOOD)                                  # shelf
    for s in (a + .1, min(b, a + 1.4) - .1):
        wall_box(_mb(M, "steel"), r, side, s - .01, s + .01, 1.6, 1.75, 0, .2, (.3, .3, .3))
    collide(P(r, side, a, 0, 0), P(r, side, b, .9, .63))
    r.setdefault("built_in", []).extend(["kitchen counter", "sink", "shelf"])
    return side


def bathroom(r, M, rng, collide):
    x0, x1, y0, y1 = r["rect"]; tile = _mb(M, "tile", "conc"); cer = _mb(M, "ceramic", "pvc")
    tc = rng.choice([C_TILE_W, (.75, .85, .9), (.85, .9, .8)])
    for side in "snwe":                                                                      # wall tiles to 1.5 m
        for a, b in free_spans(r, side, 0, 1.5, 0.0):
            wall_box(tile, r, side, a, b, 0, 1.5, 0, .008, tc)
    # pick corners for shower / WC / basin along the side with the fewest openings
    sides = sorted("snwe", key=lambda s_: (len(side_ops(r, s_)), -side_geom(r, s_)[3]))
    sd = sides[0]; o, u, n, L, a0 = side_geom(r, sd)
    spans = free_spans(r, sd, 0, 2.1)
    if not spans: return
    a, b = max(spans, key=lambda p: p[1] - p[0])
    # shower corner at the span start: tray, low upstand, mixer + head, curtain rail
    a = a + .12; sw = min(.9, (b - a) * .45)
    wall_box(tile, r, sd, a, a + sw, 0, .03, 0, .9, tc)                                      # tray
    wall_box(tile, r, sd, a + sw, a + sw + .08, 0, 1.2, 0, .9, tc)                           # tiled half wall beside the shower
    wall_box(tile, r, sd, a, a + sw, 0, .1, .86, .92, tc)                                    # kerb at the front
    fab = _mb(M, "fabric", "pvc"); ccol = rng.choice([(.75, .85, .9), (.9, .8, .6), (.85, .9, .85)])
    for k in range(6):                                   # shower curtain bunched at one end of the rail (pleats)
        s0 = a + .03 + k * .07; d0 = .9 + (.03 if k % 2 else -.03)
        q = [P(r, sd, s0, .25, d0), P(r, sd, s0 + .07, .25, .9 + (-.03 if k % 2 else .03)), P(r, sd, s0 + .07, 1.98, .9 + (-.03 if k % 2 else .03)), P(r, sd, s0, 1.98, d0)]
        fab.add(q, [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*ccol, .1)); fab.add(q[::-1], [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*ccol, .1))
    wall_box(_mb(M, "dark", "steel"), r, sd, a + sw / 2 - .05, a + sw / 2 + .05, .041, .042, .4, .5, (.2, .2, .2))
    p_m = P(r, sd, a + sw / 2, 1.1, .03)
    wall_box(_mb(M, "alu", "steel"), r, sd, a + sw / 2 - .06, a + sw / 2 + .06, 1.05, 1.15, 0, .04, C_STEELC)
    B.tube_path(_mb(M, "alu", "steel"), [p_m + n * .02, p_m + [0, 0, .95] + n * .02, p_m + [0, 0, .98] + n * .25], .011, 6, (*C_STEELC, .1))
    B.superellipsoid(_mb(M, "alu", "steel"), p_m + [0, 0, .95] + n * .27, (.07, .07, .015), (1, 1), 10, 4, (*C_STEELC, .1))
    rail = [P(r, sd, a + sw, 2.0, 0), P(r, sd, a + sw, 2.0, .9), P(r, sd, a, 2.0, .9)]
    B.tube_path(_mb(M, "alu", "steel"), rail, .01, 6, (*C_STEELC, .1))
    sc_ = P(r, sd, a + sw / 2, 0, .45); r["shower"] = [round(float(sc_[0]), 3), round(float(sc_[1]), 3)]; r["shower_side"] = sd
    # water heater high on the wall above the shower start
    hc = P(r, sd, a + sw / 2 + .1, 1.95, .22)
    rings = [[hc + u * dx + n * (.2 * math.cos(t)) + [0, 0, .2 * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 14, endpoint=False)] for dx in (-.3, .3)]
    o_ = cer.grid(np.array(rings), col=(*C_WHITE, .1), close_v=True)
    for e in (-.3, .3): B.superellipsoid(cer, hc + u * e, (.04, .2, .2), (1, 1), 12, 6, (*C_WHITE, .1), R=np.column_stack([u, n, [0, 0, 1]]))
    pv = hc - [0, 0, .2] - n * (.22 - .03)                # pipes: straight down the wall to the mixer
    B.tube_path(_mb(M, "steel"), [hc - [0, 0, .2], pv, P(r, sd, a + sw / 2 + .1, 1.15, .03), P(r, sd, a + sw / 2 + .05, 1.1, .03)], .01, 6, (.6, .6, .6, .1))
    collide(hc - u * .4 - n * .2 - [0, 0, .22], hc + u * .4 + n * .22 + [0, 0, .22])
    # WC next to the shower, basin after it (if room)
    wc = a + sw + .45
    if wc + .3 < b:
        base = P(r, sd, wc, 0, .38)
        B.superellipsoid(cer, base + [0, 0, .2], (.17, .23, .2), (.5, .8), 14, 8, (*C_WHITE, 0), R=np.column_stack([u, n, [0, 0, 1]]), taper=lambda z: (1 - .3 * (1 - z), 1 - .25 * (1 - z)))
        B.superellipsoid(cer, base + [0, 0, .41] + n * .02, (.19, .25, .02), (.6, .9), 14, 4, (*C_WHITE, 0), R=np.column_stack([u, n, [0, 0, 1]]))
        wall_box(cer, r, sd, wc - .2, wc + .2, .42, .8, .02, .2, C_WHITE)                   # cistern
        collide(P(r, sd, wc - .22, 0, 0), P(r, sd, wc + .22, .8, .65))
    bs = wc + .8; bside = sd
    if bs + .3 >= b:                                     # no room on this wall: basin on the next wall with a free stretch
        for s2 in sides[1:]:
            sp2 = [p for p in free_spans(r, s2, 0, 1.9) if p[1] - p[0] > .8]
            if sp2: bside = s2; bs = (sp2[0][0] + sp2[0][1]) / 2; break
    if bside != sd: o, u, n, L, a0 = side_geom(r, bside); sd = bside; b = bs + 1.0
    if bs + .3 < b:
        base = P(r, sd, bs, 0, .25)
        B.tube_path(cer, [base, base + [0, 0, .72]], .08, 10, (*C_WHITE, 0))
        B.superellipsoid(cer, base + [0, 0, .8] + n * .02, (.27, .22, .08), (.6, .7), 14, 6, (*C_WHITE, 0), R=np.column_stack([u, n, [0, 0, 1]]))
        B.tube_path(_mb(M, "alu", "steel"), [P(r, sd, bs, .86, .06), P(r, sd, bs, .98, .06), P(r, sd, bs, .98, .16)], .01, 6, (*C_STEELC, .1))
        mg = _mb(M, "glass")
        q = [P(r, sd, bs - .25, 1.15, .006), P(r, sd, bs + .25, 1.15, .006), P(r, sd, bs + .25, 1.75, .006), P(r, sd, bs - .25, 1.75, .006)]
        if n[0] + n[1] < 0: q = q[::-1]
        mg.add(q, [[0, 1, 2, 3]], [(0, 0)] * 4, (.85, .9, .92, 0))
        collide(P(r, sd, bs - .3, 0, 0), P(r, sd, bs + .3, .9, .5))
    r.setdefault("built_in", []).extend(["shower", "WC", "basin", "water heater", "wall tiles"])
    return sd


def shop(r, M, rng, collide):
    x0, x1, y0, y1 = r["rect"]
    cnt = [op for op in r["openings"] if op["kind"] == "counter"]
    if cnt:                                              # counter behind the shop front opening
        op = dict(cnt[0]); drs = [d for d in r["openings"] if d["kind"] == "door" and d["side"] == op["side"]]
        for d in drs:                                    # keep clear of the door leaf swing (0.95 m)
            if d["a"] >= op["b"] - .1: op["b"] = min(op["b"], d["a"] - .95)
            if d["b"] <= op["a"] + .1: op["a"] = max(op["a"], d["b"] + .95)
        if op["b"] - op["a"] > .8:
            wall_box(_mb(M, "conc"), r, op["side"], op["a"], op["b"], 0, .9, .55, 1.1, (.88, .87, .83))
            wall_box(_mb(M, "paintwood"), r, op["side"], op["a"] - .05, op["b"] + .05, .9, .94, .5, 1.15, (.7, .5, .3))
            collide(P(r, op["side"], op["a"], 0, .55), P(r, op["side"], op["b"], .94, 1.1))
    back = max("snwe", key=lambda s_: (-len(side_ops(r, s_)), side_geom(r, s_)[3]))
    for a, b in free_spans(r, back, 0, 2.2)[:1]:         # wall shelving (timber boards on uprights)
        for z in (.15, .6, 1.05, 1.5, 1.95):
            wall_box(_mb(M, "timber", "paintwood"), r, back, a + .05, b - .05, z, z + .03, 0, .4, (.85, .75, .6))
        for s in np.arange(a + .05, b - .04, max(.6, (b - a - .1) / max(1, int((b - a) / .9)))):
            wall_box(_mb(M, "timber", "paintwood"), r, back, s, s + .04, 0, 2.0, 0, .4, (.8, .7, .55))
        collide(P(r, back, a, 0, 0), P(r, back, b, 2.0, .4))
    r.setdefault("built_in", []).extend(["shop counter", "wall shelving"])
    return back


def workbench(r, M, rng, collide):
    sp = longest_free(r, "snwe", 1.2)
    if not sp: return
    side, a, b = sp; b = min(b, a + 2.4)
    wall_box(_mb(M, "timber", "paintwood"), r, side, a, b, .86, .92, 0, .65, (.75, .62, .45))
    for s in (a + .05, b - .1):
        for d in (.05, .55): wall_box(_mb(M, "timber", "paintwood"), r, side, s, s + .06, 0, .86, d, d + .06, (.7, .58, .42))
    wall_box(_mb(M, "timber", "paintwood"), r, side, a, b, .25, .28, .05, .6, (.7, .58, .42))
    wall_box(_mb(M, "paintwood"), r, side, a, b, 1.1, 1.75, 0, .02, (.55, .45, .32))            # tool board
    for k in range(int((b - a) / .25)):
        s = a + .15 + k * .25; B.tube_path(_mb(M, "steel"), [P(r, side, s, 1.5, .02), P(r, side, s, 1.5, .07)], .005, 4, (.3, .3, .3, .2))
    collide(P(r, side, a, 0, 0), P(r, side, b, .92, .65))
    r.setdefault("built_in", []).append("workbench")
    return side


def timber_lining(r, M, rng, col_wall, col_floor=(.75, .55, .38), wet=False):
    x0, x1, y0, y1 = r["rect"]; z = r["z"]; tm = _mb(M, "timber", "paintwood"); zb = 1.55 if wet else .12
    if not wet:
        for x in np.arange(x0, x1, .14):                # plank floor over the slab (3 mm gaps); wet rooms keep their tiles
            box(tm, (x + .0015, y0, z), (min(x1, x + .14) - .0015, y1, z + .012), tuple(np.array(col_floor) * rng.uniform(.85, 1.08)), .2)
    for side in "snwe":                                  # vertical boards: cover battens every 0.3 m on the painted lining
        for a, b in free_spans(r, side, zb, r["h"], .02):
            for s in np.arange(a + .15, b - .05, .3):
                wall_box(_mb(M, "paintwood"), r, side, s - .02, s + .02, zb, r["h"] - .05, .012 if not wet else .02, .022 if not wet else .03, col_wall)
    for x in np.arange(x0 + .3, x1 - .1, .3):            # boarded ceiling: batten lines
        box(_mb(M, "paintwood"), (x - .02, y0, z + r["h"] - .015), (x + .02, y1, z + r["h"]), (.92, .9, .85), .1)


def fusebox(r, M, side, s):
    wall_box(_mb(M, "steel"), r, side, s - .16, s + .16, 1.45, 1.85, 0, .09, (.82, .83, .82))
    wall_box(_mb(M, "dark", "steel"), r, side, s - .12, s + .12, 1.6, 1.64, .09, .095, (.1, .1, .1))
    conduit(r, M, side, s, 1.85, r["h"])


def wear(r, M, rng, col_wall):
    pl = _mb(M, "plaster")
    for k in range(rng.randint(2, 5)):                   # scuffs + dirt marks low on the walls
        side = rng.choice("snwe"); sp = free_spans(r, side, 0, 1.0)
        if not sp: continue
        a, b = rng.choice(sp); s = rng.uniform(a, max(a, b - .4))
        z = rng.uniform(.12, .9); w = rng.uniform(.15, .45)
        wall_box(pl, r, side, s, min(b, s + w), z, z + rng.uniform(.03, .12), .0, .0015, tuple(np.array(col_wall) * .62), .5)
    for k in range(rng.randint(0, 2)):                   # patched plaster (fresh, lighter, slightly proud)
        side = rng.choice("snwe"); sp = free_spans(r, side, .5, 2.0)
        if not sp: continue
        a, b = rng.choice(sp)
        if b - a < .6: continue
        s = rng.uniform(a, b - .5); z = rng.uniform(.6, 1.8)
        wall_box(pl, r, side, s, s + rng.uniform(.3, .5), z, z + rng.uniform(.2, .4), .0, .002, tuple(np.clip(np.array(col_wall) * 1.12 + .05, 0, 1)), 0)
    for side in "snwe":                                  # rising damp tide mark on the walls
        for a, b in free_spans(r, side, 0, .6, 0):
            if rng.random() < .5:
                wall_box(pl, r, side, a, b, .1, .1 + rng.uniform(.25, .5), .0, .001, tuple(np.array(col_wall) * .82), .6)
    x0, x1, y0, y1 = r["rect"]
    for k in range(rng.randint(0, 3)):                   # chipped / missing floor tiles
        cx, cy = rng.uniform(x0 + .3, x1 - .3), rng.uniform(y0 + .3, y1 - .3)
        w_, h_ = rng.uniform(.15, .3), rng.uniform(.12, .3)
        box(_mb(M, "conc"), (cx, cy, r["z"] - .004), (cx + w_, cy + h_, r["z"] + .0015), (.5, .48, .44), .5)   # tile corner broken off (screed shows)


ALL = ("skirting", "architraves", "curtains", "electrics", "lights", "fixtures", "wear")


def finish(rooms, M, rng, collide=lambda lo, hi: None, entrance=None, skirting_col=(.5, .35, .25), frame_col=(.92, .9, .85), wall_col=(.92, .9, .86), parts=ALL):
    for r in rooms:
        if not r.get("finish", True): continue
        t = r["type"]
        if "timber" in parts: timber_lining(r, M, rng, wall_col, wet=t in ("bathroom", "kitchen"))
        if "skirting" in parts: skirting(r, M, skirting_col if t not in ("bathroom", "kitchen") else (.9, .9, .88))
        if "architraves" in parts: architraves(r, M, frame_col)
        for op in r["openings"]:
            if "curtains" in parts and t not in ("bathroom", "store", "workshop", "garage") and (op["kind"] == "window" or (op["kind"] == "door" and op["z1"] >= 2.6)):
                curtain_rod(r, M, op, rng)
        # switch beside the first door (latch side), sockets on free walls, all on surface conduit
        doors = [op for op in r["openings"] if op["kind"] in ("door", "idoor", "opening")]
        if "electrics" not in parts: doors = []
        if doors:
            d = doors[0]; o, u, n, L, a0 = side_geom(r, d["side"])
            s = d["b"] + .18 if d["b"] + .3 < a0 + L else d["a"] - .18
            switch(r, M, d["side"], s, 1.2); conduit(r, M, d["side"], s, 1.24, r["h"])
        for k in range(0 if "electrics" not in parts else (1 if t in ("bathroom", "store") else 2)):
            side = rng.choice("snwe"); sp = free_spans(r, side, 0, .5)
            if not sp: continue
            a, b = rng.choice(sp); s = rng.uniform(a + .1, max(a + .1, b - .1))
            switch(r, M, side, s, .32 if t != "kitchen" else 1.1, "socket"); conduit(r, M, side, s, .36 if t != "kitchen" else 1.14, r["h"])
        if "lights" in parts: lights(r, M, rng, fan=t in ("living", "bedroom", "salon", "dining", "office") and rng.random() < .75)
        if "fixtures" in parts:
            fx = None
            def rec(what, r=r):                          # every built-in's collision box also goes into rooms.json
                def f(lo, hi):
                    collide(lo, hi); lo_, hi_ = np.minimum(lo, hi), np.maximum(lo, hi)
                    r.setdefault("built_in_boxes", []).append({"what": what, "box": [round(float(v), 3) for v in (*lo_, *hi_)]})
                return f
            if t == "kitchen": fx = kitchen(r, M, rng, rec("kitchen counter"))
            if t == "bathroom": fx = bathroom(r, M, rng, rec("bathroom fitting"))
            if t == "shop": fx = shop(r, M, rng, rec("shop counter / shelving"))
            if t in ("garage", "workshop"): fx = workbench(r, M, rng, rec("workbench"))
            if fx: r["fixture_wall"] = fx
        if "wear" in parts: wear(r, M, rng, wall_col)
    if entrance:
        r, side, s = entrance; fusebox(r, M, side, s)


def write_rooms(path, rooms, extra=None):
    out = []
    for r in rooms:
        cf = []
        for op in r["openings"]:
            p0 = P(r, op["side"], op["a"] - .15, 0, 0); p1 = P(r, op["side"], op["b"] + .15, 0, 1.0)
            lo, hi = np.minimum(p0, p1), np.maximum(p0, p1)
            cf.append([[round(lo[0], 3), round(lo[1], 3)], [round(hi[0], 3), round(hi[1], 3)]])
        x0, x1, y0, y1 = r["rect"]
        fl = r.get("poly") or [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        out.append({"id": r["id"], "type": r["type"], "storey": r.get("storey", 0),
                    "floor": [[round(float(p[0]), 3), round(float(p[1]), 3)] for p in fl],
                    "z": round(r["z"], 3), "height": round(r["h"], 3),
                    "openings": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in op.items()} for op in r["openings"]],
                    "cover_free": cf, "built_in": r.get("built_in", []), "fixture_wall": r.get("fixture_wall"),
                    "finished": bool(r.get("finish", True)), **({"shower": r["shower"]} if r.get("shower") else {}),
                    **({"built_in_boxes": r["built_in_boxes"]} if r.get("built_in_boxes") else {}), **({"ceiling": r["ceiling"]} if r.get("ceiling") else {})})
    json.dump({"units": "m, asset space (Unreal: x100, same axes)", "rooms": out, **(extra or {})}, open(path, "w"), indent=1)
