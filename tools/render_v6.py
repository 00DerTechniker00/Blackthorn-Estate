"""Coordinate-true cellar floor cuts with chunk boundaries."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parent.parent

def render():
 d=json.loads((ROOT/'blueprint.json').read_text());b={}
 for y,z,x,n,i in d['runs']:
  for xx in range(x,x+n):b[xx,y,z]=d['reg'][i][0]
 im=Image.new('RGB',(1850,750),'#e5e8e4');draw=ImageDraw.Draw(im)
 f=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',17);big=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',27)
 draw.text((30,20),'Blackthorn Estate · V6 · Keller und Chunkgrenzen',font=big,fill='#223b32')
 for index,(y,name) in enumerate([(96,'Untere Räume'),(116,'Großlager · mittlerer Schnitt'),(125,'Porter-Galerie · Nordwand frei')]):
  left=35+index*610;top=125
  draw.text((left,85),f'{name} · Y {y}',font=f,fill='#223b32')
  for z in range(766,815):
   for x in range(-710,-657):
    block=b.get((x,y,z));color='#f7f4ee'
    if y==125 and 767<=z<=780:color='#dfc58e'
    if block:
     color='#647581' if 'deepslate' in block else '#a0b8c0' if 'glass' in block else '#b68558' if block in ('chest','barrel','bookshelf','ladder') else '#8f918a'
    px=left+(x+710)*10;py=top+(z-766)*10;draw.rectangle((px,py,px+9,py+9),fill=color)
  for x in (-704,-688,-672):
   px=left+(x+710)*10;draw.line((px,top,px,top+490),fill='#ad5365',width=2)
   draw.text((px+2,top+495),str(x),font=f,fill='#713d45')
  for z in (768,784,800):
   py=top+(z-766)*10;draw.line((left,py,left+530,py),fill='#ad5365',width=2)
  draw.text((left,top+525),'X −710…−658 / Z 766…814 · Norden ↑',font=f,fill='#223b32')
 draw.text((35,705),'Gold: freie Porterzone · Rot: Chunkgrenzen · Bestand und Zielbau aus echten Blockkoordinaten',font=f,fill='#223b32')
 im.save(ROOT/'assets/keller_v6.png')

if __name__=='__main__':render()
