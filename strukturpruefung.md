# Strukturprüfung · 5.26

Statisches Modell, geprüft über alle Hausblöcke (Außenanlagen und Gelände gelten als tragender Boden).

## Schwebende Bauteile

40 Gruppen von Blöcken ohne durchgehende Verbindung zum Fundament.

- 30 davon sind Treppenläufe der Halle mit nur Kantenkontakt der Stufen (in Minecraft stabil, optisch freitragend; bewusst so belassen).
- 10 sind Kronleuchter, Zaunpfosten der Bibliotheksbrüstung, Liftanzeige und Liftglas, die nur über Ketten, Eisengitter oder diagonale Kanten halten (Minecraft kennt dafür keine Statik).
- 0 weitere Befunde: keine.

## Fehlende Halterungen

0 Befunde bei Fackeln, Laternen, Ketten, Leitern, Türen, Teppichen, Redstone-Bauteilen: keine.

Korrigiert in 5.26: vier Kronleuchterketten der Bibliothek hatten ein Loch zur Decke.

## Erreichbarkeit

Begehbarkeit vom Hauptportal aus (Gehen, Einblockstufen, Treppen, Leitern, geschlossene Türen) über 39 Räume: alle Räume erreichbar. Niedrigste Abdeckung: Keller 1: Lager mit 209 von 241 Bodenzellen; der Rest liegt auf Möbeln, Regalen und Stufenkanten. Der Dachraum über der Bibliothek ist bei geschlossener Luke absichtlich nicht erreichbar.

## Licht

Blocklichtprüfung für alle begehbaren Bodenzellen der Räume (ohne Plateauzufahrt): 1327 Zellen ohne Blocklicht vor, 3 nach den Korrekturen (verbleibend: [[-695, 131, 770], [-693, 131, 775], [-692, 131, 775]]). Dunkle Zellen werden mit Standlaternen an Wänden und in Ecken behoben, nicht neben Türen, Treppen oder Leitern.

## Grenzen

Die Prüfung kennt Blocklicht, aber kein Himmelslicht. Wandmaterial aus der Bestandswelt außerhalb des Modells zählt als durchlässig. Redstone-Schaltungen und Kolbenbewegungen sind nur geometrisch geprüft, nicht im Spiel.
