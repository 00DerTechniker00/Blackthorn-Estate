"""Write this exact block atlas as a modern gzip-compressed Minecraft structure NBT."""
import gzip
import hashlib
import json
import struct


def _name(s):
    raw=s.encode('utf-8');return struct.pack('>H',len(raw))+raw

def _string(name,value):return b'\x08'+_name(name)+_name(value)
def _int(name,value):return b'\x03'+_name(name)+struct.pack('>i',value)
def _int_list(name,values):return b'\x09'+_name(name)+b'\x03'+struct.pack('>i',len(values))+b''.join(struct.pack('>i',v) for v in values)
def _compound(name,tags):return b'\x0a'+_name(name)+b''.join(tags)+b'\x00'
def _list_compound(name,items):return b'\x09'+_name(name)+b'\x0a'+struct.pack('>i',len(items))+b''.join(b''.join(item)+b'\x00' for item in items)

def export(d,path):
    blocks=[]
    for y,z,x,n,i in d['runs']:
        bid,state,_=d['reg'][i]
        props=tuple(sorted(tuple(part.split('=',1)) for part in state.split(',') if '=' in part))
        for xx in range(x,x+n):blocks.append((xx,y,z,bid,props))
    coords=[(x,y,z) for x,y,z,_,_ in blocks]
    minimum=[min(p[i] for p in coords) for i in range(3)]
    maximum=[max(p[i] for p in coords) for i in range(3)]
    palette=[];lookup={};encoded=[]
    for x,y,z,bid,props in blocks:
        key=bid,props
        if key not in lookup:
            lookup[key]=len(palette)
            item=[_string('Name','minecraft:'+bid)]
            if props:item.append(_compound('Properties',[_string(k,v) for k,v in props]))
            palette.append(item)
        encoded.append((x-minimum[0],y-minimum[1],z-minimum[2],lookup[key]))
    entries=[[_int_list('pos',[x,y,z]),_int('state',state)] for x,y,z,state in encoded]
    root=_compound('BlackthornEstate',[
        _int('DataVersion',5023),
        _int_list('size',[maximum[i]-minimum[i]+1 for i in range(3)]),
        _list_compound('palette',palette),_list_compound('blocks',entries),_list_compound('entities',[])
    ])
    content=gzip.compress(root,compresslevel=9,mtime=0)
    path.write_bytes(content)
    return {'file':path.name,'format':'Minecraft structure NBT (.nbt, gzip)','data_version':5023,
        'blocks':len(blocks),'palette_entries':len(palette),'origin':minimum,
        'size':[maximum[i]-minimum[i]+1 for i in range(3)],'sha256':hashlib.sha256(content).hexdigest(),
        'inventory_nbt':'not represented in the build list; see the separate logistics plan'}
