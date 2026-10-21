# Claude Blender AutoBuild – fertige Markdown-Prompts aus dem Repository

Die Pipeline erwartet eine **bereits fertig zusammengeführte Markdown-Datei**
im Verzeichnis `prompts/` des GitHub-Repositories
`turbidtunes/bastlerkiste-start`. Es gibt **keinen Prompt-Compiler** und
**kein langes Texteingabefeld** im GitHub-Actions-Startformular.

## Für jedes neue Gebäude

1. Lass den vollständigen Gebäude-Prompt mit den nötigen Blender-/UE5-Regeln
   vorab zusammenführen. Die Datei ist inhaltlich fertig und benötigt keine
   automatische Verschmelzung durch die Pipeline.
2. Lege die gesamte Markdown-Datei unter `prompts/` ab, z. B.
   `prompts/creole_bakery_01.md`. Du kannst dazu im GitHub-Webinterface
   in den Ordner `prompts/` wechseln und **Add file → Create new file**
   benutzen, oder eine fertige `.md`-Datei hochladen.
3. Öffne [GitHub Actions](https://github.com/turbidtunes/bastlerkiste-start/actions)
   → **Claude Blender Gebaeude automatisch bauen** → **Run workflow**.
   Wähle den Branch `main`.
4. Gib die Eingaben an:

   | Feld | Beispiel |
   |---|---|
   | `building_name` | `creole_bakery_01` |
   | `prompt_path` | `prompts/creole_bakery_01.md` |
   | `reference_images` | `references/bakery_front.png` |
   | `model` | `claude-sonnet-5-5` |
   | `review_fixes` | `1` |

   Referenzbilder können in `references/` oder `referenzbilder/`
   liegen. Mehrere Pfade mit Kommas trennen. Ohne Bild das Feld leer lassen.

## Bereits vorhandener Kirchenauftrag

Die fertige Kirche liegt unter
`prompts/grand_fond_parish_church.md`. Diese Datei enthält **beides**:
die konkreten Kirchen- und Grundstücksvorgaben **sowie** die umfassenden
Blender-/UE5-Systemregeln.

- `building_name`: `grand_fond_parish_church`
- `prompt_path`: `prompts/grand_fond_parish_church.md`
- `reference_images`: `references/ref_grand_fond_H04_g_church_creole.png`

Die Kirche umfasst ein 30 × 42 m großes Grundstück und einen maximalen
Footprint von 27 × 36 m. Die tatsächlichen Kirchenmaße ermittelt Claude
im Architekturplan anhand des übergebenen Referenzbildes.

## Der Ablauf: 1/5 bis 5/5, ohne Go

- **1/5 PLAN:** Gründliche Architekturplanung unmittelbar aus der
  vollständigen Prompt-Datei und den tatsächlichen Referenzbildern.
- **2/5 SHELL:** Fundamente, Rohbau, Außen-/Innenwände.
- **3/5 ARCHITECTURE:** Dächer, Türen, Fenster, Treppen und Sonderbauteile.
- **4/5 DETAILS:** Details, UVs, Materialslots und Möbel-Placeholder.
- **5/5 EXPORT:** Qualität prüfen, GLB exportieren und reimportieren.

Nach jeder Modellierstufe werden die echten Blender-Kontrollansichten
geprüft und optional korrigiert. Erfolgreiche Lieferungen landen unter
`inbox/<building_name>/`.

**Kein 0/6-Compiler, keine doppelte automatische Einbindung
von `prompts/master_system.md`.** Der fertig zusammengeführte Prompt
bleibt unverändert und wird den Bauphasen als Kontext übergeben.

Eine zusätzliche Vorprüfung kontrolliert den Prompt-Pfad und den Dateiinhalt
**vor** der Blender-Installation und dem kostenpflichtigen API-Aufruf.

## Technische Grenzen

Es gibt keine eigene Gesamt-Tokenobergrenze oder Dollar-Softgrenze.
Technische Grenzen der Anthropic-API und von GitHub gelten weiterhin.
Fehlende Fototexturen dürfen nicht durch synthetische Bilder ersetzt werden.
Die Prompt-Datei und QA-Berichte erscheinen bei Bedarf in den
Diagnose-Artefakten, nicht im fertigen `inbox/`-Ordner.

Nur **neu gestartete** GitHub-Actions-Läufe auf `main` verwenden die
aktuelle Pipeline. Ein alter Re-run kann weiterhin auf altem Code beruhen.
