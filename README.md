# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.14**. `index.html` lokal im Browser öffnen.

## Was ist neu?

- Die Dachlaterne aus Revision 5.13 wurde auf Wunsch entfernt; die vorherige Dachform ist wiederhergestellt.
- Der interne Voxel-Renderer zeichnet nur bei Änderungen und ordnet unbekannte Blockmaterialien mit passenden Ersatzfarben ein.
- Unter **Lager → Sortierung & Technik** sind die beiden Copper-Golem-Litematics mit Maßen, Materiallisten, Einbauvorschlag und direkter Texturansicht eingebunden.

Die Maschinen sind separate, unveränderte Litematic-Vorlagen. Aushub, Servicezugang, Itemwege und Redstone wurden noch nicht in den Hauptbauplan übernommen oder im Spiel abgenommen.

## Versionsverlauf

`git log --oneline --decorate` zeigt die Revisionen. Revision 5.13 bleibt als Verlaufspunkt erhalten; der aktuelle Stand ist mit `v5.14` markiert.

## Neu aufbauen

```sh
python tools/build.py
```

Der Build verwendet die gespeicherten Modelle unter `tools/seeds/` und die Litematics unter `litematics/`.
