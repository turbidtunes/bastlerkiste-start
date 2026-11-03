# FPS-Animationen, Korrektur v2 – Llamp, Gropada, Migjorn, Garbi und Llebeig

[Alle fünf Blender-Dateien herunterladen](https://raw.githack.com/turbidtunes/bastlerkiste-start/codex/fps-animationen-v2-2026-11-03/inbox/fps_animationen_v2/Download.html)

Gewünschte Waffe auf der Downloadseite anklicken. Der Download wird automatisch aus den übertragenen Binärteilen zusammengesetzt und per SHA-256 geprüft. Offline: diesen Ordner entpacken und `python rebuild.py` ausführen.

## Änderungen

- Kamerazentrierung der Hüftpose und Visierachse beim Zielen. ADS-Sway erfolgt um und entlang der Blickachse; die Kamera bleibt unverändert.
- Sprint: Mündung nach links am unteren Bildrand, einschließlich passender Ein- und Ausgangsbewegung. Die freie Stützhand folgt ihrer eigenen Laufbewegung.
- Gleichmäßig gestaffelte rechte Griffinger mit angelegtem Ringfinger; Zeigefinger bei ADS/Fire am Abzug und bei anderen Tätigkeiten außen am Bügel. Neue Zielübergänge zusätzlich auf Hautüberschneidungen geprüft.
- Ellbogenebene und Unterarmdrehung über die Clips an die Kontaktposen angepasst, mit weich gebackenen Übergängen. Die Handposition am Griff bleibt dabei erhalten.
- Nachladen mit durchgehenden Bewegungsbögen, Gewichtsverlagerung und gedämpfter Waffenbewegung. Magazin und greifende Hand bewegen sich gemeinsam.
- Durchladen: Haltepose direkt aus dem tatsächlich bewegten Ladehebel bzw. Schlitten berechnet, Kontaktphase mit der Mechanik synchronisiert und eigener Rückweg nach dem Loslassen.
- Llamp: Stützhand um die Schusshand, Überhandgriff am Schlitten; Armreichweite und Abstand zur Kamera beim Durchladen angepasst.
- Gropada: Teller nach oben abnehmen/aufsetzen, mitbewegte Abdeckung und erhaltener Zuführrotation. Rechte Hand am rechten Ladegriff, während die linke Hand stützt; Magazinweg berücksichtigt auch die minimale Armbeugung.
- Migjorn, Garbi und Llebeig erneut auf Zentrierung, dynamischeres Nachladen, Sprint und Mechanikkontakte überarbeitet. Garbis Klappschaftkontakt und Llebeigs manuelles Repetieren bleiben erhalten.

60 fps, ursprüngliche Clip-Längen und Namen. Steuerung und Mechanik gemeinsam in jedem Hauptclip gebacken; passende separate Mechanik-Aktionen weiterhin vorhanden. Ausgangsaktionen als `ORIGINAL__*` erhalten; die hochgeladenen Ausgangsdateien wurden nicht überschrieben. Keine privaten Referenzfotos enthalten.

## Prüfung im ausgewerteten Blender-Rig

Halbe Zwischenbilder aller Clips geprüft. Angaben in Millimetern; Hand-Ziel-Abweichung und relative Ladegriffbindung sind Rig-Messwerte und keine Haut-Kollisionsmessung.

| Waffe | Clips | max. Hand-Ziel-Abweichung | max. ADS-Achsenabweichung | max. Ladegriffbindung-Abweichung |
|---|---:|---:|---:|---:|
| Llamp | 16 | 0.017 | 0.0003 | 0.005 |
| Gropada | 15 | 0.061 | 0.0007 | 0.003 |
| Migjorn | 15 | 0.051 | 0.0005 | 0.007 |
| Garbi | 16 | 0.068 | 0.0007 | 0.069 |
| Llebeig | 16 | 0.068 | 0.0005 | 0.000 |

Bei allen fünf Waffen zeigt die projizierte Visier-/Laufachse im Sprint nach links; die Waffe wird am unteren Bildrand geführt. Griff- und Kontaktphasen wurden zusätzlich lokal gerendert kontrolliert. Dateien nach verlustfreier Kompression erneut mit Blender 5.3 Beta geöffnet; Downloadrekonstruktion mit Prüfsumme getestet.

Keine vollständige Kollisionssimulation und kein Unreal-Test. Kleine Hautüberschneidungen bleiben möglich. `Fire` enthält Waffenrückstoß, der mit zusätzlichem prozeduralem Rückstoß im Spiel abgestimmt werden muss.
