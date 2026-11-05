# Revision 5.13 · Dachlaterne und Lagertechnik

Die Große Halle erhält eine verglaste Dachlaterne mit steinernem Sockel, hellem Gesims und oxidiertem Kupferabschluss. Die neue Konstruktion umfasst 85 echte Blockpositionen und steht in der Baugruppenliste `dach_schmuck`. Revision 5.12 bleibt im Git-Tag `v5.12` erhalten. Der Fortschrittsimport übernimmt alte Häkchen und setzt die geänderte Dachgruppe zurück.

## Eingebundene Litematics

- **Copper Golem MIS Cherry**: 4,919 Blockpositionen, 27 × 24 × 27 Blöcke, 56 Entities, 1104 Blockentities.
- **Golem MIS Dustless Filter**: 4,543 Blockpositionen, 27 × 22 × 27 Blöcke, 60 Entities, 1092 Blockentities.

Die Dateien bleiben unverändert und werden im Textur-Viewer direkt als `.litematic` geladen. So bleiben Kupfergolems, Truhen, Hopper, Schilder und deren NBT-Daten in der Vorlage erhalten. Die Platzierung ist als neue Technikhalle unter Keller 3 vorgeschlagen: MIS bei X −715 / Y 80 / Z 770, Dustless Filter bei X −685 / Y 82 / Z 770, ohne Drehung. Ein drei Blöcke breiter Zwischenraum ist für Wartung und Zugang reserviert. Der Aushub und die Verbindung zur bestehenden Sortierung sind Planungsarbeit und noch nicht im Bauplan enthalten.

## Prüfgrenzen

Die Litematic-Dateien wurden blockweise aus ihren gepackten Paletten gelesen; die decodierten Nicht-Luft-Zahlen stimmen mit den eingebetteten Metadaten überein. Renderer und externe 26.3-Texturansicht wurden in dieser Umgebung nicht visuell im Browser geprüft. Die Redstone- und Golem-Sortierlogik muss vor dem produktiven Einbau auf dem Server abgenommen werden.
