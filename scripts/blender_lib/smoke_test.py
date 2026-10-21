"""Zero-Claude-cost Blender regression test for the reusable building kit.

Runs on a headless Ubuntu GitHub runner before the paid agent executes.
This test is standalone and must not write any assets to inbox/.
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import building_kit as k  # noqa: E402

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

wall = k.wall(
    "KitTest_ExteriorWall", (0, 8, 0, 6), "front", 0, 3, .30,
    openings=[
        (2.0, 3.05, 0, 2.2, "door"),
        (4.0, 5.3, .9, 2.2, "window"),
    ],
    surface="plaster_white",
)
assert wall.type == "MESH" and len(wall.data.vertices) > 20

slab = k.slab("KitTest_Floor", (0, 8, 0, 6), -.2, .2)
partition = k.partition(
    "KitTest_Partition", (1, 1, 0), (1, 5, 0), 0, 3, .13,
    door_spans=[(1.0, 2.0)],
)
door = k.door_leaf(
    1, (2.01, 0, 0), 1.03, 2.19,
    hinge_side="L", opens="in", surface="wood_weathered",
)
assert door.name == "DoorLeaf_01_L_in"
assert abs(door.location.x - 2.01) < 0.00001
assert abs(min(v.co.x for v in door.data.vertices)) < 1e-8

window = k.window("KitTest_Window", (4.65, 0, 1.55), 1.3, 1.3)
assert len(window) == 2
stair = k.staircase(
    "KitTest_Stair", (6, 2, 0), 2.9, width=1.2,
    tread=.28, top_landing=1.4, surface="concrete_cast",
)
roofs = k.gable_roof("KitTest_Roof", (0, 8, 0, 6), 3, 30)
assert len(roofs) == 2
placeholder = k.placeholder(
    "chapel", "pew", 1, (4, 2, 0), (2.1, .55, 1.1), yaw_deg=90,
)
assert placeholder.name == "Ph_chapel_pew_01"
assert abs(min(v.co.z for v in placeholder.data.vertices)) < 1e-6
assert abs(placeholder.rotation_euler.z - math.pi / 2) < 1e-6

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
assert len(meshes) >= 10
assert all(k.metre_uv_present(o) for o in meshes)
assert all(len(o.data.materials) == 1 for o in meshes)
assert all(len(o.data.polygons) > 0 for o in meshes)
assert "new_" not in " ".join(m.name for o in meshes for m in o.data.materials)
assert k.CALLS.get("wall") == 1
assert k.CALLS.get("door_leaf") == 1
assert k.CALLS.get("gable_roof") == 1

with tempfile.TemporaryDirectory(prefix="building_kit_test_") as tmp:
    out = Path(tmp) / "smoketest.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(out), export_format="GLB",
        export_apply=True, export_yup=True,
        export_cameras=False, export_lights=False,
    )
    assert out.is_file() and out.stat().st_size > 1000
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(out))
    names = {o.name for o in bpy.context.scene.objects if o.type == "MESH"}
    assert door.name in names or "DoorLeaf_01_L_in" in names
    assert "Ph_chapel_pew_01" in names
    assert any(o.data.uv_layers for o in bpy.context.scene.objects if o.type == "MESH")

print("BUILDING_KIT_SMOKE_OK: legacy mesh + wall + door + window + roof + stair + placeholder + GLB reimport")
