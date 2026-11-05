# Revision 5.16 · Zugang und Technikschacht

## Treppen und Laufweg

Die Keller- und Haupttreppe sind im X-Mittelpunkt 29 Blöcke voneinander entfernt; zwischen ihren nächsten X-Kanten liegen 22 Blöcke. Die Kellertreppe kommt an der Bibliotheksseite auf EG-Höhe an. Von dort führt der Weg über Bibliothek/Halle zur Haupttreppe.

Die Blockbelegung über jeder Treppenstufe wurde statisch für drei Y-Ebenen geprüft:

- `keller_treppe`: 48 Treppenblöcke, 0 belegte Kopfraumpositionen in den drei Ebenen darüber.
- `halle_treppe`: 42 Treppenblöcke, 0 belegte Kopfraumpositionen in den drei Ebenen darüber.
- `galerie`: 48 Treppenblöcke, 0 belegte Kopfraumpositionen in den drei Ebenen darüber.

Das belegt freie Blockzellen im Modell, aber keinen Lauf- oder Türtest im Spiel. Der Ingame-Test bleibt offen.

## Technikstollen und Aufzugsvorschlag

Die zwei Vorlagen umfassen zusammen eine geplante Grundfläche von 57 × 27 und 24 Blöcke Höhe: X −715…−659, Y 80…103, Z 770…796. Der 3 Blöcke breite Wartungsspalt liegt bei X −688…−686. Als vertikale Serviceachse ist X -687, Z 790 vorgesehen.

An dieser Achse liegen derzeit Geschossblöcke bei Y 105, 113, 120, 121, 128, 129, 130. Diese Durchbrüche, die Verbindung zur Einwurfstation und die Aufzugsschaltung sind noch nicht in den Hausblockplan übernommen. Die Achse ist ein Platzierungsvorschlag, kein fertiger Dropper- oder Wasserlift.

- **Copper Golem MIS Cherry**: 27 × 24 × 27 Blöcke; Anker X −715 / Y 80 / Z 770.
- **Golem MIS Dustless Filter**: 27 × 22 × 27 Blöcke; Anker X −685 / Y 82 / Z 770.

Die Original-Litematics bleiben separat, damit Entities und Blockentity-Daten erhalten bleiben. Die Technikhalle ist nicht in der Oberflächen-Terraformingliste enthalten.
