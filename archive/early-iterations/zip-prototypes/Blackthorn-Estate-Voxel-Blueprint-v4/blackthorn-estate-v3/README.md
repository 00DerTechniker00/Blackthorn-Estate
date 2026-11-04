# Blackthorn Estate – Voxel Blueprint 04

## Starten
- ZIP entpacken.
- Linux: `chmod +x start.sh && ./start.sh`
- Windows: `start.bat`
- Browser: http://localhost:8000

Ein lokaler HTTP-Server ist erforderlich, da `blueprint.json` per fetch geladen wird.

## Revision 04
- Vollständige Blockliste mit eindeutigen X/Y/Z-Koordinaten.
- Lagerbereich erweitert: zusätzliche Fässer, Kisten, Regalböden, Sortierfläche und Beleuchtung.
- Materialbedarf global und je Baugruppe als CSV.
- Materialmengen zusätzlich als 64er-Stacks und Shulkerboxen (27 Stacks = 1.728 Items).
- 3D-Isometrie mit blockgenauer Einheitsprojektion, gemeinsamer Kantenlage und Tiefensortierung.
- 2D-Layerplan mit direkt aneinanderliegenden Rasterzellen und Gruppenfilter.
- Suche, Koordinatenabfrage und lokaler Baufortschritt.

## Wichtige Hinweise
Das Modell bleibt ein algorithmisch erzeugter Entwurf und wurde nicht automatisch im Minecraft-Client getestet. Die Blockpositionen sind eindeutig; Blockzustände (z. B. Ausrichtung von Fässern, Truhen, Treppen und Türen) sind nicht vollständig als Blockstates hinterlegt. Vor dem Survival-Bau bitte in einer Testkopie prüfen.

Anker: X=-662, Y=126, Z=790. Hauptfußboden: Y=129. Klippe: Westen (-X), Eingang: Osten (+X).
