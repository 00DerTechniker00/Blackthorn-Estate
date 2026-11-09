"""Remove floor-standing emergency lamps, preserve anchored decorative lighting.

Call enhance(d,b,air) after the final Y127 translation and access construction.
The bounded light model is deliberately conservative and is no in-game spawn test.
"""
from collections import deque
import hashlib,json
from structure_check import LIGHT,opaque,is_solid

FLOORS=(95,101,107,113,121,127,135,143)
BOUNDS=(-743,-657,95,154,748,832)
D6=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))


def _floor_digest(b):
    rows=[(x,z,b.get((x,95,z))) for x in range(-709,-658) for z in range(767,814)]
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()


def _light_report(b,zeros=None):
    x0,x1,y0,y1,z0,z1=BOUNDS
    def inside(p):return x0<=p[0]<=x1 and y0<=p[1]<=y1 and z0<=p[2]<=z1
    light={};queue=deque()
    for p,(block,state,group) in b.items():
        intensity=LIGHT.get(block,0)
        if block=='redstone_lamp' and 'lit=true' not in state:intensity=0
        if block in ('campfire','soul_campfire') and 'lit=false' in state:intensity=0
        if intensity and inside(p):light[p]=intensity;queue.append(p)
    while queue:
        x,y,z=queue.popleft();value=light[x,y,z]-1
        if value<=0:continue
        for dx,dy,dz in D6:
            p=x+dx,y+dy,z+dz
            if not inside(p) or p in b and opaque(b[p][0]) or light.get(p,0)>=value:continue
            light[p]=value;queue.append(p)
    result={}
    for floor in FLOORS:
        # New carpets occupy the feet cell but have no collision and let light pass.
        def empty(p):return p not in b or b[p][0].endswith('_carpet')
        samples=[]
        for x in range(x0,x1+1):
            for z in range(z0,z1+1):
                if floor<127 and not(-709<=x<=-659 and 767<=z<=813):continue
                if floor==143 and not(-713<=x<=-705 and 782<=z<=798):continue
                block=b.get((x,floor,z))
                if block and is_solid(block[0]) and empty((x,floor+1,z)) and empty((x,floor+2,z)):
                    samples.append(light.get((x,floor+1,z),0))
                    if zeros is not None and floor>=127 and samples[-1]==0 and not block[0].endswith(('_stairs','_slab')):zeros.append((x,floor,z))
        result[str(floor)]={'sampled_floor_cells':len(samples),'minimum_block_light':min(samples,default=0),'zero_light_cells':samples.count(0)}
    return result


def _lamp_audit(b):
    rows=[]
    for (x,y,z),(block,state,group) in sorted(b.items()):
        if block not in ('lantern','soul_lantern'):continue
        if group in ('steglicht','stall_remise') or x<-745 or z>835:continue
        hanging='hanging=true' in state
        anchor=(x,y+1 if hanging else y-1,z);chain=0
        if hanging:
            while b.get(anchor,('',))[0] in ('chain','iron_chain'):
                chain+=1;anchor=(x,anchor[1]+1,z)
        supported=anchor in b
        rows.append({'position':[x,y,z],'block':block,'hanging':hanging,'chain':chain,'anchor':list(anchor),'anchor_block':b.get(anchor,('',))[0],'supported':supported})
    return rows


