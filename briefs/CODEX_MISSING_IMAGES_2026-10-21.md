# CODEX-AUFTRAG – fehlende Bildassets in zwei GitHub-Repositories

**Nutzerauftrag:** Erstelle die noch fehlenden Bilder EINZELN aus der geprüften JSON-Arbeitsliste und speichere jedes an seinem tatsächlichen Zielpfad in genau dem angegebenen Repository. Bilder nicht gesammelt als Galerie oder ZIP produzieren. Dieser Auftrag hat Vorrang vor generischen Lieferbeispielen in AGENTS.md.

## Start und verbindliche Quelle

- Verbundenes Arbeitsrepo: `turbidtunes/bastlerkiste-start`, Branch `main`.
- Zusätzliches privates Repo: `turbidtunes/bastlerkiste`, Branch `main`.
- Lies vollständig: **`briefs/missing_images_codex_2026-10-21.json`**.
- Die JSON enthält **32 noch zu bearbeitende/zu vergleichende Motive mit 33 Datei-Zielen**, davon 20 alte Aufgaben im großen Repo und 12 neue Gebäude-Motive für 13 Zieldateien im kleinen Repo.
- Neun vorhandene HUD-Symbole sind unter **`existing_aliases_to_skip`** als andere produktive Dateinamen dokumentiert. **Nicht erneut erzeugen**, nicht umbenennen und keine zweite Kopie als vermeintlich neue Datei abliefern.
- Drei Bildschirmkarten haben verwandte vorhandene `T_Card_*`-Varianten. **Vor einer Neugenerierung** die tatsächlichen Inhalte und Einsatzzwecke visuell vergleichen. Nur wenn die alte Datei nicht die Bildanforderung erfüllt, die neue Datei mit dem im JSON angegebenen Pfad anlegen.

## Unbedingt Namen und Repositories auseinanderhalten

Der String `Input` ist **kein gefundenes Verzeichnis**. Gemeint sind die vorhandenen `inbox/`-Ablagen. Es existieren zwei Repositories:

1. `turbidtunes/bastlerkiste` – die große Spielwelt; z. B. `map/textures/gpt/int_veneer.png` oder `game/hud/images/loading_evacuation.png`.
2. `turbidtunes/bastlerkiste-start` – die GLB-Eingänge; z. B. `inbox/grand_fond_h07/new_paint_green_timber.png`.

Für **jeden** Job ausschließlich `job.destinations[].repository` und `job.destinations[].path` als Lieferadresse verwenden. **Nicht** aus einem Gebäudenamen in `note.txt`, dem Prompttitel, alten `T_Icon_*`-Abkürzungen oder `id` einen Zielpfad erraten.

Beispiel: `new_roof_corrugated_red.png` wird **einmal** generiert, aber **zweimal** identisch abgelegt:
- `turbidtunes/bastlerkiste-start/inbox/bel_air_h01/new_roof_corrugated_red.png`
- `turbidtunes/bastlerkiste-start/inbox/cite_moulin_h04/new_roof_corrugated_red.png`

**Nie bestehende Bilder, GLB-Dateien, Bauprompts, Original-PNGs, Source-Skripte oder GitHub-Workflows automatisch umbenennen oder überschreiben.**

## Schleife – ein einziges Bild zurzeit

Arbeite `jobs` in aufsteigender Reihenfolge `order` ab und nimm jeweils nur den nächsten noch offenen Eintrag.

