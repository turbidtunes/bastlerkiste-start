1. IDENTITÄT
- Name: `les_calanques_fischerhaus`, Slot `les_calanques_H08`, Les Calanques (Mallorca). Nutzung: traditionelles Fischerhaus, EG Bootsgarage mit Werkbank, Lager und Hauseingang mit Innentreppe, OG abgeschlossene Wohnung. `furniture_style` = `spanish_trad`.
- Bildquelle: fiktive, vom Nutzer beauftragte Codex-Referenz `ref_les_calanques_H08_h_fisher_house.png`, kein reales Gebäude.
- Bildbeobachtungen:
  - Kompakter Kubus mit sehr flachem Walmdach aus Hohlziegeln, Halbrundrinnen vorn und links, Fallrohr vorn rechts.
  - EG aus ockerbeigem Kalkstein-Bruchmauerwerk mit Quader-Einfassungen, OG aus warmem Kalkputz.
  - Zweiflügeliges, segmentbogiges Bootstor aus blaugrünem, gealtertem Holz mit Bandbeschlägen. Daneben links eine schmale Fußgängertür.
  - Metallbalkon mit Steinplatte und drei Konsolen über dem Tor, dahinter Balkontür mit Lamellenläden. Rechts daneben ein Fenster mit Lamellenläden.
  - Seitenfassade (links/West) mit je einem Lamellenfenster im EG und OG.

2. GRUNDSTÜCK
- Plot 16,0 (X) × 23,0 (Y), Plotmitte = (0,0). Straße bei Y=−11,5, Vorderseite −Y. z=0 = Gelände = EG-Oberkante.
- Baufenster: X ±6,5, Y ±8,5 (13,0 × 17,0). Ursprung = Mitte des Gesamt-Footprints auf z=0.
- Hauptkörper Außenkante: X −5,25..+5,25, Y −5,0..+6,0 (10,5 × 11,0).
- Gesamt-Footprint (Dach, Rinnen, Balkon, Schwelle): X −5,75..+5,75, Y −6,50..+6,50 (11,5 × 13,0).
- Höhen: Fundament −0,20, First-OK z=8,72.
- Grenzabstände: seitlich 8,0−5,75 = 2,25 ≥ 1,5 ✓. Straße 11,5−6,5 = 5,0 ≥ 3,0 ✓. Hinten 11,5−6,5 = 5,0 ≥ 3,0 ✓. Footprint 11,5×13,0 ⊂ 13×17 ✓.

3. GESCHOSSE/ROHBAU
| Ebene | z-Bereich | Anmerkung |
|---|---|---|
| Fundamentring + Bodenplatte | −0,20..0 | Ring 0,05 über Außenwand überstehend, Bodenplatte innen, UK −0,20 |
| EG | Boden 0, lichte Höhe 3,20 | Decke UK 3,20 |
| OG-Platte | 3,20..3,42 | 0,22 stark |
| OG | Boden 3,42, lichte Höhe 2,80 | Decke UK 6,22 |
| Deckenplatte unter Dach | 6,22..6,44 | 0,22 stark, Wand-OK 6,44 |

- Außenwände 0,30, Innenwände 0,12. Stein (EG) bis z=3,42, darüber Putz. Kalkstein-Gesimsband z 3,22..3,42, 0,04 vorstehend (Balkon-Konsolen sitzen darunter).
- Tragende Linien: Außenwände plus Trennwand X −1,20..−1,08 (EG und OG deckungsgleich). Keine doppelhohen Räume.

