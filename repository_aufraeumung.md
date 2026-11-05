# Repository-Bereinigung nach Revision 5.22

Die folgenden Dateien werden vom aktuellen Build und der Website nicht verwendet. Sie liegen weiterhin lokal unter `archive/repository-cleanup-5.22/` und bleiben über Git-Historie erreichbar:

- `tools/export_preview.mjs`
- `tools/test_app.mjs`
- `tools/render_preview.py`
- `tools/render_terrain.py`
- `tools/validate.py`
- `tools/region.py`
- `tools/landscape.py`
- `tools/lighting.py`
- `assets/anwesen_west.png`
- `assets/gelaende_gesamt.png`

Die alten Prüfskripte erwarten die frühere Inline-Datenstruktur bzw. Fortschrittsschlüssel aus 5.10/5.11; die alte Geländeprüfung benötigt die entfernte `mca.zip`. Die früheren Vorschau-Renderer greifen auf feste 5.11-Dateien unter /tmp zu. Ihre zwei ungenutzten Ausgabebilder werden nicht von der aktuellen Website verlinkt.

Bewusst erhalten: Build-Quellen und aktive Seeds (5.9 als UI-Vorlage, 5.21 als Modellbasis), alle aktuell verwendeten Bilder, CSV-Downloads, Technik-Anleitungen und Litematics. `blueprint.json` ist die maschinenlesbare Bauplandatei; `blueprint-data.js` lädt dieselben Daten beim lokalen Öffnen ohne Webserver. `model-data.js` versorgt den Textur-Viewer; die separate NBT-Datei dient dem Download. Diese Dateien erfüllen unterschiedliche Aufgaben.

Nach der Bereinigung wurde der aktuelle Build erneut ausgeführt. Modell-Fingerprint und NBT-Prüfsumme stimmen mit dem vorherigen Stand überein. Der aktuelle Live-Stand des Remotes konnte wegen fehlender Verbindung nicht abgerufen werden; der zuletzt lokal bekannte origin/main zeigt Revision 5.22. Diese Bereinigung entfernt Dateien im aktuellen Branch und schreibt keine alte Git-Historie um.
