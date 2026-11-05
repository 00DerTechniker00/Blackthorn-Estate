"""Revision 5.22: vineyard terraces, shore lights and an edge-triggered delivery gong."""

def enhance(d,b):
    previous=d['structure']['enhancements'];air=set(map(tuple,d.get('required_air',[])))
    def put(x,y,z,block,state='',group='weinberg'):b[x,y,z]=(block,state,group);air.discard((x,y,z))
    def clear(x,y,z):b.pop((x,y,z),None);air.add((x,y,z))
    t=d['terrain'];tx,_,tz,_=t['bounds']
    # Three planted terraces, with a separate unobstructed stair along their west edge.
    for z0,y in ((853,125),(858,124),(863,123)):
        for x in range(-710,-696):
            for z in range(z0,z0+4):
                ground=t['target_heights'][z-tz][x-tx]
                for yy in range(min(y,ground+1),y):put(x,yy,z,'cobblestone')
                put(x,y,z,'mossy_cobblestone' if z==z0+3 else 'grass_block')
                for yy in (y+1,y+2,y+3):clear(x,yy,z)
            for z in (z0+1,z0+2):
                if (x+710)%4==0:put(x,y+1,z,'spruce_fence','north=true,south=true,east=true,west=true,waterlogged=false')
                if (x+710)%4!=3:put(x,y+2,z,'oak_leaves','persistent=true,distance=1,waterlogged=false')
        # Walk aisle across the lower edge of each terrace stays open.
    for z in range(850,868):
        y=126 if z<853 else 125 if z<858 else 124 if z<863 else 123
        for x in (-712,-711):
            ground=t['target_heights'][z-tz][x-tx]
            for yy in range(min(y,ground+1),y):put(x,yy,z,'cobblestone')
            put(x,y,z,'cobblestone_stairs' if z in (852,857,862) else 'cobblestone',
                'facing=north,half=bottom,shape=straight,waterlogged=false' if z in (852,857,862) else '')
            for yy in (y+1,y+2,y+3):clear(x,yy,z)
    # Link the vineyard stair to the existing south garden/orangery walkway at Y 126.
    for z in (848,849):
        for x in (-712,-711):
            put(x,126,z,'cobblestone')
            for y in (127,128,129):clear(x,y,z)
    # Two shore lantern brackets outside the boat entry and water berth.
    for z in (750,758):
        for y in (64,65,66):put(-572,y,z,'spruce_fence',f'north=false,south=false,east={str(y==66).lower()},west=false,waterlogged=false','steglicht')
        put(-571,66,z,'spruce_fence','north=false,south=false,east=false,west=true,waterlogged=false','steglicht')
        put(-571,65,z,'soul_lantern','hanging=true,waterlogged=false','steglicht')
        put(-571,63,z,'oak_planks',group='steglicht')
        put(-572,63,z,'oak_planks',group='steglicht')
    # Real shelf blocks remain empty until the supplied setup commands fill their slots.
    shelves=[]
    for x,z,amount in ((-694,778,1),(-691,778,2),(-688,778,4),(-691,781,6)):
        state='facing=south,'+','.join(f'slot_{i}_occupied=false' for i in range(6))
        put(x,106,z,'chiseled_bookshelf',state,'bibliothek_details')
        shelves.append({'position':[x,106,z],'books':amount})
    # Display alcoves: only the setup function creates and equips the actual entities.
    stands=[]
    for x,material in ((-744,'leather'),(-742,'diamond')):
        put(x,125,764,'polished_blackstone_bricks',group='ruestungsnischen')
        stands.append({'position':[x+.5,126,764.5],'armor':material,'tag':'blackthorn_display_'+material})
    # Rising-edge monoflop from the strongly powered inventory indicator lamp.
    # Main input is immediate; a delayed, boosted side input suppresses sustained power.
    for x,z in ((-683,795),(-683,796),(-683,797),(-683,798),(-684,796),(-685,796),(-686,796),(-686,797),(-685,797),(-684,797)):
        put(x,130,z,'polished_deepslate',group='liefergong')
    put(-683,131,795,'repeater','facing=south,delay=1,locked=false,powered=false','liefergong')
    put(-683,131,797,'comparator','facing=south,mode=subtract,powered=false','liefergong')
    put(-685,131,796,'repeater','facing=west,delay=4,locked=false,powered=false','liefergong')
    put(-684,131,797,'repeater','facing=east,delay=1,locked=false,powered=false','liefergong')
    wires=[(-683,796),(-683,798),(-684,796),(-686,796),(-686,797),(-685,797)]
    for x,z in wires:put(x,131,z,'redstone_wire','north=side,south=side,east=side,west=side,power=0','liefergong')
    put(-683,130,799,'gold_block',group='liefergong')
    put(-683,131,799,'note_block','instrument=bell,note=12,powered=false','liefergong')
    clear(-683,132,799)
    # Cabinet trim stays off the note block's open sound space and off the old stair run.
    put(-682,131,799,'waxed_cut_copper',group='liefergong')
    for x,z in wires:
        parts=[]
        for name,dx,dz in (('north',0,-1),('south',0,1),('east',1,0),('west',-1,0)):
            component=b.get((x+dx,131,z+dz),('',))[0]
            parts.append(name+'='+('side' if component in ('redstone_wire','repeater','comparator','note_block') else 'none'))
        put(x,131,z,'redstone_wire',','.join(parts)+',power=0','liefergong')
    d['_clearance_air']=[list(p) for p in sorted(air)]
    d['decoration_setup']={'armor_stands':stands,'bookshelves':shelves,'entities_in_structure':False,'shelves_prefilled_in_structure':False}
    features=[
        {'group':'weinberg','name':'Terrassierter Südweinberg','description':'Drei begrünte Stufen auf Y 125, 124 und 123 mit Fichtenspalieren, Laubreben und einem eigenen seitlichen Treppenweg.'},
        {'group':'steglicht','name':'Seelenlaternen am Bootssteg','description':'Zwei fest verankerte Fichtenhalter außerhalb der östlichen Wasserzufahrt; freie Bootsbucht bleibt erhalten.'},
        {'group':'ruestungsnischen','name':'Ausgestattete Remisen-Nischen','description':'Zwei reservierte Plätze für Leder- und Diamantrüstung. Rüstungsständer werden mit remise_bibliothek_5.22.mcfunction im Spiel erzeugt und ausgestattet.'},
        {'group':'bibliothek_details','name':'Lebendige Bibliotheksregale','description':'Vier gemeißelte Regale; Einrichtungsbefehle bestücken sie mit 1, 2, 4 und 6 Büchern. Der Struktur-Export enthält die leeren Regale.'},
        {'group':'liefergong','name':'Einmaliger Liefergong','description':'Subtraktions-Monoflop am Inhaltsanzeiger: ein Ton bei leer → gefüllt. Beim Leeren kein zweiter Ton; keine Erkennung bestimmter Itemtypen.'}]+previous['features']
    return {**previous,'title':'Südweinberg, Steglicht und Liefergong','features':features,
        'limits':'Rüstungsständer und Bücherbestände brauchen die mitgelieferte Einrichtung im Spiel. Der Gong signalisiert nur leer → gefüllt; weitere Lieferungen in eine bereits gefüllte Kiste bleiben ohne Ton. Schaltung und Bootsdurchfahrt sind im Spiel abzunehmen.'}
