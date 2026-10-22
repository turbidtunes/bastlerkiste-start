# CODEX-TEXTURAUFTRAG V4 – Gesamtes fertiges Gebäude-Inventar inkl. BEIDER Kirchen

**Stand: 22. Oktober 2026.** Bezieht sich ausschließlich auf `turbidtunes/bastlerkiste-start` und vorhandene Gebäude-Assets. Dies ist der **verbindliche Nachfolger von V2, V3 und `texture_requests/CODEX_GENERATE_MISSING_IMAGES.md`**. NICHT alte Queues zusätzlich ausführen, sonst entstehen Dubletten oder falsch benannte Verzeichnisse.

## ZUERST LESEN: Datenquelle und Reihenfolge

**`briefs/missing_inbox_textures_2026-10-22_v4_ALL.json`**

Lies die gesamte JSON inklusive `jobs` **und** `reuse_jobs`. Die maschinenlesbare Liste ist verbindlich; diese MD dient als Ablaufanleitung. Sie enthält die vollständigen Einzelprompts und **exakt geprüften GitHub-Zielpfade in originaler Groß-/Kleinschreibung**, nicht die teilweise falschen Aliasnamen der V3.

**Inventur auf `main`: 48 Gebäude-GLBs; 46 fehlende `new_*.png` in 21 Ordnern.** Die alte V3 hatte nur 22 Einträge; die neue V4 ergänzt 24 zuvor ausgelassene und korrigiert alle Alias-Ziele. Prüfumfang sind die zum Inventurzeitpunkt vorhandenen `inbox/*/*.glb` plus die explizit referenzierte alternative Kirchenfassung.

## Beide Grand-Fond-H04-Kirchen sind EIGENSTÄNDIG enthalten

**Variante A – Kirche auf `main` (in der Gesamtmenge der 46 fehlenden Bilder enthalten)**

- Branch: `main`
- GLB: `inbox/fond_h04/fond_h04.glb` (bei Prüfung **6.896.988 Bytes**)
- Fehlende Oberflächen: `inbox/fond_h04/new_roof_corrugated_red.png` (**2 × 2 m**) und `inbox/fond_h04/new_stained_glass.png` (**1 × 1 m**).
- `new_stained_glass` ist ein **ausdrücklich angefordertes mehrfarbiges Glas-/Bleiverglasungsmuster**, keine einfache Putz- oder Metalltextur. Für diesen Job den speziellen `kind` und individuellen `prompt` aus der JSON befolgen. Die Farben/Glasstruktur fotografisch glaubwürdig, das Muster randlos kachelbar; **nicht durch beliebiges Weißglas ersetzen**.

**Variante B – Codex-Kirche auf anderem Branch (5 vorhandene Texturen ÜBERNEHMEN, nicht neu generieren)**

- Branch: `finish/fond-h04-codex`
- GLB: `inbox/grand_fond_parish_church_codex/grand_fond_parish_church_codex.glb` (bei Prüfung **21.872.712 Bytes**).
- Exakte fünf `new_*`-Materialien: `new_clock_enamel_ivory`, `new_limestone_pale_aged`, `new_lookout_waterproofing`, `new_roof_metal_oxblood`, `new_zinc_dome_aged`.
- Für jedes Material **existiert bereits** eine Quelle auf demselben Branch unter `rescue/grand_fond_H04/inbox/grand_fond_parish_church/<material>.png`.
- Erster Arbeitsschritt: Führe die fünf `reuse_jobs` aus. Bei korrektem PNG und fachlich passendem Material **unverändert Byte für Byte** nach `inbox/grand_fond_parish_church_codex/<material>.png` in **diesem anderen Branch** kopieren; keine neue Bildgenerierung und kein Upscaling. Bei identischem Ziel vorher überspringen.
- Die neuen PNGs **nicht** stattdessen nur auf `main` ablegen: Die zweite GLB liegt nicht dort. `main` und `finish/fond-h04-codex` niemals blind miteinander mergen.

**Zur Größenangabe:** Für die zweite Kirchenfassung wurden in diesem Audit 21,9 MB verifiziert, nicht 29 MB. Eine möglicherweise weitere 29-MB-Datei ist anhand der aktuell erreichbaren exakten Branch-Pfade **nicht** identifiziert; verwende vor einer Bearbeitung ihre echte Referenz und vermische keine unterschiedlichen GLBs. Beide hier konkret identifizierten Fassungen sind berücksichtigt.

