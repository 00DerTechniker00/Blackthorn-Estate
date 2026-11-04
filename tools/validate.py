#!/usr/bin/env python3
"""Independent consistency, topology and region checks. Run from any directory."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from region import Region

ROOT=Path(__file__).resolve().parent.parent


def main():
    html=(ROOT/'index.html').read_text()
    d=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',html,re.S).group(1))
    assert d==json.loads((ROOT/'blueprint.json').read_text()),'JSON export differs from HTML'
    b={};sequence=[];materials=Counter();groups=defaultdict(Counter)
    for y,z,x,n,ri in d['runs']:
        assert n>0 and 0<=ri<len(d['reg'])
        bid,state,gi=d['reg'][ri];g=d['groups'][gi]
        for xx in range(x,x+n):
            coord=xx,y,z
            assert coord not in b, f'Duplicate coordinate {coord}'
            b[coord]=(bid,state,g)
            sequence.append([len(sequence)+1,xx,y,z,'minecraft:'+bid,state,g])
            if not (bid=='water' or bid.endswith('_door') and 'half=upper' in state or bid.endswith('_bed') and 'part=head' in state):
                materials[bid]+=1;groups[g][bid]+=1
    assert len(b)==d['meta']['total']==78600
    with (ROOT/'blockliste.csv').open(encoding='utf-8-sig') as f:
        rows=list(csv.reader(f,delimiter=';'))[1:]
    assert rows==[[str(x) for x in row] for row in sequence]
    assert hashlib.sha256(json.dumps(sequence,separators=(',',':')).encode()).hexdigest()==d['meta']['fingerprint']
    assert dict(materials)==d['counts']
    assert {g:dict(groups[g]) for g in d['groups']}==d['gcounts']
    with (ROOT/'materialbedarf.csv').open(encoding='utf-8-sig') as f:
        assert {r['Material']:int(r['Anzahl']) for r in csv.DictReader(f,delimiter=';')}==dict(materials)
    for g,stats in d['gstats'].items():
        coords=[p for p,r in b.items() if r[2]==g]
        assert len(coords)==stats['n']
        for k,i in [('x',0),('y',1),('z',2)]:assert [min(p[i] for p in coords),max(p[i] for p in coords)]==stats[k]
    for (x,y,z),(bid,state,g) in b.items():
        if bid.endswith('_door'):
            props=dict(v.split('=') for v in state.split(',') if '=' in v)
            lower=props['half']=='lower';other=b.get((x,y+(1 if lower else -1),z))
            assert other and other[0]==bid, f'Orphan door {(x,y,z)}'
            assert ('half=upper' if lower else 'half=lower') in other[1]
            if lower:assert b.get((x,y-1,z)),f'Door has no model support {(x,y,z)}'
    direction={'north':(0,0,-1),'south':(0,0,1),'east':(1,0,0),'west':(-1,0,0),'down':(0,-1,0)}
    def trace(start,terminal):
        pos=start;seen=set()
        while pos not in seen:
            seen.add(pos);entry=b.get(pos)
            assert entry, f'Feed ends in air at {pos}'
            if entry[0]==terminal:return len(seen)
            assert entry[0]=='hopper',f'Unexpected container/block at {pos}: {entry}'
            props=dict(v.split('=') for v in entry[1].split(','));v=direction[props['facing']]
            pos=tuple(a+c for a,c in zip(pos,v))
        raise AssertionError('Hopper loop')
    assert trace((-708,123,789),'copper_chest')>40
    for bay in d['storage_system']['bulk']:trace((bay['x'],122,783),'chest')
    # Deliberately do not equate physical topology with a functioning filter circuit.
    region=Region(ROOT.parent/'mca.zip');t=d['terrain'];x0,x1,z0,z1=t['bounds']
    for z in range(z0,z1+1):
        for x in range(x0,x1+1):assert region.block(x,t['heights'][z-z0][x-x0],z)==t['surface_blocks'][z-z0][x-x0]
    # Independent known sample readings guard palette decoding and negative coordinates.
    assert region.block(-640,126,790)=='grass_block'
    assert region.block(-640,127,790)=='air'
    assert region.block(-630,115,790)=='grass_block'
    actual=Counter()
    with (ROOT/'aushub_blockliste.csv').open(encoding='utf-8-sig') as f:
        coords=set()
        for row in csv.DictReader(f,delimiter=';'):
            p=tuple(int(row[k]) for k in ['X','Y','Z']);assert p not in coords;coords.add(p)
            bid=region.block(*p);assert row['Ist-Block']=='minecraft:'+bid and bid not in ('air','cave_air','void_air')
            actual[p[0],p[2]]+=1
    assert sum(actual.values())==t['excavate_total']==52120
    assert all(actual[x,z]==n for x,z,cut,n,near in t['excavate'])
    for ref in re.findall(r'(?:src|href)="([^"]+)"',html):
        if ref.startswith('#'):continue
        assert '://' not in ref,f'External dependency {ref}'
        assert (ROOT/ref).is_file(),f'Missing local asset {ref}'
    manifest=json.loads((ROOT.parent.parent/'manifest.json').read_text())
    for f in manifest['files']:
        p=ROOT.parent/f['path']
        assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],f'Original file modified: {p}'
    print('PASS: 78,600 unique blocks; CSV/material/group counts; all door pairs and supports; feed and six output paths; 16,428 surface cells; 52,120 excavation blocks; offline assets; all 173 originals unchanged.')


if __name__=='__main__':main()
