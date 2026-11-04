(() => {
  'use strict';
  const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],D=JSON.parse($('#data').textContent),safe=BT.escape;
  const routes={overview:['start','Start'], '3d':['atlas','Bauatlas'],plan:['atlas','Ebenenplan'],steps:['atlas','Baubegleitung'],rooms:['atlas','Raumbuch'],lighting:['atlas','Leuchtenplan'],terrain:['terrain','Gelände & Erdarbeiten'],storage:['storage','Lagerbestände'],system:['storage','Sortierung & Technik'],build:['organize','Baufortschritt'],material:['organize','Materialbedarf'],downloads:['organize','Dateien & Berichte']};
  const groupNames={start:'ÜBERSICHT',atlas:'BAUATLAS',terrain:'GELÄNDE',storage:'LAGER',organize:'ORGANISATION'};
  let menuOpen=false;
  function menu(open,focus=false){menuOpen=open;document.documentElement.classList.toggle('nav-open',open);$('#navScrim').hidden=!open;$('#menuButton').setAttribute('aria-expanded',String(open));$('#sidebar').inert=matchMedia('(max-width:760px)').matches&&!open;if(open)$('#tabs button').focus?.({preventScroll:true});if(!open&&focus)$('#menuButton').focus?.();}
  $('#menuButton').onclick=()=>menu(!menuOpen);$('#navScrim').onclick=()=>menu(false,true);
  window.addEventListener('keydown',e=>{if(e.key==='Escape'&&menuOpen)menu(false,true);});
  window.addEventListener('resize',()=>{$('#sidebar').inert=matchMedia('(max-width:760px)').matches&&!menuOpen;});
  function active(){return document.querySelector('.tab.on')?.id.replace('tab-','')||'overview';}
  function paint(){const id=active(),[group,title]=routes[id]||routes.overview;
    $('#viewTitle').textContent=title;$('#viewEyebrow').textContent='BLACKTHORN ESTATE / '+groupNames[group];
    document.title=title+' · Blackthorn Estate';
    $$('#tabs button').forEach(b=>{const on=b.dataset.group===group;b.classList.toggle('on',on);b.setAttribute('aria-current',on?'page':'false');});
    $$('#subtabs [data-subgroup]').forEach(row=>{row.hidden=row.dataset.subgroup!==group;});$('#subtabs').hidden=group==='start';
    $$('#subtabs button').forEach(b=>{const on=b.dataset.tab===id;b.classList.toggle('on',on);b.setAttribute('aria-current',on?'page':'false');});
    const wasOpen=menuOpen;menu(false);if(wasOpen)$('#main').focus?.({preventScroll:true});
    if(id==='lighting')renderLights();if(id==='3d')syncFloor();
  }
  window.addEventListener('bt:tab',paint);
  function saved(){const ok=BT.storageOK(),el=$('#globalSaveStatus');el.classList.toggle('error',!ok);
    el.innerHTML='<span class="status-dot"></span>'+(ok?'Speichert lokal':'Backup erforderlich');
    const done=Object.values(BT.state.groups).filter(Boolean).length,blocks=Object.keys(BT.state.blocks).length;
    $('#homeProgress').textContent=done+' Bauteile fertig · '+blocks.toLocaleString('de-DE')+' Blöcke abgehakt';
  }
  window.addEventListener('bt:saved',saved);window.addEventListener('bt:import',saved);
  const fixtures=D.lighting.fixtures;
  $('#lightLevel').innerHTML='<option value="all">Alle Höhenbereiche</option>'+['Keller 3','Keller 2','Keller 1','EG / Außen','OG / Halle'].map(level=>`<option value="${safe(level)}">${safe(level)}</option>`).join('');
  const blockName=id=>({iron_chain:'Eisenkette',iron_bars:'Eisengitter',stone_bricks:'Steinziegel',stone_brick_wall:'Steinziegelmauer',dark_oak_planks:'Schwarzeichenholz',spruce_planks:'Fichtenholz',spruce_slab:'Fichtenstufe',deepslate_tiles:'Tiefenschieferfliesen',polished_deepslate:'Polierter Tiefenschiefer',barrel:'Fass',bookshelf:'Bücherregal',dark_oak_fence:'Schwarzeichenzaun'}[id]||id.replace(/_/g,' '));
  function renderLights(){const q=$('#lightQuery').value.toLowerCase().trim(),level=$('#lightLevel').value,kind=$('#lightKind').value;
    const rows=fixtures.filter(f=>(level==='all'||f.level===level)&&(kind==='all'||(kind==='hanging')===f.hanging)&&
      (!q||(`${f.id} ${f.x} ${f.y} ${f.z} ${f.block} ${f.group} ${window.__groupName(f.group)} ${f.source}`).toLowerCase().includes(q)));
    $('#lightSummary').textContent=rows.length+' von '+fixtures.length+' Leuchten · Träger und Anschluss geprüft';
    $('#lightRows').innerHTML=rows.map(f=>`<tr><td><b class="light-id">${f.id}</b><small class="cell-note">${f.block==='soul_lantern'?'Seelenlaterne':'Laterne'}</small></td><td>${safe(window.__groupName(f.group))}<small class="cell-note">${safe(f.level)}</small></td><td class="light-coordinate">X ${f.x}<br>Y ${f.y} · Z ${f.z}</td><td>${safe(f.kind)}<small class="cell-note">${f.chain?f.chain+' Kettenblöcke → ':''}${safe(blockName(f.anchor_block))}</small></td><td><div class="light-actions"><button class="mini" data-light3d="${f.id}">3D</button><button class="mini" data-light-plan="${f.id}">Plan</button></div></td></tr>`).join('')||'<tr><td colspan="5" class="empty-state">Keine passende Leuchte. Suchbegriff oder Filter ändern.</td></tr>';
  }
  $('#lightQuery').oninput=renderLights;$('#lightLevel').onchange=renderLights;$('#lightKind').onchange=renderLights;
  $('#lightRows').onclick=e=>{const key=e.target.dataset.light3d||e.target.dataset.lightPlan;if(!key)return;const f=fixtures.find(x=>x.id===key);if(!f)return;
    if(e.target.dataset.light3d){window.__focusFixture(f);$('#sceneFloor').value='custom';}else window.__focusPlan(f.x,f.y,f.z);
  };
  function syncFloor(){const value=$('#cut').value;$('#sceneFloor').value=['157','143','136','127','119','111'].includes(value)?value:'custom';}
  $('#sceneFloor').onchange=e=>{if(e.target.value==='custom')return;window.__leaveFixture();$('#cut').value=e.target.value;$('#cut').dispatchEvent(new Event('input'));};
  $('#cut').addEventListener('input',syncFloor);$('#cutDown').addEventListener('click',syncFloor);$('#cutUp').addEventListener('click',syncFloor);
  $('#resetScene').onclick=()=>{window.__resetScene();$('#sceneFloor').value=String(D.meta.bbox[3]);$('#terrainState').value='target';$('#terrainState').dispatchEvent(new Event('change'));};
  $('#leaveDetail').onclick=()=>$('#resetScene').click();
  saved();renderLights();paint();
})();
