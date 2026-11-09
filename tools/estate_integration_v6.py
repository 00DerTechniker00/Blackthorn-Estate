"""Keep the final lamp registry and surface work tables consistent with local estate improvements."""
import csv
from collections import defaultdict

def finalize_terrain(d,root,architecture=None):
    T=d['terrain'];x0,_,z0,_=T['bounds'];rows={(r[0],r[1]):r for r in T['work']}
    # Include relocated stable / approach and restored road columns, with final metadata.
    columns={(x,z) for x,z,*_ in (architecture or {}).get('surface_columns',[])}
    if architecture:
        sx0,sx1,_,_,sz0,sz1=architecture['stable_bounds']
        columns.update((x,z) for x in range(sx0,sx1+1) for z in range(sz0,sz1+1))
    for x,z in columns:
        target=T['target_heights'][z-z0][x-x0];old=rows.get((x,z))
        if old and old[3]==target:continue
        actual=T['heights'][z-z0][x-x0]
        rows[x,z]=[x,z,actual,target,max(0,actual-target),max(0,target-actual),'Stall und Zufahrt V6',T['target_surface_blocks'][z-z0][x-x0]]
    for (x,z),row in rows.items():
        final=T['target_heights'][z-z0][x-x0]
        if row[3]!=final:row[4]=max(0,row[2]-final);row[5]=max(0,final-row[2])
        row[3]=final
        row[7]=T['target_surface_blocks'][z-z0][x-x0]
    T['work']=sorted(rows.values(),key=lambda r:(r[0],r[1]))
    T['excavate_total']=sum(r[4] for r in T['work']);T['fill_total']=sum(r[5] for r in T['work'])
    T['excavate_columns']=sum(r[4]>0 for r in T['work']);T['fill_columns']=sum(r[5]>0 for r in T['work'])
    chunks=defaultdict(lambda:[0,0,0])
    for x,z,actual,target,cut,fill,*_ in T['work']:
        counts=chunks[x//16,z//16];counts[0]+=1;counts[1]+=cut;counts[2]+=fill
    T['chunks']=[[cx,cz,*counts] for (cx,cz),counts in sorted(chunks.items())]
    # Existing underground excavation spans stay intact. Surface additions are
    # represented separately from geological cave excavation and the cellar survey.
    with (root/'gelaende_aktuell_v6.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['X','Z','Historischer-Boden-Y','Ziel-Boden-Y','Abtrag','Auffuellung','Bereich','Oberflaeche']);w.writerows(T['work'])
    with (root/'gelaende_chunks_v6.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Chunk-X','Chunk-Z','Spalten','Abtrag','Auffuellung']);w.writerows(T['chunks'])
    return {'columns':len(T['work']),'cut':T['excavate_total'],'fill':T['fill_total'],'underground_note':'Historische Geologiespannen bleiben getrennt; Kellerumbau und Flussgalerie anhand Freiraumliste bauen.'}

def lamp_registry(d,b):
    old={(f['x'],f['y'],f['z']):f for f in d['lighting']['fixtures']};result=[]
    for (x,y,z),(bid,state,group) in sorted(b.items()):
        if bid not in ('lantern','soul_lantern'):continue
        hanging='hanging=true' in state;anchor=[x,y+1 if hanging else y-1,z];chain=0
        while hanging and b.get(tuple(anchor),('',))[0] in ('chain','iron_chain'):
            chain+=1;anchor[1]+=1
        fixture=dict(old.get((x,y,z),{}));fixture.update(id=fixture.get('id',f'V6-{x}-{y}-{z}'),x=x,y=y,z=z,block=bid,group=group,hanging=hanging,chain=chain,anchor=anchor,anchor_block=b.get(tuple(anchor),('',))[0],checked=tuple(anchor) in b)
        fixture.setdefault('level','Anwesen · aktuelle Bauhöhe');fixture.setdefault('kind','Deckenleuchte' if hanging else 'Sockelleuchte');fixture.setdefault('source','Gemeinsame Überarbeitung V6')
        result.append(fixture)
    d['lighting']['fixtures']=result;d['lighting']['attachment_checked']=all(f['checked'] for f in result)
