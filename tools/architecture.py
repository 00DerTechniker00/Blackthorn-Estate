"""Revision 5.21: service buildings, bedroom fit-out and readable logistics."""

def enhance(d,b):
    previous=d['structure']['enhancements'];air=set(map(tuple,d.get('required_air',[])))
    def put(x,y,z,block,state='',group='stall_remise'):b[x,y,z]=(block,state,group);air.discard((x,y,z))
    def clear(x,y,z):b.pop((x,y,z),None);air.add((x,y,z))
    def foundation(x,y,z,group):
        t=d['terrain'];x0,_,z0,_=t['bounds'];ground=t['target_heights'][z-z0][x-x0]
        for yy in range(min(ground+1,y),y+1):put(x,yy,z,'cobblestone',group=group)
    # A twelve-by-eight stable / carriage house north of the arrival garden.
    for x in range(-752,-740):
        for z in range(763,771):
            foundation(x,125,z,'stall_remise')
            for y in range(126,130):
                if x in (-752,-741) or z in (763,770):
                    post=x in (-752,-747,-741) or z in (763,770) and x%4==0
                    put(x,y,z,'oak_log' if post else 'oak_planks','axis=y' if post else '')
                else:clear(x,y,z)
            roof=130+min(z-763,770-z)
            put(x,roof,z,'nether_brick_stairs',f'facing={"south" if z<767 else "north"},half=bottom,shape=straight,waterlogged=false')
    # Clear two stable gates and a tall four-wide carriage entrance.
    for x in (-750,-749):
        for y in (126,127,128):clear(x,y,770)
        put(x,126,770,'oak_fence_gate','facing=south,in_wall=false,open=false,powered=false')
    for x in range(-745,-741):
        for y in (126,127,128):clear(x,y,770)
    for z in (764,768):
        put(-751,126,z,'water_cauldron','level=3')
        put(-750,126,z,'hay_block','axis=y')
    put(-750,127,764,'hay_block','axis=y')
    put(-748,126,764,'barrel','facing=south,open=false')
    for z in range(764,770):
        if z not in (766,767):put(-747,126,z,'oak_fence','north=true,south=true,east=false,west=false,waterlogged=false')
    # Paved arrival yard, founded against the actual target surface.
    for x in range(-752,-740):
        for z in (771,772):
            foundation(x,125,z,'stall_remise')
            for y in (126,127,128):clear(x,y,z)
    # Four ascending steps connect the low service yard to the actual arrival level.
    # A western branch passes outside the portico columns and meets its open center.
    for z in range(773,783):
        y=min(129,126+z-773)
        for x in (-743,-742):
            foundation(x,y,z,'stall_remise')
            if z<777:put(x,y,z,'cobblestone_stairs','facing=south,half=bottom,shape=straight,waterlogged=false')
            for yy in range(y+1,y+4):clear(x,yy,z)
    for z in range(777,791):
        for x in (-745,-744):
            foundation(x,129,z,'stall_remise')
            for y in (130,131,132):clear(x,y,z)
    for x in (-745,-744,-743,-742):
        foundation(x,129,777,'stall_remise')
        for y in (130,131,132):clear(x,y,777)
    # Victorian orangery west of the existing garden pavilion.
    for x in range(-724,-712):
        for z in range(843,851):
            foundation(x,126,z,'orangerie')
            for y in range(127,132):
                edge=x in (-724,-713) or z in (843,850)
                pillar=(x in (-724,-720,-716,-713) and z in (843,850)) or x in (-724,-713) and z in (843,847,850)
                if pillar:put(x,y,z,'polished_blackstone_bricks',group='orangerie')
                elif edge:
                    pane='north=true,south=true,east=false,west=false' if x in (-724,-713) else 'north=false,south=false,east=true,west=true'
                    put(x,y,z,'white_stained_glass_pane',pane+',waterlogged=false','orangerie')
                else:clear(x,y,z)
            roof=132+min(z-843,850-z)
            put(x,roof,z,'polished_blackstone_bricks' if x%4==0 else 'white_stained_glass',group='orangerie')
    for z,hinge in ((846,'left'),(847,'right')):
        for y,half in ((127,'lower'),(128,'upper')):
            put(-713,y,z,'dark_oak_door',f'facing=east,half={half},hinge={hinge},open=false,powered=false','orangerie')
    for x in (-722,-718,-715):
        for z in (845,848):
            put(x,127,z,'barrel','facing=up,open=false','orangerie')
            put(x,128,z,'potted_fern',group='orangerie')
    for x in (-722,-716):
        put(x,135,846,'polished_blackstone_bricks',group='orangerie')
        for y in (133,134):put(x,y,846,'iron_chain','axis=y,waterlogged=false','orangerie')
        put(x,132,846,'polished_blackstone_bricks',group='orangerie')
        put(x,131,846,'spore_blossom',group='orangerie')
    for x in range(-712,-700):
        for z in (845,846,847):
            foundation(x,126,z,'orangerie')
            for y in (127,128,129):clear(x,y,z)
            if x==-701:put(x,126,z,'stone_brick_stairs','facing=west,half=bottom,shape=straight,waterlogged=false','orangerie')
    # Hidden lights underneath existing leaves, spaced so planting remains continuous.
    hidden=[]
    for (x,y,z),(bid,state,g) in list(b.items()):
        if bid=='oak_leaves' and g=='gartendeko' and z>=835 and (x+z)%5==0:
            put(x,y-1,z,'sea_lantern',group='gartenlicht');hidden.append([x,y-1,z])
    # Rebuild two existing hall chandeliers at their real ceiling anchors.
    for cx,cz in ((-694,782),(-694,798)):
        for x in range(cx-1,cx+2):
            for z in range(cz-1,cz+2):
                for y in range(139,144):
                    if b.get((x,y,z),('','',''))[2]=='halle':clear(x,y,z)
        for y in (142,143):put(cx,y,cz,'iron_chain','axis=y,waterlogged=false','hallen_prunk')
        put(cx,141,cz,'polished_blackstone',group='hallen_prunk')
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            put(cx+dx,141,cz+dz,'polished_blackstone',group='hallen_prunk')
            put(cx+dx,142,cz+dz,'anvil','facing=north','hallen_prunk')
            put(cx+dx,140,cz+dz,'soul_lantern','hanging=true,waterlogged=false','hallen_prunk')
    # Blank heraldic positions can be customized with the builders' banner patterns.
    for z,color in ((780,'black'),(784,'white'),(796,'red'),(800,'purple')):
        put(-711,134,z,color+'_wall_banner','facing=east','hallen_prunk')
    # Six canopies with unobstructed access from the foot of the existing beds.
    bedrooms=[]
    beds=[(p,v) for p,v in b.items() if v[0].endswith('_bed') and 'part=foot' in v[1] and v[2].startswith('res')]
    for (x,y,z),(bed,state,g) in beds:
        for xx in (x-1,x+1):
            for zz in (z-1,z+1):
                for yy in range(138,142):put(xx,yy,zz,'spruce_log','axis=y','wohn_details')
                banner=bed.replace('_bed','_wall_banner')
                out=zz-1 if zz<z else zz+1;facing='north' if zz<z else 'south'
                if (xx,140,out) not in b:put(xx,140,out,banner,f'facing={facing}','wohn_details')
        for xx in range(x-1,x+2):
            for zz in range(z-1,z+2):put(xx,142,zz,'spruce_slab','type=bottom,waterlogged=false','wohn_details')
        # Each hearth has an aligned hollow flue and a roof outlet, rather than a fake link.
        fx,fz=x+4,z+5 if z<790 else z-5;top=153+(len(bedrooms)%3)
        put(fx,137,fz,'hay_block','axis=y','wohn_details')
        put(fx,138,fz,'campfire','facing=south,lit=true,signal_fire=true,waterlogged=false','wohn_details')
        for yy in range(138,top+1):
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                # Room-side opening; the flue is closed on all four sides above the mantel.
                if yy<=139 and dz==(-1 if z<790 else 1):continue
                put(fx+dx,yy,fz+dz,'bricks',group='wohn_details')
            if yy>138:clear(fx,yy,fz)
        for dx in (-1,0,1):put(fx+dx,140,fz+(-1 if z<790 else 1),'polished_blackstone_bricks',group='wohn_details')
        front=fz+(-1 if z<790 else 1)
        put(fx,138,front,'iron_bars','north=false,south=false,east=true,west=true,waterlogged=false','wohn_details')
        for dx in (-1,1):
            for yy in (138,139):put(fx+dx,yy,front,'bricks',group='wohn_details')
        bedrooms.append({'room':g,'bed':[x,y,z],'fireplace':[fx,138,fz],'flue_top':top})
    # Chest fullness display: comparator directly powers the lamp inside its copper trim.
    put(-683,130,793,'polished_deepslate',group='liftanzeige')
    put(-683,131,793,'comparator','facing=south,mode=compare,powered=false','liftanzeige')
    put(-683,131,794,'redstone_lamp','lit=false','liftanzeige')
    for x in (-684,-682):put(x,131,794,'waxed_cut_copper',group='liftanzeige')
    put(-683,132,794,'waxed_cut_copper_slab','type=bottom,waterlogged=false','liftanzeige')
    put(-683,131,795,'waxed_copper_grate',group='liftanzeige')
    # Last-page selector on the existing lectern. Empty lectern -> closed door.
    put(-691,106,772,'lectern','facing=south,has_book=false,powered=false','buchsteuerung')
    put(-691,106,771,'comparator','facing=north,mode=compare,powered=false','buchsteuerung')
    put(-690,106,771,'redstone_block',group='buchsteuerung')
    put(-691,106,770,'polished_deepslate',group='buchsteuerung')
    put(-692,106,770,'redstone_wall_torch','facing=west,lit=true','buchsteuerung')
    wire=[(x,770) for x in range(-693,-699,-1)]+[(-698,z) for z in range(771,776)]
    for x,z in wire:
        put(x,105,z,'polished_deepslate',group='buchsteuerung')
        put(x,106,z,'redstone_wire','north=side,south=side,east=side,west=side,power=15','buchsteuerung')
    put(-698,106,775,'repeater','facing=south,delay=1,locked=false,powered=true','buchsteuerung')
    put(-696,106,775,'lever','face=floor,facing=south,powered=false','geheimtechnik')
    for (x,y,z),(bid,state,g) in list(b.items()):
        if bid=='redstone_wire' and g in ('buchsteuerung','geheimtechnik'):
            parts=[]
            for name,dx,dz in (('north',0,-1),('south',0,1),('east',1,0),('west',-1,0)):
                connect=b.get((x+dx,y,z+dz),('',))[0] in ('redstone_wire','repeater','redstone_wall_torch')
                parts.append(name+'='+('side' if connect else 'none'))
            put(x,y,z,bid,','.join(parts)+',power=15',g)
    d['_clearance_air']=[list(p) for p in sorted(air)]
    features=previous['features']+[
        {'group':'stall_remise','name':'Pferdestall und Remise','description':'12 × 8 Blöcke nördlich des Ankunftsgartens. Eichentragwerk, Bruchsteinsockel, Netherziegeldach, zwei Tränken, Heu und breite Kutschenöffnung.'},
        {'group':'orangerie','name':'Viktorianische Orangerie','description':'Schwarzsteinrahmen und Weißglas im Südgarten, bepflanzte Arbeitstische und Hängeblüten. Ein breiter Weg verbindet sie mit dem Garten.'},
        {'group':'gartenlicht','name':'Leuchtende Hecken','description':f'{len(hidden)} Meereslaternen unter bestehenden Hecken; kein Ersatz für eine aktuelle Spawn-Prüfung.'},
        {'group':'hallen_prunk','name':'Zwei neue Hallenkronleuchter','description':'Vorhandene Leuchten neu gefasst: Schwarzstein, aufliegende Ambosse und je vier Seelenlaternen. Aufhängung mit je zwei Kettenblöcken; vier austauschbare Bannerplätze an der Westwand.'},
        {'group':'wohn_details','name':'Sechs eingerichtete Suiten','description':'Himmelbetten mit farbigen Bannervorhängen und sechs Wandkamine mit eigenen, durchgehend hohlen Abzügen und Dachöffnungen.'},
        {'group':'liftanzeige','name':'Materiallift mit Inhaltsanzeige','description':'Komparator hinter der EG-Ausgabe, direkt angeschlossene Redstone-Lampe in gewachster Kupfereinfassung. Leuchtet, solange die Ausgabekiste Items enthält.'},
        {'group':'buchsteuerung','name':'Geheimtür mit Buchseitenwahl','description':'Auswertung des vorhandenen Pults. Signalstärke 15 schaltet die Kolben ab; der Wartungshebel kann die Tür geschlossen halten. Buch im Spiel einsetzen.'}]
    return {**previous,'title':'Orangerie, Stall, Suiten und Buchsteuerung','features':features,'bedrooms':bedrooms,'hidden_garden_lights':hidden,
        'sites':[{'name':'Stall und Remise','bounds':[-752,-741,125,133,763,770]},{'name':'Orangerie','bounds':[-724,-713,126,135,843,850]}],
        'limits':'Buch, Tiere und Einrichtungsbestände werden im Spiel ergänzt. Pferderüstungen gehören ins Lager; normale Rüstungsständer zeigen sie nicht an. Die Inhaltsanzeige zeigt aktuelle Items, sie speichert keine Ankunftsmeldung. Redstone, Kaminrauch und Spawn-Sicherheit sind im Spiel abzunehmen. Zusätzliche Aushubdaten und explizite Luftpositionen sind im Export enthalten.'}
