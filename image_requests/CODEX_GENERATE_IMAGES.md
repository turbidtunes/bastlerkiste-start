# Codex-Arbeitsauftrag: Fehlende Bilder aus Bastlerkiste schrittweise erzeugen

## Start und Geltungsbereich

**Lies zuerst vollständig** `image_requests/missing_images_2026-10-21.json`
in `turbidtunes/bastlerkiste-start` auf `main`. Diese JSON enthält 34
einzeln abzuarbeitende Bildmotive, 35 exakte Zielpfade und neun bereits
anders benannte HUD-Bilder, die nicht ungeprüft dupliziert werden sollen.

**Repositorys:**
- `turbidtunes/bastlerkiste-start`: kleine Arbeits- und Gebäude-`inbox`;
  diese JSON und der vorliegende Codex-Auftrag liegen hier.
- `turbidtunes/bastlerkiste`: großes Spielprojekt; Originalquelle
  `AUFTRAG_BILDER_GPT.json`, neue Spieltexturen
  `map/textures/gpt/`, neue Szenen `game/hud/images/`.

Die Benennungen sind historisch uneinheitlich. Maßgeblich für jede
Datei ist ausschließlich das **Paar aus `repository` und `path`**
in `queue[].output_files`. `source_id`, `datei`, Baumname,
`note.txt`-Titel und `T_Icon_*` können voneinander abweichen.

**Wichtige Abgrenzung:** Es gibt in den geprüften Git-Bäumen keinen
Versionskontrollordner namens `Input`. Die von Nutzern gemeinte
Bild-/Gebäude-Ablage heißt `inbox` bzw. `map/textures/gpt`.
Erfinde keinen neuen `Input/`-Ordner. Bestehende Bilder dürfen nicht
ohne klare Gleichwertigkeit umbenannt oder überschrieben werden.

## Abarbeitung – eine Bilddatei nach der anderen

1. Prüfe vorab, ob du in deiner **konkreten Codex-Sitzung**
   Bildgenerierung nutzen, beide GitHub-Repositorys lesen und in den
   benötigten Zielpfaden committen/pushen kannst. Benutze deinen
   vorhandenen Codex-/ChatGPT-Plus-Zugang, soweit das Produkt dies
   erlaubt; **keine kostenpflichtige externe Bilderzeugungs-API**
   und keine stillschweigende Zusatzabrechnung.
   Falls ein Recht/Werkzeug fehlt: sauber melden, nicht Erledigung
   vortäuschen.
2. Lies `queue` aus der JSON **in Reihenfolge**. Arbeite immer nur an
   einem `queue[]`-Job gleichzeitig. Prüfe die exakten `output_files`
   zunächst gegen die aktuellen Git-Bäume beider Repositorys; die
   Inventarliste ist ein Snapshot, kein Beweis gegen spätere Änderungen.
3. Prüfe `already_present_functional_aliases` vorab: Hier existieren
   neun funktional zugeordnete `T_Icon_*` unter anderen Namen.
   **Nicht duplizieren**, wenn Motiv und Verwendung hinreichend
   übereinstimmen. Bei sichtbarer Abweichung im abschließenden Bericht
   offen als `needs_review` markieren. Die bereits vorhandenen
   `T_Card_*` sind grafische HUD-Kompositionen und ersetzen **nicht
   automatisch** die in `queue` verlangten fotorealistischen Szenen.
4. Für den aktuellen Auftrag verwende `full_prompt`, beachte
   `kind`, `physical_tile_size_m`, `required_px` und
   `output_files`. `original_prompt` erhält die historische
   Originalformulierung, `full_prompt` enthält zusätzlich die
   allgemeinen Bildregeln. Sei besonders streng bei der Unterscheidung
   von Fotos, flachen Emblemen und freigestellten UI-Symbolen.
5. **Bild wirklich erzeugen**, nicht als Blender-Render, Pseudofoto,
   prozedurale Noise-Textur, künstliche Farbfläche oder
   durch Kopieren des Referenzbildes ersetzen. Der Auftrag betrifft
   statische PNG-Bilder, keine GLB-Modellierung.
6. Für `seamless_photo_tile`: fotorealistische Oberflächen,
   orthogonale Kamera, realer Materialmaßstab, gleichmäßiges mattes
   Licht; echte nahtlose Kanten **ohne** Crossfade-Band, Spiegelhälften,
   Ghosting oder Raster. Die Kachelung als 3×3-Wiederholung überprüfen.
   Ausgabe **exakt 2048 × 2048 Pixel als native PNG**, **kein Upscaling**.
   Für Embleme, Flaggen und Bilder gelten die Maße unter
   `required_px`. UI-Symbole mit transparenter Fläche.
   Wenn die konkrete Bildfunktion das geforderte native Format nicht
   erzeugen kann, **nicht künstlich hochskalieren**: den Job
   `blocked_resolution` melden statt ein unechtes Fertigergebnis
   abzuliefern.
7. Kontrolliere die Bilddatei (PNG, Pixelmaße, Kanal/Alpha,
   nicht leer, sichtbare Motivtreue, korrektes Material); für
   nahtlose Kacheln zusätzlich 3×3-Sichtprüfung. Python darf
   Bilder ausschließlich untersuchen/prüfen, **nicht** eine
   prozedurale Ersatztextur erzeugen.
