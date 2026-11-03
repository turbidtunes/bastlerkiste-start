# Garbi und Llebeig – überarbeitete Animationen

[Blender-Dateien herunterladen](https://raw.githack.com/turbidtunes/bastlerkiste-start/codex/garbi-llebeig-animationen-2026-11-03/inbox/garbi_llebeig_animationen/Download.html)

Auf der Downloadseite die gewünschte Waffe anklicken. Sie setzt die übertragenen Teile automatisch zur vollständigen `.blend` zusammen und prüft SHA-256. Der GitHub-Anschluss konnte die großen Dateien nicht am Stück übertragen. Für die Offline-Nutzung diesen Ordner aus dem Repository-ZIP entpacken und `python rebuild.py` ausführen; beide Blender-Dateien werden daneben erstellt.

Garbi: 16 Clips einschließlich Klappschaft und Durchladen. Llebeig: 16 Clips einschließlich manuellem Repetieren, letztem Schuss mit offenem Verschluss und Schließen nach leerem Nachladen. 60 fps und ursprüngliche Clip-Längen; Ausgangsdateien unverändert. Originalaktionen als `ORIGINAL__*` erhalten.

- Rechte Griffpose mit angelegtem Ringfinger, gleichmäßiger Fingerstaffelung und gezielt gelockerten Rig-Grenzen. Korrigierte Reihenfolge der Hand-Constraints.
- Zeigefinger bei ADS/Fire am Abzug; bei Nachladen, Inspektion und Sprint außerhalb des Bügels. Gestufter, auf Durchdringungen geprüfter Zielwechsel.
- Angepasster Stützgriff und Magazin-Hand-Kopplung. Kontaktphasen, Umgreifen und Rückkehr zum Griff neu aufgebaut.
- Kontinuierliche Bewegungsbögen beim Nachladen, Gewichtsverlagerung und gedämpfte Reaktion beim Herausziehen und Einrasten. Zusätzlich Atembewegung und natürliches Sway.
- Visierachse beim Zielen auf die Bildmitte kalibriert. ADS-Sway rollt um die Blickachse und bewegt die Waffe entlang dieser Achse; die Kamera bleibt unverändert.
- Linke Hand folgt Garbis bewegtem Schaft; rechte Hand folgt Llebeigs Kammerstängel. Mechanik und Steuerung sind gemeinsam in jedem Hauptclip gebacken; separate Mechanik-Aktionen bleiben verfügbar.

Geprüft am ausgewerteten Rig einschließlich Zwischenbildern: maximale Hand-Ziel-Abweichung unter 0,07 mm, Magazin-Hand-Abweichung unter 0,02 mm und ADS-Visierachsen-Abweichung unter 0,001 mm. Fingerpolster-Abstände am Griff: Garbi ca. 2,12 / 1,87 cm, Llebeig ca. 2,10 / 1,80 cm. Zusätzliche gerenderte Kontrolle der Griffseiten und Kontaktphasen lokal durchgeführt. Speichern und erneutes Öffnen mit Blender 5.3 Beta geprüft.

Die Messwerte beschreiben das Blender-Rig, keine vollständige Kollisionssimulation. Kleine Hautüberschneidungen bleiben möglich; kein Unreal-Test durchgeführt. `Fire` enthält kurzen Waffenrückstoß, der mit zusätzlichem prozeduralem Rückstoß im Spiel abgestimmt werden muss. Private Referenzfotos sind nicht enthalten.
