import test from 'node:test';
import assert from 'node:assert/strict';
import {createBuildHandler} from '../server/build-progress.mjs';
const plan={fingerprint:'test-plan',positions:5,revision:'5.26'},time=1800000000000;
const env={SHARED_LIST_TEAM_CODE:'team-code-123456789',LIVE_BUILD_WRITE_TOKEN:'separate-writer-token-1234567890123456789',KV_REST_API_URL:'https://example.invalid',KV_REST_API_TOKEN:'db-secret',VERCEL_ENV:'production'};
function setup(){
 const values=new Map(),calls=[];
 const fetcher=async(url,opts)=>{const c=JSON.parse(opts.body);calls.push(c);let result;
  if(c[0]==='GET')result=values.get(c[1])||null;
  else{assert.equal(c[0],'EVAL');const old=values.get(c[3]);result=old&&JSON.parse(old).sampledAt>=Number(c[4])?0:1;if(result)values.set(c[3],c[5]);}
  return {ok:true,json:async()=>({result})};};
 return {values,calls,handler:(overrides={})=>createBuildHandler({plan,env:{...env,...overrides},fetcher,now:()=>time})};
}
async function call(handler,{method='GET',token=env.SHARED_LIST_TEAM_CODE,body,headers={}}={}){
 const res={setHeader(){},status(s){this.statusCode=s;return this;},json(b){this.body=b;return this;}};
 await handler({method,headers:{authorization:'Bearer '+token,'content-type':'application/json',...headers},body},res);return res;
}
const payload=(extra={})=>({fingerprint:plan.fingerprint,sampledAt:time,states:'01234',...extra});
test('plugin writes, team reads; credentials are separate and never exposed',async()=>{
 const db=setup(),handler=db.handler();
 assert.equal((await call(handler)).body.snapshot,null);
 assert.equal((await call(handler,{method:'POST',body:payload()})).statusCode,401);
 assert.equal((await call(handler,{token:env.LIVE_BUILD_WRITE_TOKEN})).statusCode,401);
 assert.equal((await call(handler,{method:'POST',token:env.LIVE_BUILD_WRITE_TOKEN,body:payload()})).statusCode,200);
 const result=await call(handler);assert.equal(result.body.snapshot.states,'01234');assert.equal(result.body.snapshot.receivedAt,time);
 assert(!JSON.stringify(result.body).includes(env.KV_REST_API_TOKEN));assert(!JSON.stringify(result.body).includes(env.LIVE_BUILD_WRITE_TOKEN));
});
test('wrong plans, malformed states and timestamps do not reach Redis',async()=>{
 const db=setup(),handler=db.handler();
 for(const body of [payload({fingerprint:'wrong'}),payload({states:'123'}),payload({states:'0123x'}),payload({sampledAt:time+60001}),payload({sampledAt:time-300001})]){
  assert([400,409].includes((await call(handler,{method:'POST',token:env.LIVE_BUILD_WRITE_TOKEN,body})).statusCode));
 }
 assert.equal(db.calls.length,0);
});
test('old uploads cannot overwrite a newer snapshot and preview is separate',async()=>{
 const db=setup(),handler=db.handler();
 await call(handler,{method:'POST',token:env.LIVE_BUILD_WRITE_TOKEN,body:payload()});
 assert.equal((await call(handler,{method:'POST',token:env.LIVE_BUILD_WRITE_TOKEN,body:payload({sampledAt:time-1,states:'11111'})})).statusCode,409);
 assert.equal((await call(handler)).body.snapshot.states,'01234');
 assert.equal((await call(db.handler({VERCEL_ENV:'preview'}))).body.snapshot,null);
});
test('missing configuration, cross-site requests and methods fail closed',async()=>{
 const db=setup();assert.equal((await call(db.handler({SHARED_LIST_TEAM_CODE:''}))).statusCode,503);
 assert.equal((await call(db.handler(),{method:'DELETE'})).statusCode,405);
 assert.equal((await call(db.handler(),{headers:{'sec-fetch-site':'cross-site'}})).statusCode,403);
 assert.equal(db.calls.length,0);
});

test('compressed plugin snapshots decode safely and are stored compressed',async()=>{
 const {gzipSync}=await import('node:zlib');const db=setup(),handler=db.handler();
 const packed={fingerprint:plan.fingerprint,sampledAt:time,statesGzip:gzipSync('01234').toString('base64')};
 assert.equal((await call(handler,{method:'POST',token:env.LIVE_BUILD_WRITE_TOKEN,body:packed})).statusCode,200);
 assert.equal((await call(handler)).body.snapshot.states,'01234');
 assert(![...db.values.values()][0].includes('01234'));
 for(const statesGzip of ['invalid',gzipSync('1'.repeat(100)).toString('base64')]){
  assert.equal((await call(handler,{method:'POST',token:env.LIVE_BUILD_WRITE_TOKEN,body:{...packed,statesGzip}})).statusCode,400);
 }
});
