# Blackthorn Estate · Revision 5.20

Geheimgang, Materiallift, Poollicht und Uferweg

- Gestaffelte Poolfassade: Zwei hohe graue Glasfelder mit vorgezogenen Basaltpfeilern, dunklen Sohlbänken und steinernen Abschlüssen.
- Begehbarer Panoramabalkon: Boden Y 137, drei Blöcke Ausladung und acht Blöcke Breite; neue OG-Doppeltür mit äußeren Anschlägen und Eisengeländer.
- Drei Stützbögen unter dem Pool: Je zwei Blöcke tiefe Querbögen bei Z 780, 790 und 800; Tiefenschiefer und einzelne Moossteine, Pfeiler bis Y 115, bei tieferem vermessenem Gelände bis zur Oberfläche verlängert.
- Drei gemauerte Dachkamine: Unterschiedliche Abschlusshöhen Y 153–156; direkt auf dem Dach verankert, mit offenen Rauchstellen.
- Monumentales Westportal: Zwei 2×2-Säulen, Schwarzstein-Kapitelle, zweilagiger Dreiecksgiebel und Kupfer-Gold-Wappen über dem freien Ankunftsweg.
- Begehbarer Aussichtsturm: OG-Zugang bei X −731 / Z 775, Leiter bis zur Galerie Y 163, steinerne Balustrade und gewachste oxidierte Kupferkrone bis Y 171.
- Zweiflügelige Südgartentreppe: Neue Doppeltür bei Z 831; obere Terrasse Y 129, zwei seitliche Läufe und gemeinsamer Gartenweg auf Y 126 bis zum Anschluss auf Y 125.
- Verbreiterte Bogenfüße: Nach unten ausgestellte Sockel aus Tiefenschiefer-Fliesen und Bruchtiefenschiefer an den freiliegenden Pfeilerfüßen.
- Zwei Klippenkaskaden: Separate, eingefasste Speier bei Z 780 und 783 mit Fallwasser und Auffangmulden; unabhängig vom Schwimmbecken.
- Verdeckte Portalbeleuchtung: Zwei Meereslaternen hinter Fichtenblenden seitlich der Frontsäulen.
- Kolben-Bücherregal: Zwei bewegliche Regalblöcke bei X −697 / Z 778. Bodenhebel X −696 / Y 106 / Z 775, getrennte Repeater für beide Kolben; geschlossen modelliert.
- Geheimer Technikzugang: Verdeckte Leiter und Unterquerung der Schaltung auf Y 100; weiter bis Y 81 bei X −697 / Z 768. Der untere Gang liegt nördlich der Litematic-Module und endet an deren Servicelücke X −687.
- Automatischer Material-Aufstieg: Separate Blasensäule neben der Wartungsleiter. Einwurf X −685 / Y 108 / Z 789; Hopper, Dropper und Komparator-Taktgeber. Ausgabe im EG X −683 / Y 131 / Z 792.
- Schaltbare Poolbeleuchtung: Sechs Lampen in den Beckenwänden. Hebel neben dem Poolausgang bei X −657 / Y 130 / Z 787; trockene Leitungen mit Repeatern unter der Terrasse.
- Vermessener Klippenabstieg: 84 Wegpositionen vom nordöstlichen Terrassenrand Y 129 bis zum Ufer auf Y 63; maximal ein Block Höhenunterschied je Schritt.
- Viktorianischer Bootsschuppen: Eichenbau mit Netherziegeldach, Westzugang und offener Wasserbucht im Osten bei X −580…−572 / Z 750…758.
- Moos an den Bogenfüßen: Zwei kleine Moosakzente an den feuchten Sockeln; ohne Bewuchs auf den Gehwegen.

Die Redstone-Module sind geometrisch angeschlossen. Schaltzyklen, Wasserfluss und die Kolbentür sind im Spiel zu prüfen. Der NBT-Export enthält die neuen Luftpositionen. Beim manuellen Bauen zuerst freiraeume_5.20.csv abarbeiten. Die Westansicht unter assets/westansicht_5.19.svg wird direkt aus dem Blockmodell erzeugt.

Die bestehende EG-Pooltür samt Steinrahmen bleibt nutzbar. Die Balkontür liegt eine Etage höher. Der Wartungsschacht K3–EG bleibt bestehen. Der geheime Zugang führt nun bis Y 80; die beiden Litematic-Module bleiben separate Dateien. Der Materiallift ist neben der Wartungsleiter modelliert; seine Inbetriebnahme steht aus.

Redstone, Kolbentür und Wassertransport sind konstruktiv modelliert, aber nicht im Spiel getestet. Der NBT-Export enthält explizite Luftpositionen für die neuen Durchgänge. Beim manuellen Bauen die Luft-/Aushubliste vorab abarbeiten. Der Lift transportiert Item-Entitäten, auch gefüllte Shulkerboxen; er ist kein Shulker-Unloader. Der Bootsschuppen liegt an der vermessenen nordöstlichen Wasserfläche, nicht an der trockenen Südklippe.

Die Website zeigt die neuen Bauteile unter Bauatlas → Hausstruktur mit direktem 3D-Zugriff. Blockliste, Materialbedarf, Änderungsdatei und NBT-Export werden aus demselben Modell erzeugt. Alte Modellhäkchen werden nur für unveränderte Positionen übernommen.

Frühere Licht-, Erreichbarkeits- und Erdarbeitszahlen sind historische Daten. Aktuelle Ingame-Abnahme, Lichtsimulation und der Anschluss der Bogenfüße an den Fels stehen aus.

Die Daten bleiben in externen JavaScript-Dateien, damit der Atlas lokal ohne Webserver geöffnet werden kann. Historische Archive und Rohwelten bleiben lokal über .gitignore ausgeschlossen.
