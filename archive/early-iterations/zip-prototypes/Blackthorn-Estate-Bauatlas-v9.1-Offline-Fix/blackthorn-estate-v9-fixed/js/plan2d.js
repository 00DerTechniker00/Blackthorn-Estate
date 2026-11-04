import {fitCanvas,point,key,fmt} from './model.js';
export function makePlan2D(canvas,m,getState){
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
