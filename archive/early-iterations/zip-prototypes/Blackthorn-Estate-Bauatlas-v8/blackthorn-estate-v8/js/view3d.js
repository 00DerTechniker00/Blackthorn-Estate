import {point,fitCanvas,fmt,key,visible} from './model.js';
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
export function makeVoxelViewer(canvas,model,getState){
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
