"""Reusable building API for incremental Blender 4.x/UE5 LOD0 assets.

Adapted from bastlerkiste/map/structures/bldlib.py and house/hlib.py.
Uses the proven legacy mesh and wall algorithms, but deliberately avoids
legacy automatic weather textures, UCX/FBX exports, and furniture geometry.

Every operation creates ordinary named Blender meshes with an allowed
material slot and metre-scaled UV0. The stage worker retains export control.

Example:
    import building_kit as kit
    kit.wall("front", (-4, 4, -6, 6), "front", 0, 3, .3,
             openings=[(1, 2.2, 0, 2.2, "door")])
    kit.door_leaf(1, (-3, -6, 0), width=1.18, height=2.18)
"""
from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
LEGACY = HERE / "legacy"
if str(LEGACY) not in sys.path:
    sys.path.insert(0, str(LEGACY))

# Imported modules are copied verbatim from the pre-existing building library.
import bldlib as B  # noqa: E402
import hlib as H    # noqa: E402

SUPPORTED = set("""
plaster_white plaster_cream_warm render_spalled_old limewash blockwork_raw concrete_cast
basalt_masonry basalt_dressed sandstone_ashlar brick_old rubble_pointing mixed_fieldstone pebble_mosaic
weatherboard_cream white_peeling_timber painted_timber_warmgrey wood_weathered wood_mahogany_varnished
oak_honey shutter_paint paint_clean roof_terracotta terracotta roof_slate_grey roof_steel_bluegrey
corrugated_rust galvanized_steel thatch_palm steel_painted_worn steel_bare_rusty aluminium_weathered
stainless_brushed copper_patina brass_tarnished floor_tiles ceramic_glazed_white pavers_concrete
flagstone limestone_flag ceramic_glazed mirror_silver stone_counter_light canvas_fabric textile_cotton
rubber_black plastic_weathered glass lamp_glass placeholder
""".split())

# Telemetry is diagnostic only; the generated script is free to use bpy for
# unusual, project-specific shapes.
CALLS: dict[str, int] = {}


def _track(name):
    CALLS[name] = CALLS.get(name, 0) + 1


def material(name: str):
    """Name-compatible, texture-free Principled BSDF preview material."""
    if name not in SUPPORTED and not re.fullmatch(r"(new|sign|poster)_[a-z0-9_]+", name):
        raise ValueError(f"Material nicht erlaubt: {name}")
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (
            (0.27, 0.37, 0.48, 1) if name == "glass"
            else (0.64, 0.56, 0.39, 1) if name in {"wood_weathered", "wood_mahogany_varnished", "oak_honey"}
            else (0.45, 0.47, 0.47, 1) if name.startswith(("steel_", "aluminium_", "galvanized_"))
            else (0.66, 0.72, 0.84, 1) if name == "placeholder"
            else (0.84, 0.82, 0.76, 1)
        )
        bsdf.inputs["Roughness"].default_value = .15 if name == "glass" else .8
        if name == "glass":
            bsdf.inputs["Transmission Weight"].default_value = .75
    return m


def _emit(mesh_builder, name: str, surface: str, location=None, yaw_deg=0):
    """Build standard Blender geometry using the original B.MB vertex/face/UV arrays.

    B.MB.obj is intentionally NOT used: the historical obj() starts an
    optional weather_geo dependency and historically handles UCX materials.
    This adapter creates only what the LOD0 worker is allowed to export.
    """
    if not mesh_builder.F:
        raise ValueError(f"Leerer Mesh-Baustein: {name}")
    if name in bpy.data.objects:
        raise ValueError(f"Objektname bereits vergeben: {name}")
    me = bpy.data.meshes.new(name)
    me.from_pydata(mesh_builder.V, [], mesh_builder.F)
    me.validate()
    me.update()
    uv = me.uv_layers.new(name="UVMap")
    # B.MB stores metre UV per vertex; duplicate them for each face corner.
    for loop in me.loops:
        i = loop.vertex_index
        uv.data[loop.index].uv = (
            float(mesh_builder.UV[i][0]),
            float(mesh_builder.UV[i][1]),
        )
    me.materials.append(material(surface))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if location is not None:
        ob.location = location
    ob.rotation_euler[2] = math.radians(yaw_deg)
    return ob


def _positive(*numbers):
    if any(not math.isfinite(float(n)) or n <= 0 for n in numbers):
        raise ValueError(f"Erwartet positive metrische Maße: {numbers}")


