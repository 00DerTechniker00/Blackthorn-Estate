export const $=s=>document.querySelector(s);
export const $$=s=>[...document.querySelectorAll(s)];
export const fmt=n=>Number(n||0).toLocaleString('de-DE');
export const clamp=(v,a,b)=>Math.max(a,Math.min(v,b));
export const key=(x,y,z)=>x+'|'+y+'|'+z;
export const escaped=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const blockStates=b=>Object.entries(b?.state||{}).map(([k,v])=>`${k}=${v}`).join(', ');
export const nameFor=(m,b)=>m.palette[b.block]?.name||b.block;
export const pack=n=>{const sh=Math.floor(n/1728),rest=n%1728,st=Math.floor(rest/64),rem=rest%64;return [sh,st,rem]};
export const packText=(n,stack=64)=>{const sh=Math.floor(n/(stack*27)),r=n%(stack*27),st=Math.floor(r/stack),rem=r%stack;return [sh?sh+' Shulker':'',st?st+' Stacks à '+stack:'',rem?rem+' einzeln':''].filter(Boolean).join(' + ')||'0'};
export function exportCSV(rows){return '\ufeff'+rows.map(row=>row.map(v=>'"'+String(v??'').replaceAll('"','""')+'"').join(';')).join('\r\n')}
export function download(filename,content,mime='text/csv;charset=utf-8'){const blob=new Blob([content],{type:mime});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000)}
export function point(e,canvas){const r=canvas.getBoundingClientRect();return {x:(e.clientX-r.left)*canvas.width/Math.max(r.width,1),y:(e.clientY-r.top)*canvas.height/Math.max(r.height,1),cssX:e.clientX-r.left,cssY:e.clientY-r.top}}
export function fitCanvas(canvas,aspect=1250/740){const w=Math.max(320,Math.min(1600,Math.round(canvas.getBoundingClientRect().width||1000)));const h=Math.round(w/aspect);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;return true}return false}
export async function load(){const m=window.__BLACKTHORN_BLUEPRINT__ || await (async()=>{const response=await fetch('blueprint.json',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status+' – blueprint.json nicht ladbar');return response.json()})();if(!Array.isArray(m.blocks)||!m.blocks.length||!m.palette||!Array.isArray(m.floors))throw Error('Blueprint hat ein ungültiges Format');
 const positions=new Set,byY=new Map,byGroup=new Map,byId=[null],counts={},groups={};let before=0;
 for(const b of m.blocks){if(!Number.isInteger(b.id)||b.id!==++before||![b.x,b.y,b.z].every(Number.isInteger)||typeof b.block!=='string'||!m.palette[b.block])throw Error('Ungültiger Block an Position '+before);
  const k=key(b.x,b.y,b.z);if(positions.has(k))throw Error('Doppelte Koordinaten: '+k);positions.add(k);
  if(!byY.has(b.y))byY.set(b.y,[]);byY.get(b.y).push(b);if(!byGroup.has(b.group))byGroup.set(b.group,[]);byGroup.get(b.group).push(b);
  byId.push(b);counts[b.block]=(counts[b.block]||0)+1;groups[b.group]=(groups[b.group]||0)+1;
 }
 m.byY=byY;m.byGroup=byGroup;m.byId=byId;m.counts=counts;m.groups=groups;m.total_blocks=m.blocks.length;
 m.index=new Map(m.blocks.map(b=>[key(b.x,b.y,b.z),b]));m.sortedY=[...byY.keys()].sort((a,b)=>a-b);
 m.floors.sort((a,b)=>a.y-b.y);m.storage_zones=m.storage_zones||[];
 m.bounds={minX:Math.min(...m.blocks.map(b=>b.x)),maxX:Math.max(...m.blocks.map(b=>b.x)),minZ:Math.min(...m.blocks.map(b=>b.z)),maxZ:Math.max(...m.blocks.map(b=>b.z)),minY:m.sortedY[0],maxY:m.sortedY.at(-1)};
 return m;
}
export function floorAt(m,y){return [...m.floors].reverse().find(f=>f.y<=y)?.y??m.floors[0].y}
export function visible(m,s){let a;if(s.displayMode==='all')a=m.blocks;else if(s.displayMode==='single')a=m.byY.get(s.layerY)||[];
 else if(s.displayMode==='below')a=m.blocks.filter(b=>b.y<=s.layerY);
 else {const next=m.floors.find(f=>f.y>s.floorY)?.y??m.bounds.maxY+1;a=m.blocks.filter(b=>b.y>=s.floorY&&b.y<next)}
 return s.group==='all'?a:a.filter(b=>b.group===s.group);
}
export function allAtHeight(m,y,phase='all',group='all',query='',remaining=false,progress=null){let a=m.byY.get(y)||[];
 if(phase!=='all')a=a.filter(b=>b.phase===Number(phase));
 if(group!=='all')a=a.filter(b=>b.group===group);
 if(query){let q=query.toLowerCase().trim().replace(/^#/,'');a=a.filter(b=>String(b.id).includes(q)||String(b.x).includes(q)||String(b.z).includes(q)||b.block.includes(q)||b.group.toLowerCase().includes(q))}
 if(remaining&&progress)a=a.filter(b=>!progress.has(b.id));
 return a;
}
export function countsFor(m,group){if(group==='all')return m.counts;const c={};for(const b of m.byGroup.get(group)||[])c[b.block]=(c[b.block]||0)+1;return c;}

export function materialItems(m,blockId,group='all'){
 const positions=group==='all'?m.counts[blockId]||0:(m.byGroup.get(group)||[]).filter(b=>b.block===blockId).length;
 let items=positions,itemId=blockId,stack=64,note='';
 if(blockId.endsWith('_door')){const list=group==='all'?m.blocks:(m.byGroup.get(group)||[]);items=list.filter(b=>b.block===blockId&&b.state?.half==='lower').length;note='Eine Tür = zwei Blockhälften'}
 if(blockId.endsWith('_bed')){const list=group==='all'?m.blocks:(m.byGroup.get(group)||[]);items=list.filter(b=>b.block===blockId&&b.state?.part==='foot').length;stack=1;note='Ein Bett = zwei Blockpositionen; nicht stapelbar'}
 if(blockId.endsWith('_wall_sign')){itemId=blockId.replace('_wall_sign','_sign');stack=16;note='Wandschild wird als normales Schild mitgeführt'}
 if(blockId==='water'){items=null;itemId='water_bucket';stack=1;note='Wasserblöcke werden aus wiederverwendbaren Wassereimern gesetzt; zwei Eimer für eine unendliche Quelle empfohlen'}
 return {positions,items,itemId,stack,note};
}

export function phaseStatus(model,progress){return model.build_phases.map((p,index)=>{const blocks=model.blocks.filter(b=>b.phase===p.id);const done=progress.count(blocks);const previous=model.build_phases.slice(0,index).map(q=>({id:q.id,name:q.name,blocks:model.blocks.filter(b=>b.phase===q.id)})).filter(q=>progress.count(q.blocks)!==q.blocks.length);return {...p,total:blocks.length,done,ratio:blocks.length?done/blocks.length:1,previous:previous.map(q=>q.name)};})}
