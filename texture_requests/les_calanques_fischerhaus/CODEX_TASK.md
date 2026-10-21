# Codex-Texturauftrag fuer les_calanques_fischerhaus

Diese Datei ist eine UEbergabe an eine Codex-Sitzung mit dem ChatGPT-Plus-Abo,
kein API-Aufruf von GitHub Actions. Codex muss wirklich Zugriff auf seine
Bildgenerierung haben; ansonsten melden und nicht mit Blender/Shader/Python
synthetische Foto-Texturen vortaeuschen.

1. Lies texture_requests/les_calanques_fischerhaus/manifest.json und plan.md.
2. Sieh dir die dort genannten Originalreferenzen in referenzbilder/ an.
3. Erzeuge ausschliesslich die als missing_textures gelisteten Bilder.
   Falls die Liste leer ist: KEINE neuen Bilder noetig.
4. Pro Material Beschreibung aus dem Plan beachten; bei unklaren
   Oberflaechen nicht raten, sondern nachfragen. Perspektive genau
   senkrecht, realistische fotografische Oberflaeche, keine gemalten
   Kanten, Schatten, Glanz, Verfahrenstricks oder Pseudo-Fotos.
   Kein Mirroring, kein Ghosting, keine vignettierten Raender.
5. Korrekte, wirklich nahtlose 2048x2048-PNG mit Dateinamen
   aus manifest.json unter inbox/les_calanques_fischerhaus/ direkt neben der
   spaeteren GLB und note.txt speichern. KEIN Upscaling.
6. Wiederholung als 3x3-Kacheln auch VISUELL pruefen. Physische
   Abdeckung in Metern dokumentieren und manifest.json aktualisieren.
7. Fuehre aus: python3 scripts/texture_handoff.py verify --repo . --slug les_calanques_fischerhaus
8. Committe und pushe die neuen PNG-Dateien unter inbox/les_calanques_fischerhaus/
   und das aktualisierte Manifest nach main. Die spaetere Actions-Buildstufe
   darf diese PNGs NICHT beim Aufraeumen des Ausgabeordners loeschen.
9. Starte den teuren Claude-Build nicht von selbst. Gib dem Benutzer
   die urspruengliche GitHub-Plan-Run-ID als resume_run_id fuer die
   separate Fortsetzung mit identischem Prompt/Referenzbild.

Standardmaterialien aus der MATERIAL LIST gehoeren nicht in diese Liste.
Bestehende engine-seitige Foto-Texturen nicht kopieren oder ersetzen.
