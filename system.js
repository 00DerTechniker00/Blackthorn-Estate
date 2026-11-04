
(() => {
'use strict';
const d=JSON.parse(document.getElementById('data').textContent),S=d.storage_system;
const $=s=>document.querySelector(s);
const row=(label,x,y,z,extra='')=>`<div class="sys-mat-row"><b>${label}</b><span>X ${x}, Y ${y}, Z ${z}${extra?' · '+extra:''}</span></div>`;
$('#sysBulk').innerHTML=S.bulk.map(b=>row(b.label,b.x,b.y,b.z,b.id)).join('');
$('#sysRegular').innerHTML=S.regular.map(b=>row(b.label,b.x,b.y,b.z)).join('');
$('#sysStalls').innerHTML=S.stalls.map(v=>row(v.id+' · '+v.profession,v.x,v.y,v.z,v.workstation)).join('');
const c=$('#sysMap'),ctx=c.getContext('2d'),info=$('#sysInfo'),markers=[];
const ext={x0:-724,x1:-669,z0:765,z1:815},dx=(c.width-100)/(ext.x1-ext.x0+1),dz=(c.height-80)/(ext.z1-ext.z0+1),scale=Math.min(dx,dz);
const px=x=>70+(x-ext.x0)*scale,pz=z=>40+(z-ext.z0)*scale;
function rect(x0,z0,x1,z1,color,label){ctx.fillStyle=color;ctx.fillRect(px(x0),pz(z0),(x1-x0+1)*scale,(z1-z0+1)*scale);if(label){ctx.fillStyle='#fff';ctx.font='13px system-ui';ctx.fillText(label,px(x0)+6,pz(z0)+16)}}
function pin(x,y,z,title,color='#f4c76d'){
 const X=px(x)+scale/2,Z=pz(z)+scale/2;ctx.beginPath();ctx.arc(X,Z,5.5,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();ctx.strokeStyle='#14231c';ctx.lineWidth=1.5;ctx.stroke();markers.push({X,Z,x,y,z,title});
}
function render(){const level=+$('#sysLevel').value;markers.length=0;ctx.clearRect(0,0,c.width,c.height);ctx.fillStyle='#13231d';ctx.fillRect(0,0,c.width,c.height);
 ctx.strokeStyle='#27372f';ctx.lineWidth=.7;for(let x=ext.x0;x<=ext.x1;x+=5){ctx.beginPath();ctx.moveTo(px(x),pz(ext.z0));ctx.lineTo(px(x),pz(ext.z1+1));ctx.stroke();}for(let z=ext.z0;z<=ext.z1;z+=5){ctx.beginPath();ctx.moveTo(px(ext.x0),pz(z));ctx.lineTo(px(ext.x1+1),pz(z));ctx.stroke();}
 ctx.fillStyle='#ccd8ca';ctx.font='13px system-ui';ctx.fillText('X → Osten',68,22);ctx.fillText('Z → Süden',730,22);
 rect(-721,767,-671,786,'#253a30','Nordräume');rect(-721,788,-671,792,'#4d4832','Mittelgang');rect(-721,794,-671,813,'#263a35','Südräume');
 if(level===121){rect(-706,767,-675,784,'#514c35','Bulklager');rect(-694,795,-671,812,'#214f46','Golems');pin(S.input.x,S.input.y,S.input.z,'Einziger Einwurf','#ffcc55');for(const b of S.bulk)pin(b.x,b.y,b.z,'Bulk: '+b.label,'#ffb366');for(const r of S.regular)pin(r.x,r.y,r.z,'Golem: '+r.label,'#65c9b5');pin(-675,123,797,'Kupfertruhe','#55a9ff')}
 if(level===113){rect(-682,768,-672,784,'#514c35','Zusatzlager');for(const x of [-680,-677,-674])pin(x,115,775,'Überlauf- und Shulkerlager','#e1b86c')}
 if(level===105){rect(-706,767,-684,786,'#514c35','Trading Hall');rect(-694,794,-684,813,'#3e304f','Geheimlounge');for(const v of S.stalls)pin(v.x,v.y,v.z,v.id+' · '+v.profession,'#65c9b5');for(const s of S.secrets)pin(s.x,s.y,s.z,s.name,'#d98ef1')}
}
function pick(e){const b=c.getBoundingClientRect(),mx=(e.clientX-b.left)*c.width/b.width,mz=(e.clientY-b.top)*c.height/b.height;let closest=null,dist=1e12;for(const p of markers){const dd=(p.X-mx)**2+(p.Z-mz)**2;if(dd<dist){dist=dd;closest=p}}if(closest&&dist<230){info.textContent=`${closest.title} · X=${closest.x}, Y=${closest.y}, Z=${closest.z}`;return}const x=Math.floor((mx-70)/scale+ext.x0),z=Math.floor((mz-40)/scale+ext.z0);info.textContent=`X=${x}, Z=${z} · Kellerboden Y=${$('#sysLevel').value}`;}
c.addEventListener('mousemove',pick);c.addEventListener('click',pick);$('#sysLevel').addEventListener('change',render);
$('#sysGotoInput').onclick=()=>{document.querySelector('#tabs button[data-tab="plan"]').click();const mode=$('#planMode');mode.value='y';mode.dispatchEvent(new Event('change'));$('#planRange').value=124;$('#planRange').dispatchEvent(new Event('input'))};
$('#sysGotoTrade').onclick=()=>{document.querySelector('#tabs button[data-tab="plan"]').click();const mode=$('#planMode');mode.value='y';mode.dispatchEvent(new Event('change'));$('#planRange').value=106;$('#planRange').dispatchEvent(new Event('input'))};
render();
})();
