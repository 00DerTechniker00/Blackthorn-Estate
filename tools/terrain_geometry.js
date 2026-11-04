/* Full surveyed surroundings; the view mode changes only the earth surface. */
function buildTerrain() {
  const T=D.terrain,[x0,x1,z0,z1]=T.bounds,mode=S3.terrainMode||'target';
  const H=mode==='original'?T.heights:T.target_heights;
  const work=new Map(T.work.map(r=>[r[0]+','+r[1],r]));
  const B=mkB(),bottom=Math.min(...T.heights.map(row=>Math.min(...row)))-8;
  const height=(x,z)=>(x<x0||x>x1||z<z0||z>z1)?bottom:H[z-z0][x-x0]+1;
  const rgb={water:[.24,.47,.66],grass_block:[.35,.52,.29],dirt:[.48,.36,.24],stone:[.49,.51,.52],stone_bricks:[.53,.55,.55],gravel:[.56,.54,.49],iron_block:[.75,.78,.77]};
  for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++){
    const h=height(x,z),r=work.get(x+','+z),variation=.95+.1*hash3(x,7,z);
    let top=(rgb[mode==='original'?T.surface_blocks[z-z0][x-x0]:r?r[7]:T.surface_blocks[z-z0][x-x0]]||[.46,.49,.43]).map(v=>v*variation);
    if(mode==='work'&&r){top=r[4]&&r[5]?[.64,.48,.71]:r[4]?[.88,.47,.20]:r[5]?[.22,.68,.64]:[.69,.63,.39];}
    addFace(B,'up',[x,0,z,x+1,h,z+1],top,1);
    for(const direction of ['north','south','east','west']){
      const v=DIRV[direction],neighbour=height(x+v[0],z+v[2]);
      if(neighbour<h){const side=mode==='work'&&r?top:mode!=='original'&&r&&r[6]==='Hausunterbau'?[.34,.36,.39]:[.43*variation,.40*variation,.34*variation];
        addFace(B,direction,[x,neighbour,z,x+1,h,z+1],side,1);}
    }
  }
  return B;
}
