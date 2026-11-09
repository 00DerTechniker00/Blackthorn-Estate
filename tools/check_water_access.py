"""Static water-shaft checks; fluid/player dynamics still need a server test."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def check():
 d=json.loads((ROOT/'blueprint.json').read_text());b={}
 for y,z,x,n,i in d['runs']:
  for xx in range(x,x+n):b[xx,y,z]=d['reg'][i][:2]
 access=d['structure']['v6']['water_access']
 for key in ('house','secret'):
  lift=access[key];ux,first,z=lift['up'];dx,_,_=lift['down'];base=lift['base'];top=lift['top'];front=lift['sign_z']
  assert b[ux,base,z][0]=='soul_sand'
  assert b[dx,base,z][0]=='polished_deepslate'
  for y in range(first,top+1):
   assert b[ux,y,z]==['bubble_column','drag=false']
   if y<=base+2:assert b[dx,y,z]==['water','level=0']
   else:assert (dx,y,z) not in b
  for floor in lift['landings']:
   feet=max(floor+1,first)
   for x,side in ((ux,ux-1),(dx,dx+1)):
    for y in (feet,feet+1):
     assert b[x,y,front][0]=='spruce_wall_sign'
     assert b[side,y,front][0]=='gray_stained_glass'
    assert (x,feet,front+1) not in b and (x,feet+1,front+1) not in b
    assert (x,feet-1,front+1) in b
  assert top==lift['landings'][-1]+2
 # A proper doorway joins the corridor and the large room.
 for x in (-686,-685,-684):
  for z in (775,776,777):
   assert (x,80,z) in b
   for y in (81,82,83):assert (x,y,z) not in b
 for x in range(-684,-669):
  for z in range(770,784):assert (x,80,z) in b and (x,88,z) in b
 # Existing main staircase is preserved, not replaced by the lifts.
 old=json.loads((ROOT/'tools/seeds/revision-5.26/blueprint.json').read_text())
 for y,z,x,n,i in old['runs']:
  block,state,g=old['reg'][i]
  if old['groups'][g]!='halle_treppe':continue
  for xx in range(x,x+n):assert b[xx,y-2,z]==[block,state]
 print('Water columns, supported fluid-stop signs, landings, clear drops, room doorway and existing main stairs passed.')
if __name__=='__main__':check()
