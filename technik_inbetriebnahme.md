# Logistik für Java/Paper 26.3 · Bau- und Inbetriebnahmeplan

**Status: Schaltentwurf, keine betriebsfertig getestete Automatik.** Komponenten,
Behälter, Richtungen und die Filter-/Vorratsstrecken stehen im Blockmodell.
Die Shulker-Sequenzsteuerung und der Taktgeber der Hubstrecke sind noch zu
verdrahten und in einer Testwelt zu prüfen. Die Sicherheits-Jumper der Bulk-Loader
halten die Hopper unter den aktiven Boxen gesperrt: Ohne diese Sperre würde ein
Loader seine eigene Box während des Füllens wieder entleeren.
Der Entwurf darf deshalb nicht als unverändert nachbaubare, bereits funktionierende
Komplettschaltung verstanden werden. `technik_module.csv` listet alle Ports.

## Daten und Minecraft-Verhalten

Serverziel und gelieferte Welt: **26.3**, Welt-DataVersion 5023. Grundlagen:
[Minecraft 26.3](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3),
[offizielle Golem-Sortierregeln](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-9).
Ein Golem nimmt bis zu 16 Items, sucht normale/Redstone-Truhen und akzeptiert
passende Typen oder leere Truhen. Sein Suchradius und die begrenzte Zahl geprüfter
Truhen begründen den separaten Raum mit neun erreichbaren Zielen. Eine leere
Überlauftruhe könnte beliebige Typen übernehmen; sie wird daher nicht als angeblich
„erst zuletzt“ verwendeter Ausgang eingebaut. Kategorienamen sind nur Beschriftungen.
Die Zieltruhen brauchen konkrete Seed-Typen. Andere/volle Ziele bleiben Klärfälle.

## Material- und Inventarlisten

- `technik_module.csv`: aktive Box, Dispenser, Kolben, Leerbox-Magazin, loser Vorrat
  und Shulker-Speicher mit aktuellen Weltkoordinaten.
- `technik_inventare.csv`: sechs Hopperfilter, jeweils 41 Zielitems plus vier
  einzeln umbenannte 64er Platzhalter. Außerdem die Seed-Items der neun Zieltruhen.
- `blockliste.csv`: vollständige Baupositionen; die Boxen an den aktiven Positionen
  sind Anschauungs-/Betriebspositionen. Für den späteren Start über den Dispenser
  nicht zusätzlich eine Box in die bereits belegte Position ausgeben lassen.

Filteritems, Seed-Items und Magazininhalt werden im Spiel eingesetzt. Die Materialliste
beschreibt Blockbau, keine vollständig befüllten Maschineninventare.

## Sechs Bulk-Strecken

Materialien: Bruchstein, Erde, Eisenbarren, Tiefenschiefer, Stein und Kies. Alle
haben Stackgröße 64. Andere Materialien gehen zur Golem-Eingangsstufe.

1. Die obere Hopperlinie transportiert Items an sechs Filtern vorbei. Ein Filter
   saugt aus der Linie. Der darunterliegende Extraktor wird über eine Fackel gesperrt.
2. 41+1+1+1+1 Items im Filter ergeben Signal 2; ein weiteres passendes Item hebt
   auf Signal 3. Drei Staubpositionen und ein Repeater bilden die Schwelle.
   Eine räumlich getrennte Rückleitung schaltet die Extraktor-Fackel.
3. Der Extraktor speist zuerst das Vorratsfass. Sein 27-Slot-Inhalt bleibt **lose**.
4. Ein zweiter Komparator wird mit einer konstanten Seitenreferenz 15 verglichen.
   Erst wenn das Vorratsfass voll ist, wird der Überlaufhopper unter der Zuleitung
   freigegeben. Er zieht nicht aus dem Vorratsfass selbst.
5. Nach Entnahme aus dem Vorrat muss dieser Überlauf sofort wieder gesperrt werden.
   Zuerst füllt sich der lose Vorrat erneut; erst dann wird weiter verpackt.

Die Sequenzsteuerung des Box-Loaders liegt hinter dieser Vorratspriorität und ist
vor Survivalbetrieb zu vervollständigen. Bei Seiten-/Nachbarstrom, Hopper-Updates
und Chunk-Neuladen darf der 41er Filter nicht leergezogen werden.

## Box-Loader: notwendige Schaltphasen

