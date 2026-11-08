"""Read-only, reproducible survey of the supplied cellar, not a blueprint update."""
from pathlib import Path
from collections import Counter
import csv,gzip,json,sys
from PIL import Image,ImageDraw,ImageFont
from world_snapshot import Snapshot
ROOT=Path(__file__).resolve().parent.parent

def survey(source):
    snap=Snapshot(source);out=ROOT/'bestandsaufnahme';out.mkdir(exist_ok=True)
    box={'x':[-710,-658],'y':[94,129],'z':[766,814]}
    counts={};runs=[];palette=[];lookup={}
    for y in range(94,130):
        c=Counter()
        for z in range(766,815):
            start=-710;last=None
            for x in range(-710,-657):
                name,props=snap.block_state(x,y,z);c[name]+=1
                key=(name,tuple(sorted(props.items())))
                if key not in lookup:lookup[key]=len(palette);palette.append({'name':name,'properties':props})
                i=lookup[key]
                if last is not None and last!=i:runs.append([y,z,start,x-start,last]);start=x
                last=i
            runs.append([y,z,start,-657-start,last])
        counts[str(y)]=dict(c.most_common())
    result={'source':Path(source).name,'source_sha256':snap.sha256,'bounds':box,'format':'world-block-runs-v1','run_fields':['y','z','x','length','palette_index'],'palette':palette,'runs':runs,'counts_per_y':counts,'includes_air':True,'inventories_and_entities':False}
    (out/'keller_bestand.json.gz').write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    (out/'keller_hoehen.json').write_text(json.dumps({'source_sha256':snap.sha256,'bounds':box,'counts_per_y':counts},ensure_ascii=False,indent=2)+'\n')
    with (out/'keller_material_je_hoehe.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Y','Block','Anzahl'])
        for y,c in counts.items():
            for name,n in c.items():w.writerow([y,name,n])
    font_path='/usr/share/fonts/TTF/DejaVuSans.ttf'
    if not Path(font_path).exists():font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font=ImageFont.truetype(font_path,17);big=ImageFont.truetype(font_path,27)
    colors={'air':'#f5f2eb','cave_air':'#f5f2eb','deepslate_bricks':'#4b5c68','polished_deepslate':'#798b99','deepslate_tiles':'#35434f','iron_block':'#d49a42','torch':'#f5c657','wall_torch':'#f5c657','ladder':'#b98656','chest':'#b98656'}
    image=Image.new('RGB',(1840,1240),'#e5e8e4');d=ImageDraw.Draw(image)
    d.text((30,20),'Blackthorn Estate · vorhandener Keller',font=big,fill='#223b32')
    d.text((30,62),'Weltdatei ausgelesen · Norden oben · X nach rechts zunehmend · keine geplanten Blöcke ergänzt',font=font,fill='#223b32')
    titles=[(95,'Durchgehender Schachbrettboden'),(101,'Teilfläche / Zwischenebene'),(105,'Bisheriger Plan: Boden Keller 3'),(113,'Bisheriger Plan: Boden Keller 2'),(121,'Bisheriger Plan: Boden Keller 1'),(127,'Oberkante der Außenwände')]
    for panel,(y,title) in enumerate(titles):
        left=30+(panel%3)*605;top=115+(panel//3)*535
        d.text((left,top),f'Y {y} · {title}',font=font,fill='#223b32')
        for z in range(766,815):
            for x in range(-710,-657):
                name=snap.block(x,y,z);px=left+(x+710)*10;py=top+35+(z-766)*9
                d.rectangle((px,py,px+9,py+8),fill=colors.get(name,'#b5baac'))
        d.text((left,top+482),'X −710 … −658  /  Z 766 … 814',font=font,fill='#223b32')
    for i,(label,color) in enumerate([('Luft / offen','#f5f2eb'),('Außenwand','#4b5c68'),('Polierter Tiefenschiefer','#798b99'),('Tiefenschieferfliesen','#35434f'),('Eisen / Markierung','#d49a42')]):
        xx=30+i*360;d.rectangle((xx,1200,xx+18,1218),fill=color);d.text((xx+25,1198),label,font=font,fill='#223b32')
    image.save(out/'keller_grundrisse.png')
    im=Image.new('RGB',(1160,620),'#e5e8e4');d=ImageDraw.Draw(im)
    d.text((30,20),'Höhenschnitt · X = −684 · Blick nach Westen',font=big,fill='#223b32')
    for y in range(94,130):
        for z in range(766,815):
            px=100+(z-766)*16;py=90+(129-y)*12
            d.rectangle((px,py,px+15,py+11),fill=colors.get(snap.block(-684,y,z),'#b5baac'))
    for y,label in [(129,'EG laut Atlas'),(121,'K1 laut Atlas'),(113,'K2 laut Atlas'),(105,'K3 laut Atlas'),(95,'Vorhandener Boden')]:
        py=90+(129-y)*12;d.line((95,py,890,py),fill='#aa6952',width=1);d.text((900,py-9),f'Y {y}: {label}',font=font,fill='#223b32')
    d.text((100,550),'Z 766 → 814 · Luft hell · Bestand farbig · Atlas-Höhen nur als Bezugslinien',font=font,fill='#223b32')
    im.save(out/'keller_hoehenschnitt.png')
    print('Read-only cellar survey written to',out)

if __name__=='__main__':survey(Path(sys.argv[1]))
