/* A single surveyed coordinate grid powers comparison, column work and profiles. */
(() => {
  'use strict';
  const $=s=>document.querySelector(s),D=window.BLACKTHORN_DATA,T=D.terrain,safe=BT.escape;
  const [x0,x1,z0,z1]=T.bounds,w=x1-x0+1,h=z1-z0+1,canvas=$('#geologyCanvas'),ctx=canvas.getContext('2d');
  const bitmap=document.createElement('canvas');bitmap.width=w;bitmap.height=h;const bc=bitmap.getContext('2d');
  const work=new Map(T.work.map(r=>[r[0]+','+r[1],r])),spans={cut:new Map(),fill:new Map()};
  for(const [kind,key] of [['cut','cut_spans'],['fill','fill_spans']])for(const [x,z,a,b] of T[key]){const k=x+','+z;spans[kind].set(k,[...(spans[kind].get(k)||[]),[a,b]]);}
  const palette={water:[61,121,170],grass_block:[100,144,81],stone:[133,139,139],dirt:[145,111,77],gravel:[180,170,143],stone_bricks:[153,159,155],iron_block:[206,214,210],dark_oak_planks:[97,73,45]};
  const min=Math.min(...T.heights.map(r=>Math.min(...r))),max=Math.max(...T.heights.map(r=>Math.max(...r)));
  let scale=3,ox=0,oz=0,ready=false,drag=null,selected={x:-745,z:790};
  const targetMaterial=(x,z)=>T.target_surface_blocks[z-z0][x-x0];
  function pixel(x,z,mode){const row=work.get(x+','+z),old=T.heights[z-z0][x-x0],target=T.target_heights[z-z0][x-x0];
    let color=palette[mode==='target'?targetMaterial(x,z):T.surface_blocks[z-z0][x-x0]]||[112,126,109];
    if(mode==='height'){const v=(old-min)/Math.max(1,max-min);color=[65+v*145,82+v*110,135-v*70];}
    if(mode==='earthworks')color=row?(row[4]&&row[5]?[167,124,185]:row[4]?[230,130,59]:row[5]?[53,171,163]:[185,174,105]):[59,78,63];
    if(mode==='delta'){const delta=target-old;color=delta>0?[44,Math.min(235,100+delta*8),165]:delta<0?[Math.min(240,115-delta*6),98,52]:[77,94,77];}
    if(mode==='surface'||mode==='target'||mode==='compare'){
      const H=mode==='target'?T.target_heights:T.heights,iz=z-z0,ix=x-x0;
      const slope=(H[iz]?.[Math.max(0,ix-1)]??old)-(H[Math.max(0,iz-1)]?.[ix]??old);
      const shade=Math.max(.76,Math.min(1.1,1+slope*.025));color=color.map(v=>Math.min(255,v*shade));
    }
    return color;
  }
  function redraw(){const mode=$('#geologyMode').value,ratio=Number($('#earthCompare').value)/100,image=bc.createImageData(w,h);
    $('#compareControl').hidden=mode!=='compare';$('#earthLegend').hidden=!['earthworks','delta'].includes(mode);
    $('#earthLegend').innerHTML=mode==='delta'?'<span><i class="swatch cut"></i>Soll tiefer</span><span><i class="swatch fill"></i>Soll höher</span><span>Grau: gleiche Bodenhöhe</span>':'<span><i class="swatch cut"></i>Abtrag</span><span><i class="swatch fill"></i>Auffüllung</span><span><i class="swatch mixed"></i>Beides in derselben Spalte</span><span><i class="swatch skin"></i>Oberfläche gestalten</span>';
    for(let iz=0;iz<h;iz++)for(let ix=0;ix<w;ix++){
      const m=mode==='compare'?(ix<w*ratio?'surface':'target'):mode,color=pixel(ix+x0,iz+z0,m),i=(iz*w+ix)*4;
      image.data[i]=color[0];image.data[i+1]=color[1];image.data[i+2]=color[2];image.data[i+3]=255;
    }bc.putImageData(image,0,0);draw();
  }
  function fit(){const r=canvas.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);canvas.width=Math.max(300,Math.round(r.width*dpr));canvas.height=Math.max(280,Math.round(r.height*dpr));scale=Math.min((canvas.width-48)/w,(canvas.height-55)/h);ox=(canvas.width-w*scale)/2;oz=(canvas.height-h*scale)/2;draw();}
  function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.imageSmoothingEnabled=false;ctx.drawImage(bitmap,ox,oz,w*scale,h*scale);
    if($('#earthHouse').checked){ctx.fillStyle='rgba(242,231,199,.32)';for(const [x,z] of T.house_footprint)ctx.fillRect(ox+(x-x0)*scale,oz+(z-z0)*scale,scale+.1,scale+.1);}
    const line=(points,color)=>{if($('#geologyMode').value==='surface')return;ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();let pen=false;for(const [x,z] of points){if($('#geologyMode').value==='compare'&&x<x0+w*Number($('#earthCompare').value)/100){pen=false;continue;}ctx[pen?'lineTo':'moveTo'](ox+(x-x0+.5)*scale,oz+(z-z0+.5)*scale);pen=true;}ctx.stroke();};
    line(T.waypoints,'#f3ddab');line(T.garden_path,'#eee5bd');
    const px=ox+(selected.x-x0+.5)*scale,pz=oz+(selected.z-z0+.5)*scale;
    ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.strokeRect(px-5,pz-5,10,10);ctx.strokeStyle='#253e32';ctx.lineWidth=1;ctx.strokeRect(px-7,pz-7,14,14);
    if($('#geologyMode').value==='compare'){
      const x=ox+w*scale*Number($('#earthCompare').value)/100;ctx.strokeStyle='#fff';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(x,oz);ctx.lineTo(x,oz+h*scale);ctx.stroke();
      ctx.fillStyle='#233b31';ctx.fillRect(x-49,oz+8,98,25);ctx.fillStyle='#fff';ctx.font='11px system-ui';ctx.fillText('Ist  ←  →  Soll',x-38,oz+25);
    }
    ctx.fillStyle='#233b31';ctx.fillRect(5,3,265,25);ctx.fillStyle='#e9eadb';ctx.font='12px system-ui';ctx.fillText('N ↑  ·  W ← X → O  ·  Z nach Süden',12,20);
  }
  function profile(){const alongX=$('#earthAxis').value==='x',center=alongX?selected.x:selected.z,lo=Math.max(alongX?x0:z0,center-28),hi=Math.min(alongX?x1:z1,center+28);
    const points=[];for(let k=lo;k<=hi;k++){const x=alongX?k:selected.x,z=alongX?selected.z:k;points.push([k,T.heights[z-z0][x-x0],T.target_heights[z-z0][x-x0]]);}
    const low=Math.min(...points.flatMap(p=>p.slice(1)))-2,high=Math.max(...points.flatMap(p=>p.slice(1)))+3;
    const X=k=>32+(k-lo)/(hi-lo)*392,Y=y=>147-(y-low)/(high-low)*120;
    const path=i=>points.map(p=>X(p[0]).toFixed(1)+','+Y(p[i]).toFixed(1)).join(' ');
    const axis=alongX?'X':'Z',px=X(center);
    $('#earthProfile').innerHTML=`<svg viewBox="0 0 450 180" role="img" aria-label="Geländeprofil entlang ${axis}, von ${lo} bis ${hi}; grau Original, grün Planung"><line x1="32" y1="147" x2="424" y2="147" stroke="currentColor" opacity=".3"/><polyline points="${path(1)}" fill="none" stroke="#9b9990" stroke-width="2"/><polyline points="${path(2)}" fill="none" stroke="#408778" stroke-width="3"/><line x1="${px}" y1="18" x2="${px}" y2="149" stroke="currentColor" opacity=".4" stroke-dasharray="3 4"/><text x="2" y="28">${high}</text><text x="2" y="150">${low}</text><text x="32" y="172">${axis} ${lo}</text><text x="345" y="172">${axis} ${hi}</text></svg>`;
  }
  function choose(x,z){if(!Number.isInteger(x)||!Number.isInteger(z)||x<x0||x>x1||z<z0||z>z1){$('#geologyHover').textContent='Bitte ganzzahlige Koordinaten innerhalb X −825…−545 / Z 680…900 wählen.';return false;}
    selected={x,z};$('#earthX').value=x;$('#earthZ').value=z;
    const k=x+','+z,row=work.get(k),old=T.heights[z-z0][x-x0],target=T.target_heights[z-z0][x-x0],cut=row?.[4]||0,fill=row?.[5]||0;
    const range=kind=>(spans[kind].get(k)||[]).map(([a,b])=>a===b?'Y '+a:'Y '+a+'…'+b).join(', ')||'keine Position';
    $('#earthZone').textContent=row?.[6]||'Unverändertes Gelände';
    $('#earthColumn').innerHTML=`<div class="column-heights"><div><small>IST-BODEN</small><b>Y ${old}</b></div><span>→</span><div><small>SOLL-BODEN</small><b>Y ${target}</b></div></div><p class="muted">Oberfläche: ${safe(targetMaterial(x,z).replace(/_/g,' '))}</p><ol class="column-jobs"><li><i class="swatch cut"></i><b>${cut} Blöcke abtragen</b><small>${range('cut')}</small></li><li><i class="swatch fill"></i><b>${fill} Blöcke auffüllen</b><small>${range('fill')}</small></li><li><i class="swatch skin"></i><b>${row?'Oberfläche nach Blockliste herstellen':'Oberfläche erhalten'}</b><small>Gras-/Erdhaut und Wege sind als echte Baublöcke erfasst.</small></li></ol>`;
    $('#geologyHover').textContent=`Ausgewählt: X ${x} / Z ${z} · Ist Y ${old} → Soll Y ${target} · ${cut} Abtrag / ${fill} Auffüllung`;
    profile();draw();return true;
  }
  function chunks(){const mode=$('#earthChunkFilter').value,rows=T.chunks.filter(r=>mode==='all'||mode==='cut'&&r[3]>0||mode==='fill'&&r[4]>0);
    $('#earthChunks').innerHTML=rows.map(([x,z,n,cut,fill])=>`<tr><td><b>${x} / ${z}</b></td><td><small>X ${x*16}…${x*16+15}<br>Z ${z*16}…${z*16+15}</small></td><td>${n}</td><td>${cut.toLocaleString('de-DE')}</td><td>${fill.toLocaleString('de-DE')}</td><td><button class="mini" data-chunk-x="${x}" data-chunk-z="${z}">Zeigen</button></td></tr>`).join('');
  }
  $('#earthChunks').onclick=e=>{if(e.target.dataset.chunkX===undefined)return;choose(Math.min(x1,Math.max(x0,Number(e.target.dataset.chunkX)*16+8)),Math.min(z1,Math.max(z0,Number(e.target.dataset.chunkZ)*16+8)));};
  $('#earthCoords').onsubmit=e=>{e.preventDefault();choose(Number($('#earthX').value),Number($('#earthZ').value));};
  $('#geologyMode').onchange=redraw;$('#earthCompare').oninput=redraw;$('#earthHouse').onchange=draw;$('#earthAxis').onchange=profile;$('#earthChunkFilter').onchange=chunks;$('#geologyReset').onclick=fit;
  $('#earth3d').onclick=()=>window.__openTerrain('work');$('#earthFocus').onclick=()=>window.__openTerrain('target',selected.x,selected.z);
  for(const b of document.querySelectorAll('[data-outdoor]'))b.onclick=()=>{const s=D.outdoor_sites[Number(b.dataset.outdoor)];window.__openTerrain('target',s.x,s.z,false);};
  function coord(e){const r=canvas.getBoundingClientRect(),px=(e.clientX-r.left)*canvas.width/r.width,pz=(e.clientY-r.top)*canvas.height/r.height;return {px,pz,x:Math.floor((px-ox)/scale)+x0,z:Math.floor((pz-oz)/scale)+z0};}
  canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);drag=[e.clientX,e.clientY,ox,oz];});
  canvas.addEventListener('pointermove',e=>{if(drag){ox=drag[2]+(e.clientX-drag[0])*canvas.width/canvas.clientWidth;oz=drag[3]+(e.clientY-drag[1])*canvas.height/canvas.clientHeight;draw();}});
  canvas.addEventListener('pointerup',e=>{const moved=drag&&Math.hypot(e.clientX-drag[0],e.clientY-drag[1])>5;drag=null;if(!moved){const p=coord(e);choose(p.x,p.z);}});canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('wheel',e=>{e.preventDefault();const {px,pz}=coord(e),next=Math.min(35,Math.max(.5,scale*(e.deltaY<0?1.12:.89))),x=(px-ox)/scale,z=(pz-oz)/scale;scale=next;ox=px-x*scale;oz=pz-z*scale;draw();},{passive:false});
  function visible(){if(!$('#tab-terrain').classList.contains('on'))return;if(!ready){ready=true;fit();redraw();}else fit();}
  window.addEventListener('bt:tab',visible);window.addEventListener('resize',()=>{if(ready)visible();});
  window.__earth={choose,pixel,selection:()=>({...selected})};chunks();choose(selected.x,selected.z);redraw();
  if(location.hash==='#terrain')setTimeout(visible,0);
})();
