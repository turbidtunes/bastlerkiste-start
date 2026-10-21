"""civlib.py – shared pieces for the civic / service buildings of Worker W2 (dispensary + community hall, police post,
fuel station, chapel, battery, mast, bridge). Builds on bldlib (MB, sweeps) and house/hlib (Ctx, cbox, walls,
windows, doors). Nothing here edits G's helpers.

Conventions: metres, Z up. Free-standing pieces take a centre (x, y) on the floor at z and a yaw in multiples of 90°:
local x = width, local y = depth, local -y = the FRONT (the side a person uses), local +y = back (against a wall).
Wall-mounted pieces take a point on the wall face p, the along-wall unit u and the outward wall normal n (pointing
into the room for interior walls).

ctx needs the MBs of hlib.Ctx plus ceramic, dark, fabric, paint, galv (add_mbs(ctx) creates them) and mats(ctx)
turns everything into material objects with the names the Session G buildings use (M_Plaster, M_Concrete …) plus
M_Fabric (two-sided cloth), M_Paint (painted steel / plastic, vertex colour), M_Galv.

Detail checklist (map/structures/REFERENCES.md "W2 detail checklist") is implemented by: sill_drip, streak,
paint_chips, crack_line, meter_box + service_drop, downpipe, spout, split_ac, tank_stand, worn_step, puddle,
plus the furniture used by the use-specific rooms (benches, desks, couches, shelving with goods, stacked chairs).
"""
import math
import numpy as np
import bpy
import bldlib as B
from bldlib import MB, srgb
from hlib import cbox

C_WHITE = (.92, .92, .9); C_GREY = (.55, .56, .57); C_DARK = (.08, .08, .09); C_STEEL = (.62, .64, .66)
C_BLUEP = srgb("#3d6fa8"); C_GREENP = srgb("#3f7a5a"); C_WOOD = (.55, .38, .24)


def add_mbs(ctx):
    for k in ("ceramic", "dark", "fabric", "paint", "galv", "lamp"):
        if not hasattr(ctx, k): setattr(ctx, k, MB())
    return ctx


# ------------------------------------------------------------------ local frames (yaw in 90° steps)
FLOOR = 0.0          # floor level for free-standing pieces placed with z=None (set per room group by the building script)


class F:
    """local frame at (x, y, z) with yaw degrees (multiples of 90); z=None = the current FLOOR"""
    def __init__(self, x, y, z=None, yaw=0):
        self.o = np.array([x, y, FLOOR if z is None else z], float); t = math.radians(yaw)
        self.ux = np.array([round(math.cos(t), 6), round(math.sin(t), 6), 0.]); self.uy = np.array([-self.ux[1], self.ux[0], 0.])

    def p(self, lx, ly, lz=0.0): return self.o + self.ux * lx + self.uy * ly + np.array([0, 0, lz])

    def box(self, mb, lo, hi, col, A=0.0, ucx=None):
        a, b = self.p(*lo), self.p(*hi)
        cbox(mb, np.minimum(a, b), np.maximum(a, b), {"all": col}, A=A)
        if ucx is not None: ucx.ucxb(np.minimum(a, b), np.maximum(a, b))

    def tube(self, mb, pts, r, n=6, col=(1, 1, 1), A=0.1):
        B.tube_path(mb, [self.p(*q) for q in pts], r, n, (*col, A))


def wbox(mb, p, u, n, a, b, z0, z1, d0, d1, col, A=0.0):
    """box on a wall: along u from a to b (m from p), height z0..z1 above p, depth d0..d1 along n"""
    p = np.asarray(p, float); u = np.asarray(u, float); n = np.asarray(n, float)
    q0 = p + u * a + n * d0 + [0, 0, z0]; q1 = p + u * b + n * d1 + [0, 0, z1]
    cbox(mb, np.minimum(q0, q1), np.maximum(q0, q1), {"all": col}, A=A)


def quad(mb, pts, col, A=0.0):
    mb.add(pts, [[0, 1, 2, 3]], [(float(p[0] + p[1]), float(p[2])) for p in pts], (*col, A))


# ------------------------------------------------------------------ exterior wear + services (detail checklist)
def streak(ctx, p, u, n, w, h, col, rng, mb=None, A=.42):
    """rain / mould streaks running down a wall face from p (top centre): thin films 1.5 mm proud, darkest at the
    top (vertex alpha = grime) fading out downwards"""
    mb = mb or ctx.plaster; p = np.asarray(p, float) + np.asarray(n) * .0015; u = np.asarray(u, float)
    flip = np.cross(u, [0, 0, 1]) @ np.asarray(n) >= 0
    for i in range(rng.randint(2, 5)):
        o = rng.uniform(-w / 2, w / 2); ww = rng.uniform(.03, .12); hh = h * rng.uniform(.4, 1.0)
        top = p + u * o; mid = top - [0, 0, hh * .4] + u * rng.uniform(-.01, .01); bot = top - [0, 0, hh]
        c = tuple(np.array(col) * rng.uniform(.82, .92)); a0 = A * rng.uniform(.6, 1.0)
        V = [top - u * ww / 2, top + u * ww / 2, mid + u * ww * .45, mid - u * ww * .45, bot + u * ww * .2, bot - u * ww * .2]
        F_ = [[0, 1, 2, 3], [3, 2, 4, 5]]
        if flip: F_ = [f[::-1] for f in F_]
        mb.add(V, F_, [(float(v @ u), float(v[2])) for v in V], [(*c, a0), (*c, a0), (*c, a0 * .55), (*c, a0 * .55), (*c, 0), (*c, 0)])


def sill_drip(ctx, c, u, n, w, col):
    """projecting precast sill with a drip groove under the nose (c = opening bottom centre on the outer face)"""
    c = np.asarray(c, float)
    wbox(ctx.conc, c, u, n, -w / 2 - .08, w / 2 + .08, -.05, -.005, -.02, .07, col)
    wbox(ctx.conc, c, u, n, -w / 2 - .08, w / 2 + .08, -.07, -.05, .03, .07, col)           # nose
    wbox(ctx.dark, c, u, n, -w / 2 - .06, w / 2 + .06, -.072, -.069, .045, .052, (.05, .05, .05))  # drip groove shadow line


def paint_chips(ctx, p, u, n, L, z0, z1, col_old, rng, k=6):
    """flaked paint showing the older colour / grey render underneath, 1 mm proud"""
    for _ in range(k):
        s = rng.uniform(.1, L - .3); z = rng.uniform(z0, z1 - .15); w = rng.uniform(.06, .28); h = rng.uniform(.04, .16)
        wbox(ctx.plaster, p, u, n, s, s + w, z, z + h, 0, .001, col_old, .15)


def crack_line(ctx, p, u, n, L, z, rng, col=(.16, .15, .14)):
    """hairline crack along a slab line (render shrinkage over the beam)"""
    s = rng.uniform(0, L * .3); pts = []
    while s < L:
        pts.append(np.asarray(p, float) + np.asarray(u) * s + np.asarray(n) * .0012 + [0, 0, z + rng.uniform(-.03, .03)]); s += rng.uniform(.25, .6)
        if rng.random() < .12 and len(pts) > 2: break
    for a, b in zip(pts[:-1], pts[1:]):
        d = np.array([0, 0, .006]); quad(ctx.dark, [a - d, b - d, b + d, a + d][::1 if np.cross(u, [0, 0, 1]) @ n < 0 else -1], col)


def downpipe(ctx, top, n, z_bot, col=(.86, .86, .83)):
    """PVC downpipe from a roof outlet down the wall, clips every 1.2 m, shoe at the bottom kicking out over a splash
    block; top = pipe top on the wall (outer face)"""
    t = np.asarray(top, float); n = np.asarray(n, float); o = t + n * .07
    B.tube_path(ctx.pvc, [t + n * .02 + [0, 0, .12], o, o - [0, 0, t[2] - z_bot - .25], o - [0, 0, t[2] - z_bot - .1] + n * .16], .045, 10, (*col, .25))
    for z in np.arange(z_bot + .6, t[2] - .2, 1.2):
        B.tube_path(ctx.galv, [t + n * .005 + [0, 0, z - t[2]], o + [0, 0, z - t[2]]], .012, 4, (.6, .6, .6, .3))
    sb = o + n * .2; cbox(ctx.conc, (sb[0] - .2, sb[1] - .2, z_bot - .01), (sb[0] + .2, sb[1] + .2, z_bot + .04), {"all": (.7, .69, .66)}, A=.5)


def spout(ctx, p, n, col=(.86, .86, .83)):
    """PVC overflow spout through a parapet with a dark run-off streak below"""
    p = np.asarray(p, float); n = np.asarray(n, float)
    B.tube_path(ctx.pvc, [p - n * .12, p + n * .25 - [0, 0, .02]], .037, 10, (*col, .2))


def meter_box(ctx, p, u, n, pole=None):
    """CEB-style meter cabinet (grey GRP box with a viewing window), conduit up to the service-drop bracket; with
    pole=(x, y, h) a sagging service-drop cable runs to that pole top (Unreal can replace it by a cable actor:
    SOCKET_Drop empty at the bracket)"""
    p = np.asarray(p, float); u = np.asarray(u, float); n = np.asarray(n, float)
    wbox(ctx.paint, p, u, n, -.22, .22, 1.2, 1.85, 0, .2, (.78, .79, .77), .15)
    wbox(ctx.glass, p, u, n, -.12, .12, 1.55, 1.75, .201, .203, (.6, .65, .65))
    wbox(ctx.dark, p, u, n, .18, .2, 1.4, 1.5, .2, .21, C_DARK)
    top = p + n * .05 + [0, 0, 1.85]; br = top + [0, 0, 1.0]
    B.tube_path(ctx.pvc, [top, br], .02, 8, (.85, .85, .83, .3))
    B.tube_path(ctx.galv, [br - [0, 0, .05], br + n * .25 - [0, 0, .05], br + n * .25 + [0, 0, .1]], .012, 6, (.6, .6, .6, .3))
    for z in (2.3, 2.75): wbox(ctx.galv, p, u, n, -.03, .03, z, z + .025, 0, .06, (.6, .6, .6))
    if pole is not None:
        a = br + n * .25 + [0, 0, .08]; b = np.asarray(pole, float); L = np.linalg.norm(b - a)
        pts = [a + (b - a) * f - [0, 0, L * .03 * math.sin(math.pi * f)] for f in np.linspace(0, 1, 14)]
        B.tube_path(ctx.dark, pts, .008, 5, (*C_DARK, 0))
    s = bpy.data.objects.new("SOCKET_Drop", None); bpy.context.scene.collection.objects.link(s); s.location = tuple(br + n * .25 + [0, 0, .08])