4. RÄUME (Raum-ID | Geschoss | X-Grenzen; Y-Grenzen | Z/lichte Höhe | Nutzung | verbunden mit)
- `hall` | EG | X −4,95..−1,20; Y −4,70..2,80 | 0/3,20 | Flur, Foyer, Treppenhaus | D02 außen, D03 Garage, D04 WC, D05 Lager, Treppe OG
- `garage` | EG | X −1,08..4,95; Y −4,70..5,70 | 0/3,20 | Bootsgarage mit Werkbankzone, freie Fläche | D01 außen, D03 Flur
- `bathroom2` (WC) | EG | X −4,95..−3,30; Y 2,92..5,70 | 0/3,20 | WC | D04 Flur
- `store` | EG | X −3,18..−1,20; Y 2,92..5,70 | 0/3,20 | Lager | D05 Flur
- `hall2` | OG | X −4,95..−1,20; Y −1,98..3,00 | 3,42/2,80 | Flur, Podest, Treppenaustritt | Treppe, D07, D08, D09, D10
- `bathroom` | OG | X −4,95..−1,20; Y −4,70..−2,10 | 3,42/2,80 | Wohnungsbad (3,75 × 2,60) | D07
- `living` | OG | X −1,08..4,95; Y −4,70..0,90 | 3,42/2,80 | Wohnraum, Balkon | D08, D06 Balkon, D11
- `kitchen` | OG | X −1,08..4,95; Y 1,02..5,70 | 3,42/2,80 | Küche mit Esstisch | D09, D11
- `bedroom` | OG | X −4,95..−1,20; Y 3,12..5,70 | 3,42/2,80 | Hauptschlafzimmer (3,75 × 2,58) | D10
- Zwischenwände: Y 2,80..2,92 (EG Nord), Y −2,10..−1,98 (Bad), Y 0,90..1,02 (Wohnen/Küche), Y 3,00..3,12 (Schlafzimmer), X −3,30..−3,18 (WC/Lager).
- Kein zweites Schlafzimmer, weil Raumbreiten (<2,40 m) es nicht tragen.

5. ERSCHLIESSUNG
- Hauseingang: Stein-Schwellenplatte X −3,85..−2,15, Y −5,30..−5,0, Oberkante z=0, bündig fundiert. Bootstor ebenerdig.
- Innentreppe `hall` → `hall2`: gerader Lauf in der Westflucht, X −4,95..−3,75 (1,20 breit), massiv aus Stein, bis zum Boden fundiert.
  - Antritt Y=−2,90, 20 Steigungen × 0,171, 19 Auftritte × 0,28, Austritt Y=2,42.
  - Unteres Podest: Flur Y −4,70..−2,90, 1,80 tief.
  - Oberes Podest: Flur `hall2`, 2,55 breit.
  - Deckenöffnung OG-Platte: X −4,95..−3,75, Y −1,35..2,42. Kopfhöhe an der Kante 2,17 ≥ 2,10 ✓.
  - Geländer h=1,00 an der Ostseite der Treppe (X=−3,75, Y −1,35..2,14) und an der Südkante der Öffnung (Y=−1,35).
  - Der Lauf hat keine Zwischenpodeste, siehe Abschnitt 11.
- Balkon: Platte X −0,70..3,30, Y −6,50..−5,0, z 3,17..3,37 (0,20), 0,15 in die Wand eingebunden.
  - 3 Konsolen (B 0,30, Ausladung 0,60, z 2,95..3,17) bei X −0,25, 1,30, 2,85. Gewölbeband-Oberkante des Tores bei 2,90, also ≥5 cm Abstand.
  - Geländer z 3,37..4,42 (≥1,00), Stäbe 0,02 × 0,02 im Raster 0,12, Handlauf 0,04 × 0,04, Pfosten 0,04 × 0,04, lückenlos rund um 3 Seiten.
- Hauptwege ≥1,20, Flure ≥1,40 ✓.

