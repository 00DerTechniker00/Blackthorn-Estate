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
  for(const name of ['progress','logistics','app','steps','terrain','system']){
    let source=fs.readFileSync(path.join(root,name+'.js'),'utf8');
    if(name==='app')source=source.replace(/\}\)\(\);\s*$/,`window.testHooks={renderMat,renderCoord,renderBuild,PHASES,rayBlock,cameraBasis,viewProjection,buildModel,buildTerrain,predNow,getGL:()=>GL};})();`);
    vm.runInContext(source,context,{filename:name+'.js'});
  }
  return {context,document,storage,downloads,runTimers(){while(timers.length)timers.shift()();},frame(){frames.shift()?.();},stats:()=>({drawCalls,uploadedFloats})};
}

async function main(){
const env=environment(),{context:c,document:doc}=env;
check(doc.getElementById('st-blocks').textContent===blueprint.meta.total.toLocaleString('de-DE'),'Overview initializes');
check(doc.querySelector('.tab.on').attrs.id==='tab-overview','Initial overview selected');
for(const button of doc.querySelectorAll('#tabs button')){
  button.click();env.runTimers();env.frame();
  check(doc.querySelector('.tab.on').attrs.id==='tab-'+button.dataset.tab,'Navigation '+button.dataset.tab);
}
check(env.stats().uploadedFloats>1000000,'Real block and terrain geometry uploaded with finite coordinates');
check(env.stats().drawCalls>0,'3D render path draws geometry');
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
check(doc.getElementById('storageZones').querySelectorAll('article').length===56,'All warehouse and private bays appear in storage UI');
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
const noGL=environment(new Map(),false);noGL.document.querySelector('#tabs button[data-tab="3d"]').click();
check(noGL.document.getElementById('loading').textContent.includes('WebGL'),'No-WebGL fallback is visible');
noGL.document.querySelector('#tabs button[data-tab="plan"]').click();
check(noGL.document.querySelector('.tab.on').attrs.id==='tab-plan','2D remains usable without WebGL');
console.log(`PASS: ${checks} runtime checks for navigation, geometry, materials, phases, XYZ search, persistence and complete backup. DOM/GL adapters used; no browser/GPU verification.`);

}
export {environment};
if(process.argv[1]===fileURLToPath(import.meta.url))await main();
