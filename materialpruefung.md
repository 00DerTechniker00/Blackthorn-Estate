# Block- und Materialprüfung · 6.0

## Positionen

138.225 eindeutige Baupositionen. 30 Türen auf Gegenhälfte, direkte Durchgänge und Boden geprüft. Befunde: 0 blockierte Nachbarzellen, 0 fehlende Türhälften, 0 Türen ohne Boden, 0 eindeutig frei hängende Schwerkraftblöcke. 0 Schwerkraftpositionen benötigen den lokalen Snapshot für eine vollständige Prüfung.

Korrigiert: zweite Wandlagen vor fünf K1-Türen geöffnet; die Südgartentür in die tatsächliche Außenwand bei Z 829 versetzt und mit der Freitreppe verbunden. Störenden Fassadenschmuck im Durchgang entfernt. Anschläge des westlichen Hauptportals nach außen gesetzt. Im übrigen Haus bleiben die bestehenden Architekturentscheidungen bestehen.

## Mengen nach Bereich

| Bereich | Items | Erde | Bruchstein |
| --- | ---: | ---: | ---: |
| Haus und Keller | 69.798 | 0 | 0 |
| Außenanlagen und Nebengebäude | 5.826 | 0 | 817 |
| Gelände und Auffüllung | 61.910 | 38.148 | 13.132 |

Die Gesamtmaterialliste enthält den vollständigen Zielplan einschließlich Gelände. Die Standardansicht im Atlas zeigt jetzt Haus und Keller; Außenanlagen und Gelände sind separat auswählbar. materialbedarf.csv bleibt die vollständige Gesamtplanung. Die zwei originalen Lager-Litematics und die Einrichtung mit Büchern/Rüstungen sind zusätzliche separate Listen.

Alle Erdblöcke im Blockmodell gehören zur Terraforming-Auffüllung. Die große Masse ist für das angehobene Plateau und dessen Bodendecke vorgesehen. 13.272 Bruchsteinblöcke liegen ebenfalls in dieser Auffüllung; die übrigen 817 in Wegen und Nebengebäuden. Diese Füllung wird nicht aus Kostengründen automatisch entfernt, weil sonst ihre Trag- und Geländeform geändert würde.

## Nachzählung und Packen

Die Itemmengen wurden unabhängig aus den Blockpositionen nachgerechnet und mit JSON und CSV verglichen. Türen und Betten zählen einmal; Flüssigkeiten und Kolbenköpfe sind keine zusätzlichen Items. Töpfe und Pflanzen werden getrennt, Wandbanner als Banner gezählt. Doppelte Platten würden zwei Items kosten; im aktuellen Modell sind keine vorhanden.

Behoben: Rest_nach_Shulkern enthielt bisher nur lose Einzelitems und unterschlug die verbleibenden ganzen Stacks. Jetzt gilt: Anzahl = volle_Shulkers × 27 × Stackgröße + Rest_nach_Shulkern. Banner werden mit 16 pro Stack gepackt. Die Blockzahlen werden dadurch nicht künstlich reduziert.

## Bestand und Wiederverwendung

Snapshot verfügbar: True. Die Vergleichsdatei zeigt nur, wo im alten gelieferten Weltstand derselbe Blocktyp steht. Daraus folgt keine Aussage über den heutigen Serverfortschritt. Die Erdmengen unterscheiden sich außerdem von der alten Auffüllungsliste, weil spätere Begrünungs- und Böschungsumbauten hinzukamen. Die ältere Auffüllungsliste ist kein zusätzlicher Materialauftrag und darf nicht zur Gesamtmaterialliste addiert werden.

Der historische Aushubplan nennt 34.081 Stein, 10.126 Erde und 5.097 Grasblöcke. Abgebauter Stein kann bei normalem Werkzeug Bruchstein liefern ([Mojang: Stein](https://www.minecraft.net/en-us/article/block-week-stone)); Gras kann Erde liefern. Das sind mögliche Wiederverwendungen, keine bereits geprüften aktuellen Lagerbestände oder garantiert zusätzlichen Erträge. Silktouch, Baufortschritt und spätere Änderungen beeinflussen die Bilanz.

Statische Blockprüfung, kein vollständiger Ingame-Lauftest. Redstone, Wasser und Spawn-Sicherheit nicht simuliert. Neue Füllung und Grabungslisten nicht als bereits erledigt voraussetzen.
