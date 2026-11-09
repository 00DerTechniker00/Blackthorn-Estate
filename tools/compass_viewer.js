/* Directions are Minecraft world vectors converted into the viewer's reflected Z coordinates. */
function updateSceneCompass(){
  const root=document.getElementById('sceneCompass');if(!root||!GL)return;
  const {right,up}=cameraBasis();
  root.style.visibility='visible';
  const headingScale=Math.hypot(up[0],up[2])||1;
  const vectors={north:[0,0,1],east:[1,0,0],south:[0,0,-1],west:[-1,0,0]};
  for(const [name,v] of Object.entries(vectors)){
    const el=root.querySelector('[data-direction="'+name+'"]');
    const x=v.reduce((sum,n,i)=>sum+n*right[i],0),y=v.reduce((sum,n,i)=>sum+n*up[i],0)/headingScale;
    el.style.left=(50+x*31)+'px';el.style.top=(44-y*31)+'px';
  }
}