6. TÜREN (Blatt 40–60 mm, Fuge 5–10 mm, Pivot auf Scharnierachse, Blatt geschlossen; L/R aus Zielseite gesehen)
| Name | von→nach | Ort | lichte B×H | Scharnier/Öffnung |
|---|---|---|---|---|
| `DoorLeaf_01a_L_in` + `DoorLeaf_01b_R_in` | außen→Garage | Front Y=−5,0, X −0,30..2,90 | 3,20 × 2,50 (Kämpfer; Scheitel 2,70, Segmentbogen) | a Scharnier +X (x=2,90), b Scharnier −X (x=−0,30), nach innen |
| `DoorLeaf_02_R_in` | außen→Flur | Front, X −3,50..−2,50 | 1,00 × 2,15 | Scharnier −X, nach innen |
| `DoorLeaf_03_L_in` | Flur→Garage | X=−1,14, Y 0,05..0,95 | 0,90 × 2,10 | Scharnier +Y, in Garage |
| `DoorLeaf_04_R_in` | Flur→WC | Y=2,86, X −4,57..−3,67 | 0,90 × 2,10 | Scharnier +X, ins WC |
| `DoorLeaf_05_R_in` | Flur→Lager | Y=2,86, X −2,65..−1,75 | 0,90 × 2,10 | Scharnier +X, ins Lager |
| `DoorLeaf_06a_L_in` + `DoorLeaf_06b_R_in` | Wohnen→Balkon | Front Y=−5,0, X 0,60..2,00 | 1,40 × 2,25 (z 3,42..5,67, verglast) | a Scharnier +X (x=2,00), b Scharnier −X (x=0,60), nach innen |
| `DoorLeaf_07_L_in` | Flur OG→Bad | Y=−2,04, X −2,95..−2,05 | 0,90 × 2,10 | Scharnier +X, ins Bad |
| `DoorLeaf_08_L_in` | Flur OG→Wohnen | X=−1,14, Y −1,40..−0,50 | 0,90 × 2,10 | Scharnier +Y, ins Wohnen |
| `DoorLeaf_09_L_in` | Flur OG→Küche | X=−1,14, Y 1,55..2,45 | 0,90 × 2,10 | Scharnier +Y, in Küche |
| `DoorLeaf_10_L_in` | Flur OG→Schlafzimmer | Y=3,06, X −2,20..−1,30 | 0,90 × 2,10 | Scharnier −X (x=−2,20), ins Schlafzimmer |
| `DoorLeaf_11_L_in` | Wohnen→Küche | Y=0,96, X 3,45..4,35 | 0,90 × 2,10 | Scharnier −X, in Küche |

- Türrahmen, Laibungen und Schwellen sind Gebäudeteile. Jede Türöffnung hat Anschlag und Laibung in der Wandstärke.

7. FENSTER/FASSADEN
- Alle Fenster: geschlossene Doppelflügel, Glas 8 mm, Rahmen 0,06 × 0,07, Sprossen 0,03, Quadereinfassung 0,22 breit mit Sturz und Sohlbank (0,05 vorstehend). Alle Fenster mit festen, geschlossenen Lamellenläden (je Flügel 10–12 echte Lamellen, Scharnierbeschläge). Fensterproportionen folgen der Referenz (Abschnitt 11).
- Front (−Y), EG: nur Tor und Tür. OG: Balkontür-Einfassung 1,90 breit, Läden aufgeklappt an der Wand (je 0,70, X −0,40..0,30 und 2,30..3,00). `F-OG-1`: X=4,10, 1,00 × 1,35, Sohlbank z 4,37, Wohnen.
- West (−X), EG: `W-EG-1` Y=−3,8, 1,00 × 1,30, Sohlbank z 1,10, Flur. `W-EG-2` Y=2,35, 1,00 × 1,30, Sohlbank z 1,10, Flur. `W-EG-3` Y=4,30, 0,70 × 0,90, Sohlbank z 1,50, WC.
- West (−X), OG: `W-OG-1` Y=−3,4, 0,90 × 1,20, Sohlbank z 4,62, Bad. `W-OG-2` Y=0,5, 1,00 × 1,35, Sohlbank z 4,37, Treppenlicht über der Öffnung. `W-OG-3` Y=4,40, 1,00 × 1,35, Sohlbank z 4,37, Schlafzimmer.
- Ost (+X), EG: `E-EG-1` Y=−2,0 und `E-EG-2` Y=1,2, je 1,20 × 1,10, Sohlbank z 1,30, Garage.
- Ost (+X), OG: `E-OG-1` Y=−1,9, 1,20 × 1,35, Sohlbank z 4,37, Wohnen. `E-OG-2` Y=3,4, 1,00 × 1,35, Sohlbank z 4,37, Küche.
- Nord (+Y), EG: `N-EG-1` X=0,6, 1,20 × 1,10, Sohlbank z 1,30, Garage. `N-EG-2` X=−2,2, 0,80 × 0,80, Sohlbank z 1,60, Lager.
- Nord (+Y), OG: `N-OG-1` X=−3,0 (Schlafzimmer), `N-OG-2` X=0,6 und `N-OG-3` X=3,4 (Küche), je 1,00 × 1,35, Sohlbank z 4,37.
- Rahmenmaterial siehe Abschnitt 9.

