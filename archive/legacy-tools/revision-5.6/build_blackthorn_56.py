import re, json, csv, zipfile, shutil, math
from pathlib import Path
from collections import Counter, defaultdict

SRC=Path('/mnt/data/Blackthorn-Estate-Revision-5.5')
OUT=Path('/mnt/data/Blackthorn-Estate-Revision-5.6')
shutil.rmtree(OUT,ignore_errors=True); OUT.mkdir()
text=(SRC/'index.html').read_text(encoding='utf-8')
D=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',text,re.S).group(1))
G=D['groups']; R=[list(t) for t in D['reg']]; rm={(a,b,c):i for i,(a,b,c) in enumerate(R)}
for g in ['sortierung','bulk_lager','golem_lager','trading_hall','geheimraum','geheimgang','lager_technik']:
 if g not in G:G.append(g)

blocks={}
for y,z,x,n,ri in D['runs']:
 for i in range(n):
  key=(x+i,y,z)
  if key in blocks: raise ValueError(f'duplicate {key}')
  blocks[key]=ri
original=blocks.copy()

def record(id='',state='',group='sortierung'):
 gi=G.index(group)
 k=(id,state,gi)
 if k not in rm:rm[k]=len(R);R.append([id,state,gi])
 return rm[k]
def setb(x,y,z,id,state='',group='sortierung'):
 blocks[(x,y,z)]=record(id,state,group)
def delete(x,y,z):blocks.pop((x,y,z),None)
def at(x,y,z):
 r=blocks.get((x,y,z));return None if r is None else R[r]
def clear_interior(x0,x1,z0,z1, y0,y1, preserve=None):
 preserve=preserve or set()
 for x in range(x0,x1+1):
  for z in range(z0,z1+1):
   for y in range(y0,y1+1):
    if (x,y,z) not in preserve:delete(x,y,z)

def floor(x0,x1,z0,z1,y,id,group):
 for x in range(x0,x1+1):
  for z in range(z0,z1+1):setb(x,y,z,id,'',group)

# ------ Floor 1 / central depot: original cellar 1 Y121..128; preserve west workshops and service stairs ------
# Central drop station in the main corridor at [-713,125,789], with underground path towards north-side bulk bays.
# Maintained 3-wide hallway at z=788..792 mostly untouched except waist-high input cabinet.
setb(-708,124,789,'chest','facing=south,type=single,waterlogged=false','sortierung')
setb(-708,123,789,'hopper','facing=north,enabled=true','lager_technik')
# pipe from hopper below input to north channel; north room z=767..786
for z in range(788,783,-1):setb(-708,123,z,'hopper','facing=north,enabled=true','lager_technik')
# horizontal sorter main feed runs east in enclosed service trunk
for x in range(-707,-674):setb(x,123,784,'hopper','facing=east,enabled=true','lager_technik')
setb(-708,123,784,'hopper','facing=east,enabled=true','lager_technik')
setb(-675,123,784,'hopper','facing=south,enabled=true','lager_technik')
# fill support maintenance runway top corridor, avoid obstructing central hallway
for x in range(-707,-676):
 if x%4==0:setb(x,125,784,'lantern','hanging=false','lager_technik')

# ---- Bulk wall -- 6 pre-seeded filter modules in cellar 1 north. A physical module skeleton only;
# filter NBT and reliable timing need manual in-game setup. Place controls at Y122 and chest outputs at Y123.
bulk=[
 ('cobblestone','Bruchstein',-704),('dirt','Erde',-699),('iron_ingot','Eisenbarren',-694),
 ('deepslate','Tiefenschiefer',-689),('stone','Stein',-684),('gravel','Kies',-679)]
# two north-facing bay corridors. Some original room partitions go away to make a longer aisle.
clear_interior(-706,-675,767,783,122,126)
# new floor decorative but no disruption to main y121 base
for x in range(-706,-675):
 for z in range(767,784):
  if (x+z)%7==0:setb(x,121,z,'polished_deepslate','','bulk_lager')
