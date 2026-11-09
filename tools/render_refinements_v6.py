"""Coordinate-true block cuts for the estate improvements, drawn from the final blueprint."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent

def render():
 d=json.loads((ROOT/'blueprint.json').read_text());b={}
 for y,z,x,n,i in d['runs']:
  for xx in range(x,x+n):b[xx,y,z]=d['reg'][i][0]
 image=Image.new('RGB',(1800,1070),'#e6e9e4');draw=ImageDraw.Draw(image)
 small=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',17);large=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',30)
 draw.text((30,20),'Blackthorn Estate · Licht, Stall, Dach und Flussgalerie',font=large,fill='#213b31')
 def color(block):
  if not block:return '#f7f5ef'
  if block in ('sea_lantern','glowstone'):return '#e9db95'
  if 'water' in block:return '#739ba8'
  if 'glass' in block:return '#aac6c5'
  if 'leaves' in block:return '#6a8a59'
  if block in ('hay_block','wheat'):return '#bea567'
  if 'carpet' in block:return '#94656a'
  if any(w in block for w in ('oak','spruce','barrel','bookshelf','ladder')):return '#947653'
  if 'copper' in block:return '#64998b'
  return '#647477'
 def cut(x0,x1,z0,z1,y,left,top,scale,title):
  draw.text((left,top-35),title,font=small,fill='#213b31')
  for z in range(z0,z1+1):
   for x in range(x0,x1+1):
    px=left+(x-x0)*scale;py=top+(z-z0)*scale
    draw.rectangle((px,py,px+scale-1,py+scale-1),fill=color(b.get((x,y,z))))
  draw.text((left,top+(z1-z0+1)*scale+12),f'Y {y} · X {x0}…{x1}',font=small,fill='#213b31')
  draw.text((left,top+(z1-z0+1)*scale+37),f'Z {z0}…{z1} · Norden ↑',font=small,fill='#213b31')
 cut(-755,-740,762,782,124,35,125,20,'Stall · Boxen und südlicher Hauptzugang')
 cut(-714,-704,781,800,144,420,125,20,'Westgiebel · Lesesaal')
 cut(-661,-628,781,789,108,760,125,26,'Flussgalerie · Zugang aus Keller 3, Osten →')
 # Longitudinal section shows the cliff and enclosed window, with a real block slice.
 left,top,scale=760,500,22
 draw.text((left,top-35),'Längsschnitt Z 785 · verglaste Ostfront statt offener Baugrube',font=small,fill='#213b31')
 T=d['terrain'];x0,_,z0,_=T['bounds'];clearance=set(map(tuple,d['required_air']))
 for x in range(-661,-621):
  height=T['target_heights'][785-z0][x-x0]
  for y in range(96,118):
   block=b.get((x,y,785));fill=color(block) if block else '#c0b59a' if y<=height and (x,y,785) not in clearance else '#f7f5ef'
   px=left+(x+661)*scale;py=top+(117-y)*scale
   draw.rectangle((px,py,px+scale-1,py+scale-1),fill=fill)
 draw.text((35,640),'Bauhöhen bleiben: Kellerboden 95 · Lagerboden 113 · EG 127.',font=small,fill='#213b31')
 draw.text((35,680),'Schnitte zeigen tatsächliche Baupositionen, keine Lichtsimulation.',font=small,fill='#213b31')
 draw.text((35,720),'Gelb: Lichtquelle · Blaugrau: Glas · Braun: Holz / Möbel.',font=small,fill='#213b31')
 draw.text((35,760),'Automatische Prüfungen und Ingame-Abnahme stehen im Atlas.',font=small,fill='#213b31')
 image.save(ROOT/'assets/ausbau_v6.png')
if __name__=='__main__':render()
