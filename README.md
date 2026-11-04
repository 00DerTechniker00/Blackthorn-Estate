# Blackthorn Estate · Revision 5.8

`index.html` im Browser öffnen. Der Atlas und alle Vorschauen funktionieren lokal,
ohne CDN oder Internet. Die 3D-Ansicht setzt WebGL voraus.

## Was sich geändert hat

- Ruhigeres viktorianisches Herrenhaus: niedrig gestaffelte Dachkörper, keine hohe
  Observatoriumskuppel, niedrige Erkerhauben, durchlaufende Steingesimse und Portikus.
- Neue Dachschalen mit Unterdeckung statt massiver Dachfüllungen. Der bestehende
  Grundriss mit sechs Residenzen und drei Kelleretagen bleibt erhalten.
- Keller 2: 50 Lagerbuchten mit zusammen 400 Fässern. Keller 3: sechs Privatreserven
  mit zusammen 48 Fässern. Alle 56 Buchten mit Kategorien und echten Koordinaten.
- Rund 221 × 171 Blöcke Originalgelände in der Umgebung. In 3D stehen
  „Originalgelände“, „Geplantes Gelände“ und „Erdarbeiten farbig“ zur Wahl.
  „Gesamtgelände“ bewegt die Kamera weiter nach außen.
- Terraforming-Karte mit Ist-/Soll-Höhen, Abtrag, Auffüllung und Vegetationsräumung.
  Zufahrt über den südöstlichen Plateaustreifen statt über die direkte östliche Hangkante.

## Wo ihr was findet

- **Übersicht:** berechnete Modellvorschau, neue Dachform und Kapazität.
- **3D-Modell:** Gebäude, Schichten, weiter herausgezoomte Landschaft und drei Geländezustände.
- **Lagerplanung:** alle Lagerkategorien, Koordinaten und Bestandsnotizen.
- **Sortierkeller & Handel:** Kellerübersicht einschließlich der 50 Regallagerbuchten.
- **Gelände & Erdarbeiten:** orange = Abtrag, türkis = Auffüllung, violett = beides,
  ocker = Oberflächenwechsel. Hover zeigt Mengen und Weltkoordinaten.
- **Bauplan:** vollständiges Backup von Fortschritt und Bestandsnotizen.

## Arbeitslisten

`blockliste.csv` und `materialbedarf*.csv` enthalten Haus, Einrichtung und geplante
Erdauffüllung. `auffuellung_materialien.csv` ist eine Teilmenge davon – nicht nochmals
zur Gesamtliste addieren. Die Abtragliste enthält vorhandene Blöcke, keine Baumaterialien.

`terraforming.csv` beschreibt jede Arbeitsspalte, `aushub_blockliste.csv` den Abtrag,
`auffuellung_blockliste.csv` den Auftrag und `vegetation_entfernen.csv` die separate
Räumung von Vegetation oberhalb des Bodens. `bestandskonflikte.csv` enthält betroffene
vorhandene Marker und gebaute Blöcke. Diese vor einer Umsetzung im Spiel prüfen.

`lagerbuchten.csv` enthält die tatsächlichen Fasspositionen als Buchtenübersicht;
alle Einzelbehälter stehen zusätzlich in `blueprint.json` und der Blockliste.

## Prüfungen

```sh
python tools/model.py
python tools/web.py
python tools/validate.py
node tools/test_app.mjs
```

Die Modell-/Webgeneratoren benötigen Python 3.10+ und die benachbarte Revision 5.7
sowie `mca.zip`. Beim normalen Öffnen des Bauatlas werden diese Quellen nicht benötigt.

Die Vorschauen unter `assets/` stammen aus den tatsächlichen Geometrien des lokalen
Viewers, die mit einem Software-Renderer gezeichnet wurden. Es sind keine KI-Bilder
und keine Browser-Screenshots. Zum Neuerzeugen: `node tools/export_preview.mjs`, dann
`python tools/render_preview.py` (dafür zusätzlich Pillow und NumPy).

Der Browserstart ist in dieser Ausführungsumgebung durch gesperrte Betriebssystem-
Sockets blockiert. Laufzeit- und Datenprüfungen ersetzen keinen Browser-/Minecraft-Test.
Licht, Redstone, Kupfergolemwege, Dachanschlüsse und Geländestabilität sind noch im Spiel
zu prüfen. Die neuen Lagerbuchten werden manuell befüllt; sie sind kein fertig
verkabeltes automatisches Lagersystem.

Fortschrittsdateien älterer Modelle werden wegen der Änderungen nicht automatisch
übernommen. Revision 5.7 und alle ursprünglichen Übergabedateien bleiben erhalten.
