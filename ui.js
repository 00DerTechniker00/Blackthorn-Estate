(() => {
  'use strict';
  const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],D=window.BLACKTHORN_DATA,safe=BT.escape;
  const routes={overview:['start','Start'], '3d':['atlas','Bauatlas'],structure:['atlas','Hausstruktur'],plan:['atlas','Ebenenplan'],steps:['atlas','Baubegleitung'],rooms:['atlas','Raumbuch'],viewer:['atlas','Minecraft-Texturen'],lighting:['atlas','Leuchtenplan'],terrain:['terrain','Gelände & Erdarbeiten'],storage:['storage','Lagerbestände'],system:['storage','Sortierung & Technik'],build:['organize','Baufortschritt'],material:['organize','Materialbedarf'],live:['organize','Live-Baufortschritt'],shared:['organize','Gemeinsame Materialliste'],downloads:['organize','Dateien & Berichte']};
  const groupNames={start:'ÜBERSICHT',atlas:'BAUATLAS',terrain:'GELÄNDE',storage:'LAGER',organize:'ORGANISATION'};
  let menuOpen=false,keyboardRouting=false;
  function menu(open,focus=false){menuOpen=open;document.documentElement.classList.toggle('nav-open',open);$('#navScrim').hidden=!open;$('#menuButton').setAttribute('aria-expanded',String(open));$('#sidebar').inert=matchMedia('(max-width:760px)').matches&&!open;if(open)($('#tabs button[aria-selected="true"]')||$('#tabs button')).focus?.({preventScroll:true});if(!open&&focus)$('#menuButton').focus?.();}
  $('#menuButton').onclick=()=>menu(!menuOpen);$('#navScrim').onclick=()=>menu(false,true);
  window.addEventListener('keydown',e=>{
    if(!menuOpen)return;
    if(e.key==='Escape'){e.preventDefault();menu(false,true);}
    if(e.key==='Tab'&&matchMedia('(max-width:760px)').matches){
      const items=$$('#sidebar a[href], #sidebar button').filter(el=>el.tabIndex>=0&&!el.disabled);
      const first=items[0],last=items[items.length-1];
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
      else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
    }
  });
  window.addEventListener('resize',()=>{$('#sidebar').inert=matchMedia('(max-width:760px)').matches&&!menuOpen;});
  function active(){return document.querySelector('.tab.on')?.id.replace('tab-','')||'overview';}
  function paint(){const id=active(),[group,title]=routes[id]||routes.overview;
    $('#viewTitle').textContent=title;$('#viewEyebrow').textContent='BLACKTHORN ESTATE / '+groupNames[group];
    document.title=title+' · Blackthorn Estate';
    $$('#tabs button').forEach(b=>{const on=b.dataset.group===group;b.classList.toggle('on',on);b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;});
    $$('#subtabs [data-subgroup]').forEach(row=>{row.hidden=row.dataset.subgroup!==group;});$('#subtabs').hidden=group==='start';
    $$('#subtabs button').forEach(b=>{const on=b.dataset.tab===id;b.classList.toggle('on',on);b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;});
    if(!keyboardRouting){const wasOpen=menuOpen;menu(false);if(wasOpen||document.activeElement?.closest('.tab[hidden]'))$('#main').focus?.({preventScroll:true});}
    $('#subtabs button.on')?.scrollIntoView({block:'nearest',inline:'nearest'});
    if(id==='lighting')renderLights();if(id==='3d')syncFloor();saved();
  }
  function keyboardTabs(list,vertical=false){
    list.addEventListener('keydown',e=>{
      const buttons=[...list.querySelectorAll('[role="tab"]')],index=buttons.indexOf(e.target);
      if(index<0)return;
      const previous=vertical?'ArrowUp':'ArrowLeft',next=vertical?'ArrowDown':'ArrowRight';
      let target;
      if(e.key===previous)target=(index+buttons.length-1)%buttons.length;
      else if(e.key===next)target=(index+1)%buttons.length;
      else if(e.key==='Home')target=0;
      else if(e.key==='End')target=buttons.length-1;
      else return;
      e.preventDefault();keyboardRouting=true;try{buttons[target].click();}finally{keyboardRouting=false;}buttons[target].focus();
    });
  }
  keyboardTabs($('#tabs'),true);
  $$('#subtabs [role="tablist"]').forEach(list=>keyboardTabs(list));
  window.addEventListener('bt:tab',paint);
  function saved(){const ok=BT.storageOK(),el=$('#globalSaveStatus');const shared=['shared','live'].includes(active());el.classList.toggle('error',!ok&&!shared);
    el.innerHTML='<span class="status-dot"></span>'+(shared?(active()==='live'?'Server-Prüfstand':'Gemeinsame Materialliste'):ok?'Speichert lokal':'Backup erforderlich');
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
    $('#lightRows').innerHTML=rows.map(f=>`<tr><td><b class="light-id">${f.id}</b><small class="cell-note">${f.block==='soul_lantern'?'Seelenlaterne':'Laterne'}</small></td><td>${safe(window.__groupName(f.group))}<small class="cell-note">${safe(f.level)}</small></td><td class="light-coordinate">X ${f.x}<br>Y ${f.y} · Z ${f.z}</td><td>${safe(f.kind)}<small class="cell-note">${f.chain?f.chain+' Kettenblöcke → ':''}${safe(blockName(f.anchor_block))}</small></td><td><div class="light-actions"><button class="mini" data-light3d="${f.id}" aria-label="${f.id} in 3D ansehen">In 3D</button><button class="mini" data-light-plan="${f.id}" aria-label="${f.id} im Ebenenplan ansehen">Im Plan</button></div></td></tr>`).join('')||'<tr><td colspan="5" class="empty-state">Keine passende Leuchte. Suchbegriff oder Filter ändern.</td></tr>';
  }
  $('#lightQuery').oninput=renderLights;$('#lightLevel').onchange=renderLights;$('#lightKind').onchange=renderLights;
  $('#lightRows').onclick=e=>{const key=e.target.dataset.light3d||e.target.dataset.lightPlan;if(!key)return;const f=fixtures.find(x=>x.id===key);if(!f)return;
    if(e.target.dataset.light3d){window.__focusFixture(f);$('#sceneFloor').value='custom';}else window.__focusPlan(f.x,f.y,f.z);
  };
  function syncFloor(){const value=$('#cut').value;$('#sceneFloor').value=[String(D.meta.bbox[3]),'144','136','128','120','112'].includes(value)?value:'custom';}
  $('#sceneFloor').onchange=e=>{if(e.target.value==='custom')return;window.__leaveFixture();$('#cut').value=e.target.value;$('#cut').dispatchEvent(new Event('input'));};
  $('#cut').addEventListener('input',syncFloor);$('#cutDown').addEventListener('click',syncFloor);$('#cutUp').addEventListener('click',syncFloor);
  $('#resetScene').onclick=()=>{window.__resetScene();$('#sceneFloor').value=String(D.meta.bbox[3]);$('#terrainState').value='target';$('#terrainState').dispatchEvent(new Event('change'));};
  $('#tab-structure').addEventListener('click',e=>{
    const level=e.target.closest('[data-level-cut]');
    if(level){window.__showTab('3d');$('#cut').value=level.dataset.levelCut;$('#cut').oninput({target:$('#cut')});$('#cut').dispatchEvent(new Event('input'));return;}
    const axis=e.target.closest('[data-axis-group]');if(axis)window.__openGroup(axis.dataset.axisGroup);
  });
  $('#leaveDetail').onclick=()=>$('#resetScene').click();
  const showCode=$('#sharedShowCode');
  if(showCode)showCode.onclick=()=>{const input=$('#sharedCode'),show=input.type==='password';input.type=show?'text':'password';showCode.textContent=show?'Verbergen':'Anzeigen';showCode.setAttribute('aria-pressed',String(show));};
  saved();renderLights();paint();
})();
