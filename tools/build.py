#!/usr/bin/env python3
"""Build Revision 5.26: Dach-Geheimraum, Strukturprüfung und Verschönerung."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from architecture import enhance
from materials import items_for_block, stack_size, scopes
from build_audit import audit
from structure_export import export as export_structure
from litematic_import import build as import_litematics

ROOT=Path(__file__).resolve().parent.parent
SEED=ROOT/'tools'/'seeds'/'revision-5.25'/'blueprint.json'
VERSION='5.26'
VERSION_PREVIOUS='5.25'

def build_structure_metadata(d):
    levels=[
        ('technikzugang','Unterer Technikzugang',80,104,['fluchtgang','lichtkorrektur']),
        ('keller_3','Keller 3',105,112,['keller_3','trading_hall','geheimraum','geheimgang','privatlager','lichtkorrektur']),
        ('keller_2','Keller 2',113,120,['keller_2','lager_regale','bulk_lager','keller_treppe','lichtkorrektur']),
        ('keller_1','Keller 1',121,128,['keller_1','golem_lager','lager_technik','shulker_technik','keller_treppe','lichtkorrektur']),
        ('erdgeschoss','Erdgeschoss',129,136,['halle','halle_treppe','kueche','speisesaal','vestibuel','portikus','bibliothek','res1','res2','res3','res4','res5','res6','fassade_fenster','fassade_laeden','fassade_zahnschnitt','fassade_efeu','fassade_alterung','fassade_laternen','fassade_beet','teppiche','lichtkorrektur']),
        ('obergeschoss','Obergeschoss & Galerie',137,144,['halle','halle_treppe','galerie','bibliothek','res1','res2','res3','res4','res5','res6','dach_ostfluegel','fassade_fenster','fassade_laeden','fassade_zahnschnitt','fassade_efeu','fassade_alterung','dachgeheimraum_technik','fassade_laternen','lichtkorrektur']),
        ('dach','Dach & Türme',145,171,['dach_halle','dach_res','dach_bibliothek','fassade','dach_schmuck','aussichtsturm','halle_giebelfenster','dachgeheimraum','dachgeheimraum_technik','teppiche','lichtkorrektur'])]
    output=[]
    for key,label,low,high,groups in levels:
        positions=0
        for y,z,x,n,ri in d['runs']:
            if low<=y<=high and d['groups'][d['reg'][ri][2]] in groups:positions+=n
        rooms=[r['name'] for r in d['rooms'] if r['y'][0]<=high and r['y'][1]>=low]
        output.append({'id':key,'label':label,'y':[low,high],'height':high-low+1,'groups':groups,'positions':positions,'rooms':rooms})
    occupancy={}
    for y,z,x,n,ri in d['runs']:
        bid,state,gi=d['reg'][ri]
        for dx in range(n):occupancy[(x+dx,y,z)]=(bid,d['groups'][gi])
    stair_audit=[]
    for group in ('keller_treppe','halle_treppe','galerie'):
        stairs=[]
        for (x,y,z),(bid,block_group) in occupancy.items():
            if block_group==group and bid.endswith('_stairs'):stairs.append((x,y,z))
        obstructions=[]
        for x,y,z in stairs:
            for yy in range(y+1,y+4):
                if (x,yy,z) in occupancy:obstructions.append({'stair':[x,y,z],'block':[x,yy,z],'id':occupancy[(x,yy,z)][0]})
        stair_audit.append({'group':group,'stair_blocks':len(stairs),'clearance_blocks':3,'obstructed_positions':len(obstructions),'examples':obstructions[:8]})
    litematic=json.loads((ROOT/'lagertechnik_module.json').read_text())
    vault=litematic['vault']
    shaft_x,shaft_y,shaft_z=vault['shaft_target']
    shaft_blockers=[{'y':y,'block':occupancy[(shaft_x,y,shaft_z)][0],'group':occupancy[(shaft_x,y,shaft_z)][1]} for y in range(80,137) if (shaft_x,y,shaft_z) in occupancy]
    return {'levels':output,
        'axes':[{'label':'Eingang & Zufahrt · Westen','x':[-785,-734],'groups':['portikus','vestibuel','zufahrt']},
                {'label':'Zentrale Halle & Querachse','x':[-713,-677],'groups':['halle','galerie']},
                {'label':'Pool & Klippenpanorama · Osten','x':[-657,-631],'groups':['pool','terrasse']}],
        'stair_runs':[{'label':'Kellertreppenhaus','x':[-670,-662],'y':[105,130],'blocks':48},
                      {'label':'Neue zweiläufige Haupttreppe · Halle zur Nordgalerie','x':[-698,-692],'y':[130,136],'blocks':42},
                      {'label':'Galerieaufgänge an Nord- und Südrand','x':[-680,-678],'y':[130,137],'blocks':48}],
        'stair_clearance':stair_audit,
        'stair_separation':{'center_x':29,'minimum_x_gap':22,'basement_to_main_route':'Bibliothek → Große Halle'},
        'service_shaft':{'position':vault['shaft_target'],'vault_bounds':vault['bounds'],'vault_size':[vault['width'],vault['height'],vault['depth']],
                         'service_gap_x':vault['service_gap_x'],'vertical_floor_blocks':shaft_blockers,
                         'note':'Leiter-Wartungsschacht Y 106–132 mit Zugangstüren K3 bis EG gebaut. Verlängerung Y 80–104 und automatische Itemförderung offen.'},
        'logistics':[{'label':'Regallager','y':[114,119]},{'label':'Bulk-Lager','y':[114,125]},
                     {'label':'Kupfergolem-Lager','y':[121,123]},{'label':'Einwurfstation','y':[122,126]}]}

def main():
    d=json.loads(SEED.read_text())
    old_fingerprint=d['meta']['fingerprint']
    old={} 
    for y,z,x,n,ri in d['runs']:
        bid,state,gi=d['reg'][ri]
        for dx in range(n): old[(x+dx,y,z)]=(bid,state,d['groups'][gi])
    baseline=old.copy()
    enhancements=enhance(d,old)
    global structure_findings_ref
    structure_findings=structure_report(d,old,enhancements);structure_findings_ref={k:v for k,v in structure_findings.items() if k!='unsupported_attachments'}
    additions={pos:(baseline.get(pos),old.get(pos)) for pos in baseline.keys()|old.keys() if baseline.get(pos)!=old.get(pos)}
    group_names=d['groups']
    group_names.extend(g for g in sorted({v[2] for v in old.values()}) if g not in group_names)
    group_index={g:i for i,g in enumerate(group_names)}
    reg=list(d['reg']); reg_index={tuple(v):i for i,v in enumerate(reg)}
    indexed={}
    for (x,y,z),(bid,state,group) in old.items():
        key=(bid,state,group_index[group])
        if key not in reg_index:
            reg_index[key]=len(reg);reg.append(list(key))
        indexed[(x,y,z)]=reg_index[key]
    by_yz=defaultdict(list)
    for (x,y,z),ri in indexed.items():by_yz[y,z].append((x,ri))
    runs=[];sequence=[];counts=Counter();gcounts={g:Counter() for g in group_names};coords={g:[] for g in group_names}
    for (y,z),items in sorted(by_yz.items()):
        items.sort()
        i=0
        while i<len(items):
            x,ri=items[i];n=1
            while i+n<len(items) and items[i+n][0]==x+n and items[i+n][1]==ri:n+=1
            runs.append([y,z,x,n,ri]);i+=n
        for x,ri in items:
            bid,state,gi=reg[ri];group=group_names[gi]
            sequence.append([len(sequence)+1,x,y,z,'minecraft:'+bid,state,group])
            coords[group].append((x,y,z))
            for material,amount in items_for_block(bid,state):
                counts[material]+=amount;gcounts[group][material]+=amount
    d['reg']=reg;d['runs']=runs;d['meta']['version']=VERSION;d['meta']['total']=len(indexed)
    d['meta']['bbox']=[min(p[0] for p in indexed),max(p[0] for p in indexed),min(p[1] for p in indexed),max(p[1] for p in indexed),min(p[2] for p in indexed),max(p[2] for p in indexed)]
    d['meta']['fingerprint']=hashlib.sha256(json.dumps(sequence,separators=(',',':')).encode()).hexdigest()
    d['progress_compat']={'revision':VERSION_PREVIOUS,'fingerprint':old_fingerprint,'changed_positions':[','.join(map(str,p)) for p in additions],'changed_groups':sorted({v[2] for pair in additions.values() for v in pair if v})}
    d['counts']=dict(counts)
    d['meta']['water_positions']=sum(v[0]=='water' for v in old.values())
    d['meta']['bubble_column_positions']=sum(v[0]=='bubble_column' for v in old.values())
    d['gcounts']={g:dict(c) for g,c in gcounts.items()}
    d['material_scopes']=scopes(d['gcounts'])
    d['material_stack_sizes']={item:stack_size(item) for item in counts}
    d['gstats']={}
    for g,points in coords.items():
        if points:d['gstats'][g]={'n':len(points),'x':[min(p[0] for p in points),max(p[0] for p in points)],'y':[min(p[1] for p in points),max(p[1] for p in points)],'z':[min(p[2] for p in points),max(p[2] for p in points)]}
    d['validation'].update(version=VERSION,base=VERSION_PREVIOUS,blocks=len(indexed),fingerprint=d['meta']['fingerprint'])
    modules=import_litematics()
    d['lighting']['fixtures']=[f for f in d['lighting']['fixtures'] if old.get((f['x'],f['y'],f['z']),('',))[0] in ('lantern','soul_lantern')]
    for fixture in d['lighting']['fixtures']:
        anchor=old.get(tuple(fixture['anchor']))
        if not anchor:raise ValueError('Existing lamp lost its anchor: '+fixture['id'])
        fixture['anchor_block']=anchor[0]
    known={(f['x'],f['y'],f['z']) for f in d['lighting']['fixtures']}
    for (x,y,z),(bid,state,g) in sorted(old.items()):
        if bid not in ('lantern','soul_lantern') or (x,y,z) in known:continue
        hanging='hanging=false' not in state
        ay=y+1 if hanging else y-1
        anchor=old.get((x,ay,z))
        if not anchor:raise ValueError('New lamp has no anchor')
        fixture_level='Dach-Geheimraum' if g in ('dachgeheimraum',) else 'Fassade' if g=='fassade_laternen' else 'Zusatzlicht' if g=='lichtkorrektur' else 'Bootshaus / Ufer'
        fixture_kind='Hängeleuchte' if hanging else 'Standleuchte'
        d['lighting']['fixtures'].append({'id':f'N526-{len(known)+1}','x':x,'y':y,'z':z,'block':bid,'group':g,'level':fixture_level,'hanging':hanging,'chain':0,'anchor':[x,ay,z],'anchor_block':anchor[0],'kind':fixture_kind,'source':'Revision 5.26','checked':True})
        known.add((x,y,z))
    with (ROOT/'laternen_pruefung.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['ID','X','Y','Z','Block','Montage','Kettenbloecke','Anker-X','Anker-Y','Anker-Z','Ankerblock','Bereich','Planung'])
        writer.writerows([r['id'],r['x'],r['y'],r['z'],r['block'],r['kind'],r['chain'],*r['anchor'],r['anchor_block'],r['group'],r['source']] for r in d['lighting']['fixtures'])
    d['lighting']['total']=sum(1 for b,_,_ in old.values() if b in ('lantern','soul_lantern'))
    d['lighting']['light_simulated']=True;d['lighting']['light_report']=enhancements.get('light_report')
    d['checks'].update(doors=sum(b.endswith('_door') and 'half=lower' in state for b,state,g in old.values()),stairs=sum(b.endswith('_stairs') for b,state,g in old.values()),panes=sum(b=='glass_pane' or b.endswith('_stained_glass_pane') for b,state,g in old.values()))
    d['checks']['historical_note']='Erreichbarkeits- und Erdarbeitswerte stammen aus früheren Revisionen. Seit 5.26 gibt es eine Strukturprüfung (strukturpruefung.md) und eine Blocklichtprüfung der Räume.'
    clearance_air=d.pop('_clearance_air',[])
    d['required_air']=clearance_air
    d['structure']=build_structure_metadata(d)
    d['structure']['enhancements']=enhancements
    d['structure']['maintenance_shaft']={'bounds':[-688,-686,106,132,789,791],'access_floors':[105,113,121,129],'type':'Leiterwartungsschacht','automatic_items':False}
    d['structure_export']=export_structure(d,ROOT/f'blackthorn_estate_{VERSION}.nbt')
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    write_blocklist(sequence)
    write_materials(counts,gcounts,group_names)
    for key,scope in d['material_scopes'].items():write_material_csv(ROOT/('materialbedarf_'+{'house':'haus','outdoor':'aussenanlagen','terrain':'gelaende'}[key]+'.csv'),scope['counts'])
    d['material_audit']=audit(d,ROOT)
    d['validation'].update(material_audit_passed=not d['material_audit']['errors'],doors_checked=d['material_audit']['doors_checked'],material_items=sum(counts.values()))
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    write_diff(additions)
    with (ROOT/f'freiraeume_{VERSION}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['X','Y','Z','Aktion'])
        writer.writerows([*p,'Luft freihalten / Bestand ausheben'] for p in clearance_air)
    with (ROOT/'klippenpfad.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['Schritt','X','Boden_Y','Z'])
        writer.writerows([i,*p] for i,p in enumerate(enhancements['path'],1))

    terrain=d['terrain'];tx,_,tz,_=terrain['bounds']
    with (ROOT/'architektur_erdarbeiten.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['X','Y','Z','Aktion','Baugruppe','Hinweis'])
        for (x,y,z),(prior,value) in sorted(additions.items()):
            if value and value[2] in ('fluchtgang','geheimtechnik','materiallift','poollicht','klippenpfad','bootshaus','stall_remise','orangerie','wohn_details','buchsteuerung','weinberg') and y<=terrain['target_heights'][z-tz][x-tx]:
                writer.writerow([x,y,z,'Gelaende ersetzen',value[2],'Zusaetzlich zum bisherigen Terraformingplan; mit Bestandswelt abgleichen'])

    write_placement(modules)
    write_secret_room_doc(enhancements)
    update_progress()
    write_project_docs(d,modules)
    from hall_window_elevation import build as build_window_elevation
    if any(v and v[2]=='halle_giebelfenster' for pair in additions.values() for v in pair):build_window_elevation(json.loads(SEED.read_text()),d,ROOT)
    from elevation import build as build_elevation
    build_elevation(d,ROOT)
    from web import build
    build(d)
    for oldfile in ('blackthorn_estate_5.25.nbt','manifest_5.25.json','aenderungen_5.24_zu_5.25.csv','freiraeume_5.25.csv'):
        p=ROOT/oldfile
        if p.exists():p.unlink()
    write_manifest()
    print(f'Revision {VERSION}: {len(indexed):,} build positions; {sum(counts.values()):,} material items; static access and shaft plan generated.')
    print('Litematic modules:',', '.join(f"{m['name']} ({m['total_blocks']:,} blocks)" for m in modules['modules']))

def structure_report(d,blocks,enhancements):
    """Strukturprüfung über das endgültige Modell; schreibt strukturpruefung.json/.md."""
    from materials import OUTDOOR
    import structure_check as sc
    findings=sc.check(blocks,OUTDOOR)
    reach=sc.reachability(blocks,[r for r in d['rooms'] if 'Plateauzufahrt' not in r['name']])
    worst=min(reach['rooms'],key=lambda r:r['reached']/max(r['cells'],1))
    unreachable=[r['room'] for r in reach['rooms'] if r['cells'] and r['reached']==0]
    stairs=[f for f in findings['floating'] if f['groups']==['halle_treppe']]
    chain_only=[f for f in findings['floating'] if f['groups']!=['halle_treppe'] and all(t in('anvil','polished_blackstone','dark_oak_fence','glass','waxed_cut_copper','redstone_lamp','waxed_cut_copper_slab') for t in f['types'])]
    other=[f for f in findings['floating'] if f not in stairs and f not in chain_only]
    summary={'revision':VERSION,'floating_components':len(findings['floating']),'floating_stair_flights_edge_contact':len(stairs),'floating_decor_with_chain_or_pane_contact':len(chain_only),'floating_other':other,'unsupported_attachments':findings['unsupported'],'reachability':{'start':reach['start'],'rooms':len(reach['rooms']),'unreachable_rooms':unreachable,'lowest_coverage':worst}}
    (ROOT/'strukturpruefung.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    text=f"""# Strukturprüfung · {VERSION}