1. Aktuelle `main`-Branches und alle `destinations` dieses Jobs prüfen. Bereits existierende Dateien **nicht überschreiben**; mit Alternativnamen/alias separat vermerken.
2. Bei `state=compare_existing_first`: vorhandene `related_existing_asset` wirklich ansehen; wenn inhaltlich brauchbar, **ohne neue Datei** als `covered_by_existing_asset` mit genauem Alias notieren. Sonst die neue Datei aus dem Originalprompt generieren.
3. Den `prompt` **inhaltlich exakt beachten**; die `group_instruction` für Kategorie/Fotoqualität und `target_resolution_px` für das Ziel verwenden. Kein prompt drift, keine Zusatzgegenstände, kein neuer Dateiname, keine abstrakte pseudo-prozedurale Fototextur.
4. Benutze **nur die tatsächlich vorhandene Bildgenerierung innerhalb dieser Codex-/ChatGPT-Plus-Sitzung**. Falls sie nicht verfügbar ist: mit klarer Meldung anhalten, niemals heimlich OpenAI-/Anthropic-/Drittanbieter-API-Kosten auslösen. Keine selbst erzeugten Blender-/PIL-/Noise-/Shader-Bilder als Ersatz für echte Fototexturen. PIL darf zum Prüfen, nicht zur Bildsynthese verwendet werden.
5. **Kein Upscaling**. Native Ausgabeauflösung prüfen; falls ein zwingendes Zielformat nativ nicht angeboten wird, einen Konflikt dokumentieren und um Erlaubnis zur Abweichung bitten, statt die Pixelzahl mittels Resampling künstlich zu erhöhen. Kein Stretching, kein verzerrendes Cropping; Motiv vollständig erhalten.
6. Bei `kind=seamless_tile`: 2×2 und 3×3 Wiederholungen **nur als temporäres Prüfbild** analysieren; exakt passende gegenüberliegende Kanten, keine sichtbaren Kreuze, Crossfade-Streifen, Ghosting, gespiegelte Hälften, gemalte Glättung, künstliche Strukturen oder eingebrannte Schatten. Korrektur durch echte Neugenerierung, nicht durch Verfahren, die eine gefälschte Fototextur ergeben.
7. Bei `emblem`, `printed_flag`, `cinematic_image` gelten die Originalvorgaben des JSON, insbesondere Transparenz, Form, fiktive Hoheitszeichen sowie keine echten Marken. Sie werden **nicht** fälschlich als nahtlose Materialkacheln behandelt.
8. Echte, validierte PNG-Datei exakt in **jedem** Ziel-Repository und Pfad committen. Bei einem Motiv mit zwei Zielpfaden nur ein Bild generieren und identische Bytes unter beiden Zielnamen speichern. Git `add` auf genau diese Pfade begrenzen.
9. Nach erfolgreichem Push in `bastlerkiste-start` die JSON-Arbeitsliste aktualisieren: pro Job `state=completed` (oder `covered_by_existing_asset`), `completed_destinations`, optional echte Commit-SHAs und `actual_native_resolution_px` eintragen. Die nächste Aufgabe muss mit diesem Zustand fortsetzbar sein. Beim nächsten Schritt zuerst wieder `git pull` ausführen.
10. Weiter zum nächsten Bild; **nicht** alle Bilder auf einmal an ein Modell senden. Bei Abbruch den letzten sauber gesicherten Job und den nächsten offenen Job melden. Bereits erzeugte Assets niemals blind regenerieren.

## Große Repo-Größe / Tokenbudget

Das große Repository `turbidtunes/bastlerkiste` ist umfangreich: **kein vollständiger Checkout sämtlicher Bild-/Binärdateien nötig.** Wenn Codex dort schreiben darf, verwende einen sicheren Sparse-Checkout mit gefiltertem Blob-Download oder die vorhandene GitHub-API für gezielte Datei-Lese-/Schreibvorgänge. Falls die zweite Repo-Verbindung fehlt, **keine Dateizieländerung** als Notlösung; melde die fehlende Berechtigung. Erzeuge auch keine ungesicherten lokalen Bilder als angeblich committed.

**Statusmeldungen sehr sparsam:** keine fortlaufenden Kommentare zu Toolbefehlen, Logs und normalen Zwischenschritten. Nur nach sinnvollen Meilensteinen (z. B. jeweils fünf Bilder), bei Blockern oder am Ende kurz berichten. GitHub-Actions-Blender-/Claude-Workflows **nicht starten** – es geht ausschließlich um Bilddateien.

## Abschlussbericht

Melde in einem knappen Überblick:
- Zahl erstellter **einzigartiger** Bilder und Zahl tatsächlich committed Zieldateien.
- Zahl durch bereits vorhandene Aliasdateien erfüllter Aufträge (inkl. der neun HUD-Icons).
- Noch offene/technisch blockierte Motive (mit `job.id`, Pfad und konkretem Grund).
- Links auf Commits/Zielordner beider Repositories.
- **Keine Behauptung, dass ein Bild erstellt wurde, wenn nur ein Prompt erzeugt oder eine Datei anders benannt wurde.**

**Beginne mit dem ersten Job der JSON-Datei. Arbeite ohne weitere Rückfragen, sofern die benötigten Tools/Berechtigungen tatsächlich vorhanden und alle Vorgaben erfüllbar sind.**
