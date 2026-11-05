#!/usr/bin/env python3
"""Build Revision 5.16 with static access checks and an explicit service-shaft plan."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from structure_export import export as export_structure
from litematic_import import build as import_litematics

ROOT=Path(__file__).resolve().parent.parent
SEED=ROOT/'tools'/'seeds'/'revision-5.15'/'blueprint.json'
VERSION='5.16'
VERSION_PREVIOUS='5.15'

def build_structure_metadata(d):
    levels=[
        ('keller_3','Keller 3',105,112,['keller_3','trading_hall','geheimraum','geheimgang','privatlager']),
        ('keller_2','Keller 2',113,120,['keller_2','lager_regale','bulk_lager','keller_treppe']),
        ('keller_1','Keller 1',121,128,['keller_1','golem_lager','lager_technik','shulker_technik','keller_treppe']),
        ('erdgeschoss','Erdgeschoss',129,136,['halle','halle_treppe','kueche','speisesaal','vestibuel','portikus','bibliothek','res1','res2','res3','res4','res5','res6']),
        ('obergeschoss','Obergeschoss & Galerie',137,144,['halle','halle_treppe','galerie','bibliothek','res1','res2','res3','res4','res5','res6','dach_ostfluegel']),
        ('dach','Dach & Türme',145,157,['dach_halle','dach_res','dach_bibliothek','fassade','dach_schmuck'])]
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
                         'note':'Nur Koordinatenvorschlag; Geschossöffnungen, Aufzugschaltung und Einwurf noch nicht umgesetzt.'},
        'logistics':[{'label':'Regallager','y':[114,119]},{'label':'Bulk-Lager','y':[114,125]},
                     {'label':'Kupfergolem-Lager','y':[121,123]},{'label':'Einwurfstation','y':[122,126]}]}

def main():
    d=json.loads(SEED.read_text())
    old_fingerprint=d['meta']['fingerprint']
    old={} 
    for y,z,x,n,ri in d['runs']:
        bid,state,gi=d['reg'][ri]
        for dx in range(n): old[(x+dx,y,z)]=(bid,state,d['groups'][gi])
    additions={}
    group_names=d['groups']
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
            if not (bid=='water' or bid.endswith('_door') and 'half=upper' in state or bid.endswith('_bed') and 'part=head' in state):
                counts[bid]+=1;gcounts[group][bid]+=1
    d['reg']=reg;d['runs']=runs;d['meta']['version']=VERSION;d['meta']['total']=len(indexed)
    d['meta']['bbox']=[min(p[0] for p in indexed),max(p[0] for p in indexed),min(p[1] for p in indexed),max(p[1] for p in indexed),min(p[2] for p in indexed),max(p[2] for p in indexed)]
    d['meta']['fingerprint']=hashlib.sha256(json.dumps(sequence,separators=(',',':')).encode()).hexdigest()
    d['progress_compat']={'revision':'5.15','fingerprint':old_fingerprint,'changed_positions':[],'changed_groups':[]}
    d['counts']=dict(counts)
    d['gcounts']={g:dict(c) for g,c in gcounts.items()}
    d['gstats']={}
    for g,points in coords.items():
        if points:d['gstats'][g]={'n':len(points),'x':[min(p[0] for p in points),max(p[0] for p in points)],'y':[min(p[1] for p in points),max(p[1] for p in points)],'z':[min(p[2] for p in points),max(p[2] for p in points)]}
    d['validation'].update(version=VERSION,base='5.15',blocks=len(indexed),fingerprint=d['meta']['fingerprint'])
    modules=import_litematics()
    d['structure']=build_structure_metadata(d)
    d['structure_export']=export_structure(d,ROOT/f'blackthorn_estate_{VERSION}.nbt')
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    write_blocklist(sequence)
    write_materials(counts,gcounts,group_names)
    write_diff(additions)
    write_placement(modules)
    update_progress()
    write_project_docs(d,modules)
    from web import build
    build(d)
    for oldfile in ('blackthorn_estate_5.15.nbt','manifest_5.15.json','aenderungen_5.14_zu_5.15.csv'):
        p=ROOT/oldfile
        if p.exists():p.unlink()
    write_manifest()
    print(f'Revision {VERSION}: {len(indexed):,} build positions; {sum(counts.values()):,} material items; static access and shaft plan generated.')
    print('Litematic modules:',', '.join(f"{m['name']} ({m['total_blocks']:,} blocks)" for m in modules['modules']))

def write_blocklist(sequence):
    with (ROOT/'blockliste.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Nummer','X','Y','Z','Minecraft-Block','Blockstate','Baugruppe']);w.writerows(sequence)

def stack_size(block):return 1 if block=='water_bucket' or block.endswith('_bed') or block.endswith('shulker_box') else 16 if block.endswith('_sign') else 64

def write_materials(counts,gcounts,groups):
    with (ROOT/'materialbedarf.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Material','Anzahl','Stackgroesse','volle_Stacks','Rest','volle_Shulkers','Rest_nach_Shulkern'])
        for block,count in sorted(counts.items(),key=lambda p:(-p[1],p[0])):
            size=stack_size(block);per=size*27;sh,remain=divmod(count,per);stacks,rest=divmod(remain,size)
            w.writerow([block,count,size,count//size,count%size,sh,rest])
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
        w.writerow(['Schachtachse · Vorschlag','Nicht gebaut',sx,80,sz,'—',1,57,1,0,0,f'Achse X {sx} / Z {sz}; Y 80…136; Geschossöffnungen erforderlich'])

def write_manifest():
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.name==f'manifest_{VERSION}.json':continue
        raw=p.read_bytes()
        files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    (ROOT/f'manifest_{VERSION}.json').write_text(json.dumps({'revision':VERSION,'files':files},ensure_ascii=False,indent=2)+'\n')

def update_progress():
    p=ROOT/'progress.js';s=(ROOT/'tools'/'seeds'/'revision-5.15'/'progress.js').read_text()
    s=s.replace('5.15','5.16').replace('5.14','5.15')
    p.write_text(s)

def write_project_docs(d,modules):
    clearance=d['structure']['stair_clearance']
    vault=d['structure']['service_shaft']
    (ROOT/'README.md').write_text("""# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.16**. `index.html` lokal im Browser öffnen.

