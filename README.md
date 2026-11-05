# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.16**. `index.html` lokal im Browser öffnen.

## Was ist neu?

- Der Atlas dokumentiert den statischen 3-Block-Kopfraum über den Treppen sowie die Koordinatendifferenz zwischen Keller- und Haupttreppe.
- Die Litematic-Technikhalle ist jetzt mit Gesamtmaßen, Servicelücke, Zugangskoordinate und den nötigen Geschossdurchbrüchen ausgewiesen.
- Die Website kennzeichnet klar, dass Laufweg, Schacht und Redstone noch nicht im Spiel abgenommen sind.

Die Hausgeometrie bleibt gegenüber 5.15 unverändert. Das Itemlift-System und die Öffnungen in den Geschossdecken sind Planungsangaben, keine gebaute oder geprüfte Mechanik.

## Versionsverlauf

`git log --oneline --decorate` zeigt die Revisionen. `v5.15` bleibt erhalten; der aktuelle Stand ist mit `v5.16` markiert.

## Neu aufbauen

```sh
python tools/build.py
```

Der Build verwendet die gespeicherten Modelle unter `tools/seeds/` und die Litematics unter `litematics/`.
