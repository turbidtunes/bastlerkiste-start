"""Small village chapel (generic, Catholic type common in Mauritian villages) – Worker W2.
python geo_chapel.py <out.blend> [seed]

Real model: the roadside village chapels of Mauritius (e.g. the small "chapelle" of every coastal village): a
single nave in rendered masonry, whitewashed with a coloured trim, gable front raised as a pediment with a bell-cote
(one bell in an arched opening, plain cross on top), round-arched double timber doors under a small porch on two
columns, pointed windows with coloured glass in steel frames, corrugated-iron roof on timber king-post trusses left
open inside, ceiling fans hung from the tie beams, tiled floor, raised sanctuary with altar, lectern, tabernacle
shelf and a plain wooden cross; timber pews with kneelers; votive candle rack and holy-water font by the door;
sacristy annex behind (vestment rail, cupboard, table, sink). Outside: a Lourdes grotto of piled basalt with a
niche, candles and flowers (very common in Mauritius), low boundary wall with a gate, benches, pots.
No text, no images (the statue in the grotto is a plain veiled figure without features).

Origin = centre of the nave footprint on finished ground, entrance = -Y, floor FL = +0.45 m.
"""
import sys, os, math, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(HERE, "..")
sys.path[:0] = [S, os.path.join(S, "house")]
import bpy
import bldlib as B
from bldlib import MB, srgb
import hlib as H
from hlib import cbox
import interior as IN
import civlib as C
from civplan import Plan

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = a[0]; SEED = int(a[1]) if len(a) > 1 else 1
rng = random.Random(SEED * 1709 + 3)
B.reset(); ctx = C.add_mbs(H.Ctx(rng)); ctx.basalt = MB()


def fade(c, f): return tuple(ci * (1 - f) + w * f for ci, w in zip(c, (.80, .78, .72)))


FD = rng.uniform(.05, .3)
C_EXT = fade(srgb("#f4f2ea"), FD); C_TRIM = fade(srgb(rng.choice(["#3d6fa8", "#5a9ab8", "#c8a040", "#7a9a6a"])), FD)
C_INT = srgb("#f2efe6"); C_GRILLE = srgb("#2a2a2a"); C_DOOR = srgb(rng.choice(["#5a3a22", "#6a4a2a"])); C_PLINTH = srgb("#5a5a5c")
C_WOOD = (.45, .3, .18)
FL = .45; T = .3; ZW = FL + 5.0; PITCH = 35
X0, X1, Y0, Y1 = -3.8, 3.8, -8.0, 8.0
SX0, SX1, SY1 = -2.8, 3.8, 10.9                                 # sacristy annex (y 8 .. 10.9)
P = Plan(ctx, rng, FL=FL, WT=T)

P.room("nave", "nave", (-3.5, 3.5, -7.7, 7.7), ZW - (FL + .012))
P.room("sacristy", "sacristy", (-2.6, 3.6, 8.0, 10.7), FL + 2.8 - (FL + .012))
P.room("porch", "porch", (-1.8, 1.8, -9.6, -8.0), 3.0 - .012, finish=False)
WINY = (-5.6, -2.1, 1.4)
for y in WINY:
    for line in (("x", X0), ("x", X1)): P.op(line, y - .5, y + .5, 1.4, 3.9, "window", True, "arch", t=T)
P.op(("x", X1), 4.6, 5.4, 1.4, 3.6, "window", True, "arch", t=T)               # sanctuary window (east)
P.op(("x", X0), 5.4, 6.3, 0, 2.2, "door", True, "single", t=T, gate=False)      # side door (sanctuary, west)
P.op(("y", Y0), -.8, .8, 0, 3.4, "door", True, "double", t=T, glazed=False, gate=False, steps="none", open=95, leaf_h=2.58)
P.op(("y", Y1), 2.7, 3.4, 0, 2.1, "door", True, "single", t=T, gate=False, steps="none", to="sacristy", open=70)   # nave (beside the platform) -> sacristy
P.op(("y", SY1), -1.6, -.6, 1.0, 2.0, "window", True, "louvre")
P.op(("x", SX0), 9.0, 10.0, 1.0, 2.0, "window", True, "louvre")
P.op(("x", SX1), 9.3, 10.2, 0, 2.1, "door", True, "single", gate=True)
P.assign()