# reapply hopper line after clearing room
for x in range(-707,-674):setb(x,123,784,'hopper','facing=east,enabled=true','lager_technik')
setb(-708,123,784,'hopper','facing=east,enabled=true','lager_technik')
setb(-675,123,784,'hopper','facing=south,enabled=true','lager_technik')
# bulk modules are separated with solid-sided partitions and pre-seeded double chests (each destination has a seed item stored in in-game GUI)
for item,label,x in bulk:
 # filter hopper and collection line into barrel buffer
 setb(x,122,784,'hopper','facing=north,enabled=false','lager_technik')
 setb(x,122,783,'hopper','facing=north,enabled=true','lager_technik')
 setb(x,122,782,'hopper','facing=north,enabled=true','lager_technik')
 # comparator redstone signal behind filter hopper; exact circuit alignment to test in-game
 setb(x,122,785,'comparator','facing=south,mode=compare,powered=false','lager_technik')
 for zz in (786,787):setb(x,122,zz,'redstone_wire','power=0','lager_technik')
 setb(x,121,786,'repeater','facing=north,delay=1,locked=false,powered=false','lager_technik')
 setb(x,121,785,'redstone_torch','lit=true','lager_technik')
 # chest stacks in bays, buffered by hopper. Chest facing north to avoid neighboring merges.
 for yy in (122,123,124):
  for zz in (779,778):
   setb(x,yy,zz,'chest','facing=north,type=single,waterlogged=false','bulk_lager')
 # alternate stairs/trim not covering chests
 for zz in (777,781):
  setb(x,121,zz,'polished_deepslate','','bulk_lager')
 # maintenance lighting above module and room signs
 setb(x,126,779,'lantern','hanging=true','bulk_lager')
 # signs could be added as wall signs but need blockstate; use readable labels in website instead
 # Use transparent glass separator for each module at x+2
 for zz in range(767,782):
  for yy in (123,124):
   if zz in (773,774):continue
   setb(x+2,yy,zz,'glass_pane','', 'bulk_lager')
# Bulk additional empty chest pairs for overflow manually mapped, no automatic connection claimed
for x in (-704,-694,-684):
 for zz in (770,769):setb(x,123,zz,'barrel','facing=up','bulk_lager')

# ---- Overflow from redstone trunk to one copper chest ----
# Continue east then south along a ceiling service run: only one user drop point
for z in range(785,797):setb(-675,123,z,'hopper','facing=south,enabled=true','lager_technik')
setb(-675,123,797,'copper_chest','facing=south,type=single,waterlogged=false','golem_lager')
# Copper chest should be accessible to golems in adjacent south room, with room to pathfind
# Golem sorting bay on southern end of cellar1
clear_interior(-694,-671,795,812,122,126)
# remove partition between previous two south storage rooms; keep main corridor wall row z=794 with access at x=-680
for x in range(-693,-671):
 for y in range(122,126):
  # interior already cleared
  pass
# bulk/regular storage chests seeded each with one item of desired type by players
regular=[
 ('wood','Holz & Pflanzen',-692,799),('food','Essen & Farming',-688,799),('mob','Mobdrops',-684,799),
 ('redstone','Redstone',-680,799),('tools','Werkzeuge',-676,799),('decor','Deko & Baublöcke',-672,799),
 ('ores','Erze & Edelsteine',-692,808),('nether','Nether & End',-688,808),('potions','Tränke & Magie',-684,808)
]
for category,label,x,z in regular:
 for y in (123,124):
  setb(x,y,z,'chest','facing=west,type=single,waterlogged=false','golem_lager')
  # back-of-chest icon pillar
  setb(x,y-1,z-1,'dark_oak_planks','','golem_lager')
 # signs for visual tags - explicit blockstate supports wall sign
 setb(x,125,z,'spruce_wall_sign','facing=north,waterlogged=false','golem_lager')
# corridor center must stay empty for pathfinding
for x in range(-693,-670):
 for z in range(802,806):
  for y in range(123,126):
   if (x,y,z) in blocks and (x,y,z) not in [(-675,123,797)]:delete(x,y,z)
# golem bay lighting on walls, clear floor for 2-3 golems; mobs spawned in game, not in blueprint
for x,z in [(-692,804),(-683,804),(-674,804)]:setb(x,126,z,'lantern','hanging=true','golem_lager')
# first copper chest intake access and safe hopper-side roof
setb(-675,123,797,'copper_chest','facing=north,type=single,waterlogged=false','golem_lager')

# ---- Lower floor 2: additional bulk overflow + workshop + logistics bay; trading lower floor 3 ----
# Floor2 Y113 floor, 114..120 interior. Reserve x[-682,-671] z[767,786] for overflow storage / shulkers.
clear_interior(-682,-672,768,784,114,119)
for x in (-680,-677,-674):
 for z in (772,775,778,781):
  for y in (115,116):setb(x,y,z,'barrel','facing=up','bulk_lager')
for x,z in [(-679,769),(-675,769),(-679,783),(-675,783)]:setb(x,119,z,'lantern','hanging=true','bulk_lager')
# floor2 hobby area w/ map room / library not destructive

# ---- Level3: consolidated Trading Hall & behind-wall worker corridor ----
# current rooms -706..-696 and -694..-684 north; merge with framed portal
clear_interior(-705,-685,768,785,106,110)
# ensure floor and ceiling, preserve outer walls and neighboring vault
for x in range(-706,-684):
 for z in range(767,787):
  if (x,105,z) not in blocks:setb(x,105,z,'deepslate_bricks','','trading_hall')
  if (x,112,z) not in blocks:setb(x,112,z,'stone_bricks','','trading_hall')
# break central partition wall x=-695 on y107..110 where hall flows, keep pillars corners
for z in range(769,785):
 for y in range(107,111):delete(-695,y,z)
