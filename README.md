# Blackthorn Estate · Revision 5.11

`index.html` im Browser öffnen. Die Website funktioniert lokal und offline. Originalwelt und frühere Revisionen bleiben unverändert.

## Terraforming ansehen

Unter **Gelände** stehen die neuen Werkzeuge zusammen:

- **Vorher ↔ Nachher:** Regler verschieben, um Originalwelt und geplante Oberfläche zu vergleichen.
- **Abtrag & Auffüllung:** Orange bedeutet Abtrag, Türkis Auffüllung, Violett beides in derselben Spalte. Erdarbeiten unterhalb der Oberfläche werden ebenfalls berücksichtigt.
- **Spalte auswählen:** Karte anklicken oder X/Z eingeben. Rechts stehen Ist-/Sollhöhe, tatsächliche Abtrags-/Auffüllmengen und alle betroffenen Y-Bereiche. Die Auswahl bleibt beim Verschieben erhalten.
- **Geländeprofil:** West–Ost oder Nord–Süd wählen. Grau zeigt die Originalhöhe, Grün die Planung. Das Profil enthält die Kellerbaugrube; es stellt keine Gebäude oder Höhlen dar.
- **Gelände ohne Haus in 3D:** Erdoberfläche und farbige Arbeitsbereiche frei ansehen. Im Bauatlas schaltet „Haus & Deko“ das Gebäude wieder hinzu.
- **Arbeitsabschnitte:** Aufklappbare Chunk-Tabelle mit exakten Mengen und Kartenverknüpfung. Das Vergleichsbild kann separat geöffnet oder ausgedruckt werden.

## Begrünung und Außenanlagen

7.819 Geländespalten wurden gestaltet. Breitere, mit Erde und Gras bedeckte Böschungen vermitteln zwischen Sockel, Vorplatz, Gartenwegen und Landschaft. 148 freiliegende Sockel-Abdeckblöcke außerhalb der Hausfläche wurden durch Gras ersetzt. 54 alte, im neu gestalteten Gelände überflüssige oder überdeckte Mauerpfosten wurden entfernt. Die übrigen Stützen und nötigen Wegeinfassungen bleiben erhalten. Die östliche Schlucht wurde nicht aufgefüllt.

Der Ankunftsgarten erhält Formschnittinseln, Margeriten und zwei Holzbänke. Ein Kiesweg führt um die Westseite zum Südgarten mit niedrigen Hecken, weißen/lila/blauen Blüten, weiteren Bänken und einem offenen Holzpavillon mit Kupferhaube. Beide Bereiche lassen sich direkt aus der Geländeansicht in 3D öffnen. Sämtliche Dekorationen sind reale Blockpositionen, keine nur gezeichneten Bildzusätze.

Die breiten Böschungen erhöhen die Auffüllmenge gegenüber 5.10 um **26.003 Blöcke**: insgesamt **61.021 Auffüll- und 51.114 Abtragspositionen**. Die zusätzliche Erde ist bewusst für weichere Übergänge eingeplant. Erde/Gras dürfen nicht durch sichtbaren Bruchstein ersetzt werden, wenn die dargestellte Oberfläche erreicht werden soll. Unter bestehenden tragenden Bauteilen bleiben diese Bauteile erhalten.

## Arbeitsdateien

- `terraforming.csv`: jede Arbeitsspalte mit Ist-/Sollhöhe und Mengen.
- `terraforming_chunks.csv`: Abschnittssummen je Minecraft-Chunk.
- `aushub_blockliste.csv`, `auffuellung_blockliste.csv`: genaue Einzelpositionen. Austausch von Stein gegen Erde ist als Abtrag und Baublock erfasst; er erscheint nicht als Auffüllung über der ursprünglichen Bodenhöhe.
- `vegetation_entfernen.csv`, `bestandskonflikte.csv`: Räumung und vorhandene Bauten prüfen.
- `blockliste.csv`, `materialbedarf.csv`, `materialbedarf_baugruppen.csv`: vollständiges Modell und Material. Auffüllblöcke sind hierin bereits enthalten, nicht nochmals addieren.
- `aussendekoration.csv`: Außenbereiche mit Koordinaten und Beschreibung.
- `aenderungen_5.10_zu_5.11.csv`: 41.788 geänderte Positionen gegenüber 5.10.
- `assets/terraforming_vergleich.png`: aus den tatsächlichen Daten berechneter Geländeplan.

## Fortschritt und bisherige Funktionen

Die fünf Hauptbereiche, die Lagerübersicht und die Laternen-Detailansicht aus 5.10 bleiben nutzbar. Unter **Organisation → Fortschritt** kann ein vollständiges 5.10-Backup importiert werden. Unveränderte Blockhäkchen, Zuständigkeiten und Bestandsnotizen bleiben erhalten. Geänderte Positionen und betroffene Baugruppen-Fertigmeldungen werden zurückgesetzt. Wenn beide lokalen Seiten denselben Browser-Speicher nutzen, erfolgt die Übernahme automatisch; der alte Stand wird nicht überschrieben. Andernfalls bitte das Backup importieren.

Die Lagerautomatik ist weiterhin ein unvollständiger Schaltentwurf. Offene Schritte stehen in [Technik und Inbetriebnahme](technik_inbetriebnahme.md).

## Reproduzieren und Prüfgrenzen

```sh
python tools/build.py
python tools/validate.py
node tools/test_app.mjs
node tools/export_preview.mjs
python tools/render_preview.py
python tools/render_terrain.py
```

Der Modellgenerator benötigt Revision 5.10 und die benachbarte `mca.zip`. Der Webgenerator verwendet zusätzlich die bewährten UI-Grundlagen aus 5.9. Die unabhängige Prüfung kontrolliert auch die bisherigen Manifeste und Revision 5.8. Die Bildwerkzeuge benötigen Pillow/NumPy; zum Öffnen der Website sind keine Zusatzprogramme nötig.

Die Modellprüfung gleicht Einzelpositionen mit den Originalregionen ab. 316 Laufzeitprüfungen verwenden DOM-/Canvas-/WebGL-Adapter, einschließlich Spaltenauswahl, Vergleichsregler, Profil, Chunk-Filter und 3D-Sichtbarkeit. HTML, CSS-Klammern, JavaScript-Syntax und beide GLSL-Shader wurden zusätzlich geprüft.

Ein echter Browser-/GPU-Sichttest ist wegen gesperrter Betriebssystem-Sockets nicht möglich. Die Vorschauen sind aus der tatsächlichen Viewer-Geometrie berechnete Software-Renderings. Ingame-Test, Licht-/Spawn-Simulation und eine vollständige Spieler- oder Redstone-Simulation stehen aus. Ausgeführte Prüfungen stehen in `pruefprotokoll.json`.
