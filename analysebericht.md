# Prüfung und Änderungen · Revision 5.7

## Ausgangspunkt und Architektur

Basis ist die unveränderte Revision 5.6. Hauptgrundriss, Ausrichtung, sechs
Residenzen, drei Keller, Pool und Dachkontur bleiben Grundlage. Die neue Version
hat 78.600 eindeutige Positionen, gegenüber 78.586 in der Basis.

Die bestehende Darstellung von Treppen, Türen, Stufen, Fenstern und Einrichtung
wurde übernommen. Ein lokaler WebGL-Renderer übernimmt Kameras und Geometrie,
sodass die Website keine externe Three.js-Datei mehr nachladen muss.
Transparenz wird näherungsweise nach Schichten gezeichnet; komplexe überlagerte
Glasflächen können Darstellungsartefakte zeigen. Blockauswahl verwendet wie vorher
Voxelzellen, keine exakten Kollisionsformen der Teilblöcke.

## Reparierte Modellfehler

- Die beiden fehlenden Förderhopper bei X=-675/Y=123/Z=795 und 796 ergänzt.
- Pro Bulkfilter die fehlenden Hopper bei Y=122/Z=781 und 780 ergänzt. Die
  Ausgabestrecke erreicht damit die vorhandene Truhe bei Z=779.
- Die verwaiste obere Türhälfte bei X=-689/Y=123/Z=787 entfernt und die Tür
  vollständig bei Z=788 auf dem vorhandenen Boden rekonstruiert. Die Redstoneleitung
  bei Z=787 bleibt erhalten.
- Die alte einzelne Türhälfte vor dem Geheimzugang bei X=-689/Y=106/Z=793 entfernt.
  Die Geheimtür bei Z=794 auf Y=106/107 abgesenkt, sodass sie auf dem Boden Y=105 steht.

Jede Änderung steht in `aenderungen_5.6_zu_5.7.csv`. Die Topologieprüfung folgt
den Hopperrichtungen vom Einwurf zur Kupfertruhe und von sechs Filterausgängen
bis zur Zieltruhe. **Das belegt den räumlichen Förderweg, keine funktionierende
Redstone-Filterlogik.** Signalstärken, Haltesignale, Kapazität, Inventare und
Golem-Sortierung müssen weiterhin im Spiel entwickelt und getestet werden.

## Gelände und Aushub

Die Palette und Blockzustandsdaten der Originalregion `r.-2.1.mca` wurden direkt
aus `mca.zip` gelesen. Der Leser unterstützt die im Snapshot tatsächlich
vorkommenden Paletteneinträge als Strings sowie als NBT-Compounds und die gepackten
Blockindices. Fehlende Chunks und Sektionen führen zu Fehlern statt zu angenommener Luft.

Alle 16.428 gespeicherten Bodenpositionen entsprechen dem jeweiligen Block in der
Originalregion. Das bestätigt das Material auf der gespeicherten Höhe; es ist keine
neue automatische Klassifizierung aller Pflanzen, Baumkronen und Oberflächen.

Die 2.988 Aushubspalten der Revision 5.6 wurden übernommen. Zwischen ihrer jeweiligen
Unterkante und der gespeicherten Bodenhöhe liegen **52.120 Nicht-Luft-Blöcke**.
`aushub_blockliste.csv` führt jeden davon auf; vorhandene Höhlenluft wird abgezogen.
Die alte Revision enthielt widersprüchliche Mengen: 50.931 in der Geländeansicht
und 43.676 im historischen Prüfbericht. Beide werden durch die einheitliche neue
Zählung ersetzt. Die neue Zahl kann trotz Abzug von Luft größer sein, weil die alte
Schätzung keine konsistente Zählung der vorhandenen Spalten war.

