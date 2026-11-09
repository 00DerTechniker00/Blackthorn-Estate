# Pool und Garten · V6

## Pool

Der bestehende Beckenplatz und die tragenden Klippenbögen bleiben Grundlage. Das Hauptbecken (X −651…−641 / Z 780…800) besitzt jetzt eine durchgehende Wasseroberfläche auf Y 127, passend zum angrenzenden Terrassenbelag auf Y 127 (Oberkante Y 128). Die westliche Beckenkante erhält einen fünf Blöcke breiten, zweistufigen Einstieg mit wassergefüllten Quarztreppen. Die Wasserphysik muss im Spiel nach dem Bau kontrolliert werden.

Der Beckenboden auf Y 124 besteht aus dunklem Prismarin mit hellerem Prismarinrahmen und sechs eingelassenen Meereslaternen. Diese zusätzlichen Unterwasserleuchten sind dauerhaft an; die bestehende separate Pool-Lampenschaltung wird nicht als Steuerung dieser Blöcke ausgegeben.

Die Terrasse wird durch ruhige Sandsteinflächen und dunkle Steinbänder gegliedert. Je drei kleine Holzsitzbänke stehen an den Nord- und Südenden, ergänzt um niedrige Beistelltische. Der zentrale Durchgang vom Haus zum Wasser bleibt frei. Geländer, Panoramabalkon und die bestehenden Pool-Stützen bleiben erhalten.

## Südgarten

Westlich der Orangerie entsteht auf X −736…−728 / Z 841…849 eine kompakte Blütenterrasse. Sie wird auf Y 123 ausnivelliert und über einen drei Blöcke breiten, gestuften Anschluss mit dem vorhandenen nördlichen Kiesweg verbunden. Eine offene Pergola aus dunklem Holz rahmt die Sitzbank; die Mitte bleibt begehbar. Blumenstreifen liegen seitlich, Meereslaternen unter niedrigen Laubpolstern sorgen für Licht ohne zusätzliche Laternenmasten.

Die vorhandenen Kieswege und Gartentreppen werden freigehalten. Die Blumenreihen südlich des Hauses werden außerhalb dieser Wege ergänzt. Orangerie, Weinberg, Pavillon und Keller werden nicht durch die neuen Pflanzflächen überbaut.

## Atlas und Mengen

Unter **Hausstruktur → Pool und Garten** führen zwei Buttons direkt zu den neuen Ansichten. Unter **Gelände** ist die Pergola als eigener Außenbereich auswählbar. `assets/aussen_v6.png` zeigt einen aus den tatsächlichen Blöcken erzeugten Oberseitenplan.

Blockliste, Haus-NBT und Materiallisten enthalten die neuen Blöcke. Die neuen Gruppen `v6_pool` und `v6_garten` werden den Außenanlagen zugerechnet. Die Keller-Zusatzmaterialliste bezieht sich weiterhin ausschließlich auf den vermessenen Keller.

Für Live-Baufortschritt muss nach Veröffentlichung das neue Plugin **1.4.0** mit dem aktualisierten Bauplan installiert werden. Bestehende Konfiguration kann weiterverwendet werden. Unveränderte lokale Bauhäkchen werden übernommen.

Die Korrektur an der Bodenhöhe der Geländeansicht verhindert, dass eine flache Geländehaut die modellierten Eingangsstufen überdeckt. Die alte globale Erdarbeitskarte ist weiterhin keine vollständige neue Vermessung eurer Welt; die modellierten zusätzlichen Erd- und Oberflächenblöcke sind in den aktuellen Außenmaterialmengen enthalten.

## Prüfung

Statisch geprüft werden der unveränderte endgültige Kellerboden, Lagergeometrie, freie Porterzone, Beckenbegrenzung und Wasserstand, freie Terrassenzugänge, Sitzbank-Untergründe sowie begehbare Pergolazugänge. Reale Wasserverteilung, Pflanzenwachstum und Lichtwirkung benötigen eine Ingame-Kontrolle.

Ab installierter Plugin-Version 1.4.0 wird der Bauplan automatisch von der Website aktualisiert. Der genannte JAR-Austausch ist für den einmaligen Wechsel von älteren Plugin-Versionen erforderlich, nicht bei jeder weiteren Bauplanänderung. Website und Server-Plandatei gemeinsam veröffentlichen; bei Bedarf `/blackthornlive sync` verwenden.
