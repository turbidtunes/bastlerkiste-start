# Ursprünglicher Architekturplan — grand_fond_H04

Dieser Text hält den vor der Modellierung festgelegten Plan aus dem Gespräch in strukturierter Form fest. Er ist keine nachträgliche Umplanung und keine Behauptung, dass sämtliche Planvorgaben bereits umgesetzt oder geprüft sind. Spätere Entscheidungen stehen separat in `modelling_decisions.md`; die unveränderten Skripte dokumentieren die konkrete Implementierung.

## Identität, Nutzung und Grundstück

Assetname: `grand_fond_parish_church`. Grundstück: `grand_fond_H04`, Grand-Fond, Mauritius. Katholische Pfarrkirche des Bourg für Gottesdienste, Gemeindetreffen, Vorbereitung des Klerus, Glockendienst und einen zugänglichen Turmausblick. Möbelstil: **authority**.

Grundstück 30 × 42 m; Abstände vorne/hinten 3 m, seitlich 1,5 m; bebaubare Fläche 27 × 36 m; höchstens drei Geschosse. Haupteingang zur Straße auf −Y. Dunkler Basalt, helle gotische Einfassungen, zentraler Eingangsturm, rote Metallbedachung, Strebepfeiler, farbige Spitzbogenfenster, Uhr und Kuppellaterne bleiben die prägenden Merkmale der Referenz.

## Abmessungen und Konstruktion

- Hauptkörper 17,6 × 23,0 m; polygonale Apsis etwa 4 m zusätzlich nach hinten.
- Eingangsturm 6,8 × 6,4 m, teilweise mit dem vorderen Kirchenjoch überlappend.
- Geplante Gesamthülle einschließlich Vorsprüngen, Strebepfeilern, Treppen und Podesten 20,8 × 34,4 m. Quer auf dem Grundstück zentriert, vorderste Stufe 3 m hinter der Straßenbegrenzung.
- Boden z = 0; Fundament bis −0,20 m; fertiger Erdgeschossboden +0,60 m; Glockengeschoss +6,60 m; Ausblick +12,60 m. Hoher Kirchenraum bleibt ein Geschoss; Zwischenpodeste der Treppe sind keine zusätzlichen Nutzungsgeschosse.
- Seitenschiffe etwa 4,2 m lichte Höhe; Mittelschiff etwa 8 m; Hauptfirst etwa 11,5 m; Kuppelkreuz etwa 18,5 m Gesamthöhe.
- Außenwände 0,30 m, Innenwände 0,12 m, Geschossplatten 0,25 m.
- Steiles Satteldach über dem Mittelschiff; niedrigere Pultdächer über den Seitenschiffen; facettiertes Walmdach über der Apsis; geschlossene Metallkuppel. Rote Wellblechprofile, Rippen, Anschlüsse und Firstkappen als Geometrie, keine Dachziegel.

## Räume und Erschließung

| Ebene / Raum | Ursprüngliches Programm und Verbindung |
|---|---|
| EG Turmvorhalle | Etwa 3,2 × 5,8 m neben dem abgetrennten Treppenraum; Hauptdoppeltür von der Freitreppe; offenes Portal zur Kirche. |
| Mittelschiff | Etwa 8 × 16,4 m zwischen Arkaden; zwei Bankblöcke, 1,8 m Mittelgang, Querwege vorne und hinten mindestens 1,4 m. |
| Seitenschiffe | Je etwa 3,2 m breit; durchgehende Arkaden, seitliche Ausgänge und Fenster auf beiden Seiten. |
| Chor / Apsis | Altar, Lesepult, Chorgestühl; bodengleich zum Schiff; hohe Fenster in den freiliegenden Apsisflächen. |
| Sakristei | Etwa 3,2 × 4,8 m; Tür zum Chor und eigener Außenzugang; Gewänder, Vorbereitungstisch und Waschbecken. |
| Pfarrbüro | Etwa 3,2 × 3,6 m; ursprünglich über hinteren Gang erreichbar; Seitenfenster. |
| Lager | Etwa 2,4 × 3,0 m; hinterer Gang; kleines Fenster. |
| WC | Etwa 1,8 × 2,4 m; WC, Waschbecken, hohes Fenster; Zugang vom hinteren Gang. |
| Hinterer Gang | Mindestens 1,4 m breit; verbindet Seitenschiff, Büro, Lager und WC, ohne den Altarbereich durchqueren zu müssen. |
| Turmtreppe | Zugang aus der Vorhalle; gegenläufige Läufe zu allen drei Nutzungsebenen; belichtende Lanzettfenster. |
| Glockenraum +6,60 m | Etwa 3,2 × 5,8 m neben dem Treppenraum; Glockenplatzhalter, festes Tragwerk, freier Kontrollweg, paarige gotische Schallöffnungen mit Lamellen. |
| Ausblick +12,60 m | Ursprünglich Umgang um die Kuppel; Zugang durch eine Tür vom Treppenraum; umlaufende 1 m hohe Sicherung, freie Wege mindestens 1,4 m. |

