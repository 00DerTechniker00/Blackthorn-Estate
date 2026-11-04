# Blackthorn Estate · Revision 5.7

Lokale Weiterentwicklung der Revision 5.6. Die Originaldateien bleiben unverändert.

## Öffnen

`index.html` im Browser öffnen. Alle Skripte, Daten und Bilder liegen im Ordner;
es werden keine CDN-Dateien, Konten oder Internetverbindungen benötigt.
Für die 3D-Ansicht muss WebGL mit 32-Bit-Indexunterstützung verfügbar sein.
Der Bauatlas benötigt keinen Server und keine Installation.

## Neu

- Lokaler WebGL-Viewer mit den bestehenden Blockformen, Kameras, Schnittregler,
  Bauteilfiltern und Blockauswahl. Hover zeigt Nummer, Blockstate und Weltkoordinaten.
- Unterbrochene Hopperwege zur Kupfertruhe und zu sechs Bulk-Ausgängen ergänzt.
  Verwaiste Türhälften bereinigt und die Geheimtür auf die Bodenhöhe gesetzt.
- Materiallisten pro Baugruppe repariert; alle 35 Gruppen im Bauablauf vorhanden.
  Wasserpositionen sind separat im Modell und werden nicht als Eimerbedarf gezählt.
- CSV-Export berücksichtigt die gewählte X-, Y- oder Z-Schnittebene und ihren Bauteilfilter.
- Ein gemeinsames, versioniertes Backup für Baugruppen, Personen, einzelne
  Blockhäkchen und Lagerbestände. Blockstatus verwendet XYZ statt wechselnder Nummern.
- 16.428 Bodenpositionen mit `mca.zip/mca/r.-2.1.mca` abgeglichen. Für die
  übernommenen 2.988 Aushubspalten sind 52.120 vorhandene Blöcke einzeln erfasst.
- Fehlendes Untergrundbild durch lokal erzeugten SVG-Regionschnitt ersetzt.
- Alte Licht- und Begehbarkeitswerte nicht mehr als aktuelle Prüfung dargestellt.

## Fortschritt

Unter „Bauplan“ ein **vollständiges Backup** herunterladen. „Backup laden“ prüft
Format und Modellfingerabdruck und ersetzt nach Bestätigung den gesamten lokalen
Stand. Es gibt keine automatische Zusammenführung und keine Live-Synchronisierung.
Alte nummernbasierte Fortschrittsdaten werden bewusst nicht automatisch übernommen.
Der Browser speichert lokal; nach Umbenennen oder Verschieben des Ordners oder bei
einem anderen Browser kann der Speicher anders zugeordnet sein. Dafür das Backup verwenden.

## Dateien

- `blockliste.csv`: 78.600 eindeutige Baupositionen.
- `materialbedarf.csv`, `materialbedarf_baugruppen.csv`: aus dem Modell abgeleitete Itemmengen.
- `aushub.csv`: Spalten und Mengen vorhandener Blöcke im mitgelieferten Weltstand.
- `aushub_blockliste.csv`, `aushub_materialien.csv`: vorhandene Einzelblöcke und Materialsumme.
- `aenderungen_5.6_zu_5.7.csv`: jede geänderte Koordinate mit vorherigem und neuem Zustand.
- `blueprint.json`: lesbarer Zugang zum vollständigen Datenmodell.
- `analysebericht.md`, `check_report.json`: Befunde und Prüfgrenzen.
- `pruefprotokoll.json`: ausgeführte Prüfungen und ausdrücklich offene Sicht-/Ingame-Tests.

## Reproduzieren und prüfen

Benötigt Python 3.10+ und für die JavaScript-Prüfung Node.js 18+.
Die Skripte benötigen keine zusätzlichen Pakete.

```sh
python tools/build_revision.py
python tools/validate.py
node tools/test_app.mjs
```

Der Generator liest standardmäßig den benachbarten Ordner
`Blackthorn-Estate-Revision-5.6` und das benachbarte `mca.zip`.
Die ausgelieferte Website benötigt diese Originaldateien beim Öffnen nicht.

Die Tests ersetzen keine Minecraft-Testwelt. Licht, Begehbarkeit, Redstone-Timing,
Golemwege und Dachdetails sind noch im Spiel zu prüfen. Der Browser-Sichttest konnte
in der Codex-Ausführungsumgebung wegen gesperrter Betriebssystem-Sockets nicht laufen.
