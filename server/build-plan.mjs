import {createHash,timingSafeEqual} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
const hash=s=>createHash('sha256').update(s).digest();
export function createPlanHandler({plan,bytes,env=process.env}){
 let valid=false;
 try{const lines=gunzipSync(bytes,{maxOutputLength:32*1024*1024}).toString('utf8').trimEnd().split('\n');valid=lines[0].split('\t')[0]===plan.fingerprint&&lines.length-1===plan.positions;}catch{}
 return (req,res)=>{
  res.setHeader('Cache-Control','no-store');res.setHeader('Vary','Authorization');
  const send=(s,b)=>res.status(s).json(b);
  if(req.method!=='GET'){res.setHeader('Allow','GET');return send(405,{error:'GET erwartet.'});}
  const secret=env.LIVE_BUILD_WRITE_TOKEN;
  if(!secret||secret.length<32)return send(503,{error:'LIVE_BUILD_WRITE_TOKEN fehlt oder ist zu kurz.'});
  const auth=req.headers.authorization||'',token=typeof auth==='string'&&auth.startsWith('Bearer ')?auth.slice(7):'';
  if(!token||token.length>512||!timingSafeEqual(hash(token),hash(secret)))return send(401,{error:'Plugin-Schreibtoken stimmt nicht.'});
  if(!valid)return send(503,{error:'Bauplandatei und Metadaten stimmen nicht überein. Deployment prüfen.'});
  res.setHeader('ETag','"'+plan.fingerprint+'"');
  res.setHeader('X-Blackthorn-Plan-Schema','1');
  res.setHeader('X-Blackthorn-Fingerprint',plan.fingerprint);
  res.setHeader('X-Blackthorn-Positions',String(plan.positions));
  if(req.headers['if-none-match']==='"'+plan.fingerprint+'"')return res.status(304).end();
  res.setHeader('Content-Type','application/gzip');
  return res.status(200).send(bytes);
 };
}