# two facing rows, five booths each; each workstation on stall floor with air access
jobs=['librarian','librarian','librarian','farmer','farmer','armorer','toolsmith','weaponsmith','cleric','mason']
workstations=['lectern','lectern','lectern','composter','composter','blast_furnace','smithing_table','grindstone','brewing_stand','stonecutter']
stalls=[]
for i,x in enumerate((-704,-700,-696,-692,-688)):
 for row,z in enumerate((771,783)):
  j=i+5*row;job=jobs[j]
  # stall at z=771 or 783; workstation on cell front; 2-block air path adjacent
  setb(x,106,z,workstations[j],'','trading_hall')
  for zz in (z-2,z+2):
   for y in (107,108):setb(x, y,zz,'dark_oak_fence','','trading_hall')
  # floor line, leaving aisle center z=775..779 empty
  setb(x,106,z-1 if row==0 else z+1,'polished_deepslate','','trading_hall')
  setb(x,110,z,'lantern','hanging=true','trading_hall')
  stalls.append({'id':f'T{j+1:02d}','profession':job,'workstation':workstations[j],'x':x,'y':106,'z':z,
                 'note':'Dorfbewohner im Spiel einsetzen; Arbeitsplatz muss erreichbar sein'})
# floor marker and side door to stock rooms
for x in range(-705,-684):
 for z in (775,779):setb(x,105,z,'polished_deepslate','','trading_hall')

# ---- Secret facilities level3 ----
# secret lounge existing at x -694..-684 north: move lounge south to preserve trading hall
# south room from x -694..-684 z 794..813 - secret library and meeting room
clear_interior(-693,-685,795,811,107,110)
for x in (-692,-689,-686):
 for z in (799,802,805,808):
  setb(x,106,z,'bookshelf','','geheimraum')
# chest vault and study, 6-player meeting table
for x in range(-691,-686):setb(x,106,803,'dark_oak_slab','type=top','geheimraum')
for x,z in [(-691,801),(-687,801),(-691,806),(-687,806)]:setb(x,106,z,'spruce_stairs','facing=north,half=bottom','geheimraum')
setb(-689,110,803,'soul_lantern','hanging=true','geheimraum')
setb(-689,106,808,'lectern','facing=north','geheimraum')
# hidden passage from central corridor via door behind book wall; behind lounge at Z=794
# maintain wall around opening and passage x=-689
for z in (791,792,793,794,795,796):
 for y in (107,108):delete(-689,y,z)
for y in (107,108):setb(-689,y,794,'dark_oak_door',f'facing=north,half={"lower" if y==107 else "upper"},hinge=left,open=false','geheimgang')
for x in (-690,-688):
 for z in (792,793,794):setb(x,107,z,'bookshelf','','geheimgang')
# player's optional painting camouflage: artwork entity not representable as blocks; note in instructions.

# vault remains west at x -721..-708 z767..786; concealed passage from hall to vault via shared wall x=-707
for x in (-709,-708,-707,-706):
 for z in (777,778):
  for y in (107,108):delete(x,y,z)
setb(-707,107,777,'iron_door','facing=east,half=lower,hinge=left,open=false,powered=false','geheimgang')
setb(-707,108,777,'iron_door','facing=east,half=upper,hinge=left,open=false,powered=false','geheimgang')
setb(-707,107,776,'lever','face=floor,facing=north,powered=false','geheimgang')
# small tucked-away emergency vault route, side chest inside preexisting vault
for x,z in [(-716,772),(-713,772),(-716,779),(-713,779)]:setb(x,107,z,'chest','facing=north,type=single,waterlogged=false','geheimraum')
# map archive in floor3 south-west room -706..-696 z794..813 preserved, add access secret door to lounge through x=-695
for z in (803,804):
 for y in (107,108):delete(-695,y,z)
setb(-695,107,803,'spruce_door','facing=east,half=lower,hinge=right,open=false','geheimgang')
setb(-695,108,803,'spruce_door','facing=east,half=upper,hinge=right,open=false','geheimgang')

# label room descriptions: remove obsolete guests? no; update affected and add functional entries
for r in D['rooms']:
 n=r['name']
 if r['group']=='keller_1' and 'Lager' in n and r['z'][0]<790:
  r['text']='Automatisches Bulk-Lager: Hopperfilter für Erde, Bruchstein, Eisen, Tiefenschiefer, Stein und Kies; Wartungsgang und Überlaufbehälter.'
 elif r['group']=='keller_1' and 'Lager' in n and r['z'][0]>790:
  r['text']='Kupfergolem-Sortierzone: Kategorien-Truhen mit Startitem, Wachs-Golems und Kupfertruhen-Übergabe; zentraler Einwurf im Mittelgang.'
 elif r['group']=='keller_3' and ('Handelshalle' in n or 'Geheimlounge' in n):
  r['text']='In die vergrößerte Handelshalle mit zehn Ständen integriert. Zugang zur Tresorkammer und verborgenen Lounge nur über markierte geheime Durchgänge.'