NAVE = (X0, X1, Y0, Y1); SAC = (SX0, SX1, Y1, SY1)
cbox(ctx.conc, (X0 + .05, Y0 + .05, 0), (X1 - .05, Y1 - .05, FL - .02), {"all": (.75, .74, .7)}); ctx.ucxb((X0, Y0, 0), (X1, Y1, FL))
cbox(ctx.conc, (SX0 + .05, Y1, 0), (SX1 - .05, SY1 - .05, FL - .02), {"all": (.75, .74, .7)}); ctx.ucxb((SX0, Y1, 0), (SX1, SY1, FL))
P.floors(skip=("porch",))
P.walls(NAVE, ("front", "back", "left", "right"), ZW, C_EXT, C_INT, mb=ctx.plaster, t=T)
P.walls(SAC, ("back", "left", "right"), FL + 2.8, C_EXT, C_INT, mb=ctx.plaster, t=.2)
for xa in (SX0, SX1 - .2): cbox(ctx.plaster, (xa, Y1, 0), (xa + .2, Y1 + .2, FL + 2.8), {"all": C_EXT}, damp_z=0, damp_amt=.4)
# arch spandrels for every arched exterior opening + the main door (round)
for o in P.ops:
    if not o["ext"]: continue
    ax, cc = o["line"]
    if ax == "x":
        u = np.array([0, 1., 0]); n = np.array([1. if cc > 0 else -1., 0, 0]); c = np.array([cc, (o["a"] + o["b"]) / 2, 0])
    else:
        u = np.array([1., 0, 0]); n = np.array([0, 1. if cc > 0 else -1., 0]); c = np.array([(o["a"] + o["b"]) / 2, cc, 0])
    w = o["b"] - o["a"]; zt = FL + o["z1"]
    if o["fit"] == "arch":
        C.arch_fill(ctx.plaster, c, u, n, w, zt - .6, zt, o.get("t", T), C_INT, "pointed")
        o["arch"] = (c, u, n, w, zt - .6, zt)
    elif o["fit"] == "double":
        C.arch_fill(ctx.plaster, c, u, n, w, zt - .8, zt, o.get("t", T), C_INT, "round")
        o["arch"] = (c, u, n, w, zt - .8, zt)
# king-post trusses, tin roof with gutters; front pediment + bell-cote; back gable from tin_roof
zr = H.tin_roof(ctx, NAVE, ZW, "gable", PITCH, .45, fade(srgb("#8a8f92"), FD), C_TRIM, rust=.35, gable_col=C_EXT, ridge="y")
tp = math.tan(math.radians(PITCH)); hR = (X1 - X0) / 2 * tp
for y in np.arange(Y0 + 2.0, Y1 - 1.0, 3.0):
    B.sweep(ctx.timber, np.array([(X0 + .1, y, ZW - .05), (X1 - .1, y, ZW - .05)]), B.rect(.1, .2), (.55, .4, .28, .3), up=(0, 0, 1))
    B.sweep(ctx.timber, np.array([(0, y, ZW + .05), (0, y, ZW + hR - .1)]), B.rect(.12, .12), (.55, .4, .28, .3), up=(1, 0, 0))
    for s_ in (-1, 1):
        B.sweep(ctx.timber, np.array([(0, y, ZW + .4), (s_ * 1.8, y, ZW + .05)]), B.rect(.07, .1), (.55, .4, .28, .3), up=(0, 1, 0))
        B.sweep(ctx.timber, np.array([(s_ * 3.6, y, ZW - .02), (0, y, ZW + hR - .05)]), B.rect(.08, .18), (.55, .4, .28, .3), up=(0, 1, 0))
    C.ceiling_fan(ctx, (0, y + .0, ZW - .15), rng) if y < 4 else None
