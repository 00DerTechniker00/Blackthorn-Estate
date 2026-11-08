/* Target surfaces share their actual materials with the construction lists. */
function buildTerrain() {
  const T=D.terrain,[x0,x1,z0,z1]=T.bounds,mode=S3.terrainMode||'target';
  const H=mode==='original'?T.heights:T.target_heights,work=new Map(T.work.map(r=>[r[0]+','+r[1],r]));
  const B=mkB(),bottom=Math.min(...T.heights.map(row=>Math.min(...row)))-8;
  const modeledSteps=new Set((D.structure?.v6?.outdoors?.steps||[]).map(([x,z])=>x+','+z));
  const height=(x,z)=>(x<x0||x>x1||z<z0||z>z1)?bottom:H[z-z0][x-x0]+1-(mode!=='original'&&modeledSteps.has(x+','+z)?1:0);
  // A height field cannot describe an underground cellar. Its old surface must not cover V6 blocks.
  const hasCellar=!!D.structure?.v6&&mode!=='original';
  const cutout=(x,z)=>hasCellar&&((x>=-710&&x<=-658&&z>=766&&z<=814)||(x>=-715&&x<=-711&&z>=774&&z<=783));
  const rgb={water:[.24,.47,.66],grass_block:[.39,.56,.31],dirt:[.52,.39,.25],stone:[.49,.51,.52],stone_bricks:[.53,.55,.55],gravel:[.67,.62,.51],iron_block:[.75,.78,.77],dark_oak_planks:[.32,.23,.14]};
  for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++){
    if(cutout(x,z))continue;
    const h=height(x,z),r=work.get(x+','+z),variation=.95+.1*hash3(x,7,z);
    const mat=mode==='original'?T.surface_blocks[z-z0][x-x0]:T.target_surface_blocks[z-z0][x-x0];
    let top=(rgb[mat]||[.46,.49,.43]).map(v=>v*variation);
    if(mode==='work'&&r)top=r[4]&&r[5]?[.65,.48,.73]:r[4]?[.90,.51,.23]:r[5]?[.21,.67,.64]:[.73,.68,.41];
    addFace(B,'up',[x,0,z,x+1,h,z+1],top,1);
    for(const dir of ['north','south','east','west']){
      const v=DIRV[dir];
      if(cutout(x+v[0],z+v[2])){
        // Close the exposed soil edge, never the top of the cellar cavity.
        // Move the face slightly into the soil so the actual masonry wins the depth test.
        const base=(x+v[0]<-710)?80:95,box=[x,base,z,x+1,h,z+1],epsilon=.002;
        if(dir==='east')box[3]-=epsilon;
        if(dir==='west')box[0]+=epsilon;
        if(dir==='south')box[5]-=epsilon;
        if(dir==='north')box[2]+=epsilon;
        if(h>base){
          const soil=mat==='grass_block'||mat==='dirt';
          const faceColor=(soil?rgb.dirt:rgb.stone).map(c=>c*variation);
          addFace(B,dir,box,mode==='work'&&r?top:faceColor,1);
        }
        continue;
      }
      const neighbour=height(x+v[0],z+v[2]);
      if(neighbour<h){
        const side=mode==='work'&&r?top:[.45*variation,.35*variation,.24*variation];
        addFace(B,dir,[x,neighbour,z,x+1,h,z+1],side,1);
        if(mat==='grass_block'&&mode!=='work')addFace(B,dir,[x,Math.max(neighbour,h-.18),z,x+1,h,z+1],top,.9);
      }
    }
  }
  return B;
}