def split_ac(ctx, p, u, n, rng, inside=None):
    """outdoor unit of a split AC on wall brackets (fan grille, fins), refrigerant pipes in a trunking to the indoor
    unit, condensate hose dripping onto the ground (dark wet patch); inside = (p_in, u_in, n_in) for the indoor unit"""
    p = np.asarray(p, float); u = np.asarray(u, float); n = np.asarray(n, float)
    for s in (-.3, .3):                                           # brackets
        wbox(ctx.galv, p, u, n, s - .02, s + .02, -.05, 0, 0, .42, (.6, .6, .6))
        B.tube_path(ctx.galv, [p + u * s + [0, 0, -.45], p + u * s + n * .4 + [0, 0, -.03]], .012, 4, (.6, .6, .6, .3))
    wbox(ctx.paint, p, u, n, -.4, .4, 0, .55, .04, .34, (.9, .9, .88), .25)
    c = p + n * .341 + u * -.08 + [0, 0, .28]
    rings = [[c + (u * math.cos(t) + np.array([0, 0, 1.]) * math.sin(t)) * r + n * d for t in np.linspace(0, 2 * math.pi, 18, endpoint=False)] for r, d in ((.2, 0), (.2, .006), (.0, .006))]
    ctx.dark.grid(np.array(rings), col=(*C_DARK, .2), close_v=True)
    for k in range(5):
        wbox(ctx.paint, p, u, n, -.3, .14, .1 + k * .085, .11 + k * .085, .345, .36, (.85, .85, .83), .2)
    tr = p + u * .45 + n * .03                                   # pipe trunking up the wall into the room
    wbox(ctx.pvc, tr, u, n, -.04, .04, .1, .9, 0, .06, (.9, .9, .88), .2)
    B.tube_path(ctx.dark, [p + u * .2 + n * .04, p + u * .2 + n * .1 - [0, 0, rng.uniform(.6, 1.6)]], .008, 5, (*C_DARK, 0))
    if inside is not None:
        pi, ui, ni = (np.asarray(v, float) for v in inside)
        wbox(ctx.paint, pi, ui, ni, -.45, .45, 0, .3, 0, .22, (.94, .94, .92), .1)
        wbox(ctx.dark, pi, ui, ni, -.4, .4, .03, .06, .2, .222, (.3, .3, .3))


def tank_stand(ctx, x, y, z, col, h=1.2, n=1):
    """galvanised angle stand on a roof slab with n polyethylene tanks (1000 l), outlet pipes down to the slab"""
    import hlib as H
    L = 1.5 * n
    for xx in (x - L / 2, x + L / 2):
        for yy in (y - .7, y + .7):
            B.sweep(ctx.galv, np.array([[xx, yy, z], [xx, yy, z + h]]), B.rect(.05, .05), (.65, .66, .66, .4), up=(1, 0, 0))
            cbox(ctx.conc, (xx - .12, yy - .12, z), (xx + .12, yy + .12, z + .1), {"all": (.75, .74, .7)}, A=.4)
    for yy in (y - .7, y + .7):
        B.sweep(ctx.galv, np.array([[x - L / 2, yy, z + h], [x + L / 2, yy, z + h]]), B.rect(.05, .05), (.65, .66, .66, .4), up=(0, 0, 1))
        B.sweep(ctx.galv, np.array([[x - L / 2, yy, z + .15], [x + L / 2, yy, z + h - .05]]), B.rect(.04, .04), (.65, .66, .66, .4), up=(0, 0, 1))
    for k in range(n):
        H.water_tank(ctx, x - L / 2 + .75 + 1.5 * k, y, z + h - .45, col)
    ctx.ucxb((x - L / 2, y - .75, z), (x + L / 2, y + .75, z + h))


def worn_step(ctx, lo, hi, col, rng):
    """concrete step with rounded-off worn front edge + dark traffic patch"""
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    cbox(ctx.conc, lo, hi - [0, 0, .02], {"all": col}, A=.3)
    cbox(ctx.conc, lo + [.03, .03, 0], hi - [.03, .03, 0], {"all": col}, A=.35)
    m = (lo + hi) / 2; w = (hi - lo) * [.3, .3, 0]
    cbox(ctx.conc, (m[0] - w[0], m[1] - w[1], hi[2] - .001), (m[0] + w[0], m[1] + w[1], hi[2] + .001), {"all": tuple(np.array(col) * .8)}, A=.55)


def roof_patch(ctx, x, y, z, w, d, rng):
    """bitumen torch-on patch: irregular outline, slightly raised (8 mm) with a lap edge"""
    k = 12; R_ = [(1 + .25 * rng.uniform(-1, 1)) for _ in range(k)]
    for lift, sc, col in ((.006, 1.0, (.13, .13, .13)), (.009, .92, (.1, .1, .1))):
        pts = [(x + w / 2 * sc * R_[i] * math.cos(2 * math.pi * i / k), y + d / 2 * sc * R_[i] * math.sin(2 * math.pi * i / k), z + lift) for i in range(k)]
        ctx.dark.add(pts + [(x, y, z + lift)], [[i, (i + 1) % k, k] for i in range(k)], [(p[0], p[1]) for p in pts] + [(x, y)], (*col, .3))


def puddle(ctx, x, y, z, r, rng):
    """dark wet patch / oil stain decal (2 mm, ground) – Unreal: replace by a decal"""
    k = 14; pts = [(x + r * (1 + .3 * rng.uniform(-1, 1)) * math.cos(2 * math.pi * i / k), y + r * .7 * (1 + .3 * rng.uniform(-1, 1)) * math.sin(2 * math.pi * i / k), z + .002) for i in range(k)]
    o = ctx.conc.add(pts + [(x, y, z + .002)], [[i, (i + 1) % k, k] for i in range(k)], [(p[0], p[1]) for p in pts] + [(x, y)], (.35, .35, .33, .85))


# ------------------------------------------------------------------ exterior furniture
def bench_concrete(ctx, x, y, yaw, L=1.8, rng=None):
    f = F(x, y, None, yaw)
    for s in (-L / 2 + .2, L / 2 - .2): f.box(ctx.conc, (s - .06, -.15, 0), (s + .06, .15, .4), (.75, .74, .7), .3)
    f.box(ctx.conc, (-L / 2, -.2, .4), (L / 2, .2, .46), (.8, .79, .76), .3, ucx=ctx)


def flagpole(ctx, x, y, h=7.5):
    cbox(ctx.conc, (x - .6, y - .6, 0), (x + .6, y + .6, .3), {"all": (.85, .84, .8)}, A=.3)
    cbox(ctx.conc, (x - .4, y - .4, .3), (x + .4, y + .4, .45), {"all": (.85, .84, .8)}, A=.3)
    B.tube_path(ctx.galv, [(x, y, .45), (x, y, h)], .04, 10, (.75, .76, .76, .2))
    B.superellipsoid(ctx.galv, (x, y, h + .05), (.06, .06, .06), (1, 1), 10, 6, (.8, .7, .3, .1))
    B.tube_path(ctx.fabric, [(x + .045, y, 1.2), (x + .045, y, h - .1)], .004, 4, (.9, .9, .88, .1))      # halyard
    B.tube_path(ctx.galv, [(x + .04, y, 1.1), (x + .1, y, 1.1)], .01, 4, (.6, .6, .6, .2))               # cleat
    ctx.ucxb((x - .6, y - .6, 0), (x + .6, y + .6, .45)); ctx.ucxb((x - .05, y - .05, .45), (x + .05, y + .05, h))


def signboard(ctx, x, y, yaw, w=2.4, h=1.0, z0=1.4, col=(.93, .93, .9), band=None):
    """blank name board on two steel posts (no text)"""
    f = F(x, y, None, yaw)
    for s in (-w / 2 + .15, w / 2 - .15):
        f.tube(ctx.galv, [(s, 0, 0), (s, 0, z0 + h)], .035, 8, (.6, .62, .62), .3)
        f.box(ctx.conc, (s - .2, -.2, -.05), (s + .2, .2, .08), (.75, .74, .7), .3)
    f.box(ctx.paint, (-w / 2, -.05, z0), (w / 2, -.03, z0 + h), col, .2)
    if band: f.box(ctx.paint, (-w / 2, -.052, z0 + h * .72), (w / 2, -.05, z0 + h * .85), band, .1)
    f.box(ctx.paint, (-w / 2 - .03, -.06, z0 + h), (w / 2 + .03, -.02, z0 + h + .04), (.5, .5, .5), .3)
    ctx.ucxb(np.minimum(f.p(-w / 2, -.1, 0), f.p(w / 2, .1, 0)), np.maximum(f.p(-w / 2, -.1, 0), f.p(w / 2, .1, z0 + h)))


def bin_wheelie(ctx, x, y, yaw, col=C_GREENP):
    f = F(x, y, None, yaw)
    f.box(ctx.paint, (-.29, -.36, .06), (.29, .36, 1.0), col, .25, ucx=ctx)
    f.box(ctx.paint, (-.31, -.4, 1.0), (.31, .38, 1.06), col, .2)
    f.box(ctx.paint, (-.25, .36, .9), (.25, .42, .96), col, .2)                       # handle
    for s in (-.24, .24): f.tube(ctx.dark, [(s, .3, .1), (s, .36, .1)], .1, 12, C_DARK, .2)


