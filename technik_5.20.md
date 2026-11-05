# Technik und Inbetriebnahme · 5.20

Diese Module sind geometrisch modelliert. Eine Abnahme im laufenden Server ist noch offen.

## Bücherregal und Fluchtgang

Bodenhebel: X -696 / Y 106 / Z 775. Zwei klebrige Kolben und getrennte Repeater bewegen die beiden Bücherregalblöcke. Der Export zeigt den geschlossenen Zustand. Zum Test den Hebel ausschalten: Beide Regale müssen je einen Block nach Westen zurückfahren. Im freien Türfeld nach Süden zur Leiter abbiegen, bis zur Passage auf Boden Y 100 absteigen; weiter nördlich führt eine zweite Leiter bis zur unteren Zugangsebene Y 80. Der untere Gang endet in der drei Blöcke breiten Litematic-Servicelücke. Die Litematics selbst sind separat einzusetzen.

## Materiallift

Einwurfkiste: X -685 / Y 108 / Z 789. Ein Hopper speist den Dropper. Ein Subtraktionskomparator mit verstärkter Rückkopplung und Repeater taktet ihn, solange Items enthalten sind. Die Blasensäule liegt bei X -685 / Z 790 auf Seelensand Y 105. Der obere Wasserkanal führt über zwei Hopper zur Ausgabekiste X -683 / Y 131 / Z 792. Die bisherige trockene Wartungsleiter bleibt erhalten.

Zuerst Wasser und Seelensand prüfen, danach ein einzelnes Testitem einwerfen. Es muss im EG ankommen und der Taktgeber anschließend stehen bleiben. Danach mehrere Stacks und eine gefüllte Shulkerbox testen. Gefüllte Shulkerboxen werden als Item transportiert; die Anlage packt sie nicht aus. Bei voller Ausgabe läuft der Lift weiter; vor längerem Betrieb müssen Rückstauabschaltung und Anschluss an das Hauptlager ergänzt werden. Der Lift verbindet K3 und EG; automatische Abzweige auf K1/K2 sind noch nicht eingebaut.

## Poollicht

Hebel: X -657 / Y 130 / Z 787, neben dem Poolausgang. Er versorgt über den massiven Sockel die Leitung darunter. Zwei trockene Leitungszweige mit Repeatern steuern sechs Lampen in der Nord- und Südwand des Beckens. Der Export zeigt AUS. Alle sechs Lampen auf EIN und AUS prüfen; anschließend die trockenen Leitungskanäle und das unveränderte Schwimmbecken kontrollieren.

## Uferweg und Bau-Reihenfolge

Der 84 Positionen lange Weg endet an der vermessenen nordöstlichen Wasserfläche. Zuerst Geländeersatz und freiraeume_5.21.csv prüfen, dann Weg und Bootshaus errichten. Der NBT-Export enthält die ausgewiesenen Luftpositionen bereits. Vor dem ersten Lauf jeden Übergang und das Geländer vor Ort prüfen.

## Technische Quellen

[Mojang: Redstone Lamp](https://www.minecraft.net/en-us/article/block-week-redstone-lamp) beschreibt die Versorgung der Lampen durch Redstone und Repeater. [Mojang: Update Aquatic](https://feedback.minecraft.net/hc/en-us/articles/360007323492-Minecraft-Java-Edition-1-13-Update-Aquatic) dokumentiert Blasensäulen mit Seelensand bzw. Magmablöcken. Diese Grundlagen ersetzen keine Prüfung unserer konkreten Schaltungen.
