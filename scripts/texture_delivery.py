"""Non-blocking photo-texture inventory for UE5 building exports.

This module deliberately checks only whether an expected new_<material>.png
file exists. Missing photos NEVER block a verified GLB delivery. It does not
inspect dimensions, image content, photo-realism, or tile seams.
"""
from __future__ import annotations

from pathlib import Path


def inventory_new_materials(materials: list[str], image_index: dict[str, Path]):
    """Return (available PNG paths, missing material names), sorted and unique."""
    names = sorted({name for name in materials if name.startswith("new_")})
    available = []
    missing = []
    for name in names:
        path = image_index.get(name)
        if path is not None and path.is_file() and path.stat().st_size > 0:
            available.append(path)
        else:
            missing.append(name)
    return available, missing


def missing_texture_note(missing: list[str], building_name: str) -> str:
    """Machine-readable appendix for note.txt; no photography quality verdict."""
    if not missing:
        return "\n=== Fehlende Fototexturen ===\nKeine.\n"
    lines = ["\n=== Fehlende Fototexturen (GLB wurde trotzdem ausgeliefert) ===",
             "Die Materialslots sind im GLB vorhanden; passende PNG-Dateien sind nachzureichen:"]
    lines += [f"- {name}: inbox/{building_name}/{name}.png (FEHLT)" for name in sorted(set(missing))]
    lines.append("Kein Bild-/Nahtlosigkeitscheck ausgefuehrt; fehlende Fotos sind kein Export-Blocker.")
    return "\n".join(lines) + "\n"
