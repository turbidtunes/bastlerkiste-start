"""PLAN -> Blender stages -> four-view Claude vision checks -> GLB reimport -> inbox.

Only the normal Claude Messages API is used. The generated Blender scripts are
executed as subprocesses without ANTHROPIC_API_KEY or GitHub push credentials.
No 'go' or second workflow is required.
"""
from __future__ import annotations

import base64
import hashlib
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
REFERENCES = os.environ.get("REFERENCE_IMAGES", "").strip()
PROMPT_PATH = os.environ.get("PROMPT_PATH", "").strip()
REVIEW_FIXES = int(os.environ.get("REVIEW_FIXES", "1"))
RESUME_RUN_ID = os.environ.get("RESUME_RUN_ID", "").strip()
STAGES = ["shell", "architecture", "details"]
RATE = {"claude-sonnet-5-5": (2, 10), "claude-opus-5-5": (4, 20)}

if not re.fullmatch(r"[a-z][a-z0-9_]{2,55}", SLUG):
    sys.exit("building_name: 3–56 Zeichen, nur lower_snake_case")
if MODEL not in RATE:
    sys.exit("Nicht unterstütztes Claude-Modell")
if not 0 <= REVIEW_FIXES <= 2:
    sys.exit("review_fixes muss 0–2 sein")
if not os.environ.get("ANTHROPIC_API_KEY"):
    sys.exit("GitHub Secret ANTHROPIC_API_KEY fehlt")


def repo_file(rel: str, allowed_root: str | None = None) -> Path:
    path = (REPO / rel).resolve()
    if not path.is_relative_to(REPO):
        raise ValueError(f"Pfad verlässt Repository: {rel}")
    if allowed_root and not path.is_relative_to((REPO / allowed_root).resolve()):
        raise ValueError(f"Pfad muss innerhalb {allowed_root}/ liegen: {rel}")
    return path


# Der vollständige, bereits kombinierte Prompt liegt unter prompts/ im Repository.
# Kein Compiler und keine zusätzliche master_system.md in den Modellkontext laden.
if not PROMPT_PATH:
    sys.exit("prompt_path fehlt: Dateipfad unter prompts/ angeben")
try:
    prompt_file = repo_file(PROMPT_PATH, "prompts")
except ValueError as exc:
    sys.exit(str(exc))
if prompt_file.suffix.lower() != ".md" or not prompt_file.is_file():
    sys.exit(f"Prompt-Datei nicht gefunden oder keine Markdown-Datei: {PROMPT_PATH}")
if prompt_file.name == "master_system.md":
    sys.exit("master_system.md ist nur ein allgemeiner Alt-Prompt; bitte eine vollständig kombinierte Gebäude-Datei wählen")
brief = prompt_file.read_text(encoding="utf-8-sig")
if len(brief.strip()) < 25:
    sys.exit(f"Prompt-Datei ist leer oder zu kurz: {PROMPT_PATH}")
print(f"VOLLSTAENDIGEN PROMPT LADEN: {PROMPT_PATH} ({len(brief)} Zeichen)", flush=True)
master = (
    "Du bist ein erfahrener Blender-4.x-bpy- und UE5-3D-Asset-Agent. "
    "Der vollständige Bauauftrag ist vom Nutzer bereits manuell zusammengeführt; "
    "bewahre seine konkreten Vorgaben und ergänze keinen zweiten Masterprompt. "
    "Der Ablauf ist stets automatisch: zuerst gründlich planen, danach ohne Go "
    "Schritt für Schritt Blender-Code erstellen, Renderbilder überprüfen, "
    "Fehler gezielt korrigieren und GLB validieren. "
    "In reinen Codephasen gib ausschließlich vollständigen ausführbaren Python-Code zurück. "
    "Keine externen Assets herunterladen oder fotorealistische Texturen synthetisieren. "
    "Behaupte keine nicht durchgeführten Blender- oder Bildprüfungen."
)
work = REPO / "_asset_work" / SLUG
delivery = REPO / "inbox" / SLUG
if work.exists() and not RESUME_RUN_ID:
    shutil.rmtree(work)
work.mkdir(parents=True, exist_ok=True)
(work / "stages").mkdir(exist_ok=True)
(work / "views").mkdir(exist_ok=True)
if RESUME_RUN_ID and not (work / "plan.md").is_file():
    sys.exit("Fortsetzung blockiert: vorheriger Actions-Artefakt-Download enthält keinen Architekturplan; kein neuer Claude-Aufruf")
images = []
for rel in [s.strip() for s in REFERENCES.split(",") if s.strip()]:
    src = repo_file(rel)
    if not any(src.is_relative_to((REPO / folder).resolve())
               for folder in ("references", "referenzbilder")):
        sys.exit(f"Referenzbild muss in references/ oder referenzbilder/ liegen: {rel}")
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

