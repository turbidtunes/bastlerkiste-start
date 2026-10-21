# CODEX-AUFTRAG – Fehlende Bildmotive sequenziell erstellen und einchecken

## Startpunkt

Du arbeitest mit GitHub-Zugriff auf die Repositories
`turbidtunes/bastlerkiste-start` (kleines Steuerungsrepository)
und `turbidtunes/bastlerkiste` (großes privates Spielprojekt).

Lies **zuerst und vollständig**:
`texture_requests/missing_images_queue.json`.

Diese Datei ist bereits mit dem GitHub-Stand vom **21.10.2026**
abgeglichen. Sie enthält **32 unterschiedliche Bildmotive** und
**33 exakt benannte Ziel-Dateipfade**. Die neun funktionsgleichen,
bereits vorhandenen HUD-Icons stehen explizit unter
`skipped_existing_icons`; diese **NICHT** neu generieren.
Der Ordner `Input` existiert im Projekt auf `main` nicht.
Die Gebäudeaufträge sind unter `bastlerkiste-start/inbox/` abgelegt.

## Absolute Regeln

- **Ein Bildmotiv nach dem anderen**, in der Reihenfolge `jobs[]`.
  Nach einem abgeschlossenen Motiv: Zieldatei(en) committen und
  **erst danach** das nächste Motiv beginnen. So gehen bei einer
  Unterbrechung keine fertig erzeugten Bilder verloren.
- **Nichts überspringen, was wirklich fehlt; nichts ersetzen, was
  inzwischen vorhanden ist.** Für jedes Job-Ziel vor der
  Bildgenerierung oder dem Upload die Existenz auf GitHub `main`
  erneut prüfen. Wenn alle Ziele existieren, Job als `already_present`
  protokollieren. Wenn nur eines der zwei Ziele existiert, dieses
  Bild erst auf seine fachliche Passung zum zweiten Ziel prüfen
  und nur bei identischer Materialanforderung wiederverwenden.
- **EXAKTE Zielpfade** aus `destinations[].repository` und
  `destinations[].path`; Dateinamen und Erweiterungen niemals
  eigenmächtig verändern. Große Spielprojekt-Dateien gehören nach
  `turbidtunes/bastlerkiste`, die `new_*.png` in die bereits
  vorhandenen Ordner `turbidtunes/bastlerkiste-start/inbox/<gebäude>/`,
  unmittelbar neben die vorhandene GLB und `note.txt`.
- Erstelle Bilder mit der **tatsächlich verfügbaren Codex-
  Bildgenerierungsfunktion über deinen ChatGPT-Plus-Zugang**.
  Falls keine solche Funktion in dieser Sitzung bereitsteht,
  MELDEN und NICHT auf kostenpflichtige externe Bild-APIs,
  Python-Noise, Blender-Shader, geometrische Pseudobilder,
  Platzhalter oder Stockfotos ausweichen.
- Jeder Job besitzt `prompt`, optional `group_prompt`,
  `size_px`, `physical_tile_m` und `kind`. Verwende diese
  Werte **wortgetreu** als inhaltliche Basis. Ergänze lediglich
  notwendige Qualitätsregeln, verändere nicht das Motiv.
- **Native Ausgabegröße:** Für jede PNG exakt `size_px`;
  keine Hochskalierung, kein nachträgliches Schärfen als Ersatz
  für unzureichende Ausgangsauflösung. Kann das verfügbare
  Bildtool die native Pixelgröße nicht erzeugen, Job
  `blocked_native_resolution` vermerken und den nächsten Job
  fortsetzen, ohne irreführende Bilddatei hochzuladen.
- `kind=tile`: realistische dokumentarische Fototextur,
  Kamera genau senkrecht, gleichmäßige diffuse Helligkeit,
  keine Reflexe/Schlagschatten, keine Perspektive, kein
  Raster, kein gezeichnetes oder KI-geglättetes Aussehen.
  Alle Kanten müssen ohne sichtbare Naht aneinander anschließen,
  keine gespiegelten Hälften, Ghosting oder dunkle
  Cross-Fade-Bänder. Physische Abdeckung gemäß
  `physical_tile_m` beachten. **3×3-Probekachelung**
  optisch prüfen; Prüfansichten nur temporär erstellen, nicht committen.
- `kind=emblem`: klare fiktive Bildmarke nach Originalprompt,
  transparent ohne Text, keine reale Marke.
- `kind=flag`: exakt flache Fahnenfläche im geforderten
  Seitenverhältnis, nicht als flatternde Fahne.
- `kind=screen`: fotografische Kinostills gemäß Originalprompt,
  nur erwachsene Personen, keine realen Logos oder Text,
  exaktes Seitenverhältnis. Die bestehenden HUD-T_Icon_*
  und T_Card_* NICHT verändern: Dies sind andere Assets.
