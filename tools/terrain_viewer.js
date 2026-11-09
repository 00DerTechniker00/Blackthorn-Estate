/* Keep solid ground below shallow building masks; only real deep cavities omit their tops. */
function buildTerrain() {
  const T=D.terrain,[x0,x1,z0,z1]=T.bounds,mode=S3.terrainMode||'target';
  const H=mode==='original'?T.heights:T.target_heights,work=new Map(T.work.map(r=>[r[0]+','+r[1],r]));
  const B=mkB(),bottom=Math.min(...T.heights.map(row=>Math.min(...row)))-8;
  const steps=new Set((D.structure?.v6?.outdoors?.steps||[]).map(([x,z])=>x+','+z));
  const height=(x,z)=>(x<x0||x>x1||z<z0||z>z1)?bottom:H[z-z0][x-x0]+1-(mode!=='original'&&steps.has(x+','+z)?1:0);
  const active=!!D.structure?.v6&&mode!=='original';
  const structure=new Map((T.structure_clearance||[]).map(([x,z,y])=>[x+','+z,y]));
  const cavity=(x,z)=>active?(x>=-710&&x<=-658&&z>=766&&z<=814?95:x>=-715&&x<=-711&&z>=774&&z<=783?80:null):null;
  const masked=(x,z)=>cavity(x,z)!==null||(active&&!S3.terrainOnly&&structure.has(x+','+z));
  const level=(x,z)=>cavity(x,z)??(masked(x,z)?Math.min(height(x,z),structure.get(x+','+z)+1):height(x,z));
  const portals=active?(T.soil_portals||[]):[];
  const rgb={water:[.24,.47,.66],grass_block:[.39,.56,.31],dirt:[.52,.39,.25],stone:[.49,.51,.52],stone_bricks:[.53,.55,.55],gravel:[.67,.62,.51],iron_block:[.75,.78,.77],dark_oak_planks:[.32,.23,.14]};
  function side(dir,x,z,nx,nz,low,high,color,inset){
    let spans=[[low,high]];
    for(const [ax,bx,ay,by,az,bz] of portals){
      const inside=(xx,zz)=>ax<=xx&&xx<=bx&&az<=zz&&zz<=bz;
      if(!inside(x,z)&&!inside(nx,nz))continue;
      const next=[];
      for(const [a,b] of spans){
        if(by+1<=a||ay>=b){next.push([a,b]);continue;}
        if(a<ay)next.push([a,Math.min(b,ay)]);
        if(b>by+1)next.push([Math.max(a,by+1),b]);
      }spans=next;
    }
    for(const [a,b] of spans){
      if(b<=a)continue;
      const box=[x,a,z,x+1,b,z+1],epsilon=inset?.002:0;
      if(dir==='east')box[3]-=epsilon;if(dir==='west')box[0]+=epsilon;
      if(dir==='south')box[5]-=epsilon;if(dir==='north')box[2]+=epsilon;
      addFace(B,dir,box,color,1);
    }
  }
  for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++){
    const hidden=masked(x,z),h=level(x,z),r=work.get(x+','+z),variation=.95+.1*hash3(x,7,z);
    const mat=mode==='original'?T.surface_blocks[z-z0][x-x0]:T.target_surface_blocks[z-z0][x-x0];
    let top=(rgb[mat]||[.46,.49,.43]).map(v=>v*variation);
    if(mode==='work'&&r)top=r[4]&&r[5]?[.65,.48,.73]:r[4]?[.90,.51,.23]:r[5]?[.21,.67,.64]:[.73,.68,.41];
    // The corrected ground lies below the building floor. Removing its top
    // would expose a black footprint as soon as upper building layers are cut away.
    if(cavity(x,z)===null)addFace(B,'up',[x,0,z,x+1,h,z+1],top,1);
    for(const dir of ['north','south','east','west']){
      const v=DIRV[dir],nx=x+v[0],nz=z+v[2],other=level(nx,nz);
      if(other>=h)continue;
      const cut=hidden||masked(nx,nz),soil=mat==='grass_block'||mat==='dirt';
      const color=mode==='work'&&r?top:cut?(soil?rgb.dirt:rgb.stone).map(c=>c*variation):[.45*variation,.35*variation,.24*variation];
      side(dir,x,z,nx,nz,other,h,color,cut);
      if(!cut&&mat==='grass_block'&&mode!=='work')addFace(B,dir,[x,Math.max(other,h-.18),z,x+1,h,z+1],top,.9);
    }
  }return B;
}
