"""Generate an orthographic west elevation from the actual block positions."""
from html import escape

def build(d,root):
    cells={}
    for y,z,x,n,r in d['runs']:
        if not(126<=y<=173 and 760<=z<=811):continue
        for xx in range(x,x+n):
            if -746<=xx<=-715 and ((y,z) not in cells or xx<cells[y,z][0]):cells[y,z]=(xx,*d['reg'][r][:2])
    colors={'smooth_basalt':'#55575d','stone_bricks':'#a6a59e','chiseled_stone_bricks':'#b8b6a7','gold_block':'#d8b34c','waxed_cut_copper':'#be8058','waxed_oxidized_cut_copper':'#4d9687','gray_stained_glass':'#8399a2'}
    def color(b):
        if b in colors:return colors[b]
        if 'blackstone' in b:return '#373a41'
        if 'deepslate' in b:return '#555962'
        if 'glass' in b:return '#a4c1c8'
        if 'copper' in b:return '#a77c5c'
        if any(s in b for s in ('wood','planks','door','spruce','oak')):return '#71573e'
        if b=='sea_lantern':return '#e2f0cc'
        return '#999991'
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 1070" role="img" aria-labelledby="title desc"><title id="title">Westansicht · Revision 5.19</title><desc id="desc">Orthografische Blockansicht von Portal und Aussichtsturm. Aus den tatsächlichen Modellpositionen berechnet, ohne Gelände.</desc><rect width="1100" height="1070" fill="#e5e9e2"/><text x="30" y="35" font-family="sans-serif" font-size="22" fill="#25392f">BLACKTHORN ESTATE · WESTANSICHT 5.19</text>']
    for (y,z),(x,b,state) in sorted(cells.items()):
        sx=42+(z-760)*19;sy=65+(173-y)*19
        svg.append(f'<rect x="{sx}" y="{sy}" width="19" height="19" fill="{color(b)}" stroke="#25392f" stroke-opacity=".15" stroke-width=".5"><title>{escape(b)} · X {x} / Y {y} / Z {z}</title></rect>')
    for y in (129,137,157,163,171):
        sy=65+(173-y)*19
        svg.append(f'<text x="1038" y="{sy+14}" font-family="sans-serif" font-size="14" fill="#25392f">Y {y}</text>')
    svg.append('<text x="30" y="1045" font-family="sans-serif" font-size="15" fill="#25392f">Berechnet aus dem Blockmodell · westlicher Gebäudeteil · ohne Gelände und Lichtsimulation</text></svg>')
    (root/'assets/westansicht_5.19.svg').write_text(''.join(svg))