8. DACH & SONDERBAUTEN
- Walmdach über Footprint X ±5,75, Y −5,50..6,50 (Überstand 0,50 rundum). First-Achse Y, X=0, Y 0,25..0,75.
- Traufe z=6,45 (Ziegel-OK am Rand), First-OK z=8,72. Neigung ca. 21,5° auf allen vier Flächen. Massiver Keilkörper 0,20 stark mit geschlossener Unterseite, Hohlraum nicht begehbar.
- Echte Ziegelreihen (Mulden- und Deckziegel, Reihenabstand 0,30 entlang der Fläche), Firstziegel und 4 Gratreihen aus `terracotta`.
- Sparrenköpfe 0,10 × 0,08 alle 0,60 am Rand, Traufbohle und Untersicht (Soffit) geschlossen.
- Halbrundrinnen Ø 0,12 an allen vier Traufen.
- 2 Fallrohre Ø 0,09, wandnah (Achse 0,05 von der Wand), mit Schwanenhals von der Rinne:
  - vorn rechts bei (4,90, −5,06),
  - Westwand hinten bei (−5,31, 5,60).
  - Schellen auf z=0,5, 2,1, 3,7, 5,3.
- Eingefasster Fußgängertür- und Tor-Rahmen (Stein, 0,35 breit) mit Bogenstein, Eckquader (Kalkstein-Eckverband) an allen vier Ecken.
- Bandbeschläge am Tor (je Flügel 3 Bänder 0,05 × 0,60 breit), Türdrücker, Fensterladen-Beschläge, Lampen innen.

9. MATERIALIEN
| Bauteilgruppe | Slot |
|---|---|
| EG-Außenwand, Fundament | `new_limestone_rubble_ochre` |
| Quader-Einfassungen, Eckquader, Gesimsband, Sohlbänke, Stürze, Balkonplatte, Konsolen, Schwelle | `new_limestone_dressed_ochre` |
| OG-Außenwand, Dachuntersicht-Putz | `plaster_cream_warm` |
| Dachfläche | `roof_terracotta` |
| First-/Gratziegel | `terracotta` |
| Bootstor- und Haustür-Blätter | `new_teal_weathered_planks` |
| Lamellenläden | `shutter_paint` |
| Fensterrahmen, Sprossen | `paint_clean` |
| Türrahmen innen, Sparrenköpfe, Soffit, Dachhohlraum | `painted_timber_warmgrey` |
| Innentürblätter | `oak_honey` |
| Balkongeländer, Beschläge, Treppengeländer, Lampengehäuse | `steel_painted_worn` |
| Rinnen, Fallrohre, Schellen | `galvanized_steel` |
| Verglasung | `glass` |
| Lampenschirme | `lamp_glass` |
| Garagenboden | `concrete_cast` |
| Flurboden, Treppe, Eingangsschwelle | `limestone_flag` |
| Bodenbeläge OG | `floor_tiles` |
| Bad-Wände bis 2,10 | `ceramic_glazed_white` |
| Innenwände, Decken (Wohnbereich) | `plaster_white` |
| Garage, Lager (Wände, Decke) | `limewash` |
| Möbel | `placeholder` |

- Fehlende `new_*`:
  - `new_limestone_rubble_ochre`: ockerbeiges Kalkstein-Bruchmauerwerk mit Mörtelfugen, Kachel 2,0 × 2,0 m.
  - `new_limestone_dressed_ochre`: behauener ockerfarbener Kalkstein, feine Werkzeugspuren, Kachel 1,6 × 1,6 m.
  - `new_teal_weathered_planks`: gealterte blaugrüne Holzbretter (0,15 breit) mit abblätternder Farbe, Kachel 1,2 × 1,2 m.
