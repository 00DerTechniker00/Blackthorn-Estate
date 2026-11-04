# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.12**. `index.html` lokal im Browser öffnen.

## Versionsverlauf

Die formalen Revisionen 5.1 bis 5.12 sind chronologisch als Git-Commits importiert und mit `v5.1` bis `v5.12` markiert.

```sh
git log --oneline --decorate
git switch --detach v5.11
```

Die Commit-Zeitpunkte zeigen den Import in dieses Repository; sie sind keine behaupteten ursprünglichen Änderungszeitpunkte.

## Materialbedarf und Detailansicht

Auf der Startseite steht die Gesamtmenge sichtbar. Unter **Bauatlas → Minecraft-Texturen** lässt sich die `.nbt`-Struktur optional an den externen Viewer übergeben.

## Lokaler Neuaufbau

```sh
python tools/build.py
```

Der Generator verwendet die `blueprint.json` im Repository und die Vorlage in `tools/seeds/revision-5.9/`. Nachbarordner oder ZIP-Dateien werden nicht benötigt.

## Quelldaten und Archiv

Die Arbeitskopie enthält keine ZIP-Dateien. Frühere ZIP-Exporte wurden inhaltlich als Git-Versionen übernommen oder ihre Quellprojekte entpackt im Ordner `archive/` abgelegt. Ursprüngliche Weltregionen und Referenzen liegen getrennt unter `source-data/`.
