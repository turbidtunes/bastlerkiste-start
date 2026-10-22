# Bisherige Modellierungsentscheidungen

Diese Aufzeichnung bewahrt den vorhandenen Stand; sie ersetzt den ursprünglichen Plan nicht. Die Originaldateien in `church_work/` und `inbox/` wurden für die Sicherung nicht verändert. Angaben beschreiben Implementierung oder Absicht, keine abschließende Abnahme.

## Geometrie und Raumprogramm

- Assetname `grand_fond_parish_church`, Grundstückskennung `grand_fond_H04`.
- Modellhülle etwa 20,80 × 33,18 m, Höhe 18,25 m. Hauptkörper 17,60 × 23,00 m. Turm auf 6,80 × 7,20 m vertieft. Modellursprung über die gesamte Hülle zentriert; rohe Y-Grenzen vor Zentrierung −15,9 bis 17,2814097737 m. Fundament −0,20 m; Nutzungsebenen +0,60, +6,60 und +12,60 m.
- Treppenaustritt/Kuppelunterbau vergrößert und leicht versetzt. Der erreichbare Ausblick liegt vorne und rechts statt als vollständiger Umgang; Schutzbrüstung 1 m.
- Acht Treppenläufe mit je neun Steigungen, jeweils 1,50 m Höhenunterschied und 0,28 m Auftritt. Laufkörper 1,26 m breit, Ziel etwa 1,20 m frei neben dem Geländer. Podeste verschoben/verbreitert auf mindestens 1,40 m; vordere Treppenraumwand und Absturzsicherung am oberen Treppenloch ergänzt.
- Letzte Änderung ausschließlich im Quelltext: Treppenunterseitenprofil von −0,22 auf −0,40 m versetzt, um eine ausreichende konstruktive Plattendicke zu erzielen. `build.py` ist damit neuer als beide GLBs. Diese Änderung ist noch nicht neu gebaut; Kopfhöhe muss danach erneut überprüft werden.
- Echte Arkaden, Obergaden, Apsisfenster und geschlossene rote Wellblechdächer; acht dreieckige Dachlüfter mit Lamellen. Kuppelanschluss durch geschlossene Dachfläche ergänzt. Quaderkanten, Gesimse, Strebepfeiler, Rinnen/Fallrohre, gotisches Maßwerk, Kreuze und leere Figurennische als Geometrie.
- Uhr mit erhabenen Indexmarken statt ausformulierten Ziffern. Geschlossene Bretterdecken in Schiff/Chor ergänzt, damit Deckenplatzhalter an einer realen Decke sitzen.
- Hauptportalprofil auf etwa 4,90 m über Boden angehoben; 2,80 m hohe Haupttür und festes Oberlicht; Oberlicht höher gesetzt, um Türköpfe freizuhalten.
- Östliche hintere Pfeiler auf x = 4,15 m zurückgesetzt, um den hinteren Gang zu verbreitern. Ungefähre Nebenraummaße im Stand: Lager 2,40 × 2,40 m; WC 2,40 × 2,22 m; Büro 3,84 × 3,58 m; Sakristei 3,84 × 4,64 m.
- Seitliche/hintere Zugangstreppen entlang der Fassade gedreht, mit ausreichend tiefen Podesten innerhalb der Hülle. Haupttreppe vier Steigungen à 0,15 m, Auftritte 0,32 m, Podesttiefe 1,54 m.

## Türen und Platzhalter

- Zwölf Türblätter in elf Öffnungen. Geschlossene 50-mm-Blätter, etwa 7-mm-Spalte, zurückgesetzte Füllungen und Beschläge. Scharnierursprung an der Innenseite, +0,175 m zum Zielraum; lokales Blatt-Y von −0,05 bis 0. Zusatzdaten für Öffnung: L −90°, R +90°.
- Bürotür erschließt das Büro jetzt aus dem östlichen Seitenschiff statt aus dem hinteren Gang. Zuletzt auf x = 5,50 m verschoben, um den Pfeiler zu meiden. Die aktuelle exportierte Fassung wurde danach noch nicht abschließend auf Kollision geprüft.
- Schiff von 20 auf 14 Bänke reduziert: sieben je Seite, Ziel 1,20 m freie Wege zwischen den Reihen. Vier Chorbänke bleiben. Altar nach hinten auf y = 14 verschoben, Lesepult auf x = −2,8 / y = 13,2.
- Vorhalle von zwei auf eine Bank reduziert, um den Weg frei zu halten.
- Glockenplatzhalter umfasst nun die gesamte bodengestützte Glocke mit Joch; eigenes festes Glockentragwerk entfernt. Platzierung x = 2,3 an der Raumseite schafft eine freie Route.
- Wandstücke an tatsächliche Wandflächen versetzt; Regale von Fensterrahmen weggerückt; Handtuchhalter an die WC-Trennwand. Deckenplatzhalter mit Ursprung oben und Box darunter. Standmöbel mit Ursprung am Boden. Lokale Ausrichtung/Abmessungen bleiben getrennt von Knotentransformationen.
- Letzter erfasster Stand: 73 Platzhalter. Die vollständigen konkreten Rollen pro Raum und Türdaten stehen unverändert in `church_work/stats.json` und werden im Sicherungs-`note.txt` wiedergegeben.

## Erzeugung und Verarbeitung

- Architektur mit Manifold vereinigt, Materialkennungen erhalten. Eigener GLB-Export mit Meter-UVs und flachen/geglätteten Normalen.
- Anschließend Blender-Bereinigung: verschweißen, degenerierte Flächen behandeln, Restlöcher schließen, importierte benutzerdefinierte Normalen entfernen, nach Materialien aufteilen, erneuter GLB-Export.
- `clean.glb` ist der jüngste bereinigte Export. `inbox/.../grand_fond_parish_church.glb` ist noch der rohe Export. Endgültige Übernahme und Mesh-Namensbereinigung durch `finalise.py` fanden nicht statt.
- `finalise.py` enthält bereits formulierte Abschlussaussagen, die noch nicht vollständig belegt sind. Diese Datei wird historisch unverändert erhalten und darf nicht als Prüfbericht gelesen oder ungeprüft als Abschluss ausgeführt werden.
- `swing_check.py` bereitet Tests bei 15°, 30°, 45°, 60°, 75° und 90° vor; es liegt kein Ergebnis `swing.json` vor.
- Die fünf bestehenden Bildkacheln stammen aus der früheren Arbeit und wurden unverändert mitgesichert. Während der Rettung wurden keine Texturen erzeugt oder bearbeitet.

## Zeitliche Zuordnung (UTC, 2026-10-22)

| Datei / Gruppe | Stand und Bedeutung |
|---|---|
| review.blend, Renderings | Um 07:12; historischer Sichtstand vor späteren Geometrie-/Layoutkorrekturen. `review.blend1` ist ebenfalls erhalten. |
| validation.log | Um 07:10; älterer Prüflauf. |
| validation.json, collisions.json | Um 07:34; älter als die letzten Exporte; noch Fehler verzeichnet. |
| build.log, stats.json, roher GLB | 07:41:10; jüngster ausgeführter Hauptaufbau. |
| clean.glb, repair.log | 07:41:27–28; jüngste lokale Blender-Bereinigung. |
| build.py | 07:41:44; enthält danach vorgenommene, noch nicht ausgeführte Treppenprofiländerung. |

Exakte ursprüngliche Zeitstempel und Prüfsummen aller kopierten Quelldateien stehen in `snapshot_manifest.json`.
