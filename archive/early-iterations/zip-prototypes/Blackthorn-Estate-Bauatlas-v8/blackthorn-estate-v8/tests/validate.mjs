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
console.log('OK:',m.blocks.length,'numbered positions; types',Object.keys(counts).length,'groups',Object.keys(groups).length,'warehouse zones',18,'doors balanced');
