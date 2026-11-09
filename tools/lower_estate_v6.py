"""Lower the above-ground estate by two blocks; retain surveyed cellar and sea-level structures."""
def lower(d,b,air,outdoors):
    fixed={'bootshaus','steglicht','fluchtgang'}
    def drop(y,g):
        if g in fixed or g.startswith('v6_') and g not in ('v6_pool','v6_garten'):return 0
        if g=='klippenpfad':return min(2,max(0,(y-63)//30))
        return 2
    moved={};keep={};surface_columns=set()
    for (x,y,z),value in b.items():
        dy=drop(y,value[2]);target=(x,y-dy,z)
        (moved if dy else keep)[target]=value
        if dy and value[2] in ('terraform_oberflaeche','v6_garten','zufahrt'):surface_columns.add((x,z))
    b.clear();b.update(keep);b.update(moved)
    # Air belonging to the house follows the same translation. Removed old positions
    # are subsequently added to the clearance list by the main builder.
    new_air={(x,y-2 if y>=129 else y,z) for x,y,z in air}
    air.clear();air.update(new_air);air.difference_update(b)
    for r in d['rooms']:
        if r['y'][0]>=129:r['y']=[v-2 for v in r['y']]
    for f in d['lighting']['fixtures']:
        dy=drop(f['y'],f['group']);f['y']-=dy;f['anchor'][1]-=dy
    for site in d['outdoor_sites']:
        if site.get('y',0)>100:site['y']-=2
    for key in d['meta']['floors']:d['meta']['floors'][key]-=2
    d['meta']['anchor'][1]-=2;d['meta']['bbox'][3]-=2
    for key in ('pool_bounds','rose_terrace'):
        outdoors[key][2]-=2;outdoors[key][3]-=2
    T=d['terrain'];x0,x1,z0,z1=T['bounds']
    for x,z in surface_columns:
        if x0<=x<=x1 and z0<=z<=z1:T['target_heights'][z-z0][x-x0]-=2
    # Existing geological excavation remains valid; only the final surface of affected
    # columns changes. Historical global earthwork exports are labelled separately.
    for row in T['work']:
        if (row[0],row[1]) in surface_columns:
            row[3]-=2;row[4]=max(0,row[2]-row[3]);row[5]=max(0,row[3]-row[2])
    T['excavate_total']=sum(row[4] for row in T['work'])
    T['fill_total']=sum(row[5] for row in T['work'])
    T['excavate_columns']=sum(row[4]>0 for row in T['work'])
    T['fill_columns']=sum(row[5]>0 for row in T['work'])
    chunks={}
    for x,z,old,new,cut,fill,*_ in T['work']:
        key=(x//16,z//16)
        bucket=chunks.setdefault(key,[key[0],key[1],0,0,0]);bucket[2]+=cut;bucket[3]+=fill;bucket[4]+=1
    T['chunks']=list(chunks.values())
    for waypoint in T.get('waypoints',[]):
        if isinstance(waypoint,dict) and 'y' in waypoint:waypoint['y']-=2
    return {'house_floor_before':129,'house_floor_after':127,'delta_y':-2,'sea_level_structures_preserved':sorted(fixed)}
