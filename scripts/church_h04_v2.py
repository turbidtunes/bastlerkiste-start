"""Fresh, resumable Grand-Fond H04 Blender build. Never generates textures."""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from anthropic import Anthropic

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "_asset_work/fond_h04"
STAGES = WORK / "stages"
OUT = ROOT / "inbox/fond_h04"
PROMPT = ROOT / "prompts/fond_h04.md"
REF = ROOT / "referenzbilder/ref_grand_fond_H04_g_church_creole.png"
WORKER = ROOT / "scripts/blender_worker.py"
API = (ROOT / "scripts/blender_lib/API.md").read_text(encoding="utf-8")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
RESUME = os.environ.get("RESUME_RUN_ID", "").strip()
LIMIT = float(os.environ.get("MAX_ESTIMATED_USD", "50"))
VISUAL = os.environ.get("VISUAL_REVIEW", "true").lower() == "true"
RATES = {"claude-sonnet-5-5": (2.0, 10.0), "claude-opus-5-5": (4.0, 20.0)}
PHASES = [
    ("shell", "Grounded foundations, floors and actual thick walls with genuine door/window openings. Create the exact nave, side aisles, choir, sacristy, tower core and ancillary rooms. No roof, stairs, doors or furniture."),
    ("nave_roofs", "Build solid main nave, lower side-aisle, choir and sacristy roof slabs and their true intersections, sealed gable ends and soffits. Do not add tile rows yet."),
    ("tower", "Construct tower shaft, bell chamber, real upper floors, lookout platform, continuous parapets and closed roof/cap. Tower must permit later real stairs."),
    ("tower_stairs", "Build real walkable tower stairs with calculated risers<=0.18m, treads>=0.28m, width>=1.2m, landings and rails, continuous route up to belfry and lookout. Add church entry/parvis steps."),
    ("windows", "Create church-specific window frames, glass, sills, lintels and bars placed within existing actual wall openings, including arches if dictated by reference."),
    ("doors", "Create all planned closed door leaves as independent correctly named nodes with correct hinge pivots and 5-10mm play, full thickness and frames; suitable outward opening main exits when explicitly planned."),
    ("roof_details", "Create real roof tile courses, ridge and hip pieces, gutters connected to wall-clipped downpipes, rafters, eaves. Stay within plot and triangle budget."),
    ("facade_details", "Model columns, capitals, plinth, cornices, facade ornaments, tower louvers, cross and exterior lamps as real geometry, only building-attached elements."),
    ("furniture_uv", "Add complete Ph_* room furniture boxes (pews, altar, lectern, sacristy and other rooms); finalize exact named PBR material slots, metric UV0 on ALL meshes and modest bevels. No bitmap textures."),
]
REVIEWS = {"tower_stairs", "doors", "furniture_uv"}
if MODEL not in RATES or not 1 <= LIMIT <= 500:
    raise SystemExit("Unzulässiges Modell oder MAX_ESTIMATED_USD")
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("ANTHROPIC_API_KEY fehlt")
if not PROMPT.is_file() or not REF.is_file():
    raise SystemExit("Originalprompt oder Referenzbild fehlt")
brief = PROMPT.read_text(encoding="utf-8-sig")
fingerprint = hashlib.sha256(brief.encode() + REF.read_bytes()).hexdigest()
if WORK.exists() and not RESUME and any(WORK.iterdir()):
    raise SystemExit("Frischer Build darf vorhandenes Work-Verzeichnis nicht überschreiben")
STAGES.mkdir(parents=True, exist_ok=True)
(WORK / "views").mkdir(exist_ok=True)
hash_file = WORK / "source_sha256.txt"
plan_file = WORK / "plan.md"
cp_file = WORK / "stage_checkpoints.json"
usage_file = WORK / "usage.json"
if RESUME:
    if not hash_file.is_file() or hash_file.read_text().strip() != fingerprint:
        raise SystemExit("Resume blockiert: ursprünglicher Prompt/Referenz nicht identisch")
    if not plan_file.is_file() or not cp_file.is_file():
        raise SystemExit("Resume blockiert: Plan oder Checkpoints fehlen")
    checkpoints = json.loads(cp_file.read_text(encoding="utf-8"))
else:
    hash_file.write_text(fingerprint + "\n", encoding="utf-8")
    checkpoints = {}
usage = json.loads(usage_file.read_text(encoding="utf-8")) if RESUME and usage_file.exists() else []
client = Anthropic(timeout=900, max_retries=2)

def spent():
    i, o = RATES[MODEL]
    return sum((x["input_tokens"] * i + x["output_tokens"] * o)/1000000 for x in usage)

