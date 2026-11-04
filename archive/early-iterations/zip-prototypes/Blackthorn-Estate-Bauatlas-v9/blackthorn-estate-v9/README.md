# Blackthorn Estate – Bauatlas V8

Die Website ist ein offline-fähiger, lokal über HTTP startbarer Bauplan. Das Blueprint hat **50,875 eindeutig nummerierte Blockpositionen**, 51 Materialien und 109 Baugruppen. Der Grundentwurf und das begehbare Lager aus V7 wurden erhalten.

## Start

Linux: `chmod +x start.sh && ./start.sh` im Ordner `blackthorn-estate-v8` ausführen. Windows: `start.bat` doppelklicken. Browseradresse: `http://localhost:8000`. Keine Mods, keine .schem-Dateien.

## V8 – Änderungen

- 28 geländebasierte Stützpunkte am westlichen Klippenrand, an gemessene Höhen angeschlossen; 245 neue Stützblöcke sowie weitere Gelände-/Sicherheitsdetails.
- 3D-Ansicht bietet zusätzlich den Schalter „Vermessenes Gelände“. Dieser ist in der Gesamtansicht sinnvoll und zeigt ausschließlich bekannte Höhenwerte; alle Terrainkacheln sind aus `blueprint.json` abgeleitet.
- Strukturblöcke erhalten beim näheren Zoom eine vereinfachte Fugen-/Holzmaserung. Treppen, Scheiben und Türen werden geometrisch wie in V7 angenähert. Es handelt sich **nicht um importierte Minecraft-Texturen**.
- Neues Gelände-Bild `assets/site-preview.png` auf Basis von echten Minecraft-XYZ-Positionen und der Höhenkarte, ohne erfundene Bäume. Es ist kein Ingame-Screenshot. Die Orange Linie zeigt das östliche Ende der bekannten Höhendaten.
- Verlässliche 2D-Übersicht `assets/terrain-survey-v8.png`: echte Geländehöhen als Zellen, Anwesen-Umfang, neue Stützen und östlicher unvermesserner Streifen.
- Neu nummerierte, vollständige `blockliste.csv`, regenerierte Item-/Materialtabellen und `fundament_stuetzen.csv`.
- Bauanleitung nach Y-Höhe, Hover XYZ, Material, Blocknummer, Häkchen und Fortschritts-Export aus V7 erhalten.

## Grenzen

**Wichtige Vermessungsgrenze:** Die mitgelieferten Höhen gehen nur bis X = −645; das Gebäude reicht bis X = −638. Für die östlichen 7–8 Blöcke fehlen im Datensatz gemessene Geländehöhen. V8 erfindet hier keine Oberflächen; vor dem Bau im Spiel die Kollision/Fundamente überprüfen.

**Die V8-Stützen sind gezielte Anschlüsse, keine vollständige Prüfung auf fehlende Träger.** Auch Treppenfreiheit, Item-/Blockstates, Schutzgeländer, alle Dachgeometrien und Höhlen wurden nicht vollständig in Minecraft simuliert. Vor einem großen Survival-Auftrag eine kleine Testbaufläche verwenden.

**Render-Genauigkeit:** Genaue XYZ-Positionen und gemessene Höhen stehen stilisiert gerenderten Materialien gegenüber. Ohne originale Texturatlas-Dateien und Minecraft-Rendering-Engine kann die Website keinen pixelidentischen Minecraft-Screenshot garantieren.

**Fortschritt:** Wegen der neu nummerierten IDs werden frühere V7-Fortschrittsdateien nicht automatisch nach V8 übernommen. Neu gesetzte Häkchen in V8 speichern sich lokal im Browser und können exportiert werden. Eine neue Version bitte als neue Baugrundlage benutzen.

## Ausführung für sechs Personen

A: Gelände, Stützen und Außenbau. B: Keller 3. C: Keller 2 und Werkstatt. D: Keller 1 und Lagerverwaltung. E: Gemeinschaftsräume und Eingänge. F: sechs Wohnflügel und Dach. Verantwortliche sollten vor dem Bauen die jeweilige Baugruppe und Y-Höhe im Browser filtern.

## Qualitätstests

Die JavaScript-Module wurden mit `node --check` geprüft. `npm test` kontrolliert alle Blockpositionen auf Dubletten, Blocknummern auf Reihenfolge und Materialien auf Plausibilität. Die V8-Website wurde mit Chromium im Inline-Modus gestartet: 3D-Canvas, Hover, 2D, Layer-Anleitung, Häkchen, Materialien sowie Terrain-Schalter funktionierten ohne JavaScript-Fehler. Das ersetzt nicht die Minecraft-Kontrolle vor Ort.


## V9 – Bauorganisation und Lagerbestände
- Website: Materialien → tatsächlich vorhandene Items eintragen; Fehlbestände für den noch offenen Bau werden dynamisch berechnet. Vorräte sind lokal und per JSON exportierbar.
- Bauanleitung: Phasenübersicht mit Warnungen bei begonnenen Folgephasen und offenen Vorarbeiten. Keine harte Sperre – sechs Spieler können parallel arbeiten.
- Blockinspektor: Auswahl direkt im 2D-Plan öffnen.
- Fachliche CSV-Testprüfungen erweitert.
- Noch keine automatische Anbindung an den Minecraft-Server, kein Nachweis von Statik oder realen Lagerkapazitäten. Die Terrain-Heightmap deckt nicht die gesamte östliche Baufläche ab.
