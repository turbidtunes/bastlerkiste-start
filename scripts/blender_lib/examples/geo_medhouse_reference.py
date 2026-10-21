"""Mediterranean village house generator for "Les Calanques" – Worker R2136 (STREAMS S2, claim map_bld_medhouse).
python geo_medhouse.py <out.blend> [seed] [storeys] [plot_w] [plot_d] [type]

Real model (REFERENCES.md, map/refs/*.jpg – the user's photos are Mallorcan village streets): rendered masonry
houses of one to three storeys on a narrow plot – lime-washed white or sand / ochre / pale salmon render, a stone
or crazy-paving plinth with white joints, louvred timber shutters ("persianes", Session M's façade kit: blue, green,
brown, black), panelled timber entrance door with an iron grille, wall lanterns, a meter box set into the front wall,
grey zinc downpipes, cables run along the façade; upper floor with a cantilevered balcony on turned balusters
(precast vase balusters between a plinth and a coping rail) or French doors; roofs of Arab / canal terracotta tiles
(gable or hip, rafter ends and a boarded soffit under the eaves – or a stone cornice) or a flat roof terrace behind
a baluster parapet; often an arched loggia / porch, a front patio behind a low rough-rendered wall with a plank gate,
a timber pergola, potted plants, wicker chairs; in the back a small yard with the washing line and a butane bottle.

Plot (H's placements.json "bld_house_med": size_m = plot w x d, storeys, type house|epicerie): origin = plot centre on
finished ground, front = -Y (the lane). The house block fills the plot width (terraced = blank party walls when the
side gap is 0) and leaves a front patio (if the plot is deep enough) and a back yard.
Plan of every storey: a main column (living + kitchen / two bedrooms) and a 2.1 m service column with a dog-leg
stair (2 x 8 risers, landing at the back) and the entrance hall / landing + bathroom in front of it.
Writes <out>_rooms.json (interior.write_rooms – Session N dresses the rooms) + SOCKET_Loot_* + SOCKET_Drop.
"""
import sys, os, math, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(HERE, ".."); MAP = os.path.join(S, "..")
sys.path[:0] = [S, os.path.join(S, "house"), os.path.join(MAP, "med"), os.path.join(MAP, "med", "facade")]
import bpy
from mathutils import Matrix, Vector
import bldlib as B
from bldlib import MB, srgb
import hlib as H
from hlib import cbox
import interior as IN
import civlib as C
import civlib as CL_
import geo_facade as GF

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = a[0]; SEED = int(a[1]) if len(a) > 1 else 1
rng = random.Random(SEED * 7727 + 5)
NS = int(a[2]) if len(a) > 2 else rng.choice([1, 2, 2, 2, 3])
PW = float(a[3]) if len(a) > 3 else rng.choice([6.5, 7.5, 8.5, 9.5, 10.5])
PD = float(a[4]) if len(a) > 4 else rng.choice([6.5, 7.5, 8.5, 9.5])
TYPE = a[5] if len(a) > 5 else "house"
B.reset(); ctx = C.add_mbs(H.Ctx(rng)); ctx.tiles = MB(); ctx.stone = MB()

# ------------------------------------------------------------------ style draw
PAL = {"white": ["#f2f0ea", "#efece4", "#f4f1e8"], "sand": ["#e8d4ac", "#e3c99c", "#ecdcbc"], "salmon": ["#ecd0bf", "#e6c3ad"], "ochre": ["#dcb985", "#e2c38f"]}
STY = rng.choice(["white", "white", "sand", "sand", "salmon", "ochre"])
C_EXT = srgb(rng.choice(PAL[STY])); C_INT = srgb(rng.choice(["#f3f1ea", "#efe9dc", "#eef0ea"]))
C_TRIM = srgb("#f6f4ee") if STY != "white" else srgb(rng.choice(["#f6f4ee", "#d9c49a"]))
C_STONE = srgb(rng.choice(["#d6c39a", "#cdb88c", "#dccaa2"]))                          # marès sandstone
PLINTH = rng.choice(["crazy", "crazy", "render", "stone"])
SHUT_SEED = rng.randint(0, 4)                                                           # M's shutter colour (seed % 5)
FL = .3; SH = 2.85; SL = .2; WT = .2                                                     # floor, storey, slab, wall
SIDE = rng.choice([0.0, 0.0, .9]) if PW >= 8.0 else 0.0                                  # side passage (detached) or terraced
FRONT = 2.2 if PD >= 9.0 else (1.6 if PD >= 8.0 else 0.0)
if TYPE == "epicerie": FRONT = 0.0
DEPTH = min(8.0, max(6.0, PD - FRONT - 1.0)); BACK = max(0.0, PD - FRONT - DEPTH)
X0, X1 = -PW / 2 + SIDE, PW / 2; Y0, Y1 = -PD / 2 + FRONT, PD / 2 - BACK                  # house block
SERV_RIGHT = rng.random() < .5                                                          # stair column on the right or left
SW = 2.1
if SERV_RIGHT: XS0, XS1 = X1 - WT - SW, X1 - WT; XM0, XM1 = X0 + WT, XS0 - WT
else: XS0, XS1 = X0 + WT, X0 + WT + SW; XM0, XM1 = XS1 + WT, X1 - WT
YI0, YI1 = Y0 + WT, Y1 - WT                                                              # inner faces
WELL = (XS0, XS1, YI1 - 3.3, YI1)                                                        # stair well
DEEP = (YI1 - YI0) >= 7.0                                                               # deep block: two bedrooms per upper floor
LND = 2.0 if DEEP else 1.0                                                               # landing depth in front of the well
YMID0 = (YI0 + YI1) / 2                                                                  # ground: living | kitchen (open arch)
YMID = WELL[2] - LND / 2 if (YI1 - YI0) >= 7.0 else (YI0 + YI1) / 2 + .3                 # upper split: landing centre (deep) or mid (rooms en suite)
ROOF = rng.choice(["gable", "gable", "hip", "flat", "lean"]) if NS < 3 else rng.choice(["gable", "flat", "hip"])
EAVE = rng.choice(["rafters", "rafters", "cornice"])
BALC = NS >= 2 and rng.random() < .7
PORCH = NS >= 2 and TYPE != "epicerie" and rng.random() < .5                          # arched entrance recess (1.0 m deep) in the service column
GARAGE = TYPE != "epicerie" and (XM1 - XM0) >= 3.2 and FRONT == 0 and rng.random() < .35
# ------------------------------------------------------------------ Worker WZ (S25): the photo types 17+ (refs/photos/med_houses)
# Every draw above stays as it was (house / épicerie seeds unchanged); a photo type overrides the style + plot after
# the draws and re-derives the plan. Own random stream wrng for anything new.
NEWT = {
    "corner_balustrade":     dict(STY="white", SHUT=0, SIDE=2.0, FRONT=2.6, ROOF="hip", OV=.8, BALC=False, PORCH=False, WALL="baluster", CORNER=1.4, feats=("chimney",)),
    "two_storey_balustrade": dict(STY="cream", SHUT=4, SIDE=1.8, FRONT=2.4, ROOF="gable", BALC="small", PORCH=False, WALL="baluster", CORNER=1.4, SURR=True, feats=("porch_tile", "chimney")),
    "stonewall_porch":       dict(STY="salmon", SHUT=0, SIDE=0.0, FRONT=2.4, ROOF="gable", BALC=False, PORCH=False, WALL="rubble", GATE="pillars", PLINTH="stone", SURR=True, feats=("porch_pillars", "chimney")),
    "corner_bungalow_wall":  dict(STY="cream", SHUT=3, SIDE=2.0, FRONT=2.4, ROOF="hip", OV=.5, BALC=False, PORCH=False, WALL="render_high", CORNER=1.2, SURR=True, GATE="steel", feats=("awning_box", "chimney")),
    "villa_arcade":          dict(STY="ochre", SHUT=0, SIDE=1.8, FRONT=2.6, ROOF="hip", BALC=False, PORCH=False, WALL="ashlar", CORNER=0.0, GATE="steel", feats=("loggia", "porch_wide", "boug_corner", "chimney")),
    "street_bougainvillea":  dict(STY="cream", SHUT=3, SIDE=0.0, FRONT=2.4, ROOF="gable", BALC=False, PORCH=False, WALL="rubble", WALL_H=1.0, GATE="steel", feats=("porch_tile", "boug_wall")),
    "pink_arcade_balustrade": dict(STY="pink", SHUT=0, SIDE=1.8, FRONT=2.6, ROOF="flat", BALC="arcade", PORCH=False, WALL="breeze", CORNER=0.0, PLINTH="crazy", feats=("arcade2", "terrace_all", "hoods", "corner_balcony")),
    "street_bungalow_poles": dict(STY="white", SHUT=3, SIDE=0.0, FRONT=2.2, ROOF="gable", BALC=False, PORCH=False, WALL="balpanel", feats=("chimney", "pergola_vine")),
    "apartment_block":       dict(STY="white", SHUT=3, SIDE=0.0, FRONT=0.0, ROOF="flat", BALC="apt", PORCH=False, GARAGE=True, WALL=None, FSOLID=True, feats=("garage2",)),
    "white_balcony_blue_shutters": dict(STY="white", SHUT=2, SIDE=0.0, FRONT=2.6, ROOF="flat", BALC="posts", PORCH=False, GARAGE=True, WALL="render_low", FSOLID=True, PLINTH="stone", feats=("awning_box", "steel_garage")),
}
NT = NEWT.get(TYPE); FEAT = NT["feats"] if NT else (); APT = TYPE == "apartment_block"
if NT:
    wrng = random.Random(SEED * 389 + 7)
    PAL.update({"cream": ["#efe2b8", "#f1e6c4"], "pink": ["#d9b2a4", "#d4a99a"]})
    STY = NT["STY"]; C_EXT = srgb(wrng.choice(PAL[STY])); SHUT_SEED = NT["SHUT"]
    C_TRIM = srgb("#f6f4ee") if STY in ("white", "salmon", "pink") else srgb("#e9dcb4")
    PLINTH = NT.get("PLINTH", wrng.choice(["render", "crazy", "stone"])); ROOF = NT["ROOF"]; EAVE = "rafters"
    SIDE = NT["SIDE"] if PW >= 8.0 else 0.0; FRONT = NT["FRONT"] if PD >= 8.0 else 0.0
    DEPTH = min(8.0, max(6.0, PD - FRONT - 1.0)); BACK = max(0.0, PD - FRONT - DEPTH)
    X0, X1 = -PW / 2 + SIDE, PW / 2; Y0, Y1 = -PD / 2 + FRONT, PD / 2 - BACK
    if SERV_RIGHT: XS0, XS1 = X1 - WT - SW, X1 - WT; XM0, XM1 = X0 + WT, XS0 - WT
    else: XS0, XS1 = X0 + WT, X0 + WT + SW; XM0, XM1 = XS1 + WT, X1 - WT
    YI0, YI1 = Y0 + WT, Y1 - WT; WELL = (XS0, XS1, YI1 - 3.3, YI1)
    DEEP = (YI1 - YI0) >= 7.0; LND = 2.0 if DEEP else 1.0; YMID0 = (YI0 + YI1) / 2
    YMID = WELL[2] - LND / 2 if (YI1 - YI0) >= 7.0 else (YI0 + YI1) / 2 + .3
    BALC = bool(NT["BALC"]) and NS >= 2; PORCH = NT["PORCH"]; GARAGE = NT.get("GARAGE", False) and (XM1 - XM0) >= 3.2
def zfl(s): return FL + s * SH                                                           # floor level of storey s
ZTOP = zfl(NS) - SL                                                                      # underside of the roof slab

ROOMS = []; LOOT = []; OPS = []


def room(id_, typ, rect, s, **kw):
    z = zfl(s) + .012; r = {"id": id_, "type": typ, "storey": s, "rect": rect, "z": z, "h": zfl(s + 1) - SL - z, "openings": [], **kw}
    ROOMS.append(r); return r


def op(line, a_, b_, z0, z1, kind, s, ext=False, fit=None):
    OPS.append({"line": line, "a": a_, "b": b_, "z0": z0, "z1": z1, "kind": kind, "st": s, "ext": ext, "fit": fit}); return OPS[-1]