8. Speichere ausschließlich unter den exakten `output_files`-Pfaden
   im **jeweils angegebenen Repository**. Wenn ein Job zwei Ziele
   besitzt (z. B. `new_roof_corrugated_red`), eine identische geprüfte
   Quelle einmal erzeugen und dann an **beide** Orte kopieren:
   `inbox/bel_air_h01/new_roof_corrugated_red.png` und
   `inbox/cite_moulin_h04/new_roof_corrugated_red.png`.
   Die .glb und note.txt der Gebäude **niemals** verändern.
9. Nach einer erfolgreichen Bilddatei committe die tatsächlich
   erzeugte(n) PNG-Datei(en) in das richtige Repository und pushe
   den Branch `main` bzw. eröffne bei fehlenden Rechten einen PR.
   Nutze aussagekräftige kleine Commits, z. B.
   `Add photoreal new_plaster_pink tile`. Kein Commit
   beliebiger temporärer Bilder, Vorschauen oder Test-Raster.
   Bei gleichzeitig laufenden anderen GitHub-Jobs vor dem Push
   vorsichtig `pull --rebase` und nur die eigene Datei committen.
10. Abarbeitungsstand möglichst nach jeder abgeschlossenen Bilddatei
    in einer kleinen ergänzenden Datei
    `image_requests/PROGRESS.md` **im kleinen Repository**
    dokumentieren: `job id | status | Commit SHA | tatsächliche Pfade`.
    Dabei JSON-Originalaufträge und die `already_present`-Liste
    nicht umschreiben. So kann die Aufgabe nach Kontextwechsel
    oder Codex-Nutzungslimit fortgesetzt werden.
11. Falls du eine bestehende Datei mit anderer Bezeichnung findest,
    prüfe zuerst visuell ihren Inhalt und die Material-/UI-Semantik.
    Ist sie wirklich gleichwertig, **keine neue Generierung**:
    in `PROGRESS.md` als `reused_existing` samt Pfad markieren.
    Andernfalls das neue Bild am vorgesehenen Pfad herstellen.
    Nur nach Dateiname zu entscheiden ist verboten.
12. Falls die Sitzung aus technischen Gründen unterbrochen wird,
    bei der nächsten Codex-Aufgabe zuerst `PROGRESS.md` und die
    tatsächlichen Repo-Zielpfade lesen und am **ersten unerledigten
    JSON-Eintrag** fortfahren. Bereits fertige Bilder nicht erneut
    erzeugen.

## Zuständigkeit nach Bildtyp

- **Spieltexturen:** `turbidtunes/bastlerkiste/map/textures/gpt/<name>.png`.
  Kein `derive.py`, `itex.py`, Shader- oder UE-Build, außer der
  Nutzer beauftragt diese zusätzlichen Schritte ausdrücklich.
- **UI-Bilder:** `turbidtunes/bastlerkiste/game/hud/images/<name>.png`;
  bereits existierende `game/hud/icons/png/T_Icon_*` behalten
  ihre Originalnamen. Die neuen fotorealistischen Moduskarten
  **nicht** auf vorhandene `T_Card_*` schreiben.
- **Neue Gebäudematerialien:**
  `turbidtunes/bastlerkiste-start/inbox/<building_name>/new_<what>.png`
  direkt neben der jeweiligen vorhandenen GLB und note.txt.
  Bei abweichendem textuellen Gebäudenamen ist nur der
  **reale Ordnername** in `output_files` maßgeblich.

## Sparsamer Arbeitsstil

- Keine fortlaufenden Statusmeldungen, keine langen Protokollausgaben,
  keine dauernden API-/GitHub-Abfragen. Nur nach je fünf
  abgeschlossenen Bildmotiven, bei Blockern und am Ende berichten.
- Das große `bastlerkiste`-Repository kann sehr umfangreich sein.
  Wenn möglich mit Sparse Checkout / vorhandenen GitHub-Funktionen
  nur die benötigten Ordner holen. **Nicht blind das gesamte Repo
  mitsamt allen Bildern herunterladen**.
- Kein paralleles Generieren verschiedener Bildmotive, keine
  eigenständigen teuren Claude-Builds; hier sind ausschließlich
  fehlende Bilder beauftragt.
- **Erfolgsmaßstab:** Jeder `queue`-Eintrag ist entweder
  `generated` mit echten geprüften und committed PNGs,
  `reused_existing` mit überprüfter passender Datei oder
  `blocked` mit konkretem Grund. Keine erfundenen
  Erfolgsmeldungen.

## Abschluss

Gib eine kurze tabellarische Zusammenfassung: neue Bilder, wiederverwendete
vorhandene Bilder, offene Fehler, Commit-/PR-Links und exakte Pfade. Weise
auf weiterhin fehlende Fotos hin. Die Datei `missing_images_2026-10-21.json`
ist die unveränderte, vollständige Arbeitsquelle. **Jetzt beim ersten
noch fehlenden `queue`-Eintrag beginnen und strikt nacheinander fortfahren.**
