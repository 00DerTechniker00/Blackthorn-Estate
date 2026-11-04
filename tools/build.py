#!/usr/bin/env python3
"""Rebuild the 5.10 model and interface from unchanged Revision 5.9."""
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
from lighting import refine
from region import Region

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'Blackthorn-Estate-Revision-5.9'


def csvout(name,header,rows):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(header);w.writerows(rows)


def main():
    d=json.loads((BASE/'blueprint.json').read_text());b={}
    for y,z,x,n,i in d['runs']:
        bid,st,gi=d['reg'][i]
        for xx in range(x,x+n):b[xx,y,z]=(bid,st,d['groups'][gi])
    before=b.copy();old_fingerprint=d['meta']['fingerprint'];b=refine(d,b)
    # New ceiling mounts can replace natural rock below the graded surface.
    # Preserve the original room clearance and add their exact extra cut positions.
    with (BASE/'aushub_blockliste.csv').open(encoding='utf-8-sig') as f:
        cuts=[[int(r['X']),int(r['Y']),int(r['Z']),r['Ist-Block'],r['Bereich']] for r in csv.DictReader(f,delimiter=';')]
    seen={tuple(r[:3]) for r in cuts};t=d['terrain'];x0,x1,z0,z1=t['bounds']
    workmap={(r[0],r[1]):r for r in t['work']};world=Region(ROOT.parent/'mca.zip');extra=0
    for (x,y,z),(bid,st,g) in b.items():
        if before.get((x,y,z))==b[x,y,z] or (x,y,z) in seen or not(x0<=x<=x1 and z0<=z<=z1) or y>t['heights'][z-z0][x-x0]:continue
        old=world.block(x,y,z)
        if old in ('air','cave_air','void_air') or old==bid:continue
        assert (x,z) in workmap,'New lighting must stay within existing work columns'
        row=workmap[x,z];row[4]+=1;extra+=1
        cuts.append([x,y,z,'minecraft:'+old,row[6]]);seen.add((x,y,z))
    cutmin={}
    for x,y,z,bid,zone in cuts:cutmin[x,z]=min(y,cutmin.get((x,z),y))
    t['excavate']=[[x,z,cutmin[x,z],cut,zone] for x,z,old,target,cut,fill,zone,top in t['work'] if cut]
    t['excavate_total']=len(cuts);t['excavate_columns']=len(t['excavate'])
    d['checks']['excavation']=len(cuts);d['validation']['excavation_blocks']=len(cuts);d['validation']['lighting_extra_excavation']=extra
    csvout('aushub_blockliste.csv',['X','Y','Z','Ist-Block','Bereich'],cuts)
    csvout('aushub.csv',['X','Z','Unterkante_Y','Abtrag','Bereich'],t['excavate'])
    csvout('aushub_materialien.csv',['Ist-Material','Bloecke'],Counter(r[3].removeprefix('minecraft:') for r in cuts).most_common())
    csvout('terraforming.csv',['X','Z','Ist-Boden-Y','Soll-Boden-Y','Abtrag_Bloecke','Auffuellung_Bloecke','Bereich','Soll-Oberflaeche'],t['work'])
    groups=d['groups'];reg=[];lookup={};runs=[];rows=[];counts=Counter();gm=defaultdict(Counter);stats={}
    for n,(x,y,z) in enumerate(sorted(b,key=lambda p:(p[1],p[2],p[0])),1):
        bid,st,g=b[x,y,z];record=bid,st,groups.index(g)
        if record not in lookup:lookup[record]=len(reg);reg.append(record)
        ri=lookup[record]
        if runs and runs[-1][0]==y and runs[-1][1]==z and runs[-1][2]+runs[-1][3]==x and runs[-1][4]==ri:runs[-1][3]+=1
        else:runs.append([y,z,x,1,ri])
        s=stats.setdefault(g,dict(n=0,x=[x,x],y=[y,y],z=[z,z]));s['n']+=1
        for key,v in [('x',x),('y',y),('z',z)]:s[key]=[min(v,s[key][0]),max(v,s[key][1])]
        if not (bid=='water' or bid.endswith('_door') and 'half=upper' in st or bid.endswith('_bed') and 'part=head' in st):counts[bid]+=1;gm[g][bid]+=1
        rows.append([n,x,y,z,'minecraft:'+bid,st,g])
    changed=[p for p in sorted(set(before)|set(b)) if before.get(p)!=b.get(p)]
    changed_groups=sorted({r[2] for p in changed for r in [before.get(p),b.get(p)] if r})
    d.update(reg=reg,runs=runs,counts=dict(counts),gcounts={g:dict(gm[g]) for g in groups},gstats=stats)
    d['progress_compat']=dict(revision='5.9',fingerprint=old_fingerprint,changed_positions=[','.join(map(str,p)) for p in changed],changed_groups=changed_groups)
    d['meta'].update(version='5.10',total=len(b),fingerprint=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest())
    d['validation'].update(version='5.10',base='5.9',blocks=len(b),lighting_attachments_checked=True,lighting_total=d['lighting']['total'],light_simulation_current=False)
    d['validation']['lantern_repairs']='Siehe lighting und laternen_pruefung.csv; ältere kumulierte Zählung ersetzt.'
    csvout('blockliste.csv',['Nummer','X','Y','Z','Minecraft-Block','Blockstate','Baugruppe'],rows)
    def stack(bid):return 1 if bid.endswith(('_bed','shulker_box')) else 16 if bid.endswith('_sign') else 64
    csvout('materialbedarf.csv',['Material','Anzahl','Stackgroesse','volle_Stacks','Rest','volle_Shulkers','Rest_nach_Shulkern'],
        [[bid,n,stack(bid),n//stack(bid),n%stack(bid),n//(27*stack(bid)),n%(27*stack(bid))] for bid,n in counts.most_common()])
    csvout('materialbedarf_baugruppen.csv',['Baugruppe','Material','Anzahl'],[[g,bid,n] for g in groups for bid,n in gm[g].most_common()])
    csvout('aenderungen_5.9_zu_5.10.csv',['X','Y','Z','Alt-Block','Alt-State','Alt-Gruppe','Neu-Block','Neu-State','Neu-Gruppe'],
        [[*p,*(before.get(p) or ('','','')),*(b.get(p) or ('','',''))] for p in changed])
    csvout('laternen_pruefung.csv',['ID','X','Y','Z','Block','Montage','Kettenbloecke','Anker-X','Anker-Y','Anker-Z','Ankerblock','Bereich','Planung'],
        [[f['id'],f['x'],f['y'],f['z'],f['block'],f['kind'],f['chain'],*f['anchor'],f['anchor_block'],f['group'],f['source']] for f in d['lighting']['fixtures']])
    (ROOT/'blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'check_report.json').write_text(json.dumps(d['validation'],ensure_ascii=False,indent=2)+'\n')
    from web import build
    build(d)
    print(json.dumps({k:v for k,v in d['lighting'].items() if k!='fixtures'},ensure_ascii=False,indent=2))
    print('Changes',len(changed),'groups',changed_groups,'blocks',len(b))


if __name__=='__main__':main()
