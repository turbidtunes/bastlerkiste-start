# Codex-Orchestrierung: komplette UE5-Gebäude mit Fototexturen

Diese Repository-Anweisung gilt, wenn der Benutzer Codex einen neuen Gebäudeauftrag
übergeben und ausdrücklich die vollständige GitHub-Produktion beauftragt hat.

## Kommunikation und Monitoring – sparsamer Standard für weitere Aufträge

- Nur wichtige abgeschlossene Meilensteine, unerwartete Fehler und erforderliche
  Entscheidungen kurz mitteilen. Keine laufenden Kommentare zu Dateioperationen,
  Git-Befehlen, normalen Prüfungen oder unveränderten Laufzuständen.
- Keine umfangreichen Logs ausgeben; bei Fehlern nur Ursache, Run-ID und relevante
  Diagnose nennen.
- Laufende GitHub-Actions-Jobs nur alle **5 Minuten** abfragen. Keine zusätzlichen
  `gh run watch`-Schleifen, Statusabfragen oder Log-Abfragen zwischen diesen
  Intervallen, solange kein konkreter Fehler oder Abschluss bekannt geworden ist.
- Ansonsten selbstständig bis zum Ergebnis weiterarbeiten. Das Warten ist kein
  Anlass für eine Bestätigung oder einen weiteren kostenpflichtigen Lauf.

## Ziel

Ein eigenständiger, geprüfter Bauauftrag in prompts/<building_name>.md, dessen
passende Referenzdateien im Repo, eine kostensparende Claude-PLAN-Phase,
automatische Generierung der WIRKLICH fehlenden new_*-Materialfotos durch
Codex (nur falls die Codex-Sitzung Bildgenerierung tatsächlich unterstützt),
und eine abschließende GitHub-Actions-Baustufe mit GLB, note.txt und neuen
Material-PNGs im selben Ordner inbox/<building_name>/.

Die externen Claude-Aufrufe in GitHub Actions kosten Anthropic-API-Guthaben.
Codex-/ChatGPT-Plus-Nutzung ist davon getrennt. GitHub Actions darf NICHT
so tun, als könnte es selbst das ChatGPT-Plus-Kontingent verwenden. Weder
OpenAI- noch sonstige Bilderzeugungs-API-Schlüssel stillschweigend einsetzen.

## Ablauf – ohne zweiten manuellen "go", falls Codex Aktionen ausführen kann

1. Repo prüfen; Originalauftrag vollständig verstehen. Exakt einen kurzen,
   stabilen lower_snake_case-Namen für das Gebäude wählen, z. B.
   les_calanques_finca für Slot les_calanques_H09.
2. Originalreferenz unter referenzbilder/ bzw. references/ identifizieren,
   Existenz und Bildinhalt prüfen; bei Mehrdeutigkeit stoppen und nachfragen.
   Eine sichtbare Datei ist NICHT automatisch ein korrektes Bild.
3. Prompts/master_system.md und das konkrete Briefing zu EINER fertigen
   vollständigen Datei prompts/<building_name>.md verbinden. Kein zusätzlicher
   Prompt-Compiler. Objekt-/Plotvorgaben und spezifische Ausnahmen haben
   Vorrang. Kompakte PLAN-Textausgabe (ca. 900 bis 2.200 Wörter), keine
   Absenkung der Blender-3D-Qualität. Automatischer Bau ohne "go".
4. Verifizieren und diese Prompt-Datei committen und nach main pushen.
   In der GitHub-Action ist review_fixes=2 der Standard.
5. Mit vorhandener gh-CLI und Workflowberechtigung den PLAN-only-Lauf starten:

   gh workflow run build-3d-asset.yml --ref main \
     -f building_name=les_calanques_finca \
     -f prompt_path=prompts/les_calanques_finca.md \
     -f reference_images=referenzbilder/ref_les_calanques_H09_g_finca.png \
     -f run_mode=plan_textures \
     -f model=claude-sonnet-5-5 \
     -f review_fixes=2

   Die Namen/Pfade sind nur das H09-Beispiel; für andere Gebäude ersetzen.
   Exakte Run-ID aus gh run list / gh run view ermitteln. Die
   GitHub-Action schreibt danach texture_requests/<building_name>/plan.md,
   manifest.json und CODEX_TASK.md nach main und speichert den Plan als
   Diagnose-Artefakt für eine spätere Fortsetzung. Warten, bis dieser Run
   ENDE und Erfolg meldet. Falls der Run scheitert: nicht eigenmächtig
   erneut kostenpflichtige Claude-Arbeit auslösen.