## Ausführungsregeln: 2 Branches, kein Verschieben von Gebäude-Assets

1. **Zuerst `reuse_jobs`**: pro Job `branch`, `source_image` und `destination` exakt befolgen. Das sind vorhandene Bilder, **keine** Neugenerierungen. Vor Übernahme tatsächliche Bilddaten prüfen und nach Übernahme PNG wieder öffnen. Je erfolgreich validiertes Bild committen und in `finish/fond-h04-codex` pushen.
2. Danach alle `jobs` sortiert nach `order` und **ein PNG nach dem anderen** auf `main` erzeugen. `job.prompt` ist der verbindliche motivspezifische Prompt; `job.destination` ist der exakte Zielpfad. Ein neues PNG neben die jeweilige GLB und `note.txt`.
3. Vor **jedem** Job Repository/Branch und `job.destination` aktuell prüfen. Existiert die Datei dort inzwischen, **überspringen und nichts überschreiben**. `existing_same_named_png_elsewhere` listet nur mögliche Wiederverwendungsquellen: Nicht allein aufgrund gleichen Namens kopieren; Motiv, Maßstab, native Pixel und Lizenz/Quelle verifizieren.
4. **Native 1254 × 1254 Pixel**, echtes PNG. Diese V4 übernimmt die zuletzt ausdrücklich festgelegte V3-Auflösung. **Kein Upscaling und kein Resampling**, keine bloße 2048-/1024-Datei mit nachträglich angepasster Größe. Bei fehlender nativer Erzeugungsmöglichkeit `blocked_native_resolution` melden; nicht fälschen.
5. Nur tatsächliche Bildgenerierung über die in Codex verfügbaren ChatGPT-Plus-Bildfähigkeiten, falls vorhanden. Keine kostenpflichtige externe OpenAI-, Anthropic- oder Drittanbieter-Bild-API ohne ausdrückliche Erlaubnis. **Nie** Rauschgeneratoren, Blender-Shader, synthetische Farbflächen, Pillow-Prozeduralmuster oder Renderings als fotografische Textur tarnen.
6. Fotorealistische nahtlose Materialaufnahme: Kamera exakt senkrecht, homogenes diffuses Licht, saubere natürliche Mikroskopie, matte Oberfläche, keine Perspektive, Schlagschatten, Schrift oder Logos. Keine Spiegelhälften, Ghosting, Crossfade-Seams, Weichzeichner-Ränder oder künstliche Muster. Materialgrößen `physical_tile_size_m` befolgen; bei `null` nicht so tun, als sei das Maß belegt.
7. Bei Schindel-, Wellblech-, Bretter-, Türen-, Sockel- und Betonlochstein-Materialien **nur Oberfläche** fotografieren. Kanten, Profile, Schindelumrisse, Lochsteinlöcher und Bauteilgrenzen gehören zur Geometrie. Einzige ausdrücklich künstlerisch strukturierte Ausnahme ist das Buntglas-Material der Hauptkirche. Für alle Materialien den individuellen Prompt lesen.
8. Vor Commit Format und native Auflösung technisch prüfen, danach eine 3×3-Kachelung mit **wirklichem Bildmaterial** auf Übergänge und auffällige Wiederholungen kontrollieren. Ein unpassendes Bild nicht commiten. Validierte Bilder einzeln nach `job.destination` einchecken; keine bereits existierenden PNGs überschreiben.
9. Niemals vorhandene `.glb`, `note.txt`, Referenzen, Architektur-Prompts, Branches, Workflows oder `new_*.png` ändern/löschen/umbenennen. Standard-MATERIAL-LIST, `glass`, `lamp_glass`, `placeholder`, `sign_*` und `poster_*` **nicht** neu bebildern. Keine Gebäude-, Blender- oder Claude-Build-Actions starten.
10. Nach je fünf abgeschlossenen Bildern oder bei einem echten Hindernis knapp berichten, inklusive Branch, Pfad und Status. Fertig erst, wenn **46 `jobs`** erledigt/vorgefunden/konkret blockiert dokumentiert sind **und 5 `reuse_jobs`** der zweiten Kirche ebenfalls geprüft/übernommen/konkret blockiert wurden. Angaben in der Inventur ersetzen **keine** spätere tatsächliche Pixelprüfung.

