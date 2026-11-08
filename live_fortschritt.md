# Live-Baufortschritt – Paper und Vercel

Der Atlas enthält jetzt **Organisation → Live-Baufortschritt**. Das Plugin liest die Welt und überträgt einen Prüfstand an Vercel. Es setzt oder entfernt keine Blöcke und lädt keine Chunks nach. Keine Portfreigabe ist erforderlich: Der Minecraft-Server sendet HTTPS-Anfragen nach außen.

## Installation

1. Den aktuellen Git-Stand auf Vercel veröffentlichen, einschließlich `api/build-progress.mjs`, `server/build-progress.mjs` und `live-plan.json`.
2. In Vercel unter **Settings → Environment Variables** zusätzlich `LIVE_BUILD_WRITE_TOKEN` für **Production** anlegen. Einen eigenen zufälligen Token mit mindestens 32 Zeichen verwenden, z. B. lokal erzeugt mit `node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))"`. Dies ist ein anderer Schlüssel als der Teamcode. Anschließend neu deployen.
3. Die vorhandenen Redis-Variablen (`KV_REST_API_URL` / `KV_REST_API_TOKEN` oder `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN`) und `SHARED_LIST_TEAM_CODE` bleiben erforderlich. Das Plugin erhält ausschließlich den neuen Schreibtoken, keine Datenbankzugangsdaten.
4. Server stoppen. `downloads/BlackthornLive.jar` in den `plugins`-Ordner kopieren. Server einmal starten, damit `plugins/BlackthornLive/config.yml` entsteht. Solange Endpoint und Token fehlen, deaktiviert sich das Plugin mit einem Hinweis.
5. Server wieder stoppen und in dieser Datei setzen:

   ```yaml
   world: world
   endpoint: https://DEIN-PROJEKT.vercel.app/api/build-progress
   write-token: 'DEIN-SEPARATER-SCHREIBTOKEN'
   offset-x: 0
   offset-y: 0
   offset-z: 0
   ```

   `world` muss der echte Bukkit-Weltname sein. Die Offsets bleiben null, wenn an den Koordinaten aus dem Atlas gebaut wird. Bei versetztem Bau gilt: Weltkoordinate = Atlas-Koordinate + Offset. Eine Rotation wird nicht unterstützt. Der Endpoint muss direkt auf das richtige Deployment zeigen; HTTP-Weiterleitungen werden nicht verfolgt. Der Server muss diese HTTPS-Adresse erreichen können. Bei einer geschützten Vercel-Vorschau kann deren Zugangsschutz den Aufruf blockieren; normale Production-Adresse verwenden.
6. Server neu starten. Als Operator `/blackthornlive status` ausführen. Es müssen die zum V6-Atlas passende Anzahl an Positionen geladen sein. Nach kurzer Zeit sollte bei Upload `OK` erscheinen.
7. Im Baugebiet spielen oder vorhandene Chunks laden. Im Atlas **Organisation → Live-Baufortschritt** mit eurem gemeinsamen Teamcode anmelden. Der Plugin-Schreibtoken gehört nicht ins Website-Anmeldefeld.

## Anzeige und Aktualisierung

- **Ungeprüft:** Bereich seit dem letzten Scan nicht geladen; wird nicht als fertig oder fehlend gezählt.
- **Richtig:** Material und alle im Bauplan ausdrücklich festgelegten Blockzustände stimmen überein.
- **Fehlt:** An einer geplanten Blockposition befindet sich Luft.
- **Anderer Block:** Das Material stimmt nicht.
- **Blockzustand weicht ab:** Etwa Treppenrichtung oder obere/untere Blockhälfte stimmen nicht.

Pro Bauteil wird der Anteil richtiger Positionen an allen geplanten Positionen angezeigt. Die Tabelle darunter kann auf eine Y-Ebene gefiltert werden und öffnet einzelne Baupositionen im 3D-Atlas. Die Koordinaten dort bleiben Atlas-Koordinaten; konfigurierte Offsets sind im Spiel hinzuzurechnen.

Übertragungen und Redis-Prüfstände werden komprimiert. Vercel und Upstash zählen trotzdem API-Aufrufe und Datenverkehr; während der Server läuft, wird alle zehn Sekunden übertragen.