- Jedes PNG technisch verifizieren (mit Pillow oder anderer
  echter Bilddateiprüfung): PNG-Format, exakte `size_px`,
  für transparente Embleme Alpha-Kanal, nicht leere
  Datei. Die visuelle Qualität und Nahtlosigkeit zusätzlich
  anhand der tatsächlichen Pixel kontrollieren. Keine
  bloß behauptete Prüfung.
- Originalbilder in `bastlerkiste` ausschließlich an den
  expliziten Zielen ergänzen; nicht eigenmächtig
  `map/textures/mapping.json`, `derive.py`, `itex.py`,
  `AUFTRAG_BILDER_GPT.json`, GLBs oder Unreal-Assets umbauen.
  Die Einbindung in die Engine ist eine **separate** Arbeit.
- Sicherheit: keine API-Schlüssel im Repository oder Log.
  Die GitHub-Commits ausschließlich für diese Bilddateien
  und den aktualisierten Queue-Fortschritt. Keine PNGs
  in einen allgemeinen Codex-Sammelordner umleiten.

## Vorgehensweise mit GitHub

1. Öffne als Arbeitsbereich `bastlerkiste-start` auf `main`.
   Prüfe `AGENTS.md` und die vorliegende Queue-Datei.
2. Verwende für die wenigen Pfade im sehr großen
   `bastlerkiste` möglichst gezielte GitHub-Datei/API-
   Operationen oder einen sparsamen Checkout; vermeide einen
   vollständigen Klon des riesigen Repositories, falls
   nicht zwingend nötig.
3. Pro Job erst Existenz jedes `destinations[]`-Pfades in
   dem angegebenen Repository prüfen. Danach genau EIN Motiv
   mit dem Codex-Bildtool erzeugen. Das Bild unter seinem
   **unveränderten `filename`** speichern.
4. Pixelzahl, PNG-Format, Bildinhalt und bei Kacheln 3×3-
   Nahtlosigkeit verifizieren. Bei Qualitätsmängeln **nur dieses
   Motiv** erneut generieren, nicht den gesamten Auftrag.
5. Das fertige Bild an jeden fehlenden, fachlich passenden
   Zielpfad übertragen und je Ziel-Repository committen/pushen.
   Bei `new_roof_corrugated_red.png` sind ZWEI separate
   Zieldateien vorgesehen.
6. `jobs[].status` erst nach erfolgreichem Push aller Ziele
   in der Queue ändern: `done`, `already_present`,
   `blocked_native_resolution` oder `blocked_capability`.
   Optional `commit` oder `failure_reason` je Job ergänzen;
   bestehende Namen, Prompts und Ziele unverändert lassen.
   Den Queue-Zustand nach jedem Job bzw. spätestens fünf Jobs
   committen, damit die Arbeit zuverlässig wiederaufgenommen
   werden kann. Bei erneuter Sitzung nur Jobs im Status
   `missing`/blockiert prüfen; bereits verifizierte Dateien
   niemals blind überschreiben.
7. Kurzstatus für den Nutzer nur nach ca. 5 fertigen Motiven,
   bei Blockern und ganz am Ende: `X/32 fertig, N blockiert`.
   Keine fortlaufenden Chat-Meldungen für jeden Dateiaufruf,
   keine vollständigen GitHub-Logs in den Chat kopieren.
8. **Keinen Claude-/Blender-Build starten.** Diese Bildaufträge
   betreffen nur fehlende Fotos, UI-Bilder und Embleme.
9. Endbericht: Anzahl Motive, Anzahl abgelegter Dateien,
   Blocker, Links zu den beiden Ziel-Repositories und zur
   aktualisierten JSON-Queue.

## Zusätzliche fachliche Hinweise

- Die alte `AUFTRAG_BILDER_GPT.json` enthält bereits die
  authentischen englischen Bildprompts. Diese stehen unverändert
  im Feld `prompt` und ihre übergreifenden Vorgaben im Feld
  `group_prompt`. Nicht alle Aufgaben sind Fototexturen:
  Emblem, Fahne und Bildschirmbilder haben andere Vorgaben.
- Für die neuen Gebäude-Kacheln sind die Beschreibungen direkt
  aus den `inbox/<name>/note.txt` zusammengefasst;
  `source_file` benennt die Quelle. Die in den GLBs
  bereits vorhandenen Materialslots werden nicht verändert.
- `size_px` der älteren Kacheln und neu erstellten
  Gebäude-Kacheln ist 2048×2048; die Bildschirmbilder sind
  1536×1024, das Emblem 1024×1024, die Flagge 1536×1024.
  Falls die Originalprompts und Rahmenregeln zusätzliche
  Besonderheiten benennen, haben diese Vorrang.
- Die Gebäude mit offenen Bildern sind:
  `bel_air_h01`, `cite_carriere_h01`,
  `cite_moulin_h04`, `grand_fond_h07`,
  `moulin_h05` und `weiler_h01`.

**Beginne sofort mit dem ersten weiterhin fehlenden Job der Queue.
Keine Rückfrage und keine Neugenerierung vorhandener Bilder.**
