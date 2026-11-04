# Blackthorn Estate · Revision 5.9

`index.html` im Browser öffnen. Vorherige Versionen und Originalwelt bleiben unverändert.

- **180° gedreht:** Pool und Panorama nach Osten, Eingang nach Westen. Die Welt
  selbst wurde nicht gedreht; Erdarbeiten sind gegen dieselben Originalregionen neu berechnet.
- **Zufahrt Nordwest:** breiterer Unterbau, Wegschultern und Abstand zum natürlichen
  Geländeeinschnitt. Die Messdefinition steht in `blueprint.json` unter `route_safety`.
- **Poolzugang:** Treppe, Möbel und Leuchten aus dem Türdurchgang entfernt. Ebenes
  Podest innen und außen; Türhälften und Richtungen mitgedreht.
- **Mehr Details:** sechs verglaste Gauben, helle Ecksteine und Gesimse, Kupferfirst
  und Erkerfinials. Die ruhige Hauptform bleibt erhalten.
- **Laternen:** Aufhängungen korrigiert, Ketten ergänzt, ungeeignete Leuchten entfernt.
  Auch der sichtbare Anschluss von Laternenbügel zu Kette ist im Renderer ergänzt.
- **Lagerentwurf:** sechs Bulk-Filter mit losem Vorrat und tiefer liegenden
  Shulker-Speichern, neun Golem-Zieltruhen, Loader/Unloader neben dem Einwurf.
  Die 400 Regallager- und 48 Privatfässer bleiben als manuelle Reserve erhalten.

**Wichtig zur Automatik:** Die Shulker-Sequenzsteuerung, die vertikale Dropper-
Taktung und die Box-Aufnahme sind noch nicht fertig verdrahtet bzw. im Spiel
bestätigt. Der Atlas kennzeichnet sie als Schaltentwurf, nicht als betriebsfertige
Automatik. Siehe [Technik und Inbetriebnahme](technik_inbetriebnahme.md).
Der Browser-Mengenrechner ersetzt keine Redstone-/Paper-Simulation.

## Listen

`blockliste.csv`, `materialbedarf.csv`, `materialbedarf_baugruppen.csv` enthalten
die tatsächlichen Baupositionen. `terraforming.csv` zeigt Ist-/Soll-Boden und
Arbeitsmengen; Abtrag und Auffüllung sind zusätzlich als Einzelblocklisten vorhanden.
Die Auffülllisten sind eine Teilmenge der Baumaterialien, nicht nochmals addieren.

`technik_module.csv` und `technik_inventare.csv` dokumentieren die technischen
Positionen sowie manuell einzurichtende Inventare. `lagerbuchten.csv` enthält die
erhaltenen Regallager-/Privatbuchten mit ihren neuen Weltkoordinaten.

Alle Blockstates, Raumbereiche, Inventarpositionen und Ziele wurden um 180° um
X=-690/Z=790 gedreht. Fortschritt früherer Versionen wird nicht automatisch übernommen.

## Prüfen / reproduzieren

```sh
python tools/model.py
python tools/web.py
python tools/validate.py
node tools/test_app.mjs
```

Generatoren brauchen die benachbarte Revision 5.8 und `mca.zip`. Zum normalen
Öffnen reicht der ausgelieferte Ordner, ohne Internet. Vorschauen werden aus der
tatsächlichen Viewer-Geometrie berechnet: `node tools/export_preview.mjs`, danach
`python tools/render_preview.py` (Pillow/NumPy erforderlich).

Ein Browser-/GPU-Sichttest ist in dieser Ausführungsumgebung wegen gesperrter
Betriebssystem-Sockets blockiert. Die Modellvorschauen sind Software-Renderings.
Minecraft-/Paper-Tests sowie eine aktuelle Lichtsimulation stehen aus.
