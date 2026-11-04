import {readFileSync} from 'node:fs';
const m=JSON.parse(readFileSync(new URL('../blueprint.json',import.meta.url),'utf8'));
let seen=new Set(),counts={},groups={},lastY=-Infinity;
for(let i=0;i<m.blocks.length;i++){
 const b=m.blocks[i];if(b.id!==i+1)throw Error('ID sequence at '+i);
 if(b.y<lastY)throw Error('Y order at '+i);lastY=b.y;
 if(!['x','y','z'].every(k=>Number.isInteger(b[k])))throw Error('noninteger at '+i);
 const key=[b.x,b.y,b.z].join('/');if(seen.has(key))throw Error('duplicate '+key);seen.add(key);
 if(!m.palette[b.block])throw Error('material missing '+b.block);
 counts[b.block]=(counts[b.block]||0)+1;groups[b.group]=(groups[b.group]||0)+1;
}
if(m.blocks.length!==m.total_blocks)throw Error('total mismatch');
for(const [id,n] of Object.entries(counts))if(m.counts[id]!==n)throw Error('count '+id);
for(const [id,n] of Object.entries(groups))if(m.groups[id]!==n)throw Error('group '+id);
if(m.storage_zones.filter(z=>[93,105,117].includes(z.floorY)).length!==18)throw Error('storage zone count');
const doors=m.blocks.filter(b=>b.block.endsWith('_door'));
if(doors.filter(b=>b.state?.half==='lower').length!==doors.filter(b=>b.state?.half==='upper').length)throw Error('door halves mismatch');
const decode=(s)=>{const lines=s.replace(/^\uFEFF/,'').trim().split(/\r?\n/);const cols=lines[0].split(';');return lines.slice(1).map(line=>{const fields=[];let value='',quoted=false;for(let i=0;i<line.length;i++){const c=line[i];if(c==='\"'){if(quoted&&line[i+1]==='\"'){value+='\"';i++}else quoted=!quoted}else if(c===';'&&!quoted){fields.push(value);value=''}else value+=c}fields.push(value);if(fields.length!==cols.length)throw Error('CSV field count mismatch '+line.slice(0,100));return Object.fromEntries(cols.map((k,i)=>[k,fields[i]]))})};
const blocksCsv=decode(readFileSync(new URL('../blockliste.csv',import.meta.url),'utf8'));
if(blocksCsv.length!==m.blocks.length)throw Error('blockliste CSV count');
const first=blocksCsv[0], keys=Object.keys(first);console.log('Block columns:',keys.slice(0,8));
for(let i=0;i<m.blocks.length;i++){const row=blocksCsv[i],b=m.blocks[i];if(Number(row['#'])!==b.id||Number(row.X)!==b.x||Number(row.Y)!==b.y||Number(row.Z)!==b.z||row['Minecraft-ID']!=='minecraft:'+b.block||row.Baugruppe!==b.group)throw Error('blockliste row '+(i+1)+' does not match blueprint');}
const materialsCsv=decode(readFileSync(new URL('../materialbedarf.csv',import.meta.url),'utf8'));
for(const row of materialsCsv){if(Number(row.Blockpositionen)!==counts[row.Block])throw Error('material count mismatch '+row.Block)}
const zonesCsv=decode(readFileSync(new URL('../lagersystem.csv',import.meta.url),'utf8'));
if(zonesCsv.length!==m.storage_zones.length)throw Error('storage zones CSV count mismatch');
const terrain=m.terrain; if(!terrain)throw Error('missing terrain heightmap metadata');
const outside=m.blocks.filter(b=>b.x<m.site.terrain_bounds[0]||b.x>m.site.terrain_bounds[1]||b.z<m.site.terrain_bounds[2]||b.z>m.site.terrain_bounds[3]);
console.log('Terrain coverage warning: '+outside.length+' building blocks outside known bounds (not an error: no invented terrain).');
console.log('OK:',m.blocks.length,'numbered positions; types',Object.keys(counts).length,'groups',Object.keys(groups).length,'warehouse zones',18,'doors balanced');
