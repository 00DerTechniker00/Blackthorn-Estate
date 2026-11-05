#!/usr/bin/env python3
"""Build Revision 5.14 without the rejected roof lantern."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from structure_export import export as export_structure
from litematic_import import build as import_litematics

ROOT=Path(__file__).resolve().parent.parent
SEED=ROOT/'tools'/'seeds'/'revision-5.12'/'blueprint.json'
PREVIOUS=ROOT/'tools'/'seeds'/'revision-5.13'/'blueprint.json'
VERSION='5.14'

CUPOLA=(-695,790)

def place(add,x,y,z,block,state='',group='dach_schmuck'):
    pos=(x,y,z)
    if pos in add: raise ValueError(f'Duplicate cupola block {pos}')
    add[pos]=(block,state,group)

def roof_lantern(d):
    cx,cz=CUPOLA
    out={}
    # A compact stone drum bridges the Great Hall ridge and carries a glazed lantern room.
    for z in range(cz-2,cz+3):
        for x in range(cx-2,cx+3): place(out,x,158,z,'stone_bricks')
    for y in (159,160):
        for x in range(cx-2,cx+3):
            for z in (cz-2,cz+2):
                if abs(x-cx)==2: place(out,x,y,z,'dark_oak_log','axis=y')
                else: place(out,x,y,z,'glass')
        for z in range(cz-1,cz+2):
            for x in (cx-2,cx+2):
                place(out,x,y,z,'glass' if abs(z-cz)<2 else 'dark_oak_log','' if abs(z-cz)<2 else 'axis=y')
    # A pale stone cornice, a low slate cap, and one oxidized copper finial.
    for x in range(cx-2,cx+3):
        for z in range(cz-2,cz+3):
            if abs(x-cx)==2 or abs(z-cz)==2:
                place(out,x,161,z,'polished_diorite_slab','type=bottom,waterlogged=false')
    for x in range(cx-1,cx+2):
        for z in range(cz-1,cz+2): place(out,x,162,z,'deepslate_tiles')
    place(out,cx,159,cz,'lantern','hanging=false')
    place(out,cx,163,cz,'waxed_oxidized_copper')
    place(out,cx,164,cz,'lightning_rod','facing=up,powered=false,waterlogged=false')
    return out

def main():
    d=json.loads(SEED.read_text())
    previous=json.loads(PREVIOUS.read_text())
    old_fingerprint=previous['meta']['fingerprint']
    old={} 
    for y,z,x,n,ri in d['runs']:
        bid,state,gi=d['reg'][ri]
        for dx in range(n): old[(x+dx,y,z)]=(bid,state,d['groups'][gi])
    removed=roof_lantern(d)
    previous_positions={}
    for y,z,x,n,ri in previous['runs']:
        bid,state,gi=previous['reg'][ri]
        for dx in range(n):previous_positions[(x+dx,y,z)]=(bid,state,previous['groups'][gi])
    for pos,value in removed.items():
        if previous_positions.get(pos)!=value:raise ValueError(f'Expected roof lantern block missing from previous revision at {pos}')
    group_names=d['groups']; group_index={g:i for i,g in enumerate(group_names)}
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
    d['progress_compat']={'revision':'5.13','fingerprint':old_fingerprint,'changed_positions':[f'{x},{y},{z}' for x,y,z in sorted(removed)],'changed_groups':[]}
    d['counts']=dict(counts)
    d['gcounts']={g:dict(c) for g,c in gcounts.items()}
    d['gstats']={}
    for g,points in coords.items():
        if points:d['gstats'][g]={'n':len(points),'x':[min(p[0] for p in points),max(p[0] for p in points)],'y':[min(p[1] for p in points),max(p[1] for p in points)],'z':[min(p[2] for p in points),max(p[2] for p in points)]}
    d['validation'].update(version=VERSION,base='5.13',blocks=len(indexed),fingerprint=d['meta']['fingerprint'])
    d['structure_export']=export_structure(d,ROOT/f'blackthorn_estate_{VERSION}.nbt')
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    write_blocklist(sequence)
    write_materials(counts,gcounts,group_names)
    write_diff(removed)
    modules=import_litematics()
    write_placement(modules)
    update_progress()
    write_project_docs(d,modules)
    from web import build
    build(d)
    for oldfile in ('blackthorn_estate_5.12.nbt','blackthorn_estate_5.13.nbt','manifest_5.12.json','manifest_5.13.json','aenderungen_5.12_zu_5.13.csv'):
        p=ROOT/oldfile
        if p.exists():p.unlink()
    write_manifest()
    print(f'Revision {VERSION}: {len(indexed):,} build positions; {sum(counts.values()):,} material items; removed {len(removed)} roof-lantern blocks.')
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
    path=ROOT/'aenderungen_5.13_zu_5.14.csv'
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['X','Y','Z','Alt-Block','Alt-State','Alt-Gruppe','Neu-Block','Neu-State','Neu-Gruppe'])
        for (x,y,z),(bid,state,group) in sorted(additions.items(),key=lambda p:(p[0][1],p[0][2],p[0][0])):
            w.writerow([x,y,z,'minecraft:'+bid,state,group,'','',''])

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
    p=ROOT/'progress.js';s=p.read_text()
    s=s.replace('5.13','5.14').replace('5.12','5.13')
    p.write_text(s)

def write_project_docs(d,modules):
    (ROOT/'README.md').write_text("""# Blackthorn Estate