# ------------------------------------------------------------------ rooms + openings per storey
fx_front = ("y", Y0); fx_back = ("y", Y1); fx_l = ("x", X0); fx_r = ("x", X1)
mx = ((XM0 + XM1) / 2); sx = (XS0 + XS1) / 2; wm = XM1 - XM0
xpart = XS0 - WT / 2 if SERV_RIGHT else XS1 + WT / 2                                     # partition line main | service
side_serv = fx_r if SERV_RIGHT else fx_l; side_main = fx_l if SERV_RIGHT else fx_r
for s in range(NS):
    if s == 0:
        if TYPE == "epicerie":
            room("shop", "shop", (XM0, XM1, YI0, YMID0 - .1), 0); room("store", "store", (XM0, XM1, YMID0 + .1, YI1), 0)
        elif GARAGE:
            room("garage", "garage", (XM0, XM1, YI0, YMID0 - .1), 0); room("kitchen", "kitchen", (XM0, XM1, YMID0 + .1, YI1), 0)
        else:
            room("living", "living", (XM0, XM1, YI0, YMID0 - .1), 0); room("kitchen", "kitchen", (XM0, XM1, YMID0 + .1, YI1), 0)
        if NS > 1:
            room("hall", "entrance", (XS0, XS1, YI0 + (1.0 if PORCH else 0), WELL[2] - .1), 0); room("stair0", "stair", (XS0, XS1, WELL[2] + .0, YI1), 0)
        else:
            room("bed0", "bedroom", (XS0, XS1, YI0, YI1 - 2.1), 0); room("bath0", "bathroom", (XS0, XS1, YI1 - 1.9, YI1), 0)
    else:
        if DEEP: room(f"bed{s}a", "bedroom", (XM0, XM1, YI0, YMID - .1), s); room(f"bed{s}b", "bedroom", (XM0, XM1, YMID + .1, YI1), s)
        else: room(f"bed{s}a", "bedroom", (XM0, XM1, YI0, YMID - .1), s); room(f"bed{s}b", "bedroom", (XM0, XM1, YMID + .1, YI1), s)
        room(f"bath{s}", "bathroom", (XS0, XS1, YI0, WELL[2] - LND - .1), s); room(f"land{s}", "landing", (XS0, XS1, WELL[2] - LND + .1, WELL[2] + .0), s)
        if s < NS - 1 or True: room(f"stair{s}", "stair", (XS0, XS1, WELL[2], YI1), s)
    # front facade
    bays = max(1, int(round(wm / 2.0)))
    xb = [XM0 + wm * (k + .5) / bays for k in range(bays)]
    if s == 0:
        if TYPE == "epicerie":
            op(fx_front, mx - 1.25, mx + 1.25, 0, 2.2, "door", 0, True, "roller")             # shop front: roller + glazed door behind
        elif GARAGE:
            g0 = mx - (1.45 if "garage2" in FEAT else 0)
            op(fx_front, g0 - 1.25, g0 + 1.25, 0, 2.2, "door", 0, True, "garage")
            if "garage2" in FEAT and g0 + 4.2 < XM1 - .2: op(fx_front, g0 + 1.65, g0 + 4.15, 0, 2.2, "door", 0, True, "garage")
        else:
            xd = (xb[-1] if SERV_RIGHT else xb[0]) if NS == 1 else None                 # single storey: entrance into the living room
            for x in xb:
                if x == xd: op(fx_front, x - .45, x + .45, 0, 2.1, "door", 0, True, "entry")
                else: op(fx_front, x - .6, x + .6, .9, 2.1, "window", 0, True, "win")
        if NS > 1 and PORCH: op(("y", YI0 + 1.0 - WT / 2), sx - .45, sx + .45, 0, 2.1, "door", 0, True, "entry")   # door at the back of the arched recess
        elif NS > 1: op(fx_front, sx - .45, sx + .45, 0, 2.1, "door", 0, True, "entry")
        elif GARAGE: op(fx_front, sx - .45, sx + .45, 0, 2.1, "door", 0, True, "entry")    # (W3 review: a garage house still has its street door)
        else: op(fx_front, sx - .6, sx + .6, .9, 2.1, "window", 0, True, "win")
    else:
        balc_door = BALC and (s == 1 or APT)
        for x in xb:
            if balc_door: op(fx_front, x - .45, x + .45, 0, 2.1, "door", s, True, "balcdoor")
            else: op(fx_front, x - .6, x + .6, .9, 2.1, "window", s, True, "win")
        op(fx_front, sx - .3, sx + .3, 1.5, 2.1, "window", s, True, "bathwin")
    # back facade: kitchen / back bedroom window(s), stair window at the landing
    for x in xb[:max(1, bays - (1 if bays > 2 else 0))]: op(fx_back, x - .6, x + .6, .9 if s else 1.1, 2.1, "window", s, True, "win")
    if NS > 1 and s < NS: op(fx_back, sx - .3, sx + .3, SH / 2 + .9, SH / 2 + 1.5, "window", s, True, "stairwin")
    if NS == 1: op(fx_back, sx - .3, sx + .3, 1.5, 2.1, "window", 0, True, "bathwin")
    if s == 0 and BACK >= .8 and TYPE == "house": op(fx_back, xb[-1] - .45, xb[-1] + .45, 0, 2.1, "door", 0, True, "backdoor") if bays > 2 else op(fx_back, (XM1 if SERV_RIGHT else XM0) + (-.75 if SERV_RIGHT else .75) - .45, (XM1 if SERV_RIGHT else XM0) + (-.75 if SERV_RIGHT else .75) + .45, 0, 2.1, "door", 0, True, "backdoor")
    # side facades (detached side only)
    if SIDE > 0:
        op(fx_l, (Y0 + Y1) / 2 - .6, (Y0 + Y1) / 2 + .6, .9, 2.1, "window", s, True, "win")
    # interior openings: main | service partition
    if NS > 1:
        if s == 0: op(("x", xpart), YI0 + (1.15 if PORCH else .4), YI0 + (2.0 if PORCH else 1.25), 0, 2.1, "idoor", 0, False, "door")   # hall -> living
        elif DEEP:
            op(("x", xpart), WELL[2] - 1.95, WELL[2] - 1.12, 0, 2.1, "idoor", s, False, "door")          # landing -> front bedroom
            op(("x", xpart), WELL[2] - .88, WELL[2] - .05, 0, 2.1, "idoor", s, False, "door")              # landing -> back bedroom
        else:
            op(("x", xpart), WELL[2] - .9, WELL[2] - .1, 0, 2.1, "idoor", s, False, "door")
            op(("y", YMID), (XM0 + .3) if SERV_RIGHT else (XM1 - 1.15), (XM0 + 1.15) if SERV_RIGHT else (XM1 - .3), 0, 2.1, "idoor", s, False, "door")   # rooms en suite
        if s > 0: op(("y", WELL[2] - LND), XS0 + .3, XS0 + 1.1, 0, 2.1, "idoor", s, False, "door")      # bathroom off the landing
    else:
        op(("x", xpart), YI0 + .4, YI0 + 1.25, 0, 2.1, "idoor", 0, False, "door")                       # living -> bedroom
        op(("y", YI1 - 2.0), XS0 + .3, XS0 + 1.1, 0, 2.1, "idoor", 0, False, "door")                    # bedroom -> bath
    if s == 0: op(("y", YMID0), XM0 + .3, XM0 + min(1.4, wm - .3), 0, 2.1, "opening", 0, False, "arch")


def assign_openings():
    for r in ROOMS:
        x0, x1, y0, y1 = r["rect"]
        for o in OPS:
            if o["st"] != r["storey"]: continue
            ax, c = o["line"]
            for side, (lax, lc, lo_, hi_) in {"s": ("y", y0, x0, x1), "n": ("y", y1, x0, x1), "w": ("x", x0, y0, y1), "e": ("x", x1, y0, y1)}.items():
                if ax == lax and abs(c - lc) <= .21 and o["a"] < hi_ - .05 and o["b"] > lo_ + .05:
                    r["openings"].append({"side": side, "a": max(o["a"], lo_), "b": min(o["b"], hi_), "z0": o["z0"], "z1": o["z1"], "kind": o["kind"], "to": "outside" if o["ext"] else "?"})
    for r in ROOMS:
        for o in r["openings"]:
            if o["to"] != "?": continue
            for r2 in ROOMS:
                if r2 is r or r2["storey"] != r["storey"]: continue
                for o2 in r2["openings"]:
                    if abs(o2["a"] - o["a"]) < .05 and abs(o2["b"] - o["b"]) < .05 and o2["side"] == {"s": "n", "n": "s", "w": "e", "e": "w"}[o["side"]]: o["to"] = r2["id"]


# porch: arched opening in the front wall of the service column (recess 1.0 m, door at its back)
if PORCH: op(fx_front, sx - .7, sx + .7, 0, 2.5, "opening", 0, True, "arch")
LGD = 1.3                                                                        # photo villa_arcade: recessed first-floor loggia over the main column
if "loggia" in FEAT and NS >= 2:
    OPS[:] = [o for o in OPS if not (o["st"] == 1 and o["line"] == fx_front and o["a"] >= XM0 - .01 and o["b"] <= XM1 + .01)]
    wa = min(2.8, (XM1 - XM0) * .5); wb = 1.2; gap_ = .5
    xa_ = (XM0 + .4, XM0 + .4 + wa) if SERV_RIGHT else (XM1 - .4 - wa, XM1 - .4)
    xb_ = (xa_[1] + gap_, xa_[1] + gap_ + wb) if SERV_RIGHT else (xa_[0] - gap_ - wb, xa_[0] - gap_)
    op(fx_front, *xa_, 0, 2.6, "opening", 1, True, "arch"); op(fx_front, *xb_, 0, 2.35, "opening", 1, True, "arch")
    yl = Y0 + LGD; xm_ = (XM0 + XM1) / 2
    op(("y", yl), xm_ - .45, xm_ + .45, 0, 2.1, "door", 1, True, "balcdoor"); op(("y", yl), xm_ + 1.0, xm_ + 2.2, .9, 2.1, "window", 1, True, "lwin")
    for r in ROOMS:
        if r["id"] == "bed1a": r["rect"] = (r["rect"][0], r["rect"][1], yl + WT / 2, r["rect"][3]); r["type"] = "living"
assign_openings()


# ------------------------------------------------------------------ shell: ground slab, floors, exterior walls
RECT = (X0, X1, Y0, Y1)
cbox(ctx.conc, (X0 + .05, Y0 + .05, 0), (X1 - .05, Y1 - .05, FL - .001), {"all": (.75, .74, .7)}); ctx.ucxb((X0, Y0, 0), (X1, Y1, FL))
C_FLOOR = srgb(rng.choice(["#d9c2a0", "#e6dccb", "#cfae8a", "#e0d6c6"]))                  # terracotta / hydraulic / marble chip
for r in ROOMS:
    x0, x1, y0, y1 = r["rect"]
    cbox(ctx.tile, (x0 - .1, y0 - .1, r["z"] - .032), (x1 + .1, y1 + .1, r["z"]), {"all": C_FLOOR if r["type"] not in ("bathroom", "garage", "store") else ((.88, .88, .86) if r["type"] == "bathroom" else (.7, .69, .66))})
if PORCH:
    cbox(ctx.tile, (XS0, Y0, FL - .02), (XS1, YI0 + 1.0 - WT, FL + .012), {"all": srgb("#c9a27a")})


def facade_ops(key, s):
    line = {"front": fx_front, "back": fx_back, "left": fx_l, "right": fx_r}[key]
    lo_, hi_ = (X0, X1) if key in ("front", "back") else (Y0, Y1)
    z0 = 0 if s == 0 else zfl(s) - SL
    out = []
    for o in OPS:
        if o["line"] != line or o["st"] != s: continue
        if key == "front": u0, u1 = o["a"] - X0, o["b"] - X0
        elif key == "back": u0, u1 = X1 - o["b"], X1 - o["a"]
        elif key == "right": u0, u1 = o["a"] - Y0, o["b"] - Y0
        else: u0, u1 = Y1 - o["b"], Y1 - o["a"]
        out.append((u0, u1, zfl(s) - z0 + o["z0"], zfl(s) - z0 + o["z1"], o["kind"], o))
    return out


for s in range(NS):
    z0 = 0 if s == 0 else zfl(s) - SL; z1 = zfl(s + 1) - SL
    for key in ("front", "back", "left", "right"):
        H.wall(ctx, RECT, key, z0, z1, WT, [o[:5] for o in facade_ops(key, s)], C_EXT, C_INT, damp_z=0 if s == 0 else None, damp_amt=.3)
    if s > 0:                                                                 # floor slab with the stair-well opening
        zs = zfl(s) - SL
        for lo, hi in (((X0 + WT, Y0 + WT), (X1 - WT, WELL[2])), ((X0 + WT, WELL[3]), (X1 - WT, Y1 - WT)),
                       ((X0 + WT, WELL[2]), (WELL[0], WELL[3])), ((WELL[1], WELL[2]), (X1 - WT, WELL[3]))):
            if hi[0] - lo[0] > .01 and hi[1] - lo[1] > .01:
                cbox(ctx.conc, (*lo, zs), (*hi, zfl(s) - .03), {"all": C_INT, "pz": (.8, .79, .76)}); ctx.ucxb((*lo, zs), (*hi, zfl(s) - .03))
# roof / ceiling slab over the top storey
cbox(ctx.conc, (X0 + WT, Y0 + WT, ZTOP), (X1 - WT, Y1 - WT, ZTOP + SL), {"all": C_INT, "pz": (.72, .71, .68)}); ctx.ucxb((X0, Y0, ZTOP), (X1, Y1, ZTOP + SL))
# slab bands on the facades (painted string course at every floor, sand style in stone)
for s in range(1, NS + 1):
    zb = zfl(s) - SL
    for key in ("front", "back", "left", "right"):
        if SIDE == 0 and key == ("right" if True else "left") and False: continue
        org, u, n, L = H.facade(RECT, key)
        if key in ("left", "right") and SIDE == 0 and key == "right": continue
        if s == NS and ROOF != "flat": continue
        C.wbox(ctx.plaster if STY in ("white", "salmon") else ctx.stone, org, u, n, -.02 if key in ("front", "back") else 0, L + (.02 if key in ("front", "back") else 0), zb + .02, zb + .2, 0, .035, C_TRIM if STY in ("white", "salmon") else C_STONE, .1)


def part(p0, p1, line, s, col_l=None, col_r=None, t=WT, z0=None, z1=None):
    ax = 0 if line[0] == "y" else 1
    lo_, hi_ = min(p0[ax], p1[ax]), max(p0[ax], p1[ax])
    ops = [(o["a"] - lo_, o["b"] - lo_, o["z0"] + .012 + .02, o["z1"] + .012 + .02) for o in OPS if o["line"] == line and o["st"] == s and o["b"] > lo_ and o["a"] < hi_]
    C.pwall(ctx, p0, p1, zfl(s) - .02 if z0 is None else z0, zfl(s + 1) - SL if z1 is None else z1, t, ops, col_l or C_INT, col_r or C_INT)


