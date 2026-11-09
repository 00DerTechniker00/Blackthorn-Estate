# Garten und Gelände · Überarbeitung auf Hausboden Y 127

Die Verbesserung arbeitet auf den endgültigen, bereits abgesenkten Weltkoordinaten. Das Original-Höhenmodell bleibt erhalten. Der vorhandene Kellerboden auf Y 95, die Kellerhülle, der geheime Westzugang, Stall und Zufahrtsrampe sowie die neue Flussloggia bleiben geschützt.

## Was sich konkret ändert

- **Sichtbare Pflanzen statt verdeckender Geländehaut:** Im Südgarten wird die Zieloberfläche mit den echten Bodenblöcken abgeglichen. Einige Hecken waren im Höhenfeld zwei Blöcke zu hoch abgedeckt: tatsächlich Boden/Seelaterne Y 123, Laub Y 124, Höhenfeld Y 125. Die Darstellung folgt jetzt der Bodenhöhe; das Laub bleibt eigene Baugeometrie.
- **Weiche Rosenterrassen-Kante:** Direkt westlich und südlich der Pergola (etwa X −738…−727 / Z 845…851) entstehen kurze, mit Gras abgeschlossene Erdübergänge. Nur 17 kleine Spalten werden angehoben, maximal zwei Blöcke; kein großer neuer Erdwall und keine großflächige Klippenverfüllung.
- **Ruhigere Beete:** Die beiden vorhandenen Beetreihen bei Z 841 und Z 845 behalten Rasen als Untergrund. Weiße Margeriten und einzelne violette Allium setzen eine wiederkehrende Farbfolge. Pflanzlücken lassen Rasen und Wege lesbar.
- **Verdecktes Licht:** Acht Heckenpositionen bei X −699, −693, −687 und −681 / Z 840 und 846 erhalten bündige Seelaternen auf Y 123 unter bestehendem Eichenlaub. Sieben davon sind zusätzliche Leuchtblöcke; ein vorhandener wird übernommen. Es kommen keine Laternenpfosten hinzu.
- **Bankdetails:** Die beiden vorhandenen südlichen Bänke bei Z 850 erhalten vier schlanke, hochgeklappte Dunkeleichen-Falltüren als Armlehnen. Sie ersetzen die breiten Platten an den Enden; Sitzflächen und freie Zugänge bleiben erhalten.
- **Freie Wege:** Eine Blume auf dem steinernen Ende der Gartentreppe bei X −697 / Y 124 / Z 841 entfällt. Vorhandene Kieswege werden auf Pflanzhindernisse und feste Unterfütterung geprüft.

Die Funktion bearbeitet nur den lokalen Südgarten und die Rosenterrasse. Orangerie, Kupferpavillon, Weinbergkonstruktion, Pool und Hausfassade werden nicht umgebaut. Der Stallkorridor X −755…−740 / Z 762…790 sowie die Flussloggia X −658…−623 / Z 782…788 sind ausdrücklich ausgespart.

## Nachvollziehbarkeit und Prüfung

`tools/landscape_estate_v6.py` liefert alle geänderten Zielspalten, die örtlichen Erdarbeiten, das Materialdelta und die geprüften Wegpositionen zurück. Original-Höhenwerte und geschützte Baupositionen werden vor und nach dem Eingriff verglichen. Die neue Zielhöhe und der Zielblock jeder berührten Geländespalte müssen einem echten Block im Modell entsprechen. Die betroffenen Gartenwegzellen müssen unterfüttert und frei von Blumen sein.

Das ist eine statische Prüfung des Bauplans. Sie ersetzt keine Prüfung von Lichtausbreitung, Spawnregeln oder Laufverhalten im Spiel. Die endgültigen Gesamtmaterialmengen und der globale Geländearbeitsbericht werden bei der Zusammenführung des gesamten Hausumbaus neu erzeugt.
