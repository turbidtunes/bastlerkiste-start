# Universelle Blender-Gebäude-Pipeline: Originalprompts unverändert verwenden

## Ziel

Bestehende, lange Gebäude-Prompts müssen NICHT manuell in eine neue Vorlage übertragen
oder gekürzt werden. Der Prompt-Compiler liest den ganzen Originalprompt und die
Referenzbilder, gleicht ihn mit `prompts/master_system.md` ab und schreibt einen
strukturierten Bauvertrag. Der **unveränderte Originalprompt** bleibt in den
folgenden Plan-, Modellier-, Korrektur- und Abschlussstufen zusätzlich erhalten.

Es gibt **keine Go-Pause**. Das Verfahren baut unmittelbar nach dem Plan weiter.

## Starten vom Smartphone

1. Öffne `https://github.com/turbidtunes/bastlerkiste-start/actions`.
2. Wähle `Claude Blender Gebaeude automatisch bauen` und `Run workflow`.
3. Stelle als Branch `main` ein.
4. Trage bei `building_name` eine neue eindeutige Kennung in lower_snake_case ein.
5. **Entweder** bei `brief_path` den Pfad zu deinem vollen Originalprompt,
   z. B. `briefs/spanish_villa_02.md`, **oder** bei `building_prompt` den
   ganzen Text direkt einfügen. Ein direkt eingefügter Text hat Vorrang.
6. Bei `reference_images` die vorhandenen Bildpfade durch Kommas getrennt
   eintragen, z. B. `referenzbilder/villa_front.png,referenzbilder/villa_side.png`.
   Zulässige Ordner: `references/` und `referenzbilder/`.
7. Modell und Zahl der optionalen Bildkorrekturen wählen, dann starten.

Bei sehr langen Prompts ist **eine Markdown-Datei unter `briefs/` empfohlen**:
GitHub begrenzt die Gesamtgröße aller `workflow_dispatch`-Eingaben auf
etwa 65.535 Zeichen. Die Markdown-Datei ist nicht auf dieses Formularlimit
beschränkt (es gelten weiterhin Repository- und API-Grenzen).

## Beispiele

### Kirchgebäude (bereits vorhanden)

- `building_name`: `grand_fond_parish_church`
- `brief_path`: `briefs/grand_fond_parish_church.md`
- `building_prompt`: LEER
- `reference_images`: `references/ref_grand_fond_H04_g_church_creole.png`

### Spanische Villa

- Vollständigen alten Bauprompt unverändert als
  `briefs/spanish_villa_02.md` hochladen.
- Referenzfoto unter `referenzbilder/spanish_villa_02.png` hochladen.
- `building_name`: `spanish_villa_02`
- `brief_path`: `briefs/spanish_villa_02.md`
- `building_prompt`: LEER
- `reference_images`: `referenzbilder/spanish_villa_02.png`

## Reihenfolge

1. Originalprompt laden und in `_asset_work/<name>/original_prompt.md` protokollieren.
2. Compiler ruft Claude mit dem Originalprompt und den echten Referenzbildern auf.
3. Compiler erstellt `_asset_work/<name>/compiled_contract.md`. Fehlende
   Pflichtabschnitte führen zu Reparaturversuchen und gegebenenfalls zum Abbruch.
4. Claude erstellt einen Plan; dann folgen `shell`, `architecture`, `details`,
   vier Blender-Kontrollbilder je Stufe und eventuelle Korrekturskripte.
5. Nach technischer Validierung und GLB-Reimport gehen **nur** GLB, `note.txt`
   und ggf. vorhandene echte neue Fototexturen nach `inbox/<name>/`.

Der Compiler ist **additiv**, nicht destruktiv: Seine Auslegung ersetzt den
Originalprompt nicht. Er dokumentiert Konflikte in `CONFLICT_RESOLUTIONS`.
Die Systemregeln haben Vorrang, u. a. bei „warte auf Go“ und Verbot synthetischer
Fototexturen. Unklare oder fehlende Angaben sind als Annahme zu kennzeichnen.

Die komplette Diagnose findest du bei GitHub Actions im Artefakt `diagnose-...`,
**nicht** im fertigen `inbox/`-Ordner. Das Artefakt beinhaltet auch Plan,
Prompt, Compiler-Vertrag und Kontrollrenderings, sofern erstellt.

## Qualitätsgrenzen

- Die GitHub-Syntax-, Compiler-Struktur- und Offline-Fixturetests (Kirche/Bäckerei)
  beweisen noch keine vollständige semantische Übernahme jeder Anforderung.
  Der Originalprompt bleibt daher bei jedem relevanten KI-Schritt zusätzlich sichtbar.
- Die automatische Bildkontrolle ist keine Garantie für ein professionell
  optimiertes oder vollständig UE5-kompatibles Game-Asset.
- `new_*.png` darf nicht synthetisiert werden. Falls entsprechende echte Fotos
  fehlen, blockiert die Lieferung wie bisher.
- API- und GitHub-Laufzeitgrenzen bleiben bestehen. Eine eigene Token- oder
  API-Dollarobergrenze setzt diese Pipeline derzeit nicht.
