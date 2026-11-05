"""Revision 5.24: paired upper hall gable windows with recessed lancet glazing."""

def enhance(d,b):
    previous=d['structure']['enhancements'];air=set(map(tuple,d.get('required_air',[])))
    def put(x,y,z,block,state=''):
        if (x,y,z) in air:raise ValueError('Gable window conflicts with reserved air')
        b[x,y,z]=(block,state,'halle_giebelfenster')
    windows=[]
    for wall,outside,side in ((-714,-715,'West'),(-676,-675,'Ost')):
        # Keep the roof outline; the stepped head fits inside the original gable.
        for z in range(787,794):
            top=154 if z==790 else 153 if abs(z-790)==1 else 152 if abs(z-790)==2 else 151
            for y in range(148,155):
                if y<=top:
                    if z in (788,792) and y<=151:
                        put(wall,y,z,'iron_bars','north=true,south=true,east=false,west=false,waterlogged=false')
                    else:
                        put(wall,y,z,'light_gray_stained_glass_pane','north=true,south=true,east=false,west=false,waterlogged=false')
                else:put(wall,y,z,'stone_bricks')
        for z in range(786,795):
            put(wall,147,z,'polished_blackstone_bricks')
            put(outside,147,z,'stone_brick_slab','type=top,waterlogged=false')
        for z in (786,794):
            for y in range(148,152):
                put(wall,y,z,'stone_bricks')
                put(outside,y,z,'stone_brick_wall','up=true,north=none,south=none,east=none,west=none,waterlogged=false')
        for z,y in ((787,152),(788,153),(789,154),(791,154),(792,153),(793,152)):
            put(outside,y,z,'stone_brick_stairs',f'facing={"south" if z<790 else "north"},half=top,shape=straight,waterlogged=false')
        put(wall,155,790,'chiseled_stone_bricks')
        put(outside,155,790,'chiseled_stone_bricks')
        # The cap closes the arch over the center pane while leaving its view open.
        windows.append({'side':side,'wall_x':wall,'outer_x':outside,'z':[786,794],'y':[147,155],
                        'glass_positions':29,'mullion_positions':8})
    d['_clearance_air']=[list(p) for p in sorted(air)]
    feature={'group':'halle_giebelfenster','name':'Obere Bogenfenster der Großen Halle','description':'West- und Ostgiebel: dreigeteilte, helle Verglasung mit zwei schlanken Metallsprossen, dunkler Sohlbank, seitlichen Steinpfeilern und gestuftem Bogen mit Schlussstein. Die Glasfläche sitzt hinter dem vorgezogenen Rahmen.'}
    return {**previous,'title':'Neue obere Giebelfenster an der Großen Halle','features':[feature]+previous['features'],
            'hall_gable_windows':windows,
            'limits':'Die beiden oberen Hallenfenster wurden innerhalb ihrer Giebel überarbeitet; die Dachsilhouette und die unteren Durchgänge bleiben erhalten. '+previous['limits']}
