"""PLAN -> Blender stages -> four-view Claude vision checks -> GLB reimport -> inbox.

Only the normal Claude Messages API is used. The generated Blender scripts are
executed as subprocesses without ANTHROPIC_API_KEY or GitHub push credentials.
No 'go' or second workflow is required.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from anthropic import Anthropic
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
SLUG = os.environ.get("BUILDING_NAME", "").strip()
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5").strip()
BRIEF_PATH = os.environ.get("BRIEF_PATH", "briefs/grand_fond_parish_church.md").strip()
REFERENCES = os.environ.get("REFERENCE_IMAGES", "").strip()
MAX_SPEND = float(os.environ.get("MAX_API_USD", "20"))
REVIEW_FIXES = int(os.environ.get("REVIEW_FIXES", "1"))
STAGES = ["shell", "architecture", "details"]
RATE = {"claude-sonnet-5-5": (2, 10), "claude-opus-5-5": (4, 20)}

if not re.fullmatch(r"[a-z][a-z0-9_]{2,55}", SLUG):
    sys.exit("building_name: 3–56 Zeichen, nur lower_snake_case")
if MODEL not in RATE:
    sys.exit("Nicht unterstütztes Claude-Modell")
if not 1 <= MAX_SPEND <= 250 or not 0 <= REVIEW_FIXES <= 2:
    sys.exit("max_api_usd muss 1–250, review_fixes 0–2 sein")
if not os.environ.get("ANTHROPIC_API_KEY"):
    sys.exit("GitHub Secret ANTHROPIC_API_KEY fehlt")


def repo_file(rel: str, allowed_root: str | None = None) -> Path:
    path = (REPO / rel).resolve()
    if not path.is_relative_to(REPO):
        raise ValueError(f"Pfad verlässt Repository: {rel}")
    if allowed_root and not path.is_relative_to((REPO / allowed_root).resolve()):
        raise ValueError(f"Pfad muss innerhalb {allowed_root}/ liegen: {rel}")
    return path


brief_file = repo_file(BRIEF_PATH, "briefs")
if not brief_file.is_file() or brief_file.suffix.lower() != ".md":
    sys.exit(f"Brief fehlt im Repo: {BRIEF_PATH}")
brief = brief_file.read_text(encoding="utf-8")
master = (REPO / "prompts" / "master_system.md").read_text(encoding="utf-8")
work = REPO / "_asset_work" / SLUG
delivery = REPO / "inbox" / SLUG
if work.exists():
    shutil.rmtree(work)
work.mkdir(parents=True)
(work / "stages").mkdir()
(work / "views").mkdir()
images = []
for rel in [s.strip() for s in REFERENCES.split(",") if s.strip()]:
    if len(images) >= 3:
        sys.exit("Maximal 3 Referenzbilder")
    src = repo_file(rel, "references")
    if not src.is_file() or src.stat().st_size > 5_000_000:
        sys.exit(f"Referenzbild fehlt oder >5 MB: {rel}")
    media = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(src.suffix.lower())
    if not media:
        sys.exit("Erlaubt: PNG, JPG, WEBP")
    images.append((rel, src, media))

# These image files are used for real material dependencies only, never generated.
texture_roots = [p for p in (REPO / "textures", REPO / "assets" / "textures") if p.is_dir()]
texture_index = {}
for root in texture_roots:
    for file in root.rglob("*.png"):
        texture_index.setdefault(file.stem, file)

client = Anthropic(timeout=360.0, max_retries=2)
usage = []


def check_budget():
    spent = sum((u["input_tokens"] * RATE[MODEL][0] + u["output_tokens"] * RATE[MODEL][1]) / 1e6 for u in usage)
    if spent >= MAX_SPEND:
        raise RuntimeError(f"Geschätztes API-Budget erreicht ({spent:.2f} / {MAX_SPEND:.2f} USD). Kein Commit.")
    return spent


def image_block(src: Path, mime: str):
    return {"type": "image", "source": {
        "type": "base64", "media_type": mime,
        "data": base64.b64encode(src.read_bytes()).decode("ascii"),
    }}


def ref_blocks():
    return [image_block(path, media) for _, path, media in images]


def ask(label: str, prompt: str, visual=None, max_tokens=9000) -> str:
    check_budget()
    print(f"CLAUDE {label}, bisher geschätzt ${check_budget():.2f}", flush=True)
    content = [{"type": "text", "text": prompt}]
    # Place images after the introductory instruction.
    content.extend(visual or [])
    response = client.messages.create(
        model=MODEL, max_tokens=max_tokens,
        system=master,
        messages=[{"role": "user", "content": content}],
    )
    usage.append({
        "label": label, "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    })
    text = "\n".join(item.text for item in response.content if item.type == "text").strip()
    if response.stop_reason == "max_tokens" or not text:
        raise RuntimeError(f"Claude-Ausgabe unvollständig bei {label}; keine unvollständigen Skripte ausführen")
    (work / "usage.json").write_text(json.dumps({"calls": usage, "estimate_usd": check_budget()}, indent=2), encoding="utf-8")
    return text


def code_clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:python)?\s*\n", "", text, count=1)
    text = re.sub(r"\n```\s*$", "", text, count=1)
    if text.startswith("```",) or text.endswith("```"):
        raise ValueError("Ungültiger Codeblock von Claude")
    compile(text, "claude_stage.py", "exec")
    return text + "\n"


def run_blender(mode: str, stage_name: str, previous: Path | None, code_file=None, output_blend=None, report=None):
    env = dict(os.environ)
    for secret in ("ANTHROPIC_API_KEY", "GH_TOKEN", "GITHUB_TOKEN", "ACTIONS_RUNTIME_TOKEN"):
        env.pop(secret, None)
    env.update({
        "WORKER_MODE": mode, "ASSET_WORK": str(work), "STAGE_NAME": stage_name,
        "STAGE_CODE": str(code_file or ""), "STAGE_OUT_BLEND": str(output_blend or ""),
        "STAGE_REPORT": str(report or ""),
        "GLB_PATH": str(work / f"{SLUG}.glb"), "MAX_TRIS": str(max_tris),
    })
    cmd = ["blender", "--background", "--factory-startup"]
    if previous is not None:
        cmd.append(str(previous))
    cmd += ["--python", str(REPO / "scripts" / "blender_worker.py")]
    try:
        result = subprocess.run(
            cmd, cwd=REPO, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=620,
        )
        log = result.stdout
        status = result.returncode
    except subprocess.TimeoutExpired as exc:
        log, status = str(exc), 124
    log_file = work / "stages" / f"{stage_name}.log"
    log_file.write_text(log, encoding="utf-8")
    print(f"BLENDER {stage_name} rc={status}\n{log[-1800:]}", flush=True)
    if status:
        raise RuntimeError(log[-15000:])
    if report is None or not report.is_file():
        raise RuntimeError("Blender-Report fehlt")
    return json.loads(report.read_text(encoding="utf-8"))


def run_code(label: str, prev: Path | None, prompt: str):
    """Generate and retry only the failed stage on the same saved predecessor."""
    failure = ""
    last_code = ""
    for retry in range(1, 4):
        task = prompt if not failure else (
            prompt + "\n\nDas vorige Stufenskript schlug fehl. Repariere gezielt diese Stufe, "
            "gebe aber wieder den vollständigen ausführbaren Stufencode aus. "
            "Vorstufen liegen schon als .blend vor.\n" +
            "BLENDER-TRACEBACK:\n" + failure[-10000:] +
            "\nVORHERIGER STUFENCODE:\n" + last_code[:38000]
        )
        answer = ask(f"{label}_code_{retry}", task, max_tokens=19000)
        try:
            last_code = code_clean(answer)
        except (SyntaxError, ValueError) as exc:
            failure = f"Python Syntaxfehler: {exc}"
            continue
        stage_code = work / "stages" / f"{label}_try{retry}.py"
        stage_code.write_text(last_code, encoding="utf-8")
        candidate = work / "stages" / f"{label}_try{retry}.blend"
        report = work / "stages" / f"{label}_try{retry}.json"
        try:
            result = run_blender("stage", label, prev, stage_code, candidate, report)
            return candidate, result
        except RuntimeError as exc:
            failure = str(exc)
    raise RuntimeError(f"Blender-Stufe '{label}' nach 3 Versuchen gescheitert: {failure[-2000:]}")


def review_stage(stage: str, report: dict, planned: str):
    previews = []
    for name in ("front", "side", "top", "threequarter"):
        path = Path(report["views"][name])
        previews.append(image_block(path, "image/png"))
    visuals = ref_blocks() + previews
    prompt = (
        "Du erhältst erst die vorhandenen Referenzfotos (Anzahl: " + str(len(images)) +
        "), danach die tatsächlichen vier Blender-Prüfansichten in der Reihenfolge FRONT, SIDE, TOP, THREEQUARTER.\n"
        "Vergleiche die nachweisbar sichtbaren Formen mit dem Plan und gegebenenfalls mit der Referenz. "
        "Nenne nur klar sichtbare größere Fehler und eine konkrete reparierbare Änderung. "
        "Bei Teilstufen ist fehlendes späteres Detail KEIN Fehler: shell = Grobkörper; "
        "architecture = Dach/Türen/Treppen; details = finale Baugeometrie/Platzhalter. "
        "Gib ausschließlich JSON zurück: {\"needs_fix\": true/false, \"issues\": [\"...\"], "
        "\"comparison_possible\": true/false}. Keine erfundenen Prüfungen.\n"
        f"STUFE: {stage}\nBERICHT:\n{json.dumps(report, ensure_ascii=False)[:12000]}\n"
        f"PLAN:\n{planned[:23000]}"
    )
    answer = ask(stage + "_vision_review", prompt, visuals, max_tokens=2200)
    raw = re.sub(r"^```(?:json)?\s*\n|\n```$", "", answer.strip())
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"needs_fix": False, "issues": ["Review nicht maschinenlesbar: " + answer[:400]], "comparison_possible": bool(images)}
    (work / "stages" / f"{stage}_review.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
    return parsed


print("1/5 PLAN – anschließend automatisch BUILD, kein GO nötig", flush=True)
refs = ref_blocks()
plan_prompt = (
    "Erstelle JETZT den vollständigen maßhaltigen Architektur- und Materialplan anhand des "
    "konkreten Briefings und aller verfügbaren echten Referenzen. Das ist die erste interne "
    "Stufe eines automatisch fortgesetzten Auftrags: WARTEN AUF GO IST VERBOTEN. "
    "Keine Blender-Codeausgabe in dieser Stufe. Plane auch alle Funktionswege, Möbelboxen, "
    "geplante Türen und die nötigen echten Fototexturen. "
    "Exaktes MAX_TRIS als einzelne Zeile 'MAX_TRIS: 150000' oder kleiner. "
    "Nenne alle bekannten Abweichungen.\n\n"
    f"BRIEF ({BRIEF_PATH}):\n{brief}\n"
    f"REFERENZFOTOS: {', '.join(n for n,_,_ in images) if images else 'KEINE – keine Bildtreue behaupten'}\n"
    f"VORHANDENE ECHTE TEXTUREN (max 120): {', '.join(list(texture_index)[:120]) or 'KEINE'}"
)
plan = ask("plan", plan_prompt, refs, max_tokens=10000)
(work / "plan.md").write_text(plan, encoding="utf-8")
max_match = re.search(r"MAX_TRIS\s*[:=]\s*(\d{4,7})", plan)
max_tris = int(max_match.group(1)) if max_match else 150000
if max_tris > 150000 or max_tris < 10000:
    raise RuntimeError(f"Plan MAX_TRIS außerhalb erlaubtem Bereich: {max_tris}")
print(f"PLAN abgeschlossen, MAX_TRIS={max_tris}. Starte SOFORT mit Blender.", flush=True)

previous = None
stage_results = {}
for idx, stage in enumerate(STAGES, start=1):
    print(f"{idx+1}/5 BUILD STUFE: {stage}", flush=True)
    purpose = {
        "shell": "Fundamente, Geschossplatten, echte dicke Wände mit realen Öffnungen, Raumvolumen, präzise Hauptsilhouette. Verteile die Teile in benannten Meshes. KEINE falsche Fassaden-Plane hinter Fenstern.",
        "architecture": "Auf bestehender shell-Szene: Dach als geschlossene Körper, Kirchturm, echte durchgängige Treppen samt Podesten, Fenster mit Laibungen, getrennte geschlossene Türblatt-Meshes samt Pivot, Geländer, Fassadenordnung.",
        "details": "Auf bestehender architecture-Szene: Detailgeometrie, echte Ziegelreihen, Dachrinnen, Fixierungen, Bevel, alle gültig benannten PBR-Materialslots, metrische UV0 (auch auf Bestand), maßhaltige Ph_*-Boxen für ALLE Räume mit lokalen Pivots. Korrigiere fehlende Slots/UVs in Bestand. Keine Fotoerzeugung.",
    }[stage]
    stage_prompt = (
        "Gib ausschließlich ausführbares Python für Blender 4.x (bpy) zurück, kein Markdown. "
        "Verwende KEINE Bildgenerierung, Downloads oder prozeduralen Texturen. "
        "Der Controller übernimmt Rendering, .blend-Speichern, Export und Prüfung. "
        "Du bearbeitest eine vorhandene .blend-Vorstufe (außer SHELL); "
        "die Python-Funktionen früherer Skripte existieren NICHT mehr, die bpy-Objekte schon. "
        "Beginne NICHT mit Szenenlöschung, außer bei SHELL (dort leert der Controller die Szene). "
        "Nutze zuverlässige bpy Mesh-Operatoren, nachvollziehbare Teilenamen, origin floor center für Ph_*. "
        "Die Materialnamen müssen aus der Systemliste stammen oder deklarierte new_* sein. "
        "Nach Blender Code wird NICHT manuell auf Go gewartet.\n"
        f"STUFE: {stage}\nAUFGABE: {purpose}\n"
        f"GEBÄUDE-BRIEF:\n{brief[:12000]}\n"
        f"VERBINDLICHER PLAN:\n{plan[:34000]}\n"
        f"VORSTUFEN-BERICHT: {json.dumps(stage_results.get(STAGES[idx-2], {}), ensure_ascii=False)[:9000] if idx>1 else 'Keine'}\n"
        f"Verfügbare Fototextur-Namen: {', '.join(list(texture_index)[:120])}"
    )
    previous, report = run_code(stage, previous, stage_prompt)
    stage_results[stage] = report
    verdict = review_stage(stage, report, plan)
    for correction in range(1, REVIEW_FIXES + 1):
        if not verdict.get("needs_fix") or not verdict.get("issues"):
            break
        issues = json.dumps(verdict["issues"], ensure_ascii=False)
        correction_prompt = (
            "Erstelle ausschließlich ausführbaren Blender-bpy-Python-Code für eine GEZIELTE KORREKTUR "
            "der bestehenden .blend-Szene, kein Neuanfang, keine Szenenlöschung. "
            "Die unten genannten Abweichungen wurden anhand ECHTER Blender-Renderings erkannt. "
            "Benenne neue Teile ordentlich und repariere vorhandene Meshes statt zusätzliche "
            "deckungslose Fassadenflächen darüberzulegen. Keine Bilderzeugung.\n"
            f"STUFE {stage}, KORREKTUR {correction}\nPROBLEME:\n{issues}\n"
            f"PLAN:\n{plan[:28000]}\nIST-BERICHT:\n{json.dumps(report, ensure_ascii=False)[:9000]}"
        )
        previous, report = run_code(f"{stage}_fix{correction}", previous, correction_prompt)
        stage_results[stage] = report
        verdict = review_stage(f"{stage}_fix{correction}", report, plan)

print("5/5 EXPORT, Materialcheck und realer GLB-Reimport", flush=True)
final_report = work / "final_validation.json"
result = run_blender("export", "final", previous, report=final_report)
new_materials = [m for m in result["materials"] if m.startswith("new_")]
missing = [m for m in new_materials if m not in texture_index]
if missing:
    raise RuntimeError(
        "Echte Fototexturen fehlen; Lieferung bewusst BLOCKIERT, keine synthetischen PNGs: "
        + ", ".join(missing)
    )

new_textures = []
for name in new_materials:
    file = texture_index[name]
    with Image.open(file) as image:
        if image.width < 1024 or image.height < 1024:
            raise RuntimeError(f"new_* Fototextur zu klein (<1024px): {file}")
    new_textures.append(file)

note_prompt = (
    "Erstelle eine kurze sachliche note.txt für das tatsächlich produzierte 3D-Gebäude "
    "in Deutsch. Keine Behauptung, dass Maße oder Bildtreue perfekt sind, wenn nicht belegt. "
    "Entscheidungen und Abweichungen zum Referenzfoto, Gebäudenutzung, furniture_style, "
    "Raumliste/Placeholder, Türen mit von/nach und Breiten aus dem Plan, exakte Materialliste, "
    "new_* Oberfläche mit real-world Tile-Maßen sofern BEKANNT; sonst unbekannt markieren. "
    "Die folgenden validierten Zahlen verwenden, nichts erfinden. Gib nur Text aus.\n"
    f"PLAN:\n{plan[:18000]}\n"
    f"PRÜFBERICHT:\n{json.dumps(result, ensure_ascii=False)[:16000]}\n"
    f"REFERENZFOTOS vorhanden: {'JA' if images else 'NEIN'}\n"
    f"NEW_MATERIAL_FILES: {[str(p.relative_to(REPO)) for p in new_textures]}\n"
    "Die visuelle Analyse ist eine KI-Einschätzung aus Blender-Workbench-Bildern, keine "
    "Garantie für Fotorealismus/Spielbarkeit oder eine automatisch durchgeführte UE5-Prüfung."
)
note = ask("note", note_prompt, max_tokens=5000)
note += (
    "\n\n=== Maschinenvalidierte Daten (Blender) ===\n"
    f"Meshes: {result['meshes']}\nTriangles: {result['triangles']}\n"
    f"Reimport Meshes: {result['reimport_meshes']}\n"
    f"Bounds m: {result['dimensions_m']}\n"
    f"Materials: {', '.join(result['materials'])}\n"
    f"Nodes Doors: {', '.join(result['doors'])}\n"
    f"Nodes Placeholders: {', '.join(result['placeholders'])}\n"
    f"API-Schätzkosten USD: {check_budget():.2f} (nicht der Abrechnungsbeleg)\n"
)
if delivery.exists():
    # Only the declared target directory may be replaced; Git commit is separately path-scoped.
    shutil.rmtree(delivery)
delivery.mkdir(parents=True)
shutil.copy2(work / f"{SLUG}.glb", delivery / f"{SLUG}.glb")
(delivery / "note.txt").write_text(note, encoding="utf-8")
for texture in new_textures:
    shutil.copy2(texture, delivery / texture.name)
if not (delivery / f"{SLUG}.glb").is_file():
    raise RuntimeError("Final GLB fehlt")
print(f"ERFOLG {delivery.relative_to(REPO)}: {result['triangles']} tris; {check_budget():.2f} USD geschätzt", flush=True)
