
(() => {
'use strict';
const $=s=>document.querySelector(s);
const d=JSON.parse($('#data').textContent);
const zones=[{"id":"L01","name":"Baumaterialien","contents":"Stein, Tiefenschiefer, Holz, Glas, Erden","room":"Keller 1: Lager","group":"keller_1","x":[-706,-696],"y":[122,128],"z":[767,786]},{"id":"L02","name":"Technik & Redstone","contents":"Redstone, Hopper, Rails, Maschinen","room":"Keller 1: Lager","group":"keller_1","x":[-694,-684],"y":[122,128],"z":[767,786]},{"id":"L03","name":"Farmprodukte","contents":"Saatgut, Nahrung, Pflanzen, Farbstoffe","room":"Keller 1: Lager","group":"keller_1","x":[-694,-684],"y":[122,128],"z":[794,813]},{"id":"L04","name":"Lebensmittel & Getränke","contents":"Fässer, Küche, Brauzutaten","room":"Keller 1: Fasskeller","group":"keller_1","x":[-682,-671],"y":[122,128],"z":[767,786]},{"id":"L05","name":"Kühl- & Vorratslager","contents":"Essen, Tierprodukte, Eis","room":"Keller 1: Kuehllager","group":"keller_1","x":[-682,-671],"y":[122,128],"z":[794,813]},{"id":"L06","name":"Ausrüstung","contents":"Werkzeuge, Rüstung, Waffen, Ersatz","room":"Keller 2: Lager","group":"keller_2","x":[-682,-671],"y":[114,120],"z":[767,786]},{"id":"L07","name":"Seltene Items","contents":"Erkundung, Schätze, Karten, Spezialitems","room":"Keller 2: Lager","group":"keller_2","x":[-682,-671],"y":[114,120],"z":[794,813]},{"id":"L08","name":"Massenspeicher A","contents":"Cobblestone, Dirt, Netherrack","room":"Keller 3: Lager","group":"keller_3","x":[-682,-671],"y":[106,112],"z":[767,786]},{"id":"L09","name":"Massenspeicher B","contents":"Tiefenschiefer, Stein, Holz","room":"Keller 3: Lager","group":"keller_3","x":[-694,-684],"y":[106,112],"z":[794,813]},{"id":"L10","name":"Persönliche Reserven","contents":"Sechs separat beschriftete Bereiche","room":"Keller 3: Lager","group":"keller_3","x":[-682,-671],"y":[106,112],"z":[794,813]}];
const reg=d.reg, runs=d.runs, byY=new Map();
let n=0;
for(const [y,z,x,len,ri] of runs){let line=byY.get(y);if(!line){line=[];byY.set(y,line);}for(let k=0;k<len;k++){line.push({n:++n,x:x+k,y,z,ri});}}
const saved=(k,def)=>{try{return JSON.parse(localStorage.getItem(k))||def}catch{return def}};
const store=(k,val)=>{try{localStorage.setItem(k,JSON.stringify(val))}catch{}};
const inv=saved('bt-r5-1-storage',{}), done=saved('bt-r5-1-blocks',{});
const fmt=v=>Number(v).toLocaleString('de-DE');
const safe=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function csv(name,rows){const txt='\ufeff'+rows.map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(';')).join('\r\n');const blob=new Blob([txt],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),800)}
function jumpToRoom(zone){const b=document.querySelector('#tabs [data-tab="plan"]');b?.click();const mode=$('#planMode');mode.value='y';mode.dispatchEvent(new Event('change'));const r=$('#planRange');r.value=zone.y[0];r.dispatchEvent(new Event('input'));}
function renderStorage(){const q=$('#storageQuery').value.toLowerCase();$('#storageZones').innerHTML=zones.filter(z=>(z.name+' '+z.room+' '+z.contents).toLowerCase().includes(q)).map(z=>`<article class="room"><header><h3>${safe(z.id)} · ${safe(z.name)}</h3><span class="tag">${safe(z.group)}</span></header><p class="muted">${safe(z.contents)}</p><small>Originalraum: ${safe(z.room)}<br>Koordinaten X ${z.x.join(' bis ')}, Y ${z.y.join(' bis ')}, Z ${z.z.join(' bis ')}</small><div class="row"><label>Notiz / tatsächlicher Bestand <input type="text" data-stock="${z.id}" value="${safe(inv[z.id]||'')}" placeholder="z. B. 6 Shulker Stein"></label></div><button class="mini" data-jump="${z.id}">Im Grundriss öffnen</button></article>`).join('');}
$('#storageQuery').addEventListener('input',renderStorage);
$('#storageZones').addEventListener('input',e=>{if(e.target.dataset.stock){inv[e.target.dataset.stock]=e.target.value;store('bt-r5-1-storage',inv)}});
$('#storageZones').addEventListener('click',e=>{const id=e.target.dataset.jump;if(id){const z=zones.find(x=>x.id===id);if(z)jumpToRoom(z)}});
$('#storageExport').onclick=()=>csv('blackthorn-lagerplan.csv',[['Zone','Name','Raum','X von','X bis','Y von','Y bis','Z von','Z bis','Planinhalt','Ist-Bestand'],...zones.map(z=>[z.id,z.name,z.room,...z.x,...z.y,...z.z,z.contents,inv[z.id]||''])]);
$('#storageReset').onclick=()=>{if(confirm('Alle manuell eingegebenen Lagerbestände löschen?')){for(const k of Object.keys(inv))delete inv[k];store('bt-r5-1-storage',inv);renderStorage()}};
renderStorage();
let shown=250;
const currentHeight=()=>+$('#stepHeight').value;
function renderStep(){const y=currentHeight(),list=byY.get(y)||[],q=$('#stepSearch').value.trim().toLowerCase();const filtered=q?list.filter(b=>(`${b.x} ${b.y} ${b.z} ${reg[b.ri][0]} ${d.groups[reg[b.ri][2]]}`).toLowerCase().includes(q)):list;
$('#stepLabel').textContent='Y = '+y;$('#stepSummary').textContent=fmt(filtered.length)+' Blockpositionen auf dieser Höhe'+(q?' (gefiltert)':'')+' · '+fmt(filtered.filter(b=>done[b.n]).length)+' abgehakt · Nummern gehören zur originalen Blockfolge';
$('#stepRows').innerHTML=filtered.slice(0,shown).map(b=>`<tr title="Block #${b.n} bei X=${b.x}, Y=${b.y}, Z=${b.z}"><td>#${b.n}</td><td>${b.x}</td><td>${b.y}</td><td>${b.z}</td><td>minecraft:${safe(reg[b.ri][0])}${reg[b.ri][1]?' ['+safe(reg[b.ri][1])+']':''}</td><td>${safe(d.groups[reg[b.ri][2]])}</td><td><input type="checkbox" data-done="${b.n}" ${done[b.n]?'checked':''}></td></tr>`).join('');$('#stepMore').hidden=filtered.length<=shown;}
$('#stepHeight').oninput=()=>{shown=250;renderStep()};$('#stepSearch').oninput=()=>{shown=250;renderStep()};
$('#stepPrev').onclick=()=>{$('#stepHeight').value=Math.max(105,currentHeight()-1);shown=250;renderStep()};$('#stepNext').onclick=()=>{$('#stepHeight').value=Math.min(175,currentHeight()+1);shown=250;renderStep()};
document.querySelectorAll('[data-steph]').forEach(b=>b.onclick=()=>{$('#stepHeight').value=b.dataset.steph;shown=250;renderStep()});
$('#stepMore').onclick=()=>{shown+=250;renderStep()};
$('#stepRows').onchange=e=>{const id=e.target.dataset.done;if(id){if(e.target.checked)done[id]=true;else delete done[id];store('bt-r5-1-blocks',done);renderStep()}};
$('#stepLayerCsv').onclick=()=>{const y=currentHeight();csv('blackthorn-y-'+y+'.csv',[['Nummer','X','Y','Z','Block','Zustand','Gruppe','Fertig'],...(byY.get(y)||[]).map(b=>[b.n,b.x,b.y,b.z,reg[b.ri][0],reg[b.ri][1],d.groups[reg[b.ri][2]],done[b.n]?'ja':'nein'])]);};
renderStep();
})();
