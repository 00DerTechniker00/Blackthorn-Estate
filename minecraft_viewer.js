/* Load house NBT or the original Litematic modules into the optional texture viewer. */
(() => {
  'use strict';
  const $=s=>document.querySelector(s),frame=$('#textureViewer'),status=$('#textureViewerStatus');
  const origin='https://structure-viewer.ewanhowell.com',version='26.3',pending=new Map();
  let sequence=0,ready=false,started=false,packsReady=false,requested='house';
  const models={house:{element:'structureNbt',name:'Blackthorn Estate · Revision '+JSON.parse($('#data').textContent).meta.version+'.nbt',url:'blackthorn_estate_'+JSON.parse($('#data').textContent).meta.version+'.nbt'},copper:{element:'litematicCopper',name:'Copper Golem MIS Cherry.litematic',url:'litematics/Copper Golem MIS Cherry.litematic'},filter:{element:'litematicFilter',name:'Golem MIS Dustless Filter.litematic',url:'litematics/Golem MIS Dustless Filter.litematic'}};
  const say=(message,error=false)=>{status.textContent=message;status.classList.toggle('error',error);};
  function send(type,body,transfer=[]){return new Promise((resolve,reject)=>{
    const id=++sequence,timer=setTimeout(()=>{pending.delete(id);reject(Error('Der Minecraft-Viewer hat nicht rechtzeitig geantwortet.'));},90000);
    pending.set(id,message=>{clearTimeout(timer);if(message.ok)resolve(message);else reject(Error(message.error||'Der Minecraft-Viewer konnte die Ansicht nicht laden.'));});
    frame.contentWindow.postMessage({source:'structure-viewer',type,id,...body},origin,transfer);
  });}
  async function loadModel(key){
    requested=key;const model=models[key];if(!model)return;
    if(!ready){say('Der Structure Viewer verbindet sich …');return;}
    try{
      if(!packsReady){say('Minecraft 26.3 Blockmodelle werden geladen …');await send('loadPacks',{base:version});packsReady=true;}
      say(model.name+' wird geladen …');
      const encoded=$('#'+model.element).textContent.trim(),binary=atob(encoded),bytes=new Uint8Array(binary.length);
      for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
      await send('loadStructure',{data:bytes,name:model.name,version},[bytes.buffer]);
      say('Fertig: '+model.name+' · drehen, zoomen und erkunden.');
    }catch(error){say(error.message+' Du kannst die Originaldatei herunterladen und im Viewer manuell öffnen.',true);}
  }
  window.addEventListener('message',async event=>{
    if(event.origin!==origin||event.source!==frame.contentWindow)return;
    const message=event.data;if(message?.source!=='structure-viewer')return;
    if(message.event==='ready'&&!started){ready=true;started=true;await loadModel(requested);return;}
    if(message.reply!==undefined){const resolve=pending.get(message.reply);if(resolve){pending.delete(message.reply);resolve(message);}}
  });
  const selector=$('#textureModel'),download=$('#downloadSelectedModel');
  function choose(key,load=false){if(!models[key])return;selector.value=key;download.href=models[key].url;download.download=models[key].url.split('/').pop();if(load){if(frame.hidden){frame.hidden=false;frame.src=origin+'/?minimal&manual&nosky&version='+encodeURIComponent(version);}loadModel(key);frame.scrollIntoView?.({behavior:'smooth',block:'start'});}}
  selector.onchange=()=>choose(selector.value,false);
  $('#launchTextureViewer').onclick=()=>choose(selector.value,true);
  document.querySelectorAll('[data-preview-module]').forEach(button=>button.onclick=()=>{
    const key=button.dataset.previewModule==='golem_mis'?'copper':'filter';
    window.__showTab('viewer');choose(key,true);
  });
})();
