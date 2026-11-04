# Blackthorn Estate — Bauatlas V7

Ein lokales, komplett offline-fähiges Webprojekt (nach Start mit einem lokalen HTTP-Server) mit nummeriertem, bearbeitetem Minecraft-Blueprint. Keine WorldEdit-/Litematica-Dateien nötig. Das Gebäude basiert auf den zuvor gelieferten Minecraft-Regiondaten und einer Höhenkarte; die Arbeiten sind ein Bauplan, **keine importierte oder im Spiel verifizierte fertige Welt**.

## Direkt starten

**Linux**: ZIP entpacken, im Terminal ins Verzeichnis `blackthorn-estate-v7` wechseln, `chmod +x start.sh`, danach `./start.sh`. Im Browser `http://localhost:8000` öffnen.

**Windows**: ZIP entpacken, `start.bat` doppelklicken, Browser `http://localhost:8000`.

**Ohne Startskript**: Im entpackten Projektordner `python3 -m http.server 8000` ausführen. Die Datei `index.html` nicht einfach direkt per `file://` starten; JavaScript-Module und JSON-Fetch benötigen einen Webserver.

## Umfang

- **50.560 eindeutige Blockkoordinaten**, nummeriert mit `#1` bis `#50560`, aufsteigend nach Y-Höhe, Bauphase und Koordinate.
- **50 Blockmaterialien**, **105 Baugruppen**.
- 3 Kellerebenen mit **18 nutzungsbezogenen Lager- und Arbeitszonen**; zusätzlich 10 markierte Haupt-/Privaträume.
- Neubearbeitete Durchgänge in den zentralen Kellerkorridoren, begehbare offene Speicherbereiche sowie eine konkrete Bestückung (Fässer, Truhen, Regale, eigene Nutzerlager, Schmelzerei, Alchemie, Verzauberung, Kartenarchiv, manuelle Farmannahme, Rüstungs-/Werkzeugbereich).
- Licht in den Kellerbereichen, private Suite-Einrichtung und Ergänzungen in Eingang, Küche und zentraler Halle.
- Zwei Geländeillustrationen: ein schematischer Render aus realen Gelände-/Blockkoordinaten und eine ausdrücklich **nicht blockgenaue** künstlerische Zielstimmung.

## Webseiten-Funktionen

**3D-Voxel**: Drehen (Ziehen), verschieben (Shift/Rechtsziehen), zoomen (Mausrad), über jeden sichtbaren Block hovern (Nummer + X/Y/Z + Material), anklicken (Blockinspektor). Einzellayer, Etagen, bis zur Höhe, das gesamte Haus sowie Baugruppenfilter. Die Nummern auf den Blöcken werden erst bei ausreichendem Zoom lesbar. Die Nummer ist in 2D, 3D, Bauanleitung und CSV identisch.

**2D-Plan**: Y-Ebene oder Stockwerkschnitt, Zoom, Koordinatenraster, Nummern im stark vergrößerten Raster, Hover-Informationen und Raum-/Lagerzonensprung.

**Bauanleitung**: Baublöcke nach aufsteigender Höhe, gefolgt von struktureller Bauphase und Baugruppe, einzeln mit Koordinaten und Blockstate. Suchfilter, 60 Einträge pro Seite, erledigt-Kontrollkästchen. Fortschritt wird im **Browser-Lokalspeicher** gespeichert und kann als JSON **exportiert und importiert** werden (identische V7-Version erforderlich). Das ist kein serverweiter synchroner Fortschritt.

**Materialien**: Blockanzahl und Survival-Itembedarf samt Shulker- und Stackmengen. Türhälften zählen als eine Tür (70 Tür-Items aus 140 Türblockpositionen); Betthälften als 11 Betten aus 22 Positionen; Betten sind nicht stapelbar, Schilder stapeln sich zu 16. Wasser ist **kein inventarisierbarer Block** – dafür wird eine Wasserquelle/Eimerlogistik empfohlen. Die CSV-Dateien `materialbedarf.csv`, `materialbedarf_baugruppen.csv`, `lager_materialbedarf.csv` und `blockliste.csv` sind enthalten.

