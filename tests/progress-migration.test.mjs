import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
test('same-version V6 correction retains unchanged ticks and resets only changed blocks',()=>{
 const data=JSON.parse(readFileSync('blueprint.json','utf8'));
 const previous=data.progress_compat.additional[0],changed=new Set(previous.changed_positions);
 const [y,z,x]=data.runs.find(([y,z,x])=>!changed.has(`${x},${y},${z}`));
 const keep=`${x},${y},${z}`,reset=previous.changed_positions[0];assert(changed.has(reset));
 const key='blackthorn:'+data.meta.version+':progress';
 const storage=new Map([[key,JSON.stringify({format:'blackthorn-progress',schema:1,blueprint:previous.fingerprint,state:{groups:{halle:true},people:{halle:'Piet'},blocks:{[keep]:true,[reset]:true},inventory:{'V6-H01':'Material'}}})]]);
 const nodes=new Map();
 const document={getElementById:id=>{if(!nodes.has(id))nodes.set(id,{classList:{toggle(){}}});return nodes.get(id);}};
 const window={BLACKTHORN_DATA:data,dispatchEvent(){}};
 vm.runInNewContext(readFileSync('progress.js','utf8'),{window,document,localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},Event,Blob,URL,setTimeout});
 assert(window.BT.storageOK());assert.equal(window.BT.state.blocks[keep],true);assert.equal(window.BT.state.blocks[reset],undefined);
 assert.equal(window.BT.state.groups.halle,true);assert.equal(window.BT.state.people.halle,'Piet');assert.equal(window.BT.state.inventory['V6-H01'],'Material');
 assert.equal(JSON.parse(storage.get(key)).blueprint,data.meta.fingerprint);
});
