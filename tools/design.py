"""5.9 local architectural edits, storage assemblies and exact 180-degree rotation."""
import math
from collections import Counter

PIVOT=(-690,790)
ROTATE={'north':'south','south':'north','east':'west','west':'east'}


def position(p):return [-1380-p[0],p[1],1580-p[2]]


def state180(state):
    out={}
    for part in state.split(','):
        if '=' not in part:continue
        key,value=part.split('=')
        if key=='facing':value=ROTATE.get(value,value)
        if key=='rotation':value=str((int(value)+8)%16)
        out[ROTATE.get(key,key)]=value
    return ','.join(f'{key}={value}' for key,value in out.items())


def metadata180(obj,key=''):
    if isinstance(obj,list):
        if key in ('containers','bins','route','supports'):
            return [position(p) for p in obj]
        if key in ('front','active_box','dispenser','piston','extract','spawn','loose','empty_supply','catch','start','end','point'):
            return position(obj)
        return [metadata180(v) for v in obj]
    if not isinstance(obj,dict):return obj
    result={k:metadata180(v,k) for k,v in obj.items()}
    if isinstance(obj.get('x'),(int,float)) and isinstance(obj.get('z'),(int,float)):
        result['x']=-1380-obj['x'];result['z']=1580-obj['z']
    elif isinstance(obj.get('x'),list) and isinstance(obj.get('z'),list):
        result['x']=sorted(-1380-v for v in obj['x']);result['z']=sorted(1580-v for v in obj['z'])
    return result