- UV0 überall metrisch (1 UV = 1 m).

10. PH-PLACEHOLDER
- Alle Rollen mit genau einem Namen `Ph_<room>_<role>_<nn>`, Origin Mitte Bodenfläche, Richtung nur über Z-Rotation. Freie Abstände ≥0,90 vor Türen, Bett, Schrank, Küche und WC; Hauptwege ≥1,20.
- `hall` (EG): coat_rack 1, shoe_cabinet 1, ceiling_lamp 1.
- `garage`: workbench 1 (2,0 × 0,70 × 0,90, Nordwand), tool_wall 1 (darüber), storage_rack 2 (Ostwand Y 3,4..5,0), ceiling_lamp 2. Mittelfläche ≥3,5 m breit frei. Kein Boot.
- `bathroom2` (EG-WC): wc 1, basin 1, mirror 1, ceiling_lamp 1.
- `store`: storage_rack 3 (Ost- und Westwand ab Y 3,9), ceiling_lamp 1.
- `hall2`: console 1 (0,35 tief), ceiling_lamp 1.
- `bathroom`: wc 1, basin 1, mirror 1, shower 1, washing_machine 1, towel_rail 1, laundry_basket 1, ceiling_lamp 1.
- `living`: sofa 1, armchair 1, coffee_table 1, sideboard 1, bookcase 1, ceiling_lamp 1. Nichts vor Balkontür und Fenstern.
- `kitchen`: kitchen_run 1 (3,0 m mit Spüle, Nordwand), cooker 1, fridge 1, kitchen_table 1, kitchen_chair 4, wall_shelf 1 (Ostwand, Y 1,2..2,4), ceiling_lamp 1. Tür-Schwenkbereiche D09 und D11 frei.
- `bedroom`: bed_double 1 (Kopf Westwand), bedside 2, wardrobe 1 (Ostwand ab Y 4,1), **genau ein `Ph_bedroom_gun_cabinet_01`** (Nordwand), ceiling_lamp 1. Schwenkbereich D10 frei.

11. REFERENZABWEICHUNGEN & RISIKEN
- Referenz-Eingangsstufe: Boden liegt bei z=0 auf Gelände, daher ebenerdige Schwelle statt Stufe.
- Balkontür-Läden: in der Referenz geschlossen, hier aufgeklappt an der Wand (Zugang bleibt möglich).
- Fensterproportionen folgen der Referenz (kleiner als 1,00 × 2,10); die Mindestmaße gelten für Türen.
- Zusätzliche Fenster an Ost- und Nordseite (in der Referenz nicht sichtbar) für Kreuzlüftung.
- Walmdach hat nur 0,5 m First, fast pyramidal wie im Bild.
- Treppe: ein gerader Lauf mit 20 Stufen ohne Zwischenpodest (Lauflänge 5,32 m), Podeste nur unten und oben.
- Schlafzimmer eng (3,75 × 2,58): Platzierung gegen Tür-Schwenkbereich prüfen.
- Gerüstreferenz fiktiv, keine Aussage über reale Gebäude. Gewölbte Torleibung: Bogen-Schnitt muss sauber an `new_*`-UV anschließen.
- Bau blockiert, bis alle drei `new_*`-PNGs real vorliegen.

12. BAUPHASEN
- SHELL: Fundament, Bodenplatte, Außen- und Innenwände mit echten Öffnungen (Tor-Segmentbogen, Laibungen), Decken, Treppenöffnung, Deckenplatte.
- ARCHITECTURE: Walmdach mit Ziegelreihen, Treppe, Balkon, Rinnen und Fallrohre, Einfassungen, Fenster- und Türrahmen, Glas, Läden, Türblätter mit Pivots.
- DETAILS: Beschläge, Geländer, Lampen, Materialzuordnung, metrische UV0, Placeholder und finale Benennung.

13. MAX_TRIS: 100000

PLAN_COMPLETE