# Gemeinsame Überarbeitung des Anwesens

Drei getrennte Fachprüfungen für Licht, Garten/Gelände und Stall/Architektur wurden mit der neuen Flussgalerie zu einem Bauplan zusammengeführt. Alle Angaben verwenden echte Weltkoordinaten des aktuellen V6-Modells.

## Licht

Störende Boden-Notlaternen im EG und OG entfallen. Verdeckte Quellen mit flachen Abdeckungen halten Laufwege frei; verankerte Tisch-, Sockel- und Hängeleuchten bleiben als Gestaltungselemente erhalten. Auch der neue Dachlesesaal ist geprüft. [Befunde und Lichtprüfung](beleuchtung_v6.md).

## Garten und Gelände

Lokale Zieloberflächen folgen wieder den echten Bodenblöcken unter Hecken und Beeten. Sanfte Erd-/Grasränder fangen kleine Terrassenversätze auf. Geordnete Blüten, verdecktes Heckenlicht und schlanke Bankdetails ergänzen den Südgarten; Kieswege und Treppen bleiben frei. [Gartenarbeiten](garten_gelaende_v6.md). Aktuelle Oberflächen: `gelaende_aktuell_v6.csv`, nach Chunks: `gelaende_chunks_v6.csv`. Der zugrunde liegende globale Weltstand ist historisch; der aktuelle Kellerbestand wird separat ausgewertet.

## Stall und Hausarchitektur

Ein breiterer Stall mit zwei großen Boxen, unterstütztem Mittelgang, Toren, Tränken und einer angepassten Zufahrt ersetzt die enge alte Einrichtung. Hinter dem Westgiebel entsteht ein Lesesaal mit Zugang von der Nordgalerie. Gezielte Fassadenprofile ergänzen die bestehende viktorianische Hauptform. [Stall, Fassade und Dachgiebel](architektur_v6.md).

## Flussaussicht

Aus Keller 3 auf Boden Y 107 führt eine geschlossene Galerie unter der Poolterrasse nach Osten. Der Gang endet in einer seitlich und frontal verglasten Loggia. Der vorhandene Fels und kurze Stützpfeiler tragen das auskragende Ende. [Baufolge und Koordinaten](flussloggia_v6.md).

## Erhaltene Grundlagen

Der fertige Boden Y 95 bleibt mit allen 2.397 Blöcken unverändert. EG-Boden Y 127, Obergeschoss Y 135, Kellerböden Y 95 / 101 / 107 / 113 / 121 bleiben bestehen. Der sieben Blöcke hohe Ersatzlagerraum bleibt frei, ebenso die nördliche Porterzone. Haupttreppe und Wasserzugänge bleiben vorhanden. Pferde, Golems und Rüstungsständer werden nicht als gebaute Entitäten vorgetäuscht.

## Prüfungen

`ausbau_pruefung_v6.json` dokumentiert lokale Prüfungen von Durchgängen, Pferdewegen, Stützen, Lampenankern, Blocklicht und Geländeoberflächen. `keller_pruefung_v6.json` prüft die Wege vom Hauseingang bis in die Kellerbereiche. `materialpruefung.md` prüft Materialmengen und Türen. Übersicht: `assets/ausbau_v6.png`.

Das ist keine vollständige Ingame-Simulation. Reiten mit Sattel und Reiter, Toröffnung, mögliches Überspringen von Zäunen, echte Wasserphysik, dynamische Beleuchtung und Spawnverhalten werden bei der Abnahme auf eurem Server geprüft.