## Fehlende PNGs auf `main` – vollständige 21-Ordner-Liste

| Tatsächlicher bestehender Gebäudeordner | Fehlend | Exakte Namen |
|---|---:|---|
| `inbox/calanques_h07/` | 1 | `new_plaster_ochre_mallorca.png` |
| `inbox/cite_rhumerie_H01/` | 3 | `new_plaster_ochre_yellow.png`, `new_plaster_oxblood_brown.png`, `new_timber_dark_stained.png` |
| `inbox/filaos_H01/` | 1 | `new_railing_steel_blue.png` |
| `inbox/fond_h04/` | 2 | `new_roof_corrugated_red.png`, `new_stained_glass.png` |
| `inbox/fond_h08/` | 1 | `new_roof_shingle_wood_weathered.png` |
| `inbox/grand_fond_H06/` | 1 | `new_castiron_green_worn.png` |
| `inbox/grand_fond_H16/` | 3 | `new_floorboards_pine.png`, `new_render_pink_weathered.png`, `new_weatherboard_pink.png` |
| `inbox/la_pointe_H01/` | 1 | `new_timber_black_paint.png` |
| `inbox/le_souffleur_H03/` | 1 | `new_plaster_pink_weathered.png` |
| `inbox/le_souffleur_H06/` | 2 | `new_plaster_ochre_peeling.png`, `new_timber_teal_peeling.png` |
| `inbox/les_calanques_H09/` | 1 | `new_door_oak_aged.png` |
| `inbox/mare_joncs_h01/` | 5 | `new_plaster_pink_weathered.png`, `new_plaster_rose_dark.png`, `new_shade_net_black.png`, `new_tank_plastic_black.png`, `new_tank_plastic_green.png` |
| `inbox/paletuviers_h01/` | 3 | `new_floor_planks_worn.png`, `new_roof_sheet_verdigris.png`, `new_weatherboard_green.png` |
| `inbox/riviere_noire_H03/` | 2 | `new_door_blue_peeling.png`, `new_tarp_green.png` |
| `inbox/riviere_noire_H04/` | 1 | `new_roof_corrugated_red.png` |
| `inbox/riviere_noire_H05/` | 4 | `new_buoy_paint_peeled.png`, `new_plaster_blue_peeled.png`, `new_rattan_woven.png`, `new_rope_hemp.png` |
| `inbox/riviere_noire_H06/` | 2 | `new_paint_red_oxide_peeling.png`, `new_plaster_sage_green_weathered.png` |
| `inbox/sarcelle_h06/` | 1 | `new_render_yellow_peeling.png` |
| `inbox/sarcelle_h07/` | 2 | `new_paint_teal_weathered.png`, `new_paint_yellow_worn.png` |
| `inbox/sarcelle_h08/` | 4 | `new_enamel_green_cross.png`, `new_paint_blue_signwriting.png`, `new_plaster_teal_faded.png`, `new_tile_plinth_teal.png` |
| `inbox/sarcelle_h12/` | 5 | `new_corrugated_blue_rusty.png`, `new_paint_blue_plinth_band.png`, `new_paint_teal_worn.png`, `new_plaster_orange_weathered.png`, `new_screen_block_concrete.png` |

## Verbindliche Abschlusskontrolle

- Auf `main` keine neuen Zielordner anlegen, die nur aus einer verkürzten V3-Aliasbezeichnung bestehen: insbesondere `fond_h16` ≠ `grand_fond_H16`, `rhumerie_h01` ≠ `cite_rhumerie_H01`, `calanques_h09` ≠ `les_calanques_H09`.
- In der Codex-Kirchenvariante auf `finish/fond-h04-codex` prüfen, dass alle **fünf** Bilddateien **direkt neben** `grand_fond_parish_church_codex.glb` liegen; die gesicherten alten Quellen beibehalten.
- Am Ende Anzahl erzeugt/wiederverwendet/vorgefunden/blockiert getrennt nach Branch nennen. Keine neu generierten Bilder, GLBs oder ein bestandenes Sicht-QA behaupten, die nicht tatsächlich überprüft wurden.

**Nur dieser Texturenauftrag; keine Bauwerksgeneration.**