**Raumprogramm**: Jedes der drei Kellerstockwerke enthält sechs besondere Funktionszonen (18 insgesamt). Klick öffnet die Zone im 2D-Plan.

## Wichtige Einschränkungen

1. Dieser Entwurf wurde **nicht in Minecraft gebaut und begangen**. Die Korridore der sechs Kellerzonen pro Ebene wurden im 2D-Grid auf Erreichbarkeit kontrolliert. Das ersetzt keine vollständige Pathfinder-/Kopffreiheits-/Kollisionsprüfung aller Bauteile und des gesamten Hauses.
2. Blockstates einiger komplizierter Blöcke (z. B. Verbindungseigenschaften von Glas, Kisten und Treppen oder die Ausrichtung der Einrichtung) sind Näherungen. Die 3D-Darstellung vereinfacht diese Geometrien.
3. Die Lageretiketten der Website sind **keine Schild-Blockentities mit Minecraft-Text**. Beim Bau Schilder selbst beschriften. Es ist ausdrücklich **kein automatisches Redstone-Sortiersystem**, sondern ein leicht zu bauendes, manuell beschriftetes Lager.
4. Die Materialrechnung erfasst geplante Block-/Itemzahlen, aber keine Werkzeuge, Gerüste, Abbauverluste, Reserve, Verbindungsmittel, mögliche Redstone-Verkabelung oder die Herstellung einzelner Gegenstände.
5. Der Geländerender nutzt die zur Verfügung gestellte Höhenkarte im Rechteck X -780…-645, Z 740…840; darüber hinaus wird die Plateauhöhe vereinfacht fortgeführt. Vegetation ist stilisiert und nicht aus den Regiondaten auf Blockebene rekonstruiert.
6. Minecraft-Serverversion: Überlieferte Angaben 26.2 und 26.3 widersprechen einander. Die exakte Paper-Version wurde hier nicht erneut geprüft. Bitte die IDs und Blockstates auf dem tatsächlichen Server verifizieren.

## Team-Aufteilung (sechs Spieler)

- A: Fundament, Stützmauern, Klippenabschluss
- B: Keller 3 und großes Materiallager
- C: Keller 2, Werkstatt und Spezialbereiche
- D: Keller 1, Lagertresen, Zugang und Eingang
- E: Haupthalle, Bibliothek, Ballsaal und Gemeinschaftsräume
- F: sechs Residenzen, Dächer, Terrasse und Außenanlagen

Die Bauanleitung ist zunächst vertikal nach Y sortiert. Innerhalb einer Höhe lassen sich Bauphasen und Baugruppen filtern, damit nicht alle Spieler dieselbe Reihe bearbeiten müssen. Fortschritt über Import/Export zwischen den Freunden abstimmen.

## Dateien

- `index.html`, `styles.css`, `js/*.js`: Website und Renderer
- `blueprint.json`: alle 50.560 Blockpositionen mit eindeutigen IDs, Materialien, Blockstates, Zonen und Metadaten
- `blockliste.csv`: eine Zeile pro Blockposition mit Bauphase und Lagerzone
- `materialbedarf.csv`: globale Materiallogistik inkl. korrekt berechneter Items bei Betten/Türen/Schildern
- `materialbedarf_baugruppen.csv`: Materiallogistik je Baugruppe
- `lager_materialbedarf.csv`: Materialbedarf je benannter Lagerzone
- `lagersystem.csv`: Name, Koordinatenbereich und Zweck der Lagerzonen
- `assets/site-preview.png`, `assets/mood-render.jpg`, `assets/terrain-heightmap.png`: Ansichten
- `tests/validate.mjs`: statische Konsistenzkontrolle