Aktueller Bauatlas: **Revision 5.14**. `index.html` lokal im Browser öffnen.

## Was ist neu?

- Die Dachlaterne aus Revision 5.13 wurde auf Wunsch entfernt; die vorherige Dachform ist wiederhergestellt.
- Der interne Voxel-Renderer zeichnet nur bei Änderungen und ordnet unbekannte Blockmaterialien mit passenden Ersatzfarben ein.
- Unter **Lager → Sortierung & Technik** sind die beiden Copper-Golem-Litematics mit Maßen, Materiallisten, Einbauvorschlag und direkter Texturansicht eingebunden.

Die Maschinen sind separate, unveränderte Litematic-Vorlagen. Aushub, Servicezugang, Itemwege und Redstone wurden noch nicht in den Hauptbauplan übernommen oder im Spiel abgenommen.

## Versionsverlauf

`git log --oneline --decorate` zeigt die Revisionen. Revision 5.13 bleibt als Verlaufspunkt erhalten; der aktuelle Stand ist mit `v5.14` markiert.

## Neu aufbauen

```sh
python tools/build.py
```

Der Build verwendet die gespeicherten Modelle unter `tools/seeds/` und die Litematics unter `litematics/`.
""")
    m1,m2=modules['modules']
    (ROOT/'analysebericht.md').write_text(f"""# Revision 5.14 · Dachlaterne entfernt

Die aufgesetzte Dachlaterne aus Revision 5.13 wurde entfernt: {len(CUPOLA_BLOCKS)} Blockpositionen entfallen. Die vorherige Dachform bleibt erhalten. Der Fortschrittsimport übernimmt gesetzte Häkchen und verwirft Status für die entfernten Positionen.

## Eingebundene Litematics

- **{m1['name']}**: {m1['total_blocks']:,} Blockpositionen, {m1['bounds_size'][0]} × {m1['bounds_size'][1]} × {m1['bounds_size'][2]} Blöcke, {m1['entity_total']} Entities, {m1['block_entity_total']} Blockentities.
- **{m2['name']}**: {m2['total_blocks']:,} Blockpositionen, {m2['bounds_size'][0]} × {m2['bounds_size'][1]} × {m2['bounds_size'][2]} Blöcke, {m2['entity_total']} Entities, {m2['block_entity_total']} Blockentities.

Die Vorlagen bleiben unverändert und werden im Textur-Viewer direkt als `.litematic` geladen. So bleiben Kupfergolems, Truhen, Hopper und Blockentity-Daten erhalten. Der Platzierungsvorschlag liegt unter Keller 3; Aushub, Zugang und Anschlüsse sind noch nicht Teil des Bauplans.

## Prüfgrenzen

Die Struktur wurde aus dem gespeicherten Revisionsmodell neu erzeugt. Externe Texturansicht und Redstone wurden nicht im Spiel abgenommen.
""")
    protocol={'revision':'5.14','status':'Dachlaterne entfernt; externe Ansicht und Redstone nicht im Spiel abgenommen.',
        'base_revision':'5.13','removed_roof_lantern_blocks':len(CUPOLA_BLOCKS),
        'litematics':[{'file':m['source'],'sha256':m['sha256'],'blocks':m['total_blocks'],'metadata_blocks_match':True} for m in modules['modules']],
        'browser_render_verified':False,'in_game_redstone_verified':False}
    (ROOT/'pruefprotokoll.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')

CUPOLA_BLOCKS=roof_lantern({})
if __name__=='__main__':main()
