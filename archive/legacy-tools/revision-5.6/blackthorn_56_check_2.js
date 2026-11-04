(() => {
'use strict';
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const D = JSON.parse(document.getElementById('data').textContent);
const fmt = n => Number(n).toLocaleString('de-DE');
const LS = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

/* ---------- Daten dekodieren ---------- */
const N = D.meta.total, BB = D.meta.bbox;
const X = new Int16Array(N), Y = new Int16Array(N), Z = new Int16Array(N), R = new Int16Array(N);
{ let n = 0; for (const r of D.runs) for (let i = 0; i < r[3]; i++) { X[n] = r[2] + i; Y[n] = r[0]; Z[n] = r[1]; R[n] = r[4]; n++; } }
const GX0 = BB[0] - 2, GY0 = BB[2] - 2, GZ0 = BB[4] - 2, NX = BB[1] - BB[0] + 5, NY = BB[3] - BB[2] + 5, NZ = BB[5] - BB[4] + 5;
const grid = new Int32Array(NX * NY * NZ);
const gidx = (x, y, z) => ((x - GX0) * NY + (y - GY0)) * NZ + (z - GZ0);
for (let i = 0; i < N; i++) grid[gidx(X[i], Y[i], Z[i])] = i + 1;
const at = (x, y, z) => (x < GX0 || y < GY0 || z < GZ0 || x >= GX0 + NX || y >= GY0 + NY || z >= GZ0 + NZ) ? -1 : grid[gidx(x, y, z)] - 1;

/* ---------- Namen & Farben ---------- */
const BASE_DE = {
  stone_bricks: 'Steinziegel', cracked_stone_bricks: 'Rissige Steinziegel', mossy_stone_bricks: 'Bemooste Steinziegel',
  deepslate_bricks: 'Tiefenschieferziegel', cracked_deepslate_bricks: 'Rissige Tiefenschieferziegel',
  deepslate_tiles: 'Tiefenschieferfliesen', polished_deepslate: 'Polierter Tiefenschiefer',
  spruce_planks: 'Fichtenholzbretter', dark_oak_planks: 'Schwarzeichenbretter', bookshelf: 'Bücherregal',
  glass: 'Glas', glass_pane: 'Glasscheibe', iron_bars: 'Eisengitter', chain: 'Kette', lantern: 'Laterne',
  soul_lantern: 'Seelenlaterne', lectern: 'Lesepult', barrel: 'Fass', chest: 'Truhe', crafting_table: 'Werkbank',
  furnace: 'Ofen', smoker: 'Räucherofen', blast_furnace: 'Schmelzofen', smithing_table: 'Schmiedetisch',
  cartography_table: 'Kartentisch', fletching_table: 'Pfeilmacher', loom: 'Webstuhl', stonecutter: 'Steinsäge',
  anvil: 'Amboss', grindstone: 'Schleifstein', brewing_stand: 'Braustand', cauldron: 'Kessel',
  enchanting_table: 'Verzauberungstisch', composter: 'Komposter', gold_block: 'Goldblock', iron_block: 'Eisenblock',
  waxed_oxidized_copper: 'Gewachstes oxidiertes Kupfer', water: 'Wasser', water_bucket: 'Wassereimer',
  red_carpet: 'Roter Teppich', gray_carpet: 'Grauer Teppich', black_carpet: 'Schwarzer Teppich',
  red_bed: 'Rotes Bett', blue_bed: 'Blaues Bett', green_bed: 'Grünes Bett', purple_bed: 'Lila Bett',
  orange_bed: 'Oranges Bett', cyan_bed: 'Türkises Bett', dark_oak_fence: 'Schwarzeichenzaun',
  lightning_rod: 'Blitzableiter', dark_oak: 'Schwarzeiche', spruce: 'Fichte', stone_brick: 'Steinziegel',
  deepslate_brick: 'Tiefenschieferziegel', deepslate_tile: 'Tiefenschieferfliesen', torch: 'Fackel'
};
function deName(id) {
  if (BASE_DE[id]) return BASE_DE[id];
  const m = id.match(/^(.*)_(stairs|slab|wall|door)$/);
  if (m) { const b = BASE_DE[m[1]] || BASE_DE[m[1] + 's'] || m[1].replace(/_/g, ' '); const suf = { stairs: 'Treppe', slab: 'Stufe', wall: 'Mauer', door: 'Tür' }[m[2]]; return `${b}-${suf}`; }
  return id.replace(/_/g, ' ');
}
const COLORS = {
  stone_bricks: '#8d8d8a', cracked_stone_bricks: '#82827f', mossy_stone_bricks: '#77876a', deepslate_bricks: '#4b4b52',
  cracked_deepslate_bricks: '#45454c', deepslate_tiles: '#3e3e45', polished_deepslate: '#5a5a62', spruce_planks: '#7d5e36',
  dark_oak_planks: '#4a331e', bookshelf: '#8b6a3a', glass: '#cfeaf5', glass_pane: '#bfe3f2', iron_bars: '#8e9298',
  chain: '#3a3c42', lantern: '#f2b84b', soul_lantern: '#52d0e6', lectern: '#8a6a3b', barrel: '#7a5a30', chest: '#a8742a',
  crafting_table: '#8a6234', furnace: '#707070', smoker: '#76706a', blast_furnace: '#5a5a5e', smithing_table: '#3a3a48',
  cartography_table: '#7a6a50', fletching_table: '#b09a60', loom: '#a2845a', stonecutter: '#8a8a8a', anvil: '#3b3b3e',
  grindstone: '#8a8a8a', brewing_stand: '#8a8a70', cauldron: '#3a3a3a', enchanting_table: '#7a1f3a', composter: '#6a4a28',
  gold_block: '#f2cd3b', iron_block: '#d6d6d6', waxed_oxidized_copper: '#4eb59a', water: '#3a6fd8',
  red_carpet: '#a12722', gray_carpet: '#6b6b6b', black_carpet: '#1c1c1f', red_bed: '#b02e26', blue_bed: '#3c44aa',
  green_bed: '#5e7c16', purple_bed: '#8932b8', orange_bed: '#f9801d', cyan_bed: '#169c9c', dark_oak_fence: '#4a331e',
  lightning_rod: '#c8744a', dark_oak_door: '#4f3720', spruce_door: '#84623a'
};
function colorOf(id) {
  if (COLORS[id]) return COLORS[id];
  const m = id.match(/^(.*)_(stairs|slab|wall)$/);
  if (m) { const b = m[1]; return COLORS[b] || COLORS[b + 's'] || COLORS[b + '_planks'] || '#999999'; }
  return '#ff00ff';
}
const CUSTOM = {
  enchanting_table: [[0, 0, 0, 16, 12, 16]], lectern: [[0, 0, 0, 16, 2, 16], [4, 2, 4, 12, 14, 12], [0, 12, 0, 16, 16, 16]],
  brewing_stand: [[7, 0, 7, 9, 14, 9], [1, 0, 1, 5, 2, 5], [11, 0, 1, 15, 2, 5], [6, 0, 11, 10, 2, 15]],
  cauldron: [[0, 0, 0, 16, 14, 16]], anvil: [[2, 0, 2, 14, 4, 14], [4, 4, 4, 12, 10, 12], [0, 10, 3, 16, 16, 13]],
  grindstone: [[2, 0, 4, 14, 12, 12]], stonecutter: [[0, 0, 0, 16, 9, 16]], chest: [[1, 0, 1, 15, 14, 15]],
  composter: [[0, 0, 0, 16, 14, 16]]
};
function kindOf(id) {
  if (id === 'water') return 'water'; if (id === 'glass') return 'glass';
  if (id.endsWith('_stairs')) return 'stairs'; if (id.endsWith('_slab')) return 'slab'; if (id.endsWith('_door')) return 'door';
  if (id === 'glass_pane' || id === 'iron_bars') return 'pane'; if (id.endsWith('_fence')) return 'fence';
  if (id.endsWith('_wall')) return 'wall'; if (id.endsWith('_carpet')) return 'carpet'; if (id.endsWith('_bed')) return 'bed';
  if (id === 'lantern' || id === 'soul_lantern') return 'lantern'; if (id === 'chain') return 'chain';
  if (id === 'lightning_rod') return 'rod'; if (CUSTOM[id]) return 'custom';
  return 'cube';
}
const REG = D.reg.map(([id, props, g]) => {
  const p = {}; if (props) props.split(',').forEach(kv => { const [k, v] = kv.split('='); p[k] = v; });
  return { id, p, props, gi: g, g: D.groups[g], kind: kindOf(id), color: colorOf(id), rgb: hexRgb(colorOf(id)) };
});
function hexRgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; }

/* ---------- Gruppen / Phasen ---------- */
const GROUP_DE = {
  fundament: 'Fundament & Sockel', terrasse: 'Westterrasse', pool: 'Panorama-Pool', keller_1: 'Keller 1', keller_2: 'Keller 2',
  keller_3: 'Keller 3', keller_treppe: 'Kellertreppenhaus', res1: 'Residenz 1', res2: 'Residenz 2', res3: 'Residenz 3',
  res4: 'Residenz 4', res5: 'Residenz 5', res6: 'Residenz 6', halle: 'Große Halle', galerie: 'Galerie', bibliothek: 'Bibliothek',
  kueche: 'Küche', speisesaal: 'Speisesaal', vestibuel: 'Vestibül', portikus: 'Portikus (Eingang)', dach_res: 'Dächer Residenzen',
  dach_halle: 'Dach Große Halle', dach_bibliothek: 'Dach Bibliothek', dach_ostfluegel: 'Dach Ostflügel',
  observatorium: 'Observatorium', beleuchtung: 'Zusatzbeleuchtung'
};
const PHASES = [
  { id: 'p1', name: '1 · Gelände & Fundament', text: 'Sockelmauern bis Y=128, Bodenplatte Y=129. Zuerst Aushub für die Keller (siehe Prüfbericht).', groups: ['fundament'] },
  { id: 'p2', name: '2 · Keller (3 Ebenen)', text: 'Drei Kellergeschosse (Y=105/113/121) plus Wendeltreppenhaus. Von unten nach oben bauen.', groups: ['keller_3', 'keller_2', 'keller_1', 'keller_treppe'] },
  { id: 'p3', name: '3 · Haupthaus', text: 'Große Halle mit Galerie und Bibliothek – das Zentrum, an dem alle Residenzen hängen.', groups: ['halle', 'galerie', 'bibliothek'] },
  { id: 'p4', name: '4 · Residenzen & Türme', text: 'Sechs Wohnflügel mit je zwei Etagen und Eckturm. Jede Residenz kann von einer eigenen Person gebaut werden.', groups: ['res1', 'res2', 'res3', 'res4', 'res5', 'res6'] },
  { id: 'p5', name: '5 · Ostflügel & Eingang', text: 'Küche, Speisesaal, Vestibül, Portikus mit Treppenstufen.', groups: ['kueche', 'vestibuel', 'speisesaal', 'portikus'] },
  { id: 'p6', name: '6 · Dächer', text: 'Satteldächer aus Treppen/Stufen, Kegeldächer der Türme.', groups: ['dach_halle', 'dach_res', 'dach_bibliothek', 'dach_ostfluegel'] },
  { id: 'p7', name: '7 · Terrasse, Pool, Observatorium', text: 'Außenanlagen und Zierturm auf dem Hallenfirst.', groups: ['terrasse', 'pool', 'observatorium'] },
  { id: 'p8', name: '8 · Zusatzbeleuchtung', text: 'Laternen am Boden entlang der Wände – verhindert Monster-Spawns in Dachböden und Ecken.', groups: ['beleuchtung'] }
];
const gname = g => GROUP_DE[g] || g;

/* ---------- Räume ---------- */
function roomAt(x, y, z) {
  let best = null, bv = 1e12;
  for (const r of D.rooms) {
    if (x >= r.x[0] && x <= r.x[1] && y >= r.y[0] && y <= r.y[1] && z >= r.z[0] && z <= r.z[1]) {
      const v = (r.x[1] - r.x[0] + 1) * (r.y[1] - r.y[0] + 1) * (r.z[1] - r.z[0] + 1);
      if (v < bv) { bv = v; best = r; }
    }
  }
  return best;
}
function describe(i) {
  const r = REG[R[i]]; const rm = roomAt(X[i], Y[i], Z[i]);
  const st = r.props ? ` [${r.props.replace(/,/g, ', ')}]` : '';
  return { title: deName(r.id), id: `minecraft:${r.id}${st}`, pos: `X ${X[i]} · Y ${Y[i]} · Z ${Z[i]}`, group: gname(r.g), room: rm ? rm.name : '—', color: r.color };
}

/* ---------- Theme ---------- */
function applyTheme(t) {
  if (t) document.documentElement.setAttribute('data-theme', t); else document.documentElement.removeAttribute('data-theme');
  if (window.__onTheme) window.__onTheme();
}
{ const t = LS.get('bt-theme', null); if (t) applyTheme(t);
  $('#themeBtn').onclick = () => {
    const cur = document.documentElement.getAttribute('data-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const nx = cur === 'dark' ? 'light' : 'dark'; LS.set('bt-theme', nx); applyTheme(nx);
  }; }

/* ---------- Tabs ---------- */
function showTab(id) {
  $$('.tab').forEach(t => t.classList.toggle('on', t.id === 'tab-' + id));
  $$('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === id));
  if (id === '3d') ensureGL();
  if (id === 'plan') { planFit(); planDraw(); }
  location.hash = id;
  window.scrollTo(0, 0);
}
$$('#tabs button').forEach(b => b.onclick = () => showTab(b.dataset.tab));
window.__showTab = showTab;

/* =====================================================================
   3D
   ===================================================================== */
let GL = null;
const S3 = { ymax: BB[3], single: false, terrain: true, hidden: new Set(), cut: BB[3] };
const SHADE = { up: 1, down: .5, north: .74, south: .92, east: .8, west: .66 };
const FACES = {
  up: b => [[b[0], b[4], b[2]], [b[3], b[4], b[2]], [b[3], b[4], b[5]], [b[0], b[4], b[5]]],
  down: b => [[b[0], b[1], b[2]], [b[3], b[1], b[2]], [b[3], b[1], b[5]], [b[0], b[1], b[5]]],
  north: b => [[b[0], b[1], b[2]], [b[3], b[1], b[2]], [b[3], b[4], b[2]], [b[0], b[4], b[2]]],
  south: b => [[b[0], b[1], b[5]], [b[3], b[1], b[5]], [b[3], b[4], b[5]], [b[0], b[4], b[5]]],
  west: b => [[b[0], b[1], b[2]], [b[0], b[1], b[5]], [b[0], b[4], b[5]], [b[0], b[4], b[2]]],
  east: b => [[b[3], b[1], b[2]], [b[3], b[1], b[5]], [b[3], b[4], b[5]], [b[3], b[4], b[2]]]
};
const mkB = () => ({ p: [], c: [], u: [], i: [], n: 0 });
function addFace(B, dir, box, col, nz) {
  const v = FACES[dir](box), s = SHADE[dir] * nz;
  for (const q of v) { B.p.push(q[0], q[1], -q[2]); B.c.push(col[0] * s, col[1] * s, col[2] * s); }
  B.u.push(0, 0, 1, 0, 1, 1, 0, 1);
  const o = B.n; B.i.push(o, o + 1, o + 2, o, o + 2, o + 3); B.n += 4;
}
function addBox(B, x, y, z, b16, col, nz, skip) {
  const b = [x + b16[0] / 16, y + b16[1] / 16, z + b16[2] / 16, x + b16[3] / 16, y + b16[4] / 16, z + b16[5] / 16];
  for (const d of ['up', 'down', 'north', 'south', 'west', 'east']) { if (skip && skip[d]) continue; addFace(B, d, b, col, nz); }
}
const DIRV = { north: [0, 0, -1], south: [0, 0, 1], east: [1, 0, 0], west: [-1, 0, 0] };

function buildModel(pred) {
  const layers = {};
  const get = y => layers[y] || (layers[y] = { main: mkB(), glass: mkB(), caps: mkB() });
  const vis = (x, y, z) => { const j = at(x, y, z); return j >= 0 && pred(j) ? REG[R[j]] : null; };
  for (let i = 0; i < N; i++) {
    if (!pred(i)) continue;
    const r = REG[R[i]], x = X[i], y = Y[i], z = Z[i];
    const L = get(y), nz = .93 + .09 * hash3(x, y, z), col = r.rgb;
    const k = r.kind;
    if (k === 'cube') {
      const nb = {}; for (const d of ['up', 'down', 'north', 'south', 'east', 'west']) {
        const dv = d === 'up' ? [0, 1, 0] : d === 'down' ? [0, -1, 0] : DIRV[d];
        const n = vis(x + dv[0], y + dv[1], z + dv[2]); nb[d] = n && n.kind === 'cube';
      }
      const box = [x, y, z, x + 1, y + 1, z + 1];
      for (const d of ['down', 'north', 'south', 'west', 'east']) if (!nb[d]) addFace(L.main, d, box, col, nz);
      addFace(nb.up ? L.caps : L.main, 'up', box, col, nz);
    } else if (k === 'glass' || k === 'water') {
      const h = k === 'water' ? .9 : 1, box = [x, y, z, x + 1, y + h, z + 1];
      for (const d of ['up', 'down', 'north', 'south', 'west', 'east']) {
        const dv = d === 'up' ? [0, 1, 0] : d === 'down' ? [0, -1, 0] : DIRV[d];
        const n = vis(x + dv[0], y + dv[1], z + dv[2]);
        if (n && (n.id === r.id || (n.kind === 'cube'))) continue;
        addFace(L.glass, d, box, col, nz);
      }
    } else {
      const boxes = shapeBoxes(r, x, y, z, vis);
      const tgt = (r.id === 'glass_pane') ? L.glass : L.main;
      for (const b of boxes) addBox(tgt, x, y, z, b, col, nz, null);
    }
  }
  return layers;
}
function hash3(x, y, z) { let h = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791); h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h >>> 0) & 0xffff) / 65535; }
function connects(r, n, dir) { return n && (n.kind === 'cube' || n.id === r.id || (r.kind === 'pane' && (n.kind === 'pane' || n.kind === 'glass'))); }
function shapeBoxes(r, x, y, z, vis) {
  const k = r.kind, p = r.p;
  switch (k) {
    case 'slab': return p.type === 'top' ? [[0, 8, 0, 16, 16, 16]] : p.type === 'double' ? [[0, 0, 0, 16, 16, 16]] : [[0, 0, 0, 16, 8, 16]];
    case 'stairs': {
      const f = p.facing || 'east', top = p.half === 'top';
      const base = top ? [0, 8, 0, 16, 16, 16] : [0, 0, 0, 16, 8, 16];
      const y0 = top ? 0 : 8, y1 = top ? 8 : 16;
      const st = { east: [8, y0, 0, 16, y1, 16], west: [0, y0, 0, 8, y1, 16], south: [0, y0, 8, 16, y1, 16], north: [0, y0, 0, 16, y1, 8] }[f];
      return [base, st];
    }
    case 'door': {
      const f = p.facing || 'east', t = { east: [0, 0, 0, 3, 16, 16], west: [13, 0, 0, 16, 16, 16], south: [0, 0, 0, 16, 16, 3], north: [0, 0, 13, 16, 16, 16] };
      return [t[f]];
    }
    case 'carpet': return [[0, 0, 0, 16, 1, 16]];
    case 'bed': return [[0, 0, 0, 16, 9, 16]];
    case 'lantern': return p.hanging === 'true' ? [[5, 1, 5, 11, 8, 11], [6, 8, 6, 10, 10, 10]] : [[5, 0, 5, 11, 7, 11], [6, 7, 6, 10, 9, 10]];
    case 'chain': return [[7, 0, 7, 9, 16, 9]];
    case 'rod': return [[7, 0, 7, 9, 16, 9]];
    case 'custom': return CUSTOM[r.id];
    case 'pane': case 'fence': case 'wall': {
      const post = k === 'pane' ? [7, 0, 7, 9, 16, 9] : k === 'fence' ? [6, 0, 6, 10, 16, 10] : [4, 0, 4, 12, 16, 12];
      const out = [post];
      for (const d of ['north', 'south', 'east', 'west']) {
        const dv = DIRV[d], n = vis(x + dv[0], y, z + dv[2]);
        if (!connects(r, n, d)) continue;
        if (k === 'pane') out.push({ north: [7, 0, 0, 9, 16, 7], south: [7, 0, 9, 9, 16, 16], west: [0, 0, 7, 7, 16, 9], east: [9, 0, 7, 16, 16, 9] }[d]);
        else if (k === 'fence') { const a = { north: [7, 6, 0, 9, 9, 6], south: [7, 6, 10, 9, 9, 16], west: [0, 6, 7, 6, 9, 9], east: [10, 6, 7, 16, 9, 9] }[d]; out.push(a, [a[0], 12, a[2], a[3], 15, a[5]]); }
        else out.push({ north: [5, 0, 0, 11, 14, 4], south: [5, 0, 12, 11, 14, 16], west: [0, 0, 5, 4, 14, 11], east: [12, 0, 5, 16, 14, 11] }[d]);
      }
      return out;
    }
  }
  return [[0, 0, 0, 16, 16, 16]];
}

