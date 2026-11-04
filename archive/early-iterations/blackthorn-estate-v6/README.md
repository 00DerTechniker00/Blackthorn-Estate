# Blackthorn Estate – Architektur-Explorer V6

Die Website zeigt das Cliffside-Anwesen blockgenau im Browser – ohne WorldEdit, Litematica, Vite, npm oder externe JavaScript-Bibliotheken.

## Start (lokal)

Linux:
```sh
chmod +x start.sh
./start.sh
```
Windows: `start.bat` doppelklicken.

Danach `http://localhost:8000` öffnen. Python 3 wird für den kleinen lokalen Webserver gebraucht. Das direkte Öffnen der `index.html` per `file://` funktioniert wegen der Browser-Sicherheitsregeln für `fetch`/ES-Module nicht zuverlässig. Internetzugriff ist nicht notwendig.

## V6 – neu an der Website

- `js/main.js`: initialisiert Oberfläche und koordiniert Eingaben.
- `js/data.js`: validiert den kompletten Bauplan vor dem Rendering (u. a. Block-IDs, Materialpalette, doppelte Weltkoordinaten) und baut Indizes auf. Verwendete Materialmengen werden aus den tatsächlichen Positionen neu berechnet.
- `js/store.js`: zentraler Ansichts- und Baufortschrittszustand; bestehende lokal gespeicherte V5-Häkchen werden weiterverwendet.
- `js/renderer-3d.js`: eigener Canvas-Voxelrenderer mit Layer-Schnitten, Sichtseiten-Verdeckung, vereinfachten Spezialblock-Geometrien, Blockauswahl und bedarfsabhängiger Zeichenanforderung. Für flüssige Gesamtansichten werden nicht anklickbare Detailflächen begrenzt; im Stockwerkmodus sind einzelne Blöcke anklickbar.
- `js/renderer-2d.js`: eigener 2D-Plan mit Raumschnitten, Einzellayer-Modus, Raster, Koordinatenbeschriftungen, Raumsprung und Detailauswahl.
- `js/panels.js`: Materialsummen, CSV-Downloads, koordinatenbasierte Suche, Baufortschritt.
- `js/utils.js`: gemeinsam genutzte Formatierungs-, Farb- und CSV-Hilfsfunktionen.
- Verbesserte mobile Navigation und CSS-Farbvariablen.
- Unveränderte V5-Baupositionen: **50.630 Blöcke** – V6 ist eine technische Website-Revision, keine neue bauliche Freigabe.

## Weshalb kein Build-Tool?

Für eine lokal entpackbare, sofort startbare Website ist ein moderner Modulaufbau mit nativen ES-Modulen ausreichend. Vite würde Installation und Toolchain voraussetzen; es brächte bei der Nutzung des fertigen Blueprints keinen entscheidenden Vorteil. Die Daten werden aus einer einzigen lokalen JSON-Datei geladen. CSV-Dateien werden **exportiert**, nicht importiert, sodass ein CSV-Parser nicht erforderlich ist.

## Genauigkeit

Der Entwurf ist nicht in einer Minecraft-Testwelt auf Kollisionen, Durchgängigkeit der Wege, Beleuchtung, Geländeverträglichkeit oder sämtliche Blockstate-Regeln geprüft. Treppen, Slabs, Glasscheiben, Türen und Möbel haben im 3D-Viewer angenäherte, nicht Minecraft-identische Geometrie. Es gibt keinen `.schem`- oder `.litematic`-Export. Die uneinheitliche Server-Version (26.2/26.3) ist weiterhin nicht geklärt.
