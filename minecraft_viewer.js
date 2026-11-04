/* Load the generated structure into the optional official-texture viewer. */
(() => {
  'use strict';
  const $=s=>document.querySelector(s),frame=$('#textureViewer'),status=$('#textureViewerStatus');
  const origin='https://structure-viewer.ewanhowell.com',version='26.3',pending=new Map();let sequence=0,ready=false,started=false;
  const say=(message,error=false)=>{status.textContent=message;status.classList.toggle('error',error);};
  function send(type,body,transfer=[]){return new Promise((resolve,reject)=>{
    const id=++sequence,timer=setTimeout(()=>{pending.delete(id);reject(Error('Der Minecraft-Viewer hat nicht rechtzeitig geantwortet.'));},90000);
    pending.set(id,message=>{clearTimeout(timer);if(message.ok)resolve(message);else reject(Error(message.error||'Der Minecraft-Viewer konnte die Ansicht nicht laden.'));});
    frame.contentWindow.postMessage({source:'structure-viewer',type,id,...body},origin,transfer);
  });}
  window.addEventListener('message',async event=>{
    if(event.origin!==origin||event.source!==frame.contentWindow)return;
    const message=event.data;if(message?.source!=='structure-viewer')return;
    if(message.event==='ready'&&!started){ready=true;started=true;
      try{
        say('Minecraft 26.3 Blockmodelle werden geladen …');await send('loadPacks',{base:version});
        const encoded=$('#structureNbt').textContent.trim(),binary=atob(encoded),bytes=new Uint8Array(binary.length);
        for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
        await send('loadStructure',{data:bytes,name:'Blackthorn Estate · Revision 5.12.nbt',version},[bytes.buffer]);
        say('Fertig. Du kannst das Haus drehen, heranzoomen und im Viewer erkunden.');
      }catch(error){say(error.message+' Du kannst die NBT-Datei herunterladen und im Viewer manuell öffnen.',true);}
      return;
    }
    if(message.reply!==undefined){const resolve=pending.get(message.reply);if(resolve){pending.delete(message.reply);resolve(message);}}
  });
  $('#launchTextureViewer').onclick=()=>{
    if(frame.hidden){frame.hidden=false;frame.src=origin+'/?minimal&manual&nosky&version='+encodeURIComponent(version);say('Der Structure Viewer verbindet sich …');}
    else if(!ready)say('Der Structure Viewer verbindet sich …');
    frame.scrollIntoView?.({behavior:'smooth',block:'start'});
  };
})();
