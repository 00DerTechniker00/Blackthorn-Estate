import {$,$$,fmt,clamp,canvasPoint,safe} from './utils.js';
import {loadBlueprint} from './data.js';
import {createStore} from './store.js';
import {createRenderer3D} from './renderer-3d.js';
import {createRenderer2D} from './renderer-2d.js';
import {createPanels} from './panels.js';

function showError(e){const div=document.createElement('div');div.className='notice error';const msg=document.createElement('span');msg.textContent='Blueprint konnte nicht geladen werden: '+e.message+' Öffne die Website über start.sh oder start.bat und prüfe die JSON-Datei.';div.append(msg);document.querySelector('main').prepend(div);console.error(e)}
async function boot(){
 try{
 const model=await loadBlueprint(),store=createStore(model);
 const viewer=createRenderer3D($('#viewerCanvas'),model,store),plan=createRenderer2D($('#planCanvas'),model,store);
 createPanels(model,store);
 $('#statBlocks').textContent=fmt(model.total_blocks);$('#statMaterials').textContent=fmt(Object.keys(model.counts).length);
 $('#statWindows').textContent=fmt(model.release_notes?.windows||0);
 $('#statLights').textContent=fmt(['lantern','soul_lantern','torch','sea_lantern','glowstone'].reduce((n,k)=>n+(model.counts[k]||0),0));
 $('#matTotal').textContent=fmt(model.total_blocks);$('#matTypes').textContent=fmt(Object.keys(model.counts).length);$('#matGroups').textContent=fmt(Object.keys(model.groups).length);
 $('#auditStatus').textContent=model.warnings.length?`Datenprüfung: ${model.warnings.join(' | ')}`:`Datenprüfung: ${fmt(model.total_blocks)} eindeutige Positionen, Materialmengen konsistent.`;
 const groups=Object.keys(model.groups).sort(),groupHTML=groups.map(g=>`<option value="${safe(g)}">${safe(g.replaceAll('_',' '))}</option>`).join('');
 for(const el of ['#groupFilter','#planGroup','#materialGroup'])$(el).insertAdjacentHTML('beforeend',groupHTML);
 const floorsHTML=model.floors.map(f=>`<option value="${f.y}"${f.y===129?' selected':''}>${safe(f.name)} · Y=${f.y}</option>`).join('');
 $('#floorSelect').innerHTML=floorsHTML;$('#planFloor').innerHTML=floorsHTML;
 const rooms=model.features.map((f,i)=>({...f,index:i})).filter(f=>f.type==='room');
 $('#roomJump').innerHTML='<option value="">Zu einem Raum springen …</option>'+rooms.map(f=>`<option value="${f.index}">${safe(f.name)} · Y=${f.y}</option>`).join('');
 const {minY,maxY}=model.bounds;$('#layerRange').min=minY;$('#layerRange').max=maxY;$('#planLayer').min=minY;$('#planLayer').max=maxY;
 $('#layerRange').value=129;$('#planLayer').value=130;$('#layerLabel').textContent='Y = 129';$('#planLayerLabel').textContent='Y = 130';
 const refreshControls=s=>{ $('#layerLabel').textContent=`Y = ${s.layerY}`;$('#planLayerLabel').textContent=`Y = ${s.planLayerY}`;
  $('#layerRange').value=s.layerY;$('#planLayer').value=s.planLayerY;$('#displayMode').value=s.displayMode;$('#floorSelect').value=s.floorY;$('#planFloor').value=s.planFloorY;$('#planMode').value=s.planMode;
  $('#renderMode').value=s.renderMode;$('#groupFilter').value=s.group;$('#planGroup').value=s.planGroup;$('#showMarkers').checked=s.showMarkers;
  $('#materialGroup').value=s.materialGroup;$('#materialSort').value=s.materialSort;
 };
 const changeView=v=>store.patch({view:v});
 $$('.nav').forEach(btn=>btn.addEventListener('click',()=>changeView(btn.dataset.view)));
 $('#exploreNow').onclick=()=>changeView('viewer');
 $('#renderMode').onchange=e=>store.patch({renderMode:e.target.value});
 $('#displayMode').onchange=e=>store.patch({displayMode:e.target.value});
 $('#groupFilter').onchange=e=>store.patch({group:e.target.value});
 $('#floorSelect').onchange=e=>{const y=Number(e.target.value);store.patch({floorY:y,layerY:y,displayMode:'floor'})};
 $('#layerRange').oninput=e=>store.patch({layerY:Number(e.target.value),displayMode:store.get().displayMode==='floor'?'below':store.get().displayMode});
 $('#layerDown').onclick=()=>{const s=store.get();store.patch({layerY:clamp(s.layerY-1,minY,maxY),displayMode:s.displayMode==='floor'?'below':s.displayMode})};
 $('#layerUp').onclick=()=>{const s=store.get();store.patch({layerY:clamp(s.layerY+1,minY,maxY),displayMode:s.displayMode==='floor'?'below':s.displayMode})};
 $('#resetView').onclick=()=>store.patch({yaw:-.68,zoom:1,panX:0,panY:0});
 $('#planFloor').onchange=e=>store.patch({planFloorY:Number(e.target.value),planLayerY:Number(e.target.value)+1});
 $('#planGroup').onchange=e=>store.patch({planGroup:e.target.value});
 $('#planMode').onchange=e=>store.patch({planMode:e.target.value});
 $('#planLayer').oninput=e=>store.patch({planLayerY:Number(e.target.value),planMode:'layer'});
 $('#showMarkers').onchange=e=>store.patch({showMarkers:e.target.checked});
 $('#planReset').onclick=()=>store.patch({planZoom:1,planPanX:0,planPanY:0});
 $('#roomJump').onchange=e=>{if(!e.target.value)return;const f=model.features[Number(e.target.value)];if(!f)return;
  const floor=store.floorAt(f.y);store.patch({view:'plan',planFloorY:floor,planLayerY:f.y,planMode:'floor',planGroup:'all'});
  plan.centerOn(f.x,f.z);const hit=model.index.get(`${f.x}|${f.y}|${f.z}`);if(hit)store.patch({selected:hit});
 };
 $('#blockSearch').oninput=e=>store.patch({materialSearch:e.target.value});
 $('#materialSort').onchange=e=>store.patch({materialSort:e.target.value});
 $('#materialGroup').onchange=e=>store.patch({materialGroup:e.target.value});
 $('#coordSearch').oninput=e=>store.patch({coordinateSearch:e.target.value});
 const cv=$('#viewerCanvas');let pointer=null;
 cv.addEventListener('contextmenu',e=>e.preventDefault());
 cv.addEventListener('pointerdown',e=>{const s=store.get();pointer={x:e.clientX,y:e.clientY,yaw:s.yaw,panX:s.panX,panY:s.panY,button:e.button};cv.setPointerCapture(e.pointerId)});
 cv.addEventListener('pointermove',e=>{if(!pointer)return;const dx=e.clientX-pointer.x,dy=e.clientY-pointer.y;
  if(pointer.button===2||e.shiftKey)store.patch({panX:pointer.panX+dx*cv.width/cv.clientWidth,panY:pointer.panY+dy*cv.height/cv.clientHeight});
  else store.patch({yaw:pointer.yaw+dx*.009,panY:pointer.panY+dy*cv.height/cv.clientHeight*.5});
 });
 cv.addEventListener('pointerup',e=>{if(pointer&&Math.hypot(e.clientX-pointer.x,e.clientY-pointer.y)<5)viewer.pick(e);pointer=null});
 cv.addEventListener('pointercancel',()=>pointer=null);
 cv.addEventListener('wheel',e=>{e.preventDefault();store.patch({zoom:clamp(store.get().zoom*(e.deltaY<0?1.11:.90),.3,8)})},{passive:false});
 const pc=$('#planCanvas');let pp=null;
 pc.addEventListener('contextmenu',e=>e.preventDefault());
 pc.addEventListener('pointerdown',e=>{const s=store.get();pp={x:e.clientX,y:e.clientY,panX:s.planPanX,panY:s.planPanY,button:e.button};pc.setPointerCapture(e.pointerId)});
 pc.addEventListener('pointermove',e=>{if(!pp)return;if(pp.button===2||e.shiftKey||e.pointerType==='touch')store.patch({planPanX:pp.panX+(e.clientX-pp.x)*pc.width/pc.clientWidth,planPanY:pp.panY+(e.clientY-pp.y)*pc.height/pc.clientHeight})});
 pc.addEventListener('pointerup',e=>{if(pp&&Math.hypot(e.clientX-pp.x,e.clientY-pp.y)<5){const q=plan.pick(e);if(!q.blocks.length)$('#planInfo').textContent=`X=${q.x}, Z=${q.z}, Y=${q.low}–${q.high}: keine geplanten Blöcke`;}pp=null});
 pc.addEventListener('pointercancel',()=>pp=null);
 pc.addEventListener('wheel',e=>{e.preventDefault();store.patch({planZoom:clamp(store.get().planZoom*(e.deltaY<0?1.12:.89),.6,12)})},{passive:false});
 store.subscribe((s,p,keys)=>{
  if(keys.includes('view')){$$('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===s.view));$$('.view').forEach(v=>v.classList.toggle('active',v.id===s.view));}
  if(keys.some(k=>['layerY','displayMode','floorY','planLayerY','planMode','planFloorY','group','planGroup','showMarkers','selected','renderMode'].includes(k)))refreshControls(s);
  if(s.view==='viewer'&&keys.some(k=>['view','renderMode','displayMode','group','floorY','layerY','yaw','zoom','panX','panY','selected'].includes(k)))viewer.request();
  if(s.view==='plan'&&keys.some(k=>['view','planFloorY','planGroup','planMode','planLayerY','planZoom','planPanX','planPanY','showMarkers','selected'].includes(k)))plan.request();
 });
 refreshControls(store.get());
 window.addEventListener('resize',()=>{if(store.get().view==='viewer')viewer.request();if(store.get().view==='plan')plan.request()});
 new ResizeObserver(()=>{if(store.get().view==='viewer')viewer.request();if(store.get().view==='plan')plan.request()}).observe(document.querySelector('main'));
 $('#loadingStatus')?.remove();
 }catch(e){showError(e)}
}
boot();