/* Terrain */
function buildTerrain() {
  const [tx0, tx1, tz0, tz1] = D.terrain.bounds, H = D.terrain.heights;
  const ex = new Map((D.terrain.excavate || []).map(r => [r[0] + ',' + r[1], r[2]]));
  const BOT = 100, B = mkB();
  const hh = (x, z) => {
    if (x < tx0 || x > tx1 || z < tz0 || z > tz1) return BOT;
    const k = x + ',' + z;
    if (ex.has(k)) return ex.get(k);
    return H[z - tz0][x - tx0] + 1;
  };
  for (let z = tz0; z <= tz1; z++) for (let x = tx0; x <= tx1; x++) {
    const h = hh(x, z); if (h <= BOT) continue;
    const k = x + ',' + z, dig = ex.has(k);
    const g = 0.9 + .15 * hash3(x, 7, z), top = dig ? [.48 * g, .40 * g, .28 * g] : [.33 * g, .5 * g, .25 * g], side = dig ? [.50 * g, .36 * g, .25 * g] : [.43 * g, .36 * g, .28 * g];
    addFace(B, 'up', [x, 0, z, x + 1, h, z + 1], top, 1);
    for (const d of ['north', 'south', 'east', 'west']) {
      const dv = DIRV[d], nh = hh(x + dv[0], z + dv[2]);
      if (nh < h) addFace(B, d, [x, nh, z, x + 1, h, z + 1], side, 1);
    }
  }
  return B;
}