Standard: maximal 300 Positionen und ungefähr 2 Millisekunden Scanbudget je Tick, Upload alle 10 Sekunden, Website-Abruf alle 10 Sekunden bei sichtbarer Live-Ansicht. Ein normaler Kontrolllauf dauert unter idealen Bedingungen ungefähr 23 Sekunden, bei Last länger. Spieler-Blockänderungen samt direkten Nachbarn werden bevorzugt beim nächsten Scan bearbeitet. Explosionen, Kolben, Flüssigkeiten, WorldEdit und andere Plugin-Änderungen werden spätestens durch den fortlaufenden Kontrolllauf erfasst. Auch das Zurücksetzen ungeladener Bereiche auf „ungeprüft“ erfolgt bei diesem Lauf. Das angezeigte Prüfdatum ist der Zeitpunkt des gesamten übermittelten Prüfstands, nicht der individuelle Prüfzeitpunkt jedes Blocks. Niedrige TPS und Netzwerkfehler verzögern die Anzeige.

Ein Übertragungsstand älter als 45 Sekunden wird als veraltet markiert. Bei Abruffehlern bleibt der letzte Stand sichtbar und wird ausdrücklich als letzter empfangener Stand bezeichnet. Nach Serverneustart beginnt der Scan bei „ungeprüft“; der alte Stand bleibt im Atlas bis zur ersten neuen Übertragung sichtbar.

`/blackthornlive rescan` setzt die Prüfung zurück. Beide Befehle benötigen `blackthorn.live.admin` (standardmäßig Operator). Konfigurationsänderungen benötigen einen Neustart; `/reload` wird nicht verwendet.

## Grenzen

Die Prüfung umfasst die geplanten Baupositionen inklusive Geländeauffüllung. Bereits vorhandene passende Naturblöcke zählen als richtig. Zusätzliche Blöcke außerhalb dieser Positionen, Aushub, erforderliche Luftbereiche, Inventare, Entitäten, Beleuchtungswirkung und funktionierende Redstone-Schaltungen werden nicht geprüft. Dynamische Zustände im Bauplan können während des Betriebs zeitweise abweichen. Die Anzeige ist eine Bauplanprüfung und keine technische Ingame-Abnahme. Automatische Ergebnisse werden getrennt von manuellen Bauhäkchen und Materialbeständen gespeichert.

Genau ein Plugin darf in dieselbe Atlas-Umgebung schreiben. Production, Preview und Development sowie unterschiedliche Bauplan-Fingerprints sind getrennt. Ein anderer Bauplan wird mit HTTP 409 abgelehnt; ab Plugin 1.4.0 den automatischen Abgleich abwarten oder `/blackthornlive sync` ausführen. Bei älteren Plugins ist die passende JAR nötig. HTTP 401 bedeutet falscher Schreibtoken, 503 fehlende Vercel-/Redis-Einrichtung oder Datenbankfehler, 400 ungültiger Prüfstand oder unpassende Serveruhr. Plugin-Logs enthalten keine Token.

## Quellcode und Build

`paper-plugin/` enthält das Plugin. Java 25 oder neuer und Gradle 9 werden benötigt. Aus dem Repository:

```sh
python tools/live_plan.py
gradle -p paper-plugin clean jar
```

Ergebnis: `paper-plugin/build/libs/BlackthornLive.jar`. Für die Website-Downloadfunktion diese Datei nach `downloads/BlackthornLive.jar` kopieren. `tools/build.py` erzeugt den Plugin-Bauplan bei Modelländerungen automatisch neu; ab Plugin 1.4.0 genügt bei reinen Bauplanänderungen das Veröffentlichen von Website und Server-Plandatei. Die API verwendet den kleinsten hier benötigten 26.x-Stand (26.1.2), das Zielsystem ist euer Paper 26.3. Das mitgelieferte JAR ist für Java 25 kompiliert.

Das JAR wurde kompiliert und die Website-/API-Prüfungen lokal ausgeführt. Ein gemeinsamer Test mit eurem tatsächlichen Paper-Server und Vercel ist nach der Konfiguration noch erforderlich. Zum Abnehmen eine bekannte Position passend setzen, falsch ausrichten und entfernen und jeweils den Zustand im Atlas kontrollieren; anschließend einen Chunk entladen und den Übergang zu „ungeprüft“ abwarten.

