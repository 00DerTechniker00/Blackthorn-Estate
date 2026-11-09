"""Functional horse stable and restrained Victorian facade / accessible west-gable reading loft.

All coordinates are final V6 world coordinates (EG floor Y127). Called after lowering
and water accesses. No entities are fabricated; original house stairs are protected.
"""
from collections import Counter

STABLE=(-754,-741,123,132,763,772)
AISLE=range(-748,-745)
APPROACH=[(773,123),(774,122),(775,121),(776,121),(777,121),(778,121),(779,121),
          (780,122),(781,122),(782,122),(783,122),(784,122),(785,123),(786,124),
          (787,125),(788,126),(789,126),(790,126)]


def enhance(d,b,air):
    before=b.copy();protected={p:v for p,v in b.items() if p[1]==95 or v[2]=='halle_treppe'}
    def put(x,y,z,bid,state='',g='v6_stall'):
        p=(x,y,z);b[p]=(bid,state,g);air.discard(p)
    def clear(x,y,z):
        p=(x,y,z);b.pop(p,None);air.add(p)
    # Remove the narrow old entrances, improvised two-cell stalls and their cobble ramp.
    for p,v in list(b.items()):
        if v[2] in ('stall_remise','ruestungsnischen'):
            b.pop(p);air.add(p)
            x,y,z=p;T=d['terrain'];tx0,_,tz0,_=T['bounds']
            if v[0]=='cobblestone' and y<=T['target_heights'][z-tz0][x-tx0]:
                put(x,y,z,'dirt',g='v6_stallweg')
    # A real 14x10 building: 12x8 inside, 3-wide aisle, two generous horse boxes.
    # New masonry foundation follows the local earth surface, not an unsupported slab.
    T=d['terrain'];x0,_,z0,_=T['bounds']
    for x in range(-754,-740):
        for z in range(763,773):
            ground=T['target_heights'][z-z0][x-x0]
            for y in range(min(ground,122),124):put(x,y,z,'stone_bricks')
            put(x,123,z,'coarse_dirt' if z not in (763,772) and x not in (-754,-741) else 'stone_bricks')
            for y in range(124,136):clear(x,y,z)
            for y in range(124,128):
                if x in (-754,-741) or z in (763,772):
                    put(x,y,z,'stripped_oak_log' if x in (-754,-741,-749,-745) else 'oak_planks', 'axis=y' if x in (-754,-741,-749,-745) else '')
            put(x,128,z,'dark_oak_planks')
            # Shallow gabled slate roof, with a continuous, supported ridge.
            ry=128+(min(x+754,-741-x)+1)//2
            put(x,ry,z,'nether_brick_stairs',f'facing={"west" if x<=-748 else "east"},half=bottom,shape=straight,waterlogged=false')
            if x in (-748,-747):put(x,132,z,'nether_brick_slab','type=bottom,waterlogged=false')
            if x not in (-754,-741):T['target_heights'][z-z0][x-x0]=123;T['target_surface_blocks'][z-z0][x-x0]='coarse_dirt'
    # The aisle has no hanging fixtures or feeders below its four-block clear headroom.
    for x in AISLE:
        for z in range(764,774):
            put(x,123,z,'stone_bricks')
            for y in range(124,128):clear(x,y,z)
        put(x,124,772,'oak_fence_gate','facing=south,in_wall=false,open=false,powered=false')
    # Continuous partitions, with 3-cell-wide side gates into each box.
    for x,face in ((-749,'east'),(-745,'west')):
        for z in range(764,772):
            put(x,124,z,'oak_fence_gate' if z in (766,767,768) else 'oak_fence',
                f'facing={face},in_wall=false,open=false,powered=false' if z in (766,767,768) else '')
    for x,z in ((-753,764),(-742,770)):put(x,124,z,'hay_block','axis=y')
    for x,z in ((-753,770),(-742,764)):put(x,124,z,'water_cauldron','level=3')
    for x in (-753,-752):put(x,124,771,'barrel','facing=south,open=false')
    # View/ventilation apertures are high enough to retain the horses and below the eaves.
    for x in (-754,-741):
        for z in (765,766,769,770):put(x,126,z,'iron_bars')
    for z in (766,769):put(-750,127,z,'lantern','hanging=true,waterlogged=false')
    for x in (-749,-745):
        put(x,128,772,'polished_blackstone_bricks')
        put(x,127,773,'polished_blackstone_brick_stairs','facing=north,half=top,shape=straight,waterlogged=false')
        put(x,123,773,'stone_bricks')
        put(x,122,773,'dirt')
        for y in (124,125,126):put(x,y,773,'stone_brick_wall')
    # A supported 3-wide way follows the hillside and rejoins the NW approach at Z790.
    for z,y in APPROACH:
        for x in AISLE:
            old=T['target_heights'][z-z0][x-x0]
            for yy in range(min(old,y),y):put(x,yy,z,'dirt',g='v6_stallweg')
            for yy in range(y+1,max(old+5,y+5)):clear(x,yy,z)
            put(x,y,z,'stone_bricks',g='v6_stallweg')
            T['target_heights'][z-z0][x-x0]=y;T['target_surface_blocks'][z-z0][x-x0]='stone_bricks'
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
        dict(name='Pferdestall · zwei Boxen',group='v6_stall',x=[-753,-742],y=[124,127],z=[764,771],text='Zwei Boxen mit 4×7 bzw. 3×7 Blöcken Innenfläche; dreibreiter Mittelgang und Haupttor. Alle drei Torflügel vor dem Reiten öffnen.',access='Dreibreiter Weg X −748…−746 vom südlichen Tor Z772 bis Zufahrt Z790. Boden Y123.',stand=0,reach=0),
        dict(name='Westgiebel · Lesesaal',group='v6_giebelsaal',x=[-713,-705],y=[144,148],z=[782,798],text='Begehbarer Lesesaal hinter dem erhaltenen Westgiebel-Fenster; Bücher, Kartentisch und Sitzbank. Die Dachschrägen bleiben als Raumbegrenzung erhalten.',access='Nordgalerie Y135, kleine Erweiterung bis Z782, Leiter X−711 / Z782 bis zum Boden Y143.',stand=0,reach=0)
    ]
    changes={p for p in before.keys()|b.keys() if before.get(p)!=b.get(p)}
    return {'stable_bounds':list(STABLE),'stable_gate':[-748,-746,124,127,772,772],
            'stable_approach':[[z,y] for z,y in APPROACH],'stable_boxes':[[ -753,-750,764,770],[-744,-742,764,770]],
            'gable_bounds':[-713,-705,143,148,782,798],'gable_access':[-711,135,782],
            'pilasters':pilasters,'facade_changes':dict(facade_changes),'changed_positions':len(changes),'rooms':rooms,
            'limits':['Horse dimensions and gate clearance checked geometrically; riding and jump escape require an in-game test','Armour stands, horses and inventory contents are not modelled','No operating redstone stable gate is claimed']}


def check(d,b):
    # Main riding passage: 3-wide, four completely clear blocks high except closed gates.
    for x in AISLE:
        for z in range(764,773):
            assert b[x,123,z][0]=='stone_bricks'
            for y in range(124,128):
                block=b.get((x,y,z))
                assert block is None or z==772 and y==124 and block[0]=='oak_fence_gate',(x,y,z,block)
    for (z,y),(nz,ny) in zip(APPROACH,APPROACH[1:]):assert nz==z+1 and abs(y-ny)<=1
    for z,y in APPROACH:
        for x in AISLE:
            assert (x,y,z) in b
            assert (x,y-1,z) in b,'Unsupported approach'
            for yy in range(y+1,y+5):assert (x,yy,z) not in b,(x,yy,z)
    for x0,x1,z0,z1 in ((-753,-750,764,770),(-744,-742,764,770)):
        assert x1-x0+1>=3 and z1-z0+1>=3
        for x in range(x0,x1+1):
            for z in (766,767,768):
                assert (x,123,z) in b
                for y in (124,125,126):assert (x,y,z) not in b
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
            'approach_steps_checked':len(APPROACH),'gable_ladder_continuous':True,'main_stairs_protected':True}
