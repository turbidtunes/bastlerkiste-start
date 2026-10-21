"""Trusted Blender 4.x stage runner. The generated code gets no API/GitHub secrets.

Modes: stage (execute one incremental script, save blend, render 4 views),
       export (validate, export GLB, re-import check). Diagnostic files stay in work/.
"""
from __future__ import annotations

import json
import math
import os
import re
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

MODE = os.environ.get("WORKER_MODE", "stage")
WORK = Path(os.environ["ASSET_WORK"]).resolve()
WORK.mkdir(parents=True, exist_ok=True)

ALLOWED = set('''plaster_white plaster_cream_warm render_spalled_old limewash blockwork_raw concrete_cast
basalt_masonry basalt_dressed sandstone_ashlar brick_old rubble_pointing mixed_fieldstone pebble_mosaic
weatherboard_cream white_peeling_timber painted_timber_warmgrey wood_weathered wood_mahogany_varnished
oak_honey shutter_paint paint_clean roof_terracotta terracotta roof_slate_grey roof_steel_bluegrey
corrugated_rust galvanized_steel thatch_palm steel_painted_worn steel_bare_rusty aluminium_weathered
stainless_brushed copper_patina brass_tarnished floor_tiles ceramic_glazed_white pavers_concrete
flagstone limestone_flag ceramic_glazed mirror_silver stone_counter_light canvas_fabric textile_cotton
rubber_black plastic_weathered glass lamp_glass placeholder'''.split())


def scene_meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_get()]


def meshes_bounds(meshes):
    if not meshes:
        raise RuntimeError("Kein Mesh vorhanden")
    corners = [obj.matrix_world @ Vector(c) for obj in meshes for c in obj.bound_box]
    a = Vector([min(v[i] for v in corners) for i in range(3)])
    b = Vector([max(v[i] for v in corners) for i in range(3)])
    return a, b


def stats(strict=False):
    meshes = scene_meshes()
    minimum, maximum = meshes_bounds(meshes)
    dim = maximum - minimum
    tris = sum(sum(max(0, len(f.vertices) - 2) for f in obj.data.polygons) for obj in meshes)
    if tris < 12 or max(dim) < .5 or max(dim) > 250:
        raise RuntimeError(f"Unplausible Maße/Dreiecke: {list(dim)} / {tris}")
    used = sorted({mat.name for o in meshes for mat in o.data.materials if mat})
    unknown = [name for name in used if name not in ALLOWED and not re.fullmatch(r"(?:new|sign|poster)_[a-z0-9_]+", name)]
    missing_slots = []
    uv_missing = []
    for ob in meshes:
        if not ob.data.polygons:
            continue
        if not ob.data.materials or any(slot.material is None for slot in ob.material_slots):
            missing_slots.append(ob.name)
        elif any(f.material_index >= len(ob.data.materials) for f in ob.data.polygons):
            missing_slots.append(ob.name)
        if not ob.data.uv_layers:
            uv_missing.append(ob.name)
    names = sorted(o.name for o in meshes)
    doors = [n for n in names if n.startswith(("DoorLeaf_", "DoorSlide_", "DoorRoll_"))]
    placeholders = [n for n in names if n.startswith("Ph_")]
    violations = []
    if unknown: violations.append(f"Unbekannte Materialien: {unknown[:20]}")
    if missing_slots: violations.append(f"Meshes ohne Material: {missing_slots[:20]}")
    if uv_missing: violations.append(f"Meshes ohne UV0: {uv_missing[:20]}")
    if not doors: violations.append("Keine getrennten DoorLeaf_/DoorSlide_/DoorRoll_-Nodes")
    if not placeholders: violations.append("Keine Furniture-Placeholder Ph_*")
    if strict and violations:
        raise RuntimeError("Qualitaetspruefung fehlgeschlagen: " + "; ".join(violations))
    return {
        "meshes": len(meshes), "triangles": tris,
        "bounds_min_m": [round(float(v), 3) for v in minimum],
        "bounds_max_m": [round(float(v), 3) for v in maximum],
        "dimensions_m": [round(float(v), 3) for v in dim],
        "materials": used, "doors": doors, "placeholders": placeholders,
        "violations": violations,
    }


