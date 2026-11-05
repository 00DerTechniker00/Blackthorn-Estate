"""Read Litematica files and report exact blocks, block entities, and entities."""
from __future__ import annotations
import gzip
import hashlib
import json
import math
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class NBTReader:
    def __init__(self, raw: bytes): self.raw, self.offset = raw, 0
    def take(self, n):
        b = self.raw[self.offset:self.offset+n]
        if len(b) != n: raise ValueError('Truncated NBT')
        self.offset += n
        return b
    def number(self, fmt): return struct.unpack('>'+fmt, self.take(struct.calcsize('>'+fmt)))[0]
    def string(self): return self.take(self.number('H')).decode('utf-8')
    def payload(self, tag):
        if tag in range(1,7): return self.number({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[tag])
        if tag == 7: return self.take(self.number('i'))
        if tag == 8: return self.string()
        if tag == 9:
            child, count = self.number('B'), self.number('i')
            if count < 0 or count > 10_000_000: raise ValueError('Invalid NBT list length')
            return [self.payload(child) for _ in range(count)]
        if tag == 10:
            out = {}
            while True:
                child = self.number('B')
                if child == 0: return out
                name = self.string(); out[name] = self.payload(child)
        if tag in (11,12):
            count = self.number('i')
            if count < 0 or count > 10_000_000: raise ValueError('Invalid NBT array length')
            fmt, width = ('i',4) if tag == 11 else ('q',8)
            raw = self.take(count*width)
            return list(struct.unpack('>'+fmt*count, raw)) if count else []
        raise ValueError(f'Unsupported NBT tag {tag}')
    def root(self):
        tag = self.number('B'); self.string(); return self.payload(tag)

def read_litematic(path: Path):
    raw = gzip.decompress(path.read_bytes())
    root = NBTReader(raw).root()
    metadata = root['Metadata']
    materials, entities, block_entities, regions = Counter(), Counter(), Counter(), []
    actual_blocks = 0
    for name, region in root['Regions'].items():
        size, pos = region['Size'], region['Position']
        sx, sy, sz = (abs(size[a]) for a in ('x','y','z'))
        volume = sx * sy * sz
        palette, packed = region['BlockStatePalette'], region.get('BlockStates', [])
        bits = max(2, (len(palette)-1).bit_length()); mask=(1<<bits)-1
        if len(packed) < math.ceil(volume*bits/64): raise ValueError(f'Incomplete block array in {name}')
        region_blocks=0
        for index in range(volume):
            bit=index*bits; word, shift=divmod(bit,64)
            value=(packed[word] & ((1<<64)-1)) >> shift
            if shift+bits>64: value |= (packed[word+1] & ((1<<64)-1)) << (64-shift)
            block=palette[value & mask]['Name']
            if block != 'minecraft:air':
                materials[block.removeprefix('minecraft:')]+=1
                region_blocks += 1
        for tile in region.get('TileEntities',[]): block_entities[tile.get('id','unknown').removeprefix('minecraft:')]+=1
        for entity in region.get('Entities',[]): entities[entity.get('Id',entity.get('id','unknown')).removeprefix('minecraft:')]+=1
        regions.append({'name':name,'position':pos,'signed_size':size,
            'size':[sx,sy,sz],'volume':volume,
            'blocks':region_blocks})
        regions[-1]['block_entities']=len(region.get('TileEntities',[]))
        regions[-1]['entities']=len(region.get('Entities',[]))
    total=sum(materials.values())
    if total != metadata['TotalBlocks']:
        raise ValueError(f"{path.name}: decoded {total} non-air blocks; metadata says {metadata['TotalBlocks']}")
    return {
        'name':metadata.get('Name',path.stem),'source':path.name,
        'author':metadata.get('Author',''),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'data_version':root.get('MinecraftDataVersion'),'litematic_version':root.get('Version'),
        'total_blocks':total,'total_volume':metadata.get('TotalVolume'),
        'bounds_size':[abs(metadata['EnclosingSize'][a]) for a in ('x','y','z')],
        'regions':regions,'materials':dict(sorted(materials.items(),key=lambda v:(-v[1],v[0]))),
        'block_entities':dict(sorted(block_entities.items(),key=lambda v:(-v[1],v[0]))),
        'block_entity_total':sum(block_entities.values()),
        'entities':dict(sorted(entities.items(),key=lambda v:(-v[1],v[0]))),
        'entity_total':sum(entities.values()),
    }

def build():
    specs=[
        ('Copper Golem MIS Cherry.litematic',[-715,80,770],'golem_mis'),
        ('Golem MIS Dustless Filter.litematic',[-685,82,770],'dustless_filter'),
    ]
    modules=[]
    for filename,anchor,key in specs:
        model=read_litematic(ROOT/'litematics'/filename)
        model['key']=key; model['proposed_world_anchor']=anchor
        model['rotation']='unverändert; Quellorientierung beibehalten'
        modules.append(model)
    result={'source':'cubicmetre','source_note':'Originale Litematic-Dateien; Inventardaten/Blockentities und Entities bleiben in den Dateien erhalten.',
        'placement_status':'Planungsvorschlag; Grube, Zugang und Redstone-Verbindung noch nicht im Hauptbauplan bzw. im Spiel abgenommen.',
        'vault':{'bounds':[-715,-659,80,103,770,796], 'width':57,'height':24,'depth':27,
            'service_gap_x':[-688,-686], 'shaft_target':[-687,105,790],
            'note':'Vorgeschlagene Technikhalle direkt unter Keller 3; die Litematics separat und ohne Rotation an ihren Ankern platzieren.'},
        'modules':modules}
    (ROOT/'lagertechnik_module.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

if __name__=='__main__':
    result=build()
    for m in result['modules']:
        print(m['name'],m['total_blocks'],m['bounds_size'],m['entity_total'],'entities',m['block_entity_total'],'block entities')
