"""Revision 5.26: Dach-Geheimraum mit Redstone-Lesepultschloss, Strukturkorrekturen, Verschönerung außen und innen, Zusatzlicht.

Alle neuen Blöcke stehen auf freien Positionen (geprüft, sonst Abbruch). Ersetzt werden nur:
- die Dachboden-Bodenplatten über der Bibliothek (Halbstufen -> volle Bretter; Deckenunterseite bleibt identisch),
- ein Teil der Deckenplatten für Kolben, Fackel und Lukensockel.
"""
import hashlib
from collections import deque
import structure_check as sc

D6=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
NEW_GROUPS=('dachgeheimraum','dachgeheimraum_technik','fassade_laternen','fassade_beet','teppiche','lichtkorrektur')
WINDOWS=((-705,-704),(-699,-698),(-687,-686),(-681,-680),(-669,-668),(-663,-662))
FACADES=((751,-1,'north'),(829,1,'south'))
SLAB='type=bottom,waterlogged=false'

def noise(x,y,z,salt):
    return int(hashlib.md5(f'{salt}:{x},{y},{z}'.encode()).hexdigest()[:8],16)/0xffffffff

def enhance(d,b):
    previous=d['structure']['enhancements'];air=set(map(tuple,d.get('required_air',[])))
    stats={g:0 for g in NEW_GROUPS};stats.update(replaced=0,chains_fixed=0)
    skipped=[]
    def free(p):return p not in b and p not in air
    def put(p,block,state,group):
        if not free(p):raise ValueError(f'Position belegt: {p} {b.get(p)}')
        b[p]=(block,state,group);stats[group]+=1
    def try_put(p,block,state,group):
        if not free(p):return False
        b[p]=(block,state,group);stats[group]+=1;return True
    def solid_below(p):
        v=b.get((p[0],p[1]-1,p[2]));return bool(v) and sc.is_solid(v[0]) and not v[0].endswith('_slab') or bool(v) and v[0].endswith('_slab') and ('type=top' in v[1] or 'type=double' in v[1])

    # ---------- A) Dach-Geheimraum über der Bibliothek ----------
    # Bibliotheksleiter an der Nordwand, Regalsäule und Schrank mit Lesepult-Schloss.
    for y in range(130,145):
        put((-671,y,774),'bookshelf','','dachgeheimraum_technik')
        put((-671,y,775),'ladder','facing=south,waterlogged=false','dachgeheimraum_technik')
    special={(-670,144,775):('lectern','facing=west,has_book=false,powered=false'),
             (-669,144,775):('comparator','facing=east,mode=compare,powered=false'),
             (-668,144,775):('polished_deepslate',''),
             (-669,144,774):('redstone_block','')}
    for x in range(-670,-667):
        for z in range(774,777):
            for y in range(130,145):
                p=(x,y,z)
                if p in special:put(p,*special[p],'dachgeheimraum_technik')
                else:put(p,'bookshelf','','dachgeheimraum_technik')
    # Kolbenluke in der Deckenebene (Y 145): Luke = vorhandene Halbstufe, wird von der Kolbenspitze gehalten.
    hatch=b.get((-671,145,775))
    if not hatch or hatch[0]!='spruce_slab':raise ValueError('Luke: erwartete Deckenplatte fehlt')
    for p,(blk,st) in {(-670,145,775):('piston_head','facing=west,type=sticky,short=false'),
                       (-669,145,775):('sticky_piston','facing=west,extended=true'),
                       (-668,145,775):('redstone_torch','lit=true')}.items():
        old=b.get(p)
        if not old or old[0]!='spruce_slab':raise ValueError('Deckenplatte fehlt an '+str(p))
        b[p]=(blk,st,'dachgeheimraum_technik');stats['dachgeheimraum_technik']+=1;stats['replaced']+=1
    b[(-671,145,775)]=('spruce_slab',SLAB,'dachgeheimraum_technik')
    put((-669,146,775),'lever','face=floor,facing=north,powered=false','dachgeheimraum_technik')
    # Fußboden des Dachraums: Halbstufen -> volle dunkle Eichenbretter (Unterseite der Decke bleibt gleich).
    room_x=range(-671,-660);room_z=range(776,805)
    for x in room_x:
        for z in room_z:
            p=(x,145,z);old=b.get(p)
            if old and old[0]=='spruce_slab' and old[1].startswith('type=bottom'):
                b[p]=('dark_oak_planks','','dachgeheimraum');stats['dachgeheimraum']+=1;stats['replaced']+=1
    for z in (775,):
        for x in (-667,-666,-665,-664,-663,-662,-661):
            p=(x,145,z);old=b.get(p)
            if old and old[0]=='spruce_slab' and old[1].startswith('type=bottom'):
                b[p]=('dark_oak_planks','','dachgeheimraum');stats['dachgeheimraum']+=1;stats['replaced']+=1
    # Einrichtung (Y 146 ff.)
    for z in range(777,792):
        for y in (146,147):
            for x in (-671,-661):
                if z in range(777,782) or z in range(783,792):
                    if z in (780,781,783,784) and x in(-671,-661) and y==146:continue
                    try_put((x,y,z),'bookshelf','','dachgeheimraum')
    for x,face in ((-671,'east'),(-661,'west')):
        try_put((x,146,780),'chest',f'facing={face},type=single,waterlogged=false','dachgeheimraum')
        try_put((x,146,781),'barrel','facing=up,open=false','dachgeheimraum')
        try_put((x,146,783),'barrel','facing=up,open=false','dachgeheimraum')
        try_put((x,146,784),'chest',f'facing={face},type=single,waterlogged=false','dachgeheimraum')
    for z in range(793,804):
        for y in (146,147):
            for x in (-671,-661):
                try_put((x,y,z),'bookshelf','','dachgeheimraum')
    for x in (-668,-664):
        try_put((x,146,787),'cartography_table','','dachgeheimraum')
        try_put((x,147,787),'candle','candles=2,lit=true,waterlogged=false','dachgeheimraum')
    try_put((-668,146,789),'lectern','facing=east,has_book=false,powered=false','dachgeheimraum')
    try_put((-664,146,789),'lectern','facing=west,has_book=false,powered=false','dachgeheimraum')
    # Sternwarte: Podest mit Zaubertisch und Standleuchten
    for x in range(-668,-663):
        for z in range(797,802):
            try_put((x,146,z),'polished_blackstone_bricks','','dachgeheimraum')
    try_put((-666,147,799),'enchanting_table','','dachgeheimraum')
    for x,z in ((-668,797),(-664,797),(-668,801),(-664,801)):
        try_put((x,147,z),'lantern','hanging=false,waterlogged=false','dachgeheimraum')
    # Kronleuchter an der Firstlinie (Kette + Laterne, Anker: Dachziegel Y 151)
    for z in (779,785,791,797,803):
        if (-666,151,z) in b and free((-666,150,z)) and free((-666,149,z)):
            put((-666,150,z),'iron_chain','axis=y,waterlogged=false','dachgeheimraum')
            put((-666,149,z),'lantern','hanging=true,waterlogged=false','dachgeheimraum')
    # Läufer im Dachraum
    for z in range(776,804):
        for x,col in ((-667,'light_gray_carpet'),(-666,'blue_carpet'),(-665,'light_gray_carpet')):
            p=(x,146,z)
            if free(p) and b.get((x,145,z),('',))[0]=='dark_oak_planks':put(p,col,'','teppiche')

    # ---------- B) Strukturkorrektur: Kronleuchterketten der Bibliothek erreichen die Decke ----------
    for x in (-670,-664):
        for z in (781,797):
            p=(x,144,z)
            if free(p) and b.get((x,143,z),('',))[0]=='iron_chain' and b.get((x,145,z),('',))[0] in ('spruce_slab','dark_oak_planks'):
                b[p]=('iron_chain','axis=y,waterlogged=false','bibliothek');stats['chains_fixed']+=1

    # ---------- C) Außen: Konsollaternen und Beete an Nord- und Südfassade ----------
    for wall_z,out,facing in FACADES:
        oz=wall_z+out;side='south' if out<0 else 'north'
        fence=','.join(f'{s}={"true" if s==side else "false"}' for s in ('east','north','south','west'))+',waterlogged=false'
        for x in (-701,-683,-665):
            for fy,ly in ((135,134),(143,142)):
                if free((x,fy,oz)) and free((x,ly,oz)) and b.get((x,fy,wall_z),('',))[0] in('stone_bricks','mossy_stone_bricks','cracked_stone_bricks'):
                    put((x,fy,oz),'spruce_fence',fence,'fassade_laternen')
                    put((x,ly,oz),'lantern','hanging=true,waterlogged=false','fassade_laternen')
                else:skipped.append(('laterne',x,fy,oz))
        bed_z=oz+out*2
        for x in range(-714,-655):
            ground=b.get((x,128,bed_z))
            if not ground or ground[0]!='grass_block':continue
            r=noise(x,0,bed_z,'bed')
            if r<0.55 and free((x,129,bed_z)):
                kind=('allium','cornflower','oxeye_daisy','flowering_azalea','azalea')[int(noise(x,1,bed_z,'kind')*5)]
                try_put((x,129,bed_z),kind,'','fassade_beet')
            hg=b.get((x,128,bed_z+out))
            if noise(x,2,bed_z,'hedge')<0.18 and hg and hg[0]=='grass_block':
                try_put((x,129,bed_z+out),'azalea_leaves','distance=7,persistent=true,waterlogged=false','fassade_beet')

    # ---------- D) Innen: Teppiche in der Großen Halle und der Bibliothek ----------
    def rug(x0,x1,z0,z1,y,rings,inner):
        for x in range(x0,x1+1):
            for z in range(z0,z1+1):
                ring=min(x-x0,x1-x,z-z0,z1-z)
                col=rings[ring] if ring<len(rings) else inner
                p=(x,y,z)
                if free(p) and solid_below(p):try_put(p,col,'','teppiche')
    rug(-706,-686,780,786,130,('black_carpet','light_gray_carpet'),'blue_carpet')
    rug(-706,-688,794,802,130,('black_carpet','light_gray_carpet'),'blue_carpet')
    for p in ((-696,130,783),(-697,130,783),(-695,130,783),(-696,130,782),(-696,130,784)):
        if p in b and b[p][2]=='teppiche':b[p]=('white_carpet','','teppiche')
    for x,col in ((-667,'brown_carpet'),(-666,'green_carpet'),(-665,'brown_carpet')):
        for z in range(777,806):
            p=(x,130,z)
            if free(p) and solid_below(p):try_put(p,col,'','teppiche')

    # ---------- E) Lichtprüfung und Zusatzlicht gegen Monsterspawn ----------
    rooms=[r for r in d['rooms'] if 'Plateauzufahrt' not in r['name']]
    doors={p for p,v in b.items() if v[0].endswith('_door') and 'half=lower' in v[1]}
    stairs_or_ladder={p for p,v in b.items() if v[0].endswith('_stairs') or v[0]=='ladder'}
    level={};dq=deque()
    def spread(dq):
        while dq:
            p=dq.popleft();l=level[p]
            if l<=1:continue
            for dx,dy,dz in D6:
                q=(p[0]+dx,p[1]+dy,p[2]+dz)
                if q in b and sc.opaque(b[q][0]):continue
                if level.get(q,0)<l-1:level[q]=l-1;dq.append(q)
    for p,(blk,st,g) in b.items():
        l=sc.LIGHT.get(blk,0)
        if blk=='redstone_lamp' and 'lit=true' not in st:l=0
        if blk=='candle':l=3*int(sc.props(st).get('candles','1')) if 'lit=true' in st else 0
        if blk in('campfire','soul_campfire') and 'lit=false' in st:l=0
        if l>0:level[p]=l;dq.append(p)
    spread(dq)
    def standable(p):
        x,y,z=p;below=b.get((x,y-1,z))
        return p not in b and (x,y+1,z) not in b and below is not None and sc.is_solid(below[0]) and not below[0].endswith('_trapdoor')
    def in_rooms(p):
        return any(r['x'][0]<=p[0]<=r['x'][1] and r['y'][0]<=p[1]<=r['y'][1] and r['z'][0]<=p[2]<=r['z'][1] for r in rooms)
    cells=set()
    for r in rooms:
        for x in range(r['x'][0],r['x'][1]+1):
            for y in range(r['y'][0],r['y'][1]+1):
                for z in range(r['z'][0],r['z'][1]+1):
                    if standable((x,y,z)):cells.add((x,y,z))
    def near(p,pool,rad=1):
        return any((p[0]+i,p[1]+j,p[2]+k) in pool for i in range(-rad,rad+1) for j in (-1,0,1) for k in range(-rad,rad+1))
    dark_before=sum(1 for p in cells if level.get(p,0)==0)
    def candidate_ok(c,need_wall=True):
        if not free(c) or not standable(c):return False
        if near(c,doors,1) or near(c,stairs_or_ladder,1):return False
        if not need_wall:return True
        return any((c[0]+dx,c[1],c[2]+dz) in b and sc.opaque(b[(c[0]+dx,c[1],c[2]+dz)][0]) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))
    placed=0;unresolved=[]
    dark={p for p in cells if level.get(p,0)==0}
    while dark:
        p=min(dark,key=lambda c:(c[1],c[0],c[2]))
        best=None;score=-1
        for rad,need_wall in ((4,True),(6,False)):
            for dx in range(-rad,rad+1):
                for dz in range(-rad,rad+1):
                    c=(p[0]+dx,p[1],p[2]+dz)
                    if not candidate_ok(c,need_wall):continue
                    gain=sum(1 for q in dark if abs(q[0]-c[0])<=6 and abs(q[2]-c[2])<=6 and q[1]==c[1])
                    if gain>score:score=gain;best=c
            if best is not None:break
        if best is None:
            if candidate_ok(p,False):best=p
            else:
                unresolved.append(p);dark.discard(p);continue
        b[best]=('lantern','hanging=false,waterlogged=false','lichtkorrektur');stats['lichtkorrektur']+=1;placed+=1
        level[best]=15;dq.append(best);spread(dq)
        dark={q for q in dark if level.get(q,0)==0}
    dark_after=sum(1 for p in cells if level.get(p,0)==0)

    d['_clearance_air']=[list(p) for p in sorted(air)]
    report={'cells_checked':len(cells),'dark_before':dark_before,'dark_after':dark_after,'lanterns_added':placed,'unresolved':[list(p) for p in unresolved[:20]],'skipped_facade_lanterns':len(skipped)}
    features=[
        {'group':'dachgeheimraum_technik','name':'Dach-Geheimraum mit Lesepultschloss','description':'Bibliotheksleiter und Regalschrank an der Nordwand der Bibliothek, vom Erdgeschossboden bis zur Decke. Am Leiterkopf liegt ein Lesepult: Ein Buch auf die letzte Seite blättern, dann gibt der Komparator Stärke 15 und die Fackel schaltet ab. Der Kolben zieht die Deckenluke zurück. Der Hebel im Dachraum riegelt wieder zu.'},
        {'group':'dachgeheimraum','name':'Dachraum: Kartenkammer und Sternwarte','description':f'Dunkler Eichenboden, Läufer, Regalwände, Kartentische, Lesepulte, Truhen und Fässer, Podest mit Zaubertisch, Kerzen und fünf Kronleuchter an der Firstlinie.'},
        {'group':'fassade_laternen','name':'Konsollaternen an Nord- und Südfassade','description':f'{stats["fassade_laternen"]//2} Fichtenzaun-Konsolen mit hängenden Laternen zwischen den Fensterpaaren, beide Geschosse.'},
        {'group':'fassade_beet','name':'Beete vor der Fassade','description':f'{stats["fassade_beet"]} Blumen und Azaleenbüsche in Beeten vor der Nord- und Südfassade.'},
        {'group':'teppiche','name':'Teppiche und Läufer','description':f'{stats["teppiche"]} Teppiche: zwei gemusterte Teppiche in der Großen Halle, Läufer in der Bibliothek und im Dachraum.'},
        {'group':'lichtkorrektur','name':'Zusatzlicht gegen Monsterspawn','description':f'Lichtprüfung über {len(cells)} begehbare Bodenzellen in den Räumen: {dark_before} Zellen ohne Blocklicht. {placed} Standlaternen an Wänden und in Ecken beheben das; danach {dark_after} dunkle Zellen.'},
        {'group':'bibliothek','name':'Kronleuchterketten bis zur Decke','description':f'{stats["chains_fixed"]} Ketten in der Bibliothek hatten ein Loch zur Decke; jetzt durchgehend.'}]+previous['features']
    return {**previous,'title':'Dach-Geheimraum, Strukturprüfung und Verschönerung','features':features,'secret_room':{'entry':[-671,130,776],'hatch':[-671,145,775],'lectern':[-670,144,775],'piston':[-669,145,775],'torch':[-668,145,775],'lever':[-669,146,775],'room':{'x':[-671,-661],'y':[146,149],'z':[776,804]}},'light_report':report,'enhance_stats':stats,
        'limits':'Das Lesepultschloss und die Kolbenluke sind nur geometrisch geprüft, nicht im Spiel. Das Buch (mindestens zwei Seiten) legt man selbst ins Lesepult. Das Licht rechnet nur Blocklicht und lässt Wandmaterial aus der Bestandswelt außer Acht. '+previous['limits']}