client = Anthropic(timeout=900.0, max_retries=2)
# Die Anthropic-API verlangt pro Anfrage max_tokens.
# Wir nutzen das Maximum laut Models API und setzen ggf. automatisch fort.
MODEL_MAX_TOKENS = int(client.models.retrieve(model_id=MODEL).max_tokens)
usage = []


def check_budget():
    spent = sum((u["input_tokens"] * RATE[MODEL][0] + u["output_tokens"] * RATE[MODEL][1]) / 1e6 for u in usage)
    return spent


def image_block(src: Path, mime: str):
    return {"type": "image", "source": {
        "type": "base64", "media_type": mime,
        "data": base64.b64encode(src.read_bytes()).decode("ascii"),
    }}


def ref_blocks():
    return [image_block(path, media) for _, path, media in images]


def ask(label: str, prompt: str, visual=None) -> str:
    """Streaming bis zum natürlichen Abschluss; kein eigenes Gesamt-Token- oder Budgetlimit.

    max_tokens ist ein Pflichtparameter der API und wird aus der Modell-API ermittelt.
    Wenn er erreicht wird, schreibt Claude automatisch in Folgeturns weiter.
    """
    print(f"CLAUDE {label}, bisher geschätzt ${check_budget():.2f}", flush=True)
    content = [{"type": "text", "text": prompt}]
    content.extend(visual or [])
    messages = [{"role": "user", "content": content}]
    chunks = []
    empty_count = 0

    while True:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MODEL_MAX_TOKENS,
            system=master,
            messages=messages,
        ) as stream:
            response = stream.get_final_message()

        part = "".join(block.text for block in response.content if block.type == "text")
        usage.append({
            "label": label,
            "part": len(usage) + 1,
            "stop_reason": response.stop_reason,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        })
        if part:
            chunks.append(part)
            empty_count = 0
        else:
            empty_count += 1
        (work / "usage.json").write_text(json.dumps({
            "calls": usage, "estimate_usd": check_budget()
        }, indent=2), encoding="utf-8")
        print(f"CLAUDE {label}: stop={response.stop_reason}, "
              f"Tokens={response.usage.output_tokens}, "
              f"gesamt geschätzt USD={check_budget():.2f}", flush=True)

        if response.stop_reason == "end_turn":
            complete = "".join(chunks).strip()
            if not complete:
                raise RuntimeError(f"Claude lieferte keinen Text bei {label}")
            return complete
        if response.stop_reason not in ("max_tokens", "pause_turn"):
            raise RuntimeError(f"Claude stoppte bei {label}: {response.stop_reason}")
        if empty_count >= 3:
            raise RuntimeError(f"Claude produziert bei {label} keinen Textfortschritt")

        messages.append({
            "role": "assistant",
            "content": [block.model_dump(exclude_none=True) for block in response.content],
        })
        messages.append({
            "role": "user",
            "content": (
                "Fahre exakt an der unterbrochenen Stelle fort. "
                "Gib ausschließlich den fehlenden Rest aus, "
                "ohne Wiederholung, ohne Einleitung und ohne neue Code-Fences. "
                "Schließe den ursprünglichen Auftrag vollständig ab."
            ),
        })
        print(f"CLAUDE {label}: automatisch fortsetzen...", flush=True)


def code_clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:python)?\s*\n", "", text, count=1)
    text = re.sub(r"\n```\s*$", "", text, count=1)
    if text.startswith("```",) or text.endswith("```"):
        raise ValueError("Ungültiger Codeblock von Claude")
    compile(text, "claude_stage.py", "exec")
    return text + "\n"


