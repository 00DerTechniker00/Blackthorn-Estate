# Blackthorn Estate · Revision 5.10

`index.html` im Browser öffnen. Die Website funktioniert ohne Server und ohne Internet. Revision 5.9 und die Originalwelt wurden nicht verändert.

Die fünf Hauptbereiche führen direkt zur jeweiligen Aufgabe:

- **Start:** kurze Übersicht und Einstieg in Haus, Gelände oder Lager.
- **Bauatlas:** 3D-Modell, Ebenenplan, Baubegleitung, Raumbuch und Leuchtenplan. In 3D lassen sich Etagen direkt auswählen und weitere Filter bei Bedarf aufklappen.
- **Gelände:** Ist-/Soll-Karte mit Koordinaten und Arbeitsmengen. Messdetails sind einklappbar.
- **Lager:** durchsuchbare Tabelle der 56 Lagerbuchten sowie eine eigene Technikansicht.
- **Organisation:** Baufortschritt in aufklappbaren Phasen, Materialbedarf und alle Arbeitsdateien.

Auf schmalen Bildschirmen öffnet „Bereiche“ die Navigation. Der Schalter „Darstellung wechseln“ wählt ein helles oder dunkles Design.

## Laternen

236 Leuchten ersetzen die bisherige Verteilung mit 414 Leuchten. Die 211 automatisch ergänzten Boden- und Langkettenleuchten wurden entfernt und durch 33 gezielte Deckenleuchten ergänzt. Geplante Kronleuchter und Terrassenleuchten bleiben erhalten. Keine Aufhängung braucht mehr als zwei Kettenblöcke.

Unter **Bauatlas → Leuchtenplan** kann jede Laterne gesucht und nach Höhe oder Montageart gefiltert werden. „3D“ zeigt Leuchte, Kette und Träger isoliert; „Ganzes Haus“ stellt das Modell wieder her. „Plan“ öffnet ihre Position im Ebenenplan. Metallrahmen, Leuchtkern, Bügel und Anschluss sind separat modelliert. `laternen_pruefung.csv` führt alle tatsächlichen Positionen und Träger auf.

Die Befestigungen sind am Blockmodell geprüft. Eine Licht-/Spawn-Simulation und ein Minecraft-/Paper-Test stehen aus.

## Fortschritt übernehmen

Unter **Organisation → Fortschritt** vollständiges Backup exportieren oder importieren. Ein unverändertes 5.9-Backup wird erkannt: unveränderte Blockhäkchen, Zuständigkeiten und Lagerbestände bleiben erhalten; geänderte Leuchtenpositionen und die Fertigmeldung der Baugruppe „Beleuchtung“ bleiben offen. Der alte Browser-Speicher wird nicht überschrieben. Wenn beide lokalen Seiten denselben Browser-Speicher nutzen, wird der Stand auch automatisch übernommen. Andernfalls das Backup importieren.

## Arbeitsdateien

`blockliste.csv`, `materialbedarf.csv` und `materialbedarf_baugruppen.csv` entsprechen dem aktuellen Modell. `aenderungen_5.9_zu_5.10.csv` enthält 447 geänderte Positionen ausschließlich der Beleuchtung. `terraforming.csv` und die Abtrag-/Auffülllisten enthalten auch den einen zusätzlich auszubauenden Steinblock für eine neue Deckenleuchte. Auffüllblöcke sind bereits Teil der Baumaterialien, nicht nochmals addieren.

Der Architektur- und Lagerentwurf aus 5.9 bleibt erhalten: Pool im Osten, Eingang im Westen, Zufahrt aus Nordwesten. Die Lagerautomatik ist weiterhin ein unvollständiger Schaltentwurf. Siehe [Technik und Inbetriebnahme](technik_inbetriebnahme.md).

## Prüfen und reproduzieren

```sh
python tools/build.py
python tools/validate.py
node tools/test_app.mjs
node tools/export_preview.mjs
python tools/render_preview.py
```

Der Generator benötigt die benachbarte Revision 5.9 und `mca.zip`; die unabhängige Prüfung zusätzlich die bisherigen Originalmanifeste und Revision 5.8. Die Vorschauen benötigen Pillow und NumPy. Zum normalen Öffnen ist davon nichts nötig.

295 Laufzeitprüfungen verwenden DOM-/WebGL-Adapter. GLSL-Shader, HTML-Struktur, Modellmengen, Listen, Türen, Lagerzugänge und Befestigungen wurden zusätzlich geprüft. Ein echter Browser-/GPU-Sichttest ist hier wegen gesperrter Betriebssystem-Sockets nicht möglich. Die Bilder unter `assets/` sind aus der tatsächlichen Viewer-Geometrie berechnete Modellvorschauen.