for s in range(NS):
    part((xpart, YI0), (xpart, YI1), ("x", xpart), s)
    if s == 0: part((XM0, YMID0), (XM1, YMID0), ("y", YMID0), s)
    else: part((XM0, YMID), (XM1, YMID), ("y", YMID), s)
    if NS > 1 and s > 0: part((XS0, WELL[2] - LND), (XS1, WELL[2] - LND), ("y", WELL[2] - LND), s)
    if NS == 1: part((XS0, YI1 - 2.0), (XS1, YI1 - 2.0), ("y", YI1 - 2.0), 0)
if PORCH:                                                                     # back wall of the recess with the entrance door
    part((XS0, YI0 + .9), (XS1, YI0 + .9), ("y", YI0 + .9), 0)


# ------------------------------------------------------------------ dog-leg stair in the well (2 x 8 risers, waist slabs)
HA = (XS1 - 1.05, XS1) if SERV_RIGHT else (XS0, XS0 + 1.05)                    # flight A against the outer wall (goes up to the back)
HB = (XS0, XS0 + 1.0) if SERV_RIGHT else (XS1 - 1.0, XS1)                      # flight B against the partition (comes back to the front)
C_TREAD = srgb(rng.choice(["#d8d0c0", "#c9b89a", "#e2ddd2"]))                  # marble / terrazzo treads
G7 = 7 * .27


def flight(x0, x1, y0, dirn, z0, z1):
    r_ = (z1 - z0) / 8
    for k in range(7):
        ya, yb = y0 + dirn * k * .27, y0 + dirn * (k + 1) * .27
        zt = z0 + (k + 1) * r_
        cbox(ctx.conc, (x0, min(ya, yb), zt - r_ - .02), (x1, max(ya, yb), zt - .025), {"all": (.85, .84, .8)})
        cbox(ctx.tile, (x0, min(ya, yb) - .02 * (dirn < 0), zt - .025), (x1, max(ya, yb) + .02 * (dirn > 0), zt), {"all": C_TREAD}, A=.15)
    ya = y0; yb = y0 + dirn * G7
    P = np.array([[(x0 + x1) / 2, ya - dirn * .1, z0 - .1], [(x0 + x1) / 2, yb, z1 - r_ - .12]])
    B.sweep(ctx.conc, P, B.rect(x1 - x0, .16, 0, -.08), (*C_INT, .05), up=(0, 0, 1))
    ctx.hull([[x, y, z] for x in (x0, x1) for (y, z) in ((ya, z0), (yb, z1 - r_), (ya, z0 - .05), (yb, z1 - r_ - .2))])


if NS > 1:
    W2, W3 = WELL[2], WELL[3]
    for s in range(NS - 1):
        zA, zM, zB = zfl(s), zfl(s) + SH / 2, zfl(s + 1)
        flight(*HA, W2, 1, zA, zM)
        cbox(ctx.conc, (XS0, W2 + G7, zM - .15), (XS1, W3, zM - .025), {"all": (.85, .84, .8)}); ctx.ucxb((XS0, W2 + G7, zM - .15), (XS1, W3, zM))
        cbox(ctx.tile, (XS0, W2 + G7, zM - .025), (XS1, W3, zM), {"all": C_TREAD})
        flight(*HB, W2 + G7, -1, zM, zB)
    # spine wall between the flights, every storey, + a timber handrail on it
    xsp = (HA[0] + HB[1]) / 2 if SERV_RIGHT else (HA[1] + HB[0]) / 2
    for s in range(NS):
        C.pwall(ctx, (xsp, W2 + .05), (xsp, W2 + G7), zfl(s) - .02, zfl(s + 1) - SL, .1, [], C_INT, C_INT)
        if s < NS - 1:
            r_ = SH / 16
            for hx, z0_ in ((xsp + (.08 if SERV_RIGHT else -.08), zfl(s)), (xsp - (.08 if SERV_RIGHT else -.08), zfl(s) + SH / 2)):
                up = hx > xsp if SERV_RIGHT else hx < xsp
                ya, yb = (W2, W2 + G7) if (hx - xsp) * (1 if SERV_RIGHT else -1) > 0 else (W2 + G7, W2)
                za, zb = (z0_ + .9 + r_, z0_ + SH / 2 + .9) if ya < yb else (z0_ + .9 + r_, z0_ + SH / 2 + .9)
                B.tube_path(ctx.timber, [(hx, ya, za), (hx, yb, zb)], .025, 8, (.45, .3, .18, .2))
    # top storey: the hole over flight A gets a baluster-less steel rail at the landing edge
    zt = zfl(NS - 1)
    H.railing(ctx, [(HA[0] + .02, W2 - .03), (HA[1] - .02, W2 - .03)], zt, srgb("#2a2a28"), "bars", h=.95, posts=1.0)


# ------------------------------------------------------------------ roof
C_TILE = [srgb(h) for h in ("#b8643c", "#a95a36", "#c27448", "#9e5232", "#b26a44", "#8f4a2e")]
ZE = ZTOP + SL                                                                 # roof bearing level (slab top)
OV = NT.get("OV", .35) if NT else .35                                          # eave overhang
PITCH = math.radians(rng.uniform(18, 24))


def tile_face(O, uax, vax, U, vmax, pitch=.21, amp=.045, course=.38, col_seed=0):
    """Arab canal-tile roof surface: covers + channels as a wave across u, a butt step at every course along v;
    columns are clipped to vmax(u) (hips / verges are covered by ridge tiles). O = eave corner, vax = up-slope unit,
    uax = along the eave, n = outward normal."""
    O = np.asarray(O, float); uax = np.asarray(uax, float); vax = np.asarray(vax, float); n = np.cross(uax, vax)
    if n[2] < 0: n = -n
    nu = max(2, int(U / (pitch / 4)))
    us = np.linspace(0, U, nu + 1)
    trng = random.Random(col_seed)
    for i in range(nu):
        ua, ub = us[i], us[i + 1]; vm = min(vmax(ua), vmax(ub))
        if vm <= .02: continue
        def off(u): return amp * (.5 + .5 * math.cos(2 * math.pi * u / pitch))
        vs = []; v = 0.0
        while v < vm - 1e-3:
            vs.append(v); v += course
        vs.append(vm)
        cc = C_TILE[(int(ua / pitch) * 7 + col_seed) % len(C_TILE)]
        for k in range(len(vs) - 1):
            va, vb = vs[k], vs[k + 1]; st = .018 if k > 0 else 0.0                  # butt step (lower end raised)
            Q = [O + uax * ua + vax * va + n * (off(ua) + st), O + uax * ub + vax * va + n * (off(ub) + st),
                 O + uax * ub + vax * vb + n * off(ub), O + uax * ua + vax * vb + n * off(ua)]
            lich = .25 if trng.random() < .06 else .1                                   # lichen / dirt patches
            ctx.tiles.add(Q, [[0, 1, 2, 3]], [(ua, va), (ub, va), (ub, vb), (ua, vb)], (*cc, lich))
            if k > 0 and i % 4 == 0:                                                      # butt face of the course
                Q2 = [O + uax * ua + vax * va + n * off(ua), O + uax * (ua + pitch / 4 * 4 if False else ub) + vax * va + n * off(ub),
                      O + uax * ub + vax * va + n * (off(ub) + st), O + uax * ua + vax * va + n * (off(ua) + st)]
        # eave nose: the first course overhangs as a visible tile end (thickness)
        Q = [O + uax * ua + n * (off(ua) - .015), O + uax * ub + n * (off(ub) - .015), O + uax * ub + n * off(ub), O + uax * ua + n * off(ua)]
        ctx.tiles.add(Q, [[0, 1, 2, 3]], [(ua, 0), (ub, 0), (ub, .02), (ua, .02)], (*cc, .2))


def ridge(p0, p1, r=.12):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float); L = np.linalg.norm(p1 - p0); d = (p1 - p0) / L
    k = max(1, int(L / .4))
    for i in range(k):
        a_, b_ = p0 + d * L * i / k, p0 + d * L * (i + 1) / k
        B.tube_path(ctx.tiles, [a_ - d * .02, b_ + d * .02], r, 10, (*C_TILE[i % len(C_TILE)], .15))
        B.tube_path(ctx.plaster, [a_ + [0, 0, -.06], b_ + [0, 0, -.06]], r * .85, 8, (.85, .83, .78, .3))       # mortar bedding


def rafters(y_face, n_out, x0, x1, z, ov):
    """projecting rafter ends + boarded soffit under a tile eave (photo street_house_white)"""
    for x in np.arange(x0 + .25, x1 - .1, .6):
        lo = np.array([x - .04, min(y_face, y_face + n_out * ov), z - .14]); hi = np.array([x + .04, max(y_face, y_face + n_out * ov), z - .02])
        cbox(ctx.timber, lo, hi, {"all": (.5, .34, .2)}, A=.25)
    lo = np.array([x0 - .05, min(y_face, y_face + n_out * ov), z - .02]); hi = np.array([x1 + .05, max(y_face, y_face + n_out * ov), z + .0])
    cbox(ctx.timber, lo, hi, {"all": (.58, .4, .24)}, A=.2)


def cornice(y_face, n_out, x0, x1, z):
    for k, (d, h) in enumerate(((.06, .1), (.12, .06), (.2, .07))):
        lo = np.array([x0 - d, min(y_face, y_face + n_out * d), z - .23 + k * .07]); hi = np.array([x1 + d, max(y_face, y_face + n_out * d), z - .23 + k * .07 + h])
        cbox(ctx.stone if STY != "white" else ctx.plaster, lo, hi, {"all": C_STONE if STY != "white" else C_TRIM}, A=.15)


def gable_tri(x, x_in, y0, y1, zb, zr):
    """triangular gable wall (rendered) between the eaves at zb and the ridge zr"""
    ym = (y0 + y1) / 2
    for xx, flip in ((x, x > x_in), (x_in, x_in > x)):
        V = [(xx, y0 - .02, zb), (xx, y1 + .02, zb), (xx, ym, zr)]
        ctx.plaster.add(V, [[0, 1, 2] if flip else [2, 1, 0]], [(v[1], v[2]) for v in V], (*C_EXT, .05))
    for (ya, za), (yb, zb_) in (((y0 - .02, zb), (ym, zr)), ((ym, zr), (y1 + .02, zb))):
        V = [(x, ya, za), (x_in, ya, za), (x_in, yb, zb_), (x, yb, zb_)]
        ctx.plaster.add(V, [[0, 1, 2, 3], [3, 2, 1, 0]], [(v[0], v[2]) for v in V], (*C_EXT, .05))
    ctx.hull([(x, y0, zb), (x_in, y0, zb), (x, y1, zb), (x_in, y1, zb), (x, ym, zr), (x_in, ym, zr)])


if ROOF in ("gable", "hip"):
    D_ = (Y1 - Y0) / 2 + OV; ZR = ZE + .12 + (D_ - .0) * math.tan(PITCH)
    vl = D_ / math.cos(PITCH)
    for sgn in (1, -1):                                                        # front (sgn = 1: from Y0 up), back
        ye = Y0 - OV if sgn > 0 else Y1 + OV
        O = np.array([X0 - (OV if ROOF == "hip" else .25), ye, ZE + .12 - OV * math.tan(PITCH) * 0])
        uax = np.array([1., 0, 0]); vax = np.array([0, sgn * math.cos(PITCH), math.sin(PITCH)])
        U = (X1 - X0) + 2 * (OV if ROOF == "hip" else .25)
        if ROOF == "hip":
            vmax = lambda u, U=U: min(D_, u, U - u) / math.cos(PITCH)
        else:
            vmax = lambda u: vl
        if sgn < 0: O = O + uax * U; uax = -uax
        tile_face(O, uax, vax, U, vmax, col_seed=SEED + (sgn > 0))
    xa, xb = (X0 - OV + D_, X1 + OV - D_) if ROOF == "hip" else (X0 - .25, X1 + .25)
    if xa > xb: xa = xb = (X0 + X1) / 2
    if xb > xa: ridge((xa, (Y0 + Y1) / 2, ZR + .06), (xb, (Y0 + Y1) / 2, ZR + .06))
    if ROOF == "hip":
        for xc, sx_ in ((X0 - OV, 1), (X1 + OV, -1)):                          # hip ridges + the two end slopes
            for sy in (1, -1):
                ridge((xc, (Y0 - OV) if sy > 0 else (Y1 + OV), ZE + .2), (xa if sx_ > 0 else xb, (Y0 + Y1) / 2, ZR + .06), .1)
            O = np.array([xc, Y1 + OV if sx_ > 0 else Y0 - OV, ZE + .12]); uax = np.array([0, -1. if sx_ > 0 else 1., 0]); vax = np.array([sx_ * math.cos(PITCH), 0, math.sin(PITCH)])
            U = (Y1 - Y0) + 2 * OV
            tile_face(O, uax, vax, U, lambda u, U=U: min(u, U - u, (X1 - X0) / 2 + OV) / math.cos(PITCH), col_seed=SEED + 3)
    else:
        for xg, xin in ((X0, X0 + WT), (X1, X1 - WT)): gable_tri(xg, xin, Y0, Y1, ZE, ZR - .05)
        for xg in (X0 - .25, X1 + .25):                                         # verge: mortared edge tiles
            for sgn in (1, -1):
                ye = Y0 - OV if sgn > 0 else Y1 + OV
                B.tube_path(ctx.plaster, [(xg, ye, ZE + .12), (xg, (Y0 + Y1) / 2, ZR)], .05, 6, (.88, .86, .8, .3))
    # eaves: rafter ends + soffit, or a moulded cornice
    for y_face, n_out in ((Y0, -1), (Y1, 1)):
        if EAVE == "rafters": rafters(y_face, n_out, X0 - (OV if ROOF == "hip" else .2), X1 + (OV if ROOF == "hip" else .2), ZE + .1, OV)
        else: cornice(y_face, n_out, X0, X1, ZE + .1)
    ctx.hull([(x, y, ZE) for x in (X0 - OV, X1 + OV) for y in (Y0 - OV, Y1 + OV)] + [(x, (Y0 + Y1) / 2, ZR + .1) for x in (X0, X1)])
    if NT and ROOF == "hip":                                                     # boarded soffit under the hip ends too (deep photo-type eaves)
        for xa_, xb_ in ((X0 - OV, X0), (X1, X1 + OV)):
            cbox(ctx.timber, (xa_, Y0 - OV, ZE + .08), (xb_, Y1 + OV, ZE + .1), {"all": (.58, .4, .24)}, A=.2)