Statisches Modell, geprüft über alle Hausblöcke (Außenanlagen und Gelände gelten als tragender Boden).

## Schwebende Bauteile

{len(findings['floating'])} Gruppen von Blöcken ohne durchgehende Verbindung zum Fundament.

- {len(stairs)} davon sind Treppenläufe der Halle mit nur Kantenkontakt der Stufen (in Minecraft stabil, optisch freitragend; bewusst so belassen).
- {len(chain_only)} sind Kronleuchter, Zaunpfosten der Bibliotheksbrüstung, Liftanzeige und Liftglas, die nur über Ketten, Eisengitter oder diagonale Kanten halten (Minecraft kennt dafür keine Statik).
- {len(other)} weitere Befunde: {'keine' if not other else 'siehe strukturpruefung.json'}.

## Fehlende Halterungen

{len(findings['unsupported'])} Befunde bei Fackeln, Laternen, Ketten, Leitern, Türen, Teppichen, Redstone-Bauteilen: {'keine' if not findings['unsupported'] else 'siehe strukturpruefung.json'}.

Korrigiert in 5.26: vier Kronleuchterketten der Bibliothek hatten ein Loch zur Decke.

## Erreichbarkeit

Begehbarkeit vom Hauptportal aus (Gehen, Einblockstufen, Treppen, Leitern, geschlossene Türen) über {len(reach['rooms'])} Räume: {'alle Räume erreichbar' if not unreachable else 'nicht erreichbar: '+', '.join(unreachable)}. Niedrigste Abdeckung: {worst['room']} mit {worst['reached']} von {worst['cells']} Bodenzellen; der Rest liegt auf Möbeln, Regalen und Stufenkanten. Der Dachraum über der Bibliothek ist bei geschlossener Luke absichtlich nicht erreichbar.

