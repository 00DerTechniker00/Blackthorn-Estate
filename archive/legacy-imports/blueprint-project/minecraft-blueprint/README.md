# Blackthorn Estate — Minecraft Blueprint Studio

Browserbasierter Architektur- und Bauplanungsentwurf für ein großes viktorianisch-gotisches Anwesen für sechs Bewohner.

## Starten

### Linux
```bash
chmod +x start.sh
./start.sh
```

### Windows
Doppelklick auf `start.bat`.

Danach `http://localhost:8000` im Browser öffnen.

Alternativ kann ein beliebiger statischer Webserver den Ordner bereitstellen. Es werden keine npm-Pakete oder externen Dienste benötigt.

## Projektvorgaben
- Seed (vom Nutzer angegeben): `-4815224116428668341`
- Bauanker: `X=-662, Y=126, Z=790`
- Vorgesehener Weltbereich: `X=-780..-645`, `Z=740..840`
- Architektur: Victorian / Gothic, Klippenanwesen
- Sechs private Gebäudeflügel plus zentrale Gemeinschaftsbereiche
- Survival-orientierte Materialauswahl

## Funktionen
- Übersicht und schematische axonometrische Konzeptansicht
- 2D-Grundrisse für sieben Ebenen (drei Keller, Erdgeschoss, zwei Obergeschosse, Dachgeschoss)
- Raum- und Flügelatlas
- Koordinatenanzeige je Raum auf Basis des Planungsrasters
- Materialübersicht mit Sammel-Markierungen
- Bauphasen-Checklisten
- Lokale Speicherung im Browser
- Fortschritt als JSON exportieren/importieren

## Wichtige Planungsgrenzen
Diese Version ist ein **Architektur- und Koordinatenentwurf**, noch kein fertiger Block-für-Block-Schematic-Export.

Die hochgeladenen MCA-Regionen und das Referenzbild wurden als Projektmaterial bereitgestellt. Die App enthält jedoch noch keine vollständige blockweise Geländeklassifizierung, keine geprüfte Klippenkante pro Koordinate und keine automatisch abgeleitete Fundament-/Aushubliste. Vor dem Aushub müssen die Grundstücksgrenzen, Höhen und tragfähigen Bereiche direkt in der Welt (oder mit einem vollständigen Terrain-Scan) bestätigt werden.

Die Weltversion wird in dieser App nicht als verifiziert festgeschrieben. Die zuvor übermittelte `level.dat` wurde als 26.3 interpretiert, während 26.2 als Zielversion genannt wurde. Bitte im Spiel/Server prüfen, welche Version tatsächlich läuft.

Materialmengen sind grobe Entwurfsbudgets, keine exakten Summen aus einer vollständigen Blockgeometrie. Der finale Blockplan sollte nach Freigabe des Grundrisses aus präzisen Layer-Daten generiert werden.

## Bedienung
- Links zwischen Übersicht, Grundrissen, Wohnbereichen, Materialien und Bauphasen wechseln.
- In „Grundrisse“ die Etage über das Dropdown wählen.
- Raster und Koordinaten lassen sich ein- und ausschalten.
- Material- und Bauphasen-Häkchen werden lokal gespeichert.
- Über „Fortschritt exportieren“ kann ein JSON-Stand geteilt werden. Das ist kein Live-Multiplayer.

## Dateien
- `index.html` — Oberfläche
- `styles.css` — Layout und Gestaltung
- `app.js` — Grundrisse, Raumdaten, Material- und Fortschrittslogik
- `referenzen/` — bisherige Referenzbilder aus dem Projekt
