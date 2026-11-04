"""Revision 5.9: architectural massing, storage furniture and surveyed earthworks."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from region import Region

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'Blackthorn-Estate-Revision-5.8'
AIR={'air','cave_air','void_air'}
PLANTS={'short_grass','tall_grass','allium','wildflowers','leaf_litter','torch','wall_torch',
 'oak_leaves','birch_leaves','oak_log','birch_log','dandelion','poppy','azure_bluet','cornflower',
 'oxeye_daisy','fern','large_fern','vine','pink_petals','sunflower','rose_bush','lilac','peony',
 'spruce_log','spruce_leaves','brown_mushroom','red_mushroom'}
PLANTS |= {'bush','firefly_bush','lily_of_the_valley','blue_orchid','closed_eyeblossom','open_eyeblossom','pointed_dripstone','bee_nest'}


def ignored_ground(bid):
    return bid in AIR|PLANTS or bid.endswith(('_leaves','_log','_wood','_sapling','_banner','_wall_banner'))


def csvout(name,header,rows):
    with (ROOT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f,delimiter=';');w.writerow(header);w.writerows(rows)


def build():
    d=json.loads((BASE/'blueprint.json').read_text());b={}
    for y,z,x,n,ri in d['runs']:
        bid,st,gi=d['reg'][ri]
        for xx in range(x,x+n):b[xx,y,z]=(bid,st,d['groups'][gi])
    before=b.copy()
    def put(x,y,z,bid,st='',g='fassade'):b[x,y,z]=(bid,st,g)
    def clear(x0,x1,y0,y1,z0,z1):
        for p in list(b):
            x,y,z=p
            if x0<=x<=x1 and y0<=y<=y1 and z0<=z<=z1:del b[p]
    def room(name,g,xx,yy,zz,text,access):
        return dict(name=name,group=g,x=xx,y=yy,z=zz,text=text,access=access,stand=0,reach=0)

    from design import design,terrain_plan
    d,b,design_report=design(d,b)
    print('Anwesen gedreht, Architektur und Technik modelliert.',flush=True)

    # Read a much wider scene. Heights include actual man-made solid blocks; trees,
    # grasses and flowers are separately excluded from the ground definition.
    world=Region(ROOT.parent/'mca.zip');bounds=[-825,-545,680,900];x0,x1,z0,z1=bounds
    H=[];M=[];surface_stats=Counter();caves=[]
    highest={}
    def surface(x,z):
        key=x//16,z//16
        if key not in highest:
            candidates=[]
            for sy,section in world.chunk(*key).items():
                palette=section.get('block_states',{}).get('palette',[])
                names=[(p if isinstance(p,str) else p.get('Name') or p.get('id') or p['']).removeprefix('minecraft:') for p in palette]
                if any(not ignored_ground(name) for name in names):candidates.append(sy*16+15)
            if not candidates:raise ValueError(f'No ground sections in chunk {key}')
            highest[key]=max(candidates)
        y=highest[key]
        while y>=-64:
            bid=world.block(x,y,z)
            if not ignored_ground(bid):return y,bid
            y-=1
        raise ValueError(f'No ground in column {x},{z}')
    for z in range(z0,z1+1):
        hs=[];ms=[]
        for x in range(x0,x1+1):
            y,bid=surface(x,z);hs.append(y);ms.append(bid);surface_stats[bid]+=1
            start=None
            for yy in range(99,min(y,128)+1):
                air=world.block(x,yy,z) in AIR
                if air and start is None:start=yy
                if not air and start is not None:caves.append([x,z,start,yy-1]);start=None
            if start is not None:caves.append([x,z,start,min(y,128)])
        H.append(hs);M.append(ms)
    grade,zones,surface_block,waypoints=terrain_plan(d,b,H,bounds)

    work=[];cutrows=[];fillrows=[];vegetation=[];conflicts=[];cutcounts=Counter();fillcounts=Counter()
    for (x,z),target_y in sorted(grade.items()):
        natural=H[z-z0][x-x0];zone=zones[x,z];top=surface_block[x,z]
        # Only fill above the surveyed surface. Existing structural blocks take priority.
        for y in range(natural+1,target_y+1):
            if (x,y,z) not in b:
                material=top if y==target_y else ('cobblestone' if zone=='Hausunterbau' else 'dirt')
                g='terraform_auffuellung';put(x,y,z,material,'',g)
            material=b[x,y,z][0];fillrows.append([x,y,z,'minecraft:'+material,zone]);fillcounts[material]+=1
        # Road and garden surfaces are explicit build blocks, never inferred textures.
        if zone not in ('Kellerbaugrube','Hausunterbau'):
            if (x,target_y,z) not in b or b[x,target_y,z][2].startswith('terraform'):
                put(x,target_y,z,top,'','zufahrt' if zone in ('Zufahrt Nordwest','Eingangshof') else 'terraform_oberflaeche')
        column_cut=0
        for y in range(target_y+1,natural+1):
            old=world.block(x,y,z)
            if old in AIR:continue
            # Planned blocks can reuse the identical existing material; else remove it.
            if (x,y,z) in b and b[x,y,z][0]==old:continue
            cutrows.append([x,y,z,'minecraft:'+old,zone]);cutcounts[old]+=1;column_cut+=1
            if old in ('iron_block','beacon','chest','barrel','crafting_table'):conflicts.append([x,y,z,old,zone])
        new_at_surface=b.get((x,target_y,z))
        old_at_surface=world.block(x,target_y,z)
        if target_y<=natural and new_at_surface and old_at_surface not in AIR and new_at_surface[0]!=old_at_surface:
            cutrows.append([x,target_y,z,'minecraft:'+old_at_surface,zone]);cutcounts[old_at_surface]+=1;column_cut+=1
            if old_at_surface in ('iron_block','beacon','chest','barrel','crafting_table'):conflicts.append([x,target_y,z,old_at_surface,zone])
        # Surveyed vegetation is a separate clearance operation, not hidden in rock counts.
        if zone not in ('Kellerbaugrube',):
            for y in range(natural+1,min(170,natural+20)+1):
                old=world.block(x,y,z)
                if old not in AIR and (y<=target_y+3 or ignored_ground(old)):vegetation.append([x,y,z,'minecraft:'+old,zone])
        if column_cut or target_y>natural or zone not in ('Hausunterbau','Kellerbaugrube'):
            final_top=b.get((x,target_y,z),(world.block(x,target_y,z),'',''))[0]
            work.append([x,z,natural,target_y,column_cut,max(0,target_y-natural),zone,final_top])
    # Account for foundation and other planned blocks which replace natural material
    # below the formation height. A height difference alone would miss these collisions.
    cutset={(r[0],r[1],r[2]) for r in cutrows};workmap={(r[0],r[1]):r for r in work}
    for (x,y,z),(material,state,group) in b.items():
        if not(x0<=x<=x1 and z0<=z<=z1) or y>H[z-z0][x-x0] or (x,y,z) in cutset:continue
        old=world.block(x,y,z)
        if old in AIR or old==material:continue
        zone=zones.get((x,z),'Einzelne Baukollisionen')
        cutrows.append([x,y,z,'minecraft:'+old,zone]);cutset.add((x,y,z));cutcounts[old]+=1
        if old in ('iron_block','beacon','chest','barrel','crafting_table'):conflicts.append([x,y,z,old,zone])
        if (x,z) not in workmap:
            planned=grade.get((x,z),H[z-z0][x-x0]);top=b.get((x,planned,z),(world.block(x,planned,z),'',''))[0]
            row=[x,z,H[z-z0][x-x0],planned,0,0,zone,top];work.append(row);workmap[x,z]=row
        workmap[x,z][4]+=1
    cut_min={}
    for x,y,z,bid,zone in cutrows:cut_min[x,z]=min(y,cut_min.get((x,z),y))
    # Clip the terrain to the actual structural bottoms where foundations/terrace piers
    # penetrate it; these columns are construction clearance rather than garden grading.
    newH=[[grade.get((x,z),H[z-z0][x-x0]) for x in range(x0,x1+1)] for z in range(z0,z1+1)]
    terrain=dict(bounds=bounds,heights=H,target_heights=newH,surface_blocks=M,cave_spans=caves,
        surface_stats=dict(surface_stats),vegetation_stats=d['terrain']['vegetation_stats'],work=work,
        excavate=[[x,z,cut_min[x,z],cut,zone] for x,z,old,planned,cut,fill,zone,top in work if cut],
        excavate_total=len(cutrows),excavate_columns=sum(1 for row in work if row[4]),
        fill_total=len(fillrows),fill_columns=sum(1 for row in work if row[5]),waypoints=waypoints)
    d['terrain']=terrain
    csvout('terraforming.csv',['X','Z','Ist-Boden-Y','Soll-Boden-Y','Abtrag_Bloecke','Auffuellung_Bloecke','Bereich','Soll-Oberflaeche'],work)
    csvout('aushub_blockliste.csv',['X','Y','Z','Ist-Block','Bereich'],cutrows)
    csvout('auffuellung_blockliste.csv',['X','Y','Z','Soll-Block','Bereich'],fillrows)
    csvout('vegetation_entfernen.csv',['X','Y','Z','Ist-Block','Bereich'],vegetation)
    csvout('bestandskonflikte.csv',['X','Y','Z','Ist-Block','Bereich'],conflicts)
    csvout('aushub_materialien.csv',['Ist-Material','Bloecke'],cutcounts.most_common())
    csvout('auffuellung_materialien.csv',['Soll-Material','Bloecke'],fillcounts.most_common())
    csvout('aushub.csv',['X','Z','Unterkante_Y','Abtrag','Bereich'],terrain['excavate'])
    csvout('gelaende_oberflaeche.csv',['X','Y','Z','Ist-Block'],
        [[x,H[z-z0][x-x0],z,M[z-z0][x-x0]] for z in range(z0,z1+1) for x in range(x0,x1+1)])

    # Visible load-bearing plinth at the occupied footprint perimeter.
    for (x,z),height in grade.items():
        if zones[x,z]!='Hausunterbau':continue
        edge=any((x+dx,z+dz) not in grade or zones.get((x+dx,z+dz))!='Hausunterbau' for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)])
        if edge:
            for y in range(max(120,H[z-z0][x-x0]+1),129):
                if (x,y,z) not in b or b[x,y,z][2]=='terraform_auffuellung':put(x,y,z,'deepslate_bricks','','sockel')
    # Re-evaluate the fill materials after the visible retaining plinth replaced
    # some of the preliminary filler blocks. CSV and model must describe the same blocks.
    fillrows=[[x,y,z,'minecraft:'+b[x,y,z][0],zone] for x,y,z,material,zone in fillrows]
    fillcounts=Counter(row[3].removeprefix('minecraft:') for row in fillrows)
    csvout('auffuellung_blockliste.csv',['X','Y','Z','Soll-Block','Bereich'],fillrows)
    csvout('auffuellung_materialien.csv',['Soll-Material','Bloecke'],fillcounts.most_common())
    # Ensure no old door was accidentally cut by the furniture/roof edits.
    for p,(bid,st,g) in list(b.items()):
        if not bid.endswith('_door'):continue
        x,y,z=p;lower='half=lower' in st;other=b.get((x,y+(1 if lower else -1),z))
        if not other or other[0]!=bid:b.pop(p)

    groups=list(dict.fromkeys([g for g in d['groups'] if any(v[2]==g for v in b.values())]+[v[2] for v in b.values()]))
    counts=Counter();gm=defaultdict(Counter);stats={};reg=[];lookup={};runs=[];rows=[]
    for n,p in enumerate(sorted(b,key=lambda p:(p[1],p[2],p[0])),1):
        x,y,z=p;bid,st,g=b[p];record=(bid,st,groups.index(g))
        if record not in lookup:lookup[record]=len(reg);reg.append(record)
        ri=lookup[record]
        if runs and runs[-1][0]==y and runs[-1][1]==z and runs[-1][2]+runs[-1][3]==x and runs[-1][4]==ri:runs[-1][3]+=1
        else:runs.append([y,z,x,1,ri])
        s=stats.setdefault(g,dict(n=0,x=[x,x],y=[y,y],z=[z,z]));s['n']+=1
        for key,v in [('x',x),('y',y),('z',z)]:s[key]=[min(v,s[key][0]),max(v,s[key][1])]
        if not (bid=='water' or bid.endswith('_door') and 'half=upper' in st or bid.endswith('_bed') and 'part=head' in st):counts[bid]+=1;gm[g][bid]+=1
        rows.append([n,x,y,z,'minecraft:'+bid,st,g])
    d.update(groups=groups,reg=reg,runs=runs,counts=dict(counts),gcounts={g:dict(gm[g]) for g in groups},gstats=stats)
    d['meta'].update(version='5.9',total=len(b),bbox=[min(p[0] for p in b),max(p[0] for p in b),min(p[1] for p in b),max(p[1] for p in b),min(p[2] for p in b),max(p[2] for p in b)],
        fingerprint=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),
        roof_note='Viktorianisches Klippenanwesen mit sechs Gauben, steinernen Gesimsen und Kupferakzenten; Poolpanorama nach Osten.')
    d['checks'].update(excavation=len(cutrows),doors=sum(1 for bid,st,g in b.values() if bid.endswith('_door') and 'half=lower' in st),
        stairs=sum(1 for bid,st,g in b.values() if bid.endswith('_stairs')),panes=sum(1 for bid,st,g in b.values() if bid=='glass_pane'))
    roof_before=sum(1 for bid,st,g in before.values() if g.startswith('dach_') or g=='observatorium')
    roof_after=sum(1 for bid,st,g in b.values() if g.startswith('dach_'))
    stats_storage=Counter(v[0] for v in b.values() if v[0] in ('barrel','chest','copper_chest','waxed_copper_chest'))
    old_containers=sum(1 for bid,st,g in before.values() if bid in ('barrel','chest','copper_chest','waxed_copper_chest'))
    d['storage_summary']=dict(bulk_box_slots=486,bulk_ready_slots=162,rack_bays=sum(a['floor']==113 for a in d['storage_bays']),private_bays=sum(a['floor']==105 for a in d['storage_bays']),new_barrels=448,new_slots=448*27,
        previous_total_slots=old_containers*27,total_slots=sum(stats_storage.values())*27,
        net_added_slots=(sum(stats_storage.values())-old_containers)*27,
        all_containers=dict(stats_storage),roof_before=roof_before,roof_after=roof_after)
    report=dict(version='5.9',base='5.8',style='Ruhigeres viktorianisches Herrenhaus',blocks=len(b),
        terrain_columns=len(H)*len(H[0]),terrain_bounds=bounds,excavation_blocks=len(cutrows),fill_blocks=len(fillrows),
        vegetation_clear=len(vegetation),existing_structure_conflicts=len(conflicts),roof_before=roof_before,roof_after=roof_after,
        warehouse_barrels=400,private_barrels=48,new_storage_slots=448*27,not_tested_in_game=True,
        light_simulation_current=False,walkability_simulation_current=False,**design_report)
    d['validation']=report
    csvout('blockliste.csv',['Nummer','X','Y','Z','Minecraft-Block','Blockstate','Baugruppe'],rows)
    def stack(bid):return 1 if bid.endswith(('_bed','shulker_box')) else 16 if bid.endswith('_sign') else 64
    csvout('materialbedarf.csv',['Material','Anzahl','Stackgroesse','volle_Stacks','Rest','volle_Shulkers','Rest_nach_Shulkern'],
        [[bid,n,stack(bid),n//stack(bid),n%stack(bid),n//(27*stack(bid)),n%(27*stack(bid))] for bid,n in counts.most_common()])
    csvout('materialbedarf_baugruppen.csv',['Baugruppe','Material','Anzahl'],[[g,bid,n] for g in groups for bid,n in gm[g].most_common()])
    csvout('lagerbuchten.csv',['ID','Kategorie','Kellerboden_Y','X','Y','Z','Faesser','Inventarplaetze','Betrieb'],
        [[a['id'],a['name'],a['floor'],a['x'],a['y'],a['z'],a['container_count'],a['slots'],a['automation']] for a in d['storage_bays']])
    csvout('aenderungen_5.8_zu_5.9.csv',['X','Y','Z','Alt-Block','Alt-State','Alt-Gruppe','Neu-Block','Neu-State','Neu-Gruppe'],
        [[*p,*(before.get(p) or ('','','')),*(b.get(p) or ('','',''))] for p in sorted(set(before)|set(b)) if before.get(p)!=b.get(p)])
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    return d


if __name__=='__main__':build()
