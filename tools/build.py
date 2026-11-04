#!/usr/bin/env python3
"""Add a Minecraft-textured viewer export while preserving Revision 5.11 exactly."""
import csv
import json
from pathlib import Path
from structure_export import export as export_structure

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT


def main():
    d=json.loads((ROOT/'blueprint.json').read_text())
    old=d['meta']['fingerprint']
    d['meta']['version']='5.12'
    d['progress_compat']={'revision':'5.11','fingerprint':old,'changed_positions':[],'changed_groups':[]}
    d['validation'].update(version='5.12',base='5.11',blocks=d['meta']['total'])
    d['structure_export']=export_structure(d,ROOT/'blackthorn_estate_5.12.nbt')
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    with (ROOT/'aenderungen_5.11_zu_5.12.csv').open('w',encoding='utf-8-sig',newline='') as f:
        csv.writer(f,delimiter=';').writerow(['X','Y','Z','Alt-Block','Alt-State','Alt-Gruppe','Neu-Block','Neu-State','Neu-Gruppe'])
    from web import build
    build(d)
    print('Revision 5.12 generated:',d['meta']['total'],'unchanged blocks;',d['structure_export']['blocks'],'structure NBT blocks.')
    print('NBT size:',(ROOT/d['structure_export']['file']).stat().st_size,'bytes')


if __name__=='__main__':main()
