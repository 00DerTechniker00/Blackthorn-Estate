
(() => {
'use strict';
const $=s=>document.querySelector(s);
const d=JSON.parse($('#data').textContent);
const zones=d.storage_zones;
const reg=d.reg, runs=d.runs, byY=new Map();
let n=0;
for(const [y,z,x,len,ri] of runs){let line=byY.get(y);if(!line){line=[];byY.set(y,line);}for(let k=0;k<len;k++){line.push({n:++n,key:`${x+k},${y},${z}`,x:x+k,y,z,ri});}}
const saved=(k,def)=>{try{return JSON.parse(localStorage.getItem(k))||def}catch{return def}};
const store=(k,val)=>{try{localStorage.setItem(k,JSON.stringify(val))}catch{}};
const inv=BT.state.inventory, done=BT.state.blocks;
const fmt=v=>Number(v).toLocaleString('de-DE');
const safe=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function csv(name,rows){const txt='\ufeff'+rows.map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(';')).join('\r\n');const blob=new Blob([txt],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),800)}
function jumpToRoom(zone){window.__focusPlan(zone.x[0],zone.y[0],zone.z[0]);}
function renderStorage(){const q=$('#storageQuery').value.toLowerCase();const rows=zones.filter(z=>(z.id+' '+z.name+' '+z.room+' '+z.contents).toLowerCase().includes(q));
      $('#storageSummary').textContent=rows.length+' von '+zones.length+' Lagerbuchten';
      $('#storageZones').innerHTML=rows.map(z=>`<tr><td><b>${safe(z.id)}</b></td><td><b>${safe(z.name)}</b><small class="cell-note">${safe(z.room)}</small></td><td><small>${safe(z.contents)}</small></td><td><input class="stock-note" type="text" maxlength="2000" aria-label="Bestandsnotiz ${safe(z.id)}" data-stock="${z.id}" value="${safe(inv[z.id]||'')}" placeholder="Bestand oder Notiz …"></td><td><button class="mini" data-jump="${z.id}">Im Plan</button></td></tr>`).join('')||'<tr><td colspan="5" class="empty-state">Keine passende Bucht. Suchbegriff ändern.</td></tr>';}

$('#storageQuery').addEventListener('input',renderStorage);
$('#storageZones').addEventListener('input',e=>{if(e.target.dataset.stock){inv[e.target.dataset.stock]=e.target.value;BT.save()}});
$('#storageZones').addEventListener('click',e=>{const id=e.target.dataset.jump;if(id){const z=zones.find(x=>x.id===id);if(z)jumpToRoom(z)}});
$('#storageExport').onclick=()=>csv('blackthorn-lagerplan.csv',[['Zone','Name','Raum','X von','X bis','Y von','Y bis','Z von','Z bis','Planinhalt','Ist-Bestand'],...zones.map(z=>[z.id,z.name,z.room,...z.x,...z.y,...z.z,z.contents,inv[z.id]||''])]);
$('#storageReset').onclick=()=>{if(confirm('Alle manuell eingegebenen Lagerbestände löschen?')){for(const k of Object.keys(inv))delete inv[k];BT.save();renderStorage()}};
renderStorage();
let shown=250;
const currentHeight=()=>+$('#stepHeight').value;
function renderStep(){const y=currentHeight(),list=byY.get(y)||[],q=$('#stepSearch').value.trim().toLowerCase();const filtered=q?list.filter(b=>(`${b.x} ${b.y} ${b.z} ${reg[b.ri][0]} ${d.groups[reg[b.ri][2]]}`).toLowerCase().includes(q)):list;
$('#stepLabel').textContent='Y = '+y;$('#stepSummary').textContent=fmt(filtered.length)+' Blockpositionen auf dieser Höhe'+(q?' (gefiltert)':'')+' · '+fmt(filtered.filter(b=>done[b.key]).length)+' abgehakt · Status wird nach XYZ gespeichert, Nummern gelten für Revision 5.16';
$('#stepRows').innerHTML=filtered.slice(0,shown).map(b=>`<tr title="Block #${b.n} bei X=${b.x}, Y=${b.y}, Z=${b.z}"><td>#${b.n}</td><td>${b.x}</td><td>${b.y}</td><td>${b.z}</td><td>minecraft:${safe(reg[b.ri][0])}${reg[b.ri][1]?' ['+safe(reg[b.ri][1])+']':''}</td><td>${safe(d.groups[reg[b.ri][2]])}</td><td><input type="checkbox" data-done="${b.key}" ${done[b.key]?'checked':''}></td></tr>`).join('');$('#stepMore').hidden=filtered.length<=shown;}
$('#stepHeight').oninput=()=>{shown=250;renderStep()};$('#stepSearch').oninput=()=>{shown=250;renderStep()};
$('#stepPrev').onclick=()=>{$('#stepHeight').value=Math.max(105,currentHeight()-1);shown=250;renderStep()};$('#stepNext').onclick=()=>{$('#stepHeight').value=Math.min(157,currentHeight()+1);shown=250;renderStep()};
document.querySelectorAll('[data-steph]').forEach(b=>b.onclick=()=>{$('#stepHeight').value=b.dataset.steph;shown=250;renderStep()});
$('#stepMore').onclick=()=>{shown+=250;renderStep()};
$('#stepRows').onchange=e=>{const id=e.target.dataset.done;if(id){if(e.target.checked)done[id]=true;else delete done[id];BT.save();renderStep()}};
$('#stepLayerCsv').onclick=()=>{const y=currentHeight();csv('blackthorn-y-'+y+'.csv',[['Nummer','X','Y','Z','Block','Zustand','Gruppe','Fertig'],...(byY.get(y)||[]).map(b=>[b.n,b.x,b.y,b.z,reg[b.ri][0],reg[b.ri][1],d.groups[reg[b.ri][2]],done[b.key]?'ja':'nein'])]);};
renderStep();
window.addEventListener('bt:import',()=>{renderStep();renderStorage();});
})();
