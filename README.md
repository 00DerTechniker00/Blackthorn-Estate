# Blackthorn Estate · Revision 5.12

`index.html` im Browser öffnen. Haus, Gelände, Lager und Baupläne bleiben lokal nutzbar.

## Minecraft-Ansicht mit Originaltexturen

Unter **Bauatlas → Minecraft-Texturen** kannst du das Anwesen mit dem externen [Structure Viewer](https://structure-viewer.ewanhowell.com/) ansehen. Er lädt die Java-26.3-Blockmodelle und Texturen und unterstützt Orbit- und Rundgangansichten.

Die Website lädt die Ansicht erst nach deinem Klick. Dabei werden die 132.070 Blockpositionen an den externen Viewer übergeben; die Spielgrafiken lädt er aus dem Internet. Seine Statusmeldung erscheint direkt über der Ansicht. Bei einer Netzwerkstörung kannst du `blackthorn_estate_5.12.nbt` herunterladen und auf der Viewer-Website öffnen. Die übrigen Ansichten des Bauatlas funktionieren weiter offline.

Die NBT-Datei enthält alle Blocktypen und Blockstates im selben Aufbau wie das Bauplanmodell. Ihr Ursprung ist X −791 / Y 105 / Z 703. Inventarinhalte sind nicht in den Baupositionen gespeichert und deshalb auch nicht in der 3D-Datei enthalten; nutze dafür die Lager- und Techniklisten. Die Gesamtstruktur ist für die Ansicht gedacht und überschreitet die Größe eines einzelnen Ingame-Strukturblocks.

## Gelände, Garten und Bauplanung

Unter **Gelände** gibt es den Vorher-nachher-Vergleich, ausgewählte Arbeitsspalten mit Höhenprofil, Chunk-Abschnitte und ein druckbares Vergleichsbild. Die weichen, begrünten Böschungen, Kieswege, Formschnittinseln, Blumenbeete, Bänke und der Gartenpavillon gehören zum unveränderten Modell aus 5.11. Alle Terraforming- und Materiallisten enthalten dieselben Mengen wie in Revision 5.11.

Unter **Lager** stehen die 56 Lagerbuchten. Im Bauatlas gibt es Ebenenplan, Blocklisten, Räume und Leuchtenplan. Unter **Organisation** lassen sich Fortschritt, Material und Dateien verwalten.

## Fortschritt aus 5.11

Unter **Organisation → Fortschritt** kann ein vollständiges 5.11-Backup importiert werden. Da das Blockmodell unverändert ist, bleiben alle Häkchen, Zuständigkeiten und Bestandsnotizen erhalten. Der bisherige lokale Stand wird nicht überschrieben. Wenn beide Seiten denselben Browser-Speicher nutzen, wird der Stand automatisch übernommen; andernfalls importiere das Backup.

Die Lagerautomatik ist weiterhin ein unvollständiger Schaltentwurf. Offene Schritte stehen in [Technik und Inbetriebnahme](technik_inbetriebnahme.md).

## Arbeitsdateien

`blackthorn_estate_5.12.nbt` enthält 132.070 Baupositionen in Minecraft-Strukturform. `aenderungen_5.11_zu_5.12.csv` enthält nur die Kopfzeile, da keine Baupositionen geändert wurden. Blockliste, Material- und Geländedateien bleiben gegenüber 5.11 identisch. `manifest_5.12.json` führt Prüfsummen aller ausgelieferten Dateien.

## Reproduzieren

```sh
python tools/build.py
```

Der Exportgenerator benötigt die benachbarte Revision 5.11. Der Viewer selbst benötigt eine Internetverbindung. Da der Browser in der Arbeitsumgebung nicht gestartet werden konnte, ist der externe Embed-Aufruf hier nicht visuell bestätigt; ein direkter Download steht als Ausweichweg bereit.