class BlenderEnvironmentError(RuntimeError):
    """Blender cannot start because the runner lacks a runtime library."""


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
        lower_log = log.lower()
        if any(marker in lower_log for marker in (
            "libegl.so.1",
            "error while loading shared libraries",
            "cannot open shared object file",
        )):
            raise BlenderEnvironmentError(
                "BLENDER-RUNNER-FEHLER: Systembibliothek fehlt. "
                "Erneute Claude-Codegenerierung kann das nicht beheben. "
                "Pruefe die GitHub-Actions-Installation.\n" + log[-15000:]
            )
        raise RuntimeError(log[-15000:])
    if report is None or not report.is_file():
        raise RuntimeError(
            "Blender-Report fehlt: Blender-Skript/GLB-Export vermutlich abgebrochen "
            "oder intern fehlgeschlagen. Laufzeitlog:\n" + log[-7500:]
        )
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
            "BLENDER-TRACEBACK:\n" + failure +
            "\nVORHERIGER STUFENCODE:\n" + last_code
        )
        answer = ask(f"{label}_code_{retry}", task)
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
        except BlenderEnvironmentError:
            # Environment defects are not generated-code defects; don't waste API tokens.
            raise
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
        f"STUFE: {stage}\nBERICHT:\n{json.dumps(report, ensure_ascii=False)}\n"
        f"PLAN:\n{planned}\nVOLLSTÄNDIGER EINGABEPROMPT:\n{brief}"
    )
    answer = ask(stage + "_vision_review", prompt, visuals)
    raw = re.sub(r"^```(?:json)?\s*\n|\n```$", "", answer.strip())
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"needs_fix": False, "issues": ["Review nicht maschinenlesbar: " + answer[:400]], "comparison_possible": bool(images)}
    (work / "stages" / f"{stage}_review.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
    return parsed


# A resumed run must match the original instructions and reference images exactly.
# A changed prompt or different reference may require rebuilding from the start.
source_digest = hashlib.sha256()
source_digest.update(brief.encode("utf-8"))
for ref_name, ref_file, _ in images:
    source_digest.update(ref_name.encode("utf-8"))
    source_digest.update(ref_file.read_bytes())
fingerprint = source_digest.hexdigest()
fingerprint_path = work / "source_fingerprint.txt"
checkpoint_path = work / "stage_checkpoints.json"
if RESUME_RUN_ID:
    if not fingerprint_path.is_file() or fingerprint_path.read_text().strip() != fingerprint:
        sys.exit("Fortsetzung blockiert: Prompt oder Referenzfoto ist anders als beim gespeicherten Build; kein Claude-Aufruf")
    if not checkpoint_path.is_file():
        sys.exit("Fortsetzung blockiert: keine fertigen Stufen-Checkpoints im gewählten Lauf; kein Claude-Aufruf")
    checkpoints = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    print(f"FORTSETZUNG AUS GITHUB-RUN {RESUME_RUN_ID}: {', '.join(checkpoints) or 'nur Plan'}", flush=True)
else:
    fingerprint_path.write_text(fingerprint + "\n", encoding="utf-8")
    checkpoints = {}

# Reuse pre-validated building primitives instead of re-generating boilerplate bpy.
KIT_GUIDE = (REPO / "scripts" / "blender_lib" / "API.md").read_text(encoding="utf-8")
print("BUILDING_KIT aktiv: bewährte Bauteile und Blueprint-API geladen", flush=True)
print("1/5 PLAN – anschließend automatisch BUILD, kein GO nötig", flush=True)
refs = ref_blocks()
(work / "input_prompt.md").write_text(brief, encoding="utf-8")
plan_prompt = (
    "Erstelle JETZT den vollständigen maßhaltigen Architektur- und Materialplan anhand des "
    "konkreten Briefings und aller verfügbaren echten Referenzen. Das ist die erste interne "
    "Stufe eines automatisch fortgesetzten Auftrags: WARTEN AUF GO IST VERBOTEN. "
    "Keine Blender-Codeausgabe in dieser Stufe. Plane auch alle Funktionswege, Möbelboxen, "
    "geplante Türen und die nötigen echten Fototexturen. "
    "Exaktes MAX_TRIS als einzelne Zeile 'MAX_TRIS: 150000' oder kleiner. "
    "Nenne alle bekannten Abweichungen.\n\n"
    f"VOLLSTÄNDIGER MANUELL ZUSAMMENGEFÜHRTER EINGABEPROMPT:\n{brief}\n"
    f"REFERENZFOTOS: {', '.join(n for n,_,_ in images) if images else 'KEINE – keine Bildtreue behaupten'}\n"
    f"VORHANDENE ECHTE TEXTUREN (alle vorhandenen): {', '.join(list(texture_index)) or 'KEINE'}"
)
if RESUME_RUN_ID:
    plan = (work / "plan.md").read_text(encoding="utf-8")
    print("PLAN aus vorherigem Lauf geladen: keine erneuten Plan-Tokens", flush=True)
else:
    plan = ask("plan", plan_prompt, refs)
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
    if stage in checkpoints:
        if any(previous_stage not in checkpoints for previous_stage in STAGES[:idx-1]):
            raise RuntimeError(f"Ungültige Checkpoint-Reihenfolge: {stage}")
        prior = checkpoints[stage]
        previous = (work / "stages" / prior["blend_file"]).resolve()
        if not previous.is_relative_to((work / "stages").resolve()) or not previous.is_file():
            raise RuntimeError(f"Gesicherter Blender-Checkpoint fehlt: {previous}")
        report = prior["report"]
        stage_results[stage] = report
        print(f"STUFE {stage} AUS CHECKPOINT: {previous.name}, keine Claude-Neugenerierung", flush=True)
        continue
    purpose = {
        "shell": "Fundamente, Geschossplatten, echte dicke Wände mit realen Öffnungen, Raumvolumen, präzise Hauptsilhouette. Verteile die Teile in benannten Meshes. KEINE falsche Fassaden-Plane hinter Fenstern.",
        "architecture": "Auf bestehender shell-Szene: geplante Dachform und gebäudespezifische Sonderbauten (nur falls laut Auftrag), echte Treppen und Podeste, Fenster mit Laibungen, getrennte geschlossene Türblatt-Meshes samt Pivot, Geländer, Fassadenordnung gemäß Plan.",
        "details": "Auf bestehender architecture-Szene: maßhaltige Details der laut Plan vorgesehenen Dachdeckung (Ziegel/Wellblech/Schiefer/andere), Dachrinnen, Befestigungen, Bevel, PBR-Materialslots und metrische UV0 auch im Bestand, maßhaltige Ph_*-Boxen für alle Räume. Korrigiere fehlende Slots und UVs. Keine Fotoerzeugung.",
    }[stage]
    stage_prompt = (
        "Gib ausschließlich ausführbares Python für Blender 4.x (bpy) zurück, kein Markdown. "
        "Verwende KEINE Bildgenerierung, Downloads oder prozeduralen Texturen. "
        "Der Controller übernimmt Rendering, .blend-Speichern, Export und Prüfung. "
        "Du bearbeitest eine vorhandene .blend-Vorstufe (außer SHELL); "
        "die Python-Funktionen früherer Skripte existieren NICHT mehr, die bpy-Objekte schon. "
        "Beginne NICHT mit Szenenlöschung, außer bei SHELL (dort leert der Controller die Szene). "
        "Verwende für Standardelemente vorrangig 'import building_kit as kit' und die getesteten "
        "kit-Methoden für Wände, Öffnungen, Dächer, Treppen, Türen und Platzhalter. "
        "Individuelle Gebäudeformen weiterhin maßhaltig in bpy umsetzen. "
        "Jede Stufe importiert building_kit erneut, die bereits gebauten Meshes bleiben in der Szene. "
        "Nutze zuverlässige bpy Mesh-Operatoren, nachvollziehbare Teilenamen, origin floor center für Ph_*. "
        "Die Materialnamen müssen aus der Systemliste stammen oder deklarierte new_* sein. "
        "Nach Blender Code wird NICHT manuell auf Go gewartet.\n"
        f"STUFE: {stage}\nAUFGABE: {purpose}\n"
        f"GETESTETE WIEDERVERWENDBARE BAUBIBLIOTHEK (im Blender-Lauf als import building_kit verfügbar):\n{KIT_GUIDE}\n"
        f"VOLLSTÄNDIGER EINGABEPROMPT:\n{brief}\n"
        f"VERBINDLICHER PLAN:\n{plan}\n"
        f"VORSTUFEN-BERICHT: {json.dumps(stage_results.get(STAGES[idx-2], {}), ensure_ascii=False) if idx>1 else 'Keine'}\n"
        f"Verfügbare Fototextur-Namen: {', '.join(list(texture_index))}"
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
            f"WIEDERVERWENDBARE BLENDER-API:\n{KIT_GUIDE}\n"
            f"EINGABEPROMPT:\n{brief}\nPLAN:\n{plan}\nIST-BERICHT:\n{json.dumps(report, ensure_ascii=False)}"
        )
        previous, report = run_code(f"{stage}_fix{correction}", previous, correction_prompt)
        stage_results[stage] = report
        verdict = review_stage(f"{stage}_fix{correction}", report, plan)

    # Persist the last visually checked .blend before continuing to the next stage.
    checkpoints[stage] = {"blend_file": previous.name, "report": report}
    checkpoint_path.write_text(json.dumps(checkpoints, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"CHECKPOINT_GESICHERT {stage}: {previous.name}", flush=True)

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
    f"EINGABEPROMPT:\n{brief}\nPLAN:\n{plan}\n"
    f"PRÜFBERICHT:\n{json.dumps(result, ensure_ascii=False)}\n"
    f"REFERENZFOTOS vorhanden: {'JA' if images else 'NEIN'}\n"
    f"NEW_MATERIAL_FILES: {[str(p.relative_to(REPO)) for p in new_textures]}\n"
    "Die visuelle Analyse ist eine KI-Einschätzung aus Blender-Workbench-Bildern, keine "
    "Garantie für Fotorealismus/Spielbarkeit oder eine automatisch durchgeführte UE5-Prüfung."
)
note = ask("note", note_prompt)
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
