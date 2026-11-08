# Blackthorn Estate · Version 6.0

## Bestehender Keller als Grundlage

Grundriss außen X −710…−658 / Z 766…814 (53 × 49), innen 51 × 47. Der aus eurer aktuellen Region ausgelesene Schachbrettboden auf Y 95 und die Außenwände bis Y 127 werden übernommen. Die obere Wandlage Y 128 wird bis zur Geschossdecke geschlossen. Kleine Bodendurchbrüche entstehen nur für die beiden Leiterzugänge. Die neue untere Decke auf Y 101 erweitert die bereits begonnene nördliche Teilfläche; lichte Höhe darunter Y 96…100, also fünf Blöcke.

| Zone | Höhen | Nutzung |
| --- | --- | --- |
| Untere Räume | Boden 95, Decke 101 | Bibliothek, geheime Nebenräume, Werkstattreserve und Handlager |
| Großlager | Modul 102…123 | Volle Dustless-Schaltung, vier Chunks |
| Porter-Galerie | Boden 124, freie Höhe 125…128 | Gesamte Nordwand frei; Decke / EG-Boden 129 |

Die große Bühne des Lagers ist technisch mehrgeschossig. Sie wurde nicht auf eine gewöhnliche Geschosshöhe zusammengestaucht. Hauptzugang: durchgehende Leiter im Südosten bei X −661 / Z 803, vom EG zu den drei Ebenen. Zwei zusammenhängende freie Säulen neben der Leiter bieten Austrittsraum; die Deckendurchbrüche bleiben offen. Im Spiel gegen Absturz sichern. Es gibt hier keine als fertige Treppe ausgegebene Leiter.

Hinter der unteren Bibliothek führt die zweite Leiter bei X −706 / Z 776 nach Y 81 auf den Gangboden Y 80. Ein drei Blöcke hoher, drei Blöcke breiter Verbindungsgang schließt dort in Richtung des bisherigen Technikzugangs an. Die Öffnung ist begehbar modelliert; ein neues automatisches Geheimtürschloss ist nicht vorgetäuscht.

## Gesamte nördliche Wand für eure Porter

Freier Streifen: **X −709…−659 / Z 767…780**, also **51 × 14 = 714 Bodenpositionen**. Zwischen Boden Y 124 und Decke Y 129 sind vier Blöcke frei. Keine Möbel, Beleuchtungsständer oder dekorativen Säulen stehen im Streifen. Beleuchtung sitzt bündig in der Decke. Meißelsteinlinien im Boden bei X −704, −688 und −672 kennzeichnen Chunkgrenzen ohne Stolperkanten.

Für die technische Umsetzung eurer bereits gebauten Porter sind drei Chunkzonen vorgesehen:

| Bereich | X | Z | Chunk X/Z |
| --- | --- | --- | --- |
| West | −703…−690 | 769…780 | −44 / 48 |
| Mitte | −687…−674 | 769…780 | −43 / 48 |
| Ost | −671…−660 | 769…780 | −42 / 48 |

Die Zone ganz im Westen bleibt für Wartung und Zugang nutzbar. Die nördliche Chunkgrenze liegt auf Z 768. Perlen, Auslöser und gesamte notwendige Schaltung innerhalb der jeweiligen Zone aufbauen; Bodenmarkierungen allein gewährleisten keine Chunkladung. Eure Porter werden selbst umgesetzt und sind nicht in Materialmengen, Entities oder Live-Baupositionen enthalten. Wenn eure vorhandene Schaltung höher als vier Blöcke ist, muss dafür ein gezielter Deckeneingriff geplant werden.

## Lager übernehmen – wichtig für die Funktion

Verwendete Vorlage: **Golem MIS Dustless Filter von cubicmetre**, 4.543 Blöcke und 27 × 22 × 27 Gesamtausdehnung. Ursprung **X −701 / Y 102 / Z 771**, keine Rotation. Maximalkoordinate X −675 / Y 123 / Z 797. Die vier Chunks X −44/−43 und Z 48/49 müssen für den Betrieb gemeinsam ausreichend geladen sein.

