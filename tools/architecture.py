"""Revision 5.25: repair blocked door connections found by the house audit."""

def enhance(d,b):
    previous=d['structure']['enhancements'];air=set(map(tuple,d.get('required_air',[])));repairs=[]
    def put(p,block,state='',group='anschluss_korrekturen'):b[p]=(block,state,group);air.discard(p)
    def clear(p):b.pop(p,None);air.add(p)
    # Open the extra wall layer behind each existing K1 entrance, keeping its door.
    for x,z in ((-703,786),(-691,786),(-679,786),(-681,787),(-680,787)):
        for y in (122,123,124):
            if b.get((x,y,z),('',))[0] in ('stone_bricks','deepslate_bricks','polished_deepslate'):clear((x,y,z))
        repairs.append({'kind':'K1 wall opening','position':[x,122,z]})
    # The south door was two blocks outside the real wall and had no modeled sill.
    for x,hinge in ((-706,'right'),(-705,'left')):
        for y in (130,131,132):
            clear((x,y,830));clear((x,y,831))
        for y,half in ((130,'lower'),(131,'upper')):
            put((x,y,829),'dark_oak_door',f'facing=south,half={half},hinge={hinge},open=false,powered=false')
        put((x,132,829),'stone_bricks')
        for z in (830,831):put((x,129,z),'stone_bricks')
    repairs.append({'kind':'South garden door moved into exterior wall, bridge added','position':[-706,130,829]})
    # The principal western entrance had its double-door hinges at the center.
    for z,hinge in ((790,'left'),(791,'right')):
        for y,half in ((130,'lower'),(131,'upper')):
            prior=b[-734,y,z];put((-734,y,z),prior[0],f'facing=east,half={half},hinge={hinge},open=false,powered=false',prior[2])
    repairs.append({'kind':'West main entrance outer hinges','position':[-734,130,790]})
    d['_clearance_air']=[list(p) for p in sorted(air)]
    feature={'group':'anschluss_korrekturen','name':'Geprüfte Türanschlüsse','description':'Fünf K1-Zugänge durch die zweite Wandlage geöffnet. Gartentür sitzt in der echten Außenwand und hat einen durchgehenden Boden zur Freitreppe. Hauptportal mit äußeren Türanschlägen.'}
    return {**previous,'title':'Hausanschlüsse und Materialprüfung','features':[feature]+previous['features'],'connection_repairs':repairs,
            'limits':'Gesamtmengen sind Zielmengen inklusive Gelände und keine Einkaufsliste zusätzlich zu den Erdarbeitslisten. Die unabhängige Prüfung und Grenzen stehen in materialpruefung.md. '+previous['limits']}
