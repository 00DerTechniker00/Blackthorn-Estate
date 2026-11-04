/* Original, target and cut/fill maps all use the exact same surveyed grid. */
(() => {
  'use strict';
  const $=s=>document.querySelector(s),D=JSON.parse($('#data').textContent),T=D.terrain;
  const [x0,x1,z0,z1]=T.bounds,w=x1-x0+1,h=z1-z0+1;
  const canvas=$('#geologyCanvas'),ctx=canvas.getContext('2d'),bitmap=document.createElement('canvas');bitmap.width=w;bitmap.height=h;
  const imageCtx=bitmap.getContext('2d'),work=new Map(T.work.map(r=>[r[0]+','+r[1],r]));
  const palette={water:[61,121,170],grass_block:[94,141,82],stone:[128,135,137],dirt:[141,106,74],gravel:[143,138,125],stone_bricks:[151,157,155],iron_block:[206,214,210]};
  let scale=3,ox=0,oz=0,ready=false,drag=null;
  function redraw(){
    const mode=$('#geologyMode').value,image=imageCtx.createImageData(w,h);
    const min=Math.min(...T.heights.map(r=>Math.min(...r))),max=Math.max(...T.heights.map(r=>Math.max(...r)));
    for(let z=0;z<h;z++)for(let x=0;x<w;x++){
      const row=work.get((x+x0)+','+(z+z0)),old=T.heights[z][x],target=T.target_heights[z][x];
      let color=palette[T.surface_blocks[z][x]]||[112,126,109];
      if(mode==='target')color=palette[row?row[7]:T.surface_blocks[z][x]]||color;
      if(mode==='height'){const v=(old-min)/Math.max(1,max-min);color=[65+v*145,82+v*110,135-v*70];}
      if(mode==='earthworks')color=row?(row[4]&&row[5]?[163,122,181]:row[4]?[225,122,51]:row[5]?[56,175,163]:[176,161,99]):[47,66,53];
      if(mode==='delta'){const diff=target-old;color=diff>0?[41,Math.min(235,100+diff*8),163]:diff<0?[Math.min(240,115-diff*6),95,49]:[56,72,60];}
      const i=(z*w+x)*4;image.data[i]=color[0];image.data[i+1]=color[1];image.data[i+2]=color[2];image.data[i+3]=255;
    }imageCtx.putImageData(image,0,0);draw();
  }
  function fit(){const rect=canvas.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);canvas.width=Math.max(300,Math.round(rect.width*dpr));canvas.height=Math.max(280,Math.round(rect.height*dpr));scale=Math.min((canvas.width-60)/w,(canvas.height-60)/h);ox=(canvas.width-w*scale)/2;oz=(canvas.height-h*scale)/2;draw();}
  function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.imageSmoothingEnabled=false;ctx.drawImage(bitmap,ox,oz,w*scale,h*scale);
    const rect=(a,b,c,d,color)=>{ctx.strokeStyle=color;ctx.lineWidth=2;ctx.strokeRect(ox+(a-x0)*scale,oz+(b-z0)*scale,(c-a+1)*scale,(d-b+1)*scale);};
    rect(-739,747,-654,833,'#e8d6ae');rect(-710,766,-658,814,'#c9ba8e');
    ctx.strokeStyle='#f0d398';ctx.lineWidth=2;ctx.beginPath();T.waypoints.forEach(([x,z],i)=>ctx[i?'lineTo':'moveTo'](ox+(x-x0+.5)*scale,oz+(z-z0+.5)*scale));ctx.stroke();
    ctx.fillStyle='#e9eadb';ctx.font='13px system-ui';ctx.fillText('Norden ↑ · Westen ← X → Osten · Z nach Süden',12,20);
  }
  function coordinates(e){const r=canvas.getBoundingClientRect(),px=(e.clientX-r.left)*canvas.width/r.width,pz=(e.clientY-r.top)*canvas.height/r.height;return {px,pz,x:Math.floor((px-ox)/scale)+x0,z:Math.floor((pz-oz)/scale)+z0};}
  function hover(e){const {x,z}=coordinates(e);if(x<x0||x>x1||z<z0||z>z1)return;
    const row=work.get(x+','+z),old=T.heights[z-z0][x-x0],target=T.target_heights[z-z0][x-x0];
    $('#geologyHover').textContent=`X ${x} / Z ${z} · Ist-Boden Y ${old} (${T.surface_blocks[z-z0][x-x0]}) · Soll-Boden Y ${target}`+
      (row?` · ${row[6]} · ${row[4]} Blöcke abtragen · ${row[5]} Blöcke auffüllen`:' · Gelände unverändert');
  }
  $('#geologyMode').onchange=redraw;$('#geologyReset').onclick=fit;
  canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);drag=[e.clientX,e.clientY,ox,oz];});
  canvas.addEventListener('pointermove',e=>{if(drag){ox=drag[2]+(e.clientX-drag[0])*canvas.width/canvas.clientWidth;oz=drag[3]+(e.clientY-drag[1])*canvas.height/canvas.clientHeight;draw();}else hover(e);});
  canvas.addEventListener('pointerup',e=>{drag=null;hover(e);});canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('wheel',e=>{e.preventDefault();const {px,pz}=coordinates(e),next=Math.min(35,Math.max(.5,scale*(e.deltaY<0?1.12:.89)));const x=(px-ox)/scale,z=(pz-oz)/scale;scale=next;ox=px-x*scale;oz=pz-z*scale;draw();},{passive:false});
  function visible(){if(!$('#tab-terrain').classList.contains('on'))return;if(!ready){ready=true;fit();redraw();}else fit();}
  window.addEventListener('bt:tab',visible);
  window.addEventListener('resize',()=>{if(ready)visible();});
  if(location.hash==='#terrain')setTimeout(visible,0);
})();
