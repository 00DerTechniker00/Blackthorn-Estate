import test from 'node:test';
import assert from 'node:assert/strict';
import {createHandler,UPDATE_SCRIPT} from '../server/shared-materials.mjs';
const plan={meta:{version:'5.26',fingerprint:'plan-1'},material_scopes:{house:{counts:{stone_bricks:100,glass:20}},outdoor:{counts:{stone_bricks:10}},terrain:{counts:{dirt:1000}}}};
const environment={SHARED_LIST_TEAM_CODE:'test-team-code-123456789',UPSTASH_REDIS_REST_URL:'https://example.upstash.io',UPSTASH_REDIS_REST_TOKEN:'private-test-token',VERCEL_ENV:'production'};
function store(){
  const hashes=new Map(),calls=[];
  const fetcher=async(url,options)=>{
    const command=JSON.parse(options.body);calls.push({url,command,headers:options.headers});
    const get=key=>{if(!hashes.has(key))hashes.set(key,new Map());return hashes.get(key);};
    if(command[0]==='HGETALL')return {ok:true,json:async()=>({result:[...get(command[1])].flat()})};
    assert.equal(command[0],'EVAL');assert.equal(command[1],UPDATE_SCRIPT);assert.equal(command[2],'1');
    const [, , ,key,field,version,mutation,patch,author,time]=command;
    const hash=get(key),current=JSON.parse(hash.get(field)||'{"amount":0,"done":false,"note":"","version":0}');
    if(current.mutation===mutation)return {ok:true,json:async()=>({result:JSON.stringify({ok:true,row:current})})};
    if(current.version!==Number(version))return {ok:true,json:async()=>({result:JSON.stringify({ok:false,row:current})})};
    const next={...current,...JSON.parse(patch),version:current.version+1,mutation,updatedBy:author,updatedAt:time};
    hash.set(field,JSON.stringify(next));return {ok:true,json:async()=>({result:JSON.stringify({ok:true,row:next})})};
  };
  return {hashes,calls,fetcher};
}
async function call(handler,{method='GET',body,headers={}}={}){
  const res={headers:{},setHeader(k,v){this.headers[k]=v;},status(code){this.statusCode=code;return this;},json(value){this.body=value;return this;}};
  await handler({method,headers:{authorization:'Bearer '+environment.SHARED_LIST_TEAM_CODE,'content-type':'application/json',...headers},body},res);return res;
}
const patch=(extra={})=>({scope:'house',item:'stone_bricks',fingerprint:'plan-1',expectedVersion:0,mutation:'test-mutation-12345',author:'Piet',changes:{amount:12},...extra});
const handlerFor=(db,env=environment)=>createHandler({plan,env,fetcher:db.fetcher,now:()=> '2026-11-08T12:00:00Z'});

