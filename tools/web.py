"""Package the new model in the existing local atlas, with current UI text only."""
import json
import re
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'Blackthorn-Estate-Revision-5.7'


def patch(s,old,new):
    if old not in s:raise ValueError('Missing source fragment: '+old[:80])
    return s.replace(old,new)


def build():
    d=json.loads((ROOT/'blueprint.json').read_text());t=d['terrain'];v=d['validation'];summary=d['storage_summary']
    fmt=lambda n:f'{n:,}'.replace(',','.')
    html=(BASE/'index.html').read_text()
    html=re.sub(r'<script type="application/json" id="data">.*?</script>','__DATA__',html,flags=re.S)
    html=html.replace('5.7','5.9').replace('Gelände &amp; Höhlen','Gelände &amp; Erdarbeiten')
    overview=f'''<section class="tab" id="tab-overview">
      <div class="hero"><div class="card lead"><small class="eyebrow">REVISION 5.9 · VIKTORIANISCHES KLIPPENANWESEN</small>
      <h1>Das Panorama am Pool.<br>Neue Details. Neue Logistik.</h1>
      <p class="muted">Um 180° gedreht: Pool und Aussicht liegen jetzt im Osten, Eingang und Zufahrt im Westen. Gauben, Kupferakzente und steinerne Gesimse ergänzen den Entwurf. Die Logistik bekommt Bulk-Puffer, Shulker-Stationen und einen eigenen Golemraum.</p>
      <div class="cta"><button class="btn primary" data-go="3d">Anwesen in 3D</button><button class="btn" data-go="storage">Lager ansehen</button><button class="btn" data-go="terrain">Erdarbeiten planen</button></div></div>
      <a class="preview card" href="assets/anwesen_ost.png"><img src="assets/anwesen_ost.png" alt="Aus dem tatsächlichen Blockmodell berechnete Ostansicht des neuen Hauses"><span>Modellvorschau · Poolansicht von Osten</span></a></div>
      <div class="stats overview-stats"><div class="stat"><b id="st-blocks">–</b><span>Baupositionen inkl. Erdauftrag</span></div><div class="stat"><b id="st-items">–</b><span>Material-Items</span></div><div class="stat"><b>{summary['new_barrels']}</b><span>Fässer in neuen Lagerbuchten</span></div><div class="stat"><b>{fmt(summary['total_slots'])}</b><span>Inventarplätze insgesamt</span></div><div class="stat"><b id="st-rooms">–</b><span>Räume / Bereiche</span></div><div class="stat"><b id="st-doors">–</b><span>Türen</span></div><div class="stat"><b id="st-stairs">–</b><span>Treppenblöcke</span></div><div class="stat"><b id="st-panes">–</b><span>Glasscheiben</span></div></div>
      <div class="facts" id="facts"></div>
      <div class="grid2"><div class="card"><h2>Mehr viktorianische Details</h2><p>Sechs verglaste Gauben, profilierte Gesimse, helle Ecksteine und grün patinierte Kupferakzente. Die vorhandenen Dachschalen bleiben erhalten; die hohen Turmgeschosse kehren nicht zurück.</p><p>Der Weg durch die Bibliothek zum Pool ist freigeräumt. Die hohe Treppe und die Möblierung aus dem Türbereich sind entfernt, der Vorplatz ist eben. Laternen wurden auf Halt und Kettenanschlüsse geprüft.</p><a href="assets/anwesen_west.png">Westansicht mit Eingang öffnen</a></div>
      <div class="card"><h2>Automatik als konkreter Bauentwurf</h2><p>50 Lagerbuchten mit je acht Fässern im zweiten Keller: 400 Fässer und 10.800 Plätze. Dazu kommen sechs Privatreserven mit je acht Fässern im dritten Keller. Das bestehende Sortierlager bleibt separat.</p><p>Zusätzlich: sechs Bulk-Module mit losem Vorrat und Shulker-Reserven, neun vorbestückte Golem-Zieltruhen und zwei Shulker-Stationen neben dem Einwurf. Controller und Pickup müssen noch in einer 26.3-Testwelt abgenommen werden.</p><button class="btn" data-go="storage">Kategorien &amp; Koordinaten</button></div></div>
      <div class="card" style="margin-top:18px"><h2>Prüfstand dieser Revision</h2><div id="checks"></div><a href="analysebericht.md">Änderungen und Prüfgrenzen lesen</a></div>
      <div class="notice" style="margin-top:18px">3D: ziehen = drehen · Shift/Rechtsklick = verschieben · Mausrad = zoomen. Unter <b>Gelände</b> zwischen Original, Zielzustand und Erdarbeiten wechseln. Einzelblöcke nach Höhe bauen; vollständige Fortschritts-Backups unter <b>Bauplan</b>.</div>
    </section>'''
    html=re.sub(r'<section class="tab" id="tab-overview">.*?</section>',lambda _:overview,html,flags=re.S)
    terrain=f'''<section class="tab" id="tab-terrain">
      <div class="card"><small class="eyebrow">ORIGINALREGION · 281 × 221 BLÖCKE</small><h1>Die Landschaft um das Anwesen</h1>
      <p class="muted">X −825…−545 · Z 680…900. Die umliegenden Hangkanten sind Teil der Ansicht. Ist- und Soll-Boden werden pro Spalte gegenübergestellt; weiter draußen bleibt die Landschaft unverändert.</p>
      <div class="toolbar"><label>Karte <select id="geologyMode"><option value="earthworks">Abtrag &amp; Auffüllung</option><option value="surface">Originaloberfläche</option><option value="target">Geplante Oberfläche</option><option value="height">Natürliche Bodenhöhe</option><option value="delta">Höhenänderung</option></select></label><button class="mini" id="geologyReset">Karte einpassen</button><button class="mini" data-go="3d">In 3D ansehen</button></div>
      <p class="earth-legend"><span class="cut-key">Orange: Abtrag</span><span class="fill-key">Türkis: Auffüllung</span><span>Violett: beides in einer Spalte</span><span>Ocker: Oberflächenwechsel</span></p>
      <div class="stage" style="height:min(72vh,760px)"><canvas id="geologyCanvas"></canvas><div class="hint">Ziehen / zoomen · Hover zeigt Ist-Y, Soll-Y und Blockmengen</div></div>
      <div id="geologyHover" class="notice" style="margin-top:12px" role="status">Mit der Maus über eine Spalte fahren.</div></div>
      <div class="stats" style="margin:18px 0"><div class="stat"><b>{fmt(v['excavation_blocks'])}</b><span>vorhandene Blöcke entfernen</span></div><div class="stat"><b>{fmt(v['fill_blocks'])}</b><span>Blöcke oberhalb des bisherigen Bodens auffüllen</span></div><div class="stat"><b>{fmt(v['vegetation_clear'])}</b><span>Vegetations-/Aufbauten-Blöcke separat räumen</span></div></div>
      <div class="grid2"><div class="card"><h2>So wird das Grundstück angepasst</h2><p><b>Keller:</b> Baugrube bis unter die Bodenplatte Y=105. <b>Haus:</b> Unterbau bis Y=128 unter dem bewohnten Hauptkörper. <b>Garten:</b> schmale Böschungsübergänge an Nord und Süd. Pool und Terrasse schauen jetzt nach Osten über den Geländeeinschnitt. Die darunter liegende Landschaft wird nicht pauschal aufgefüllt.</p><p><b>Zufahrt:</b> fünf Blöcke breiter Weg nach Nordwesten bis X≈−783 / Z≈711, mit breiten Schultern statt einer Führung direkt an der Hangkante. Höhensprünge sind als begehbare Stufen im Zielgelände modelliert.</p></div>
      <div class="card"><h2>Vorhandene Welt respektieren</h2><p>Die Mengen stammen aus dem mitgelieferten Welt-Snapshot. Vorhandene identische Baumaterialien werden nicht als Abtrag gezählt. Auffüllungen sind im Bauplan enthalten; ihre Materiallisten sind eine Teilmenge der Gesamtmaterialien.</p><p><b>{v['existing_structure_conflicts']} vorhandene Bau-/Markerblöcke</b> liegen im Arbeitsbereich. Diese vor dem Bauen prüfen: <a href="bestandskonflikte.csv" download>Bestandskonflikte als CSV</a>. Licht, Standsicherheit und Weganschlüsse müssen im Spiel kontrolliert werden.</p></div></div>
      <div class="card" style="margin-top:18px"><h2>Arbeitslisten für eure Gruppe</h2><div class="row"><a class="btn" href="terraforming.csv" download>Ist-/Soll-Spalten</a><a class="btn" href="aushub_blockliste.csv" download>Abtrag: Einzelblöcke</a><a class="btn" href="auffuellung_blockliste.csv" download>Auffüllung: Einzelblöcke</a><a class="btn" href="vegetation_entfernen.csv" download>Vegetation räumen</a></div><div class="row"><a class="btn" href="aushub_materialien.csv" download>Abtrag nach Material</a><a class="btn" href="auffuellung_materialien.csv" download>Auffüllung nach Material</a></div><p class="muted">Die 3D-Geländeoberfläche ist eine Höhenfläche. Sie zeigt die großen Formen und Erdarbeiten, aber keine vollständigen unterirdischen Höhlen. Die Einzelblocklisten wurden aus den tatsächlichen Regionsblöcken abgeleitet.</p></div>
    </section>'''
    terrain=terrain.replace('</section>','<div class="card" style="margin-top:18px"><h2>Das gesamte Umfeld im Modell</h2><a href="assets/gelaende_gesamt.png"><img src="assets/gelaende_gesamt.png" alt="Berechnete Gesamtansicht mit erweitertem Gelände" style="width:100%;height:auto;border-radius:10px"></a><p class="muted">Berechnete Modellvorschau. Im 3D-Reiter über „Gesamtgelände“ frei drehen und zoomen.</p></div></section>')
    html=re.sub(r'<section class="tab" id="tab-terrain">.*?</section>',lambda _:terrain,html,flags=re.S)
    html=patch(html,'<button class="mini" data-cam="east">','<button class="mini" data-cam="estate">Gesamtgelände</button><button class="mini" data-cam="east">')
    html=patch(html,'<span>Gelände</span></label>','<span>Gelände</span></label><label>Geländezustand <select id="terrainState"><option value="target">Geplantes Gelände</option><option value="original">Originalgelände</option><option value="work">Erdarbeiten farbig</option></select></label>')
    html=patch(html,'<button class="mini" data-floor="175">Alles</button>',f'<button class="mini" data-floor="{d["meta"]["bbox"][3]}">Alles</button>')
    html=patch(html,'<h1>Lagerplanung für die echten Kellerräume</h1>','<h1>56 neue Lagerbuchten für eure Materialien</h1>')
    a=html.index('<p class="muted">Der neue Sortierkeller enthält');end=html.index('</p>',a)+4
    html=html[:a]+f'<p class="muted">400 Fässer im zweiten Keller und 48 Fässer in sechs Privatreserven: {fmt(summary["new_slots"])} Plätze in diesen neuen Buchten, insgesamt {fmt(summary["total_slots"])} Plätze im Anwesen. Jede Kategorie verweist auf ihre echte Position. Das Sortierlager in Keller 1 ist zusätzlich vorhanden. Die neuen Reserven werden manuell befüllt.</p><div class="row"><button class="btn" onclick="__openGroup(\'lager_regale\')">Regallager in 3D</button><a class="btn" href="lagerbuchten.csv" download>Alle Buchten als CSV</a></div>'+html[end:]
    html=html.replace('Alle Blockpositionen','Alle Blockpositionen')
    html=patch(html,'min="105" max="175"',f'min="{d["meta"]["bbox"][2]}" max="{d["meta"]["bbox"][3]}"')
    html=html.replace('__DATA__','<script type="application/json" id="data">'+json.dumps(d,ensure_ascii=False,separators=(',',':'))+'</script>')
    (ROOT/'index.html').write_text(html)

    app=(BASE/'app.js').read_text()
    a=app.index('function buildTerrain()');end=app.index('/* Dependency-free WebGL viewer.',a)
    app=app[:a]+(ROOT/'tools/terrain_geometry.js').read_text()+'\n'+app[end:]
    app=patch(app,"function predNow() { return i=>!S3.hidden.has(REG[R[i]].gi); }", "function predNow() { return i=>!S3.hidden.has(REG[R[i]].gi) && !['terraform_auffuellung','terraform_oberflaeche','zufahrt'].includes(REG[R[i]].g); }")
    app=patch(app,"function buildGroupPanel() {", "function buildGroupPanel() {")
    app=patch(app,"  D.groups.map((g, i) => [g, i]).sort", "  D.groups.map((g, i) => [g, i]).filter(([g])=>!['terraform_auffuellung','terraform_oberflaeche','zufahrt'].includes(g)).sort")
    app=patch(app,"preset('east'); $('#loading')","preset('iso'); $('#loading')")
    app=patch(app,"const PRESETS={", "const PRESETS={estate:{th:.68,ph:.80,d:320,t:[-695,112,790]},")
    app=patch(app,'east:{th:.25,ph:1.12,d:135','east:{th:.25,ph:1.12,d:175')
    app=patch(app,'west:{th:Math.PI-.3,ph:1.15,d:140','west:{th:Math.PI-.3,ph:1.15,d:180')
    app=patch(app,'iso:{th:.75,ph:.95,d:165','iso:{th:.75,ph:.95,d:195')
    app=patch(app,"lager_technik:'Lagertechnik'", "lager_technik:'Lagertechnik',fassade:'Fassade & Gesimse',sockel:'Tragender Sockel',lager_regale:'Regallager · 400 Fässer',privatlager:'Private Lagerreserven',terraform_auffuellung:'Erdauftrag & Unterbau',terraform_oberflaeche:'Gartenoberflächen',zufahrt:'Vorplatz & Zufahrt',dach_schmuck:'Gauben & Kupferdetails',shulker_technik:'Shulker-Stationen'")
    app=patch(app,"groups: ['fundament','hang_stuetzen','eingang_vorplatz']", "groups: ['fundament','hang_stuetzen','eingang_vorplatz','sockel','terraform_auffuellung','terraform_oberflaeche','zufahrt']")
    app=patch(app,"'geheimgang','lager_technik']", "'geheimgang','lager_technik','lager_regale','privatlager','shulker_technik']")
    app=patch(app,"groups: ['halle', 'galerie', 'bibliothek']","groups: ['halle', 'galerie', 'bibliothek','fassade']")
    app=app.replace('Terrasse, Pool, Observatorium','Terrasse & Pool').replace('Außenanlagen und Zierturm auf dem Hallenfirst.','Außenanlagen zur westlichen Klippe; niedrige Erkerhauben sind Teil des Daches.')
    app=app.replace("'lager_technik'].includes(g)","'lager_technik','lager_regale','privatlager'].includes(g)")
    app=app.replace("${fmt(D.validation.surface_columns_checked)} Bodensäulen mit der Minecraft-Region abgeglichen; ${fmt(D.validation.surface_mismatches.length)} Abweichungen.","${fmt(D.validation.terrain_columns)} Bodensäulen aus der Originalregion eingelesen. Ist-/Soll-Höhen und Erdarbeiten sind im erweiterten Geländeplan verfügbar.")
    app=app.replace('Die übernommenen Aushubgrenzen sind noch keine vollständig geprüfte Baugrube.','Baugrube und Auffüllung wurden für den neuen Grundriss berechnet. Auffüllung: ${fmt(D.terrain.fill_total)} Blöcke; diese sind in den Baumaterialien enthalten.')
    app=app.replace('(Kuppel)','(First)').replace('Dachgruppen: Halle bis Y 155 · Residenzen bis Y 155 · Ostflügel bis Y 141','Halle Y 157 · Gauben Y 154 · Kupferdetails')
    app=patch(app,"const COLORS = {","const COLORS = {bricks:'#986c60',polished_diorite:'#d4d5ce',waxed_oxidized_cut_copper_slab:'#5d9d88',waxed_copper_chest:'#bf7950',shulker_box:'#9567a4',piston:'#8d826c',dispenser:'#777e7c',dropper:'#777e7c',redstone_block:'#a82822',redstone_wall_torch:'#bb4c2c',")
    # Public view controls reuse exactly the geometry read by the 2D work map.
    app=patch(app,"window.__showTab = showTab;", "window.__showTab = showTab;\nwindow.__focusPlan=(x,y,z)=>{planSetMode('y');PL.val=y;$('#planRange').value=y;showTab('plan');planCenter(x,z);};")
    app=patch(app,'  location.hash = id;','  location.hash = id;\n  window.dispatchEvent(new Event(\'bt:tab\'));')
    end=app.rfind('})();')
    app=app[:end]+'''$('#terrainState').onchange=e=>{S3.terrainMode=e.target.value;if(GL&&GL.terrain){GL.terrain.buffers.forEach(b=>GL.gl.deleteBuffer(b));GL.terrain=uploadGeometry(buildTerrain());GL.dirty=true;}};
''' + app[end:]
    (ROOT/'app.js').write_text(app)
    for name in ['progress.js','steps.js','system.js','styles.css']:
        s=(BASE/name).read_text().replace('5.7','5.9')
        if name=='steps.js':
            start=s.index('function jumpToRoom(');end=s.index('\nfunction renderStorage',start)
            s=s[:start]+"function jumpToRoom(zone){window.__focusPlan(zone.x[0],zone.y[0],zone.z[0]);}"+s[end:]
            s=s.replace('Originalraum:','Bereich:').replace('Math.max(105,currentHeight()-1)',f'Math.max({d["meta"]["bbox"][2]},currentHeight()-1)').replace('Math.min(175,currentHeight()+1)',f'Math.min({d["meta"]["bbox"][3]},currentHeight()+1)')
        if name=='system.js':
            s=patch(s,"if(level===113){rect(-682,768,-672,784,'#514c35','Zusatzlager');for(const x of [-680,-677,-674])pin(x,115,775,'Überlauf- und Shulkerlager','#e1b86c')}",
                "if(level===113){rect(-706,767,-671,813,'#35423b','50 Lagerbuchten · 400 Fässer');rect(-706,788,-671,792,'#645943','Mittelgang');for(const b of d.storage_bays.filter(b=>b.floor===113))pin(b.x,b.y,b.z,b.id+' · '+b.name+' · '+b.slots+' Plätze','#e1b86c');}")
            s=patch(s,"if(level===105){rect(","if(level===105){for(const b of d.storage_bays.filter(b=>b.floor===105))pin(b.x,b.y,b.z,b.name,'#d2b790');rect(")
        (ROOT/name).write_text(s)
    with (ROOT/'styles.css').open('a') as f:f.write('''
.eyebrow{display:block;letter-spacing:1.8px;color:var(--accent);font-weight:600;margin-bottom:14px}
.overview-stats{grid-template-columns:repeat(4,minmax(0,1fr));margin-bottom:20px}.hero .preview{padding:0;overflow:hidden;position:relative;display:block;color:var(--ink);text-decoration:none}.preview img{display:block;width:100%;height:100%;min-height:300px;object-fit:cover}.preview span{position:absolute;bottom:0;left:0;right:0;padding:10px 16px;background:var(--panel);font-size:12px;color:var(--muted)}
.earth-legend{display:flex;gap:18px;flex-wrap:wrap;font-size:13px}.cut-key{color:#c66b24}.fill-key{color:#258b82}#terrainState{max-width:220px}
@media(max-width:650px){.overview-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.preview img{min-height:220px}}
''')
    for name in ['villager_staende.csv','lager_kategorien.csv']:
        shutil.copyfile(BASE/name,ROOT/name)
    from web_extra import finalize
    finalize(ROOT,d)
    print('Weboberfläche 5.9 erzeugt.')


if __name__=='__main__':build()
