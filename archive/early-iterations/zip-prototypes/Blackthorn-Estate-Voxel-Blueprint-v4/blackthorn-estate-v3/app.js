const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let model=null, yaw=.68, zoom=1, panX=0, panY=0, drag=null, selected=null;
const saved=JSON.parse(localStorage.getItem("blackthorn-v4-progress")||"{}");
fetch("blueprint.json").then(r=>r.json()).then(d=>{model=d;init()}).catch(e=>alert("blueprint.json konnte nicht geladen werden: "+e));
const fmt=n=>Number(n).toLocaleString("de-DE");
function init(){
 $("#statBlocks").textContent=fmt(model.total_blocks);$("#statMaterials").textContent=Object.keys(model.counts).length;$("#statLayers").textContent=Object.keys(model.y_layers).length;
 $("#matTotal").textContent=fmt(model.total_blocks);$("#matTypes").textContent=Object.keys(model.counts).length;$("#matGroups").textContent=Object.keys(model.groups).length;
 const ys=Object.keys(model.y_layers).map(Number).sort((a,b)=>a-b);
 $("#layerRange").min=ys[0];$("#layerRange").max=ys.at(-1);$("#layerRange").value=129;
 $("#planY").innerHTML=ys.map(y=>`<option value="${y}">Y=${y}</option>`).join("");$("#planY").value=129;
 const groups=Object.keys(model.groups).sort();
 $("#groupFilter").innerHTML='<option value="all">Alle Baugruppen</option>'+groups.map(g=>`<option value="${g}">${g.replaceAll("_"," ")}</option>`).join("");
 if($("#planGroup"))$("#planGroup").innerHTML=$("#groupFilter").innerHTML;
 drawAll();renderMaterials();renderBuildGroups();
 $$(".nav").forEach(b=>b.onclick=()=>{$$(".nav").forEach(n=>n.classList.toggle("active",n===b));$$(".view").forEach(v=>v.classList.toggle("active",v.id===b.dataset.view));if(b.dataset.view==="viewer")drawViewer();if(b.dataset.view==="plan")drawPlan()});
 $("#layerRange").oninput=()=>{updateLayerLabel();drawViewer();drawPlan()};$("#layerDown").onclick=()=>changeLayer(-1);$("#layerUp").onclick=()=>changeLayer(1);
 $("#renderMode").onchange=drawViewer;$("#displayMode").onchange=drawViewer;$("#groupFilter").onchange=drawViewer;
 $("#resetView").onclick=()=>{yaw=.68;zoom=1;panX=panY=0;drawViewer()};
 $("#planY").onchange=drawPlan;if($("#planGroup"))$("#planGroup").onchange=drawPlan;
 $("#blockSearch").oninput=renderMaterials;$("#materialSort").onchange=renderMaterials;$("#coordSearch").oninput=renderCoords;
 $("#downloadCsv").onclick=downloadCSV;$("#downloadMaterials").onclick=()=>download("blackthorn-materialbedarf.csv",csvMaterials(),"text/csv;charset=utf-8");
 $("#downloadGroupMaterials").onclick=()=>download("blackthorn-materialbedarf-baugruppen.csv",csvGroups(),"text/csv;charset=utf-8");
 $("#exportProgress").onclick=()=>download("blackthorn-progress.json",JSON.stringify({project:model.project,checked:saved,exportedAt:new Date().toISOString()},null,2),"application/json");
 const c=$("#viewerCanvas");
 c.addEventListener("pointerdown",e=>{drag={x:e.clientX,y:e.clientY,yaw,panX,panY,button:e.button};c.setPointerCapture(e.pointerId)});
 c.addEventListener("pointermove",e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(drag.button===2){panX=drag.panX+dx;panY=drag.panY+dy}else{yaw=drag.yaw+dx*.008;panY=drag.panY+dy*.5}drawViewer()});
 c.addEventListener("pointerup",e=>{if(drag&&Math.abs(e.clientX-drag.x)<4&&Math.abs(e.clientY-drag.y)<4)pickBlock(e);drag=null});
 c.addEventListener("contextmenu",e=>e.preventDefault());c.addEventListener("wheel",e=>{e.preventDefault();zoom=Math.max(.3,Math.min(4,zoom*(e.deltaY<0?1.1:.9)));drawViewer()},{passive:false});
 $("#planCanvas").onclick=pickPlan;drawViewer();drawPlan();drawMini();
}
function changeLayer(d){let ys=Object.keys(model.y_layers).map(Number).sort((a,b)=>a-b),v=+$("#layerRange").value,i=ys.indexOf(v);$("#layerRange").value=ys[Math.max(0,Math.min(ys.length-1,i+d))];updateLayerLabel();drawViewer();drawPlan()}
function updateLayerLabel(){$("#layerLabel").textContent="Y = "+$("#layerRange").value}
function visibleBlocks(){const y=+$("#layerRange").value,mode=$("#displayMode").value,g=$("#groupFilter").value;return model.blocks.filter(b=>(mode==="upto"?b.y<=y:b.y===y)&&(g==="all"||b.group===g))}
function bounds(bs){return {minX:Math.min(...bs.map(b=>b.x)),maxX:Math.max(...bs.map(b=>b.x)),minY:Math.min(...bs.map(b=>b.y)),maxY:Math.max(...bs.map(b=>b.y)),minZ:Math.min(...bs.map(b=>b.z)),maxZ:Math.max(...bs.map(b=>b.z))}}
function camera(bs,w,h){
 const bb=bounds(bs),c=Math.cos(yaw),s=Math.sin(yaw),corners=[];
 for(const x of [bb.minX,bb.maxX+1])for(const z of [bb.minZ,bb.maxZ+1])for(const y of [bb.minY,bb.maxY+1]){
  const rx=(x-bb.minX)*c-(z-bb.minZ)*s, rz=(x-bb.minX)*s+(z-bb.minZ)*c;
  corners.push({x:(rx-rz)*.866,y:(rx+rz)*.5-(y-bb.minY)*.92});
 }
 const minX=Math.min(...corners.map(p=>p.x)),maxX=Math.max(...corners.map(p=>p.x)),minY=Math.min(...corners.map(p=>p.y)),maxY=Math.max(...corners.map(p=>p.y));
 const scale=Math.min((w-100)/(maxX-minX||1),(h-110)/(maxY-minY||1))*zoom;
 return {bb,c,s,scale,ox:w/2-(minX+maxX)/2*scale+panX,oy:h/2-(minY+maxY)/2*scale+panY};
}
function projectBlock(b,cam){
 const {bb,c,s,scale,ox,oy}=cam;
 const x=b.x-bb.minX,z=b.z-bb.minZ,y=b.y-bb.minY;
 const rx=x*c-z*s,rz=x*s+z*c;
 return {x:ox+(rx-rz)*.866*scale,y:oy+((rx+rz)*.5-y*.92)*scale,depth:rx+rz+y*.7};
}
function shade(hex,f){let n=parseInt(hex.slice(1),16),r=Math.min(255,((n>>16)&255)*f),g=Math.min(255,((n>>8)&255)*f),b=Math.min(255,(n&255)*f);return `rgb(${r|0},${g|0},${b|0})`}
function drawCube(ctx,p,scale,color){
 // A unit cube: all three visible faces share exact projected edges with their neighbours.
 const ux=.866*scale, vz=.5*scale, hh=.92*scale, x=p.x,y=p.y;
 ctx.beginPath();ctx.moveTo(x,y-hh);ctx.lineTo(x+ux,y-hh+vz);ctx.lineTo(x,y-hh+2*vz);ctx.lineTo(x-ux,y-hh+vz);ctx.closePath();ctx.fillStyle=shade(color,1.18);ctx.fill();
 ctx.beginPath();ctx.moveTo(x-ux,y-hh+vz);ctx.lineTo(x,y-hh+2*vz);ctx.lineTo(x,y+2*vz);ctx.lineTo(x-ux,y+vz);ctx.closePath();ctx.fillStyle=shade(color,.70);ctx.fill();
 ctx.beginPath();ctx.moveTo(x+ux,y-hh+vz);ctx.lineTo(x,y-hh+2*vz);ctx.lineTo(x,y+2*vz);ctx.lineTo(x+ux,y+vz);ctx.closePath();ctx.fillStyle=shade(color,.88);ctx.fill();
}
function drawViewer(){
 if(!model)return;const c=$("#viewerCanvas"),ctx=c.getContext("2d"),w=c.width,h=c.height;
 ctx.fillStyle="#101711";ctx.fillRect(0,0,w,h);let bs=visibleBlocks();$("#visibleCount").textContent=fmt(bs.length)+" sichtbare Blöcke";
 const iso=$("#renderMode").value!=="top";
 if(!bs.length){ctx.fillStyle="#c9b58b";ctx.fillText("Keine Blöcke in dieser Auswahl",24,34);return}
 if(!iso){drawTop(ctx,bs,w,h);return}
 const cam=camera(bs,w,h);
 // Painter order by camera depth; one unit in world space is one touching voxel.
 bs=bs.slice().sort((a,b)=>{const pa=projectBlock(a,cam),pb=projectBlock(b,cam);return pa.depth-pb.depth});
 for(const b of bs){const p=projectBlock(b,cam);drawCube(ctx,p,cam.scale,model.palette[b.block]?.color||"#aaa")}
 ctx.fillStyle="#c9b58b";ctx.font="14px sans-serif";ctx.fillText("BLACKTHORN · ISOMETRISCHE VOXELANSICHT",20,28);
 ctx.fillStyle="#91a08f";ctx.font="11px sans-serif";ctx.fillText("Bis Y="+$("#layerRange").value+" · "+$("#groupFilter").value.replaceAll("_"," "),20,47);
}
function drawTop(ctx,bs,w,h){
 const bb=bounds(bs),pad=45,scale=Math.min((w-2*pad)/(bb.maxX-bb.minX+1),(h-2*pad)/(bb.maxZ-bb.minZ+1));
 const ox=(w-(bb.maxX-bb.minX+1)*scale)/2,oy=(h-(bb.maxZ-bb.minZ+1)*scale)/2;
 for(const b of bs){ctx.fillStyle=model.palette[b.block]?.color||"#aaa";ctx.fillRect(ox+(b.x-bb.minX)*scale,oy+(b.z-bb.minZ)*scale,scale+.15,scale+.15)}
 ctx.fillStyle="#c9b58b";ctx.font="14px sans-serif";ctx.fillText("BLACKTHORN · DRAUFSICHT",20,25);
}
function drawMini(){const c=$("#mini3d"),ctx=c.getContext("2d");ctx.fillStyle="#111913";ctx.fillRect(0,0,c.width,c.height);let bs=model.blocks.filter(b=>b.y<=150);const cam=camera(bs,c.width,c.height);bs.sort((a,b)=>projectBlock(a,cam).depth-projectBlock(b,cam).depth);for(const b of bs)drawCube(ctx,projectBlock(b,cam),cam.scale,model.palette[b.block]?.color||"#aaa")}
function planGeometry(c){const w=c.width,h=c.height,pad=52,scale=Math.min((w-2*pad)/105,(h-2*pad)/90);return {pad,scale,x:v=>pad+(v+742)*scale,z:v=>pad+(v-746)*scale}}
function drawPlan(){
 const c=$("#planCanvas"),ctx=c.getContext("2d"),w=c.width,h=c.height,y=+$("#planY").value,g=$("#planGroup")?$("#planGroup").value:"all",geo=planGeometry(c);
 ctx.fillStyle="#111913";ctx.fillRect(0,0,w,h);
 // Draw grid at exact cell boundaries; adjacent cells meet without gaps.
 ctx.strokeStyle="#26372b";ctx.lineWidth=1;ctx.beginPath();
 for(let x=-742;x<=-638;x+=5){ctx.moveTo(geo.x(x),geo.z(746));ctx.lineTo(geo.x(x),geo.z(834)+geo.scale)}
 for(let z=746;z<=834;z+=5){ctx.moveTo(geo.x(-742),geo.z(z));ctx.lineTo(geo.x(-638)+geo.scale,geo.z(z))}
 ctx.stroke();
 const bs=model.blocks.filter(b=>b.y===y&&(g==="all"||b.group===g));
 for(const b of bs){const x=geo.x(b.x),z=geo.z(b.z);ctx.fillStyle=model.palette[b.block]?.color||"#aaa";ctx.fillRect(x,z,geo.scale+.2,geo.scale+.2)}
 ctx.fillStyle="#d5bd8e";ctx.font="13px sans-serif";ctx.fillText(`LAYER Y=${y} · ${g==="all"?"ALLE GRUPPEN":g.replaceAll("_"," ")}`,52,25);
}
function pickBlock(e){const c=$("#viewerCanvas"),r=c.getBoundingClientRect(),mx=(e.clientX-r.left)/r.width*c.width,my=(e.clientY-r.top)/r.height*c.height,bs=visibleBlocks();if(!bs.length)return;const iso=$("#renderMode").value!=="top";let cam=iso?camera(bs,c.width,c.height):null,best=null,dist=1e12;
 for(const b of bs){const p=iso?projectBlock(b,cam):topProject(b,bs,c.width,c.height),d=(p.x-mx)**2+(p.y-my)**2;if(d<dist){dist=d;best=b}}
 if(best&&dist<Math.max(18,(cam?.scale||8)**2*2.5)){selected=best;$("#selectedBlock").textContent=`minecraft:${best.block} · ${model.palette[best.block]?.name||best.block} · X=${best.x}, Y=${best.y}, Z=${best.z} · ${best.group}`}
}
function topProject(b,bs,w,h){const bb=bounds(bs),pad=45,scale=Math.min((w-2*pad)/(bb.maxX-bb.minX+1),(h-2*pad)/(bb.maxZ-bb.minZ+1));return {x:(w-(bb.maxX-bb.minX+1)*scale)/2+(b.x-bb.minX+.5)*scale,y:(h-(bb.maxZ-bb.minZ+1)*scale)/2+(b.z-bb.minZ+.5)*scale}}
function pickPlan(e){const c=$("#planCanvas"),r=c.getBoundingClientRect(),px=(e.clientX-r.left)/r.width*c.width,pz=(e.clientY-r.top)/r.height*c.height,geo=planGeometry(c),wx=Math.floor((px-geo.pad)/geo.scale-742),wz=Math.floor((pz-geo.pad)/geo.scale+746),y=+$("#planY").value,g=$("#planGroup")?$("#planGroup").value:"all",b=model.blocks.find(b=>b.x===wx&&b.z===wz&&b.y===y&&(g==="all"||b.group===g));$("#planInfo").textContent=b?`X=${wx}, Y=${y}, Z=${wz} · minecraft:${b.block} · ${b.group}`:`X=${wx}, Y=${y}, Z=${wz} · in diesem Layer kein Block geplant.`}
function itemUnits(n){const sh=Math.floor(n/1728),rem=n%1728,st=Math.floor(rem/64),loose=rem%64;return {sh,st,loose}}
function unitsText(n){const u=itemUnits(n),parts=[];if(u.sh)parts.push(`${u.sh} Shulker`);if(u.st)parts.push(`${u.st} Stacks`);if(u.loose)parts.push(`${u.loose} einzeln`);return parts.join(" + ")||"0"}
function materialCsvRows(){return Object.entries(model.counts).sort((a,b)=>b[1]-a[1])}
function csvMaterials(){return [["Minecraft-Block-ID","Material","Anzahl","Shulkerboxen","Stacks nach Shulkern","Einzelne Items"],...materialCsvRows().map(([k,n])=>{const u=itemUnits(n);return ["minecraft:"+k,model.palette[k]?.name||k,n,u.sh,u.st,u.loose]})].map(r=>r.join(";")).join("\n")}
function csvGroups(){const rows=[["Baugruppe","Minecraft-Block-ID","Material","Anzahl","Shulkerboxen","Stacks nach Shulkern","Einzelne Items"]],map={};for(const b of model.blocks){map[b.group]??={};map[b.group][b.block]=(map[b.group][b.block]||0)+1}for(const g of Object.keys(map).sort())for(const [k,n] of Object.entries(map[g]).sort((a,b)=>b[1]-a[1])){const u=itemUnits(n);rows.push([g,"minecraft:"+k,model.palette[k]?.name||k,n,u.sh,u.st,u.loose])}return rows.map(r=>r.join(";")).join("\n")}
function renderMaterials(){
 if(!model)return;const q=$("#blockSearch").value.toLowerCase(),arr=materialCsvRows().filter(([k,n])=>(k+" "+(model.palette[k]?.name||k)).toLowerCase().includes(q));
 if($("#materialSort").value==="name")arr.sort((a,b)=>a[0].localeCompare(b[0]));
 $("#materialRows").innerHTML=arr.map(([k,n])=>{const u=itemUnits(n);return `<tr><td><span class="swatch" style="background:${model.palette[k]?.color||"#aaa"}"></span>${model.palette[k]?.name||k}</td><td>minecraft:${k}</td><td>${fmt(n)}</td><td>${u.sh?u.sh+" Shulker · ":""}${u.st?u.st+" Stacks · ":""}${u.loose?u.loose+" einzeln":""}</td><td><div class="bar"><i style="width:${n/model.total_blocks*100}%"></i></div></td></tr>`}).join("");
}
function renderCoords(){const q=$("#coordSearch").value.toLowerCase().trim(),arr=model.blocks.filter(b=>!q||(`${b.x} ${b.y} ${b.z} ${b.block} ${b.group}`).toLowerCase().includes(q)).slice(0,500);$("#coordRows").innerHTML=arr.map(b=>`<tr><td>${b.x}</td><td>${b.y}</td><td>${b.z}</td><td>minecraft:${b.block}</td><td>${b.group}</td></tr>`).join("");$("#coordResult").textContent=arr.length+" Treffer (max. 500 angezeigt)"}
function renderBuildGroups(){const gs=Object.keys(model.groups).sort();$("#buildGroups").innerHTML=gs.map(g=>`<article class="build-group"><h3>${g.replaceAll("_"," ")}</h3><small>${fmt(model.groups[g])} Blockpositionen</small><label><input type="checkbox" data-group="${g}" ${saved[g]?"checked":""}> Baugruppe fertiggestellt</label></article>`).join("");$("#buildGroups").onchange=e=>{if(e.target.matches("input")){saved[e.target.dataset.group]=e.target.checked;localStorage.setItem("blackthorn-v4-progress",JSON.stringify(saved));updateProgress()}};updateProgress()}
function updateProgress(){const gs=Object.keys(model.groups),done=gs.filter(g=>saved[g]).length,p=Math.round(done/gs.length*100);$("#progressBar").style.width=p+"%";$("#progressLabel").textContent=p+" % · "+done+"/"+gs.length+" Baugruppen"}
function downloadCSV(){download("blackthorn-blockliste.csv",["X;Y;Z;Minecraft-Block-ID;Baugruppe",...model.blocks.map(b=>`${b.x};${b.y};${b.z};minecraft:${b.block};${b.group}`)].join("\n"),"text/csv;charset=utf-8")}
function download(name,data,type){const a=document.createElement("a"),url=URL.createObjectURL(new Blob(["\ufeff",data],{type}));a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function drawAll(){updateLayerLabel();renderCoords()}