`litematics/Blackthorn_V6_Dustless.litematic` ist die angepasste Vorlage: Nur weißes Glas wurde in graues Glas geändert. Alle ursprünglichen Containerdaten, Inventare, Blockstates und Entities bleiben erhalten. Die mechanischen Positionen wurden nicht verschoben. Vorlage zuerst auf das richtige Ursprungsschema in Litematica prüfen; die Quelle besitzt mehrere Regionen mit teilweise negativen Abmessungen. Im Atlas entsprechen diese bereits der oben genannten normalisierten Gesamthülle.

Die komplette Blockgeometrie ist auch im Hausmodell und den Materiallisten enthalten. Das Haus-NBT enthält jedoch **keine Container-NBT oder Entities**. Für Filter-Seed-Inventare und Golems die V6-Litematic heranziehen. Im Survival-Modus sind Materialien und Bestückung im Spiel einzubauen; ein Bauplan-Import bestückt nicht automatisch alle Inventare. Die Cherry-Litematic bleibt nur als alternative Originalvorlage verfügbar und wird nicht zusätzlich eingebaut.

Die bisherige kleine Bulk-/Golem-Anlage, das 400-Fass-Regallager und die alte Keller-Trading-Hall entfallen an ihren alten Positionen. Die neuen fünf Reservefässer stehen unten auf Y 96. Ein neuer automatischer Materiallift ins EG und weitere Technikstationen sind keine Bestandteile dieser Revision. Die alten Techniktexte und älteren Geländeberichte sind historische Dokumente, keine neuen Abnahmeprotokolle.

## Empfohlene Umbaufolge

1. Welt sichern und vorhandenen Boden / Außenwände mit den Bestandsplänen abgleichen.
2. `keller_umbau_6.0.csv` verwenden: Sie vergleicht die Zielpositionen mit eurer gelieferten Region, einschließlich notwendiger Durchbrüche. Sie ist auf X −710…−658 / Z 766…814 / Y 94…129 begrenzt. Der tiefere Gang und seine Erdarbeiten stehen zusätzlich in der vollständigen Freiraumliste.
3. Durchbrüche und den tiefen Zugang ausheben. Bestehende Böden nur dort öffnen, wo die Freiraumliste dies vorsieht.
4. Untere Räume, Decke Y 101, seitliche Lagerzugänge sowie Leiterkerne setzen.
5. Großlager in Originalhöhe nach der V6-Litematic bauen und bestücken. Binnenluft und Wartungszugänge erhalten.
6. Galerieboden Y 124 und Deckenanschlüsse ergänzen, Nordstreifen frei halten. Vorhandene Porter chunkweise versetzen.
7. Alle Zugänge ablaufen, Lagerfunktionen und Relog-Porter auf eurem Paper-Server prüfen.

`materialbedarf.csv` ist der komplette Zielplan. **`materialbedarf_keller_zusaetzlich.csv`** enthält nur zusätzlich zu setzende Items innerhalb des ausgewerteten Bestandsschnitts; vorhandene passende Blöcke werden nicht erneut verlangt. Wiedergewinnbare Materialien beim Rückbau sind darin nicht gegengerechnet. Die globale alte Terraforming-Karte ist keine aktuelle Vermessung dieser gelieferten Serverregion; für den Keller sind die neue Umbau- und Freiraumliste maßgeblich.

## Atlas und Live-Plugin

Website und neuer Plugin-Bauplan verwenden denselben V6-Fingerprint. Nach Veröffentlichung das neue `downloads/BlackthornLive.jar` (Version 1.1.0) auf dem Server austauschen und neu starten. Bestehende Konfiguration und Schreibtoken bleiben verwendbar. Alte Plugin-Prüfstände werden nicht mit dem neuen Bauplan vermischt.

Lokale Bauhäkchen aus 5.26 werden nur für unveränderte Positionen übernommen. Entfernte Lagerbuchten und geänderte Bauteil-Fertigmeldungen werden verworfen. Gemeinsame Materialbestände bleiben gespeichert; neue Sollmengen und Häkchen im Team gegenprüfen.

## Prüfung

Statische Prüfung: eindeutige Positionen, Materialmengen, Türhälften, direkte Türzugänge, Luft-/Blockkonflikte, durchgehende Leiterwege, Freihaltung der Porterzone, unveränderte Schaltungsgeometrie und erhaltene Litematic-Container-/Entitydaten. Das ersetzt keinen Ingame-Lauftest, keine Lichtsimulation und keine Redstone-Abnahme.
