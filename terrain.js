
(() => {
 'use strict';
 const doc=document; const D=JSON.parse(doc.getElementById('data').textContent);
 const T=D.terrain, [x0,x1,z0,z1]=T.bounds;
 const c=doc.getElementById('geologyCanvas');const info=doc.getElementById('geologyHover');
 let ready=false,offsetX=0,offsetZ=0,zoom=5;
 const grass=['grass_block'], palette={grass_block:'#659c5c',dirt:'#896a4b',stone:'#8a8b8a',andesite:'#92918b',dripstone_block:'#756d67'};
 const cw=x1-x0+1,ch=z1-z0+1;
 const M=T.surface_blocks,H=T.heights, EX=T.excavate||[];
 const excMap=new Map(EX.map(r=>[r[0]+','+r[1],{cut:r[2],count:r[3],near:r[4]||''}]));
 const voidMap=new Map();for(const [x,z,a,b] of T.cave_spans)if(b>=99){const k=x+','+z;const v=voidMap.get(k)||[];v.push([a,b]);voidMap.set(k,v)}
 let used=doc.createElement('canvas');used.width=cw;used.height=ch;const us=used.getContext('2d');const img=us.createImageData(cw,ch);
 const hcolor=h=>{const t=Math.min(1,Math.max(0,(h-60)/70));return [Math.floor(65+130*t),Math.floor(75+110*t),Math.floor(100-55*t)]};
 function redrawMap(){
  const mode=doc.getElementById('geologyMode').value;
  for(let z=0;z<ch;z++)for(let x=0;x<cw;x++){
   const id=(z*cw+x)*4,name=M[z]?.[x]||'unknown',y=H[z]?.[x]||0,worldX=x+x0,worldZ=z+z0;
   let rgb;
   if(mode==='height')rgb=hcolor(y);
   else if(mode==='caves')rgb=voidMap.has(worldX+','+worldZ)?[216,99,82]:[65,84,69];
   else if(mode==='plants')rgb=name==='grass_block'?[92,141,82]:[125,112,88];
   else if(mode==='excavation'){ const ex=excMap.get(worldX+','+worldZ); rgb = ex ? [194,133,67] : [55,69,59]; }
   else rgb= name==='grass_block'?[93,152,88]:name==='stone'?[142,142,143]:name==='dirt'?[142,103,75]:[119,126,120];
   img.data.set([...rgb,255],id);
  }
  us.putImageData(img,0,0);render();
 }
 function fit(){const r=c.getBoundingClientRect();c.width=Math.max(300,Math.floor(r.width*devicePixelRatio));c.height=Math.max(240,Math.floor(r.height*devicePixelRatio));zoom=Math.min((c.width-60)/cw,(c.height-60)/ch);offsetX=(c.width-cw*zoom)/2;offsetZ=(c.height-ch*zoom)/2;render()}
 function render(){if(!ready)return;const ctx=c.getContext('2d');ctx.clearRect(0,0,c.width,c.height);ctx.imageSmoothingEnabled=false;ctx.drawImage(used,offsetX,offsetZ,cw*zoom,ch*zoom);
  const rect=(xa,za,xb,zb,color)=>{ctx.strokeStyle=color;ctx.lineWidth=Math.max(2,devicePixelRatio);ctx.strokeRect(offsetX+(xa-x0)*zoom,offsetZ+(za-z0)*zoom,(xb-xa+1)*zoom,(zb-za+1)*zoom)};
  rect(-742,747,-637,833,'#e2c695');rect(-646,787,-629,800,'#68c7ed');rect(-746,779,-723,810,'#9facff');
  if(doc.getElementById('geologyMode').value==='excavation'){ ctx.fillStyle='rgba(194,133,67,.35)'; for(const r of EX){ const xx=offsetX+(r[0]-x0)*zoom, zz=offsetZ+(r[1]-z0)*zoom; ctx.fillRect(xx,zz,zoom,zoom);} }
  ctx.fillStyle='#f4e8c8';ctx.font=Math.max(11,11*devicePixelRatio)+'px sans-serif';ctx.fillText('Eingang / Plateau →',Math.max(4,offsetX+105*zoom),Math.max(18,offsetZ+16*zoom));ctx.fillText('← Klippe / Pool',Math.max(4,offsetX+5),Math.max(18,offsetZ+32*zoom));
 }
 function hit(evt){const r=c.getBoundingClientRect();let px=(evt.clientX-r.left)/r.width*c.width,pz=(evt.clientY-r.top)/r.height*c.height;const i=Math.floor((px-offsetX)/zoom),j=Math.floor((pz-offsetZ)/zoom);if(i<0||i>=cw||j<0||j>=ch){info.textContent='Außerhalb des vermessenen Bereichs';return}const x=i+x0,z=j+z0,name=M[j][i],y=H[j][i];const v=voidMap.get(x+','+z)||[]; const ex=excMap.get(x+','+z); info.innerHTML=`<b>X=${x}, Z=${z}</b> · Oberster Bodenblock: <b>minecraft:${name}</b> bei <b>Y=${y}</b>. ${ex?`<br><b>Aushub:</b> bis Y=${ex.cut}, ca. ${ex.count} Blöcke in dieser Spalte${ex.near?` · nahe ${ex.near}`:''}.`:''} ${v.length?'<br>Luftspalten: '+v.map(a=>a.join('–')).join(', ')+' (weitere in CSV)':'<br>Keine hohen Luftspalten in der gezeigten Prüfkategorie.'}`;}
 let down=null;doc.getElementById('geologyMode').addEventListener('change', redrawMap);doc.getElementById('geologyReset').onclick=fit;c.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY,offsetX,offsetZ];c.setPointerCapture(e.pointerId)});
 c.addEventListener('pointermove',e=>{if(down){offsetX=down[2]+(e.clientX-down[0])*c.width/c.clientWidth;offsetZ=down[3]+(e.clientY-down[1])*c.height/c.clientHeight;render()}else hit(e)});
 c.addEventListener('pointerup',()=>{down=null});c.addEventListener('pointercancel',()=>{down=null});
 c.addEventListener('wheel',e=>{e.preventDefault();const next=Math.max(.8,Math.min(20,zoom*(e.deltaY<0?1.13:.88)));const rect=c.getBoundingClientRect(),mx=(e.clientX-rect.left)/rect.width*c.width,my=(e.clientY-rect.top)/rect.height*c.height;const a=(mx-offsetX)/zoom,b=(my-offsetZ)/zoom;zoom=next;offsetX=mx-a*zoom;offsetZ=my-b*zoom;render()},{passive:false});
 doc.getElementById('geologyMode').addEventListener('change',redrawMap);doc.getElementById('geologyReset').addEventListener('click',fit);
 const mc=Object.entries(T.surface_stats).sort((a,b)=>b[1]-a[1]).slice(0,8);
 const pc=Object.entries(T.vegetation_stats).sort((a,b)=>b[1]-a[1]).slice(0,7);
 doc.getElementById('geologyMaterials').innerHTML='<p><b>Bodenmaterialien:</b> '+mc.map(([n,v])=>`<code>${n}</code>: ${v.toLocaleString('de-DE')}`).join(', ')+'</p><p><b>Vegetation oberhalb des Bodens:</b> '+pc.map(([n,v])=>`<code>${n}</code>: ${v.toLocaleString('de-DE')}`).join(', ')+'</p>';
 // Original tabs are powered by existing script; initialize only when visible.
 function onTab(){if(!doc.getElementById('tab-terrain').classList.contains('on'))return;if(!ready){ready=true;fit();redrawMap()}else fit()}
 doc.querySelectorAll('[data-tab="terrain"]').forEach(btn=>btn.addEventListener('click',()=>setTimeout(onTab,0)));
 window.addEventListener('resize',()=>{if(ready&&doc.getElementById('tab-terrain').classList.contains('on'))fit()});
})();
