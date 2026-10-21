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
from prompt_contract import (compiler_task, contract_context, source_brief,
                             validate_compiled_contract, sha256_text)

REPO = Path(__file__).resolve().parents[1]
SLUG = os.environ.get("BUILDING_NAME", "").strip()
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5").strip()
BRIEF_PATH = os.environ.get("BRIEF_PATH", "briefs/grand_fond_parish_church.md").strip()
REFERENCES = os.environ.get("REFERENCE_IMAGES", "").strip()
DIRECT_PROMPT = os.environ.get("BUILDING_PROMPT", "")
REVIEW_FIXES = int(os.environ.get("REVIEW_FIXES", "1"))
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


brief_file = repo_file(BRIEF_PATH, "briefs") if BRIEF_PATH else None
if not DIRECT_PROMPT.strip() and (brief_file is None or brief_file.suffix.lower() != ".md"):
    sys.exit("Ein .md-Briefing innerhalb briefs/ wird benötigt")
try:
    brief, brief_source = source_brief(brief_file, DIRECT_PROMPT)
except (FileNotFoundError, ValueError) as error:
    sys.exit(str(error))
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
        f"PLAN:\n{planned}\nBAUVERTRAG:\n{building_contract}"
    )
    answer = ask(stage + "_vision_review", prompt, visuals)
    raw = re.sub(r"^```(?:json)?\s*\n|\n```$", "", answer.strip())
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"needs_fix": False, "issues": ["Review nicht maschinenlesbar: " + answer[:400]], "comparison_possible": bool(images)}
    (work / "stages" / f"{stage}_review.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
    return parsed


print("0/6 PROMPT-COMPILER – Originalprompt automatisch verschmelzen", flush=True)
refs = ref_blocks()
(work / "original_prompt.md").write_text(brief, encoding="utf-8")
compiled = ask("compiler", compiler_task(
    brief, [name for name, _, _ in images], SLUG), refs)
for attempt in range(1, 4):
    try:
        validate_compiled_contract(compiled)
        break
    except ValueError as error:
        print(f"PROMPT-COMPILER: {error}", flush=True)
        if attempt == 3:
            raise RuntimeError("Compiler konnte den Pflichtvertrag nicht erzeugen") from error
        compiled = ask(
            f"compiler_repair_{attempt}",
            "Repariere die Struktur des folgenden Compiler-Vertrags. "
            "Übernimm alle Anforderungen aus dem vollständigen ORIGINALPROMPT, "
            "verwende exakt die verlangten Überschriften. Warte nicht auf Go. "
            "Gib den gesamten korrigierten Vertrag aus.\n"
            + str(error) + "\nVORHERIGER VERTRAG:\n" + compiled
            + "\nORIGINALPROMPT:\n" + brief,
            refs,
        )
building_contract = contract_context(brief, compiled, brief_source)
(work / "compiled_contract.md").write_text(
    "# Automatisch verschmolzener Gebäudeauftrag\n\n"
    + f"Original: {brief_source}\nSHA256: {sha256_text(brief)}\n\n"
    + building_contract, encoding="utf-8",
)
print("1/6 PLAN – Vertrag geprüft; BUILD folgt ohne Go", flush=True)
plan_prompt = (
    "Erstelle JETZT den vollständigen maßhaltigen Architektur- und Materialplan anhand des "
    "konkreten Briefings und aller verfügbaren echten Referenzen. Das ist die erste interne "
    "Stufe eines automatisch fortgesetzten Auftrags: WARTEN AUF GO IST VERBOTEN. "
    "Keine Blender-Codeausgabe in dieser Stufe. Plane auch alle Funktionswege, Möbelboxen, "
    "geplante Türen und die nötigen echten Fototexturen. "
    "Exaktes MAX_TRIS als einzelne Zeile 'MAX_TRIS: 150000' oder kleiner. "
    "Nenne alle bekannten Abweichungen.\n\n"
    f"VERBINDLICHER BAUVERTRAG MIT ORIGINALPROMPT:\n{building_contract}\n"
    f"REFERENZFOTOS: {', '.join(n for n,_,_ in images) if images else 'KEINE – keine Bildtreue behaupten'}\n"
    f"VORHANDENE ECHTE TEXTUREN (max 120): {', '.join(list(texture_index)[:120]) or 'KEINE'}"
)
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
        "Nutze zuverlässige bpy Mesh-Operatoren, nachvollziehbare Teilenamen, origin floor center für Ph_*. "
        "Die Materialnamen müssen aus der Systemliste stammen oder deklarierte new_* sein. "
        "Nach Blender Code wird NICHT manuell auf Go gewartet.\n"
        f"STUFE: {stage}\nAUFGABE: {purpose}\n"
        f"BAUVERTRAG UND VOLLSTÄNDIGER ORIGINALPROMPT:\n{building_contract}\n"
        f"VERBINDLICHER PLAN:\n{plan}\n"
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
            f"BAUVERTRAG:\n{building_contract}\nPLAN:\n{plan}\nIST-BERICHT:\n{json.dumps(report, ensure_ascii=False)[:9000]}"
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
    f"BAUVERTRAG:\n{building_contract}\nPLAN:\n{plan}\n"
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