def img(path):
    return {"type": "image", "source": {"type": "base64", "media_type": "image/png",
            "data": base64.b64encode(Path(path).read_bytes()).decode("ascii")}}

def ask(label, prompt, max_tokens, pictures=()):
    if spent() >= LIMIT:
        raise RuntimeError(f"Kostenschutz erreicht: USD {spent():.2f} / {LIMIT:.2f}")
    print(f"CLAUDE {label} bisher USD {spent():.2f}", flush=True)
    with client.messages.stream(
        model=MODEL, max_tokens=max_tokens,
        system=("Du bist ein Blender 4.x bpy Programmierer fuer eine begehbare"
                " UE5 LOD0 Kirche. Halte den numerischen Plan und Referenzentwurf"
                " exakt ein. Keine prozeduralen oder generierten Bildtexturen."
                " Liefere nur das verlangte Ausgabeformat."),
        messages=[{"role":"user", "content":[{"type":"text", "text":prompt}, *pictures]}],
    ) as stream:
        response = stream.get_final_message()
    usage.append({"label":label, "input_tokens":response.usage.input_tokens,
                  "output_tokens":response.usage.output_tokens,
                  "stop_reason":response.stop_reason})
    usage_file.write_text(json.dumps(usage, indent=2), encoding="utf-8")
    print(f"CLAUDE {label}: {response.stop_reason}; Gesamtschaetzung USD {spent():.2f}", flush=True)
    if response.stop_reason != "end_turn":
        raise RuntimeError("Antwort abgeschnitten; Codefragmente werden NICHT verkettet")
    value = "".join(b.text for b in response.content if b.type == "text").strip()
    if not value:
        raise RuntimeError("Leere Claude-Antwort")
    return value

if RESUME:
    plan = plan_file.read_text(encoding="utf-8")
else:
    plan_request = (
        "Plane dieses Gebaeude zur NEUGENERIERUNG, kein alter Resume-Build."
        " Nutze das beigefuegte Referenzbild. Ausgabe: EINE einzige numerische"
        " Bauspezifikation mit absoluten X/Y/Z-Massen, exakten Raeumen, tragenden"
        " Teilen, Fenstern, ECHTEN Tueroeffnungen, Tuerliste, Kirchturm mit"
        " durchgaengiger begehbarer Treppe samt rechnerischen Podest-/Stufenmassen,"
        " Glockenraum, Aussicht, Dachschnitten, Materialnamen, new_* Beschreibung"
        " und Kachelgroesse in Metern, Placeholder pro Raum, Abweichungen und"
        " MAX_TRIS<=150000. Bau inklusive Stufen und Dach max. X +/-13.5 und"
        " Y +/-18 Meter (3m Strassen- und Rueckabstand, 1.5m Nachbarn)."
        " Kirchenschiff und Seitenschiffe wirklich doppelhoch, nicht in 3m"
        " Etagen zerstueckeln. Spaetere neun Bauphasen muessen konsistent sein:"
        "\n" + "\n".join(x[0] + ": " + x[1] for x in PHASES) +
        "\nMaximal 2200 Woerter, kompakte Tabellen statt Essays."
        " Abschluss als letzte Zeile PLAN_COMPLETE.\nAUFTRAG:\n" + brief
    )
    for attempt in range(2):
        try:
            plan = ask(f"plan_try{attempt+1}", plan_request +
                       ("\nANTWORT KUERZER, KEINE WIEDERHOLUNG." if attempt else ""),
                       4700, [img(REF)])
            if not plan.rstrip().endswith("PLAN_COMPLETE"):
                raise RuntimeError("PLAN_COMPLETE fehlt")
            break
        except RuntimeError:
            if attempt:
                raise
    plan_file.write_text(plan + "\n", encoding="utf-8")
    cp_file.write_text("{}\n", encoding="utf-8")
print("PLAN READY", flush=True)

def clean_code(answer):
    ticks = chr(96)*3
    code = re.sub(r"^" + ticks + r"(?:python)?\s*\n", "", answer.strip(), count=1)
    code = re.sub(r"\n" + ticks + r"\s*$", "", code, count=1)
    if ticks in code or not re.search(r"(?m)^# STAGE_DONE\s*$", code):
        raise SyntaxError("Codefences oder Abschlussmarkierung falsch")
    compile(code, "church_phase.py", "exec")
    if re.search(r"\bbpy\.ops\.wm\.open_mainfile\s*\(", code):
        raise SyntaxError("Kein Wechsel der geladenen Blender-Datei erlaubt")
    return code + "\n"

