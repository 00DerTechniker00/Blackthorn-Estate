import { $,fmt,canvasPoint,resizeCanvas } from './utils.js';
export function createRenderer2D(canvas,model,store){
 let pending=0,geometry=null,tiles=new Map;
 const ctx=canvas.getContext('2d',{alpha:false}), bounds=model.site?.bounds||model.bounds;
 const nx=bounds.maxX-bounds.minX+1,nz=bounds.maxZ-bounds.minZ+1;
 function request(){if(pending)return;pending=requestAnimationFrame(()=>{pending=0;draw()})}
 function geom(){const s=store.get(),w=canvas.width,h=canvas.height;
  const unit=Math.min((w-105)/nx,(h-110)/nz)*s.planZoom;
  return {unit,x:x=>w/2+s.planPanX+(x-bounds.minX-nx/2)*unit,z:z=>h/2+s.planPanY+(z-bounds.minZ-nz/2)*unit};}
 function range(s){if(s.planMode==='layer')return [s.planLayerY,s.planLayerY];
  const above=model.floors.find(f=>f.y>s.planFloorY)?.y??s.planFloorY+15;
  return [s.planFloorY,Math.min(s.planFloorY+7,above-1)];}
 function floorBlocks(s){const [low,high]=range(s);const ret=[];for(let y=low;y<=high;y++){
  const arr=model.byY.get(y)||[];
  if(s.planGroup==='all')ret.push(...arr);else for(const b of arr)if(b.group===s.planGroup)ret.push(b);
 }return ret;}
 function draw(){resizeCanvas(canvas);const s=store.get(),w=canvas.width,h=canvas.height;
  ctx.fillStyle='#111913';ctx.fillRect(0,0,w,h);
  geometry=geom();const {unit,x,z}=geometry;tiles=new Map;
  const blocks=floorBlocks(s);
  // Highest chosen Y at each X/Z is the block visible in plan; individual layers remain accessible.
  for(const b of blocks){const k=b.x+'|'+b.z,prev=tiles.get(k);if(!prev||prev.y<=b.y)tiles.set(k,b)}
  for(const b of tiles.values()){
   const px=x(b.x),pz=z(b.z);if(px+unit<0||px>w||pz+unit<0||pz>h)continue;
   ctx.fillStyle=model.palette[b.block]?.color||'#aaa';ctx.fillRect(px,pz,unit+.2,unit+.2);
  }
  if(unit>8){ctx.strokeStyle='#d8e4d522';ctx.lineWidth=Math.min(1,unit*.07);ctx.beginPath();
   for(let ix=bounds.minX;ix<=bounds.maxX+1;ix++){let xx=x(ix);if(xx>=0&&xx<=w){ctx.moveTo(xx,Math.max(0,z(bounds.minZ)));ctx.lineTo(xx,Math.min(h,z(bounds.maxZ+1)))}}
   for(let iz=bounds.minZ;iz<=bounds.maxZ+1;iz++){let zz=z(iz);if(zz>=0&&zz<=h){ctx.moveTo(Math.max(0,x(bounds.minX)),zz);ctx.lineTo(Math.min(w,x(bounds.maxX+1)),zz)}}ctx.stroke();
  }
  if(unit>2){ctx.fillStyle='#b7c8b2';ctx.font='11px system-ui';ctx.textAlign='center';
   for(let xx=Math.ceil(bounds.minX/10)*10;xx<=bounds.maxX;xx+=10)ctx.fillText('X '+xx,x(xx),Math.max(16,z(bounds.minZ)-8));
   ctx.textAlign='right';for(let zz=Math.ceil(bounds.minZ/10)*10;zz<=bounds.maxZ;zz+=10)ctx.fillText('Z '+zz,Math.max(37,x(bounds.minX)-7),z(zz)+4);ctx.textAlign='left';
  }
  if(s.showMarkers){for(const f of model.features){if(!['room','stair'].includes(f.type)||f.y<s.planFloorY||f.y>s.planFloorY+5)continue;
   const mx=x(f.x+.5),mz=z(f.z+.5);if(mx<0||mx>w||mz<0||mz>h)continue;
   const name=f.type==='stair'?'↗ Treppe':f.name;
   ctx.font='600 11px system-ui';const labelWidth=ctx.measureText(name).width;
   ctx.fillStyle='#132019eb';ctx.fillRect(mx-labelWidth/2-5,mz-15,labelWidth+10,20);
   ctx.fillStyle=f.type==='stair'?'#efd38e':'#fff5dc';ctx.textAlign='center';ctx.fillText(name,mx,mz);ctx.textAlign='left';
  }}
  if(s.selected){const q=s.selected,px=x(q.x),pz=z(q.z);ctx.strokeStyle='#ffd566';ctx.lineWidth=Math.max(2,unit*.18);ctx.strokeRect(px,pz,unit,unit)}
  const floor=model.floors.find(f=>f.y===s.planFloorY),label=s.planMode==='layer'?`EINZELLAYER Y=${s.planLayerY}`:`${floor?.name||'Etage'} · Y=${s.planFloorY} … ${range(s)[1]}`;
  ctx.fillStyle='#ead5ac';ctx.font='600 13px system-ui';ctx.fillText('2D-RAUMPLAN · '+label.toUpperCase(),16,25);
  ctx.fillStyle='#aebca8';ctx.font='11px system-ui';ctx.fillText(`${fmt(tiles.size)} belegte Rasterzellen · Osten → · Westen ← (Klippe)`,16,44);
 }
 function pick(e){if(!geometry)return;const p=canvasPoint(e,canvas),s=store.get(),x=Math.floor((p.x-canvas.width/2-s.planPanX)/geometry.unit+nx/2+bounds.minX),z=Math.floor((p.y-canvas.height/2-s.planPanY)/geometry.unit+nz/2+bounds.minZ);
  const [low,high]=range(s),all=[];for(let y=high;y>=low;y--){const b=model.index.get(`${x}|${y}|${z}`);if(b&&(s.planGroup==='all'||s.planGroup===b.group))all.push(b)}
  if(all.length)store.patch({selected:all[0]});return {x,z,low,high,blocks:all};
 }
 function centerOn(x,z){const s=store.get(),unit=Math.min((canvas.width-105)/nx,(canvas.height-110)/nz)*s.planZoom;
  store.patch({planPanX:-(x-bounds.minX-nx/2)*unit,planPanY:-(z-bounds.minZ-nz/2)*unit});}
 return {request,pick,centerOn,get range(){return range(store.get())}};
}
