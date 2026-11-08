import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,globSync,existsSync} from 'node:fs';
const config=JSON.parse(readFileSync('vercel.json','utf8'));
test('Vercel function includes are valid glob strings and bundle each runtime data file',()=>{
 const expected={
  'api/materials.mjs':['shared-plan.json'],
  'api/build-progress.mjs':['live-plan.json'],
  'api/build-plan.mjs':['live-plan.json','live-server-plan.tsv.gz']
 };
 for(const [entry,files] of Object.entries(expected)){
  assert(existsSync(entry));
  const pattern=config.functions[entry].includeFiles;
  assert.equal(typeof pattern,'string',entry+' includeFiles must be a glob string');
  const included=new Set(globSync(pattern));
  for(const file of files)assert(included.has(file),entry+' is missing '+file);
 }
});