def run_blender(mode, name, previous, codefile=None):
    env = os.environ.copy()
    for k in ("ANTHROPIC_API_KEY","GH_TOKEN","GITHUB_TOKEN","ACTIONS_RUNTIME_TOKEN",
              "LD_LIBRARY_PATH","PYTHONHOME","PYTHONUSERBASE","VIRTUAL_ENV",
              "PYTHONNOUSERSITE"):
        env.pop(k, None)
    env["PYTHONPATH"] = "/usr/lib/python3/dist-packages"
    report = STAGES / f"{name}.json" if mode == "stage" else WORK / "final_validation.json"
    output = STAGES / f"{name}.blend"
    env.update({"WORKER_MODE":mode, "ASSET_WORK":str(WORK), "STAGE_NAME":name,
                "STAGE_CODE":str(codefile or ""), "STAGE_OUT_BLEND":str(output),
                "STAGE_REPORT":str(report), "MAX_TRIS":"150000",
                "GLB_PATH":str(WORK / "fond_h04.glb")})
    cmd = ["blender","--background","--factory-startup","--python-exit-code","37"]
    if previous:
        cmd.append(str(previous))
    cmd += ["--python", str(ROOT / "scripts/blender_worker.py")]
    try:
        p = subprocess.run(cmd,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,timeout=620)
        rc, log = p.returncode, p.stdout
    except subprocess.TimeoutExpired as e:
        rc, log = 124, str(e)
    (STAGES / f"{name}.log").write_text(log, encoding="utf-8")
    print(f"BLENDER {name} RC={rc}\n{log[-1500:]}", flush=True)
    if rc:
        raise RuntimeError(log[-11000:])
    if not report.is_file():
        raise RuntimeError("Erforderlicher Blender-Pruefbericht fehlt")
    return output, json.loads(report.read_text(encoding="utf-8"))

def build_phase(phase, purpose, base, before, attempts=3):
    last_error, bad_code = "", ""
    for attempt in range(1,attempts+1):
        target = f"{phase}_try{attempt}"
        ask_text = (
            "Erzeuge ausschliesslich vollstaendigen LAUFFAEHIGEN Blender-bpy-Python-Code"
            " fuer EINE kleine Phase (maximal ca. 6500 Tokens). Kein Markdown."
            " Letzte Zeile genau # STAGE_DONE. Der Controller laedt zuvor das"
            " gespeicherte .blend. Fruehere Python-Funktionen sind NICHT da,"
            " also import building_kit as kit. Nur in der Phase shell darf die"
            " Szene geleert werden. In spaeteren Phasen nie pauschal loeschen."
            " Alle Meshes als echte geschlossene koerperliche Geometrie,"
            " UV0 metrisch, erlaubte Materialnamen, keine Bildtexturen."
            " Nur das fuer die aktuelle Phase Noetige erzeugen."
            "\nPHASE: "+phase+"\nARBEIT: "+purpose+
            "\nVORHERIGER BERICHT:\n"+json.dumps(before or {},ensure_ascii=False)+
            "\nVERFUEGBARE GETESTETE API:\n"+API+
            "\nVERBINDLICHER PLAN:\n"+plan+
            "\nURSPRUENGLICHER BAUAUFTRAG:\n"+brief
        )
        if last_error:
            ask_text += ("\nREPARATUR NUR DIESER PHASE, KEINE NEUE PLANUNG!"
                         "\nFEHLER:\n"+last_error[-11000:]+
                         "\nVORHERIGER CODE:\n"+bad_code[-28000:])
        script = STAGES / f"{target}.py"
        try:
            answer=ask(target,ask_text,9000)
            script.write_text(answer+"\n", encoding="utf-8")
            bad_code=answer
            code=clean_code(answer)
            script.write_text(code, encoding="utf-8")
            blend, report=run_blender("stage","shell" if phase=="shell" else target,base,script)
            if before and report["meshes"] < before["meshes"]*0.85:
                raise RuntimeError("Bestand geloescht: zu viele Meshes verschwunden")
            if not blend.is_file():
                raise RuntimeError("BLEND-Checkpoint fehlt")
            return blend,report
        except (RuntimeError,ValueError,SyntaxError) as e:
            last_error=str(e)
            (STAGES / f"{target}.failure.txt").write_text(last_error[-14000:],encoding="utf-8")
            print(f"FEHLER {target}: {last_error[-1400:]}",flush=True)
    raise RuntimeError(f"Phase {phase} gescheitert: {last_error[-3000:]}")

