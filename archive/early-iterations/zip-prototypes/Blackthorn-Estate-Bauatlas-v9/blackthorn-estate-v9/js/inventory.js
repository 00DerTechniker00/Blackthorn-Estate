import {materialItems,download} from './model.js';
export class Inventory{
 constructor(model){this.model=model;this.key='blackthorn-v9-stock-'+model.total_blocks;try{this.data=JSON.parse(localStorage.getItem(this.key)||'{}')}catch{this.data={}}}
 get(item){return Number.isSafeInteger(this.data[item])&&this.data[item]>=0?this.data[item]:0}
 set(item,n){if(!Number.isSafeInteger(n)||n<0)throw Error('Vorrat muss eine nichtnegative ganze Zahl sein');this.data[item]=n;this.save()}
 save(){localStorage.setItem(this.key,JSON.stringify(this.data))}
 reset(){this.data={};this.save()}
 import(obj){if(!obj||obj.blueprintBlocks!==this.model.total_blocks||typeof obj.stock!=='object'||Array.isArray(obj.stock))throw Error('Vorratsdatei passt nicht zum Bauplan');const clean={};for(const [k,v] of Object.entries(obj.stock)){if(!/^[a-z0-9_]+$/.test(k)||!Number.isSafeInteger(v)||v<0)throw Error('Ungültiger Bestand für '+k);clean[k]=v}this.data=clean;this.save()}
 export(){download('Blackthorn-Vorrat-v9.json',JSON.stringify({version:9,blueprintBlocks:this.model.total_blocks,stock:this.data},null,2),'application/json')}
 needed(itemId,progress){let total=0;const m=this.model;for(const id of Object.keys(m.counts)){const config=materialItems(m,id);if(config.itemId!==itemId||config.items===null)continue;for(const b of m.blocks){if(b.block!==id||progress.has(b.id))continue;if(id.endsWith('_door')&&b.state?.half!=='lower')continue;if(id.endsWith('_bed')&&b.state?.part!=='foot')continue;total++}}
 return total}
 requirements(progress,group='all'){const m=this.model,byItem=new Map();const blocks=group==='all'?m.blocks:m.byGroup.get(group)||[];for(const b of blocks){if(progress.has(b.id))continue;const config=materialItems(m,b.block,group);if(config.items===null)continue;if(b.block.endsWith('_door')&&b.state?.half!=='lower')continue;if(b.block.endsWith('_bed')&&b.state?.part!=='foot')continue;byItem.set(config.itemId,(byItem.get(config.itemId)||0)+1)}return byItem}
 shortfall(progress,group='all'){const req=this.requirements(progress,group);return [...req].map(([item,needed])=>({item,needed,stock:this.get(item),missing:Math.max(0,needed-this.get(item))}))}
}
