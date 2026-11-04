export const $=s=>document.querySelector(s);
export const $$=s=>[...document.querySelectorAll(s)];
export const fmt=n=>Number(n).toLocaleString('de-DE');
export const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const key=(x,y,z)=>`${x}|${y}|${z}`;
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export const units=n=>{const sh=Math.floor(n/1728),r=n%1728;return {sh,st:Math.floor(r/64),rem:r%64}};
export const formatUnits=n=>{const u=units(n),parts=[];if(u.sh)parts.push(`${u.sh} Shulker`);if(u.st)parts.push(`${u.st} Stacks`);if(u.rem)parts.push(`${u.rem} einzeln`);return parts.join(' + ')||'0'};
export const states=b=>Object.entries(b.state||{}).map(([k,v])=>`${k}=${v}`).join(', ');
export const blockName=(model,id)=>model.palette[id]?.name||id;
export function makeCSV(rows){return '\ufeff'+rows.map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(';')).join('\r\n')}
export function download(name,data,type='text/csv;charset=utf-8'){
  const url=URL.createObjectURL(new Blob([data],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),2500);
}
export function color(hex,mult=1){const n=parseInt(hex.slice(1),16);if(!Number.isFinite(n))return '#aaa';return `rgb(${Math.min(255,((n>>16)&255)*mult)|0},${Math.min(255,((n>>8)&255)*mult)|0},${Math.min(255,(n&255)*mult)|0})`}
export function insidePolygon(poly,x,y){let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit}return hit}
export function canvasPoint(e,canvas){const r=canvas.getBoundingClientRect();return {x:(e.clientX-r.left)*canvas.width/r.width,y:(e.clientY-r.top)*canvas.height/r.height}}
export function resizeCanvas(canvas,maxWidth=1500){const cssWidth=Math.max(320,canvas.clientWidth||900),ratio=Math.min(window.devicePixelRatio||1,1.5);const width=Math.min(maxWidth,Math.round(cssWidth*ratio)),height=Math.round(width*(canvas.id==='planCanvas'?900/1300:850/1400));if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;return true}return false}
