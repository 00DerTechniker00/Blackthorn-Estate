"""5.9-specific UI: current rotation, real component coordinates and flow examples."""
import csv
import json
import re
from pathlib import Path


def finalize(root,d):
    s=d['storage_system'];html=(root/'index.html').read_text()
    (root/'system.js').write_text((root/'tools/system.js').read_text())
    tech='''<section class="tab" id="tab-system">
      <div class="hero"><div class="card lead"><small class="eyebrow">LOGISTIK · JAVA / PAPER 26.3</small><h1>Lose Stacks oben.<br>Shulker-Reserven darunter.</h1><p>Einwurf und Shulker-Unloader speisen die Hubstrecke. Sechs Filter ziehen die festgelegten Bulk-Typen ab. Alles andere gelangt zur Kupfertruhe des getrennten Golemraums.</p><div class="cta"><button class="btn" id="sysGotoInput">Einwurf im Plan</button><button class="btn" id="sysGotoTrade">Trading Hall</button></div></div><div class="card"><h2>Was schon konkret ist</h2><p>Bauteile, Behälter, Hopperrichtungen, sechs Filterstrecken, Sensoren und Vorratsräume stehen im Blockmodell. Filterinventare und Zieltypen sind als CSV dokumentiert.</p><p class="muted">Die Signalverriegelungen, Taktgeber, vertikale Hubstrecke und Shulker-Abwurfaufnahme brauchen noch einen Test in Minecraft. Die folgende Mengenprobe ist ein Logikmodell, kein Nachweis einer lauffähigen Schaltung.</p><a href="technik_inbetriebnahme.md">Schaltphasen &amp; Testfolge</a></div></div>
      <div class="sys-flow"><div>Einwurf / Unloader</div><span>→</span><div>6 Bulkfilter</div><span>→</span><div>Kupfer-Eingang</div><span>→</span><div>9 Zieltruhen</div></div>
      <div class="grid2"><div class="card"><h2>Bulk: zuerst Vorrat, dann Verpackung</h2><p>Pro Material bleibt ein Fass mit bis zu 27 Stacks losem Vorrat verfügbar. Der Überlauf wird aus der Zuleitung entnommen – nicht aus dem Vorratsfass. Volle Shulker fallen über eine Hopper-Säule in drei darunter liegende Fässer: zusammen 81 Boxplätze je Material.</p><p>Fehlende Leerboxen oder ein voller Ausgang müssen die Zufuhr sperren. Der Packzyklus lautet: Füllen → Zufuhr sperren → volle Box brechen → Aufnahme bestätigen → Leerbox setzen → weiterfüllen.</p><div id="sysBulk"></div></div><div class="card"><h2>Kupfergolems: konkrete Typen statt Etiketten</h2><p>Alle neun Zieltruhen werden mit passenden Itemtypen vorbestückt. Andere Typen fallen nicht automatisch unter eine Kategorie. Mindestens ein Seed-Item pro gewünschtem Typ erhalten; keine leere Catch-all-Truhe in den Raum stellen.</p><p>Unbekannte Typen und volle Zieltruhen bleiben ein sichtbarer Klärfall am Kupfer-Eingang. Die Fässer im Regallager bleiben als große manuelle Reserve erhalten.</p><div id="sysRegular"></div></div></div>
      <div class="card" style="margin-top:18px"><h2>Shulker-Stationen neben dem Einwurf</h2><div id="sysStations"></div><p>Der Unloader gibt den Inhalt voller Boxen in dieselbe Sortierstrecke. Die leere Hülle muss getrennt zurückgegeben werden. Der allgemeine Loader erhält einen eigenen Materialvorrat; er verpackt gezielt eingelegte Items und mischt nicht automatisch den gesamten Einwurf.</p><div class="row"><a class="btn" href="technik_module.csv" download>Module &amp; Koordinaten</a><a class="btn" href="technik_inventare.csv" download>Filter- &amp; Seed-Inventare</a><a class="btn" href="technik_inbetriebnahme.md">Inbetriebnahme</a></div></div>
      <div class="card" style="margin-top:18px"><h2>Mengenprobe für ein Bulk-Modul</h2><p class="muted">Frisches Modul, leeres Vorratsfass, keine gespeicherten Boxen. Nur 64er Bulk-Items. Diese Probe prüft Kapazität und Priorität, keine Redstone-Timingeffekte.</p><div class="toolbar"><label>Material <select id="simItem"></select></label><label>Neue Items <input id="simAmount" type="number" min="0" max="1000000" value="5000"></label><label>Leere Boxen <input id="simBoxes" type="number" min="0" max="1000" value="27"></label><button class="btn" id="simRun">Durchlauf berechnen</button></div><p id="simResult" role="status"></p></div>
      <div class="card" style="margin-top:18px"><h2>Aktueller Kellergrundriss</h2><label>Etage <select id="sysLevel"><option value="121">Keller 1 · Logistik</option><option value="113">Keller 2 · Regale &amp; Shulker-Silos</option><option value="105">Keller 3 · Handel &amp; Privat</option></select></label><div class="sys-map-wrap"><canvas id="sysMap" width="980" height="580"></canvas></div><p id="sysInfo" role="status">Markierung auswählen, um ihre Weltkoordinaten zu sehen.</p></div>
      <div class="grid2" style="margin-top:18px"><div class="card"><h2>Trading Hall</h2><div id="sysStalls"></div></div><div class="card"><h2>Technische Grenzen</h2><p>Die Platzhalter-Shulker im Modell zeigen die aktive Boxposition. Inventare, Villager und Golems werden im Spiel eingerichtet. Das Logikmodell zählt keine Box doppelt und meldet Rückstau. Physische Itemaufnahme, Pulsreihenfolge, Chunk-Neuladen und Paper-Einstellungen müssen separat geprüft werden.</p><p>Grundlage für das Golemverhalten: <a href="https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-9">offizielle Minecraft-Regeln</a>. Zielversion: <a href="https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3">26.3</a>.</p></div></div>
    </section>'''
    html=re.sub(r'<section class="tab" id="tab-system">.*?</section>',lambda _:tech,html,flags=re.S)
    # Patch captions outside the embedded JSON only.
    parts=re.split(r'(<script type="application/json" id="data">.*?</script>)',html,flags=re.S)
    for i in range(0,len(parts),2):parts[i]=parts[i].replace('Eingang (Ost)','Pool (Ost)').replace('Klippe (West)','Eingang (West)')
    html=''.join(parts)
    html=html.replace('<script src="app.js">','<script src="logistics.js"></script>\n<script src="app.js">')
    # Inline data was injected before this step: only replace exterior HTML text.
    (root/'index.html').write_text(html)
    app=(root/'app.js').read_text()
    app=app.replace("'dach_bibliothek', 'dach_ostfluegel']","'dach_bibliothek', 'dach_ostfluegel','dach_schmuck']")
    app=app.replace("'lager_regale','privatlager']","'lager_regale','privatlager','shulker_technik']")
    app=app.replace("const stackOf = id => (STACK1.has(id) || id.endsWith('_bed'))", "const stackOf = id => (STACK1.has(id) || id.endsWith('_bed') || id.endsWith('shulker_box'))")
    app=app.replace('d:320,t:[-695,112,790]','d:380,t:[-690,112,790]')
    app=app.replace('Eingang (Ost)','Pool (Ost)')
    app=app.replace('Außenanlagen zur westlichen Klippe','Außenanlagen mit Panorama nach Osten').replace('5 · Ostflügel & Eingang','5 · Westlicher Eingangsflügel').replace('Dach Ostflügel','Dach Eingangsflügel')
    app=app.replace("'terraform_oberflaeche','zufahrt']", "'terraform_oberflaeche','zufahrt','weg_sicherung']",1)
    app=app.replace("const GROUP_DE = {", "const GROUP_DE = {weg_sicherung:'Wegeinfassung & Absturzschutz',")
    app=app.replace("id === 'chain'", "(id === 'chain' || id === 'iron_chain')")
    app=app.replace("const BASE_DE = {", "const BASE_DE = {iron_chain:'Eisenkette',shulker_box:'Shulkerkiste',waxed_copper_chest:'Gewachste Kupfertruhe',")
    app=app.replace("const COLORS = {", "const COLORS = {iron_chain:'#3a3c42',")
    app=app.replace('[[5, 1, 5, 11, 8, 11], [6, 8, 6, 10, 10, 10]]', '[[5, 1, 5, 11, 8, 11], [6, 8, 6, 10, 10, 10], [7,10,7,9,16,9]]')
    app=app.replace('const CUSTOM = {', '''const CUSTOM = {
      hopper:[],waxed_copper_chest:[[1,0,1,15,14,15]],redstone_wire:[[0,0,0,16,1,16]],
      repeater:[[0,0,0,16,2,16]],comparator:[[0,0,0,16,2,16]],redstone_wall_torch:[[6,3,6,10,14,10]],''')
    app=app.replace('function shapeBoxes(r, x, y, z, vis) {','''function shapeBoxes(r, x, y, z, vis) {
      if(r.id==='hopper'){const spout={down:[6,0,6,10,6,10],north:[6,4,0,10,8,6],south:[6,4,10,10,8,16],east:[10,4,6,16,8,10],west:[0,4,6,6,8,10]}[r.p.facing||'down'];return [[0,10,0,16,16,16],[4,5,4,12,10,12],spout];}''')
    # Explicitly localize all introduced materials so none falls back to magenta.
    app=app.replace("const COLORS = {", "const COLORS = {polished_diorite:'#d1d0c9',waxed_oxidized_cut_copper_slab:'#579989',waxed_copper_chest:'#bd7953',shulker_box:'#8d6aa1',dispenser:'#777e7b',dropper:'#777e7b',piston:'#9b8a69',redstone_block:'#af302a',redstone_wall_torch:'#bc4e2d',")
    app=app.replace("const GROUP_DE = {", "const GROUP_DE = {dach_schmuck:'Gauben & Kupferdetails',shulker_technik:'Shulker-Stationen',")
    (root/'app.js').write_text(app)
    # The regular terrain module uses current world coordinates and measured waypoints.
    terrain=(root/'terrain.js').read_text().replace('rect(-725,749,-641,831','rect(-739,747,-654,833').replace('rect(-722,766,-670,814','rect(-710,766,-658,814')
    (root/'terrain.js').write_text(terrain)
    with (root/'technik_module.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Modul','Material','Rolle','X','Y','Z','Status'])
        for a in s['bulk']:
            for role in ['loose','active_box','dispenser','piston','empty_supply']:
                w.writerow([a['id'],a['label'],role,*a[role],'26.3-Ingame-Test ausstehend'])
            for p in a['bins']:w.writerow([a['id'],a['label'],'Shulker-Reserve',*p,'27 Boxplätze'])
        for a in s['stations']:
            for role in ['active_box','dispenser','piston','catch']:w.writerow([a['id'],a['name'],role,*a[role],'26.3-Ingame-Test ausstehend'])
    with (root/'technik_inventare.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Modul','X','Y','Z','Slot','Item','Anzahl','Hinweis'])
        for a in s['bulk']:
            p=a['filter'];w.writerow([a['id'],p['x'],p['y'],p['z'],1,a['id'],41,'64er Filteritem'])
            for slot in range(2,6):w.writerow([a['id'],p['x'],p['y'],p['z'],slot,'paper',1,f'Im Amboss umbenennen: BLACKTHORN_FILTER_{slot}'])
        for a in s['regular']:
            for slot,bid in enumerate(a['seeds'],1):w.writerow([a['id'],a['x'],a['y'],a['z'],slot,bid,1,'Seed erhalten; Typenliste kann gezielt ergänzt werden'])
