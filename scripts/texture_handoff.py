"""Prepare Codex Plus image handoff from a finished architecture plan.

Never invokes an image API or synthesizes an image. The Codex session must
generate genuine photorealistic textures with its own available image feature.
"""
import argparse
import json
import re
import sys
from pathlib import Path

RX = re.compile(r"\bnew_[a-z][a-z0-9_]*\b")
BAD = {"new_what", "new_name", "new_material", "new_texture", "new_surface"}
SLUG = re.compile(r"[a-z][a-z0-9_]{2,55}\Z")
TEXTURE_SIZE = (1254, 1254)


def requested(plan, roots):
    existing = {p.stem for root in roots if root.exists() for p in root.rglob("*.png")}
    names = sorted(set(RX.findall(plan)) - BAD - existing)
    lines = plan.splitlines()
    result = []
    for name in names:
        desc = next((x.strip()[:350] for x in lines
                     if name in x and len(x.strip()) > len(name) + 15), "")
        result.append({
            "material": name, "filename": name + ".png",
            "description_from_plan": desc,
            "pixel_size": list(TEXTURE_SIZE), "physical_tile_size_m": None,
            "status": "awaiting_codex_image",
        })
    return result


def prepare(repo, name, plan_path, refs):
    if not SLUG.fullmatch(name):
        raise ValueError("Invalid slug")
    for rel in refs:
        file = (repo / rel).resolve()
        if not file.is_relative_to(repo) or not file.is_file():
            raise ValueError("Reference image missing: " + rel)
    plan = plan_path.read_text(encoding="utf-8")
    if not plan.strip():
        raise ValueError("Empty plan")
    folder = repo / "texture_requests" / name
    folder.mkdir(parents=True, exist_ok=True)
    missing = requested(plan, [
        repo / "inbox" / name, repo / "textures", repo / "assets" / "textures"
    ])
    data = {
        "version": 1, "building_name": name, "reference_images": refs,
        "plan_file": "texture_requests/" + name + "/plan.md",
        "texture_directory": "inbox/" + name,
        "missing_textures": missing,
        "requirements": "Photorealistic seamless photo-like image; no procedural or rendered look; exact native 1254x1254 PNG; no upscaling; matte diffuse even lighting; perpendicular camera; 3x3 repeat check",
    }
    (folder / "manifest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "plan.md").write_text(plan, encoding="utf-8")
    guide = """# Codex-Texturauftrag fuer """ + name + """

Diese Datei ist eine UEbergabe an eine Codex-Sitzung mit dem ChatGPT-Plus-Abo,
kein API-Aufruf von GitHub Actions. Codex muss wirklich Zugriff auf seine
Bildgenerierung haben; ansonsten melden und nicht mit Blender/Shader/Python
synthetische Foto-Texturen vortaeuschen.

1. Lies texture_requests/""" + name + """/manifest.json und plan.md.
2. Sieh dir die dort genannten Originalreferenzen in referenzbilder/ an.
3. Erzeuge ausschliesslich die als missing_textures gelisteten Bilder.
   Falls die Liste leer ist: KEINE neuen Bilder noetig.
4. Pro Material Beschreibung aus dem Plan beachten; bei unklaren
   Oberflaechen nicht raten, sondern nachfragen. Perspektive genau
   senkrecht, realistische fotografische Oberflaeche, keine gemalten
   Kanten, Schatten, Glanz, Verfahrenstricks oder Pseudo-Fotos.
   Kein Mirroring, kein Ghosting, keine vignettierten Raender.
5. Korrekte, wirklich nahtlose native 1254x1254-PNG mit Dateinamen
   aus manifest.json unter inbox/""" + name + """/ direkt neben der
   spaeteren GLB und note.txt speichern. KEIN Upscaling.
6. Wiederholung als 3x3-Kacheln auch VISUELL pruefen. Physische
   Abdeckung in Metern dokumentieren und manifest.json aktualisieren.
7. Fuehre aus: python3 scripts/texture_handoff.py verify --repo . --slug """ + name + """
8. Committe und pushe die neuen PNG-Dateien unter inbox/""" + name + """/
   und das aktualisierte Manifest nach main. Die spaetere Actions-Buildstufe
   darf diese PNGs NICHT beim Aufraeumen des Ausgabeordners loeschen.
9. Starte den teuren Claude-Build nicht von selbst. Gib dem Benutzer
   die urspruengliche GitHub-Plan-Run-ID als resume_run_id fuer die
   separate Fortsetzung mit identischem Prompt/Referenzbild.

Standardmaterialien aus der MATERIAL LIST gehoeren nicht in diese Liste.
Bestehende engine-seitige Foto-Texturen nicht kopieren oder ersetzen.
"""
    (folder / "CODEX_TASK.md").write_text(guide, encoding="utf-8")
    return data


def verify(repo, name):
    if not SLUG.fullmatch(name):
        raise ValueError("Invalid slug")
    manifest = repo / "texture_requests" / name / "manifest.json"
    if not manifest.is_file():
        print("NO_TEXTURE_REQUESTS: " + str(manifest))
        return 0
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("building_name") != name:
        raise ValueError("Wrong building in manifest")
    from PIL import Image
    failures = []
    for item in data.get("missing_textures", []):
        material = item["material"]
        if not RX.fullmatch(material):
            raise ValueError("Invalid material name")
        file = next((p for p in (repo / "inbox" / name / (material + ".png"),
                                 repo / "textures" / (material + ".png"),
                                 repo / "assets" / "textures" / (material + ".png"))
                     if p.is_file()), None)
        if file is None:
            failures.append("MISSING " + material)
            continue
        try:
            with Image.open(file) as im:
                if im.format != "PNG" or im.size != TEXTURE_SIZE:
                    failures.append("EXPECTED_1254_PNG " + str(file))
                im.verify()
        except OSError:
            failures.append("CORRUPT " + str(file))
    for issue in failures:
        print("TEXTURE_ERROR: " + issue)
    if failures:
        return 1
    print("CODEX_TEXTURES_READY:", name, len(data.get("missing_textures", [])))
    return 0


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("prepare")
    a.add_argument("--repo", type=Path, default=Path("."))
    a.add_argument("--slug", required=True)
    a.add_argument("--plan", type=Path, required=True)
    a.add_argument("--ref", action="append", default=[])
    b = sub.add_parser("verify")
    b.add_argument("--repo", type=Path, default=Path("."))
    b.add_argument("--slug", required=True)
    args = p.parse_args()
    root = args.repo.resolve()
    if args.cmd == "prepare":
        result = prepare(root, args.slug, args.plan, args.ref)
        print("CODEX_TEXTURE_HANDOFF_READY:", len(result["missing_textures"]))
    else:
        sys.exit(verify(root, args.slug))


if __name__ == "__main__":
    main()