def pot_plant(ctx, x, y, rng, r=.25, z0=None):
    """terracotta / concrete pot with a clump of leaves (simple blade fans – a placeholder for Session L plants)"""
    z0 = FLOOR if z0 is None else z0
    rings = [[(x + rr * math.cos(t), y + rr * math.sin(t), z0 + z) for t in np.linspace(0, 2 * math.pi, 14, endpoint=False)] for rr, z in ((r * .7, 0), (r, r * 1.5), (r * 1.08, r * 1.55), (r * .95, r * 1.6), (r * .9, r * 1.3))]
    ctx.paint.grid(np.array(rings), col=(*srgb(rng.choice(["#a5582f", "#b8b2a6", "#8c4a2a"])), .3), close_v=True)
    gcol = srgb(rng.choice(["#3c6b2c", "#4f7d32", "#2f5d2a"]))
    for k in range(rng.randint(7, 12)):
        t = rng.uniform(0, 2 * math.pi); L = rng.uniform(.35, .7) * r / .25; e = rng.uniform(.4, 1.1)
        d = np.array([math.cos(t), math.sin(t), 0]); s = np.cross(d, [0, 0, 1]) * .03
        b0 = np.array([x, y, z0 + r * 1.35]); tip = b0 + d * L * math.cos(e) + [0, 0, L * math.sin(e)]; mid = (b0 + tip) / 2 + [0, 0, .05]
        ctx.fabric.add([b0, mid + s * 2, tip, mid - s * 2], [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*gcol, .1))


def lpg_bottle(ctx, x, y, col=None, rng=None):
    col = col or srgb("#b03a2e"); z0 = FLOOR
    rings = [[(x + rr * math.cos(t), y + rr * math.sin(t), z) for t in np.linspace(0, 2 * math.pi, 14, endpoint=False)] for rr, z in ((.13, z0), (.15, z0 + .04), (.155, z0 + .45), (.12, z0 + .55), (.05, z0 + .6))]
    ctx.paint.grid(np.array(rings), col=(*col, .35), close_v=True)
    B.tube_path(ctx.galv, [(x, y, z0 + .6), (x, y, z0 + .66)], .03, 8, (.7, .65, .4, .2))
    B.tube_path(ctx.paint, [(x - .1, y, z0 + .62), (x - .1, y, z0 + .7), (x + .1, y, z0 + .7), (x + .1, y, z0 + .62)], .012, 5, (*col, .3))


def water_drum(ctx, x, y, col=C_BLUEP):
    z0 = FLOOR
    rings = [[(x + rr * math.cos(t), y + rr * math.sin(t), z0 + z) for t in np.linspace(0, 2 * math.pi, 18, endpoint=False)] for rr, z in ((.27, 0), (.29, .03), (.29, .3), (.3, .32), (.29, .34), (.29, .6), (.3, .62), (.29, .64), (.29, .9), (.0, .9))]
    ctx.paint.grid(np.array(rings), col=(*col, .3), close_v=True)
    ctx.ucxb((x - .3, y - .3, z0), (x + .3, y + .3, z0 + .9))


def monobloc(ctx, x, y, z, yaw, col=(.93, .93, .9), lite=False):
    """moulded polypropylene garden chair: splayed square-section legs, dished seat with a rolled front edge, back
    raked 12° with five vertical slots, curved arms from the front legs into the back"""
    f = F(x, y, z, yaw); c = (*col, .2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.tube(ctx.paint, [(sx * .25, sy * .24, 0), (sx * .22, sy * .2, .42)], .018, 4, col, .2)
    R = np.column_stack([f.ux, f.uy, [0, 0, 1.]])
    B.superellipsoid(ctx.paint, f.p(0, -.01, .43), (.23, .22, .025), (.3, .5), 10 if lite else 16, 4 if lite else 6, c, R=R)
    t = math.radians(12); Rb = R @ np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])
    for k in range(2 if lite else 6):                     # back: six slats between five slots, top rail, bottom rail
        if lite: B.box(ctx.paint, f.p(-.2 + k * .4, .23, .66), (.05, .02, .36), Rb, c); continue
        sx = -.2 + k * .08
        B.box(ctx.paint, f.p(sx, .23, .66) + f.uy * .0, (.05, .02, .36), Rb, c)
    B.box(ctx.paint, f.p(0, .26, .86), (.46, .025, .08), Rb, c)
    B.box(ctx.paint, f.p(0, .215, .5), (.46, .02, .06), Rb, c)
    for sx in (-.24, .24):
        f.tube(ctx.paint, [(sx, -.2, .44), (sx * 1.03, -.18, .62), (sx * 1.04, .05, .65), (sx, .22, .62)], .018, 5, col, .2)


def chair_stack(ctx, x, y, yaw, k=8, col=(.93, .93, .9)):
    for i in range(k): monobloc(ctx, x, y, FLOOR + i * .085, yaw, col, lite=i < k - 1)
    ctx.ucxb((x - .3, y - .3, FLOOR), (x + .3, y + .3, FLOOR + .85 + k * .085))


# ------------------------------------------------------------------ interior furniture (use-specific)
def beam_bench(ctx, x, y, yaw, seats=3, col=C_BLUEP):
    """public-waiting tandem bench: 80x40 steel beam on T-legs with floor feet, moulded seat + back shells per seat
    (separate, 25 mm gap, back raked on a bent steel arm), alloy arm rests between seats"""
    f = F(x, y, None, yaw); L = seats * .6; R = np.column_stack([f.ux, f.uy, [0, 0, 1.]]); dk = (.3, .31, .32)
    for s_ in (-L / 2 + .22, L / 2 - .22):
        f.box(ctx.paint, (s_ - .03, -.28, 0), (s_ + .03, .28, .025), dk, .3)
        f.box(ctx.paint, (s_ - .035, -.035, .025), (s_ + .035, .035, .34), dk, .3)
    f.box(ctx.paint, (-L / 2, -.04, .34), (L / 2, .04, .38), dk, .3)
    t = math.radians(12); Rb = R @ np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])
    for i in range(seats):
        c = -L / 2 + .3 + i * .6
        f.box(ctx.paint, (c - .03, -.12, .38), (c + .03, .12, .42), dk, .3)                       # seat bracket
        B.superellipsoid(ctx.paint, f.p(c, -.02, .445), (.235, .22, .022), (.25, .45), 14, 6, (*col, .15), R=R)
        f.tube(ctx.paint, [(c, .08, .41), (c, .2, .44), (c, .25, .55)], .014, 5, dk, .3)
        B.superellipsoid(ctx.paint, f.p(c, .27, .69), (.22, .02, .17), (.3, .45), 14, 6, (*col, .15), R=Rb)
        if i < seats - 1:
            f.tube(ctx.galv, [(c + .3, .05, .38), (c + .3, -.05, .62), (c + .3, .2, .62)], .012, 5, C_STEEL, .15)
    a, b = f.p(-L / 2, -.28, 0), f.p(L / 2, .3, .86); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def desk(ctx, x, y, yaw, w=1.4, d=.7, col=(.75, .62, .45), steel=False):
    """office desk: melamine top, drawer pedestal right, modesty panel; steel=True grey steel desk (police)"""
    f = F(x, y, None, yaw); cc = (.6, .62, .62) if steel else col
    mb = ctx.paint if steel else ctx.timber
    f.box(mb, (-w / 2, -d / 2, .72), (w / 2, d / 2, .75), cc, .15)
    f.box(mb, (w / 2 - .42, -d / 2 + .02, 0), (w / 2 - .02, d / 2 - .02, .72), cc, .2)
    for k in range(3): f.box(ctx.dark, (w / 2 - .3, -d / 2 + .01, .15 + k * .2), (w / 2 - .14, -d / 2 + .02, .17 + k * .2), (.2, .2, .2))
    f.box(mb, (-w / 2 + .02, -d / 2 + .02, 0), (-w / 2 + .05, d / 2 - .02, .72), cc, .2)
    f.box(mb, (-w / 2 + .05, d / 2 - .05, .3), (w / 2 - .42, d / 2 - .03, .72), cc, .2)
    a, b = f.p(-w / 2, -d / 2, 0), f.p(w / 2, d / 2, .75); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def desk_items(ctx, x, y, yaw, rng, screen=True):
    """things on a desk: monitor + keyboard (blank), file stack, mug, phone"""
    f = F(x, y, FLOOR + .75, yaw)
    if screen:
        f.box(ctx.dark, (-.25, .05, .1), (.25, .08, .4), C_DARK, .1); f.box(ctx.dark, (-.03, .06, 0), (.03, .12, .1), C_DARK)
        f.box(ctx.dark, (-.12, .05, 0), (.12, .2, .01), C_DARK); f.box(ctx.dark, (-.22, -.2, 0), (.22, -.05, .02), (.15, .15, .15))
    for k in range(rng.randint(2, 6)):
        f.box(ctx.paint, (.35 + rng.uniform(-.02, .02), -.1 + rng.uniform(-.02, .02), k * .025), (.6, .2, k * .025 + .022), srgb(rng.choice(["#e8e4d8", "#d8c070", "#9ab8d8", "#e0a0a0"])), .1)
    f.tube(ctx.ceramic, [(-.45, -.1, 0), (-.45, -.1, .1)], .04, 10, (.9, .9, .88), .1)
    f.box(ctx.dark, (-.6, .05, 0), (-.42, .25, .06), (.15, .15, .15))


def office_chair(ctx, x, y, yaw, col=(.12, .12, .14)):
    f = F(x, y, None, yaw)
    for k in range(5):
        t = 2 * math.pi * k / 5; f.tube(ctx.dark, [(0, 0, .08), (.28 * math.cos(t), .28 * math.sin(t), .06)], .015, 5, C_DARK, .1)
    f.tube(ctx.galv, [(0, 0, .08), (0, 0, .45)], .025, 8, C_STEEL, .1)
    f.box(ctx.fabric, (-.24, -.24, .45), (.24, .22, .53), col, .1)
    f.box(ctx.fabric, (-.22, .2, .58), (.22, .27, 1.0), col, .1)
    f.tube(ctx.dark, [(0, .2, .5), (0, .24, .6)], .02, 6, C_DARK, .1)


