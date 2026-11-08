"""Shared semantic navigation and external, file-compatible atlas data."""
import json
import re

AREAS={
    'start':('Start',['overview']),
    'atlas':('Bauatlas',['3d','structure','plan','steps','rooms','lighting','viewer']),
    'terrain':('Gelände',['terrain']),
    'storage':('Lager',['storage','system']),
    'organize':('Organisation',['live','build','material','shared','downloads']),
}
LABELS={'live':'Live-Baufortschritt','shared':'Gemeinsame Materialliste','overview':'Start','3d':'3D-Modell','structure':'Hausstruktur','plan':'Ebenenplan','steps':'Blockliste','rooms':'Räume','lighting':'Leuchten','viewer':'Minecraft-Texturen','terrain':'Karte und Erdarbeiten','storage':'Lagerbestände','system':'Sortierung und Technik','build':'Baufortschritt','material':'Materialbedarf','downloads':'Dateien und Berichte'}

def group_panels(source):
    groups=[]
    for area,(label,ids) in AREAS.items():
        panels=[]
        for id in ids:
            match=re.search(r'<section class="tab[^\"]*" id="tab-'+id+r'">.*?</section>',source,re.S)
            if not match:raise ValueError('Missing panel: '+id)
            panel=match.group(0)
            role='region' if area=='start' else 'tabpanel'
            labelled='btn-area-start' if area=='start' else 'btn-view-'+id
            attrs=f'role="{role}" aria-labelledby="{labelled}" tabindex="0"'+(' hidden' if id!='overview' else '')
            panel=panel.replace(f'id="tab-{id}"',f'id="tab-{id}" {attrs}',1)
            first=re.search(r'<h([2-6])\b',panel)
            if not first or first[1]!='2':
                panel=panel.replace('>',f'><h2 class="visually-hidden">{LABELS[id]}</h2>',1)
            # A heading can return to a parent level, but must not skip a level downward.
            level=1
            def heading(m):
                nonlocal level
                n=min(int(m[1]),level+1);level=n
                return f'<h{n}{m[2]}>{m[3]}</h{n}>'
            panel=re.sub(r'<h([2-6])([^>]*)>(.*?)</h[2-6]>',heading,panel,flags=re.S)
            panels.append(panel)
        hidden='' if area=='start' else ' hidden'
        groups.append(f'<section id="area-{area}" class="tab-group" role="tabpanel" aria-labelledby="btn-area-{area}"{hidden}>'+''.join(panels)+'</section>')
    return '\n'.join(groups)

def externalize(root,data,payloads):
    from live_plan import generate
    generate(root,data)
    shared_plan={'meta':{'version':data['meta']['version'],'fingerprint':data['meta']['fingerprint']},'material_scopes':data['material_scopes']}
    (root/'shared-plan.json').write_text(json.dumps(shared_plan,ensure_ascii=False,separators=(',',':'))+'\n')
    (root/'blueprint-data.js').write_text('window.BLACKTHORN_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
    (root/'model-data.js').write_text('window.BLACKTHORN_MODELS='+json.dumps(payloads,separators=(',',':'))+';\n')
    for name in ('progress','app','steps','terrain','system','ui','minecraft_viewer'):
        p=root/(name+'.js');s=p.read_text()
        s=s.replace("JSON.parse(document.getElementById('data').textContent)",'window.BLACKTHORN_DATA')
        s=s.replace("JSON.parse($('#data').textContent)",'window.BLACKTHORN_DATA')
        p.write_text(s)