def enhance(d,b,air):
    digest=_floor_digest(b)
    before=_light_report(b)
    sources=[]
    lamps=[(p,value) for p,value in sorted(b.items()) if value[0]=='lantern' and value[2]=='lichtkorrektur' and 'hanging=false' in value[1]]
    for (x,y,z),value in lamps:
        under=(x,y-1,z);base=b.get(under)
        # Restrict alterations to actual upstairs full floors, never machinery or stairs.
        if y not in (128,136) or not base or not is_solid(base[0]) or base[0].endswith(('_stairs','_slab')):continue
        group=base[2]
        carpet='red_carpet' if group in ('halle','teppiche','vestibuel') else 'gray_carpet' if group in ('kueche','portikus') else 'brown_carpet'
        b.pop((x,y,z));air.add((x,y,z))
        b[under]=('sea_lantern','','v6_beleuchtung_verdeckt');air.discard(under)
        b[x,y,z]=(carpet,'','v6_beleuchtung_verdeckt');air.discard((x,y,z))
        sources.append({'position':[x,y-1,z],'cover':[x,y,z],'cover_block':carpet,'previous_floor':base[0],'context_group':group})
    # Complete dark pockets with the same flush detail, never a new post or floor lamp.
    # Each choice is based on the actual bounded propagation after the previous change.
    removed_count=len(sources)
    # The roof architect provides two actual floor sources. Conceal their faces
    # without moving furniture, the ladder, or the retained gable glass.
    for z in (786,793):
        source=(-709,143,z);cover=(-709,144,z)
        if b.get(source,('',))[0]=='sea_lantern' and cover not in b:
            b[cover]=('brown_carpet','','v6_beleuchtung_verdeckt');air.discard(cover)
            sources.append({'position':list(source),'cover':list(cover),'cover_block':'brown_carpet','previous_floor':'sea_lantern','context_group':b[source][2],'kind':'Dachlesesaal · vorhandene Quelle verdeckt'})
    supplementary=[]
    for attempt in range(40):
        zeros=[];after=_light_report(b,zeros)
        if not zeros:break
        chosen=max(zeros,key=lambda p:sum(q[1]==p[1] and abs(q[0]-p[0])+abs(q[2]-p[2])<=7 for q in zeros))
        x,y,z=chosen;base=b[chosen]
        if y==143:
            ceiling=next((cy for cy in range(147,155) if b.get((x,cy,z)) and is_solid(b[x,cy,z][0]) and not b[x,cy,z][0].endswith(('_stairs','_slab')) and all((x,yy,z) not in b for yy in range(145,cy))),None)
            if ceiling is None:break  # Report remaining darkness rather than inventing a roof anchor.
            source=(x,ceiling,z);cover=(x,ceiling-1,z);original=b[source]
            b[source]=('sea_lantern','','v6_beleuchtung_verdeckt');air.discard(source)
            b[cover]=('dark_oak_trapdoor','facing=north,half=top,open=false,powered=false,waterlogged=false','v6_beleuchtung_verdeckt');air.discard(cover)
            fixture={'position':list(source),'cover':list(cover),'cover_block':'dark_oak_trapdoor','previous_floor':original[0],'context_group':original[2],'kind':'Dachlesesaal · bündige Deckenleuchte'}
            sources.append(fixture);supplementary.append(fixture)
            continue
        cover=(x,y+1,z);carpet='gray_carpet' if not(-735<=x<=-658 and 750<=z<=830) else 'brown_carpet'
        b[chosen]=('sea_lantern','','v6_beleuchtung_verdeckt');air.discard(chosen)
        b[cover]=(carpet,'','v6_beleuchtung_verdeckt');air.discard(cover)
        fixture={'position':list(chosen),'cover':list(cover),'cover_block':carpet,'previous_floor':base[0],'context_group':base[2]}
        sources.append(fixture);supplementary.append(fixture)
    after=_light_report(b)
    audit=_lamp_audit(b)
    result={'title':'Freie Böden und ruhige, verdeckte Raumbeleuchtung','removed_floor_lanterns':removed_count,'supplementary_concealed_sources':len(supplementary),'replaced_lantern_positions':[s['cover'] for s in sources[:removed_count]],'orphaned_chain_positions':[],'concealed_sources':sources,'decorative_lanterns_checked':len(audit),'max_chain':max((r['chain'] for r in audit),default=0),'unanchored_lanterns':[r for r in audit if not r['supported']],'floor_y95_sha256':digest,'block_light_before':before,'block_light_after':after,'limits':['Conservative bounded block-light propagation; no skylight, entity collisions or fluid simulation','Full blocks approximate opacity; daylight and individual mob spawn rules are not simulated','Ceiling lamps and table lamps retain their anchored decorative positions; no new freestanding exterior lamp posts']}
    d['lighting']['concealed_fixtures']=sources
    d['lighting']['estate_review']=result
    check(d,b,result)
    return result


def check(d,b,metadata=None):
    metadata=metadata or d['lighting']['estate_review']
    assert _floor_digest(b)==metadata['floor_y95_sha256'],'Existing Y95 floor changed'
    assert not metadata['unanchored_lanterns'],'Decorative lantern lost its anchor'
    assert metadata['max_chain']<=2,'Overlong decorative suspension'
    for fixture in metadata['concealed_sources']:
        source=tuple(fixture['position']);cover=tuple(fixture['cover'])
        assert b[source][0]=='sea_lantern' and b[cover][0]==fixture['cover_block']
        assert source[1]>95
        if fixture['cover_block'].endswith('_trapdoor'):
            assert -713<=source[0]<=-705 and 782<=source[2]<=798 and cover[1]==source[1]-1 and cover[1]>=146
        else:assert cover[1] in (128,136,144)
    for x in range(-709,-658):
        for z in range(767,781):
            for y in range(122,127):assert (x,y,z) not in b,'Porter north wall obstructed'
    return {'removed_floor_lanterns':metadata['removed_floor_lanterns'],'checked_decorative_lanterns':metadata['decorative_lanterns_checked'],'maximum_chain_length':metadata['max_chain'],'existing_floor_preserved':True,'roof_reading_room':metadata['block_light_after']['143'],'sampled_zero_light_cells':sum(row['zero_light_cells'] for row in metadata['block_light_after'].values())}