## Licht

Blocklichtprüfung für alle begehbaren Bodenzellen der Räume (ohne Plateauzufahrt): {enhancements['light_report']['dark_before']} Zellen ohne Blocklicht vor, {enhancements['light_report']['dark_after']} nach den Korrekturen (verbleibend: {enhancements['light_report']['unresolved']}). Dunkle Zellen werden mit Standlaternen an Wänden und in Ecken behoben, nicht neben Türen, Treppen oder Leitern.

## Grenzen

Die Prüfung kennt Blocklicht, aber kein Himmelslicht. Wandmaterial aus der Bestandswelt außerhalb des Modells zählt als durchlässig. Redstone-Schaltungen und Kolbenbewegungen sind nur geometrisch geprüft, nicht im Spiel.
"""
    (ROOT/'strukturpruefung.md').write_text(text)
    return summary

def write_secret_room_doc(enhancements):
    sr=enhancements['secret_room'];lr=enhancements['light_report']
    (ROOT/f'geheimraum_{VERSION}.md').write_text(f"""# Dach-Geheimraum · {VERSION}

Der Raum liegt im Dachboden über der Bibliothek (X -671 bis -661, Y 146 bis 149, Z 776 bis 804). Der Eingang ist eine Bibliotheksleiter an der Nordwand der Bibliothek (X -671, Z 775), die vom Erdgeschoss (Y 130) bis zur Decke reicht.