def render_views(stage: str):
    meshes = scene_meshes()
    minimum, maximum = meshes_bounds(meshes)
    center = (minimum + maximum) / 2
    size = max(maximum[i] - minimum[i] for i in range(3))
    if size <= 0:
        raise RuntimeError("Leere Szene")
    distances = {
        "front": Vector((0, -1, .13)),
        "side": Vector((1, 0, .13)),
        "top": Vector((0, 0, 1)),
        "threequarter": Vector((1.35, -1.5, .95)),
    }
    camera_data = bpy.data.cameras.new("_QA_CAMERA")
    camera = bpy.data.objects.new("_QA_CAMERA", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = size * 1.95
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 704
    scene.render.resolution_y = 704
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.render.filepath = str(WORK / "views" / "placeholder.png")
    (WORK / "views").mkdir(exist_ok=True)
    produced = {}
    for name, direction in distances.items():
        camera.location = center + direction.normalized() * size * 3.3
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
        path = WORK / "views" / f"{stage}_{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        if not path.is_file() or path.stat().st_size < 500:
            raise RuntimeError(f"Ansicht nicht gerendert: {name}")
        produced[name] = str(path)
    bpy.data.objects.remove(camera, do_unlink=True)
    return produced


def stage():
    name = os.environ["STAGE_NAME"]
    code = Path(os.environ["STAGE_CODE"])
    # SHELL starts from a blank scene; all others load the prior saved .blend via Blender CLI.
    if name == "shell":
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    data = code.read_text(encoding="utf-8")
    # Run Claude code with a script path, not in the controlling Python's namespace.
    exec(compile(data, str(code), "exec"), {"__name__": "__main__", "__file__": str(code)})
    all_meshes = scene_meshes()
    if not all_meshes:
        raise RuntimeError("Skript hat kein Mesh erzeugt")
    output_blend = Path(os.environ["STAGE_OUT_BLEND"])
    output_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))
    views = render_views(name)
    report = stats(strict=False)
    report["stage"] = name
    report["views"] = views
    Path(os.environ["STAGE_REPORT"]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("STAGE_OK", name, report["meshes"], report["triangles"])


def export():
    report = stats(strict=True)
    max_tris = int(os.environ.get("MAX_TRIS", "150000"))
    if report["triangles"] > max_tris:
        raise RuntimeError(f"Triangle-Budget ueberschritten: {report['triangles']} > {max_tris}")
    output = Path(os.environ["GLB_PATH"])
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(output), export_format="GLB", export_apply=True,
        export_yup=True, export_cameras=False, export_lights=False,
        use_visible=True,
    )
    if not output.exists() or output.stat().st_size < 1024:
        raise RuntimeError("GLB nicht geschrieben oder zu klein")
    if output.stat().st_size >= 100_000_000:
        raise RuntimeError("GLB ist >= 100 MB; GitHub kann die Datei nicht direkt speichern")
    # Inspect embedded glTF JSON. User-provided photos for standard/new_* material
    # slots must NOT be silently baked into the GLB. Only unique sign/poster images
    # are allowed in this pipeline (when corresponding material exists).
    with output.open("rb") as f:
        head = f.read(20)
        if len(head) < 20 or head[:4] != b"glTF":
            raise RuntimeError("GLB-Header ungueltig")
        json_len, json_chunk_type = struct.unpack_from("<II", head, 12)
        if json_chunk_type != 0x4E4F534A:
            raise RuntimeError("GLB enthält keinen JSON-Chunk")
        gltf = json.loads(f.read(json_len))
    images = gltf.get("images", [])
    if images and not any(n.startswith(("sign_", "poster_")) for n in report["materials"]):
        raise RuntimeError("Verbotene eingebettete Foto-/Bildtexturen im GLB")
    expected = report["meshes"]
    expected_nodes = report["doors"] + report["placeholders"]
    # Confirm glTF is actually readable, with selected key nodes present.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(output))
    imported = [ob for ob in bpy.context.scene.objects if ob.type == "MESH"]
    imported_names = {ob.name for ob in bpy.context.scene.objects}
    missing = [n for n in expected_nodes if n not in imported_names]
    if not imported or len(imported) < max(1, expected // 4) or missing:
        raise RuntimeError(f"GLB-Reimport fehlgeschlagen: mesh={len(imported)}, missing={missing[:15]}")
    a, b = meshes_bounds(imported)
    reimport_dims = [float(b[i] - a[i]) for i in range(3)]
    if any(abs(reimport_dims[i] - report["dimensions_m"][i]) > max(.15, .03 * report["dimensions_m"][i]) for i in range(3)):
        raise RuntimeError(f"GLB-Reimport Abmessungen abweichend: {reimport_dims}, davor {report['dimensions_m']}")
    report["reimport_meshes"] = len(imported)
    report["glb_bytes"] = output.stat().st_size
    report["blender_version"] = bpy.app.version_string
    Path(os.environ["STAGE_REPORT"]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("EXPORT_REIMPORT_OK", report["triangles"], report["glb_bytes"])


if __name__ == "__main__":
    if MODE == "stage": stage()
    elif MODE == "export": export()
    else: raise ValueError("Ungültiger WORKER_MODE")
