import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=readFileSync('app.js','utf8');
function setup(th=-Math.PI/2,ph=.02){
 const points=[[-684,95,790],[-681,95,789],[-682,95,785]],lookup=new Map(points.map((p,i)=>[p.join(','),i]));
 const context={GL:{cam:{t:{x:-684,y:95,z:-790},d:100,th,ph}},Float32Array,Math,S3:{single:false,ymax:105},BB:[-700,-660,90,110,770,810],predNow:()=>()=>true,at:(x,y,z)=>lookup.get([x,y,z].join(','))??-1,$:()=>({width:1024,height:1024,getBoundingClientRect:()=>({left:0,top:0,width:1024,height:1024})})};
 for(const name of ['cameraBasis','viewProjection','rayBlock'])vm.runInNewContext(source.match(new RegExp('function '+name+'\\([^]*?^}', 'm'))[0],context);
 function project([x,y,z]){
  const matrix=context.viewProjection(),p=[x,y,-z,1],q=[0,0,0,0];
  for(let r=0;r<4;r++)for(let k=0;k<4;k++)q[r]+=matrix[k*4+r]*p[k];
  return [q[0]/q[3],q[1]/q[3]];
 }
 return {context,project,points};
}
test('north-up 3D top view agrees with the X-right / Z-down map axes',()=>{
 const {project}=setup(),center=project([-684,95,790]),east=project([-681,95,790]),north=project([-684,95,787]);
 assert(east[0]>center[0],'East (+X) must be on the right');
 assert(north[1]>center[1],'North (-Z) must be at the top');
});
test('orbiting the scene preserves the physical orientation of cardinal directions',()=>{
 for(const [name,th,point,side] of [['north',Math.PI/2,[3,0,0],-1],['south',-Math.PI/2,[3,0,0],1],['east',0,[0,0,-3],1],['west',Math.PI,[0,0,-3],-1]]){
  const {project}=setup(th,1),center=project([-684,95,790]),p=project([-684+point[0],95,790+point[2]]);
  assert((p[0]-center[0])*side>0,name+' view is mirrored');
 }
});
test('click rays recover the exact original world coordinates after projection',()=>{
 for(const [th,ph] of [[-Math.PI/2,.02],[.75,.95],[Math.PI/2,1.1]]){
  const {context,project,points}=setup(th,ph);
  for(const [i,p] of points.entries()){
   const q=project(p.map(v=>v+.5));
   const hit=context.rayBlock({clientX:(q[0]+1)*512,clientY:(1-q[1])*512});
   assert.equal(hit,i,'Wrong block for '+p.join(','));
  }
 }
});
test('2D floor plan uses east-right / south-down coordinates and clicks negative X correctly',()=>{
 const info={},picked=[];
 const context={PL:{mode:'y',val:95,s:10,ox:7000,oy:-7500},X:[-684,-681,-684],Y:[95,95,95],Z:[790,790,787],devicePixelRatio:2,pc:{getBoundingClientRect:()=>({left:0,top:0})},at:(...p)=>{picked.push(p);return -1;},$:()=>info};
 vm.runInNewContext(source.match(/function planUV\(i\) \{[^\n]+/)[0],context);
 vm.runInNewContext(source.match(/function planHover\([^]*?^}/m)[0],context);
 assert(context.planUV(1)[0]>context.planUV(0)[0]);assert(context.planUV(2)[1]<context.planUV(0)[1]);
 context.planHover({clientX:82.5,clientY:202.5},false);assert.deepEqual(picked[0],[-684,95,790]);
});
test('terrain map picks the same Minecraft coordinate as the floor plan',()=>{
 const terrain=readFileSync('terrain.js','utf8'),context={x0:-825,z0:680,scale:2,ox:10,oz:10,canvas:{width:1200,height:1000,getBoundingClientRect:()=>({left:0,top:0,width:600,height:500})}};
 vm.runInNewContext(terrain.match(/function coord\(e\)\{[^\n]+/)[0],context);
 const result=context.coord({clientX:146.5,clientY:115.5});assert.equal(result.x,-684);assert.equal(result.z,790);
});
