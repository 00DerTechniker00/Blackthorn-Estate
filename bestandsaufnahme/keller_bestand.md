# Kellerbestand und Umbauvorplanung

Quelle: neu gelieferte `r.-2.1.mca`, unverändert gelesen. Der Ausschnitt ist ein Bestand, kein neuer Bauplan. Die komprimierte JSON-Datei enthält Blocktypen und Blockzustände einschließlich Luft, keine Inventare oder Entitäten. Quelle und Prüfsumme stehen in `keller_hoehen.json`.

## Gemessener Bestand

- Außenabmessung: X −710…−658, Z 766…814, also **53 × 49 Blöcke**.
- Nutzbare Innenfläche: X −709…−659, Z 767…813, also **51 × 47 = 2.397 Positionen**.
- Boden auf Y 95: 1.199 polierte Tiefenschieferblöcke und 1.198 Tiefenschieferfliesen im Schachbrettmuster.
- Außenwände Y 96…127: 200 Tiefenschieferziegel pro Lage, zusammen **6.400 Blöcke**.
- Auf Y 101 liegt im Norden eine Teilfläche mit **306 Tiefenschieferfliesen**. Das ist keine vollständige Geschossdecke.
- Auf Y 105 und Y 113 ist die gesamte Innenfläche Luft: Die im alten Atlas vorgesehenen Kellerböden sind dort nicht gebaut.
- Auf Y 121 besteht der Innenraum aus 2.388 Luftpositionen und neun Eisenblöcken; keine durchgehende Decke.

Die Form ist somit eine hohe, weitgehend offene Hülle mit tiefem Boden. Bestehende Schale und Boden bilden die Grundlage für den neuen Ausbau. Die bisherige Dreiteilung Y 105 / 113 / 121 wird nicht als Bestand vorausgesetzt.

## Gewünschte Nutzung

Unten: Geheimräume, Nebenräume und Zugang zum tieferen Geheimgang. Darüber: großes Lager nach einer der gelieferten cubicmetre-Litematics. Oben: in die Wand integrierter Enderperlen-Login-Porter.

## Höhenprüfung der Lager-Vorlagen

Die Vorlagen sind **Alternativen**, keine zwei nebeneinander einzubauenden Lager:

| Vorlage | Gesamtabmessung |
| --- | --- |
| Copper Golem MIS Cherry | 27 × 24 × 27 Blöcke (X × Y × Z) |
| Golem MIS Dustless Filter | 27 × 22 × 27 Blöcke (X × Y × Z) |

Das große Lager ist technisch ein mehrgeschossiges Modul. Es passt nicht in einen üblichen acht Blöcke hohen Keller. Redstone-Höhen dürfen nicht ohne Prüfung gekürzt werden.

**Vorläufig bevorzugt: Dustless-Variante**, weil sich drei Nutzungszonen innerhalb eurer bestehenden Höhe sinnvoll unterbringen lassen:

| Zone | Vorgesehene Höhen | Bemerkung |
| --- | --- | --- |
| Untere Räume | Boden Y 95, Innenraum Y 96…101 | Bestehenden Boden erhalten; nördliche Teilfläche Y 101 einplanen. |
| Großlager | Modul Y 102…123 | Volle Höhe der Dustless-Vorlage, kein Zusammendrücken der Technik. |
| Oberer Zugang / Porter | Boden Y 124, Innenraum Y 125…128 | Vier Blöcke lichte Höhe bis zum geplanten EG-Boden Y 129; technische Porterhöhe noch offen. |

Die Cherry-Variante benötigt zwei zusätzliche Höhenblöcke. Ohne technisch geprüfte Änderung würde sie entweder die unteren Räume oder den oberen Porterbereich verkleinern. Der gewünschte geheime Abstieg unter Y 95 muss gesondert erschlossen werden; ein dort vorhandener durchgängiger Gang wird nicht unterstellt.

## Chunkplanung

Chunkgrenzen innerhalb der Hülle: **X −704, −688, −672** und **Z 768, 784, 800**. Bei negativen Koordinaten wird abgerundet.

Mögliche unveränderte Dustless-Ausrichtung: Anker **X −701 / Y 102 / Z 771**, Hülle X −701…−675, Y 102…123, Z 771…797. Diese 27 × 27 Grundfläche liegt vollständig in vier Chunks: X −44/−43, Z 48/49. Diese vier Chunks müssen für zuverlässigen Betrieb gemeinsam passend geladen sein. Dies ist eine Reservierung, noch kein Nachweis der Schaltungsfunktion oder Zugangsanbindung. Blockentities, Inventare und Golems müssen aus der originalen Litematic erhalten bleiben.

Porter-Reservierung oben an der **Nordwand**: X **−703…−690**, Z **769…778**, also **14 × 10 Blöcke**. Gesamte Zone in **Chunk X −44 / Z 48**. Boden Y 124, freier Innenraum Y 125…128. Die nördliche Außenwand bleibt bei Z 766; zwei Reihen Z 767/768 trennen sie von der Technikzone, deren Nordkante einen Block innerhalb der Chunkgrenze Z 768 liegt. Eine vorgesetzte Innenverkleidung kann den Porter optisch in die Nordwand integrieren. Die vorhandene Schaltung wird versetzt; hier wird kein Ersatz modelliert. Ihre tatsächliche Höhe und gesamte Verkabelung müssen in die reservierte Zone passen, sonst sind die Nachbarflächen bzw. die obere Raumhöhe anzupassen.

Für einen Relog-Porter reichen feste Chunkgrenzen allein nicht: Er muss auch bei Abwesenheit und beim erneuten Einloggen des Besitzers wie vorgesehen reagieren. Paper-Einstellungen und die konkrete Schaltung sind dafür zu prüfen. Ihr habt den Porter bereits gebaut und möchtet ihn verschieben. Geplant wird deshalb nur eine freie Einbauzone an der Nordwand, keine neue Schaltung. Ob die reservierten Abmessungen genügen, ist beim Versetzen anhand eures bestehenden Porters zu prüfen.

## Dateien

- `keller_grundrisse.png`: sechs horizontale Bestandsschnitte.
- `keller_hoehenschnitt.png`: vertikaler Bestandsschnitt mit bisherigen Atlas-Höhen.
- `keller_chunks.png`: tatsächlicher Bestand und reservierte Lager-/Porterflächen.
- `keller_bestand.json.gz`: vollständiger Blockausschnitt mit Weltkoordinaten und Blockzuständen.
- `keller_material_je_hoehe.csv`: gemessene Blockanzahlen pro Höhe, einschließlich Luft und Naturblöcken im Ausschnitt.

Hausmodell, Website-Bauplan und Plugin-Fingerprint werden erst mit der eigentlichen Umsetzung gemeinsam aktualisiert. Die Vorplanung verändert euren Minecraft-Server nicht.
