(() => {
  'use strict';
  const $=s=>document.querySelector(s),D=window.BLACKTHORN_DATA,S=D.storage_system;
  const fmt=n=>n.toLocaleString('de-DE');
  const row=(name,p,extra='')=>`<div class="sys-mat-row"><b>${name}</b><span>X ${p[0]} / Y ${p[1]} / Z ${p[2]}${extra?' · '+extra:''}</span></div>`;
  $('#sysBulk').innerHTML=S.bulk.map(b=>row(b.label,b.loose,'27 Stacks lose · 81 Shulkerplätze darunter')).join('');
  $('#sysRegular').innerHTML=S.regular.map(b=>row(b.label,[b.x,b.y,b.z],b.seeds.join(', '))).join('');
  $('#sysStations').innerHTML=S.stations.map(b=>row(b.name,b.active_box,'eigener Leerbox-/Rückgabeweg')).join('');
  $('#sysStalls').innerHTML=S.stalls.map(b=>row(b.id+' · '+b.profession,[b.x,b.y,b.z])).join('');
  $('#simItem').innerHTML=S.bulk.map(b=>`<option value="${b.id}">${b.label}</option>`).join('');
  function simulate(){try{
    const r=Logistics.bulk(Number($('#simAmount').value),Number($('#simBoxes').value));
    $('#simResult').textContent=`Loser Vorrat: ${fmt(r.ready)} Items · ${r.full_boxes} volle Boxen eingelagert · aktive Box: ${fmt(r.active_items)} Items · ${fmt(r.unaccepted)} Items noch nicht angenommen`+(r.blocked?' · STOPP: '+r.reason:'');
  }catch(e){$('#simResult').textContent=e.message;}}
  $('#simRun').onclick=simulate;simulate();
  const c=$('#sysMap'),ctx=c.getContext('2d'),bounds={x0:-716,x1:-651,z0:763,z1:817},scale=Math.min((c.width-70)/(bounds.x1-bounds.x0+1),(c.height-65)/(bounds.z1-bounds.z0+1));
  const px=x=>45+(x-bounds.x0+.5)*scale,pz=z=>35+(z-bounds.z0+.5)*scale;let markers=[];
  function pin(name,p,color){const [x,y,z]=p;ctx.fillStyle=color;ctx.beginPath();ctx.arc(px(x),pz(z),4.8,0,Math.PI*2);ctx.fill();markers.push({name,p,x:px(x),z:pz(z)});}
  function render(){const level=+$('#sysLevel').value;markers=[];ctx.clearRect(0,0,c.width,c.height);ctx.fillStyle='#13231c';ctx.fillRect(0,0,c.width,c.height);ctx.strokeStyle='#33463b';ctx.lineWidth=.5;
    for(let x=bounds.x0;x<=bounds.x1;x+=5){ctx.beginPath();ctx.moveTo(px(x),pz(bounds.z0));ctx.lineTo(px(x),pz(bounds.z1));ctx.stroke();}
    for(let z=bounds.z0;z<=bounds.z1;z+=5){ctx.beginPath();ctx.moveTo(px(bounds.x0),pz(z));ctx.lineTo(px(bounds.x1),pz(z));ctx.stroke();}
    ctx.fillStyle='#e2decf';ctx.font='13px system-ui';ctx.fillText('Norden ↑ · Osten → · Markierungen anklicken',40,20);
    if(level===121){pin('Einwurf',[S.input.x,S.input.y,S.input.z],'#f2ce79');for(const a of S.bulk)pin('Bulk '+a.label,a.loose,'#c69e73');for(const a of S.stations)pin(a.name,a.active_box,'#ba8ece');for(const a of S.regular)pin(a.label,[a.x,a.y,a.z],'#77c1ac');pin('Kupfer-Eingang',[S.copper_input.x,S.copper_input.y,S.copper_input.z],'#da8e53');}
    else {for(const a of D.storage_bays.filter(a=>a.floor===level))pin(a.id+' '+a.name,[a.x,a.y,a.z],'#cfbd8e');
      if(level===113)for(const a of S.bulk)for(const p of a.bins)pin('Gepackte Shulker: '+a.label,p,'#b08bc4');
      if(level===105)for(const a of S.stalls)pin(a.id,[a.x,a.y,a.z],'#80c4c0');}
  }
  function pick(e,open){const rect=c.getBoundingClientRect(),x=(e.clientX-rect.left)*c.width/rect.width,z=(e.clientY-rect.top)*c.height/rect.height;
    const closest=markers.map(p=>({...p,d:(p.x-x)**2+(p.z-z)**2})).sort((a,b)=>a.d-b.d)[0];
    if(closest&&closest.d<250){$('#sysInfo').textContent=`${closest.name} · X ${closest.p[0]} / Y ${closest.p[1]} / Z ${closest.p[2]}`;if(open)window.__focusPlan(...closest.p);}}
  c.addEventListener('pointermove',e=>pick(e,false));c.addEventListener('click',e=>pick(e,true));$('#sysLevel').onchange=render;render();
  $('#sysGotoInput').onclick=()=>window.__focusPlan(S.input.x,S.input.y,S.input.z);
  $('#sysGotoTrade').onclick=()=>{const p=S.stalls[0];window.__focusPlan(p.x,p.y,p.z);};
})();
