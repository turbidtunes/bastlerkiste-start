# Claude Blender AutoBuild – Prompt direkt vom Smartphone starten

## Einmalige Einrichtung

Die GitHub-Actions-Pipeline ist bereits im Repository angelegt. Stelle sicher,
dass das GitHub Actions Secret `ANTHROPIC_API_KEY` gesetzt ist. Der zugehörige
Workspace muss API-Abrechnung erlauben.

## Jeden neuen Bauauftrag starten

1. Öffne https://github.com/turbidtunes/bastlerkiste-start/actions
2. Öffne **Claude Blender Gebaeude automatisch bauen** → **Run workflow**
3. Wähle den Branch **main**.
4. `building_name`: eindeutiger Name in `lower_snake_case`
   (z. B. `creole_bakery_01`).
5. `building_prompt`: **den ganzen fertig zusammengeführten Prompt**
   direkt hineinkopieren. Du kannst ihn vorher mit ChatGPT individuell
   verschmelzen lassen. Die Pipeline führt **keinen Prompt-Compiler mehr aus**
   und hängt den alten `prompts/master_system.md`-Prompt nicht erneut an.
6. `reference_images`: Bildpfade im Repository, mit Komma getrennt
   (z. B. `referenzbilder/bakery_01.png` oder `references/bakery_01.png`).
   Lass dieses Feld leer, wenn kein Bild vorhanden ist.
7. Modell auswählen und bei `review_fixes` die Anzahl erlaubter visueller
   Korrekturrunden auswählen. Mit **Run workflow** starten.

**Wichtig:** GitHub Actions begrenzt alle `workflow_dispatch`-Eingaben
zusammen auf **65.535 Zeichen**. Das ist ein Plattformlimit, kein
künstliches Claude-Tokenlimit. Wenn ein von ChatGPT zusammengeführter Prompt
größer ist, passt er nicht vollständig in dieses Actions-Formular. Bitte
nicht einfach abschneiden, sondern dafür einen anderen Eingabeweg verwenden.

Die Eingabe wird als `_asset_work/<building_name>/input_prompt.md`
im temporären Arbeitsverzeichnis protokolliert und bei der Diagnose als
Actions-Artefakt bereitgestellt (nicht als Datei in `inbox/` committed).

## Ablauf (ohne Go und ohne Compiler)

1. **1/5 PLAN:** Claude liest deinen eingegebenen Prompt und die verfügbaren
   Referenzbilder und erstellt den ausführlichen Architekturplan.
2. **2/5 SHELL:** Blender modelliert Fundament, Geschossplatten und Hauptwände.
3. **3/5 ARCHITECTURE:** Gebäudeabhängige Architektur, Dächer, Fenster, Türen.
4. **4/5 DETAILS:** Geometrie-Details, Materialnamen, UVs und Platzhalter.
5. **5/5 EXPORT:** GLB technisch prüfen, exportieren und wieder importieren.

Nach jeder der drei Bauphasen werden Blender-Kontrollrenderings erstellt;
Claude kann anhand dieser Aufnahmen Änderungen beauftragen. Nach erfolgreicher
Validierung committet der GitHub Actions Bot die endgültigen Dateien nach
`inbox/<building_name>/`.

## Was unverändert bleibt

- Kein künstliches Gesamt-Tokenlimit und keine eigene API-Dollargrenze.
  Die Anthropic-API setzt weiterhin ein technisches Limit je Anfrage; der
  Agent setzt Ausgaben beim Erreichen des Modelllimits automatisch fort.
- Keine generierten Fototexturen als Ersatz für echte Fotos.
- Fehlende erforderliche `new_*.png`-Dateien blockieren weiter die Lieferung.
- QA-Renderings, Fehlerprotokolle, Zwischenstände und ursprünglicher Prompt
  landen **nicht** in der fertigen `inbox/`-Lieferung.
- GitHub-/Anthropic-Kontingente und technische Laufzeitgrenzen bleiben gültig.

## Bestehende Workflows

Nur **neue** GitHub-Actions-Durchläufe auf dem aktualisierten Branch `main`
verwenden die direkte Prompteingabe. Ein bereits gestarteter Lauf arbeitet mit
dem Commit, von dem er gestartet wurde, und führt gegebenenfalls noch den
alten Compiler aus. Starte neue Läufe über **Run workflow**, nicht über
**Re-run failed jobs** für einen alten Durchlauf.

## Fehlerdiagnose

Wenn der Run fehlschlägt, öffne den roten Schritt unter GitHub **Actions**
und lies die letzten Logzeilen. Die Diagnose-Dateien und Kontrollbilder
liegen bei **Artifacts** des jeweiligen Durchlaufs. Bei fehlenden Blender-
Systembibliotheken beendet der Workflow den Lauf vor der kostenpflichtigen
Claude-Arbeit.
