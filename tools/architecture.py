"""Revision 5.20: secret passage, item lift, pool lighting and a surveyed shore route."""
from cliff_path import route

def enhance(d,b):
    previous=d['structure'].get('enhancements',{})
    air=set()
    def put(x,y,z,block,state='',group='materiallift'):
        b[x,y,z]=(block,state,group);air.discard((x,y,z))
    def clear(x,y,z):b.pop((x,y,z),None);air.add((x,y,z))
    def floor(x,y,z,group):put(x,y,z,'polished_deepslate',group=group)
    # Keep the ladder shaft; add a fully enclosed bubble tube alongside its east face.
    for y in range(106,134):
        for x in range(-686,-683):
            for z in range(789,792):
                if x==-686:continue # shared existing shaft wall
                put(x,y,z,'glass')
        put(-685,y,790,'bubble_column','drag=false')
    put(-685,105,790,'soul_sand')
    # Floor-106 automatic dropper, with subtract-comparator feedback clock.
    put(-685,106,789,'dropper','facing=south,triggered=false')
    put(-685,107,789,'hopper','facing=down,enabled=true')
    put(-685,108,789,'chest','facing=north,type=single,waterlogged=false')
    put(-685,106,788,'comparator','facing=north,mode=subtract,powered=false')
    put(-685,106,786,'repeater','facing=north,delay=2,locked=false,powered=false')
    wires=[(-685,787),(-685,785),(-684,785),(-683,785),(-683,786),(-683,787),(-684,787),(-684,788),(-683,789),(-684,789)]
    for x,z in wires:
        floor(x,105,z,'materiallift');put(x,106,z,'redstone_wire','north=side,south=side,east=side,west=side,power=0')
    for x,z in ((-685,788),(-685,786)):floor(x,105,z,'materiallift')
    floor(-683,105,788,'materiallift')
    put(-683,106,788,'redstone_wire','north=side,south=none,east=none,west=side,power=0')
    put(-684,106,788,'repeater','facing=west,delay=1,locked=false,powered=false')
    # Top overflow over a hopper into a chest, with a roof against item escape.
    for x in (-684,-683):
        put(x,132,790,'water','level=1' if x==-684 else 'level=2')
        put(x,133,790,'glass')
        for z in (789,791):put(x,132,z,'glass')
    put(-685,133,790,'glass')
    put(-683,131,790,'hopper','facing=south,enabled=true')
    put(-683,131,791,'hopper','facing=south,enabled=true')
    put(-684,131,790,'glass')
    put(-683,131,792,'chest','facing=south,type=single,waterlogged=false')
    put(-682,132,790,'glass')
    # Two-high piston bookshelf, initially closed. The retracting panels slide west.
    for y in (106,107):
        put(-699,y,778,'sticky_piston','facing=east,extended=true','geheimtechnik')
        put(-698,y,778,'piston_head','facing=east,type=sticky,short=false','geheimtechnik')
        put(-697,y,778,'bookshelf',group='geheimtechnik')
    # A side turn behind the sliding panel leads to a short descending ladder.
    for y in (106,107):clear(-697,y,779)
    # Lever branches to a lower repeater and a separately supported upper repeater.
    wire_positions=[(-696,106,776),(-697,106,776),(-698,106,776),(-699,106,776),(-700,106,776),(-701,106,776),(-701,106,777),(-701,107,778)]
    for x,y,z in wire_positions:
        floor(x,y-1,z,'geheimtechnik');put(x,y,z,'redstone_wire','north=side,south=side,east=side,west=side,power=15','geheimtechnik')
    for x,y,z,facing in ((-699,106,777,'south'),(-700,107,778,'east')):
        floor(x,y-1,z,'geheimtechnik');put(x,y,z,'repeater',f'facing={facing},delay=1,locked=false,powered=true','geheimtechnik')
    floor(-696,105,775,'geheimtechnik')
    put(-696,106,775,'lever','face=floor,facing=south,powered=true','geheimtechnik')
    # Shaft descends outside the module bounding box; lower corridor enters the service gap.
    for y in range(81,104):
        put(-698,y,768,'deepslate_bricks',group='fluchtgang')
        put(-697,y,768,'ladder','facing=east,waterlogged=false','fluchtgang')
    for x in range(-697,-686):
        floor(x,80,768,'fluchtgang')
        for y in (81,82,83):
            if x!=-697:clear(x,y,768)
        for z in (767,769):put(x,81,z,'deepslate_bricks',group='fluchtgang')
    for z in (769,770):
        floor(-687,80,z,'fluchtgang')
        for y in (81,82,83):clear(-687,y,z)
    # Low passage passes beneath the piston wiring and joins the lower shaft.
    for y in range(101,107):
        put(-698,y,779,'deepslate_bricks',group='fluchtgang')
        put(-697,y,779,'ladder','facing=east,waterlogged=false','fluchtgang')
    for z in range(769,780):
        floor(-697,100,z,'fluchtgang')
        for y in (101,102,103):
            if z!=779:clear(-697,y,z)
    for y in (104,105):put(-697,y,768,'deepslate_bricks',group='fluchtgang')
    # Separate dry lighting conduits below the terrace; six lamps face into the pool.
    for z in range(777,804):
        floor(-657,127,z,'poollicht')
        put(-657,128,z,'redstone_wire','north=side,south=side,east=none,west=none,power=0','poollicht')
    for z,facing in ((781,'north'),(795,'south')):
        put(-657,128,z,'repeater',f'facing={facing},delay=1,locked=false,powered=false','poollicht')
    for bus,repeat_z,lamp_z,facing in ((777,778,779,'south'),(803,802,801,'north')):
        for x in range(-657,-637):
            floor(x,127,bus,'poollicht')
            put(x,128,bus,'redstone_wire','north=none,south=none,east=side,west=side,power=0','poollicht')
        for x in (-653,-645):put(x,128,bus,'repeater','facing=east,delay=1,locked=false,powered=false','poollicht')
        for x in (-650,-644,-638):
            floor(x,127,repeat_z,'poollicht')
            put(x,128,repeat_z,'repeater',f'facing={facing},delay=1,locked=false,powered=false','poollicht')
            put(x,128,lamp_z,'redstone_lamp','lit=false','poollicht')
    put(-657,129,787,'polished_deepslate',group='poollicht')
    put(-657,130,787,'lever','face=floor,facing=south,powered=false','poollicht')
    # Shore route is generated against the supplied natural surface, not an assumed ocean.
    path=route(d['terrain']);walk={(x,z):y for x,y,z in path}
    for i,(x,y,z) in enumerate(path):
        if i+1<len(path) and path[i+1][1]<y:
            nx,_,nz=path[i+1];facing='west' if nx>x else 'east' if nx<x else 'north' if nz>z else 'south'
            put(x,y,z,'cobblestone_stairs',f'facing={facing},half=bottom,shape=straight,waterlogged=false','klippenpfad')
        else:put(x,y,z,'tuff',group='klippenpfad')
        for yy in range(y+1,y+4):clear(x,yy,z)
    # Side walkways widen level sections; fences never occupy the reserved path columns.
    for x,y,z in path:
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            q=x+dx,z+dz
            if q not in walk:
                ground=d['terrain']['heights'][q[1]-d['terrain']['bounds'][2]][q[0]-d['terrain']['bounds'][0]]
                if abs(ground-y)<=1:
                    put(q[0],y,q[1],'cobblestone',group='klippenpfad')
                    put(q[0],y+1,q[1],'spruce_fence','north=true,south=true,east=true,west=true,waterlogged=false','klippenpfad')
    # Boat house: west door on the path, east water opening and an interior water berth.
    for x in range(-580,-571):
        for z in range(750,759):
            rim=x<=-578 or z in (750,751,757,758)
            if rim:put(x,63,z,'oak_planks',group='bootshaus')
            else:
                put(x,62,z,'water','level=0','bootshaus')
                for y in (63,64,65):clear(x,y,z)
            for y in (64,65,66):
                if x==-580 or z in (750,758):put(x,y,z,'oak_planks',group='bootshaus')
            roof=67+min(z-750,758-z)//2
            put(x,roof,z,'nether_brick_stairs',f'facing={"south" if z<754 else "north"},half=bottom,shape=straight,waterlogged=false','bootshaus')
    for y,half in ((64,'lower'),(65,'upper')):put(-580,y,754,'oak_door',f'facing=west,half={half},hinge=left,open=false,powered=false','bootshaus')
    # Moist, planted footing accents kept off all walking routes.
    for x,z in ((-637,779),(-635,782)):
        ground=d['terrain']['heights'][z-d['terrain']['bounds'][2]][x-d['terrain']['bounds'][0]]
        put(x,ground,z,'moss_block',group='klippenvegetation')
    # Explicit wire shapes reflect their modeled neighbours, including the raised branch.
    components={'redstone_wire','repeater','comparator','lever','dropper'}
    for (x,y,z),(block,state,g) in list(b.items()):
        if block!='redstone_wire' or g not in ('poollicht','materiallift','geheimtechnik'):continue
        parts=[]
        for direction,dx,dz in (('north',0,-1),('south',0,1),('east',1,0),('west',-1,0)):
            value='none'
            if b.get((x+dx,y,z+dz),('',))[0] in components:value='side'
            elif b.get((x+dx,y+1,z+dz),('',))[0]=='redstone_wire':value='up'
            elif b.get((x+dx,y-1,z+dz),('',))[0]=='redstone_wire':value='side'
            parts.append(direction+'='+value)
        put(x,y,z,block,','.join(parts)+(',power=15' if g=='geheimtechnik' else ',power=0'),g)
    d['_clearance_air']=[list(p) for p in sorted(air)]
    features=previous.get('features',[])+[
        {'group':'geheimtechnik','name':'Kolben-Bücherregal','description':'Zwei bewegliche Regalblöcke bei X −697 / Z 778. Bodenhebel X −696 / Y 106 / Z 775, getrennte Repeater für beide Kolben; geschlossen modelliert.'},
        {'group':'fluchtgang','name':'Geheimer Technikzugang','description':'Verdeckte Leiter und Unterquerung der Schaltung auf Y 100; weiter bis Y 81 bei X −697 / Z 768. Der untere Gang liegt nördlich der Litematic-Module und endet an deren Servicelücke X −687.'},
        {'group':'materiallift','name':'Automatischer Material-Aufstieg','description':'Separate Blasensäule neben der Wartungsleiter. Einwurf X −685 / Y 108 / Z 789; Hopper, Dropper und Komparator-Taktgeber. Ausgabe im EG X −683 / Y 131 / Z 792.'},
        {'group':'poollicht','name':'Schaltbare Poolbeleuchtung','description':'Sechs Lampen in den Beckenwänden. Hebel neben dem Poolausgang bei X −657 / Y 130 / Z 787; trockene Leitungen mit Repeatern unter der Terrasse.'},
        {'group':'klippenpfad','name':'Vermessener Klippenabstieg','description':f'{len(path)} Wegpositionen vom nordöstlichen Terrassenrand Y 129 bis zum Ufer auf Y 63; maximal ein Block Höhenunterschied je Schritt.'},
        {'group':'bootshaus','name':'Viktorianischer Bootsschuppen','description':'Eichenbau mit Netherziegeldach, Westzugang und offener Wasserbucht im Osten bei X −580…−572 / Z 750…758.'},
        {'group':'klippenvegetation','name':'Moos an den Bogenfüßen','description':'Zwei kleine Moosakzente an den feuchten Sockeln; ohne Bewuchs auf den Gehwegen.'}]
    return {'title':'Geheimgang, Materiallift, Poollicht und Uferweg','features':features,'path':[list(p) for p in path],
        'limits':'Redstone, Kolbentür und Wassertransport sind konstruktiv modelliert, aber nicht im Spiel getestet. Der NBT-Export enthält explizite Luftpositionen für die neuen Durchgänge. Beim manuellen Bauen die Luft-/Aushubliste vorab abarbeiten. Der Lift transportiert Item-Entitäten, auch gefüllte Shulkerboxen; er ist kein Shulker-Unloader. Der Bootsschuppen liegt an der vermessenen nordöstlichen Wasserfläche, nicht an der trockenen Südklippe.'}
