"""Plan previews from actual new exterior block positions, not an artist impression."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parent.parent

def render():
 d=json.loads((ROOT/'blueprint.json').read_text());b={}
 for y,z,x,n,i in d['runs']:
  for xx in range(x,x+n):b[xx,y,z]=d['reg'][i][0]
 im=Image.new('RGB',(1400,1000),'#e5e8e4');draw=ImageDraw.Draw(im);f=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',18);large=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',28)
 draw.text((30,20),'Blackthorn Estate · Pool und Südgarten',font=large,fill='#223b32')
 colors={'water':'#509aa6','dark_prismarine':'#315d61','prismarine_bricks':'#7ca6a0','smooth_sandstone':'#d0c5ab','polished_deepslate':'#52606b','sea_lantern':'#e5ead0','gravel':'#b0a490','grass_block':'#83a273','allium':'#b47da1','oxeye_daisy':'#e7e5d1','azalea_leaves':'#678b58','oak_leaves':'#678b58'}
 for x0,x1,z0,z1,left,top,scale,title in [(-657,-634,770,810,35,125,17,'Poolterrasse · Norden oben'),(-738,-675,834,858,540,150,12,'Südgarten · Terrasse westlich der Orangerie')]:
  draw.text((left,top-35),title,font=f,fill='#223b32')
  for z in range(z0,z1+1):
   for x in range(x0,x1+1):
    candidates=[(y,b[x,y,z]) for y in range(121,134) if (x,y,z) in b]
    block=max(candidates)[1] if candidates else 'grass_block';color=colors.get(block,'#536664' if 'deepslate' in block else '#775c40' if any(v in block for v in ('oak','spruce','cherry')) else '#929b91')
    px=left+(x-x0)*scale;py=top+(z-z0)*scale;draw.rectangle((px,py,px+scale-1,py+scale-1),fill=color)
 draw.text((540,525),'Blockplan: sichtbare Oberseiten, keine Lichtsimulation.',font=f,fill='#223b32')
 draw.text((540,565),'Pool: ruhiger Steinrahmen, Unterwasserlicht,',font=f,fill='#223b32');draw.text((540,595),'flacher Einstieg und Holzbänke.',font=f,fill='#223b32')
 draw.text((540,645),'Garten: offene Pergola, Blumenstreifen,',font=f,fill='#223b32');draw.text((540,675),'Sitzbank und Anschluss an den vorhandenen Weg.',font=f,fill='#223b32')
 im.save(ROOT/'assets/aussen_v6.png')
if __name__=='__main__':render()
