#!/usr/bin/env python3
"""Rebuild the 5.11 landscape and interface from unchanged Revision 5.10."""
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
from region import Region

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'Blackthorn-Estate-Revision-5.10'


def csvout(name,header,rows):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(header);w.writerows(rows)


def main():
    d=json.loads((BASE/'blueprint.json').read_text());b={}
    for y,z,x,n,i in d['runs']:
        bid,st,gi=d['reg'][i]
        for xx in range(x,x+n):b[xx,y,z]=(bid,st,d['groups'][gi])
    before=b.copy();old_fingerprint=d['meta']['fingerprint']
    from landscape import design
    plan=design(d,b);t=d['terrain'];x0,x1,z0,z1=t['bounds'];world=Region(ROOT.parent/'mca.zip')
    def read(name):
        with (BASE/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f,delimiter=';'))
    cuts=[[int(r['X']),int(r['Y']),int(r['Z']),r['Ist-Block'],r['Bereich']] for r in read('aushub_blockliste.csv') if (int(r['X']),int(r['Z'])) not in plan]
    workmap={(r[0],r[1]):r[:] for r in t['work']}
    target=[r[:] for r in t['target_heights']];surfaces=[r[:] for r in t['surface_blocks']]
    for r in workmap.values():surfaces[r[1]-z0][r[0]-x0]=r[7]
    for (x,z),(y,zone,top) in plan.items():
        natural=t['heights'][z-z0][x-x0];target[z-z0][x-x0]=y;surfaces[z-z0][x-x0]=top
        workmap[x,z]=[x,z,natural,y,0,0,zone,top]
        for yy in range(y+1,natural+1):
            old=world.block(x,yy,z)
            if old not in ('air','cave_air','void_air') and b.get((x,yy,z),('',))[0]!=old:cuts.append([x,yy,z,'minecraft:'+old,zone])
    cutset={tuple(r[:3]) for r in cuts}
    for (x,y,z),(bid,st,g) in b.items():
        if (x,z) not in plan or y>t['heights'][z-z0][x-x0] or (x,y,z) in cutset:continue
        old=world.block(x,y,z)
        if old in ('air','cave_air','void_air') or old==bid:continue
        cuts.append([x,y,z,'minecraft:'+old,plan[x,z][1]]);cutset.add((x,y,z))
    cuts.sort(key=lambda r:(r[2],r[0],r[1]));fills=[];cutcounts=Counter();cutmin={};fillcounts=Counter()
    for x,y,z,bid,zone in cuts:
        cutcounts[x,z]+=1;cutmin[x,z]=min(y,cutmin.get((x,z),y))
    for (x,z),row in workmap.items():
        old,y=row[2],row[3];row[4]=cutcounts[x,z];row[5]=max(0,y-old)
        for yy in range(old+1,y+1):
            assert (x,yy,z) in b,('Unfilled column',x,yy,z)
            fills.append([x,yy,z,'minecraft:'+b[x,yy,z][0],row[6]])
    work=sorted(workmap.values(),key=lambda r:(r[0],r[1]))
    t.update(work=work,target_heights=target,target_surface_blocks=surfaces,
        excavate=[[x,z,cutmin[x,z],cut,zone] for x,z,old,y,cut,fill,zone,top in work if cut],
        excavate_total=len(cuts),excavate_columns=sum(bool(r[4]) for r in work),fill_total=len(fills),fill_columns=sum(bool(r[5]) for r in work))
    t['cut_spans']=[];t['fill_spans']=[]
    for values,key in [(cuts,'cut_spans'),(fills,'fill_spans')]:
        bycol=defaultdict(list)
        for x,y,z,bid,zone in values:bycol[x,z].append(y)
        for (x,z),ys in sorted(bycol.items()):
            ys=sorted(ys);start=prev=ys[0]
            for y in ys[1:]:
                if y!=prev+1:t[key].append([x,z,start,prev]);start=y
                prev=y
            t[key].append([x,z,start,prev])
    chunks={}
    for x,z,old,y,cut,fill,zone,top in work:
        if not cut and not fill:continue
        cx,cz=x//16,z//16;row=chunks.setdefault((cx,cz),[cx,cz,0,0,0]);row[2]+=1;row[3]+=cut;row[4]+=fill
    t['chunks']=sorted(chunks.values())
    t['house_footprint']=sorted({(x,z) for (x,y,z),(bid,st,g) in b.items() if y==129 and g not in ('terraform_auffuellung','terraform_oberflaeche','zufahrt','gartendeko','weg_sicherung')})
    vegetation=[[int(r['X']),int(r['Y']),int(r['Z']),r['Ist-Block'],r['Bereich']] for r in read('vegetation_entfernen.csv')]
    vegset={tuple(r[:3]) for r in vegetation}
    plant=lambda bid:bid.endswith(('_leaves','_log','_wood','_sapling')) or bid in {'short_grass','tall_grass','fern','large_fern','allium','dandelion','poppy','oxeye_daisy','cornflower','pink_petals','wildflowers','bush','leaf_litter','rose_bush','lilac','peony','vine','bee_nest'}
    for (x,z),(y,zone,top) in plan.items():
        n=t['heights'][z-z0][x-x0]
        for yy in range(n+1,min(170,n+20)+1):
            bid=world.block(x,yy,z)
            if (x,yy,z) not in vegset and plant(bid):vegetation.append([x,yy,z,'minecraft:'+bid,zone]);vegset.add((x,yy,z))
    conflicts=[r for r in cuts if r[3].removeprefix('minecraft:') in {'iron_block','beacon','chest','barrel','crafting_table'}]
    d['checks']['excavation']=len(cuts)
    d['validation'].update(excavation_blocks=len(cuts),fill_blocks=len(fills),vegetation_clear=len(vegetation),existing_structure_conflicts=len(conflicts),landscape=d['landscape_changes'])
    csvout('aushub_blockliste.csv',['X','Y','Z','Ist-Block','Bereich'],cuts)
    csvout('aushub.csv',['X','Z','Unterkante_Y','Abtrag','Bereich'],t['excavate'])
    csvout('aushub_materialien.csv',['Ist-Material','Bloecke'],Counter(r[3].removeprefix('minecraft:') for r in cuts).most_common())
    csvout('auffuellung_blockliste.csv',['X','Y','Z','Soll-Block','Bereich'],fills)
    csvout('auffuellung_materialien.csv',['Soll-Material','Bloecke'],Counter(r[3].removeprefix('minecraft:') for r in fills).most_common())
    csvout('terraforming.csv',['X','Z','Ist-Boden-Y','Soll-Boden-Y','Abtrag_Bloecke','Auffuellung_Bloecke','Bereich','Soll-Oberflaeche'],work)
    csvout('terraforming_chunks.csv',['Chunk-X','Chunk-Z','Arbeitsspalten','Abtrag','Auffuellung'],t['chunks'])
    csvout('vegetation_entfernen.csv',['X','Y','Z','Ist-Block','Bereich'],vegetation)
    csvout('bestandskonflikte.csv',['X','Y','Z','Ist-Block','Bereich'],conflicts)
    csvout('aussendekoration.csv',['Bereich','X','Boden-Y','Z','Beschreibung'],[[s['name'],s['x'],s['y'],s['z'],s['text']] for s in d['outdoor_sites']])
    d['groups']=list(dict.fromkeys(d['groups']+[r[2] for r in b.values()]));groups=d['groups'];reg=[];lookup={};runs=[];rows=[];counts=Counter();gm=defaultdict(Counter);stats={}
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
    d['progress_compat']=dict(revision='5.10',fingerprint=old_fingerprint,changed_positions=[','.join(map(str,p)) for p in changed],changed_groups=changed_groups)
    d['checks'].update(doors=sum(r[0].endswith('_door') and 'half=lower' in r[1] for r in b.values()),stairs=sum(r[0].endswith('_stairs') for r in b.values()),panes=sum(r[0]=='glass_pane' for r in b.values()))
    d['meta'].update(version='5.11',total=len(b),bbox=[min(p[0] for p in b),max(p[0] for p in b),min(p[1] for p in b),max(p[1] for p in b),min(p[2] for p in b),max(p[2] for p in b)],fingerprint=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest())
    d['validation'].update(version='5.11',base='5.10',blocks=len(b),lighting_attachments_checked=True,lighting_total=d['lighting']['total'],light_simulation_current=False)
    d['validation']['lantern_repairs']='Siehe lighting und laternen_pruefung.csv; ältere kumulierte Zählung ersetzt.'
    csvout('blockliste.csv',['Nummer','X','Y','Z','Minecraft-Block','Blockstate','Baugruppe'],rows)
    def stack(bid):return 1 if bid.endswith(('_bed','shulker_box')) else 16 if bid.endswith('_sign') else 64
    csvout('materialbedarf.csv',['Material','Anzahl','Stackgroesse','volle_Stacks','Rest','volle_Shulkers','Rest_nach_Shulkern'],
        [[bid,n,stack(bid),n//stack(bid),n%stack(bid),n//(27*stack(bid)),n%(27*stack(bid))] for bid,n in counts.most_common()])
    csvout('materialbedarf_baugruppen.csv',['Baugruppe','Material','Anzahl'],[[g,bid,n] for g in groups for bid,n in gm[g].most_common()])
    csvout('aenderungen_5.10_zu_5.11.csv',['X','Y','Z','Alt-Block','Alt-State','Alt-Gruppe','Neu-Block','Neu-State','Neu-Gruppe'],
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
