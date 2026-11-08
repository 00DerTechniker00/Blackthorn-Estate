(() => {
 'use strict';
 const $=id=>document.getElementById(id),D=window.BLACKTHORN_DATA,escape=BT.escape;
 const names=['Ungeprüft','Richtig','Fehlt','Anderer Block','Blockzustand weicht ab'];
 const positions=[];
 for(const [y,z,x,n,ri] of D.runs)for(let dx=0;dx<n;dx++)positions.push({x:x+dx,y,z,ri});
 let code='',snapshot=null,busy=false,generation=0,environment='';
 function status(message,error=false){$('liveStatus').textContent=message;$('liveStatus').classList.toggle('error',error);}
 function age(){
  if(!snapshot)return;
  const seconds=Math.max(0,Math.floor((Date.now()-snapshot.receivedAt)/1000));
  status((environment==='production'?'Production':'Testumgebung')+' · Übertragung vor '+seconds+' Sekunden · Prüfung vom '+new Date(snapshot.sampledAt).toLocaleString('de-DE')+(seconds>45?' · VERALTETER STAND: Verbindung oder Server prüfen.':''),seconds>45);
 }
 function render(){
  if(!snapshot)return;
  const totals=[0,0,0,0,0],groups=D.groups.map(()=>({total:0,correct:0,unknown:0}));
  positions.forEach((p,i)=>{const state=Number(snapshot.states[i]),g=groups[D.reg[p.ri][2]];totals[state]++;g.total++;if(state===1)g.correct++;if(state===0)g.unknown++;});
  $('liveTotals').innerHTML=totals.map((n,i)=>`<div class="stat live-state-${i}"><b>${n.toLocaleString('de-DE')}</b><span>${names[i]}${i===1?' · '+(100*n/positions.length).toFixed(1)+'% gesamt':''}</span></div>`).join('');
  $('liveGroups').innerHTML=groups.map((g,i)=>{const percent=(100*g.correct/g.total).toFixed(1);return `<tr><td>${escape(window.__groupName?.(D.groups[i])||D.groups[i])}</td><td>${g.correct.toLocaleString('de-DE')} / ${g.total.toLocaleString('de-DE')}</td><td><progress max="${g.total}" value="${g.correct}" aria-label="Fortschritt ${escape(D.groups[i])}"></progress> ${percent}%</td><td>${g.unknown.toLocaleString('de-DE')}</td></tr>`;}).join('');
  renderPositions();age();
 }
 function renderPositions(){
  if(!snapshot)return;
  const y=Number($('liveY').value),filter=$('liveFilter').value;
  const matches=[];positions.forEach((p,i)=>{const s=snapshot.states[i];if(p.y===y&&(filter==='all'||filter==='errors'&&Number(s)>=2||filter===s))matches.push(i);});
  $('liveRowSummary').textContent=matches.length+' Positionen auf Y '+y+' · maximal 200 auf einmal angezeigt';
  $('livePositions').innerHTML=matches.slice(0,200).map(i=>{const p=positions[i],s=Number(snapshot.states[i]);return `<tr><td>X ${p.x} · Y ${p.y} · Z ${p.z}</td><td>${escape(D.reg[p.ri][0])}<small class="cell-note">${escape(D.reg[p.ri][1])}</small></td><td class="live-state-${s}">${names[s]}</td><td><button type="button" class="mini" data-live-position="${i}">In 3D ansehen</button></td></tr>`;}).join('')||'<tr><td colspan="4">Keine Positionen für diese Auswahl.</td></tr>';
 }
 async function refresh(){
  if(busy||!code)return;busy=true;const run=generation;$('liveRefresh').disabled=true;$('liveLogin').querySelector('button').disabled=true;
  try{
   const response=await fetch('/api/build-progress',{headers:{Authorization:'Bearer '+code},cache:'no-store',signal:AbortSignal.timeout(12000)});
   let data;try{data=await response.json();}catch{throw Error('Live-API nicht erreichbar. Bitte das aktuelle Atlas-Deployment prüfen.');}
   if(run!==generation)return;
   if(!response.ok)throw Object.assign(Error(data.error||'Abruf fehlgeschlagen.'),{status:response.status});
   if(data.plan.fingerprint!==D.meta.fingerprint)throw Error('Bauplan wurde aktualisiert. Website neu laden.');
   if(data.snapshot&&(data.snapshot.states.length!==positions.length||/[^0-4]/.test(data.snapshot.states)))throw Error('Ungültiger Server-Prüfstand.');
   $('liveLogin').hidden=true;$('liveSession').hidden=false;environment=data.environment;
   try{sessionStorage.setItem('blackthorn:live:code',code);}catch{}
   snapshot=data.snapshot;$('liveWorkspace').hidden=!snapshot;
   if(snapshot)render();else status('Noch kein Prüfstand für Bauplan '+data.plan.revision+' ('+data.plan.positions.toLocaleString('de-DE')+' Positionen). Auf dem Server /blackthornlive status prüfen. Ab Plugin 1.4.0: /blackthornlive sync lädt den aktuellen Plan. Bei HTTP 401 den separaten Schreibtoken prüfen.');
  }catch(e){if(run!==generation)return;status(e.message+(snapshot?' Der letzte empfangene Stand bleibt sichtbar.':''),true);if(e.status===401){code='';snapshot=null;$('liveWorkspace').hidden=true;$('liveLogin').hidden=false;$('liveSession').hidden=true;try{sessionStorage.removeItem('blackthorn:live:code');}catch{}}}
  finally{busy=false;$('liveRefresh').disabled=false;$('liveLogin').querySelector('button').disabled=false;}
 }
 $('liveLogin').onsubmit=e=>{e.preventDefault();code=$('liveCode').value;$('liveCode').value='';generation++;refresh();};
 $('liveRefresh').onclick=refresh;
 $('liveLogout').onclick=()=>{generation++;code='';snapshot=null;$('liveWorkspace').hidden=true;$('liveSession').hidden=true;$('liveLogin').hidden=false;try{sessionStorage.removeItem('blackthorn:live:code');}catch{}status('Abgemeldet.');};
 $('liveY').onchange=renderPositions;$('liveFilter').onchange=renderPositions;
 $('livePositions').onclick=e=>{const button=e.target.closest('[data-live-position]');if(button){const p=positions[Number(button.dataset.livePosition)];window.__focusBlock(p.x,p.y,p.z);}};
 const active=()=>!document.hidden&&$('tab-live').classList.contains('on');
 setInterval(()=>{if(active())refresh();},10000);
 window.addEventListener('bt:tab',()=>{if(active())refresh();});
 document.addEventListener('visibilitychange',()=>{if(active())refresh();});
 window.addEventListener('online',()=>{if(active())refresh();});
 $('liveY').min=D.meta.bbox[2];$('liveY').max=D.meta.bbox[3];
 if(location.protocol==='file:'){status('Live-Fortschritt ist auf der veröffentlichten Website verfügbar.');$('liveLogin').querySelector('button').disabled=true;}
 else{try{code=sessionStorage.getItem('blackthorn:live:code')||sessionStorage.getItem('blackthorn:shared:code:v1')||'';}catch{}if(code&&active())refresh();}
})();
