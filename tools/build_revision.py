#!/usr/bin/env python3
"""Rebuild 5.7 from the unchanged 5.6 handover. No network or pip required."""
import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from region import Region

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_RE = r'<script type="application/json" id="data">(.*?)</script>'
AIR = {'air', 'cave_air', 'void_air'}


def write_csv(path, header, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(header)
        w.writerows(rows)


def replace(s, old, new):
    if old not in s:
        raise ValueError('Source changed, missing patch: ' + old[:100])
    return s.replace(old, new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent/'Blackthorn-Estate-Revision-5.6')
    args = parser.parse_args()
    source = args.source.resolve()
    if source == ROOT:
        raise ValueError('Source must be the original 5.6 directory')
    original = (source/'index.html').read_text()
    d = json.loads(re.search(DATA_RE, original, re.S).group(1))
    assert d['meta']['version'] == '5.6'
    blocks = {}
    for y,z,x,n,ri in d['runs']:
        for xx in range(x,x+n):
            assert (xx,y,z) not in blocks
            bid,state,gi = d['reg'][ri]
            blocks[xx,y,z] = (bid,state,d['groups'][gi])
    before = blocks.copy()

    def put(x,y,z,bid,state='',group='lager_technik'):
        blocks[x,y,z] = (bid,state,group)

    # The room-clear pass in 5.6 deleted the last two feed hoppers.
    for z in (795,796):
        put(-675,123,z,'hopper','facing=south,enabled=true')
    # Each bulk output used to terminate in empty space, three blocks before its chest.
    for bay in d['storage_system']['bulk']:
        for z in (781,780):
            put(bay['x'],122,z,'hopper','facing=north,enabled=true')
    # Move the south-facing central door away from the filter wiring below it.
    blocks.pop((-689,123,787))
    for y,half in ((122,'lower'),(123,'upper')):
        put(-689,y,788,'dark_oak_door',f'facing=south,half={half},hinge=left,open=false,powered=false','keller_1')
    # Remove the obsolete orphan in front of the new secret door. Move that door
    # down onto the actual Y=105 floor instead of leaving it unsupported in air.
    blocks.pop((-689,106,793))
    blocks.pop((-689,108,794))
    for y,half in ((106,'lower'),(107,'upper')):
        put(-689,y,794,'dark_oak_door',f'facing=north,half={half},hinge=left,open=false,powered=false','geheimgang')

    # Keep the architectural roof silhouette; no unverified hollowing/spawn cavities.
    # Identify heavy enclosed roof fill for the next architecture pass.
    solid = {p for p,(bid,_,g) in blocks.items() if g.startswith('dach_') and bid=='deepslate_tiles'}
    roof_core = sum(all((x+dx,y+dy,z+dz) in solid for dx,dy,dz in
        [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]) for x,y,z in solid)

    # Material and group counts are independently derived from block coordinates.
    groups = d['groups']
    reg, lookup, runs = [], {}, []
    counts, group_materials = Counter(), defaultdict(Counter)
    stats = {}
    ordered = sorted(blocks, key=lambda p:(p[1],p[2],p[0]))
    rows=[]
    for number,(x,y,z) in enumerate(ordered,1):
        bid,state,g = blocks[x,y,z]
        record=(bid,state,groups.index(g))
        if record not in lookup:
            lookup[record]=len(reg);reg.append(record)
        ri=lookup[record]
        if runs and runs[-1][0]==y and runs[-1][1]==z and runs[-1][2]+runs[-1][3]==x and runs[-1][4]==ri:
            runs[-1][3]+=1
        else:
            runs.append([y,z,x,1,ri])
        st=stats.setdefault(g,{'n':0,'x':[x,x],'y':[y,y],'z':[z,z]});st['n']+=1
        for k,value in [('x',x),('y',y),('z',z)]:st[k]=[min(st[k][0],value),max(st[k][1],value)]
        if not (bid=='water' or bid.endswith('_door') and 'half=upper' in state or bid.endswith('_bed') and 'part=head' in state):
            counts[bid]+=1;group_materials[g][bid]+=1
        rows.append([number,x,y,z,'minecraft:'+bid,state,g])
    d.update(reg=reg,runs=runs,counts=dict(counts),gcounts={g:dict(group_materials[g]) for g in groups},gstats=stats)
    fingerprint=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
    d['meta'].update(version='5.7',total=len(blocks),fingerprint=fingerprint)
    changes=[]
    for p in sorted(set(before)|set(blocks),key=lambda p:(p[1],p[2],p[0])):
        if before.get(p)!=blocks.get(p):changes.append([*p,*(before.get(p) or ('','','')),*(blocks.get(p) or ('','',''))])
    write_csv(ROOT/'aenderungen_5.6_zu_5.7.csv',['X','Y','Z','Alt-Block','Alt-State','Alt-Gruppe','Neu-Block','Neu-State','Neu-Gruppe'],changes)
    write_csv(ROOT/'blockliste.csv',['Nummer','X','Y','Z','Minecraft-Block','Blockstate','Baugruppe'],rows)
    def stack(bid):return 1 if bid.endswith('_bed') or bid=='water_bucket' else 16 if bid.endswith('_sign') else 64
    write_csv(ROOT/'materialbedarf.csv',['Material','Anzahl','Stackgroesse','volle_Stacks','Rest','volle_Shulkers','Rest_nach_Shulkern'],
        [[bid,n,stack(bid),n//stack(bid),n%stack(bid),n//(27*stack(bid)),n%(27*stack(bid))] for bid,n in counts.most_common()])
    write_csv(ROOT/'materialbedarf_baugruppen.csv',['Baugruppe','Material','Anzahl'],
        [[g,bid,n] for g in groups for bid,n in group_materials[g].most_common()])
    # The material table tracks water positions separately from inventory items.
    d['meta']['water_positions']=sum(1 for bid,_,g in blocks.values() if bid=='water')
    d['meta']['material_note']='Wasserpositionen stehen nur in der Blockliste, nicht in den Itemmengen. Türen und Betten zählen je einmal.'
    for name in ['lager_kategorien.csv','villager_staende.csv','untergrund_pruefstellen.csv']:
        shutil.copyfile(source/name,ROOT/name)

    # Read real blocks, not a solid heightmap approximation, in existing planned cut columns.
    region=Region(source.parent/'mca.zip')
    t=d['terrain']; x0,x1,z0,z1=t['bounds']
    new_excavate=[]; excavation_rows=[]; removals=Counter(); height_mismatches=[]; cut_total=0
    for x,z,cut,old_count,near in t['excavate']:
        high=t['heights'][z-z0][x-x0]
        column=Counter()
        for y in range(cut,high+1):
            bid=region.block(x,y,z)
            if bid not in AIR:
                column[bid]+=1;excavation_rows.append([x,y,z,'minecraft:'+bid,near]);removals[bid]+=1
        count=sum(column.values());cut_total+=count
        new_excavate.append([x,z,cut,count,near])
    # Check all surveyed surface cells against the supplied region snapshot.
    for z in range(z0,z1+1):
        for x in range(x0,x1+1):
            y=t['heights'][z-z0][x-x0]; actual=region.block(x,y,z)
            if actual!=t['surface_blocks'][z-z0][x-x0]:height_mismatches.append([x,y,z,actual,t['surface_blocks'][z-z0][x-x0]])
    t.update(excavate=new_excavate,excavate_total=cut_total,excavate_columns=len(new_excavate))
    write_csv(ROOT/'aushub.csv',['X','Z','Unterkante_Y','Bloecke_im_Regionsnapshot','Bereiche'],new_excavate)
    write_csv(ROOT/'aushub_blockliste.csv',['X','Y','Z','Ist-Block','Bereiche'],excavation_rows)
    write_csv(ROOT/'aushub_materialien.csv',['Ist-Material','Bloecke'],removals.most_common())
    write_csv(ROOT/'gelaende_oberflaeche.csv',['X','Y','Z','Ist-Block'],
        [[x,t['heights'][z-z0][x-x0],z,t['surface_blocks'][z-z0][x-x0]] for z in range(z0,z1+1) for x in range(x0,x1+1)])
    # Produce an offline SVG cross-section from region blocks, replacing the missing PNG.
    palette={'air':'#101e30','cave_air':'#101e30','grass_block':'#668f50','dirt':'#92714f','stone':'#7e8788',
             'deepslate':'#4e5460','water':'#4283ae','gravel':'#9d9993'}
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 300" role="img"><title>Originalregion: Boden und Höhlen entlang Z=790</title><rect width="640" height="300" fill="#101e30"/>']
    for x in range(x0,x1+1):
        for y in range(65,133):
            bid=region.block(x,y,790)
            if bid not in AIR:svg.append(f'<rect x="{35+(x-x0)*4}" y="{18+(132-y)*3.5}" width="4" height="3.5" fill="{palette.get(bid,"#747a78")}"/>')
    for y in (70,90,105,113,121,129):
        sy=18+(132-y)*3.5
        svg.append(f'<path d="M35 {sy}H627" stroke="#fff" opacity=".16"/><text x="2" y="{sy+3}" fill="#d8e1dc" font-size="9">Y {y}</text>')
    for x in (-760,-730,-700,-670,-640,-620):svg.append(f'<text x="{35+(x-x0)*4}" y="280" fill="#d8e1dc" font-size="10">{x}</text>')
    svg.append('<text x="35" y="297" fill="#d8e1dc" font-size="10">Westen ← X → Osten · Blau: Luft / Höhlen · Region-Snapshot, vor dem Aushub</text></svg>')
    (ROOT/'assets/untergrund_schnitt_z790.svg').write_text(''.join(svg))

    report={'version':'5.7','base':'5.6','blocks':len(blocks),'unique':len(blocks),'fingerprint':fingerprint,
        'changed_coordinates':len(changes),'surface_columns_checked':(x1-x0+1)*(z1-z0+1),
        'surface_mismatches':height_mismatches,'excavation_columns':len(new_excavate),'excavation_nonair_blocks':cut_total,
        'roof_enclosed_tile_positions':roof_core,'bulk_filters':6,'golem_categories':9,'trading_stalls':10,
        'light_simulation_current':False,'walkability_simulation_current':False,'not_tested_in_game':True,
        'excavation_scope':'Actual non-air blocks within inherited planned column cuts, through surveyed ground height. Vegetation above ground excluded. Not an independently validated clearance volume.'}
    (ROOT/'check_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    d['validation']=report
    d['checks'].update(excavation=cut_total,doors=sum(1 for bid,st,g in blocks.values() if bid.endswith('_door') and 'half=lower' in st))
    # Preserve original room catalogue, but remove old reachability figures from the UI.
    d['storage_zones']=[
        {'id':'L01','name':'Bulkfilter & Massenlager','contents':'Bruchstein, Erde, Eisen, Tiefenschiefer, Stein, Kies','room':'Keller 1 · Nord','group':'bulk_lager','x':[-706,-675],'y':[121,127],'z':[767,787]},
        {'id':'L02','name':'Kupfergolem-Lager','contents':'Neun Kategorien · Startitems und Wege im Spiel prüfen','room':'Keller 1 · Südost','group':'golem_lager','x':[-694,-671],'y':[121,128],'z':[795,812]},
        {'id':'L03','name':'Überlauf & Shulker','contents':'Fässer als manuell verwaltete Reserve','room':'Keller 2 · Nordost','group':'bulk_lager','x':[-682,-672],'y':[113,120],'z':[768,784]}]
    d['storage_system']['mechanics']['notes']=[n for n in d['storage_system']['mechanics']['notes'] if 'öffentliches Fass' not in n]
    d['storage_system']['mechanics']['notes'].append('Förderwege sind geometrisch ergänzt; Sortierschaltung, Taktung und Golemwege im Spiel prüfen.')
    for room in d['rooms']:
        room['text']=room['text'].replace('gewerbliche Beleuchtung','geplante Beleuchtung')

    # Unbundle the inherited HTML, patching its source explicitly and reproducibly.
    html=re.sub(DATA_RE,'__BLUEPRINT_DATA__',original,flags=re.S)
    scripts=re.findall(r'<script>(.*?)</script>',html,re.S)
    app=scripts[0]
    app=app[:app.index('function toGeom(B)')] + (HERE/'viewer.js').read_text() + '\n' + app[app.index('function hover(e)'):]
    app=replace(app,"const PROG = LS.get('bt-prog', {}), WHO = LS.get('bt-who', {});","const PROG = BT.state.groups, WHO = BT.state.people;")
    app=replace(app,"LS.set('bt-prog', PROG)",'BT.save()')
    app=replace(app,"LS.set('bt-who', WHO)",'BT.save()')
    a=app.index("$('#dlProg').onclick");b=app.index('renderBuild();',app.index("$('#impProg').onchange",a))
    # Remove both legacy backup handlers together, not the first nested renderBuild call only.
    end=app.index('\nrenderBuild();',b)
    app=app[:a]+"window.addEventListener('bt:import',renderBuild);\n"+app[end:]
    app=replace(app,"${(WHO[g] || '').replace(/\"/g, '&quot;')}","${BT.escape(WHO[g] || '')}")
    app=replace(app,"const STACK1 = new Set(['water_bucket']); const stackOf = id => (STACK1.has(id) || id.endsWith('_bed')) ? 1 : 64;",
        "const STACK1 = new Set(['water_bucket']); const stackOf = id => (STACK1.has(id) || id.endsWith('_bed')) ? 1 : id.endsWith('_sign') ? 16 : 64;")
    app=replace(app,"if (!a.every(v => c.includes(v))) continue;","if (a.length !== 3 || !a.every((v,k) => c[k] === v)) continue;")
    a=app.index("$('#dlLayer').onclick");b=app.index('\n',a)
    app=app[:a]+'''$('#dlLayer').onclick = () => {
      const source = PL.mode === 'y' ? byY : PL.mode === 'x' ? byX : byZ;
      const rows=['Nummer;X;Y;Z;Block;Zustand;Bauteil'];
      for(const i of source[PL.val] || []) {const r=REG[R[i]];if(PL.group!=='all'&&r.g!==PL.group)continue;
        rows.push(`${i+1};${X[i]};${Y[i]};${Z[i]};minecraft:${r.id};${r.props};${r.g}`);}
      download(`blackthorn-schnitt-${PL.mode}${PL.val}.csv`,rows.join('\\n'));
    };''' + app[b:]
    app=replace(app,"title=\"Begehbare Bodenzellen, die vom Eingang aus zu Fuß erreichbar sind\"","hidden")
    app=replace(app,"`Begehbarkeit: ${pct} % (${fmt(r.reach)} von ${fmt(r.stand)} Bodenzellen)`","'Begehbarkeit nach dem Umbau noch nicht simuliert'")
    app=replace(app,"observatorium: 'Observatorium', beleuchtung: 'Zusatzbeleuchtung'", "observatorium: 'Observatorium', beleuchtung: 'Zusatzbeleuchtung', hang_stuetzen:'Hangstützen', eingang_vorplatz:'Eingang & Vorplatz', sortierung:'Einwurfstation', bulk_lager:'Bulk-Lager', golem_lager:'Kupfergolem-Lager', trading_hall:'Trading Hall', geheimraum:'Geheimräume', geheimgang:'Geheimgänge', lager_technik:'Lagertechnik'")
    app=replace(app,"groups: ['fundament']","groups: ['fundament','hang_stuetzen','eingang_vorplatz']")
    app=replace(app,"groups: ['keller_3', 'keller_2', 'keller_1', 'keller_treppe']","groups: ['keller_3', 'keller_2', 'keller_1', 'keller_treppe','sortierung','bulk_lager','golem_lager','trading_hall','geheimraum','geheimgang','lager_technik']")
    app=replace(app,'verhindert Monster-Spawns in Dachböden und Ecken.','Lichtwirkung im aktuellen Modell noch im Spiel prüfen.')
    app=replace(app,"const roof = g.startsWith('dach_') || g === 'observatorium', cellar = g.startsWith('keller'), light = g === 'beleuchtung';",
        "const roof = g.startsWith('dach_') || g === 'observatorium', cellar = g.startsWith('keller') || ['sortierung','bulk_lager','golem_lager','trading_hall','geheimraum','geheimgang','lager_technik'].includes(g), light = g === 'beleuchtung';")
    app=replace(app,"if (!GL || !GL.terrain) return setTimeout(wait, 80);","if (!GL) return; if (!GL.terrain) return setTimeout(wait, 80);")
    app=replace(app,"${d.title} · ${X[j]}, ${Y[j]}, ${Z[j]}","#${j+1} · ${d.id}${REG[R[j]].props ? ' ['+REG[R[j]].props+']' : ''} · X ${X[j]} / Y ${Y[j]} / Z ${Z[j]}")
    app=replace(app,'<span>Position</span><b>${d.pos}</b>','<span>Blocknummer</span><b>#${j+1}</b><span>Blockstate</span><code>${REG[R[j]].props || "Standard"}</code><span>Position</span><b>${d.pos}</b>')
    a=app.index("  const hist = C.light_hist");b=app.index("  $('#facts').innerHTML",a)
    app=app[:a]+'''  $('#checks').innerHTML = `
      <div class="chk-item ok"><b>Modell und Listen</b><p>${fmt(N)} eindeutige Positionen. CSV, Material je Baugruppe, Türhälften und Förderwege werden mit dem Prüfskript abgeglichen.</p></div>
      <div class="chk-item ok"><b>Originalgelände</b><p>${fmt(D.validation.surface_columns_checked)} Bodensäulen mit der Minecraft-Region abgeglichen; ${fmt(D.validation.surface_mismatches.length)} Abweichungen.</p></div>
      <div class="chk-item"><b>Aushub im Region-Snapshot</b><p>${fmt(D.terrain.excavate_total)} vorhandene Blöcke in ${fmt(D.terrain.excavate_columns)} geplanten Spalten. Höhlenluft ist abgezogen. Die übernommenen Aushubgrenzen sind noch keine vollständig geprüfte Baugrube.</p></div>
      <div class="chk-item warn"><b>Noch im Spiel zu prüfen</b><p>Licht, Begehbarkeit, Dachanschlüsse und die Sortierschaltung sind nach den Umbauten nicht im Spiel validiert. Alte Simulationswerte werden deshalb nicht als aktuelles Ergebnis angezeigt.</p></div>`;
''' + app[b:]
    app=replace(app,'Halle Y 162 · Residenzen Y 155 · Ostflügel Y 149','Dachgruppen: Halle bis Y 155 · Residenzen bis Y 155 · Ostflügel bis Y 141')
    # Standard 3D context resize observes its own canvas; render on demand.
    (ROOT/'app.js').write_text(app)
    extras=scripts[1:]
    steps=extras[0]
    steps=re.sub(r'const zones=\[.*?\];','const zones=d.storage_zones;',steps,flags=re.S)
    steps=replace(steps,"const inv=saved('bt-r5-1-storage',{}), done=saved('bt-r5-1-blocks',{});","const inv=BT.state.inventory, done=BT.state.blocks;")
    steps=replace(steps,"store('bt-r5-1-storage',inv)",'BT.save()')
    steps=replace(steps,"store('bt-r5-1-blocks',done)",'BT.save()')
    steps=replace(steps,"{n:++n,x:x+k,y,z,ri}","{n:++n,key:`${x+k},${y},${z}`,x:x+k,y,z,ri}")
    steps=replace(steps,'done[b.n]','done[b.key]')
    steps=replace(steps,'data-done="${b.n}"','data-done="${b.key}"')
    steps=replace(steps,'Nummern gehören zur originalen Blockfolge','Status wird nach XYZ gespeichert, Nummern gelten für Revision 5.7')
    steps += "\nwindow.addEventListener('bt:import',()=>{renderStep();renderStorage();});\n"
    # Listener must live inside the IIFE so its render functions remain in scope.
    steps=steps.replace("})();\n\nwindow.addEventListener('bt:import',()=>{renderStep();renderStorage();});", "window.addEventListener('bt:import',()=>{renderStep();renderStorage();});\n})();")
    (ROOT/'steps.js').write_text(steps)
    (ROOT/'terrain.js').write_text(extras[1])
    (ROOT/'system.js').write_text(extras[2])
    shutil.copyfile(HERE/'progress.js',ROOT/'progress.js')
    # CSS and application code are local, and JSON remains inline for file:// support.
    styles=re.findall(r'<style>(.*?)</style>',html,re.S)
    (ROOT/'styles.css').write_text('\n'.join(styles)+'''
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid var(--accent2);outline-offset:3px}
.backup-status{font-size:13px;color:var(--muted);margin:10px 0}.backup-status.error{color:var(--warn);font-weight:600}
.notice{border-left:4px solid var(--accent2);padding:12px 16px;background:var(--panel);border-radius:8px;margin-bottom:18px}
@media(max-width:650px){main{padding:14px 10px 40px}.top{position:relative;padding:10px}#tabs{width:100%;flex-wrap:nowrap;overflow-x:auto;padding-bottom:6px}#tabs button{white-space:nowrap}.stats{grid-template-columns:repeat(2,minmax(0,1fr))!important}.rooms,.groups{grid-template-columns:minmax(0,1fr)}.toolbar input[type=search]{min-width:0!important;max-width:100%}.stage{min-height:300px}.tag{white-space:normal}.sys-mat-row{flex-wrap:wrap}.tw{max-width:100%;overflow:auto}}
''')
    html=re.sub(r'<style>.*?</style>','',html,flags=re.S)
    html=html.replace('</head>','<link rel="stylesheet" href="styles.css">\n</head>')
    html=re.sub(r'<script(?: src="[^"]+")?>.*?</script>','',html,flags=re.S)
    html=html.replace('Revision 5.6','Revision 5.7')
    html=replace(html,'Das Herrenhaus über der Klippe – Dachlandschaft überarbeitet','Blackthorn Estate · gemeinsam Schicht für Schicht')
    html=re.sub(r'<p class="muted">Die Revision 5.7 konzentriert.*?</p>', '<p class="muted">Sechs Residenzen, drei Keller und der Blick über die Klippe. Revision 5.7 verbindet den Bauatlas mit korrigierten Förderwegen, geprüften Listen und einem vollständigen Fortschritts-Backup. Alle Ansichten funktionieren ohne Internet.</p>',html,count=1,flags=re.S)
    html=replace(html,'Prüfbericht (Originalmodell vor Fassadenzusätzen)','Prüfstand · Revision 5.7')
    html=replace(html,'<div class="facts" id="facts"></div>','<div class="notice"><b>Revision 5.7</b> · Modell und Listen automatisch geprüft · Technik und Begehbarkeit noch im Spiel prüfen. <a href="analysebericht.md">Änderungen &amp; Prüfgrenzen</a></div><div class="facts" id="facts"></div>')
    html=replace(html,'<div class="card"><b id="progTxt">','<p id="backupStatus" class="backup-status" role="status" aria-live="polite"></p><div class="card"><b id="progTxt">')
    html=replace(html,'Fortschritt exportieren','Vollständiges Backup')
    html=replace(html,'Importieren<input type="file"','Backup laden<input type="file"')
    html=replace(html,'Wird nur in diesem Browser gespeichert (Export/Import zum Teilen).','Speichert Baugruppen, Zuständigkeiten, einzelne Blöcke und Lagerbestand lokal. Ein Backup lädt einen vollständigen Stand und ersetzt den lokalen Stand nach Bestätigung. Keine Live-Synchronisation zwischen Spielern.')
    html=replace(html,'Alle Blockpositionen stammen aus dem originalen Revision-5-Blueprint. Eine Nummer beschreibt die Position in der entpackten Blockfolge; sie ist nicht mit älteren V8/V9-Nummern kompatibel. Benutze die Höhe und die Koordinaten zur Orientierung.','Blocknummern gelten für Revision 5.7. Häkchen werden anhand der Weltkoordinaten gespeichert. Das vollständige Backup unter „Bauplan“ enthält auch diesen Blockstatus; ältere nummernbasierte Stände werden nicht automatisch übernommen.')
    html=replace(html,'assets/untergrund_schnitt_z790.png','assets/untergrund_schnitt_z790.svg')
    html=replace(html,'2,988',f'{len(new_excavate):,}'.replace(',','.'))
    html=replace(html,'50,931',f'{cut_total:,}'.replace(',','.'))
    html=replace(html,'geschätzte Erdblöcke','vorhandene Blöcke im Snapshot')
    html=replace(html,'Y=104…127',f'Y={min(r[2] for r in new_excavate)}…{max(r[2] for r in new_excavate)}')
    html=replace(html,'Diese Ansicht markiert nur die Spalten, in denen für Keller, Fundamente, Vorplatz oder Pool tatsächlich Erdreich entfernt werden muss. Sie ersetzt die bisherigen großen Leerflächen durch einen echten Erdarbeitsplan.','Diese Ansicht übernimmt die geplanten Aushubspalten der Revision 5.6. Die Mengen wurden jetzt aus den echten Regionsblöcken gezählt: Luft wird nicht mitgezählt. Die Grenzen der Baugrube müssen vor Ort geprüft werden; Pflanzen oberhalb des Bodens sind nicht enthalten.')
    html=replace(html,'Die Detaildaten stehen auch als CSV bereit.','Spalten, Einzelpositionen und vorhandene Materialien stehen als CSV bereit. Die Menge beschreibt das Freiräumen bis zur Unterkante einschließlich vorhandener Blöcke an späteren Baupositionen; wiederverwendbare Blöcke werden nicht abgezogen.')
    html=replace(html,'Aushub als CSV</a>','Aushub als CSV</a><a class="btn" href="aushub_blockliste.csv" download>Einzelblöcke</a><a class="btn" href="aushub_materialien.csv" download>Aushub-Materialien</a>')
    html=replace(html,'Wasser als ein Eimer.',f'Wasser ist mit {d["meta"]["water_positions"]} Positionen nur in der Blockliste enthalten, nicht in diesen Itemmengen.')
    html=replace(html,'Stacks (64er)','benötigte Stackplätze')
    html=replace(html,'Vorschlag für das praktische Sortiersystem','Geometrie ergänzt · Inbetriebnahme offen')
    html=replace(html,'<nav id="tabs">','<nav id="tabs" aria-label="Bauatlas-Ansichten">')
    for id,label in [('cut','3D-Schnitthöhe'),('planRange','Position der Schnittebene'),('planMode','Schnittrichtung'),
                     ('planGroup','Baugruppe im Plan'),('matG','Material nach Baugruppe'),('matQ','Material suchen'),
                     ('roomQ','Räume suchen'),('stepHeight','Bauhöhe'),('stepSearch','Blöcke auf dieser Höhe suchen')]:
        html=replace(html,f'id="{id}"',f'id="{id}" aria-label="{label}"')
    html=replace(html,'id="themeBtn" title="Hell/Dunkel"','id="themeBtn" title="Hell/Dunkel" aria-label="Helles oder dunkles Design umschalten"')
    html=html.replace('__BLUEPRINT_DATA__','<script type="application/json" id="data">'+json.dumps(d,ensure_ascii=False,separators=(',',':'))+'</script>\n'+
        '\n'.join(f'<script src="{name}.js"></script>' for name in ['progress','app','steps','terrain','system']))
    (ROOT/'index.html').write_text(html)
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