def box(name: str, lo, hi, surface="plaster_white"):
    """Closed solid in WORLD coordinates (min/max XYZ), metre UVs."""
    a = np.asarray(lo, dtype=float)
    b = np.asarray(hi, dtype=float)
    if a.shape != (3,) or b.shape != (3,):
        raise ValueError("lo/hi brauchen XYZ")
    _positive(*(b - a))
    mb = B.MB()
    B.box(mb, (a + b) / 2, b - a)
    _track("box")
    return _emit(mb, name, surface)


def wall(name: str, rect, side: str, z0: float, z1: float,
         thickness: float, openings=(), surface="plaster_white"):
    """Wall along a rectangular footprint, with REAL door/window holes.

    rect=(x0,x1,y0,y1). side='front'|'back'|'left'|'right'.
    Opening offsets (u0,u1,sill_z,height_top_z,kind) run from the
    direction-specific start of that façade, metres above z0.
    E.g. (2,3.2,0,2.2,'door'), (4,5.2,.9,2.1,'window').
    """
    if side not in ("front", "back", "left", "right"):
        raise ValueError("side muss front/back/left/right sein")
    _positive(z1 - z0, thickness)
    coords = tuple(float(v) for v in rect)
    if len(coords) != 4 or coords[1] <= coords[0] or coords[3] <= coords[2]:
        raise ValueError("rect=(x0<x1,y0<y1) erforderlich")
    L = coords[1] - coords[0] if side in ("front", "back") else coords[3] - coords[2]
    ops = []
    for entry in openings:
        if len(entry) != 5:
            raise ValueError("opening=(u0,u1,z0,z1,kind)")
        u0, u1, lo, hi, kind = entry
        if not (0 <= u0 < u1 <= L and 0 <= lo < hi <= z1 - z0):
            raise ValueError(f"Öffnung außerhalb der Wand: {entry}")
        ops.append((u0, u1, lo, hi, kind))
    ctx = H.Ctx(random.Random(0))
    H.wall(ctx, coords, side, z0, z1, thickness, ops, (.85, .85, .85),
           (.82, .82, .82), ucx=False)
    _track("wall")
    return _emit(ctx.plaster, name, surface)


def partition(name: str, start, end, z0, z1, thickness=.12,
              door_spans=(), surface="plaster_white"):
    """Interior partition using original hlib.partition, real 2.1-m door holes."""
    _positive(z1 - z0, thickness)
    start = tuple(start)
    end = tuple(end)
    if len(start) != 3 or len(end) != 3:
        raise ValueError("start,end als XYZ")
    ctx = H.Ctx(random.Random(0))
    H.partition(ctx, start, end, z0, z1, thickness,
                doors=list(door_spans), col=(.85, .85, .85))
    _track("partition")
    return _emit(ctx.plaster, name, surface)


def slab(name: str, rect, z0: float, thickness=.22,
         surface="concrete_cast"):
    """Solid slab; rect=(x0,x1,y0,y1), lower face at z0."""
    x0, x1, y0, y1 = map(float, rect)
    _positive(x1 - x0, y1 - y0, thickness)
    _track("slab")
    return box(name, (x0, y0, z0), (x1, y1, z0 + thickness), surface)


def door_leaf(number: int, hinge, width=1.0, height=2.1, thickness=.05,
              hinge_side="L", opens="in", yaw_deg=0, surface="wood_weathered"):
    """Separate closed hinge-pivot door leaf, local +X from hinge to latch."""
    _positive(width, height, thickness)
    if not .04 <= thickness <= .06:
        raise ValueError("Türblattstärke 40–60 mm erwartet")
    if hinge_side not in ("L", "R") or opens not in ("in", "out"):
        raise ValueError("hinge_side=L/R, opens=in/out")
    if len(hinge) != 3:
        raise ValueError("hinge braucht XYZ")
    name = f"DoorLeaf_{int(number):02d}_{hinge_side}_{opens}"
    mb = B.MB()
    B.box(mb, (width / 2, 0, height / 2), (width, thickness, height))
    _track("door_leaf")
    return _emit(mb, name, surface, location=tuple(hinge), yaw_deg=yaw_deg)


def placeholder(room: str, role: str, number: int, location,
                size, yaw_deg=0):
    """One furniture box, local origin at floor centre, front points -Y."""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", room + "_" + role):
        raise ValueError("Raum/Rolle nur lower_snake_case")
    w, d, h = map(float, size)
    _positive(w, d, h)
    if len(location) != 3:
        raise ValueError("location als XYZ am Box-Fußpunkt")
    mb = B.MB()
    B.box(mb, (0, 0, h / 2), (w, d, h))
    _track("placeholder")
    return _emit(mb, f"Ph_{room}_{role}_{int(number):02d}",
                 "placeholder", location=tuple(location), yaw_deg=yaw_deg)