elif ROOF == "lean":                                                            # mono-pitch falling to the back, front parapet
    LP = math.radians(9); D_ = (Y1 - Y0) + OV; ZR = ZE + .12 + D_ * math.tan(LP)
    O = np.array([X1 + .1, Y1 + OV, ZE + .12]); uax = np.array([-1., 0, 0]); vax = np.array([0, -math.cos(LP), math.sin(LP)])
    tile_face(O, uax, vax, X1 - X0 + .2, lambda u: D_ / math.cos(LP), col_seed=SEED)
    cbox(ctx.plaster, (X0, Y0, ZE), (X1, Y0 + WT, ZR + .3), {"all": C_EXT}, damp_z=None); ctx.ucxb((X0, Y0, ZE), (X1, Y0 + WT, ZR + .3))
    cbox(ctx.stone if STY != "white" else ctx.plaster, (X0 - .03, Y0 - .05, ZR + .3), (X1 + .03, Y0 + WT + .03, ZR + .36), {"all": C_STONE if STY != "white" else C_TRIM})
    for xs_, xi in ((X0, X0 + WT), (X1 - WT, X1)):                              # trapezoid side walls
        V = [(xs_, Y0 + WT, ZE), (xs_, Y1, ZE), (xs_, Y1, ZE + .12), (xs_, Y0 + WT, ZR + .1)]
        for xx, fl in ((xs_, True), (xs_ + WT, False)):
            Vv = [(xx, v[1], v[2]) for v in V]; ctx.plaster.add(Vv, [[0, 1, 2, 3] if fl else [3, 2, 1, 0]], [(v[1], v[2]) for v in Vv], (*C_EXT, .05))
    if EAVE == "rafters": rafters(Y1, 1, X0 - .1, X1 + .1, ZE + .1, OV)
    else: cornice(Y1, 1, X0, X1, ZE + .1)
    ctx.hull([(x, y, z) for x in (X0, X1) for (y, z) in ((Y0, ZR + .36), (Y1 + OV, ZE), (Y0, ZE), (Y1 + OV, ZE + .2))])
else:                                                                           # flat roof terrace: baluster parapet front, solid elsewhere
    cbox(ctx.conc, (X0 + WT, Y0 + WT, ZE), (X1 - WT, Y1 - WT, ZE + .06), {"all": (.75, .5, .38)}, A=.2)          # tiled terrace finish
    if NT and "terrace_all" in FEAT:                                            # photo pink_arcade: balusters on every street side, marès pier caps
        H.railing(ctx, [(X0 + .12, Y1 - .12), (X0 + .12, Y0 + .12), (X1 - .12, Y0 + .12)] if SIDE else [(X0 + .12, Y0 + .12), (X1 - .12, Y0 + .12)], ZE, (0, 0, 0), "baluster", h=.95, conc_col=C_STONE)
        for (p, q) in ((((X1 - WT, Y0 + .25), (X1, Y1 - WT)), ((X0, Y1 - WT), (X1, Y1))) + ((((X0, Y0 + .25), (X0 + WT, Y1 - WT)),) if not SIDE else ())):
            cbox(ctx.plaster, (*p, ZE), (*q, ZE + .95), {"all": C_EXT}); ctx.ucxb((*p, ZE), (*q, ZE + .95))
            cbox(ctx.stone, (p[0] - .03, p[1] - .03, ZE + .95), (q[0] + .03, q[1] + .03, ZE + 1.0), {"all": C_STONE})
    elif NT and NT.get("FSOLID"):                                               # plain rendered parapet all round (apartment block, white balcony house)
        for (p, q) in (((X0, Y0), (X1, Y0 + WT)), ((X0, Y0 + WT), (X0 + WT, Y1 - WT)), ((X1 - WT, Y0 + WT), (X1, Y1 - WT)), ((X0, Y1 - WT), (X1, Y1))):
            cbox(ctx.plaster, (*p, ZE), (*q, ZE + 1.0), {"all": C_EXT}); ctx.ucxb((*p, ZE), (*q, ZE + 1.0))
            cbox(ctx.plaster, (p[0] - .02, p[1] - .02, ZE + 1.0), (q[0] + .02, q[1] + .02, ZE + 1.05), {"all": C_TRIM})
    else: H.railing(ctx, [(X0 + .12, Y0 + .12), (X1 - .12, Y0 + .12)], ZE, (0, 0, 0), "baluster", h=.95, conc_col=C_TRIM if STY == "white" else C_STONE)
    for (p, q) in (() if NT and ("terrace_all" in FEAT or NT.get("FSOLID")) else (((X0, Y0 + .25), (X0 + WT, Y1 - WT)), ((X1 - WT, Y0 + .25), (X1, Y1 - WT)), ((X0, Y1 - WT), (X1, Y1)))):   # sides stop at the back parapet (no coplanar end faces)
        cbox(ctx.plaster, (*p, ZE), (*q, ZE + .95), {"all": C_EXT}); ctx.ucxb((*p, ZE), (*q, ZE + .95))
        cbox(ctx.stone if STY != "white" else ctx.plaster, (p[0] - .03, p[1] - .03, ZE + .95), (q[0] + .03, q[1] + .03, ZE + 1.0), {"all": C_STONE if STY != "white" else C_TRIM})
    for x in np.linspace(X0 + .6, X1 - .6, 2):                                  # gargoyle spouts through the back parapet
        B.tube_path(ctx.pvc, [(x, Y1 - .1, ZE + .1), (x, Y1 + .3, ZE + .08)], .035, 8, (.6, .62, .62, .3))
    ZR = ZE + 1.0
    # access (W3 review): galvanised cat ladder up the back wall from the yard, over the parapet, grab hoops
    _bo = [o for o in facade_ops("back", NS - 1)] + [o for s_ in range(NS - 1) for o in facade_ops("back", s_)]
    for lu in [X1 - .45 - k * .3 for k in range(int((X1 - X0 - .9) / .3))]:
        u_ = X1 - lu
        if all(not (o[0] - .35 < u_ < o[1] + .35) for o in _bo): break
    ly = Y1 + .2; zt_ = ZE + 1.0
    for dx in (-.22, .22):
        B.tube_path(ctx.galv, [(lu + dx, ly, .05), (lu + dx, ly, zt_ + .9), (lu + dx, Y1 - .05, zt_ + 1.05), (lu + dx, Y1 - .45, zt_ + .6), (lu + dx, Y1 - .45, ZE + .06)], .022, 8, (.62, .63, .63, .4))
        for zz in (1.0, ZE - .8): B.tube_path(ctx.galv, [(lu + dx, ly, zz), (lu + dx, Y1 + .01, zz)], .014, 6, (.6, .6, .6, .4))      # wall brackets
    for zz in np.arange(.35, zt_ + .6, .3): B.tube_path(ctx.galv, [(lu - .22, ly, zz), (lu + .22, ly, zz)], .014, 6, (.62, .63, .63, .4))
    ctx.ucxb((lu - .25, Y1 + .02, 0), (lu + .25, ly + .05, zt_ + 1.0))
    s_ = bpy.data.objects.new("SOCKET_Ladder_Bottom", None); bpy.context.scene.collection.objects.link(s_); s_.location = (lu, ly + .3, 0)
    s_ = bpy.data.objects.new("SOCKET_Ladder_Top", None); bpy.context.scene.collection.objects.link(s_); s_.location = (lu, Y1 - .6, ZE + .06)


# ------------------------------------------------------------------ façade fittings (Session M's kit: shutters, doors, lantern, letterbox, step, planter, washline)
PROPS = []                                                                       # (kind, seed, world matrix) – placed as real objects + listed in rooms.json


def mplace(kind, seed, org, u, n, z):
    """place one of M's façade pieces: origin = opening centre on the outer face at the sill; local x = along the wall,
    local -y = outward (street)"""
    R = np.column_stack([u, -n, [0, 0, 1.]])
    M = Matrix(((R[0][0], R[0][1], R[0][2], org[0]), (R[1][0], R[1][1], R[1][2], org[1]), (R[2][0], R[2][1], R[2][2], org[2] + z), (0, 0, 0, 1)))
    objs = GF.build(kind, seed)
    for o in objs:
        o.matrix_world = M @ o.matrix_world; o.name = f"MED_{kind}_{len(PROPS)}_{o.name}"
    PROPS.append({"piece": kind, "seed": seed, "loc": [round(float(v), 3) for v in (org[0], org[1], org[2] + z)], "rot_z": round(math.degrees(math.atan2(u[1], u[0])), 1)})


def casement(c, u, n, w, h, depth):
    """timber casement window inside the reveal: frame, two glazed leaves (one ajar inwards), glazing bars"""
    c = np.asarray(c, float) - n * depth; col = (*srgb(rng.choice(["#f2f0ea", "#5a3a24", "#e8e4da"])), .1)
    def P(du, dz, dn=0): return c + u * du + np.array([0, 0, dz]) - n * dn
    for a_, b_ in (((-w / 2, .02), (w / 2, .02)), ((-w / 2, h - .02), (w / 2, h - .02)), ((-w / 2 + .02, 0), (-w / 2 + .02, h)), ((w / 2 - .02, 0), (w / 2 - .02, h))):
        B.sweep(ctx.paintwood, np.array([P(*a_), P(*b_)]), B.rect(.06, .07), col, up=tuple(n))
    for k, (sgn, ang) in enumerate(((-1, rng.choice([0, 0, 25])), (1, 0))):
        hinge = P(sgn * (w / 2 - .05), .05); lw = w / 2 - .06; t = math.radians(ang)
        d = -u * sgn * math.cos(t) - n * math.sin(t)
        for (pa, pb) in ((0, 0), (lw, lw)): B.sweep(ctx.paintwood, np.array([hinge + d * pa, hinge + d * pb + [0, 0, h - .1]]), B.rect(.05, .05), col, up=tuple(np.cross(d, [0, 0, 1])))
        for z in (0, h * .5, h - .1): B.sweep(ctx.paintwood, np.array([hinge + [0, 0, z], hinge + d * lw + [0, 0, z]]), B.rect(.04, .04), col, up=(0, 0, 1))
        Q = [hinge + [0, 0, .02], hinge + d * lw + [0, 0, .02], hinge + d * lw + [0, 0, h - .12], hinge + [0, 0, h - .12]]
        ctx.glass.add(Q, [[0, 1, 2, 3], [3, 2, 1, 0]], [(0, 0)] * 4, (.7, .78, .78, 0))


