# Blackthorn Estate — komplette Codex-Übergabe

**Stand:** 2026-11-04, letzter bearbeiteter Entwurf: **Revision 5.6**.

## Einstieg

- `workspace_snapshot/Blackthorn-Estate-Revision-5.6/index.html` — neueste Browser-Website als Hauptansicht.
- `workspace_snapshot/Blackthorn-Estate-Revision-5.6/blockliste.csv` — neueste Baublöcke mit Koordinaten und Zuständen.
- `workspace_snapshot/Blackthorn-Estate-Revision-5.6/materialbedarf.csv` — Materialbedarf.
- `workspace_snapshot/Blackthorn-Estate-Revision-5.6/lager_kategorien.csv` — Kategorien des Lagers.
- `workspace_snapshot/Blackthorn-Estate-Revision-5.6/villager_staende.csv` — Trading-Hall-Standplanung.
- `workspace_snapshot/Blackthorn-Estate-Revision-5.6/aushub.csv` — aus einem vorherigen Modell abgeleiteter Aushubplan.
- `workspace_snapshot/Blackthorn Estate – Bauplan Revision 5.html` — ursprünglicher, bevorzugter Design-Ansatz (Revision 5).
- `workspace_snapshot/mca.zip` — hochgeladene Minecraft-Regiondaten.
- `workspace_snapshot/level(1).dat` — hochgeladene Welt-Metadaten.
- `workspace_snapshot/image(2).png` … `image(6).png` — bereitgestellte Screenshots / Kritik an Rendern.
- `workspace_snapshot/build_blackthorn_56.py` — lokales Generator-/Änderungsskript der jüngsten Revision.

Alle hier noch verfügbaren Dateien aus der Arbeitsumgebung liegen unter `workspace_snapshot/` mit ihrem ursprünglichen relativen Pfad. Sowohl alte ZIP-Archive als auch entpackte Ordner sind zur lückenlosen Nachverfolgung enthalten; dadurch gibt es bewusst Dopplungen. `manifest.json` listet alle Originalpfade mit Größe und SHA-256.

## Nutzerziel / Anforderungen

Minecraft-Paper-Welt, großes viktorianisches/gotisches Klippenanwesen für 6 Spieler; je 1 private Residenz, gemeinsame Halle/Bibliothek/Ballsaal, 3 Keller, Pool-Aussicht, Survival-taugliche Materialien. Hauptziel **browserbasierter Bauatlas**, nicht `.schem` / `.litematic`: gutes 3D, präzises 2D, Layer für Layer, Hover über Blöcken (Nummer, Blockstate, X/Y/Z), Materiallogistik und gemeinsamer Fortschritt.

Weltseed aus vorherigem Projektkontext: `-4815224116428668341`; Bauanker ursprünglich X=-662, Y=126/129, Z=790; Boden EG meist Y=129. **Klippe westlich (−X), Eingang östlich (+X).** Der Nutzer äußerte später den Wunsch nach 180°-Drehung; diese wurde wegen des realen Geländes in den letzten Revisionen nicht tatsächlich ausgeführt. Pool soll auf Westseite weit über die Klippe blicken. Verifizierte Weltgeometrie ist entscheidend.

## Versionen / Historie (grober Überblick)

- Voxel Blueprint v2–v4, Bauatlas v5–v9.1: ältere Modell-/UI-Versuche.
- Hochgeladene `Blackthorn Estate – Bauplan Revision 5.html`: bevorzugter Three.js-Stil mit eingebettetem Datenmodell.
- Revisionen 5.1–5.2.1: Zusammenführung, Orientierung und Fassadenkorrekturen.
- Revision 5.3: originale Regiondaten erneut zur Boden-/Höhlenanalyse benutzt; Aushub, Fundament und Eingang untersucht.
- Revision 5.4: spaltenbasierter Aushub statt großflächig freigeschnittenem Gelände; Pool-Aussichtsbereich erweitert.
- Revision 5.5: neues Dachkonzept. **Wichtige Warnung:** Dachmaterial/Blockzahl sprangen von ~54.000 auf ~78.000 Positionen, insbesondere durch massive `deepslate_tiles`-Dachfüllungen; nicht automatisch als fertig oder survival-optimiert betrachten.
- Revision 5.6: eine Einwurftruhe; geplante Redstone-Bulkfilter (Dirt, Cobblestone, Eisen etc.), Kupfergolem-Normalware, 10 Villager-Trading-Stände, Geheimräume. Die Redstone-/Kupfergolem-Technik ist **noch nicht im Minecraft-Spiel getestet**.

## Risiken und offene Aufgaben

1. **Priorität: Datenvalidierung und realistische Geometrie.** Nicht jede bisherige generierte Revision war fehlerfrei. Gab schwebende Elemente, leere Gelände-Void-Flächen und unpassende Dachübergänge. Die Bauhöhe/Blocksituation muss in echter Welt gegen Regiondaten geprüft werden.
2. **Aushub** und Höhlen: Höhenkarte allein erfasst keine echten Höhlenverbindungen; Aushubschätzung ist kein Block-für-Block-NBT-Differenzmodell. Vor Survival-Bau verifizieren.
3. **Dach 5.5/5.6** wurde generativ stark gefüllt; auf zu viele massive Blöcke, Kollisionen, ungültige Treppen-Blockstates und fehlende Kopffreiheit prüfen.
4. **Lagertechnik**: Einwurftruhe -> Redstone-Massenfilter -> Kupfertruhe -> Kupfergolems; sorgfältige Taktung, Kapazität, Overflow, Entnahme und Golem-Wege müssen geprüft werden. Die vorhandenen technischen Positionen sind eher räumliche Planung als garantiert funktionierende Schaltung.
5. **Browser**: originale Three.js-Website benötigt ggf. CDN/Internet. Für echte Offline-Nutzung Bibliothek lokal bündeln. Rendering und Clicks in Browser testen (nicht nur Syntax).
6. **Vermessung**: Grün ist überwiegend `grass_block`, Pflanzen wie Allium/Wildflowers stehen obenauf; Pflanzen nicht als Boden oder 3D-Schichten verwechseln.
7. Materiallisten/Block-IDs bei jeder Änderung automatisch aus tatsächlichen Koordinaten ableiten. Prüfen auf doppelte Koordinaten, Treppen-/Türhälften und Blockstates.

## Codex Workflow-Vorschlag

1. Aktuelle V5.6 Website und Blueprint aus HTML öffnen, Daten dekodieren (siehe `script#data` im HTML).
2. MCA-Dateien und Höhenprofil einlesen; Chunk-/Blockdaten statt nur Heightmap zur Geländeanbindung nutzen.
3. Mit Tests gegen CSVs prüfen. Erst danach Roof-/Foundation-/Trading-/Sorting-Refinements durchführen.
4. Website mit lokaler Three.js-Abhängigkeit und Browserautomation testen.
5. Bei neuen Revisionen alte Dateien unverändert archivieren; Tests, Materialzahlen, 3D-Screenshots und Unterschiede festhalten.

## Datenverzeichnis

`manifest.json` enthält eine vollständige Hash-Liste der archivierten Workspace-Dateien. Im Archiv befinden sich ebenfalls alle verfügbaren alten ZIP-Dateien — einschließlich doppelter Kopien ihrer entpackten Inhalte.
