"""Pool detailing and compact garden terrace; cellar geometry is excluded."""
def enhance(d,b,air):
    changed=set();protected={p:v for p,v in b.items() if p[1]<=124 and -710<=p[0]<=-658 and 766<=p[2]<=814}
    def put(x,y,z,block,state='',group='v6_garten'):
        p=x,y,z;b[p]=(block,state,group);air.discard(p);changed.add(p)
    # Pool bottom and existing terrace surfaces; no changes to the door or load-bearing cliffs.
    for (x,y,z),(block,state,g) in list(b.items()):
        if y==129 and -657<=x<=-638 and 770<=z<=810 and g in ('terrasse','pool') and block in ('stone_bricks','deepslate_tiles','polished_deepslate'):
            border=x in (-657,-638) or z in (770,810,778,802)
            put(x,y,z,'polished_deepslate' if border else 'smooth_sandstone',group='v6_pool')
    for x in range(-651,-640):
        for z in range(780,801):
            assert b[x,127,z][0]=='water' and b[x,128,z][0]=='water'
            put(x,126,z,'prismarine_bricks' if x in (-651,-641) or z in (780,800) else 'dark_prismarine',group='v6_pool')
            put(x,129,z,'water','level=0',group='v6_pool')
    for x in (-649,-645):
        for z in (783,790,797):put(x,126,z,'sea_lantern',group='v6_pool')
    for z in range(788,793):
        put(-651,129,z,'smooth_quartz_stairs','facing=west,half=bottom,shape=straight,waterlogged=true','v6_pool')
        put(-650,128,z,'smooth_quartz_stairs','facing=west,half=bottom,shape=straight,waterlogged=true','v6_pool')
    # Seats stay clear of the central west-to-east passage and the pool water.
    for z,facing in ((775,'north'),(806,'south')):
        for x in (-652,-647,-642):
            for xx in (x,x+1):
                assert (xx,130,z) not in b
                put(xx,130,z,'dark_oak_stairs',f'facing={facing},half=bottom,shape=straight,waterlogged=false','v6_pool')
    for x in (-649,-644):
        for z in (775,806):
            if (x,130,z) not in b:
                put(x,130,z,'polished_blackstone_brick_slab','type=bottom,waterlogged=false','v6_pool')
    # Rose terrace west of the orangery: only a 9x9 patch, tied into the existing northern gravel path.
    T=d['terrain'];x0,_,z0,_=T['bounds']
    def surface(x,z,y,block):
        old=T['target_heights'][z-z0][x-x0]
        for yy in range(min(old,y),y):
            if (x,yy,z) not in b:put(x,yy,z,'dirt')
        for yy in range(y+1,old+1):b.pop((x,yy,z),None);air.add((x,yy,z))
        put(x,y,z,block)
        T['target_heights'][z-z0][x-x0]=y;T['target_surface_blocks'][z-z0][x-x0]=block
    for x in range(-736,-727):
        for z in range(841,850):
            edge=x in (-736,-728) or z in (841,849)
            surface(x,z,125,'stone_bricks' if edge else 'gravel')
    for z,y in ((838,126),(839,125),(840,125),(841,125)):
        for x in range(-733,-730):
            surface(x,z,y,'stone_bricks' if z<840 else 'gravel')
            if z<840:put(x,y,z,'stone_brick_stairs','facing=north,half=bottom,shape=straight,waterlogged=false')
    for x in (-735,-729):
        for z in range(843,848):
            surface(x,z,125,'grass_block')
            put(x,126,z,'allium' if z%2 else 'oxeye_daisy')
    # Open pergola: four supported uprights, connected side beams and open roof slats.
    for x in (-735,-729):
        for z in (842,848):
            for y in range(126,130):put(x,y,z,'dark_oak_fence',group='v6_garten')
    for x in range(-735,-728):
        for z in range(842,849):
            if z%2==0 or x in (-735,-729):put(x,130,z,'dark_oak_slab','type=bottom,waterlogged=false')
    for x in range(-733,-730):put(x,126,848,'dark_oak_stairs','facing=south,half=bottom,shape=straight,waterlogged=false')
    # Low clipped shrubs and hidden lighting, outside the seating and entry axes.
    for x in (-736,-728):
        for z in (843,845,847):
            put(x,125,z,'sea_lantern');T['target_surface_blocks'][z-z0][x-x0]='sea_lantern'
            put(x,126,z,'azalea_leaves','distance=1,persistent=true,waterlogged=false')
    # Existing south-garden beds: preserve all gravel and stairs.
    for x in range(-699,-677):
        for z in (841,845):
            base=b.get((x,125,z));above=b.get((x,126,z))
            if T['target_surface_blocks'][z-z0][x-x0]!='grass_block':continue
            if base and base[2] not in ('terraform_auffuellung','terraform_oberflaeche'):continue
            if above and above[0] not in ('allium','oxeye_daisy','cornflower'):continue
            if x%3!=0:put(x,126,z,'allium' if x%2 else 'oxeye_daisy')
    assert all(b.get(p)==v for p,v in protected.items()),'Cellar touched by outdoor work'
    d['outdoor_sites'][1]['text']='Südgarten mit freien Kieswegen, geordneten Blütenbeeten, Orangerie und Pavillon. Westlich ergänzt eine kleine Rosenterrasse mit offener Pergola und Sitzbank den Rundgang.'
    d['outdoor_sites'].append({'name':'Rosenterrasse & Pergola','x':-732,'y':125,'z':845,'text':'Kompakte Terrasse mit offenem Holzgerüst, Blütenstreifen, verdecktem Licht und Anschluss an den vorhandenen Kiesweg.'})
    return {'positions':len(changed),'pool_bounds':[-651,-641,126,129,780,800],'rose_terrace':[-736,-728,125,130,841,849],'steps':[[x,z] for x in range(-733,-730) for z in (838,839)]}