G_GRILLE = srgb("#1e1e1c")
for s in range(NS):
    for key in ("front", "back", "left", "right"):
        org, u, n, L = H.facade(RECT, key)
        zb = 0 if s == 0 else zfl(s) - SL
        fo = facade_ops(key, s)
        for (u0, u1, v0, v1, kind, oo) in fo:
            w, h = u1 - u0, v1 - v0; zz = zb + v0; fit = oo["fit"]
            c_out = org + u * (u0 + u1) / 2 + [0, 0, zz]; c_in = c_out - n * WT
            if kind == "window":
                if fit == "win":
                    casement(c_out, u, n, w, h, .12)
                    st = rng.choices(["shut_win_open", "shut_win_half", "shut_win_closed"], [6, 2, 2])[0]
                    mplace(st, SHUT_SEED, c_out, u, n, 0)
                    if s == 0 and key == "front" and rng.random() < .7: H.grille(ctx, c_out - n * .16, u, w, h, n, G_GRILLE, 0)   # reja in the reveal
                else:                                                                 # bath / stair windows: small louvre + bars
                    H.louvre(ctx, c_out - n * .1, u, w, h, n); H.grille(ctx, c_out - n * .03, u, w, h, n, G_GRILLE, 0)
                if (STY in ("sand", "ochre") or (NT and NT.get("SURR"))) and fit == "win":   # sandstone surround + sill
                    for (a_, b_) in (((-w / 2 - .12, h), (w / 2 + .12, h + .14)), ((-w / 2 - .12, -.04), (-w / 2, h)), ((w / 2, -.04), (w / 2 + .12, h))):
                        lo = c_out + u * a_[0] + [0, 0, a_[1]]; hi = c_out + u * b_[0] + [0, 0, b_[1]] + n * .02
                        cbox(ctx.stone, np.minimum(lo, hi), np.maximum(lo, hi), {"all": C_STONE}, A=.15)
                C.sill_drip(ctx, c_out, u, n, w, C_STONE if STY != "white" else (.88, .87, .84))
                C.streak(ctx, c_out + n * .02 - [0, 0, .08], u, n, w * .8, rng.uniform(.3, .8), C_EXT, rng, A=.3)
            elif kind == "door":
                if fit == "entry":
                    mplace("door", SEED % 3, c_out, u, n, 0)
                    q0 = org + u * (u0 - .25); q1 = org + u * (u1 + .25) + n * .32 + [0, 0, FL]
                    C.worn_step(ctx, np.minimum(q0, q1), np.maximum(q0, q1), (.84, .8, .72), rng); ctx.ucxb(np.minimum(q0, q1), np.maximum(q0, q1))
                    mplace("lantern", 1, org + u * (u1 + .35), u, n, zz + 2.0)
                    mplace("letterbox", 1, org + u * (u0 - .4), u, n, zz + 1.25)
                elif fit == "balcdoor":
                    H.door_leaf(ctx, c_out - n * .14 - u * w / 2, u, -n, srgb("#f2f0ea"), open_deg=rng.choice([0, 70]), w=w - .04, h=h - .03, glazed=True)
                    mplace(rng.choice(["shut_door_open", "shut_door_open", "shut_door_closed"]), SHUT_SEED, c_out, u, n, 0)
                elif fit == "backdoor":
                    mplace("door", (SEED + 1) % 3, c_out, u, n, 0)
                elif fit == "garage" and "steel_garage" in FEAT:                     # plain steel double garage door (photo white_balcony_blue_shutters)
                    gc = srgb("#5aa0d0")
                    for sg in (-1, 1):
                        C.wbox(ctx.steel, c_out, u, n, sg * w / 2 if sg < 0 else .005, -.005 if sg < 0 else w / 2, 0, h, -.1, -.06, gc, .2)
                        for k in range(1, 4): C.wbox(ctx.steel, c_out, u, n, (sg * w / 2) * (1 - k / 4) - .015, (sg * w / 2) * (1 - k / 4) + .015, .05, h - .05, -.06, -.05, tuple(c * .9 for c in gc), .25)
                    C.wbox(ctx.steel, c_out, u, n, -.12, -.02, 1.05, 1.1, -.05, -.03, (.6, .6, .6))
                    lo = c_out + u * (-w / 2) - n * .12; hi = c_out + u * (w / 2) + [0, 0, h]; ctx.ucxb(np.minimum(lo, hi), np.maximum(lo, hi))
                elif fit == "garage":
                    mplace("roller", SEED % 3, c_out, u, n, 0)
                    lo = c_out + u * (-w / 2) - n * .12; hi = c_out + u * (w / 2) + [0, 0, h]          # closed roller: blocks like the wall
                    ctx.ucxb(np.minimum(lo, hi), np.maximum(lo, hi))
                elif fit == "roller":                                                 # épicerie: shutter rolled up, glazed shop front
                    for k, du in enumerate((-w / 2 + .03, -.45, .45, w / 2 - .03)):
                        B.sweep(ctx.alu, np.array([c_out + u * du - n * .1, c_out + u * du - n * .1 + [0, 0, h]]), B.rect(.05, .08), (.3, .3, .3, .1), up=tuple(n))
                    for (pa, pb) in ((-w / 2 + .05, -.47), (.47, w / 2 - .05)):
                        Q = [c_out + u * pa - n * .1 + [0, 0, .05], c_out + u * pb - n * .1 + [0, 0, .05], c_out + u * pb - n * .1 + [0, 0, h - .05], c_out + u * pa - n * .1 + [0, 0, h - .05]]
                        ctx.glass.add(Q, [[0, 1, 2, 3], [3, 2, 1, 0]], [(0, 0)] * 4, (.7, .78, .78, 0))
                    H.door_leaf(ctx, c_out - n * .1 - u * .43, u, -n, (.3, .3, .3), open_deg=60, w=.86, h=h - .05, glazed=True)
                    C.wbox(ctx.galv, c_out, u, n, -w / 2 - .06, w / 2 + .06, h + .02, h + .3, 0, .28, (.62, .64, .63), .3)      # shutter coil box
                    for sg in (-1, 1): C.wbox(ctx.galv, c_out, u, n, sg * (w / 2 + .03) - .03, sg * (w / 2 + .03) + .03, 0, h, 0, .07, (.62, .64, .63), .3)
                    C.wbox(ctx.paint, c_out, u, n, -w / 2 - .3, w / 2 + .3, h + .35, h + .8, 0, .04, srgb(rng.choice(["#2f5f8a", "#3d5a3a", "#8a2a20"])), .2)   # blank sign board
            elif kind == "opening" and fit == "arch" and NT:                          # photo types: spandrel cut exactly on the curve + smooth intrados
                r_ = w / 2; zs = zz + h - r_; cx = org + u * (u0 + u1) / 2; ztop_ = zz + h      # (the wall above the opening is hlib's)
                for i in range(24):
                    t0, t1 = math.pi * i / 24, math.pi * (i + 1) / 24
                    a0, a1 = cx + u * r_ * math.cos(t0) + [0, 0, zs + r_ * math.sin(t0)], cx + u * r_ * math.cos(t1) + [0, 0, zs + r_ * math.sin(t1)]
                    for dn, fl in ((0.0, True), (-WT, False)):
                        V = [a0 + n * dn, a1 + n * dn, np.array([*(a1 + n * dn)[:2], ztop_]), np.array([*(a0 + n * dn)[:2], ztop_])]
                        nrm = np.cross(V[1] - V[0], V[3] - V[0]); ok = (np.dot(nrm, n) > 0) == fl
                        ctx.plaster.add(V, [[0, 1, 2, 3] if ok else [3, 2, 1, 0]], [(float(np.dot(v_, u)), v_[2]) for v_ in V], (*C_EXT, 0))
                    V = [a0, a1, a1 - n * WT, a0 - n * WT]; nrm = np.cross(V[1] - V[0], V[3] - V[0])
                    ctx.plaster.add(V, [[0, 1, 2, 3] if nrm[2] < 0 else [3, 2, 1, 0]], [(math.pi * r_ * i / 24, 0), (math.pi * r_ * (i + 1) / 24, 0), (math.pi * r_ * (i + 1) / 24, WT), (math.pi * r_ * i / 24, WT)], (*C_EXT, 0))
                    q0 = cx + u * (r_ + .02) * math.cos(t0) + [0, 0, zs + (r_ + .02) * math.sin(t0)]; q1 = cx + u * (r_ + .02) * math.cos(t1) + [0, 0, zs + (r_ + .02) * math.sin(t1)]
                    B.sweep(ctx.stone, np.array([q0 + n * .01, q1 + n * .01]), B.rect(.025, .2), (*C_STONE, .15), up=tuple(n))
                ctx.ucxb(np.minimum(cx + u * -r_ - n * WT + [0, 0, zs + r_ * .7], cx + u * r_ + [0, 0, zz + h]), np.maximum(cx + u * -r_ - n * WT + [0, 0, zs + r_ * .7], cx + u * r_ + [0, 0, zz + h]))
                if s >= 1: H.railing(ctx, [tuple((org + u * (u0 + .05))[:2] - n[:2] * WT / 2), tuple((org + u * (u1 - .05))[:2] - n[:2] * WT / 2)], zz, (0, 0, 0), "baluster", h=.95, conc_col=C_STONE)
            elif kind == "opening" and fit == "arch":                                 # spandrel of the round arch + stone voussoir ring
                r_ = w / 2; zs = zz + h - r_; cx = org + u * (u0 + u1) / 2
                for i in range(16):
                    t0, t1 = math.pi * i / 16, math.pi * (i + 1) / 16
                    xa_, xb_ = r_ * math.cos(t1), r_ * math.cos(t0)
                    za_ = zs + r_ * min(math.sin(t0), math.sin(t1))
                    lo = cx + u * min(xa_, xb_) - n * WT + [0, 0, za_]; hi = cx + u * max(xa_, xb_) + [0, 0, zz + h]
                    cbox(ctx.plaster, np.minimum(lo, hi), np.maximum(lo, hi), {"all": C_EXT})
                    if STY != "white":
                        q0 = cx + u * (r_ + .02) * math.cos(t0) + [0, 0, zs + (r_ + .02) * math.sin(t0)]; q1 = cx + u * (r_ + .02) * math.cos(t1) + [0, 0, zs + (r_ + .02) * math.sin(t1)]
                        B.sweep(ctx.stone, np.array([q0 + n * .01, q1 + n * .01]), B.rect(.025, .2), (*C_STONE, .15), up=tuple(n))
                ctx.ucxb(np.minimum(cx + u * -r_ - n * WT + [0, 0, zs + r_ * .7], cx + u * r_ + [0, 0, zz + h]), np.maximum(cx + u * -r_ - n * WT + [0, 0, zs + r_ * .7], cx + u * r_ + [0, 0, zz + h]))


# ------------------------------------------------------------------ balcony on the first floor (baluster railing)
if BALC and not (NT and NT["BALC"] in ("arcade", "posts", "apt")):
    bx0, bx1 = (XM0 - .1, XM1 + .1) if not (NT and NT["BALC"] == "small") else (mx - 1.3, mx + 1.3); bd = 1.0; zb_ = zfl(1)
    cbox(ctx.conc, (bx0, Y0 - bd, zb_ - .17), (bx1, Y0, zb_ - .03), {"all": C_TRIM, "pz": (.8, .79, .76)}); ctx.ucxb((bx0, Y0 - bd, zb_ - .17), (bx1, Y0, zb_ - .03))
    cbox(ctx.tile, (bx0 + .02, Y0 - bd + .02, zb_ - .03), (bx1 - .02, Y0, zb_ - .015), {"all": C_FLOOR})
    cbox(ctx.conc, (bx0 - .04, Y0 - bd - .04, zb_ - .22), (bx1 + .04, Y0, zb_ - .17), {"all": C_TRIM})          # moulded edge
    H.railing(ctx, [(bx0 + .1, Y0), (bx0 + .1, Y0 - bd + .1), (bx1 - .1, Y0 - bd + .1), (bx1 - .1, Y0)], zb_ - .015, (0, 0, 0), "baluster", h=.95,
              conc_col=C_TRIM if STY in ("white", "salmon") else C_STONE)
    for x in (bx0 + .2, bx1 - .2): B.tube_path(ctx.pvc, [(x, Y0 - bd + .15, zb_ - .02), (x, Y0 - bd - .15, zb_ - .06)], .02, 8, (.6, .62, .62, .3))
    C.streak(ctx, np.array([(bx0 + bx1) / 2, Y0 - bd - .04, zb_ - .22]), np.array([1., 0, 0]), np.array([0, -1., 0]), bx1 - bx0 - .4, .1, C_TRIM, rng, A=.3)


# ------------------------------------------------------------------ plinth, quoins, services, wear
def crazy_paving(org, u, n, a_, b_, z0, z1):
    """irregular limestone slabs set in white mortar (photo porch_crazypaving_shutters): mortar coat + jittered slabs 8 mm proud"""
    C.wbox(ctx.plaster, org, u, n, a_, b_, z0, z1, 0, .012, (.9, .89, .85), .15)
    prng = random.Random(int(abs(org[0] * 13 + org[1] * 7 + a_ * 31)) + SEED)
    nz = max(2, int((z1 - z0) / .2)); nu = max(1, int((b_ - a_) / .27))
    J = [[(a_ + (b_ - a_) * i / nu + (prng.uniform(-.09, .09) if 0 < i < nu else 0), z0 + (z1 - z0) * j / nz + (prng.uniform(-.07, .07) if 0 < j < nz else 0)) for j in range(nz + 1)] for i in range(nu + 1)]
    for i in range(nu):
        for j in range(nz):
            q = [J[i][j], J[i + 1][j], J[i + 1][j + 1], J[i][j + 1]]; cx_, cz_ = np.mean([p[0] for p in q]), np.mean([p[1] for p in q])
            q = [(cx_ + (p[0] - cx_) * .86, cz_ + (p[1] - cz_) * .84) for p in q]
            col = srgb(prng.choice(["#dccb9f", "#cfb98c", "#e3d4ae", "#c8ad80", "#d6c39a", "#bfae8c", "#e0c79a"]))
            V = [np.asarray(org, float) + u * p[0] + n * .02 + [0, 0, p[1]] for p in q]
            ctx.stone.add(V, [[0, 1, 2, 3] if np.cross(u, [0, 0, 1]) @ n < 0 else [3, 2, 1, 0]], [(p[0], p[1]) for p in q], (*col, .15))


for key in ("front", "back", "left", "right"):
    if key == "right" or (key == "left" and SIDE == 0): continue
    org, u, n, L = H.facade(RECT, key)
    fo = facade_ops(key, 0); doors = [o for o in fo if o[4] in ("door", "opening")]
    cuts = [0.0] + [v for o in sorted(doors) for v in (o[0], o[1])] + [L]
    ph = .85 if PLINTH != "render" else .45
    for ua, ub in zip(cuts[0::2], cuts[1::2]):
        if ub - ua < .05: continue
        if PLINTH == "crazy": crazy_paving(org, u, n, ua, ub, 0, ph)
        elif PLINTH == "stone":
            for k, z in enumerate(np.arange(0, ph, .28)):
                s0 = ua - (.2 if k % 2 else 0)
                for x in np.arange(s0, ub, .55):
                    xa_, xb_ = max(ua, x), min(ub, x + .53)
                    if xb_ - xa_ > .05: C.wbox(ctx.stone, org, u, n, xa_, xb_, z, min(ph, z + .27), 0, .025, tuple(np.array(C_STONE) * rng.uniform(.88, 1.04)), .2)
        else: C.wbox(ctx.plaster, org, u, n, ua, ub, 0, ph, 0, .008, (.62, .6, .57), .4)
    C.paint_chips(ctx, org, u, n, L, ph + .2, ZTOP - .3, tuple(np.array(C_EXT) * .85), rng, rng.randint(3, 8))
    C.crack_line(ctx, org, u, n, L, zfl(1) - SL + .05 if NS > 1 else ZTOP - .1, rng)
    for k in range(rng.randint(2, 5)):
        s_ = rng.uniform(.4, L - .4)
        fo_ = fo + ([o for s2 in range(1, NS) for o in facade_ops(key, s2) if o[4] == "opening"] if NT else [])   # (photo types: never down a loggia arch)
        if not any(o[0] - .3 < s_ < o[1] + .3 for o in fo_): C.streak(ctx, org + u * s_ + [0, 0, ZE - .02], u, n, rng.uniform(.3, .7), rng.uniform(.8, 2.0), C_EXT, rng, A=.3)
    if STY in ("sand", "ochre") and key == "front":                                 # sandstone quoins at the front corners
        for k, z in enumerate(np.arange(ph, ZE - .1, .3)):
            for ua, sg in ((0, 1), (L, -1)):
                ln = .45 if k % 2 else .3
                C.wbox(ctx.stone, org, u, n, min(ua, ua + sg * ln), max(ua, ua + sg * ln), z + .01, z + .29, 0, .025, tuple(np.array(C_STONE) * rng.uniform(.9, 1.03)), .15)
