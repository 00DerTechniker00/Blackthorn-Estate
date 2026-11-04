"""Replace legacy floor-light spam with a deliberate, attached lighting layout."""
from collections import Counter

LAMPS={'lantern','soul_lantern'}
CHAINS={'chain','iron_chain'}


def support(record,standing=False):
    if not record:return False
    bid,st,g=record
    if bid.endswith('_slab'):
        return 'type=double' in st or ('type=top' in st if standing else 'type=bottom' in st)
    if bid.endswith(('_stairs','_door','_sign','_carpet','_bed','_button','_torch')):return False
    if bid in LAMPS|CHAINS|{'water','hopper','chest','waxed_copper_chest','comparator','repeater','redstone_wire','lever','brewing_stand','flower_pot','lectern','composter','cauldron','anvil','grindstone','stonecutter'}:return False
    return True


def refine(d,b):
    original=b.copy();removed=0;added=0;reasons={}
    # The old auto-light group includes 195 floor fixtures and long curtain-like chains.
    for (x,y,z),(bid,st,g) in list(b.items()):
        if bid not in LAMPS or g!='beleuchtung':continue
        b.pop((x,y,z));removed+=1;reasons[x,y,z]='Automatisch ergänzte Boden-/Langkettenleuchte entfernt'
        yy=y+1
        while b.get((x,yy,z),('','',''))[0] in CHAINS:
            if b[x,yy,z][2]!='beleuchtung':break
            b.pop((x,yy,z));yy+=1
        below=b.get((x,y-1,z))
        if below and below[2]=='beleuchtung' and below[0].endswith('_fence'):b.pop((x,y-1,z))
    # Remove abandoned vertical auto chains, but retain chandelier arms and their chains.
    columns={}
    for (x,y,z),(bid,st,g) in b.items():
        if bid in CHAINS and g=='beleuchtung':columns.setdefault((x,z),[]).append(y)
    for (x,z),ys in columns.items():
        ys=sorted(ys);segments=[];current=[]
        for y in ys:
            if current and y!=current[-1]+1:segments.append(current);current=[]
            current.append(y)
        if current:segments.append(current)
        for segment in segments:
            end=b.get((x,segment[0]-1,z))
            if not end:
                for y in segment:b.pop((x,y,z),None)
    floor_lights=[]
    for (x,y,z),(bid,st,g) in list(b.items()):
        if bid in LAMPS and 'hanging=true' not in st and y in (106,114,122,130,138):
            b.pop((x,y,z));floor_lights.append((x,y,z));removed+=1
            reasons[x,y,z]='Leuchte aus der begehbaren Bodenebene entfernt'
    def near(x,y,z):
        return any(bid in LAMPS and abs(yy-y)<=2 and (xx-x)**2+(zz-z)**2<16 for (xx,yy,zz),(bid,st,g) in b.items())
    def pendant(x,y,z,zone):
        nonlocal added
        if (x,y,z) in b or near(x,y,z):return False
        yy=y+1
        while yy<=y+3 and (x,yy,z) not in b:yy+=1
        if yy>y+3 or not support(b.get((x,yy,z))):return False
        b[x,y,z]=('lantern','hanging=true,waterlogged=false','beleuchtung')
        for h in range(y+1,yy):b[x,h,z]=('iron_chain','axis=y,waterlogged=false','beleuchtung')
        reasons[x,y,z]=zone;added+=1;return True
    for x,y,z in floor_lights:pendant(x,y+4,z,'Ehemalige Bodenleuchte · jetzt Deckenmontage')
    # Main basement circulation: above head height, avoiding every existing machine.
    for floor in (105,113,121):
        for x in (-704,-695,-686,-677,-668,-659):
            for shift in (0,1,-1,2,-2):
                if pendant(x+shift,floor+5,790,f'Kellergang · Boden Y={floor}'):break
    # Dedicated golem room had lost its lights when the machinery was rebuilt.
    for x in (-702,-690,-678):
        for z in (773,781):pendant(x,126,z,'Kupfergolem-Halle')
    # Six task lights in the bulk maintenance aisle, below the ceiling and above paths.
    for module in d['storage_system']['bulk']:
        x,y,z=module['loose']
        for shift in (0,1,-1,2,-2):
            if pendant(x+shift,127,z+1,'Bulk-Wartungsgang'):break
    # Two compact pendants per residence; existing chandeliers remain the main fixtures.
    for room in d['rooms']:
        if room['group'] not in ('res1','res2','res3','res4','res5','res6'):continue
        cx=(room['x'][0]+room['x'][1])//2;cz=(room['z'][0]+room['z'][1])//2
        for x,z in [(room['x'][0]+3,cz),(room['x'][1]-3,cz-4)]:
            for dx,dz in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
                if pendant(x+dx,134,z+dz,room['name']+' · EG'):break
    fixtures=[]
    for (x,y,z),(bid,state,g) in sorted(b.items(),key=lambda a:(a[0][1],a[0][2],a[0][0])):
        if bid not in LAMPS:continue
        hanging='hanging=true' in state;yy=y+1 if hanging else y-1;chain=0
        while hanging and b.get((x,yy,z),('','',''))[0] in CHAINS:yy+=1;chain+=1
        anchor=b.get((x,yy,z));assert support(anchor,not hanging),f'Invalid support for {x,y,z}: {anchor}'
        level='Keller 3' if y<=112 else 'Keller 2' if y<=120 else 'Keller 1' if y<=128 else 'EG / Außen' if y<=137 else 'OG / Halle'
        fixtures.append(dict(id=f'L{len(fixtures)+1:03d}',x=x,y=y,z=z,block=bid,group=g,level=level,
            hanging=hanging,chain=chain,anchor=[x,yy,z],anchor_block=anchor[0],
            kind='Deckenleuchte' if hanging else 'Sockel-/Möbelleuchte',
            source=reasons.get((x,y,z),'Bestehende geplante Leuchte'),checked=True))
    assert not any(not f['hanging'] and f['group']=='beleuchtung' for f in fixtures)
    assert max((f['chain'] for f in fixtures),default=0)<=2
    d['lighting']=dict(fixtures=fixtures,total=len(fixtures),previous_total=sum(r[0] in LAMPS for r in original.values()),
        auto_removed=removed,new_pendants=added,max_chain=max(f['chain'] for f in fixtures),
        attachment_checked=True,light_simulated=False,
        note='Originale Kronleuchter und Terrassenleuchten erhalten; automatische Bodenleuchten ersetzt. Keine Licht-/Spawn-Simulation.')
    return b