D['rooms'].extend([
 {'name':'Zentrale Einwurfstation','group':'sortierung','x':[-710,-705],'y':[122,126],'z':[787,791], 'text':'Einziger öffentlicher Einwurf: Truhe über Hopperleitung. Alle Items laufen erst an Bulkfiltern vorbei und anschließend in eine Kupfertruhe für Kupfergolems.', 'access':'Keller 1, zentraler Mittelgang. Hopperroute z=784 nach Osten; nur von der Wartungsseite zugänglich.','stand':30,'reach':0},
 {'name':'Bulk-Lager und Redstone-Filter','group':'bulk_lager','x':[-706,-675],'y':[121,127],'z':[767,787], 'text':'Sechs Filterkategorien; je fünf Blöcke Abstand. Truhenstapel, Hopper, Komparatoren, Repeater und Wartungszugang.', 'access':'Keller 1 Nordbereich; Truhen bleiben von der Gangseite erreichbar.','stand':380,'reach':0},
 {'name':'Kupfergolem-Lagerhalle','group':'golem_lager','x':[-694,-671],'y':[121,128],'z':[795,812], 'text':'Neun beschriftete Kategorien-Truhen und eine Kupfertruhe als Sortiereingang. Zwei bis drei gewachste Kupfergolems im Spiel einsetzen.', 'access':'Keller 1 Südostbereich. Golems in der Sortierhalle halten; Truhen mit Startitem vorbereiten.','stand':350,'reach':0},
 {'name':'Große Trading Hall','group':'trading_hall','x':[-706,-684],'y':[105,112],'z':[767,786], 'text':'Zehn Villager-Stände, fünf pro Seite, vier Bibliothek/Farmer und spezialisierte Schmiede; gewerbliche Beleuchtung und Wartungsgang.', 'access':'Keller 3 über Kellertreppenhaus und Mittelgang. Dorfbewohner können nicht als Block in die CSV aufgenommen werden.','stand':270,'reach':0},
 {'name':'Verborgene Bibliothekslounge','group':'geheimraum','x':[-694,-684],'y':[105,112],'z':[794,813], 'text':'Privater Besprechungsraum für sechs Personen, mit Bücherregalen, Lesepult und verstecktem Eingang hinter Bücherwand.', 'access':'Verdeckter Durchgang vom Keller-3-Mittelgang bei X=-689, Z=794, Y=107.','stand':100,'reach':0},
 {'name':'Tresor-Geheimzugang','group':'geheimgang','x':[-710,-706],'y':[105,112],'z':[775,780], 'text':'Kurzer verborgener Korridor zur Tresorkammer, mit abschließbarer Eisentür und verstecktem Schalter.', 'access':'Keller 3, zwischen Handelshalle und Tresor.','stand':20,'reach':0}
])

# ---- Functional plan metadata: explicit limitations and categories ----
D['storage_system']={
 'title':'Blackthorn Zentral-Lager',
 'input':{'x':-708,'y':124,'z':789,'block':'chest','name':'Einzige Einwurfstelle'},
 'mechanism':'Hopperleitung -> 6 Redstone-Bulkfilter -> Kupfertruhe -> Kupfergolems -> sortierte Truhen',
 'bulk':[{'id':it,'label':label,'x':x,'y':123,'z':778,'filter':{'x':x,'y':122,'z':784}} for it,label,x in bulk],
 'regular':[{'id':cat,'label':label,'x':x,'y':123,'z':z} for cat,label,x,z in regular],
 'stalls':stalls,
 'secrets':[{'name':'Geheime Bibliothekslounge','x':-689,'y':107,'z':794}, {'name':'Tresor-Geheimzugang','x':-707,'y':107,'z':777}],
 'mechanics':{'golem_max_items_per_trip':16,'golem_max_chests_per_search':10,'golem_search_horizontal':32,'golem_search_vertical':8,
 'notes':['Golems greifen nur aus Kupfertruhen zu und sortieren in normale Truhen.','Normale Zieltruhen mit mindestens einem entsprechenden Item initialisieren; leere Truhen werden sonst ebenfalls als gültig erkannt.','Kupfergolems gegen vollständige Oxidation wachsen.','Bulk-Filter brauchen in der Testwelt je 41 Zielfilter-Items und 4 umbenannte Platzhalter in den vier anderen Slots.','Die Blockliste enthält keine Hopper-Inventar-NBT; Inbetriebnahme und zuverlässiges Redstone-Timing müssen im Spiel geprüft werden.','Ein einzelnes öffentliches Fass; die anderen Behälter sind Maschinen- und Zielinventare.']}}

# regroup counts and integrity
coords=sorted(((x,y,z,ri) for (x,y,z),ri in blocks.items()),key=lambda t:(t[1],t[2],t[0]))
used=[]; seen={}
for x,y,z,ri in coords:
 key=tuple(R[ri])
 if key not in seen:seen[key]=len(used);used.append(list(key))