# meter box set into the front wall (grey GRP door flush, photo banana_balustrade), downpipes, cables, AC, aerial, chimney
org, u, n, L = H.facade(RECT, "front")
mx_ = (XM0 + .5 - X0) if SERV_RIGHT else (XM1 - .5 - X0)
C.wbox(ctx.paint, org, u, n, mx_ - .25, mx_ + .25, .5, 1.25, -.02, .006, (.78, .78, .76), .25)
for k in range(9): C.wbox(ctx.paint, org, u, n, mx_ - .2, mx_ + .2, .6 + k * .07, .62 + k * .07, .006, .01, (.68, .68, .66))
s_ = bpy.data.objects.new("SOCKET_Drop", None); bpy.context.scene.collection.objects.link(s_); s_.location = tuple(org + u * (mx_) + n * .1 + [0, 0, ZE - .3])
B.tube_path(ctx.dark, [org + n * .03 + [0, 0, ZE - .35], org + u * L + n * .03 + [0, 0, ZE - .35]], .007, 5, (.05, .05, .05, 0))      # cable along the façade
B.tube_path(ctx.dark, [org + u * mx_ + n * .03 + [0, 0, ZE - .35], org + u * mx_ + n * .03 + [0, 0, 1.25]], .009, 5, (.05, .05, .05, 0))
for k in np.arange(.5, L, 1.0): C.wbox(ctx.galv, org, u, n, k - .01, k + .01, ZE - .37, ZE - .33, 0, .04, (.5, .5, .5))
if ROOF != "flat":
    for x in (X0 + .15, X1 - .15) if SIDE else ((X0 + .15,) if not SERV_RIGHT else (X1 - .15,)):
        B.tube_path(ctx.galv, [(x, Y0 - OV + .05, ZE + .05), (x, Y0 - .06, ZE - .2), (x, Y0 - .06, .2), (x, Y0 - .2, .05)], .04, 10, (.55, .57, .58, .3))
    if rng.random() < .6:                                                        # half-round zinc gutter along the front eave
        B.tube_path(ctx.galv, [(X0 - .25, Y0 - OV + .05, ZE + .05), (X1 + .25, Y0 - OV + .05, ZE + .05)], .06, 8, (.6, .62, .63, .3))
C.split_ac(ctx, np.array([(XM0 + XM1) / 2, Y1, zfl(min(1, NS - 1)) + 2.0]), np.array([-1., 0, 0]), np.array([0, 1., 0]), rng)
B.tube_path(ctx.galv, [(X1 - 1.0, Y1 - 1.0, ZR - .1), (X1 - 1.0, Y1 - 1.0, ZR + 2.0)], .02, 8, (.7, .7, .7, .2))     # TV aerial mast + Yagi
for k in range(6): B.tube_path(ctx.alu, [(X1 - 1.0 + .1 * k - .25, Y1 - 1.3, ZR + 1.9), (X1 - 1.0 + .1 * k - .25, Y1 - .7, ZR + 1.9)], .005, 4, (.8, .8, .8, .1))
B.tube_path(ctx.alu, [(X1 - 1.25, Y1 - 1.0, ZR + 1.9), (X1 - .7, Y1 - 1.0, ZR + 1.9)], .008, 4, (.8, .8, .8, .1))
if (rng.random() < .55 or "chimney" in FEAT) and ROOF != "flat":             # chimney stack with a tiled hood
    cx_, cy_ = (XM0 + .5, Y1 - 1.0)
    zc0 = ZE + .12 + max(0, (Y1 - cy_)) * math.tan(PITCH) - .2
    cbox(ctx.plaster, (cx_ - .25, cy_ - .25, ZE), (cx_ + .25, cy_ + .25, ZR + .6), {"all": C_EXT}); ctx.ucxb((cx_ - .25, cy_ - .25, ZE), (cx_ + .25, cy_ + .25, ZR + .6))
    for sx_ in (-1, 1): cbox(ctx.plaster, (cx_ + sx_ * .2 - .05, cy_ - .25, ZR + .6), (cx_ + sx_ * .2 + .05, cy_ + .25, ZR + .85), {"all": C_EXT})
    for sg in (-1, 1):
        V = [(cx_ - .35, cy_, ZR + 1.0), (cx_ + .35, cy_, ZR + 1.0), (cx_ + .35, cy_ + sg * .35, ZR + .85), (cx_ - .35, cy_ + sg * .35, ZR + .85)]
        ctx.tiles.add(V, [[0, 1, 2, 3], [3, 2, 1, 0]], [(v[0], v[1]) for v in V], (*C_TILE[1], .3))
    C.streak(ctx, np.array([cx_, cy_ - .25, ZR + .6]), np.array([1., 0, 0]), np.array([0, -1., 0]), .4, .8, (.3, .28, .25), rng, A=.6)


# ------------------------------------------------------------------ front patio, back yard
YP = -PD / 2                                                                    # plot front line
def wicker_chair(x, y, yaw):
    f = C.F(x, y, FL, yaw); col = srgb("#a8804a")
    for sx_ in (-.22, .22):
        for sy_ in (-.2, .2): f.tube(ctx.timber, [(sx_, sy_, 0), (sx_ * 1.05, sy_, .42)], .015, 5, col, .2)
    f.box(ctx.timber, (-.26, -.24, .38), (.26, .22, .45), col, .2)
    for k in range(9): f.tube(ctx.timber, [(-.25 + k * .0625, .22, .45), (-.25 + k * .0625, .26, .9)], .012, 4, col, .2)
    f.tube(ctx.timber, [(-.26, .26, .9), (.26, .26, .9)], .02, 6, col, .2)
    for sx_ in (-.26, .26): f.tube(ctx.timber, [(sx_, -.22, .45), (sx_, -.2, .65), (sx_, .22, .68)], .016, 5, col, .2)
    a_, b_ = f.p(-.27, -.25, 0), f.p(.27, .27, .9); ctx.ucxb(np.minimum(a_, b_), np.maximum(a_, b_))


def garden_wall_run(p0, p1, h, rough=True, gate=None):
    """rough-rendered low wall (rubble core, lime render) with a rounded coping; gate = (u0, u1) gap with a plank gate"""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float); L = np.linalg.norm(p1 - p0); d = (p1 - p0) / L; nrm = np.array([-d[1], d[0]])
    cuts = [(0, L)] if gate is None else [(0, gate[0]), (gate[1], L)]
    for ua, ub in cuts:
        if ub - ua < .05: continue
        a_ = p0 + d * ua - nrm * .1; b_ = p0 + d * ub + nrm * .1
        lo = np.array([min(a_[0], b_[0]), min(a_[1], b_[1]), 0]); hi = np.array([max(a_[0], b_[0]), max(a_[1], b_[1]), h])
        cbox(ctx.plaster, lo, hi, {"all": C_EXT}, damp_z=0, damp_amt=.35); ctx.ucxb(lo, hi)
        q0 = np.array([*(p0 + d * ua), h]); q1 = np.array([*(p0 + d * ub), h])
        B.tube_path(ctx.plaster, [q0, q1], .12, 8, (*C_EXT, .2))                                         # rounded lime coping
    if gate is not None:                                                                                  # timber plank / picket gate, two leaves
        col = (*srgb(rng.choice(["#a0582c", "#6b4528", "#3d5a3a"])), .2)
        for sg, hu in ((1, gate[0] + .03), (-1, gate[1] - .03)):
            ang = rng.choice([0, 0, 35]) * sg; t = math.radians(ang)
            dd = d * sg * math.cos(t) + np.array([0, 0]) ; dd = np.array([d[0] * sg * math.cos(t) - d[1] * math.sin(t), d[1] * sg * math.cos(t) + d[0] * math.sin(t)])
            hp = p0 + d * hu; lw = (gate[1] - gate[0]) / 2 - .04
            for zz in (.15, h - .05): B.sweep(ctx.timber, np.array([[*hp, zz], [*(hp + dd * lw), zz]]), B.rect(.07, .03), col, up=(0, 0, 1))
            for k in range(int(lw / .1)):
                q = hp + dd * (.05 + k * .1); top = h + .25 - abs(k * .1 - lw / 2) * .35
                B.sweep(ctx.timber, np.array([[*q, .05], [*q, top]]), B.rect(.06, .02), col, up=(0, 0, 1))
            B.tube_path(ctx.steel, [[*(hp + dd * (lw - .1)), h * .55], [*(hp + dd * (lw - .02)), h * .55]], .012, 6, (.15, .15, .15, .2))
        for u_ in gate:                                                                                  # gate piers
            q = p0 + d * u_; cbox(ctx.plaster, (q[0] - .15, q[1] - .15, 0), (q[0] + .15, q[1] + .15, h + .25), {"all": C_EXT}); ctx.ucxb((q[0] - .15, q[1] - .15, 0), (q[0] + .15, q[1] + .15, h + .25))


if FRONT > 0:
    cbox(ctx.tile, (X0 - (SIDE if SIDE else 0), YP + .1, 0), (X1, Y0, .03), {"all": srgb(rng.choice(["#c9a27a", "#b8957a", "#d6c3a2"]))}, A=.15)   # patio tiles
    for k in range(2): C.worn_step(ctx, (sx - .7, Y0 - .3 * (k + 1), 0), (sx + .7, Y0 - .3 * k, FL - .15 * k), (.84, .8, .72), rng)
    gx = sx if TYPE == "house" else mx
    if not NT: garden_wall_run((-PW / 2, YP + .1), (PW / 2, YP + .1), .85, gate=(gx - .6 + PW / 2, gx + .6 + PW / 2))
    for xw in ((-PW / 2 + .1,) if SIDE == 0 else (-PW / 2 + .1, X0 - .1)):
        pass
    # pergola / timber porch roof over part of the patio (photo street_house_white) or chairs under the balcony
    if rng.random() < .55 and not BALC and not NT:
        pa, pb = XM0 + .1, XM1 - .1; zp = 2.45; dp = min(FRONT - .4, 1.9)
        for x in (pa, pb): B.sweep(ctx.timber, np.array([[x, Y0 - dp, .03], [x, Y0 - dp, zp]]), B.rect(.12, .12), (.55, .36, .2, .25), up=(1, 0, 0)); ctx.ucxb((x - .06, Y0 - dp - .06, 0), (x + .06, Y0 - dp + .06, zp))
        B.sweep(ctx.timber, np.array([[pa - .2, Y0 - dp, zp + .08], [pb + .2, Y0 - dp, zp + .08]]), B.rect(.16, .08), (.55, .36, .2, .25), up=(0, 0, 1))
        for x in np.arange(pa, pb + .01, .6): B.sweep(ctx.timber, np.array([[x, Y0 - dp - .25, zp + .2], [x, Y0, zp + .45]]), B.rect(.06, .12), (.55, .36, .2, .25), up=(0, 0, 1))
        V = [(pa - .25, Y0 - dp - .3, zp + .27), (pb + .25, Y0 - dp - .3, zp + .27), (pb + .25, Y0, zp + .52), (pa - .25, Y0, zp + .52)]
        ctx.timber.add(V, [[0, 1, 2, 3], [3, 2, 1, 0]], [(v[0], v[1]) for v in V], (.6, .42, .26, .2))                # boarded roof
        tile_face(np.array([pb + .25, Y0 - dp - .3, zp + .29]), np.array([-1., 0, 0]), np.array([0, math.cos(.15), math.sin(.15)]), pb - pa + .5, lambda u: .45, col_seed=SEED + 9)
    t_ = (mx, Y0 - min(FRONT, 2.0) / 2 - .1)
    if not (NT and GARAGE):                                                       # (a garage forecourt keeps the drive free)
        cbox(ctx.timber, (t_[0] - .45, t_[1] - .3, .72), (t_[0] + .45, t_[1] + .3, .76), {"all": (.5, .34, .2)}); ctx.ucxb((t_[0] - .45, t_[1] - .3, 0), (t_[0] + .45, t_[1] + .3, .76))
        for sx_ in (-.4, .4):
            for sy_ in (-.25, .25): B.tube_path(ctx.timber, [(t_[0] + sx_, t_[1] + sy_, 0), (t_[0] + sx_, t_[1] + sy_, .72)], .02, 6, (.5, .34, .2, .2))
        for dx in (-.85, .85): wicker_chair(t_[0] + dx, t_[1], 90 if dx < 0 else 270)
    for k in range(rng.randint(2, 4)): C.pot_plant(ctx, rng.uniform(X0 + .4, X1 - .4), YP + (.45 if not NT else .8), rng, rng.uniform(.18, .3))   # (photo types: clear of the new garden walls)
else:
    if rng.random() < .5: C.pot_plant(ctx, X0 + .4 if SERV_RIGHT else X1 - .4, Y0 - .35, rng, .22)
