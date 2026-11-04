"""Read modern Java Anvil block palettes, using only Python's standard library.

Missing chunks/sections fail explicitly; they are never silently assumed to be air.
"""
import gzip
import io
import struct
import zipfile
import zlib
from functools import lru_cache


class NBT:
    def __init__(self, data):
        self.f = io.BytesIO(data)

    def number(self, fmt):
        return struct.unpack('>' + fmt, self.f.read(struct.calcsize('>' + fmt)))[0]

    def string(self):
        return self.f.read(self.number('H')).decode('utf-8')

    def payload(self, tag):
        if tag in range(1, 7):
            return self.number({1:'b', 2:'h', 3:'i', 4:'q', 5:'f', 6:'d'}[tag])
        if tag == 7:
            return self.f.read(self.number('i'))
        if tag == 8:
            return self.string()
        if tag == 9:
            child, count = self.number('B'), self.number('i')
            return [self.payload(child) for _ in range(count)]
        if tag == 10:
            value = {}
            while True:
                child = self.number('B')
                if child == 0:
                    return value
                name = self.string()
                value[name] = self.payload(child)
        if tag in (11, 12):
            return [self.number('i' if tag == 11 else 'Q') for _ in range(self.number('i'))]
        raise ValueError(f'Unknown NBT tag: {tag}')

    def root(self):
        tag = self.number('B')
        self.string()
        return self.payload(tag)


class Region:
    def __init__(self, archive, rx=-2, rz=1):
        name = f'r.{rx}.{rz}.mca'
        with zipfile.ZipFile(archive) as z:
            matches = [n for n in z.namelist() if n.split('/')[-1] == name]
            if len(matches) != 1:
                raise ValueError(f'Expected one {name}, found {matches}')
            self.data = z.read(matches[0])
        self.rx, self.rz = rx, rz

    @lru_cache(maxsize=256)
    def chunk(self, cx, cz):
        if cx // 32 != self.rx or cz // 32 != self.rz:
            raise ValueError('Coordinate outside supplied region')
        offset = 4 * ((cx % 32) + (cz % 32) * 32)
        location = int.from_bytes(self.data[offset:offset + 3], 'big') * 4096
        if not location:
            raise ValueError(f'Missing chunk {cx}, {cz}')
        length = int.from_bytes(self.data[location:location + 4], 'big')
        method = self.data[location + 4]
        packed = self.data[location + 5:location + 4 + length]
        if method & 128:
            raise ValueError('External chunk storage is not supported')
        raw = {1:gzip.decompress, 2:zlib.decompress, 3:lambda x:x}[method](packed)
        root = NBT(raw).root()
        if root.get('Status') not in ('minecraft:full', 'full'):
            raise ValueError(f'Incomplete chunk {cx}, {cz}: {root.get("Status")}')
        return {section['Y']:section for section in root['sections']}

    def block(self, x, y, z):
        sections = self.chunk(x // 16, z // 16)
        section = sections.get(y // 16)
        if section is None or 'block_states' not in section:
            raise ValueError(f'Missing block section at {x}, {y}, {z}')
        states = section['block_states']
        palette = states['palette']
        if len(palette) == 1:
            entry = palette[0]
            return (entry if isinstance(entry, str) else entry.get('Name') or entry.get('id') or entry['']).removeprefix('minecraft:')
        bits = max(4, (len(palette) - 1).bit_length())
        per_long = 64 // bits
        index = (y % 16) * 256 + (z % 16) * 16 + (x % 16)
        value = (states['data'][index // per_long] >> ((index % per_long) * bits)) & ((1 << bits) - 1)
        entry = palette[value]
        return (entry if isinstance(entry, str) else entry.get('Name') or entry.get('id') or entry['']).removeprefix('minecraft:')
