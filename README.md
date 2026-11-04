# Blackthorn Estate – Revision 5.3: Gelände & Untergrund

## Datenbasis
- Originale Minecraft-Region `r.-2.1.mca` aus `mca.zip`.
- Ausgewerteter Geländebereich: X=-765 bis -618, Z=735 bis 845.
- Verwendeter Bauplan: Revision 5.2.1 (Eingang Osten, Pool Westen).
- Boden = höchster fester Block je X/Z, ohne Pflanzen, Bäume und Wasser.
- Pflanzen = Blöcke oberhalb dieses Bodenblocks.
- Untergrund = senkrechte Luftspalten unter der Bodenoberfläche; keine garantierte Höhlenkonnektivität.

## Änderungen
- Eingangsvorplatz und Weg auf echten Boden abgestützt; Zugang weicht südlich aus, weil östlich bei Z≈789–790 die Kante abfällt.
- Gezielte Stützen unter vorhandenen Terrassenpositionen, nicht als durchgehende künstliche Wand.
- Eindeutig isolierte Außendekorationen ohne benachbarte Bauteile entfernt.
- Neue Website-Karte `Gelände & Höhlen` mit X/Z-Hover und Materialien; 3D-Gelände nutzt jetzt die vervollständigte, aus der Regiondatei ermittelte Höhenkarte.

## Status
53526 originale Positionen; 54150 Positionen nach Änderungen. Neue Positionen 624, ausgetauscht 0, entfernt 0.

## Einschränkungen
- Die sichtbare Grasoberfläche besteht überwiegend aus Grasblöcken; die Blumen wurden separat aus der Regiondatei erfasst.
- Höhlendaten sind Luftspalten in senkrechten Säulen, nicht automatisch zusammenhängende Hohlraum-Netzwerke.
- Die Geländeansicht ist blockbasiert und kein vollständiger Minecraft-Textur-Renderer.
- Minecraft-Licht, reale Begehbarkeit und bauliche Kollisionen wurden für die aktuelle Revision nicht vollständig im Spiel simuliert.
- Three.js wird weiterhin über das CDN der hochgeladenen Website bezogen: für 3D Internetverbindung nötig.
