import {createHash,timingSafeEqual} from 'node:crypto';
import {gzipSync,gunzipSync} from 'node:zlib';
const hash=v=>createHash('sha256').update(v).digest();
const same=(a,b)=>typeof a==='string'&&a.length<=512&&timingSafeEqual(hash(a),hash(b));
const saveScript=`local old=redis.call('GET',KEYS[1]); if old then local v=cjson.decode(old); if v.sampledAt>=tonumber(ARGV[1]) then return 0 end end; redis.call('SET',KEYS[1],ARGV[2]); return 1`;
export function createBuildHandler({plan,env=process.env,fetcher=fetch,now=Date.now}){
 return async(req,res)=>{
  res.setHeader('Cache-Control','no-store');res.setHeader('Vary','Authorization');
  const send=(s,b)=>res.status(s).json(b);
  if(!['GET','POST'].includes(req.method)){res.setHeader('Allow','GET, POST');return send(405,{error:'Methode nicht erlaubt.'});}
  if(req.headers['sec-fetch-site']==='cross-site')return send(403,{error:'Bitte den Atlas direkt öffnen.'});
  const write=req.method==='POST',secret=write?env.LIVE_BUILD_WRITE_TOKEN:env.SHARED_LIST_TEAM_CODE;
  if(!secret||secret.length<(write?32:16))return send(503,{error:write?'LIVE_BUILD_WRITE_TOKEN fehlt oder ist zu kurz.':'SHARED_LIST_TEAM_CODE fehlt oder ist zu kurz.'});
  const auth=req.headers.authorization||'';
  if(typeof auth!=='string'||!auth.startsWith('Bearer ')||!same(auth.slice(7),secret))return send(401,{error:write?'Plugin-Schreibtoken stimmt nicht.':'Teamcode stimmt nicht mit diesem Deployment überein.'});
  const url=env.UPSTASH_REDIS_REST_URL||env.KV_REST_API_URL,token=env.UPSTASH_REDIS_REST_TOKEN||env.KV_REST_API_TOKEN;
  if(!url?.startsWith('https://')||!token)return send(503,{error:'Redis-Verbindung in Vercel fehlt.'});
  const namespace=env.SHARED_LIST_NAMESPACE||'blackthorn:materials:v1',mode=env.VERCEL_ENV||'development';
  if(!/^[a-zA-Z0-9:_-]{1,100}$/.test(namespace)||!['production','preview','development'].includes(mode))return send(503,{error:'Ungültige Serverkonfiguration.'});
  const key=namespace+':live:'+mode+':'+plan.fingerprint;
  async function redis(command){
   const response=await fetcher(url.replace(/\/$/,''),{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(command),signal:AbortSignal.timeout(8000)});
   if(!response.ok)throw Error('store');const value=await response.json();if(value.error||!Object.hasOwn(value,'result'))throw Error('store');return value.result;
  }
  try{
   if(!write){const raw=await redis(['GET',key]);const snapshot=raw?JSON.parse(raw):null;if(snapshot){snapshot.states=gunzipSync(Buffer.from(snapshot.statesGzip,'base64'),{maxOutputLength:plan.positions+1}).toString('ascii');delete snapshot.statesGzip;}return send(200,{plan,environment:mode,snapshot});}
   if(!(req.headers['content-type']||'').startsWith('application/json'))return send(415,{error:'JSON erwartet.'});
   let body;try{body=typeof req.body==='string'?JSON.parse(req.body):req.body;}catch{return send(400,{error:'Ungültiges JSON.'});}
   if(!body||body.fingerprint!==plan.fingerprint)return send(409,{error:'Plugin und Website verwenden unterschiedliche Baupläne. Plugin mit aktuellem Plan neu bauen.'});
   if(body.statesGzip!==undefined){
    if(body.states!==undefined||typeof body.statesGzip!=='string'||body.statesGzip.length>2*plan.positions+4096||!/^[a-zA-Z0-9+/]+={0,2}$/.test(body.statesGzip))return send(400,{error:'Ungültiger komprimierter Prüfstand.'});
    try{body.states=gunzipSync(Buffer.from(body.statesGzip,'base64'),{maxOutputLength:plan.positions+1}).toString('utf8');}catch{return send(400,{error:'Ungültiger komprimierter Prüfstand.'});}
   }
   if(typeof body.states!=='string'||body.states.length!==plan.positions||/[^0-4]/.test(body.states)||!Number.isSafeInteger(body.sampledAt)||body.sampledAt<now()-300000||body.sampledAt>now()+60000)return send(400,{error:'Ungültiger Prüfstand oder abweichende Serveruhr.'});
   const snapshot={fingerprint:plan.fingerprint,statesGzip:gzipSync(body.states).toString('base64'),sampledAt:body.sampledAt,receivedAt:now()};
   const saved=await redis(['EVAL',saveScript,'1',key,String(body.sampledAt),JSON.stringify(snapshot)]);
   return send(saved===1?200:409,{saved:saved===1});
  }catch{return send(503,{error:'Fortschritt konnte nicht übertragen werden. Die Verbindung wird erneut versucht.'});}
 };
}
