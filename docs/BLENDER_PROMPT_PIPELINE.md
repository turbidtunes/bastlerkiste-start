# Claude Blender AutoBuild – fertige Markdown-Prompts aus dem Repository

Die Pipeline erwartet eine **bereits fertig zusammengeführte Markdown-Datei**
im Verzeichnis `prompts/` des GitHub-Repositories
`turbidtunes/bastlerkiste-start`. Es gibt **keinen Prompt-Compiler** und
**kein langes Texteingabefeld** im GitHub-Actions-Startformular.

## Direkt mit einem ursprünglichen Gebäude-Prompt bauen (Standard)

Ein bisheriger, vollständiger Gebäude-Prompt kann **unverändert** als
`.md` unter `prompts/` liegen. Es muss kein Codex-Prompt-Compiler, keine
separate Plan-Texturphase und kein Bildgenerierungsauftrag laufen.
Starte GitHub Actions mit `run_mode=build` (Standard), `resume_run_id` leer,
dem richtigen Referenzbild und `review_fixes=2`. Nach der Modellierung
wird die GLB bei bestandener geometrischer Validierung samt `note.txt`
nach `inbox/<building_name>/` geliefert, **auch wenn einzelne
`new_*.png` fehlen**. Die Dateien können später neben der GLB ergänzt
werden, ohne das Gebäude neu modellieren zu lassen.

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
   | `review_fixes` | `2` (Standard, maximal zwei Korrekturrunden) |

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
Fehlende `new_*.png`-Fototexturen sind **kein Abbruchgrund mehr**: Der GLB-Export
und die Validierung laufen normal; unvollständige Fototexturen werden
in `note.txt` namentlich als offene Aufgaben vermerkt. Es findet beim
regulären `run_mode=build` **kein Bildinhalt-/Auflösungs-/Nahtlosigkeitscheck**
statt. Vorhandene PNGs bleiben im Gebäudeordner erhalten. Künstliche
oder prozedurale Ersatz-Fototexturen werden weiterhin nicht erzeugt.
Die Prompt-Datei und QA-Berichte erscheinen bei Bedarf in den
Diagnose-Artefakten, nicht im fertigen `inbox/`-Ordner.

Nur **neu gestartete** GitHub-Actions-Läufe auf `main` verwenden die
aktuelle Pipeline. Ein alter Re-run kann weiterhin auf altem Code beruhen.

## Wiederverwendbare Blender-Bauteile (neu)

Die Pipeline besitzt jetzt unter `scripts/blender_lib/` eine getestete
Gebäude-API `building_kit.py`, basierend auf wiederverwendbaren Modulen
des Repositories `turbidtunes/bastlerkiste`.

Die API stellt Funktionen für geschlossene Boxen/Platten, Wände mit echten
Öffnungen, Trennwände, separate Türblätter mit Scharnier-Origin,
Fensterrahmen/Glas, normgerechte Geradeaus-Treppen, Satteldachplatten und
`Ph_*`-Möbelboxen bereit. Für ungewöhnliche Architektur verwendet Claude
weiterhin individuelle Blender-Geometrie. Materialnamen, UV0 und Export
liegen unter Kontrolle des aktuellen Workers. Ein vollständiger Funktions-
Smoke-Test führt einen echten GLB-Export/Reimport vor jedem kostenpflichtigen
Run durch.

Die exakte Import- und Funktionsbeschreibung steht in
`scripts/blender_lib/API.md`. Historische Generatoren aus bastlerkiste
liegen unter `scripts/blender_lib/legacy/` bzw. als Studienvorlagen in
`scripts/blender_lib/examples/`. Letztere **nicht** als komplette Gebäude
direkt ausführen: ihre Material-/Exportkonventionen sind älter.

## Eine unterbrochene Modellierung fortsetzen (neu)

Neue Läufe sichern jetzt nach jeder fertig geprüften Blender-Stufe
`stage_checkpoints.json`, die jeweilige `.blend`, erzeugten Stufencode,
den vollständigen Plan, QA-Ansichten sowie einen SHA256-Fingerprint des
Eingabeprompts und aller übergebenen Referenzbilder.

Diese Dateien werden **auch bei einem Fehler** als GitHub-Actions-Artefakt
mit der Bezeichnung `diagnose-<building_name>-<laufnummer>` hochgeladen.
Sie sind derzeit 7 Tage verfügbar.

Um bei einem späteren Fehler kostensparend fortzufahren:

1. In GitHub Actions die **Run-ID** des fehlgeschlagenen Laufs aus seiner URL
   kopieren, z. B. aus `.../actions/runs/123456789` den Wert `123456789`.
2. Unter **Run workflow** auf `main` ein neues Mal starten. Derselbe
   `building_name`, `prompt_path` und dieselben `reference_images`
   sind erforderlich.