Treppe: mindestens 1,2 m freie Laufbreite, Podeste mindestens 1,4 m; Steigung etwa 0,167 m, Auftritt 0,28 m; je 6 m Höhenunterschied vier Läufe mit neun Steigungen; mindestens 2,6 m Kopfhöhe. Eingang: vier Steigungen zu 0,15 m. Nebeneingänge erhalten eigene gebäudegebundene Stufen/Podeste. Die geneigten Dächer sind nur Wartungsflächen, keine Spielerterrassen. Fenster auf allen vier Fassaden und in sämtlichen Aufenthaltsräumen.

## Ursprüngliche Türliste

Alle Blätter separat, geschlossen, 50 mm dick, mit etwa 7 mm umlaufendem Spalt und Ursprung am Scharnier; Zargen Bestandteil der Architektur. Außen nach innen öffnend, innen in den Zielraum. Alle Maße sind geplante lichte Öffnungsbreiten.

| Knoten | Von → nach | Breite |
|---|---|---:|
| DoorLeaf_01a_L_in + DoorLeaf_01b_R_in | Eingangspodest → Vorhalle | zusammen 2,40 m, Höhe 2,80 m, festes gotisches Oberlicht |
| DoorLeaf_02_L_in | Westpodest → Westseitenschiff | 1,10 m |
| DoorLeaf_03_R_in | Ostpodest → Ostseitenschiff | 1,10 m |
| DoorLeaf_04_L_in | Hinteres Podest → Sakristei | 1,10 m |
| DoorLeaf_05_R_in | Chor → Sakristei | 0,90 m |
| DoorLeaf_06_L_in | Hinterer Gang → Büro | 0,90 m |
| DoorLeaf_07_R_in | Hinterer Gang → Lager | 0,90 m |
| DoorLeaf_08_L_in | Hinterer Gang → WC | 0,90 m |
| DoorLeaf_09_R_in | Vorhalle → Turmtreppe | 0,90 m |
| DoorLeaf_10_L_in | Turmpodest → Glockenraum | 0,90 m |
| DoorLeaf_11_R_in | Ausblick → eingehauster Turmaustritt | 1,10 m |

Einflügelige Außentüren 2,20 m hoch, Innentüren 2,10 m. Bewegungsraum und Wege bleiben frei.

## Ursprüngliches Platzhalterprogramm

- `hall` Vorhalle: bench ×2, notice_board, ceiling_lamp.
- `chapel` Schiff / Seitenschiffe: pew ×20, ceiling_lamp ×6, ceiling_fan ×4.
- `chapel2` Chor: altar, lectern, pew ×4, ceiling_lamp ×2.
- `store` Sakristei: vestment_cabinet ×2, preparation_table, chair ×2, basin, mirror, wall_shelf, ceiling_lamp.
- `office`: office_desk, office_chair, visitor_chair ×2, filing_cabinet, file_shelf, ceiling_lamp, ceiling_fan.
- `store2`: storage_rack ×2, ceiling_lamp.
- `bathroom`: wc, basin, mirror, towel_rail, ceiling_lamp.
- `hall2` hinterer Gang: ceiling_lamp ×2.
- `hall3` Turmtreppe: wall_lamp an jedem Podest.
- `hall4` Glockenraum: church_bell, wall_lamp.
- Ausblick: kein loses Mobiliar; feste Außenleuchte.

Zusätzliche Rollen: vestment_cabinet, preparation_table, church_bell. Typische Außenmaße: Kirchenbank 2,7 × 0,65 × 0,95 m; Altar 2,4 × 1,0 × 1,0 m; Schreibtisch 1,4 × 0,7 × 0,75 m. Nur geschlossene Boxen mit Material `placeholder`, keine ausmodellierten Möbel. Lokale X-Achse Breite, Y-Achse Tiefe, −Y Vorderseite; Position ausschließlich im Knoten, Drehung nur vertikal. Ursprung für Standmöbel auf dem Boden in der Grundrissmitte, für Wandstücke an der Wand in Montagehöhe, für Deckenstücke an der Decke. Hauptwege mindestens 1,2 m, Bedienflächen mindestens 0,9 m.

## Vollständige geplante Materialzuordnung

