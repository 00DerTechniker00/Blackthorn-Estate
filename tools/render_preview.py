"""Software-render the real viewer quads; requires Pillow + numpy for previews only.

This is an architectural model preview, not a browser screenshot or GPU QA.
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
faces=json.loads(Path('/tmp/blackthorn-58-geometry.json').read_text())
points=np.array([f[0] for f in faces]).reshape(-1,4,3)
colors=np.clip(np.array([f[1] for f in faces])*255,0,255).astype('uint8')
alpha=np.array([round(f[2]*255) for f in faces])


def render(name,theta,phi,distance,target,width=1600,height=1000):
    back=np.array([math.sin(phi)*math.cos(theta),math.cos(phi),math.sin(phi)*math.sin(theta)])
    right=np.array([math.sin(theta),0,-math.cos(theta)])
    up=np.cross(back,right)
    eye=np.array(target)+distance*back
    delta=points-eye
    depth=-(delta@back)
    f=height/(2*math.tan(math.pi/8))
    sx=width/2+(delta@right)/np.maximum(.1,depth)*f
    sy=height/2-(delta@up)/np.maximum(.1,depth)*f
    # Painter ordering suffices for orthogonal voxel quads; no photorealistic additions.
    order=np.argsort(depth.mean(axis=1))[::-1]
    img=Image.new('RGB',(width,height),(216,225,220));draw=ImageDraw.Draw(img,'RGBA')
    for i in order:
        if depth[i].min()<.5:continue
        if sx[i].max()<0 or sx[i].min()>width or sy[i].max()<0 or sy[i].min()>height:continue
        poly=list(zip(sx[i].tolist(),sy[i].tolist()))
        color=tuple(int(v) for v in colors[i]);a=int(alpha[i])
        draw.polygon(poly,fill=(*color,a))
    draw.rectangle((0,height-48,width,height),fill=(16,29,23,235))
    font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',18)
    draw.text((22,height-34),'BLACKTHORN ESTATE  ·  REVISION 5.8  ·  BERECHNETE MODELLVORSCHAU',font=font,fill=(232,228,211,255))
    img.save(ROOT/'assets'/name)
    print('Rendered',name)


render('anwesen_ost.png',.42,1.02,170,[-683,137,-790])
render('anwesen_west.png',math.pi-.42,1.02,173,[-700,135,-790])
render('gelaende_gesamt.png',.68,.75,310,[-695,110,-790])
