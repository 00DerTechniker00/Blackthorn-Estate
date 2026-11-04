"""Buildable lawn shoulders and a planted arrival court; keep the eastern ravine open."""
import math
from collections import Counter

EARTH={'terraform_auffuellung','terraform_oberflaeche','zufahrt'}

def design(d,b):
    t=d['terrain'];x0,x1,z0,z1=t['bounds'];H=t['heights'];old_target=t['target_heights']
    rows={(r[0],r[1]):r for r in t['work']};plan={};sites=[];columns={}
    for p,r in b.items():columns.setdefault((p[0],p[2]),[]).append((p,r))
    def natural(x,z):return H[z-z0][x-x0]
    def surface(x,z,y,zone,top='grass_block'):
        if (x,z) in rows and rows[x,z][6] in {'Kellerbaugrube','Techniknische'}:return
        plan[x,z]=[y,zone,top]
    # Extend the occupied plinth into a soft lawn apron. The east pool piers stay exposed.
    seeds=[(x,z) for (x,z),r in rows.items() if r[6]=='Hausunterbau']
    apron={}
    for x,z in seeds:
        if all((x+dx,z+dz) in rows and rows[x+dx,z+dz][6] in {'Hausunterbau','Kellerbaugrube','Techniknische'} for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]):continue
        for dx in range(-14,15):
            for dz in range(-14,15):
                distance=math.hypot(dx,dz);xx,zz=x+dx,z+dz
                if distance>14 or xx>-656 or not(x0<xx<x1 and z0<zz<z1):continue
                if (xx,zz) in rows and rows[xx,zz][6] not in {'Einzelne Baukollisionen','Wegschulter'}:continue
                n=natural(xx,zz)
                if n<112:continue
                # Two grass blocks at the wall, then a gradual fall into the existing hill.
                weight=max(0,1-max(0,distance-2)/12)
                y=round(n+(128-n)*weight)
                if (xx,zz) not in apron or distance<apron[xx,zz][0]:apron[xx,zz]=(distance,y)
    for (x,z),(distance,y) in apron.items():surface(x,z,y,'Begrünte Böschung')
    # Skin exposed artificial ground strips next to the house rather than leave raw stone.
    for (x,z),r in rows.items():
        if r[6]=='Hausunterbau' and (x,129,z) not in b and x<=-656:
            surface(x,z,128,'Sockelbegrünung')
    # Arrival courtyard: unobstructed centre, garden islands to either side.
    for x in range(-745,-738):
        for z in range(773,809):
            if (x,129,z) in b and b[x,129,z][2] not in EARTH:continue
            if (x,z) in rows and rows[x,z][6]=='Zufahrt Nordwest':continue
            surface(x,z,128,'Ankunftsgarten','gravel' if 785<=z<=795 else 'grass_block')
    # South lawn room, set below the house to keep the facade and outlook visible.
    for x in range(-707,-672):
        for z in range(835,852):
            surface(x,z,125,'Südgarten')
    for x in range(-694,-685):
        for z in range(850,859):surface(x,z,125,'Gartenpavillon','dark_oak_planks')
    # A feathered ten-block transition around the new lawn, not a sheer garden platform.
    garden=list((x,z) for x,z in plan if plan[x,z][1] in {'Südgarten','Gartenpavillon'})
    blend={}
    for x,z in garden:
        if -706<x<-674 and 835<z<850:continue
        for dx in range(-10,11):
            for dz in range(-10,11):
                dist=math.hypot(dx,dz);xx,zz=x+dx,z+dz
                if not 0<dist<=10 or (xx,zz) in plan or (xx,zz) in rows and rows[xx,zz][6] in {'Hausunterbau','Kellerbaugrube','Techniknische'}:continue
                n=natural(xx,zz)
                if n<112:continue
                y=round(n+(125-n)*(1-dist/10))
                if (xx,zz) not in blend or dist<blend[xx,zz][0]:blend[xx,zz]=(dist,y)
    for (x,z),(dist,y) in blend.items():surface(x,z,y,'Gartenböschung')
    # Gravel promenade linking the west arrival court to the south garden.
    # Flat treads are three blocks long per one-block descent.
    # Use an explicit continuous centreline (one-block rises, no gaps between diagonal steps).
    points=[(-745,798,128),(-745,829,128),(-736,835,127),(-723,840,126),(-707,843,125),(-676,843,125)]
    path=[]
    for (ax,az,ay),(cx,cz,cy) in zip(points,points[1:]):
        n=max(abs(cx-ax),abs(cz-az))
        for i in range(n+1):
            f=i/n;x=round(ax+(cx-ax)*f);z=round(az+(cz-az)*f);y=round(ay+(cy-ay)*f);path.append([x,z,y])
            for dx in range(-1,2):
                for dz in range(-1,2):surface(x+dx,z+dz,y,'Gartenweg','gravel')
    for x in range(-704,-675):
        for z in range(838,849):
            if x in (-704,-703,-677,-676) or z in (838,839,847,848):surface(x,z,125,'Gartenweg','gravel')
    # Taper the raised promenade and court over a broad soil skirt rather than
    # exposing vertical fill faces. Road cells remain fixed height constraints.
    hard={p:v for p,v in plan.items() if v[1] in {'Ankunftsgarten','Gartenweg','Südgarten','Gartenpavillon'}}
    skirt={}
    for (x,z),(y,zone,top) in hard.items():
        if all((x+dx,z+dz) in hard for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]):continue
        for dx in range(-18,19):
            for dz in range(-18,19):
                dist=math.hypot(dx,dz);xx,zz=x+dx,z+dz
                if not 0<dist<=18 or (xx,zz) in hard:continue
                if (xx,zz) in rows and rows[xx,zz][6] in {'Hausunterbau','Kellerbaugrube','Techniknische','Zufahrt Nordwest','Eingangshof'}:continue
                n=natural(xx,zz)
                if n<112 or xx>-656:continue
                yy=round(n+(y-n)*(1-dist/18))
                if (xx,zz) not in skirt or dist<skirt[xx,zz][0]:skirt[xx,zz]=(dist,yy)
    for (x,z),(dist,y) in skirt.items():
        if (x,z) in plan:y=max(y,plan[x,z][0])
        surface(x,z,y,'Weiche Gartenböschung')
    # No new raised soil strip makes a sheer edge beside the original drive.
    road={(x,z):r[3] for (x,z),r in rows.items() if r[6]=='Zufahrt Nordwest'}
    caps={}
    for (x,z),y in road.items():
        for dx in range(-12,13):
            for dz in range(-12,13):
                dist=max(abs(dx),abs(dz));p=x+dx,z+dz
                if p in plan:caps[p]=min(caps.get(p,999),y+dist)
    for p,cap in caps.items():
        if plan[p][1] not in {'Gartenweg','Gartenpavillon'}:plan[p][0]=min(plan[p][0],cap)
    # Update only outdoor columns; never lower occupied structures or buried service space.
    for (x,z),(y,zone,top) in list(plan.items()):
        protected=[p[1] for p,r in columns.get((x,z),[]) if r[2] not in EARTH and p[1]<=128 and r[2] not in {'sockel','hang_stuetzen','weg_sicherung'}]
        if protected and max(protected)>y:
            plan.pop((x,z));continue
        for p,r in columns.get((x,z),[]):
            if r[2] in EARTH:del b[p]
        n=natural(x,z)
        # Soil skin is a real three-block layer, also where stone is replaced at equal height.
        for yy in range(min(n+1,y-2),y+1):
            p=x,yy,z
            if p not in b:b[p]=(top if yy==y else 'dirt','','terraform_oberflaeche' if yy==y else 'terraform_auffuellung')
        if (x,y,z) in b and b[x,y,z][2]=='sockel' and top=='grass_block' and (x,y+1,z) not in b:
            b[x,y,z]=('grass_block','','terraform_oberflaeche')
        if (x,y,z) in b and b[x,y,z][2] not in EARTH:top=b[x,y,z][0]
        plan[x,z]=[y,zone,top]
    redundant=0
    def planned_height(x,z):return plan.get((x,z),[old_target[z-z0][x-x0]])[0]
    for (x,y,z),record in list(b.items()):
        if record[2]!='weg_sicherung' or (x,z) not in plan:continue
        ground=planned_height(x,z)
        if ground>=y or min(planned_height(x+dx,z+dz) for dx in range(-3,4) for dz in range(-3,4))>=ground-2:
            del b[x,y,z];redundant+=1
            if y<=ground:
                top='gravel' if plan[x,z][1]=='Gartenweg' else 'grass_block'
                b[x,y,z]=(top if y==ground else 'dirt','','terraform_oberflaeche' if y==ground else 'terraform_auffuellung')
                if y==ground:plan[x,z][2]=top
        elif ground+1!=y:
            del b[x,y,z]
            if (x,ground+1,z) not in b:b[x,ground+1,z]=record
    d['route_safety']['raised_ramp_guard_posts']=sum(r[2]=='weg_sicherung' for r in b.values())
    def put(x,y,z,bid,st=''):
        if (x,y,z) in b:return False
        b[x,y,z]=(bid,st,'gartendeko');return True
    def planted(x,z,flower='allium'):
        y=plan.get((x,z),[old_target[z-z0][x-x0]])[0]
        if (x,y,z) not in b or b[x,y,z][0]!='grass_block':return
        put(x,y+1,z,flower)
    def hedge(x,z,height=2):
        y=plan.get((x,z),[old_target[z-z0][x-x0]])[0]
        for yy in range(y+1,y+height+1):put(x,yy,z,'oak_leaves','distance=1,persistent=true,waterlogged=false')
    def bench(x,z,y=129):
        for dx in range(-2,3):
            ground=planned_height(x+dx,z)
            for yy in range(ground+1,y):put(x+dx,yy,z,'dark_oak_fence','east=false,north=false,south=false,west=false,waterlogged=false')
        for dx in range(-1,2):put(x+dx,y,z,'dark_oak_stairs','facing=north,half=bottom,shape=straight,waterlogged=false')
        for dx in (-2,2):put(x+dx,y,z,'dark_oak_slab','type=bottom,waterlogged=false')
    # Four compact topiary islands around the arrival lawn, leaving the drive clear.
    for z in (777,802):
        for x in (-741,):
            hedge(x,z,3)
            for dx,dz in [(-1,0),(1,0),(0,-1),(0,1)]:hedge(x+dx,z+dz,2)
            for dx in (-2,2):
                for dz in (-2,2):planted(x+dx,z+dz,'oxeye_daisy')
    bench(-741,780);bench(-741,805)
    sites.append(dict(name='Ankunftsgarten',x=-745,z=790,y=128,text='Freie Zufahrt, zwei Formschnittinseln, weiße Blüten und zwei Holzbänke.'))
    # A restrained southern parterre: low hedges, mixed white/purple/blue beds.
    for x in range(-701,-678):
        if not -692<=x<=-688:
            hedge(x,840,1);hedge(x,846,1)
    for x in range(-701,-678,2):
        for z in (841,845):planted(x,z,['allium','oxeye_daisy','cornflower'][(x+z)%3])
    for x in (-700,-680):
        bench(x,850,126)
    # Open four-post garden pavilion with a copper cap, off the main walking axis.
    cx,cz=-690,854
    for dx in (-3,3):
        for dz in (-3,3):
            for yy in range(126,130):put(cx+dx,yy,cz+dz,'dark_oak_fence','east=false,north=false,south=false,west=false,waterlogged=false')
    for radius,yy in [(4,130),(3,131),(2,132),(1,133)]:
        for dx in range(-radius,radius+1):
            for dz in range(-radius,radius+1):
                if max(abs(dx),abs(dz))==radius:put(cx+dx,yy,cz+dz,'waxed_oxidized_cut_copper_slab','type=bottom,waterlogged=false')
                else:put(cx+dx,yy,cz+dz,'dark_oak_planks')
    put(cx,134,cz,'waxed_oxidized_cut_copper_slab','type=bottom,waterlogged=false')
    sites.append(dict(name='Südgarten & Pavillon',x=-690,z=843,y=125,text='Kiesrundweg, niedrige Hecken, Blütenbeete, Bänke und ein offener Holzpavillon mit Kupferhaube.'))
    t['garden_path']=path
    t['landscape_plan']=[[x,z,*v] for (x,z),v in sorted(plan.items())]
    d['outdoor_sites']=sites
    d['landscape_changes']={'columns':len(plan),'decor_blocks':sum(v[2]=='gartendeko' for v in b.values()),'eastern_ravine_preserved':True,'soil_skin_layers':3,'removed_redundant_guard_posts':redundant}
    return plan