function toGeom(B) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(B.p, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(B.c, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(B.u, 2));
  g.setIndex(B.n > 65000 ? new THREE.Uint32BufferAttribute(B.i, 1) : new THREE.Uint16BufferAttribute(B.i, 1));
  return g;
}
function blockTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 16; const x = c.getContext('2d');
  x.fillStyle = '#fff'; x.fillRect(0, 0, 16, 16); x.strokeStyle = 'rgba(0,0,0,.22)'; x.lineWidth = 1; x.strokeRect(.5, .5, 15, 15);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.LinearMipmapLinearFilter; return t;
}

function ensureGL() {
  if (GL) { resize3d(); return; }
  if (typeof THREE === 'undefined') { $('#loading').textContent = 'three.js konnte nicht geladen werden (Internetverbindung nötig).'; return; }
  const cv = $('#gl');
  const renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true });
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(45, 1, .5, 3000);
  const tex = blockTexture();
  const mOpaque = new THREE.MeshBasicMaterial({ vertexColors: true, map: tex, side: THREE.DoubleSide });
  const mGlass = new THREE.MeshBasicMaterial({ vertexColors: true, map: tex, transparent: true, opacity: .4, side: THREE.DoubleSide, depthWrite: false });
  const mTerr = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide });
  GL = { renderer, scene, camera, mOpaque, mGlass, mTerr, meshes: {}, root: new THREE.Group(), terrain: null,
    cam: { th: 0.0, ph: 1.05, d: 190, t: new THREE.Vector3(-690, 140, -790) }, sel: null };
  scene.add(GL.root);
  const eg = new THREE.EdgesGeometry(new THREE.BoxGeometry(1.02, 1.02, 1.02));
  GL.hl = new THREE.LineSegments(eg, new THREE.LineBasicMaterial({ color: 0xff3d2e })); GL.hl.visible = false; scene.add(GL.hl);
  bindControls(cv);
  setBg(); resize3d();
  new ResizeObserver(resize3d).observe($('.stage'));
  buildGroupPanel();
  $('#loading').style.display = 'flex';
  setTimeout(() => { rebuild(); GL.terrain = new THREE.Mesh(toGeom(buildTerrain()), mTerr); scene.add(GL.terrain); $('#loading').style.display = 'none'; preset('east'); loop(); }, 30);
}
function setBg() { if (!GL) return; const dark = getComputedStyle(document.documentElement).getPropertyValue('--mode').trim() === 'dark'; GL.scene.background = new THREE.Color(dark ? 0x0d130f : 0xcfd9d8); }
function resize3d() { if (!GL) return; const st = $('.stage'), w = st.clientWidth, h = st.clientHeight; GL.renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1)); GL.renderer.setSize(w, h, false); GL.camera.aspect = w / h; GL.camera.updateProjectionMatrix(); GL.dirty = true; }
function predNow() { const hid = S3.hidden; return i => !hid.has(REG[R[i]].gi); }
function rebuild() {
  for (const k in GL.meshes) { const m = GL.meshes[k]; for (const q of ['main', 'glass', 'caps']) if (m[q]) { GL.root.remove(m[q]); m[q].geometry.dispose(); } }
  GL.meshes = {};
  const layers = buildModel(predNow());
  for (const y in layers) {
    const L = layers[y], m = {};
    if (L.main.n) { m.main = new THREE.Mesh(toGeom(L.main), GL.mOpaque); GL.root.add(m.main); }
    if (L.caps.n) { m.caps = new THREE.Mesh(toGeom(L.caps), GL.mOpaque); GL.root.add(m.caps); }
    if (L.glass.n) { m.glass = new THREE.Mesh(toGeom(L.glass), GL.mGlass); m.glass.renderOrder = 2; GL.root.add(m.glass); }
    GL.meshes[y] = m;
  }
  applyCut();
}
function applyCut() {
  const ym = S3.ymax;
  for (const y in GL.meshes) {
    const m = GL.meshes[y], Y_ = +y, on = S3.single ? Y_ === ym : Y_ <= ym;
    if (m.main) m.main.visible = on; if (m.glass) m.glass.visible = on; if (m.caps) m.caps.visible = (Y_ === ym);
  }
  if (GL.terrain) GL.terrain.visible = S3.terrain && !S3.single;
  $('#cutLabel').textContent = `Y = ${ym}` + (S3.single ? ' (nur diese Ebene)' : '');
  GL.dirty = true;
}
function camPos() { const c = GL.cam; return new THREE.Vector3(c.t.x + c.d * Math.sin(c.ph) * Math.cos(c.th), c.t.y + c.d * Math.cos(c.ph), c.t.z + c.d * Math.sin(c.ph) * Math.sin(c.th)); }
function loop() { requestAnimationFrame(loop); if (!GL.dirty) return; GL.dirty = false; GL.camera.position.copy(camPos()); GL.camera.lookAt(GL.cam.t); GL.renderer.render(GL.scene, GL.camera); }
const PRESETS = {
  east: { th: 0.25, ph: 1.12, d: 135, t: [-680, 143, 790] }, west: { th: Math.PI - 0.3, ph: 1.15, d: 140, t: [-700, 138, 790] },
  north: { th: Math.PI / 2 + .1, ph: 1.1, d: 150, t: [-690, 140, 790] }, south: { th: -Math.PI / 2 - .2, ph: 1.1, d: 150, t: [-690, 140, 790] },
  top: { th: -Math.PI / 2, ph: .02, d: 200, t: [-690, 130, 790] }, iso: { th: .75, ph: .95, d: 165, t: [-690, 135, 790] }
};
function preset(n) { const p = PRESETS[n]; Object.assign(GL.cam, { th: p.th, ph: p.ph, d: p.d }); GL.cam.t.set(p.t[0], p.t[1], -p.t[2]); GL.dirty = true; }
function focusBox(x, y, z, span) { GL.cam.t.set(x, y, -z); GL.cam.d = Math.max(30, span * 1.9); GL.cam.ph = 1.0; GL.dirty = true; }
function bindControls(cv) {
  const pts = new Map(); let last = null, moved = 0, pinch = 0;
  cv.addEventListener('contextmenu', e => e.preventDefault());
  cv.addEventListener('pointerdown', e => { cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, e); last = { x: e.clientX, y: e.clientY, b: e.button, sh: e.shiftKey }; moved = 0; });
  cv.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) { hover(e); return; }
    pts.set(e.pointerId, e);
    if (pts.size === 2) {
      const [a, b] = [...pts.values()], d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      if (pinch) { GL.cam.d = clamp(GL.cam.d * pinch / d, 8, 700); GL.dirty = true; }
      pinch = d; moved += 10; return;
    }
    const dx = e.clientX - last.x, dy = e.clientY - last.y; moved += Math.abs(dx) + Math.abs(dy);
    last.x = e.clientX; last.y = e.clientY;
    if (last.b === 2 || last.sh || last.b === 1) pan(dx, dy); else { GL.cam.th -= dx * .006; GL.cam.ph = clamp(GL.cam.ph - dy * .006, .02, 1.55); }
    GL.dirty = true;
  });
  const up = e => { pts.delete(e.pointerId); pinch = 0; if (moved < 5 && e.type === 'pointerup') pick(e); };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('wheel', e => { e.preventDefault(); GL.cam.d = clamp(GL.cam.d * (e.deltaY > 0 ? 1.1 : .9), 8, 700); GL.dirty = true; }, { passive: false });
}
function pan(dx, dy) {
  const cam = GL.camera, k = GL.cam.d * .0016, right = new THREE.Vector3().setFromMatrixColumn(cam.matrix, 0), up = new THREE.Vector3(0, 1, 0);
  const fwd = new THREE.Vector3(-right.z, 0, right.x).normalize();
  GL.cam.t.addScaledVector(right, -dx * k).addScaledVector(fwd, -dy * k * (GL.cam.ph < .3 ? 1 : 0)).addScaledVector(up, dy * k * (GL.cam.ph < .3 ? 0 : 1));
}
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
function rayBlock(e) {
  const cv = $('#gl'), r = cv.getBoundingClientRect(), m = new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  GL.camera.updateMatrixWorld(); const rc = new THREE.Raycaster(); rc.setFromCamera(m, GL.camera);
  const o = rc.ray.origin, d = rc.ray.direction, ox = o.x, oy = o.y, oz = -o.z, dx = d.x, dy = d.y, dz = -d.z;
  let cx = Math.floor(ox), cy = Math.floor(oy), cz = Math.floor(oz);
  const sx = Math.sign(dx), sy = Math.sign(dy), sz = Math.sign(dz);
  const tdx = dx ? Math.abs(1 / dx) : 1e9, tdy = dy ? Math.abs(1 / dy) : 1e9, tdz = dz ? Math.abs(1 / dz) : 1e9;
  let tx = dx ? ((sx > 0 ? cx + 1 - ox : ox - cx) * tdx) : 1e9, ty = dy ? ((sy > 0 ? cy + 1 - oy : oy - cy) * tdy) : 1e9, tz = dz ? ((sz > 0 ? cz + 1 - oz : oz - cz) * tdz) : 1e9;
  const pred = predNow();
  for (let s = 0; s < 900; s++) {
    const j = at(cx, cy, cz);
    if (j >= 0 && pred(j) && (S3.single ? cy === S3.ymax : cy <= S3.ymax)) return j;
    if (tx < ty && tx < tz) { cx += sx; tx += tdx; } else if (ty < tz) { cy += sy; ty += tdy; } else { cz += sz; tz += tdz; }
    if (cy < BB[2] - 3 && sy < 0) break; if (cy > BB[3] + 3 && sy > 0) break;
  }
  return -1;
}
function hover(e) { if (GL.hoverT) return; GL.hoverT = setTimeout(() => { GL.hoverT = 0; }, 60); const j = rayBlock(e); const t = $('#hoverTip'); if (j < 0) { t.style.display = 'none'; return; } const d = describe(j); t.style.display = 'block'; t.textContent = `${d.title} · ${X[j]}, ${Y[j]}, ${Z[j]}`; }
function pick(e) {
  const j = rayBlock(e); if (j < 0) { GL.hl.visible = false; $('#selInfo').innerHTML = '<span class="muted">Klicke auf einen Block für Details.</span>'; GL.dirty = true; return; }
  GL.hl.position.set(X[j] + .5, Y[j] + .5, -(Z[j] + .5)); GL.hl.visible = true; GL.dirty = true;
  const d = describe(j);
  $('#selInfo').innerHTML = `<div class="selhead"><i style="background:${d.color}"></i><b>${d.title}</b></div><code>${d.id}</code><div class="kv"><span>Position</span><b>${d.pos}</b><span>Bauteil</span><b>${d.group}</b><span>Raum</span><b>${d.room}</b></div><button class="mini" id="selPlan">Im Grundriss zeigen</button>`;
  $('#selPlan').onclick = () => { PL.mode = 'y'; PL.val = Y[j]; PL.mark = [X[j], Z[j]]; showTab('plan'); planCenter(X[j], Z[j]); };
}
function buildGroupPanel() {
  const box = $('#groupList'); box.innerHTML = '';
  D.groups.map((g, i) => [g, i]).sort((a, b) => gname(a[0]).localeCompare(gname(b[0]), 'de')).forEach(([g, i]) => {
    const l = document.createElement('label'); l.className = 'chk';
    l.innerHTML = `<input type="checkbox" data-gi="${i}" checked><span>${gname(g)}</span><em>${fmt(D.gstats[g].n)}</em>`; box.appendChild(l);
  });
  box.onchange = e => { const i = +e.target.dataset.gi; if (e.target.checked) S3.hidden.delete(i); else S3.hidden.add(i); schedRebuild(); };
  $$('[data-gpreset]').forEach(b => b.onclick = () => {
    const p = b.dataset.gpreset; S3.hidden.clear();
    D.groups.forEach((g, i) => {
      const roof = g.startsWith('dach_') || g === 'observatorium', cellar = g.startsWith('keller'), light = g === 'beleuchtung';
      if (p === 'noroof' && roof) S3.hidden.add(i);
      if (p === 'shell' && (cellar || light)) S3.hidden.add(i);
      if (p === 'cellar' && !(cellar || g === 'fundament')) S3.hidden.add(i);
    });
    $$('#groupList input').forEach(c => c.checked = !S3.hidden.has(+c.dataset.gi)); schedRebuild();
  });
}
let rbT = 0; function schedRebuild() { clearTimeout(rbT); rbT = setTimeout(() => { rebuild(); }, 40); }
$('#cut').oninput = e => { S3.ymax = +e.target.value; if (GL) applyCut(); };
$('#cut').min = BB[2]; $('#cut').max = BB[3]; $('#cut').value = BB[3];
$('#cutDown').onclick = () => { $('#cut').value = Math.max(BB[2], +$('#cut').value - 1); $('#cut').oninput({ target: $('#cut') }); };
$('#cutUp').onclick = () => { $('#cut').value = Math.min(BB[3], +$('#cut').value + 1); $('#cut').oninput({ target: $('#cut') }); };
$('#single').onchange = e => { S3.single = e.target.checked; if (GL) applyCut(); };
$('#terrainChk').onchange = e => { S3.terrain = e.target.checked; if (GL) applyCut(); };
$$('[data-cam]').forEach(b => b.onclick = () => { ensureGL(); if (GL && GL.meshes) preset(b.dataset.cam); });
$$('[data-floor]').forEach(b => b.onclick = () => { $('#cut').value = b.dataset.floor; $('#cut').oninput({ target: $('#cut') }); });
window.__openRoom = (idx) => {
  const r = D.rooms[idx]; showTab('3d');
  const wait = () => { if (!GL || !GL.terrain) return setTimeout(wait, 80); S3.hidden.clear(); D.groups.forEach((g, i) => { if (g !== r.group) S3.hidden.add(i); });
    $$('#groupList input').forEach(c => c.checked = !S3.hidden.has(+c.dataset.gi)); rebuild(); focusBox((r.x[0] + r.x[1]) / 2, (r.y[0] + r.y[1]) / 2, (r.z[0] + r.z[1]) / 2, Math.max(r.x[1] - r.x[0], r.z[1] - r.z[0], 20)); };
  wait();
};
window.__openGroup = (g) => {
  showTab('3d');
  const wait = () => { if (!GL || !GL.terrain) return setTimeout(wait, 80); S3.hidden.clear(); D.groups.forEach((gg, i) => { if (gg !== g) S3.hidden.add(i); });
    $$('#groupList input').forEach(c => c.checked = !S3.hidden.has(+c.dataset.gi)); rebuild(); const s = D.gstats[g]; focusBox((s.x[0] + s.x[1]) / 2, (s.y[0] + s.y[1]) / 2, (s.z[0] + s.z[1]) / 2, Math.max(s.x[1] - s.x[0], s.z[1] - s.z[0], 20)); };
  wait();
};

