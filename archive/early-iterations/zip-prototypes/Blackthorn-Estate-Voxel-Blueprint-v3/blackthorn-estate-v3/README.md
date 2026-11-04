# Blackthorn Estate – Voxel Blueprint 03

## Starten
- ZIP entpacken.
- Linux: `chmod +x start.sh && ./start.sh`
- Windows: `start.bat`
- Browser: http://localhost:8000

Ein lokaler HTTP-Server ist erforderlich, da `blueprint.json` per fetch geladen wird.

## Enthalten
- `blueprint.json`: 49.139 konkrete Blockpositionen, absolute Weltkoordinaten, Materialpalette, Layer und Gruppen.
- `blockliste.csv`: vollständiges Blockregister mit X/Y/Z und Minecraft-Block-ID.
- `materialbedarf.csv`: Materialmengen.
- 3D-Isometrie-Viewer mit Rotation, Zoom, Gruppenfilter und Y-Layer-Steuerung.
- 2D-Draufsicht je Y-Layer.
- Baugruppen-Fortschritt lokal im Browser.

## Wichtige Hinweise
Dies ist eine algorithmisch erzeugte, vollständige erste Konstruktion und kein bereits im Minecraft-Client getestetes Gebäude. Türen, Treppen, Dachdetails und Möbel sind teilweise als Block-Platzhalter umgesetzt. Vor dem Survival-Bau bitte die Baugruppen in einer Testkopie prüfen. Terrain-Höhen stammen aus den vom Nutzer bereitgestellten MCA-Heightmaps. Der Serverstand in `level.dat` wurde zuvor als 26.3 erkannt; die gewünschte Version 26.2 muss am Server geprüft werden.

Die Koordinaten im Modell sind absolute Weltkoordinaten. Anker: X=-662, Y=126, Z=790. Hauptfußboden: Y=129.
