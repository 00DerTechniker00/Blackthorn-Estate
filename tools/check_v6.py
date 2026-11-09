"""Independent V6 geometry, data preservation and packaged-plan checks."""
import gzip,json,zipfile,sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from litematic_import import NBTReader
ROOT=Path(__file__).resolve().parent.parent

def check():
 d=json.loads((ROOT/'blueprint.json').read_text());b={}
 for y,z,x,n,i in d['runs']:
  bid,st,gi=d['reg'][i]
  for xx in range(x,x+n):
   assert (xx,y,z) not in b
   b[xx,y,z]=(bid,st,d['groups'][gi])
 assert d['meta']['version']=='6.0'
 assert not set(map(tuple,d['required_air']))&b.keys()
 for y in range(96,127):
  for x in range(-710,-657):
   for z in (766,814):assert b[x,y,z][0]=='deepslate_bricks'
  for z in range(767,814):
   for x in (-710,-658):
    if x==-710 and 96<=y<=98 and (775<=z<=777 or 781<=z<=782):continue
    assert b[x,y,z][0]=='deepslate_bricks'
 for x in range(-709,-658):
  for z in range(767,781):
   for y in range(122,127):assert (x,y,z) not in b
 for y in range(96,130):assert b[-661,y,803][0]=='ladder'
 for floor in (101,107,113,121,127):
  assert b[-660,floor,803][0]=='polished_deepslate'
  for dy in (1,2):assert (-660,floor+dy,803) not in b
 survey=json.loads(gzip.decompress((ROOT/'bestandsaufnahme/keller_bestand.json.gz').read_bytes()))
 checked=0
 for y,z,x,n,i in survey['runs']:
  if y!=95:continue
  pal=survey['palette'][i]
  for xx in range(x,x+n):
   if -709<=xx<=-659 and 767<=z<=813:
    assert b[xx,y,z][0]==pal['name']
    assert dict(kv.split('=',1) for kv in b[xx,y,z][1].split(',') if '=' in kv)==pal['properties'];checked+=1
 assert checked==2397
 for y in range(81,100):
  assert b[-712,y,776][0]=='ladder'
  assert b[-713,y,776][0]=='deepslate_bricks'
 original=NBTReader(gzip.decompress((ROOT/'litematics/Golem MIS Dustless Filter.litematic').read_bytes())).root()
 derived=NBTReader(gzip.decompress((ROOT/'litematics/Blackthorn_V6_Dustless.litematic').read_bytes())).root()
 for key,region in original['Regions'].items():
  dest=derived['Regions'][key]
  for field in ('BlockStates','TileEntities','Entities','Size','Position'):assert region[field]==dest[field],(key,field)
  for pal in region['BlockStatePalette']:
   if pal['Name']=='minecraft:white_stained_glass':pal['Name']='minecraft:gray_stained_glass'
  assert region==dest
 # Removed storage must not remain in the model or material counts.
 assert 'v6_grosslager' not in d['groups']
 assert d['structure']['v6']['storage_removed'] is True
 assert not any(-701<=x<=-675 and 114<=y<=120 and 771<=z<=797 for x,y,z in b)
 # Five real clear heights, single-layer floors, unchanged house footprint.
 assert d['meta']['floors']=={'EG':127,'OG':135,'Decke':142,'Dach':143}
 assert d['structure']['v6']['proposed_cellar_layout']['floors_bottom_up']==[95,101,107,113,121,127]
 for bottom,top,height in ((101,107,5),(107,113,5),(113,121,7),(121,127,5)):
  assert top-bottom-1==height
  for x in range(-701,-674):
   for z in range(771,798):
    assert (x,bottom,z) in b and (x,top,z) in b
    for y in range(bottom+1,top):assert (x,y,z) not in b,(x,y,z)
 with zipfile.ZipFile(ROOT/'downloads/BlackthornLive.jar') as jar:
  embedded=gzip.decompress(jar.read('plan.tsv.gz')).decode().splitlines()
  assert len(embedded)>1 and len(embedded[0].split('\t')[0])==64
  assert jar.read('plugin.yml')==(ROOT/'paper-plugin/src/main/resources/plugin.yml').read_bytes()
 # The hosted plan must match the atlas; an auto-sync JAR may retain an older fallback plan.
 rows=gzip.decompress((ROOT/'live-server-plan.tsv.gz').read_bytes()).decode().splitlines()
 assert rows[0].split('\t')[0]==d['meta']['fingerprint']
 assert len(rows)==len(b)+1
 i=1
 for y,z,x,n,ri in d['runs']:
  for xx in range(x,x+n):assert rows[i].split('\t')[:3]==list(map(str,(xx,y,z)));i+=1
 class HTML(HTMLParser):
  def __init__(self):super().__init__();self.ids=[];self.targets=[];self.links=[]
  def handle_starttag(self,t,a):
   a=dict(a)
   if 'id' in a:self.ids.append(a['id'])
   if 'aria-controls' in a:self.targets.append(a['aria-controls'])
   for key in ('href','src'):
    if key in a:self.links.append(a[key])
 html=HTML();html.feed((ROOT/'index.html').read_text());assert len(set(html.ids))==len(html.ids)
 assert all(t in html.ids for t in html.targets)
 for link in html.links:
  if urlsplit(link).scheme or link.startswith('#'):continue
  assert (ROOT/unquote(urlsplit(link).path)).exists(),link
 print(f'V6 passed: {len(b)} positions; existing walls; north clearance; ladder exits; old storage removed; original inventories/entities retained in source; hosted plan fingerprint; links/ARIA.')
if __name__=='__main__':check()
