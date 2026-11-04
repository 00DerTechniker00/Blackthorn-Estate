import { $,fmt,key,color,clamp,insidePolygon,canvasPoint,resizeCanvas } from './utils.js';
import {filteredBlocks} from './data.js';
const FULL_EXCEPT=/(?:_stairs|_slab|_pane|_door|_fence|_wall|_carpet|_bed)$/;
function isSolid(b){if(!b)return false;const id=b.block;return !FULL_EXCEPT.test(id)&&!['chain','lantern','soul_lantern','torch','water','iron_bars','lectern'].includes(id)}
const cube={x0:0,x1:1,y0:0,y1:1,z0:0,z1:1};
function shapes(b){const id=b.block,st=b.state||{};
 if(id.endsWith('_slab'))return [{...cube,y0:st.type==='top'?.5:0,y1:st.type==='top'?1:.5}];
 if(id.endsWith('_stairs')){
  const upper=st.half==='top',facing=st.facing||'north';
  let step={...cube,y0:upper?0:.5,y1:upper?.5:1};
  if(facing==='north')step.z1=.5;else if(facing==='south')step.z0=.5;
  else if(facing==='east')step.x0=.5;else step.x1=.5;
  return [{...cube,y0:upper?.5:0,y1:upper?1:.5},step];
 }
 if(id.endsWith('_door')){
  const stf=st.facing||'north';return [stf==='east'||stf==='west'?{...cube,x0:.41,x1:.59}:{...cube,z0:.41,z1:.59}];
 }
 if(id.endsWith('_glass_pane')||id==='glass_pane'||id==='white_stained_glass_pane')return [{...cube,x0:.46,x1:.54},{...cube,z0:.46,z1:.54}];
 if(id==='iron_bars'||id.endsWith('_fence'))return [{...cube,x0:.36,x1:.64,z0:.36,z1:.64}];
 if(id.endsWith('_wall'))return [{...cube,x0:.25,x1:.75,z0:.25,z1:.75}];
 if(id==='chain')return [{...cube,x0:.43,x1:.57,z0:.43,z1:.57}];
 if(id==='lantern'||id==='soul_lantern')return [{...cube,x0:.2,x1:.8,z0:.2,z1:.8,y1:.7}];
 if(id==='torch')return [{...cube,x0:.43,x1:.57,z0:.43,z1:.57,y1:.78}];
 if(id.endsWith('_carpet'))return [{...cube,y1:.08}];
 if(id.endsWith('_bed'))return [{...cube,x0:.03,x1:.97,z0:.03,z1:.97,y1:.56}];
 if(id==='water')return [{...cube,y1:.92}];
 return [cube];
}
function boxOf(bs){const r={minX:Infinity,minY:Infinity,minZ:Infinity,maxX:-Infinity,maxY:-Infinity,maxZ:-Infinity};for(const b of bs){r.minX=Math.min(r.minX,b.x);r.maxX=Math.max(r.maxX,b.x);r.minY=Math.min(r.minY,b.y);r.maxY=Math.max(r.maxY,b.y);r.minZ=Math.min(r.minZ,b.z);r.maxZ=Math.max(r.maxZ,b.z)}return r}
export function createRenderer3D(canvas,model,store){
 let hitFaces=[],lastScale=0,lastCount=0,selectionVisible=false,job=0,cacheKey='',cacheBlocks=[];
 const ctx=canvas.getContext('2d',{alpha:false});
 function visible(s){const k=[s.displayMode,s.layerY,s.floorY,s.group].join('|');if(k!==cacheKey){cacheKey=k;cacheBlocks=filteredBlocks(model,s)}return cacheBlocks}
 function request(){if(job)return;job=requestAnimationFrame(()=>{job=0;draw()})}
 function draw(){
  if(!canvas.isConnected)return;
  resizeCanvas(canvas);const w=canvas.width,h=canvas.height,s=store.get();
  ctx.fillStyle='#101811';ctx.fillRect(0,0,w,h);hitFaces=[];selectionVisible=false;
  const bs=visible(s);lastCount=bs.length;$('#visibleCount').textContent=fmt(bs.length)+' sichtbare Blöcke';
  if(!bs.length){ctx.fillStyle='#e1ceaa';ctx.font='14px system-ui';ctx.fillText('Keine Blöcke im gewählten Ausschnitt.',22,34);return}
  const bnd=boxOf(bs),top=s.renderMode==='top',cos=Math.cos(s.yaw),sin=Math.sin(s.y),slope=.62;
  const raw=(x,y,z)=>{const dx=x-bnd.minX,dy=y-bnd.minY,dz=z-bnd.minZ;return top?[dx,dz]:[dx*cos-dz*sin,(dx*sin+dz*cos)*slope-dy*.96]};
  let minU=Infinity,maxU=-Infinity,minV=Infinity,maxV=-Infinity;
  for(const x of [bnd.minX,bnd.maxX+1])for(const z of [bnd.minZ,bnd.maxZ+1])for(const y of [bnd.minY,bnd.maxY+1]){
   const [u,v]=raw(x,y,z);minU=Math.min(u,minU);maxU=Math.max(u,maxU);minV=Math.min(v,minV);maxV=Math.max(v,maxV);
  }
  const scale=Math.min((w-70)/Math.max(maxU-minU,1),(h-85)/Math.max(maxV-minV,1))*s.zoom;lastScale=scale;
  const midU=(minU+maxU)/2,midV=(minV+maxV)/2;
  const p=(x,y,z)=>{const [u,v]=raw(x,y,z);return [(u-midU)*scale+w/2+s.panX,(v-midV)*scale+h/2+s.panY]};
  const vis=new Map(bs.map(b=>[key(b.x,b.y,b.z),b]));
  const hasSolid=(x,y,z)=>isSolid(vis.get(key(x,y,z)));
  const drawOrder=bs.slice().sort((a,b)=>((a.x-bnd.minX)*sin+(a.z-bnd.minZ)*cos+a.y*.65)-((b.x-bnd.minX)*sin+(b.z-bnd.minZ)*cos+b.y*.65));
  const pickable=bs.length<=18000&&scale>=1.8;
  const shades={};for(const [id,material] of Object.entries(model.palette))shades[id]=[color(material.color,1.10),color(material.color,.70),color(material.color,.84)];
  function face(b,corners,shadeIndex){const pts=corners.map(q=>p(b.x+q[0],b.y+q[1],b.z+q[2]));
   // Offscreen culling: useful at deep zoom or on small screens.
   const xs=pts.map(q=>q[0]),ys=pts.map(q=>q[1]);if(Math.max(...xs)<-3||Math.min(...xs)>w+3||Math.max(...ys)<-3||Math.min(...ys)>h+3)return;
   ctx.beginPath();ctx.moveTo(...pts[0]);for(let i=1;i<pts.length;i++)ctx.lineTo(...pts[i]);ctx.closePath();ctx.fillStyle=(shades[b.block]||['#aaa','#777','#999'])[shadeIndex];ctx.fill();
   if(scale>12){ctx.strokeStyle='#02060355';ctx.lineWidth=.5;ctx.stroke()}
   if(pickable)hitFaces.push([pts,b]);
   if(s.selected&&s.selected.x===b.x&&s.selected.y===b.y&&s.selected.z===b.z){ctx.strokeStyle='#ffd76c';ctx.lineWidth=Math.max(1.8,scale*.075);ctx.stroke();selectionVisible=true}
  }
  if(top){const tiles=new Map;for(const b of bs){const k=b.x+'|'+b.z,prev=tiles.get(k);if(!prev||b.y>prev.y)tiles.set(k,b)}
   for(const b of tiles.values()){
    const a=cube;face(b,[[a.x0,a.y1,a.z0],[a.x1,a.y1,a.z0],[a.x1,a.y1,a.z1],[a.x0,a.y1,a.z1]],0);
   }
  }else{
   for(const b of drawOrder){const partial=!isSolid(b),x=b.x,y=b.y,z=b.z;
    for(const a of shapes(b)){
     // Only opaque, full neighbouring cubes occlude an entire exposed face.
     const xPlus=!(a.x1===1&&hasSolid(x+1,y,z)),xMinus=!(a.x0===0&&hasSolid(x-1,y,z));
     const zPlus=!(a.z1===1&&hasSolid(x,y,z+1)),zMinus=!(a.z0===0&&hasSolid(x,y,z-1));
     const yPlus=!(a.y1===1&&hasSolid(x,y+1,z));
     if(sin>0?xPlus:xMinus){const v=sin>0?a.x1:a.x0;face(b,[[v,a.y0,a.z0],[v,a.y0,a.z1],[v,a.y1,a.z1],[v,a.y1,a.z0]],1)}
     if(cos>0?zPlus:zMinus){const v=cos>0?a.z1:a.z0;face(b,[[a.x0,a.y0,v],[a.x1,a.y0,v],[a.x1,a.y1,v],[a.x0,a.y1,v]],2)}
     if(yPlus||partial)face(b,[[a.x0,a.y1,a.z0],[a.x1,a.y1,a.z0],[a.x1,a.y1,a.z1],[a.x0,a.y1,a.z1]],0);
    }
   }
  }
  ctx.fillStyle='#e6d0a5';ctx.font='600 13px system-ui';ctx.fillText(top?'DRAUFSICHT':'3D-VOXELANSICHT',17,24);
  ctx.fillStyle='#aebda9';ctx.font='11px system-ui';ctx.fillText((pickable?'Blöcke anklickbar':'Für die Blockauswahl: auf ein Stockwerk eingrenzen')+' · '+fmt(bs.length)+' Positionen',17,44);
 }
 function pick(e){if(!hitFaces.length)return;
  const q=canvasPoint(e,canvas);for(let i=hitFaces.length-1;i>=0;i--){const [poly,b]=hitFaces[i];if(insidePolygon(poly,q.x,q.y)){store.patch({selected:b});return}}
 }
 return {request,pick,visible:()=>visible(store.get()),get info(){return {lastScale,lastCount,selectionVisible}}};
}