/* =====================================================================
   2D: Grundriss & Schnitte
   ===================================================================== */
const byY = {}, byX = {}, byZ = {};
for (let i = 0; i < N; i++) { (byY[Y[i]] = byY[Y[i]] || []).push(i); (byX[X[i]] = byX[X[i]] || []).push(i); (byZ[Z[i]] = byZ[Z[i]] || []).push(i); }
const PL = { mode: 'y', val: 130, group: 'all', ghost: true, grid: true, s: 8, ox: 0, oy: 0, mark: null, pin: null };
const RANGE = { y: [BB[2], BB[3]], x: [BB[0], BB[1]], z: [BB[4], BB[5]] };
const pc = $('#planCv'), pctx = pc.getContext('2d');

function planUV(i) { return PL.mode === 'y' ? [X[i], Z[i]] : PL.mode === 'z' ? [X[i], -Y[i] - 1] : [Z[i], -Y[i] - 1]; }
function planExt() {
  if (PL.mode === 'y') return [BB[0] - 2, BB[4] - 2, BB[1] + 3, BB[5] + 3];
  if (PL.mode === 'z') return [BB[0] - 2, -BB[3] - 3, BB[1] + 3, -BB[2] + 2];
  return [BB[4] - 2, -BB[3] - 3, BB[5] + 3, -BB[2] + 2];
}
function planFit() {
  const r = pc.getBoundingClientRect(), dpr = devicePixelRatio || 1;
  pc.width = Math.max(300, r.width * dpr); pc.height = Math.max(300, r.height * dpr);
  const e = planExt(), w = pc.width, h = pc.height;
  PL.s = Math.min(w / (e[2] - e[0]), h / (e[3] - e[1]));
  PL.ox = -e[0] * PL.s + (w - (e[2] - e[0]) * PL.s) / 2; PL.oy = -e[1] * PL.s + (h - (e[3] - e[1]) * PL.s) / 2;
}
function planCenter(x, z) {
  const u = PL.mode === 'y' ? x : (PL.mode === 'z' ? x : z), v = PL.mode === 'y' ? z : -PL.val;
  PL.s = Math.max(PL.s, 26); PL.ox = pc.width / 2 - u * PL.s; PL.oy = pc.height / 2 - v * PL.s; planDraw();
}
function shapeRects(r, mode) {
  const p = r.p, k = r.kind, sec = mode !== 'y';
  const F = [[0, 0, 1, 1]];
  switch (k) {
    case 'stairs': {
      if (!sec) return F;
      const f = p.facing, top = p.half === 'top', along = mode === 'z' ? ['east', 'west'] : ['south', 'north'];
      if (!along.includes(f)) return F;
      const back = f === along[0];
      const low = top ? [0, 0, 1, .5] : [0, .5, 1, 1], st = top ? (back ? [.5, .5, 1, 1] : [0, .5, .5, 1]) : (back ? [.5, 0, 1, .5] : [0, 0, .5, .5]);
      return [low, st];
    }
    case 'slab': return !sec ? F : (p.type === 'top' ? [[0, 0, 1, .5]] : p.type === 'double' ? F : [[0, .5, 1, 1]]);
    case 'door': {
      const f = p.facing;
      if (!sec) return { east: [[0, 0, .19, 1]], west: [[.81, 0, 1, 1]], south: [[0, 0, 1, .19]], north: [[0, .81, 1, 1]] }[f];
      const along = mode === 'z' ? ['east', 'west'] : ['south', 'north'];
      if (!along.includes(f)) return F;
      const a = f === along[0]; return [a ? [0, 0, .19, 1] : [.81, 0, 1, 1]];
    }
    case 'pane': return sec ? [[.4, 0, .6, 1]] : [[.42, 0, .58, 1], [0, .42, 1, .58]];
    case 'fence': case 'wall': case 'chain': case 'rod': return sec ? [[.38, 0, .62, 1]] : [[.36, .36, .64, .64]];
    case 'carpet': return sec ? [[0, .94, 1, 1]] : F;
    case 'bed': return sec ? [[0, .44, 1, 1]] : F;
    case 'lantern': return [[.3, .25, .7, .75]];
    case 'water': return sec ? [[0, .1, 1, 1]] : F;
    case 'custom': return sec ? [[0, .25, 1, 1]] : F;
  }
  return F;
}
function drawCell(c, i, alpha) {
  const r = REG[R[i]], [u, v] = planUV(i), s = PL.s, px = PL.ox + u * s, py = PL.oy + v * s;
  c.globalAlpha = (r.kind === 'glass' || r.kind === 'pane' ? .75 : 1) * alpha; c.fillStyle = r.color;
  for (const q of shapeRects(r, PL.mode)) c.fillRect(px + q[0] * s, py + q[1] * s, (q[2] - q[0]) * s + .6, (q[3] - q[1]) * s + .6);
  if (s >= 9 && alpha === 1) {
    c.globalAlpha = 1;
    if (r.kind === 'stairs' && PL.mode === 'y') {
      const f = r.p.facing, dx = f === 'east' ? 1 : f === 'west' ? -1 : 0, dz = f === 'south' ? 1 : f === 'north' ? -1 : 0, cx = px + s / 2, cy = py + s / 2, L = s * .32;
      c.fillStyle = 'rgba(255,255,255,.85)'; c.beginPath(); c.moveTo(cx + dx * L, cy + dz * L); c.lineTo(cx - dx * L + dz * L * .8, cy - dz * L + dx * L * .8); c.lineTo(cx - dx * L - dz * L * .8, cy - dz * L - dx * L * .8); c.fill();
    }
    if (r.kind === 'lantern') { c.fillStyle = '#fff3b0'; c.fillRect(px + s * .42, py + s * .42, s * .16, s * .16); }
  }
  c.globalAlpha = 1;
}
function sliceList() {
  const L = PL.mode === 'y' ? byY[PL.val] : PL.mode === 'z' ? byZ[PL.val] : byX[PL.val];
  const gi = PL.group === 'all' ? -1 : D.groups.indexOf(PL.group);
  return (L || []).filter(i => gi < 0 || REG[R[i]].gi === gi);
}
function planDraw() {
  if (!$('#tab-plan').classList.contains('on')) return;
  const c = pctx, w = pc.width, h = pc.height, s = PL.s;
  c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = css('--canvas'); c.fillRect(0, 0, w, h);
  const list = sliceList();
  if (PL.mode === 'y' && PL.ghost) { const set = new Set(list.map(i => X[i] * 4096 + Z[i])); for (const i of (byY[PL.val - 1] || [])) { if (!set.has(X[i] * 4096 + Z[i])) drawCell(c, i, .28); } }
  for (const i of list) drawCell(c, i, 1);
  const e = planExt();
  if (PL.grid) {
    const step = s >= 14 ? 1 : 5; c.lineWidth = 1;
    const u0 = Math.floor((-PL.ox) / s), u1 = Math.ceil((w - PL.ox) / s), v0 = Math.floor((-PL.oy) / s), v1 = Math.ceil((h - PL.oy) / s);
    for (let u = Math.ceil(u0 / step) * step; u <= u1; u += step) { c.strokeStyle = u % 5 === 0 ? css('--grid5') : css('--grid'); c.beginPath(); c.moveTo(PL.ox + u * s, 0); c.lineTo(PL.ox + u * s, h); c.stroke(); }
    for (let v = Math.ceil(v0 / step) * step; v <= v1; v += step) { c.strokeStyle = v % 5 === 0 ? css('--grid5') : css('--grid'); c.beginPath(); c.moveTo(0, PL.oy + v * s); c.lineTo(w, PL.oy + v * s); c.stroke(); }
    c.fillStyle = css('--muted'); c.font = `${Math.round(11 * (devicePixelRatio || 1))}px system-ui`;
    const ls = s >= 14 ? 5 : 10;
    for (let u = Math.ceil(u0 / ls) * ls; u <= u1; u += ls) c.fillText(String(u), PL.ox + u * s + 3, 12 * (devicePixelRatio || 1));
    for (let v = Math.ceil(v0 / ls) * ls; v <= v1; v += ls) c.fillText(String(PL.mode === 'y' ? v : -v), 3, PL.oy + v * s - 3);
  }
  if (PL.mark) { const u = PL.mode === 'y' ? PL.mark[0] : (PL.mode === 'z' ? PL.mark[0] : PL.mark[1]), v = PL.mode === 'y' ? PL.mark[1] : -PL.val - 1; c.strokeStyle = '#ff3d2e'; c.lineWidth = 2; c.strokeRect(PL.ox + u * s - 1, PL.oy + v * s - 1, s + 2, s + 2); }
  if (PL.pin) { c.strokeStyle = '#2f9bff'; c.lineWidth = 2; c.strokeRect(PL.ox + PL.pin[0] * s, PL.oy + PL.pin[1] * s, s, s); }
  // Legende
  const cnt = {}; for (const i of list) { const r = REG[R[i]]; const k = r.id; cnt[k] = (cnt[k] || 0) + 1; }
  const rows = Object.entries(cnt).sort((a, b) => b[1] - a[1]);
  $('#legend').innerHTML = `<div class="lgh"><b>${rows.reduce((a, b) => a + b[1], 0)}</b> Blöcke in dieser Schicht</div>` + rows.map(([k, n]) => `<div class="lg"><i style="background:${colorOf(k)}"></i><span>${deName(k)}</span><em>${fmt(n)}</em></div>`).join('');
  const lab = { y: `Grundriss Ebene Y = ${PL.val}`, z: `Schnitt bei Z = ${PL.val} (Blick nach Norden)`, x: `Schnitt bei X = ${PL.val} (Blick nach Osten, rechts = Süden)` }[PL.mode];
  $('#planTitle').textContent = lab + (PL.mode === 'y' ? ` · Norden oben, Osten rechts` : '');
  $('#planVal').textContent = PL.val; $('#planRange').value = PL.val;
}
function planSetMode(m) {
  PL.mode = m; PL.val = Math.min(RANGE[m][1], Math.max(RANGE[m][0], m === 'y' ? 130 : m === 'z' ? 790 : -690));
  $('#planRange').min = RANGE[m][0]; $('#planRange').max = RANGE[m][1]; planFit(); planDraw();
}
$('#planMode').onchange = e => planSetMode(e.target.value);
$('#planRange').oninput = e => { PL.val = +e.target.value; planDraw(); };
$('#planDown').onclick = () => { PL.val = Math.max(RANGE[PL.mode][0], PL.val - 1); planDraw(); };
$('#planUp').onclick = () => { PL.val = Math.min(RANGE[PL.mode][1], PL.val + 1); planDraw(); };
$('#planGroup').onchange = e => { PL.group = e.target.value; planDraw(); };
$('#planGhost').onchange = e => { PL.ghost = e.target.checked; planDraw(); };
$('#planGrid').onchange = e => { PL.grid = e.target.checked; planDraw(); };
$('#planFit').onclick = () => { planFit(); planDraw(); };
$$('[data-plany]').forEach(b => b.onclick = () => { if (PL.mode !== 'y') { PL.mode = 'y'; $('#planMode').value = 'y'; $('#planRange').min = RANGE.y[0]; $('#planRange').max = RANGE.y[1]; planFit(); } PL.val = +b.dataset.plany; planDraw(); });
{
  const gs = $('#planGroup'); gs.innerHTML = '<option value="all">Alle Bauteile</option>' + D.groups.slice().sort((a, b) => gname(a).localeCompare(gname(b), 'de')).map(g => `<option value="${g}">${gname(g)}</option>`).join('');
  $('#planRange').min = RANGE.y[0]; $('#planRange').max = RANGE.y[1]; $('#planRange').value = PL.val;
  let drag = null;
  pc.addEventListener('pointerdown', e => { pc.setPointerCapture(e.pointerId); drag = { x: e.clientX, y: e.clientY, ox: PL.ox, oy: PL.oy, m: 0 }; });
  pc.addEventListener('pointermove', e => {
    if (drag) { const k = devicePixelRatio || 1; drag.m += Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y); PL.ox = drag.ox + (e.clientX - drag.x) * k; PL.oy = drag.oy + (e.clientY - drag.y) * k; planDraw(); }
    else planHover(e, false);
  });
  pc.addEventListener('pointerup', e => { if (drag && drag.m < 5) planHover(e, true); drag = null; });
  pc.addEventListener('wheel', e => {
    e.preventDefault(); const k = devicePixelRatio || 1, r = pc.getBoundingClientRect(), mx = (e.clientX - r.left) * k, my = (e.clientY - r.top) * k, f = e.deltaY < 0 ? 1.15 : .87, ns = clamp(PL.s * f, 2, 90);
    const u = (mx - PL.ox) / PL.s, v = (my - PL.oy) / PL.s; PL.s = ns; PL.ox = mx - u * ns; PL.oy = my - v * ns; planDraw();
  }, { passive: false });
}
function planHover(e, pin) {
  const k = devicePixelRatio || 1, r = pc.getBoundingClientRect(), mx = (e.clientX - r.left) * k, my = (e.clientY - r.top) * k;
  const u = Math.floor((mx - PL.ox) / PL.s), v = Math.floor((my - PL.oy) / PL.s);
  let x, y, z; if (PL.mode === 'y') { x = u; z = v; y = PL.val; } else if (PL.mode === 'z') { x = u; y = -v - 1; z = PL.val; } else { z = u; y = -v - 1; x = PL.val; }
  const j = at(x, y, z), info = $('#planInfo');
  if (pin) { PL.pin = [u, v]; planDraw(); }
  if (j < 0) { info.innerHTML = `<b>X ${x} · Y ${y} · Z ${z}</b> – leer`; return; }
  const d = describe(j); info.innerHTML = `<i class="sw" style="background:${d.color}"></i><b>${d.title}</b> <code>${d.id}</code> · ${d.pos} · ${d.group} · Raum: ${d.room}`;
}
window.__onTheme = () => { setBg(); planDraw(); };
new ResizeObserver(() => { if ($('#tab-plan').classList.contains('on')) { planFit(); planDraw(); } }).observe(pc.parentElement);

