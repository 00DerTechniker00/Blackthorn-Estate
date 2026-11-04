# Revision 5.12 · Minecraft-Strukturviewer

Revision 5.12 macht das vollständige Anwesen mit den originalen Java-26.3-Blockmodellen und -Texturen darstellbar. Dazu exportiert der Generator sämtliche 132.070 Positionen des bestehenden Modells als gzip-komprimierte Minecraft-Strukturdatei. Der Export umfasst Palette, Blocknamen, Eigenschaften/Blockstates und den ursprünglichen Weltursprung X −791 / Y 105 / Z 703. Er enthält keine erfundenen Inventardaten.

Im Unterbereich **Bauatlas → Minecraft-Texturen** wird die Datei erst nach einem bewussten Klick an den externen Structure Viewer übergeben. Der Viewer kann `.nbt` direkt laden und bietet freie 3D-Ansicht sowie Rundgang. Beim eingebetteten Aufruf nutzt die Seite die dokumentierte `postMessage`-Schnittstelle, wartet auf das Bereitschaftssignal und lädt zuerst die Minecraft-Daten für 26.3. Die externe Seite erhält damit dieselben Blockdaten, die auch in der mitgelieferten NBT-Datei stehen. Ein Link zum manuellen Herunterladen und Öffnen bleibt sichtbar.

Die Transferinformation steht direkt vor dem Viewer. Die Nutzerseite weist darauf hin, dass die Daten an `structure-viewer.ewanhowell.com` übergeben werden und die Minecraft-Texturen eine Internetverbindung brauchen. Andere Atlas-Ansichten bleiben lokal. Die Website lädt den externen Renderer nicht beim Öffnen der Startseite.

Das Gebäude, die 236 Laternen, der neue Garten, das Gelände, die Materiallisten und Erdarbeiten sind gegenüber 5.11 unverändert. Die Kompatibilität des Fortschritts speichert exakt den 5.11-Fingerabdruck und eine leere Änderungsmenge; Häkchen, Zuständigkeiten und Lagernotizen bleiben deshalb erhalten. `aenderungen_5.11_zu_5.12.csv` dokumentiert die fehlenden Modelländerungen.

Der Site-Code und die Strukturdatei wurden lokal erzeugt. In dieser Umgebung war kein echter Browser verfügbar, daher wurde der externe 26.3-Renderlauf nicht visuell überprüft. Falls die Verbindung oder ein Versionsdownload beim Anwender fehlschlägt, kann die ausgelieferte `.nbt`-Datei direkt in der Viewer-Website geöffnet werden. Die technische Ingame-Simulation, Redstone- und Lichtsimulation bleiben außerhalb dieses Renderexports.
