(() => {
'use strict';
const data = window.MANSION_DATA;
if (!data) { document.body.innerHTML = '<p style="padding:2rem">Blueprint-Daten konnten nicht geladen werden.</p>'; return; }
const $ = id => document.getElementById(id);
const state = {
  layer: 17, view: '2d', grid: true, coords: true, allLayers: false,
  zoom: 1, panX: 0, panY: 0, dragging: false, start: null,
  completed: {}, materials: {}, phaseChecks: {}, selectedBlock: null
};
const STORE = 'blockplan_mansion_v3';
function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE) || '{}');
    Object.assign(state, {completed:saved.completed||{}, materials:saved.materials||{}, phaseChecks:saved.phaseChecks||{}});
  } catch(e) { console.warn('Lokaler Fortschritt konnte nicht geladen werden',e); }
}
function save() {
  try { localStorage.setItem(STORE, JSON.stringify({completed:state.completed,materials:state.materials,phaseChecks:state.phaseChecks})); }
  catch(e) { console.warn('Speichern fehlgeschlagen',e); }
  updateProgress();
}
function esc(s) { return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function layer() { return data.layers[state.layer]; }
function blockMeta(id) { return data.palette[String(id)] || {name:'Unbekannt',color:'#777',glyph:'?'}; }
function topBlock(x,z) { for (let i=data.layers.length-1;i>=0;i--) { const id=data.layers[i].grid?.[z]?.[x]||0; if(id) return id; } return 0; }
function countProgress(obj) { return Object.values(obj).filter(Boolean).length; }
function updateProgress() {
  const done=countProgress(state.completed), pct=Math.round(done/data.layers.length*100);
  $('overallPercent').textContent=pct+'%'; $('overallBar').style.width=pct+'%';
  $('sideProgress').style.width=pct+'%'; $('sideProgressText').textContent=pct+' % abgeschlossen';
  $('teamPercent').textContent=pct+'%'; $('teamBar').style.width=pct+'%';
  $('doneLayers').textContent=done; $('teamStatus').textContent=done===0?'Noch keine Ebene abgeschlossen.':`${done} von ${data.layers.length} Ebenen fertiggestellt.`;
  $('doneMaterials').innerHTML=`${countProgress(state.materials)}<small> / ${data.materials.length}</small>`;
}
function setLayer(n) {
  state.layer=Math.max(0,Math.min(data.layers.length-1,Number(n)));
  $('layerSlider').value=state.layer;
  const l=layer(), y=Number(String(l.yLevel).match(/-?\d+/)?.[0]||126);
  $('layerNumber').textContent='Y '+y;
  $('layerTitle').textContent=l.name;
  $('layerDescription').textContent=l.description;
  $('layerCategory').textContent=l.category.toUpperCase();
  $('layerRel').textContent=l.relativeY;
  $('layerName').textContent=l.name;
  $('layerDesc').textContent=l.description;
  $('featureCount').textContent=(l.keyFeatures||[]).length;
  $('featureList').innerHTML=(l.keyFeatures||[]).map(x=>`<li>${esc(x)}</li>`).join('');
  $('completeLayer').textContent=state.completed[l.id]?'✓ Ebene abgeschlossen':'✓ Ebene als fertig markieren';
  $('completeLayer').classList.toggle('btn-primary',!state.completed[l.id]);
  const counts=Object.entries(l.counts||{}).filter(([id,n])=>id!=='0'&&n>0).sort((a,b)=>b[1]-a[1]);
  $('blockCount').textContent=counts.length;
  $('layerBlocks').innerHTML=counts.slice(0,8).map(([id,n])=>{const m=blockMeta(id);return `<div class="block-row"><i class="block-swatch" style="background:${esc(m.color)}"></i><span>${esc(m.name)}</span><small>${n.toLocaleString('de-DE')}</small></div>`}).join('') || '<small>Keine gesetzten Blöcke.</small>';
  draw();
}
function resizeCanvas() {
  const c=$('blueprintCanvas'), rect=c.getBoundingClientRect(), dpr=Math.min(devicePixelRatio||1,2);
  c.width=Math.max(1,Math.round(rect.width*dpr)); c.height=Math.max(1,Math.round(rect.height*dpr));
  draw();
}
function draw() {
  const c=$('blueprintCanvas'); if(!c) return;
  const ctx=c.getContext('2d'), w=c.width,h=c.height;
  if(!w||!h)return;
  ctx.clearRect(0,0,w,h);
  const dpr=Math.min(devicePixelRatio||1,2), W=data.dimensions.width,D=data.dimensions.depth;
  if(state.view==='2d') {
    const base=Math.min((w-80*dpr)/W,(h-70*dpr)/D)*state.zoom;
    const cell=Math.max(1,base), ox=(w-W*cell)/2+state.panX*dpr, oy=(h-D*cell)/2+state.panY*dpr;
    ctx.save();
    if(state.grid){ctx.strokeStyle='#50635335';ctx.lineWidth=1;for(let x=0;x<=W;x++){ctx.beginPath();ctx.moveTo(ox+x*cell,oy);ctx.lineTo(ox+x*cell,oy+D*cell);ctx.stroke()}for(let z=0;z<=D;z++){ctx.beginPath();ctx.moveTo(ox,oy+z*cell);ctx.lineTo(ox+W*cell,oy+z*cell);ctx.stroke()}}
    let any=false;
    for(let z=0;z<D;z++)for(let x=0;x<W;x++){
      let id=state.allLayers?topBlock(x,z):layer().grid?.[z]?.[x]||0;
      if(!id)continue; any=true;
      const m=blockMeta(id);ctx.fillStyle=m.color==='transparent'?'#0000':m.color;
      ctx.fillRect(ox+x*cell+.35,oy+z*cell+.35,Math.max(0,cell-.7),Math.max(0,cell-.7));
      if(cell>14*dpr){ctx.strokeStyle='#ffffff22';ctx.strokeRect(ox+x*cell+.5,oy+z*cell+.5,cell-1,cell-1)}
    }
    ctx.strokeStyle='#9bb68c';ctx.lineWidth=1.5*dpr;ctx.strokeRect(ox,oy,W*cell,D*cell);
    if(state.coords){ctx.fillStyle='#92a895';ctx.font=`${10*dpr}px monospace`;ctx.fillText(`X ${-697} → ${-628}`,ox,Math.max(14*dpr,oy-9*dpr));ctx.save();ctx.translate(ox-9*dpr,oy+D*cell);ctx.rotate(-Math.PI/2);ctx.fillText(`Z 765 → 814`,0,0);ctx.restore()}
    ctx.restore(); $('canvasEmpty').hidden=any;
  } else {
    const cell=Math.min((w-80*dpr)/(W+D)*1.25,(h-90*dpr)/(W+D)*1.05)*state.zoom;
    const unitY=cell*.72, cx=w/2+state.panX*dpr, cy=h*.62+state.panY*dpr;
    const project=(x,z,y)=>({x:cx+(x-z)*cell*.5,y:cy+(x+z)*cell*.25-y*unitY});
    const cols=[];
    for(let z=0;z<D;z++)for(let x=0;x<W;x++){
      let min=999,max=-1,top=0;
      for(let i=0;i<data.layers.length;i++){let id=data.layers[i].grid?.[z]?.[x]||0;if(id){const yy=Number(String(data.layers[i].yLevel).match(/-?\d+/)?.[0]||105);min=Math.min(min,yy);if(yy>=max){max=yy;top=id}}}
      if(max>=0)cols.push({x,z,min,max,top});
    }
    cols.sort((a,b)=>(a.x+a.z)-(b.x+b.z)||a.max-b.max);
    const poly=(pts,color)=>{ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);ctx.closePath();ctx.fillStyle=color;ctx.fill();ctx.strokeStyle='#09110c88';ctx.lineWidth=.55*dpr;ctx.stroke()};
    for(const q of cols){
      const p=project(q.x,q.z,q.max-105), ht=Math.max(1,q.max-q.min+1)*unitY, c0=blockMeta(q.top).color;
      const half=cell*.5, quarter=cell*.25;
      const top=[{x:p.x,y:p.y},{x:p.x+half,y:p.y+quarter},{x:p.x,y:p.y+quarter*2},{x:p.x-half,y:p.y+quarter}];
      poly([{x:p.x-half,y:p.y+quarter},{x:p.x,y:p.y+quarter*2},{x:p.x,y:p.y+quarter*2+ht},{x:p.x-half,y:p.y+quarter+ht}],shade(c0,.68));
      poly([{x:p.x,y:p.y+quarter*2},{x:p.x+half,y:p.y+quarter},{x:p.x+half,y:p.y+quarter+ht},{x:p.x,y:p.y+quarter*2+ht}],shade(c0,.48));
      poly(top,c0);
    }
    $('canvasEmpty').hidden=cols.length>0;
  }
}
function shade(hex,f){if(!/^#[0-9a-f]{6}$/i.test(hex))return hex;let n=parseInt(hex.slice(1),16),r=Math.min(255,Math.round((n>>16)*f)),g=Math.min(255,Math.round(((n>>8)&255)*f)),b=Math.min(255,Math.round((n&255)*f));return `rgb(${r},${g},${b})`}
function tab(name) {
  document.querySelectorAll('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.toggle('active',p.id==='panel-'+name));
  const titles={blueprint:['Bauplan-Workbench','Jeder Block an seinem Platz. Plant, baut und verfolgt euren Fortschritt gemeinsam.'],materials:['Materialübersicht','Plant eure Ressourcen, bevor ihr mit dem Bau beginnt.'],rooms:['Raum- und Bereichsatlas','Alle Räume, Funktionen und Spezialanlagen des Herrenhauses.'],phases:['Bauphasen','Ein gemeinsamer Bauplan in überschaubaren Etappen.'],team:['Team & Fortschritt','Haltet euren Baufortschritt fest und teilt ihn mit euren Freunden.']};
  $('pageTitle').textContent=titles[name][0];$('pageSubtitle').textContent=titles[name][1];
}
function renderMaterials(){
  const cats=[...new Set(data.materials.map(m=>m.category))];
  $('materialCategory').innerHTML='<option value="all">Alle Kategorien</option>'+cats.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join('');
  $('materialSummary').innerHTML=[['BLOCKTYPEN',data.materials.length],['GESAMTBLOCKMENGE',data.materials.reduce((a,m)=>a+m.count,0).toLocaleString('de-DE')],['GESCHÄTZTE SHULKER',data.materials.reduce((a,m)=>a+m.shulkers,0).toFixed(1).replace('.',',')]].map(([a,b])=>`<div class="summary-card"><span>${a}</span><strong>${b}</strong><small>${a==='BLOCKTYPEN'?'verschiedene Materialien':a==='GESAMTBLOCKMENGE'?'Blöcke insgesamt':'Shulkerboxen (rechnerisch)'}</small></div>`).join('');
  renderMaterialCards();
}
function renderMaterialCards(){
  const q=$('materialSearch').value.toLowerCase(),cat=$('materialCategory').value;
  const mats=data.materials.filter(m=>(cat==='all'||m.category===cat)&&(`${m.name} ${m.category}`.toLowerCase().includes(q)));
  $('materialsGrid').innerHTML=mats.map(m=>`<label class="material-card ${state.materials[m.id]?'checked':''}"><span class="material-swatch" style="background:${esc(m.color)}">${esc(m.glyph)}</span><span class="material-info"><strong>${esc(m.name)}</strong><small>${esc(m.category)}</small><span class="material-qty">${m.count.toLocaleString('de-DE')} Stück · ${m.stacks} Stacks · ${m.shulkers} Shulker</span></span><input class="material-check" type="checkbox" data-material="${esc(m.id)}" ${state.materials[m.id]?'checked':''}></label>`).join('')||'<p>Keine Materialien gefunden.</p>';
}
function renderRooms(){
  $('roomsGrid').innerHTML=data.rooms.map(r=>`<article class="room-card"><div class="room-top"><span>${esc(r.level)}</span></div><h3>${esc(r.name)}</h3><p>${esc(r.desc)}</p><ul>${(r.highlights||[]).map(h=>`<li>${esc(h)}</li>`).join('')}</ul><div class="room-dims">${esc(r.coords)} · ${esc(r.dimensions)}</div></article>`).join('');
  $('redstoneGrid').innerHTML=data.redstoneGuides.map(r=>`<article class="room-card"><div class="room-top"><span>${esc(r.category)}</span></div><h3>${esc(r.name)}</h3><p>${esc(r.desc)}</p><ul>${(r.materials||[]).slice(0,5).map(x=>`<li>${esc(x)}</li>`).join('')}</ul><div class="room-dims">${esc(r.level)} · ${esc(r.coords)}</div></article>`).join('');
}
function renderPhases(){
  $('phasesList').innerHTML=data.phases.map((p,i)=>{let checks=p.checklist||[],done=checks.filter((_,j)=>state.phaseChecks[`${p.id}-${j}`]).length;return `<article class="phase-card ${i===0?'open':''}"><div class="phase-head" data-phase="${i}"><span class="phase-num">${String(p.id).padStart(2,'0')}</span><div><h3>${esc(p.name)}</h3><p>${esc(p.yRange)} · ${esc(p.focus)}</p></div><span class="phase-count">${done}/${checks.length} ✓</span></div><div class="phase-body">${checks.map((c,j)=>`<label class="phase-check ${state.phaseChecks[`${p.id}-${j}`]?'done':''}"><input type="checkbox" data-phase-check="${p.id}-${j}" ${state.phaseChecks[`${p.id}-${j}`]?'checked':''}><span>${esc(c)}</span></label>`).join('')}</div></article>`}).join('');
}
function exportProject(){
  const payload={format:'blockplan-project',version:1,project:'Bergkamm-Herrenhaus',exportedAt:new Date().toISOString(),world:{seed:data.dimensions.anchor.seed,minecraftVersion:'26.2',anchor:data.dimensions.anchor},progress:{completed:state.completed,materials:state.materials,phaseChecks:state.phaseChecks}};
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='bergkamm-herrenhaus-fortschritt.json';a.click();URL.revokeObjectURL(url);
}
function importProject(file){
  const reader=new FileReader();reader.onload=()=>{try{const obj=JSON.parse(reader.result);if(obj.format!=='blockplan-project'||!obj.progress)throw Error('Keine gültige Blockplan-Projektdatei.');state.completed=obj.progress.completed||{};state.materials=obj.progress.materials||{};state.phaseChecks=obj.progress.phaseChecks||{};save();renderMaterials();renderPhases();setLayer(state.layer);alert('Projektfortschritt wurde importiert.')}catch(e){alert('Import fehlgeschlagen: '+e.message)}};reader.readAsText(file);
}
function copy(text){if(navigator.clipboard?.writeText)navigator.clipboard.writeText(text).then(()=>toast('In Zwischenablage kopiert')).catch(()=>prompt('Kopieren:',text));else prompt('Kopieren:',text)}
let toastTimer;function toast(msg){let el=document.createElement('div');el.textContent=msg;el.style.cssText='position:fixed;bottom:22px;right:22px;background:#263b28;border:1px solid #638353;color:#e6f2e3;padding:11px 15px;border-radius:7px;z-index:99;font:12px sans-serif';document.body.append(el);clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.remove(),1900)}
document.querySelectorAll('.nav-item').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.tab)));
document.querySelectorAll('.view-btn').forEach(b=>b.addEventListener('click',()=>{state.view=b.dataset.view;document.querySelectorAll('.view-btn').forEach(x=>x.classList.toggle('active',x===b));draw()}));
['prevLayer','prevLayerBottom'].forEach(id=>$(id).addEventListener('click',()=>setLayer(state.layer-1)));
['nextLayer','nextLayerBottom'].forEach(id=>$(id).addEventListener('click',()=>setLayer(state.layer+1)));
$('layerSlider').addEventListener('input',e=>setLayer(e.target.value));
$('completeLayer').addEventListener('click',()=>{const id=layer().id;state.completed[id]=!state.completed[id];save();setLayer(state.layer)});
$('gridToggle').addEventListener('click',e=>{state.grid=!state.grid;e.currentTarget.classList.toggle('active',state.grid);draw()});
$('coordToggle').addEventListener('click',e=>{state.coords=!state.coords;e.currentTarget.classList.toggle('active',state.coords);draw()});
$('allLayersToggle').addEventListener('click',e=>{state.allLayers=!state.allLayers;e.currentTarget.classList.toggle('active',state.allLayers);draw()});
$('zoomIn').addEventListener('click',()=>{state.zoom=Math.min(3,state.zoom*1.2);draw()});
$('zoomOut').addEventListener('click',()=>{state.zoom=Math.max(.35,state.zoom/1.2);draw()});
$('zoomReset').addEventListener('click',()=>{state.zoom=1;state.panX=state.panY=0;draw()});
$('blueprintCanvas').addEventListener('wheel',e=>{e.preventDefault();state.zoom=Math.max(.35,Math.min(3,state.zoom*(e.deltaY<0?1.1:.9)));draw()},{passive:false});
const canvas=$('blueprintCanvas');
canvas.addEventListener('pointerdown',e=>{state.dragging=true;state.start={x:e.clientX-state.panX,y:e.clientY-state.panY,clientX:e.clientX,clientY:e.clientY};canvas.setPointerCapture(e.pointerId)});
canvas.addEventListener('pointermove',e=>{if(!state.dragging)return;state.panX=e.clientX-state.start.x;state.panY=e.clientY-state.start.y;draw()});
canvas.addEventListener('pointerup',e=>{
  const moved=state.start && (Math.abs(e.clientX-state.start.clientX)>5 || Math.abs(e.clientY-state.start.clientY)>5);
  state.dragging=false;
  if(!moved && state.view==='2d'){
    const rect=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2),w=canvas.width,h=canvas.height,W=data.dimensions.width,D=data.dimensions.depth;
    const cell=Math.min((w-80*dpr)/W,(h-70*dpr)/D)*state.zoom,ox=(w-W*cell)/2+state.panX*dpr,oy=(h-D*cell)/2+state.panY*dpr;
    const x=Math.floor(((e.clientX-rect.left)*dpr-ox)/cell),z=Math.floor(((e.clientY-rect.top)*dpr-oy)/cell);
    if(x>=0&&x<W&&z>=0&&z<D){const id=state.allLayers?topBlock(x,z):(layer().grid?.[z]?.[x]||0);const y=Number(String(layer().yLevel).match(/-?\d+/)?.[0]||126);toast(id?`${blockMeta(id).name} · X ${-697+x} / Y ${y} / Z ${765+z}`:`Leer · X ${-697+x} / Y ${y} / Z ${765+z}`)}
  }
});
canvas.addEventListener('pointercancel',()=>state.dragging=false);
$('materialSearch').addEventListener('input',renderMaterialCards);$('materialCategory').addEventListener('change',renderMaterialCards);
$('materialsGrid').addEventListener('change',e=>{const id=e.target.dataset.material;if(!id)return;state.materials[id]=e.target.checked;save();renderMaterialCards()});
$('resetMaterials').addEventListener('click',()=>{if(confirm('Alle Material-Markierungen zurücksetzen?')){state.materials={};save();renderMaterialCards()}});
$('roomsGrid').innerHTML='';$('phasesList').addEventListener('click',e=>{const h=e.target.closest('.phase-head');if(h)h.parentElement.classList.toggle('open')});
$('phasesList').addEventListener('change',e=>{const key=e.target.dataset.phaseCheck;if(key===undefined)return;state.phaseChecks[key]=e.target.checked;save();renderPhases()});
$('copyTp').addEventListener('click',()=>copy('/tp @p -662 126 790'));
$('exportBtn').addEventListener('click',exportProject);$('teamExport').addEventListener('click',exportProject);
$('importBtn').addEventListener('click',()=>$('importFile').click());$('importFile').addEventListener('change',e=>{if(e.target.files[0])importProject(e.target.files[0]);e.target.value=''});
window.addEventListener('resize',resizeCanvas);
load();renderMaterials();renderRooms();renderPhases();setLayer(state.layer);resizeCanvas();updateProgress();
})();