def visitor_chair(ctx, x, y, yaw, col=(.2, .3, .5)):
    """tubular-steel visitor chair (sled base), padded vinyl seat + back"""
    f = F(x, y, None, yaw); R = np.column_stack([f.ux, f.uy, [0, 0, 1.]])
    for sx in (-.21, .21):
        f.tube(ctx.galv, [(sx, -.24, 0), (sx, .2, 0), (sx, .2, .45), (sx, -.2, .45)], .011, 6, C_STEEL, .1)
        f.tube(ctx.galv, [(sx, .2, .45), (sx, .24, .88)], .011, 6, C_STEEL, .1)
    B.superellipsoid(ctx.fabric, f.p(0, -.01, .48), (.23, .22, .035), (.3, .4), 12, 6, (*col, .1), R=R)
    B.superellipsoid(ctx.fabric, f.p(0, .235, .74), (.22, .025, .13), (.3, .4), 12, 6, (*col, .1), R=R)


def exam_couch(ctx, x, y, yaw, rng):
    """examination couch (steel frame, vinyl pad, head raised, paper roll) + 2-step stool"""
    f = F(x, y, None, yaw); L, W = 1.9, .6
    for sx in (-L / 2 + .05, L / 2 - .05):
        for sy in (-W / 2 + .04, W / 2 - .04): f.box(ctx.galv, (sx - .02, sy - .02, 0), (sx + .02, sy + .02, .62), (.85, .86, .86))
    f.box(ctx.galv, (-L / 2, -W / 2, .58), (L / 2, W / 2, .62), (.85, .86, .86))
    f.box(ctx.fabric, (-L / 2 + .55, -W / 2, .62), (L / 2, W / 2, .7), srgb("#2f5a7a"), .1)
    a0 = f.p(-L / 2, -W / 2, .62); a1 = f.p(-L / 2 + .55, W / 2, .62)
    t = math.radians(25); dz = .55 * math.sin(t)
    V = [f.p(-L / 2 + .55, -W / 2, .62), f.p(-L / 2 + .55, W / 2, .62), f.p(-L / 2 + .55 - .55 * math.cos(t), W / 2, .62 + dz), f.p(-L / 2 + .55 - .55 * math.cos(t), -W / 2, .62 + dz)]
    V += [v + [0, 0, .08] for v in V]
    ctx.fabric.add(V, [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]], [(v[0] + v[1], v[2]) for v in V], (*srgb("#2f5a7a"), .1))
    f.box(ctx.fabric, (-L / 2 + .6, -W / 2 + .05, .702), (L / 2 - .05, W / 2 - .05, .704), (.95, .95, .93), 0)      # paper sheet
    f.tube(ctx.fabric, [(L / 2 + .02, -W / 2 + .05, .66), (L / 2 + .02, W / 2 - .05, .66)], .05, 10, (.95, .95, .93), 0)
    s = F(*f.p(0, -W / 2 - .3, 0)[:2], None, 0)
    for k, (h, d) in enumerate(((.2, .36), (.4, .18))): s.box(ctx.galv, (-.22, -.18, h - .03), (.22, -.18 + d, h), (.85, .86, .86))
    for sx in (-.2, .2): s.box(ctx.galv, (sx - .01, -.18, 0), (sx + .01, .18, .4), (.85, .86, .86))
    a, b = f.p(-L / 2, -W / 2, 0), f.p(L / 2, W / 2, .75); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def screen_rail(ctx, pts, z, rng, col=srgb("#8fb8c8")):
    """ceiling curtain track (L) with a pleated privacy curtain hanging to 0.25 m above the floor, partly drawn"""
    pts = [np.array([p[0], p[1], z]) for p in pts]
    B.tube_path(ctx.galv, pts, .012, 6, (.85, .86, .86, .1))
    for pa, pb in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(pb - pa); d = (pb - pa) / L; s = np.cross([0, 0, 1], d); m = max(2, int(L * rng.uniform(.4, .8) / .12))
        for k in range(m):
            q0 = pa + d * k * .12; q1 = q0 + d * .12; o0 = s * (.035 if k % 2 else -.035); o1 = -o0
            V = [q0 + o0 - [0, 0, z - .25], q1 + o1 - [0, 0, z - .25], q1 + o1 - [0, 0, .04], q0 + o0 - [0, 0, .04]]
            ctx.fabric.add(V, [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*col, .05)); ctx.fabric.add(V[::-1], [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*col, .05))


def shelving(ctx, x, y, yaw, w=1.0, d=.4, h=2.0, levels=5, rng=None, goods="boxes", col=(.6, .62, .62)):
    """slotted-angle steel shelving with goods: boxes (blank coloured cartons), files (ring binders), meds (small
    packs + bottles), linen (folded stacks)"""
    f = F(x, y, None, yaw)
    for sx in (-w / 2, w / 2 - .035):
        for sy in (-d / 2, d / 2 - .035): f.box(ctx.galv, (sx, sy, 0), (sx + .035, sy + .035, h), col)
    zs = np.linspace(.08, h - .05, levels)
    for z in zs: f.box(ctx.galv, (-w / 2, -d / 2, z - .02), (w / 2, d / 2, z), col)
    for z in zs[:-1] if goods != "boxes" else zs:
        x_ = -w / 2 + .03
        while x_ < w / 2 - .1:
            if goods == "files":
                bw = .055; c = srgb(rng.choice(["#2a4f8f", "#7a2a2a", "#2f6b45", "#c8a030", "#202020", "#e8e4d8"]))
                f.box(ctx.paint, (x_, -d / 2 + .04, z), (x_ + bw - .004, d / 2 - .06, z + .3), c, .1); x_ += bw
            elif goods == "meds":
                bw = rng.uniform(.05, .14); hh = rng.uniform(.05, .16); c = srgb(rng.choice(["#f2f2ee", "#e8e4d8", "#d8e8f0", "#f0e0e0", "#e0f0e0", "#f4e9c8"]))
                if rng.random() < .25:
                    r = bw / 2.2; f.tube(ctx.paint, [(x_ + r, -d / 2 + .1, z), (x_ + r, -d / 2 + .1, z + hh + .05)], r, 8, srgb(rng.choice(["#6a3a1a", "#f2f2ee", "#3a6a9a"])), .1)
                else:
                    for dd in (0, .12): f.box(ctx.paint, (x_, -d / 2 + .04 + dd, z), (x_ + bw - .006, -d / 2 + .11 + dd, z + hh), c, .1)
                x_ += bw
            elif goods == "oil":
                k_ = rng.random(); hh_top = (zs[1] - zs[0]) - .05 if len(zs) > 1 else .3
                if k_ < .4:                                   # 4-5 l jugs with a handle (unlabelled)
                    c = srgb(rng.choice(["#1a3a8a", "#c8a020", "#2a6a3a", "#d8d8d0", "#8a1a1a"]))
                    f.box(ctx.paint, (x_, -.12, z), (x_ + .14, .12, z + min(.3, hh_top)), c, .15); f.box(ctx.paint, (x_ + .04, .02, z + min(.3, hh_top)), (x_ + .1, .1, z + min(.3, hh_top) + .04), c, .15)
                    x_ += .16
                elif k_ < .8:                                 # 1 l bottles in a row
                    for j in range(3):
                        c = srgb(rng.choice(["#1a3a8a", "#c8a020", "#2a6a3a", "#e8e8e0"])); f.tube(ctx.paint, [(x_ + .04, -.1 + j * .1, z), (x_ + .04, -.1 + j * .1, z + .2), (x_ + .04, -.1 + j * .1, z + .25)], .035, 8, c, .15)
                    x_ += .09
                else:                                         # 20 l pail
                    f.tube(ctx.paint, [(x_ + .15, 0, z), (x_ + .15, 0, z + min(.36, hh_top))], .14, 12, srgb(rng.choice(["#1a3a8a", "#c8281e", "#2a2a2a"])), .2); x_ += .31
            elif goods == "linen":
                bw = .32; c = srgb(rng.choice(["#f2f2ee", "#cfe0ee", "#e8d8e8"]))
                f.box(ctx.fabric, (x_, -d / 2 + .04, z), (x_ + bw - .02, d / 2 - .04, z + rng.uniform(.12, .25)), c, .1); x_ += bw
            else:
                bw = rng.uniform(.25, .5); hh = min(rng.uniform(.18, .38), (zs[1] - zs[0]) - .05) if len(zs) > 1 else .3
                if rng.random() < .8:
                    f.box(ctx.paint, (x_, -d / 2 + .02, z), (x_ + bw - .02, d / 2 - .02, z + hh), srgb(rng.choice(["#b89a6a", "#c8aa78", "#a88a5a", "#d8d0c0"])), .2)
                x_ += bw
    a, b = f.p(-w / 2, -d / 2, 0), f.p(w / 2, d / 2, h); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def filing_cabinet(ctx, x, y, yaw, drawers=4, col=(.42, .5, .46)):
    """steel 4-drawer filing cabinet: drawer fronts with shadow gaps, pull handles, label-holder frames (blank)"""
    f = F(x, y, None, yaw); h = drawers * .33
    f.box(ctx.paint, (-.235, -.29, 0), (.235, .31, h), col, .25)
    f.box(ctx.dark, (-.225, -.291, .02), (.225, -.29, h - .01), (.1, .1, .1))
    for k in range(drawers):
        z = .03 + k * .33; f.box(ctx.paint, (-.222, -.31, z), (.222, -.292, z + .31), tuple(np.array(col) * 1.06), .2)
        f.tube(ctx.galv, [(-.09, -.31, z + .2), (-.09, -.35, z + .2), (.09, -.35, z + .2), (.09, -.31, z + .2)], .011, 5, (.9, .9, .9), .1)
        f.box(ctx.dark, (-.222, -.313, z + .305), (.222, -.31, z + .315), (.05, .05, .05))
        f.box(ctx.galv, (-.04, -.315, z + .24), (.04, -.31, z + .27), (.8, .8, .8))
    a, b = f.p(-.235, -.31, 0), f.p(.235, .31, h); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def fridge(ctx, x, y, yaw, h=1.45, col=(.93, .93, .92), glass=False, rng=None):
    """upright fridge; glass=True: glass-door drinks cooler – lit interior, wire shelves with unlabelled bottles and
    cans, door frame + handle, plinth grille"""
    f = F(x, y, None, yaw)
    if not glass:
        f.box(ctx.paint, (-.3, -.3, .02), (.3, .32, h), col, .2)
        f.box(ctx.galv, (.22, -.34, h * .5), (.25, -.3, h * .8), (.8, .8, .8))
        f.box(ctx.dark, (-.3, .32, .1), (.3, .34, h - .2), C_DARK)
    else:
        import random as _r
        rr = rng or _r.Random(int(abs(x * 100 + y * 10)))
        for (lo, hi) in (((-.3, -.3, .02), (.3, .34, .14)), ((-.3, -.3, h - .2), (.3, .34, h)), ((-.3, -.3, .14), (-.27, .34, h - .2)), ((.27, -.3, .14), (.3, .34, h - .2)), ((-.3, .31, .14), (.3, .34, h - .2))):
            f.box(ctx.paint, lo, hi, col, .2)
        f.box(ctx.lamp, (-.26, .3, .16), (.26, .305, h - .22), (.9, .95, 1.0))                       # lit back panel
        for k in range(4): f.box(ctx.dark, (-.26 + k * .15, -.302, .04), (-.18 + k * .15, -.3, .12), (.1, .1, .1))   # plinth grille
        zs_ = np.linspace(.2, h - .35, 5)
        for z in zs_:
            f.box(ctx.galv, (-.27, -.25, z - .01), (.27, .3, z), (.75, .75, .75))
            xx = -.24
            while xx < .22:
                r_ = rr.uniform(.025, .04); hh = rr.uniform(.12, .22) if z < zs_[-1] else .1
                c = srgb(rr.choice(["#2a6a3a", "#8a2a1a", "#e8e0c0", "#3a5aa8", "#c8a030", "#f2f2ee"]))
                f.tube(ctx.glass if rr.random() < .6 else ctx.paint, [(xx + r_, 0, z), (xx + r_, 0, z + hh * .75), (xx + r_, 0, z + hh)], r_, 8, c, .05)
                xx += 2 * r_ + .01
        f.box(ctx.glass, (-.27, -.3, .14), (.27, -.295, h - .2), (.75, .85, .88))
        f.box(ctx.galv, (.2, -.33, h * .35), (.23, -.3, h * .7), (.8, .8, .8))
    a, b = f.p(-.3, -.3, 0), f.p(.3, .34, h); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))