## Was ist neu?

- Der Atlas dokumentiert den statischen 3-Block-Kopfraum über den Treppen sowie die Koordinatendifferenz zwischen Keller- und Haupttreppe.
- Die Litematic-Technikhalle ist jetzt mit Gesamtmaßen, Servicelücke, Zugangskoordinate und den nötigen Geschossdurchbrüchen ausgewiesen.
- Die Website kennzeichnet klar, dass Laufweg, Schacht und Redstone noch nicht im Spiel abgenommen sind.

Die Hausgeometrie bleibt gegenüber 5.15 unverändert. Das Itemlift-System und die Öffnungen in den Geschossdecken sind Planungsangaben, keine gebaute oder geprüfte Mechanik.

## Versionsverlauf

`git log --oneline --decorate` zeigt die Revisionen. `v5.15` bleibt erhalten; der aktuelle Stand ist mit `v5.16` markiert.

## Neu aufbauen

```sh
python tools/build.py
```

Der Build verwendet die gespeicherten Modelle unter `tools/seeds/` und die Litematics unter `litematics/`.
""")
    m1,m2=modules['modules']
    (ROOT/'analysebericht.md').write_text(f"""# Revision 5.16 · Zugang und Technikschacht

## Treppen und Laufweg

Die Keller- und Haupttreppe sind im X-Mittelpunkt 29 Blöcke voneinander entfernt; zwischen ihren nächsten X-Kanten liegen 22 Blöcke. Die Kellertreppe kommt an der Bibliotheksseite auf EG-Höhe an. Von dort führt der Weg über Bibliothek/Halle zur Haupttreppe.

Die Blockbelegung über jeder Treppenstufe wurde statisch für drei Y-Ebenen geprüft:

{chr(10).join(f"- `{entry['group']}`: {entry['stair_blocks']} Treppenblöcke, {entry['obstructed_positions']} belegte Kopfraumpositionen in den drei Ebenen darüber." for entry in clearance)}

Das belegt freie Blockzellen im Modell, aber keinen Lauf- oder Türtest im Spiel. Der Ingame-Test bleibt offen.

## Technikstollen und Aufzugsvorschlag

Die zwei Vorlagen umfassen zusammen eine geplante Grundfläche von 57 × 27 und 24 Blöcke Höhe: X −715…−659, Y 80…103, Z 770…796. Der 3 Blöcke breite Wartungsspalt liegt bei X −688…−686. Als vertikale Serviceachse ist X {vault['position'][0]}, Z {vault['position'][2]} vorgesehen.

An dieser Achse liegen derzeit Geschossblöcke bei Y {', '.join(str(p['y']) for p in vault['vertical_floor_blocks'])}. Diese Durchbrüche, die Verbindung zur Einwurfstation und die Aufzugsschaltung sind noch nicht in den Hausblockplan übernommen. Die Achse ist ein Platzierungsvorschlag, kein fertiger Dropper- oder Wasserlift.

- **{m1['name']}**: {m1['bounds_size'][0]} × {m1['bounds_size'][1]} × {m1['bounds_size'][2]} Blöcke; Anker X −715 / Y 80 / Z 770.
- **{m2['name']}**: {m2['bounds_size'][0]} × {m2['bounds_size'][1]} × {m2['bounds_size'][2]} Blöcke; Anker X −685 / Y 82 / Z 770.

Die Original-Litematics bleiben separat, damit Entities und Blockentity-Daten erhalten bleiben. Die Technikhalle ist nicht in der Oberflächen-Terraformingliste enthalten.
""")
    protocol={'revision':'5.16','status':'Statischer Treppen-Kopfraum und Technikschacht-Koordinaten dokumentiert; Ingame-Lauftest und Lift nicht umgesetzt.',
        'base_revision':'5.15','geometry_changed':False,
        'stair_clearance':clearance,'stair_separation':d['structure']['stair_separation'],
        'service_shaft':vault,
        'litematics':[{'file':m['source'],'sha256':m['sha256'],'blocks':m['total_blocks'],'metadata_blocks_match':True} for m in modules['modules']],
        'browser_render_verified':False,'in_game_walk_test':False,'in_game_redstone_verified':False}
    (ROOT/'pruefprotokoll.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