Grundlagen: [Paper-Projektaufbau](https://docs.papermc.io/paper/dev/project-setup/), [BlockData-Vergleich](https://jd.papermc.io/paper/26.1.2/org/bukkit/block/data/BlockData.html#matches(org.bukkit.block.data.BlockData)), [Scheduler](https://docs.papermc.io/paper/dev/scheduler/).

## Ab Plugin 1.4.0: Baupläne automatisch übernehmen

Einmalig Plugin **1.4.0** installieren und die neue Website einschließlich `api/build-plan.mjs` sowie `live-server-plan.tsv.gz` veröffentlichen. Die Vercel-Funktion benötigt weiterhin den vorhandenen `LIVE_BUILD_WRITE_TOKEN`; es gibt keinen zusätzlichen Schlüssel. Die bestehende Plugin-Konfiguration bleibt verwendbar.

Danach wird **beim Start, ungefähr jede Minute und nach einem Bauplan-Konflikt** der aktuelle Plan beim gleichen Website-Host abgefragt. Ändert sich nur der Bauplan, ist keine neue JAR und kein Serverneustart mehr nötig. Die Download-Adresse wird automatisch aus dem vorhandenen Endpoint abgeleitet. Veröffentlichte Bauplanrevisionen müssen Website-Metadaten und die komprimierte Server-Plandatei gemeinsam enthalten; `python tools/build.py` erzeugt beides.

Bei einem neuen Plan werden unveränderte Positionen mit ihren Prüfergebnissen übernommen. Neue oder geänderte Positionen werden neu geprüft. Die Website hält Prüfstände verschiedener Fingerprints weiterhin getrennt. Nach dem Wechsel dauert es bis zur nächsten Übertragung, bevor dort Werte erscheinen.

Das Plugin speichert einen erfolgreich übernommenen Plan in `plugins/BlackthornLive/current-plan.tsv.gz`. Bei einem Neustart ist dieser Plan auch ohne Website verfügbar. Ist die lokale Datei ungültig, wird der eingebettete Plan verwendet. Fehlerhafte Downloads, fehlende neue Endpunkte oder unbekannte Blockzustände ersetzen keinen aktiven Plan. Größe, Koordinaten, Format, doppelte Positionen und Weltgrenzen werden geprüft. Netzwerkfehler haben Zeitlimits und werden erneut versucht. Downloads enthalten nur Blockdaten und keine auszuführenden Java-Dateien.

Mit `/blackthornlive sync` lässt sich der Abgleich manuell starten; `/blackthornlive status` zeigt **Upload** und **Abgleich** getrennt. `sync-seconds: 60` ist der Standard; alte Konfigurationsdateien ohne diesen Eintrag verwenden ihn ebenfalls. HTTP 404 beim Planabgleich bedeutet meistens, dass die Website den neuen Endpunkt noch nicht enthält. HTTP 401 bedeutet weiterhin einen falschen Plugin-Schreibtoken. Ein blockierter Vercel-Zugang muss unabhängig davon freigegeben werden.

Die automatische Anpassung gilt für Baupläne im unterstützten Schema 1, nicht für beliebige zukünftige Paper-/Minecraft-API-Änderungen. Neue, auf dem laufenden Server unbekannte Blocktypen oder ein geändertes Datenformat können ein Server- beziehungsweise Plugin-Update erfordern. Der Decoder unterstützt bis zu 500.000 Positionen und maximal 2 MiB komprimierte / 32 MiB entpackte Plandaten. Solche Fehler werden gemeldet, der bisherige Plan bleibt erhalten.

Lokal geprüft: kompilierte JAR, Download-Authentifizierung, unveränderte Pläne (HTTP 304), Plan-/Metadatenkonsistenz, Versionswechsel im Decoder, beschädigte Dateien, doppelte Koordinaten und Downloadgrößenlimit. Die vollständige automatische Übernahme auf eurem laufenden Paper-Server muss nach Installation einmal geprüft werden.
