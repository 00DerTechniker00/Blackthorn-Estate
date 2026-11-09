# Plateauanschluss und geschlossene Kelleransicht

## Fehlende Erdseiten

Die Hausmaske begrenzt das Gelände auf die Höhe unter dem Fußboden. Außerhalb des tatsächlichen Kellers bleibt dieses Erdreich geschlossen – auch wenn die darüberliegenden Hausgeschosse in einer Schnittansicht ausgeblendet werden. Nur die echte Kellerhöhlung und die westliche Zugangsnische werden oben ausgespart. Zwischen einer flachen Hausausspartiefe und dem tiefen Kellerausschnitt müssen weiterhin vertikale Erdflächen sichtbar sein. Genau diese fehlten nach der letzten Erweiterung der Maske.

Der Renderer unterscheidet echte Hohlräume von massivem Boden unter einem Gebäude. Außerhalb der Hohlräume zeichnet er auch die korrekt abgesenkte Oberseite, damit keine schwarzen Hausgrundrisse entstehen. Zusätzlich vergleicht er die tatsächlichen Schnitthöhen beider Nachbarn. Er zeichnet auch zwischen zwei maskierten Spalten den nötigen Erdabschluss. Die Seiten liegen minimal hinter dem Mauerwerk, damit die realen Mauerblöcke im Vordergrund bleiben. Die echten Öffnungen zum Geheimgang und zur Flussgalerie sind aus diesen Flächen ausgeschnitten.

Die Kellerwände selbst waren vollständig vorhanden. Es wurden weder Fenster zugemauert noch der fertige Boden auf Y 95 verändert. Tests prüfen den gesamten 214 Kanten langen Außenabschluss, einen vollständig umlaufenden Hausmaskenring und die weiterhin offene Flussgalerie.

## Sanfter Rand statt abgesenkter Ringkante

Nach dem Absenken des Anwesens um zwei Blöcke blieb die ursprüngliche Außenkontur stehen. Neue zwei bis drei Blöcke hohe Kanten entstanden dort, wo vorher nur eine flache Geländestufe lag.

Das neue Übergangsband reicht bis zu acht Blöcke nach außen. Nur vorher sanfte, natürliche Gras-/Erdbereiche an den neu entstandenen Kanten werden bearbeitet. Direkt am Rand werden höchstens zwei Blöcke abgetragen, weiter außen einer; der Rand läuft ins unveränderte Gelände aus. Natürliche Steilhänge, Wasser, Wege, Gebäude und modellierte Bepflanzung sind ausgenommen. Im Band erfolgt keine Auffüllung. Originalhöhen bleiben als Vergleich erhalten.

Die genaue Zahl der bearbeiteten Spalten und der Abtrag stehen unter `terrain_blend` in `ausbau_pruefung_v6.json`. Die neue Grasoberfläche, Aushub-Freiraumpositionen und Arbeitslisten gehören zum selben Zielmodell.

## Kleiner Altgraben am Westfundament

Ein gesonderter, bereits älterer Graben bei X −715…−711 / Z 790…814 lag teilweise auf Y 118 unter dem Hausboden Y 127. Der neu gelieferte Weltstand zeigt dort tatsächlich fehlende Erde. Hier genügt reine Renderkorrektur nicht: 104 Spalten werden bis Y 126 lokal unterfüttert. Die Unterfütterung reicht an jeder Stelle bis zum im neu gelieferten Weltstand nachgewiesenen tragfähigen Grund hinab. Die daraus berechneten zusätzlichen Erdpositionen stehen getrennt vom Abtrag des äußeren Übergangsbands im Prüfbericht; die 104 Stützbasen und die Quellenprüfsumme sind dokumentiert.

Diese Unterfütterung bleibt außerhalb des gebauten Kellers. Kellerboden Y 95, Kelleretagen, Porterzone, Treppen, Wasserzugänge, Flussgalerie und die wiederhergestellte Hauptzufahrt bleiben erhalten. Die Änderungen betreffen den Bauplan und verschieben keine Blöcke automatisch auf dem Server.
