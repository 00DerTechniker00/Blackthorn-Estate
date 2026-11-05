"""Read a local Anvil region snapshot. Missing data is reported, never invented."""
from functools import lru_cache
from pathlib import Path
import gzip,zlib,re,hashlib
from litematic_import import NBTReader

class Snapshot:
    def __init__(self,path):
        self.path=Path(path);self.raw=self.path.read_bytes()
        match=re.fullmatch(r'r\.(-?\d+)\.(-?\d+)\.mca',self.path.name)
        if not match:raise ValueError('Invalid region filename')
        self.rx,self.rz=map(int,match.groups());self.sha256=hashlib.sha256(self.raw).hexdigest()
    @lru_cache(maxsize=256)
    def chunk(self,cx,cz):
        if cx//32!=self.rx or cz//32!=self.rz:raise ValueError('Coordinate outside snapshot')
        index=4*((cx%32)+(cz%32)*32);offset=int.from_bytes(self.raw[index:index+3],'big')*4096
        if not offset:raise ValueError('Missing chunk')
        length=int.from_bytes(self.raw[offset:offset+4],'big');compression=self.raw[offset+4]
        if compression&128:raise ValueError('External chunk not supported')
        data=self.raw[offset+5:offset+4+length]
        data={1:gzip.decompress,2:zlib.decompress,3:lambda v:v}[compression](data)
        root=NBTReader(data).root()
        if root.get('Status') not in ('full','minecraft:full'):raise ValueError('Incomplete chunk')
        return {s['Y']:s for s in root['sections']}
    def block(self,x,y,z):
        section=self.chunk(x//16,z//16).get(y//16)
        if section is None or 'block_states' not in section:raise ValueError('Missing block section')
        states=section['block_states'];palette=states['palette'];slot=0
        if len(palette)>1:
            bits=max(4,(len(palette)-1).bit_length());per=64//bits;index=(y%16)*256+(z%16)*16+x%16
            slot=(states['data'][index//per]>>((index%per)*bits))&((1<<bits)-1)
        entry=palette[slot]
        return (entry if isinstance(entry,str) else entry.get('Name') or entry.get('id') or entry['']).removeprefix('minecraft:')