for s_ in (-1, 1):                                                   # half-round gutters + downpipes
    xe = s_ * (X1 + .45 + .06)
    pts = [(xe, Y0 - .45, ZW - .45 * tp - .12), (xe, Y1 + .45, ZW - .45 * tp - .12)]
    B.sweep(ctx.galv, np.array(pts), [(-.07, .05), (-.07, -.03), (.0, -.07), (.07, -.03), (.07, .05), (.055, .05), (.055, -.02), (0, -.055), (-.055, -.02), (-.055, .05)], (.7, .72, .72, .35), up=(0, 0, 1))
    for y in (Y0 + .2, Y1 - .2): C.downpipe(ctx, (s_ * X1, y, ZW - .45 * tp - .2), (s_ * 1., 0, 0), 0)
ctx.ucxb((X0, Y0 - .3, ZW), (X1, Y0, ZW + hR + .6))
# front pediment: the facade rises above the roof as a gable parapet with a coping, bell-cote at the apex
V = [(X0, Y0 - .0, ZW), (X1, Y0, ZW), (0, Y0, ZW + hR + .6)]
Vb = [(v[0], v[1] + T, v[2]) for v in V]
ctx.plaster.add(V + Vb, [[0, 2, 1], [3, 4, 5], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]], [(v[0], v[2]) for v in V + Vb], (*C_EXT, .1))
for s_ in (-1, 1):                                                   # coping along both rakes
    B.sweep(ctx.conc, np.array([(s_ * (X1 + .08), Y0 + T / 2, ZW + .05), (0, Y0 + T / 2, ZW + hR + .68)]), B.rect(T + .12, .08), (*C_TRIM, .2), up=(0, 1, 0))
bx = .7; zb0 = ZW + hR + .3
for (lo, hi) in (((-bx, Y0 - .02, zb0), (-bx + .25, Y0 + T + .02, zb0 + 1.7)), ((bx - .25, Y0 - .02, zb0), (bx, Y0 + T + .02, zb0 + 1.7)), ((-bx, Y0 - .02, zb0 + 1.7), (bx, Y0 + T + .02, zb0 + 2.0))):
    cbox(ctx.plaster, lo, hi, {"all": C_EXT}, A=.15); ctx.ucxb(lo, hi)
C.arch_fill(ctx.plaster, np.array([0, Y0 - .02, 0]), np.array([1., 0, 0]), np.array([0, -1., 0]), 2 * bx - .5, zb0 + 1.3, zb0 + 1.7, T + .04, C_EXT, "round")
cbox(ctx.conc, (-bx - .06, Y0 - .08, zb0 + 2.0), (bx + .06, Y0 + T + .08, zb0 + 2.08), {"all": C_TRIM}, A=.2)
rings = [[(r_ * math.cos(t), Y0 + T / 2 + r_ * math.sin(t), zb0 + 1.25 - z) for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)] for r_, z in ((.04, 0), (.12, .08), (.2, .32), (.23, .36))]
ctx.galv.grid(np.array(rings), col=(.55, .45, .25, .5), close_v=True)                             # bronze bell
B.tube_path(ctx.galv, [(-bx + .25, Y0 + T / 2, zb0 + 1.3), (bx - .25, Y0 + T / 2, zb0 + 1.3)], .025, 6, (.3, .3, .3, .4))    # yoke
B.tube_path(ctx.fabric, [(0.15, Y0 + T / 2, zb0 + 1.2), (.15, Y0 + T / 2, zb0 + .9), (.15, Y0 + T + .05, ZW + hR - .1)], .008, 4, (.75, .7, .55, .3))   # bell rope into the roof
for (lo, hi) in (((-.04, Y0 + T / 2 - .04, zb0 + 2.08), (.04, Y0 + T / 2 + .04, zb0 + 2.9)), ((-.25, Y0 + T / 2 - .04, zb0 + 2.55), (.25, Y0 + T / 2 + .04, zb0 + 2.63))):
    cbox(ctx.paint, lo, hi, {"all": (.9, .9, .88)}, A=.2)                                             # plain cross
# blind oculus over the door: moulded ring + inset coloured glass disc
oc = np.array([0, Y0 - .012, FL + 4.45])
B.tube_path(ctx.plaster, [oc + [.55 * math.cos(t), 0, .55 * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 33)], .05, 8, (*C_TRIM, .1), up=(0, 1, 0))
ctx.glass.add([oc + [.5 * math.cos(t), .0, .5 * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)][::-1], [list(range(24))], [(0, 0)] * 24, (.35, .45, .7, 0))
# pilasters at the front corners + string course
for x in (X0, X1 - .35):
    cbox(ctx.plaster, (x, Y0 - .06, 0), (x + .35, Y0 + .001, ZW), {"all": C_EXT}, damp_z=0, damp_amt=.4)
