"""Revision 5.18: restrained east facade, accessible balcony and terrace arches."""

def enhance(d,b):
    def put(x,y,z,block,state='',group='poolfassade'):
        b[x,y,z]=(block,state,group)
    def vacant(x,y,z,block,state='',group='poolfassade'):
        if (x,y,z) not in b:put(x,y,z,block,state,group)
    # Retain both tall window bays, recess their glazing behind the projecting trim.
    for center in (780,800):
        for z in range(center-1,center+2):
            for y in range(131,143):
                if b.get((-658,y,z),('',))[0]=='glass_pane':
                    put(-658,y,z,'gray_stained_glass_pane','north=true,south=true,east=false,west=false,waterlogged=false')
            vacant(-657,130,z,'polished_blackstone_brick_slab','type=top,waterlogged=false')
        for z in (center-2,center+2):
            for y in range(130,143):
                vacant(-657,y,z,'polished_basalt','axis=y')
        for z in range(center-2,center+3):
            vacant(-657,143,z,'stone_brick_slab','type=bottom,waterlogged=false')
    # Project a proper balcony over the pool approach; floor height matches the OG.
    for x in range(-657,-654):
        for z in range(786,794):put(x,137,z,'polished_blackstone_bricks',group='panoramabalkon')
    for x in range(-657,-654):
        for z in (786,793):
            put(x,138,z,'iron_bars','north=false,south=false,east=true,west=true,waterlogged=false','panoramabalkon')
    for z in range(787,793):
        put(-655,138,z,'iron_bars','north=true,south=true,east=false,west=false,waterlogged=false','panoramabalkon')
    # Corner connections and stone terminals eliminate unconnected bar ends.
    for z in (786,793):put(-655,138,z,'chiseled_stone_bricks',group='panoramabalkon')
    for z,hinge in ((789,'left'),(790,'right')):
        for y,half in ((138,'lower'),(139,'upper')):
            put(-658,y,z,'dark_oak_door',f'facing=east,half={half},hinge={hinge},open=false,powered=false','panoramabalkon')
    for z in (788,791):
        for y in (138,139):put(-658,y,z,'polished_deepslate',group='panoramabalkon')
    for z in range(788,792):put(-658,140,z,'stone_bricks',group='panoramabalkon')
    # Corbels stand beside the existing pool door, never above the clear doorway.
    for z in (786,793):
        for x,y in ((-657,135),(-657,136),(-656,136)):
            vacant(x,y,z,'polished_blackstone_bricks',group='panoramabalkon')
    # Three load-bearing cross arches tie into the existing pool floor at Y 126.
    # Lowest footings are explicit masonry, not a claim that the cliff was surveyed.
    for z in (780,790,800):
        for zz in (z,z+1):
            for x in range(-652,-635):
                edge=min(x+652,-636-x)
                lower=115 if edge<2 else 119 if edge<4 else 122 if edge<6 else 124
                for y in range(lower,126):
                    material='mossy_cobblestone' if y<=118 and (x+y+zz)%4==0 else 'deepslate_bricks'
                    vacant(x,y,zz,material,group='poolboegen')
    # Extend exposed pier feet to the surveyed surface instead of leaving air gaps.
    terrain=d['terrain'];x0,_,z0,_=terrain['bounds']
    for z in (780,790,800):
        for zz in (z,z+1):
            for x in (-652,-651,-637,-636):
                ground=terrain['heights'][zz-z0][x-x0]
                for y in range(ground+1,115):vacant(x,y,zz,'deepslate_bricks',group='poolboegen')
    # Weather exposed existing external terrace masonry, preserving its structure.
    for (x,y,z),(block,state,g) in list(b.items()):
        if g=='terrasse' and 115<=y<=128 and block=='deepslate_bricks' and (x+2*z+y)%7==0:
            put(x,y,z,'mossy_cobblestone',state,'poolboegen')
    # Three modest chimney stacks anchored into existing roofs.
    chimneys=[]
    for x,z,top in ((-704,778,154),(-686,803,153),(-666,775,156)):
        footprint=[(xx,zz) for xx in (x,x+1) for zz in (z,z+1)]
        base=min(max(y for xx,y,zz in b if (xx,zz)==p) for p in footprint)
        for xx,zz in footprint:
            for y in range(base,top):put(xx,y,zz,'bricks',group='dach_kamine')
            put(xx,top,zz,'polished_blackstone_brick_slab','type=bottom,waterlogged=false','dach_kamine')
        put(x,top,z,'campfire','facing=north,lit=true,signal_fire=false,waterlogged=false','dach_kamine')
        chimneys.append({'x':x,'z':z,'base':base,'top':top})
    return {'title':'Poolfassade, Panoramabalkon und Klippenbögen',
        'features':[
            {'group':'poolfassade','name':'Gestaffelte Poolfassade','description':'Zwei hohe graue Glasfelder mit vorgezogenen Basaltpfeilern, dunklen Sohlbänken und steinernen Abschlüssen.'},
            {'group':'panoramabalkon','name':'Begehbarer Panoramabalkon','description':'Boden Y 137, drei Blöcke Ausladung und acht Blöcke Breite; neue OG-Doppeltür mit äußeren Anschlägen und Eisengeländer.'},
            {'group':'poolboegen','name':'Drei Stützbögen unter dem Pool','description':'Je zwei Blöcke tiefe Querbögen bei Z 780, 790 und 800; Tiefenschiefer und einzelne Moossteine, Pfeiler bis Y 115, bei tieferem vermessenem Gelände bis zur Oberfläche verlängert.'},
            {'group':'dach_kamine','name':'Drei gemauerte Dachkamine','description':'Unterschiedliche Abschlusshöhen Y 153–156; direkt auf dem Dach verankert, mit offenen Rauchstellen.'}],
        'chimneys':chimneys,
        'limits':'Bogenfüße berücksichtigen die mitgelieferte Oberflächenkarte; der Anschluss an den tatsächlichen Klippenfels muss vor Ort geprüft werden. Die Kamine sind Dachdetails ohne durchgehende Innenraum-Abzüge. Neue Lichtquellen sind kein Nachweis für Spawn-Sicherheit.'}