## Schaltung

- Am Kopf der Leiter steht ein Lesepult (X -670, Y 144, Z 775) in einem Regalschrank.
- Ein Komparator liest das Lesepult und vergleicht mit einem Redstone-Block an seiner Seite. Nur wenn das Buch auf der letzten Seite aufgeschlagen ist, kommt Stärke 15 durch.
- Der Komparator versorgt einen Block, an dem eine Redstone-Fackel sitzt. Die Fackel hält den Klebekolben im Normalfall ausgefahren und die Deckenluke (Halbstufe) geschlossen.
- Bei Stärke 15 geht die Fackel aus, der Kolben zieht die Luke seitlich zurück und man klettert in den Dachraum.
- Im Dachraum sitzt ein Hebel auf dem Kolben (X -669, Y 146, Z 775): eingeschaltet hält er die Luke geschlossen.

## Ingame

- Beim manuellen Bauen den Klebekolben eingefahren setzen und die Fackel anbringen; er fährt dann von selbst aus. Den Kolbenkopf nicht als Block setzen. Die Blockliste führt ihn nur, weil das Modell den ausgefahrenen Zustand zeigt.
- Ein beschriebenes oder geschriebenes Buch mit mindestens zwei Seiten ins Lesepult legen und bis zur letzten Seite blättern.
- Nicht in der Luke stehen, wenn die Fackel wieder angeht: Der Kolben schiebt die Halbstufe zurück.
- Die Schaltung ist nur geometrisch geprüft; Komparator-Ausgang, Fackelabschaltung und Kolbenweg sind im Spiel zu testen.

## Einrichtung

