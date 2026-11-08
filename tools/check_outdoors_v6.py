"""Checks physically meaningful invariants of the new pool and garden."""
import json
from pathlib import Path
from structure_check import reachability
ROOT=Path(__file__).resolve().parent.parent

def check():
 d=json.loads((ROOT/'blueprint.json').read_text());b={}
 for y,z,x,n,i in d['runs']:
  bid,st,g=d['reg'][i]
  for xx in range(x,x+n):b[xx,y,z]=(bid,st,d['groups'][g])
 # Surface water is bounded by full walls or waterlogged stairs. Bottom lights are fully supported.
 for x in range(-651,-640):
  for z in range(780,801):
   bid,state,_=b[x,129,z]
   assert bid=='water' or bid=='smooth_quartz_stairs' and 'waterlogged=true' in state
   assert b[x,126,z][0] in ('sea_lantern','prismarine_bricks','dark_prismarine')
 for x in range(-651,-640):
  for z in (779,801):assert b[x,129,z][0] not in ('water','air')
 for z in range(780,801):
  for x in (-652,-640):assert b[x,129,z][0] not in ('water','air')
 for x in (-652,-651,-647,-646,-642,-641):
  for z in (775,806):assert (x,129,z) in b and b[x,130,z][0]=='dark_oak_stairs'
 for x in range(-656,-652):
  for z in (789,790,791):
   assert (x,129,z) in b
   assert (x,130,z) not in b and (x,131,z) not in b
 for x in range(-733,-730):
  for z in range(841,848):assert (x,126,z) not in b and (x,127,z) not in b
 result=reachability(b,d['rooms'])
 for name in ('Poolterrasse und flacher Einstieg','Rosenterrasse mit Pergola'):
  row=next(r for r in result['rooms'] if r['room']==name);assert row['reached']>0,row;print(row)
 print('Pool boundary, waterlogged entry, seating supports, clear paths and garden access passed.')
if __name__=='__main__':check()
