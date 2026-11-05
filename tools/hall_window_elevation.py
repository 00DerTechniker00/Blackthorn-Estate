"""Before/after diagram from actual west-gable block positions."""
from html import escape

def cells(d):
    out={}
    for y,z,x,n,r in d['runs']:
        if 146<=y<=156 and 785<=z<=795:
            for xx in (-715,-714):
                if x<=xx<x+n:out[xx,y,z]=d['reg'][r][:2]
    return out

def build(before,after,root):
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 470" role="img" aria-labelledby="title desc"><title id="title">Hallenfenster · vorher und Revision 5.24</title><desc id="desc">Schematische Frontalansicht aus den tatsächlichen Blöcken im Westgiebel. Gleiche Gestaltung am Ostgiebel.</desc><rect width="760" height="470" fill="#e7ebe5"/><g font-family="sans-serif" fill="#263d33"><text x="28" y="32" font-size="21">OBERE HALLENFENSTER · REVISION 5.24</text>']
    for left,label,data in ((35,'VORHER · 5.23',cells(before)),(405,'NEU · 5.24',cells(after))):
        svg.append(f'<text x="{left}" y="70" font-size="15">{label}</text>')
        for y in range(146,157):
            for z in range(785,796):
                entry=data.get((-715,y,z)) or data.get((-714,y,z))
                if not entry:continue
                bid,state=entry;x=left+(z-785)*28;sy=92+(156-y)*28
                color='#c3dce1' if 'glass' in bid else '#555a60' if 'deepslate' in bid or 'blackstone' in bid else '#aaa99f'
                if bid=='iron_bars':
                    svg.append(f'<rect x="{x+11}" y="{sy}" width="6" height="28" fill="#50565b"/>');continue
                if bid.endswith('_wall'):
                    svg.append(f'<rect x="{x+7}" y="{sy}" width="14" height="28" fill="{color}"/>');continue
                if bid.endswith('_slab'):
                    svg.append(f'<rect x="{x}" y="{sy}" width="28" height="14" fill="{color}"/>');continue
                if bid.endswith('_stairs'):
                    top='half=top' in state;right='facing=south' in state
                    svg.append(f'<rect x="{x}" y="{sy if top else sy+14}" width="28" height="14" fill="{color}"/>')
                    svg.append(f'<rect x="{x+14 if right else x}" y="{sy+14 if top else sy}" width="14" height="14" fill="{color}"/>');continue
                svg.append(f'<rect x="{x}" y="{sy}" width="28" height="28" fill="{color}" stroke="#35463c" stroke-opacity=".2" stroke-width=".7"><title>{escape(bid)} · Y {y} / Z {z}</title></rect>')
                if 'glass' in bid:svg.append(f'<path d="M{x+6} {sy+21}l15 -15" stroke="#f4faf7" opacity=".7"/>')
                if bid=='chiseled_stone_bricks':svg.append(f'<rect x="{x+6}" y="{sy+6}" width="16" height="16" fill="none" stroke="#667068"/>')
    svg.append('<text x="28" y="445" font-size="13">West- und Ostgiebel · zurückgesetztes Glas, Metallsprossen und gestufter Steinbogen</text></g></svg>')
    (root/'assets/hallenfenster_5.24.svg').write_text(''.join(svg))
