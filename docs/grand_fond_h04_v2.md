# Grand-Fond H04 – neuer Kirchen-Workflow V2

**Zweck:** Vollständige **Neugenerierung** der katholischen Pfarrkirche im Slot `grand_fond_H04`, keine Rekonstruktion einer früheren Codex-Sitzung. Der bisherige allgemeine Workflow wird **nicht** verändert.

## Ausführung

GitHub → `turbidtunes/bastlerkiste-start` → **Actions** → **Grand-Fond H04 - Kirche neu bauen (V2)** → **Run workflow** auf `main`.

1. Zunächst optional `preflight_only=true` auswählen und kostenlos überprüfen, ob Python, Blender 4.x und die Building-Kit-Bibliothek starten. Dieser Test verwendet **keine Claude API**.
2. Zum eigentlichen Bau `preflight_only=false` wählen. Standardmodell ist `claude-sonnet-5-5`; optional `claude-opus-5-5`.
3. `max_estimated_usd=40` ist **nur eine geschätzte** Kostenbremse, keine garantierte Obergrenze der Anthropic-Abrechnung. Der Agent prüft vor jedem weiteren API-Aufruf seinen bisherigen geschätzten Verbrauch. Ein einzelner letzter Aufruf kann die Grenze überschreiten.
4. `visual_review=true` prüft die wichtigsten Phasen gegen die Referenz; bei sichtbaren Problemen erfolgt eine gezielte Zusatzphase. Das erzeugt zusätzliche API-Aufrufe.
5. `resume_run_id` beim ersten Lauf **leer lassen**. Für die Fortsetzung **dieses V2-Workflows** nach einem Fehler die GitHub-Actions-Run-ID des fehlgeschlagenen V2-Laufs eintragen. Die heruntergeladenen `.blend`-Checkpoints und der unveränderte Plan müssen vorhanden sein; nach 30 Tagen können die Artefakte ablaufen.

Es muss das bestehende Repository-Secret `ANTHROPIC_API_KEY` vorhanden sein. GitHub-Actions-Runtime und Anthropic-API-Nutzung sind unterschiedliche Kostenquellen.

## Technischer Ablauf

`scripts/church_h04_v2.py` führt folgenden Ablauf aus:

| Stufe | Inhalt |
|---|---|
| PLAN | Einmalige kompakte, koordinatenbasierte Planung aus `prompts/fond_h04.md` und `referenzbilder/ref_grand_fond_H04_g_church_creole.png` |
| shell | Fundament, Gebäudekörper, echte Wandöffnungen, Räume |
| nave_roofs | Kirchenschiff-, Seitenschiff-, Chor- und Sakristeidächer |
| tower | Turmschaft, Glockenraum, Aussichtspunkt, Abschluss |
| tower_stairs | Treppen, Zwischenpodeste, Geländer, Eingangs-/Parvisstufen |
| windows | Reale Fensterrahmen und Verglasung |
| doors | Getrennte, scharniergelagerte Türnodes |
| roof_details | Ziegel, Dachrinnen, Fallrohre und Dachanschlüsse |
| facade_details | Kapitelle, Gesimse, Fassadendetails |
| furniture_uv | Möbel-Placeholder, Materialien, UV0 |

Jede Phase erhält einen **separat generierten, ausführbaren Python-Code**. Fehlgeschlagene Phasen erhalten höchstens drei Reparaturversuche mit Originalfehler und dem vorherigen Code; frühere fertige Phasen bleiben unberührt. Lange, abgeschnittene Codeantworten werden **nicht mehr blind aneinandergehängt**. Nach jeder gelungenen Phase wird das Zwischen-`.blend` gesichert.

Wichtige Phasen werden mit Originalreferenz und vier echten Blender-Ansichten überprüft. Die numerische Stage-Prüfung verhindert Überschreitung des Polygonbudgets von 150.000 und des Grundstücksbaufensters (maximal X ±13,5 m, Y ±18 m, mit 5 cm technischer Toleranz). Am Ende erfolgen regulärer GLB-Export und GLB-Reimport mit dem bereits vorhandenen `blender_worker.py`.

## Ausgabe

Bei Erfolg schreibt der Workflow **nur**:

- `inbox/fond_h04/fond_h04.glb`
- `inbox/fond_h04/note.txt`

**Keine Texturen:** Alle Namen der erforderlichen `new_*.png`-Fototexturen werden in `note.txt` zusammen mit den Angaben aus dem Plan aufgeführt, ohne PNG-Dateien zu generieren.

Bei Erfolg und bei Fehlschlag entstehen GitHub-Actions-Artefakte mit `plan.md`, `usage.json`, Python-Code, Blender-Checkpoints, Prüfreports und Renderansichten. Retention: 30 Tage.

## Grenzen

Der technische GLB-Reimport ist keine vollständige physikalische UE5-Begehbarkeitsprüfung. Auch eine automatisierte Sichtkontrolle kann einen Referenzfehler übersehen. Ein erfolgreicher Workflow garantiert deshalb nicht, dass jede Fensteröffnung, jeder Türschwenk und jede Turmstufe den Anforderungen entspricht. Die Pipeline reduziert die häufigsten Ursachen für Komplettabbrüche, kann die Erfolgswahrscheinlichkeit aber nicht quantifizieren.

**Kostenkontrolle:** Der Workflow startet ausschließlich über `workflow_dispatch`. Das Anlegen/Aktualisieren der Workflow-Dateien startet keinen kostenpflichtigen Bau.