/* =====================================================================
   Raumbuch
   ===================================================================== */
function renderRooms() {
  const q = ($('#roomQ').value || '').toLowerCase(), gsel = $('#roomG').value;
  const rows = D.rooms.map((r, i) => [r, i]).filter(([r]) => (gsel === 'all' || r.group === gsel) && (r.name + ' ' + r.text + ' ' + r.access).toLowerCase().includes(q));
  $('#roomList').innerHTML = rows.map(([r, i]) => {
    const pct = r.stand ? Math.round(100 * r.reach / r.stand) : 0;
    return `<article class="room"><header><h3>${r.name}</h3><span class="tag">${gname(r.group)}</span></header><p>${r.text}</p>
    <dl><dt>X</dt><dd>${r.x[0]} … ${r.x[1]}</dd><dt>Y</dt><dd>${r.y[0]} … ${r.y[1]}</dd><dt>Z</dt><dd>${r.z[0]} … ${r.z[1]}</dd><dt>Maße</dt><dd>${r.x[1] - r.x[0] + 1} × ${r.z[1] - r.z[0] + 1} × ${r.y[1] - r.y[0] + 1}</dd></dl>
    <p class="acc"><b>Zugang:</b> ${r.access}</p>
    <div class="reach" title="Begehbare Bodenzellen, die vom Eingang aus zu Fuß erreichbar sind"><div style="width:${pct}%"></div></div><small class="muted">${r.group === 'observatorium' ? 'Zierraum – bewusst ohne Zugang' : `Begehbarkeit: ${pct} % (${fmt(r.reach)} von ${fmt(r.stand)} Bodenzellen)`}</small>
    <div class="row"><button class="mini" onclick="__openRoom(${i})">3D</button><button class="mini" data-plan="${i}">Grundriss</button></div></article>`;
  }).join('') || '<p class="muted">Keine Räume gefunden.</p>';
  $$('[data-plan]').forEach(b => b.onclick = () => { const r = D.rooms[+b.dataset.plan]; PL.mode = 'y'; $('#planMode').value = 'y'; PL.val = r.y[0]; PL.group = 'all'; $('#planGroup').value = 'all'; PL.mark = null; showTab('plan'); planCenter((r.x[0] + r.x[1]) / 2, (r.z[0] + r.z[1]) / 2); });
}
{ const g = $('#roomG'); g.innerHTML = '<option value="all">Alle Bauteile</option>' + [...new Set(D.rooms.map(r => r.group))].map(x => `<option value="${x}">${gname(x)}</option>`).join(''); g.onchange = renderRooms; $('#roomQ').oninput = renderRooms; renderRooms(); }

