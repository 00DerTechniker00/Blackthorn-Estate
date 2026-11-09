"""Local planted garden edges, clear paths and coordinate-consistent terrain surfaces.

Call after the estate is lowered to EG Y127. Original survey terrain is read-only.
"""
from collections import Counter

SOFT={'grass_block','dirt','coarse_dirt','rooted_dirt','moss_block'}
FLOWERS={'allium','oxeye_daisy','cornflower','short_grass','fern'}
GROUND={'grass_block','dirt','coarse_dirt','gravel','stone_bricks','sea_lantern'}
LANDSCAPE_GROUPS={'terraform_auffuellung','terraform_oberflaeche','v6_garten','gartenlicht','gartendeko','weinberg','v6_gelaendepflege','v6_gartenpflege'}

def protected(x,z):
    return (-710<=x<=-658 and 766<=z<=814 or
            -715<=x<=-710 and 774<=z<=783 or
            -755<=x<=-740 and 762<=z<=790 or
            -658<=x<=-623 and 782<=z<=788)

def enhance(d,b,air):
    T=d['terrain'];x0,_,z0,_=T['bounds'];changed={};surface_changes={};cleared_paths=[]
    initial_heights=[row[:] for row in T['heights']]
    before_protected={p:v for p,v in b.items() if protected(p[0],p[2])}
    def put(x,y,z,block,state='',group='v6_gartenpflege'):
        assert not protected(x,z)
        p=x,y,z;value=(block,state,group)
        if b.get(p)==value:return
        changed.setdefault(p,b.get(p));b[p]=value;air.discard(p)
    def clear(x,y,z):
        assert not protected(x,z)
        p=x,y,z
        if p not in b:return
        changed.setdefault(p,b[p]);b.pop(p);air.add(p)
    def target(x,z,y,block):
        iy,ix=z-z0,x-x0;old=T['target_heights'][iy][ix]
        old_mat=T['target_surface_blocks'][iy][ix]
        if (old,old_mat)==(y,block):return
        surface_changes.setdefault((x,z),(old,old_mat))
        T['target_heights'][iy][ix]=y;T['target_surface_blocks'][iy][ix]=block
    # A heightfield represents the garden ground, never the top of a leaf hedge.
    # Only reconcile actual surface blocks in our southern garden; exclude buildings.
    for x in range(-747,-676):
        for z in range(833,870):
            if protected(x,z):continue
            if -724<=x<=-701 and 843<=z<=850:continue  # Orangery
            if -694<=x<=-686 and 850<=z<=858:continue  # Copper pavilion
            candidates=[(y,b[x,y,z]) for y in range(112,128) if (x,y,z) in b
                        and b[x,y,z][0] in GROUND and b[x,y,z][2] in LANDSCAPE_GROUPS]
            if not candidates:continue
            y,value=max(candidates)
            # Structural masonry and pergola border caps remain visible as geometry.
            if value[0]=='stone_bricks':continue
            target(x,z,y,value[0])
    # Small earthen apron below the south and west sides of the rose terrace.
    # No cliff filling or blanket leveling: only bare grass, at most two added layers.
    apron=[]
    for x in range(-740,-724):
        for z in range(839,853):
            if -736<=x<=-728 and 841<=z<=849:continue
            distance=max(-736-x,0,x+728)+max(841-z,0,z-849)
            if distance>3:continue
            old=T['target_heights'][z-z0][x-x0];wanted=max(old,123-distance)
            if wanted==old or wanted-old>2:continue
            value=b.get((x,old,z))
            if not value or value[0]!='grass_block' or value[2] not in LANDSCAPE_GROUPS:continue
            if any((x,y,z) in b for y in range(old+1,wanted+3)):continue
            for y in range(old,wanted):put(x,y,z,'dirt',group='v6_gelaendepflege')
            put(x,wanted,z,'grass_block',group='v6_gelaendepflege');target(x,z,wanted,'grass_block')
            apron.append([x,z,old,wanted])
    # Calm white/purple beds in the two existing strips; leave the central cross-aisle open.
    for z in (841,845):
        for x in range(-699,-677):
            ground=b.get((x,123,z));above=b.get((x,124,z))
            if not ground or ground[0]!='grass_block':continue
            if above and above[0] not in FLOWERS:continue
            if above:clear(x,124,z)
            if x%3:put(x,124,z,'allium' if (x+z)%4==0 else 'oxeye_daisy')
    # Each glow source replaces the ground under an existing hedge, not the walking lane.
    hedge_lights=[]
    for z in (840,846):
        for x in (-699,-693,-687,-681):
            if b.get((x,124,z),('',))[0]!='oak_leaves':continue
            if b.get((x,123,z),('',))[0] not in ('grass_block','sea_lantern'):continue
            put(x,123,z,'sea_lantern');target(x,z,123,'sea_lantern');hedge_lights.append([x,123,z])
    # Add slim armrests to existing south-side benches; seats and paths stay untouched.
    armrests=[]
    for x,facing in ((-702,'east'),(-698,'west'),(-682,'east'),(-678,'west')):
        if b.get((x,123,850),('',))[0]=='grass_block' and b.get((x,124,850),('',))[0] in ('','dark_oak_slab'):
            put(x,124,850,'dark_oak_trapdoor',f'facing={facing},half=bottom,open=true,powered=false,waterlogged=false')
            armrests.append([x,124,850])
    # Remove plants planted on gravel or the terminal stone landing of the garden stairs.
    # Existing steps, benches and structures are never treated as plant obstructions.
    path_positions=[]
    for (x,y,z),value in list(b.items()):
        if not(-747<=x<=-677 and 833<=z<=851) or protected(x,z):continue
        if value[0]!='gravel' and not(value[0]=='stone_bricks' and value[2]=='gartentreppe'):continue
        if not 118<=y<=126:continue
        path_positions.append([x,y,z])
        if b.get((x,y+1,z),('',))[0] in FLOWERS:
            clear(x,y+1,z);cleared_paths.append([x,y+1,z])
    # Synchronize affected work rows. Root integration may regenerate the global earthwork report.
    work={(row[0],row[1]):row for row in T['work']}
    for (x,z),(old_h,old_mat) in surface_changes.items():
        y=T['target_heights'][z-z0][x-x0];mat=T['target_surface_blocks'][z-z0][x-x0]
        if (x,z) not in work:
            original=T['heights'][z-z0][x-x0];row=[x,z,original,y,max(0,original-y),max(0,y-original),'Gartenpflege V6',mat]
            T['work'].append(row);work[x,z]=row
        else:
            row=work[x,z];row[3]=y;row[4]=max(0,row[2]-y);row[5]=max(0,y-row[2]);row[6]='Gartenpflege V6';row[7]=mat
    assert T['heights']==initial_heights,'Original terrain changed'
    assert all(b.get(p)==v for p,v in before_protected.items()),'Protected structures changed'
    material_delta=Counter()
    for p,old in changed.items():
        if old:material_delta[old[0]]-=1
        if p in b:material_delta[b[p][0]]+=1
    metadata={'title':'Weiche Gartenränder und klare Wege','bounds':[-747,-677,833,869],
              'changed_positions':len(changed),'terrain_columns':len(surface_changes),
              'apron_columns':apron,'hedge_lights':hedge_lights,'armrests':armrests,
              'removed_path_plants':cleared_paths,'path_positions':path_positions,
              'surface_changes':[[x,z,T['target_heights'][z-z0][x-x0],T['target_surface_blocks'][z-z0][x-x0]] for x,z in sorted(surface_changes)],
              'material_delta':{k:v for k,v in sorted(material_delta.items()) if v},
              'limits':'Lokale statische Prüfung; keine vollständige Spawn- oder Spielphysik-Simulation.'}
    d.setdefault('structure',{}).setdefault('v6',{})['landscape_refinement']=metadata
    check(d,b)
    return metadata

def check(d,b):
    T=d['terrain'];x0,_,z0,_=T['bounds'];m=d['structure']['v6']['landscape_refinement']
    for x,z,y,material in m['surface_changes']:
        assert not protected(x,z)
        assert T['target_heights'][z-z0][x-x0]==y
        assert T['target_surface_blocks'][z-z0][x-x0]==material
        assert b[x,y,z][0]==material,(x,y,z,material)
    for x,z,old,wanted in m['apron_columns']:
        assert 1<=wanted-old<=2
        assert b[x,wanted,z][0]=='grass_block'
        for y in range(old,wanted):assert b[x,y,z][0]=='dirt'
    for x,y,z in m['hedge_lights']:
        assert b[x,y,z][0]=='sea_lantern' and b[x,y+1,z][0]=='oak_leaves'
    for x,y,z in m['path_positions']:
        assert (x,y,z) in b
        assert b.get((x,y+1,z),('',))[0] not in FLOWERS
        assert (x,y-1,z) in b,'Unsupported garden path'
    return {'terrain_columns_consistent':len(m['surface_changes']),
            'supported_path_cells':len(m['path_positions']),
            'hidden_hedge_lights':len(m['hedge_lights']),
            'soft_apron_columns':len(m['apron_columns'])}
