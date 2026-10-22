"""Best-effort H04 church delivery: never mislabel an unverified GLB as finished.

First run the complete strict original pipeline. If it fails, publish a
loadable, independently-named PREVIEW GLB together with exact failure notes.
No Claude or Blender installation. Works on Python/Manifold GitHub Actions.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from pygltflib import GLTF2

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
WORK=Path("/workspace/church_work")
OUT=REPO/"inbox/grand_fond_parish_church_codex"
LOGS=HERE/"finish_logs"
OUT.mkdir(parents=True,exist_ok=True)
LOGS.mkdir(parents=True,exist_ok=True)
target=OUT/"grand_fond_parish_church_codex.glb"
pipeline=HERE/"finish_pipeline.py"
logfile=LOGS/"best_effort_pipeline.log"

print("H04 BEST-EFFORT: attempt strict complete build and quality checks",flush=True)
start=time.monotonic()
timed_out=False
exit_code=-1
with logfile.open("w",encoding="utf-8") as f:
    try:
        # Stream complete original diagnostic output into both job and artifact.
        proc=subprocess.Popen(
            [sys.executable,"-u",str(pipeline)],
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
            text=True,bufsize=1
        )
        deadline=time.monotonic()+650
        while True:
            if proc.poll() is not None:
                remainder=proc.stdout.read()
                if remainder:
                    f.write(remainder);f.flush();print(remainder,end="",flush=True)
                break
            # Popen output can be large; force finite execution with "timeout".
            # The pipe reads lines as the generator prints stage status.
            if time.monotonic()>deadline:
                timed_out=True;proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
                break
            # Standard Python readline can block between output lines, but each
            # subprocess stage has an independent timeout in finish_pipeline.py.
            line=proc.stdout.readline()
            if line:
                f.write(line);f.flush();print(line,end="",flush=True)
        exit_code=proc.returncode
    except Exception as exc:
        f.write("\nCONTROLLER ERROR "+repr(exc)+"\n")
        print("CONTROLLER ERROR",repr(exc),flush=True)
print("STRICT RESULT",exit_code,"elapsed",round(time.monotonic()-start,2),flush=True)

if exit_code==0 and target.is_file() and target.stat().st_size>100000:
    # Original pipeline passed strict QA. Keep exactly that file.
    qa=LOGS/"qa_status.json"
    if qa.is_file():
        shutil.copy2(qa,OUT/"qa_status.json")
    print("H04_COMPLETE_VALIDATED",target,flush=True)
    raise SystemExit(0)

# STRICT pipeline did not finish. Select actual loadable GLB, preferring the
# newest original generator output over older restored binaries.
candidates=[
    ("latest_repaired",WORK/"clean.glb"),
    ("latest_generated_raw",WORK/"fresh_raw.glb"),
    ("latest_generated_raw_path",Path("/workspace/inbox/grand_fond_parish_church/grand_fond_parish_church.glb")),
    ("archived_repaired_older",HERE/"church_work/clean.glb"),
    ("archived_raw_older",HERE/"inbox/grand_fond_parish_church/grand_fond_parish_church.glb"),
]
picked=None
inspection=None
for label,p in candidates:
    if not p.is_file() or p.stat().st_size<100000:
        continue
    try:
        g=GLTF2().load(str(p))
        nodes=[n for n in g.nodes if n.mesh is not None]
        names=[n.name or "" for n in nodes]
        architecture=len([n for n in names if not n.startswith(("Ph_","Door"))])
        doors=len([n for n in names if n.startswith("Door")])
        ph=len([n for n in names if n.startswith("Ph_")])
        tri=0
        for mesh in g.meshes:
            for prim in mesh.primitives:
                if prim.indices is None or prim.indices>=len(g.accessors):
                    raise ValueError("Missing GLB triangle index accessor")
                a=g.accessors[prim.indices]
                if a.count%3:
                    raise ValueError("Non-triangle index count")
                tri+=a.count//3
        if architecture<12 or doors<10 or ph<60 or not 10000<tri<300000:
            raise ValueError(f"GLB incomplete: architecture={architecture}, doors={doors}, ph={ph}, tris={tri}")
        inspection={
            "nodes":len(nodes),"architecture_nodes":architecture,
            "door_nodes":doors,"placeholder_nodes":ph,
            "triangles":tri,"materials":len(g.materials),
            "embedded_images":len(g.images),
            "source_bytes":p.stat().st_size
        }
        picked=(label,p)
        print("PREVIEW_CANDIDATE_ACCEPTED",label,json.dumps(inspection),flush=True)
        break
    except Exception as e:
        print("PREVIEW_CANDIDATE_REJECTED",label,str(e),flush=True)

if picked is None:
    raise SystemExit("No parseable complete-enough GLB present for best-effort delivery")

label,chosen=picked
shutil.copy2(chosen,target)
reopen=GLTF2().load(str(target))
if len(reopen.meshes)<15:
    raise SystemExit("Export failed post-copy GLB integrity check")
issues=[]
qa_file=LOGS/"qa_status.json"
if qa_file.is_file():
    try:
        qa=json.loads(qa_file.read_text(encoding="utf-8"))
        issues=list(qa.get("issues",[]))
    except Exception as e:
        issues.append("Could not read QA report: "+str(e))
for f in ("validation.json","collisions.json","swing.json","repair_python_stats.json"):
    p=WORK/f
    if p.is_file():
        shutil.copy2(p,OUT/f)
        if p.suffix==".json" and f=="validation.json":
            try:
                v=json.loads(p.read_text(encoding="utf-8"))
                if not v.get("shell_watertight"):
                    issues.append("Final architecture watertightness not proven / failed")
                if v.get("issues"):
                    issues.append("Geometry validation issues: "+str(v["issues"][:15]))
            except Exception as e:
                issues.append("Could not parse validation: "+str(e))
if not issues:
    issues.append("Strict full QA interrupted or not completed; refer to diagnostic logs")
reason="".join(logfile.read_text(encoding="utf-8",errors="replace").splitlines(keepends=True)[-35:])
status={
    "status":"PREVIEW_NOT_APPROVED",
    "ready_for_visual_inspection":True,
    "strict_pipeline_exit_code":exit_code,
    "strict_pipeline_timed_out":timed_out,
    "chosen_version":label,
    "latest_source_included":label.startswith("latest_"),
    "file":str(target.relative_to(REPO)),
    "inspection":inspection,
    "known_or_unresolved_issues":issues,
    "important":"A parseable glTF is NOT evidence of correct walls, collision-free doors or a fully navigable tower",
    "pipeline_log_tail":reason[-4000:],
}
(OUT/"qa_status.json").write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
lines=[
    "GRAND-FOND H04 / CODEX ALTERNATIVE – VORABVERSION, NICHT ENDABGENOMMEN",
    "",
    "Datei: grand_fond_parish_church_codex.glb",
    f"Quelle: {label}",
    f"Dreiecke: {inspection['triangles']}; Architektur-Meshes: {inspection['architecture_nodes']}",
    f"Tueren: {inspection['door_nodes']}; Moebel-Platzhalter: {inspection['placeholder_nodes']}",
    "Fuer Unreal Engine 5 / glTF. Keine Texturen eingebettet.",
    "",
    "WICHTIG: Der strenge Fertigstellungsprozess wurde nicht erfolgreich abgeschlossen.",
    "Die GLB konnte numerisch als glTF geladen werden, aber dies ist KEINE",
    "Zusicherung ueber wasserdichte Architektur, Kollisionen, begehbaren Turm,",
    "Tuerschwenks, UV-Qualitaet, Triangulation oder UE5 Import.",
    "Es wird keine vollstaendige Qualitaetspruefung behauptet.",
    "",
    "Gefundene bzw. ungepruefte Probleme:",
    *[" - "+str(s) for s in issues],
    "",
    "Vollstaendige Fehlerdetails: qa_status.json und Action-Artefakt finish_logs/.",
    "Historische Originaldateien unveraendert in rescue/grand_fond_H04/.",
    "Fototexturen weiterhin separat im Rettungsordner; keine neuen erzeugt.",
]
(OUT/"note.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("H04_PREVIEW_DELIVERED",target,target.stat().st_size,
      "source",label,"strict_qc","NOT_PASSED",flush=True)
