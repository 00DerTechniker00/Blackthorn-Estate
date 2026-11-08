"""Bounded static route and block-light checks; no redstone simulation."""
import json
from collections import deque
from pathlib import Path
from structure_check import reachability,opaque,LIGHT
ROOT=Path(__file__).resolve().parent.parent

def check():
 d=json.loads((ROOT/'blueprint.json').read_text());b={}
 for y,z,x,n,i in d['runs']:
  bid,st,g=d['reg'][i]
  for xx in range(x,x+n):b[xx,y,z]=(bid,st,d['groups'][g])
 routes=reachability(b,d['rooms']);rooms=[r for r in routes['rooms'] if r['room'] in [v['name'] for v in d['rooms'] if v['y'][0]<129 and v['group'] not in ('v6_pool','v6_garten')]]
 assert all(r['reached']>0 for r in rooms)
 assert next(r for r in rooms if r['room'].startswith('Porter'))['reached']==714
 def inside(p):x,y,z=p;return -710<=x<=-658 and 80<=y<=129 and 766<=z<=814
 light={};queue=deque()
 for p,(bid,st,g) in b.items():
  intensity=LIGHT.get(bid,0)
  if bid=='redstone_lamp' and 'lit=true' not in st:intensity=0
  if bid in ('campfire','soul_campfire') and 'lit=false' in st:intensity=0
  if intensity and inside(p):light[p]=intensity;queue.append(p)
 while queue:
  x,y,z=queue.popleft();value=light[x,y,z]-1
  if value<=0:continue
  for dx,dy,dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
   p=x+dx,y+dy,z+dz
   if not inside(p) or p in b and opaque(b[p][0]) or light.get(p,0)>=value:continue
   light[p]=value;queue.append(p)
 checks={}
 for label,floor,zlo,zhi in [('Untere Räume',95,767,813),('Porterfläche',124,767,780)]:
  samples=[]
  for x in range(-709,-658):
   for z in range(zlo,zhi+1):
    if (x,floor,z) in b and (x,floor+1,z) not in b and (x,floor+2,z) not in b:samples.append(light.get((x,floor+1,z),0))
  checks[label]={'sampled_floor_cells':len(samples),'minimum_block_light':min(samples),'zero_light_cells':samples.count(0)}
  assert 0 not in samples,(label,checks[label])
 # Side guards must leave a walkable eastern landing, with the ladder column continuous.
 for floor in (102,124,129):
  for z in (802,804):assert b[-661,floor+1,z][0]=='polished_blackstone_wall'
  assert (-660,floor+1,803) not in b and (-660,floor+2,803) not in b
 result={'revision':d['meta']['version'],'fingerprint':d['meta']['fingerprint'],'route_model':'Static supported-cell traversal; no player collision or redstone simulation','rooms':rooms,'block_light':checks,'limits':['Block opacity approximated for non-full blocks','No sky light, changing redstone states, entity collisions or real server test','Reachable furniture tops are counted as floor cells; partial room coverage is not a claim that every surface is walkable','Spawn rules of individual mobs are not simulated']}
 (ROOT/'keller_pruefung_v6.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':check()