cbox(ctx.plaster, (X0 - .05, Y0 - .1, ZW - .25), (X1 + .05, Y0 + .0, ZW), {"all": C_TRIM}, A=.15)
P.fit_exterior([(NAVE, ("front", "back", "left", "right"), ZW), (SAC, ("back", "left", "right"), FL + 2.8)], C_EXT, C_TRIM, C_GRILLE, C_DOOR,
               c_plinth=C_PLINTH, c_old=fade(srgb("#e0d8b8"), FD))
# arched windows: coloured glass in a steel glazing-bar grid + protective mesh outside (replaces the louvres)
for o in P.ops:
    if o.get("fit") != "arch": continue
    c, u, n, w, zs, zt = o["arch"]; z0 = FL + o["z0"]; ci = c - n * T / 2
    cols = [srgb(h) for h in ("#2a4f9a", "#c8a030", "#a82a2a", "#3a7a4a", "#e8e0c0", "#6a3a8a")]
    nz = int((zs - z0) / .25)
    for i in range(4):
        for j in range(nz):
            q0 = ci + u * (-w / 2 + i * w / 4) + [0, 0, z0 + j * (zs - z0) / nz]; q1 = q0 + u * (w / 4) + [0, 0, (zs - z0) / nz]
            col = cols[(i * 3 + j * 2 + SEED) % len(cols)] if (i in (0, 3) or j in (0, nz - 1)) else cols[4]
            ctx.glass.add([q0, q0 + u * (w / 4), q1, q1 - u * (w / 4)], [[0, 1, 2, 3], [3, 2, 1, 0]], [(0, 0)] * 4, (*col, 0))
            B.sweep(ctx.steel, np.array([q0, q0 + u * (w / 4)]), B.rect(.015, .03), (.15, .15, .15, .2), up=tuple(n))
        B.sweep(ctx.steel, np.array([ci + u * (-w / 2 + i * w / 4) + [0, 0, z0], ci + u * (-w / 2 + i * w / 4) + [0, 0, zs]]), B.rect(.015, .03), (.15, .15, .15, .2), up=tuple(n))
    tri = [ci + u * (-w / 2) + [0, 0, zs], ci + u * (w / 2) + [0, 0, zs], ci + [0, 0, zt - .02]]
    ctx.glass.add(tri, [[0, 1, 2], [2, 1, 0]], [(0, 0)] * 3, (*cols[2], 0))
    for k in range(1, int(w / .12)):                                  # protective bars on the outer face
        q = c + n * .03 + u * (-w / 2 + k * w / int(w / .12)) + [0, 0, z0]
        B.tube_path(ctx.steel, [q, q + [0, 0, zs - z0 + .25]], .008, 5, (*C_GRILLE, .3))
