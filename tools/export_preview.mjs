/* Export actual app geometry for a deterministic software-rendered preview. */
import {environment} from './test_app.mjs';
import fs from 'node:fs';
const blueprint=JSON.parse(fs.readFileSync(new URL('../blueprint.json',import.meta.url)));
const env=environment();
const hooks=env.context.testHooks;
const layers=hooks.buildModel(hooks.predNow()),faces=[];
for(const layer of Object.values(layers))for(const [key,B] of Object.entries(layer)){
  if(key==='caps')continue;
  for(let i=0;i<B.p.length;i+=12)faces.push([B.p.slice(i,i+12),B.c.slice(i,i+3),key==='glass'?.48:1]);
}
const terrain=hooks.buildTerrain();
for(let i=0;i<terrain.p.length;i+=12)faces.push([terrain.p.slice(i,i+12),terrain.c.slice(i,i+3),1]);
fs.writeFileSync('/tmp/blackthorn-511-geometry.json',JSON.stringify(faces));
console.log('Geometry exported:',faces.length,'quads');

for(const [name,fixture] of [
  ['pendant',blueprint.lighting.fixtures.find(f=>f.hanging&&f.chain===2)],
  ['standing',blueprint.lighting.fixtures.find(f=>!f.hanging&&f.y>=129)]
]) {
  env.context.__focusFixture(fixture);env.runTimers();
  const detail=[];
  for(const layer of Object.values(hooks.buildModel(hooks.predNow())))for(const [key,B] of Object.entries(layer)) {
    if(key==='caps')continue;
    for(let i=0;i<B.p.length;i+=12)detail.push([B.p.slice(i,i+12),B.c.slice(i,i+3),key==='glass'?.48:1]);
  }
  fs.writeFileSync(`/tmp/blackthorn-511-${name}.json`,JSON.stringify({faces:detail,fixture}));
}