compact=[(x,y,z,seen[tuple(R[ri])]) for x,y,z,ri in coords]
runs=[]; curr=None
for x,y,z,ri in compact:
 if curr is not None and curr[0]==y and curr[1]==z and curr[4]==ri and x==curr[2]+curr[3]:curr[3]+=1
 else:
  if curr:runs.append(curr)
  curr=[y,z,x,1,ri]
if curr:runs.append(curr)
D['reg']=used; D['runs']=runs
D['meta']['total']=len(compact);D['meta']['version']='5.6';D['meta']['bbox']=[min(x for x,y,z,i in compact),max(x for x,y,z,i in compact),min(y for x,y,z,i in compact),max(y for x,y,z,i in compact),min(z for x,y,z,i in compact),max(z for x,y,z,i in compact)]

# counts (no blocks for spawned copper golems/villagers)
cnt=Counter();gc=Counter();gstats={g:{'n':0,'x':[10**9,-10**9],'y':[10**9,-10**9],'z':[10**9,-10**9]} for g in G}
for x,y,z,i in compact:
 bid,st,gi=used[i];g=G[gi]
 if not ((bid.endswith('_door') and 'half=upper' in st) or (bid.endswith('_bed') and 'part=head' in st)):cnt[bid]+=1
 gc[g]+=1; v=gstats[g];v['n']+=1
 for coord,k in ((x,'x'),(y,'y'),(z,'z')):
  v[k][0]=min(v[k][0],coord);v[k][1]=max(v[k][1],coord)
D['counts']=dict(cnt); D['gcounts']=dict(gc);D['gstats']=gstats
D['checks']['doors']=sum(1 for x,y,z,i in compact if used[i][0].endswith('_door') and 'half=lower' in used[i][1]); D['checks']['stairs']=sum(1 for x,y,z,i in compact if 'stairs' in used[i][0]); D['checks']['panes']=sum(1 for x,y,z,i in compact if used[i][0]=='glass_pane');D['checks']['storage_note']='Keller 1 und 3 umgebaut: neue Blöcke und Infrastruktur sind modelliert; Hopper-NBT und vollständig getestete Ingame-Redstone-Schaltung noch ausstehend.'

# copy existing assets
for p in SRC.rglob('*'):
 if not p.is_file():continue
 if p.name in ['index.html','blockliste.csv','materialbedarf.csv','README.md']:continue
 target=OUT/p.relative_to(SRC);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
with (OUT/'blockliste.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Nummer','X','Y','Z','Minecraft-Block','Blockstate','Baugruppe']);
 for n,(x,y,z,i) in enumerate(compact,1):
  a,b,gi=used[i];w.writerow([n,x,y,z,'minecraft:'+a,b,G[gi]])
with (OUT/'materialbedarf.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Material','Anzahl','volle_Stacks','Rest','volle_Shulkers_64','Rest_nach_Shulkern']);
 for a,n in cnt.most_common():
  stack=16 if a.endswith('_sign') else 1 if a.endswith('_bed') else 64
  w.writerow([a,n,n//stack,n%stack,n//(27*stack),n%(27*stack)])
with (OUT/'lager_kategorien.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Technik','Kategorie','Material/Typ','X','Y','Z']);
 for b in D['storage_system']['bulk']:w.writerow(['Bulk-Redstone',b['label'],b['id'],b['x'],b['y'],b['z']])
 for b in D['storage_system']['regular']:w.writerow(['Kupfergolem',b['label'],b['id'],b['x'],b['y'],b['z']])
with (OUT/'villager_staende.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Stand','Beruf','Arbeitsblock','X','Y','Z']);
 for v in stalls:w.writerow([v['id'],v['profession'],v['workstation'],v['x'],v['y'],v['z']])

