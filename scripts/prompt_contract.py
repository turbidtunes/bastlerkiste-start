"""Lossless prompt contract helpers for the UE5 Blender building agent.

This module intentionally has no Anthropic dependency and does not call the API.
Claude's compiled plan is ADDITIVE; the source brief is always passed through.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

MIN_BRIEF_LENGTH = 25
MANDATORY_SECTIONS = (
    "IDENTITY_AND_USE",
    "SITE_AND_DIMENSIONS",
    "ARCHITECTURE_AND_ACCESS",
    "ROOMS_AND_FURNITURE",
    "DOORS_AND_WINDOWS",
    "MATERIALS_AND_UVS",
    "REFERENCE_AND_DEVIATIONS",
    "CONFLICT_RESOLUTIONS",
    "ACCEPTANCE_CHECKLIST",
)


def source_brief(brief_path: Path | None, free_prompt: str = "") -> tuple[str, str]:
    """A complete pasted prompt takes precedence over a file, without truncation."""
    if free_prompt.strip():
        result, source = free_prompt.strip(), "workflow_dispatch:building_prompt"
    elif brief_path is not None:
        if not brief_path.is_file():
            raise FileNotFoundError(f"Gebäude-Prompt fehlt: {brief_path}")
        result, source = brief_path.read_text(encoding="utf-8"), str(brief_path)
    else:
        raise ValueError("Gebäude-Prompt oder Briefing-Datei erforderlich")
    if len(result.strip()) < MIN_BRIEF_LENGTH:
        raise ValueError("Gebäude-Prompt ist leer oder zu kurz")
    return result, source


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compiler_task(brief: str, reference_names: list[str], asset_name: str) -> str:
    """Build an additive, auditable compiler request; never replace the source."""
    return f"""AUFGABE: VEREINHEITLICHE DIESEN VOLLSTÄNDIGEN ALTEN GEBÄUDE-PROMPT
MIT DEM SEPARAT ÜBERGEBENEN GLOBALEN BLENDER-SYSTEMPROMPT. KEINE KÜRZUNG
DER REGELN UND KEINE NEUEN HARTEN TOKENLIMITS.

Dies ist die verpflichtende VORSTUFE eines automatischen Blender-Builds.
Der Originalprompt bleibt IN JEDEM WEITEREN SCHRITT zusätzlich erhalten.
Das Ergebnis ist ein strukturierter Arbeitsvertrag, keine Blender-Codeausgabe.
Keine Freigabe, kein 'Go' abwarten; die Pipeline modelliert direkt anschließend.

Konflikte verbindlich lösen:
- Systemregeln übersteuern widersprechende Anweisungen im alten Prompt,
  insbesondere Warten auf 'Go', externe Downloads oder Bilderzeugung.
- Gebäudespezifische Architektur, Grundstück, Stil, Funktion, Materialien,
  Raumprogramm, Tür- und Placeholder-Vorgaben aus dem Original bleiben erhalten.
- Ein Bauobjekt erhält nur die tatsächlich beschriebenen Sondermerkmale.
  Keine generischen Kirchtürme, Ziegeldächer oder Wohnräume erzwingen.
- Nie behaupten, Referenzen gesehen zu haben, wenn sie fehlen.
- Fehlende echte Fototexturen dokumentieren; keine synthetischen Ersatzbilder.
- Echte Abweichungen und unauflösbare Widersprüche ausdrücklich auflisten.

Erzeuge ein Markdown-Dokument, bei dem ALLE folgenden Überschriften
wortgleich als '## NAME' vorkommen:
{chr(10).join('## ' + section for section in MANDATORY_SECTIONS)}

- IDENTITY_AND_USE: Nutzungsart und genau ein furniture_style.
- SITE_AND_DIMENSIONS: konkrete Maße, Grundstück, Geschosse und Ausrichtung.
- ARCHITECTURE_AND_ACCESS: konstruktiver Aufbau, Räume und begehbare Wege.
- ROOMS_AND_FURNITURE: Raumliste und jede erforderliche Placeholder-Rolle.
- DOORS_AND_WINDOWS: reale Öffnungen, Türnamen, Scharnierseiten, Fenster.
- MATERIALS_AND_UVS: alle Materialnamen, new_* und UV-Regeln.
- REFERENCE_AND_DEVIATIONS: nur nachweisbare Referenzbeobachtungen.
- CONFLICT_RESOLUTIONS: jede angewendete Vorrangregel und offene Konflikte.
- ACCEPTANCE_CHECKLIST: prüfbare vollständige Liste der Muss-Anforderungen.

Schreibe ohne informelle Abkürzungen; komplexe Gebäude ausführlich.
Wenn Angaben nicht im Original stehen, kennzeichne Annahmen sichtbar.

ASSET_ID: {asset_name}
REFERENZEN: {', '.join(reference_names) if reference_names else 'KEINE'}

=== ORIGINALPROMPT – UNVERÄNDERT, VOLLSTÄNDIG ===
{brief}
=== ENDE ORIGINALPROMPT ===
"""


def validate_compiled_contract(compiled: str) -> None:
    missing = [s for s in MANDATORY_SECTIONS if not re.search(
        rf"^##\s+{re.escape(s)}\s*$", compiled, re.MULTILINE)]
    if missing:
        raise ValueError("Compiler-Vertrag hat fehlende Abschnitte: " + ", ".join(missing))
    if len(compiled.strip()) < 400:
        raise ValueError("Compiler-Vertrag ist ungewöhnlich kurz")


def contract_context(brief: str, compiled: str, source: str) -> str:
    """Always include the entire untouched source alongside the normalized spec."""
    validate_compiled_contract(compiled)
    return ("=== VERBINDLICHER KOMPILIERTER BAUVERTRAG ===\n" + compiled +
            "\n=== ORIGINALPROMPT (VERBATIM, BEI KONFLIKTEN SYSTEMPRIORITÄT) ===\n" +
            brief + "\n=== ENDE ORIGINALPROMPT ===\n" +
            f"ORIGINAL_SOURCE: {source}\nORIGINAL_SHA256: {sha256_text(brief)}")