# fanlight (semicircular glazing) in the round arch over the main door
o = [o for o in P.ops if o.get("fit") == "double"][0]; c, u, n, w, zs, zt = o["arch"]; ci = c - n * T / 2 + [0, 0, 0]
fan = [ci + [0, 0, zs - .05]] + [ci + u * (w / 2 * math.cos(t)) + [0, 0, zs + (zt - zs) * math.sin(t)] for t in np.linspace(0, math.pi, 13)]
ctx.glass.add(fan, [[0, k, k + 1] for k in range(1, 13)] + [[0, k + 1, k] for k in range(1, 13)], [(0, 0)] * 14, (.6, .7, .75, 0))
cbox(ctx.paintwood, ci - u * w / 2 - n * .04 + [0, 0, zs - .08], ci + u * w / 2 + n * .04 + [0, 0, zs], {"all": C_DOOR})
for t in np.linspace(.4, math.pi - .4, 4): B.sweep(ctx.paintwood, np.array([ci + [0, 0, zs], ci + u * (w / 2 * math.cos(t)) + [0, 0, zs + (zt - zs) * math.sin(t)]]), B.rect(.03, .04), (*C_DOOR, .1), up=tuple(n))
# porch: slab on two round columns + steps
cbox(ctx.conc, (-1.8, -9.6, 0), (1.8, Y0, FL), {"all": (.75, .74, .7)}, A=.3); ctx.ucxb((-1.8, -9.6, 0), (1.8, Y0, FL))
cbox(ctx.tile, (-1.75, -9.55, FL), (1.75, Y0 - .02, FL + .012), {"all": (.85, .82, .74)})
for k in range(3): C.worn_step(ctx, (-1.8, -9.6 - (k + 1) * .3, 0), (1.8, -9.6 - k * .3, FL - (k + 1) * .15), (.7, .69, .66), rng)
ctx.ucxb((-1.8, -10.5, 0), (1.8, -9.6, .3))
cbox(ctx.conc, (-2.0, -9.8, FL + 3.0), (2.0, Y0, FL + 3.18), {"all": C_TRIM, "pz": (.7, .69, .66), "nz": (.93, .92, .88)}); ctx.ucxb((-2.0, -9.8, FL + 3.0), (2.0, Y0, FL + 3.18))
for x in (-1.55, 1.55):
    B.tube_path(ctx.plaster, [(x, -9.4, FL), (x, -9.4, FL + 3.0)], .12, 16, (*C_EXT, .15)); ctx.ucxb((x - .12, -9.52, FL), (x + .12, -9.28, FL + 3.0))
    cbox(ctx.conc, (x - .17, -9.57, FL), (x + .17, -9.23, FL + .15), {"all": (.85, .84, .8)}); cbox(ctx.conc, (x - .17, -9.57, FL + 2.85), (x + .17, -9.23, FL + 3.0), {"all": (.85, .84, .8)})
H.slab(ctx, SAC, FL + 2.8, .15, C_TRIM, (.7, .69, .66), C_INT, front_extra=-.15)
C.meter_box(ctx, np.array([X1, -6.6, 0]), np.array([0, 1., 0]), np.array([1., 0, 0]), pole=(9.0, -12.0, 7.6))

# ------------------------------------------------------------------ interior
Mp = {"plaster": ctx.plaster, "tile": ctx.tile, "conc": ctx.conc, "steel": ctx.steel, "alu": ctx.alu, "glass": ctx.glass,
      "timber": ctx.timber, "paintwood": ctx.paintwood, "pvc": ctx.pvc, "ceramic": ctx.ceramic, "dark": ctx.dark, "fabric": ctx.fabric}
irng = random.Random(SEED * 977 + 61)
IN.finish([P.R["nave"]], Mp, irng, collide=ctx.ucxb, wall_col=C_INT, parts=("skirting", "electrics", "wear"), skirting_col=(.3, .25, .2))
IN.finish([P.R["sacristy"]], Mp, irng, collide=ctx.ucxb, wall_col=C_INT, parts=("skirting", "architraves", "electrics", "lights", "wear"), skirting_col=(.3, .25, .2))
IN.fusebox(P.R["sacristy"], Mp, "w", 8.5)
F_ = FL + .012
C.FLOOR = F_
P.dado("nave", fade(C_TRIM, .5), 1.1)
# wall lights: tube battens on brackets between the windows
for y in (-3.85, -.35, 3.0):
    for s_ in (-1, 1):
        cbox(ctx.paint, (s_ * 3.5 - (.08 if s_ > 0 else 0), y - .62, FL + 3.0), (s_ * 3.5 + (.08 if s_ < 0 else 0), y + .62, FL + 3.08), {"all": (.92, .92, .9)})
        B.tube_path(ctx.lamp, [(s_ * 3.44, y - .6, FL + 2.98), (s_ * 3.44, y + .6, FL + 2.98)], .016, 8, (1, 1, .97, 0))