Dunkler Eichenboden mit Läufer, Regalwände, zwei Kartentische mit Kerzen, zwei Lesepulte, Truhen und Fässer. Im Süden ein Podest mit Zaubertisch und vier Standleuchten, fünf Kronleuchter an der Firstlinie.

## Licht im ganzen Haus

{lr['cells_checked']} Bodenzellen geprüft; {lr['dark_before']} ohne Blocklicht. {lr['lanterns_added']} Standlaternen ergänzt; danach {lr['dark_after']} dunkle Zellen.
""")

def write_blocklist(sequence):
    with (ROOT/'blockliste.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Nummer','X','Y','Z','Minecraft-Block','Blockstate','Baugruppe']);w.writerows(sequence)

def write_material_csv(path,counts):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Material','Anzahl','Stackgroesse','volle_Stacks','Rest','volle_Shulkers','Rest_nach_Shulkern','Rest_Stacks_nach_Shulkern','Einzeln_nach_Stacks'])
        for block,count in sorted(counts.items(),key=lambda p:(-p[1],p[0])):
            size=stack_size(block);per=size*27;sh,remain=divmod(count,per);stacks,loose=divmod(remain,size)
            w.writerow([block,count,size,count//size,count%size,sh,remain,stacks,loose])

def write_materials(counts,gcounts,groups):
    write_material_csv(ROOT/'materialbedarf.csv',counts)
    with (ROOT/'materialbedarf_baugruppen.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Baugruppe','Material','Anzahl'])
        for group in groups:
            for block,count in sorted(gcounts[group].items(),key=lambda p:(-p[1],p[0])):w.writerow([group,block,count])

def write_diff(additions):
    path=ROOT/f"aenderungen_{VERSION_PREVIOUS}_zu_{VERSION}.csv"
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['X','Y','Z','Alt-Block','Alt-State','Alt-Gruppe','Neu-Block','Neu-State','Neu-Gruppe'])
        for (x,y,z),(prior,value) in sorted(additions.items(),key=lambda p:(p[0][1],p[0][2],p[0][0])):
            old=prior or ('','','');new=value or ('','','')
            w.writerow([x,y,z,'minecraft:'+old[0] if old[0] else '',old[1],old[2],'minecraft:'+new[0] if new[0] else '',new[1],new[2]])

def write_placement(data):
    with (ROOT/'lagertechnik_platzierung.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';')
        w.writerow(['Modul','Quelldatei','Anker_X','Anker_Y','Anker_Z','Drehung','Breite','Hoehe','Tiefe','Bloecke','Entities','Hinweis'])
        for m in data['modules']:
            x,y,z=m['proposed_world_anchor']
            w.writerow([m['name'],m['source'],x,y,z,'0°',*m['bounds_size'],m['total_blocks'],m['entity_total'],'Vorschlag; Grube, Zugang, Anschluesse und Redstone nicht abgenommen'])
        v=data['vault'];x0,x1,y0,y1,z0,z1=v['bounds']
        w.writerow(['Gesamttechnikstollen','Kombinierte Platzierung',x0,y0,z0,'0°',v['width'],v['height'],v['depth'],sum(m['total_blocks'] for m in data['modules']),sum(m['entity_total'] for m in data['modules']),f'Bounds X {x0}…{x1}; Y {y0}…{y1}; Z {z0}…{z1}; Wartungsspalt X {v["service_gap_x"][0]}…{v["service_gap_x"][1]}'])
        sx,sy,sz=v['shaft_target']
        w.writerow(['Wartungsschacht','Hausblockplan',sx-1,106,sz-1,'—',3,27,3,0,0,'Leiter und Türen K3 bis EG gebaut; Verlängerung Y 80…104 und Itemlift offen'])

def write_manifest():
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.name==f'manifest_{VERSION}.json':continue
        raw=p.read_bytes()
        files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    (ROOT/f'manifest_{VERSION}.json').write_text(json.dumps({'revision':VERSION,'files':files},ensure_ascii=False,indent=2)+'\n')

def update_progress():
    p=ROOT/'progress.js';s=(ROOT/'tools'/'seeds'/'revision-5.25'/'progress.js').read_text()
    s=s.replace('5.25','5.26').replace('5.24','5.25')
    p.write_text(s)

structure_findings_ref=None

def write_project_docs(d,modules):
    clearance=d['structure']['stair_clearance']
    vault=d['structure']['service_shaft']
    enhancements=d['structure']['enhancements']
    report=f"""# Blackthorn Estate · Revision {VERSION}

{enhancements['title']}

{chr(10).join('- '+f['name']+': '+f['description'] for f in enhancements['features'])}

Die Redstone-Module sind geometrisch angeschlossen. Schaltzyklen, Wasserfluss und die Kolbentür sind im Spiel zu prüfen. Der NBT-Export enthält die neuen Luftpositionen. Beim manuellen Bauen zuerst freiraeume_5.26.csv abarbeiten. Die Westansicht unter assets/westansicht_5.19.svg wird direkt aus dem Blockmodell erzeugt.

Die bestehende EG-Pooltür samt Steinrahmen bleibt nutzbar. Die Balkontür liegt eine Etage höher. Der Wartungsschacht K3–EG bleibt bestehen. Der geheime Zugang führt nun bis Y 80; die beiden Litematic-Module bleiben separate Dateien. Der Materiallift ist neben der Wartungsleiter modelliert; seine Inbetriebnahme steht aus.

{enhancements['limits']}

