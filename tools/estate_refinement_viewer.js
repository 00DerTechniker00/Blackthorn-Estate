/* Focus the exact final coordinates of the reviewed estate additions. */
window.__showRefinementV6=(kind)=>{
  window.__showTab('3d');
  let attempts=0;
  const wait=()=>{
    if(!GL||!GL.terrain){if(++attempts<100)setTimeout(wait,80);return;}
    window.__resetScene();
    const configs={stable:[127,-747,126,772,35,true],garden:[169,-707,125,845,80,true],roof:[146,-709,145,790,26,false],river:[112,-643,110,785,48,false],facade:[169,-692,141,790,120,true]};
    const [cut,x,y,z,span,terrain]=configs[kind]||configs.facade;
    S3.terrain=terrain;$('#terrainChk').checked=terrain;
    $('#terrainState').value='target';$('#terrainState').dispatchEvent(new Event('change'));
    preset(kind==='river'?'east':'iso');S3.ymax=cut;$('#cut').value=cut;$('#sceneFloor').value='custom';applyCut();focusBox(x,y,z,span);
  };wait();
};
document.querySelectorAll('[data-v6-refinement]').forEach(button=>button.addEventListener('click',()=>window.__showRefinementV6(button.dataset.v6Refinement)));
