#!/usr/bin/env python3
"""Build Revision 5.15 with coordinate-based architecture navigation."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from structure_export import export as export_structure
from litematic_import import build as import_litematics

ROOT=Path(__file__).resolve().parent.parent
SEED=ROOT/'tools'/'seeds'/'revision-5.14'/'blueprint.json'
VERSION='5.15'

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
    return {'levels':output,
        'axes':[{'label':'Eingang & Zufahrt · Westen','x':[-785,-734],'groups':['portikus','vestibuel','zufahrt']},
                {'label':'Zentrale Halle & Querachse','x':[-713,-677],'groups':['halle','galerie']},
                {'label':'Pool & Klippenpanorama · Osten','x':[-657,-631],'groups':['pool','terrasse']}],
        'stair_runs':[{'label':'Kellertreppenhaus','x':[-670,-662],'y':[105,130],'blocks':48},
                      {'label':'Neue zweiläufige Haupttreppe · Halle zur Nordgalerie','x':[-698,-692],'y':[130,136],'blocks':42},
                      {'label':'Galerieaufgänge an Nord- und Südrand','x':[-680,-678],'y':[130,137],'blocks':48}],
        'logistics':[{'label':'Regallager','y':[114,119]},{'label':'Bulk-Lager','y':[114,125]},
                     {'label':'Kupfergolem-Lager','y':[121,123]},{'label':'Einwurfstation','y':[122,126]}]}

def build_main_staircase(blocks):
    changes={};group='halle_treppe'
    # Split 7-step stair into two 3-wide flights with a shared divider and rails.
    for step in range(7):
        y,z=130+step,790-step
        state='facing=north,half=bottom,shape=straight,waterlogged=false'
        for x in (*range(-698,-695),*range(-694,-691)):
            pos=(x,y,z)
            prior=blocks.get(pos)
            if prior:
                if y!=130 or prior[0]!='red_carpet' or prior[2]!='halle':
                    raise ValueError(f'Main stair collides at {pos}: {prior}')
                changes[pos]=(prior,('dark_oak_stairs',state,group))
            else:changes[pos]=(None,('dark_oak_stairs',state,group))
        for x in (-699,-695,-691):
            pos=(x,y+1,z);prior=blocks.get(pos)
            if prior:raise ValueError(f'Main stair handrail collides at {pos}: {prior}')
            changes[pos]=(None,('dark_oak_fence','',group))
    # The upper landing bridges the open atrium to the existing north gallery.
    for z in range(778,784):
        for x in range(-700,-690):
            pos=(x,137,z);prior=blocks.get(pos)
            if prior:raise ValueError(f'Main stair landing collides at {pos}: {prior}')
            changes[pos]=(None,('dark_oak_planks','',group))
        for x in (-701,-689):
            pos=(x,138,z);prior=blocks.get(pos)
            if prior:raise ValueError(f'Main stair gallery rail collides at {pos}: {prior}')
            changes[pos]=(None,('dark_oak_fence','',group))
    for pos,(prior,value) in changes.items():
        if prior is not None and blocks.get(pos)!=prior:raise ValueError(f'Main stair replacement changed at {pos}')
        blocks[pos]=value
    return changes

def main():
    d=json.loads(SEED.read_text())
    old_fingerprint=d['meta']['fingerprint']
    old={} 
    for y,z,x,n,ri in d['runs']:
        bid,state,gi=d['reg'][ri]
        for dx in range(n): old[(x+dx,y,z)]=(bid,state,d['groups'][gi])
    additions=build_main_staircase(old)
    group_names=d['groups']
    if 'halle_treppe' not in group_names:group_names.append('halle_treppe')
    d['groups']=group_names
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
    d['progress_compat']={'revision':'5.14','fingerprint':old_fingerprint,'changed_positions':[f'{x},{y},{z}' for x,y,z in sorted(additions)],'changed_groups':[]}
    d['counts']=dict(counts)
    d['gcounts']={g:dict(c) for g,c in gcounts.items()}
    d['gstats']={}
    for g,points in coords.items():
        if points:d['gstats'][g]={'n':len(points),'x':[min(p[0] for p in points),max(p[0] for p in points)],'y':[min(p[1] for p in points),max(p[1] for p in points)],'z':[min(p[2] for p in points),max(p[2] for p in points)]}
    d['validation'].update(version=VERSION,base='5.14',blocks=len(indexed),fingerprint=d['meta']['fingerprint'])
    d['structure']=build_structure_metadata(d)
    d['structure_export']=export_structure(d,ROOT/f'blackthorn_estate_{VERSION}.nbt')
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    write_blocklist(sequence)
    write_materials(counts,gcounts,group_names)
    write_diff(additions)
    modules=import_litematics()
    write_placement(modules)
    update_progress()
    write_project_docs(d,modules)
    from web import build
    build(d)
    for oldfile in ('blackthorn_estate_5.14.nbt','manifest_5.14.json','aenderungen_5.13_zu_5.14.csv'):
        p=ROOT/oldfile
        if p.exists():p.unlink()
    write_manifest()
    print(f'Revision {VERSION}: {len(indexed):,} build positions; {sum(counts.values()):,} material items; {len(additions)} main-stair positions added or replaced.')
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
    path=ROOT/'aenderungen_5.14_zu_5.15.csv'
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

def write_manifest():
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.name==f'manifest_{VERSION}.json':continue
        raw=p.read_bytes()
        files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    (ROOT/f'manifest_{VERSION}.json').write_text(json.dumps({'revision':VERSION,'files':files},ensure_ascii=False,indent=2)+'\n')

def update_progress():
    p=ROOT/'progress.js';s=(ROOT/'tools'/'seeds'/'revision-5.14'/'progress.js').read_text()
    s=s.replace('5.14','5.15').replace('5.13','5.14')
    s=s.replace("old=!saved&&localStorage.getItem('blackthorn:5.15:progress')", "old=!saved&&localStorage.getItem('blackthorn:5.14:progress')")
    s=s.replace('Revision 5.15 oder ein unverändertes 5.15-Backup verwenden.', 'Revision 5.15 oder ein unverändertes 5.14-Backup verwenden.')
    s=s.replace('Stand aus 5.15 übernommen.', 'Stand aus 5.14 übernommen.')
    p.write_text(s)

def write_project_docs(d,modules):
    (ROOT/'README.md').write_text("""# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.15**. `index.html` lokal im Browser öffnen.

