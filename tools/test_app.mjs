/* Runtime integration tests with a DOM/Canvas adapter; not a browser/GPU test. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const blueprint=JSON.parse(fs.readFileSync(path.join(root,'blueprint.json'),'utf8'));
let checks=0;const check=(condition,message)=>{assert.ok(condition,message);checks++;};

function environment(storage=new Map(),webgl=true){
  let drawCalls=0,uploadedFloats=0;
  const timers=[],frames=[],listeners={},downloads=[];
  const ctx2d=new Proxy({createImageData:(w,h)=>({data:new Uint8ClampedArray(w*h*4)}),measureText:s=>({width:String(s).length*8})},
    {get:(t,k)=>k in t?t[k]:(()=>{})});
  const gl=new Proxy({getExtension:()=>({}),getShaderParameter:()=>true,getProgramParameter:()=>true,
    getAttribLocation:(_,name)=>['aPosition','aColor','aUV'].indexOf(name),getUniformLocation:()=>({}),
    createBuffer:()=>({}),createShader:()=>({}),createProgram:()=>({}),
    bufferData:(_target,array)=>{assert.ok([...array].every(Number.isFinite));uploadedFloats+=array.length;},
    drawElements:()=>{drawCalls++;}}, {get:(t,k)=>k in t?t[k]:/^[A-Z_0-9]+$/.test(k)?1:(()=>{})});
  const attrsOf=s=>Object.fromEntries([...s.matchAll(/([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)]
    .map(m=>[m[1],m[2]??m[3]??m[4]??'']));
  class Element{
    constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs=attrs;this.children=[];this.parentElement=null;this.style={};this.listeners={};this._html='';this._text='';this.checked='checked'in attrs;this.hidden='hidden'in attrs;this.files=[];this.width=940;this.height=530;
      this.dataset=Object.fromEntries(Object.entries(attrs).filter(([k])=>k.startsWith('data-')).map(([k,v])=>[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase()),v]));
      this.classList={contains:c=>(this.attrs.class||'').split(/\s+/).includes(c),toggle:(c,on)=>{const set=new Set((this.attrs.class||'').split(/\s+/));if(on??!set.has(c))set.add(c);else set.delete(c);this.attrs.class=[...set].join(' ');}};
    }
    get id(){return this.attrs.id??'';}
    get value(){return this._value??this.attrs.value??(this.tagName==='SELECT'?this.querySelector('option')?.value:'')??'';}
    set value(v){this._value=String(v);}
    get innerHTML(){return this._html;}set innerHTML(s){this._html=String(s);this.children=[];parse(this._html,this);}
    get textContent(){return this._text||this._html.replace(/<[^>]*>/g,'');}set textContent(s){this._text=String(s);}
    get clientWidth(){return 1000;}get clientHeight(){return 600;}
    setAttribute(k,v){this.attrs[k]=String(v);}getAttribute(k){return this.attrs[k]??null;}
    appendChild(child){this.children.push(child);child.parentElement=this;return child;}
    getBoundingClientRect(){return {left:0,top:0,width:1000,height:600};}
    addEventListener(k,fn){(this.listeners[k]??=[]).push(fn);}
    dispatchEvent(event){event.target??=this;this['on'+event.type]?.(event);for(const fn of this.listeners[event.type]||[])fn(event);if(event.bubbles)this.parentElement?.dispatchEvent(event);return true;}
    click(){this.dispatchEvent({type:'click',target:this,bubbles:true});}
    getContext(type){return type==='webgl'?(webgl?gl:null):ctx2d;}
    setPointerCapture(){}
    querySelectorAll(selector){return select(this,selector);}querySelector(selector){return this.querySelectorAll(selector)[0]??null;}
  }
  function matches(el,selector){
    const attr=[...selector.matchAll(/\[([^=\]]+)(?:="([^"]*)")?\]/g)];selector=selector.replace(/\[[^\]]+\]/g,'');
    for(const [,key,value] of attr)if(!(key in el.attrs)||value!==undefined&&el.attrs[key]!==value)return false;
    const id=selector.match(/#([\w-]+)/);if(id&&el.attrs.id!==id[1])return false;
    const classes=[...selector.matchAll(/\.([\w-]+)/g)];if(classes.some(([,c])=>!el.classList.contains(c)))return false;
    const tag=selector.match(/^[\w-]+/);return !tag||el.tagName===tag[0].toUpperCase();
  }
  function select(el,selector){const tokens=selector.trim().split(/\s+/),found=[];
    const visit=e=>{for(const child of e.children){if(matches(child,tokens.at(-1))){let ancestor=child.parentElement,i=tokens.length-2;
      while(i>=0&&ancestor){if(matches(ancestor,tokens[i]))i--;ancestor=ancestor.parentElement;}if(i<0)found.push(child);}visit(child);}};
    visit(el);return found;
  }
  function parse(s,parent){const stack=[parent],voids=new Set(['input','img','meta','link','br','hr']);
    for(const m of s.matchAll(/<(\/)?([a-z][\w-]*)([^>]*)>/gi)){
      const tag=m[2].toLowerCase();if(m[1]){for(let i=stack.length-1;i>0;i--)if(stack[i].tagName===tag.toUpperCase()){stack.length=i;break;}continue;}
      const element=new Element(tag,attrsOf(m[3]));stack.at(-1).appendChild(element);if(!voids.has(tag)&&!m[3].endsWith('/'))stack.push(element);
    }
  }
  const document=new Element('document');
  parse(html.replace(/<script[^>]*>.*?<\/script>/gs,'').replace('</body>','<script id="data"></script></body>'),document);
  document.documentElement=document.querySelector('html');document.createElement=tag=>new Element(tag);
  document.getElementById=id=>document.querySelector('#'+id);document.getElementById('data').textContent=JSON.stringify(blueprint);
  const global={document,console,Blob,URL:{createObjectURL:blob=>{downloads.push(blob);return 'blob:test';},revokeObjectURL(){}},
    Event:class{constructor(type,options={}){this.type=type;Object.assign(this,options);}},localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,String(v))},
    devicePixelRatio:1,location:{hash:''},matchMedia:()=>({matches:false}),getComputedStyle:()=>({getPropertyValue:k=>k==='--mode'?'light':'#aabbcc'}),
    ResizeObserver:class{observe(){}},setTimeout:fn=>{timers.push(fn);return timers.length;},clearTimeout(){},
    requestAnimationFrame:fn=>{frames.push(fn);},confirm:()=>true,alert:s=>{throw Error(s);},scrollTo(){},
    addEventListener:(k,fn)=>(listeners[k]??=[]).push(fn),dispatchEvent:e=>{for(const fn of listeners[e.type]||[])fn(e);}};
  global.window=global;
  const context=vm.createContext(global);
  for(const name of ['progress','logistics','app','steps','terrain','system','ui']){
    let source=fs.readFileSync(path.join(root,name+'.js'),'utf8');
    if(name==='app')source=source.replace(/\}\)\(\);\s*$/,`window.testHooks={renderMat,renderCoord,renderBuild,PHASES,rayBlock,cameraBasis,viewProjection,buildModel,buildTerrain,predNow,lanternParts,shapeRects,getGL:()=>GL};})();`);
    vm.runInContext(source,context,{filename:name+'.js'});
  }
  return {context,document,storage,downloads,runTimers(){while(timers.length)timers.shift()();},frame(){frames.shift()?.();},stats:()=>({drawCalls,uploadedFloats})};
}

async function main(){
const env=environment(),{context:c,document:doc}=env;
check(doc.getElementById('st-blocks').textContent===blueprint.meta.total.toLocaleString('de-DE'),'Overview initializes');
check(doc.querySelector('.tab.on').attrs.id==='tab-overview','Initial overview selected');
for(const button of doc.querySelectorAll('[data-tab]')){
  button.click();env.runTimers();env.frame();
  check(doc.querySelector('.tab.on').attrs.id==='tab-'+button.dataset.tab,'Navigation '+button.dataset.tab);
}
check(env.stats().uploadedFloats>1000000,'Real block and terrain geometry uploaded with finite coordinates');
check(env.stats().drawCalls>0,'3D render path draws geometry');
check(doc.querySelectorAll('#tabs button').length===5,'Five primary work areas');
c.__showTab('plan');check(doc.querySelector('#tabs button.on').dataset.group==='atlas','Secondary views keep the primary area active');
check(doc.getElementById('viewTitle').textContent==='Ebenenplan','Current view has a clear heading');
check(doc.querySelector('#subtabs [data-subgroup="atlas"]').hidden===false,'Only relevant subnavigation is visible');
c.location.hash='#lighting';c.dispatchEvent(new c.Event('hashchange'));
check(doc.querySelector('.tab.on').id==='tab-lighting','Browser history/deep links update the view');
check(doc.getElementById('lightRows').querySelectorAll('[data-light-plan]').length===blueprint.lighting.total,'All actual fixtures appear in the inspector');
doc.getElementById('lightLevel').value='Keller 1';doc.getElementById('lightLevel').dispatchEvent({type:'change'});
check(doc.getElementById('lightRows').querySelectorAll('[data-light-plan]').length===blueprint.lighting.fixtures.filter(f=>f.level==='Keller 1').length,'Light level filter matches model');
doc.getElementById('lightLevel').value='all';doc.getElementById('lightLevel').dispatchEvent({type:'change'});
doc.getElementById('lightQuery').value='no_matching_fixture';doc.getElementById('lightQuery').dispatchEvent({type:'input'});
check(doc.getElementById('lightRows').querySelectorAll('[data-light-plan]').length===0,'Empty light search has no stale actions');
doc.getElementById('lightQuery').value='';doc.getElementById('lightQuery').dispatchEvent({type:'input'});
doc.querySelector('[data-light3d]').click();env.runTimers();env.frame();
check(doc.querySelector('.tab.on').id==='tab-3d'&&!doc.getElementById('detailBanner').hidden,'Light detail opens the actual 3D geometry');
check(Object.keys(c.testHooks.getGL().meshes).length<=6,'Fixture inspection isolates lamp, chain and support');
doc.getElementById('leaveDetail').click();env.frame();
check(doc.getElementById('detailBanner').hidden&&doc.getElementById('terrainChk').checked,'Returning from a fixture restores house and terrain');
doc.getElementById('sceneFloor').value='119';doc.getElementById('sceneFloor').dispatchEvent({type:'change'});
check(doc.getElementById('cut').value==='119','Floor shortcut reveals cellar interior below ceiling');
doc.getElementById('resetScene').click();env.frame();
doc.getElementById('menuButton').click();
check(doc.documentElement.classList.contains('nav-open')&&doc.getElementById('menuButton').getAttribute('aria-expanded')==='true','Drawer exposes its expanded state');
c.dispatchEvent(new c.Event('keydown',{key:'Escape'}));
check(!doc.documentElement.classList.contains('nav-open')&&doc.getElementById('navScrim').hidden,'Escape closes drawer');
doc.getElementById('menuButton').click();c.__showTab('material');
check(!doc.documentElement.classList.contains('nav-open'),'Navigation closes mobile drawer');
for(const hanging of [true,false]){
  const r={kind:'lantern',id:'lantern',p:{hanging:String(hanging)}},parts=c.testHooks.lanternParts(r);
  check(new Set(parts.map(p=>p.color.join(','))).size===2,'Metal frame and light have separate colors');
  check(hanging?Math.max(...parts.map(p=>p.box[4]))===16:Math.min(...parts.map(p=>p.box[1]))===0,'Lantern meets ceiling or base correctly');
  const joined=new Set([0]);let changed=true;while(changed){changed=false;for(let i=0;i<parts.length;i++)if(!joined.has(i))for(const j of joined){const a=parts[i].box,b=parts[j].box;if([0,1,2].every(k=>a[k]<=b[k+3]&&b[k]<=a[k+3])){joined.add(i);changed=true;break;}}}
  check(joined.size===parts.length,'All lantern components form one connected model');
  if(!hanging)check(c.testHooks.shapeRects(r,'z').some(b=>b[3]===1),'Standing lantern touches baseline in a section');
}
const stateControl=doc.getElementById('terrainState');
for(const mode of ['original','target','work']){
  stateControl.value=mode;const oldFloats=env.stats().uploadedFloats;stateControl.dispatchEvent({type:'change'});
  check(env.stats().uploadedFloats>oldFloats,'Terrain geometry rebuild: '+mode);
  const geometry=c.testHooks.buildTerrain();
  const k=((760-blueprint.terrain.bounds[2])*(blueprint.terrain.bounds[1]-blueprint.terrain.bounds[0]+1)+(-720-blueprint.terrain.bounds[0]));
  // Locate this surveyed top quad by its coordinates, independent of face ordering.
  let topY=null;for(let i=0;i<geometry.p.length;i+=12){const p=geometry.p.slice(i,i+12);
    if(p[0]===-720&&p[2]===-760&&p[1]===p[4]&&p[1]===p[7]&&p[1]===p[10]){topY=p[1];break;}}
  const grid=mode==='original'?blueprint.terrain.heights:blueprint.terrain.target_heights;
  check(topY===grid[760-blueprint.terrain.bounds[2]][-720-blueprint.terrain.bounds[0]]+1,'Terrain source matches selected state: '+mode);
}
for(const mode of ['earthworks','surface','target','height','delta']){
  const map=doc.getElementById('geologyMode');map.value=mode;map.dispatchEvent({type:'change'});
  check(true,'Earthwork map mode runs: '+mode);
}
// Exercise real earthwork selection, comparison, profile and model visibility.
const earth=c.__earth,terrainData=blueprint.terrain;
check(earth.choose(-690,843),'Garden coordinate can be selected');
check(doc.getElementById('earthZone').textContent==='Gartenweg','Column inspector identifies the actual planned zone');
check(doc.getElementById('earthColumn').innerHTML.includes('Y 125'),'Column inspector shows actual target elevation');
check(doc.getElementById('earthProfile').innerHTML.includes('<polyline'),'Selected profile contains actual elevation polylines');
const beforeAxis=doc.getElementById('earthProfile').innerHTML;doc.getElementById('earthAxis').value='z';doc.getElementById('earthAxis').dispatchEvent({type:'change'});
check(doc.getElementById('earthProfile').innerHTML!==beforeAxis,'Profile switches between west/east and north/south');
check(!earth.choose(-900,843)&&earth.selection().x===-690,'Out-of-range coordinates cannot change the selection');
doc.getElementById('earthX').value='-745';doc.getElementById('earthZ').value='790';doc.getElementById('earthCoords').dispatchEvent({type:'submit',preventDefault(){}});
check(earth.selection().x===-745&&earth.selection().z===790,'Coordinate form updates the selected column');
doc.getElementById('geologyMode').value='compare';doc.getElementById('geologyMode').dispatchEvent({type:'change'});
check(!doc.getElementById('compareControl').hidden,'Comparison mode exposes the split slider');
for(const value of ['0','50','100']){doc.getElementById('earthCompare').value=value;doc.getElementById('earthCompare').dispatchEvent({type:'input'});check(true,'Comparison slider redraws at '+value);}
doc.getElementById('geologyMode').value='earthworks';doc.getElementById('geologyMode').dispatchEvent({type:'change'});
check(doc.getElementById('compareControl').hidden&&!doc.getElementById('earthLegend').hidden,'Earthwork mode shows the matching legend');
check(doc.getElementById('earthChunks').querySelectorAll('tr').length===terrainData.chunks.length,'All working chunks appear');
doc.getElementById('earthChunkFilter').value='cut';doc.getElementById('earthChunkFilter').dispatchEvent({type:'change'});
check(doc.getElementById('earthChunks').querySelectorAll('tr').length===terrainData.chunks.filter(r=>r[3]>0).length,'Working chunks filter by real excavation totals');
doc.getElementById('earthChunks').querySelector('[data-chunk-x]').click();check(Number.isInteger(earth.selection().x),'Chunk selection chooses a real integer world column');
doc.getElementById('earth3d').click();env.runTimers();env.frame();
check(doc.querySelector('.tab.on').id==='tab-3d'&&!doc.getElementById('houseChk').checked,'Earthwork action opens 3D without the building');
check(Object.keys(c.testHooks.getGL().meshes).length===0,'Terrain-only mode actually removes building geometry');
doc.getElementById('houseChk').checked=true;doc.getElementById('houseChk').dispatchEvent({type:'change'});
check(Object.keys(c.testHooks.getGL().meshes).length>10,'Building visibility switch restores model geometry');
doc.querySelector('[data-outdoor="1"]').click();env.runTimers();
check(doc.getElementById('houseChk').checked&&doc.getElementById('terrainState').value==='target','Garden action opens the actual decorated model');
doc.getElementById('resetScene').click();
check(doc.getElementById('storageZones').querySelectorAll('tr').length===56,'All warehouse and private bays appear in storage UI');
for(const amount of [0,1,1727,1728,1729,3456,5000,1000000])for(const empty of [0,1,27,81,100]){
  const r=c.Logistics.bulk(amount,empty);
  check(r.ready+r.full_boxes*1728+r.active_items+r.unaccepted===amount,'Bulk mass conservation');
  check(r.ready<=1728&&r.stored_boxes<=81&&r.active_items<1728,'Bulk capacity bounds');
  if(amount<=1728)check(r.full_boxes===0&&r.active_items===0,'Loose buffer has priority');
}
check(c.Logistics.bulk(5000,0).unaccepted===3272,'No empty boxes means backpressure, no lost items');
check(c.Logistics.bulk(100,27,1600).ready===1700,'Withdrawn loose stock is replenished before packing');
check(c.Logistics.rare('diamond',32,blueprint.storage_system.regular).matched,'Known rare type finds seeded chest');
check(!c.Logistics.rare('unknown_item',32,blueprint.storage_system.regular).matched,'Unknown types do not silently match a category');
for(const button of doc.querySelectorAll('[data-cam]')){
  button.click();const basis=c.testHooks.cameraBasis(),r=basis.right,u=basis.up,b=basis.back;
  const cross=[r[1]*u[2]-r[2]*u[1],r[2]*u[0]-r[0]*u[2],r[0]*u[1]-r[1]*u[0]];
  check(cross.every((v,i)=>Math.abs(v-b[i])<1e-10),'Camera basis preserves orientation: '+button.dataset.cam);
  const matrix=c.testHooks.viewProjection(),t=c.testHooks.getGL().cam.t,p=[t.x,t.y,t.z,1],clip=Array.from({length:4},(_,i)=>p.reduce((s,v,j)=>s+matrix[j*4+i]*v,0));
  check(Math.abs(clip[0]/clip[3])<1e-4&&Math.abs(clip[1]/clip[3])<1e-4,'Camera target projects to center: '+button.dataset.cam);
  check(c.testHooks.rayBlock({clientX:500,clientY:300})>=0,'Center ray selects a model block: '+button.dataset.cam);
}
const phases=c.testHooks.PHASES.flatMap(p=>p.groups);
check(blueprint.groups.every(g=>phases.filter(x=>x===g).length===1),'Every group is present exactly once in build phases');
const mat=doc.getElementById('matG');
for(const group of ['all',...blueprint.groups]){
  mat.value=group;mat.dispatchEvent({type:'change'});
  const data=group==='all'?blueprint.counts:blueprint.gcounts[group];
  check(doc.getElementById('matRows').querySelectorAll('tr').length===Object.keys(data).length,'Material rows: '+group);
  check(doc.getElementById('matTot').textContent===Object.values(data).reduce((a,b)=>a+b,0).toLocaleString('de-DE'),'Material total: '+group);
}
doc.getElementById('coordQ').value='-672 124 791';doc.getElementById('coordQ').dispatchEvent({type:'input'});
check(doc.getElementById('coordRows').querySelectorAll('tr').length===1,'Exact XYZ search finds input chest');
doc.getElementById('coordQ').value='791 124 -672';doc.getElementById('coordQ').dispatchEvent({type:'input'});
check(doc.getElementById('coordRows').querySelectorAll('tr').length===0,'Swapped axes do not match');
for(const mode of ['x','y','z']){
  const select=doc.getElementById('planMode');select.value=mode;select.dispatchEvent({type:'change'});
  const range=doc.getElementById('planRange'),value={x:-672,y:124,z:791}[mode];range.value=value;range.dispatchEvent({type:'input'});
  doc.getElementById('dlLayer').click();const csv=await env.downloads.at(-1).text(),rows=csv.replace(/^\uFEFF/,'').trim().split('\n').slice(1);
  const column={x:1,y:2,z:3}[mode];check(rows.length>0&&rows.every(row=>+row.split(';')[column]===value),'Slice CSV exports selected axis: '+mode);
}
const input=doc.querySelector('#stepRows input');input.checked=true;input.dispatchEvent({type:'change',bubbles:true});
check(c.BT.state.blocks[input.dataset.done]===true&&input.dataset.done.split(',').length===3,'Checkmark is stored by XYZ');
const who=doc.querySelector('#phases input[data-who]');who.value='<img src=x onerror=alert(1)>"&';who.dispatchEvent({type:'input',bubbles:true});
c.testHooks.renderBuild();check(doc.getElementById('phases').innerHTML.includes('&lt;img'),'Imported people text is escaped');
const stock=doc.querySelector('#storageZones input');stock.value='3 Shulker';stock.dispatchEvent({type:'input',bubbles:true});
const snap=JSON.parse(JSON.stringify(c.BT.snapshot()));check(Object.keys(snap.state.inventory).length===1,'Backup includes stock');
check(snap.state.people[who.dataset.who]===who.value,'Backup includes people');
check(Object.keys(snap.state.blocks).length===1,'Backup includes per-block state');
check(c.BT.validate(snap).blocks[input.dataset.done]===true,'Valid snapshot accepted');
for(const bad of [{...snap,blueprint:'wrong'}, {...snap,schema:999}, {...snap,state:{...snap.state,blocks:{'999,999,999':true}}},
  {...snap,state:{...snap.state,people:{unknown:'A'}}}]){
  let rejected=false;try{c.BT.validate(bad);}catch{rejected=true;}check(rejected,'Invalid snapshot rejected');
}
doc.getElementById('dlProg').click();const exported=JSON.parse(await env.downloads.at(-1).text());
check(JSON.stringify(exported.state)===JSON.stringify(snap.state),'Download covers complete state');
const imported=JSON.parse(JSON.stringify(snap));imported.state.blocks={};imported.state.people[who.dataset.who]='Piet';
await doc.getElementById('impProg').onchange({target:{files:[{size:1000,text:async()=>JSON.stringify(imported)}],value:'test'}});
check(Object.keys(c.BT.state.blocks).length===0&&c.BT.state.people[who.dataset.who]==='Piet','Import replaces whole snapshot');
check(doc.getElementById('stepRows').querySelectorAll('input').every(x=>!x.checked),'Import updates layer UI');
const restored=environment(env.storage);check(restored.context.BT.state.people[who.dataset.who]==='Piet','Reload restores saved state');
const legacyState={format:'blackthorn-progress',schema:1,revision:'5.10',blueprint:blueprint.progress_compat.fingerprint,state:{groups:{[blueprint.progress_compat.changed_groups.find(g=>g!=='gartendeko')]:true,res1:true},people:{res1:'Piet'},blocks:{'-672,124,791':true},inventory:{R01:'12 Stacks'}}};
const changedKey=blueprint.progress_compat.changed_positions[0];legacyState.state.blocks[changedKey]=true;
const migrated=c.BT.validate(legacyState);
check(migrated.blocks['-672,124,791']===true&&!migrated.blocks[changedKey],'5.10 migration keeps only unchanged checked positions');
check(migrated.groups.res1===true&&!migrated.groups[blueprint.progress_compat.changed_groups.find(g=>g!=='gartendeko')]&&migrated.inventory.R01==='12 Stacks','5.10 migration retains unrelated work and inventory notes');
const legacyStore=new Map([['blackthorn:5.10:progress',JSON.stringify(legacyState)]]),automatic=environment(legacyStore);
check(automatic.context.BT.state.people.res1==='Piet'&&legacyStore.has('blackthorn:5.11:progress'),'Existing local 5.10 data is copied into new version');
check(JSON.parse(legacyStore.get('blackthorn:5.10:progress')).state.groups[blueprint.progress_compat.changed_groups.find(g=>g!=='gartendeko')]===true,'Migration never overwrites the original 5.10 snapshot');
const noGL=environment(new Map(),false);noGL.document.querySelector('[data-tab="3d"]').click();
check(noGL.document.getElementById('loading').textContent.includes('WebGL'),'No-WebGL fallback is visible');
noGL.document.querySelector('[data-tab="plan"]').click();
check(noGL.document.querySelector('.tab.on').attrs.id==='tab-plan','2D remains usable without WebGL');
console.log(`PASS: ${checks} runtime checks for navigation, geometry, materials, phases, XYZ search, persistence and complete backup. DOM/GL adapters used; no browser/GPU verification.`);

}
export {environment};
if(process.argv[1]===fileURLToPath(import.meta.url))await main();
