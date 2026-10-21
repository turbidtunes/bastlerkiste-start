# Blender Building Kit – API für Claude und Entwickler

**Import in jedem generierten Stufenskript:**
```python
import building_kit as kit
```

Die Pipeline setzt den Ordner `scripts/blender_lib` auf `sys.path`.
Das ist bereits **vor** Ausführung des generierten Codes geschehen.
Benutze für Standard-Bauteile zuerst diese fertigen Funktionen. Schreibe
nur echte individuelle Architekturformen selbst mit `bpy`. **Keinen
weiteren Prompt-Compiler oder Architekturplan ausführen.**

## Sofort nutzbare Methoden

```python
# Rechteckiger Gebäudeumriss: (x0,x1,y0,y1), Front liegt an y0 / -Y.
kit.wall(
    "Wall_Front", (-6,6,-8,8), "front", 0.0, 3.5, 0.30,
    openings=[
        (1.3,2.6,0.0,2.2,"door"),   # u0,u1,sill,top,type
        (4.0,5.4,0.9,2.3,"window")
    ],
    surface="plaster_cream_warm"
)
# Seiten heißen: front, back, left, right. Die u-Offsets beginnen
# an der jeweiligen hlib-Fassadenstartkante. Reale Löcher, nicht aufgemalt.

kit.partition(
    "Partition_Sacristy", (0,2,0), (0,7,0), 0,3, .12,
    door_spans=[(1.0,2.0)], surface="plaster_white"
)
kit.slab("Floor0", (-6,6,-8,8), -.20, .22, "concrete_cast")
kit.box("Plinth", (-6,-8,-.2), (6,8,0), "mixed_fieldstone")

# Türposition ist exakt der reale Scharnierpunkt / Pivot an der UNTERSEITE.
# Das Blatt bleibt geschlossen und hat einen eigenen Node.
kit.door_leaf(1, hinge=(-4.7,-8,0), width=1.20, height=2.2,
              thickness=.05, hinge_side="L", opens="out",
              yaw_deg=0, surface="wood_mahogany_varnished")

# Fenster nur IN einer vorher ausgeschnittenen echten Wandöffnung:
kit.window("NaveWindow01", centre=(-2.4,-8,1.65),
           width=1.2, height=1.5, yaw_deg=0,
           frame_surface="painted_timber_warmgrey")

# Platzhalter mit Origin am Fußpunkt, Front ist lokale -Y Richtung.
kit.placeholder("chapel","pew",1,location=(-2,-2,0),
                size=(2.5,.6,1.1),yaw_deg=0)

# Treppe in lokaler +Y Richtung; mindestens .28 Auftritt,
# höchstens .18 Stufenhöhe, mindestens 1.2 m Breite.
kit.staircase("Stair1",location=(3,1,0),rise_total=3.0,
              width=1.2,tread=.28,top_landing=1.4,yaw_deg=0)

# ZWEI geschlossene Dachhälften mit First parallel zur Y-Achse.
# Giebeldreiecke, Firsthauben, Dachziegel, Sparren individuell ergänzen.
kit.gable_roof("MainRoof", rect=(-6,6,-8,8),
               eaves_z=4.2,pitch_deg=32,thickness=.18,
               overhang=.3,surface="roof_terracotta")

# PBR-Material mit exakt erlaubtetem Namen; keine Bilderzeugung.
mat = kit.material("steel_painted_worn")
```

## Wichtige Qualitätsregeln

1. Bibliotheksobjekte sind gewöhnliche Blender-Meshes. Alle Methoden
   erzeugen **geschlossene geometrische Körper** mit Materialslot und UV0
   im Metermaß. Platziere durchgängig entsprechend dem verbindlichen Plan.
2. Die vorhandene `hlib.wall()`-Logik und `bldlib.MB` sind eingebunden.
   Der Adapter verzichtet bewusst auf das alte `weather_geo` (synthetische
   Alterung/Materialbilder), automatische Kollisionskörper und den historischen
   FBX/GLB-Export. Der **Controller** bleibt für Rendering, Export, Reimport
   und Qualitätskontrolle verantwortlich.
3. `kit.window()` erzeugt echte Fensterrahmen und Glasscheiben, aber
   **schneidet selbst keine Öffnung**. Das erfolgt mit `kit.wall(...openings=...)`.
   Unterschiedliche Winkel/Mauersysteme bei Sonderfällen mit eigenem Code lösen.
4. `kit.partition()` verwendet bei übergebenen `door_spans` feste
   2,1-m-Öffnungen des Altmoduls. Für abweichende lichte Höhen einen
   spezialisierten Wandbaustein schreiben.
5. `kit.gable_roof()` baut zwei volle geneigte und geschlossene Dachplatten,
   **nicht** die vollständigen Dachziegel/First- und Giebelkonstruktionen.
   Diese bei Gebäuden mit entsprechenden sichtbaren Details ergänzen.
6. Türblätter und `Ph_*` bleiben getrennte benannte Nodes. Generiere keine
   zusätzliche Tür als unbenannte Flächen auf der Fassade.
7. Eine Etage/Stage liest nur die gespeicherte .blend der Vorstufe.
   Bibliotheksfunktionen stehen durch den `import` in JEDER Stage erneut zur
   Verfügung. Niemals spätere Stufen durch ein `bpy.ops.object.delete` leeren.
8. Verwende exakte Materialnamen aus dem Bauprompt; reguläre Oberflächen
   erhalten **keine** eingebetteten Foto- oder prozeduralen Texturen. Falls
   `new_*` benötigt wird, muss die echte Foto-PNG bereits vorhanden sein.
9. Kein `kit`-Baustein ersetzt detaillierte Architekturplanung:
   Abmessungen, Räume und Referenztreue bleiben Aufgabe des Plans.
10. Wenn das Referenzbild ein Sonderbauteil zeigt, nutze die Library für
    Standardteile und erzeuge den individuellen Rest gezielt mit `bpy`.
    Nutze nur Bibliotheksoperationen, deren Geometrie zum Auftrag passt.

## Bewährter Vorbestand aus bastlerkiste

Folgende historische Module wurden unverändert aus
`turbidtunes/bastlerkiste` kopiert nach `scripts/blender_lib/legacy/`:
- `bldlib.py`: Meter-UV-Meshbuilder, Sweeps, Boxen, Profile
- `hlib.py`: Gebäudewände/Öffnungen, Dächer, Türen, Treppen
- `civlib.py`: zivile Fassaden-/Detailgeometrie
- `civplan.py`: Raum- und Öffnungszuordnung
- `interior.py`: Grundriss-Innenausbau
- `medwalls.py`: mediterrane Mauern/Balustraden
- `roles.py`: Placeholder → Einrichtungsstil

Die Originaldateien in `examples/` sind **Studierbeispiele**, keine direkt
auszuführenden Bau-Skripte. Die Kapelle und das Les-Calanques-Medhaus waren
besonders relevante Ausgangspunkte.

Direktimport historischer Generatoren wird im Produktions-Stage **nicht**
automatisch gemacht; sie sind teilweise für den alten Export-/Materialworkflow
geschrieben und dürfen die aktuellen LOD0- und Fototextur-Regeln nicht verletzen.

## Verifikation

Der kostenlose GitHub-Runner führt vor dem kostenpflichtigen Claude-Aufruf
`blender --background --factory-startup --python scripts/blender_lib/smoke_test.py`
aus und prüft die Bibliothek einschließlich GLB-Reimport.

Das ist ein **Funktions-Smoke-Test**, keine Garantie, dass jede gewünschte
Kirchenform oder jeder per Claude erzeugte Produktions-Build fehlerfrei ist.
