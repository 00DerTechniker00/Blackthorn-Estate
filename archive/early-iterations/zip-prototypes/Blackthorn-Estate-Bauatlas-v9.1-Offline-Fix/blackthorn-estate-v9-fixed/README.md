# Blackthorn Estate V9.1 – Offline-Fix

## Start (empfohlen)

1. ZIP vollständig entpacken.
2. Die Datei **index.html doppelklicken**. Ein Server ist nicht mehr erforderlich.
3. Falls der Browser sehr langsam ist: 3D-Ansicht zunächst auf ein einzelnes Stockwerk stellen.

Die neue `app.bundle.js` enthält die JavaScript-Module in einer ausführbaren Datei; `blueprint-data.js` stellt alle Blockdaten lokal ohne `fetch` bereit. Die ursprünglichen `js/*.js` und `blueprint.json` bleiben für Änderungen im Archiv erhalten.

## Unverändert
50.875 Blockpositionen, Lagerzonen, Materialien, Koordinaten, Gelände- und Fundamentdaten. Bestehender Fortschritt bleibt im selben Browser grundsätzlich erhalten, sofern die Browser-Speicherherkunft gleich bleibt; beim Wechsel von http://localhost zu file:// kann er getrennt sein. Fortschritt vorher exportieren, wenn die alte Website noch erreichbar ist.

## Technische Hinweise
Diese Version behebt insbesondere das Problem beim direkten Öffnen aus dem Dateisystem (ES-Module/Fetch). Bei erneuten Problemen Browserkonsole öffnen (F12), Fehlermeldung ablesen. Ein direkter Datei-Browsertest war in der Erstellungsumgebung durch eine Sicherheitsrichtlinie gesperrt; JavaScript-Syntax und Datenkonsistenz wurden überprüft.
