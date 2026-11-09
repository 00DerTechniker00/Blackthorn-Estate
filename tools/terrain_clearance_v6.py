"""Keep terrain surfaces below actual house/deck floors instead of drawing soil through rooms."""

def enhance(d,b,air,architecture):
    T=d['terrain'];x0,_,z0,_=T['bounds'];before_heights=[row[:] for row in T['heights']]
    cap={(x,z):126 for x,z in T['house_footprint']}
    # The water surface is not the supporting terrain surface: the pool bed is Y124.
    for x in range(-651,-640):
        for z in range(780,801):cap[x,z]=123
    sx0,sx1,floor,top,sz0,sz1=architecture['stable_bounds']
    for x in range(sx0,sx1+1):
        for z in range(sz0,sz1+1):cap[x,z]=floor-1
    # Render the real approach blocks, never a second flat terrain skin above them.
    for (x,y,z),(bid,state,group) in b.items():
        if group in ('zufahrt','v6_stallweg','v6_ankunftsweg') and bid in ('gravel','stone_bricks','stone_brick_stairs'):
            cap[x,z]=min(cap.get((x,z),y-1),y-1)
        elif group=='portikus' and bid.endswith('_stairs') and y<=127:
            cap[x,z]=min(cap.get((x,z),y-1),y-1)
    # Keep the cellar's deeper existing cut and the western access untouched.
    changes=[];work={(row[0],row[1]):row for row in T['work']}
    for (x,z),ceiling in sorted(cap.items()):
        iy,ix=z-z0,x-x0;old=T['target_heights'][iy][ix];target=min(old,ceiling)
        if old==target:continue
        T['target_heights'][iy][ix]=target
        changes.append([x,z,old,target])
        original=T['heights'][iy][ix]
        row=work.get((x,z))
        if row is None:
            row=[x,z,original,target,max(0,original-target),max(0,target-original),'Gelände unter Baukörper',T['target_surface_blocks'][iy][ix]]
            T['work'].append(row);work[x,z]=row
        else:
            row[3]=target;row[4]=max(0,original-target);row[5]=max(0,target-original);row[6]='Gelände unter Baukörper'
    # The old geological excavation is retained, but lowered house/road surfaces
    # also require their newly exposed natural blocks to be cleared in the game.
    from collections import defaultdict
    intervals=defaultdict(list)
    for x,z,low,high in T['cut_spans']:intervals[x,z].append((low,high))
    extra_clearance=0
    for (x,z),base in cap.items():
        target=T['target_heights'][z-z0][x-x0];original=T['heights'][z-z0][x-x0]
        if original<=target:continue
        intervals[x,z].append((target+1,original))
        for y in range(target+1,original+1):
            p=x,y,z
            if p not in b and p not in air:air.add(p);extra_clearance+=1
    merged=[]
    for (x,z),spans in sorted(intervals.items()):
        packed=[]
        for low,high in sorted(spans):
            if packed and low<=packed[-1][1]+1:packed[-1][1]=max(packed[-1][1],high)
            else:packed.append([low,high])
        merged.extend([x,z,low,high] for low,high in packed)
    T['cut_spans']=merged
    T['soil_portals']=[[-713,-710,96,98,775,777],[-711,-710,96,98,781,782],[-711,-710,81,83,775,782],[-658,-629,108,112,783,787]]
    T['structure_clearance']=[[x,z,y] for (x,z),y in sorted(cap.items())]
    assert T['heights']==before_heights
    return {'masked_columns':len(cap),'corrected_columns':len(changes),'surface_changes':changes,'house_floor':127,'stable_floor':floor,'pool_floor':124,'new_explicit_air_positions':extra_clearance}

def check(d,b):
    T=d['terrain'];x0,_,z0,_=T['bounds'];mask={(x,z):y for x,z,y in T['structure_clearance']}
    for (x,z),base in mask.items():assert T['target_heights'][z-z0][x-x0]<=base
    for x,z in [(-733,787),(-733,796),(-733,774),(-675,824),(-711,785),(-734,790),(-734,791),(-657,789),(-657,790)]:
        assert (x,z) in mask
        assert T['target_heights'][z-z0][x-x0]<=126,(x,z)
    for x in range(-651,-640):
        for z in range(780,801):assert mask[x,z]==123
    return {'terrain_below_house_and_stable':True,'known_door_and_room_conflicts_resolved':9,'pool_ground_below_bed':True,'masked_columns':len(mask)}