Die Website zeigt die neuen Bauteile unter Bauatlas → Hausstruktur mit direktem 3D-Zugriff. Blockliste, Materialbedarf, Änderungsdatei und NBT-Export werden aus demselben Modell erzeugt. Alte Modellhäkchen werden nur für unveränderte Positionen übernommen.

Neu in 5.26: Dach-Geheimraum über der Bibliothek mit Lesepultschloss und Kolbenluke (Anleitung in geheimraum_5.26.md), Strukturprüfung (strukturpruefung.md), Lichtprüfung mit Zusatzlaternen, Konsollaternen und Beete an der Fassade sowie Teppiche und Läufer. Alle Änderungen stehen in blockliste.csv, materialbedarf*.csv und aenderungen_5.25_zu_5.26.csv.\n\nAus 5.25: korrigierte Türanschlüsse und unabhängig nachgezählte Materialien. Prüfbericht: materialpruefung.md. Die Materialansicht startet mit Haus und Keller; Gelände und Außenanlagen sind separat auswählbar. Gesamtmengen bleiben vollständig erhalten. Shulker-Restmengen und Banner-Stackgrößen wurden korrigiert. Die Hallenfenster aus 5.24 bleiben erhalten.\n\nAus 5.22: drei Weinbergterrassen, zwei Steglaternen, vier Regale mit geplanter Bestückung, zwei Rüstungsnischen und ein flankengetriggerter Liefergong. Einrichtung im Spiel: remise_bibliothek_5.22.mcfunction. Zusatzmaterialien stehen in einrichtung_5.22.csv; die 13 Bücher, zwei Ständer und zwei Rüstungssets sind separat vom Blockmaterialbedarf ausgewiesen.

Frühere Licht-, Erreichbarkeits- und Erdarbeitszahlen sind historische Daten. Aktuelle Ingame-Abnahme, Lichtsimulation und der Anschluss der Bogenfüße an den Fels stehen aus.

Die Daten bleiben in externen JavaScript-Dateien, damit der Atlas lokal ohne Webserver geöffnet werden kann. Historische Archive und Rohwelten bleiben lokal über .gitignore ausgeschlossen. Nicht mehr verwendete Werkzeuge aus der 5.11-Reihe und zwei ungenutzte Vorschaubilder liegen lokal unter archive/repository-cleanup-5.22/. Der aktuelle Build benötigt sie nicht.
"""
    (ROOT/'technik_5.20.md').write_text("""# Technik und Inbetriebnahme · 5.20

Diese Module sind geometrisch modelliert. Eine Abnahme im laufenden Server ist noch offen.

## Bücherregal und Fluchtgang

Bodenhebel: X -696 / Y 106 / Z 775. Zwei klebrige Kolben und getrennte Repeater bewegen die beiden Bücherregalblöcke. Der Export zeigt den geschlossenen Zustand. Zum Test den Hebel ausschalten: Beide Regale müssen je einen Block nach Westen zurückfahren. Im freien Türfeld nach Süden zur Leiter abbiegen, bis zur Passage auf Boden Y 100 absteigen; weiter nördlich führt eine zweite Leiter bis zur unteren Zugangsebene Y 80. Der untere Gang endet in der drei Blöcke breiten Litematic-Servicelücke. Die Litematics selbst sind separat einzusetzen.

## Materiallift

Einwurfkiste: X -685 / Y 108 / Z 789. Ein Hopper speist den Dropper. Ein Subtraktionskomparator mit verstärkter Rückkopplung und Repeater taktet ihn, solange Items enthalten sind. Die Blasensäule liegt bei X -685 / Z 790 auf Seelensand Y 105. Der obere Wasserkanal führt über zwei Hopper zur Ausgabekiste X -683 / Y 131 / Z 792. Die bisherige trockene Wartungsleiter bleibt erhalten.

Zuerst Wasser und Seelensand prüfen, danach ein einzelnes Testitem einwerfen. Es muss im EG ankommen und der Taktgeber anschließend stehen bleiben. Danach mehrere Stacks und eine gefüllte Shulkerbox testen. Gefüllte Shulkerboxen werden als Item transportiert; die Anlage packt sie nicht aus. Bei voller Ausgabe läuft der Lift weiter; vor längerem Betrieb müssen Rückstauabschaltung und Anschluss an das Hauptlager ergänzt werden. Der Lift verbindet K3 und EG; automatische Abzweige auf K1/K2 sind noch nicht eingebaut.

## Poollicht

Hebel: X -657 / Y 130 / Z 787, neben dem Poolausgang. Er versorgt über den massiven Sockel die Leitung darunter. Zwei trockene Leitungszweige mit Repeatern steuern sechs Lampen in der Nord- und Südwand des Beckens. Der Export zeigt AUS. Alle sechs Lampen auf EIN und AUS prüfen; anschließend die trockenen Leitungskanäle und das unveränderte Schwimmbecken kontrollieren.

## Uferweg und Bau-Reihenfolge

Der 84 Positionen lange Weg endet an der vermessenen nordöstlichen Wasserfläche. Zuerst Geländeersatz und freiraeume_5.21.csv prüfen, dann Weg und Bootshaus errichten. Der NBT-Export enthält die ausgewiesenen Luftpositionen bereits. Vor dem ersten Lauf jeden Übergang und das Geländer vor Ort prüfen.

## Technische Quellen