def trolley(ctx, x, y, yaw, rng):
    """stainless dressing trolley, two shelves, with a kidney dish, bottles, gauze packs"""
    f = F(x, y, None, yaw)
    for sx in (-.3, .3):
        for sy in (-.2, .2):
            f.tube(ctx.galv, [(sx, sy, .08), (sx, sy, .9)], .012, 6, (.85, .86, .86), .05)
            f.tube(ctx.dark, [(sx, sy - .03, .04), (sx, sy + .03, .04)], .035, 8, C_DARK, .1)
    for z in (.3, .86): f.box(ctx.galv, (-.32, -.22, z), (.32, .22, z + .015), (.85, .86, .86), .05)
    f.box(ctx.galv, (-.2, -.1, .875), (.0, .02, .9), (.88, .88, .88))
    for k in range(3): f.tube(ctx.paint, [(.08 + k * .07, .1, .875), (.08 + k * .07, .1, .99)], .025, 8, srgb(rng.choice(["#f2f2ee", "#8a4a2a", "#3a6aaa"])), .05)
    f.box(ctx.fabric, (-.28, -.18, .315), (.1, .1, .37), (.95, .95, .93), 0)


def wall_basin(ctx, p, u, n, col=(.95, .95, .94)):
    """small wall-hung hand-wash basin with a lever tap, paper towel box and soap dispenser above"""
    p = np.asarray(p, float); u = np.asarray(u, float); n = np.asarray(n, float)
    R = np.column_stack([u, n, [0, 0, 1]])
    B.superellipsoid(ctx.ceramic, p + n * .2 + [0, 0, .8], (.22, .18, .08), (.6, .7), 14, 6, (*col, 0), R=R)
    B.tube_path(ctx.galv, [p + n * .03 + [0, 0, .88], p + n * .03 + [0, 0, .98], p + n * .14 + [0, 0, .98]], .01, 6, (.8, .8, .8, .1))
    wbox(ctx.paint, p, u, n, .3, .58, 1.3, 1.65, 0, .12, (.95, .95, .94), .05)
    wbox(ctx.paint, p, u, n, -.4, -.28, 1.2, 1.42, 0, .1, (.92, .92, .9), .05)
    B.tube_path(ctx.galv, [p + n * .01 + [0, 0, .72], p + n * .01 + [0, 0, .1]], .015, 6, (.8, .8, .8, .2))


def notice_board(ctx, p, u, n, w, h, z0, rng):
    """cork / felt notice board with pinned blank sheets (no text)"""
    wbox(ctx.timber, p, u, n, -w / 2, w / 2, z0, z0 + h, 0, .02, (.6, .45, .3))
    wbox(ctx.fabric, p, u, n, -w / 2 + .04, w / 2 - .04, z0 + .04, z0 + h - .04, .02, .022, srgb("#2f5a3a"))
    for k in range(rng.randint(4, 9)):
        a = rng.uniform(-w / 2 + .08, w / 2 - .3); z = rng.uniform(z0 + .08, z0 + h - .35)
        ww, hh = (.21, .297) if rng.random() < .7 else (.297, .21)
        wbox(ctx.paint, p, u, n, a, a + ww, z, z + hh, .022, .0235, srgb(rng.choice(["#f4f2ec", "#f4f2ec", "#f0e6a0", "#d8e8f4", "#f4d8d8"])))


def wall_clock(ctx, p, n, z=2.2):
    p = np.asarray(p, float) + [0, 0, z]; n = np.asarray(n, float); up = np.array([0, 0, 1.])
    s = np.cross(n, up)
    rings = [[p + n * d + (s * math.cos(t) + up * math.sin(t)) * r for t in np.linspace(0, 2 * math.pi, 20, endpoint=False)] for r, d in ((.15, 0), (.15, .04), (.13, .04), (0, .035))]
    ctx.paint.grid(np.array(rings), col=(.95, .95, .93, .05), close_v=True)
    for (a, L) in ((.3, .09), (1.9, .06)):
        q = p + n * .036; quad(ctx.dark, [q - s * .004, q + s * .004, q + s * .004 + (s * math.cos(a) + up * math.sin(a)) * L, q - s * .004 + (s * math.cos(a) + up * math.sin(a)) * L][::-1], C_DARK)


def extinguisher(ctx, p, u, n):
    p = np.asarray(p, float); n = np.asarray(n, float)
    c = p + n * .1
    rings = [[c + np.array([.08 * math.cos(t), .08 * math.sin(t), z]) for t in np.linspace(0, 2 * math.pi, 12, endpoint=False)] for z in (.6, .62, 1.05, 1.1)]
    ctx.paint.grid(np.array(rings), col=(.75, .08, .06, .1), close_v=True)
    B.tube_path(ctx.dark, [c + [0, 0, 1.1], c + [0, 0, 1.18], c + np.asarray(u) * .06 + [0, 0, 1.18]], .015, 6, (*C_DARK, .1))
    wbox(ctx.galv, p, u, n, -.04, .04, .9, .96, 0, .03, (.6, .6, .6))


def ceiling_fan(ctx, c, rng, col=(.92, .92, .9)):
    """ceiling fan hanging from c (ceiling point): downrod, motor, 3 blades"""
    c = np.asarray(c, float)
    B.tube_path(ctx.galv, [c, c - [0, 0, .45]], .012, 6, (*col, .1))
    B.superellipsoid(ctx.paint, c - [0, 0, .02], (.07, .07, .03), (1, 1), 10, 4, (*col, .1))
    B.superellipsoid(ctx.paint, c - [0, 0, .5], (.12, .12, .07), (1, .7), 14, 6, (*col, .1))
    a0 = rng.uniform(0, 2)
    for k in range(3):
        t = a0 + 2 * math.pi * k / 3; d = np.array([math.cos(t), math.sin(t), 0]); s = np.array([-d[1], d[0], 0])
        p = c - [0, 0, .52] + d * .12; q = c - [0, 0, .53] + d * .7
        for V in ([p - s * .05, p + s * .05, q + s * .07, q - s * .07], [q - s * .07, q + s * .07, p + s * .05, p - s * .05]):
            ctx.paint.add(V, [[0, 1, 2, 3]], [(0, 0), (1, 0), (1, 1), (0, 1)], (*col, .1))


def tube_light(ctx, c):
    c = np.asarray(c, float)
    cbox(ctx.paint, c + [-.62, -.05, -.06], c + [.62, .05, 0], {"all": (.92, .92, .9)}, A=.1)
    B.tube_path(ctx.lamp, [c + [-.6, 0, -.075], c + [.6, 0, -.075]], .016, 8, (1, 1, .97, 0))


def folding_table(ctx, x, y, yaw, L=1.8, W=.75, folded=False):
    f = F(x, y, None, yaw)
    if folded:                                       # leaning on a wall: top vertical (local +y = wall)
        f.box(ctx.paint, (-L / 2, .02, .02), (L / 2, .06, W), (.88, .87, .84), .2); return
    f.box(ctx.paint, (-L / 2, -W / 2, .7), (L / 2, W / 2, .74), (.9, .89, .86), .2)
    for sx in (-L / 2 + .15, L / 2 - .15):
        for sy in (-W / 2 + .08, W / 2 - .08): f.tube(ctx.galv, [(sx, sy, 0), (sx, sy, .7)], .013, 6, (.4, .4, .4), .2)
    a, b = f.p(-L / 2, -W / 2, 0), f.p(L / 2, W / 2, .74); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def boxes_pile(ctx, x, y, rng, n=4):
    z = FLOOR
    for k in range(n):
        w, d, h = rng.uniform(.3, .6), rng.uniform(.3, .5), rng.uniform(.2, .4)
        dx, dy = rng.uniform(-.05, .05), rng.uniform(-.05, .05)
        cbox(ctx.paint, (x - w / 2 + dx, y - d / 2 + dy, z), (x + w / 2 + dx, y + d / 2 + dy, z + h), {"all": srgb(rng.choice(["#b89a6a", "#c8aa78", "#a88a5a"]))}, A=.25)
        z += h
    ctx.ucxb((x - .3, y - .25, FLOOR), (x + .3, y + .25, z))


