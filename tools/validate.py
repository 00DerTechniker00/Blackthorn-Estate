#!/usr/bin/env python3
"""Independent model, warehouse-access and earthwork validation for Revision 5.9."""
import csv
import hashlib
import json
import re
from collections import Counter,defaultdict,deque
from pathlib import Path
from region import Region

ROOT=Path(__file__).resolve().parent.parent


def read(name):
    with (ROOT/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f,delimiter=';'))


def main():
    d=json.loads((ROOT/'blueprint.json').read_text());b={};sequence=[];counts=Counter();gm=defaultdict(Counter)
    html=(ROOT/'index.html').read_text()
    assert d==json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',html,re.S).group(1))
    for y,z,x,n,i in d['runs']:
        bid,st,gi=d['reg'][i];g=d['groups'][gi]
        for xx in range(x,x+n):
            p=xx,y,z;assert p not in b
            b[p]=bid,st,g;sequence.append([len(sequence)+1,xx,y,z,'minecraft:'+bid,st,g])
            if not (bid=='water' or bid.endswith('_door') and 'half=upper' in st or bid.endswith('_bed') and 'part=head' in st):counts[bid]+=1;gm[g][bid]+=1
    assert len(b)==d['meta']['total']
    assert hashlib.sha256(json.dumps(sequence,separators=(',',':')).encode()).hexdigest()==d['meta']['fingerprint']
    assert list(map(lambda r:list(r.values()),read('blockliste.csv')))==[[str(v) for v in row] for row in sequence]
    assert counts==d['counts']
    assert {g:dict(gm[g]) for g in d['groups']}==d['gcounts']
    assert {r['Material']:int(r['Anzahl']) for r in read('materialbedarf.csv')}==counts
    for g,s in d['gstats'].items():
        coords=[p for p,v in b.items() if v[2]==g];assert len(coords)==s['n']
        for key,i in [('x',0),('y',1),('z',2)]:assert [min(p[i] for p in coords),max(p[i] for p in coords)]==s[key]
    for (x,y,z),(bid,st,g) in b.items():
        if bid.endswith('_door'):
            lower='half=lower' in st;other=b.get((x,y+(1 if lower else -1),z))
            assert other and other[0]==bid and ('half=upper' if lower else 'half=lower') in other[1],f'Orphan {x,y,z}'
            if lower:assert b.get((x,y-1,z)),f'Floating door {x,y,z}'
    def reachable(floor,start,box):
        xmin,xmax,zmin,zmax=box
        def free(x,z):return (x,floor,z) in b and (x,floor+1,z) not in b and (x,floor+2,z) not in b
        assert free(*start),f'Blocked route start {start}'
        reached={start};todo=deque([start])
        while todo:
            x,z=todo.popleft()
            for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
                p=x+dx,z+dz
                if p not in reached and xmin<=p[0]<=xmax and zmin<=p[1]<=zmax and free(*p):reached.add(p);todo.append(p)
        return reached
    warehouse=reachable(113,(-674,790),(-710,-673,767,813))
    private=reachable(105,(-702,790),(-709,-698,767,792))
    seen=set();nslots=0
    for bay in d['storage_bays']:
        for p in bay['containers']:
            assert tuple(p) not in seen;seen.add(tuple(p));assert b[tuple(p)][0]=='barrel'
            state=dict(v.split('=') for v in b[tuple(p)][1].split(','));facing=state['facing']
            dx,dz={'north':(0,-1),'south':(0,1),'east':(1,0),'west':(-1,0)}[facing]
            x,y,z=p
            assert (x+dx,y,z+dz) not in b,f'Container front blocked {p}'
        fx,fy,fz=bay['front'];assert (fx,fz) in (warehouse if bay['floor']==113 else private),f'Unreachable bay {bay["id"]}'
        assert len(bay['containers'])==bay['container_count'] and bay['slots']==27*bay['container_count'];nslots+=bay['slots']
    assert len(d['storage_bays'])==56 and len(seen)==448 and nslots==12096
    assert sum(d['storage_summary']['all_containers'].values())*27==d['storage_summary']['total_slots']
    assert d['validation']['rotation_degrees']==180
    assert not any(g=='observatorium' for bid,st,g in b.values())
    assert max(p[1] for p,v in b.items() if v[2].startswith('dach_'))==157
    # All remaining lanterns have an immediate support or a continuous ceiling chain.
    lamp_rows=[]
    for (x,y,z),(bid,state,g) in b.items():
        if bid not in ('lantern','soul_lantern'):continue
        if 'hanging=true' in state:
            yy=y+1
            while b.get((x,yy,z),('','',''))[0] in ('chain','iron_chain'):yy+=1
            assert (x,yy,z) in b,f'Unattached lamp {x,y,z}'
        else:
            yy=y-1;assert (x,yy,z) in b,f'Floating floor lamp {x,y,z}'
        lamp_rows.append([x,y,z,state,x,yy,z,b[x,yy,z][0]])
    with (ROOT/'laternen_pruefung.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['X','Y','Z','Zustand','Anker-X','Anker-Y','Anker-Z','Ankerblock']);w.writerows(lamp_rows)
    for x in range(-662,-652):
        for z in (789,790):
            assert (x,129,z) in b
            for y in (130,131,132):assert (x,y,z) not in b or b[x,y,z][0].endswith('_door'),f'Pool route obstruction {x,y,z}'
    for i in range(8):
        for x in (-661,-660,-659):
            y,z=130+i,798+i
            assert b[x,y,z][0]=='dark_oak_stairs' and 'facing=south' in b[x,y,z][1]
            assert (x,y+1,z) not in b and (x,y+2,z) not in b
    assert d['route_safety']['min_center_distance_to_natural_drop_9']>=15
    # Directed container topology remains an explicit check, not a circuit simulation.
    direction={'north':(0,0,-1),'south':(0,0,1),'east':(1,0,0),'west':(-1,0,0),'down':(0,-1,0)}
    def trace(pos,terminal):
        seen=set()
        while pos not in seen:
            seen.add(pos);entry=b.get(pos);assert entry,f'Feed terminates at {pos}'
            if entry[0]==terminal:return
            assert entry[0]=='hopper'
            props=dict(v.split('=') for v in entry[1].split(','));vec=direction[props['facing']];pos=tuple(a+c for a,c in zip(pos,vec))
        raise AssertionError('Hopper loop')
    trace((-672,127,796),'waxed_copper_chest')
    for bay in d['storage_system']['bulk']:
        for role in ['loose','active_box','dispenser','piston','empty_supply']:
            assert tuple(bay[role]) in b
        for p in bay['bins']:assert b[tuple(p)][0]=='barrel'
        p=bay['active_box'];assert b[tuple(p)][0]=='shulker_box'
        assert b[p[0],p[1]-1,p[2]][0]=='hopper' and 'enabled=false' in b[p[0],p[1]-1,p[2]][1]
        trace((p[0],p[1]-2,p[2]),'barrel')
    region=Region(ROOT.parent/'mca.zip');t=d['terrain'];x0,x1,z0,z1=t['bounds']
    assert (x1-x0+1)*(z1-z0+1)==62101
    for z in range(z0,z1+1):
        for x in range(x0,x1+1):assert region.block(x,t['heights'][z-z0][x-x0],z)==t['surface_blocks'][z-z0][x-x0]
    cuts=read('aushub_blockliste.csv');fills=read('auffuellung_blockliste.csv');cut_by_column=Counter();fill_by_column=Counter();seen_cut=set();seen_fill=set()
    for row in cuts:
        p=tuple(int(row[k]) for k in ['X','Y','Z']);assert p not in seen_cut;seen_cut.add(p)
        actual=region.block(*p);assert actual not in ('air','cave_air','void_air') and row['Ist-Block']=='minecraft:'+actual
        cut_by_column[p[0],p[2]]+=1
    for row in fills:
        x,y,z=[int(row[k]) for k in ['X','Y','Z']];p=x,y,z;assert p not in seen_fill;seen_fill.add(p)
        assert y>t['heights'][z-z0][x-x0] and y<=t['target_heights'][z-z0][x-x0]
        assert row['Soll-Block']=='minecraft:'+b[p][0],f'Wrong fill material {p}'
        fill_by_column[x,z]+=1
    assert not seen_cut&seen_fill
    for (x,y,z),(bid,state,group) in b.items():
        if x0<=x<=x1 and z0<=z<=z1 and y<=t['heights'][z-z0][x-x0]:
            old=region.block(x,y,z)
            if old not in ('air','cave_air','void_air') and old!=bid:assert (x,y,z) in seen_cut,f'Missing construction collision {x,y,z}'
    assert len(cuts)==t['excavate_total'] and len(fills)==t['fill_total']
    assert Counter(r['Soll-Block'].removeprefix('minecraft:') for r in fills)=={r['Soll-Material']:int(r['Bloecke']) for r in read('auffuellung_materialien.csv')}
    for x,z,old,target,cut,fill,zone,top in t['work']:
        assert cut_by_column[x,z]==cut and fill_by_column[x,z]==fill
        assert old==t['heights'][z-z0][x-x0] and target==t['target_heights'][z-z0][x-x0]
    # Outside designated work columns the expanded landscape must be identical.
    work={(r[0],r[1]) for r in t['work']}
    for z in range(z0,z1+1):
        for x in range(x0,x1+1):
            if (x,z) not in work:assert t['heights'][z-z0][x-x0]==t['target_heights'][z-z0][x-x0]
    for ref in re.findall(r'(?:src|href)="([^"]+)"',html):
        if ref.startswith('#'):continue
        assert ref.startswith('https://www.minecraft.net/') or ('://' not in ref and (ROOT/ref).is_file()),f'Missing/local asset: {ref}'
    original=json.loads((ROOT.parent.parent/'manifest.json').read_text())
    for f in original['files']:
        p=ROOT.parent/f['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
    base=ROOT.parent/'Blackthorn-Estate-Revision-5.8'
    for f in json.loads((base/'manifest_5.8.json').read_text()):assert hashlib.sha256((base/f['path']).read_bytes()).hexdigest()==f['sha256']
    print(f'PASS: {len(b):,} unique build positions, all materials and door pairs; 56 accessible bays / 448 barrels; 62,101 surveyed columns; {len(cuts):,} exact cut and {len(fills):,} fill positions; unchanged originals.')


if __name__=='__main__':main()