def design(d,b):
    # Earthworks are recomputed against the unchanged original world, never rotated.
    b={p:r for p,r in b.items() if not r[2].startswith('terraform') and r[2] not in ('zufahrt','sockel')}
    def put(x,y,z,bid,st='',g='fassade'):b[x,y,z]=(bid,st,g)
    def clear(x0,x1,y0,y1,z0,z1):
        for x,y,z in list(b):
            if x0<=x<=x1 and y0<=y<=y1 and z0<=z<=z1:del b[x,y,z]
    def hopper(x,y,z,f='north',g='lager_technik'):put(x,y,z,'hopper',f'facing={f},enabled=true',g)
    def solid(x,y,z,g='lager_technik'):put(x,y,z,'polished_andesite','',g)
    def dust(x,y,z):solid(x,y-1,z);put(x,y,z,'redstone_wire','power=0','lager_technik')
    def repeater(x,y,z,f):solid(x,y-1,z);put(x,y,z,'repeater',f'facing={f},delay=1,locked=false,powered=false','lager_technik')
    def comparator(x,y,z,f):solid(x,y-1,z);put(x,y,z,'comparator',f'facing={f},mode=compare,powered=false','lager_technik')
    # Move the complete library mezzanine stair to the south/north side of the
    # local room, rather than merely deleting its lowest obstructions at the door.
    clear(-721,-719,130,137,791,798)
    for x in range(-721,-718):
        for z in range(791,799):put(x,137,z,'dark_oak_planks','','bibliothek')
    clear(-721,-718,130,140,775,782)
    for i in range(8):
        y,z=130+i,782-i
        for x in range(-721,-718):
            for yy in range(130,y):put(x,yy,z,'dark_oak_planks','','bibliothek')
            put(x,y,z,'dark_oak_stairs','facing=north,half=bottom,shape=straight,waterlogged=false','bibliothek')
        put(-718,y+1,z,'dark_oak_fence','waterlogged=false','bibliothek')
    # Clear both the stair/furniture bottleneck inside and the bench/lamp outside.
    doorway={(x,y,z) for x in range(-727,-717) for y in range(130,133) for z in range(789,793)}
    for p in doorway:
        if p in b and not b[p][0].endswith('_door'):del b[p]
    for x in range(-727,-717):
        for z in range(789,793):put(x,129,z,'polished_deepslate','','terrasse' if x<-722 else 'bibliothek')
    for z in (790,791):
        for y,half in [(130,'lower'),(131,'upper')]:
            put(-722,y,z,'dark_oak_door',f'facing=west,half={half},hinge={"left" if z==790 else "right"},open=false,powered=false','bibliothek')
    # Quoins, projecting cornices and six glazed roof dormers, within the existing massing.
    for z in (750,830):
        outside=z-1 if z==750 else z+1
        for x in range(-721,-668):
            for y in (137,144):
                put(x,y,outside,'polished_diorite_slab','type=top,waterlogged=false','fassade')
        for x in (-721,-704,-686,-669):
            for y in range(130,144):
                if (x,y,z) in b and b[x,y,z][0] not in ('glass','glass_pane'):
                    put(x,y,z,'polished_diorite' if y%2 else 'stone_bricks','','fassade')
        for cx in (-713,-695,-677):
            front=754 if z==750 else 826;back=758 if z==750 else 822
            for xx in range(cx-2,cx+3):
                for zz in range(min(front,back),max(front,back)+1):
                    roof=152+(2-abs(xx-cx))
                    for y in range(148,roof):
                        if xx in (cx-2,cx+2) or zz in (front,back):
                            bid='glass' if zz==front and abs(xx-cx)<=1 and 149<=y<=151 else 'stone_bricks'
                            put(xx,y,zz,bid,'','dach_schmuck')
                    put(xx,roof-1,zz,'deepslate_tiles','','dach_schmuck')
                    put(xx,roof,zz,'waxed_oxidized_cut_copper_slab' if xx==cx else 'deepslate_tile_stairs',
                        'type=bottom,waterlogged=false' if xx==cx else f'facing={"east" if xx<cx else "west"},half=bottom,shape=straight,waterlogged=false','dach_schmuck')
    for x in range(-704,-665):put(x,157,790,'waxed_oxidized_cut_copper_slab','type=bottom,waterlogged=false','dach_schmuck')
    for cx,cz in [(-722,751),(-668,751),(-722,829),(-668,829)]:
        put(cx,149,cz,'waxed_oxidized_copper','','dach_schmuck')
        put(cx,150,cz,'lightning_rod','facing=up,powered=false,waterlogged=false','dach_schmuck')
    # Rebuild Keller 1 north as six isolated bulk slices with actual vertical shafts.
    clear(-706,-665,122,127,767,790)
    for x in range(-706,-664):
        for z in range(766,791):
            put(x,121,z,'deepslate_tiles','','keller_1');put(x,128,z,'stone_bricks','','keller_1')
            if x==-665 or z==766:
                for y in range(122,128):put(x,y,z,'stone_bricks','','keller_1')
    modules=[]
    items=[('cobblestone','Bruchstein'),('dirt','Erde'),('iron_ingot','Eisenbarren'),('deepslate','Tiefenschiefer'),('stone','Stein'),('gravel','Kies')]
    for (item,label),x in zip(items,[-705,-698,-691,-684,-677,-670]):
        # Feed 127 -> filter 126 -> locked extractor 125 -> loose buffer 125/779.
        hopper(x,126,784,'north');solid(x,126,783);hopper(x,125,784)
        for z in range(783,779,-1):hopper(x,125,z)
        put(x,125,779,'barrel','facing=south,open=false','bulk_lager')
        solid(x,124,779);solid(x,123,779);solid(x,122,779)
        comparator(x,126,785,'south')
        for z in (786,787,788):dust(x,126,z)
        repeater(x,126,789,'south');solid(x,126,790)
        # Isolated return bus: three-dust threshold, then relay and lower torch lock.
        dust(x+1,126,790);dust(x+2,126,790)
        for z in (789,788,787,786):dust(x+2,125,z)
        repeater(x+2,125,785,'north');solid(x+2,125,784)
        put(x+1,125,784,'redstone_wall_torch','facing=west,lit=true','lager_technik')
        # Overflow is extracted from the feed hopper, never from the ready-stock barrel.
        hopper(x,124,780,'west')
        for z in range(780,774,-1):hopper(x-1,124,z,'north' if z>775 else 'east')
        hopper(x,124,775,'north')
        # Full-barrel threshold: comparator main input vs constant side signal 15.
        comparator(x+1,125,779,'east');repeater(x+1,125,778,'south')
        put(x+1,125,777,'redstone_block','','lager_technik')
        for xx in (x+2,x+3,x+4):dust(xx,125,779)
        dust(x+4,124,780);repeater(x+3,124,780,'west');solid(x+2,124,780)
        put(x+1,124,780,'redstone_wall_torch','facing=west,lit=true','lager_technik')
        # Shulker station: input from south, placement from north, breaker east.
        put(x,124,774,'shulker_box','facing=up','shulker_technik')
        put(x,124,773,'dispenser','facing=south,triggered=false','shulker_technik')
        hopper(x,125,773,'down','shulker_technik');put(x,126,773,'barrel','facing=north,open=false','shulker_technik')
        put(x+1,124,774,'piston','facing=west,extended=false','shulker_technik')
        comparator(x-1,124,774,'west')
        # Safe commissioning jumper: do not continuously drain a filling shulker.
        # Replace this block with the sequencer-controlled strong-power input only
        # after validating lock -> break -> collect -> place -> unlock in a test world.
        put(x-1,123,774,'redstone_block','','shulker_technik')
        for y in range(123,118,-1):hopper(x,y,774,'down','shulker_technik')
        bins=[]
        for y in (118,116,114):
            put(x,y,774,'barrel','facing=south,open=false','bulk_lager');bins.append([x,y,774])
            if y>114:hopper(x,y-1,774,'down','shulker_technik')
        for p in [(x,125,784),(x,124,780),(x,123,774)]:
            bid,st,g=b[p];b[p]=(bid,st.replace('enabled=true','enabled=false'),g)
        modules.append(dict(id=item,label=label,x=x,y=125,z=779,filter=dict(x=x,y=126,z=784),loose=[x,125,779],
            active_box=[x,124,774],dispenser=[x,124,773],piston=[x+1,124,774],empty_supply=[x,126,773],bins=bins,
            loose_slots=27,packed_box_slots=81,packed_item_capacity_64=81*1728,
            controller='Filter 41+1+1+1+1; ready barrel signal 15; shulker full signal 15; interlocked break/collect/place cycle',
            commissioning='Redstone routing and entity collection require a 26.3 test-world run'))
    # Relocate the one rack whose old front is now occupied by a service shaft.
    for index,cx in zip(range(6,11),[-702,-695,-688,-681,-674]):
        bay=next(a for a in d['storage_bays'] if a['id']==f'R{index:02d}')
        for p in bay['containers']:
            x,y,z=p;b.pop(tuple(p),None);b.pop((x,y,z-1),None)
        lp=(bay['x'],119,bay['z']+1)
        if b.get(lp,('',''))[0]=='lantern':b.pop(lp)
        bay.update(x=cx,y=114,z=812,front=[cx,114,813],containers=[])
        for x in (cx,cx+1):
            for y in range(114,118):
                put(x,y,812,'barrel','facing=south,open=false','lager_regale');put(x,y,811,'dark_oak_planks','','lager_regale');bay['containers'].append([x,y,812])
    # The eastern-most silo opens through the old wall into the existing aisle.
    clear(-670,-670,114,119,775,775)
    # A single closed, walkable golem room: nine matching destinations, no empty catch-all.
    clear(-706,-671,122,127,795,813)
    for x in range(-706,-670):
        for y in range(122,128):
            if x not in (-700,-699):put(x,y,794,'stone_bricks','','keller_1')
    for y,half in [(122,'lower'),(123,'upper')]:
        for x in (-700,-699):put(x,y,794,'dark_oak_door',f'facing=north,half={half},hinge={"left" if x==-700 else "right"},open=false,powered=false','keller_1')
    # Other nearby storage uses barrels; copper golems sort into chests, not barrels.
    for p,(bid,st,g) in list(b.items()):
        if bid=='chest' and 122<=p[1]<=128 and g!='sortierung':b[p]=('barrel','facing=south,open=false',g)
    seeds=[('Holz & Pflanzen',['oak_log','spruce_log','birch_log','dark_oak_log','oak_sapling','bone_meal','moss_block','vine']),
      ('Nahrung & Farming',['wheat','carrot','potato','bread','apple','sugar_cane','pumpkin','melon_slice']),
      ('Mobdrops',['rotten_flesh','bone','string','gunpowder','spider_eye','slime_ball','ender_pearl','leather']),
      ('Redstone & Technik',['redstone','repeater','comparator','piston','observer','hopper','rail','redstone_torch']),
      ('Werkzeuge & Ausrüstung',['diamond_pickaxe','diamond_axe','diamond_shovel','bow','shield','elytra','shears','flint_and_steel']),
      ('Deko & Bauteile',['glass','lantern','chain','terracotta','bricks','flower_pot','calcite','polished_diorite']),
      ('Erze & Wertvolles',['diamond','emerald','lapis_lazuli','gold_ingot','copper_ingot','raw_iron','raw_gold','quartz']),
      ('Nether & End',['netherrack','soul_sand','nether_wart','blaze_rod','end_stone','purpur_block','chorus_fruit','obsidian']),
      ('Magie & Bücher',['book','paper','enchanted_book','glass_bottle','blaze_powder','glowstone_dust','amethyst_shard','experience_bottle'])]
    regular=[]
    for i,((label,types),(x,z)) in enumerate(zip(seeds,[(-704,797),(-697,797),(-690,797),(-683,797),(-676,797),(-704,810),(-695,810),(-686,810),(-677,810)])):
        put(x,123,z,'chest',f'facing={"south" if z==797 else "north"},type=single,waterlogged=false','golem_lager')
        put(x,122,z,'polished_deepslate','','golem_lager')
        regular.append(dict(id=f'G{i+1:02d}',label=label,x=x,y=123,z=z,seeds=types,slots=27))
    copper=(-675,123,803);put(*copper,'waxed_copper_chest','facing=west,type=single,waterlogged=false','golem_lager');solid(-675,122,803,'golem_lager')
    # Item input and adjacent box stations; all returned boxes use a separate collection port.
    clear(-719,-707,123,127,785,789)
    put(-708,124,789,'chest','facing=south,type=single,waterlogged=false','sortierung')
    for z in range(789,784,-1):hopper(-708,123,z)
    for y in range(123,127):put(-708,y,784,'dropper','facing=up,triggered=false','lager_technik')
    for x in range(-708,-669):hopper(x,127,784,'east' if x<-670 else 'south')
    for z in range(785,804):hopper(-670,127,z,'south' if z<803 else 'west')
    for x in range(-671,-675,-1):hopper(x,127,803,'west')
    for y in range(127,123,-1):hopper(-675,y,803,'down')
    stations=[]
    for x,kind,label in [(-712,'unloader','Shulker-Unloader'),(-716,'loader','Shulker-Loader')]:
        put(x,124,789,'shulker_box','facing=up','shulker_technik')
        put(x,124,788,'dispenser','facing=south,triggered=false','shulker_technik')
        hopper(x,125,788,'down','shulker_technik');put(x,126,788,'barrel','facing=south,open=false','shulker_technik')
        put(x+1,124,789,'piston','facing=west,extended=false','shulker_technik')
        comparator(x,124,790,'south')
        if kind=='unloader':
            for xx in range(x,-708):hopper(xx,123,789,'east','shulker_technik')
        else:
            hopper(x,125,789,'down','shulker_technik');put(x,126,789,'barrel','facing=south,open=false','shulker_technik')
            solid(x,123,789,'shulker_technik')
        # Side pickup is explicitly a commissioning port, not asserted lossless physics.
        hopper(x-1,123,789,'down','shulker_technik');put(x-1,122,789,'barrel','facing=south,open=false','shulker_technik')
        stations.append(dict(id=kind,name=label,x=x,y=124,z=789,active_box=[x,124,789],dispenser=[x,124,788],
            piston=[x+1,124,789],catch=[x-1,122,789],
            commissioning='Full/empty detection, empty-box return and piston drop capture must be tested in 26.3'))
    # Pool corridor must remain free after all decoration, including lamp relocation.
    for p in doorway:
        if p in b and not b[p][0].endswith('_door'):del b[p]
    # Repair every lantern's attachment; low corridor fixtures move overhead.
    lanterns=[(p,r) for p,r in b.items() if r[0] in ('lantern','soul_lantern')]
    repaired=0;removed=0
    def supports(r,top=False):
        if not r:return False
        bid,st,g=r
        if bid.endswith('_slab'):return ('type=top' in st or 'type=double' in st) if top else ('type=bottom' in st or 'type=double' in st)
        if bid.endswith('_stairs'):return False
        return not (bid in ('lantern','soul_lantern','water','redstone_wire','hopper','chain','brewing_stand','flower_pot') or
            bid.endswith(('_door','_sign','_wall_sign','_torch','_pane','_carpet','_bed')))
    for (x,y,z),r in lanterns:
        if (x,y,z) not in b:continue
        bid,st,g=r;hanging='hanging=true' in st
        # Five-wide cellar thoroughfares and the new pool vestibule have no floor lamps.
        in_corridor=(788<=z<=792 and y in (106,114,122,130)) or ((x,y,z) in doorway)
        if in_corridor:
            b.pop((x,y,z),None);y+=3;hanging=True;st='hanging=true';repaired+=1
            if (x,y,z) in b:removed+=1;continue
            put(x,y,z,bid,st,g)
        if hanging:
            yy=y+1
            while yy<=min(y+14,159) and (not b.get((x,yy,z)) or b[x,yy,z][0]=='chain'):yy+=1
            if yy<=min(y+14,159) and supports(b.get((x,yy,z))):
                for h in range(y+1,yy):put(x,h,z,'chain','axis=y,waterlogged=false','beleuchtung')
                if yy>y+1:repaired+=1
            else:b.pop((x,y,z),None);removed+=1
        elif not supports(b.get((x,y-1,z)),True):
            b.pop((x,y,z),None);removed+=1
    # Updated metadata is transformed together with every block and direction.
    d['storage_system'].update(title='Blackthorn Logistik 26.3',bulk=modules,regular=regular,
        copper_input=dict(x=copper[0],y=copper[1],z=copper[2]),golem_spawn=dict(x=-690,y=122,z=804),stations=stations,
        mechanism='Einwurf / Shulker-Unloader → Hubstrecke → sechs Bulkfilter → Kupfertruhe → neun vorbestückte Zieltruhen',
        mechanics=dict(target_version='26.3',golem_max_items_per_trip=16,golem_max_chests_per_search=10,
            golem_search_horizontal=32,golem_search_vertical=8,notes=[
             'Golems erkennen konkrete Itemtypen, keine Kategorien oder Mengen.',
             'Alle Zieltruhen mit ihren gelisteten Itemtypen vorbestücken und mindestens ein Seed-Item erhalten.',
             'Keine leere Catch-all-Truhe im Golemraum: sie würde die übrige Sortierung umgehen.',
             'Unbekannte Itemtypen bleiben zur manuellen Zuordnung in der Kupfer-Eingangsstufe.',
             'Filter- und Controllerinventare sind in technik_inventare.csv dokumentiert.',
             'Schaltungen sind ein konkreter Bauentwurf; Pulsfolge, Pickup und Paper-Verhalten noch nicht im Spiel geprüft.']))
    # Use the Copper Age registry name in the 26.3 build lists.
    b={p:('iron_chain' if bid=='chain' else bid,st,g) for p,(bid,st,g) in b.items()}
    for a in regular:a['seeds']=['iron_chain' if item=='chain' else item for item in a['seeds']]
    d['storage_zones']=[]
    for a in d['storage_bays']:
        ps=a['containers'];d['storage_zones'].append(dict(id=a['id'],name=a['name'],contents=f"{len(ps)} Fässer · {a['slots']} Plätze · manuelle Reserve",room='Regal-/Privatlager',group='lager_regale' if a['floor']==113 else 'privatlager',
            x=[min(p[0] for p in ps),max(p[0] for p in ps)],y=[min(p[1] for p in ps),max(p[1] for p in ps)],z=[min(p[2] for p in ps),max(p[2] for p in ps)]))
    d['access_routes']=[dict(id='pool',start=[-718,130,790],end=[-727,130,790],width=4)]
    for key in ('rooms','storage_system','storage_bays','storage_zones','access_routes'):d[key]=metadata180(d[key])
    # Descriptions use coordinates generated from transformed records, never old compass text.
    for r in d['rooms']:
        r['access']='Revision 5.9: Zugang im aktuellen Grundriss prüfen; Koordinaten und Bauteilansichten sind um 180° gedreht.'
        if r['group']=='bibliothek':r['text']='Bibliothek mit freiem Zugang zur östlichen Poolterrasse; die vollständige Mezzanin-Treppe ist seitlich versetzt, der Durchgang bleibt eben.'
    d['meta'].update(orientation='Eingang Westen; Pool und Panorama Osten; Zufahrt Nordwesten',rotation_pivot=[-690,790],rotation_degrees=180,anchor=position(d['meta']['anchor']))
    b={tuple(position(p)):(bid,state180(st),g) for p,(bid,st,g) in b.items()}
    report=dict(rotation_degrees=180,lantern_repairs=repaired,lanterns_removed=removed,bulk_modules=6,bulk_box_slots=486,
        bulk_ready_slots=162,technical_in_game_verified=False,pool_access_clear=True,target_minecraft='26.3')
    return d,b,report