# ------------------------------------------------------------------ materials
def mats(ctx, extra=()):
    """all ctx MBs -> objects (names + materials as Session G); returns the object list"""
    def corr_mat():
        m = B.plain_mat("M_Corrugated", (.62, .63, .62), .45, .9)
        N_, L_ = m.node_tree.nodes, m.node_tree.links; bs = N_["Principled BSDF"]
        vc = [n for n in N_ if n.bl_idname == "ShaderNodeVertexColor"][0]; src = bs.inputs["Base Color"].links[0].from_socket
        mx = N_.new("ShaderNodeMix"); mx.data_type = 'RGBA'; L_.new(vc.outputs["Alpha"], mx.inputs["Factor"]); L_.new(src, mx.inputs["A"])
        mx.inputs["B"].default_value = (*srgb("#7a3e1f"), 1); L_.new(mx.outputs["Result"], bs.inputs["Base Color"]); return m

    def glass_mat():
        gm = bpy.data.materials.new("M_Glass"); gm.use_nodes = True; gb = gm.node_tree.nodes["Principled BSDF"]
        gb.inputs["Base Color"].default_value = (.7, .8, .78, 1); gb.inputs["Roughness"].default_value = .25; gb.inputs["Transmission Weight"].default_value = .7
        return gm
    def lamp_mat():
        """fluorescent tube / bulb, switched on (Unreal: emissive MI, intensity per level)"""
        m = bpy.data.materials.new("M_LampOn"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (1, 1, .97, 1); b.inputs["Emission Color"].default_value = (1, .98, .92, 1)
        b.inputs["Emission Strength"].default_value = 6.0; return m
    table = [(ctx.plaster, "Walls", lambda: B.paint_mat("M_Plaster", tex="Plaster", tile=2.0), 20),
             (ctx.raw, "Blockwork", lambda: B.tint_mat("M_Blockwork", "Blockwork", 2.0), 20),
             (ctx.tile, "Floors", lambda: B.tint_mat("M_FloorTile", "FloorTile", 1.8), 20),
             (ctx.conc, "Concrete", lambda: B.paint_mat("M_Concrete", tex="Concrete", tile=3.5), 20),
             (ctx.rebar, "Rebar", lambda: B.plain_mat("M_Rebar", srgb("#5a3a26"), .85, .4), 60),
             (ctx.steel, "Steel", lambda: B.plain_mat("M_Steel", (1, 1, 1), .55, .2), 40),
             (ctx.alu, "Alu", lambda: B.plain_mat("M_Alu", (1, 1, 1), .35, .9), 40),
             (ctx.glass, "Glass", glass_mat, 30),
             (ctx.timber, "Timber", lambda: B.tint_mat("M_Timber", "WoodWeathered", 1.0), 30),
             (ctx.paintwood, "PaintedWood", lambda: B.paint_mat("M_PaintedWood", tex="BoatPaint", tile=1.0), 30),
             (ctx.door, "Doors", lambda: B.paint_mat("M_DoorPaint", tex="BoatPaint", tile=1.0), 30),
             (ctx.corr, "Corrugated", corr_mat, 30),
             (ctx.tank, "Tank", lambda: B.plain_mat("M_TankPE", (1, 1, 1), .6), 40),
             (ctx.pvc, "PVC", lambda: B.plain_mat("M_PVC", (1, 1, 1), .5), 40),
             (ctx.ceramic, "Ceramic", lambda: B.plain_mat("M_Ceramic", (1, 1, 1), .12, 0, .6), 40),
             (ctx.dark, "Dark", lambda: B.plain_mat("M_Dark", (1, 1, 1), .7), 40),
             (ctx.paint, "Paint", lambda: B.plain_mat("M_Paint", (1, 1, 1), .45), 40),
             (ctx.galv, "Galv", lambda: B.plain_mat("M_Galv", (.75, .76, .76), .4, 1.0), 40),
             (ctx.fabric, "Fabric", lambda: B.plain_mat("M_Fabric", (1, 1, 1), .85), 40),
             (ctx.lamp, "Lamp", lamp_mat, 40)] + list(extra)
    import bmesh
    objs = []
    for mb, nm, mk, sm in table:
        if not (mb.n() or mb.leaves): continue
        o = mb.obj(nm, mk(), sm, recalc=False)
        # box faces (cbox / B.box) are single-face islands with correct winding; only closed multi-face islands
        # (superellipsoids, lathe rings) are recalculated – a global recalc flips single faces at random
        bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table(); seen = set(); multi = []
        for f in bm.faces:
            if f.index in seen: continue
            isl, st = [], [f]; seen.add(f.index)
            while st:
                g = st.pop(); isl.append(g)
                for e in g.edges:
                    for h in e.link_faces:
                        if h.index not in seen: seen.add(h.index); st.append(h)
            if len(isl) >= 6 and nm not in ("Corrugated", "Fabric"): multi.extend(isl)
        if multi: bmesh.ops.recalc_face_normals(bm, faces=multi)
        bm.to_mesh(o.data); bm.free(); objs.append(o)
    return objs


def ucx_objs(ctx):
    U = [B.ucx([c + s / 2 * np.array([i, j, k]) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], f"UCX_b{n}") for n, (c, s) in enumerate(ctx.ucx)]
    U += [B.ucx(p, f"UCX_h{n}") for n, p in enumerate(ctx.hulls)]
    for o in U: o.hide_set(True)
    return U


# ------------------------------------------------------------------ partitions + interior doors (axis aligned)
def pwall(ctx, p0, p1, z0, z1, t, ops=(), col_l=(1, 1, 1), col_r=(1, 1, 1), mb=None, ucx=True):
    """interior wall p0 -> p1 (axis aligned), thickness t centred on the line, openings [(u0, u1, v0, v1)] in metres
    along the wall from p0 and above z0. col_l = face on the left of p0->p1 (seen from above), col_r = right face."""
    mb = mb or ctx.plaster
    p0, p1 = np.asarray(p0, float)[:2], np.asarray(p1, float)[:2]; L = float(np.linalg.norm(p1 - p0)); d = (p1 - p0) / L
    nl = np.array([-d[1], d[0]])
    cuts = sorted({0.0, L, *[min(max(o[0], 0), L) for o in ops], *[min(max(o[1], 0), L) for o in ops]})
    kl = ("py" if nl[1] > 0 else "ny") if abs(nl[1]) > .5 else ("px" if nl[0] > 0 else "nx")
    kr = {"px": "nx", "nx": "px", "py": "ny", "ny": "py"}[kl]
    for ua, ub in zip(cuts[:-1], cuts[1:]):
        if ub - ua < 1e-4: continue
        um = (ua + ub) / 2; H_ = z1 - z0
        bl = sorted([(o[2], o[3]) for o in ops if o[0] < um < o[1]]); iv, cur = [], 0.0
        for v0, v1 in bl:
            if v0 > cur: iv.append((cur, v0))
            cur = max(cur, v1)
        if cur < H_: iv.append((cur, H_))
        for va, vb in iv:
            if vb - va < .005: continue
            a = p0 + d * ua - nl * t / 2; b = p0 + d * ub + nl * t / 2
            lo = np.array([min(a[0], b[0]), min(a[1], b[1]), z0 + va]); hi = np.array([max(a[0], b[0]), max(a[1], b[1]), z0 + vb])
            cbox(mb, lo, hi, {"all": col_l, kl: col_l, kr: col_r})
            if ucx: ctx.ucxb(lo, hi)


def idoor(ctx, hinge, u, n_in, col, open_deg=75, w=.86, h=2.06, frame_col=(.92, .9, .85), t=.2):
    """interior door: leaf (hlib.door_leaf) + pressed-steel / timber lining in the opening (both faces flush)"""
    import hlib as H
    hinge = np.asarray(hinge, float); u = np.asarray(u, float); n_in = np.asarray(n_in, float)
    H.door_leaf(ctx, hinge, u, n_in, col, open_deg=open_deg, w=w, h=h)
    for s0, s1 in ((-.04, 0.0), (w, w + .04)):
        q0 = hinge + u * s0 - n_in * t + [0, 0, 0]; q1 = hinge + u * s1 + [0, 0, h + .04]
        cbox(ctx.paintwood, np.minimum(q0, q1), np.maximum(q0, q1), {"all": frame_col})
    q0 = hinge + u * -.04 - n_in * t + [0, 0, h]; q1 = hinge + u * (w + .04) + [0, 0, h + .04]
    cbox(ctx.paintwood, np.minimum(q0, q1), np.maximum(q0, q1), {"all": frame_col})


def breeze_block(ctx, c, u, n, w, h, t=.2, col=(.92, .9, .86)):
    """claustra / breeze-block ventilation panel (cast 'cross' blocks 200 mm) filling an opening; c = bottom centre
    on the wall centre line"""
    c = np.asarray(c, float); u = np.asarray(u, float); n = np.asarray(n, float)
    nb_u = max(1, int(round(w / .2))); nb_v = max(1, int(round(h / .2))); bu = w / nb_u; bv = h / nb_v
    for i in range(nb_u):
        for j in range(nb_v):
            o = c + u * (-w / 2 + (i + .5) * bu) + [0, 0, (j + .5) * bv]
            for (du, dv, su, sv) in ((0, -bv / 2 + .015, bu, .03), (0, bv / 2 - .015, bu, .03), (-bu / 2 + .015, 0, .03, bv), (bu / 2 - .015, 0, .03, bv), (0, 0, bu, .03), (0, 0, .03, bv)):
                q = o + u * du + [0, 0, dv]
                lo = q - u * su / 2 - n * t / 2 - [0, 0, sv / 2]; hi = q + u * su / 2 + n * t / 2 + [0, 0, sv / 2]
                cbox(ctx.plaster, np.minimum(lo, hi), np.maximum(lo, hi), {"all": col})


def wheel(mb, c, axis, r, w=.03, n=20, col=C_DARK, spokes=0):
    """tyre ring (rectangular section swept round axis) + optional spokes/hand rim"""
    c = np.asarray(c, float); ax = np.asarray(axis, float); ax /= np.linalg.norm(ax)
    e1 = np.cross(ax, [0, 0, 1.]) if abs(ax[2]) < .9 else np.array([1., 0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
    pts = [c + (e1 * math.cos(t) + e2 * math.sin(t)) * r for t in np.linspace(0, 2 * math.pi, n + 1)]
    B.tube_path(mb, pts, w, 6, (*col, .1))
    for k in range(spokes):
        t = 2 * math.pi * k / spokes; B.tube_path(mb, [c, c + (e1 * math.cos(t) + e2 * math.sin(t)) * r * .95], .004, 3, (.75, .75, .75, .1))


def wheelchair(ctx, x, y, yaw):
    """folding steel wheelchair: 24" rear wheels with hand rims, castors, sling seat + back, footplates"""
    f = F(x, y, None, yaw); st = (.75, .76, .77)
    for sx in (-.3, .3):
        wheel(ctx.dark, f.p(sx, .12, .3), f.ux, .3, .016, 24, C_DARK, 12)
        wheel(ctx.galv, f.p(sx * 1.08, .12, .3), f.ux, .27, .008, 24, st)
        wheel(ctx.dark, f.p(sx * .85, -.35, .09), f.ux, .08, .015, 12, C_DARK)
        f.tube(ctx.galv, [(sx * .85, -.35, .17), (sx * .85, -.3, .48), (sx * .85, .2, .5), (sx * .85, .25, .95), (sx * .85, .3, 1.0)], .012, 6, st, .1)
        f.tube(ctx.galv, [(sx * .85, -.3, .48), (sx * .8, -.45, .12)], .01, 6, st, .1)
        f.box(ctx.dark, (sx * .85 - .07, -.52, .1), (sx * .85 + .07, -.4, .12), C_DARK)
    f.box(ctx.fabric, (-.25, -.25, .48), (.25, .2, .5), (.12, .12, .14), .1)
    f.box(ctx.fabric, (-.25, .2, .55), (.25, .23, .92), (.12, .12, .14), .1)
    a, b = f.p(-.33, -.5, 0), f.p(.33, .42, 1.0); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def wall_tv(ctx, p, u, n, z=2.0, w=.9):
    """flat TV on a tilting wall bracket (screen off, no logo)"""
    p = np.asarray(p, float); u = np.asarray(u, float); n = np.asarray(n, float)
    wbox(ctx.galv, p, u, n, -.1, .1, z - .1, z + .1, 0, .12, (.2, .2, .2))
    wbox(ctx.dark, p, u, n, -w / 2, w / 2, z - w * .29, z + w * .29, .12, .17, (.04, .04, .045))
    wbox(ctx.glass, p, u, n, -w / 2 + .015, w / 2 - .015, z - w * .29 + .015, z + w * .29 - .015, .171, .172, (.05, .06, .07))
    B.tube_path(ctx.dark, [p + n * .02 + u * .05 + [0, 0, z - .2], p + n * .02 + u * .05 + [0, 0, .35]], .006, 4, (*C_DARK, 0))


def posters(ctx, p, u, n, L, z0, rng, k=3):
    """blank health-campaign posters (coloured sheets, no text) taped to a wall"""
    s = rng.uniform(.1, .4)
    for i in range(k):
        w, h = (.42, .594) if rng.random() < .6 else (.297, .42)
        if s + w > L: break
        z = z0 + rng.uniform(-.05, .1)
        wbox(ctx.paint, p, u, n, s, s + w, z, z + h, 0, .0015, srgb(rng.choice(["#f4f2ec", "#cfe6f4", "#f6e3b4", "#d8efd2", "#f4d4d0"])))
        wbox(ctx.paint, p, u, n, s + .03, s + w - .03, z + h * .62, z + h * .9, .0015, .002, srgb(rng.choice(["#3a6aa8", "#c84a3a", "#3f8a5a", "#e09a30"])))
        s += w + rng.uniform(.15, .6)


def counter(ctx, x, y, yaw, L=2.0, d=.6, h=1.05, col=(.7, .55, .38), top=(.85, .85, .82)):
    """reception counter: panelled front (cover 1.0), worktop behind at desk height, raised top"""
    f = F(x, y, None, yaw)
    f.box(ctx.timber, (-L / 2, -d / 2, 0), (L / 2, -d / 2 + .05, h), col, .2)
    for sx in (-L / 2, L / 2 - .05): f.box(ctx.timber, (sx, -d / 2, 0), (sx + .05, d / 2, h), col, .2)
    f.box(ctx.timber, (-L / 2, -d / 2 + .05, .72), (L / 2, d / 2, .75), col, .2)
    f.box(ctx.paint, (-L / 2 - .03, -d / 2 - .06, h), (L / 2 + .03, -d / 2 + .25, h + .03), top, .2)
    f.box(ctx.dark, (-L / 2, -d / 2 - .002, 0), (L / 2, -d / 2, .1), (.15, .15, .15))
    a, b = f.p(-L / 2, -d / 2, 0), f.p(L / 2, d / 2, h); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def bunk_bed(ctx, x, y, yaw, rng, col=(.35, .4, .38)):
    """steel bunk bed (barrack room): square-tube frame, ladder, two foam mattresses, blanket, pillow"""
    f = F(x, y, None, yaw); L, W = 1.95, .9
    for sx in (-L / 2, L / 2):
        for sy in (-W / 2, W / 2): f.tube(ctx.paint, [(sx, sy, 0), (sx, sy, 1.75)], .018, 4, col, .3)
    for z in (.35, 1.3):
        for sy in (-W / 2, W / 2): f.box(ctx.paint, (-L / 2, sy - .015, z - .05), (L / 2, sy + .015, z), col, .3)
        for sx in (-L / 2, L / 2): f.box(ctx.paint, (sx - .015, -W / 2, z - .05), (sx + .015, W / 2, z), col, .3)
        f.box(ctx.fabric, (-L / 2 + .02, -W / 2 + .02, z), (L / 2 - .02, W / 2 - .02, z + .12), (.75, .72, .6), .2)
        f.box(ctx.fabric, (-L / 2 + .3, -W / 2 + .01, z + .12), (L / 2 - .02, W / 2 - .01, z + .15), srgb(rng.choice(["#4a5a3a", "#5a4a3a", "#3a4a6a", "#7a2a2a"])), .2)
        f.box(ctx.fabric, (-L / 2 + .04, -W / 2 + .15, z + .12), (-L / 2 + .3, W / 2 - .15, z + .22), (.92, .92, .9), .1)
    f.box(ctx.paint, (-L / 2, W / 2 - .02, 1.45), (L / 2, W / 2 + .01, 1.48), col, .3)       # upper guard rail
    for z in np.arange(.55, 1.3, .25): f.tube(ctx.paint, [(L / 2 - .02, -W / 2 + .1, z), (L / 2 - .02, W / 2 - .1, z)], .012, 4, col, .3)
    a, b = f.p(-L / 2, -W / 2, 0), f.p(L / 2, W / 2, 1.75); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def locker(ctx, x, y, yaw, n=2, col=(.55, .6, .58)):
    """steel personal locker bank: doors with vent louvres, padlock hasps"""
    f = F(x, y, None, yaw); w = .38 * n
    f.box(ctx.paint, (-w / 2, -.25, 0), (w / 2, .25, 1.8), col, .3)
    for i in range(n):
        x0 = -w / 2 + i * .38
        f.box(ctx.paint, (x0 + .01, -.255, .05), (x0 + .37, -.25, 1.78), tuple(np.array(col) * 1.06), .25)
        for k in range(6): f.box(ctx.dark, (x0 + .1, -.257, 1.45 + k * .04), (x0 + .28, -.255, 1.465 + k * .04), (.1, .1, .1))
        f.box(ctx.galv, (x0 + .31, -.27, .95), (x0 + .34, -.255, 1.05), (.8, .75, .5))
    a, b = f.p(-w / 2, -.25, 0), f.p(w / 2, .25, 1.8); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def gun_rack(ctx, x, y, yaw, slots=6, col=(.28, .3, .3)):
    """steel rifle rack: butt trough with slotted divider plate, upright posts, notched muzzle bar with felt pads,
    hinged locking bar with a padlock hasp (the rifles themselves are loot – SOCKET_Loot_* in the slots)"""
    f = F(x, y, None, yaw); w = slots * .16 + .1
    f.box(ctx.paint, (-w / 2, -.22, 0), (w / 2, .1, .04), col, .3)                                 # base tray
    f.box(ctx.paint, (-w / 2, -.22, .04), (w / 2, -.2, .22), col, .3)                              # trough front
    for k in range(slots + 1): f.box(ctx.paint, (-w / 2 + .03 + k * .16, -.2, .04), (-w / 2 + .05 + k * .16, .1, .2), col, .3)   # butt dividers
    for sx in (-w / 2, w / 2 - .04): f.box(ctx.paint, (sx, .05, 0), (sx + .04, .12, 1.25), col, .3)
    f.box(ctx.paint, (-w / 2, -.06, 1.0), (w / 2, .12, 1.04), col, .3)                             # muzzle bar
    for k in range(slots):
        sx = -w / 2 + .07 + k * .16
        f.box(ctx.dark, (sx, -.061, 1.0), (sx + .06, .02, 1.041), (.04, .04, .04))                  # notches
        f.box(ctx.fabric, (sx - .005, .02, 1.0), (sx + .065, .025, 1.045), (.15, .3, .15), .1)      # felt pad
    f.box(ctx.steel, (-w / 2, -.09, 1.06), (w / 2, -.07, 1.1), (.55, .56, .56), .3)                # locking bar
    f.box(ctx.steel, (w / 2 - .02, -.12, 1.03), (w / 2 + .03, -.06, 1.13), (.7, .6, .3), .2)        # hasp + padlock
    a, b = f.p(-w / 2, -.22, 0), f.p(w / 2, .12, 1.25); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))

def steel_cabinet(ctx, x, y, yaw, w=.9, d=.45, h=1.9, col=(.5, .54, .52)):
    """two-door steel cupboard: door gaps, swing handle with padlock hasp, vent slots top + bottom, plinth"""
    f = F(x, y, None, yaw)
    f.box(ctx.paint, (-w / 2, -d / 2, .05), (w / 2, d / 2, h), col, .3)
    f.box(ctx.dark, (-w / 2 + .02, -d / 2 + .02, 0), (w / 2 - .02, d / 2 - .02, .05), (.08, .08, .08))
    f.box(ctx.dark, (-.003, -d / 2 - .002, .08), (.003, -d / 2, h - .03), (.08, .08, .08))
    for sx in (-1, 1):
        for z0_ in (.15, h - .3):
            for k in range(4): f.box(ctx.dark, (sx * .12 - .08 * sx, -d / 2 - .002, z0_ + k * .035), (sx * .32, -d / 2, z0_ + k * .035 + .015), (.08, .08, .08))
    f.box(ctx.galv, (.03, -d / 2 - .035, h * .5 - .1), (.055, -d / 2, h * .5 + .1), (.8, .8, .8))
    f.box(ctx.steel, (.06, -d / 2 - .03, h * .5 - .02), (.1, -d / 2, h * .5 + .04), (.7, .6, .3), .2)
    a, b = f.p(-w / 2, -d / 2, 0), f.p(w / 2, d / 2, h); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))

