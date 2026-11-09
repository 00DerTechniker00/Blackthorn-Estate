"""Functional horse stable and restrained Victorian facade / accessible west-gable reading loft.

All coordinates are final V6 world coordinates (EG floor Y127). Called after lowering
and water accesses. No entities are fabricated; original house stairs are protected.
"""
from collections import Counter
from pathlib import Path
import json

STABLE=(-774,-761,123,132,744,753)
AISLE=range(-768,-765)
APPROACH=[(754,123),(755,122),(756,121),(757,121),(758,121)]
SIDE_APPROACH=[(x,z,121 if x<=-762 else 120) for x in range(-765,-754) for z in (756,757,758)]
ROOT=Path(__file__).resolve().parent.parent


def original_drive():
    seed=json.loads((ROOT/'tools/seeds/revision-5.26/blueprint.json').read_text())
    result={}
    for y,z,x,n,i in seed['runs']:
        bid,state,gi=seed['reg'][i]
        if seed['groups'][gi]=='zufahrt':
            for xx in range(x,x+n):result[xx,y-2,z]=(bid,state,'zufahrt')
    return seed,result


def enhance(d,b,air):
    before=b.copy();protected={p:v for p,v in b.items() if p[1]==95 or v[2]=='halle_treppe'}
    def put(x,y,z,bid,state='',g='v6_stall'):
        p=(x,y,z);b[p]=(bid,state,g);air.discard(p)
    def clear(x,y,z):
        p=(x,y,z);b.pop(p,None);air.add(p)
    # The previous stable reservation cut across the original NW drive. Restore
    # that footprint to lawn, and reinstate every original drive block at Y-2.
    seed,drive=original_drive();T=d['terrain'];x0,_,z0,_=T['bounds'];surface_columns={}
    def surface(x,z,y,material,group='v6_stall_rueckbau'):
        old=T['target_heights'][z-z0][x-x0]
        for yy in range(min(old,y)-1,y):
            if (x,yy,z) not in b:put(x,yy,z,'dirt',g=group)
        for yy in range(y+1,max(old+1,y+5)):
            value=b.get((x,yy,z))
            if value and value[2] in ('terraform_auffuellung','terraform_oberflaeche','v6_stall','v6_stallweg','stall_remise','ruestungsnischen','v6_stall_rueckbau'):clear(x,yy,z)
        put(x,y,z,material,g=group)
        T['target_heights'][z-z0][x-x0]=y;T['target_surface_blocks'][z-z0][x-x0]=material
        surface_columns[x,z]=[x,z,y,material]
    removed_columns=set()
    for p,v in list(b.items()):
        if v[2] in ('stall_remise','ruestungsnischen','v6_stall','v6_stallweg','v6_stall_rueckbau'):
            clear(*p);removed_columns.add((p[0],p[2]))
    sx0,_,sz0,_=seed['terrain']['bounds']
    old_columns={(x,z) for x in range(-754,-740) for z in range(763,773)}
    old_columns.update((x,z) for x in range(-748,-745) for z in range(773,791))
    old_columns.update((x,z) for x,z in removed_columns if -755<=x<=-740 and 762<=z<=790)
    road_columns={(x,z) for x,y,z in drive}
    for x,z in sorted(old_columns):
        if (x,z) in road_columns:continue
        y=seed['terrain']['target_heights'][z-sz0][x-sx0]-2
        surface(x,z,y,'grass_block')
    # Restore road positions before constructing the building, so a conflict fails
    # the final preservation check instead of silently erasing part of the drive.
    for (x,y,z),v in drive.items():
        b[x,y,z]=v;air.discard((x,y,z))
        if -755<=x<=-740 and 744<=z<=783 and v[0]=='gravel':
            for yy in range(y+1,y+5):
                value=b.get((x,yy,z))
                if value and value[2] in ('terraform_auffuellung','terraform_oberflaeche','v6_stall','v6_stallweg','stall_remise','ruestungsnischen','v6_stall_rueckbau'):clear(x,yy,z)
            if (x,y-1,z) not in b:put(x,y-1,z,'dirt',g='v6_stall_rueckbau')
        T['target_heights'][z-z0][x-x0]=y;T['target_surface_blocks'][z-z0][x-x0]=v[0]
        surface_columns[x,z]=[x,z,y,v[0]]
    # A real 14x10 building: 12x8 inside, 3-wide aisle, two generous horse boxes.
    # New masonry foundation follows the local earth surface, not an unsupported slab.
    T=d['terrain'];x0,_,z0,_=T['bounds']
    for x in range(-774,-760):
        for z in range(744,754):
            ground=T['target_heights'][z-z0][x-x0]
            for y in range(min(ground,122),124):put(x,y,z,'stone_bricks')
            put(x,123,z,'coarse_dirt' if z not in (744,753) and x not in (-774,-761) else 'stone_bricks')
            for y in range(124,136):clear(x,y,z)
            for y in range(124,128):
                if x in (-774,-761) or z in (744,753):
                    put(x,y,z,'stripped_oak_log' if x in (-774,-761,-769,-765) else 'oak_planks', 'axis=y' if x in (-774,-761,-769,-765) else '')
            put(x,128,z,'dark_oak_planks')
            # Shallow gabled slate roof, with a continuous, supported ridge.
            ry=128+(min(x+774,-761-x)+1)//2
            put(x,ry,z,'nether_brick_stairs',f'facing={"west" if x<=-768 else "east"},half=bottom,shape=straight,waterlogged=false')
            if x in (-768,-767):put(x,132,z,'nether_brick_slab','type=bottom,waterlogged=false')
            T['target_heights'][z-z0][x-x0]=123;T['target_surface_blocks'][z-z0][x-x0]='coarse_dirt'
            surface_columns[x,z]=[x,z,123,'coarse_dirt']
    # The aisle has no hanging fixtures or feeders below its four-block clear headroom.
    for x in AISLE:
        for z in range(745,755):
            put(x,123,z,'stone_bricks')
            for y in range(124,128):clear(x,y,z)
        put(x,124,753,'oak_fence_gate','facing=south,in_wall=false,open=false,powered=false')
    # Continuous partitions, with 3-cell-wide side gates into each box.
    for x,face in ((-769,'east'),(-765,'west')):
        for z in range(745,753):
            put(x,124,z,'oak_fence_gate' if z in (747,748,749) else 'oak_fence',
                f'facing={face},in_wall=false,open=false,powered=false' if z in (747,748,749) else '')
    for x,z in ((-773,745),(-762,751)):put(x,124,z,'hay_block','axis=y')
    for x,z in ((-773,751),(-762,745)):put(x,124,z,'water_cauldron','level=3')
    for x in (-773,-772):put(x,124,752,'barrel','facing=south,open=false')
    # View/ventilation apertures are high enough to retain the horses and below the eaves.
    for x in (-774,-761):
        for z in (746,747,750,751):put(x,126,z,'iron_bars')
    for z in (747,750):put(-770,127,z,'lantern','hanging=true,waterlogged=false')
    for x in (-769,-765):
        put(x,128,753,'polished_blackstone_bricks')
        put(x,127,754,'polished_blackstone_brick_stairs','facing=north,half=top,shape=straight,waterlogged=false')
        put(x,123,754,'stone_bricks')
        put(x,122,754,'dirt')
        for y in (124,125,126):put(x,y,754,'stone_brick_wall')
    # A supported 3-wide way follows the hillside and joins its separate side access at Z756–758.
    for z,y in APPROACH:
        for x in AISLE:
            old=T['target_heights'][z-z0][x-x0]
            for yy in range(min(old,y)-1,y):put(x,yy,z,'dirt',g='v6_stallweg')
            for yy in range(y+1,max(old+5,y+5)):clear(x,yy,z)
            put(x,y,z,'stone_bricks',g='v6_stallweg')
            T['target_heights'][z-z0][x-x0]=y;T['target_surface_blocks'][z-z0][x-x0]='stone_bricks'
            surface_columns[x,z]=[x,z,y,'stone_bricks']
    # The side access joins from the west, ending before the original path.
    for x,z,y in SIDE_APPROACH:
        old=T['target_heights'][z-z0][x-x0]
        for yy in range(min(old,y)-1,y):put(x,yy,z,'dirt',g='v6_stallweg')
        for yy in range(y+1,max(old+5,y+5)):clear(x,yy,z)
        put(x,y,z,'stone_bricks',g='v6_stallweg')
        T['target_heights'][z-z0][x-x0]=y;T['target_surface_blocks'][z-z0][x-x0]='stone_bricks'
        surface_columns[x,z]=[x,z,y,'stone_bricks']
    assert all(b.get(p)==v for p,v in drive.items()),'Stable must preserve every original drive block'
    # Continue the recovered drive across the two-cell gap to the west portico.
    for x in (-745,-744):
        for z in (789,790,791):
            p=(x,126,z)
            if p not in drive:put(x,126,z,'stone_bricks',g='v6_ankunftsweg')
            for y in (127,128,129):
                value=b.get((x,y,z))
                if value and value[2] in ('v6_stall_rueckbau','terraform_auffuellung','terraform_oberflaeche'):clear(x,y,z)
            T['target_heights'][z-z0][x-x0]=126;T['target_surface_blocks'][z-z0][x-x0]='stone_bricks'
            surface_columns[x,z]=[x,z,126,'stone_bricks']
    # The old entrance stairs were buried beneath a full floor block. Swap the
    # central three into the actual floor layer so the last rise is two half steps.
    for z in (789,790,791):
        put(-743,126,z,'polished_deepslate',g='portikus')
        put(-743,127,z,'polished_deepslate_stairs','facing=east,half=bottom,shape=straight,waterlogged=false','portikus')
    # Restrained facade hierarchy: dark plinth, cut-stone course and small copper gable details.
    facade_changes=Counter()
    for (x,y,z),(bid,state,g) in list(b.items()):
        replacement=None
        if g=='fassade' and bid=='stone_bricks':
            if y in (127,128):replacement='polished_blackstone_bricks'
            elif y==134 and (x%6==0 or z%6==0):replacement='chiseled_stone_bricks'
        elif g=='halle_giebelfenster' and bid=='stone_bricks':
            if y==152 and z in (789,791):replacement='waxed_cut_copper'
            elif y in (146,150):replacement='chiseled_stone_bricks'
        if replacement:
            put(x,y,z,replacement,state,'v6_fassadendetails');facade_changes[replacement]+=1
    # Four slim pilasters project one block from the solid corners of the middle wings.
    # They run from real plinths to the eaves; no window is screened or door moved.
    pilasters=[]
    for x in (-695,-677):
        for z,back,outside,face in ((750,751,749,'north'),(830,829,831,'south')):
            for y in range(128,142):
                anchor=b.get((x,y,back))
                assert anchor and not any(t in anchor[0] for t in ('glass','door')),('Bad pilaster anchor',x,y,back,anchor)
            put(x,127,z,'polished_blackstone_bricks',g='v6_fassadenprofil')
            for y in range(128,142):
                put(x,y,z,'chiseled_stone_bricks' if y==134 else 'polished_diorite' if y==141 else 'stone_brick_wall',g='v6_fassadenprofil')
            put(x,141,outside,'polished_diorite_stairs',f'facing={face},half=top,shape=straight,waterlogged=false','v6_fassadenprofil')
            pilasters.append([x,127,z])
    # Convert the real empty space behind the west gable into a reading loft.
    # Existing glazed gable, roof shell and main staircase are left in place.
    for x in range(-713,-704):
        for z in range(782,799):put(x,143,z,'dark_oak_planks',g='v6_giebelsaal')
    # Small gallery extension from the existing north gallery (floor135); no floating ladder.
    for x in range(-713,-709):
        for z in range(777,783):put(x,135,z,'dark_oak_planks',g='v6_giebelzugang')
    for x in (-711,-710):
        for y in (136,137):clear(x,y,777)
    for z in range(778,783):put(-709,136,z,'dark_oak_fence',g='v6_giebelzugang')
    for x in range(-713,-709):put(x,136,783,'dark_oak_fence',g='v6_giebelzugang')
    for y in range(136,145):
        put(-712,y,782,'dark_oak_log','axis=y','v6_giebelzugang')
        put(-711,y,782,'ladder','facing=east,waterlogged=false','v6_giebelzugang')
        if y!=143:clear(-710,y,782)
    # Low rails guard the shaft at the top, while the eastern exit remains open.
    for z in (781,783):put(-711,144,z,'dark_oak_fence',g='v6_giebelzugang')
    for z in (786,787,793,794):
        for y in (144,145):put(-713,y,z,'bookshelf',g='v6_giebelsaal')
    put(-712,144,790,'cartography_table',g='v6_giebelsaal')
    for x in (-708,-707):put(x,144,796,'dark_oak_stairs','facing=north,half=bottom,shape=straight,waterlogged=false','v6_giebelsaal')
    put(-707,144,794,'dark_oak_slab','type=bottom,waterlogged=false','v6_giebelsaal')
    # Flush floor lights avoid a new hanging obstruction under the pitched roof.
    for x,z in ((-709,786),(-709,793)):put(x,143,z,'sea_lantern',g='v6_giebelsaal')
    assert all(b.get(p)==v for p,v in protected.items()),'Protected floor or main staircase changed'
    rooms=[
        dict(name='Pferdestall · zwei Boxen',group='v6_stall',x=[-773,-762],y=[124,127],z=[745,752],text='Zwei Boxen mit 4×7 bzw. 3×7 Blöcken Innenfläche; dreibreiter Mittelgang und Haupttor. Alle drei Torflügel vor dem Reiten öffnen.',access='Dreibreiter Weg X −768…−766 vom südlichen Tor Z753, dann östlich auf Z756…758 bis X−755 vor die unveränderte Hauptzufahrt. Boden Y123.',stand=0,reach=0),
        dict(name='Westgiebel · Lesesaal',group='v6_giebelsaal',x=[-713,-705],y=[144,148],z=[782,798],text='Begehbarer Lesesaal hinter dem erhaltenen Westgiebel-Fenster; Bücher, Kartentisch und Sitzbank. Die Dachschrägen bleiben als Raumbegrenzung erhalten.',access='Nordgalerie Y135, kleine Erweiterung bis Z782, Leiter X−711 / Z782 bis zum Boden Y143.',stand=0,reach=0)
    ]
    changes={p for p in before.keys()|b.keys() if before.get(p)!=b.get(p)}
    return {'stable_bounds':list(STABLE),'stable_gate':[-768,-766,124,127,753,753],
            'stable_approach':[[z,y] for z,y in APPROACH],'stable_boxes':[[-773,-770,745,751],[-764,-762,745,751]],'stable_approach_bounds':[-768,-755,120,123,754,758],'surface_columns':list(surface_columns.values()),'drive_blocks_preserved':len(drive),'original_drive_bounds':[-785,-743,118,127,709,796],'drive_clearance_bounds':[-755,-740,744,783],
            'gable_bounds':[-713,-705,143,148,782,798],'gable_access':[-711,135,782],
            'pilasters':pilasters,'facade_changes':dict(facade_changes),'changed_positions':len(changes),'rooms':rooms,
            'limits':['Horse dimensions and gate clearance checked geometrically; riding and jump escape require an in-game test','Armour stands, horses and inventory contents are not modelled','No operating redstone stable gate is claimed']}