# preserve existing HTML layout; new view matches existing design
html=text.replace('Revision 5.5','Revision 5.6').replace('Bauplan Revision 5.5','Bauplan Revision 5.6')
# Add sidebar tab in familiar look
html=html.replace('<button data-tab="storage">Lagerplanung</button>', '<button data-tab="storage">Lagerplanung</button><button data-tab="system">Sortierkeller & Handel</button>')
# update storage old description to reference actual new model
html=html.replace('Diese Aufteilung ist eine <strong>Einrichtungsplanung</strong>, keine bereits gesetzte Truhen-/Sortieranlage.', 'Der neue Sortierkeller enthält <strong>konkrete Blockpositionen</strong> für Bulkfilter, Kupfergolem-Lager, Handel und Geheimräume. Die Hopper-Inventare und Dorfbewohner müssen jedoch noch im Spiel eingerichtet werden.')
html=html.replace('Truhen zunächst manuell nach Kategorien beschriften. Für automatische Sortierung erst Platzbedarf, Wasserwege und Redstone-Mechanik im Spiel prüfen.', 'Das konkret geplante Sortiersystem findest du unter „Sortierkeller & Handel“. Von einer einzigen Einwurfstelle führen Hopper zuerst zu Bulk-Filtern, dann zur Kupfertruhe für Golems. Vor dem Survivalbau die Schaltung in einer Testwelt prüfen.')
# new page HTML preexisting classes
new_section='''<section class="tab" id="tab-system">
 <div class="hero"><div class="card lead"><h1>Die Kellerzentrale</h1><p class="muted">Ein öffentlicher Einwurf, zwei automatische Sortierverfahren, zehn Villager-Stände und verborgene Räume. Dieser Bauplan enthält die Koordinaten der Technik und Container. Filterinventare, Villager und Kupfergolems müssen im Minecraft-Spiel eingesetzt werden.</p><div class="cta"><button class="btn primary" id="sysGotoInput">Einwurf im Grundriss</button><button class="btn" id="sysGotoTrade">Trading-Hall im Grundriss</button></div></div>
 <div class="stats"><div class="stat"><b>1</b><span>öffentlicher Einwurf</span></div><div class="stat"><b>6</b><span>Bulkfilter-Module</span></div><div class="stat"><b>10</b><span>Trading-Stände</span></div></div></div>
 <div class="card" style="margin-bottom:16px"><h2>So funktioniert der Materialfluss</h2><div class="sys-flow"><div>Einwurftruhe<br><small>X −708 / Y 124 / Z 789</small></div><span>→</span><div>6 Bulkfilter<br><small>Hopper & Redstone</small></div><span>→</span><div>Kupfertruhe<br><small>Restliche Materialien</small></div><span>→</span><div>Kupfergolems<br><small>9 Kategorien</small></div></div><p class="muted">Wichtig: Das ist der geplante Maschinenfluss, keine bereits in Minecraft durchlaufgetestete Schaltung. Die normalen Kategorie-Truhen müssen jeweils mit passenden Startitems belegt werden; leere Truhen würden sonst ebenfalls Items annehmen.</p></div>
 <div class="grid2" style="margin-bottom:16px"><div class="card"><h2>Bulk-Materialien</h2><div id="sysBulk"></div></div><div class="card"><h2>Kupfergolem-Kategorien</h2><div id="sysRegular"></div></div></div>
 <div class="card" style="margin-bottom:16px"><h2>Kellergrundriss – X/Z mit Koordinaten</h2><div class="toolbar"><label>Etage <select id="sysLevel"><option value="121">Keller 1 · Y 121–128</option><option value="113">Keller 2 · Y 113–120</option><option value="105">Keller 3 · Y 105–112</option></select></label><span class="muted">Über markierte Elemente fahren oder klicken</span></div><div class="sys-map-wrap"><canvas id="sysMap" width="940" height="530"></canvas></div><div id="sysInfo" class="card" style="margin-top:10px">Fahre über eine Markierung für X/Y/Z und Funktion.</div></div>
 <div class="grid2" style="margin-bottom:16px"><div class="card"><h2>Trading Hall · Keller 3</h2><div id="sysStalls"></div></div><div class="card"><h2>Geheimräume</h2><p><b>Bibliothekslounge</b> bei X −689, Y 107, Z 794: versteckter Bücherwandzugang, Besprechungstisch für sechs Spieler und Archiv.</p><p><b>Tresorpassage</b> bei X −707, Y 107, Z 777: Eisentür mit Hebel, Zugang zur Tresorkammer.</p><p class="muted">Geheime Türen sind sichtbar für den Blockplan; Verkleidungen mit Bildern sind Minecraft-Entities und nicht Teil der Blockliste.</p></div></div>
 <div class="card"><h2>Inbetriebnahme – unbedingt prüfen</h2><ol class="changes"><li>In einer Testwelt die Hopperrichtung und den Durchlauf vom Einwurf zum Kupferbehälter prüfen.</li><li>Je Bulkfilter das Filterinventar einstellen und Komparator/Repeater/Redstone-Signal testen. Übliche Vorlage: 41 Zielfilter-Items plus je ein umbenannter Platzhalter in vier Slots (für 64er Items).</li><li>Die neun Zieltruhen vor dem ersten Start jeweils mit einem passenden Item vorbereiten. Keine leeren Truhen in Reichweite der Golems lassen.</li><li>Gewachste Kupfergolems in der südlichen Lagerhalle einsetzen und kontrollieren, ob sie alle Kategorien erreichen.</li><li>Zehn Villager in der Trading Hall platzieren. Jeden Arbeitsplatz vom zugehörigen Stand aus erreichbar halten und Restocks prüfen.</li><li>Geheimtüren / Hebel / Bilder im Spiel testen; blockgetreue Darstellung allein garantiert die Schaltung nicht.</li></ol></div>
</section>'''
html=html.replace('<section class="tab" id="tab-steps">',new_section+'\n<section class="tab" id="tab-steps">')
html=html.replace('</style>\n</head>','''
.sys-flow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:18px 0}.sys-flow div{border:1px solid var(--line);background:var(--code);border-radius:10px;padding:12px 16px;text-align:center;min-width:130px;flex:1}.sys-flow span{color:var(--accent);font-weight:bold;font-size:22px}.sys-map-wrap{overflow:auto;border:1px solid var(--line);border-radius:10px;background:#15231d;margin-top:12px}.sys-map-wrap canvas{width:100%;height:auto;min-width:660px;display:block;cursor:crosshair}.sys-mat-row{display:flex;gap:10px;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--line)}.sys-mat-row span{color:var(--muted);font-size:13px}.sys-mat-row button{margin-left:auto}@media(max-width:720px){.sys-flow{flex-direction:column}.sys-flow div{width:100%}.sys-flow span{transform:rotate(90deg)}}
</style>\n</head>''')
# fix duplicate CSS closure? replacement matches last </style> preceding </head> yes
# inject JSON after transformations
html=re.sub(r'<script type="application/json" id="data">.*?</script>',lambda m:'<script type="application/json" id="data">'+json.dumps(D,ensure_ascii=False,separators=(',',':'))+'</script>',html,flags=re.S)
# script before closing body; inline self-contained script for map and data, can use tab showTab global for link
script=r'''<script>
(() => {
'use strict';
const d=JSON.parse(document.getElementById('data').textContent),S=d.storage_system;
const $=s=>document.querySelector(s);
const row=(label,x,y,z,extra='')=>`<div class="sys-mat-row"><b>${label}</b><span>X ${x}, Y ${y}, Z ${z}${extra?' · '+extra:''}</span></div>`;
$('#sysBulk').innerHTML=S.bulk.map(b=>row(b.label,b.x,b.y,b.z,b.id)).join('');
$('#sysRegular').innerHTML=S.regular.map(b=>row(b.label,b.x,b.y,b.z)).join('');
$('#sysStalls').innerHTML=S.stalls.map(v=>row(v.id+' · '+v.profession,v.x,v.y,v.z,v.workstation)).join('');
const c=$('#sysMap'),ctx=c.getContext('2d'),info=$('#sysInfo'),markers=[];
const ext={x0:-724,x1:-669,z0:765,z1:815},dx=(c.width-100)/(ext.x1-ext.x0+1),dz=(c.height-80)/(ext.z1-ext.z0+1),scale=Math.min(dx,dz);
const px=x=>70+(x-ext.x0)*scale,pz=z=>40+(z-ext.z0)*scale;
function rect(x0,z0,x1,z1,color,label){ctx.fillStyle=color;ctx.fillRect(px(x0),pz(z0),(x1-x0+1)*scale,(z1-z0+1)*scale);if(label){ctx.fillStyle='#fff';ctx.font='13px system-ui';ctx.fillText(label,px(x0)+6,pz(z0)+16)}}
function pin(x,y,z,title,color='#f4c76d'){
 const X=px(x)+scale/2,Z=pz(z)+scale/2;ctx.beginPath();ctx.arc(X,Z,5.5,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();ctx.strokeStyle='#14231c';ctx.lineWidth=1.5;ctx.stroke();markers.push({X,Z,x,y,z,title});
}
function render(){const level=+$('#sysLevel').value;markers.length=0;ctx.clearRect(0,0,c.width,c.height);ctx.fillStyle='#13231d';ctx.fillRect(0,0,c.width,c.height);
 ctx.strokeStyle='#27372f';ctx.lineWidth=.7;for(let x=ext.x0;x<=ext.x1;x+=5){ctx.beginPath();ctx.moveTo(px(x),pz(ext.z0));ctx.lineTo(px(x),pz(ext.z1+1));ctx.stroke();}for(let z=ext.z0;z<=ext.z1;z+=5){ctx.beginPath();ctx.moveTo(px(ext.x0),pz(z));ctx.lineTo(px(ext.x1+1),pz(z));ctx.stroke();}
 ctx.fillStyle='#ccd8ca';ctx.font='13px system-ui';ctx.fillText('X → Osten',68,22);ctx.fillText('Z → Süden',730,22);
 rect(-721,767,-671,786,'#253a30','Nordräume');rect(-721,788,-671,792,'#4d4832','Mittelgang');rect(-721,794,-671,813,'#263a35','Südräume');
 if(level===121){rect(-706,767,-675,784,'#514c35','Bulklager');rect(-694,795,-671,812,'#214f46','Golems');pin(S.input.x,S.input.y,S.input.z,'Einziger Einwurf','#ffcc55');for(const b of S.bulk)pin(b.x,b.y,b.z,'Bulk: '+b.label,'#ffb366');for(const r of S.regular)pin(r.x,r.y,r.z,'Golem: '+r.label,'#65c9b5');pin(-675,123,797,'Kupfertruhe','#55a9ff')}
 if(level===113){rect(-682,768,-672,784,'#514c35','Zusatzlager');for(const x of [-680,-677,-674])pin(x,115,775,'Überlauf- und Shulkerlager','#e1b86c')}
 if(level===105){rect(-706,767,-684,786,'#514c35','Trading Hall');rect(-694,794,-684,813,'#3e304f','Geheimlounge');for(const v of S.stalls)pin(v.x,v.y,v.z,v.id+' · '+v.profession,'#65c9b5');for(const s of S.secrets)pin(s.x,s.y,s.z,s.name,'#d98ef1')}
}
function pick(e){const b=c.getBoundingClientRect(),mx=(e.clientX-b.left)*c.width/b.width,mz=(e.clientY-b.top)*c.height/b.height;let closest=null,dist=1e12;for(const p of markers){const dd=(p.X-mx)**2+(p.Z-mz)**2;if(dd<dist){dist=dd;closest=p}}if(closest&&dist<230){info.textContent=`${closest.title} · X=${closest.x}, Y=${closest.y}, Z=${closest.z}`;return}const x=Math.floor((mx-70)/scale+ext.x0),z=Math.floor((mz-40)/scale+ext.z0);info.textContent=`X=${x}, Z=${z} · Kellerboden Y=${$('#sysLevel').value}`;}
c.addEventListener('mousemove',pick);c.addEventListener('click',pick);$('#sysLevel').addEventListener('change',render);
$('#sysGotoInput').onclick=()=>{document.querySelector('#tabs button[data-tab="plan"]').click();const mode=$('#planMode');mode.value='y';mode.dispatchEvent(new Event('change'));$('#planRange').value=124;$('#planRange').dispatchEvent(new Event('input'))};
$('#sysGotoTrade').onclick=()=>{document.querySelector('#tabs button[data-tab="plan"]').click();const mode=$('#planMode');mode.value='y';mode.dispatchEvent(new Event('change'));$('#planRange').value=106;$('#planRange').dispatchEvent(new Event('input'))};
render();
})();
</script>'''
html=html.replace('</body>',script+'\n</body>')
(OUT/'index.html').write_text(html,encoding='utf-8')
readme=f'''# Blackthorn Estate Revision 5.6 – Keller und Lagersystem

Grundlage: Revision 5.5. Hauptgebäude/Dach wurden nicht erneut verändert.

## Lagerkonzept
Öffentliche Einwurftruhe: X=-708 Y=124 Z=789. Eine Hopperleitung geht zu 6 Bulkfiltern (Bruchstein, Erde, Eisen, Tiefenschiefer, Stein, Kies), danach in eine einzelne Kupfertruhe. In der abgetrennten Kupfergolem-Halle stehen 9 Zielkategorien. Der Keller enthält nun konkrete geplante Container, Leitungen, Filterbauteile und Arbeitsräume.

## Trading Hall / Geheimräume
Keller 3 enthält 10 Arbeitsplatz-Stände in zwei Reihen, neu zusammengefasst aus zwei früheren Räumen. Dazu kommen eine verborgene Bibliothekslounge, ein Tresor-Geheimzugang und zusätzliche Durchgänge.

## Wichtige Einschränkungen
- Hopperinventare (Filteritems, Zieltruhen-Seed-Items) sind **nicht im Blueprint enthalten** und müssen in Minecraft konfiguriert werden.
- Hopper/Redstone-Schaltung ist ein konkreter räumlicher Entwurf, aber nicht in einer Minecraft-Testwelt validiert. Nicht als garantiert funktionierendes Automatiksystem behandeln.
- Kupfergolems und Villager sind Entities, nicht einzelne Blöcke; die 3D-Vorschau zeigt ihre geplanten Standorte als Koordinaten im neuen Reiter, sie müssen im Spiel erzeugt werden.
- Ein öffentlich zugänglicher Einwurf, mehrere versteckte Maschinen- und Zielcontainer.
- Alte blocknummernbasierte Fortschrittsdateien sind aufgrund der Änderungen nicht direkt kompatibel.

Gesamt: {len(compact):,} eindeutige Blockpositionen.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
with (OUT/'check_report.json').open('w',encoding='utf-8') as f:
 json.dump({'version':D['meta']['version'],'blocks':len(compact),'unique':len(blocks),'bulk_filters':len(bulk),'golem_categories':len(regular),'trading_stalls':len(stalls),'input':D['storage_system']['input'],'not_tested_in_game':True},f,indent=2,ensure_ascii=False)

zpath=Path('/mnt/data/Blackthorn-Estate-Revision-5.6.zip')
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,str(p.relative_to(OUT.parent)))
print('CREATED',zpath,'BLOCKS',len(compact),'CHANGE',len(set(blocks)-set(original)),'GROUPS',len(G),'BYTES',zpath.stat().st_size)
