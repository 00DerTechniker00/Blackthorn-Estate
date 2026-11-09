"""Strukturprüfung des Blockmodells: schwebende Bauteile, fehlende Halterungen, Lichtverhältnisse."""
from collections import Counter,deque

D6=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
FACING={'north':(0,0,-1),'south':(0,0,1),'east':(1,0,0),'west':(-1,0,0)}
NONSUPPORT_SUFFIX=('_carpet','_banner','_sign','_button','_pressure_plate','_pane','_bars','_door','_trapdoor','_fence_gate','_candle','_hanging_sign')
NONSUPPORT={'air','water','bubble_column','ladder','vine','lantern','soul_lantern','iron_chain','chain','torch','wall_torch','soul_torch','soul_wall_torch','redstone_wire','redstone_torch','redstone_wall_torch','lever','repeater','comparator','flower_pot','lightning_rod','end_rod','piston_head','campfire','soul_campfire','cake','iron_bars','glass_pane','allium','oxeye_daisy','cornflower','azalea','flowering_azalea','short_grass','tall_grass','fern','large_fern','sweet_berry_bush','moss_carpet','tripwire','tripwire_hook'}
LIGHT={'lantern':15,'soul_lantern':10,'torch':14,'wall_torch':14,'soul_torch':10,'soul_wall_torch':10,'redstone_lamp':15,'sea_lantern':15,'glowstone':15,'shroomlight':15,'end_rod':14,'campfire':15,'soul_campfire':10,'ochre_froglight':15,'verdant_froglight':15,'pearlescent_froglight':15,'jack_o_lantern':15,'lava':15,'magma_block':3,'redstone_torch':7,'redstone_wall_torch':7,'beacon':15,'enchanting_table':7,'respawn_anchor':0,'candle':3}

def props(state):
    return dict(p.split('=',1) for p in state.split(',') if '=' in p)

def is_solid(block):
    return block not in NONSUPPORT and not block.endswith(NONSUPPORT_SUFFIX) and not block.startswith('potted_') and not block.endswith(('_slab','_stairs')) or block.endswith(('_slab','_stairs'))

def opaque(block):
    return is_solid(block) and not block.endswith(('_slab','_stairs','_fence','_wall','glass','_leaves','_stained_glass','tinted_glass')) and block not in ('glass','ice','barrier','iron_bars','chain','iron_chain','lantern')

def check(occ,outdoor_groups,air=frozenset(),limit_rows=40):
    house=lambda g: g not in outdoor_groups and not g.startswith('terraform_')
    findings={}
    # 1) schwebende Bauteile im Haus: alles Nicht-Hausmaterial und Fundament (y<=128) gilt als Boden
    solids={p for p,v in occ.items() if is_solid(v[0])}
    grounded=set();dq=deque()
    for p in solids:
        v=occ[p]
        if (not house(v[2])) or p[1]<=128: grounded.add(p);dq.append(p)
    while dq:
        x,y,z=dq.popleft()
        for dx,dy,dz in D6:
            q=(x+dx,y+dy,z+dz)
            if q in solids and q not in grounded: grounded.add(q);dq.append(q)
    floating=solids-grounded;seen=set();comps=[]
    for p in floating:
        if p in seen:continue
        st=[p];seen.add(p);c=[]
        while st:
            a=st.pop();c.append(a)
            for dx,dy,dz in D6:
                q=(a[0]+dx,a[1]+dy,a[2]+dz)
                if q in floating and q not in seen:seen.add(q);st.append(q)
        comps.append(c)
    comps.sort(key=len,reverse=True)
    findings['floating']=[{'blocks':len(c),'x':[min(p[0] for p in c),max(p[0] for p in c)],'y':[min(p[1] for p in c),max(p[1] for p in c)],'z':[min(p[2] for p in c),max(p[2] for p in c)],'groups':sorted({occ[p][2] for p in c})[:3],'types':[k for k,_ in Counter(occ[p][0] for p in c).most_common(3)]} for c in comps]
    # 2) Halterungen
    def blk(p):return occ.get(p,('air','',''))[0]
    def ok_face(p,d):
        q=(p[0]+d[0],p[1]+d[1],p[2]+d[2]);b=blk(q);return is_solid(b) and not b.endswith(('_slab','_stairs')) or b.endswith(('_slab','_stairs')) and False or b in('bookshelf','chiseled_bookshelf')
    unsupported=[]
    for p,(b,s,g) in occ.items():
        x,y,z=p;pr=props(s);below=(x,y-1,z);above=(x,y+1,z);bad=None
        if b in ('wall_torch','soul_wall_torch','redstone_wall_torch'):
            f=FACING.get(pr.get('facing'));
            if f and not ok_face(p,(-f[0],0,-f[2])):bad='Wandfackel ohne Wand'
        elif b in ('torch','soul_torch','redstone_torch','repeater','comparator','redstone_wire','lever') and (b!='lever' or pr.get('face')=='floor'):
            bb=blk(below)
            if not(is_solid(bb) or bb in('hopper','observer')) :bad=f'{b} ohne tragenden Block'
            elif bb.endswith(('_slab',)) and 'type=top' not in occ[below][1] and 'type=double' not in occ[below][1] :bad=f'{b} auf Halbstufe'
        elif b=='ladder':
            f=FACING.get(pr.get('facing'))
            if f and not ok_face(p,(-f[0],0,-f[2])):bad='Leiter ohne Rückwand'
        elif b.endswith('_door') and pr.get('half')=='lower':
            if not is_solid(blk(below)) and blk(below) not in('air',) : pass
            if blk(below)=='air' or blk(below)=='water':bad='Tür ohne Boden'
        elif b in ('lantern','soul_lantern'):
            if pr.get('hanging')=='true':
                ab=blk(above)
                if not(is_solid(ab) or ab in('iron_chain','chain','iron_bars') or ab.endswith('_fence')):bad='hängende Laterne ohne Halt'
            elif blk(below)=='air':bad='stehende Laterne ohne Boden'
        elif b in ('iron_chain','chain'):
            ab,bw=blk(above),blk(below)
            if pr.get('axis','y')=='y' and not(is_solid(ab) or ab in('iron_chain','chain','lantern','iron_bars','soul_lantern') or ab.endswith('_fence')):bad='Kette ohne Halt'
        elif b.endswith('_carpet') and blk(below)=='air':bad='Teppich ohne Boden'
        elif b=='vine':
            if not any(is_solid(blk((x+dx,y,z+dz))) for dx,_,dz in D6 if dy_ok if False) if False else False:pass
        if bad:unsupported.append({'position':[x,y,z],'block':b,'group':g,'problem':bad})
    findings['unsupported']=unsupported
    # 3) Licht (Blocklicht, Ausbreitung ohne undurchsichtige Blöcke)
    level={};dq=deque()
    for p,(b,s,g) in occ.items():
        l=LIGHT.get(b,0)
        if b=='redstone_lamp' and 'lit=true' not in s:l=0
        if b in('campfire','soul_campfire') and 'lit=false' in s:l=0
        if b in('lantern','soul_lantern'):pass
        if l>0:level[p]=l;dq.append(p)
    while dq:
        p=dq.popleft();l=level[p]
        if l<=1:continue
        for dx,dy,dz in D6:
            q=(p[0]+dx,p[1]+dy,p[2]+dz)
            if q in occ and opaque(occ[q][0]):continue
            if level.get(q,0)<l-1:level[q]=l-1;dq.append(q)
    findings['light']=level
    return findings


