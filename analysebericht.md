# Architektur, Lager und Erdarbeiten · Revision 5.8

## Entwurfsrichtung

Auf Nutzerwunsch ist der Entwurf ein ruhigeres viktorianisches Herrenhaus. Die hohe
Observatoriumskuppel und die hohen Eckturmaufsätze entfallen. Stattdessen gibt es
eine klare Haupthalle, zwei etwas niedrigere Wohnflügel, eine quer dazu angeordnete
Bibliothek und den eingeschossigen Ostflügel mit niedrigem Eingangsvorbau.
Durchlaufende Gesimse, ruhigere Steinflächen und zwei kleine Schornsteine verbinden
die Baukörper. Die vier vorhandenen Erker bleiben erhalten und werden niedrig gekappt.

Die Dachkörper sind gemeinsam als Höhenhülle berechnet, damit Überschneidungen nicht
erneut massive Füllvolumen erzeugen. Die Hülle hat eine Unterdeckung und eine obere
Treppen-/Stufenschicht. Innere Dachböden erhalten untere Holzstufen. Die tatsächlichen
Mengen und Firsthöhen stehen in `check_report.json` und der Blockliste. Eine aktuelle
Lichtsimulation gibt es weiterhin nicht; Spawnfreiheit wird nicht zugesichert.

## Lagerplanung und Kapazität

Der zweite Keller wurde östlich des bestehenden Verzauberungsraums geöffnet.
Die westliche Treppe und der zentrale fünf Blöcke breite Gang bleiben erhalten.
50 Buchten enthalten je zwei Fässer nebeneinander auf vier Höhen: acht Fässer bzw.
216 Inventarplätze pro Bucht. Zusammen 400 Fässer / 10.800 Plätze. Quergänge führen
zu jeder Fassfront; die Rückseiten werden als geordnete Regalrücken aus Holz gebaut.

Im dritten Keller gibt es zusätzlich sechs persönliche Buchten mit je acht Fässern:
48 Fässer / 1.296 Plätze. Das Sortierlager in Keller 1 bleibt erhalten.
Die neuen Buchten ersetzen ältere Einrichtung und einige kleine Lager; ihre 12.096
Plätze sind deshalb die Kapazität der neuen Buchten, nicht der Nettozuwachs des
gesamten Anwesens. Die Gesamtkapazität wird aus allen tatsächlich vorhandenen
Fass-, Truhen- und Kupfertruhenblöcken mit je 27 Inventarplätzen berechnet.

Kategorien, ID und Kapazität sind im Bauatlas dokumentiert. Fassbeschriftungen sind
keine fertig befüllten Schild-NBT-Daten. Alle neuen Lagerbuchten sind manuell zu
befüllen. Die bestehende Redstone-/Golemsortierung ist weiterhin als Technikentwurf
zu verstehen; mehr Lagerkapazität macht daraus keine bereits getestete Schaltung.

Die neue Prüfung benutzt eine 2D-Flutsuche auf der tatsächlichen Kellerbodenhöhe,
mit zwei freien Blöcken über dem Boden. Sie kontrolliert Wege zu allen 56 Buchten
und freie Fronten aller 448 Fässer. Das ist eine lokale geometrische Prüfung der
Lageretagen, keine vollständige Spielerbewegungs-/Treppen- oder Interaktionssimulation.

## Erweiterte Weltvermessung

Originalquelle: `mca.zip`, Region `r.-2.1.mca`. Der Ausschnitt reicht von
X=-805 bis -585 und Z=705 bis 875, insgesamt 37.791 Säulen gegenüber vorher 16.428.
Die obere tatsächliche feste Oberfläche wird gelesen; Blumen, Gräser, Holzstämme und
Blätter werden beim Bestimmen des Bodens ausgelassen. Menschliche Bauwerke können
als Oberfläche erhalten bleiben. Höhlenluft in Baugruben wird nicht als Stein gezählt.

In der 3D-Ansicht wird der gleiche vermessene Ausschnitt als Höhenfläche dargestellt:
Original, geplante Geländeoberfläche oder geplante Oberfläche mit Arbeitsfarben.
Damit sind Hangkanten und Höhenübergänge erkennbar; die 3D-Fläche zeigt jedoch keine
vollständigen Höhlen und keine exakten unterirdischen Materialschichten.

## Abtrag und Auffüllung

Die Baugrube folgt dem Kellerrechteck und endet unter der Bodenplatte bei Y=104.
Unter dem übrigen Hauptbaukörper liegt der Unterbau bis Y=128. Westterrasse und Pool
bekommen keine pauschal angehobene Klippe; ihre bisherigen Stützen bleiben erhalten.
Nord und Süd erhalten schmale Böschungsübergänge. Sichtbare Sockelkanten werden mit
Tiefenschieferziegeln gefasst. Die Zufahrt verläuft fünf Blöcke breit über den
südöstlichen Plateaustreifen; Höhenänderungen erfolgen als Stufen im Zielgelände.

Die Abtragliste nennt vorhandene Nicht-Luft-Blöcke, die entfernt werden müssen.
Zusätzlich werden Kollisionen einzelner Baupositionen mit dem Originalboden geprüft,
damit auch einzeln versenkte Fundamente unterhalb des Zielniveaus erfasst werden.
Identische vorhandene Materialien an Baupositionen werden wiederverwendet und nicht
als Abtrag gezählt. Die Auffüllliste enthält alle Zielpositionen oberhalb des
vermessen natürlichen Bodens, einschließlich vorhandener modellierter Tragblöcke.
Diese Positionen stehen auch in der Blockliste; sie sind keine zusätzliche Menge
außerhalb der Gesamtmaterialliste. Oberflächenwechsel auf derselben Höhe können
Abtrag und eine neue Oberfläche erfordern, ohne dass Gelände in der Höhe wächst.

Vegetation oberhalb des Bodens wird separat ausgewiesen. Vorhandene Eisen-/Beacon-
Marker und andere betroffene Baucontainer stehen in `bestandskonflikte.csv`.
Es wird ausschließlich ein Plan erzeugt; die Minecraft-Welt wird nicht verändert.

Die Arbeitslisten sind an den gelieferten Weltstand gebunden. Nach späteren
Änderungen im Spiel müssen die Mengen und vorhandenen Bauwerke erneut abgeglichen
werden. Stützwände, Böschungen, Wasserführung und Anschlüsse sind vor Ort zu prüfen.

## Daten, Fortschritt und Prüfgrenzen

Alle Positionen, Mengen, Gruppensummen und CSVs werden aus einem Modell erzeugt.
Die Revision hat einen eigenen Modellfingerabdruck und Speicherbereich für
Fortschritt. Alte Häkchen werden nicht auf verschobene oder entfernte Blöcke übertragen.
Der lokale Atlas benötigt kein CDN und kann per `index.html` geöffnet werden.

Die Software-Vorschauen wurden aus genau den Geometrien des Viewers berechnet.
Sie dienen der Entwurfsprüfung und werden als Modellvorschau gekennzeichnet.
Der Browserstart ist hier wegen gesperrter Betriebssystem-Sockets nicht möglich;
es liegt kein bestätigter GPU-/Browser-Sichttest vor. Die Anwendungsskripte werden
mit dem vorhandenen DOM-/Canvas-Testadapter auf Navigation, Datenfilter, Backup,
Kameras und Geometrieaufbau geprüft. Ein Ingame-Test steht weiterhin aus.
