import test from 'node:test';
import assert from 'node:assert/strict';
import {gzipSync} from 'node:zlib';
import {createPlanHandler} from '../server/build-plan.mjs';
const fingerprint='a'.repeat(64),plan={fingerprint,revision:'6.0',positions:1};
const bytes=gzipSync(fingerprint+'\t6.0\n-700\t95\t790\tminecraft:stone\n');
const secret='private-plugin-token-12345678901234567890';
function call(handler,headers={},method='GET'){
 const res={headers:{},setHeader(k,v){this.headers[k]=v;},status(s){this.statusCode=s;return this;},json(b){this.body=b;return this;},send(b){this.body=b;return this;},end(){return this;}};
 handler({method,headers:{authorization:'Bearer '+secret,...headers}},res);return res;
}
test('only plugin credential can download the current plan; matching fingerprint returns 304',()=>{
 const handler=createPlanHandler({plan,bytes,env:{LIVE_BUILD_WRITE_TOKEN:secret}});
 assert.equal(call(handler,{authorization:''}).statusCode,401);
 assert.equal(call(handler,{authorization:'Bearer team-code-123456789'}).statusCode,401);
 const result=call(handler);assert.equal(result.statusCode,200);assert(result.body.equals(bytes));
 assert.equal(result.headers['X-Blackthorn-Fingerprint'],fingerprint);assert.equal(result.headers['X-Blackthorn-Plan-Schema'],'1');assert.equal(result.headers['X-Blackthorn-Positions'],'1');
 assert.equal(call(handler,{'if-none-match':'"'+fingerprint+'"'}).statusCode,304);
});
test('invalid packaging, missing config and unsupported methods fail clearly',()=>{
 assert.equal(call(createPlanHandler({plan:{...plan,positions:2},bytes,env:{LIVE_BUILD_WRITE_TOKEN:secret}})).statusCode,503);
 assert.equal(call(createPlanHandler({plan,bytes,env:{}})).statusCode,503);
 assert.equal(call(createPlanHandler({plan,bytes,env:{LIVE_BUILD_WRITE_TOKEN:secret}}),{},'POST').statusCode,405);
});
