/* Shared inventory is stored centrally; local building progress remains in BT. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id),D=window.BLACKTHORN_DATA,escape=BT.escape;
  const PROFILE='blackthorn:shared:name:v1',SESSION='blackthorn:shared:code:v1',DRAFTS='blackthorn:shared:drafts:v1';
  const blank=()=>({amount:0,done:false,note:'',version:0,updatedBy:'',updatedAt:''});
  let rows={},drafts={},connected=false,code='',author='',refreshing=false,planMismatch=false,generation=0;
  const pending=new Set();
  const offline=location.protocol==='file:';
  const uid=()=>crypto.randomUUID();
  const stamp=value=>value?new Date(value).toLocaleString('de-DE',{dateStyle:'short',timeStyle:'short'}):'';
  const status=(text,error=false)=>{const el=$('sharedStatus');el.textContent=text;el.classList.toggle('error',error);};
  function saveDrafts(){try{sessionStorage.setItem(DRAFTS,JSON.stringify(drafts));}catch{status('Entwurf bleibt nur bis zum Schließen der Seite erhalten. Browser-Speicher ist nicht verfügbar.',true);}}
  try{
    $('sharedName').value=localStorage.getItem(PROFILE)||'';
    const saved=JSON.parse(sessionStorage.getItem(DRAFTS)||'{}');
    if(saved&&typeof saved==='object'&&!Array.isArray(saved))for(const [key,draft] of Object.entries(saved)){
      const [scope,item]=key.split(':');
      if(D.material_scopes[scope]?.counts[item]!==undefined&&draft&&typeof draft.changes==='object'&&Number.isSafeInteger(draft.expectedVersion))drafts[key]=draft;
    }
    code=sessionStorage.getItem(SESSION)||'';
  }catch{drafts={};}
  if(offline){$('sharedConnect').disabled=true;status('Die gemeinsame Liste ist auf der veröffentlichten Website verfügbar. Lokal bleiben die bisherigen Bauhäkchen nutzbar.');}
  function current(key){return rows[key]||blank();}
  function updateDraft(key,field,value){
    const draft=drafts[key]||(drafts[key]={expectedVersion:current(key).version,changes:{},mutation:uid()});
    draft.changes[field]=value;draft.mutation=uid();delete draft.error;saveDrafts();
    return draft;
  }
  async function request(method='GET',body){
    const response=await fetch('/api/materials',{
      method,headers:{Authorization:'Bearer '+code,...(body?{'Content-Type':'application/json'}:{})},
      ...(body?{body:JSON.stringify(body)}:{}),cache:'no-store',signal:AbortSignal.timeout(12000)
    });
    let result;
    try{result=await response.json();}catch{throw Object.assign(Error('Die gemeinsame Liste ist auf dieser Website noch nicht erreichbar. Bitte die Vercel-Einrichtung prüfen.'),{status:response.status});}
    if(!response.ok)throw Object.assign(Error(result.error||'Die Anfrage ist fehlgeschlagen.'),{status:response.status,...result});
    return result;
  }
  function setSession(on){
    connected=on;$('sharedLogin').hidden=on;$('sharedSession').hidden=!on;$('sharedWorkspace').hidden=!on;
    $('sharedIdentity').textContent='Verbunden als '+author;
  }
  async function refresh(){
    if(!connected||refreshing||offline)return;
    refreshing=true;const run=generation;const versions=Object.fromEntries(Object.entries(rows).map(([key,row])=>[key,row.version]));
    try{
      const result=await request();if(run!==generation)return;
      const incoming=result.entries;
      for(const [key,row] of Object.entries(rows))if(row.version>(versions[key]||0)&&(!incoming[key]||row.version>incoming[key].version))incoming[key]=row;
      rows=incoming;planMismatch=result.fingerprint!==D.meta.fingerprint;
      if(planMismatch)status('Auf dem Server liegt eine neue Bauplanversion. Bitte diese Seite neu laden; Entwürfe bleiben erhalten.',true);
      else status((result.preview?'Vercel-Vorschau: getrennte Testliste · ':result.development?'Lokale Testliste · ':'')+'Aktuell · '+stamp(result.serverTime)+' · automatische Aktualisierung alle 5 Sekunden'+(Object.keys(drafts).length?' · '+Object.keys(drafts).length+' ungespeicherte Entwürfe':''));
      render();
    }catch(error){if(run!==generation)return;status(error.message+' Entwürfe sind noch nicht zentral bestätigt.',true);if(error.status===401){setSession(false);try{sessionStorage.removeItem(SESSION);}catch{}}}
    finally{refreshing=false;}
  }
  function render(){
    const scope=$('sharedScope').value,query=$('sharedQuery').value.toLocaleLowerCase('de-DE').trim(),openOnly=$('sharedOpenOnly').checked;
    const counts=D.material_scopes[scope].counts;
    const active=document.activeElement,focus=active?.dataset.sharedKey?{key:active.dataset.sharedKey,field:active.dataset.sharedField,start:active.selectionStart,end:active.selectionEnd}:null;
    const entries=Object.entries(counts).sort((a,b)=>b[1]-a[1]);let done=0;
    const displayed=entries.filter(([item])=>{
      const key=scope+':'+item,row={...current(key),...drafts[key]?.changes};if(row.done)done++;
      return (!query||(`${item} ${window.__materialName?.(item)||''} ${row.note}`).toLocaleLowerCase('de-DE').includes(query))&&(!openOnly||!row.done||!!drafts[key]);
    });
    $('sharedSummary').textContent=`${done} von ${entries.length} Materialien abgehakt · ${displayed.length} angezeigt`;
    $('sharedRows').innerHTML=displayed.map(([item,required])=>{
      const key=scope+':'+item,confirmed=current(key),draft=drafts[key],row={...confirmed,...draft?.changes},busy=pending.has(key),disabled=busy||planMismatch?'disabled':'';
      const left=Math.max(0,required-(Number(row.amount)||0));
      const name=window.__materialName?.(item)||item.replace(/_/g,' ');
      const history=confirmed.updatedBy?`${confirmed.updatedBy} · ${stamp(confirmed.updatedAt)}`:'Noch keine Änderung';
      const problem=draft?.error?`<span class="shared-row-error">${escape(draft.error)}</span>`:'';
      const actions=draft?`<div class="shared-row-actions"><button type="button" class="mini" data-shared-save="${escape(key)}" ${disabled}>${draft.conflict?'Meine Änderung übernehmen':'Speichern'}</button><button type="button" class="mini" data-shared-discard="${escape(key)}" ${busy?'disabled':''}>${draft.conflict?'Aktuellen Stand verwenden':'Verwerfen'}</button></div>`:'';
      return `<tr class="${draft?'shared-draft':''}"><td><b>${escape(name)}</b><small class="cell-note">minecraft:${escape(item)}</small></td><td class="num">${required.toLocaleString('de-DE')}</td><td><input class="shared-amount" type="number" min="0" max="1000000000" step="1" data-shared-key="${escape(key)}" data-shared-field="amount" value="${escape(row.amount)}" aria-label="Vorhanden: ${escape(name)}" ${disabled}></td><td class="num">${left.toLocaleString('de-DE')}</td><td><input type="checkbox" data-shared-key="${escape(key)}" data-shared-field="done" aria-label="Abgehakt: ${escape(name)}" ${row.done?'checked':''} ${disabled}></td><td><input class="shared-note" type="text" maxlength="240" data-shared-key="${escape(key)}" data-shared-field="note" value="${escape(row.note)}" aria-label="Notiz: ${escape(name)}" placeholder="z. B. Lagerplatz …" ${disabled}></td><td><small>${escape(history)}</small>${busy?'<span class="cell-note">Wird gespeichert …</span>':''}${problem}${actions}</td></tr>`;
    }).join('')||'<tr><td colspan="7">Keine passenden Materialien.</td></tr>';
    if(focus){
      const input=[...$('sharedRows').querySelectorAll('[data-shared-key]')].find(el=>el.dataset.sharedKey===focus.key&&el.dataset.sharedField===focus.field);
      if(input&&!input.disabled){input.focus({preventScroll:true});if(input.type==='text'&&focus.start!==null)input.setSelectionRange(focus.start,focus.end);}
    }
  }
  async function save(key,acceptConflict=false){
    const draft=drafts[key];if(!draft||pending.has(key)||!connected||planMismatch)return;
    if(draft.conflict&&!acceptConflict){render();return;}
    const changes={...draft.changes};
    if(Object.hasOwn(changes,'amount')){
      const value=String(changes.amount);
      if(!/^\d+$/.test(value)||!Number.isSafeInteger(Number(value))||Number(value)>1_000_000_000){draft.error='Bitte eine ganze, nichtnegative Anzahl eingeben.';saveDrafts();render();return;}
      changes.amount=Number(value);
    }
    if(acceptConflict){draft.expectedVersion=current(key).version;draft.mutation=uid();delete draft.conflict;}
    const [scope,item]=key.split(':');const sentMutation=draft.mutation;const run=generation;
    pending.add(key);render();
    try{
      const result=await request('PATCH',{scope,item,changes,expectedVersion:draft.expectedVersion,mutation:sentMutation,author,fingerprint:D.meta.fingerprint});
      if(run!==generation)return;
      rows[key]=result.row;
      if(drafts[key]?.mutation===sentMutation)delete drafts[key];
      else if(drafts[key])drafts[key].expectedVersion=result.row.version;
      status('Zentral gespeichert · '+stamp(result.row.updatedAt));
    }catch(error){
      if(run!==generation)return;
      if(error.code==='ROW_CONFLICT'&&error.row){rows[key]=error.row;draft.conflict=true;draft.error=`Inzwischen geändert von ${error.row.updatedBy||'jemandem aus dem Team'}: Bestand ${error.row.amount}, ${error.row.done?'abgehakt':'offen'}, Notiz „${error.row.note||'—'}“. Bitte wählen.`;}
      else {draft.error=error.message;if(error.code==='PLAN_CHANGED')planMismatch=true;}
      status('Änderung noch nicht gespeichert. Bitte den Hinweis am Material prüfen.',true);
    }finally{pending.delete(key);saveDrafts();if(run===generation)render();}
  }
  $('sharedRows').addEventListener('input',event=>{
    const el=event.target,key=el.dataset.sharedKey,field=el.dataset.sharedField;if(!key||!field||field==='done')return;
    updateDraft(key,field,el.value);
  });
  $('sharedRows').addEventListener('change',event=>{
    const el=event.target,key=el.dataset.sharedKey,field=el.dataset.sharedField;if(!key||!field)return;
    updateDraft(key,field,field==='done'?el.checked:el.value);save(key);
  });
  $('sharedRows').addEventListener('keydown',event=>{if(event.key==='Enter'&&event.target.dataset.sharedKey){event.preventDefault();save(event.target.dataset.sharedKey);}});
  $('sharedRows').addEventListener('click',event=>{
    const saveButton=event.target.closest('[data-shared-save]'),discard=event.target.closest('[data-shared-discard]');
    if(saveButton)save(saveButton.dataset.sharedSave,true);
    if(discard){delete drafts[discard.dataset.sharedDiscard];saveDrafts();render();}
  });
  $('sharedScope').onchange=render;$('sharedQuery').oninput=render;$('sharedOpenOnly').onchange=render;
  $('sharedRefresh').onclick=()=>refresh();
  $('sharedLogin').onsubmit=async event=>{
    event.preventDefault();if(offline)return;
    author=$('sharedName').value.trim();code=$('sharedCode').value||code;
    if(!author||!code){status('Bitte Name und Teamcode angeben.',true);return;}
    $('sharedConnect').disabled=true;status('Gemeinsame Liste wird geöffnet …');generation++;
    try{
      const result=await request();rows=result.entries;planMismatch=result.fingerprint!==D.meta.fingerprint;
      try{localStorage.setItem(PROFILE,author);sessionStorage.setItem(SESSION,code);}catch{}
      $('sharedCode').value='';setSession(true);render();
      status(planMismatch?'Bitte die Seite neu laden: der Server hat einen neueren Bauplan.':'Verbunden. Alle Teammitglieder sehen dieselbe Liste.',planMismatch);
    }catch(error){status(error.message,true);}
    finally{$('sharedConnect').disabled=false;}
  };
  $('sharedLogout').onclick=()=>{
    if(pending.size){status('Bitte warten, bis die laufende Speicherung beendet ist.',true);return;}
    generation++;connected=false;code='';rows={};setSession(false);try{sessionStorage.removeItem(SESSION);}catch{}
    status('Abgemeldet. Ungespeicherte Entwürfe bleiben in diesem Tab erhalten.');
  };
  $('sharedExport').onclick=()=>{
    const payload={format:'blackthorn-shared-materials',schema:1,revision:D.meta.version,exported_at:new Date().toISOString(),entries:rows};
    const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='blackthorn-gemeinsame-materialliste-'+new Date().toISOString().slice(0,10)+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  const active=()=>connected&&!document.hidden&&document.getElementById('tab-shared').classList.contains('on');
  setInterval(()=>{if(active())refresh();},5000);
  window.addEventListener('bt:tab',()=>{if(active())refresh();});
  window.addEventListener('online',()=>{if(active())refresh();});
  document.addEventListener('visibilitychange',()=>{if(active())refresh();});
  if(!offline&&code&&$('sharedName').value){$('sharedCode').required=false;$('sharedLogin').requestSubmit();$('sharedCode').required=true;}
})();
