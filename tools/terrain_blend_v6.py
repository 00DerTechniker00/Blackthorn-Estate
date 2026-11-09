"""Blend only the new two-block lowering seam; shore up the small obsolete west trench."""
from collections import deque,defaultdict
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
DIRECTIONS=((1,0),(-1,0),(0,1),(0,-1))

def enhance(d,b,air):
    T=d['terrain'];x0,x1,z0,z1=T['bounds'];H=T['target_heights'];O=T['heights']
    seed=json.loads((ROOT/'tools/seeds/revision-5.26/blueprint.json').read_text())['terrain'];S=seed['target_heights']
    original=[row[:] for row in O];mask={(x,z) for x,z,_ in T['structure_clearance']}
    def height(grid,p):x,z=p;return grid[z-z0][x-x0]
    def bounds(p):x,z=p;return x0<=x<=x1 and z0<=z<=z1
    objects=set()
    for (x,y,z),(bid,state,group) in b.items():
        if bounds((x,z)) and not group.startswith('terraform_') and y>=height(H,(x,z)):
            objects.add((x,z))
    def eligible(p):
        if not bounds(p) or p in mask or p in objects:return False
        x,z=p;h=height(H,p)
        return h>=108 and h==height(S,p)==height(O,p) and T['target_surface_blocks'][z-z0][x-x0] in ('grass_block','dirt') and T['surface_blocks'][z-z0][x-x0] in ('grass_block','dirt')
    starts=set()
    for z in range(z0,z1+1):
        for x in range(x0,x1+1):
            p=x,z
            if height(H,p)!=height(S,p)-2:continue
            for dx,dz in DIRECTIONS:
                q=x+dx,z+dz
                if eligible(q) and abs(height(S,p)-height(S,q))<=1 and height(H,q)-height(H,p)>=2:starts.add(q)
    dist={p:0 for p in starts};queue=deque(sorted(starts))
    while queue:
        p=queue.popleft()
        if dist[p]>=8:continue
        for dx,dz in DIRECTIONS:
            q=p[0]+dx,p[1]+dz
            if q in dist or not eligible(q) or abs(height(S,p)-height(S,q))>1:continue
            dist[q]=dist[p]+1;queue.append(q)
    work={(r[0],r[1]):r for r in T['work']};changes=[];underfill=[];removed=0;filled=0;cuts=defaultdict(list)
    for x,z,a,c in T['cut_spans']:cuts[x,z].append((a,c))
    def record(x,z,y,name,mat):
        H[z-z0][x-x0]=y;T['target_surface_blocks'][z-z0][x-x0]=mat
        row=work.get((x,z))
        if row is None:
            row=[x,z,height(O,(x,z)),y,0,0,name,mat];T['work'].append(row);work[x,z]=row
        row[3]=y;row[4]=max(0,row[2]-y);row[5]=max(0,y-row[2]);row[6]=name;row[7]=mat
    for (x,z),distance in sorted(dist.items()):
        drop=2 if distance<=1 else 1 if distance<=5 else 0
        if not drop:continue
        old=height(H,(x,z));new=old-drop
        for y in range(new+1,old+1):b.pop((x,y,z),None);air.add((x,y,z));removed+=1
        b[x,new,z]=('grass_block','','terraform_oberflaeche');air.discard((x,new,z))
        record(x,z,new,'Sanfter Plateauanschluss','grass_block');cuts[x,z].append((new+1,old));changes.append([x,z,old,new,distance])
    # The old west service trench is not part of the new cellar. Its real void
    # directly below the house needs local support, not a larger landscape berm.
    support=json.loads((ROOT/'tools/seeds/revision-6.0/west_foundation_support.json').read_text())
    bases={(x,z):y for x,z,y in support['columns']}
    for x in range(-715,-710):
        for z in range(790,815):
            old=height(H,(x,z))
            if (x,z) not in mask or old!=118:continue
            count=0;start=min(old+1,bases[x,z]+1)
            for y in range(start,127):
                p=x,y,z
                if p not in b or b[p][2].startswith('terraform_'):
                    value=('dirt','','terraform_auffuellung')
                    if b.get(p)!=value:count+=1;filled+=1
                    b[p]=value
                air.discard(p)
            # Keep the natural earth hidden directly beneath the existing floor.
            record(x,z,126,'Lokale Unterfütterung Westfundament',b[x,126,z][0]);underfill.append([x,z,old,126,count,start])
            new_spans=[]
            for a,c in cuts[x,z]:
                if a<start:new_spans.append((a,min(c,start-1)))
                if c>126:new_spans.append((max(a,127),c))
            cuts[x,z]=new_spans
    merged=[]
    for (x,z),spans in sorted(cuts.items()):
        rows=[]
        for a,c in sorted(spans):
            if a>c:continue
            if rows and a<=rows[-1][1]+1:rows[-1][1]=max(c,rows[-1][1])
            else:rows.append([a,c])
        merged.extend([x,z,a,c] for a,c in rows)
    T['cut_spans']=merged
    assert T['heights']==original
    result={'transition_width':8,'start_columns':len(starts),'softened_columns':len(changes),'cut_blocks':removed,'band_fill_blocks':0,'changes':changes,'underpinning_columns':underfill,'underpinning_blocks':filled,'support_source_sha256':support['source_sha256']}
    check(d,b,result)
    return result

def check(d,b,metadata=None):
    m=metadata or d['structure']['v6']['refinement']['terrain_blend'];T=d['terrain'];x0,_,z0,_=T['bounds']
    for x,z,old,new,distance in m['changes']:
        assert old-new in (1,2) and distance<=5
        assert T['target_heights'][z-z0][x-x0]==new and b[x,new,z][0]=='grass_block'
        for y in range(new+1,old+1):assert (x,y,z) not in b
    for x,z,old,new,count,start in m['underpinning_columns']:
        assert -715<=x<=-711 and 790<=z<=814 and new==126
        assert T['target_heights'][z-z0][x-x0]==126
        for y in range(start,127):assert (x,y,z) in b
    return {'softened_columns':len(m['changes']),'local_cut_blocks':m['cut_blocks'],'landscape_band_fill':0,'underpinning_columns':len(m['underpinning_columns']),'underpinning_blocks':m['underpinning_blocks']}
