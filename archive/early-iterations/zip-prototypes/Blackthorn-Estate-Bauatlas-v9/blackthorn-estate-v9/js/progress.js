import {download} from './model.js';
export class Progress{
 constructor(n){this.n=n;this.bytes=new Uint8Array(Math.ceil(n/8));this.name='blackthorn-v7-bits-'+n;try{const s=localStorage.getItem(this.name);if(s){const raw=atob(s);for(let i=0;i<Math.min(raw.length,this.bytes.length);i++)this.bytes[i]=raw.charCodeAt(i)}}catch(e){console.warn('Fortschritt konnte nicht geladen werden',e)}}
 has(id){if(!id||id>this.n)return false;const i=id-1;return !!(this.bytes[i>>3]&(1<<(i&7)))}
 set(id,v){if(!id||id>this.n)return;const i=id-1;if(v)this.bytes[i>>3]|=1<<(i&7);else this.bytes[i>>3]&=~(1<<(i&7));this.save()}
 count(ids){let n=0;for(const b of ids)if(this.has(typeof b==='object'?b.id:b))n++;return n}
 get total(){let n=0;for(const v of this.bytes){let k=v;while(k){k&=k-1;n++}}return n}
 save(){try{let s='';for(const c of this.bytes)s+=String.fromCharCode(c);localStorage.setItem(this.name,btoa(s))}catch(e){console.warn('Fortschritt konnte nicht gespeichert werden',e)}}
 clear(){this.bytes.fill(0);this.save()}
 importIds(ids){if(!Array.isArray(ids))throw Error("Ungültige Fortschrittsliste");this.bytes.fill(0);for(const id of ids){if(Number.isInteger(id)&&id>0&&id<=this.n){const i=id-1;this.bytes[i>>3]|=1<<(i&7)}}this.save()}
 export(){download('Blackthorn-Baufortschritt-v7.json',JSON.stringify({version:'7.0',totalBlocks:this.n,completed:this.total,completedIds:Array.from({length:this.n},(_,i)=>i+1).filter(id=>this.has(id))},null,2),'application/json')}
}
