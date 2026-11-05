"""Independent coordinate/material audit over the generated CSV and original terrain."""
import csv,json,re
from collections import Counter
from pathlib import Path
from world_snapshot import Snapshot

FOCUS=('dirt','cobblestone','grass_block','stone')

def audit(d,root):
    root=Path(root);positions={};counts=Counter();duplicates=[]
    for y,z,x,n,r in d['runs']:
        block,state,g=d['reg'][r]
        for xx in range(x,x+n):
            p=(xx,y,z)
            if p in positions:duplicates.append(p)
            positions[p]=(block,state,d['groups'][g])
            # Separate implementation from the builder's conversion helper.
            if block in ('water','bubble_column','piston_head') or block.endswith('_door') and 'half=upper' in state or block.endswith('_bed') and 'part=head' in state:continue
            if block.startswith('potted_'):counts.update(['flower_pot',block[7:]])
            else:
                aliases={'water_cauldron':'cauldron','redstone_wall_torch':'redstone_torch','wall_torch':'torch','soul_wall_torch':'soul_torch'}
                item=aliases.get(block,block.replace('_wall_banner','_banner').replace('_wall_hanging_sign','_hanging_sign').replace('_wall_sign','_sign'))
                counts[item]+=2 if block.endswith('_slab') and 'type=double' in state else 1
    csv_counts={row['Material']:int(row['Anzahl']) for row in csv.DictReader((root/'materialbedarf.csv').open(encoding='utf-8-sig'),delimiter=';')}
    errors=[]
    if duplicates:errors.append('Duplicate positions')
    if dict(counts)!=d['counts'] or dict(counts)!=csv_counts:errors.append('Material count mismatch')
    air=set(map(tuple,d['required_air']))
    if air.intersection(positions):errors.append('Required air overlaps blocks')
    packed=[]
    for row in csv.DictReader((root/'materialbedarf.csv').open(encoding='utf-8-sig'),delimiter=';'):
        n=int(row['Anzahl']);stack=int(row['Stackgroesse']);sh=int(row['volle_Shulkers']);rest=int(row['Rest_nach_Shulkern'])
        if sh*27*stack+rest!=n or rest>=27*stack:packed.append(row['Material'])
    if packed:errors.append('Invalid shulker remainder')
    region=root/'source-data/world-regions/from-mca-import/r.-2.1.mca'
    snapshot=Snapshot(region) if region.exists() else None
    snapshot_info={'available':bool(snapshot),'note':'Originaler mitgelieferter Snapshot, kein aktueller Serverstand. Gleicher Blocktyp bedeutet nicht zwingend gleicher Blockstate.'}
    same=Counter();unknown=Counter()
    if snapshot:
        snapshot_info.update(file=str(region.relative_to(root)),sha256=snapshot.sha256)
        for (x,y,z),(block,state,g) in positions.items():
            if block not in FOCUS:continue
            try:original=snapshot.block(x,y,z)
            except ValueError:unknown[block]+=1;continue
            if original==block:same[block]+=1
    snapshot_info['materials']={block:{'planned':counts[block],'same_type_in_snapshot':same[block] if snapshot else None,'different_type':counts[block]-same[block]-unknown[block] if snapshot else None,'unknown_positions':unknown[block] if snapshot else counts[block]} for block in FOCUS}
    cut={}
    for x,z,low,high in d['terrain']['cut_spans']:cut.setdefault((x,z),[]).append((low,high))
    def effective(p):
        if p in positions:return positions[p][0]
        x,y,z=p
        if p in air or any(a<=y<=b for a,b in cut.get((x,z),[])):return 'air'
        if snapshot:
            try:return snapshot.block(x,y,z)
            except ValueError:pass
        return 'unknown'
    def passable(block):return block in ('air','cave_air','void_air','water','bubble_column','ladder') or block.endswith(('_carpet','_door','_banner'))
    blocked=[];bad_pairs=[];unsupported=[];door_count=0
    for (x,y,z),(block,state,g) in positions.items():
        if not block.endswith('_door') or 'half=lower' not in state:continue
        door_count+=1;upper=positions.get((x,y+1,z))
        if not upper or upper[0]!=block:bad_pairs.append([x,y,z])
        props=dict(p.split('=') for p in state.split(',') if '=' in p)
        dx,dz=(1,0) if props['facing'] in ('east','west') else (0,1)
        for sign in (-1,1):
            for yy in (y,y+1):
                p=(x+sign*dx,yy,z+sign*dz);material=effective(p)
                if material!='unknown' and not passable(material):blocked.append({'door':[x,y,z],'obstacle':list(p),'block':material})
        if effective((x,y-1,z)) in ('air','cave_air','void_air','water'):unsupported.append([x,y,z])
    gravity=[];unchecked_gravity=[]
    for (x,y,z),(block,state,g) in positions.items():
        if block not in ('anvil','sand','red_sand','gravel'):continue
        below=effective((x,y-1,z))
        if below in ('air','cave_air','void_air','water'):gravity.append([x,y,z])
        if below=='unknown':unchecked_gravity.append([x,y,z])
    if blocked or bad_pairs or unsupported or gravity:errors.append('Position audit has unresolved findings')
    report={'revision':d['meta']['version'],'positions':len(positions),'items':sum(counts.values()),'duplicates':duplicates,'material_counts_match':dict(counts)==d['counts']==csv_counts,'packing_errors':packed,'doors_checked':door_count,'door_obstacles':blocked,'unpaired_doors':bad_pairs,'unsupported_doors':unsupported,'unsupported_gravity_blocks':gravity,'gravity_not_checked_against_snapshot':unchecked_gravity,'snapshot':snapshot_info,'scopes':{key:{'label':v['label'],'items':sum(v['counts'].values()),'focus':{block:v['counts'].get(block,0) for block in FOCUS}} for key,v in d['material_scopes'].items()},'errors':errors,'limits':'Statische Blockprüfung, kein vollständiger Ingame-Lauftest. Redstone, Wasser und Spawn-Sicherheit nicht simuliert. Neue Füllung und Grabungslisten nicht als bereits erledigt voraussetzen.'}
    (root/'materialpruefung.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    with (root/'materialbedarf_bestandsvergleich.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Material','Planpositionen','Gleicher_Blocktyp_im_alten_Snapshot','Anderer_Blocktyp','Nicht_geprueft'])
        for block,v in snapshot_info['materials'].items():w.writerow([block,v['planned'],v['same_type_in_snapshot'],v['different_type'],v['unknown_positions']])
    rows='\n'.join(f"| {v['label']} | {v['items']:,} | {v['focus']['dirt']:,} | {v['focus']['cobblestone']:,} |" for v in report['scopes'].values())
    text=f"""# Block- und Materialprüfung · {d['meta']['version']}

## Positionen

{len(positions):,} eindeutige Baupositionen. {door_count} Türen auf Gegenhälfte, direkte Durchgänge und Boden geprüft. Befunde: {len(blocked)} blockierte Nachbarzellen, {len(bad_pairs)} fehlende Türhälften, {len(unsupported)} Türen ohne Boden, {len(gravity)} eindeutig frei hängende Schwerkraftblöcke. {len(unchecked_gravity)} Schwerkraftpositionen benötigen den lokalen Snapshot für eine vollständige Prüfung.

Korrigiert: zweite Wandlagen vor fünf K1-Türen geöffnet; die Südgartentür in die tatsächliche Außenwand bei Z 829 versetzt und mit der Freitreppe verbunden. Störenden Fassadenschmuck im Durchgang entfernt. Anschläge des westlichen Hauptportals nach außen gesetzt. Im übrigen Haus bleiben die bestehenden Architekturentscheidungen bestehen.

## Mengen nach Bereich

| Bereich | Items | Erde | Bruchstein |
| --- | ---: | ---: | ---: |
{rows}

Die Gesamtmaterialliste enthält den vollständigen Zielplan einschließlich Gelände. Die Standardansicht im Atlas zeigt jetzt Haus und Keller; Außenanlagen und Gelände sind separat auswählbar. materialbedarf.csv bleibt die vollständige Gesamtplanung. Die zwei originalen Lager-Litematics und die Einrichtung mit Büchern/Rüstungen sind zusätzliche separate Listen.

Alle Erdblöcke im Blockmodell gehören zur Terraforming-Auffüllung. Die große Masse ist für das angehobene Plateau und dessen Bodendecke vorgesehen. 13.272 Bruchsteinblöcke liegen ebenfalls in dieser Auffüllung; die übrigen 817 in Wegen und Nebengebäuden. Diese Füllung wird nicht aus Kostengründen automatisch entfernt, weil sonst ihre Trag- und Geländeform geändert würde.

## Nachzählung und Packen

Die Itemmengen wurden unabhängig aus den Blockpositionen nachgerechnet und mit JSON und CSV verglichen. Türen und Betten zählen einmal; Flüssigkeiten und Kolbenköpfe sind keine zusätzlichen Items. Töpfe und Pflanzen werden getrennt, Wandbanner als Banner gezählt. Doppelte Platten würden zwei Items kosten; im aktuellen Modell sind keine vorhanden.

Behoben: Rest_nach_Shulkern enthielt bisher nur lose Einzelitems und unterschlug die verbleibenden ganzen Stacks. Jetzt gilt: Anzahl = volle_Shulkers × 27 × Stackgröße + Rest_nach_Shulkern. Banner werden mit 16 pro Stack gepackt. Die Blockzahlen werden dadurch nicht künstlich reduziert.

## Bestand und Wiederverwendung

Snapshot verfügbar: {bool(snapshot)}. Die Vergleichsdatei zeigt nur, wo im alten gelieferten Weltstand derselbe Blocktyp steht. Daraus folgt keine Aussage über den heutigen Serverfortschritt. Die Erdmengen unterscheiden sich außerdem von der alten Auffüllungsliste, weil spätere Begrünungs- und Böschungsumbauten hinzukamen. Die ältere Auffüllungsliste ist kein zusätzlicher Materialauftrag und darf nicht zur Gesamtmaterialliste addiert werden.

Der historische Aushubplan nennt 34.081 Stein, 10.126 Erde und 5.097 Grasblöcke. Abgebauter Stein kann bei normalem Werkzeug Bruchstein liefern ([Mojang: Stein](https://www.minecraft.net/en-us/article/block-week-stone)); Gras kann Erde liefern. Das sind mögliche Wiederverwendungen, keine bereits geprüften aktuellen Lagerbestände oder garantiert zusätzlichen Erträge. Silktouch, Baufortschritt und spätere Änderungen beeinflussen die Bilanz.

{report['limits']}
"""
    text=re.sub(r'\d{1,3}(?:,\d{3})+',lambda m:m.group().replace(',','.'),text)
    (root/'materialpruefung.md').write_text(text)
    if errors:raise ValueError('; '.join(errors))
    return report
