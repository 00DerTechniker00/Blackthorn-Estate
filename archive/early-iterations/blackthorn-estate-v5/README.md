# Blackthorn Estate – Architektur-Explorer Revision 05

## Start

1. ZIP entpacken.
2. Im entpackten Ordner unter Linux `./start.sh` ausführen (ggf. vorher `chmod +x start.sh`), unter Windows `start.bat` doppelklicken.
3. `http://localhost:8000` im Browser öffnen.

Die Website funktioniert nach dem Entpacken lokal ohne Cloud-Konto und benötigt keine Minecraft-Mods oder Schematic-Dateien.

## Neue Funktionen

- Überarbeitete Voxelblockliste mit Treppenverbindungen zwischen Keller 3, Keller 2, Keller 1, Erdgeschoss, Obergeschoss und Dachgeschoss.
- Zweiter Treppenlauf für einen Teil des Hauses; Eingang und zusätzliche Durchgangstüren mit Türhälften und Orientierung.
- Fassadenfenster, Fensterrahmen, Strebepfeiler und Simsdetails.
- Erweiterte Deckenbeleuchtung und Kronleuchter.
- Sechs möblierte Wohnflügel, Lager/Arbeitsraum, Bibliothek und Ballsaal.
- Dachkanten mit Treppen und Slabs; das Modell stellt die tatsächliche Form dieser Spezialblöcke im Renderer vereinfachend als Würfel dar.
- 3D-Ansicht: drehen, zoomen, verschieben, nach Etage oder Baugruppe filtern, Blockdetails klicken.
- 2D-Etagenplan: die sechs Geschosse einschließlich Wänden/Einrichtungsblocks im Schnitt, Raumbezeichnungen, Klick auf Koordinaten, Zoom.
- Vollständige CSV-Blockliste mit Blockstates, Materialien global und nach Baugruppen, Stack- und Shulkerlogistik.
- Lokaler Baufortschritt.

## Genauigkeit und Grenzen

Dies ist ein umfangreicher konzeptioneller Blockplan, aber kein in einem Minecraft-Testserver vollständig auf Kollisionen, Treppen-Kopffreiheit, Mob-Spawn-Bedingungen, Raumverbindungen, Material-State-Support und exaktes Gelände validierter Bau. Die visualisierten Treppen, Slabs, Glasscheiben und Türen werden als voxelartige Würfel dargestellt, ihre Blockstates sind in der CSV hinterlegt. Alle Blockpositionen sind eindeutig. Die vorhandene Terrain-Höhenkarte erfasst Oberflächenhöhen, nicht alle unterirdischen Räume oder Höhlen. Die früheren Minecraft-Versionsangaben 26.2 und 26.3 widersprechen sich, deshalb vor dem Bau auf dem Paper-Server überprüfen.

Anker: X=-662, Y=126, Z=790. West = Klippe, Ost = Eingang.
