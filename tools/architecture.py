"""Revision 5.19: west portal, accessible lookout, garden stair and cliff details."""

def enhance(d,b):
    previous=d['structure'].get('enhancements',{})
    def put(x,y,z,block,state='',group='prunkportal'):b[x,y,z]=(block,state,group)
    def clear(x,y,z):b.pop((x,y,z),None)
    # Two solid 2x2 front columns, with full support on the existing portico floor.
    for z0 in (784,795):
        for x in (-743,-742):
            for z in (z0,z0+1):
                for y in range(130,137):put(x,y,z,'smooth_basalt')
                for y,half in ((130,'bottom'),(136,'top')):
                    put(x,y,z,'polished_blackstone_stairs',f'facing=west,half={half},shape=straight,waterlogged=false')
    # Two-layer triangular pediment. Its center stays well above the entrance path.
    for x in (-744,-743):
        for z in range(783,798):
            top=138+(7-abs(z-790))//2
            for y in range(138,top+1):
                put(x,y,z,'polished_blackstone_bricks' if y==top or y==138 else 'chiseled_stone_bricks')
    for z in (789,790,791):put(-745,140,z,'waxed_cut_copper')
    put(-745,141,790,'gold_block')
    put(-745,139,790,'waxed_cut_copper')
    # Octagonal lookout with a real route from the upper west wing.
    cx,cz=-728,775
    footprint=[(x,z) for x in range(cx-3,cx+4) for z in range(cz-3,cz+4) if not(abs(x-cx)==3 and abs(z-cz)==3)]
    def inside(x,z):return (x,z) in footprint
    for x,z in footprint:
        for y in range(138,163):
            wall=not all(inside(x+dx,z+dz) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))
            if wall:put(x,y,z,'stone_bricks' if y<155 else 'chiseled_stone_bricks',group='aussichtsturm')
            else:clear(x,y,z)
    # West entry on OG; preserve the existing floor, remove the low slab just inside.
    for y,half in ((138,'lower'),(139,'upper')):
        put(cx-3,y,cz,'dark_oak_door',f'facing=west,half={half},hinge=left,open=false,powered=false','aussichtsturm')
        for x in range(cx-2,cx):clear(x,y,cz)
        clear(cx-4,y,cz)
    for y in range(138,165):
        put(cx+1,y,cz,'smooth_basalt',group='aussichtsturm')
        put(cx,y,cz,'ladder','facing=west,waterlogged=false','aussichtsturm')
    # Observation deck with a full perimeter; the ladder opening remains climbable.
    for x in range(cx-4,cx+5):
        for z in range(cz-4,cz+5):
            if (x,z)==(cx,cz):continue
            put(x,163,z,'polished_blackstone_bricks',group='aussichtsturm')
            if abs(x-cx)==4 or abs(z-cz)==4:
                put(x,164,z,'stone_brick_wall','up=true,north=low,south=low,east=low,west=low,waterlogged=false','aussichtsturm')
    # Oxidized copper roof held by four posts above the deck, without blocking its route.
    for dx in (-2,2):
        for dz in (-2,2):
            for y in (164,165):put(cx+dx,y,cz+dz,'smooth_basalt',group='aussichtsturm')
    for y,radius in ((166,3),(167,3),(168,2),(169,1),(170,0)):
        for x in range(cx-radius,cx+radius+1):
            for z in range(cz-radius,cz+radius+1):
                block='waxed_oxidized_cut_copper';state=''
                if radius and (abs(x-cx)==radius or abs(z-cz)==radius):
                    facing=('east' if x<cx else 'west') if abs(x-cx)==radius else ('south' if z<cz else 'north')
                    block='waxed_oxidized_cut_copper_stairs';state=f'facing={facing},half=bottom,shape=straight,waterlogged=false'
                put(x,y,z,block,state,group='aussichtsturm')
    put(cx,171,cz,'lightning_rod','facing=up,powered=false,waterlogged=false','aussichtsturm')
    # Tall slit windows, kept clear of the central ladder support.
    for y in range(150,160):
        for z in (cz-3,cz+3):put(cx,y,z,'gray_stained_glass','', 'aussichtsturm')
    # Twin garden stair: central landing, outward flights, joined lower garden court.
    for x in range(-708,-701):
        for z in range(832,837):put(x,129,z,'stone_bricks',group='gartentreppe')
    for x,hinge in ((-706,'right'),(-705,'left')):
        for y,half in ((130,'lower'),(131,'upper')):
            put(x,y,831,'dark_oak_door',f'facing=south,half={half},hinge={hinge},open=false,powered=false','gartentreppe')
        for z in (830,832):
            for y in (130,131):clear(x,y,z)
    for side in (-1,1):
        for step in range(3):
            x=(-709-step) if side==-1 else (-701+step);y=129-step
            for z in range(834,837):put(x,y,z,'stone_brick_stairs',f'facing={"east" if side==-1 else "west"},half=bottom,shape=straight,waterlogged=false','gartentreppe')
            for z in (833,837):put(x,y+1,z,'stone_brick_wall','up=true,north=low,south=low,east=low,west=low,waterlogged=false','gartentreppe')
    for x in list(range(-714,-711))+list(range(-698,-695)):
        for z in range(834,840):put(x,126,z,'stone_bricks',group='gartentreppe')
    for x in range(-714,-695):put(x,126,839,'stone_bricks',group='gartentreppe')
    for x in range(-708,-701):put(x,130,837,'stone_brick_wall','up=true,north=low,south=low,east=low,west=low,waterlogged=false','gartentreppe')
    for x in range(-698,-695):
        put(x,126,840,'stone_brick_stairs','facing=north,half=bottom,shape=straight,waterlogged=false','gartentreppe')
        put(x,125,841,'stone_bricks',group='gartentreppe')
    # Foundation beneath every landing and stair, respecting existing basement work.
    T=d['terrain'];x0,_,z0,_=T['bounds']
    for (x,y,z),(bid,state,g) in list(b.items()):
        if g=='gartentreppe' and (bid=='stone_bricks' or bid.endswith('_stairs')):
            ground=T['target_heights'][z-z0][x-x0]
            for yy in range(ground+1,y):
                if (x,yy,z) not in b:put(x,yy,z,'deepslate_bricks',group='gartentreppe')
    # Flared feet only on the exposed low northeastern cliff; avoid burying waterfalls.
    for z in (780,790,800):
        for x in (-652,-636):
            for dx in range(-1,2):
                for zz in range(z-1,z+3):
                    ground=T['heights'][zz-z0][x+dx-x0]
                    for y in range(ground+1,117):
                        if (x+dx,y,zz) not in b:put(x+dx,y,zz,'deepslate_tiles' if y<115 else 'cobbled_deepslate',group='klippenfuesse')
    # Two bounded spillway channels; their water is independent of the swimming pool.
    for z in (780,783):
        for x in range(-635,-632):
            put(x,124,z,'prismarine_bricks',group='kaskaden')
            put(x,125,z,'water','level=0' if x==-635 else 'level=1','kaskaden')
            for zz in (z-1,z+1):put(x,125,zz,'deepslate_bricks',group='kaskaden')
        x=-632;ground=T['heights'][z-z0][x-x0]
        for y in range(ground+1,126):put(x,y,z,'water','level=8','kaskaden')
        # Catch basin raised above the surveyed surface, its wall contains lower spreading.
        for xx in range(x-1,x+2):
            for zz in range(z-1,z+2):
                put(xx,ground,zz,'prismarine_bricks',group='kaskaden')
                if (xx,zz)!=(x,z):put(xx,ground+1,zz,'deepslate_bricks',group='kaskaden')
    # Recessed, survival-buildable light panels; no claim of directional Minecraft light.
    for z in (783,797):
        put(-742,130,z,'sea_lantern',group='fassadenlicht')
        put(-743,130,z,'spruce_trapdoor','facing=west,half=bottom,open=true,powered=false,waterlogged=false','fassadenlicht')
    features=previous.get('features',[])+[
        {'group':'prunkportal','name':'Monumentales Westportal','description':'Zwei 2×2-Säulen, Schwarzstein-Kapitelle, zweilagiger Dreiecksgiebel und Kupfer-Gold-Wappen über dem freien Ankunftsweg.'},
        {'group':'aussichtsturm','name':'Begehbarer Aussichtsturm','description':'OG-Zugang bei X −731 / Z 775, Leiter bis zur Galerie Y 163, steinerne Balustrade und gewachste oxidierte Kupferkrone bis Y 171.'},
        {'group':'gartentreppe','name':'Zweiflügelige Südgartentreppe','description':'Neue Doppeltür bei Z 831; obere Terrasse Y 129, zwei seitliche Läufe und gemeinsamer Gartenweg auf Y 126 bis zum Anschluss auf Y 125.'},
        {'group':'klippenfuesse','name':'Verbreiterte Bogenfüße','description':'Nach unten ausgestellte Sockel aus Tiefenschiefer-Fliesen und Bruchtiefenschiefer an den freiliegenden Pfeilerfüßen.'},
        {'group':'kaskaden','name':'Zwei Klippenkaskaden','description':'Separate, eingefasste Speier bei Z 780 und 783 mit Fallwasser und Auffangmulden; unabhängig vom Schwimmbecken.'},
        {'group':'fassadenlicht','name':'Verdeckte Portalbeleuchtung','description':'Zwei Meereslaternen hinter Fichtenblenden seitlich der Frontsäulen.'}]
    return {'title':'Herrschaftliches Westportal, Aussichtsturm und Gartentreppe','features':features,
        'limits':'Wasserfluss, Lichtwirkung und Laufwege sind im Spiel abzunehmen. Lichtquellen strahlen in Minecraft nicht gerichtet nach oben. Der Turm ist per Leiter erreichbar; ein Uhrenmechanismus ist nicht eingebaut. Zusätzliche Aushubpositionen für Garten und Kaskaden stehen in architektur_erdarbeiten.csv.'}
