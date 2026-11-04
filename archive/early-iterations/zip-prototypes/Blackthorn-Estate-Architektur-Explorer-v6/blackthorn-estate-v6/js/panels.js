import { $,fmt,safe,units,formatUnits,states,blockName,makeCSV,download } from './utils.js';
const csvUnitRows=(model,entries,includeGroup=false)=>entries.map(([id,n,group])=>{const u=units(n);return includeGroup?[group,blockName(model,id),'minecraft:'+id,n,u.sh,u.st,u.rem]:[blockName(model,id),'minecraft:'+id,n,u.sh,u.st,u.rem]});
export function createPanels(model,store){
 let coordinateRows=model.blocks;
 function updateMaterials(){const s=store.get(),group=s.materialGroup,q=s.materialSearch.toLowerCase();const source=group==='all'?new Map(Object.entries(model.counts)):model.countsByGroup.get(group)||new Map;
  let rows=[...source].filter(([id])=>(id+' '+blockName(model,id)).toLowerCase().includes(q));
  rows.sort(s.materialSort==='name'?(a,b)=>blockName(model,a[0]).localeCompare(blockName(model,b[0])):(a,b)=>b[1]-a[1]);
  $('#materialRows').innerHTML=rows.map(([id,n])=>`<tr><td><span class="swatch" style="background:${model.palette[id]?.color||'#aaa'}"></span>${safe(blockName(model,id))}</td><td><code>minecraft:${safe(id)}</code></td><td>${fmt(n)}</td><td>${formatUnits(n)}</td></tr>`).join('');
  $('#materialsNotice').textContent=`${fmt(rows.reduce((n,r)=>n+r[1],0))} Positionen in der aktuellen Materialauswahl`;
 }
 function updateCoordinates(){const q=store.get().coordinateSearch.toLowerCase().replaceAll(',',' ').trim();const query=q.split(/\s+/).filter(Boolean);
  const matching=query.length?model.blocks.filter(b=>query.every(term=>[b.x,b.y,b.z,b.block,b.group,states(b)].join(' ').toLowerCase().includes(term))):model.blocks;
  coordinateRows=matching;$('#coordResult').textContent=fmt(matching.length)+' Treffer · max. 300 sichtbar';
  $('#coordRows').innerHTML=matching.slice(0,300).map(b=>`<tr data-x="${b.x}" data-y="${b.y}" data-z="${b.z}"><td>${b.x}</td><td>${b.y}</td><td>${b.z}</td><td>minecraft:${safe(b.block)}</td><td>${safe(b.group)}</td><td>${safe(states(b))}</td></tr>`).join('');
 }
 function updateProgress(){const s=store.get(),groups=Object.keys(model.groups),done=groups.filter(g=>s.progress[g]).length;
  $('#progressLabel').textContent=`${done} / ${groups.length} Baugruppen`;$('#progressBar').style.width=`${Math.round(done/groups.length*100)}%`;
 }
 function setSelected(){const b=store.get().selected;
  const message=b?`<b>${safe(blockName(model,b.block))}</b> · <code>minecraft:${safe(b.block)}</code><br>Weltkoordinaten <b>X=${b.x}, Y=${b.y}, Z=${b.z}</b> · Baugruppe ${safe(b.group)}<br>Blockstates: <code>${safe(states(b)||'keine hinterlegt')}</code>`:'Klicke auf einen Block, um Material, Weltkoordinaten und Blockstates zu untersuchen.';
  $('#selectedBlock').innerHTML=message;$('#planInfo').innerHTML=message;
 }
 const groups=Object.keys(model.groups).sort();$('#buildGroups').innerHTML=groups.map(g=>`<article class="build-group"><h3>${safe(g.replaceAll('_',' '))}</h3><small>${fmt(model.groups[g])} Blockpositionen</small><label><input type="checkbox" data-group="${safe(g)}" ${store.get().progress[g]?'checked':''}> Fertiggestellt</label></article>`).join('');
 $('#buildGroups').addEventListener('change',e=>{if(e.target.matches('input[data-group]'))store.toggleGroup(e.target.dataset.group,e.target.checked)});
 $('#coordRows').addEventListener('click',e=>{const r=e.target.closest('tr[data-x]');if(!r)return;const b=model.index.get([r.dataset.x,r.dataset.y,r.dataset.z].join('|'));if(b){store.patch({selected:b,planFloorY:store.floorAt(b.y),planLayerY:b.y});document.querySelector('.nav[data-view="plan"]').click();}});
 $('#downloadCsv').onclick=()=>download('blackthorn-v6-blockliste.csv',makeCSV([['X','Y','Z','Minecraft-ID','Baugruppe','Blockstates'],...model.blocks.map(b=>[b.x,b.y,b.z,'minecraft:'+b.block,b.group,states(b)])]));
 $('#downloadMaterials').onclick=()=>download('blackthorn-v6-materialbedarf.csv',makeCSV([['Material','Minecraft-ID','Anzahl','Shulkerboxen','Stacks danach','Einzelstücke'],...csvUnitRows(model,Object.entries(model.counts))]));
 $('#downloadGroupMaterials').onclick=()=>{const entries=[];for(const [g,items] of model.countsByGroup)for(const [id,n] of items)entries.push([id,n,g]);download('blackthorn-v6-materialbedarf-baugruppen.csv',makeCSV([['Baugruppe','Material','Minecraft-ID','Anzahl','Shulkerboxen','Stacks danach','Einzelstücke'],...csvUnitRows(model,entries,true)]))};
 $('#exportProgress').onclick=()=>download('blackthorn-v6-baufortschritt.json',JSON.stringify({release:'6.0',checked:store.get().progress,exportedAt:new Date().toISOString()},null,2),'application/json');
 store.subscribe((s,p,changed)=>{
  if(changed.some(x=>['materialGroup','materialSearch','materialSort'].includes(x)))updateMaterials();
  if(changed.includes('coordinateSearch'))updateCoordinates();
  if(changed.includes('selected'))setSelected();
  if(changed.includes('progress'))updateProgress();
 });
 updateMaterials();updateCoordinates();updateProgress();setSelected();
}
