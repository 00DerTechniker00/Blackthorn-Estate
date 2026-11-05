"""Revision 5.23: lebendigere Nord- und Südfassade.

Fensterbänke, Stürze, offene Fensterläden, Zahnschnitt-Gesims, Efeu und verwitterte Mauersteine.
Alle neuen Blöcke werden nur auf freie Positionen gesetzt; bestehende Fenster, Pfeiler und Freiräume bleiben unberührt.
Einzige Ersetzungen: einzelne Mauersteine der Nord- und Südwand (stone_bricks -> mossy/cracked).
"""
import hashlib

WINDOWS=((-705,-704),(-699,-698),(-687,-686),(-681,-680),(-669,-668),(-663,-662))
FLOORS=((131,134),(139,142))        # Fensterhöhen Erdgeschoss / Obergeschoss
FACADES=((751,-1,'north'),(829,1,'south'))   # Wandebene, Richtung nach außen, Blickrichtung
WALL_X=(-714,-656)
WEATHER_Y=(130,143)
GROUPS=('fassade_fenster','fassade_laeden','fassade_zahnschnitt','fassade_efeu','fassade_alterung')

def noise(x,y,z,salt):
    return int(hashlib.md5(f'{salt}:{x},{y},{z}'.encode()).hexdigest()[:8],16)/0xffffffff

def enhance(d,b):
    previous=d['structure']['enhancements'];air=set(map(tuple,d.get('required_air',[])))
    glass_before={p for p,v in b.items() if v[0]=='glass_pane'}
    stats={g:0 for g in GROUPS};stats['moss']=0;stats['cracked']=0
    def put(x,y,z,block,state,group):
        p=(x,y,z)
        if p in b or p in air:return False
        b[p]=(block,state,group);stats[group]+=1;return True
    window_cols={x for x0,x1 in WINDOWS for x in range(x0-1,x1+2)}
    for wall_z,out,facing in FACADES:
        oz=wall_z+out
        for x0,x1 in WINDOWS:
            for lo,hi in FLOORS:
                for x in range(x0,x1+1):
                    put(x,lo-1,oz,'stone_brick_slab','type=top,waterlogged=false','fassade_fenster')
                for x in range(x0-1,x1+2):
                    put(x,hi+1,oz,'stone_brick_stairs',f'facing={facing},half=top,shape=straight,waterlogged=false','fassade_fenster')
                wood='dark_oak_trapdoor' if lo<135 else 'spruce_trapdoor'
                for x in (x0-1,x1+1):
                    for y in range(lo,hi+1):
                        put(x,y,oz,wood,f'facing={facing},half=bottom,open=true,powered=false,waterlogged=false','fassade_laeden')
        # Zahnschnitt: umgekehrte Treppen im Zwei-Block-Takt unter dem Gesims.
        for x in range(WALL_X[0],WALL_X[1]+1):
            if x%2==0 and x not in window_cols:
                put(x,143,oz,'stone_brick_stairs',f'facing={facing},half=top,shape=straight,waterlogged=false','fassade_zahnschnitt')
        # Efeu: unregelmäßige Bahnen an fensterfreien Wandstreifen.
        vine_side='south' if out<0 else 'north'
        ivy_cols=[]
        for x in range(WALL_X[0],WALL_X[1]+1):
            if x in window_cols or (x,136,oz) in b:continue
            if noise(x,0,wall_z,'ivy')<0.40:
                length=4+int(noise(x,1,wall_z,'len')*8)
                state=','.join(f'{s}={"true" if s==vine_side else "false"}' for s in ('east','north','south','up','west'))
                placed=False
                for y in range(142,142-length,-1):
                    wall=b.get((x,y,wall_z),('',))[0]
                    if wall in ('','glass_pane'):break
                    placed|=put(x,y,oz,'vine',state,'fassade_efeu')
                if placed:ivy_cols.append(x)
        # Verwitterung: Moos am Sockel und um Efeubahnen, vereinzelt rissige Steine.
        for x in range(WALL_X[0],WALL_X[1]+1):
            for y in range(WEATHER_Y[0],WEATHER_Y[1]+1):
                block=b.get((x,y,wall_z))
                if not block or block[0]!='stone_bricks':continue
                r=noise(x,y,wall_z,'weather')
                moss=0.10 if y<=134 else 0.03
                if any(abs(x-c)<=1 for c in ivy_cols):moss+=0.15
                if r<moss:b[(x,y,wall_z)]=('mossy_stone_bricks',block[1],'fassade_alterung');stats['moss']+=1;stats['fassade_alterung']+=1
                elif r>0.955:b[(x,y,wall_z)]=('cracked_stone_bricks',block[1],'fassade_alterung');stats['cracked']+=1;stats['fassade_alterung']+=1
    # Prüfung: kein Fenster geht verloren, nichts steht auf Freiraum-Positionen.
    glass_after={p for p,v in b.items() if v[0]=='glass_pane'}
    if glass_before-glass_after:raise ValueError('Fassadenschmuck hat Fenster entfernt')
    if any(p in air for p,v in b.items() if v[2] in GROUPS):raise ValueError('Fassadenschmuck liegt auf Freiraum')
    d['_clearance_air']=[list(p) for p in sorted(air)]
    features=[
        {'group':'fassade_laeden','name':'Offene Fensterläden','description':f'{stats["fassade_laeden"]} offene Falltüren rahmen die Fenster: dunkle Eiche im Erdgeschoss, Fichte im Obergeschoss. Die Fensterflächen bleiben frei.'},
        {'group':'fassade_fenster','name':'Sohlbänke und Stürze','description':f'{stats["fassade_fenster"]} Steinziegel-Platten und umgedrehte Treppen betonen jedes Fenster der Nord- und Südfassade mit Bank und Sturz.'},
        {'group':'fassade_zahnschnitt','name':'Zahnschnitt-Gesims','description':f'{stats["fassade_zahnschnitt"]} umgedrehte Treppen im Zwei-Block-Takt unter dem Traufgesims geben den langen Wänden Rhythmus und Schatten.'},
        {'group':'fassade_efeu','name':'Efeu an den Wänden','description':f'{stats["fassade_efeu"]} Rankenblöcke in unregelmäßigen Bahnen an fensterfreien Wandstreifen; auf der Bauseite beliebig verschiebbar.'},
        {'group':'fassade_alterung','name':'Verwitterte Mauersteine','description':f'{stats["moss"]} bemooste und {stats["cracked"]} rissige Steinziegel ersetzen einzelne Mauersteine, vor allem am Sockel und neben dem Efeu.'}]+previous['features']
    return {**previous,'title':'Lebendige Nord- und Südfassade','features':features,'facade_stats':stats,
        'limits':'Fensterläden, Efeu und Verwitterung sind gestalterisch; Position und Dichte lassen sich beim Bauen nach Geschmack anpassen. Alle Fassadenteile stehen auf bislang freien Positionen, nur einzelne Mauersteine werden ersetzt. '+previous['limits']}
