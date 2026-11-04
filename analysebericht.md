# Revision 5.9 · Ausrichtung, Zugang, Laternen und Lager

Die Architektur aus 5.8 wurde um X=-690/Z=790 um 180° gedreht. Blockrichtungen,
Türhälften, Filterausgänge, Raumbereiche und Inventarpositionen werden zusammen
transformiert. Das ursprüngliche Gelände bleibt unverändert orientiert; die
neuen Arbeitsmengen werden aus den Originalblöcken erneut berechnet.

Der Pool liegt damit im Osten und schaut über den tiefen Geländeeinschnitt. Die
Zufahrt kommt von Nordwesten. Die Wegmittellinie liegt nach der verwendeten Messung
mindestens 15 Blöcke von einer natürlichen Bodensäule entfernt, die mehr als acht
Blöcke tiefer liegt. Gesucht wurde innerhalb von 22 Blöcken Radius. Das ist eine
nachvollziehbare Geländeprüfung, keine vollständige Absturz-/Spielersicherheitssimulation.
Der fünf Blöcke breite Weg erhält zusätzliche Schultern und Böschungsübergänge.
An stärker angehobenen Rampenteilen ergänzt eine steinerne Wegeinfassung den
Abstand zur natürlichen Hangkante; sie wird als echtes Bauteil mitgezählt.

Der Pooldurchgang war sowohl außen durch Treppen-/Dekorblöcke als auch innen durch
Bibliotheksmöbel eingeengt. Ein vier Blöcke breiter Bereich wird freigeräumt; der
zweiflügelige Türdurchgang bleibt auf der Geschosshöhe begehbar. Die Mezzanin-Treppe
der Bibliothek wird vollständig seitlich versetzt und mit Unterbau sowie Geländer
neu gebaut. Die eigentliche Kellertreppe bleibt erhalten.

Aufhängungen der Laternen wurden überprüft und mit Deckenketten ergänzt. Bodenleuchten
in den zentralen Durchgängen werden höher gehängt oder entfernt. Wo kein geeigneter
Halt gefunden wird, bleibt keine schwebende Leuchte stehen. Im Viewer wurde zusätzlich
das fehlende obere Verbindungsstück der Hängelaterne ergänzt. Eine Licht-/Spawnprüfung
ist damit ausdrücklich noch nicht erfolgt.

Die sechs Gauben, Gesimse, hellen Ecksteine und Kupferakzente ergänzen die vorhandene
Dachhülle. Die dichten Dachfüllungen früherer Revisionen werden nicht wiederhergestellt.
Die Vorschauen unter `assets/` verwenden die tatsächlichen Geometrien des Viewers.

Im Keller sind sechs Bulk-Scheiben neu angeordnet. Ihre Filter, Vorratsfässer,
Überlaufleitungen, Box-Positionen, Dispenser und Kolben stehen im Modell. Unter
jedem Loader führt eine senkrechte Strecke in drei Fässer für volle Shulker.
Fünf Regallagerbuchten werden dafür an andere freie Positionen derselben Etage
versetzt; alle 400 Regalfässer und 48 Privatfässer bleiben erhalten.

Der Golemraum hat neun vorbestückte Zieltruhen. Die Listen enthalten konkrete
Itemtypen; Kategorien werden nicht als magische Filter behandelt. Unbekannte oder
nicht mehr unterzubringende Typen müssen am Eingang geklärt werden. Die Grundregeln
folgen den [offiziellen Minecraft-Angaben](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-9).

Die Automatik ist **noch kein fertiger Funktionsnachweis**. Besonders die Shulker-
Sequenzsteuerung, das Abwurf-Pickup und der Droppertakt sind zu vervollständigen.
Feste Jumper sperren vorerst die Pickup-Hopper unter den Bulk-Boxen, damit sie
ihren Inhalt nicht beim Beladen wieder absaugen. Die nötigen Schaltphasen und die
Abnahmefolge stehen in `technik_inbetriebnahme.md`. Der Browserrechner prüft nur
Mengen, Priorität und Rückstau, keine echten Redstone-Ticks oder Golem-KI.

`check_report.json` nennt die aktuellen Modellmengen; `pruefprotokoll.json` hält
die tatsächlichen Prüfungen und offenen Grenzen fest. Ein Ingame-Test wurde nicht
durchgeführt. Die Website ist weiterhin lokal und ohne CDN nutzbar.
