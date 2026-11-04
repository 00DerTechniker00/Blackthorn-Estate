"""Printable comparison from the same surveyed grids as the interactive map."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
d=json.loads((ROOT/'blueprint.json').read_text());t=d['terrain'];x0,x1,z0,z1=t['bounds'];w=x1-x0+1;h=z1-z0+1
palette={'grass_block':(100,144,81),'dirt':(145,111,77),'stone':(133,139,139),'gravel':(180,170,143),'dark_oak_planks':(97,73,45),'stone_bricks':(153,159,155),'iron_block':(206,214,210),'water':(61,121,170)}
work={(r[0],r[1]):r for r in t['work']};canvas=Image.new('RGB',(1860,700),'#f5f4ee');draw=ImageDraw.Draw(canvas)
font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
draw.text((30,18),'BLACKTHORN ESTATE · GELÄNDEPLAN 5.11',font=font(25),fill='#243a30')
for index,(mode,title) in enumerate([('surface','01 / Originalwelt'),('target','02 / Begrünte Planung'),('work','03 / Abtrag und Auffüllung')]):
 im=Image.new('RGB',(w,h));pix=im.load();H=t['heights'] if mode=='surface' else t['target_heights'];M=t['surface_blocks'] if mode=='surface' else t['target_surface_blocks']
 for iz in range(h):
  for ix in range(w):
   row=work.get((ix+x0,iz+z0));col=palette.get(M[iz][ix],(112,126,109))
   if mode=='work':col=((167,124,185) if row[4] and row[5] else (230,130,59) if row[4] else (53,171,163) if row[5] else (185,174,105)) if row else (59,78,63)
   else:
    shade=max(.76,min(1.1,1+(H[iz][max(0,ix-1)]-H[max(0,iz-1)][ix])*.025));col=tuple(min(255,round(c*shade)) for c in col)
   pix[ix,iz]=col
 # Ghost outline gives orientation; the house itself is not an earthwork surface.
 overlay=Image.new('RGBA',im.size);od=ImageDraw.Draw(overlay)
 for x,z in t['house_footprint']:od.point((x-x0,z-z0),fill=(242,231,199,85))
 im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');panel=im.resize((562,442),Image.Resampling.NEAREST)
 px=30+index*610;py=115;canvas.paste(panel,(px,py));draw.text((px,74),title,font=font(19),fill='#243a30')
 for points,color in ([] if mode=='surface' else [(t['waypoints'],'#f3ddab'),(t['garden_path'],'#eee5bd')]):draw.line([(px+(p[0]-x0+.5)*2,py+(p[1]-z0+.5)*2) for p in points],fill=color,width=2)
 draw.text((px,565),'N ↑  ·  X −825…−545  /  Z 680…900',font=font(12),fill='#66766a')
 if mode=='target':
  for n,s in enumerate(d['outdoor_sites'],1):
   x=px+(s['x']-x0+.5)*2;y=py+(s['z']-z0+.5)*2;draw.ellipse((x-9,y-9,x+9,y+9),fill='#243a30',outline='#fffefa',width=1);draw.text((x-4,y-8),str(n),font=font(12),fill='white')
legend=[('#e6823b','Abtrag'),('#35aba3','Auffüllung'),('#a77cb9','Beides in einer Spalte'),('#b9ae69','Oberfläche gestalten')]
for i,(color,label) in enumerate(legend):
 x=30+i*330;draw.rectangle((x,615,x+11,626),fill=color);draw.text((x+20,610),label,font=font(15),fill='#243a30')
draw.text((30,648),f"{t['excavate_total']:,} Abtragsblöcke · {t['fill_total']:,} Auffüllblöcke · 1 Ankunftsgarten · 2 Südgarten & Pavillon".replace(',','.'),font=font(15),fill='#243a30')
draw.text((30,674),'Aus den tatsächlichen Höhen- und Arbeitslisten. Hausumriss zur Orientierung; keine Browseraufnahme oder Höhlendarstellung.',font=font(12),fill='#66766a')
canvas.save(ROOT/'assets'/'terraforming_vergleich.png')
print('Rendered terraforming_vergleich.png')
