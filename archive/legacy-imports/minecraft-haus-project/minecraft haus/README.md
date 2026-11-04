# 🏰 Minecraft Bergkamm-Herrenhaus & Kellergewölbe

> **Offizieller Server-Bauplan & Layer-für-Layer Web-Bauanleitung**  
> Angepasst für euer Multiplayer-Team auf dem Server.

---

## ⚡ Schnellstart

Öffne die interaktive Bauanleitung direkt im Browser:

```bash
./start_bauanleitung.sh
```

*Oder öffne einfach die Datei `index.html` mit Doppelklick in deinem Browser.*

---

## 📐 Projekt-Eckdaten & Welt-Position

| Eigenschaft | Wert |
| :--- | :--- |
| **Seed** | `-4815224116428668341` (Version 26.2 / 1.20+) |
| **Bauplatz-Koordinaten** | **X: -662 \| Y: 126 \| Z: 790** |
| **Teleport-Befehl** | `/tp @p -662 126 790` |
| **Grundriss** | 47 Blöcke Breite × 39 Blöcke Tiefe (Baugrenzen X: -685 bis -639, Z: 771 bis 809) |
| **Gesamthöhe** | 42 Blöcke (von Keller 3 Y=105 bis Dachfirst Y=146) |
| **Untergeschosse** | 3 Untergeschosse tief in die Bergwand geschlagen |
| **Frontausrichtung** | Süd-West (Facing: 220°) direkt zur Sonne (wie auf `image.png`) |
| **Rückseite** | Nord-Ost (Facing: 40°) Klippenkante mit überhängendem Infinity Pool |

---

## 🌟 Highlights & Sonderbauten

1. **Infinity Pool an der Klippen-Rückseite**:
   - Der Brunnen/Pool aus der Vorlage (`images.png`) vor dem Haus wurde entfernt, um eine freie Auffahrt mit Wendehammer zu schaffen.
   - Hinten ragt der Infinity Pool 7 Blöcke frei über den Steilabgrund des Bergmassivs hinaus.
   - Klarglasfront und Seelaternen-Beckenboden für spektakuläre Beleuchtung.

2. **Kupfergolem-Sortierhalle (Keller 1, Y ≈ 108)**:
   - Über 90 Doppelkisten (180 Kistenblöcke) in 4 Doppelreihen.
   - Gewachste Kupferblöcke, Laufbahnen und Kupferknöpfe für Kupfergolems.
   - Decken-Hopperlinie zur automatischen Materialverteilung.

3. **Enderperl-Stasis Relog-Teleporter (Keller 1, Y ≈ 109)**:
   - 7 Blöcke tiefe Seelensand-Blasensäule hält geworfene Enderperlen in der Schwebe.
   - Zuklappende Falltür aktiviert den Sofort-Teleport ins Haus bei schnellem Aus- und Einloggen.

4. **Villager-'Folterkeller' & Trading-Dungeon (Keller 2, Y ≈ 102)**:
   - 16 isolierte Handelszellen mit Arbeitsplätzen (Mending, Diamant-Rüstung etc.).
   - Zombie-Lore auf Schienenkreis + Piston-Schotten für kontrollierte Zombifizierung.
   - Braustand-Altar für Schwächetränke & Goldene Äpfel -> 1-Smaragd Dauerrabatte!

5. **Expansions-Katakomben**:
   - 4 vorbereitete Rundbogentore in Keller 2 für spätere Erweiterungen (Super-Smelter, Netherportal-Gewölbe, Brausaal, Minenexpress).

6. **Cliffside Chill Lounge & Glas-Balkon (Keller 3, Y ≈ 95)**:
   - Tief im Fels mit 16 Blöcke breiter Panorama-Glasfront direkt über dem Tal.
   - Schwebender Balkon mit Glasboden-Kassetten.
   - Tiefenschiefer-Kamin mit blauem Seelenfeuer (keine Brandgefahr für Holzdecken!).

---

## 🛠️ Enthaltene Features in der Web-App (`index.html`)

- **Interactive 2D Grid Layer Viewer**:
  - Jede Schicht einzeln durchschalten (-15 bis +16)
  - Schatten-Schicht (Ghost Layer) der darunterliegenden Ebene
  - Klickbare Blöcke zur Hervorhebung
  - Koordinatenanzeige (X, Z) und Block-Tooltip
- **Interactive 3D Isometric Model**:
  - 360° Drehung in 4 Winkeln
  - Schichtenschnitt-Slider
  - Echtes Voxel-Shading mit Sonnenlicht
- **Kategorisierter Material-Rechner**:
  - Genaue Stückzahlen, Stacks und Shulker-Kisten
  - Interaktive Checkliste mit Fortschrittsbalken (speichert automatisch in `localStorage`)
  - Filter nach Kategorien (Struktur, Dach, Holz, Glas, Kupfer, Redstone, Dungeon)
- **Redstone-Schaltpläne**:
  - Schritt-für-Schritt Anleitung für die Stasis-Kammer & Zombifizierung
- **Multiplayer-Bauphasen**:
  - 8-Tage Bauplan mit Rollenverteilung für das Serverteam
- **Referenzfoto-Galerie**:
  - Direkter Abgleich der Vorlage mit eurem Bauplatz
