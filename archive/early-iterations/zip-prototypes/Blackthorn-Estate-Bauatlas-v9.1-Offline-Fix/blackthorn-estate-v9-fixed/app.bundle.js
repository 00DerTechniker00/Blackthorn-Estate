"use strict";
// --- model ---
const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const fmt=n=>Number(n||0).toLocaleString('de-DE');
const clamp=(v,a,b)=>Math.max(a,Math.min(v,b));
const key=(x,y,z)=>x+'|'+y+'|'+z;
const escaped=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const blockStates=b=>Object.entries(b?.state||{}).map(([k,v])=>`${k}=${v}`).join(', ');
const nameFor=(m,b)=>m.palette[b.block]?.name||b.block;
const pack=n=>{const sh=Math.floor(n/1728),rest=n%1728,st=Math.floor(rest/64),rem=rest%64;return [sh,st,rem]};
const packText=(n,stack=64)=>{const sh=Math.floor(n/(stack*27)),r=n%(stack*27),st=Math.floor(r/stack),rem=r%stack;return [sh?sh+' Shulker':'',st?st+' Stacks à '+stack:'',rem?rem+' einzeln':''].filter(Boolean).join(' + ')||'0'};
function exportCSV(rows){return '\ufeff'+rows.map(row=>row.map(v=>'"'+String(v??'').replaceAll('"','""')+'"').join(';')).join('\r\n')}
function download(filename,content,mime='text/csv;charset=utf-8'){const blob=new Blob([content],{type:mime});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000)}
function point(e,canvas){const r=canvas.getBoundingClientRect();return {x:(e.clientX-r.left)*canvas.width/Math.max(r.width,1),y:(e.clientY-r.top)*canvas.height/Math.max(r.height,1),cssX:e.clientX-r.left,cssY:e.clientY-r.top}}
function fitCanvas(canvas,aspect=1250/740){const w=Math.max(320,Math.min(1600,Math.round(canvas.getBoundingClientRect().width||1000)));const h=Math.round(w/aspect);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;return true}return false}
async function load(){const m=window.__BLACKTHORN_BLUEPRINT__ || await (async()=>{const response=await fetch('blueprint.json',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status+' – blueprint.json nicht ladbar');return response.json()})();if(!Array.isArray(m.blocks)||!m.blocks.length||!m.palette||!Array.isArray(m.floors))throw Error('Blueprint hat ein ungültiges Format');
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
function floorAt(m,y){return [...m.floors].reverse().find(f=>f.y<=y)?.y??m.floors[0].y}
function visible(m,s){let a;if(s.displayMode==='all')a=m.blocks;else if(s.displayMode==='single')a=m.byY.get(s.layerY)||[];
 else if(s.displayMode==='below')a=m.blocks.filter(b=>b.y<=s.layerY);
 else {const next=m.floors.find(f=>f.y>s.floorY)?.y??m.bounds.maxY+1;a=m.blocks.filter(b=>b.y>=s.floorY&&b.y<next)}
 return s.group==='all'?a:a.filter(b=>b.group===s.group);
}
function allAtHeight(m,y,phase='all',group='all',query='',remaining=false,progress=null){let a=m.byY.get(y)||[];
 if(phase!=='all')a=a.filter(b=>b.phase===Number(phase));
 if(group!=='all')a=a.filter(b=>b.group===group);
 if(query){let q=query.toLowerCase().trim().replace(/^#/,'');a=a.filter(b=>String(b.id).includes(q)||String(b.x).includes(q)||String(b.z).includes(q)||b.block.includes(q)||b.group.toLowerCase().includes(q))}
 if(remaining&&progress)a=a.filter(b=>!progress.has(b.id));
 return a;
}
function countsFor(m,group){if(group==='all')return m.counts;const c={};for(const b of m.byGroup.get(group)||[])c[b.block]=(c[b.block]||0)+1;return c;}

function materialItems(m,blockId,group='all'){
 const positions=group==='all'?m.counts[blockId]||0:(m.byGroup.get(group)||[]).filter(b=>b.block===blockId).length;
 let items=positions,itemId=blockId,stack=64,note='';
 if(blockId.endsWith('_door')){const list=group==='all'?m.blocks:(m.byGroup.get(group)||[]);items=list.filter(b=>b.block===blockId&&b.state?.half==='lower').length;note='Eine Tür = zwei Blockhälften'}
 if(blockId.endsWith('_bed')){const list=group==='all'?m.blocks:(m.byGroup.get(group)||[]);items=list.filter(b=>b.block===blockId&&b.state?.part==='foot').length;stack=1;note='Ein Bett = zwei Blockpositionen; nicht stapelbar'}
 if(blockId.endsWith('_wall_sign')){itemId=blockId.replace('_wall_sign','_sign');stack=16;note='Wandschild wird als normales Schild mitgeführt'}
 if(blockId==='water'){items=null;itemId='water_bucket';stack=1;note='Wasserblöcke werden aus wiederverwendbaren Wassereimern gesetzt; zwei Eimer für eine unendliche Quelle empfohlen'}
 return {positions,items,itemId,stack,note};
}

function phaseStatus(model,progress){return model.build_phases.map((p,index)=>{const blocks=model.blocks.filter(b=>b.phase===p.id);const done=progress.count(blocks);const previous=model.build_phases.slice(0,index).map(q=>({id:q.id,name:q.name,blocks:model.blocks.filter(b=>b.phase===q.id)})).filter(q=>progress.count(q.blocks)!==q.blocks.length);return {...p,total:blocks.length,done,ratio:blocks.length?done/blocks.length:1,previous:previous.map(q=>q.name)};})}

// --- progress ---

class Progress{
 constructor(n){this.n=n;this.bytes=new Uint8Array(Math.ceil(n/8));this.name='blackthorn-v7-bits-'+n;try{const s=localStorage.getItem(this.name);if(s){const raw=atob(s);for(let i=0;i<Math.min(raw.length,this.bytes.length);i++)this.bytes[i]=raw.charCodeAt(i)}}catch(e){console.warn('Fortschritt konnte nicht geladen werden',e)}}
 has(id){if(!id||id>this.n)return false;const i=id-1;return !!(this.bytes[i>>3]&(1<<(i&7)))}
 set(id,v){if(!id||id>this.n)return;const i=id-1;if(v)this.bytes[i>>3]|=1<<(i&7);else this.bytes[i>>3]&=~(1<<(i&7));this.save()}
 count(ids){let n=0;for(const b of ids)if(this.has(typeof b==='object'?b.id:b))n++;return n}
 get total(){let n=0;for(const v of this.bytes){let k=v;while(k){k&=k-1;n++}}return n}
 save(){try{let s='';for(const c of this.bytes)s+=String.fromCharCode(c);localStorage.setItem(this.name,btoa(s))}catch(e){console.warn('Fortschritt konnte nicht gespeichert werden',e)}}
 clear(){this.bytes.fill(0);this.save()}
 importIds(ids){if(!Array.isArray(ids))throw Error("Ungültige Fortschrittsliste");this.bytes.fill(0);for(const id of ids){if(Number.isInteger(id)&&id>0&&id<=this.n){const i=id-1;this.bytes[i>>3]|=1<<(i&7)}}this.save()}
 export(){download('Blackthorn-Baufortschritt-v7.json',JSON.stringify({version:'7.0',totalBlocks:this.n,completed:this.total,completedIds:Array.from({length:this.n},(_,i)=>i+1).filter(id=>this.has(id))},null,2),'application/json')}
}

// --- inventory ---

class Inventory{
 constructor(model){this.model=model;this.key='blackthorn-v9-stock-'+model.total_blocks;try{this.data=JSON.parse(localStorage.getItem(this.key)||'{}')}catch{this.data={}}}
 get(item){return Number.isSafeInteger(this.data[item])&&this.data[item]>=0?this.data[item]:0}
 set(item,n){if(!Number.isSafeInteger(n)||n<0)throw Error('Vorrat muss eine nichtnegative ganze Zahl sein');this.data[item]=n;this.save()}
 save(){localStorage.setItem(this.key,JSON.stringify(this.data))}
 reset(){this.data={};this.save()}
 import(obj){if(!obj||obj.blueprintBlocks!==this.model.total_blocks||typeof obj.stock!=='object'||Array.isArray(obj.stock))throw Error('Vorratsdatei passt nicht zum Bauplan');const clean={};for(const [k,v] of Object.entries(obj.stock)){if(!/^[a-z0-9_]+$/.test(k)||!Number.isSafeInteger(v)||v<0)throw Error('Ungültiger Bestand für '+k);clean[k]=v}this.data=clean;this.save()}
 export(){download('Blackthorn-Vorrat-v9.json',JSON.stringify({version:9,blueprintBlocks:this.model.total_blocks,stock:this.data},null,2),'application/json')}
 needed(itemId,progress){let total=0;const m=this.model;for(const id of Object.keys(m.counts)){const config=materialItems(m,id);if(config.itemId!==itemId||config.items===null)continue;for(const b of m.blocks){if(b.block!==id||progress.has(b.id))continue;if(id.endsWith('_door')&&b.state?.half!=='lower')continue;if(id.endsWith('_bed')&&b.state?.part!=='foot')continue;total++}}
 return total}
 requirements(progress,group='all'){const m=this.model,byItem=new Map();const blocks=group==='all'?m.blocks:m.byGroup.get(group)||[];for(const b of blocks){if(progress.has(b.id))continue;const config=materialItems(m,b.block,group);if(config.items===null)continue;if(b.block.endsWith('_door')&&b.state?.half!=='lower')continue;if(b.block.endsWith('_bed')&&b.state?.part!=='foot')continue;byItem.set(config.itemId,(byItem.get(config.itemId)||0)+1)}return byItem}
 shortfall(progress,group='all'){const req=this.requirements(progress,group);return [...req].map(([item,needed])=>({item,needed,stock:this.get(item),missing:Math.max(0,needed-this.get(item))}))}
}

// --- view3d ---

const C={x0:0,x1:1,y0:0,y1:1,z0:0,z1:1};
const NOT_FULL=/(stairs|slab|door|pane|fence|wall|carpet|bed|sign|chain|lantern|torch|water|hopper|flower_pot|anvil|chest|barrel|table|stand|bookshelf|cauldron|loom|composter|lectern|grindstone|stonecutter)$/;
function solid(b){return !!b&&!NOT_FULL.test(b.block)}
function blocksOf(b){const n=b.block,st=b.state||{};
 if(n.endsWith('_slab'))return [{...C,y0:st.type==='top'?.5:0,y1:st.type==='top'?1:.5}];
 if(n.endsWith('_stairs')){const u=st.half==='top',a={...C,y0:u?0:.5,y1:u?.5:1};const f=st.facing||'north';if(f==='north')a.z1=.5;else if(f==='south')a.z0=.5;else if(f==='west')a.x1=.5;else a.x0=.5;return [{...C,y0:u?.5:0,y1:u?1:.5},a]}
 if(n.endsWith('_door')){const f=st.facing||'north';return [f==='north'||f==='south'?{...C,z0:.43,z1:.57}:{...C,x0:.43,x1:.57}]}
 if(n.endsWith('_pane')||n==='iron_bars')return [{...C,x0:.42,x1:.58},{...C,z0:.42,z1:.58}];
 if(n.endsWith('_fence')||n.endsWith('_wall')||n==='chain')return [{...C,x0:.35,x1:.65,z0:.35,z1:.65}];
 if(n==='lantern'||n==='soul_lantern')return [{...C,x0:.22,x1:.78,y1:.69,z0:.22,z1:.78}];
 if(n==='torch')return [{...C,x0:.42,x1:.58,y1:.8,z0:.42,z1:.58}];
 if(n.endsWith('_carpet'))return [{...C,y1:.07}];
 if(n.endsWith('_bed'))return [{...C,y1:.55}];
 if(n==='chest'||n==='trapped_chest'||n==='ender_chest')return [{...C,x0:.06,x1:.94,z0:.06,z1:.94,y1:.87}];
 if(n==='barrel')return [{...C,x0:.03,x1:.97,z0:.03,z1:.97}];
 if(n.endsWith('_sign'))return [{...C,x0:.38,x1:.62,y0:.35,y1:.9,z0:.38,z1:.62}];
 if(n==='flower_pot')return [{...C,x0:.3,x1:.7,z0:.3,z1:.7,y1:.4}];
 if(n==='water')return [{...C,y1:.9}];
 return [C];
}
function clr(hex,n){const v=parseInt((hex||'#888888').slice(1),16)||0;return `rgb(${Math.min(255,(v>>16&255)*n)|0},${Math.min(255,(v>>8&255)*n)|0},${Math.min(255,(v&255)*n)|0})`}
function idRGB(id){return `rgb(${id&255},${id>>8&255},${id>>16&255})`}
function makeVoxelViewer(canvas,model,getState){
 const ctx=canvas.getContext('2d',{alpha:false}),hit=document.createElement('canvas'),hitCtx=hit.getContext('2d',{willReadFrequently:true});
 let requestId=0,last=[];let hover=null;const byId=model.byId;let cacheSignature='',cache=[];
 function request(){if(requestId)return;requestId=requestAnimationFrame(()=>{requestId=0;draw()})}
 function draw(){if(canvas.offsetParent===null)return;fitCanvas(canvas);if(hit.width!==canvas.width||hit.height!==canvas.height){hit.width=canvas.width;hit.height=canvas.height}
  const w=canvas.width,h=canvas.height,s=getState();ctx.fillStyle='#101a15';ctx.fillRect(0,0,w,h);hitCtx.clearRect(0,0,w,h);last=[];
  let signature=[s.displayMode,s.floorY,s.layerY,s.group].join('/');if(signature!==cacheSignature){cacheSignature=signature;cache=visible(model,s)}let blocks=cache;
  const tag=document.querySelector('#visibleCount');if(tag)tag.textContent=fmt(blocks.length)+' Blöcke';if(!blocks.length)return;
  let minX=Infinity,minY=Infinity,minZ=Infinity,maxX=-Infinity,maxY=-Infinity,maxZ=-Infinity;
  for(const b of blocks){if(b.x<minX)minX=b.x;if(b.x>maxX)maxX=b.x;if(b.y<minY)minY=b.y;if(b.y>maxY)maxY=b.y;if(b.z<minZ)minZ=b.z;if(b.z>maxZ)maxZ=b.z}
  const cos=Math.cos(s.yaw),sin=Math.sin(s.yaw),top=s.renderMode==='top';
  const raw=(x,y,z)=>{let a=x-minX,v=y-minY,c=z-minZ;return top?[a,c]:[a*cos-c*sin,(a*sin+c*cos)*.62-v*.95]};
  let u0=Infinity,u1=-Infinity,v0=Infinity,v1=-Infinity;
  for(const x of [minX,maxX+1])for(const z of [minZ,maxZ+1])for(const y of [minY,maxY+1]){let [u,v]=raw(x,y,z);u0=Math.min(u0,u);u1=Math.max(u1,u);v0=Math.min(v0,v);v1=Math.max(v1,v)}
  const scale=Math.max(.4,Math.min((w-75)/(u1-u0||1),(h-85)/(v1-v0||1))*s.zoom),centerU=(u0+u1)/2,centerV=(v0+v1)/2;
  const P=(x,y,z)=>{const [u,v]=raw(x,y,z);return [(u-centerU)*scale+w/2+s.panX,(v-centerV)*scale+h/2+s.panY]};
  // Surveyed terrain only: never extrapolate beyond actual recorded height samples.
  // Terrain is a contextual, optional background, not an invented Minecraft world.
  if(s.showTerrain && !top && s.displayMode==='all'){
   const [tx0,tx1,tz0,tz1]=model.terrain.bounds,H=model.terrain.heights;
   const step=s.zoom>2?1:2;
   const paths=[];
   for(let z=tz0;z<tz1;z+=step)for(let x=tx0;x<tx1;x+=step){
    const h00=H[z-tz0][x-tx0],h10=H[z-tz0][Math.min(x+step,tx1)-tx0],h11=H[Math.min(z+step,tz1)-tz0][Math.min(x+step,tx1)-tx0],h01=H[Math.min(z+step,tz1)-tz0][x-tx0];
    const pts=[P(x,h00+1,z),P(x+step,h10+1,z),P(x+step,h11+1,z+step),P(x,h01+1,z+step)];
    const steep=Math.max(Math.abs(h00-h11),Math.abs(h10-h01));
    const avg=(h00+h10+h11+h01)/4;
    const clr=steep>=5?'#69756c':avg<104?'#526450':avg<121?'#617e58':'#648459';
    paths.push({pts,clr,depth:(x-minX)*sin+(z-minZ)*cos});
   }
   paths.sort((a,b)=>a.depth-b.depth);
   for(const p of paths){ctx.beginPath();ctx.moveTo(...p.pts[0]);for(let i=1;i<4;i++)ctx.lineTo(...p.pts[i]);ctx.closePath();ctx.fillStyle=p.clr;ctx.fill()}
  }
  const occupied=new Map(blocks.map(b=>[key(b.x,b.y,b.z),b]));
  const col={};for(const [bid,pal] of Object.entries(model.palette))col[bid]=[clr(pal.color,1.16),clr(pal.color,.72),clr(pal.color,.9)];
  const ordered=blocks.slice().sort((a,b)=>(a.x-b.x)*sin+(a.z-b.z)*cos+(a.y-b.y)*.01||a.y-b.y);
  const labelCandidates=[];
  function face(b,coords,ci,topface=false){const poly=coords.map(q=>P(b.x+q[0],b.y+q[1],b.z+q[2]));const xx=poly.map(p=>p[0]),yy=poly.map(p=>p[1]);if(Math.max(...xx)<0||Math.min(...xx)>w||Math.max(...yy)<0||Math.min(...yy)>h)return;
   for(const [context,fill] of [[ctx,(col[b.block]||['#aaa','#777','#999'])[ci]],[hitCtx,idRGB(b.id)]]){
    context.beginPath();context.moveTo(poly[0][0],poly[0][1]);for(let i=1;i<poly.length;i++)context.lineTo(poly[i][0],poly[i][1]);context.closePath();context.fillStyle=fill;context.fill();
   }
   if(scale>10 && /deepslate|stone_bricks|planks|log|tiles/.test(b.block)){
    ctx.save();ctx.beginPath();ctx.moveTo(poly[0][0],poly[0][1]);for(let i=1;i<poly.length;i++)ctx.lineTo(poly[i][0],poly[i][1]);ctx.closePath();ctx.clip();
    const mnx=Math.min(...xx),mxx=Math.max(...xx),mny=Math.min(...yy),mxy=Math.max(...yy);
    const size=Math.max(3,Math.min(13,scale/2.8));ctx.strokeStyle=/planks|log/.test(b.block)?'#271b1444':'#0b131a44';ctx.lineWidth=.85;
    for(let yy=mny;yy<=mxy+size;yy+=size){ctx.beginPath();ctx.moveTo(mnx,yy);ctx.lineTo(mxx,yy);ctx.stroke()}
    for(let rr=0,yy=mny;yy<mxy+size;rr++,yy+=size){for(let xx=mnx+(rr%2)*size;xx<mxx+size;xx+=2*size){ctx.beginPath();ctx.moveTo(xx,yy);ctx.lineTo(xx,yy+size);ctx.stroke()}}
    ctx.restore();
   }
   if(scale>13){ctx.lineWidth=.65;ctx.strokeStyle='#050c0c75';ctx.stroke()}
   if(s.selectedId===b.id){ctx.lineWidth=Math.max(2,scale*.085);ctx.strokeStyle='#ffe08c';ctx.stroke()}
   if(topface&&s.showNumbers&&scale>17&&blocks.length<14000){const t=P(b.x+.5,b.y+1,b.z+.5);labelCandidates.push([t[0],t[1],b.id])}
  }
  if(top){const highest=new Map;for(const b of blocks){let q=b.x+'|'+b.z,prior=highest.get(q);if(!prior||prior.y<b.y)highest.set(q,b)}
   for(const b of highest.values())face(b,[[0,1,0],[1,1,0],[1,1,1],[0,1,1]],0,true);
  }else{
   const plusX=sin>0,plusZ=cos>0;
   for(const b of ordered){const x=b.x,y=b.y,z=b.z,partial=!solid(b);for(const a of blocksOf(b)){
    const onX=plusX?a.x1:a.x0,neighborX=occupied.get(key(x+(plusX?1:-1),y,z));
    if(!(plusX?a.x1===1:a.x0===0)||!solid(neighborX))face(b,[[onX,a.y0,a.z0],[onX,a.y0,a.z1],[onX,a.y1,a.z1],[onX,a.y1,a.z0]],1);
    const onZ=plusZ?a.z1:a.z0,neighborZ=occupied.get(key(x,y,z+(plusZ?1:-1)));
    if(!(plusZ?a.z1===1:a.z0===0)||!solid(neighborZ))face(b,[[a.x0,a.y0,onZ],[a.x1,a.y0,onZ],[a.x1,a.y1,onZ],[a.x0,a.y1,onZ]],2);
    if(a.y1!==1||!solid(occupied.get(key(x,y+1,z)))||partial)face(b,[[a.x0,a.y1,a.z0],[a.x1,a.y1,a.z0],[a.x1,a.y1,a.z1],[a.x0,a.y1,a.z1]],0,true);
   }}
  }
  if(s.showNumbers&&scale>17&&blocks.length<14000){ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`bold ${Math.min(17,Math.max(9,scale*.55))}px ui-monospace,monospace`;for(const [x,y,id] of labelCandidates){if(x<12||x>w-12||y<12||y>h-12)continue;ctx.lineWidth=2.6;ctx.strokeStyle='#101710e6';ctx.strokeText(String(id),x,y);ctx.fillStyle='#fff7da';ctx.fillText(String(id),x,y)}ctx.textAlign='left';ctx.textBaseline='alphabetic'}
  ctx.fillStyle='#f4ddb1';ctx.font='600 12px system-ui';ctx.fillText(top?'DRAUFSICHT':'BLOCKGENAUE 3D-VOXELANSICHT',17,23);
  if(s.showTerrain&&s.displayMode==='all'){ctx.fillStyle='#f0d9a5';ctx.font='11px system-ui';ctx.fillText('GELÄNDE: reale Höhe X −780…−645 · östlicher Rand nicht vermessen',17,61)}
  ctx.fillStyle='#b0bdac';ctx.font='11px system-ui';ctx.fillText(`Y ${s.displayMode==='all'?'gesamt':s.displayMode==='single'?s.layerY:s.displayMode==='below'?'≤'+s.layerY:s.floorY+' +'} · ${fmt(blocks.length)} Positionen${scale<17?' · Für Nummern näher zoomen':''}`,17,42);
 }
 function pick(e){const p=point(e,canvas),x=Math.floor(p.x),y=Math.floor(p.y);if(x<0||x>=hit.width||y<0||y>=hit.height)return null;
  const v=hitCtx.getImageData(x,y,1,1).data,id=v[0]+(v[1]<<8)+(v[2]<<16);return v[3]?byId[id]||null:null}
 return {request,pick,draw};
}

// --- plan2d ---

function makePlan2D(canvas,m,getState){
 const ctx=canvas.getContext('2d',{alpha:false});let requestId=0,lastGeom=null,tiles=new Map;
 const box=m.site.bounds,nx=box.maxX-box.minX+1,nz=box.maxZ-box.minZ+1;
 function request(){if(requestId)return;requestId=requestAnimationFrame(()=>{requestId=0;draw()})}
 function floorRange(s){if(s.planMode==='layer')return [s.planY,s.planY];const next=m.floors.find(f=>f.y>s.planFloor)?.y??m.bounds.maxY+1;return [s.planFloor,Math.min(s.planFloor+7,next-1)]}
 function geom(){const s=getState(),w=canvas.width,h=canvas.height,unit=Math.min((w-95)/nx,(h-96)/nz)*s.planZoom;return {unit,x:x=>w/2+s.planPanX+(x-box.minX-nx/2)*unit,z:z=>h/2+s.planPanY+(z-box.minZ-nz/2)*unit}}
 function draw(){if(canvas.offsetParent===null)return;fitCanvas(canvas,1250/800);const w=canvas.width,h=canvas.height,s=getState();ctx.fillStyle='#101b17';ctx.fillRect(0,0,w,h);const g=geom();lastGeom=g;tiles=new Map;
  const [a,b]=floorRange(s);for(let y=a;y<=b;y++){for(const bl of m.byY.get(y)||[]){if(s.planGroup!=='all'&&s.planGroup!==bl.group)continue;tiles.set(bl.x+'|'+bl.z,bl)}}
  for(const bl of tiles.values()){const xx=g.x(bl.x),zz=g.z(bl.z),sz=g.unit;if(xx+sz<0||xx>w||zz+sz<0||zz>h)continue;
   ctx.fillStyle=m.palette[bl.block]?.color||'#8e9188';ctx.fillRect(xx,zz,sz+.18,sz+.18);
   if(s.selectedId===bl.id){ctx.strokeStyle='#fce18c';ctx.lineWidth=Math.max(2,sz*.1);ctx.strokeRect(xx,zz,sz,sz)}
   if(s.planNumbers&&sz>19){ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`bold ${Math.min(14,sz*.6)}px ui-monospace,monospace`;ctx.strokeStyle='#102018f0';ctx.lineWidth=2.8;ctx.strokeText(String(bl.id),xx+sz*.5,zz+sz*.5);ctx.fillStyle='#fff4d5';ctx.fillText(String(bl.id),xx+sz*.5,zz+sz*.5)}
  }
  if(g.unit>6){ctx.beginPath();ctx.strokeStyle='#e9e7df25';ctx.lineWidth=.7;for(let x=box.minX;x<=box.maxX+1;x++){let px=g.x(x);if(px<0||px>w)continue;ctx.moveTo(px,Math.max(0,g.z(box.minZ)));ctx.lineTo(px,Math.min(h,g.z(box.maxZ+1)))}for(let z=box.minZ;z<=box.maxZ+1;z++){let pz=g.z(z);if(pz<0||pz>h)continue;ctx.moveTo(Math.max(0,g.x(box.minX)),pz);ctx.lineTo(Math.min(w,g.x(box.maxX+1)),pz)}ctx.stroke()}
  ctx.textAlign='left';ctx.textBaseline='alphabetic';ctx.font='600 13px system-ui';ctx.fillStyle='#e9d6ad';ctx.fillText(`2D-GRUNDRISS · Y=${a}${a!==b?'–'+b:''} · ${fmt(tiles.size)} Positionen`,18,25);
  ctx.font='11px system-ui';ctx.fillStyle='#b2c0b0';ctx.fillText('OSTEN → (X steigt) · SÜDEN ↓ (Z steigt)',18,44);
  if(s.planNumbers&&g.unit<=19){ctx.fillStyle='#b2bca8';ctx.fillText('Für Blocknummern weiter hineinzoomen',18,61)}
  if(s.showMarkers){const fs=[...m.storage_zones.map(t=>({type:'zone',x:t.center.x,z:t.center.z,y:t.floorY+1,name:t.name})),...(m.features||[]).filter(t=>t.type==='stair')];
   for(const f of fs){if(f.y<a||f.y>b)continue;const x=g.x(f.x+.5),y=g.z(f.z+.5);if(x<0||x>w||y<0||y>h)continue;
    const text=f.type==='stair'?'↗ Treppe':f.name;if(g.unit>8){ctx.font='bold 10px system-ui';let tw=ctx.measureText(text).width;ctx.fillStyle='#16231cd9';ctx.fillRect(x-tw/2-5,y-14,tw+10,20);ctx.fillStyle='#ffe1a5';ctx.textAlign='center';ctx.fillText(text,x,y);ctx.textAlign='left'}}}
 }
 function pick(e){if(!lastGeom)return null;const s=getState(),p=point(e,canvas),x=Math.floor((p.x-canvas.width/2-s.planPanX)/lastGeom.unit+nx/2+box.minX),z=Math.floor((p.y-canvas.height/2-s.planPanY)/lastGeom.unit+nz/2+box.minZ),b=tiles.get(x+'|'+z)||null;return {x,z,block:b}}
 function center(x,z,zoom){const s=getState();if(zoom!=null)s.planZoom=zoom;const unit=Math.min((canvas.width-95)/nx,(canvas.height-96)/nz)*s.planZoom;s.planPanX=-(x-box.minX-nx/2)*unit;s.planPanY=-(z-box.minZ-nz/2)*unit;request()}
 return {request,pick,center,draw};
}

// --- main ---





const S={view:'overview',displayMode:'floor',floorY:129,layerY:129,renderMode:'3d',group:'all',yaw:-.71,zoom:1,panX:0,panY:0,showNumbers:true,showTerrain:false,
 planFloor:129,planY:130,planMode:'layer',planGroup:'all',planZoom:1,planPanX:0,planPanY:0,planNumbers:true,showMarkers:true,selectedId:0};
let m,progress,inventory,viewer,plan,guideY=93,guidePage=0,guidePhase='all',guideGroup='all',guideSearch='',guideRemaining=false,guideList=[];
const PAGE=60;
const safeOpt=(v,label)=>`<option value="${escaped(v)}">${escaped(label)}</option>`;
function showError(e){console.error(e);const el=$('#errorBanner');el.hidden=false;el.textContent='Fehler beim Laden der Website: '+e.message+' — Bitte die ZIP vollständig entpacken und start.sh bzw. start.bat verwenden.';$('#loadState').textContent='Fehler beim Laden'}
function showView(id){S.view=id;$$('.view').forEach(e=>e.classList.toggle('active',e.id===id));$$('.nav').forEach(e=>e.classList.toggle('active',e.dataset.view===id));window.scrollTo({top:0,behavior:'instant'});if(id==='viewer')viewer.request();if(id==='plan')plan.request();if(id==='build')renderGuide();if(id==='storage')renderStorage();if(id==='materials')renderMaterials()}
function setSelection(bl){if(!bl)return;S.selectedId=bl.id;const text=`<div class="selectedmeta"><strong>Block #${fmt(bl.id)}</strong><br>${escaped(nameFor(m,bl))} · <code>minecraft:${escaped(bl.block)}</code><br>Koordinaten: <strong>X=${bl.x} · Y=${bl.y} · Z=${bl.z}</strong><br>Baugruppe: ${escaped(bl.group)} · ${escaped(m.build_phases[bl.phase]?.name||'')}<br>Blockstates: ${escaped(blockStates(bl)||'keine')}</div>`;
 $('#selectedBlock').innerHTML=text;$('#planInfo').innerHTML=text;
 if(S.view==='viewer')viewer.request();if(S.view==='plan')plan.request();
}
function makeTooltip(el,info,e){if(!info){el.hidden=true;return}const p=point(e,e.target),r=e.target.getBoundingClientRect();el.innerHTML=`<strong>#${fmt(info.id)} · ${escaped(nameFor(m,info))}</strong><br>X=${info.x}, Y=${info.y}, Z=${info.z}<br>${escaped(info.group)}${info.zone?' · '+escaped(info.zone):''}`;el.hidden=false;
 let x=p.cssX+15,y=p.cssY+16;let maxX=r.width-260;if(x>maxX)x=Math.max(8,p.cssX-255);el.style.left=x+'px';el.style.top=y+'px'}
function sync3d(){ $('#layerLabel').textContent='Y = '+S.layerY;$('#layerRange').value=S.layerY;$('#floorSelect').value=S.floorY;$('#displayMode').value=S.displayMode;$('#groupFilter').value=S.group;$('#showNumbers').checked=S.showNumbers;$('#showTerrain').checked=S.showTerrain;viewer.request()}
function sync2d(){ $('#planLayerLabel').textContent=S.planY;$('#planLayer').value=S.planY;$('#planFloor').value=S.planFloor;$('#planMode').value=S.planMode;$('#planGroup').value=S.planGroup;$('#planNumbers').checked=S.planNumbers;plan.request()}
function syncGuideY(y){const list=m.sortedY;guideY=list.reduce((p,c)=>Math.abs(c-y)<Math.abs(p-y)?c:p,list[0]);guidePage=0;$('#guideY').value=guideY;$('#guideRange').value=guideY;renderGuide()}
function placementHint(bl){
 if(bl.block.endsWith('_door')&&bl.state?.half==='upper')return 'Wird beim Setzen der unteren Türhälfte automatisch erzeugt.';
 if(bl.block.endsWith('_bed')&&bl.state?.part==='head')return 'Entsteht beim Platzieren des Bettes (Fußteil).';
 if(bl.block==='water')return 'Wasser mit Eimer / unendlicher Quelle einfüllen.';
 if(bl.block.endsWith('_wall_sign'))return 'Schild mit Lagerzone beschriften (siehe Lager & Räume).';
 if(bl.block.endsWith('_stairs')&&bl.state?.facing)return 'Treppenausrichtung: '+bl.state.facing;
 return '';
}
function renderPhases(){const phases=phaseStatus(m,progress);$('#phaseRows').innerHTML=phases.map(p=>`<div class="phasebox"><small>PHASE ${p.id+1}</small><strong>${escaped(p.name)}</strong><div class="mini"><span style="width:${Math.round(100*p.ratio)}%"></span></div><small>${fmt(p.done)} / ${fmt(p.total)} · ${Math.round(100*p.ratio)} %</small>${p.done&&p.previous.length?`<p class="warning-text">⚠ Vorher offen: ${escaped(p.previous.join(', '))}</p>`:''}</div>`).join('');const warnings=phases.filter(p=>p.done&&p.previous.length);$('#phaseWarning').textContent=warnings.length?`${warnings.length} aktive spätere Phasen haben noch offene Vorarbeiten. Arbeiten bleiben bewusst erlaubt.`:'Keine übersprungenen Bauphasen im erfassten Fortschritt.'}
function renderGuide(){renderPhases();if(!m)return;guideList=allAtHeight(m,guideY,guidePhase,guideGroup,guideSearch,guideRemaining,progress);const pageCount=Math.max(1,Math.ceil(guideList.length/PAGE));guidePage=clamp(guidePage,0,pageCount-1);
 const layer=m.byY.get(guideY)||[],done=progress.count(layer),total=progress.total,percentage=(100*total/m.total_blocks).toFixed(1);
 $('#buildProgress').textContent=percentage+' %';$('#progressBar').style.width=percentage+'%';$('#layerProgress').innerHTML=`<strong>Y=${guideY}</strong><br>${fmt(done)} von ${fmt(layer.length)} Blöcken erledigt · ${Math.round(done/Math.max(layer.length,1)*100)} %<br>Gesamt: ${fmt(total)} / ${fmt(m.total_blocks)}`;
 $('#guideTitle').textContent='Bauschritte · Höhe Y='+guideY;$('#guideCount').textContent=fmt(guideList.length)+' Schritte im aktuellen Filter · nach Phase, Raum und Koordinate sortiert';$('#guidePage').textContent=(guidePage+1)+' / '+pageCount;$('#guidePrev').disabled=guidePage===0;$('#guideNext').disabled=guidePage>=pageCount-1;
 const list=guideList.slice(guidePage*PAGE,(guidePage+1)*PAGE);
 $('#guideRows').innerHTML=list.map(bl=>`<div class="guide-row ${progress.has(bl.id)?'done ':''}${S.selectedId===bl.id?'current':''}" data-id="${bl.id}" title="Block #${bl.id} · X=${bl.x}, Y=${bl.y}, Z=${bl.z} · minecraft:${bl.block}"><label aria-label="Block ${bl.id} abgeschlossen"><input type="checkbox" data-done="${bl.id}" ${progress.has(bl.id)?'checked':''}></label><code>#${bl.id}</code><div><strong>${escaped(nameFor(m,bl))}</strong><small>X=${bl.x} · Y=${bl.y} · Z=${bl.z}</small><small>minecraft:${escaped(bl.block)} ${escaped(blockStates(bl))}</small>${placementHint(bl)?`<small class="hint">${escaped(placementHint(bl))}</small>`:""}</div><em>${escaped(m.build_phases[bl.phase]?.name||bl.group)}<br><span>${escaped(bl.group.replaceAll('_',' '))}</span></em></div>`).join('')||'<p class="hint">Keine Blöcke für diese Auswahl.</p>';
}
function guideSelected(){if(!S.selectedId)return;const b=m.byId[S.selectedId];if(!b)return;guideY=b.y;$('#guideY').value=guideY;$('#guideRange').value=guideY;guidePhase=guideGroup='all';guideSearch=String(b.id);guideRemaining=false;$('#guidePhase').value='all';$('#guideGroup').value='all';$('#guideSearch').value=guideSearch;$('#guideRemaining').checked=false;showView('build')}
function renderStorage(){const floor=$('#storageFloor').value,cat=$('#storageType').value;const zs=m.storage_zones.filter(z=>(floor==='all'||z.floorY===+floor)&&(cat==='all'||z.category===cat));$('#storageCards').innerHTML=zs.map(z=>`<button class="zonecard" data-zone="${escaped(z.id)}"><span class="zonetag">${escaped(z.category.toUpperCase())} · Y ${z.floorY}</span><h3>${escaped(z.name)}</h3><p>${escaped(z.notes)}</p><code>X ${z.x1}…${z.x2} · Z ${z.z1}…${z.z2}</code></button>`).join('')}
function jumpZone(z){S.planFloor=z.floorY;S.planY=z.floorY+1;S.planMode='layer';S.planGroup='all';S.showMarkers=true;showView('plan');sync2d();plan.center(z.center.x,z.center.z,3.2)}
function renderMaterials(){const group=$('#materialGroup').value,search=$('#materialSearch').value.toLowerCase(),arr=Object.entries(countsFor(m,group)).filter(([id])=>(id+' '+m.palette[id].name).toLowerCase().includes(search));arr.sort($('#materialSort').value==='name'?(a,b)=>a[0].localeCompare(b[0]):(a,b)=>b[1]-a[1]);const requirements=inventory.requirements(progress,group),overall=inventory.requirements(progress,'all');let seen=new Set();$('#materialRows').innerHTML=arr.map(([id,n])=>{const v=materialItems(m,id,group),item=v.itemId;if(seen.has(item))return '';seen.add(item);const need=requirements.get(item)||0,stock=inventory.get(item),missing=Math.max(0,need-stock);return `<tr title="${escaped(v.note||'')}"><td><span class="swatch" style="background:${m.palette[id].color}"></span>${escaped(m.palette[id].name)}${v.note?'<br><small class="hint">'+escaped(v.note)+'</small>':''}</td><td><code>minecraft:${escaped(item)}</code></td><td>${fmt(v.positions)} / ${v.items==null?'Wassereimer':fmt(v.items)}</td><td>${v.items==null?'Wasserquelle (2 Eimer empfohlen)':packText(need,v.stack)}</td><td>${v.items==null?'—':`<input class="stock" data-stock="${escaped(item)}" type="number" min="0" step="1" value="${stock}" aria-label="Vorrat ${escaped(item)}">`}</td><td>${v.items==null?'—':`<span class="${missing?'shortfall':'covered'}">${fmt(missing)}${missing?' fehlen':' ✓'}</span>`}</td></tr>`}).join('');const deficits=inventory.shortfall(progress,'all').filter(x=>x.missing);$('#inventorySummary').textContent=`${deficits.length} Materialarten fehlen für den gesamten verbleibenden Bau. Vorräte können mehrfach für Baugruppen benötigt werden: Baugruppenansichten sind Filter, keine getrennten Lagerbestände.`}
function renderCoords(){const q=$('#coordSearch').value.toLowerCase().replace(/^#/,'').trim();const arr=[];for(const b of m.blocks){if(!q||String(b.id).includes(q)||[b.x,b.y,b.z].some(n=>String(n).includes(q))||b.block.includes(q)||b.group.includes(q)){arr.push(b);if(arr.length>=130)break}}
 $('#coordResult').textContent=fmt(arr.length)+' Treffer angezeigt (max. 130)';$('#coordRows').innerHTML=arr.map(b=>`<tr data-id="${b.id}" class="clickable" title="In 3D ansehen"><td>#${b.id}</td><td>${b.x}</td><td>${b.y}</td><td>${b.z}</td><td>${escaped(nameFor(m,b))}</td><td>${escaped(b.group)}</td></tr>`).join('')}
function directCSV(file){const a=document.createElement('a');a.href=file;a.download=file;a.click()}
function openSelected3d(b){S.layerY=b.y;S.displayMode='single';S.floorY=m.floors.filter(f=>f.y<=b.y).at(-1)?.y||129;S.group='all';S.zoom=2.2;showView('viewer');sync3d()}
function bindEvents(){
 $$('.nav').forEach(b=>b.onclick=()=>showView(b.dataset.view));$$('[data-go]').forEach(b=>b.onclick=()=>showView(b.dataset.go));
 $('#displayMode').onchange=e=>{S.displayMode=e.target.value;if(S.displayMode!=='all')S.showTerrain=false;sync3d()};$('#floorSelect').onchange=e=>{S.floorY=+e.target.value;S.layerY=S.floorY;S.displayMode='floor';sync3d()};$('#groupFilter').onchange=e=>{S.group=e.target.value;sync3d()};$('#renderMode').onchange=e=>{S.renderMode=e.target.value;viewer.request()};$('#showNumbers').onchange=e=>{S.showNumbers=e.target.checked;viewer.request()};$('#showTerrain').onchange=e=>{S.showTerrain=e.target.checked;if(S.showTerrain){S.displayMode='all';$('#displayMode').value='all'}viewer.request()};
 $('#layerRange').oninput=e=>{S.layerY=+e.target.value;S.displayMode='single';sync3d()};$('#layerDown').onclick=()=>{S.layerY=clamp(S.layerY-1,m.bounds.minY,m.bounds.maxY);S.displayMode='single';sync3d()};$('#layerUp').onclick=()=>{S.layerY=clamp(S.layerY+1,m.bounds.minY,m.bounds.maxY);S.displayMode='single';sync3d()};
 $('#reset3d').onclick=()=>{S.yaw=-.71;S.zoom=1;S.panX=0;S.panY=0;viewer.request()};
 $('#planFloor').onchange=e=>{S.planFloor=+e.target.value;S.planY=S.planFloor+1;sync2d()};$('#planMode').onchange=e=>{S.planMode=e.target.value;sync2d()};$('#planGroup').onchange=e=>{S.planGroup=e.target.value;sync2d()};$('#planNumbers').onchange=e=>{S.planNumbers=e.target.checked;sync2d()};$('#planLayer').oninput=e=>{S.planY=+e.target.value;S.planMode='layer';sync2d()};$('#planReset').onclick=()=>{S.planZoom=1;S.planPanX=S.planPanY=0;sync2d()};
 $('#roomJump').onchange=e=>{let z=m.storage_zones.find(q=>q.id===e.target.value);if(z)jumpZone(z);else{let f=m.features.find(q=>q.name===e.target.value);if(f){S.planY=f.y;S.planFloor=m.floors.filter(q=>q.y<=f.y).at(-1)?.y||129;S.planMode='layer';sync2d();plan.center(f.x,f.z,3)}}};
 $('#copyBlock').onclick=async()=>{const b=m.byId[S.selectedId];if(!b)return;const t=`#${b.id} X=${b.x} Y=${b.y} Z=${b.z} minecraft:${b.block}`;try{await navigator.clipboard.writeText(t);$('#copyBlock').textContent='Kopiert ✓';setTimeout(()=>$('#copyBlock').textContent='Koordinaten kopieren',1600)}catch{window.prompt('Koordinaten:',t)}};
 $('#selectInGuide').onclick=guideSelected;$('#selectInPlan').onclick=()=>{const b=m.byId[S.selectedId];if(!b)return;S.planY=b.y;S.planFloor=m.floors.filter(f=>f.y<=b.y).at(-1)?.y||129;S.planMode='layer';S.planGroup='all';showView('plan');sync2d();plan.center(b.x,b.z,5)};
 $('#guideY').onchange=e=>syncGuideY(+e.target.value);$('#guideRange').oninput=e=>syncGuideY(+e.target.value);$('#guideDown').onclick=()=>{const ys=m.sortedY;syncGuideY(ys[Math.max(0,ys.indexOf(guideY)-1)])};$('#guideUp').onclick=()=>{const ys=m.sortedY;syncGuideY(ys[Math.min(ys.length-1,ys.indexOf(guideY)+1)])};
 $('#guidePhase').onchange=e=>{guidePhase=e.target.value;guidePage=0;renderGuide()};$('#guideGroup').onchange=e=>{guideGroup=e.target.value;guidePage=0;renderGuide()};$('#guideSearch').oninput=e=>{guideSearch=e.target.value;guidePage=0;renderGuide()};$('#guideRemaining').onchange=e=>{guideRemaining=e.target.checked;guidePage=0;renderGuide()};
 $('#guidePrev').onclick=()=>{guidePage--;renderGuide()};$('#guideNext').onclick=()=>{guidePage++;renderGuide()};
 $('#guideRows').addEventListener('click',e=>{let row=e.target.closest('[data-id]');if(!row)return;let b=m.byId[+row.dataset.id];if(e.target.matches('input[type="checkbox"]')){progress.set(b.id,e.target.checked);renderGuide();return}setSelection(b);renderGuide()});
 $('#guideIn3d').onclick=()=>{S.layerY=guideY;S.displayMode='single';S.group='all';S.zoom=1.4;showView('viewer');sync3d()};$('#guideIn2d').onclick=()=>{S.planY=guideY;S.planMode='layer';S.planFloor=m.floors.filter(f=>f.y<=guideY).at(-1)?.y||129;showView('plan');sync2d()};
 $('#progressReset').onclick=()=>{if(window.confirm('Wirklich alle Häkchen in diesem Browser zurücksetzen?')){progress.clear();renderGuide()}};$('#exportProgress').onclick=()=>progress.export();$('#importProgress').onclick=()=>$('#progressFile').click();$('#progressFile').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{const data=JSON.parse(await file.text());if(data.totalBlocks!==m.total_blocks||!Array.isArray(data.completedIds))throw Error('Datei passt nicht zu dieser Blueprint-Version');if(window.confirm('Vorhandene Häkchen durch diese Datei ersetzen?')){progress.importIds(data.completedIds);renderGuide();alert('Fortschritt importiert: '+progress.total+' Blöcke.')}}catch(err){alert('Import fehlgeschlagen: '+err.message)}finally{e.target.value=''}};
 $('#storageFloor').onchange=renderStorage;$('#storageType').onchange=renderStorage;$('#storageCards').addEventListener('click',e=>{let card=e.target.closest('[data-zone]');if(card){let z=m.storage_zones.find(t=>t.id===card.dataset.zone);if(z)jumpZone(z)}});
 $('#inventoryExport').onclick=()=>inventory.export();$('#inventoryClear').onclick=()=>{if(confirm('Erfasste Vorräte löschen?')){inventory.reset();renderMaterials()}};$('#inventoryImport').onclick=()=>$('#inventoryFile').click();$('#inventoryFile').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{inventory.import(JSON.parse(await file.text()));renderMaterials()}catch(err){alert(err.message)}finally{e.target.value=''}};$('#materialRows').addEventListener('change',e=>{if(!e.target.matches('[data-stock]'))return;try{inventory.set(e.target.dataset.stock,Number(e.target.value));renderMaterials()}catch(err){alert(err.message);renderMaterials()}});$('#materialGroup').onchange=renderMaterials;$('#materialSort').onchange=renderMaterials;$('#materialSearch').oninput=renderMaterials;$('#coordSearch').oninput=renderCoords;$('#coordRows').addEventListener('click',e=>{let row=e.target.closest('[data-id]');if(!row)return;let b=m.byId[+row.dataset.id];setSelection(b);openSelected3d(b)});
 $('#downloadCsv').onclick=()=>directCSV('blockliste.csv');$('#downloadMaterials').onclick=()=>directCSV('materialbedarf.csv');$('#downloadGroups').onclick=()=>directCSV('materialbedarf_baugruppen.csv');$('#downloadStorage').onclick=()=>directCSV('lagersystem.csv');
 const cv=$('#viewerCanvas'),cv2=$('#planCanvas');let mouse=null,planMouse=null,lastHover=0;
 cv.addEventListener('contextmenu',e=>e.preventDefault());cv.addEventListener('pointerdown',e=>{mouse={x:e.clientX,y:e.clientY,button:e.button,yaw:S.yaw,panX:S.panX,panY:S.panY};cv.setPointerCapture(e.pointerId)});
 cv.addEventListener('pointermove',e=>{if(mouse){const dx=e.clientX-mouse.x,dy=e.clientY-mouse.y;if(mouse.button===2||e.shiftKey){S.panX=mouse.panX+dx*cv.width/cv.clientWidth;S.panY=mouse.panY+dy*cv.height/cv.clientHeight}else{S.yaw=mouse.yaw+dx*.009;S.panY=mouse.panY+dy*.32}viewer.request();$('#tooltip3d').hidden=true;return}
  const b=viewer.pick(e);makeTooltip($('#tooltip3d'),b,e)});
 cv.addEventListener('pointerleave',()=>{$('#tooltip3d').hidden=true});cv.addEventListener('pointerup',e=>{if(mouse&&Math.hypot(e.clientX-mouse.x,e.clientY-mouse.y)<5){let b=viewer.pick(e);if(b)setSelection(b)}mouse=null});cv.addEventListener('pointercancel',()=>mouse=null);
 cv.addEventListener('wheel',e=>{e.preventDefault();S.zoom=clamp(S.zoom*(e.deltaY<0?1.16:.86),.35,18);viewer.request()},{passive:false});
 cv2.addEventListener('contextmenu',e=>e.preventDefault());cv2.addEventListener('pointerdown',e=>{planMouse={x:e.clientX,y:e.clientY,button:e.button,panX:S.planPanX,panY:S.planPanY};cv2.setPointerCapture(e.pointerId)});
 cv2.addEventListener('pointermove',e=>{if(planMouse&&(planMouse.button===2||e.shiftKey||e.pointerType==='touch')){S.planPanX=planMouse.panX+(e.clientX-planMouse.x)*cv2.width/cv2.clientWidth;S.planPanY=planMouse.panY+(e.clientY-planMouse.y)*cv2.height/cv2.clientHeight;plan.request();$('#tooltip2d').hidden=true;return}let q=plan.pick(e);makeTooltip($('#tooltip2d'),q?.block,e)});
 cv2.addEventListener('pointerleave',()=>$('#tooltip2d').hidden=true);cv2.addEventListener('pointerup',e=>{if(planMouse&&Math.hypot(e.clientX-planMouse.x,e.clientY-planMouse.y)<5){const q=plan.pick(e);if(q?.block)setSelection(q.block);else $('#planInfo').textContent=`X=${q?.x}, Z=${q?.z}, Y=${S.planY}: kein Block in dieser Ansicht`}planMouse=null});cv2.addEventListener('pointercancel',()=>planMouse=null);
 cv2.addEventListener('wheel',e=>{e.preventDefault();S.planZoom=clamp(S.planZoom*(e.deltaY<0?1.2:.84),.65,24);plan.request()},{passive:false});
 window.addEventListener('resize',()=>{if(S.view==='viewer')viewer.request();if(S.view==='plan')plan.request()});
 window.addEventListener('keydown',e=>{if(e.target.matches('input,select,textarea'))return;if(e.key==='ArrowUp'&&S.view==='build'){e.preventDefault();const ys=m.sortedY;syncGuideY(ys[Math.min(ys.length-1,ys.indexOf(guideY)+1)])}if(e.key==='ArrowDown'&&S.view==='build'){e.preventDefault();const ys=m.sortedY;syncGuideY(ys[Math.max(0,ys.indexOf(guideY)-1)])}});
}
async function boot(){try{m=await load();progress=new Progress(m.total_blocks);inventory=new Inventory(m);viewer=makeVoxelViewer($('#viewerCanvas'),m,()=>S);plan=makePlan2D($('#planCanvas'),m,()=>S);
 $('#statBlocks').textContent=fmt(m.total_blocks);$('#statTypes').textContent=fmt(Object.keys(m.counts).length);$('#statGroups').textContent=fmt(Object.keys(m.groups).length);$('#statZones').textContent=m.storage_zones.filter(z=>[93,105,117].includes(z.floorY)).length;
 $('#matTotal').textContent=fmt(m.total_blocks);$('#matTypes').textContent=Object.keys(m.counts).length;$('#matGroups').textContent=Object.keys(m.groups).length;
 $('#loadState').textContent='✓ '+fmt(m.total_blocks)+' Positionen geprüft';
 const groups=Object.keys(m.groups).sort();for(const id of ['groupFilter','planGroup','guideGroup','materialGroup'])$('#'+id).insertAdjacentHTML('beforeend',groups.map(g=>safeOpt(g,g.replaceAll('_',' '))).join(''));
 const floors=m.floors.map(f=>safeOpt(f.y,f.name+' · Y='+f.y)).join('');$('#floorSelect').innerHTML=floors;$('#planFloor').innerHTML=floors;
 const yOptions=m.sortedY.map(y=>safeOpt(y,`Y=${y} · ${fmt((m.byY.get(y)||[]).length)} Blöcke`)).join('');$('#guideY').innerHTML=yOptions;
 const fz=m.storage_zones.map(z=>safeOpt(z.id,z.name+' · Keller Y'+z.floorY));const rooms=(m.features||[]).filter(f=>f.type==='room'&&!m.storage_zones.some(z=>z.name===f.name)).map(f=>safeOpt(f.name,f.name));$('#roomJump').insertAdjacentHTML('beforeend',fz.concat(rooms).join(''));
 const cats=[...new Set(m.storage_zones.map(z=>z.category))];$('#storageType').insertAdjacentHTML('beforeend',cats.map(c=>safeOpt(c,c)).join(''));
 $('#guidePhase').insertAdjacentHTML('beforeend',m.build_phases.map(p=>safeOpt(p.id,`${p.id+1}. ${p.name}`)).join(''));
 for(const [id,value] of [['layerRange',129],['planLayer',130],['guideRange',m.sortedY[0]]]){const e=$('#'+id);e.min=m.bounds.minY;e.max=m.bounds.maxY;e.value=value}
 $('#guideY').value=m.sortedY[0];$('#guideRange').value=m.sortedY[0];guideY=m.sortedY[0];
 $('#floorSelect').value='129';$('#planFloor').value='129';
 bindEvents();sync3d();sync2d();renderGuide();renderStorage();renderMaterials();renderCoords();
 }catch(e){showError(e)}}
boot();