def window(name, centre, width, height, yaw_deg=0,
           frame_thickness=.06, frame_depth=.09,
           frame_surface="painted_timber_warmgrey", with_glass=True):
    """Rectangular closed window frame and separate solid glass inside an opening.

    centre is window opening CENTRE, yaw=0 means across X on Y=centre.y;
    supply a real wall opening separately (this does not cut walls).
    """
    _positive(width, height, frame_thickness, frame_depth)
    if width < 2 * frame_thickness or height < 2 * frame_thickness:
        raise ValueError("Fenster zu klein für Rahmenstärke")
    if len(centre) != 3:
        raise ValueError("centre als XYZ")
    mb = B.MB()
    t, d, w, h = frame_thickness, frame_depth, width, height
    B.box(mb, (-w / 2 + t / 2, 0, 0), (t, d, h))
    B.box(mb, (w / 2 - t / 2, 0, 0), (t, d, h))
    B.box(mb, (0, 0, -h / 2 + t / 2), (w - 2 * t, d, t))
    B.box(mb, (0, 0, h / 2 - t / 2), (w - 2 * t, d, t))
    _track("window")
    obs = [_emit(mb, name + "_Frame", frame_surface,
                 location=tuple(centre), yaw_deg=yaw_deg)]
    if with_glass:
        pane = B.MB()
        B.box(pane, (0, 0, 0), (w - 2 * t, .008, h - 2 * t))
        obs.append(_emit(pane, name + "_Glass", "glass",
                         location=tuple(centre), yaw_deg=yaw_deg))
    return obs


def staircase(name: str, location, rise_total, width=1.2,
              tread=.28, top_landing=1.4, yaw_deg=0,
              surface="concrete_cast"):
    """Solid straight run (+local Y), each step supported down to floor.

    No automatically invented turn; for U/L stairs compose multiple runs.
    Conforms to minimum tread .28 m and maximum rise .18 m.
    """
    _positive(rise_total, width, tread, top_landing)
    if tread < .28 or width < 1.2 or top_landing < 1.2:
        raise ValueError("Treppe braucht Breite>=1.2, Auftritt>=.28, Podest>=1.2")
    n = int(math.ceil(rise_total / .18))
    actual_rise = rise_total / n
    mb = B.MB()
    for i in range(n):
        step_h = actual_rise * (i + 1)
        B.box(mb, (0, (i + .5) * tread, step_h / 2),
              (width, tread, step_h))
    B.box(mb, (0, n * tread + top_landing / 2, rise_total - .11),
          (width, top_landing, .22))
    _track("staircase")
    return _emit(mb, name, surface, location=tuple(location), yaw_deg=yaw_deg)


def gable_roof(name, rect, eaves_z, pitch_deg=30, thickness=.18,
               overhang=.25, surface="roof_terracotta"):
    """Two CLOSED pitched roof slabs, ridge parallel to Y (front/back).

    This is roof decking/cover profile only: generate any required gable
    infill/end walls, rafters, ridge caps and discrete tiles separately.
    """
    x0, x1, y0, y1 = map(float, rect)
    _positive(x1 - x0, y1 - y0, thickness)
    if not 3 < pitch_deg < 70 or overhang < 0:
        raise ValueError("Dachneigung 3..70 Grad, Überstand >= 0")
    run = (x1 - x0) / 2 + overhang
    pitch = math.radians(pitch_deg)
    length = run / math.cos(pitch)
    mid_x = (x0 + x1) / 2
    y_c = (y0 + y1) / 2
    rise = run * math.tan(pitch)
    objs = []
    for suffix, sign in (("Left", -1), ("Right", 1)):
        mb = B.MB()
        # local X runs from eave to ridge, with pitch applied around Y.
        a = sign * pitch
        rot = np.asarray(((math.cos(a), 0, math.sin(a)),
                          (0, 1, 0),
                          (-math.sin(a), 0, math.cos(a))), dtype=float)
        B.box(mb, (0, 0, 0), (length, (y1 - y0) + 2 * overhang,
                                 thickness), rot=rot)
        cx = mid_x + sign * run / 2
        cz = eaves_z + rise / 2
        objs.append(_emit(mb, name + "_" + suffix, surface,
                          location=(cx, y_c, cz)))
    _track("gable_roof")
    return objs


def metre_uv_present(obj):
    """Return whether the object has the metre-oriented UV0 channel."""
    return bool(obj.type == "MESH" and obj.data.uv_layers
                and obj.data.uv_layers.active.name == "UVMap")