def radio_set(ctx, x, y, z, yaw):
    """base-station radio on a desk: transceiver, PSU, desk microphone, coax up the wall"""
    f = F(x, y, z, yaw)
    f.box(ctx.dark, (-.15, 0, 0), (.15, .25, .08), (.12, .12, .13)); f.box(ctx.dark, (.18, 0, 0), (.38, .22, .12), (.2, .2, .2))
    f.box(ctx.glass, (-.12, -.001, .02), (-.02, 0, .06), (.3, .6, .3))
    f.tube(ctx.dark, [(-.3, .05, 0), (-.3, .05, .2), (-.28, 0, .26)], .008, 5, C_DARK, .1)
    f.tube(ctx.dark, [(0, .25, .05), (0, .4, .05), (0, .4, 1.5)], .007, 5, C_DARK, .1)


def logbook(ctx, x, y, z, yaw, rng):
    """open occurrence book (blank pages), pen, rubber stamp pad"""
    f = F(x, y, z, yaw)
    f.box(ctx.paint, (-.32, -.22, 0), (0, .22, .025), (.2, .25, .45), .2); f.box(ctx.paint, (0, -.22, 0), (.32, .22, .025), (.2, .25, .45), .2)
    f.box(ctx.paint, (-.3, -.2, .025), (-.005, .2, .03), (.95, .94, .9)); f.box(ctx.paint, (.005, -.2, .025), (.3, .2, .03), (.95, .94, .9))
    f.tube(ctx.dark, [(.1, -.1, .035), (.22, .05, .035)], .004, 4, (.1, .1, .3), 0)
    f.box(ctx.dark, (.4, -.1, 0), (.5, .0, .02), (.15, .15, .15))