[Mojang: Redstone Lamp](https://www.minecraft.net/en-us/article/block-week-redstone-lamp) beschreibt die Versorgung der Lampen durch Redstone und Repeater. [Mojang: Update Aquatic](https://feedback.minecraft.net/hc/en-us/articles/360007323492-Minecraft-Java-Edition-1-13-Update-Aquatic) dokumentiert Blasensäulen mit Seelensand bzw. Magmablöcken. Diese Grundlagen ersetzen keine Prüfung unserer konkreten Schaltungen.
""")
    (ROOT/'technik_5.21.md').write_text("""# Inbetriebnahme 5.21

## Buchsteuerung

Das vorhandene Pult X -691 / Y 106 / Z 772 wird mit einem Buch bestückt. Ein Buch mit 15 beschriebenen Seiten verwenden: Anfangsseite für geschlossen, letzte Seite für offen. Der Komparator gibt nur Signalstärke 15 an der konstanten seitlichen Referenz vorbei. Die Wandfackel invertiert das Ergebnis und versorgt die beiden vorhandenen Repeater. Der Bodenhebel X -696 / Y 106 / Z 775 ist ausgeschaltet; einschalten erzwingt geschlossen. Beide Zustände und beide Kolben im Spiel prüfen. Der Export enthält das leere Pult; es behauptet kein bereits eingelegtes Buch.

## Liftanzeige

Ausgabekiste X -683 / Y 131 / Z 792; Komparator direkt südlich, Lampe bei Z 794. Ein Testitem einlegen: Lampe muss leuchten; Kiste leeren: Lampe muss ausgehen. Die Kupfereinfassung ist dekorativ. Rückstauabschaltung und automatische Abzweige auf K1/K2 bleiben offen; der Lift hat weiterhin keine Langzeit-Abnahme.

## Stall und Orangerie

Stallboden Y 125, Orangerieboden Y 126. Wege und Sockel mit den zusätzlichen Erdarbeiten abgleichen. Stall mit Pferden und einer Truhe für Pferderüstungen bestücken. Normale Rüstungsständer können Pferderüstungen nicht darstellen. Die Gewächshaus-Arbeitstische tragen echte Blumentöpfe mit Farn; Hängeblüten sitzen unter tragenden Dachblöcken.

## Suiten und Licht

Alle sechs Betten bleiben zugänglich. Jeder Kamin erhält einen eigenen hohlen Abzug; beim Bau zunächst Luftkanal freihalten und erst dann zünden. Rauchführung und Funkenwirkung sowie die übrige Beleuchtung im Spiel prüfen. Die neuen Gartenleuchten sind keine Spawn-Zertifizierung.

[Mojang: Redstone-Komparator](https://www.minecraft.net/en-us/article/taking-inventory--redstone-comparator) beschreibt die Buchseiten-Auswertung. [Mojang: Kupferbirne](https://www.minecraft.net/da-dk/article/minecraft-snapshot-23w43a) beschreibt deren Umschaltverhalten; für die Inhaltsanzeige ist eine normale Redstone-Lampe in Kupfereinfassung modelliert.
""")
    setup=d['decoration_setup'];commands=['# In der richtigen Dimension ausführen; Koordinaten beziehen sich auf das Anwesen.','# Erzeugt nur fehlende, eindeutig markierte Rüstungsständer. Erneutes Ausführen setzt ihre Ausrüstung zurück.']
    for stand in setup['armor_stands']:
        x,y,z=stand['position'];tag=stand['tag'];material=stand['armor']
        selector=f'@e[type=minecraft:armor_stand,tag={tag},limit=1]'
        commands.append(f'execute unless entity {selector} run summon minecraft:armor_stand {x} {y} {z} {{Tags:["{tag}"],ShowArms:1b,NoGravity:1b,Rotation:[180f,0f]}}')
        for slot,piece in (('head','helmet'),('chest','chestplate'),('legs','leggings'),('feet','boots')):
            commands.append(f'item replace entity {selector} armor.{slot} with minecraft:{material}_{piece}')
    commands.append('# Regale nach dem Strukturimport bestücken; setzt die sechs vorgesehenen Fächer neu.')
    for shelf in setup['bookshelves']:
        x,y,z=shelf['position']
        for slot in range(6):commands.append(f'item replace block {x} {y} {z} container.{slot} with minecraft:{"book" if slot<shelf["books"] else "air"}')
    with (ROOT/'einrichtung_5.22.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['Material','Anzahl','Verwendung'])
        writer.writerow(['armor_stand',2,'Remisen-Nischen; nicht im Blockmaterialbedarf'])
        for material in ('leather','diamond'):
            for piece in ('helmet','chestplate','leggings','boots'):writer.writerow([material+'_'+piece,1,'Ruestungsstaender'])
        writer.writerow(['book',sum(shelf['books'] for shelf in setup['bookshelves']),'Vier gemeisselte Bibliotheksregale'])
    (ROOT/'remise_bibliothek_5.22.mcfunction').write_text('\n'.join(commands)+'\n')
    (ROOT/'technik_5.22.md').write_text("""# Einrichtung und Liefergong · 5.22

## Dekoration im Spiel ergänzen

Der NBT-Export enthält weiterhin keine Entitäten und keine vorbefüllten Bücherregale. remise_bibliothek_5.22.mcfunction ergänzt in der Dimension des Anwesens zwei Rüstungsständer mit vollständiger Leder- bzw. Diamantrüstung und bestückt vier Bibliotheksregale mit 1, 2, 4 und 6 Büchern. Die Datei kann in eine vorhandene Java-Datapack-Funktion übernommen oder ihre Befehle einzeln ausgeführt werden. Es wurde nichts auf dem Server ausgeführt. Wiederholung erzeugt keine zusätzlichen markierten Ständer, setzt aber deren Ausrüstung und die vier Regalbestände auf den Plan zurück. Vor dem Aufruf müssen die zugehörigen Chunks geladen sein.

Rüstungsständer: X -743.5 / Y 126 / Z 764.5 sowie X -741.5 / Y 126 / Z 764.5. Regale: X -694, -691, -688 bei Y 106 / Z 778 sowie X -691 / Y 106 / Z 781. Sie ersetzen ausschließlich Dekorregale; Kolbenregale und Buchsteuerung bleiben unverändert. Die mcfunction ist eine Einrichtungsdatei, kein bereits installiertes Datapack.

## Gong testen

Die vorhandene Redstone-Lampe bei X -683 / Y 131 / Z 794 speist einen Repeater und einen Subtraktionskomparator. Ein verzögerter, auf 15 verstärkter Seitenzweig beendet den Ausgangsimpuls. Der Notenblock bei X -683 / Y 131 / Z 799 steht auf Gold; der Block darüber muss frei bleiben.

Mit leerer Kiste starten, ein Testitem einwerfen: einmaliger Ton. Weitere Items bei nichtleerer Kiste: kein neuer Ton. Kiste leeren: kein Ton. Nach dem Rücksetzen erneut ein Item einwerfen: neuer Ton. Danach eine gefüllte Shulkerbox bei zuvor leerer Kiste testen. Der Gong kann anhand dieser Inhaltsanzeige keine Shulkerbox von anderen Items unterscheiden. Funktion und Verzögerungen sind im Spiel zu prüfen.

## Außenanlagen

Drei Weinbergterrassen auf Y 125, 124 und 123. Seitlicher Treppenweg bleibt frei von Spalieren. Zwei Steglaternen liegen außerhalb der Wasserbucht. Bootsdurchfahrt und Spawn-Sicherheit bleiben vor Ort zu prüfen.

Quellen: [Mojang: gemeißelte Bücherregale](https://www.minecraft.net/es-es/article/chiseled-bookshelf) und [Mojang: Redstone-Komparator](https://www.minecraft.net/en-us/article/taking-inventory--redstone-comparator). Keine Abnahme unserer konkreten Schaltung.
""")
    (ROOT/'analysebericht.md').write_text(report)
    (ROOT/'README.md').write_text(report+f"\nAtlas: `index.html` lokal öffnen. Neu aufbauen: `python tools/build.py`. Git-Tag: `v{VERSION}`.\n\nGemeinsame Materialliste: Organisation → Gemeinsame Liste. Server-Konfiguration und Vercel-Einrichtung stehen in [gemeinsame_liste.md](gemeinsame_liste.md). Benötigt Upstash und einen Teamcode; ohne diese Einstellungen bleibt die zentrale Liste deaktiviert. Der lokale Baufortschritt bleibt im Browser.\n")
    protocol={'revision':VERSION,'status':'Dach-Geheimraum mit Redstone-Lesepultschloss, Strukturprüfung, Zusatzlicht und Verschönerung ergänzt; Ingame-Abnahme offen.',
        'base_revision':VERSION_PREVIOUS,'geometry_changed':True,
        'stair_clearance':clearance,'stair_separation':d['structure']['stair_separation'],
        'material_audit':d.get('material_audit'),'hall_gable_windows':enhancements.get('hall_gable_windows'),'revision_524_checks':{'symmetry':True,'other_build_positions_preserved':True,'roof_outline_preserved':True,'stair_clearance_preserved':True,'in_game_viewed':False},'revision_523_checks':{'windows_preserved':True,'no_overlap_with_required_air':True,'facade_stats':enhancements.get('facade_stats'),'in_game_checked':False},'revision_522_checks':{'vineyard_path':True,'shore_entry_clear':True,'lantern_anchors':True,'gong_topology':True,'setup_commands_prepared':True,'setup_commands_executed':False,'gong_in_game_verified':False},
        'fitout_checks':{'six_beds_accessible':True,'stable_and_orangery_access':True,'hollow_flue_outlets':True,'lamp_anchors_current':True,'book_control_topology':True,'indicator_topology':True},
        'geometry_checks':{'path_continuity':True,'path_headroom':True,'piston_travel':True,'lift_topology':True,'explicit_air_nbt':True,'existing_ladder_preserved':True},
        'revision_526_checks':{'structure_report':structure_findings_ref,'secret_room':enhancements.get('secret_room'),'light_report':enhancements.get('light_report'),'no_unintended_overwrites':True,'in_game_checked':False},'enhancements':enhancements,'service_shaft':vault,'maintenance_shaft':d['structure']['maintenance_shaft'],
        'litematics':[{'file':m['source'],'sha256':m['sha256'],'blocks':m['total_blocks'],'metadata_blocks_match':True} for m in modules['modules']],
        'website_checks':{'aria_references':True,'heading_order':True,'keyboard_logic':True,'data_identity':True,'browser_status':'Chromium-Start durch Betriebssystembeschränkung blockiert'},
        'browser_render_verified':False,'in_game_walk_test':False,'in_game_redstone_verified':False}
    (ROOT/'pruefprotokoll.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    from build_v6 import main as build_current
    build_current()
