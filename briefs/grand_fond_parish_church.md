# KONKRETER BAUAUFTRAG — Katholische Pfarrkirche Grand-Fond, Mauritius

**BUILDING:** Das **tatsächlich mit der API-Nachricht übermittelte Referenzfoto**. Wenn es in dieser Ausführung fehlt, ist `REFERENCE_IMAGE_MISSING = true`; verwende das folgende Programm für den Plan, aber behaupte keinerlei Bildvergleich oder spezifische Referenztreue.

**PLOT:** Slot `grand_fond_H04` in **Grand-Fond, Mauritius**; mauritisch-kreolischer Dorfkontext. Grundstück **30,0 m breit an der Straße (X) × 42,0 m tief (Y)**, bei Bedarf terrassiert. Straße und Hauptfassade im Süden / **−Y**. Grenzabstände: **3,0 m vorne**, **3,0 m hinten**, **1,5 m links und rechts**. Maximal zulässiger Footprint **27,0 × 36,0 m** (kleiner ausdrücklich erlaubt), maximal **3 Geschosse**; den Kirchturm in Geschoss-/Höhenkonzept ausdrücklich darstellen. Gebäudemittelpunkt für lokale Modellkoordinaten sinnvoll auf Fußabdruckzentrum setzen; Grundstücksplatzierung/Abstände numerisch im Plan nachweisen.

**USE:** **Katholische Pfarrkirche** für die Gemeinde Grand-Fond, mit **Kirchenschiff und Seitenschiffen, Chorraum, Sakristei, Glockenturm, echter Treppe zum Glockenraum und erreichbarem Aussichtspunkt, Eingangs-/Parvisstufen zur Straße**. Im Plan zusätzlich passende Nebenräume nur, soweit der Footprint dies sinnvoll erlaubt (z. B. kleiner Vorraum, Lager, WC). Kein Wohnprogramm erzwingen.

**FURNITURE STYLE:** exakt **`authority`**. Das ist eine öffentliche religiöse Einrichtung, kein Familienhaus.

**PRODUKTIONSZIEL:** UE5-LOD0, innen begehbar, sehr nahe an der tatsächlich gelieferten Referenz, falls vorhanden; plausible mauritisch-kreolische Bauart und Witterung. Alle Kirchenmöbel als maßhaltige **`Ph_*`-Boxen**, insbesondere `pew`, `altar`, `lectern`, plus sinnvolle liturgische/organisatorische Rollen für nicht aufgeführte Möbel. **Kirchturm und Aussichtszugang dürfen nicht nur dekorativ sein.** Wähle im Plan realistische absolute Maße und ein explizites `MAX_TRIS` (bis 150.000); unmittelbar danach ohne Rückfrage modellieren.

**AUFTRAGSSTART:** Planen → ohne Rückfrage modellieren → iterativ Blender rendern und korrigieren →
GLB validieren → fertige Datei in `inbox/grand_fond_parish_church/` committen.
Wenn kein echtes Bild in `reference_images` übergeben wird: KEIN Referenzvergleich behaupten.
