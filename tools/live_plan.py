"""Deterministic plugin plan, indexed in precisely the same order as atlas runs."""
import gzip
import json
from pathlib import Path

def generate(root, data):
    header = {'fingerprint': data['meta']['fingerprint'], 'revision': data['meta']['version'],
              'positions': sum(run[3] for run in data['runs'])}
    (root/'live-plan.json').write_text(json.dumps(header,separators=(',',':'))+'\n')
    dest=root/'paper-plugin/src/main/resources/plan.tsv.gz'
    dest.parent.mkdir(parents=True,exist_ok=True)
    rows=[header['fingerprint']+'\t'+header['revision']]
    for y,z,x,n,ri in data['runs']:
        block,states,group=data['reg'][ri]
        block='minecraft:'+block+('['+states+']' if states else '')
        for dx in range(n):rows.append(f'{x+dx}\t{y}\t{z}\t{block}')
    packed=gzip.compress(('\n'.join(rows)+'\n').encode(),mtime=0)
    dest.write_bytes(packed)
    (root/'live-server-plan.tsv.gz').write_bytes(packed)

if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent
    generate(root,json.loads((root/'blueprint.json').read_text()))