/* =====================================================================
   Material
   ===================================================================== */
const STACK1 = new Set(['water_bucket']); const stackOf = id => (STACK1.has(id) || id.endsWith('_bed')) ? 1 : 64;
function packing(id, n) { const st = stackOf(id), per = st * 27, sh = Math.floor(n / per), rem = n % per, stacks = Math.floor(rem / st), loose = rem % st; return { sh, stacks, loose, st }; }
function packText(id, n) { const p = packing(id, n), a = []; if (p.sh) a.push(`${p.sh} Shulker`); if (p.stacks) a.push(`${p.stacks} Stack${p.stacks > 1 ? 's' : ''}`); if (p.loose) a.push(`${p.loose} einzeln`); return a.join(' + ') || '0'; }
function matData(g) { return g === 'all' ? D.counts : (D.gcounts[g] || {}); }
function renderMat() {
  const g = $('#matG').value, q = ($('#matQ').value || '').toLowerCase(), sort = $('#matSort').value, data = matData(g);
  let rows = Object.entries(data).filter(([k]) => (k + ' ' + deName(k)).toLowerCase().includes(q));
  rows.sort(sort === 'name' ? (a, b) => deName(a[0]).localeCompare(deName(b[0]), 'de') : (a, b) => b[1] - a[1]);
  const tot = Object.values(data).reduce((a, b) => a + b, 0), mx = Math.max(1, ...Object.values(data));
  $('#matTot').textContent = fmt(tot); $('#matTyp').textContent = fmt(Object.keys(data).length);
  $('#matStacks').textContent = fmt(Object.entries(data).reduce((a, [k, n]) => a + Math.ceil(n / stackOf(k)), 0));
  $('#matRows').innerHTML = rows.map(([k, n]) => `<tr><td><i class="sw" style="background:${colorOf(k)}"></i>${deName(k)}</td><td><code>minecraft:${k}</code></td><td class="num">${fmt(n)}</td><td>${packText(k, n)}</td><td class="barc"><div class="bar"><i style="width:${Math.max(1.5, 100 * n / mx)}%"></i></div></td></tr>`).join('');
}
{ const g = $('#matG'); g.innerHTML = '<option value="all">Gesamtes Bauwerk</option>' + D.groups.slice().sort((a, b) => gname(a).localeCompare(gname(b), 'de')).map(x => `<option value="${x}">${gname(x)}</option>`).join('');
  g.onchange = renderMat; $('#matQ').oninput = renderMat; $('#matSort').onchange = renderMat; renderMat(); }