if BACK > .5:
    cbox(ctx.conc, (-PW / 2, Y1, -.02), (PW / 2, PD / 2 - .1, .02), {"all": (.72, .7, .66)}, A=.35)
    garden_wall_run((-PW / 2, PD / 2 - .1), (PW / 2, PD / 2 - .1), 1.9)
    if BACK >= 1.0: mplace("washline", 3, np.array([mx, PD / 2 - .2, 0]), np.array([-1., 0, 0]), np.array([0, -1., 0]), 0)
    col_b = srgb("#e8742a")                                                   # orange butane bottle (12.5 kg)
    bx_, by_ = X0 + .4, Y1 + .35
    rings = [[(bx_ + rr * math.cos(t), by_ + rr * math.sin(t), z) for t in np.linspace(0, 2 * math.pi, 14, endpoint=False)] for rr, z in ((.14, 0), (.16, .04), (.16, .5), (.11, .58), (.04, .62))]
    ctx.paint.grid(np.array(rings), col=(*col_b, .3), close_v=True)
    C.water_drum(ctx, X1 - .5, Y1 + .4, srgb("#3a6aa8")) if BACK > .8 else None
    C.pot_plant(ctx, mx + .8, PD / 2 - .45, rng, .25)
for sgn in ((-1, 1) if SIDE == 0 else ()):
    pass
if SIDE > 0 and not (NT and NT.get("CORNER") is not None):                     # side passage: wall to the neighbour
    garden_wall_run((-PW / 2 + .1, YP + .1), (-PW / 2 + .1, PD / 2 - .1), 1.6)

# ------------------------------------------------------------------ Worker WZ (S25): walls, gates, porches, arcades, balconies of the photo types
VEG = []                                                                         # vegetation kit instances (rooms.json "veg_items")


import medwalls as MW
MW.init(ctx, C_EXT, C_STONE, C_TRIM, wrng if NT else random.Random(SEED * 389 + 7), crazy_paving)
obox, pier, wall_run, gate_leaves = MW.obox, MW.pier, MW.wall_run, MW.gate_leaves
PIERS = MW.PIERS


def garden_walls():
    """front (+ corner side) walls of the photo types: style, piers, gate at the entrance, chamfered or square corner"""
    style = NT.get("WALL"); h = NT.get("WALL_H", {"rubble": 1.0, "ashlar": 1.1, "render_high": 1.35, "render_low": .55}.get(style, 1.0))
    if not style: return
    yf = YP + .17; xs_ = -PW / 2 + .17; CH = NT.get("CORNER")
    ex = next(((o["a"] + o["b"]) / 2 for o in OPS if o["fit"] == "entry" and o["line"] == fx_front), sx)
    gw = 1.1 if NT.get("GATE") != "pillars" else 1.3; gpost = .45 if NT.get("GATE") == "pillars" else (.44 if style in ("baluster", "balpanel", "ashlar") else (.48 if style == "rubble" else .32))
    corner = CH is not None and SIDE > 0
    fx0 = xs_ + (CH or 0) if corner else -PW / 2
    if style == "render_low": gw = 1.6
    if corner and not CH: fx0 = -PW / 2
    runs = [((fx0, yf), (ex - gw / 2 - gpost / 2, yf)), ((ex + gw / 2 + gpost / 2, yf), (PW / 2, yf))]
    if style == "render_low" and GARAGE:                                         # open forecourt: the drive to the garage stays free
        gx_ = [((o["a"] + o["b"]) / 2, o["b"] - o["a"]) for o in OPS if o["fit"] == "garage"]
        if gx_:
            g0, g1 = min(gx_[0][0] - gx_[0][1] / 2, ex - gw / 2) - .2, max(gx_[0][0] + gx_[0][1] / 2, ex + gw / 2) + .2
            runs = [((fx0, yf), (g0, yf)), ((g1, yf), (PW / 2, yf))]
    if corner:
        runs.append(((xs_, PD / 2 - .1), (xs_, yf + (CH or .17))))
        if CH: runs.append(((xs_, yf + CH), (xs_ + CH, yf)))
    gh = (h if style not in ("baluster", "balpanel") else (1.2 if style == "baluster" else .95))
    if style != "render_low" and NT.get("GATE") == "pillars":                    # gate piers first (they win over run-end piers)
        for xg in (ex - gw / 2 - gpost / 2, ex + gw / 2 + gpost / 2): pier(xg, yf, gpost, 2.5, stone=True)
    elif style != "render_low":
        for xg in (ex - gw / 2 - gpost / 2, ex + gw / 2 + gpost / 2): pier(xg, yf, gpost, gh + .15, stone=style not in ("render_high", "breeze"))
    if corner and CH:                                                             # piers on the chamfer joints
        for (xj, yj) in ((xs_, yf + CH), (xs_ + CH, yf)): pier(xj, yj, .48, {"baluster": 1.36, "balpanel": 1.09}.get(style, h + .2), stone=style not in ("render_high", "breeze"))
    for q0, q1 in runs: wall_run(style, q0, q1, h)
    if style == "render_low": return                                             # open forecourt: no gate
    if NT.get("GATE") == "pillars":                                               # tall marès pillars – they also carry the porch beam
        for sg, hx in ((1, ex - gw / 2), (-1, ex + gw / 2)): gate_leaves((hx, yf), (sg, 0), gw / 2 - .03, 1.25, "timber")
    else:
        kind = "steel" if NT.get("GATE") == "steel" else "timber"
        ang = math.radians(wrng.choice([0, 25])); dd = np.array([math.cos(ang), -math.sin(ang)])
        gate_leaves((ex - gw / 2 + .02, yf), dd, gw - .06, min(1.2, gh), kind)
    cbox(ctx.tile, (ex - gw / 2, YP, 0), (ex + gw / 2, yf + .2, .025), {"all": srgb("#c9a27a")}, A=.15)
    return ex, yf


def porch_tile(ex, pd, pw=2.6, zh=2.95, piers=True):
    """tile porch roof in front of the entrance: dark timber beams, boarded soffit, Arab tiles, on two piers (or on the
    gate pillars at the garden wall)"""
    p = math.radians(10); zl = zh - pd * math.tan(p); x0p, x1p = ex - pw / 2, ex + pw / 2; yf_ = Y0 - pd
    if piers:
        for x in (x0p + .17, x1p - .17) + (((x0p + x1p) / 2,) if pw > 4.5 else ()): pier(x, yf_ + .17, .3, zl - .1, stone=STY != "white")
    dk = (.32, .22, .14, .25)
    B.sweep(ctx.timber, np.array([[x0p - .1, yf_ + .17, zl - .05], [x1p + .1, yf_ + .17, zl - .05]]), B.rect(.12, .16), dk, up=(0, 0, 1))
    for x in np.linspace(x0p, x1p, 4):
        B.sweep(ctx.timber, np.array([[x, yf_ - .1, zl + .05], [x, Y0, zh]]), B.rect(.08, .12), dk, up=(0, 0, 1))
    V = [(x0p - .2, yf_ - .25, zl + .09), (x1p + .2, yf_ - .25, zl + .09), (x1p + .2, Y0, zh + .1), (x0p - .2, Y0, zh + .1)]
    ctx.timber.add(V, [[0, 1, 2, 3], [3, 2, 1, 0]], [(v[0], v[1]) for v in V], (.5, .36, .22, .2))
    tile_face(np.array([x1p + .2, yf_ - .25, zl + .11]), np.array([-1., 0, 0]), np.array([0, math.cos(p), math.sin(p)]), pw + .4, lambda u: (pd + .25) / math.cos(p), col_seed=SEED + 11)
    ctx.hull([(x, y, z) for x in (x0p - .2, x1p + .2) for (y, z) in ((yf_ - .25, zl), (Y0, zh + .2), (yf_ - .25, zl + .2))])
    cbox(ctx.tile, (x0p, yf_, 0), (x1p, Y0, .03), {"all": srgb("#b8957a")}, A=.15)


def arcade(n_):
    """portico of n round arches across the front (photos villa_arcade, pink_arcade): piers, arch spandrels with a marès
    voussoir ring, the slab on top = first-floor terrace behind a vase-baluster parapet"""
    AD = min(FRONT - .4, 2.2); ya = Y0 - AD; xa0, xa1 = X0, X1; zt = zfl(1) - SL
    xs = np.linspace(xa0, xa1, n_ + 1); pw_ = .42
    for x in xs:
        cx_ = min(max(x, xa0 + pw_ / 2), xa1 - pw_ / 2)
        cbox(ctx.plaster, (cx_ - pw_ / 2, ya, 0), (cx_ + pw_ / 2, ya + pw_, zt), {"all": C_EXT}, damp_z=0, damp_amt=.3); ctx.ucxb((cx_ - pw_ / 2, ya, 0), (cx_ + pw_ / 2, ya + pw_, zt))
        if PLINTH == "crazy": crazy_paving(np.array([cx_ - pw_ / 2, ya, 0.]), np.array([1., 0, 0]), np.array([0, -1., 0]), 0, pw_, 0, .8)
    for a_, b_ in zip(xs[:-1], xs[1:]):
        a_ = max(a_, xa0 + pw_ / 2) + (pw_ / 2 if a_ > xa0 + .01 else 0); b_ = min(b_, xa1 - pw_ / 2) - (pw_ / 2 if b_ < xa1 - .01 else 0)
        a_ = a_ if a_ > xa0 + pw_ / 2 + .01 else xa0 + pw_; b_ = b_ if b_ < xa1 - pw_ - .01 else xa1 - pw_
        r_ = (b_ - a_) / 2; cxa = (a_ + b_) / 2; zs = max(1.1, zt - .3 - r_)
        for i in range(24):                                                     # spandrel faces cut exactly on the curve + a smooth intrados
            t0, t1 = math.pi * i / 24, math.pi * (i + 1) / 24
            P0 = (cxa + r_ * math.cos(t0), zs + r_ * math.sin(t0)); P1 = (cxa + r_ * math.cos(t1), zs + r_ * math.sin(t1))
            for yy, fl in ((ya, False), (ya + pw_, True)):
                V = [(P0[0], yy, P0[1]), (P1[0], yy, P1[1]), (P1[0], yy, zt), (P0[0], yy, zt)]
                ctx.plaster.add(V, [[0, 1, 2, 3] if fl else [3, 2, 1, 0]], [(v[0], v[2]) for v in V], (*C_EXT, 0))
            V = [(P0[0], ya, P0[1]), (P1[0], ya, P1[1]), (P1[0], ya + pw_, P1[1]), (P0[0], ya + pw_, P0[1])]
            ctx.plaster.add(V, [[0, 1, 2, 3]], [(math.pi * r_ * i / 24, 0), (math.pi * r_ * (i + 1) / 24, 0), (math.pi * r_ * (i + 1) / 24, pw_), (math.pi * r_ * i / 24, pw_)], (*C_EXT, 0))
            q0 = np.array([cxa + (r_ + .02) * math.cos(t0), ya - .01, zs + (r_ + .02) * math.sin(t0)]); q1 = np.array([cxa + (r_ + .02) * math.cos(t1), ya - .01, zs + (r_ + .02) * math.sin(t1)])
            B.sweep(ctx.stone, np.array([q0, q1]), B.rect(.025, .18), (*C_STONE, .15), up=(0, -1, 0))
        for x in (a_, b_ - .0): cbox(ctx.plaster, (x - .001, ya, 0), (x + .001, ya + pw_, zs), {"all": C_EXT})
        ctx.ucxb((a_, ya, zs + r_ * .7), (b_, ya + pw_, zt))
    cbox(ctx.conc, (xa0 - .03, ya - .05, zt), (xa1 + .03, Y0, zt + SL - .02), {"all": C_TRIM, "pz": (.8, .79, .76), "nz": C_EXT}); ctx.ucxb((xa0, ya, zt), (xa1, Y0, zt + SL))
    cbox(ctx.tile, (xa0, ya, zt + SL - .02), (xa1, Y0, zt + SL), {"all": srgb("#c08a62")})
    cbox(ctx.tile, (xa0, ya, 0), (xa1, Y0, FL - .01), {"all": srgb("#c9a27a"), "nz": (.7, .68, .64)}); ctx.ucxb((xa0, ya, 0), (xa1, Y0, FL))
    for k in range(2): C.worn_step(ctx, (sx - .7, ya - .3 * (k + 1), 0), (sx + .7, ya - .3 * k, FL - .15 * k), (.84, .8, .72), rng)
    pts = [(xa0 + .12, Y0 - .02), (xa0 + .12, ya + .12), (xa1 - .12, ya + .12), (xa1 - .12, Y0 - .02)]
    if "corner_balcony" in FEAT and SIDE > 0:                                       # cantilevered corner balcony round the left side
        cbox(ctx.conc, (xa0 - 1.0, ya - .05, zt), (xa0, Y0 + 2.0, zt + SL - .02), {"all": C_TRIM, "pz": (.8, .79, .76)}); ctx.ucxb((xa0 - 1.0, ya, zt), (xa0, Y0 + 2.0, zt + SL))
        cbox(ctx.tile, (xa0 - 1.0, ya, zt + SL - .02), (xa0, Y0 + 2.0, zt + SL), {"all": srgb("#c08a62")})
        cbox(ctx.stone, (xa0 - 1.05, ya - .1, zt - .08), (xa0 - .95, Y0 + 2.05, zt), {"all": C_STONE})
        pts = [(xa0, Y0 + 1.9), (xa0 - .88, Y0 + 1.9), (xa0 - .88, ya + .12), (xa1 - .12, ya + .12), (xa1 - .12, Y0 - .02)]
    H.railing(ctx, pts, zt + SL, (0, 0, 0), "baluster", h=.95, conc_col=C_STONE)
    return ya