3. Die alte Run-ID in das neue optionale Feld `resume_run_id` eintragen.
4. GitHub lädt das frühere Diagnose-Artefakt automatisch, **bevor** Claude
   aufgerufen wird. Der Agent prüft die Originaleingaben und überspringt
   vorhandene gültige Planungs- und Blender-Checkpoints. Bei einer bereits
   vollständigen `details`-Stufe beginnt er direkt beim GLB-Export.

Ist das Artefakt verschwunden, fehlen die Checkpoints oder hat sich
der Eingabeprompt/das Referenzbild verändert, bricht die Fortsetzung ab,
**ohne erneut API-Tokens für den Bau zu verbrauchen**.

**Grenze:** Die Läufe **vor** Einführung der Checkpoint-Funktion haben
weder `stage_checkpoints.json` noch gespeicherte `.blend`-Artefakte.
Für sie ist dieser neue Resume-Pfad leider nicht rückwirkend verwendbar.

## Kostenloser Bibliothekstest

Das separate GitHub-Workflow
`Blender-Bauteilbibliothek kostenlos pruefen` prüft ohne
`ANTHROPIC_API_KEY` und ohne Claude-API-Kosten die Blender-Bibliothek
inklusive tatsächlichem GLB-Roundtrip. Ausführung über GitHub Actions.

## Optional: Codex mit ChatGPT Plus – Planung → Fototexturen → Gebäude

Dieser mehrstufige Ablauf ist optional. Er ist **nicht nötig**, um
einen vorhandenen Originalprompt erfolgreich als GLB zu liefern.

Codex liest automatisch die Anweisung in
[AGENTS.md](../AGENTS.md), wenn du ihm einen neuen Gebäudeauftrag gibst.
Die ausführliche Einmal-Anweisung steht dort einschließlich der
`gh workflow run`-Befehle.

1. Codex erstellt unter `prompts/<building_name>.md` den vollständigen
   Einzelprompt, findet das echte Referenzbild und committet den Prompt.
2. Codex startet die GitHub Action mit **`run_mode=plan_textures`**.
   Claude erstellt eine einzige kompakte Bauspezifikation, aber **noch
   keine** kostenpflichtigen Blender-Stufenskripte.
3. Die Action committed
   `texture_requests/<building_name>/plan.md`,
   `manifest.json` und `CODEX_TASK.md` nach GitHub. Das Manifest enthält
   nur die tatsächlich fehlenden `new_*`-Fototexturen. Die Plan-Diagnose
   wird 7 Tage als GitHub-Actions-Artefakt aufbewahrt.
4. **Codex (ChatGPT Plus) erzeugt die Bilder**, soweit seine konkrete
   Codex-Sitzung Bildgenerierung unterstützt. Die Dateien müssen exakt
   `1254 × 1254` Pixel groß sein, als PNG echte fotorealistische,
   nahtlose Materialkacheln ergeben und die visuelle 3×3-Kontrolle
   bestehen. Kein Upscaling, keine prozeduralen Pseudotexturen.
5. Neue Texturen werden **NICHT** in einem globalen Ordner gespeichert,
   sondern **direkt neben die endgültige GLB**:

   `inbox/<building_name>/new_<what>.png`

   Beispiel: `inbox/les_calanques_finca/new_finca_plaster.png`.
   Diese PNGs werden vor dem Modell-Build von Codex committed und vom
   Blender-Agent ausdrücklich **nicht mehr gelöscht**.
6. Codex kontrolliert mit
   `python3 scripts/texture_handoff.py verify --repo . --slug <building_name>`
   PNG-Dateinamen, Dateiformat und 1254×1254-Auflösung. Das Prüfen der
   echten optischen Nahtlosigkeit bleibt eine zusätzliche visuelle Aufgabe.
7. Danach optional neuer **`run_mode=build`**-Lauf mit derselben Referenz und
   **`resume_run_id` = ID des abgeschlossenen plan_textures-Laufs**.
   Die Pipeline lädt den Originalplan und spart eine zweite Planungsrechnung;
   **fehlende Bilder sperren den Build nicht mehr**. Es folgen wie bisher
   standardmäßig **2** visuelle Korrekturrunden pro Stufe.
   Am Ende liegen `<building_name>.glb`, `note.txt` und alle für das
   konkrete Gebäude verwendeten `new_*.png` zusammen im selben
   `inbox/<building_name>/`-Ordner.

**Wichtige Grenze:** GitHub Actions kann nicht automatisch Codex über
dein Plus-Abo aufrufen. Ein aktiver Codex-Task kann die GitHub-Action
verfolgen und den nächsten Schritt ausführen, sofern er Zugriff auf
GitHub Actions, Bildgenerierung und Git-Push hat. Andernfalls ist die
`CODEX_TASK.md`-Datei die Übergabe zur nächsten Codex-Sitzung.
Es wird **keine kostenpflichtige OpenAI-Bilderzeugungs-API** stillschweigend
verwendet. Die Claude-Actions-Aufrufe werden weiterhin über dein
Anthropic-API-Guthaben abgerechnet.
