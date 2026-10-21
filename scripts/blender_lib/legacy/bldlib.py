"""bldlib.py – shared helpers for the structure kits (Session G): mesh building (grids, sweeps, boxes,
superellipsoids), materials, UCX collision, export (FBX for Unreal + GLB for the catalogue), asset.json.

Conventions (map/AUFTRAG_MAP.md §1): metres, Z up, Unreal export scale 100 (FBX global scale 1.0, apply unit).
Vertex colour "Col" on structures: RGB = paint / tint colour of the part (linear), A = grime / wetness 0..1.
UV channels: "UVMap" = metres (the material scales by its texture tile size), "Paint" (painted parts only):
x = 1 on hull exteriors (gets antifouling + boot-top), y = height above the design waterline in metres.
"""
import os, json, math
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "textures", "out")


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def srgb(h):
    """'#rrggbb' -> linear RGB tuple"""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)


class MB:
    """mesh builder: verts with per-vertex uv (metres), uv2 (paint), colour (rgba)"""
    def __init__(self):
        self.V, self.UV, self.UV2, self.C, self.F = [], [], [], [], []
        self.leaves = []           # working door leaves drawn for this material: (name, MB, meta) – hlib.door_leaf

    def n(self): return len(self.V)

    def add(self, verts, faces, uv=None, col=(1, 1, 1, 0), uv2=None):
        o = len(self.V); verts = np.asarray(verts, float).reshape(-1, 3); k = len(verts)
        self.V.extend(verts.tolist())
        self.UV.extend((np.zeros((k, 2)) if uv is None else np.asarray(uv, float).reshape(-1, 2)).tolist())
        self.UV2.extend((np.zeros((k, 2)) if uv2 is None else np.asarray(uv2, float).reshape(-1, 2)).tolist())
        col = np.asarray(col, float)
        self.C.extend((np.tile(col, (k, 1)) if col.ndim == 1 else col.reshape(-1, 4)).tolist())
        self.F.extend([[i + o for i in f] for f in faces])
        return o

    def grid(self, P, uv=None, col=(1, 1, 1, 0), uv2=None, close_v=False, flip=False):
        """P (nu, nv, 3) -> quads; close_v wraps the second index"""
        P = np.asarray(P, float); nu, nv = P.shape[:2]; F = []
        mv = nv if close_v else nv - 1
        for i in range(nu - 1):
            for j in range(mv):
                a, b, c, d = i * nv + j, (i + 1) * nv + j, (i + 1) * nv + (j + 1) % nv, i * nv + (j + 1) % nv
                F.append([a, d, c, b] if flip else [a, b, c, d])
        col = np.asarray(col, float)
        if col.ndim > 1: col = col.reshape(-1, 4)
        return self.add(P.reshape(-1, 3), F, None if uv is None else np.asarray(uv).reshape(-1, 2), col,
                        None if uv2 is None else np.asarray(uv2).reshape(-1, 2))

    def cap(self, idx, flip=False):
        """fan-free cap of a closed ring (vertex indices) as one n-gon (triangulated on export)"""
        self.F.append(list(idx[::-1]) if flip else list(idx))

    def obj(self, name, mat=None, smooth_deg=35, coll=None, recalc=True, weld=None):
        """mesh object of this builder; its door leaves become own objects <leaf>_<name> (same material, custom prop
        'door' = hinge frame, export_bld.py cuts them out). An empty builder with leaves returns the first leaf."""
        lv = []
        for ln, lmb, meta in getattr(self, "leaves", []):
            if not lmb.V: continue
            lmb._noweather = True; lo = lmb.obj(f"{ln}_{name}", mat, smooth_deg, coll, recalc); lo["door"] = json.dumps(meta); lv.append(lo)
        if not self.V and lv: return lv[0]
        extra = None
        if not getattr(self, "_noweather", False):            # S38 O2: out of true, chips, spalls, splash (weather_geo.py)
            import weather_geo as WG
            extra = WG.process(self, mat.name if mat else "", name)
        if extra is not None:
            extra._noweather = True
            bm_ = bpy.data.materials.get("M_Blockwork") or tint_mat("M_Blockwork", "Blockwork", 2.0)
            extra.obj(name + "_Spall", bm_, smooth_deg, coll, recalc=False)
        me = bpy.data.meshes.new(name); me.from_pydata(self.V, [], self.F); me.validate()
        vi = np.zeros(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", vi)
        for nm, arr in (("UVMap", self.UV), ("Paint", self.UV2)):
            if nm == "Paint" and not np.any(np.asarray(arr)): continue
            uvl = me.uv_layers.new(name=nm); uvl.data.foreach_set("uv", np.asarray(arr, np.float32)[vi].ravel())
        ca = me.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT')
        ca.data.foreach_set("color", np.asarray(self.C, np.float32).ravel())
        if weld:                                         # merge coincident vertices (smooth shading across quads)
            bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=weld); bm.to_mesh(me); bm.free()
        if recalc:
            bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        me.shade_smooth()
        if smooth_deg is not None: me.set_sharp_from_angle(angle=math.radians(smooth_deg))
        if mat: me.materials.append(mat)
        o = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(o); return o


