"""Finish the Codex H04 church from its actual source, without Claude API.

Run on GitHub Actions runner. Historical input in rescue/grand_fond_H04/
is never modified. Final alternate asset is inbox/grand_fond_parish_church_codex/.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

REPO=Path(__file__).resolve().parents[2]
SRC=REPO/"rescue/grand_fond_H04"
WORK=Path("/workspace/church_work")
ORIG_OUT=Path("/workspace/inbox/grand_fond_parish_church")
ALTERNATE=REPO/"inbox/grand_fond_parish_church_codex"
# Blender installation deliberately omitted; geometry is rebuilt by manifold3d.
LOGS=SRC/"finish_logs" # only local working tree; archived regardless of result
LOGS.mkdir(parents=True,exist_ok=True)
EXPECTED=["build.py","repair.py","validate.py","swing_check.py"]
for name in EXPECTED:
    if not (SRC/"church_work"/name).is_file():
        raise SystemExit(f"Missing Codex source: {name}")
WORK.mkdir(parents=True,exist_ok=True)
ORIG_OUT.mkdir(parents=True,exist_ok=True)
for name in EXPECTED:
    shutil.copy2(SRC/"church_work"/name, WORK/name)

# Python/Manifold repair needs no Blender or Ubuntu system downloads.
shutil.copy2(SRC/"repair_gltf_python.py",WORK/"repair_gltf_python.py")
print("Source SHA256",hashlib.sha256((WORK/"build.py").read_bytes()).hexdigest(),flush=True)

def run(label,cmd,timeout=900,env=None):
    print("BEGIN",label," ".join(map(str,cmd)),flush=True)
    start=time.monotonic()
    try:
        with (LOGS/(label+".log")).open("w",encoding="utf-8") as f:
            proc=subprocess.run(cmd,cwd=REPO,env=env,stdout=f,stderr=subprocess.STDOUT,
                                timeout=timeout)
        text=(LOGS/(label+".log")).read_text(encoding="utf-8",errors="replace")
        print("DONE",label,"rc",proc.returncode,"duration",round(time.monotonic()-start,1),flush=True)
        print(text[-2800:],flush=True)
        if proc.returncode:
            raise RuntimeError(f"{label}: return code {proc.returncode}: {text[-3000:]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{label}: timeout {timeout}s; log {LOGS/(label+'.log')}")
    return text

# Run the latest saved generator *not* the older 8MB raw GLB.
# This includes the author's final under-stair slab depth adjustment.
run("01_rebuild", [sys.executable,"-u",str(WORK/"build.py")],timeout=1050)
raw=ORIG_OUT/"grand_fond_parish_church.glb"
if not raw.is_file() or raw.stat().st_size<100000:
    raise RuntimeError("Fresh raw GLB missing")
shutil.copy2(raw, WORK/"fresh_raw.glb")

# Python-only architecture stitching, normal reconstruction and GLB export.
run("02_repair_python", [sys.executable,"-u",str(WORK/"repair_gltf_python.py")],timeout=650)
clean=WORK/"clean.glb"
if not clean.is_file() or clean.stat().st_size<100000:
    raise RuntimeError("Repaired GLB missing")

# External independent numerical QA on the *repaired* export.
# validate.py uses the old raw GLB path by default, so patch the local
# temporary copy only. Do not change the Codex original in Git.
source=(WORK/"validate.py").read_text(encoding="utf-8")
needle="p='/workspace/inbox/grand_fond_parish_church/grand_fond_parish_church.glb'"
if needle not in source:
    raise RuntimeError("Unexpected original validation path; refuse silent wrong-file validation")
(WORK/"validate_clean.py").write_text(
    source.replace(needle,"p='/workspace/church_work/clean.glb'"),
    encoding="utf-8")
run("03_validate_clean", [sys.executable,"-u",str(WORK/"validate_clean.py")],timeout=500)
validation=json.loads((WORK/"validation.json").read_text(encoding="utf-8"))
print("VALIDATION",json.dumps({k:v for k,v in validation.items()
                               if k not in ("issues","bounds_gltf")},ensure_ascii=False),flush=True)
shutil.copy2(WORK/"validation.json",LOGS/"validation.json")
shutil.copy2(WORK/"collisions.json",LOGS/"collisions.json")

# Swing verification can be computationally expensive, but needs to occur
# on *latest* geometry (not the historical intermediate).
run("04_swing", [sys.executable,"-u",str(WORK/"swing_check.py")],timeout=1050)
if not (WORK/"swing.json").is_file():
    raise RuntimeError("Door-swing report missing")
swing=json.loads((WORK/"swing.json").read_text(encoding="utf-8"))
shutil.copy2(WORK/"swing.json",LOGS/"swing.json")
print("Door-swing intersections",len(swing),flush=True)

stats=json.loads((WORK/"stats.json").read_text(encoding="utf-8"))
tri=validation["triangles"]
doors=validation["door_leaves"]
ph=validation["placeholders"]
bounds=validation.get("bounds_gltf")
errors=[]
if not 10000<tri<=150000: errors.append(f"Triangle count invalid {tri}")
if doors!=12: errors.append(f"Expected 12 separate door leaves: {doors}")
if ph<70: errors.append(f"Furniture nodes missing: {ph}")
if validation.get("embedded_images")!=0: errors.append("Embedded images in GLB")
if not validation.get("shell_watertight",False): errors.append("Architecture non-watertight")
if validation.get("boundary_edges",1)!=0: errors.append("Open architecture edges")
if validation.get("nonmanifold_edges",1)!=0: errors.append("Nonmanifold architecture edges")
if validation.get("issues"): errors.append(f"Geometry/normal issues: {validation['issues'][:15]}")
if json.loads((WORK/"collisions.json").read_text(encoding="utf-8")):
    errors.append("Door/furniture collisions with architecture")
if swing:
    errors.append(f"Door swing intersections: {swing[:16]}")
if bounds:
    dims=[bounds[1][i]-bounds[0][i] for i in range(3)]
    # glTF Y-up: X width, Y height, Z depth
    if dims[0]>27.1 or dims[2]>36.1 or dims[1]>26:
        errors.append(f"Footprint or height outside plot: {dims}")
(LOGS/"qa_status.json").write_text(json.dumps({
    "source":str(SRC),"triangles":tri,"doors":doors,"placeholders":ph,
    "bounds_gltf":bounds,"issues":errors,"validation":validation,
    "collisions":json.loads((WORK/"collisions.json").read_text()),"swing":swing
},ensure_ascii=False,indent=2),encoding="utf-8")
if errors:
    print("QA FAILURE",json.dumps(errors,ensure_ascii=False,indent=2),flush=True)
    # Prevent a faulty alternative from being called finished.
    raise RuntimeError("Final QA gate failed: "+ "; ".join(errors[:6]))

# Preserve one architectural node per material and each independent door,
# placeholder and extras. Only rename the glTF *meshes* to their node names.
from pygltflib import GLTF2
g=GLTF2().load(str(clean))
for n in g.nodes:
    if n.mesh is not None:
        g.meshes[n.mesh].name=n.name
g.asset.generator="Codex H04 alternate – rebuilt and QA-tested"
ALTERNATE.mkdir(parents=True,exist_ok=True)
glb=ALTERNATE/"grand_fond_parish_church_codex.glb"
g.save_binary(str(glb))
# verify the file saved and is byte-readable
again=GLTF2().load(str(glb))
if len(again.nodes)!=len(g.nodes) or len(again.meshes)!=len(g.meshes):
    raise RuntimeError("Final GLB round-trip changed node/mesh counts")
shutil.copy2(WORK/"validation.json", ALTERNATE/"validation.json")
shutil.copy2(WORK/"swing.json", ALTERNATE/"swing.json")
new_mats=[m for m in stats["materials"] if m.startswith("new_")]
lines=[
    "Grand-Fond H04 / Codex-Alternative – eigenstaendiger Produktionsstand",
    "Quelle: rescue/fond_h04 / rescue/grand_fond_H04/church_work/build.py",
    "vollstaendig NEU aus der letzten Quellfassung gebaut, nicht aus altem GLB kopiert.",
    "Fuer Unreal Engine 5: LOD0, Meter, glTF Y-up.",
    f"Dreiecke: {tri}; Tuernodes: {doors}; Moebelplatzhalter: {ph}",
    f"gltf bounding box: {bounds}",
    "PASS: Wasserfeste Architektur, keine degenerierten Dreiecke, keine Restkollisionen,",
    "alle Tuer-Schwenkwinkel 15/30/45/60/75/90 Grad getestet.",
    "Foto-Materialien fehlen im GLB absichtlich; vorhandene Texturkacheln aus dem",
    "Codex-Rettungsordner sind separate, unveraenderte 1254-Pixel-Bilder.",
    "Keine neuen oder prozeduralen Texturen wurden erzeugt.",
    "Materialien: "+", ".join(stats["materials"]),
    "Anschlussfotos (bestehende, unveraenderte Dateinamen):"
]
for m in new_mats:lines.append(" - "+m+".png (separat aus rescue/grand_fond_H04/inbox/)")
lines+=["","Tuerrollen (aus dem aktuellen neu gebauten Modell):"]
lines += [f" - {d['name']}: {d['from_to']}; Oeffnung {d['opening_width_m']:.2f}m"
          for d in stats["doors"]]
lines += ["", "Moebelrollen nach Raum:"]
for room,items in stats["rooms"].items():
    from collections import Counter
    counts=Counter(item["role"] for item in items)
    lines.append(" - "+room+": "+", ".join(f"{name} x{n}" for name,n in counts.items()))
lines += ["", "Unvermeidbare Referenzabweichungen und vollstaendiger Architekturplan:",
          "siehe rescue/grand_fond_H04/original_plan.md und modelling_decisions.md.",
          "GLB-Unreal-Import und Material-Binding bleiben in UE5 zu testen; es wurden",
          "keine UE5-Spezifischen Interaktionen im Game-Editor ausgefuehrt."]
(ALTERNATE/"note.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("CODEX_ALTERNATE_COMPLETE",glb,glb.stat().st_size,flush=True)
