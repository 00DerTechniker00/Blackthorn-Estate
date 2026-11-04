'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let d, occupied, faces=[], yaw=-.68, zoom=1, panX=0, panY=0, planZoom=1, planPan=[0,0], pointer=null, planPointer=null;
const old=JSON.parse(localStorage.getItem('blackthorn-progress-v5')||'{}');
const FLOOR=[93,105,117,129,143,157];
const fmt=n=>Number(n).toLocaleString('de-DE');
const blockName=k=>d.palette[k]?.name||k;
const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const key=(x,y,z)=>x+'|'+y+'|'+z;
const units=n=>{let q=Math.floor(n/1728),r=n%1728;return {sh:q,st:Math.floor(r/64),rem:r%64}};
const formatUnits=n=>{const a=units(n),t=[];if(a.sh)t.push(a.sh+' Shulker');if(a.st)t.push(a.st+' Stacks');if(a.rem)t.push(a.rem+' einzeln');return t.join(' + ')||'0';};
fetch('blueprint.json').then(r=>{if(!r.ok)throw new Error(r.status);return r.json()}).then(data=>{d=data;occupied=new Map(d.blocks.map((b,i)=>[key(b.x,b.y,b.z),i]));setup()}).catch(e=>{document.querySelector('main').insertAdjacentHTML('afterbegin',`<div class="notice">Daten konnten nicht geladen werden: ${safe(e.message)}. Bitte über start.sh oder start.bat öffnen, nicht die HTML-Datei direkt.</div>`)});
function setup(){
 $('#statBlocks').textContent=fmt(d.total_blocks);$('#statMaterials').textContent=Object.keys(d.counts).length;
 $('#statWindows').textContent=fmt(d.release_notes.windows);
 $('#statLights').textContent=fmt((d.counts.lantern||0)+(d.counts.soul_lantern||0)+(d.counts.torch||0));
 $('#matTotal').textContent=fmt(d.total_blocks);$('#matTypes').textContent=Object.keys(d.counts).length;$('#matGroups').textContent=Object.keys(d.groups).length;
 const groups=Object.keys(d.groups).sort();const optionGroups=groups.map(g=>`<option value="${safe(g)}">${safe(g.replaceAll('_',' '))}</option>`).join('');
 for(const s of ['#groupFilter','#planGroup','#materialGroup'])$(s).insertAdjacentHTML('beforeend',optionGroups);
 const floorOpts=d.floors.map(f=>`<option value="${f.y}" ${f.y===129?'selected':''}>${f.name} · Y=${f.y}</option>`).join('');
 $('#floorSelect').innerHTML=floorOpts;$('#planFloor').innerHTML=floorOpts;
 $('#layerRange').min=93;$('#layerRange').max=185;$('#layerRange').value=129;labelLayer();
 $$('.nav').forEach(b=>b.onclick=()=>selectView(b.dataset.view));$('#exploreNow').onclick=()=>selectView('viewer');
 for(const s of ['#displayMode','#renderMode','#groupFilter'])$(s).onchange=queueDraw;
 $('#floorSelect').onchange=()=>{$('#layerRange').value=$('#floorSelect').value;labelLayer();queueDraw()};
 $('#layerRange').oninput=()=>{labelLayer();queueDraw()};$('#layerDown').onclick=()=>changeLayer(-1);$('#layerUp').onclick=()=>changeLayer(1);
 $('#resetView').onclick=()=>{yaw=-.68;zoom=1;panX=panY=0;queueDraw()};
 $('#planFloor').onchange=drawPlan;$('#planGroup').onchange=drawPlan;$('#showMarkers').onchange=drawPlan;
 $('#planReset').onclick=()=>{planZoom=1;planPan=[0,0];drawPlan()};
 $('#blockSearch').oninput=renderMaterials;$('#materialSort').onchange=renderMaterials;$('#materialGroup').onchange=renderMaterials;
 $('#coordSearch').oninput=renderCoordinates;
 $('#downloadCsv').onclick=()=>download('blockliste-v5.csv',makeCSV([['X','Y','Z','Minecraft-ID','Baugruppe','Blockstates'],...d.blocks.map(b=>[b.x,b.y,b.z,'minecraft:'+b.block,b.group,states(b)])]));
 $('#downloadMaterials').onclick=()=>download('materialbedarf-v5.csv',makeCSV([['Material','Minecraft-ID','Anzahl','Shulker','Stacks','Einzelstücke'],...Object.entries(d.counts).map(([k,n])=>{const u=units(n);return [blockName(k),'minecraft:'+k,n,u.sh,u.st,u.rem]})]));
 $('#downloadGroupMaterials').onclick=()=>{const m=new Map;for(const b of d.blocks){let k=b.group+'|'+b.block;m.set(k,(m.get(k)||0)+1)}download('materialbedarf-baugruppen-v5.csv',makeCSV([['Baugruppe','Material','Minecraft-ID','Anzahl','Shulker','Stacks','Einzelstücke'],...[...m].map(([gk,n])=>{let [g,k]=gk.split('|'),u=units(n);return [g,blockName(k),'minecraft:'+k,n,u.sh,u.st,u.rem]})]))};
 $('#exportProgress').onclick=()=>download('blackthorn-fortschritt-v5.json',JSON.stringify({version:'5',checked:old},null,2),'application/json');
 const cv=$('#viewerCanvas');cv.oncontextmenu=e=>e.preventDefault();cv.addEventListener('pointerdown',e=>{pointer={x:e.clientX,y:e.clientY,yaw,panX,panY,button:e.button};cv.setPointerCapture(e.pointerId)});
 cv.addEventListener('pointermove',e=>{if(!pointer)return;const dx=e.clientX-pointer.x,dy=e.clientY-pointer.y;if(pointer.button===2){panX=pointer.panX+dx*cv.width/cv.clientWidth;panY=pointer.panY+dy*cv.height/cv.clientHeight}else{yaw=pointer.yaw+dx*.009;panY=pointer.panY+dy*.45}queueDraw()});
 cv.addEventListener('pointerup',e=>{if(pointer&&Math.abs(pointer.x-e.clientX)<5&&Math.abs(pointer.y-e.clientY)<5)pickFace(e);pointer=null});
 cv.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.25,Math.min(6,zoom*(e.deltaY<0?1.1:.9)));queueDraw()},{passive:false});
 const pc=$('#planCanvas');pc.oncontextmenu=e=>e.preventDefault();pc.addEventListener('pointerdown',e=>{planPointer={x:e.clientX,y:e.clientY,pan:[...planPan],button:e.button};pc.setPointerCapture(e.pointerId)});
 pc.addEventListener('pointermove',e=>{if(!planPointer||planPointer.button!==2)return;planPan=[planPointer.pan[0]+(e.clientX-planPointer.x)*pc.width/pc.clientWidth,planPointer.pan[1]+(e.clientY-planPointer.y)*pc.height/pc.clientHeight];drawPlan()});
 pc.addEventListener('pointerup',e=>{if(planPointer&&Math.hypot(planPointer.x-e.clientX,planPointer.y-e.clientY)<5)pickPlan(e);planPointer=null});
 pc.addEventListener('wheel',e=>{e.preventDefault();planZoom=Math.max(.6,Math.min(9,planZoom*(e.deltaY<0?1.12:.89)));drawPlan()},{passive:false});
 renderMaterials();renderCoordinates();renderGroups();queueDraw();
}
function selectView(v){$$('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===v));$$('.view').forEach(t=>t.classList.toggle('active',t.id===v));if(v==='viewer')queueDraw();if(v==='plan')drawPlan()}
function labelLayer(){let y=+$('#layerRange').value;$('#layerLabel').textContent='Y = '+y;if(FLOOR.includes(y))$('#floorSelect').value=y;}
function changeLayer(i){$('#layerRange').value=Math.max(93,Math.min(185,+$('#layerRange').value+i));labelLayer();queueDraw()}
function visible(){const mode=$('#displayMode').value,y=+$('#layerRange').value,group=$('#groupFilter').value;
 return d.blocks.filter(b=>(mode==='all'||(mode==='single'?b.y===y:mode==='below'?b.y<=y:b.y>=y&&b.y<y+(y<129?12:y===129?14:14)))&&(group==='all'||b.group===group));}
let request=0;function queueDraw(){if(request)return;request=requestAnimationFrame(()=>{request=0;draw3D()})}
function draw3D(){if(!d)return;const cv=$('#viewerCanvas'),c=cv.getContext('2d'),w=cv.width,h=cv.height;c.fillStyle='#101811';c.fillRect(0,0,w,h);faces=[];
 let bs=visible();$('#visibleCount').textContent=fmt(bs.length)+' sichtbare Blöcke';if(!bs.length){textAt(c,'Keine Blöcke in dieser Auswahl',20,32);return}
 const mn={x:Math.min(...bs.map(b=>b.x)),y:Math.min(...bs.map(b=>b.y)),z:Math.min(...bs.map(b=>b.z))},mx={x:Math.max(...bs.map(b=>b.x)),y:Math.max(...bs.map(b=>b.y)),z:Math.max(...bs.map(b=>b.z))};
 const isTop=$('#renderMode').value==='top';const cos=Math.cos(yaw),sin=Math.sin(yaw),r=.62;
 function rel(x,y,z){let a=x-mn.x,b=y-mn.y,t=z-mn.z;return isTop?[a,t]:[(a*cos-t*sin),(a*sin+t*cos)*r-b*.95]}
 let corners=[];for(let x of [mn.x,mx.x+1])for(let z of [mn.z,mx.z+1])for(let y of [mn.y,mx.y+1])corners.push(rel(x,y,z));
 let lx=Math.min(...corners.map(v=>v[0])),hx=Math.max(...corners.map(v=>v[0])),ly=Math.min(...corners.map(v=>v[1])),hy=Math.max(...corners.map(v=>v[1]));
 let scale=Math.min((w-80)/Math.max(hx-lx,1),(h-90)/Math.max(hy-ly,1))*zoom;
 function p(x,y,z){let [a,b]=rel(x,y,z);return [(a-(lx+hx)/2)*scale+w/2+panX,(b-(ly+hy)/2)*scale+h/2+panY]}
 let vis=new Set(bs.map(b=>key(b.x,b.y,b.z)));
 const viewDepth=b=>(b.x-mn.x)*sin+(b.z-mn.z)*cos-(b.y-mn.y)*.22;
 bs.sort((a,b)=>viewDepth(a)-viewDepth(b));
 function poly(b,pts,color,shade=1){const arr=pts.map(v=>p(b.x+v[0],b.y+v[1],b.z+v[2]));c.beginPath();c.moveTo(...arr[0]);for(let i=1;i<arr.length;i++)c.lineTo(...arr[i]);c.closePath();c.fillStyle=tint(color,shade);c.fill();if(scale>8){c.strokeStyle='#00000035';c.lineWidth=.42;c.stroke()}faces.push([arr,b])}
 for(let b of bs){const x=b.x,y=b.y,z=b.z,col=d.palette[b.block]?.color||'#aaa';
  // Accurate local voxel proportions for slabs, stairs, panes, doors, carpets and fences.
  // Cubes only occlude their immediate fully occupied neighboring faces.
  let parts=[{x0:0,x1:1,y0:0,y1:1,z0:0,z1:1}];let id=b.block,st=b.state||{};
  if(id.endsWith('_slab'))parts=[{x0:0,x1:1,y0:st.type==='top'?.5:0,y1:st.type==='top'?1:.5,z0:0,z1:1}];
  else if(id.endsWith('_stairs')){let half=st.half==='top';parts=[{x0:0,x1:1,y0:half?.5:0,y1:half?1:.5,z0:0,z1:1}];let upper={x0:0,x1:1,y0:half?0:.5,y1:half?.5:1,z0:0,z1:1};
   if(st.facing==='north')upper.z1=.5;else if(st.facing==='south')upper.z0=.5;else if(st.facing==='east')upper.x0=.5;else upper.x1=.5;parts.push(upper)}
  else if(id.endsWith('_door'))parts=[{x0:.4,x1:.6,y0:0,y1:1,z0:0,z1:1}];
  else if(id.includes('glass_pane'))parts=[{x0:.44,x1:.56,y0:0,y1:1,z0:0,z1:1}];
  else if(id==='iron_bars')parts=[{x0:.39,x1:.61,y0:0,y1:1,z0:.39,z1:.61}];
  else if(id.endsWith('_fence'))parts=[{x0:.36,x1:.64,y0:0,y1:1,z0:.36,z1:.64}];
  else if(id==='chain')parts=[{x0:.43,x1:.57,y0:0,y1:1,z0:.43,z1:.57}];
  else if(id==='lantern'||id==='soul_lantern')parts=[{x0:.21,x1:.79,y0:0,y1:.72,z0:.21,z1:.79}];
  else if(id.endsWith('_carpet'))parts=[{x0:0,x1:1,y0:0,y1:.08,z0:0,z1:1}];
  else if(id.endsWith('_bed'))parts=[{x0:.05,x1:.95,y0:0,y1:.55,z0:.05,z1:.95}];
  for(const a of parts){let ext=(dx,dy,dz)=>vis.has(key(x+dx,y+dy,z+dz));
   const fully=v=>v===0||v===1;
   if(!isTop){if(sin>0 && !(a.x1===1&&ext(1,0,0)))poly(b,[[a.x1,a.y0,a.z0],[a.x1,a.y0,a.z1],[a.x1,a.y1,a.z1],[a.x1,a.y1,a.z0]],col,.70);
    else if(sin<=0 && !(a.x0===0&&ext(-1,0,0)))poly(b,[[a.x0,a.y0,a.z1],[a.x0,a.y0,a.z0],[a.x0,a.y1,a.z0],[a.x0,a.y1,a.z1]],col,.72);
    if(cos>0 && !(a.z1===1&&ext(0,0,1)))poly(b,[[a.x0,a.y0,a.z1],[a.x1,a.y0,a.z1],[a.x1,a.y1,a.z1],[a.x0,a.y1,a.z1]],col,.82);
    else if(cos<=0 && !(a.z0===0&&ext(0,0,-1)))poly(b,[[a.x1,a.y0,a.z0],[a.x0,a.y0,a.z0],[a.x0,a.y1,a.z0],[a.x1,a.y1,a.z0]],col,.82);
   }
   if(a.y1<1||!ext(0,1,0)||isTop)poly(b,[[a.x0,a.y1,a.z0],[a.x1,a.y1,a.z0],[a.x1,a.y1,a.z1],[a.x0,a.y1,a.z1]],col,1.08);
  }
 }
 textAt(c,isTop?'DRAUFSICHT · BLOCKGENAUES RASTER':'3D · KANTENBÜNDIGE VOXELFLÄCHEN',18,26);textAt(c,'Ansicht: '+$('#displayMode').selectedOptions[0].text+' · '+fmt(bs.length)+' Blöcke',18,47,'#aabb9c',11);
}
function tint(hex,amt){let x=parseInt(hex.substring(1),16);return `rgb(${Math.min(255,(x>>16&255)*amt)|0},${Math.min(255,(x>>8&255)*amt)|0},${Math.min(255,(x&255)*amt)|0})`}
function textAt(c,t,x,y,color='#dbc9a1',size=13){c.fillStyle=color;c.font=size+'px system-ui';c.fillText(t,x,y)}
function inside(pts,x,y){let hit=false;for(let i=0,j=pts.length-1;i<pts.length;j=i++){const a=pts[i],b=pts[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit}return hit}
function pickFace(e){const cv=$('#viewerCanvas'),r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*cv.width/r.width,y=(e.clientY-r.top)*cv.height/r.height;for(let i=faces.length-1;i>=0;i--)if(inside(faces[i][0],x,y)){const b=faces[i][1];$('#selectedBlock').innerHTML=`<b>${safe(blockName(b.block))}</b> · <code>minecraft:${safe(b.block)}</code><br>Welt: <b>X=${b.x}, Y=${b.y}, Z=${b.z}</b> · Baugruppe: ${safe(b.group)}<br>Blockstates: <code>${safe(states(b)||'keine hinterlegt')}</code>`;return}}
let planGeometry=()=>{const cv=$('#planCanvas'),unit=Math.min((cv.width-100)/105,(cv.height-100)/90)*planZoom;return {u:unit,x:x=>cv.width/2+planPan[0]+(x+742-52)*unit,z:z=>cv.height/2+planPan[1]+(z-746-44)*unit}}
function planTiles(y,group){const out=new Map;for(let b of d.blocks){if(b.y<y||b.y>y+6||group!=='all'&&b.group!==group)continue;let k=b.x+'|'+b.z;let prev=out.get(k);if(!prev||b.y>prev.y)out.set(k,b)}return out}
function drawPlan(){if(!d)return;const cv=$('#planCanvas'),ctx=cv.getContext('2d'),y=+$('#planFloor').value,g=$('#planGroup').value,geo=planGeometry(),u=geo.u;ctx.fillStyle='#101811';ctx.fillRect(0,0,cv.width,cv.height);
 const tiles=planTiles(y,g);for(let b of tiles.values()){let x=geo.x(b.x),z=geo.z(b.z);ctx.fillStyle=d.palette[b.block]?.color||'#aaa';ctx.fillRect(x,z,u+.25,u+.25)}
 if(u>5){ctx.beginPath();ctx.strokeStyle='#ffffff18';ctx.lineWidth=.5;for(let x=-742;x<=-638;x++){ctx.moveTo(geo.x(x),geo.z(746));ctx.lineTo(geo.x(x),geo.z(835))}for(let z=746;z<=835;z++){ctx.moveTo(geo.x(-742),geo.z(z));ctx.lineTo(geo.x(-637),geo.z(z))}ctx.stroke()}
 if($('#showMarkers').checked){for(const f of d.features){if(f.y<y||f.y>y+4)continue;if(f.type==='room'||f.type==='stair'){let x=geo.x(f.x+.5),z=geo.z(f.z+.5);ctx.fillStyle='#131c18df';let label=f.type==='stair'?'↗ Treppe':f.name;ctx.font='bold 12px system-ui';let width=ctx.measureText(label).width;ctx.fillRect(x-width/2-5,z-13,width+10,19);ctx.fillStyle=f.type==='stair'?'#e8c77c':'#e7e5cf';ctx.textAlign='center';ctx.fillText(label,x,z+1);ctx.textAlign='start'}}}
 textAt(ctx,'GRUNDRISS · '+d.floors.find(f=>f.y===y)?.name.toUpperCase()+' · Y='+y,20,28);textAt(ctx,fmt(tiles.size)+' belegte X/Z-Zellen',20,46,'#9ab19f',11);
}
function pickPlan(e){let cv=$('#planCanvas'),r=cv.getBoundingClientRect(),px=(e.clientX-r.left)*cv.width/r.width,pz=(e.clientY-r.top)*cv.height/r.height,geo=planGeometry(),x=Math.floor((px-cv.width/2-planPan[0])/geo.u+52-742),z=Math.floor((pz-cv.height/2-planPan[1])/geo.u+44+746),y=+$('#planFloor').value;
 let found=d.blocks.filter(b=>b.x===x&&b.z===z&&b.y>=y&&b.y<=y+6).sort((a,b)=>b.y-a.y);
 $('#planInfo').innerHTML=`<b>X=${x}, Z=${z} · Stockwerk Y=${y}</b>`+(found.length?'<br>'+found.map(b=>`Y=${b.y} · <b>${safe(blockName(b.block))}</b> · ${safe(b.group)} ${states(b)?' · '+safe(states(b)):''}`).join('<br>'):'<br>Hier befinden sich im sichtbaren Stockwerkschnitt keine geplanten Blöcke.');
}
function renderMaterials(){if(!d)return;const group=$('#materialGroup').value,q=$('#blockSearch').value.toLowerCase(),counts={};if(group==='all')Object.assign(counts,d.counts);else for(const b of d.blocks)if(b.group===group)counts[b.block]=(counts[b.block]||0)+1;
 let rows=Object.entries(counts).filter(([k])=>(k+' '+blockName(k)).toLowerCase().includes(q));rows.sort($('#materialSort').value==='name'?(a,b)=>blockName(a[0]).localeCompare(blockName(b[0])):(a,b)=>b[1]-a[1]);
 $('#materialRows').innerHTML=rows.map(([k,n])=>`<tr><td><span class="swatch" style="background:${d.palette[k]?.color||'#aaa'}"></span>${safe(blockName(k))}</td><td><code>minecraft:${safe(k)}</code></td><td>${fmt(n)}</td><td>${formatUnits(n)}</td></tr>`).join('');}
function states(b){return Object.entries(b.state||{}).map(([k,v])=>k+'='+v).join(', ')}
function renderCoordinates(){if(!d)return;const q=$('#coordSearch').value.trim().toLowerCase().replaceAll(',',' ');let a=d.blocks.filter(b=>([b.x,b.y,b.z,b.block,b.group,states(b)].join(' ').toLowerCase().includes(q)));$('#coordResult').textContent=fmt(a.length)+' Treffer · 300 angezeigt';$('#coordRows').innerHTML=a.slice(0,300).map(b=>`<tr><td>${b.x}</td><td>${b.y}</td><td>${b.z}</td><td>minecraft:${safe(b.block)}</td><td>${safe(b.group)}</td><td>${safe(states(b))}</td></tr>`).join('')}
function renderGroups(){let arr=Object.entries(d.groups).sort((a,b)=>a[0].localeCompare(b[0]));$('#buildGroups').innerHTML=arr.map(([g,n])=>`<article class="build-group"><h3>${safe(g.replaceAll('_',' '))}</h3><small>${fmt(n)} Blöcke</small><label><input type="checkbox" data-group="${safe(g)}" ${old[g]?'checked':''}> Fertiggestellt</label></article>`).join('');$('#buildGroups').onchange=e=>{if(e.target.matches('input[type=checkbox]')){old[e.target.dataset.group]=e.target.checked;localStorage.setItem('blackthorn-progress-v5',JSON.stringify(old));updateProgress()}};updateProgress()}
function updateProgress(){const a=Object.keys(d.groups);const n=a.filter(k=>old[k]).length;$('#progressLabel').textContent=n+' / '+a.length+' Baugruppen';$('#progressBar').style.width=Math.round(100*n/a.length)+'%'}
function makeCSV(a){return '\ufeff'+a.map(r=>r.map(x=>'"'+String(x).replaceAll('"','""')+'"').join(';')).join('\r\n')}
function download(name,raw,type='text/csv;charset=utf-8'){let blob=new Blob([raw],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)}