def review(phase, report):
    if not VISUAL or phase not in REVIEWS:
        return []
    prompt = (
        "Vergleiche die folgenden 4 echten Blender-Ansichten mit dem"
        " Originalreferenzfoto und Plan. Beachte: spaetere Phasen sind"
        " noch NICHT gebaut. Nenne maximal 3 eindeutig sichtbare grosse"
        " und reparierbare GEOMETRIEFEHLER. Ausschliesslich JSON"
        " {\"issues\":[\"...\"]}. Keine erfundenen Maengellisten."
        "\nPHASE:"+phase+"\nPLAN:\n"+plan[:18000]+
        "\nREPORT:"+json.dumps({k:report.get(k) for k in
           ("meshes","triangles","dimensions_m","doors","placeholders")}))
    pictures=[img(REF)]+[img(report["views"][n]) for n in
                         ("front","side","top","threequarter")]
    raw=ask(phase+"_vision",prompt,1200,pictures)
    try:
        return [str(v)[:600] for v in json.loads(raw.strip().strip(chr(96)))["issues"][:3]]
    except (ValueError,TypeError,KeyError):
        (STAGES / f"{phase}_review.txt").write_text(raw,encoding="utf-8")
        print("WARNUNG: Review unparsebar",flush=True)
        return []

previous=None
last_report=None
for phase,purpose in PHASES:
    if phase in checkpoints:
        saved=checkpoints[phase]
        previous=(STAGES/saved["blend_file"]).resolve()
        if not previous.is_relative_to(STAGES.resolve()) or not previous.is_file():
            raise RuntimeError(f"Checkpoint fehlt: {phase}")
        last_report=saved["report"]
        print(f"CHECKPOINT REUSE: {phase}",flush=True)
        continue
    new_blend,new_report=build_phase(phase,purpose,previous,last_report)
    issues=review(phase,new_report)
    if issues:
        (STAGES/f"{phase}_issues.json").write_text(
            json.dumps(issues,ensure_ascii=False,indent=2),encoding="utf-8")
        try:
            new_blend,new_report=build_phase(
                phase+"_fix","Nur gezielte Korrektur der vorhandenen"
                " .blend fuer diese Probleme: "+json.dumps(issues,ensure_ascii=False),
                new_blend,new_report,attempts=2)
        except RuntimeError as e:
            print(f"WARNUNG: visuelle Nachbesserung misslungen: {e}",flush=True)
    previous,last_report=new_blend,new_report
    checkpoints[phase]={"blend_file":previous.name,"report":last_report}
    cp_file.write_text(json.dumps(checkpoints,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"GESICHERT: {phase} -> {previous.name}",flush=True)
assert previous is not None
_, final=run_blender("export","final",previous)
if not final["doors"] or not final["placeholders"] or final["triangles"]>150000:
    raise RuntimeError("Endkontrolle: Tueren/Placeholder/Tris unzureichend")
glb=WORK/"fond_h04.glb"
if not glb.is_file():
    raise RuntimeError("Fertige GLB fehlt")
OUT.mkdir(parents=True,exist_ok=True)
new_materials=[m for m in final["materials"] if m.startswith("new_")]
lines=[
    "fond_h04: katholische Pfarrkirche Grand-Fond, Mauritius",
    "Stil: authority; Quelle: prompts/fond_h04.md + echtes Referenzbild",
    f"Tris: {final['triangles']}; Meshes: {final['meshes']};"
    f" reimportierte Meshes: {final['reimport_meshes']}",
    "Tuernodes: "+", ".join(final["doors"]),
    "Materialien: "+", ".join(final["materials"]),
    "",
    "Placeholder-Nodes:", *final["placeholders"],
    "",
    "Fehlende neue Fototexturen (NUR LISTEN, keine PNG erzeugt):"
]
for m in new_materials:
    lines.append(m+".png – nicht erzeugt")
    lines.extend("  Plan: "+line.strip()[:500] for line in plan.splitlines()
                 if m in line) 
if not new_materials:
    lines.append("Keine new_*-Materialien")
lines.extend(["","Numerischer Original-Bauplan (Raeume, Tueren, Abweichungen,"
              " Materialbeschreibungen und Kachelgroessen):",plan,"",
              "Hinweis: GLB-Reimport und Namens-/Materialcheck sind kein"
              " vollstaendiger UE5-Begehbarkeitstest.",
              f"Geschaetzte Claude-API-Kosten: USD {spent():.2f}"])
(OUT/"note.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
shutil.copy2(glb, OUT/"fond_h04.glb")
print(f"FOND_H04_V2_SUCCESS {final['triangles']} tris; USD {spent():.2f}",flush=True)
