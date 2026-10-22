> **ARCHIV / NICHT MEHR AUSFÜHREN (Stand 22.10.2026):** Der aktualisierte, branch-spezifische Gesamtauftrag steht unter [`briefs/CODEX_INBOX_TEXTURES_2026-10-22_v4_ALL.md`](../briefs/CODEX_INBOX_TEXTURES_2026-10-22_v4_ALL.md), zugehörige JSON: `briefs/missing_inbox_textures_2026-10-22_v4_ALL.json`. Darin sind beide Grand-Fond-H04-Kirchen berücksichtigt. Diese ältere Liste kann falsche Alias-Zielordner oder unvollständige Bestände enthalten.

# CODEX-AUFTRAG V2: Fehlende Gebäudefototexturen – AUSSCHLIESSLICH inbox/

## Verbindlicher Auftrag und genaue Datenquelle

Arbeite nur im Repo **`turbidtunes/bastlerkiste-start`**, auf `main`. **Keine weiteren Repositories prüfen oder bearbeiten**, insbesondere NICHT `turbidtunes/bastlerkiste`.

Lies zuerst diese **aktuelle**, maschinenlesbare Auftragsliste vollständig:

**`briefs/missing_inbox_textures_2026-10-21_v2.json`**

Dieses Dokument beauftragt **33 fehlende PNG-Zieldateien in 14 vorhandenen Gebäudeordnern**. Die Inventur basiert ausschließlich auf `inbox/<building_name>/note.txt`, den GLB-Dateien und vorhandenen `new_*.png` in `inbox/`. Die alte Liste `briefs/missing_images_codex_2026-10-21.json` bezieht weitere Repositories ein und gilt **hier nicht**.

## Ausführung: seriell, zuverlässig, verlustfrei

1. Prüfe `git status`, `main` und die angegebene neue JSON. Arbeite die `jobs` genau nach aufsteigender `order` ab, **immer nur EINEN Bildgenerierungsauftrag gleichzeitig**. Ignoriere die alte v1-Liste und jede externe Map-/HUD-Bildarbeit.
2. Vor jedem einzelnen Job: `job.destination` erneut gegen den aktuellen Git-Stand prüfen. Wenn bereits eine passende PNG-Datei existiert, **nicht überschreiben**, sondern als bereits erledigt überspringen. Die Ausgabe darf nur im angegebenen **bestehenden** Ordner `inbox/<building_name>/` liegen. Das dazugehörige `note.txt` darf zur Prüfung gelesen, aber nicht verändert werden.
3. Verwende für die eigentliche Bilderstellung die **tatsächlich verfügbare Codex-Bildgenerierungsfunktion deines ChatGPT-Plus-Zugangs**. Keine separat abrechenbare OpenAI-/Anthropic-/Drittanbieter-Bild-API verwenden. Nutze **keine Python/PIL/Blender/Shader/Noise-/Verlaufsgeneratoren**, um fotorealistische Bilder vorzutäuschen. PIL darf für Dateiprüfung und 3×3-Kachelansicht eingesetzt werden, niemals als Bildersatz.
4. Für jedes Bild den **vollständigen spezifischen `job.prompt`** der JSON verwenden, das Motiv strikt nach `surface_description_english` umsetzen. Keine erfundenen Fenster, Bretterfugen, Fliesenfugen, Dachprofile, Objektkanten oder gebackenen Schatten hineinzeichnen: Solche Details sind Baugeometrie. Keine Beschriftung, Logos, Perspektive, Vignette, Spiegelhälften, verschwommene Kreuzblende, doppelten Motiv-Geister oder rasterartigen Wiederholungsmerkmale.
5. **Genau 2048 × 2048 native Pixel, PNG. Kein Upscaling, kein Resampling** – auch nicht 1024→2048 oder 1254→2048. Wenn die in deiner konkreten Codex-Sitzung erreichbare Bildgenerierung native 2048² nicht liefern kann, **melde diese Einschränkung und stoppe die Produktion**. Nicht fälschlich erklären, die Auflösung sei eingehalten.
6. Reale Abdeckung: `job.physical_tile_m` ist der im Gebäudenotiztext tatsächlich dokumentierte Metermaßstab. Wenn `null`, ist die physische Größe in der Quelle nicht belegt; `suggested_tile_m_unverified` darf zur Motivskalierung herangezogen werden, aber **nur als Schätzung**, nicht als gesicherter Planwert gemeldet werden.
7. Vor dem Commit je Bild: Datei ist lesbares PNG, exakte native Pixelabmessung, kein verkehrter Dateiname; visuelle 3×3-Wiederholung beurteilen (die Ränder müssen nahtlos sein, nicht nur ähnliche Durchschnittsfarben haben). Schlechte Kachel komplett neu erzeugen; **keine** Mirroring-/Blurring-/Crossfade-Seam-Tricks als akzeptiertes Endergebnis deklarieren.
8. Speichere **genau an `job.destination`** und committe das einzelne erfolgreich geprüfte Bild (plus optional den von dir gepflegten Fortschrittsvermerk in `briefs/`) nach `main`. Vor dem Push aktuelle Remote-Änderungen berücksichtigen. So bleibt jede fertige Textur auch bei Unterbrechung erhalten. Du darfst eine PR nutzen, wenn die Branch-Regeln direkten Push verbieten.
9. Wenn die Bildgenerierung an einem Job scheitert: Job mit Grund melden, keine Fakedatei und keinen bereits fertigen Build zurücksetzen. Überlege nicht, den fehlenden Teil automatisch mit einem kostenpflichtigen API-Ersatz zu erzeugen.
10. Keine erneute Ausführung von `.github/workflows/build-3d-asset.yml`: Die Gebäude sind bereits als GLB vorhanden und müssen **nicht** erneut modelliert werden.

## Schutz vorhandener Arbeit

- **Niemals** GLB-Dateien, bestehende PNGs, `note.txt`, Architektur-Prompts, `AGENTS.md`, Blender-Skripte oder Actions-Workflows umbenennen, verschieben, überschreiben oder löschen.
- Wenn die GLB beim Abarbeiten anders heißt als der Ordner, trotzdem unverändert lassen. Die JSON benennt den **exakten PNG-Zielpfad**, nie aus dem Bauwerknamen ableiten.
- **Keine** Texturen für Materialien der Standard-MATERIAL-LIST, `glass`, `lamp_glass`, `placeholder`, `sign_*` oder `poster_*` erstellen. Diese stehen nicht in der neuen Liste.
- Fotoauflösung, Nativität und tatsächliche Kachelqualität ehrlich prüfen; der Name einer PNG beweist sie nicht.

## Sparsam arbeiten und berichten

Keine laufenden Statusmeldungen zu jedem Git-Befehl, Tokenfortschritt oder CI-Log. **Maximal eine knappe Meldung nach je 5 erledigten Bildern**, außerdem bei echtem Fehler/Blocker und zum Abschluss eine Zusammenfassung mit erledigt/übersprungen/offen samt Links. Dateien nicht ständig erneut komplett einlesen.

**Fertig**, wenn alle aktuell noch fehlenden Jobs aus der JSON validiert und in ihren jeweiligen `inbox/<building_name>/`-Ordner committed wurden oder nachvollziehbar als blockiert gemeldet sind. Kein Erfolg ohne überprüfbare PNG-Dateien.