# ---------------------------------------------------------------- primitives (all add into an MB)
def frames(pts, up=(0, 0, 1)):
    """tangent / side / up frames along a polyline (up projected, falls back to parallel transport)"""
    P = np.asarray(pts, float); T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    U = np.zeros_like(P); u0 = np.asarray(up, float)
    for k in range(len(P)):
        u = u0 - T[k] * np.dot(u0, T[k])
        if np.linalg.norm(u) < 1e-4:
            u = U[k - 1] if k else np.cross(T[k], [0, 1, 0])
        U[k] = u / np.linalg.norm(u)
    S = np.cross(T, U); return T, S, U


def sweep(mb, pts, prof, col=(1, 1, 1, 0), up=(0, 0, 1), caps=True, scale=None, uv2=None, V=None):
    """sweep closed 2D profile prof [(s, u)] (s = side, u = up) along pts; scale[k] scales the profile.
    V = explicit (T, S, U) frames. UV: u = length along the path, v = profile perimeter (metres)"""
    P = np.asarray(pts, float); T, S, U = V if V is not None else frames(P, up)
    pr = np.asarray(prof, float)
    if pr.ndim == 2: pr = np.broadcast_to(pr, (len(P),) + pr.shape)
    m = pr.shape[1]
    sc = np.ones(len(P)) if scale is None else np.asarray(scale, float)
    G = P[:, None, :] + (pr[:, :, 0, None] * S[:, None, :] + pr[:, :, 1, None] * U[:, None, :]) * sc[:, None, None]
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    p0 = pr[len(P) // 2]; per = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(np.vstack([p0, p0[:1]]), axis=0), axis=1))])[:m]
    uv = np.stack(np.broadcast_arrays(L[:, None], per[None, :]), -1)
    o = mb.grid(G, uv, col, None if uv2 is None else np.broadcast_to(np.asarray(uv2, float), (len(P), m, 2)), close_v=True)
    if caps:
        mb.cap([o + j for j in range(m)], flip=False); mb.cap([o + (len(P) - 1) * m + j for j in range(m)], flip=True)
    return o


def rect(w, h, cx=0, cy=0, r=0.0, n=3):
    """rectangle profile (side w, up h), optional corner radius r with n segments per corner (CCW)"""
    if r <= 0:
        return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    out = []
    for (sx, sy, a0) in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n); out.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return out


def circle(r, n=12, cx=0, cy=0, ry=None):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + (ry or r) * math.sin(2 * math.pi * k / n)) for k in range(n)]


