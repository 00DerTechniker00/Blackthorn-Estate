#!/usr/bin/env python3
"""V6: preserve surveyed cellar shell, integrate original Dustless storage geometry."""
import copy,csv,gzip,hashlib,json,struct
from pathlib import Path
from collections import Counter,defaultdict
from litematic_import import NBTReader,read_litematic
from materials import items_for_block,scopes,stack_size
from structure_export import export
import build as reports
ROOT=Path(__file__).resolve().parent.parent
VERSION='6.0'
SEED=ROOT/'tools/seeds/revision-5.26/blueprint.json'

def module():
    source=ROOT/'litematics/Golem MIS Dustless Filter.litematic'
    raw=gzip.decompress(source.read_bytes())
    def string(s):b=s.encode();return struct.pack('>H',len(b))+b
    # Only palette Name tags are changed: container NBT and entities remain byte-for-byte intact.
    old=b'\x08'+string('Name')+string('minecraft:white_stained_glass')
    new=b'\x08'+string('Name')+string('minecraft:gray_stained_glass')
    assert old in raw
    target=ROOT/'litematics/Blackthorn_V6_Dustless.litematic'
    target.write_bytes(gzip.compress(raw.replace(old,new),mtime=0))
    root=NBTReader(gzip.decompress(target.read_bytes())).root();result={}
    for region in root['Regions'].values():
        size=region['Size'];pos=region['Position'];sx,sy,sz=[abs(size[a]) for a in ('x','y','z')]
        low=[pos[a]+min(0,size[a]+1) for a in ('x','y','z')]
        palette=region['BlockStatePalette'];packed=region['BlockStates'];bits=max(2,(len(palette)-1).bit_length());mask=(1<<bits)-1
        for index in range(sx*sy*sz):
            word,shift=divmod(index*bits,64);v=(packed[word]&((1<<64)-1))>>shift
            if shift+bits>64:v|=(packed[word+1]&((1<<64)-1))<<(64-shift)
            item=palette[v&mask];bid=item['Name'].removeprefix('minecraft:')
            if bid=='air':continue
            p=(low[0]+index%sx-701,low[1]+index//(sx*sz)+102,low[2]+(index//sx)%sz+771)
            state=','.join(f'{k}={val}' for k,val in sorted(item.get('Properties',{}).items()))
            if p in result:assert result[p][:2]==(bid,state)
            result[p]=(bid,state,'v6_grosslager')
    meta=read_litematic(target);assert len(result)==meta['total_blocks']
    return result,meta

def main():
    d=json.loads(SEED.read_text());prior={}
    for y,z,x,n,ri in d['runs']:
        bid,state,g=d['reg'][ri]
        for dx in range(n):prior[x+dx,y,z]=(bid,state,d['groups'][g])
    b=prior.copy();air=set(map(tuple,d['required_air']))
    def inside(p):x,y,z=p;return -710<=x<=-658 and 94<=y<=128 and 766<=z<=814
    removed={'keller_1','keller_2','keller_3','keller_treppe','lager_regale','bulk_lager','sortierung','golem_lager','lager_technik','shulker_technik','trading_hall','geheimraum','geheimgang','privatlager','geheimtechnik','buchsteuerung','materiallift','liefergong'}
    for p,v in list(b.items()):
        if inside(p) or v[2] in removed:b.pop(p,None)
    air={p for p in air if not inside(p)}
    # Remove redundant old lift/shaft remnants in the EG, retain roof access.
    for p,v in list(b.items()):
        if v[2] in ('materiallift','liefergong','buchsteuerung','liftanzeige'):b.pop(p,None);air.add(p)
    def put(x,y,z,bid,state='',group='v6_keller'):b[x,y,z]=(bid,state,group);air.discard((x,y,z))
    def clear(x,y,z):b.pop((x,y,z),None);air.add((x,y,z))
    def floor(y,block='deepslate_tiles',group='v6_keller'):
        for x in range(-709,-658):
            for z in range(767,814):put(x,y,z,block,group=group)
    # Exact built shell and checkered bottom are read from the committed survey, not invented.
    survey=json.loads(gzip.decompress((ROOT/'bestandsaufnahme/keller_bestand.json.gz').read_bytes()))
    for y,z,x,n,ri in survey['runs']:
        pal=survey['palette'][ri]
        if y==95 and -709<=x and x+n-1<=-659 or 96<=y<=127 and pal['name']=='deepslate_bricks':
            for xx in range(x,x+n):put(xx,y,z,pal['name'],','.join(f'{k}={v}' for k,v in sorted(pal['properties'].items())), 'v6_bestand')
    for y in range(96,129):
        for x in range(-709,-658):
            for z in range(767,814):clear(x,y,z)
    for x in range(-710,-657):
        for z in (766,814):put(x,128,z,'deepslate_bricks')
    for z in range(767,814):
        for x in (-710,-658):put(x,128,z,'deepslate_bricks')
    floor(101);floor(102);floor(124)
    for x in range(-709,-658):
        for z in range(767,814):
            if (x,129,z) not in b:put(x,129,z,'dark_oak_planks')
    # Full-height storage, original orientation. Air within its envelope is part of the mechanism.
    for y in range(102,124):
        for x in range(-701,-674):
            for z in range(771,798):clear(x,y,z)
    storage,meta=module()
    for p,value in storage.items():b[p]=value;air.discard(p)
    # Walkable outside ring at the lower entry level.
    for x in range(-709,-658):
        for z in range(767,814):
            if not(-701<=x<=-675 and 771<=z<=797):put(x,102,z,'polished_deepslate')
    # Lower rooms, central east-west corridor and broad door openings (no misleading piston mock-up).
    for z in (787,794):
        for x in range(-709,-658):
            if -688<=x<=-684:continue
            for y in range(96,101):put(x,y,z,'deepslate_bricks',group='v6_geheimraeume')
    for z in range(768,787):
        for y in range(96,101):
            if z not in (776,777,778):put(-686,y,z,'deepslate_bricks',group='v6_geheimraeume')
    for x in range(-708,-689,3):
        for y in (96,97):put(x,y,768,'bookshelf',group='v6_geheimraeume')
    for x in range(-708,-699,2):
        put(x,96,812,'barrel','facing=north,open=false','v6_handlager')
    # Ceiling lights, no floor lanterns or obstructions in portals.
    for y in (101,129):
        for x in (-706,-698,-690,-682,-674,-666,-662):
            for z in (770,778,784,790,798,806,812):put(x,y,z,'sea_lantern',group='v6_licht')
    # Generous unobstructed north strip across the whole interior width. Chunk boundaries remain visible in atlas.
    for x in range(-709,-658):
        for z in range(767,781):
            for y in range(125,129):clear(x,y,z)
    for x in (-704,-688,-672):
        for z in range(767,781):put(x,124,z,'chiseled_stone_bricks',group='v6_chunkraster')
    # Main vertical access in the southeast, entirely outside the storage envelope.
    for y in range(96,132):
        for x in (-662,-661,-660):
            for z in (802,803,804):clear(x,y,z)
        put(-662,y,803,'polished_deepslate',group='v6_zugang')
        put(-661,y,803,'ladder','facing=east,waterlogged=false','v6_zugang')
    # EG landing connects to existing southeast residence, with headroom.
    for x in range(-661,-658):
        for z in (802,804):put(x,129,z,'dark_oak_planks',group='v6_zugang')
    for y in (102,124,129):
        for x in (-660,-659):put(x,y,803,'polished_deepslate',group='v6_zugang')
    for y in (102,124,129):
        for x in (-662,-661,-660):
            for z in (802,803,804):
                if (x,z)!=(-661,803):put(x,y,z,'polished_deepslate',group='v6_zugang')
        for z in (802,804):put(-661,y+1,z,'polished_blackstone_wall',group='v6_zugang')
    # Secret descent is outside the west wall: the existing Y95 interior floor stays intact.
    for y in range(81,100):
        for x in range(-714,-709):
            for z in range(774,779):
                edge=x in (-714,-710) or z in (774,778)
                if edge:put(x,y,z,'deepslate_bricks',group='v6_geheimabstieg')
                else:clear(x,y,z)
        put(-713,y,776,'deepslate_bricks',group='v6_geheimabstieg')
        put(-712,y,776,'ladder','facing=east,waterlogged=false','v6_geheimabstieg')
    for x in range(-714,-709):
        for z in range(774,779):put(x,100,z,'deepslate_bricks',group='v6_geheimabstieg')
    for x in (-711,-710):
        for z in (775,776,777):
            put(x,95,z,'polished_deepslate',group='v6_geheimabstieg')
            for y in (96,97,98):clear(x,y,z)
    for z in (775,777):put(-712,96,z,'polished_blackstone_wall',group='v6_geheimabstieg')
    for x in range(-713,-686):
        for z in range(775,778):
            put(x,80,z,'deepslate_tiles',group='v6_geheimabstieg')
            for y in range(81,84):
                if (x,z) not in ((-713,776),(-712,776)):clear(x,y,z)
            if x>-711:put(x,84,z,'deepslate_bricks',group='v6_geheimabstieg')
    from access_v6 import enhance as build_water_access
    water_access=build_water_access(b,air)
    # Restore every one of the 2397 original floor blocks including their exact properties.
    for y,z,x,n,ri in survey['runs']:
        if y!=95:continue
        pal=survey['palette'][ri]
        for xx in range(x,x+n):
            if -709<=xx<=-659 and 767<=z<=813:
                put(xx,95,z,pal['name'],','.join(f'{k}={v}' for k,v in sorted(pal['properties'].items())),'v6_bestand')
    from outdoors_v6 import enhance as improve_outdoors
    outdoor_changes=improve_outdoors(d,b,air)
    # No blocks and required-air positions may overlap.
    air.update(prior.keys()-b.keys())
    air.difference_update(b)
    d['required_air']=[list(p) for p in sorted(air)]
    groups=sorted({v[2] for v in b.values()});gi={g:i for i,g in enumerate(groups)};reg=[];lookup={};by=defaultdict(list);coords=defaultdict(list);counts=Counter();gc={g:Counter() for g in groups};seq=[]
    for (x,y,z),(bid,state,g) in sorted(b.items(),key=lambda v:(v[0][1],v[0][2],v[0][0])):
        key=(bid,state,gi[g])
        if key not in lookup:lookup[key]=len(reg);reg.append(list(key))
        by[y,z].append((x,lookup[key]));coords[g].append((x,y,z));seq.append([len(seq)+1,x,y,z,'minecraft:'+bid,state,g])
        for item,n in items_for_block(bid,state):counts[item]+=n;gc[g][item]+=n
    runs=[]
    for (y,z),row in sorted(by.items()):
        i=0
        while i<len(row):
            x,ri=row[i];n=1
            while i+n<len(row) and row[i+n]==(x+n,ri):n+=1
            runs.append([y,z,x,n,ri]);i+=n
    d.update(groups=groups,reg=reg,runs=runs,counts=dict(counts),gcounts={g:dict(v) for g,v in gc.items()},gstats={g:{'n':len(ps),'x':[min(p[0] for p in ps),max(p[0] for p in ps)],'y':[min(p[1] for p in ps),max(p[1] for p in ps)],'z':[min(p[2] for p in ps),max(p[2] for p in ps)]} for g,ps in coords.items()})
    d['meta'].update(version=VERSION,total=len(b),fingerprint=hashlib.sha256(json.dumps(seq,separators=(',',':')).encode()).hexdigest())
    d['material_scopes']=scopes(d['gcounts']);d['material_stack_sizes']={k:stack_size(k) for k in counts}
    changes={p:(prior.get(p),b.get(p)) for p in prior.keys()|b.keys() if prior.get(p)!=b.get(p)}
    d['progress_compat']={'revision':'5.26','fingerprint':json.loads(SEED.read_text())['meta']['fingerprint'],'changed_positions':[','.join(map(str,p)) for p in changes],'changed_groups':sorted({v[2] for pair in changes.values() for v in pair if v})}
    migration_path=ROOT/'tools/seeds/revision-6.0/progress_compat.json'
    if migration_path.exists():
        migration=json.loads(migration_path.read_text())
        candidates=migration if isinstance(migration,list) else [migration]
        d['progress_compat']['additional']=[m for m in candidates if m['target_fingerprint']==d['meta']['fingerprint']]
    d['rooms']=[r for r in d['rooms'] if r['y'][0]>=129]
    def room(name,g,x,y,z,text):d['rooms'].append(dict(name=name,group=g,x=x,y=y,z=z,text=text,access='Zentraler Leiterzugang im Südosten, X −661 / Z 803.',stand=0,reach=0))
    room('Geheime Bibliothek','v6_geheimraeume',[-708,-687],[96,100],[768,786],'Bestehender Schachbrettboden; geheimer Leiterabstieg zum Y80-Gang.')
    room('Werkstatt und Reserve','v6_geheimraeume',[-685,-659],[96,100],[768,786],'Freier Ausbauplatz für weitere Funktionen.')
    room('Handlager und Nebenräume','v6_handlager',[-708,-659],[96,100],[795,812],'Manuelle Fässer als Reserve; keine alte Trading-Hall unterstellt.')
    room('Dustless-Großlager','v6_grosslager',[-701,-675],[102,123],[771,797],'Originale Schaltungshöhe, graue Glasverkleidung. Inventare und Golems aus V6-Litematic übernehmen.')
    room('Porter-Galerie · gesamte Nordwand','v6_keller',[-709,-659],[125,128],[767,780],'51 × 14 freie Bodenpositionen; gesamte Nordseite bleibt ohne Möbel. Eigene Porter chunkweise einsetzen.')
    room('Poolterrasse und flacher Einstieg','v6_pool',[-657,-634],[130,130],[770,810],'Ruhiger Steinbelag, Holzbänke und beleuchtetes Becken; mittlerer Hauszugang bleibt frei.')
    room('Rosenterrasse mit Pergola','v6_garten',[-736,-728],[126,126],[841,849],'Über den nördlichen Kiesweg erreichbar; offene Mitte und Sitzbank im Süden.')
    room('Geheimsalon am tiefen Gang','v6_geheimsalon',[-684,-670],[81,87],[770,783],'15 × 14 freie Innenabmessung vor Möbeln, sieben Blöcke hoch; Auf- und Abfahrt in der westlichen Nische.')
    d['storage_zones']=[];d['storage_bays']=[]
    for i,x in enumerate(range(-708,-699,2),1):
        id=f'V6-H{i:02d}';d['storage_zones'].append(dict(id=id,name=f'Reserve {i}',contents='1 Fass · 27 Plätze',room='Unteres Handlager',group='v6_handlager',x=[x,x],y=[96,96],z=[812,812]))
    d['storage_summary']={'bays':len(d['storage_zones']),'containers':len(d['storage_zones']),'slots':27*len(d['storage_zones'])}
    d['storage_system'].update(input={'x':-677,'y':103,'z':773},bulk=[],regular=[],stations=[],stalls=[])
    d['storage_system']['modules']=[]
    d['storage_bays']=[dict(id=z['id'],name=z['name'],floor=95,x=z['x'][0],y=96,z=812,containers=[[z['x'][0],96,812]],container_count=1,slots=27,front=[z['x'][0],96,811],automation='Manuell') for z in d['storage_zones']]
    d['lighting']['fixtures']=[f for f in d['lighting']['fixtures'] if b.get((f['x'],f['y'],f['z']),('',))[0] in ('lantern','soul_lantern') and b.get(tuple(f['anchor']))]
    d['checks'].update(doors=sum(v[0].endswith('_door') and 'half=lower' in v[1] for v in b.values()),stairs=sum(v[0].endswith('_stairs') for v in b.values()),panes=sum(v[0]=='glass_pane' or v[0].endswith('_stained_glass_pane') for v in b.values()))
    d['lighting']['total']=sum(v[0] in ('lantern','soul_lantern') for v in b.values())
    d['lighting']['light_simulated']=False;d['lighting']['light_report']=None
    levels=[('v6_salon','Tiefer Geheimsalon',80,88),('v6_unten','Geheim- und Nebenräume',95,101),('v6_lager','Großlager · 22 Ebenen',102,123),('v6_porter','Porter-Galerie · Nordwand frei',124,128),('erdgeschoss','Erdgeschoss',129,136),('obergeschoss','Obergeschoss & Galerie',137,144),('dach','Dach & Türme',145,171)]
    d['structure']['levels']=[dict(id=k,label=label,y=[lo,hi],height=hi-lo+1,groups=sorted({v[2] for p,v in b.items() if lo<=p[1]<=hi}),positions=sum(lo<=p[1]<=hi for p in b),rooms=[r['name'] for r in d['rooms'] if lo<=r['y'][0]<=hi]) for k,label,lo,hi in levels]
    d['structure']['stair_runs']=[];d['structure']['stair_clearance']=[]
    d['structure']['service_shaft']={'position':[-661,95,803],'vault_bounds':[-701,-675,102,123,771,797],'vault_size':[27,22,27],'service_gap_x':[-674,-659],'vertical_floor_blocks':[],'note':'Durchgehende Leiter Y96–131 mit Austritten auf Y95, 102, 124 und 129.'}
    d['structure']['logistics']=[{'label':'Dustless-Großlager','y':[102,123]},{'label':'Porter-Galerie · Nordwand frei','y':[124,128]}]
    d['structure']['enhancements']['title']='Version 6 · Keller nach eurem gebauten Bestand'
    d['structure']['enhancements']['features']=[dict(name='Gebauter Keller bleibt erhalten',description='Boden Y95 und Außenwände bilden die Grundlage.',group='v6_bestand'),dict(name='Großlager integriert',description='Dustless-Litematic in voller Höhe, keine gestauchten Schaltungen.',group='v6_grosslager'),dict(name='Nordwand vollständig frei',description='51 × 14 Bodenpositionen für eure vorhandenen Porter; Chunkraster im Plan beachten.',group='v6_keller')]
    d['structure']['v6']={'north_reserve':[-709,-659,125,128,767,780],'storage_anchor':[-701,102,771],'source_sha256':survey['source_sha256'],'outdoors':outdoor_changes,'water_access':water_access}
    # Preserve original entity and inventory data in the derived Litematic. Main house NBT is block-only.
    modules=json.loads((ROOT/'lagertechnik_module.json').read_text())
    meta.update(key='dustless_filter',proposed_world_anchor=[-701,102,771],rotation='unverändert')
    modules['modules'][1]=meta;modules['placement_status']='V6: Dustless-Blockgeometrie integriert. V6-Litematic enthält Filterinventare und Entities.'
    modules['vault'].update(bounds=[-701,-675,102,123,771,797],width=27,height=22,depth=27,service_gap_x=[-674,-659],shaft_target=[-661,95,803])
    (ROOT/'lagertechnik_module.json').write_text(json.dumps(modules,ensure_ascii=False,indent=2)+'\n')
    reports.VERSION=VERSION;reports.VERSION_PREVIOUS='5.26';reports.write_blocklist(seq);reports.write_materials(counts,gc,groups);reports.write_diff(changes)
    for key,label in [('house','haus'),('outdoor','aussenanlagen'),('terrain','gelaende')]:reports.write_material_csv(ROOT/f'materialbedarf_{label}.csv',d['material_scopes'][key]['counts'])
    d['structure_export']=export(d,ROOT/'blackthorn_estate_6.0.nbt')
    d['validation'].update(version=VERSION,base='5.26',blocks=len(b),fingerprint=d['meta']['fingerprint'])
    from build_audit import audit
    d['material_audit']=audit(d,ROOT)
    assert not d['material_audit']['errors'],d['material_audit']['errors']
    d['validation'].update(material_items=sum(counts.values()),material_audit_passed=True,doors_checked=d['material_audit']['doors_checked'])
    d['meta']['water_positions']=sum(v[0]=='water' for v in b.values())
    d['meta']['bubble_column_positions']=sum(v[0]=='bubble_column' for v in b.values())
    d['structure']['maintenance_shaft']={'bounds':[-662,-659,95,131,802,804],'access_floors':[95,102,124,129],'type':'Leiterzugang','automatic_items':False}
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    write_current_delta(survey,b,air)
    (ROOT/'freiraeume_6.0.csv').write_text('X;Y;Z\n'+'\n'.join(';'.join(map(str,p)) for p in sorted(air))+'\n')
    from render_v6 import render
    render()
    from render_outdoors import render as render_exterior
    render_exterior()
    from web import build
    build(d)
    from check_cellar_routes import check
    check()
    from check_outdoors_v6 import check as check_outdoors
    check_outdoors()
    from check_water_access import check as check_access
    check_access()
    print('V6 built:',len(b),'positions;',len(storage),'storage blocks;',len(air),'explicit clearance positions.')

def write_current_delta(survey,b,air):
    source={}
    for y,z,x,n,i in survey['runs']:
        pal=survey['palette'][i]
        for xx in range(x,x+n):source[xx,y,z]=(pal['name'],pal['properties'])
    needed=Counter();rows=[]
    for p,(actual,props) in source.items():
        target=b.get(p)
        if not target and p not in air:continue
        wanted,state,_=target or ('air','','')
        expected=dict(v.split('=',1) for v in state.split(',') if '=' in v)
        if actual==wanted and all(props.get(k)==v for k,v in expected.items()):continue
        rows.append([*p,actual,wanted,state,'Entfernen' if wanted=='air' else 'Setzen' if actual in ('air','cave_air') else 'Ersetzen'])
        if wanted!='air':
            for item,n in items_for_block(wanted,state):needed[item]+=n
    with (ROOT/'keller_umbau_6.0.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['X','Y','Z','Ist-Block','Ziel-Block','Ziel-State','Aktion']);w.writerows(rows)
    reports.write_material_csv(ROOT/'materialbedarf_keller_zusaetzlich.csv',needed)

if __name__=='__main__':main()
