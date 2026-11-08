import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
const source=readFileSync('shared-list.js','utf8');
const plan={meta:{version:'5.26',fingerprint:'p1'},material_scopes:{house:{counts:{stone:10,glass:5}},outdoor:{counts:{stone:4}},terrain:{counts:{dirt:20}}}};
const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const unescape=v=>v.replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function api(){
 const state={entries:{},calls:[],fail:false};
 state.fetch=async(_url,options)=>{
  state.calls.push(options);if(state.fail)throw Error('offline');
  if(options.method==='GET')return {ok:true,json:async()=>({entries:structuredClone(state.entries),fingerprint:'p1',serverTime:'2026-11-08T12:00:00Z'})};
  const body=JSON.parse(options.body),key=body.scope+':'+body.item,prior=state.entries[key]||{amount:0,done:false,note:'',version:0};
  if(prior.version!==body.expectedVersion)return {ok:false,status:409,json:async()=>({code:'ROW_CONFLICT',error:'conflict',row:structuredClone(prior)})};
  const row={...prior,...body.changes,version:prior.version+1,updatedBy:body.author,updatedAt:'2026-11-08T12:01:00Z'};state.entries[key]=row;
  return {ok:true,json:async()=>({row:structuredClone(row)})};
 };
 return state;
}
function browser(server,{protocol='https:',session=new Map(),profile=new Map()}={}){
 const nodes=new Map(),intervals=[];let doc;
 class Element{
  constructor(id=''){this.id=id;this.value='';this.checked=false;this.hidden=false;this.disabled=false;this.required=false;this.dataset={};this.listeners={};this.fields=[];this.selectionStart=null;this.selectionEnd=null;this.textContent='';const classes=new Set(id==='tab-shared'?['on']:[]);this.classList={contains:k=>classes.has(k),toggle:(k,on)=>on?classes.add(k):classes.delete(k)};}
  addEventListener(type,fn){(this.listeners[type]||=[]).push(fn);}
  fire(type,event){for(const fn of this.listeners[type]||[])fn(event);}
  querySelectorAll(){return this.fields;}
  focus(){doc.activeElement=this;}
  setSelectionRange(){}
  set innerHTML(html){this.html=html;this.fields=[];for(const match of html.matchAll(/<input\s+([^>]+)>/g)){
   const attrs=Object.fromEntries([...match[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(m=>[m[1],unescape(m[2])]));
   if(!attrs['data-shared-key'])continue;
   const el=new Element();el.dataset={sharedKey:attrs['data-shared-key'],sharedField:attrs['data-shared-field']};el.value=attrs.value||'';el.type=attrs.type;el.checked=/\schecked(?:\s|$)/.test(match[1]);el.disabled=/\sdisabled(?:\s|$)/.test(match[1]);this.fields.push(el);
  }}
  get innerHTML(){return this.html||'';}
  requestSubmit(){this.onsubmit?.({preventDefault(){}});}
 }
 const names=['sharedConnection','sharedLogin','sharedName','sharedCode','sharedConnect','sharedSession','sharedIdentity','sharedRefresh','sharedLogout','sharedStatus','sharedWorkspace','sharedScope','sharedQuery','sharedOpenOnly','sharedExport','sharedSummary','sharedRows','tab-shared'];
 for(const name of names)nodes.set(name,new Element(name));nodes.get('sharedScope').value='house';
 doc={getElementById:id=>nodes.get(id),activeElement:null,hidden:false,addEventListener(){},createElement:()=>new Element()};
 const storage=data=>({getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)});
 const window={BLACKTHORN_DATA:plan,__materialName:k=>k,addEventListener(){}};
 vm.runInNewContext(source,{window,document:doc,BT:{escape},location:{protocol},localStorage:storage(profile),sessionStorage:storage(session),crypto:{randomUUID},fetch:server.fetch,AbortSignal,Date,URL,Blob,setTimeout,setInterval:fn=>{intervals.push(fn);}});
 const field=(key,kind)=>nodes.get('sharedRows').fields.find(el=>el.dataset.sharedKey===key&&el.dataset.sharedField===kind);
 return {nodes,intervals,session,profile,field,async login(name='Piet'){nodes.get('sharedName').value=name;nodes.get('sharedCode').value='team-code-123456789';await nodes.get('sharedLogin').onsubmit({preventDefault(){}});},async edit(key,kind,value){const el=field(key,kind);assert(el,'missing input '+key);el.value=String(value);el.checked=!!value;nodes.get('sharedRows').fire('change',{target:el});await flush();}};
}

test('two browser contexts see saved stock, checkboxes and names; code stays out of the list data',async()=>{
 const backend=api(),one=browser(backend),two=browser(backend);
 await one.login('Piet');await two.login('Alex');
 await one.edit('house:stone','amount',7);
 two.intervals[0]();await flush();assert.equal(two.field('house:stone','amount').value,'7');
 await two.edit('house:stone','done',true);
 one.intervals[0]();await flush();assert(one.field('house:stone','done').checked);
 assert.match(one.nodes.get('sharedRows').innerHTML,/Alex/);
 assert(!JSON.stringify(backend.entries).includes('team-code-123456789'));
});
test('a stale row keeps the local edit and asks before applying it to the newest version',async()=>{
 const backend=api(),one=browser(backend),two=browser(backend);await one.login();await two.login('Alex');
 await one.edit('house:stone','amount',7);
 await two.edit('house:stone','note','Truhe 2');
 assert.match(two.nodes.get('sharedRows').innerHTML,/Meine Änderung übernehmen/);assert.equal(backend.entries['house:stone'].note,'');
 const button={dataset:{sharedSave:'house:stone'}};
 two.nodes.get('sharedRows').fire('click',{target:{closest:selector=>selector==='[data-shared-save]'?button:null}});await flush();
 assert.equal(backend.entries['house:stone'].amount,7);assert.equal(backend.entries['house:stone'].note,'Truhe 2');
});
test('offline writes remain explicit unsaved drafts and survive reconnecting the tab',async()=>{
 const backend=api(),session=new Map(),one=browser(backend,{session});await one.login();backend.fail=true;
 await one.edit('house:glass','amount',3);
 assert.match(one.nodes.get('sharedStatus').textContent,/noch nicht gespeichert/);
 assert(session.get('blackthorn:shared:drafts:v1').includes('house:glass'));assert(!backend.entries['house:glass']);
 backend.fail=false;const reloaded=browser(backend,{session,profile:one.profile});await flush();
 assert.equal(reloaded.field('house:glass','amount').value,'3');
});
test('local file mode does not claim a central connection or send requests',()=>{
 const backend=api(),view=browser(backend,{protocol:'file:'});
 assert.equal(view.nodes.get('sharedConnect').disabled,true);assert.equal(backend.calls.length,0);assert.match(view.nodes.get('sharedStatus').textContent,/veröffentlichten Website/);
});
test('names and notes are escaped in table markup',async()=>{
 const backend=api(),view=browser(backend);await view.login('<img src=x onerror=alert(1)>');
 await view.edit('house:stone','note','<script>alert(1)</script>');
 const markup=view.nodes.get('sharedRows').innerHTML;assert(!markup.includes('<script>'));assert(!markup.includes('<img src=x'));assert(markup.includes('&lt;script&gt;'));
});