test('configuration stays closed, and secrets are never returned',async()=>{
  const db=store(),handler=handlerFor(db,{}),result=await call(handler);
  assert.equal(result.statusCode,503);assert.equal(result.body.code,'SETUP_REQUIRED');assert.equal(db.calls.length,0);
});
test('team authentication is required before any database request',async()=>{
  const db=store(),handler=handlerFor(db);
  for(const authorization of ['', 'Bearer wrong', ['not','a','string']]){
    const response=await call(handler,{headers:{authorization}});assert.equal(response.statusCode,401);
  }
  assert.equal(db.calls.length,0);
});
test('save, read on a second client, and clear a checkbox without losing stock',async()=>{
  const db=store(),handler=handlerFor(db);
  let result=await call(handler,{method:'PATCH',body:patch({changes:{amount:12,done:true,note:'Keller R01'}})});
  assert.equal(result.statusCode,200);assert.equal(result.body.row.version,1);
  result=await call(handler);assert.equal(result.body.entries['house:stone_bricks'].note,'Keller R01');
  assert(!JSON.stringify(result.body).includes(environment.UPSTASH_REDIS_REST_TOKEN));
  result=await call(handler,{method:'PATCH',body:patch({expectedVersion:1,mutation:'test-mutation-54321',changes:{done:false}})});
  assert.equal(result.body.row.done,false);assert.equal(result.body.row.amount,12);assert.equal(result.body.row.note,'Keller R01');
});
test('concurrent edits of the same row conflict; a reviewed retry preserves other fields',async()=>{
  const db=store(),handler=handlerFor(db);
  const results=await Promise.all([
    call(handler,{method:'PATCH',body:patch()}),
    call(handler,{method:'PATCH',body:patch({mutation:'other-mutation-12345',author:'Alex',changes:{note:'Truhe 2'}})})
  ]);
  assert.deepEqual(results.map(r=>r.statusCode).sort(),[200,409]);
  const conflict=results.find(r=>r.statusCode===409);assert.equal(conflict.body.code,'ROW_CONFLICT');assert.equal(conflict.body.row.amount,12);
  const retry=await call(handler,{method:'PATCH',body:patch({expectedVersion:1,mutation:'reviewed-retry-12345',author:'Alex',changes:{note:'Truhe 2'}})});
  assert.equal(retry.body.row.amount,12);assert.equal(retry.body.row.note,'Truhe 2');
});
test('different materials and disjoint scopes do not overwrite each other',async()=>{
  const db=store(),handler=handlerFor(db);
  const results=await Promise.all([
    call(handler,{method:'PATCH',body:patch()}),
    call(handler,{method:'PATCH',body:patch({item:'glass',mutation:'glass-mutation-12345',changes:{amount:5}})}),
    call(handler,{method:'PATCH',body:patch({scope:'outdoor',mutation:'outdoor-mutation-12345',changes:{amount:3}})})
  ]);
  assert(results.every(r=>r.statusCode===200));const data=(await call(handler)).body.entries;
  assert.equal(data['house:stone_bricks'].amount,12);assert.equal(data['house:glass'].amount,5);assert.equal(data['outdoor:stone_bricks'].amount,3);
});
test('a lost-response retry is idempotent',async()=>{
  const db=store(),handler=handlerFor(db);
  await call(handler,{method:'PATCH',body:patch()});const again=await call(handler,{method:'PATCH',body:patch()});
  assert.equal(again.statusCode,200);assert.equal(again.body.row.version,1);
});
test('bad inputs never reach Redis',async()=>{
  const db=store(),handler=handlerFor(db);
  for(const body of [patch({item:'__proto__'}),patch({scope:'all'}),patch({author:''}),patch({expectedVersion:-1}),patch({mutation:'short'}),patch({changes:{amount:-1}}),patch({changes:{amount:1.2}}),patch({changes:{amount:1_000_000_001}}),patch({changes:{done:'yes'}}),patch({changes:{note:'x'.repeat(241)}}),patch({changes:{administrator:true}}),patch({changes:{}})]){
    assert.equal((await call(handler,{method:'PATCH',body})).statusCode,400);
  }
  assert.equal(db.calls.length,0);
});
test('a changed plan requires reloading; unsupported methods and content types are rejected',async()=>{
  const db=store(),handler=handlerFor(db);
  assert.equal((await call(handler,{method:'PATCH',body:patch({fingerprint:'old-plan'})})).body.code,'PLAN_CHANGED');
  assert.equal((await call(handler,{method:'DELETE'})).statusCode,405);
  assert.equal((await call(handler,{method:'PATCH',body:patch(),headers:{'content-type':'text/plain'}})).statusCode,415);
  assert.equal((await call(handler,{headers:{'sec-fetch-site':'cross-site'}})).statusCode,403);
  assert.equal(db.calls.length,0);
});
test('database outages return a recoverable message without credentials',async()=>{
  const handler=createHandler({plan,env:environment,fetcher:async()=>{throw Error('secret-token');}});
  const result=await call(handler);assert.equal(result.statusCode,503);assert.equal(result.body.code,'STORE_UNAVAILABLE');assert(!JSON.stringify(result.body).includes('secret-token'));
});
test('Vercel KV variables work and preview data is isolated from production',async()=>{
  const db=store();
  const env={...environment,UPSTASH_REDIS_REST_URL:undefined,UPSTASH_REDIS_REST_TOKEN:undefined,KV_REST_API_URL:'https://example.upstash.io',KV_REST_API_TOKEN:'token'};
  const production=handlerFor(db,env),preview=handlerFor(db,{...env,VERCEL_ENV:'preview'});
  await call(production,{method:'PATCH',body:patch()});assert.deepEqual((await call(preview)).body.entries,{});
  const result=await call(preview,{method:'PATCH',body:patch({changes:{amount:99}})});assert.equal(result.statusCode,200);
  assert.equal((await call(production)).body.entries['house:stone_bricks'].amount,12);
});
