/* Dependency-free WebGL viewer. Shares the block geometry and UI of Revision 5.6. */
function ensureGL() {
  if (GL) { resize3d(); return; }
  const cv = $('#gl'), gl = cv.getContext('webgl', {antialias:true, alpha:false});
  const failed = message => {
    const el = $('#loading'); el.textContent = message + ' Grundriss und Schichtpläne bleiben verfügbar.';
    el.style.display = 'flex'; el.style.pointerEvents = 'none';
  };
  if (!gl || !gl.getExtension('OES_element_index_uint')) { failed('WebGL ist hier nicht verfügbar.'); return; }
  try {
    const shader = (type, source) => {
      const s = gl.createShader(type); gl.shaderSource(s, source); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw Error(gl.getShaderInfoLog(s));
      return s;
    };
    const program = gl.createProgram();
    gl.attachShader(program, shader(gl.VERTEX_SHADER, `
      attribute vec3 aPosition; attribute vec3 aColor; attribute vec2 aUV;
      uniform mat4 uMatrix; varying vec3 vColor; varying vec2 vUV;
      void main(){gl_Position=uMatrix*vec4(aPosition,1.);vColor=aColor;vUV=aUV;}`));
    gl.attachShader(program, shader(gl.FRAGMENT_SHADER, `
      precision mediump float; varying vec3 vColor; varying vec2 vUV; uniform float uAlpha;
      void main(){float e=min(min(vUV.x,1.-vUV.x),min(vUV.y,1.-vUV.y));
      gl_FragColor=vec4(vColor*mix(.76,1.,smoothstep(0.,.025,e)),uAlpha);}`));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw Error(gl.getProgramInfoLog(program));
    GL = {gl, program, meshes:{}, terrain:null, dirty:true,
      attrs:['aPosition','aColor','aUV'].map(n=>gl.getAttribLocation(program,n)),
      matrix:gl.getUniformLocation(program,'uMatrix'), alpha:gl.getUniformLocation(program,'uAlpha'),
      cam:{th:0, ph:1.05, d:190, t:vec(-690,140,-790)},
      hl:{visible:false,mesh:null,position:{set(x,y,z){
        if(GL.hl.mesh)GL.hl.mesh.buffers.forEach(b=>gl.deleteBuffer(b));
        const B={p:[],c:[],u:[],i:[0,1,1,3,3,2,2,0,4,5,5,7,7,6,6,4,0,4,1,5,2,6,3,7],n:8};
        for(let i=0;i<8;i++){B.p.push(x+(i&1?.51:-.51),y+(i&2?.51:-.51),z+(i&4?.51:-.51));B.c.push(1,.2,.08);B.u.push(.5,.5);}
        GL.hl.mesh=uploadGeometry(B);
      }}}};
    gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);
    bindControls(cv); buildGroupPanel(); resize3d();
    new ResizeObserver(resize3d).observe(cv.parentElement);
    $('#loading').style.display = 'flex';
    setTimeout(() => {
      try { rebuild(); GL.terrain = uploadGeometry(buildTerrain()); preset('east'); $('#loading').style.display='none'; loop(); }
      catch(e) { failed('Der 3D-Aufbau ist fehlgeschlagen.'); console.error(e); }
    }, 30);
    cv.addEventListener('webglcontextlost', e=>{e.preventDefault(); failed('Die Grafikverbindung wurde unterbrochen. Bitte Seite neu laden.');});
  } catch(e) { GL=null; failed('Der 3D-Viewer konnte nicht starten.'); console.error(e); }
}
function vec(x,y,z) { return {x,y,z,set(a,b,c){this.x=a;this.y=b;this.z=c;}}; }
function cameraBasis() {
  const c=GL.cam, sp=Math.sin(c.ph), cp=Math.cos(c.ph), st=Math.sin(c.th), ct=Math.cos(c.th);
  return {eye:[c.t.x+c.d*sp*ct,c.t.y+c.d*cp,c.t.z+c.d*sp*st],
    right:[st,0,-ct], up:[-cp*ct,sp,-cp*st], back:[sp*ct,cp,sp*st]};
}
function viewProjection() {
  const {eye,right:r,up:u,back:b}=cameraBasis(), dot=(a,c)=>a.reduce((s,v,i)=>s+v*c[i],0);
  const v=[r[0],u[0],b[0],0,r[1],u[1],b[1],0,r[2],u[2],b[2],0,-dot(r,eye),-dot(u,eye),-dot(b,eye),1];
  const cv=$('#gl'), f=1/Math.tan(Math.PI/8), near=.5, far=3000;
  const p=[f/(cv.width/cv.height),0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0];
  const out=new Float32Array(16);
  for(let c=0;c<4;c++) for(let r=0;r<4;r++) for(let k=0;k<4;k++) out[c*4+r]+=p[k*4+r]*v[c*4+k];
  return out;
}
function uploadGeometry(B) {
  if (!B.n) return null;
  const gl=GL.gl, buffers=[];
  for(const [values,Type,target] of [[B.p,Float32Array,gl.ARRAY_BUFFER],[B.c,Float32Array,gl.ARRAY_BUFFER],
    [B.u,Float32Array,gl.ARRAY_BUFFER],[B.i,Uint32Array,gl.ELEMENT_ARRAY_BUFFER]]) {
    const buffer=gl.createBuffer(); gl.bindBuffer(target,buffer); gl.bufferData(target,new Type(values),gl.STATIC_DRAW); buffers.push(buffer);
  }
  return {buffers,count:B.i.length};
}
function drawGeometry(mesh, alpha=1, mode=GL.gl.TRIANGLES) {
  if(!mesh) return;
  const gl=GL.gl;
  for(let i=0;i<3;i++) {gl.bindBuffer(gl.ARRAY_BUFFER,mesh.buffers[i]);gl.enableVertexAttribArray(GL.attrs[i]);gl.vertexAttribPointer(GL.attrs[i],i===2?2:3,gl.FLOAT,false,0,0);}
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,mesh.buffers[3]); gl.uniform1f(GL.alpha,alpha);
  gl.drawElements(mode,mesh.count,gl.UNSIGNED_INT,0);
}
function setBg() { if(GL) GL.dirty=true; }
function resize3d() {
  if(!GL || !$('#tab-3d').classList.contains('on')) return;
  const cv=$('#gl'), st=cv.parentElement, ratio=Math.min(2,devicePixelRatio||1);
  cv.width=Math.max(1,Math.round(st.clientWidth*ratio)); cv.height=Math.max(1,Math.round(st.clientHeight*ratio));
  GL.gl.viewport(0,0,cv.width,cv.height); GL.dirty=true;
}
function predNow() { return i=>!S3.hidden.has(REG[R[i]].gi); }
function rebuild() {
  const gl=GL.gl;
  for(const layer of Object.values(GL.meshes)) for(const mesh of Object.values(layer)) if(mesh) mesh.buffers.forEach(b=>gl.deleteBuffer(b));
  GL.meshes={};
  for(const [y,layer] of Object.entries(buildModel(predNow()))) {
    GL.meshes[y]={}; for(const k of ['main','glass','caps']) GL.meshes[y][k]=uploadGeometry(layer[k]);
  }
  applyCut();
}
function applyCut() {
  $('#cutLabel').textContent=`Y = ${S3.ymax}`+(S3.single?' (nur diese Ebene)':'');
  if(GL) GL.dirty=true;
}
function loop() {
  requestAnimationFrame(loop);
  if(!GL || !GL.dirty || !$('#tab-3d').classList.contains('on')) return;
  GL.dirty=false; const gl=GL.gl, dark=css('--mode')==='dark';
  gl.clearColor(...(dark?[.05,.075,.06,1]:[.81,.85,.85,1])); gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
  gl.useProgram(GL.program); gl.uniformMatrix4fv(GL.matrix,false,viewProjection());
  gl.disable(gl.BLEND);gl.depthMask(true);
  if(GL.terrain && S3.terrain && !S3.single) drawGeometry(GL.terrain);
  const visible=Object.entries(GL.meshes).filter(([y])=>S3.single?+y===S3.ymax:+y<=S3.ymax);
  for(const [y,layer] of visible) {drawGeometry(layer.main);if(+y===S3.ymax)drawGeometry(layer.caps);}
  gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);
  // Back-to-front layer order follows the camera's vertical position.
  for(const [,layer] of visible) drawGeometry(layer.glass,.48);
  if(GL.hl.visible&&GL.hl.mesh){gl.disable(gl.DEPTH_TEST);drawGeometry(GL.hl.mesh,1,gl.LINES);gl.enable(gl.DEPTH_TEST);}
  gl.depthMask(true);
}
const PRESETS={
  east:{th:.25,ph:1.12,d:135,t:[-680,143,790]},west:{th:Math.PI-.3,ph:1.15,d:140,t:[-700,138,790]},
  north:{th:Math.PI/2+.1,ph:1.1,d:150,t:[-690,140,790]},south:{th:-Math.PI/2-.2,ph:1.1,d:150,t:[-690,140,790]},
  top:{th:-Math.PI/2,ph:.02,d:200,t:[-690,130,790]},iso:{th:.75,ph:.95,d:165,t:[-690,135,790]}
};
function preset(n) { if(!GL) return;const p=PRESETS[n];Object.assign(GL.cam,{th:p.th,ph:p.ph,d:p.d});GL.cam.t.set(p.t[0],p.t[1],-p.t[2]);GL.dirty=true; }
function focusBox(x,y,z,span) {if(!GL)return;GL.cam.t.set(x,y,-z);GL.cam.d=Math.max(30,span*1.9);GL.cam.ph=1;GL.dirty=true;}
function bindControls(cv) {
  const points=new Map();let last=null,moved=0,pinch=0;
  cv.addEventListener('contextmenu',e=>e.preventDefault());
  cv.addEventListener('pointerdown',e=>{cv.setPointerCapture(e.pointerId);points.set(e.pointerId,e);last={x:e.clientX,y:e.clientY,b:e.button,sh:e.shiftKey};moved=0;});
  cv.addEventListener('pointermove',e=>{
    if(!points.has(e.pointerId)){hover(e);return;}points.set(e.pointerId,e);
    if(points.size===2){const [a,b]=[...points.values()],d=Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);if(pinch&&d)GL.cam.d=clamp(GL.cam.d*pinch/d,8,700);pinch=d;moved=10;GL.dirty=true;return;}
    const dx=e.clientX-last.x,dy=e.clientY-last.y;moved+=Math.abs(dx)+Math.abs(dy);last.x=e.clientX;last.y=e.clientY;
    if(last.b===2||last.b===1||last.sh)pan(dx,dy);else{GL.cam.th-=dx*.006;GL.cam.ph=clamp(GL.cam.ph-dy*.006,.02,1.55);}GL.dirty=true;
  });
  const up=e=>{points.delete(e.pointerId);pinch=0;if(moved<5&&e.type==='pointerup')pick(e);
    if(points.size===1){const p=[...points.values()][0];last={x:p.clientX,y:p.clientY,b:p.button,sh:p.shiftKey};moved=10;}};
  cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',up);
  cv.addEventListener('wheel',e=>{e.preventDefault();GL.cam.d=clamp(GL.cam.d*(e.deltaY>0?1.1:.9),8,700);GL.dirty=true;},{passive:false});
}
function pan(dx,dy) { const {right:r,up:u}=cameraBasis(),k=GL.cam.d*.0016,t=GL.cam.t;
  t.x+=(-dx*r[0]+dy*u[0])*k;t.y+=dy*u[1]*k;t.z+=(-dx*r[2]+dy*u[2])*k; }
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function rayBlock(e) {
  const rect=$('#gl').getBoundingClientRect(), mx=(e.clientX-rect.left)/rect.width*2-1,my=1-(e.clientY-rect.top)/rect.height*2;
  const {eye,right,up,back}=cameraBasis(),f=Math.tan(Math.PI/8),aspect=rect.width/rect.height;
  let d=back.map((v,i)=>-v+mx*f*aspect*right[i]+my*f*up[i]);const len=Math.hypot(...d);d=d.map(v=>v/len);
  const [ox,oy,oz]=[eye[0],eye[1],-eye[2]],[dx,dy,dz]=[d[0],d[1],-d[2]];
  let cx=Math.floor(ox),cy=Math.floor(oy),cz=Math.floor(oz);
  const sx=Math.sign(dx),sy=Math.sign(dy),sz=Math.sign(dz),tdx=dx?Math.abs(1/dx):1e9,tdy=dy?Math.abs(1/dy):1e9,tdz=dz?Math.abs(1/dz):1e9;
  let tx=dx?(sx>0?cx+1-ox:ox-cx)*tdx:1e9,ty=dy?(sy>0?cy+1-oy:oy-cy)*tdy:1e9,tz=dz?(sz>0?cz+1-oz:oz-cz)*tdz:1e9;
  const pred=predNow();
  for(let step=0;step<2500;step++) {const j=at(cx,cy,cz);if(j>=0&&pred(j)&&(S3.single?cy===S3.ymax:cy<=S3.ymax))return j;
    if(tx<ty&&tx<tz){cx+=sx;tx+=tdx;}else if(ty<tz){cy+=sy;ty+=tdy;}else{cz+=sz;tz+=tdz;}
    if(cy<BB[2]-3&&sy<0||cy>BB[3]+3&&sy>0)break;
  }return -1;
}
