# Einrichtung und Liefergong · 5.22

## Dekoration im Spiel ergänzen

Der NBT-Export enthält weiterhin keine Entitäten und keine vorbefüllten Bücherregale. remise_bibliothek_5.22.mcfunction ergänzt in der Dimension des Anwesens zwei Rüstungsständer mit vollständiger Leder- bzw. Diamantrüstung und bestückt vier Bibliotheksregale mit 1, 2, 4 und 6 Büchern. Die Datei kann in eine vorhandene Java-Datapack-Funktion übernommen oder ihre Befehle einzeln ausgeführt werden. Es wurde nichts auf dem Server ausgeführt. Wiederholung erzeugt keine zusätzlichen markierten Ständer, setzt aber deren Ausrüstung und die vier Regalbestände auf den Plan zurück. Vor dem Aufruf müssen die zugehörigen Chunks geladen sein.

Rüstungsständer: X -743.5 / Y 126 / Z 764.5 sowie X -741.5 / Y 126 / Z 764.5. Regale: X -694, -691, -688 bei Y 106 / Z 778 sowie X -691 / Y 106 / Z 781. Sie ersetzen ausschließlich Dekorregale; Kolbenregale und Buchsteuerung bleiben unverändert. Die mcfunction ist eine Einrichtungsdatei, kein bereits installiertes Datapack.

## Gong testen

Die vorhandene Redstone-Lampe bei X -683 / Y 131 / Z 794 speist einen Repeater und einen Subtraktionskomparator. Ein verzögerter, auf 15 verstärkter Seitenzweig beendet den Ausgangsimpuls. Der Notenblock bei X -683 / Y 131 / Z 799 steht auf Gold; der Block darüber muss frei bleiben.

Mit leerer Kiste starten, ein Testitem einwerfen: einmaliger Ton. Weitere Items bei nichtleerer Kiste: kein neuer Ton. Kiste leeren: kein Ton. Nach dem Rücksetzen erneut ein Item einwerfen: neuer Ton. Danach eine gefüllte Shulkerbox bei zuvor leerer Kiste testen. Der Gong kann anhand dieser Inhaltsanzeige keine Shulkerbox von anderen Items unterscheiden. Funktion und Verzögerungen sind im Spiel zu prüfen.

## Außenanlagen

Drei Weinbergterrassen auf Y 125, 124 und 123. Seitlicher Treppenweg bleibt frei von Spalieren. Zwei Steglaternen liegen außerhalb der Wasserbucht. Bootsdurchfahrt und Spawn-Sicherheit bleiben vor Ort zu prüfen.

Quellen: [Mojang: gemeißelte Bücherregale](https://www.minecraft.net/es-es/article/chiseled-bookshelf) und [Mojang: Redstone-Komparator](https://www.minecraft.net/en-us/article/taking-inventory--redstone-comparator). Keine Abnahme unserer konkreten Schaltung.
