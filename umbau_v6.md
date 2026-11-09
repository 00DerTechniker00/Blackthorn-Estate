# Kellerumbau · Haus auf Y 127

Der vorhandene Schachbrettboden bleibt auf Y 95 mit allen 2.397 Blöcken unverändert. Das alte Dustless-Lager ist entfernt. Seine Originaldateien dienen nur noch als Referenz; seine Blöcke zählen nicht zum aktuellen Materialbedarf.

Die aktuelle [Höhenplanung](keller_hoehenplanung.md) enthält fünf Kelleretagen mit 5 / 7 / 5 / 5 / 5 Blöcken freier Höhe von oben nach unten. Alle Geschossdecken sind einen Block dick. Böden von unten: Y 95, 101, 107, 113 und 121; EG-Boden Y 127. Obergeschoss Y 135, Dachbeginn Y 143. Das Haus und seine oberen Anschlüsse sind zwei Blöcke tiefer als im bisherigen Plan.

## Umsetzung

1. Fertigen Boden auf Y 95 schützen. Alte Lagerblöcke und nicht mehr passende Zwischendecken nach der aktuellen Umbau-CSV entfernen.
2. Neue Geschossböden Y 101, 107, 113 und 121 bauen. Leiter- und Wasserschächte einschließlich ihrer Austritte offen lassen.
3. Untere Geheim- und Nebenräume bleiben bei Y 96–100; der externe Abstieg und der Salon am Gang auf Y 80 bleiben erhalten.
4. Die freien Reservegeschosse liegen bei Y 102–106 und Y 108–112. Das Ersatzlager erhält freie Höhe Y 114–120 auf Boden Y 113. Noch keine Schaltung für das neue Lager modelliert.
5. Porter an der gesamten Nordwand auf Boden Y 121, freie Höhe Y 122–126. Bereich X −709…−659 / Z 767…780 bleibt frei. Chunkgrenzen bei X −704, −688, −672 und Z 768, 784, 800 beachten; jedes vollständige Portermodul muss passend geladen sein.
6. Haus, Poolterrasse und Gartenanschlüsse anhand des abgesenkten Hausmodells bauen. Bootshaus und Steg bleiben auf ihrer bisherigen Meereshöhe. Die Verbindung des Klippenpfads ist angepasst.

## Dateien und Prüfgrenzen

`keller_umbau_6.0.csv` und `materialbedarf_keller_zusaetzlich.csv` vergleichen mit eurem zuletzt gelieferten Kellerbestand. `blackthorn_estate_6.0.nbt`, `blockliste.csv` und die Materiallisten gehören zum aktuellen Zielmodell. Historische globale Geländeexporte beziehen sich auf den älteren Weltstand. Der Atlas zeigt die abgesenkten Zieloberflächen; Gelände vor Ort an den Bestand anpassen.

Durchgänge, vorhandener Boden, Lagerfreiraum, Leiter-Austritte und Wasserzugänge werden statisch geprüft. Fluidverhalten, Absturzschutz, Porter und Ersatzlager müssen im Spiel abgenommen werden. Die Automatik des Paper-Plugins lädt nach Deployment den aktuellen Bauplan; eine neue JAR ist dafür nicht nötig.
