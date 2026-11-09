"""A roofed river-facing loggia reached from cellar three, without cutting the plateau open."""

def enhance(d,b,air):
    before=b.copy();changed=set();cleared=set();group='v6_flussloggia'
    def put(x,y,z,bid,state=''):
        p=x,y,z;b[p]=(bid,state,group);air.discard(p);changed.add(p)
    def clear(x,y,z):
        p=x,y,z;b.pop(p,None);air.add(p);cleared.add(p)
    # A five-wide gallery between the three existing pool-support axes.
    for x in range(-658,-628):
        for z in range(782,789):
            put(x,107,z,'deepslate_bricks' if x==-658 else 'polished_deepslate' if z in (782,788) else 'dark_oak_planks')
            put(x,113,z,'deepslate_bricks' if x==-658 else 'deepslate_tiles')
            for y in range(108,113):
                edge=z in (782,788) or x==-629
                if not edge:clear(x,y,z)
                else:
                    glazed=x>=-634 and 109<=y<=111 and (x==-629 or -633<=x<=-630)
                    put(x,y,z,'gray_stained_glass' if glazed else 'deepslate_bricks')
    # Open the existing eastern cellar wall only at this entrance.
    for z in range(783,788):
        for y in range(108,113):clear(-658,y,z)
    # Quiet seating bays leave a three-wide supported central passage unobstructed.
    for x in (-653,-646,-639,-632):
        for z,facing in ((783,'south'),(787,'north')):
            if x==-632 or x in (-653,-646):
                put(x,108,z,'dark_oak_stairs',f'facing={facing},half=bottom,shape=straight,waterlogged=false')
        put(x,113,785,'sea_lantern')
    # Footings stop at the surveyed cliff surface rather than descending to sea level.
    T=d['terrain'];x0,_,z0,_=T['bounds'];footings=[]
    for z in (783,787):
        x=-630;base=T['target_heights'][z-z0][x-x0]
        for y in range(base+1,107):put(x,y,z,'deepslate_bricks')
        footings.append([x,base,z])
    return {'floor':107,'free_height':5,'entry':[-658,108,785],
            'bounds':[-658,-629,107,113,782,788],'view_direction':'Osten · Fluss',
            'window_x':-629,'footings':footings,'changed_positions':sum(before.get(p)!=b.get(p) for p in changed|cleared),
            'required_clearance':len(cleared),'rooms':[{'name':'Flussgalerie im Klippenkeller','group':group,'x':[-657,-630],'y':[108,112],'z':[783,787],
             'text':'Fünf Blöcke hohe Galerie aus Keller 3 mit Sitznischen und geschlossener Panoramaverglasung zum Fluss. Kein offener Einschnitt im Plateau.',
             'access':'Vom östlichen Rand der Kelleretage mit Boden Y 107, Durchgang X −658 / Z 783–787.','stand':0,'reach':0}]}

def check(d,b):
    def bid(p):return b[p][0] if p in b else 'air'
    for x in range(-658,-629):
        for z in (784,785,786):
            assert (x,107,z) in b
            for y in range(108,113):assert (x,y,z) not in b,(x,y,z)
    for z in range(783,788):
        for y in (109,110,111):assert bid((-629,y,z))=='gray_stained_glass'
    T=d['terrain'];x0,_,z0,_=T['bounds']
    # Both near terrain and the distant river bank stay below the central line of sight.
    for x in range(-628,-589):assert T['target_heights'][785-z0][x-x0]<109
    assert bid((-669,107,785))!='air'  # landing belongs to existing K3 floor
    from collections import deque
    from structure_check import LIGHT,opaque
    levels={p:LIGHT[v[0]] for p,v in b.items() if -658<=p[0]<=-629 and 107<=p[1]<=113 and 782<=p[2]<=788 and LIGHT.get(v[0],0)}
    queue=deque(levels)
    while queue:
        x,y,z=queue.popleft();value=levels[x,y,z]-1
        for dx,dy,dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            p=x+dx,y+dy,z+dz
            if value<=0 or not(-658<=p[0]<=-629 and 107<=p[1]<=113 and 782<=p[2]<=788) or p in b and opaque(b[p][0]) or levels.get(p,0)>=value:continue
            levels[p]=value;queue.append(p)
    minimum=min(levels.get((x,108,z),0) for x in range(-658,-629) for z in (784,785,786));assert minimum>0
    return {'minimum_path_block_light':minimum,'central_path_width':3,'clear_headroom':5,'window_closed':True,'view_axis':'east','near_cliff_line_clear':True}