PASSABLE_SUFFIX=('_carpet','_door','_trapdoor','_button','_sign','_banner','_fence_gate')
PASSABLE={'air','ladder','lever','vine','flower_pot','allium','cornflower','oxeye_daisy','azalea','flowering_azalea','redstone_wire','iron_chain','water','bubble_column','lantern','candle','comparator','repeater','redstone_torch','torch','wall_torch','piston_head'}
SMALL={'lantern','candle','comparator','repeater','redstone_torch','torch','wall_torch','piston_head','water','bubble_column'}

def reachability(occ,rooms,start_x_range=range(-760,-735),start_z=790,start_y=130):
    """Begehbarkeit vom Hauptportal: Gehen, Stufen von einem Block, Fallen bis drei Blöcke, Leitern, geschlossene Türen."""
    def passable(b):return b in PASSABLE or b.endswith(PASSABLE_SUFFIX)
    def free(p):
        v=occ.get(p);return v is None or passable(v[0]) and v[0] not in SMALL
    def supported(p):
        v=occ.get((p[0],p[1]-1,p[2]))
        if v and not passable(v[0]):return True
        c=occ.get(p);return bool(c and c[0]=='ladder')
    start=next((x,start_y,start_z) for x in start_x_range if free((x,start_y,start_z)) and free((x,start_y+1,start_z)) and supported((x,start_y,start_z)))
    seen={start};dq=deque([start])
    while dq:
        x,y,z=dq.popleft();cur=occ.get((x,y,z));on_l=bool(cur and cur[0]=='ladder')
        cand=[(x+dx,y+dy,z+dz) for dx,dz in((1,0),(-1,0),(0,1),(0,-1)) for dy in (0,1,-1,-2,-3)]
        if on_l:cand+=[(x,y+1,z),(x,y-1,z)]
        for q in cand:
            if q in seen or not free(q) or not free((q[0],q[1]+1,q[2])):continue
            if q[1]==y+1 and (q[0]!=x or q[2]!=z) and not free((x,y+2,z)):continue
            vert=(q[0]==x and q[2]==z)
            if not supported(q) and not (vert and (on_l or q[1]==y+1)):continue
            seen.add(q);dq.append(q)
    rows=[]
    for r in rooms:
        cells=[(x,y,z) for x in range(r['x'][0],r['x'][1]+1) for y in range(r['y'][0],r['y'][1]+1) for z in range(r['z'][0],r['z'][1]+1)
               if (x,y,z) not in occ and (x,y+1,z) not in occ and (x,y-1,z) in occ and not passable(occ[(x,y-1,z)][0])]
        rows.append({'room':r['name'],'cells':len(cells),'reached':sum(1 for c in cells if c in seen)})
    return {'start':list(start),'reached_cells':len(seen),'rooms':rows}