| Phase | Zufuhr zur Box | Hopper unter Box | Kolben | Dispenser |
|---|---|---|---|---|
| Füllen | freigegeben, sofern loser Vorrat voll | gesperrt | eingefahren | aus |
| Voll erkannt | sperren | gesperrt | noch eingefahren | aus |
| Box abbauen | gesperrt | freigeben | einmal pulsieren | aus |
| Aufnehmen | gesperrt | freigegeben | eingefahren | aus |
| Neu setzen | gesperrt | sperren | eingefahren | genau ein Puls |
| Prüfen | gesperrt | gesperrt | eingefahren | aus |
| Weiterfüllen | nur bei bestätigter Box | gesperrt | eingefahren | aus |

Die festen Redstoneblöcke an den Pickup-Sperreingängen sind **Inbetriebnahme-Jumper**.
Sie sind durch das gesteuerte Signal des Sequenzers zu ersetzen; nicht einfach
entfernen und den Hopper dauerhaft freigeben. Erst nach bestätigter Aufnahme der
alten Box darf die nächste gesetzt werden. Fehlt eine Leerbox oder ist der
Ausgang voll, bleiben Zufuhr und Automatiktakt gesperrt.

Unter der aktiven Box liegen drei Speicherfässer mit Hoppern dazwischen. Die
unterste Reserve füllt sich zuerst. Insgesamt 81 nicht stapelbare Shulker pro
Material; zusätzlich ein Fass mit 27 losen Stacks. Bei vollen 64er Boxen entsprechen
die Shulker-Reserven 139.968 Items je Material. Diese Zahl ist eine Kapazitätsrechnung,
keine Aussage über bereits vorhandene Boxen oder Materialvorräte.

## Stationen neben dem Einwurf

**Unloader:** Volle Boxen ins eigene Dispenser-Magazin, nicht als Item in die
normale Einwurftruhe. Erst nach stabiler Leer-Erkennung den Breaker auslösen.
Die seitliche Rückgabe ist ein Pickup-Port für die leere Hülle. Ob die Hülle durch
den Kolben zuverlässig dort und nicht im normalen Inhaltsstrom landet, muss im
Spiel geprüft werden; diese Sammlung ist derzeit keine garantierte Schaltung.

**Allgemeiner Loader:** Eigener Materialvorrat oberhalb der Box. Der feste Sockel
unter der Box verhindert das versehentliche Leersaugen. Volle Boxen werden seitlich
gesammelt. Hier werden bewusst eingelegte Items verpackt, nicht der gemischte
Einwurf ungefragt in gemischte Boxen gefüllt. Pickup/Sequencer noch prüfen.

**Hubstrecke:** Der Einwurf liegt tiefer als der Filterbus. Vier aufwärts gerichtete
Dropper verbinden beide Höhen. Dafür ist eine getaktete, verlustfrei rückstauende
Impulsleitung erforderlich; deren Taktgeber ist noch nicht vollständig modelliert.

## Abnahmefolge in einer Testwelt

1. Nur ein Bulk-Modul aktivieren. Je 100 richtige und falsche Items einspeisen;
   nach dem Durchlauf müssen die 41 Filteritems und vier Platzhalter erhalten sein.
2. Vorrat bis 1.727, dann 1.728 Items füllen. Vor 1.728 darf nichts zur Box gelangen.
   Danach überlaufen lassen, anschließend einen Stack entnehmen: Vorrat zuerst auffüllen.
3. Eine vollständige Box füllen, brechen, aufnehmen und ersetzen lassen. Alle
   1.728 Items müssen in genau einer ausgegebenen Box bleiben; kein doppelter Setzpuls.
4. Leerbox-Magazin leeren und alle drei Speicherfässer füllen. Die Maschine muss
   anhalten, statt Items auszuwerfen. Ein teilweise gefüllter aktiver Shulker darf
   beim Wiederanlauf nicht verschwinden.
5. Unloader mit gemischter Box prüfen, einschließlich Werkzeugen und leeren Hüllen.
   Inhalt und leere Box müssen getrennt und vollständig herauskommen.
6. Golems mit Honigwaben gegen Oxidation behandeln, Seed-Items setzen, neun
   Zieltruhen nacheinander testen. Unbekannte Typen und volle Ziele separat prüfen.
7. Alle sechs Bulk-Module gleichzeitig, anschließend Chunk-Neuladen, Serverneustart
   und Betrieb mit den tatsächlichen Paper-Einstellungen testen.

Der Browser-Mengenrechner prüft nur Kapazität, Vorratspriorität und Rückstau.
Er simuliert weder Redstone-Ticks noch Blockupdates, Kolben-Itemphysik oder Mob-KI.
