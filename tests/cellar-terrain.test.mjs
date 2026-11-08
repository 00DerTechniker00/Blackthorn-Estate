import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=readFileSync('tools/terrain_viewer.js','utf8');
test('V6 terrain exposes the cellar floor while closing the excavation rim',()=>{
 for(const mode of ['target','work','original']){
  const faces=[],D={structure:{v6:{}},terrain:{bounds:[-711,-709,789,791],heights:[[120,120,120],[120,120,120],[120,120,120]],target_heights:[[128,104,104],[128,104,104],[128,104,104]],surface_blocks:Array.from({length:3},()=>['stone','stone','stone']),target_surface_blocks:Array.from({length:3},()=>['stone','stone','stone']),work:[]}};
  const context={D,S3:{terrainMode:mode},mkB:()=>({}),hash3:()=>.5,DIRV:{north:[0,0,-1],south:[0,0,1],west:[-1,0,0],east:[1,0,0]},addFace:(_b,dir,box)=>faces.push({dir,box})};
  vm.runInNewContext(source,context);context.buildTerrain();
  assert(faces.some(f=>f.dir==='up'&&f.box[0]===-711));
  if(mode==='original')assert(faces.some(f=>f.dir==='up'&&f.box[0]===-710));
  else{assert(!faces.some(f=>f.dir==='up'&&f.box[0]>=-710));const rim=faces.find(f=>f.dir==='east'&&f.box[0]===-711);assert(rim,'missing soil closure');assert.equal(rim.box[1],95);assert.equal(rim.box[4],129);assert(rim.box[3]<-710,'soil face must be behind the masonry');}
 }
});
test('terrain-only target shows the actual surveyed Y95 floor through normal model layers',()=>{
 const app=readFileSync('app.js','utf8'),definition=app.match(/function predNow\(\) \{[^\n]+/)[0];
 const context={S3:{terrainOnly:true,terrain:true,terrainMode:'target'},Y:[95,96],R:[0,1],REG:[{g:'v6_bestand'},{g:'v6_bestand'}]};
 vm.runInNewContext(definition,context);assert(context.predNow()(0));assert(!context.predNow()(1));
 context.S3.terrainMode='original';assert(!context.predNow()(0));
});
test('all 212 boundary faces close the cellar and west shaft without a horizontal lid',()=>{
 const bounds=[-716,-655,764,816],width=62,height=53,faces=[];
 const grid=()=>Array.from({length:height},()=>Array(width).fill(128));
 const context={D:{structure:{v6:{}},terrain:{bounds,heights:grid(),target_heights:grid(),surface_blocks:grid().map(r=>r.map(()=> 'stone')),target_surface_blocks:grid().map(r=>r.map(()=> 'stone')),work:[]}},S3:{terrainMode:'target'},mkB:()=>({}),hash3:()=>.5,DIRV:{north:[0,0,-1],south:[0,0,1],west:[-1,0,0],east:[1,0,0]},addFace:(_b,dir,box)=>faces.push({dir,box})};
 vm.runInNewContext(source,context);context.buildTerrain();
 const boundary=faces.filter(f=>f.dir!=='up'&&[80,95].includes(f.box[1]));
 assert.equal(boundary.length,212);assert(boundary.every(f=>f.box[4]===129));
 assert(boundary.some(f=>f.dir==='north'));assert(boundary.some(f=>f.dir==='south'));assert(boundary.some(f=>f.dir==='east'));assert(boundary.some(f=>f.dir==='west'));
 assert(!faces.some(f=>f.dir==='up'&&f.box[0]===-684&&f.box[2]===790));
});
