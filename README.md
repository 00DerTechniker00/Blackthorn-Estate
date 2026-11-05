# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.13**. `index.html` lokal im Browser öffnen.

## Was ist neu?

- Eine begehbare Dachlaterne mit Kupferabschluss sitzt über dem First der Großen Halle.
- Der interne Voxel-Renderer lädt die Szene nur bei Änderungen und ordnet unbekannte Blockmaterialien mit passenden Ersatzfarben ein.
- Unter **Lager → Sortierung & Technik** sind die beiden mitgelieferten Copper-Golem-Litematics mit Maßen, Materiallisten, Vorschlagskoordinaten und direkter Texturansicht eingebunden.

Die Maschinen sind separate, unveränderte Litematic-Vorlagen. Der vorgeschlagene Technikstollen liegt unter Keller 3; Aushub, Servicezugang, Itemwege und Redstone wurden noch nicht in den Hauptbauplan übernommen oder im Spiel abgenommen. Die Originaldateien bleiben als Litematics erhalten.

## Versionsverlauf

`git log --oneline --decorate` zeigt die Revisionen. `v5.12` bleibt als vorheriger Stand erhalten; der neue Stand ist mit `v5.13` markiert.

## Neu aufbauen

```sh
python tools/build.py
```

Der Build verwendet die gespeicherte 5.12-Grundlage, die Vorlagenoberfläche unter `tools/seeds/revision-5.9/` und die Litematics unter `litematics/`.
