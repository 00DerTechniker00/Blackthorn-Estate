/* One versioned snapshot covers phases, block checkmarks, people and inventory. */
(() => {
  'use strict';
  const data=JSON.parse(document.getElementById('data').textContent);
  const KEY='blackthorn:5.9:progress', groups=new Set(data.groups), validBlocks=new Set();
  for(const [y,z,x,n] of data.runs)for(let i=0;i<n;i++)validBlocks.add(`${x+i},${y},${z}`);
  const empty=()=>({groups:{},people:{},blocks:{},inventory:{}});
  const state=empty();let storageOK=true;
  function validate(snapshot) {
    if(!snapshot || snapshot.format!=='blackthorn-progress' || snapshot.schema!==1 || snapshot.blueprint!==data.meta.fingerprint)
      throw Error('Das Backup gehört nicht zu diesem Bauplan. Bitte eine Fortschrittsdatei der Revision 5.9 verwenden.');
    if(!snapshot.state || typeof snapshot.state!=='object')throw Error('Im Backup fehlt der Fortschritt.');
    const result=empty();
    for(const kind of Object.keys(result)) {
      const values=snapshot.state[kind];
      if(!values || typeof values!=='object' || Array.isArray(values))throw Error('Ungültiger Bereich: '+kind);
      for(const [key,value] of Object.entries(values)) {
        if(kind==='blocks') {if(!validBlocks.has(key)||value!==true)throw Error('Ungültige Blockkoordinate im Backup.');}
        else if(kind==='groups') {if(!groups.has(key)||typeof value!=='boolean')throw Error('Ungültige Baugruppe im Backup.');}
        else if(kind==='people') {if(!groups.has(key)||typeof value!=='string'||value.length>200)throw Error('Ungültige Zuständigkeit.');}
        else if(!data.storage_zones.some(z=>z.id===key)||typeof value!=='string'||value.length>2000)throw Error('Ungültiger Lagerbestand.');
        result[kind][key]=value;
      }
    }return result;
  }
  function snapshot(){return {format:'blackthorn-progress',schema:1,revision:data.meta.version,blueprint:data.meta.fingerprint,
    exported_at:new Date().toISOString(),state};}
  function message(text,error=false){const el=document.getElementById('backupStatus');if(el){el.textContent=text;el.classList.toggle('error',error);}}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(snapshot()));storageOK=true;message('Lokal gespeichert · '+Object.keys(state.blocks).length.toLocaleString('de-DE')+' Blöcke abgehakt');}
    catch(e){storageOK=false;message('Browser-Speicher nicht verfügbar. Bitte Backup herunterladen.',true);}}
  function assign(next){for(const kind of Object.keys(state)){for(const key of Object.keys(state[kind]))delete state[kind][key];Object.assign(state[kind],next[kind]);}}
  try {const saved=localStorage.getItem(KEY);if(saved)assign(validate(JSON.parse(saved)));}
  catch(e){storageOK=false;message('Gespeicherter Stand konnte nicht geladen werden. Vor Änderungen vorhandenes Backup prüfen.',true);}
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  window.BT={state,save,validate,snapshot,escape,storageOK:()=>storageOK};
  document.getElementById('dlProg').onclick=()=>{
    const a=document.createElement('a'),url=URL.createObjectURL(new Blob([JSON.stringify(snapshot(),null,2)],{type:'application/json'}));
    a.href=url;a.download='blackthorn-5.9-fortschritt-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    message('Backup enthält Baugruppen, Zuständigkeiten, Blockstatus und Lagerbestand.');
  };
  document.getElementById('impProg').onchange=async e=>{
    const file=e.target.files[0];if(!file)return;
    try{
      if(file.size>10*1024*1024)throw Error('Die Datei ist größer als 10 MB.');
      const next=validate(JSON.parse((await file.text()).replace(/^\uFEFF/,'')));
      if(!confirm('Dieses Backup ersetzt den lokalen Fortschritt einschließlich Zuständigkeiten und Lagerbestand. Fortfahren?'))return;
      assign(next);save();window.dispatchEvent(new Event('bt:import'));
      if(storageOK)message('Backup geladen und lokal gespeichert.');
    }catch(err){message(err.message,true);}finally{e.target.value='';}
  };
  if(storageOK)message('Fortschritt wird lokal gespeichert · vollständiges Backup unter „Bauplan“.');
})();
