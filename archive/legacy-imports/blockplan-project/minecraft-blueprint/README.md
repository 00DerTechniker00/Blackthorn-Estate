# BLOCKPLAN — Bergkamm-Herrenhaus

Eine lokale, browserbasierte Blueprint-Workbench für euren Minecraft-Server. Kein Node.js, keine Installation und keine Desktop-Laufzeit erforderlich.

## Start

**Linux / macOS**
```bash
./start.sh
```
Dann `http://localhost:8000` im Browser öffnen.

**Windows**
```powershell
py -m http.server 8000
```
Dann `http://localhost:8000` öffnen.

Alternativ kann `index.html` direkt geöffnet werden. Für zuverlässiges Speichern und den Projektimport wird der lokale Server empfohlen.

## Projektkoordinaten

| Eigenschaft | Wert |
|---|---|
| Seed | `-4815224116428668341` |
| Minecraft-Version | `26.2` (Projektangabe) |
| Anker / Referenzpunkt | X `-662`, Y `126`, Z `790` |
| Grundriss-Raster | 70 × 50 Blöcke |
| Rasterbereich | X `-697` bis `-628`, Z `765` bis `814` |
| Layer | 37 Ebenen, Y `105` bis `145` |
| Gebäudehöhe im Blueprint | 41 Y-Ebenen |

Das Raster ist um den Ankerpunkt zentriert. X wächst nach rechts, Z nach unten im 2D-Grundriss. Jede Zelle steht für einen Block. Die Ebene Y=126 liegt bei Layer 17 (0-basiert gezählt).

**Wichtig:** Der Seed ist eine Welt-Referenz und kein Geländemodell. Die vorhandenen Screenshots/Referenzbilder sind keine verifizierte Ingame-Vermessung. Prüft vor dem Fundamentbau die tatsächliche Höhe, Hangkante und Ausrichtung in eurer Welt. Die bisherige automatische Ausrichtung auf Südwest wurde deshalb nicht als gesicherte Angabe übernommen.

## Funktionen

- 2D-Blockraster für jede einzelne Y-Ebene
- Isometrische 3D-Übersicht aus den vorhandenen Layerdaten
- Zoom, Verschieben, Raster und Koordinaten ein-/ausblenden
- Klick auf eine Zelle zeigt Blocktyp und Weltkoordinaten
- Materialliste mit Mengen, Stacks und rechnerischem Shulker-Bedarf
- Räume, Redstone-Anlagen und Bauphasen
- Fortschritt für Layer, Materialien und Bauphasen
- Projektfortschritt als JSON exportieren und auf einem anderen Rechner importieren

## Mit Freunden zusammenarbeiten

Die Website speichert den Fortschritt lokal im Browser. Über **Fortschritt teilen** exportiert ihr eine JSON-Datei. Schickt diese Datei in euren Discord- oder Server-Chat; die nächste Person importiert sie, arbeitet weiter und exportiert die aktualisierte Datei.

Das ist bewusst noch keine Live-Kollaboration: Zwei Browser synchronisieren sich nicht automatisch. Für echte gleichzeitige Zusammenarbeit wäre ein Backend (z. B. Supabase oder ein kleiner eigener WebSocket-Server) erforderlich. Die Anwendung ist bereits als statische Web-App gehalten und kann später ohne Neuentwicklung in Tauri verpackt oder auf einem Webserver veröffentlicht werden.

## Projektstruktur

- `index.html` — Oberfläche
- `styles.css` — Layout und Design
- `app.js` — Viewer, Navigation, Fortschritt und Import/Export
- `data.js` — generierte Blueprint-Layer, Materialmengen, Räume und Phasen
- `referenzen/` — ursprüngliche Bilder und Gelände-Referenzen

## Hinweise zum Blueprint

Die Layerdaten aus dem gelieferten Projekt wurden beibehalten, damit eure bisherige Hausplanung nicht verloren geht. Offensichtliche Metadaten-Widersprüche wurden korrigiert: Die 37 vorhandenen Bau-Layer liegen verteilt zwischen Y=105 und Y=145; die vertikale Spannweite beträgt 41 Koordinatenstufen, weil nicht jede Zwischenhöhe als eigener Bau-Layer definiert ist. Die alten Angaben 47×39 und 70×50 waren widersprüchlich; das tatsächlich generierte Raster in `data.js` ist 70×50 und wird hier als verbindliche Blueprint-Fläche verwendet.

Die Materialzahlen sind aus den Layerdaten berechnet. Bei Redstone-Schaltungen, Villager-Anlagen und Wassermechaniken können je nach Minecraft-Version/Serverregeln Anpassungen nötig sein.