| Material | Oberfläche |
|---|---|
| basalt_masonry | Äußere Wandfelder, Strebepfeilerkörper, Apsis |
| basalt_dressed | Fundament-/Sockelsteine, Außentreppen, Podeste, Stufenkanten |
| rubble_pointing | Zurückliegende Mörtelfugen |
| new_limestone_pale_aged | Quaderkanten, gotische Portale, Fenstergewände, Maßwerk, Bänke/Stürze, Arkadensäulen und Kapitelle, Gesimse, Turmbrüstung, steinerne Kuppellaterne |
| limewash | Innere Wandfelder, Laibungen und Treppenraumwände |
| limestone_flag | Böden in Schiff, Seitenschiffen, Chor, Vorhalle und hinterem Gang |
| floor_tiles | Böden in Sakristei, Büro und WC |
| concrete_cast | Sichtbare Plattenkanten, Turmtreppe und Podeste, Lager-/Glockenraumboden, verdeckte Dachunterseiten und Fundamente |
| plaster_white | Flache Deckenunterseiten der Neben- und Turmräume |
| new_roof_metal_oxblood | Rote Wellblechflächen einschließlich sichtbarer Unterseiten, First-/Gratkappen und Anschlüsse |
| new_zinc_dome_aged | Kuppelblech, Falze und Metallschürze |
| white_peeling_timber | Dekorative Traufbretter, ausgesägte Friese, Sparrenenden und Untersichtbretter |
| wood_mahogany_varnished | Türblätter und Futter, sichtbare Kirchendachhölzer und Deckenbretter |
| painted_timber_warmgrey | Glockenlamellen und deren Rahmen, geschlossene Dachlüfter |
| galvanized_steel | Rinnen, Schwanenhälse, Fallrohre, Schellen und Nebenanschlüsse |
| steel_painted_worn | Türbänder/-griffe, Treppengeländer, Glockentragwerk, Uhrzeiger/-ziffern, Fenstergitter und Bleiruten, Kreuze und Leuchtengehäuse |
| new_clock_enamel_ivory | Uhrzifferblätter; Ziffern als separate erhabene Geometrie |
| new_lookout_waterproofing | Mineralisch beschichtete Ausblickfläche |
| glass | Klare und farbige, 8 mm dicke geschlossene Scheiben; ohne Textur |
| lamp_glass | Abdeckungen fester Außenleuchten |
| placeholder | Ausschließlich Möbelboxen; ohne Textur |

Farbglas aus einzelnen farbigen Scheiben und geometrischen Bleiruten, Vertexfarben unter einem Glasmaterial; keine aufgemalten Fenster. UV0 in Metern, 1 UV-Einheit = 1 m. Fallrohre an der Wand, Schwanenhals unter der Traufe und Schellen alle 1,5–2 m. Beschreibungen und Maßstab der fünf neuen Oberflächen bleiben in `note.txt` dokumentiert.

## Ursprünglich erklärte Abweichungen und technische Ziele

1. Maße und Innenräume sind mangels Aufmaß aus der Referenz abgeleitet und an das Grundstück angepasst.
2. Turm verbreitert, damit Vorhalle, gegenläufige Treppe, Glockenraum und Ausblick funktionieren.
3. Zwei Höhenintervalle zu 6 m erhalten die Turmproportionen bei drei Nutzungsgeschossen.
4. Ausblick erhält eine neue 1 m hohe Sicherung und eine echte Zugangstür.
5. Nebenräume liegen hinten unter untergeordneten Dächern.
6. Türen werden begehbar dimensioniert; Chor und Schiff bleiben bodengleich.
7. Vorplatz entfällt; nur gebäudeeigene Treppen und Podeste werden gebaut.
8. Die Figurennische bleibt leer; keine Menschenfiguren.
9. Alterung über reale Oberflächen; keine Vegetation oder modellierter Bewuchs.

Ziel: LOD0 etwa 130–150 Tausend Dreiecke; keine weiteren LODs, Kollisionen, Proxies, Terrain, Vegetation, Fahrzeuge oder lose Außenrequisiten. Geschlossene Festkörper mit echten Laibungen, Dachunterseiten, Profilen und Glasstärken; Details im Zentimeterbereich und darüber als Geometrie. Kleine Kantenfasen. Saubere verschweißte Geometrie, keine degenerierten oder doppelten Flächen; konsistente Außennormalen. Materialweise zusammengefasste Architektur; Türblätter und Platzhalter eigene Knoten. Modellierung in Metern/Z-up, Export glTF Y-up, Front +Z in glTF, Ursprung mittig auf Geländeniveau. Die endgültige Lieferung ist noch nicht freigegeben; dieser Branch ist ausschließlich eine Rettungskopie.