def hoods():
    """small tile hoods on brackets over the windows of the street fronts (photo pink_arcade)"""
    for key in ("front",) + (("left",) if SIDE else ()):
        org, u, n, L = H.facade(RECT, key)
        for s_ in range(NS):
            zb = 0 if s_ == 0 else zfl(s_) - SL
            for (u0, u1, v0, v1, kind, oo) in facade_ops(key, s_):
                if kind != "window" or oo["fit"] != "win" or (s_ == 0 and "arcade2" in FEAT and key == "front"): continue
                zt_ = zb + v1 + .18; p = math.radians(28); D_ = .38
                O = org + u * (u1 + .22) + n * D_ + [0, 0, zt_]; vax = -n * math.cos(p) + np.array([0, 0, math.sin(p)])
                tile_face(O, -u, vax, (u1 - u0) + .44, lambda uu: D_ / math.cos(p), col_seed=SEED + int(u0 * 10))
                C.wbox(ctx.plaster, org, u, n, u0 - .22, u1 + .22, zt_ - .08, zt_, 0, D_, C_TRIM, .1)


def awning_box(z):
    """folding-arm awning: aluminium cassette along the front + a striped valance (photos white_balcony, corner_bungalow)"""
    org, u, n, L = H.facade(RECT, "front"); a_, b_ = (XM0 - X0 - .1, XM1 - X0 + .1)
    C.wbox(ctx.alu, org, u, n, a_, b_, z, z + .17, 0, .2, (.92, .92, .9), .15)
    vc = srgb(wrng.choice(["#2f5f8a", "#3d5a3a", "#8a2a20", "#c8b07a"]))
    for k, x in enumerate(np.arange(a_, b_ - .01, .25)): C.wbox(ctx.fabric, org, u, n, x, min(b_, x + .25), z - .14, z, .19, .2, vc if k % 2 else (.93, .92, .88), .15)


def pergola_vine():
    """vine pergola on steel posts over a corner of the front patio (photo street_bungalow_poles)"""
    xa_, xb_ = X1 - 2.6, X1 - .3; yb_ = Y0 - min(FRONT - .5, 1.8); zp = 2.45; col = (.2, .2, .2, .3)
    for x in (xa_, xb_):
        B.tube_path(ctx.steel, [(x, yb_, 0), (x, yb_, zp)], .04, 8, col); ctx.ucxb((x - .05, yb_ - .05, 0), (x + .05, yb_ + .05, zp))
    B.sweep(ctx.steel, np.array([[xa_ - .1, yb_, zp], [xb_ + .1, yb_, zp]]), B.rect(.06, .06), col, up=(0, 0, 1))
    for x in np.arange(xa_, xb_ + .01, .45): B.sweep(ctx.steel, np.array([[x, yb_ - .1, zp + .04], [x, Y0, zp + .2]]), B.rect(.04, .03), col, up=(0, 0, 1))
    tw = [(xa_ + .08, yb_ + .05, 0)] + [(xa_ + .08 + .04 * math.sin(k), yb_ + .05 + .03 * math.cos(k * 1.3), .25 * k) for k in range(1, 10)] + [(xa_ + .4, yb_ + .3, zp + .15)]
    B.tube_path(ctx.timber, tw, .04, 6, (.35, .26, .18, .4))
    for k in range(28):                                                           # leaf canopy clumps + a few bunches
        x = wrng.uniform(xa_, xb_); y = wrng.uniform(yb_ - .1, Y0 - .05); r_ = wrng.uniform(.18, .32)
        B.superellipsoid(ctx.fabric, (x, y, zp + .2 + wrng.uniform(-.03, .08)), (r_, r_ * .9, r_ * .35), (.7, .7), 8, 5, (*srgb(wrng.choice(["#4f7a2a", "#5f8a32", "#3f6a25"])), .2))
    for k in range(4):
        x = wrng.uniform(xa_ + .3, xb_ - .3); y = wrng.uniform(yb_, Y0 - .3)
        B.superellipsoid(ctx.fabric, (x, y, zp - .12), (.06, .06, .11), (.8, .8), 8, 5, (*srgb("#4a2a4a"), .2))


if NT:
    if NT.get("WALL") and FRONT > 0: garden_walls()
    ex_ = next(((o["a"] + o["b"]) / 2 for o in OPS if o["fit"] == "entry" and o["line"] == fx_front), sx)
    if "porch_tile" in FEAT and FRONT > 1.6: porch_tile(ex_, min(FRONT - .5, 1.7))
    if "porch_pillars" in FEAT and FRONT > 1.6: porch_tile(ex_, Y0 - (YP + .17), pw=1.75, piers=False)
    if "arcade3" in FEAT: arcade(3)
    if "arcade2" in FEAT: arcade(2)
    if "hoods" in FEAT: hoods()
    if "awning_box" in FEAT: awning_box(2.45 if NS == 1 else ZTOP - .45)
    if "pergola_vine" in FEAT and FRONT > 1.6: pergola_vine()
    if NT["BALC"] == "apt":                                                        # cantilevered balcony every upper floor, black bar railing
        for s_ in range(1, NS):
            zb_ = zfl(s_)
            cbox(ctx.conc, (XM0 - .1, Y0 - 1.1, zb_ - .19), (XM1 + .1, Y0, zb_ - .03), {"all": srgb("#d8bf8e"), "pz": (.8, .79, .76)}); ctx.ucxb((XM0 - .1, Y0 - 1.1, zb_ - .19), (XM1 + .1, Y0, zb_ - .03))
            cbox(ctx.tile, (XM0 - .08, Y0 - 1.08, zb_ - .03), (XM1 + .08, Y0, zb_ - .015), {"all": srgb("#c9a27a")})
            H.railing(ctx, [(XM0, Y0 - .05), (XM0, Y0 - 1.0), (XM1, Y0 - 1.0), (XM1, Y0 - .05)], zb_ - .015, (.08, .08, .08), "bars", h=1.0, posts=1.2)
    if NT["BALC"] == "posts":                                                      # full-width balcony on two slim posts, white bar railing
        zb_ = zfl(1)
        cbox(ctx.conc, (X0, Y0 - 1.6, zb_ - .19), (X1, Y0, zb_ - .03), {"all": C_TRIM, "pz": (.8, .79, .76)}); ctx.ucxb((X0, Y0 - 1.6, zb_ - .19), (X1, Y0, zb_ - .03))
        cbox(ctx.tile, (X0 + .02, Y0 - 1.58, zb_ - .03), (X1 - .02, Y0, zb_ - .015), {"all": srgb("#c9a27a")})
        for x in (X0 + .25, X1 - .25): cbox(ctx.plaster, (x - .075, Y0 - 1.5, 0), (x + .075, Y0 - 1.35, zb_ - .19), {"all": C_TRIM}, damp_z=0); ctx.ucxb((x - .075, Y0 - 1.5, 0), (x + .075, Y0 - 1.35, zb_ - .19))
        H.railing(ctx, [(X0 + .1, Y0 - .05), (X0 + .1, Y0 - 1.5), (X1 - .1, Y0 - 1.5), (X1 - .1, Y0 - .05)], zb_ - .015, (.95, .95, .93), "bars", h=1.0, posts=1.8)
    if "loggia" in FEAT and NS >= 2:                                               # back wall of the loggia (window + French door), tiled floor
        yl = Y0 + LGD; z1_ = zfl(1)
        part((XM0, yl), (XM1, yl), ("y", yl), 1, col_l=C_INT, col_r=C_EXT)
        cbox(ctx.tile, (XM0, Y0 + WT, z1_ - .03), (XM1, yl - WT / 2, z1_ - .012), {"all": srgb("#c08a62")})
        u_, n_ = np.array([1., 0, 0]), np.array([0, -1., 0])
        for o in OPS:
            if o["line"] != ("y", yl): continue
            w_, h_ = o["b"] - o["a"], o["z1"] - o["z0"]; c_out = np.array([(o["a"] + o["b"]) / 2, yl - WT / 2, z1_ + o["z0"]])
            if o["kind"] == "window":
                casement(c_out, u_, n_, w_, h_, .12); mplace("shut_win_open", SHUT_SEED, c_out, u_, n_, 0)
            else:
                H.door_leaf(ctx, c_out - n_ * .14 - u_ * w_ / 2, u_, -n_, srgb("#f2f0ea"), open_deg=70, w=w_ - .04, h=h_ - .03, glazed=True)
                mplace("shut_door_open", SHUT_SEED, c_out, u_, n_, 0)
        mplace("lantern", 2, np.array([(XM0 + XM1) / 2 - .9, yl - WT / 2, z1_]), u_, n_, 2.0)
    if "porch_wide" in FEAT and FRONT > 1.6:                                       # tiled lean-to over the ground-floor terrace (under the loggia)
        porch_tile((XM0 + XM1) / 2, min(FRONT - .4, 2.0), pw=XM1 - XM0, zh=zfl(1) - SL - .1)
    if "boug_corner" in FEAT and SIDE > 0:                                         # bougainvillea over the corner of the garden wall (vegm kit, variant C)
        VEG.append({"asset": "vegm_bougainvillea", "variant": "C", "pos": [round(-PW / 2, 3), round(YP, 3), 0.0], "rot_z": -90.0})
    if "boug_wall" in FEAT:                                                        # bougainvillea over the front wall beside the gate (variant B, 5 m)
        xb_ = ex_ + 3.2 if ex_ + 3.2 < PW / 2 - 2.6 else ex_ - 3.2
        VEG.append({"asset": "vegm_bougainvillea", "variant": "B", "pos": [round(min(max(xb_, -PW / 2 + 2.6), PW / 2 - 2.6), 3), round(YP, 3), 0.0], "rot_z": 0.0})
    for k, v in enumerate(VEG):
        s_ = bpy.data.objects.new(f"SOCKET_Veg_{v['asset']}_{v['variant']}_{k}", None); bpy.context.scene.collection.objects.link(s_)
        s_.location = tuple(v["pos"]); s_.rotation_euler = (0, 0, math.radians(v["rot_z"]))


# ------------------------------------------------------------------ interior finish (interior.py) + loot sockets
Mp = {"plaster": ctx.plaster, "tile": ctx.tile, "conc": ctx.conc, "steel": ctx.steel, "alu": ctx.alu, "glass": ctx.glass,
      "timber": ctx.timber, "paintwood": ctx.paintwood, "pvc": ctx.pvc, "ceramic": ctx.ceramic, "dark": ctx.dark, "fabric": ctx.fabric}
irng = random.Random(SEED * 977 + 31)
for r in ROOMS:
    t = r["type"]; parts = ["skirting", "architraves", "electrics", "wear", "lights"]
    if t in ("kitchen", "bathroom", "shop"): parts += ["fixtures"]
    if t in ("living", "bedroom"): parts += ["curtains"]
    if t == "stair": parts = ["skirting", "electrics", "lights"]
    IN.finish([r], Mp, irng, collide=ctx.ucxb, wall_col=C_INT, parts=tuple(parts), skirting_col=srgb("#8a7a66"), frame_col=(.92, .9, .85))
IN.fusebox(ROOMS[0], Mp, "s", ROOMS[0]["rect"][0] + .5) if ROOMS[0]["type"] != "shop" else None
for r in ROOMS:
    if r["type"] == "stair": continue
    x0, x1, y0, y1 = r["rect"]
    pts = [((x0 + x1) / 2 + rng.uniform(-.3, .3), y0 + .45, r["z"]), (x0 + .4, (y0 + y1) / 2, r["z"])][:2 if (x1 - x0) * (y1 - y0) > 5 else 1]
    for k, p in enumerate(pts):
        s_ = bpy.data.objects.new(f"SOCKET_Loot_{r['id']}_{k}", None); bpy.context.scene.collection.objects.link(s_); s_.location = tuple(float(v) for v in p)
        LOOT.append({"name": s_.name, "room": r["id"], "loc": [round(float(v), 3) for v in p]})

# ------------------------------------------------------------------ write
IN.write_rooms(os.path.splitext(os.path.abspath(OUT))[0] + "_rooms.json", ROOMS,
               {"piece": "medhouse", "seed": SEED, "storeys": NS, "plot_m": [PW, PD], "type": TYPE, "style": "med", "facade_style": STY, "roof": ROOF,
                "note": "origin = plot centre on finished ground; ground floor +0.30 m; storey 2.85 m; front -Y (lane)",
                "facade_props": PROPS, "loot_sockets": LOOT, **({"photo_type": TYPE, "veg_items": VEG} if NT else {}),
                "zones": {"house": [X0, X1, Y0, Y1], "patio": [-PW / 2, PW / 2, -PD / 2, Y0] if FRONT else None, "yard": [-PW / 2, PW / 2, Y1, PD / 2] if BACK > .5 else None}})
_tx = lambda n: os.path.exists(os.path.join(B.TEX, f"T_{n}_BaseColor.png"))   # photo textures (Worker TX 16.10.)
objs = C.mats(ctx, extra=[(ctx.tiles, "RoofTiles", lambda: B.tint_mat("M_RoofTile", "RoofTerracotta", 1.5) if _tx("RoofTerracotta")
                           else B.plain_mat("M_RoofTile", (1, 1, 1), .7), 40),
                          (ctx.stone, "Sandstone", lambda: B.tint_mat("M_Sandstone", "SandstoneAshlar" if _tx("SandstoneAshlar") else "Concrete",
                                                                      1.6 if _tx("SandstoneAshlar") else 1.2), 30)])
UCX = C.ucx_objs(ctx)
mt = sum(len(o.data.polygons) for o in bpy.data.objects if o.name.startswith("MED_") and o.type == 'MESH')
print("TRIS", B.tris(objs), "+M", mt, "PIECE medhouse SEED", SEED, "NS", NS, "PLOT", PW, PD, TYPE, STY, ROOF, "UCX", len(UCX), "ROOMS", len(ROOMS), "LOOT", len(LOOT))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT))
