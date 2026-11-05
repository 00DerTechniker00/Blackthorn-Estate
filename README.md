# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.15**. `index.html` lokal im Browser öffnen.

## Was ist neu?

- Eine breite zweiläufige Haupttreppe führt aus der Großen Halle hinauf zur Nordgalerie.
- **Hausstruktur** zeigt Etagen, Höhen, Raumbezüge, Gebäudeachsen und Treppen auf Basis des tatsächlichen Blockmodells.
- Die Richtungshinweise sind korrigiert: Eingang und Zufahrt liegen westlich, Pool und Klippenpanorama östlich.
- Der interne Voxel-Renderer zeichnet nur bei Änderungen und ordnet unbekannte Blockmaterialien mit passenden Ersatzfarben ein.
- Die beiden Copper-Golem-Litematics bleiben unter **Lager → Sortierung & Technik** mit Materialübersichten und Einbauvorschlag erreichbar.

Erdgeschoss und Obergeschoss bleiben bei je acht Y-Ebenen. Die Lagertechnik bleibt vorerst auf Keller 1 und 2 verteilt; ihre Verlegung braucht noch einen abgestimmten Grundriss. Aushub, Zugang, Itemwege und Redstone der Litematic-Module sind weiterhin nicht im Spiel abgenommen.

## Versionsverlauf

`git log --oneline --decorate` zeigt die Revisionen. Revision 5.14 bleibt als Verlaufspunkt erhalten; der aktuelle Stand ist mit `v5.15` markiert.

## Neu aufbauen

```sh
python tools/build.py
```

Der Build verwendet die gespeicherten Modelle unter `tools/seeds/` und die Litematics unter `litematics/`.