# sanctuary platform + steps, altar, lectern, tabernacle shelf, cross, candle stands, flowers
cbox(ctx.conc, (-2.6, 4.6, F_), (2.6, 7.7, F_ + .45), {"all": (.85, .82, .74)}, A=.2); ctx.ucxb((-2.6, 4.6, F_), (2.6, 7.7, F_ + .45))
cbox(ctx.tile, (-2.6, 4.6, F_ + .45), (2.6, 7.7, F_ + .462), {"all": (.9, .86, .78)})
for k in range(2): cbox(ctx.conc, (-2.0, 4.6 - (k + 1) * .3, F_), (2.0, 4.6 - k * .3, F_ + .45 - (k + 1) * .15), {"all": (.85, .82, .74)}, A=.25)
ctx.ucxb((-2.0, 4.0, F_), (2.0, 4.6, F_ + .2))
zp = F_ + .462
cbox(ctx.conc, (-1.0, 6.0, zp), (1.0, 6.8, zp + .95), {"all": (.93, .92, .88)}, A=.15); ctx.ucxb((-1.0, 6.0, zp), (1.0, 6.8, zp + .95))   # altar
cbox(ctx.fabric, (-1.08, 5.94, zp + .95), (1.08, 6.86, zp + .97), {"all": (.97, .97, .95)})
cbox(ctx.fabric, (-1.08, 5.935, zp + .55), (1.08, 5.94, zp + .97), {"all": (.97, .97, .95)})                    # altar frontal cloth
for x in (-.75, .75): C.candle(ctx.paint, (x, 6.6, zp + .97), .3, .025, True, ctx)
for x in (-.35, .35):
    rings = [[(x + rr * math.cos(t), 6.6 + rr * math.sin(t), zp + .97 + z) for t in np.linspace(0, 2 * math.pi, 10, endpoint=False)] for rr, z in ((.05, 0), (.07, .15), (.05, .2))]
    ctx.ceramic.grid(np.array(rings), col=(.95, .95, .95, 0), close_v=True)
cbox(ctx.timber, (-2.7, 5.0, zp), (-2.3, 5.4, zp + 1.15), {"all": C_WOOD}, A=.2)                                 # lectern
B.box(ctx.timber, (-2.5, 5.15, zp + 1.2), (.55, .45, .04), np.array([[1, 0, 0], [0, math.cos(.35), -math.sin(.35)], [0, math.sin(.35), math.cos(.35)]]), (*C_WOOD, .2))
cbox(ctx.conc, (-.8, 7.35, zp + 1.0), (.8, 7.7, zp + 1.08), {"all": (.9, .89, .85)})                             # tabernacle shelf
cbox(ctx.paint, (-.25, 7.4, zp + 1.08), (.25, 7.68, zp + 1.48), {"all": (.75, .62, .3)}, A=.1)
cbox(ctx.timber, (-.05, 7.62, zp + 1.7), (.05, 7.7, zp + 3.5), {"all": (.35, .22, .12)}); cbox(ctx.timber, (-.5, 7.62, zp + 2.85), (.5, 7.7, zp + 2.95), {"all": (.35, .22, .12)})   # wooden cross
for x in (-1.6, 1.6):                                                                                            # standing candle holders
    B.tube_path(ctx.galv, [(x, 6.4, zp), (x, 6.4, zp + 1.2)], .02, 8, (.7, .6, .35, .2)); B.superellipsoid(ctx.galv, (x, 6.4, zp + .03), (.15, .15, .03), (1, 1), 10, 4, (.7, .6, .35, .2))
    C.candle(ctx.paint, (x, 6.4, zp + 1.2), .4, .03, True, ctx)
