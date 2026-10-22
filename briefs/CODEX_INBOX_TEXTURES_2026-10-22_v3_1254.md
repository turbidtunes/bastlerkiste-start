> **ARCHIV / NICHT MEHR AUSFÜHREN (Stand 22.10.2026):** Der aktualisierte, branch-spezifische Gesamtauftrag steht unter [`briefs/CODEX_INBOX_TEXTURES_2026-10-22_v4_ALL.md`](../briefs/CODEX_INBOX_TEXTURES_2026-10-22_v4_ALL.md), zugehörige JSON: `briefs/missing_inbox_textures_2026-10-22_v4_ALL.json`. Darin sind beide Grand-Fond-H04-Kirchen berücksichtigt. Diese ältere Liste kann falsche Alias-Zielordner oder unvollständige Bestände enthalten.

# CODEX-FOLGEAUFTRAG V3 – nur fehlende Fototexturen in inbox/ (1254×1254)

Du arbeitest ausschließlich im GitHub-Repository **turbidtunes/bastlerkiste-start**, auf \`main\`.

**Maßgeblich ist die neue JSON-Datei:**

\`briefs/missing_inbox_textures_2026-10-22_v3_1254.json\`

Die aktuelle Prüfung ergab **22 fehlende, eindeutige Bilddateien in 12 vorhandenen Gebäudeordnern**. Alle 33 PNG-Zieldateien aus dem vorigen Auftrag V2 sind bereits vorhanden und dürfen NICHT erneut erzeugt werden.

## WICHTIG: Auflösung 1254×1254 ist verbindlich

**Für diesen gesamten Auftrag gilt ausdrücklich eine native Ausgabegröße von exakt 1254 × 1254 Pixeln als PNG.** Die Angabe hat Vorrang vor sämtlichen älteren 2048×2048-Vorgaben in AGENTS.md, den Gebäude-Originalprompts oder vergangenen Arbeitslisten.

Kein Upscaling, keine nachträgliche Vergrößerung von 1024 auf 1254, kein Resampling auf die verlangte Größe. Wenn deine Bildgenerierung 1254 × 1254 nicht nativ unterstützt, melde das als Blockade und lege keine Fakedateien an.

## Serielle Abarbeitung, genau ein Bild zurzeit

1. Lies die JSON vollständig. Sortiere ihre \`jobs\` nach \`order\`; verwende **immer exakt \`job.prompt\`** als individuellen Bildauftrag. Erzeuge nur die 22 als fehlend markierten Materialoberflächen.
2. Vor jedem Bild: Prüfe den aktuellen GitHub-Stand und den exakten \`job.destination\`-Pfad. Wenn die PNG unter exakt diesem Pfad inzwischen schon existiert, **überspringen**, keinesfalls überschreiben oder anders benennen.
3. Nutze die **tatsächlich verfügbare Bildgenerierungsfunktion von Codex mit ChatGPT Plus**, sofern sie die geforderte native Pixelgröße unterstützt. Keine separate kostenpflichtige OpenAI-/Anthropic-/Drittanbieter-Bild-API ohne vorherige ausdrückliche Zustimmung.
4. Jedes Bild muss eine **fotorealistische Aufnahme nur des benannten Materials** sein: Kamera senkrecht zur Oberfläche; diffuse homogene Beleuchtung; echte ungeschönte Materialdetails; natürliche Farben; keine Perspektive, Spiegelungen, Schatten, Logos oder Schrift. **Nahtlos** an sämtlichen vier Kanten, kein Mirroring, Ghosting, Crossfade, künstliche verwaschene Randzone oder Raster. Aus der Textur keine Gebäudekomponenten oder modellierbare Details machen – Brettfugen, Profile, Fliesenfugen und Wellenblechrippen gehören zur 3D-Geometrie.
5. Im Job \`physical_tile_size_m\`: Wenn vorhanden, genau diese reale Abdeckung beachten. Wenn \`null\`, steht das physische Maß in der \`note.txt\` nicht; kein erfundenes bestätigtes Maß behaupten. Gegebenenfalls als Schätzung kennzeichnen.
6. Nach jedem Bild: Datei als native **1254×1254 PNG** prüfen, eine 3×3-Anordnung der identischen Kachel visuell ansehen und an Übergängen/auffälligen Wiederholungen bewerten. PIL/Python sind **nur zur Prüfung** zulässig, nicht zum prozeduralen Erzeugen, Upscalen, Spiegeln oder Verschleiern von Mängeln. Schlechte Bilder vollständig neu generieren.
7. **Nur an dem vorgegebenen exakten Pfad ablegen**: \`inbox/<building_name>/new_<material>.png\`. Danach genau diese erfolgreich geprüfte Bilddatei committen und nach \`main\` pushen. Ein Bild pro Schritt; vor dem nächsten Bild Remote-Änderungen berücksichtigen.
8. Keine GLBs, \`note.txt\`, vorhandene PNGs, Bauprompts, Repo-Skripte, Workflow-YAMLs oder bereits erfüllte Altaufträge anfassen, umbenennen, löschen oder überschreiben. Keine GitHub Blender Actions starten. Ausschließlich **inbox/** als Prüfumfang und Bildablage; die JSON und diese Anleitung unter \`briefs/\` dienen nur als Auftrag.
9. Wenn die Ausgabe technisch nicht nativer 1254-Auflösung entspricht, wenn ein Motiv nicht nahtlos erzeugbar ist oder ein Git-Push nicht möglich ist: den konkreten Job und Grund nennen, keine erfolgreiche Lieferung behaupten.

## Kommunikation, Tokenkosten und Fortschritt

Keine Meldung nach jedem einfachen Toolaufruf. Kurze Zwischenmeldung nur alle fünf erfolgreich geprüften/committeten PNGs oder bei echtem Fehler. Bei Abschluss: Anzahl neu erstellt / vorgefunden / offen und direkte Pfade auf GitHub nennen. Komplette Protokolle und identische große Dateien nicht dauernd erneut in den Kontext ziehen.

## Beispiel: die richtige Ablage

Der Job \`calanques_h09__new_door_oak_aged\` ergibt genau:
\`inbox/calanques_h09/new_door_oak_aged.png\`

Nicht \`inbox/les_calanques_finca/\`, nicht \`textures/\`, keine alten Aliasnamen. Der Ordnername der tatsächlichen GLB und \`job.destination\` ist verbindlich.
