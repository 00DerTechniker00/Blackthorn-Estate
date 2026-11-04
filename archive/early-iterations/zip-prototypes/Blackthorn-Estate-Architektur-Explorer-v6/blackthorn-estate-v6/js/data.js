import {key} from './utils.js';
const ID=/^[a-z0-9_]+$/;
// Validate only fields used by the viewer, and calculate totals from actual block positions.
// An invalid blueprint is rejected *before* a canvas renderer is constructed.
export function validateBlueprint(d){
 const errors=[],warnings=[];
 if(!d||typeof d!=='object')return {errors:['Kein gültiges JSON-Objekt.'],warnings};
 if(!Array.isArray(d.blocks)||!d.blocks.length||d.blocks.length>250000)errors.push('"blocks" muss ein Array mit 1 bis 250.000 Positionen sein.');
 if(!d.palette||typeof d.palette!=='object')errors.push('Materialpalette fehlt.');
 if(!Array.isArray(d.floors)||!d.floors.length)errors.push('Etagenliste fehlt.');
 if(errors.length)return {errors,warnings};
 const positions=new Set,actual={},actualGroups={};
 for(let i=0;i<d.blocks.length;i++){
  const b=d.blocks[i];if(!b||![b.x,b.y,b.z].every(Number.isInteger)||!ID.test(b.block||'')||!ID.test(b.group||'')){
   errors.push(`Ungültiger Block an Index ${i}.`);if(errors.length>10)break;continue;
  }
  const k=key(b.x,b.y,b.z);if(positions.has(k)){errors.push(`Doppelte Position ${k}`);if(errors.length>10)break;}positions.add(k);
  if(!d.palette[b.block]){errors.push(`Palette enthält minecraft:${b.block} nicht.`);if(errors.length>10)break;}
  if(b.state!=null&&(typeof b.state!=='object'||Array.isArray(b.state)))errors.push(`Blockstates ungültig an Index ${i}.`);
  actual[b.block]=(actual[b.block]||0)+1;actualGroups[b.group]=(actualGroups[b.group]||0)+1;
 }
 for(const f of d.floors)if(!Number.isInteger(f.y)||typeof f.name!=='string')errors.push('Etagenliste enthält einen ungültigen Eintrag.');
 if(Number(d.total_blocks)!==d.blocks.length)warnings.push('Gesamtzahl in den Metadaten weicht ab; tatsächliche Positionen werden verwendet.');
 for(const [id,count] of Object.entries(actual))if(d.counts?.[id]!==count){warnings.push(`Materialanzahl ${id} wurde neu berechnet.`);break}
 for(const [name,count] of Object.entries(actualGroups))if(d.groups?.[name]!==count){warnings.push(`Baugruppenzahl ${name} wurde neu berechnet.`);break}
 return {errors,warnings,actual,actualGroups};
}
export async function loadBlueprint(){
 const response=await fetch('blueprint.json');if(!response.ok)throw new Error(`Blueprint konnte nicht geladen werden (HTTP ${response.status}).`);
 const raw=await response.json();const audit=validateBlueprint(raw);if(audit.errors.length)throw new Error('Blueprint-Validierung: '+audit.errors.slice(0,5).join(' · '));
 const model={...raw,counts:audit.actual,groups:audit.actualGroups,total_blocks:raw.blocks.length,warnings:audit.warnings};
 model.index=new Map;model.byY=new Map;model.byGroup=new Map;model.countsByGroup=new Map;
 let bounds={minX:Infinity,minY:Infinity,minZ:Infinity,maxX:-Infinity,maxY:-Infinity,maxZ:-Infinity};
 model.blocks.forEach((b,i)=>{
  model.index.set(key(b.x,b.y,b.z),b);
  if(!model.byY.has(b.y))model.byY.set(b.y,[]);model.byY.get(b.y).push(b);
  if(!model.byGroup.has(b.group))model.byGroup.set(b.group,[]);model.byGroup.get(b.group).push(b);
  if(!model.countsByGroup.has(b.group))model.countsByGroup.set(b.group,new Map);
  const cm=model.countsByGroup.get(b.group);cm.set(b.block,(cm.get(b.block)||0)+1);
  bounds.minX=Math.min(bounds.minX,b.x);bounds.maxX=Math.max(bounds.maxX,b.x);
  bounds.minY=Math.min(bounds.minY,b.y);bounds.maxY=Math.max(bounds.maxY,b.y);
  bounds.minZ=Math.min(bounds.minZ,b.z);bounds.maxZ=Math.max(bounds.maxZ,b.z);
 });
 model.bounds=bounds;
 model.floors=[...model.floors].sort((a,b)=>a.y-b.y);
 model.features=Array.isArray(model.features)?model.features:[];
 return model;
}
export function filteredBlocks(model,{displayMode,layerY,group,floorY}){
 let arr;
 const mode=displayMode;
 if(mode==='all')arr=model.blocks;
 else if(mode==='single')arr=model.byY.get(layerY)||[];
 else if(mode==='below')arr=model.blocks.filter(b=>b.y<=layerY);
 else {
  const next=model.floors.find(f=>f.y>floorY)?.y??floorY+15;
  arr=model.blocks.filter(b=>b.y>=floorY&&b.y<next);
 }
 return group==='all'?arr:arr.filter(b=>b.group===group);
}
export function floorAtY(model,y){return [...model.floors].reverse().find(f=>f.y<=y)?.y??model.floors[0].y}