function download(name, text, type) { const a = document.createElement('a'), u = URL.createObjectURL(new Blob(['\ufeff' + text], { type: type || 'text/csv;charset=utf-8' })); a.href = u; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(u), 1500); }
$('#dlMat').onclick = () => download('blackthorn-material.csv', 'Minecraft-ID;Name;Anzahl;Shulker;Stacks;Einzeln\n' + Object.entries(D.counts).sort((a, b) => b[1] - a[1]).map(([k, n]) => { const p = packing(k, n); return `minecraft:${k};${deName(k)};${n};${p.sh};${p.stacks};${p.loose}`; }).join('\n'));
$('#dlGroup').onclick = () => { const o = ['Bauteil;Minecraft-ID;Name;Anzahl']; for (const g of Object.keys(D.gcounts).sort()) for (const [k, n] of Object.entries(D.gcounts[g]).sort((a, b) => b[1] - a[1])) o.push(`${gname(g)};minecraft:${k};${deName(k)};${n}`); download('blackthorn-material-je-bauteil.csv', o.join('\n')); };
$('#dlBlocks').onclick = () => { const o = ['X;Y;Z;Block;Zustand;Bauteil']; const ord = Array.from({ length: N }, (_, i) => i).sort((a, b) => Y[a] - Y[b] || Z[a] - Z[b] || X[a] - X[b]); for (const i of ord) { const r = REG[R[i]]; o.push(`${X[i]};${Y[i]};${Z[i]};minecraft:${r.id};${r.props};${r.g}`); } download('blackthorn-blockliste.csv', o.join('\n')); };
$('#dlLayer').onclick = () => { const y = PL.mode === 'y' ? PL.val : 130, o = ['X;Z;Block;Zustand;Bauteil']; for (const i of (byY[y] || []).slice().sort((a, b) => Z[a] - Z[b] || X[a] - X[b])) { const r = REG[R[i]]; o.push(`${X[i]};${Z[i]};minecraft:${r.id};${r.props};${r.g}`); } download(`blackthorn-ebene-y${y}.csv`, o.join('\n')); };