Prüfgrenzen: Die Baugrubenform selbst wurde nicht neu unabhängig abgeleitet. Es wird
auch kein minimaler Block-für-Block-Umbauplan berechnet: Blöcke an späteren Baupositionen
werden beim Freiräumen mitgezählt, selbst wenn sie eventuell weiterverwendet werden
könnten. Pflanzen oberhalb der gespeicherten Bodenhöhe sind ausgeschlossen. Die
Gelände-3D-Ansicht ist weiterhin eine vereinfachte Oberfläche, keine vollständige
Höhlengeometrie. Das neue SVG zeigt echte Blöcke im Schnitt Z=790, Y=65…132.

## Dach und Survival-Aufwand

Das Dach wurde nicht automatisch ausgehöhlt. 13.717 Dachziegelpositionen sind an
allen sechs Seiten von weiteren Dachziegeln umgeben. Das ist ein konkreter Hinweis
auf Einsparpotenzial, keine pauschal sichere Löschliste. Eine Dachüberarbeitung
muss Innenraum, Anschlüsse, Auflager und Beleuchtung gemeinsam behandeln; sonst
entstehen neue dunkle Hohlräume. Die Dachmaterialmenge bleibt in 5.7 deshalb ehrlich
in den aus dem Modell erzeugten Listen enthalten.

Wasser bleibt mit seinen Positionen in der Blockliste und im 3D-Modell. Material-
Itemmengen enthalten keine Wasserpositionen als vermeintlich benötigte Wassereimer.
Türen und Betten zählen je einmal; Schilder werden mit Stackgröße 16 verpackt.

## Oberfläche und Datenpflege

`gcounts` war in 5.6 eine reine Blockzahl je Baugruppe, während die Materialansicht
dort ein Material-Dictionary erwartete. Jetzt wird es aus den tatsächlichen
Positionen als Materialmenge je Gruppe erzeugt. Alle 35 Baugruppen erscheinen in
den Bauphasen; zuvor fehlten neu hinzugefügte Logistikbereiche und Hangstützen.
Die Koordinatensuche vergleicht X, Y und Z in der angegebenen Reihenfolge.
Der Ebenenexport verwendet tatsächlich die gewählte Schnittrichtung und Position;
zuvor wurde bei X-/Z-Schnitten stattdessen die Y-Ebene 130 exportiert.

Fortschritt wird in einem eigenen Speicherbereich abgelegt. Ein Backup enthält
Baugruppen, Zuständigkeiten, Koordinaten-Häkchen und die drei aktuellen Lagerzonen.
Das Importformat prüft Typen, bekannte Koordinaten und Modellfingerabdruck vor
Änderungen. Der Import ersetzt einen vollständigen Stand; die UI sagt dies vor der
Bestätigung ausdrücklich. Ältere nummernbasierte Daten werden nicht vermischt.

## Prüfung und offene Grenzen

`tools/validate.py` kontrolliert eindeutige Koordinaten, komprimierte Daten gegen
CSV, Material- und Gruppensummen, Türhälften samt Auflager, gerichtete Förderwege,
Geländepositionen, Einzel-Aushubdaten, lokale Ressourcen und die Unverändertheit
aller 173 Originaldateien anhand des Übergabemanifests.

`tools/test_app.mjs` führt die wirklichen Anwendungsskripte mit einem kleinen
DOM-/Canvas-Testadapter aus. Es prüft Navigation, Materialfilter, alle Bauphasen,
Blockstatus, Speicherung, Backup-Validierung, X/Y/Z-CSV-Schnitte, Kamerabasis,
Projektionsmatrizen, Blockauswahl und den Geometrieaufbau. 126 Prüfungen erfolgreich. Dieser Test
ist kein Browser und kein GPU-Sichttest. Der installierte Chromium konnte hier
wegen gesperrter Betriebssystem-Sockets nicht gestartet werden.
Beide WebGL-Shader wurden zusätzlich mit `glslangValidator` erfolgreich übersetzt.

Die historischen Licht-/Begehbarkeitswerte bleiben nur als alte Modelldaten erhalten,
werden aber nicht mehr als aktuelle Zusicherung angezeigt. Eine Minecraft-Testwelt
und ein Sichttest im normalen Browser bleiben erforderlich.