def box(mb, c, size, rot=None, col=(1, 1, 1, 0), uv_off=(0, 0)):
    """axis box (optionally rotated by a 3x3 matrix rot), UVs per face in metres (box projection)"""
    c = np.asarray(c, float); hs = np.asarray(size, float) / 2; R = np.eye(3) if rot is None else np.asarray(rot, float)
    faces = [((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (1, 0, 0), (0, -1, 0)), ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
             ((-1, 0, 0), (0, -1, 0), (0, 0, 1)), ((0, 1, 0), (-1, 0, 0), (0, 0, 1)), ((0, -1, 0), (1, 0, 0), (0, 0, 1))]
    for n, a, b in faces:
        n, a, b = map(np.asarray, (n, a, b)); ca = hs[np.argmax(np.abs(a))]; cb = hs[np.argmax(np.abs(b))]
        cn = hs[np.argmax(np.abs(n))]
        q = [n * cn + a * sa * ca + b * sb * cb for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        V = [c + R @ p for p in q]; uv = [(uv_off[0] + sa * ca + np.dot(c, a), uv_off[1] + sb * cb + np.dot(c, b)) for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        mb.add(V, [[0, 1, 2, 3]], uv, col)


def superellipsoid(mb, c, h, e=(0.35, 0.35), nu=24, nv=14, col=(1, 1, 1, 0), R=None, taper=None):
    """rounded box: |x/hx|^(2/e2) + ... (e small = boxy); taper(z01) -> (sx, sy) scale per height"""
    c = np.asarray(c, float); R = np.eye(3) if R is None else np.asarray(R, float)
    def sp(w, m): return np.sign(w) * np.abs(w) ** m
    vs = np.linspace(-math.pi / 2, math.pi / 2, nv); us = np.linspace(-math.pi, math.pi, nu, endpoint=False)
    P = np.zeros((nv, nu, 3)); UV = np.zeros((nv, nu, 2))
    for i, v in enumerate(vs):
        for j, u in enumerate(us):
            x = h[0] * sp(math.cos(v), e[0]) * sp(math.cos(u), e[1]); y = h[1] * sp(math.cos(v), e[0]) * sp(math.sin(u), e[1])
            z = h[2] * sp(math.sin(v), e[0])
            if taper:
                sx, sy = taper((z / h[2] + 1) / 2); x *= sx; y *= sy
            P[i, j] = c + R @ np.array([x, y, z]); UV[i, j] = (u * max(h[0], h[1]), v * h[2])
    o = mb.grid(P, UV, col, close_v=True)
    mb.cap([o + j for j in range(nu)], flip=True); mb.cap([o + (nv - 1) * nu + j for j in range(nu)])
    return o


def tube_path(mb, pts, r, n=8, col=(1, 1, 1, 0), up=(0, 0, 1), caps=True):
    return sweep(mb, pts, circle(r, n), col, up, caps)


# ---------------------------------------------------------------- materials
def _img(N_, L_, vec, name, kind, non_color=False):
    t = N_.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(TEX, f"T_{name}_{kind}.png"), check_existing=True)
    if non_color: t.image.colorspace_settings.name = "Non-Color"
    L_.new(vec, t.inputs["Vector"]); return t


def _base(name, tex, tile, rough=(0, 1)):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N_, L_ = nt.nodes, nt.links
    b = N_["Principled BSDF"]; uv = N_.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"
    mp = N_.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / tile, 1 / tile, 1)
    L_.new(uv.outputs["UV"], mp.inputs["Vector"]); v = mp.outputs["Vector"]
    col = _img(N_, L_, v, tex, "BaseColor"); rg = _img(N_, L_, v, tex, "Rough", True); nr = _img(N_, L_, v, tex, "Normal", True)
    nm = N_.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = .8
    L_.new(nr.outputs["Color"], nm.inputs["Color"]); L_.new(nm.outputs["Normal"], b.inputs["Normal"])
    rm = N_.new("ShaderNodeMapRange"); rm.inputs["To Min"].default_value, rm.inputs["To Max"].default_value = rough
    L_.new(rg.outputs["Color"], rm.inputs["Value"]); L_.new(rm.outputs["Result"], b.inputs["Roughness"])
    vc = N_.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
    return m, N_, L_, b, col, vc


def _mix(N_, L_, fac, a, b_, blend='MIX'):
    mx = N_.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = blend
    L_.new(fac, mx.inputs["Factor"]) if not isinstance(fac, float) else mx.inputs["Factor"].__setattr__("default_value", fac)
    for s, x in (("A", a), ("B", b_)):
        if isinstance(x, tuple): mx.inputs[s].default_value = (*x, 1)
        else: L_.new(x, mx.inputs[s])
    return mx.outputs["Result"]


def paint_mat(name, tex="BoatPaint", tile=1.5, antifoul=None, boot=None, boot_h=.05, algae=False):
    """painted wood: the bright paint layer of the texture is tinted by the vertex colour, the dark chips keep the
    bare wood. Hull exteriors (Paint.x = 1): antifouling below Paint.y = 0, boot-top stripe 0..boot_h.
    Unreal: same graph in M_PaintedWood (params Antifoul, BootTop, BootH, TileM)."""
    m, N_, L_, b, col, vc = _base(name, tex, tile, (.5, .85))
    tint = vc.outputs["Color"]
    if antifoul:
        uv2 = N_.new("ShaderNodeUVMap"); uv2.uv_map = "Paint"; sep = N_.new("ShaderNodeSeparateXYZ")
        L_.new(uv2.outputs["UV"], sep.inputs["Vector"])
        def cmp(op, a, val):
            n = N_.new("ShaderNodeMath"); n.operation = op; L_.new(a, n.inputs[0]); n.inputs[1].default_value = val; return n.outputs[0]
        def mul(a, b_):
            n = N_.new("ShaderNodeMath"); n.operation = 'MULTIPLY'; L_.new(a, n.inputs[0]); L_.new(b_, n.inputs[1]); return n.outputs[0]
        flag = cmp('GREATER_THAN', sep.outputs["X"], .5)
        below_boot = mul(flag, cmp('LESS_THAN', sep.outputs["Y"], boot_h if boot else 0))
        below_wl = mul(flag, cmp('LESS_THAN', sep.outputs["Y"], 0))
        if boot: tint = _mix(N_, L_, below_boot, tint, boot)
        tint = _mix(N_, L_, below_wl, tint, antifoul)
        if algae:
            band = mul(flag, cmp('LESS_THAN', sep.outputs["Y"], .02))
            tint = _mix(N_, L_, band, tint, (.10, .13, .06), 'MIX')
    bw = N_.new("ShaderNodeRGBToBW"); L_.new(col.outputs["Color"], bw.inputs["Color"])
    mr = N_.new("ShaderNodeMapRange"); L_.new(bw.outputs["Val"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = .36; mr.inputs["From Max"].default_value = .46
    painted = _mix(N_, L_, 1.0, col.outputs["Color"], tint, 'MULTIPLY')
    painted = _mix(N_, L_, 1.0, painted, (1.15, 1.15, 1.15), 'MULTIPLY')
    out = _mix(N_, L_, mr.outputs["Result"], col.outputs["Color"], painted)
    out = _mix(N_, L_, vc.outputs["Alpha"], out, (.30, .27, .20), 'MULTIPLY')
    L_.new(out, b.inputs["Base Color"]); return m


def tint_mat(name, tex, tile=1.0, metal=0.0):
    """texture x vertex colour (rope, weathered timber tinted per board); A = wet/grime darkening"""
    m, N_, L_, b, col, vc = _base(name, tex, tile)
    out = _mix(N_, L_, 1.0, col.outputs["Color"], vc.outputs["Color"], 'MULTIPLY')
    out = _mix(N_, L_, vc.outputs["Alpha"], out, (.35, .33, .28), 'MULTIPLY')
    L_.new(out, b.inputs["Base Color"]); b.inputs["Metallic"].default_value = metal; return m


def plain_mat(name, rgb, rough=.5, metal=0.0, coat=0.0):
    """untextured material (plastic, painted metal, galvanised steel) – vertex colour multiplies"""
    m = bpy.data.materials.new(name); m.use_nodes = True; N_, L_ = m.node_tree.nodes, m.node_tree.links
    b = N_["Principled BSDF"]; vc = N_.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
    out = _mix(N_, L_, 1.0, vc.outputs["Color"], rgb, 'MULTIPLY')
    L_.new(out, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal; b.inputs["Coat Weight"].default_value = coat
    return m


# ---------------------------------------------------------------- collision + export
def ucx(points, name, coll=None):
    """convex hull of points -> UCX_<name> mesh (Unreal convex collision)"""
    bm = bmesh.new()
    for p in np.asarray(points, float).reshape(-1, 3): bm.verts.new(p)
    r = bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(bm, geom=list({g for g in r["geom_interior"] + r["geom_unused"] if isinstance(g, bmesh.types.BMVert)}), context='VERTS')
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(o)
    o.display_type = 'WIRE'; o.hide_render = True; return o


def tris(objs):
    t = 0
    for o in objs:
        if o.type == 'MESH' and not o.name.startswith("UCX_"):
            t += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return t


def export(objs, mesh_name, outdir, ucx_objs=(), sockets=()):
    """join the render meshes into SM_<mesh_name> (one slot per material), rename the hulls UCX_SM_<mesh_name>_NN,
    write <outdir>/SM_<mesh_name>.fbx (+ UCX) and .glb (render meshes only). Returns tri count."""
    os.makedirs(outdir, exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    objs = [o for o in objs if o.type == 'MESH']
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); sm = bpy.context.view_layer.objects.active
    sm.name = sm.data.name = f"SM_{mesh_name}"
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for i, u in enumerate(ucx_objs):
        u.name = u.data.name = f"UCX_SM_{mesh_name}_{i:02d}"
    t = tris([sm])
    bpy.ops.object.select_all(action='DESELECT'); sm.select_set(True)
    for u in ucx_objs: u.hide_set(False); u.select_set(True)
    for s in sockets:      # SOCKET_* empties -> Unreal static-mesh sockets (children of the mesh)
        mw = s.matrix_world.copy(); s.parent = sm; s.matrix_world = mw; s.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(outdir, f"SM_{mesh_name}.fbx"), use_selection=True,
                             apply_unit_scale=True, global_scale=1.0, mesh_smooth_type='FACE', use_triangles=True,
                             add_leaf_bones=False, colors_type='LINEAR', bake_space_transform=False)
    bpy.ops.object.select_all(action='DESELECT'); sm.select_set(True)
    for im in bpy.data.images:            # catalogue GLB: 512 px previews of the textures (Unreal uses the FBX + 2K maps)
        if im.size[0] > 512: im.scale(512, 512)
    bpy.ops.export_scene.gltf(filepath=os.path.join(outdir, f"SM_{mesh_name}.glb"), use_selection=True,
                              export_format='GLB', export_vertex_color='ACTIVE', export_image_format='JPEG',
                              export_jpeg_quality=80)
    return t


def asset_json(path, **kw):
    with open(path, "w") as f: json.dump(kw, f, indent=1, ensure_ascii=False)
