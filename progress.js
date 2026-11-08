/* Complete backups; compatible 5.25 progress retains only unchanged positions/groups. */
(() => {
  'use strict';
  const data=window.BLACKTHORN_DATA,compat=data.progress_compat;
  const KEY='blackthorn:'+data.meta.version+':progress',groups=new Set(data.groups),validBlocks=new Set();
  for(const [y,z,x,n] of data.runs)for(let i=0;i<n;i++)validBlocks.add(`${x+i},${y},${z}`);
  const empty=()=>({groups:{},people:{},blocks:{},inventory:{}}),state=empty();let storageOK=true,initialMigration=null;
  function validate(snapshot){
    const migration=[compat,...(compat.additional||[])].find(candidate=>candidate.fingerprint===snapshot?.blueprint);
    const migrate=!!migration,changedForMigration=new Set(migration?.changed_positions||[]);
    if(!snapshot||snapshot.format!=='blackthorn-progress'||snapshot.schema!==1||snapshot.blueprint!==data.meta.fingerprint&&!migrate)
      throw Error('Das Backup gehört nicht zu diesem Bauplan. Aktuellen Bauplan oder ein kompatibles Backup der Vorversion verwenden.');
    if(!snapshot.state||typeof snapshot.state!=='object')throw Error('Im Backup fehlt der Fortschritt.');
    const result=empty();let skipped=0,reset=0;
    for(const kind of Object.keys(result)){
      const values=snapshot.state[kind];if(!values||typeof values!=='object'||Array.isArray(values))throw Error('Ungültiger Bereich: '+kind);
      for(const [key,value] of Object.entries(values)){
        if(kind==='blocks'){
          if(value!==true)throw Error('Ungültiger Blockstatus.');
          if(migrate&&changedForMigration.has(key)){skipped++;continue;}
          if(!validBlocks.has(key))throw Error('Unbekannte Blockkoordinate im Backup.');
        }else if(kind==='groups'){
          if(migrate&&!groups.has(key)){skipped++;continue;}
          if(!groups.has(key)||typeof value!=='boolean')throw Error('Ungültige Baugruppe.');
          if(migrate&&migration.changed_groups.includes(key)){if(value)reset++;continue;}
        }else if(kind==='people'){
          if(migrate&&!groups.has(key)){skipped++;continue;}
          if(!groups.has(key)||typeof value!=='string'||value.length>200)throw Error('Ungültige Zuständigkeit.');
        }else if(migrate&&!data.storage_zones.some(z=>z.id===key)){skipped++;continue;}
        else if(!data.storage_zones.some(z=>z.id===key)||typeof value!=='string'||value.length>2000)throw Error('Ungültiger Lagerbestand.');
        result[kind][key]=value;
      }
    }
    if(migrate)result._migration={skipped,reset};return result;
  }
  function snapshot(){return {format:'blackthorn-progress',schema:1,revision:data.meta.version,blueprint:data.meta.fingerprint,exported_at:new Date().toISOString(),state};}
  function message(text,error=false){const el=document.getElementById('backupStatus');el.textContent=text;el.classList.toggle('error',error);}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(snapshot()));storageOK=true;message('Lokal gespeichert · '+Object.keys(state.blocks).length.toLocaleString('de-DE')+' Blöcke abgehakt.');}
    catch(e){storageOK=false;message('Browser-Speicher nicht verfügbar. Bitte vollständiges Backup herunterladen.',true);}
    window.dispatchEvent(new Event('bt:saved'));
  }
  function assign(next){for(const kind of Object.keys(state)){for(const key of Object.keys(state[kind]))delete state[kind][key];Object.assign(state[kind],next[kind]);}}
  try{
    const saved=localStorage.getItem(KEY),old=!saved&&localStorage.getItem('blackthorn:'+compat.revision+':progress');
    if(saved){const next=validate(JSON.parse(saved));assign(next);initialMigration=next._migration;}
    else if(old){const next=validate(JSON.parse(old));assign(next);initialMigration=next._migration;}
  }catch(e){storageOK=false;message('Gespeicherter Stand konnte nicht geladen werden. Vorhandenes Backup prüfen.',true);}
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  window.BT={state,save,validate,snapshot,escape,storageOK:()=>storageOK};
  document.getElementById('dlProg').onclick=()=>{const a=document.createElement('a'),url=URL.createObjectURL(new Blob([JSON.stringify(snapshot(),null,2)],{type:'application/json'}));a.href=url;a.download='blackthorn-'+data.meta.version+'-fortschritt-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('Backup enthält Baugruppen, Zuständigkeiten, Blockstatus und Lagerbestand.');};
  document.getElementById('impProg').onchange=async e=>{const file=e.target.files[0];if(!file)return;
    try{
      if(file.size>10*1024*1024)throw Error('Die Datei ist größer als 10 MB.');
      const next=validate(JSON.parse((await file.text()).replace(/^\uFEFF/,'')));
      const note=next._migration?` Aus der Vorversion werden unveränderte Positionen übernommen; ${next._migration.skipped} geänderte Blockhäkchen und ${next._migration.reset} betroffene Fertigmeldungen bleiben offen.`:'';
      if(!confirm('Dieses Backup ersetzt den lokalen Fortschritt einschließlich Zuständigkeiten und Lagerbestand.'+note+' Fortfahren?'))return;
      assign(next);save();window.dispatchEvent(new Event('bt:import'));if(storageOK)message('Backup geladen und lokal gespeichert.'+note);
    }catch(err){message(err.message,true);}finally{e.target.value='';}
  };
  if(initialMigration){save();if(storageOK)message('Stand aus der Vorversion übernommen. Geänderte Blockmodell-Positionen und betroffene Fertigmeldungen bleiben offen.');}
  else if(storageOK)message('Speichert nur in diesem Browser. Vollständiges Backup zum Teilen oder Umziehen herunterladen.');
})();
