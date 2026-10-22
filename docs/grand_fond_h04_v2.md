# Grand-Fond H04 – neuer Kirchen-Workflow V2

**Zweck:** Vollständige **Neugenerierung** der katholischen Pfarrkirche im Slot `grand_fond_H04`, keine Rekonstruktion einer früheren Codex-Sitzung. Der bisherige allgemeine Workflow wird **nicht** verändert.

## Ausführung

GitHub → `turbidtunes/bastlerkiste-start` → **Actions** → **Kirche H04 - Neubau (5 USD)** → **Run workflow** auf `main`.

1. Zunächst optional `preflight_only=true` auswählen und kostenlos überprüfen, ob Python, Blender 4.x und die Building-Kit-Bibliothek starten. Dieser Test verwendet **keine Claude API**.
2. Zum eigentlichen Bau `preflight_only=false` wählen. Es steht ausschließlich `claude-sonnet-5-5` zur Verfügung, um das Restbudget nicht durch ein versehentlich teureres Modell zu gefährden.
3. `max_estimated_usd=5.00` ist die Voreinstellung; **hartes Limit der Agent-Konfiguration ist 5.30 USD**, mit 0.70 USD Reserve zu deinem verbleibenden Guthaben von 6 USD. Vor jedem generierenden API-Aufruf zählt der Agent kostenlos die Eingabetokens und reserviert den maximal möglichen Ausgabetokenverbrauch mit 10 % Sicherheitsaufschlag. Dieses Limit ist eine vorsichtige Kostenschätzung auf Basis der veröffentlichten Sonnet-Preise, keine Garantie der tatsächlichen API-Abrechnung. Anthropic-Guthaben muss auf der passenden API-Organisation liegen.
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

Um den Workflow im GitHub-Mobile-Browser zu finden: zuerst im Repository **Actions** öffnen, auf **Kirche H04 - Neubau (5 USD)** tippen und dann **Run workflow** wählen. Bei fehlendem Button gegebenenfalls die Desktop-Ansicht des Browsers aktivieren. Die Datei wurde zunächst wegen eines YAML-Fehlers nicht korrekt geladen; dieser Fehler ist korrigiert und ein kostenloser Aktivierungslauf registriert den Namen. Direkter Link: https://github.com/turbidtunes/bastlerkiste-start/actions/workflows/build-grand-fond-h04-v2.yml .

Der technische GLB-Reimport ist keine vollständige physikalische UE5-Begehbarkeitsprüfung. Auch eine automatisierte Sichtkontrolle kann einen Referenzfehler übersehen. Ein erfolgreicher Workflow garantiert deshalb nicht, dass jede Fensteröffnung, jeder Türschwenk und jede Turmstufe den Anforderungen entspricht. Die Pipeline reduziert die häufigsten Ursachen für Komplettabbrüche, kann die Erfolgswahrscheinlichkeit aber nicht quantifizieren.

**Kostenkontrolle:** Der Workflow startet ausschließlich über `workflow_dispatch`. Das Anlegen/Aktualisieren der Workflow-Dateien startet keinen kostenpflichtigen Bau.