def kettle_counter(ctx, x, y, z, yaw, rng):
    """tea corner on a worktop: electric kettle, mugs, sugar tin, biscuit tin"""
    f = F(x, y, z, yaw)
    f.tube(ctx.paint, [(0, 0, 0), (0, 0, .22)], .085, 12, (.9, .9, .88), .1); f.tube(ctx.dark, [(0, 0, .22), (0, 0, .25)], .03, 8, (.2, .2, .2), .1)
    for k in range(3): f.tube(ctx.ceramic, [(.2 + k * .1, .05, 0), (.2 + k * .1, .05, .1)], .04, 10, srgb(rng.choice(["#f2f2ee", "#c84a3a", "#3a6aa8"])), .1)
    f.tube(ctx.galv, [(-.22, .05, 0), (-.22, .05, .15)], .06, 12, (.8, .7, .3), .2)


def block_pile(ctx, x, y, rng, n=8, col=(.62, .61, .58)):
    """leftover 400x200x200 hollow blocks stacked loosely (builders' leftovers behind every Mauritian building)"""
    k = 0
    for row in range(3):
        for i in range(max(1, n // 3 - row)):
            dx = i * .41 - .4 + row * .2 + rng.uniform(-.02, .02); z = row * .2
            cbox(ctx.raw, (x + dx - .2, y - .1, z), (x + dx + .2, y + .1, z + .195), {"all": col}, A=.4); k += 1
    ctx.ucxb((x - .62, y - .12, 0), (x + .62, y + .12, .6))


def ladder(ctx, p_foot, p_top, w=.42):
    """aluminium step ladder leaning on a wall"""
    a, b = np.asarray(p_foot, float), np.asarray(p_top, float); d = b - a; s = np.cross(d, [0, 0, 1.]); s = s / np.linalg.norm(s) * w / 2
    for sg in (-1, 1): B.tube_path(ctx.galv, [a + s * sg, b + s * sg * .8], .02, 4, (.8, .8, .8, .2))
    for f in np.linspace(.08, .95, 9): B.tube_path(ctx.galv, [a + d * f - s * (1 - .2 * f), a + d * f + s * (1 - .2 * f)], .012, 4, (.8, .8, .8, .2))


def arch_fill(mb, c, u, n, w, zs, zt, t, col, kind="pointed", A=0.0, seg=10):
    """solid spandrels that turn a rectangular wall opening (top at zt) into an arch springing at zs: c = bottom
    centre of the opening on the OUTER face, the wall runs from the outer face inwards (-n) over t."""
    c = np.asarray(c, float); u = np.asarray(u, float); n = np.asarray(n, float); h = zt - zs
    def curve(s):                                           # s 0..1 from the left spring to the apex
        if kind == "round":
            a = math.pi * (1 - s / 2); return (w / 2 * math.cos(a), zs + h * math.sin(a) if h > 0 else zs)
        R = w * .8                                          # pointed: two arcs of radius R (equilateral-ish)
        cx = -w / 2 + R; ang0 = math.pi; x_ap = 0.0
        a1 = math.acos((x_ap - cx) / R); a = ang0 + (a1 - ang0) * s
        return (cx + R * math.cos(a), zs + (h / (R * math.sin(a1))) * R * abs(math.sin(a)))
    for side in (-1, 1):
        pts = [curve(k / seg) for k in range(seg + 1)]
        pts = [(side * x, z) for x, z in pts]
        poly = pts + [(side * w / 2, zt)]                   # curve from spring to apex, then the corner
        for d0, d1, flip in ((0, 0, False),):
            pass
        V = [c + u * x + [0, 0, z] for x, z in poly] + [c + u * x - n * t + [0, 0, z] for x, z in poly]
        m = len(poly); F_ = [list(range(m)), list(range(2 * m - 1, m - 1, -1))]
        if side < 0: F_ = [f[::-1] for f in F_]
        for i in range(m):
            j = (i + 1) % m; q = [i, j, j + m, i + m]
            F_.append(q if side > 0 else q[::-1])
        mb.add(V, F_, [(float(v @ u + v @ n), float(v[2])) for v in V], (*col, A))


def pew(ctx, x, y, yaw, L=2.8, col=(.45, .3, .18)):
    """timber church pew: shaped end panels, seat, raked back, book shelf, hinged kneeler (front -y = towards the altar
    is the BACK of the pew in front: the person sits facing local -y)"""
    f = F(x, y, None, yaw)
    for sx in (-L / 2, L / 2 - .05):
        f.box(ctx.timber, (sx, -.25, 0), (sx + .05, .3, .9), col, .2)
        f.box(ctx.timber, (sx - .01, .2, .88), (sx + .06, .32, .95), col, .2)
    f.box(ctx.timber, (-L / 2 + .05, -.2, .43), (L / 2 - .05, .2, .47), col, .15)
    R = np.column_stack([f.ux, f.uy, [0, 0, 1.]]); t = math.radians(10)
    Rb = R @ np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])
    for z in (.62, .82): B.box(ctx.timber, f.p(0, .24 + (z - .62) * .18, z), (L - .1, .025, .16), Rb, (*col, .15))
    f.box(ctx.timber, (-L / 2 + .05, .3, .6), (L / 2 - .05, .45, .62), col, .15)              # book shelf on the back
    f.box(ctx.timber, (-L / 2 + .05, .43, .62), (L / 2 - .05, .45, .7), col, .15)
    f.box(ctx.fabric, (-L / 2 + .07, .5, .1), (L / 2 - .07, .67, .16), srgb("#6a2a2a"), .2)   # kneeler for the row behind
    a, b = f.p(-L / 2, -.25, 0), f.p(L / 2, .45, .95); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))


def candle(mb, p, h=.25, r=.02, lit=False, ctx=None):
    p = np.asarray(p, float)
    B.tube_path(mb, [p, p + [0, 0, h]], r, 8, (.96, .94, .86, .05))
    if lit and ctx is not None: B.superellipsoid(ctx.lamp, p + [0, 0, h + .02], (.006, .006, .015), (1, 1), 6, 4, (1, .8, .4, 0))


def votive_rack(ctx, x, y, yaw, rng):
    """tiered steel votive-candle stand with tealight cups, some burning, wax drips"""
    f = F(x, y, None, yaw)
    for sx in (-.45, .45):
        f.tube(ctx.galv, [(sx, -.2, 0), (sx, -.2, .9)], .015, 6, (.25, .25, .25), .3); f.tube(ctx.galv, [(sx, .2, 0), (sx, .2, 1.2)], .015, 6, (.25, .25, .25), .3)
    for k, (yy, z) in enumerate(((-.15, .85), (0, 1.0), (.15, 1.15))):
        f.box(ctx.galv, (-.5, yy - .07, z - .02), (.5, yy + .07, z), (.3, .3, .3), .4)
        for j in range(8):
            if rng.random() < .75:
                p = f.p(-.44 + j * .125, yy, z); B.tube_path(ctx.galv, [p, p + [0, 0, .03]], .02, 8, (.7, .1, .08, .1))
                if rng.random() < .5: B.superellipsoid(ctx.lamp, p + [0, 0, .045], (.005, .005, .012), (1, 1), 6, 4, (1, .8, .4, 0))
        f.box(ctx.paint, (-.5, yy - .07, z - .025), (.5, yy + .07, z - .02), (.92, .9, .82), .1)   # wax spill
    a, b = f.p(-.5, -.25, 0), f.p(.5, .25, 1.2); ctx.ucxb(np.minimum(a, b), np.maximum(a, b))