6. Repo mit git pull aktualisieren. Codex liest
   texture_requests/<building_name>/manifest.json,
   texture_requests/<building_name>/plan.md und das Referenzbild.
   Der Manifest-Eintrag missing_textures bestimmt die Arbeit, nicht
   die vollständige Materialliste und nicht das eigene Bauchgefühl.
7. Für jeden missing_textures-Eintrag unter Verwendung der tatsächlich
   verfügbaren Codex-Bildgenerierung ein photorealistisches neues PNG
   erzeugen. Künftiger Standard: exakt native 1254 × 1254 Pixel (q1254),
   vom Nutzer als ausreichend freigegeben; kein Hochskalieren auf 2048.
   Fotografischer Materiallook,
   senkrechte Kamera, homogene diffuse matte Beleuchtung, physisch
   realistische Detailgröße, alle vier Kanten nahtlos, keine Spiegel-
   wiederholungen, kein Ghosting, keine künstlichen Farb-/Texturflächen,
   KEIN Upscaling. 3×3-Kachelung auch optisch beurteilen. Bei schlechtem
   Ergebnis erneut generieren statt Fake-Dateien einzureichen.
   Pro Textur physische Meterabdeckung im Manifest ergänzen.
8. VORGESCHRIEBENE BILDABLAGE:
   inbox/<building_name>/new_<what>.png

   Also beim H09-Beispiel neben der späteren
   inbox/les_calanques_finca/les_calanques_finca.glb und note.txt.
   Nicht in textures/, nicht in assets/textures/ und nicht in einem
   generischen globalen Materialordner. Keine GLB-Datei erfinden.
9. Die vorbereiteten PNG-Dateien überprüfen:

   python3 scripts/texture_handoff.py verify --repo . --slug les_calanques_finca

   Diese maschinelle Prüfung kann Dateiformat/Größe, NICHT echte
   Fotorealistik oder nahtlose Kanten garantieren. Nach erfolgreicher
   Prüfung nur neue/aktualisierte PNGs plus Manifest committen und
   nach main pushen.
10. Die fertige Modellierung mit dem Plan-Run als resume_run_id anstoßen:

    gh workflow run build-3d-asset.yml --ref main \
      -f building_name=les_calanques_finca \
      -f prompt_path=prompts/les_calanques_finca.md \
      -f reference_images=referenzbilder/ref_les_calanques_H09_g_finca.png \
      -f run_mode=build \
      -f model=claude-sonnet-5-5 \
      -f review_fixes=2 \
      -f resume_run_id=<GENAUE_PLAN_RUN_ID>

    Diese Wiederaufnahme spart die schon bezahlte Architekturplanung.
    Bei älteren gespeicherten Prompts gilt ebenfalls die aktuelle native
    q1254-Texturvorgabe; der Controller ergänzt sie, ohne Originalprompt,
    Referenzfingerprints oder Plan für eine neue Planung zu verändern.
    Die neue Action muss aus dem GitHub-Artefakt den exakten Originalprompt,
    die Referenzbildfingerprints und den gespeicherten Plan übernehmen.
    Vor neuen Claude-Build-API-Aufrufen muss das Manifest erfolgreich
    geprüft werden. Bei Fehlern Diagnose-Artefakte verwenden, keinen
    vollständigen Neubau starten.
11. Erfolg NUR melden, wenn der Workflow GLB-Export, Blender-Reimport und
    Commit nach inbox/<building_name>/ erfolgreich abgeschlossen hat.
    Dort nur <building_name>.glb, note.txt und relevante new_*.png.
    Im Fall von Fehlern exakte Ursache und Run-ID liefern.

## Grenzen und Ausnahmen

- Codex ohne Bildgenerierung: Datei- und Planarbeiten durchführen, aber
  die Bildphase nicht als erledigt ausgeben. Bericht mit den fehlenden
  new_*.png und Link zu texture_requests/<building_name>/CODEX_TASK.md.
- Leeres missing_textures-Array: keine Bilder generieren; den Build
  direkt mit resume_run_id des Plan-Runs fortsetzen.
- Falls auf main kein gh CLI oder keine Actions-Schreibrechte verfügbar
  sind: die letzten nötigen GitHub-Schritte klar benennen statt Ausführung
  zu behaupten. Keine wiederholten Gebühren verursachen.
- Während die Action läuft, ist Codex nur dann aktiv am Weiterarbeiten,
  wenn seine konkrete Task/Sitzung das Warten und die Nachbearbeitung
  unterstützt. Ein GitHub-Run selbst kann nicht dein ChatGPT Plus-/Codex-
  Bildkontingent starten.
- Kein Secret, Token oder OAuth-Guthaben in Log, Prompt, Code oder PNG.
- Sonstige Regeln für Blender, Referenztreue und Texturqualität stehen
  im vollständigen Bauprompt. Keine prozeduralen Pseudotexturen.
