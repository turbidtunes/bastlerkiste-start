"""No-model-cost regression: Codex handoff files belong beside final GLB."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from sys import path as sys_path

sys_path.insert(0, str(Path(__file__).resolve().parents[1]))
from texture_handoff import prepare, verify

from PIL import Image

with tempfile.TemporaryDirectory(prefix="codex_texture_test_") as d:
    repo = Path(d)
    (repo / "referenzbilder").mkdir()
    (repo / "referenzbilder" / "finca.png").write_bytes(b"test reference")
    (repo / "_asset_work" / "les_calanques_finca").mkdir(parents=True)
    plan_path = repo / "_asset_work" / "les_calanques_finca" / "plan.md"
    plan_path.write_text(
        "1. IDENTITÄT: spanisch-traditionelle Finca\n"
        "9. MATERIALIEN:\n"
        "   Barn roof: roof_terracotta\n"
        "   Exterior unusual plaster: new_finca_plaster – faded ochre rough limestone plaster\n"
        "13. MAX_TRIS: 120000\n"
        "PLAN_COMPLETE\n", encoding="utf-8"
    )
    name = "les_calanques_finca"
    ref = "referenzbilder/finca.png"
    manifest = prepare(repo, name, plan_path, [ref])
    assert manifest["texture_directory"] == "inbox/" + name, manifest
    assert [x["material"] for x in manifest["missing_textures"]] == [
        "new_finca_plaster"], manifest
    assert manifest["missing_textures"][0]["pixel_size"] == [1254, 1254]
    assert (repo / "texture_requests" / name / "CODEX_TASK.md").is_file()
    guide = (repo / "texture_requests" / name / "CODEX_TASK.md").read_text()
    assert "inbox/" + name + "/" in guide
    assert "textures/ speichern" not in guide
    assert verify(repo, name) == 1, "Must reject missing image BEFORE build"
    image_dir = repo / "inbox" / name
    image_dir.mkdir(parents=True)
    file = image_dir / "new_finca_plaster.png"
    # Both the former resolution and smaller/non-square images must fail.
    for size in [(2048, 2048), (1024, 1024), (1254, 1024)]:
        Image.new("RGB", size, (151, 132, 104)).save(file)
        assert verify(repo, name) == 1, f"Must reject {size}"
    Image.new("RGB", (1254, 1254), (151, 132, 104)).save(file, format="JPEG")
    assert verify(repo, name) == 1, "A PNG extension is not sufficient"
    file.write_bytes(b"not an image")
    assert verify(repo, name) == 1, "Must reject corrupt image"
    Image.new("RGB", (1254, 1254), (151, 132, 104)).save(file)
    assert verify(repo, name) == 0
    assert not (repo / "textures" / "new_finca_plaster.png").exists()
    with Image.open(file) as img:
        assert img.size == (1254, 1254)
    # The presence of an image makes a NEW plan omit it from pending requests.
    manifest2 = prepare(repo, name, plan_path, [ref])
    assert manifest2["missing_textures"] == []
    assert verify(repo, name) == 0

print("CODEX_TEXTURE_HANDOFF_SMOKE_OK: pre-build verify and PNG next to GLB destination")