def terrain_plan(d,b,H,bounds):
    x0,x1,z0,z1=bounds;grade={};zones={};tops={}
    def set_(x,z,y,zone,top='grass_block'):grade[x,z]=y;zones[x,z]=zone;tops[x,z]=top
    # Rotate the architectural formation, not its previous cut/fill quantities.
    for x in range(-723,-641):
        for z in range(751,830):set_(-1380-x,1580-z,128,'Hausunterbau','stone')
    for x in range(-722,-669):
        for z in range(766,815):set_(-1380-x,1580-z,104,'Kellerbaugrube','stone')
    for x in range(-669,-664):
        for z in range(766,791):set_(-1380-x,1580-z,120,'Techniknische','stone')
    for x,y,z in b:
        if y==129 and b[x,y,z][2] in ('res1','res4','terrasse','pool') and b[x,y,z][2]!='terrasse':
            # The pool is supported on piers; no plateau fills the panorama ravine.
            if b[x,y,z][2] in ('res1','res4'):set_(x,z,128,'Hausunterbau','stone')
    waypoints=[(-744,790,128),(-750,780,123),(-752,768,120),(-752,753,122),(-757,739,125),(-766,724,128),(-783,711,129)]
    centers={}
    for a,c in zip(waypoints,waypoints[1:]):
        steps=max(abs(c[0]-a[0]),abs(c[1]-a[1]))
        for i in range(steps+1):
            f=i/steps;x=round(a[0]+(c[0]-a[0])*f);z=round(a[1]+(c[1]-a[1])*f);y=round(a[2]+(c[2]-a[2])*f);centers[x,z]=y
    # Broad shoulders, then a softened embankment: the path is not on the raw cliff lip.
    shoulder={};road={}
    for (cx,cz),y in centers.items():
        for dx in range(-8,9):
            for dz in range(-8,9):
                distance=math.hypot(dx,dz)
                if distance>8:continue
                x,z=cx+dx,cz+dz;natural=H[z-z0][x-x0]
                yy=y if distance<=4 else round(y+(natural-y)*(distance-4)/4)
                old=shoulder.get((x,z))
                if old is None or distance<old[0]:shoulder[x,z]=(distance,yy)
                if distance<=2.4:road[x,z]=y
    for (x,z),(distance,y) in shoulder.items():
        if (x,z) not in grade:set_(x,z,y,'Wegschulter','grass_block')
    for (x,z),y in road.items():set_(x,z,y,'Zufahrt Nordwest','gravel')
    for x in range(-746,-736):
        for z in range(784,797):set_(x,z,128,'Eingangshof','stone_bricks')
    # Guard the raised ramp as well as moving it away from the natural cliff.
    railings=0
    for (x,z),(distance,y) in shoulder.items():
        if 3<=distance<=4 and (x,z) not in road and zones.get((x,z))=='Wegschulter' and y-H[z-z0][x-x0]>4:
            b[x,y+1,z]=('stone_brick_wall','up=true,north=none,east=none,south=none,west=none,waterlogged=false','weg_sicherung');railings+=1
    # Measured relative to the natural terrain, excluding the constructed ramp height.
    minimum=99
    for x,z in centers:
        natural=H[z-z0][x-x0]
        for dx in range(-22,23):
            for dz in range(-22,23):
                xx,zz=x+dx,z+dz
                if x0<=xx<=x1 and z0<=zz<=z1 and H[zz-z0][xx-x0]<natural-8:minimum=min(minimum,math.hypot(dx,dz))
    d['route_safety']=dict(min_center_distance_to_natural_drop_9=round(minimum,2),definition='Nearest surveyed column more than 8 blocks below the natural route-center ground; radius 22 blocks.',road_halfwidth=2.4,flat_shoulder_radius=4,raised_ramp_guard_posts=railings)
    return grade,zones,tops,waypoints
