# Gemeinsame Materialliste auf Vercel

Die neue Ansicht **Organisation → Gemeinsame Liste** speichert Materialbestände, Häkchen und Notizen zentral. Alle im Team nutzen denselben Teamcode und sehen die Änderungen, während die Liste geöffnet ist, nach spätestens etwa fünf Sekunden. Name und Zeitpunkt stehen an jedem Material. „Abgehakt“ ist eine manuelle Fertigmeldung; „Vorhanden“ bleibt eine eigene Zahl. Haus/Keller, Außenanlagen und Gelände haben getrennte Bestände, sodass sich ihre Mengen nicht doppelt verrechnen.

Die vorhandenen Baugruppen- und Blockhäkchen bleiben lokal. Die gemeinsame Liste hat eine eigene Backup-Datei; der Teamcode steht darin nicht.

## Einmalig auf Vercel aktivieren

1. Den aktuellen Git-Stand inklusive `api/`, `server/`, `shared-list.js`, `shared-plan.json`, `package.json` und `vercel.json` veröffentlichen.
2. Im Vercel-Projekt unter **Storage / Marketplace** eine **Upstash Redis**-Datenbank verbinden. Ihre REST-Zugangsdaten werden in den Server-Einstellungen benötigt:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN` (Token mit Schreibrechten)

   Automatisch gesetzte Vercel-Variablen `KV_REST_API_URL` und `KV_REST_API_TOKEN` werden ebenfalls unterstützt; dann braucht ihr sie nicht umzubenennen.
3. Unter **Settings → Environment Variables** zusätzlich `SHARED_LIST_TEAM_CODE` setzen. Mindestens 16 Zeichen, am besten ein zufälliger Code, den ihr nur im Team teilt. Ein Beispiel zum lokalen Erzeugen:

   ```sh
   node -e "console.log(require('node:crypto').randomBytes(24).toString('hex'))"
   ```

4. Die Variablen für **Production** setzen und das Projekt **neu deployen**. Keine echten Werte in Git oder in Frontend-JavaScript eintragen. `.env.example` zeigt nur die Namen der Einstellungen.
5. In der veröffentlichten Website **Organisation → Gemeinsame Liste** öffnen, Namen und Teamcode eingeben. Auf einem zweiten Gerät anmelden und eine Änderung kontrollieren.

Vercel-Einstellungen: Framework **Other**, Build- und Install-Befehl leer, Output Directory `.`. `vercel.json` bereitet die Node-Funktion vor; das vorhandene Python-Bauprojekt wird auf Vercel nicht neu gebaut. Die Datenbankzugänge bleiben ausschließlich im Server. Der Teamcode wird im Browser nur für den jeweiligen Tab gespeichert.

Der optionale Listenname `SHARED_LIST_NAMESPACE` hat den Standard `blackthorn:materials:v1`. Diesen Namen und die Datenbank bei normalen Deployments beibehalten, damit eure Liste erhalten bleibt. Vercel-Preview-Deployments verwenden automatisch eine separate Liste mit dem Suffix `:preview`. Lokale Entwicklungsumgebungen verwenden entsprechend `:development`. Für eine Preview müssen die Variablen auch in dieser Vercel-Umgebung eingerichtet sein.

## Gemeinsam bearbeiten

- Menge und Notiz beim Verlassen des Felds speichern; Checkboxen speichern sofort.
- Während des Tippens ist die Änderung ein Entwurf. Erst **Zentral gespeichert** bestätigt die Datenbank-Speicherung.
- Bei gleichzeitigen Änderungen am selben Material zeigt die Liste den anderen Stand. **Meine Änderung übernehmen** wendet die eigenen geänderten Felder auf den aktuellen Stand an. **Aktuellen Stand verwenden** verwirft den eigenen Entwurf.
- Änderungen an verschiedenen Materialien überschreiben sich nicht. Eine wiederholte Anfrage nach einem Verbindungsabbruch wird anhand ihrer Änderungs-ID erkannt.
- Bei Verbindungsfehlern bleiben Entwürfe im Tab erhalten. Sie werden nicht automatisch über fremde Änderungen geschrieben.
- **Listen-Backup** exportiert den zuletzt bestätigten zentralen Stand. Noch ungespeicherte Entwürfe stehen nicht in diesem Backup.

Die Sollmengen kommen aus dem jeweiligen veröffentlichten Bauplan. Bei einer neuen Hausversion bleibt der Bestand erhalten; erforderliche Mengen und manuelle Häkchen sollten dann im Team geprüft werden. Bei unterschiedlichen Bauplanversionen fordert die Website zum Neuladen auf.

Alle mit dem Teamcode haben dieselben Bearbeitungsrechte. Der eingegebene Name dient der Zuordnung, nicht als separates Benutzerkonto. Datenbanktoken und Teamcode werden serverseitig geprüft; der Datenbanktoken wird nicht an Browser ausgeliefert.

## Prüfen

```sh
npm test
```

Die Tests verwenden zwei simulierte Browser und einen Redis-REST-Adapter. Zusätzlich wird das tatsächliche Lua-Skript lokal ausgeführt, wenn Python und liblua5.4 verfügbar sind. Sie prüfen Autorisierung, Eingaben, konkurrierende Änderungen, erneute Anfragen, Datenbankfehler und die Trennung von Vorschau und Produktion. Ein Test gegen die tatsächlich verbundene Vercel-/Upstash-Installation ist nach dem Einrichten erforderlich. Datenbank und Functions haben eigene Nutzungsgrenzen; Abfragen werden nur bei geöffneter, sichtbarer Liste ausgeführt.

Technische Grundlagen: [Vercel Node-Funktionen](https://vercel.com/docs/functions/runtimes/node-js), [Dateien in Vercel-Funktionen](https://vercel.com/kb/guide/how-can-i-use-files-in-serverless-functions), [Upstash REST API](https://upstash.com/docs/redis/features/restapi). Die Aktualisierung eines Materials verwendet eine atomare Redis-Lua-Operation mit Versionsvergleich.