def check(d,b):
    # Main riding passage: 3-wide, four completely clear blocks high except closed gates.
    for x in AISLE:
        for z in range(745,754):
            assert b[x,123,z][0]=='stone_bricks'
            for y in range(124,128):
                block=b.get((x,y,z))
                assert block is None or z==753 and y==124 and block[0]=='oak_fence_gate',(x,y,z,block)
    for (z,y),(nz,ny) in zip(APPROACH,APPROACH[1:]):assert nz==z+1 and abs(y-ny)<=1
    for z,y in APPROACH:
        for x in AISLE:
            assert (x,y,z) in b
            assert (x,y-1,z) in b,'Unsupported approach'
            for yy in range(y+1,y+5):assert (x,yy,z) not in b,(x,yy,z)
    for x0,x1,z0,z1 in ((-773,-770,745,751),(-764,-762,745,751)):
        assert x1-x0+1>=3 and z1-z0+1>=3
        for x in range(x0,x1+1):
            for z in (747,748,749):
                assert (x,123,z) in b
                for y in (124,125,126):assert (x,y,z) not in b
    for x,z,y in SIDE_APPROACH:
        assert (x,y,z) in b and (x,y-1,z) in b
        for yy in range(y+1,y+5):assert (x,yy,z) not in b,(x,yy,z)
    _,drive=original_drive()
    assert all(b.get(p)==v for p,v in drive.items()),'Original drive must remain unchanged'
    for z in (756,757,758):
        joined=[y for x,y,zz in drive if x==-754 and zz==z and drive[x,y,zz][0]=='gravel']
        assert joined and abs(joined[0]-120)<=1,('Invalid stable side access join',z,joined)
    for (x,y,z),v in drive.items():
        if v[0]=='gravel' and -755<=x<=-740 and 744<=z<=783:
            for yy in range(y+1,y+5):assert (x,yy,z) not in b,('Drive blocked',x,yy,z,b.get((x,yy,z)))
    for z in (789,790,791):
        for x in (-745,-744):
            assert (x,126,z) in b
            for y in (127,128,129):assert (x,y,z) not in b
        assert b[-743,127,z][0]=='polished_deepslate_stairs'
        for y in (128,129):assert (-743,y,z) not in b
    for y in range(136,145):
        assert b[-711,y,782][0]=='ladder';assert b[-712,y,782][0]=='dark_oak_log'
        if y!=143:assert (-710,y,782) not in b
    assert b[-711,135,782][0]=='dark_oak_planks'
    assert b[-710,143,782][0]=='dark_oak_planks'
    # Gable glass remains unblocked behind the viewing/reading aisle.
    for y in (146,147,148):
        assert b[-714,y,790][0]=='light_gray_stained_glass_pane'
        assert (-713,y,790) not in b
    for x in (-695,-677):
        for z,back,outside in ((750,751,749),(830,829,831)):
            assert (x,126,z) in b
            for y in range(127,142):assert (x,y,z) in b
            assert b[x,141,outside][0]=='polished_diorite_stairs'
            for y in range(128,142):assert (x,y,back) in b
    return {'riding_passage_width':3,'riding_passage_clear_height':4,'box_areas':[28,21],
            'approach_steps_checked':len(APPROACH)+len(SIDE_APPROACH),'drive_blocks_preserved':len(drive),'drive_clearance_height':4,'gable_ladder_continuous':True,'main_stairs_protected':True}
