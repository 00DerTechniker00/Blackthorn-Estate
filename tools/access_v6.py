"""Twin water accesses and a lower secret salon. No edits to the finished Y95 floor."""
def enhance(b,air):
    def put(x,y,z,block,state='',group='v6_wasserzugang'):
        b[x,y,z]=(block,state,group);air.discard((x,y,z))
    def clear(x,y,z):b.pop((x,y,z),None);air.add((x,y,z))
    def twin(left,z,base,top,landings):
        # Up on the west, down on the east; front is south. Signs are anchored to side walls.
        for y in range(base,top+2):
            for x in range(left,left+5):
                for zz in range(z-1,z+2):
                    if x in (left,left+2,left+4) or zz in (z-1,z+1):put(x,y,zz,'gray_stained_glass')
                    else:clear(x,y,zz)
        for x in (left+1,left+3):
            put(x,base,z,'soul_sand' if x==left+1 else 'polished_deepslate')
            for y in range(base+1,top+1):
                if x==left+1:put(x,y,z,'bubble_column','drag=false')
                elif y<=base+2:put(x,y,z,'water','level=0')
                else:clear(x,y,z)
        for floor in landings:
            feet=max(floor+1,base+1)
            # Solid landing, two-high fluid stops and open front approach.
            for x in range(left,left+5):
                for zz in (z+2,z+3):
                    put(x,feet-1,zz,'polished_deepslate')
                    for y in (feet,feet+1,feet+2):clear(x,y,zz)
            for x,facing in ((left+1,'east'),(left+3,'west')):
                for y in (feet,feet+1):put(x,y,z+1,'spruce_wall_sign',f'facing={facing},waterlogged=false')
        return {'up':[left+1,base+1,z],'down':[left+3,base+1,z],'base':base,'top':top,'landings':landings,'sign_z':z+1}
    main=twin(-670,801,96,137,[95,101,107,113,121,127,135])
    # Shallow entry step above the existing finished floor, not a hole through it.
    for x in range(-670,-665):
        put(x,96,805,'polished_deepslate_stairs','facing=north,half=bottom,shape=straight,waterlogged=false')
        for y in (97,98,99):clear(x,y,805)
    # West-side lift foyer, outside the finished cellar perimeter.
    for y in range(81,101):
        for x in range(-715,-709):
            for z in range(778,784):
                if x in (-715,-710) or z in (778,783):put(x,y,z,'deepslate_bricks')
                else:clear(x,y,z)
    for x in range(-715,-709):
        for z in range(778,784):put(x,100,z,'deepslate_bricks')
    secret=twin(-715,779,80,97,[80,95])
    # Two-level connections to the original secret shaft/corridor and the lower library.
    for floor in (80,95):
        for x in (-711,-710):
            for z in (781,782):
                put(x,floor,z,'polished_deepslate')
                for y in range(floor+1,floor+4):clear(x,y,z)
    # Connect the lower foyer with the existing corridor north of it.
    for z in range(776,783):
        put(-710,80,z,'deepslate_tiles')
        for y in (81,82,83):clear(-710,y,z)
    # Larger room at the eastern end of the Y80 passage: 15x14 clear interior, 7 high.
    for x in range(-685,-668):
        for z in range(769,785):
            for y in range(80,89):
                edge=x in (-685,-669) or z in (769,784)
                if y==80:put(x,y,z,'polished_deepslate' if edge else 'dark_oak_planks',group='v6_geheimsalon')
                elif y==88:put(x,y,z,'deepslate_tiles',group='v6_geheimsalon')
                elif edge:put(x,y,z,'deepslate_bricks',group='v6_geheimsalon')
                else:clear(x,y,z)
    for x in (-686,-685):
        for z in (775,776,777):
            put(x,80,z,'polished_deepslate',group='v6_geheimsalon')
            for y in (81,82,83):clear(x,y,z)
    for x in range(-683,-670,2):
        for y in (81,82):put(x,y,770,'bookshelf',group='v6_geheimsalon')
    for x in range(-680,-674):put(x,81,782,'dark_oak_stairs','facing=south,half=bottom,shape=straight,waterlogged=false','v6_geheimsalon')
    for x in (-678,-677):put(x,81,780,'polished_andesite_slab','type=bottom,waterlogged=false','v6_geheimsalon')
    for z in (772,773):put(-670,81,z,'barrel','facing=west,open=false','v6_geheimsalon')
    for x in (-682,-677,-672):
        for z in (772,777,782):put(x,88,z,'sea_lantern',group='v6_geheimsalon')
    return {'house':main,'secret':secret,'salon_bounds':[-685,-669,80,88,769,784]}