## Was ist neu?

- Eine breite zweiläufige Haupttreppe führt aus der Großen Halle hinauf zur Nordgalerie.
- **Hausstruktur** zeigt Etagen, Höhen, Raumbezüge, Gebäudeachsen und Treppen auf Basis des tatsächlichen Blockmodells.
- Die Richtungshinweise sind korrigiert: Eingang und Zufahrt liegen westlich, Pool und Klippenpanorama östlich.
- Der interne Voxel-Renderer zeichnet nur bei Änderungen und ordnet unbekannte Blockmaterialien mit passenden Ersatzfarben ein.
- Die beiden Copper-Golem-Litematics bleiben unter **Lager → Sortierung & Technik** mit Materialübersichten und Einbauvorschlag erreichbar.

Erdgeschoss und Obergeschoss bleiben bei je acht Y-Ebenen. Die Lagertechnik bleibt vorerst auf Keller 1 und 2 verteilt; ihre Verlegung braucht noch einen abgestimmten Grundriss. Aushub, Zugang, Itemwege und Redstone der Litematic-Module sind weiterhin nicht im Spiel abgenommen.

## Versionsverlauf

`git log --oneline --decorate` zeigt die Revisionen. Revision 5.14 bleibt als Verlaufspunkt erhalten; der aktuelle Stand ist mit `v5.15` markiert.

## Neu aufbauen

```sh
python tools/build.py
```

Der Build verwendet die gespeicherten Modelle unter `tools/seeds/` und die Litematics unter `litematics/`.
""")
    m1,m2=modules['modules']
    (ROOT/'analysebericht.md').write_text(f"""# Revision 5.15 · Hausstruktur im Bauatlas

Die Große Halle erhält eine zweiläufige, 7 Stufen hohe Haupttreppe mit Handläufen und Galeriebrücke zur bestehenden Nordgalerie. Der neue Bereich **Bauatlas → Hausstruktur** zeigt Etagen, Gebäudeachsen und Treppenpositionen aus dem Revisionsmodell.

## Abgleich der vorgelegten Analyse

- Keller 3, Keller 2 und Keller 1 umfassen jeweils acht Y-Ebenen: 105–112, 113–120 und 121–128.
- Erdgeschoss 129–136 und Obergeschoss 137–144 sind ebenfalls jeweils acht Ebenen hoch. Eine zusätzliche Erhöhung der EG-Raumhöhe ist im aktuellen Modell daher nicht nötig.
- Die genannten Raumzahlen sind gesetzte Blöcke, keine Grundfläche. Das Vestibül reicht über X −733…−713 und Z 787…793 (21 × 7 Grundfläche); die Küche über 21 × 12.
- Die Kellertreppe verläuft von Y 105 bis 130 und die zwei Galerierand-Läufe von Y 130 bis 137. Die neue zweiläufige Haupttreppe sitzt zentral in der Großen Halle und führt auf die Nordgalerie. Der Übergang von der Kellertreppe aus der Bibliotheksseite zur neuen Haupttreppe muss im Spiel noch auf freien Durchgang geprüft werden.
- Die Lagertechnik ist über Keller 1 und 2 verteilt. Der Atlas weist diese Höhen jetzt gesammelt aus. Die Verlegung in einen Technikstollen erfordert noch einen eigenen Grundriss und Geländeabgleich.

## Lagertechnik-Vorlagen

- **{m1['name']}**: {m1['total_blocks']:,} Blöcke, {m1['entity_total']} Entities und {m1['block_entity_total']} Blockentities.
- **{m2['name']}**: {m2['total_blocks']:,} Blöcke, {m2['entity_total']} Entities und {m2['block_entity_total']} Blockentities.

Die Litematics bleiben originalgetreu und separat vom Hausblockplan. Ihre Aushub- und Anschlussplanung ist noch nicht im Spiel geprüft.
""")
    protocol={'revision':'5.15','status':'Zweiläufige Haupttreppe in die Große Halle eingefügt; Ingame-Wegeprüfung ausstehend.',
        'base_revision':'5.14','geometry_changed':True,'changed_positions':len(d['progress_compat']['changed_positions']),
        'litematics':[{'file':m['source'],'sha256':m['sha256'],'blocks':m['total_blocks'],'metadata_blocks_match':True} for m in modules['modules']],
        'browser_render_verified':False,'in_game_redstone_verified':False}
    (ROOT/'pruefprotokoll.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