/* Koordinatensuche */
function renderCoord() {
  const q = ($('#coordQ').value || '').toLowerCase().trim(); const out = []; const nums = q.match(/-?\d+/g);
  for (let i = 0; i < N && out.length < 300; i++) {
    const r = REG[R[i]];
    if (nums && nums.length >= 2 && /^[-\d\s,;.]+$/.test(q)) { const a = nums.map(Number), c = [X[i], Y[i], Z[i]]; if (!a.every(v => c.includes(v))) continue; }
    else if (q && !(`${r.id} ${deName(r.id)} ${r.g} ${gname(r.g)}`).toLowerCase().includes(q)) continue;
    out.push(i);
  }
  $('#coordRows').innerHTML = out.map(i => { const r = REG[R[i]]; return `<tr><td>${X[i]}</td><td>${Y[i]}</td><td>${Z[i]}</td><td>${deName(r.id)}</td><td><code>${r.props}</code></td><td>${gname(r.g)}</td></tr>`; }).join('');
  $('#coordN').textContent = out.length >= 300 ? '300+ Treffer (erste 300)' : out.length + ' Treffer';
}
$('#coordQ').oninput = renderCoord; renderCoord();

/* =====================================================================
   Bauplan
   ===================================================================== */
const PROG = LS.get('bt-prog', {}), WHO = LS.get('bt-who', {});
function renderBuild() {
  let done = 0, total = 0, blocksDone = 0;
  $('#phases').innerHTML = PHASES.map(ph => {
    const gs = ph.groups.filter(g => D.gstats[g]);
    const n = gs.reduce((a, g) => a + D.gstats[g].n, 0), d = gs.filter(g => PROG[g]).length;
    return `<article class="phase"><header><h3>${ph.name}</h3><span class="tag">${fmt(n)} Blöcke · ${d}/${gs.length}</span></header><p class="muted">${ph.text}</p>
    <div class="groups">${gs.map(g => { const s = D.gstats[g], top = Object.entries(D.gcounts[g] || {}).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([k, c]) => `${deName(k)} ${fmt(c)}`).join(' · ');
      return `<div class="grp ${PROG[g] ? 'done' : ''}"><label class="chk big"><input type="checkbox" data-done="${g}" ${PROG[g] ? 'checked' : ''}><span><b>${gname(g)}</b><small>${fmt(s.n)} Blöcke · X ${s.x[0]}…${s.x[1]} · Y ${s.y[0]}…${s.y[1]} · Z ${s.z[0]}…${s.z[1]}</small><small class="muted">${top}</small></span></label>
      <div class="row"><input class="who" data-who="${g}" placeholder="Wer baut das?" value="${(WHO[g] || '').replace(/"/g, '&quot;')}"><button class="mini" onclick="__openGroup('${g}')">3D</button></div></div>`; }).join('')}</div></article>`;
  }).join('');
  for (const g of Object.keys(D.gstats)) { total += D.gstats[g].n; if (PROG[g]) { done++; blocksDone += D.gstats[g].n; } }
  const pct = Math.round(100 * blocksDone / total); $('#progBar').style.width = pct + '%'; $('#progTxt').textContent = `${pct} % der Blöcke · ${done}/${Object.keys(D.gstats).length} Bauteile fertig`;
}
$('#phases').addEventListener('change', e => { if (e.target.dataset.done) { PROG[e.target.dataset.done] = e.target.checked; LS.set('bt-prog', PROG); renderBuild(); } });
$('#phases').addEventListener('input', e => { if (e.target.dataset.who) { WHO[e.target.dataset.who] = e.target.value; LS.set('bt-who', WHO); } });
$('#dlProg').onclick = () => download('blackthorn-fortschritt.json', JSON.stringify({ fertig: PROG, zuständig: WHO, stand: new Date().toISOString() }, null, 2), 'application/json');
$('#impProg').onchange = e => { const f = e.target.files[0]; if (!f) return; f.text().then(t => { try { const j = JSON.parse(t); Object.assign(PROG, j.fertig || {}); Object.assign(WHO, j['zuständig'] || {}); LS.set('bt-prog', PROG); LS.set('bt-who', WHO); renderBuild(); } catch (err) { alert('Datei konnte nicht gelesen werden.'); } }); };
renderBuild();

/* =====================================================================
   Übersicht
   ===================================================================== */
{
  const C = D.checks, items = Object.values(D.counts).reduce((a, b) => a + b, 0);
  $('#st-blocks').textContent = fmt(D.meta.total); $('#st-items').textContent = fmt(items); $('#st-rooms').textContent = fmt(D.rooms.length);
  $('#st-doors').textContent = fmt(C.doors); $('#st-stairs').textContent = fmt(C.stairs); $('#st-panes').textContent = fmt(C.panes);
  const hist = C.light_hist, hmax = Math.max(...Object.values(hist));
  $('#checks').innerHTML = `
  <div class="chk-item ok"><b>Begehbarkeit</b><p>Per Simulation (Gehen, Springen, Treppen, Türen) vom Haupteingang aus: <b>${C.reach_pct} %</b> aller ${fmt(C.stand)} Bodenzellen in den ${D.rooms.length - 1} Wohn- und Kellerräumen sind erreichbar. Gegenprobe: Mit zugemauertem Eingang sind nur ${fmt(C.sealed_cells)} Zellen (nur draußen) erreichbar, mit Eingang ${fmt(C.reach_cells)}. Der Rest sind Zellen hinter Möbeln, in Türmen und Dachräumen.</p></div>
  <div class="chk-item ok"><b>Licht / Monster-Schutz</b><p>${fmt(C.lanterns_designed)} Laternen wurden von Hand geplant (Kronleuchter, Hängelampen), ${fmt(C.lanterns_auto)} weitere automatisch an Wänden ergänzt. In allen ${fmt(C.spawn_cells)} geschlossenen Bodenzellen (inkl. Dachböden) gilt: Mindestlicht <b>${C.min_light}</b>, Zellen mit Licht 0: <b>${C.zero_light}</b>. Seit Java 1.18 spawnen Monster nur bei Blocklicht 0.</p>
  <div class="hist">${Object.entries(hist).map(([l, n]) => `<div title="Licht ${l}: ${n} Zellen"><i style="height:${Math.max(3, 60 * n / hmax)}px"></i><small>${l}</small></div>`).join('')}</div></div>
  <div class="chk-item"><b>Aushub</b><p>Für die drei Keller müssen ca. <b>${fmt(C.excavation)}</b> Blöcke Fels/Erde zwischen Y=106 und Geländehöhe entfernt werden (aus der Höhenkarte berechnet, ±10 %). Im Survival-Modus ist das der größte Einzelaufwand – am besten zuerst und mit Effizienz-Werkzeugen.</p></div>
  <div class="chk-item warn"><b>Ehrlicher Hinweis</b><p>Das Modell wurde algorithmisch erzeugt und per Simulation geprüft, aber nicht im Spiel gebaut. Treppenecken verbindet Minecraft beim Setzen selbst (hier sind alle Treppen „gerade“ eingetragen). Prüft die Geländehöhen vor dem Aushub mit F3. Der Weltstand laut level.dat ist 26.3.</p></div>`;
  $('#facts').innerHTML = `<div><small>GRUNDSTÜCK</small><b>X ${D.meta.bbox[0]} … ${D.meta.bbox[1]} · Z ${D.meta.bbox[4]} … ${D.meta.bbox[5]}</b></div><div><small>HÖHE</small><b>Y ${D.meta.bbox[2]} (Keller 3) … ${D.meta.bbox[3]} (Kuppel)</b></div><div><small>EBENEN</small><b>Keller 105/113/121 · EG 129 · OG 137 · Dach ab 145</b></div><div><small>EINGANG</small><b>Osten, X −646 · Treppe bei X −637 · Z 789/790</b></div><div><small>KLIPPE</small><b>Westen · Terrasse X −742 … −723</b></div><div><small>FIRSTHÖHEN</small><b>Halle Y 162 · Residenzen Y 155 · Ostflügel Y 149</b></div>`;
}
$$('[data-go]').forEach(b => b.onclick = () => showTab(b.dataset.go));
if (location.hash && $('#tab-' + location.hash.slice(1))) showTab(location.hash.slice(1)); else showTab('overview');
})();
