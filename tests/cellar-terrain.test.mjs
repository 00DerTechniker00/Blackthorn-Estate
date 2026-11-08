import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=readFileSync('tools/terrain_viewer.js','utf8');
test('V6 terrain cannot cover the cellar floor or create brown faces at the excavation rim',()=>{
 for(const mode of ['target','work','original']){
  const faces=[],D={structure:{v6:{}},terrain:{bounds:[-711,-709,789,791],heights:[[120,120,120],[120,120,120],[120,120,120]],target_heights:[[128,104,104],[128,104,104],[128,104,104]],surface_blocks:Array.from({length:3},()=>['stone','stone','stone']),target_surface_blocks:Array.from({length:3},()=>['stone','stone','stone']),work:[]}};
  const context={D,S3:{terrainMode:mode},mkB:()=>({}),hash3:()=>.5,DIRV:{north:[0,0,-1],south:[0,0,1],west:[-1,0,0],east:[1,0,0]},addFace:(_b,dir,box)=>faces.push({dir,box})};
  vm.runInNewContext(source,context);context.buildTerrain();
  assert(faces.some(f=>f.dir==='up'&&f.box[0]===-711));
  if(mode==='original')assert(faces.some(f=>f.dir==='up'&&f.box[0]===-710));
  else{assert(!faces.some(f=>f.dir==='up'&&f.box[0]>=-710));assert(!faces.some(f=>f.dir==='east'&&f.box[0]===-711));}
 }
});
test('terrain-only target shows the actual surveyed Y95 floor through normal model layers',()=>{
 const app=readFileSync('app.js','utf8'),definition=app.match(/function predNow\(\) \{[^\n]+/)[0];
 const context={S3:{terrainOnly:true,terrain:true,terrainMode:'target'},Y:[95,96],R:[0,1],REG:[{g:'v6_bestand'},{g:'v6_bestand'}]};
 vm.runInNewContext(definition,context);assert(context.predNow()(0));assert(!context.predNow()(1));
 context.S3.terrainMode='original';assert(!context.predNow()(0));
});