for x in (-2.2, 2.2): C.pot_plant(ctx, x, 7.3, rng, .25, z0=zp)
C.FLOOR = zp
for k in range(4): C.visitor_chair(ctx, 1.5 + (k % 2) * .5, 5.2 + (k // 2) * .55, 270, (.5, .2, .2))          # chairs for the servers
C.FLOOR = F_
# pews: 2 x 9, aisle in the middle
for k, y in enumerate(np.arange(-6.2, 3.4, .95)):
    for x in (-1.95, 1.95): C.pew(ctx, x, y, 180, 2.9)
# entrance: votive rack, holy-water font, notice board (blank), hymn board
C.votive_rack(ctx, -2.9, -7.2, 90, rng)
B.tube_path(ctx.conc, [(1.3, -7.35, F_), (1.3, -7.35, F_ + .85)], .08, 10, (.88, .87, .83, .2))
rings = [[(1.3 + rr * math.cos(t), -7.35 + rr * math.sin(t), F_ + .85 + z) for t in np.linspace(0, 2 * math.pi, 14, endpoint=False)] for rr, z in ((.08, 0), (.2, .1), (.22, .14), (.18, .12))]
ctx.conc.grid(np.array(rings), col=(.9, .89, .85, .2), close_v=True)
C.notice_board(ctx, np.array([3.5, -6.8, F_]), np.array([0, 1., 0]), np.array([-1., 0, 0]), .9, .9, 1.3, rng)
cbox(ctx.timber, (3.45, 4.0, F_ + 1.6), (3.5, 4.5, F_ + 2.4), {"all": C_WOOD}); [cbox(ctx.paint, (3.44, 4.05, F_ + 1.7 + k * .17), (3.45, 4.45, F_ + 1.82 + k * .17), {"all": (.95, .95, .92)}) for k in range(4)]
P.loot("nave", [(-1.95, -1.45, F_ + .47), (1.95, 2.35, F_ + .47), (-2.9, -7.2, F_ + .85), (2.5, 5.7, zp)])
# sacristy: vestment rail, cupboard, table + chairs, wall basin, candle boxes
r = P.R["sacristy"]
B.tube_path(ctx.galv, [(-2.5, 10.4, F_ + 1.7), (-.4, 10.4, F_ + 1.7)], .015, 6, (.75, .75, .75, .2))
for k in range(6):
    x = -2.35 + k * .32; c = srgb(["#f2f2ee", "#f2f2ee", "#3a6a3a", "#7a1a2a", "#f2f2ee", "#4a2a6a"][k])
    V = [(x - .15, 10.4, F_ + 1.66), (x + .15, 10.4, F_ + 1.66), (x + .2, 10.42, F_ + .6), (x - .2, 10.38, F_ + .6)]
    ctx.fabric.add(V, [[0, 1, 2, 3], [3, 2, 1, 0]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*c, .1))
C.steel_cabinet(ctx, 2.0, 10.45, 180, 1.0, .45, 1.9, (.55, .42, .3))
C.folding_table(ctx, .6, 8.9, 0, 1.4, .7); C.visitor_chair(ctx, .2, 9.5, 180); C.visitor_chair(ctx, 1.0, 9.5, 180)
C.wall_basin(ctx, np.array([SX1 - .2, 8.6, F_]), np.array([0, 1., 0]), np.array([-1., 0, 0]))
C.boxes_pile(ctx, -2.2, 8.4, rng, 3)
P.loot("sacristy", [(.6, 8.9, F_ + .74), (2.0, 10.45, F_ + 1.9)])

C.FLOOR = 0.0
# ------------------------------------------------------------------ yard: path, boundary wall + gate, grotto, benches
cbox(ctx.conc, (-1.2, -14.0, -.02), (1.2, -10.5, .012), {"all": (.72, .71, .68)}, A=.25)
H.garden_wall(ctx, -9.0, 9.0, -14.2, .9, C_EXT, 0.0, 2.4, C_GRILLE, rng, returns=[((-9.0, -14.05), (-9.0, 12.5)), ((8.85, -14.05), (8.85, 12.5))])
# Lourdes grotto (west front lawn): piled basalt boulders round an arched niche, statue on a ledge, candles, flowers
gx, gy = -6.0, -10.5
stones = []
for k in range(70):
    t = rng.uniform(.05, math.pi - .05); r_ = rng.uniform(1.1, 1.6); z = abs(math.sin(t)) * 2.6 * rng.uniform(.75, 1.05)
    x = gx + math.cos(t) * r_ * 1.0; y = gy + rng.uniform(-.2, .7)
    if abs(math.cos(t)) < .4 and z < 2.0: continue                      # keep the niche open
    sz = np.array([rng.uniform(.25, .45), rng.uniform(.25, .4), rng.uniform(.2, .35)])
    B.superellipsoid(ctx.basalt, (x, y, z * .85 + sz[2] * .5), sz, (rng.uniform(.4, .7), rng.uniform(.5, .8)), 8, 6, (.95, .95, .95, .3))
    stones.append((x, y, z))
for z in np.arange(.2, 2.6, .4):
    for s_ in (-1, 1):
        sz = np.array([.35, .4, .25]); B.superellipsoid(ctx.basalt, (gx + s_ * (.75 + .1 * math.sin(z * 3)), gy + .3, z), sz, (.5, .6), 8, 6, (.95, .95, .95, .3))
B.superellipsoid(ctx.basalt, (gx, gy + .5, 2.55), (.9, .45, .3), (.5, .6), 10, 6, (.95, .95, .95, .3))
cbox(ctx.basalt, (gx - .8, gy - .2, 0), (gx + .8, gy + .9, .25), {"all": (.95, .95, .95)}, A=.3)
ctx.hull([(gx + dx, gy + dy, z) for dx in (-1.7, 1.7) for dy in (-.4, 1.1) for z in (0, 2.9)])
cbox(ctx.conc, (gx - .35, gy + .5, 1.0), (gx + .35, gy + .9, 1.08), {"all": (.9, .89, .85)})                    # statue ledge
prof = [(.14, 0), (.16, .3), (.14, .7), (.11, .95), (.09, 1.05), (.07, 1.12), (.09, 1.2), (.06, 1.3), (0, 1.33)]
rings = [[(gx + rr * math.cos(t), gy + .7 + rr * .8 * math.sin(t), 1.08 + z) for t in np.linspace(0, 2 * math.pi, 14, endpoint=False)] for rr, z in prof]
ctx.paint.grid(np.array(rings), col=(.95, .95, .94, .1), close_v=True)                                          # plain veiled figure (white)
for k in range(14):                                                                                              # candles on the base, flowers
    x = gx + rng.uniform(-.6, .6); y = gy + rng.uniform(-.15, .3)
    C.candle(ctx.paint, (x, y, .25), rng.uniform(.05, .2), .02, rng.random() < .4, ctx)
for x in (gx - .55, gx + .55): C.pot_plant(ctx, x, gy - .05, rng, .16)
cbox(ctx.galv, (gx - 1.0, gy - .9, 0), (gx + 1.0, gy - .86, .6), {"all": (.25, .25, .25)}); ctx.ucxb((gx - 1.0, gy - .9, 0), (gx + 1.0, gy - .86, .6))   # low railing in front
P.loot(P.room("grotto", "shrine", (gx - .8, gx + .8, gy - .2, gy + .9), 2.4, z=.25, finish=False), [(gx + .3, gy, .25)])
for (x, y) in ((5.5, -11.0), (5.5, -9.0)): C.bench_concrete(ctx, x, y, 270, 1.8)
for (x, y) in ((-1.6, -10.8), (1.6, -10.8), (-8.3, -13.5), (8.2, -13.5), (-4.4, 9.0), (4.4, -2.0)): C.pot_plant(ctx, x, y, rng, rng.uniform(.25, .34))
C.bin_wheelie(ctx, 3.6, 11.4, 180, C.C_GREENP)
C.water_drum(ctx, -3.4, 10.2, C.C_BLUEP)
B.tube_path(ctx.timber, [(9.0, -12.0, 0), (9.0, -12.0, 8.0)], .13, 12, (.55, .45, .35, .3)); ctx.ucxb((8.87, -12.13, 0), (9.13, -11.87, 8.0))

P.write(os.path.splitext(os.path.abspath(OUT))[0] + "_rooms.json",
        {"piece": "chapel", "note": "origin = nave footprint centre on finished ground; floor +0.45; entrance -Y",
         "zones": {"nave": [X0, X1, Y0, Y1], "sacristy": [SX0, SX1, Y1, SY1], "grotto": [gx - 1.7, gx + 1.7, gy - .9, gy + 1.1]}})
objs = C.mats(ctx, extra=[(ctx.basalt, "Basalt", lambda: B.tint_mat("M_BasaltMasonry", "BasaltMasonry", 2.0), 20)])
UCX = C.ucx_objs(ctx)
print("TRIS", B.tris(objs), "PIECE chapel SEED", SEED, "UCX", len(UCX), "ROOMS", len(P.rooms), "LOOT", len(P.LOOT))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT))
