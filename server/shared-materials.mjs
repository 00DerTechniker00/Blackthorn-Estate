import { createHash, timingSafeEqual } from 'node:crypto';

export const UPDATE_SCRIPT = `
local raw = redis.call('HGET', KEYS[1], ARGV[1])
local current = {amount=0, done=false, note='', version=0}
if raw then current = cjson.decode(raw) end
if current.mutation == ARGV[3] then return cjson.encode({ok=true, row=current}) end
if current.version ~= tonumber(ARGV[2]) then return cjson.encode({ok=false, row=current}) end
local patch = cjson.decode(ARGV[4])
if patch.amount ~= nil then current.amount = patch.amount end
if patch.done ~= nil then current.done = patch.done end
if patch.note ~= nil then current.note = patch.note end
current.version = current.version + 1
current.updatedBy = ARGV[5]
current.updatedAt = ARGV[6]
current.mutation = ARGV[3]
redis.call('HSET', KEYS[1], ARGV[1], cjson.encode(current))
return cjson.encode({ok=true, row=current})
`;

const hash = value => createHash('sha256').update(value).digest();
const scopes = new Set(['house', 'outdoor', 'terrain']);
const validRow = row => row && Number.isSafeInteger(row.amount) && row.amount >= 0 && row.amount <= 1_000_000_000 && typeof row.done === 'boolean' && typeof row.note === 'string' && row.note.length <= 240 && Number.isSafeInteger(row.version) && row.version >= 0;
const rowView = row => ({amount: row.amount, done: row.done, note: row.note, version: row.version, updatedBy: row.updatedBy || '', updatedAt: row.updatedAt || ''});

export function createHandler({plan, env = process.env, fetcher = fetch, now = () => new Date().toISOString()}) {
  return async function handler(req, res) {
    res.setHeader('Cache-Control', 'no-store, max-age=0');
    res.setHeader('Vary', 'Authorization');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    const send = (status, body) => res.status(status).json(body);
    const secret = env.SHARED_LIST_TEAM_CODE || '';
    const url = env.UPSTASH_REDIS_REST_URL || env.KV_REST_API_URL || '';
    const token = env.UPSTASH_REDIS_REST_TOKEN || env.KV_REST_API_TOKEN || '';
    const setupIssues = [];
    if (!secret) setupIssues.push('SHARED_LIST_TEAM_CODE fehlt');
    else if (secret.length < 16) setupIssues.push('der Wert von SHARED_LIST_TEAM_CODE hat weniger als 16 Zeichen');
    if (!/^https:\/\//.test(url)) setupIssues.push('die Redis-REST-URL fehlt oder beginnt nicht mit https:// (KV_REST_API_URL oder UPSTASH_REDIS_REST_URL)');
    if (!token) setupIssues.push('der Redis-Schreibtoken fehlt (KV_REST_API_TOKEN oder UPSTASH_REDIS_REST_TOKEN)');
    if (setupIssues.length) return send(503, {code:'SETUP_REQUIRED', error:'Server-Einrichtung unvollständig: '+setupIssues.join('; ')+'. In Vercel unter Settings → Environment Variables für die verwendete Umgebung korrigieren, speichern und anschließend neu deployen.'});
    const authorization = req.headers.authorization || '';
    const supplied = typeof authorization==='string' && authorization.startsWith('Bearer ') ? authorization.slice(7) : '';
    if (!supplied || supplied.length > 512 || !timingSafeEqual(hash(secret), hash(supplied))) return send(401, {code:'UNAUTHORIZED', environment:env.VERCEL_ENV || 'development', error:'Anmeldung abgelehnt: Der eingegebene Teamcode stimmt nicht mit dem Wert von SHARED_LIST_TEAM_CODE in diesem Deployment überein.'});
    if (!['GET', 'PATCH'].includes(req.method)) {
      res.setHeader('Allow', 'GET, PATCH');
      return send(405, {error:'Methode nicht erlaubt.'});
    }
    // No cookie authentication and no cross-origin access to the team endpoint.
    if (req.headers['sec-fetch-site'] === 'cross-site') return send(403, {error:'Bitte die Liste auf der Atlas-Website öffnen.'});
    const namespace = env.SHARED_LIST_NAMESPACE || 'blackthorn:materials:v1';
    if (!/^[a-zA-Z0-9:_-]{1,100}$/.test(namespace)) return send(503, {error:'Der Listenname in der Serverkonfiguration ist ungültig.'});
    const mode=env.VERCEL_ENV||'development';
    if(!['production','preview','development'].includes(mode))return send(503,{error:'Ungültige Serverumgebung.'});
    const suffix=mode==='production'?'':':'+mode;
    const key = namespace + suffix;
    async function redis(command) {
      const response = await fetcher(url.replace(/\/$/, ''), {
        method:'POST', headers:{Authorization:`Bearer ${token}`, 'Content-Type':'application/json'},
        body:JSON.stringify(command), signal:AbortSignal.timeout(8000)
      });
      if (!response.ok) throw Error('Redis transport');
      const payload = await response.json();
      if (payload.error || !Object.hasOwn(payload, 'result')) throw Error('Redis result');
      return payload.result;
    }
    try {
      if (req.method === 'GET') {
        const raw = await redis(['HGETALL', key]);
        if (!raw || typeof raw !== 'object' || Array.isArray(raw) && raw.length%2!==0) throw Error('Invalid store');
        const pairs = Array.isArray(raw) ? Array.from({length:raw.length/2}, (_,i)=>[raw[i*2],raw[i*2+1]]) : Object.entries(raw);
        const entries = {};
        for (const [id, value] of pairs) {
          const parts = String(id).split(':');
          if (parts.length!==2 || !scopes.has(parts[0]) || !Object.hasOwn(plan.material_scopes[parts[0]].counts, parts[1])) continue;
          const row = typeof value === 'string' ? JSON.parse(value) : value;
          if (!validRow(row)) throw Error('Invalid row');
          entries[id] = rowView(row);
        }
        return send(200, {entries, revision:plan.meta.version, fingerprint:plan.meta.fingerprint, serverTime:now(), preview:mode==='preview', development:mode==='development'});
      }
      if (!(req.headers['content-type'] || '').toLowerCase().startsWith('application/json')) return send(415, {error:'JSON erwartet.'});
      let body;
      try { body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body; } catch { return send(400, {error:'Ungültiges JSON.'}); }
      if (!body || typeof body!=='object' || Array.isArray(body) || JSON.stringify(body).length>4096) return send(400, {error:'Ungültige Änderung.'});
      const {scope, item, expectedVersion, mutation, author, changes, fingerprint} = body;
      if (fingerprint!==plan.meta.fingerprint) return send(409, {code:'PLAN_CHANGED',error:'Der Bauplan wurde aktualisiert. Bitte die Seite neu laden.'});
      if (!scopes.has(scope) || typeof item!=='string' || !Object.hasOwn(plan.material_scopes[scope].counts,item)) return send(400, {error:'Unbekanntes Material oder Bereich.'});
      if (!Number.isSafeInteger(expectedVersion) || expectedVersion<0 || expectedVersion>=Number.MAX_SAFE_INTEGER || typeof mutation!=='string' || !/^[a-zA-Z0-9-]{16,80}$/.test(mutation)) return send(400,{error:'Ungültige Versionsangabe.'});
      if (typeof author!=='string' || !author.trim() || author.length>60 || /[\u0000-\u001f]/.test(author)) return send(400,{error:'Bitte einen Namen mit höchstens 60 Zeichen angeben.'});
      if (!changes || typeof changes!=='object' || Array.isArray(changes)) return send(400,{error:'Keine Änderung angegeben.'});
      const fields = Object.keys(changes);
      if (!fields.length || fields.some(k=>!['amount','done','note'].includes(k))) return send(400,{error:'Unbekanntes Listenfeld.'});
      if (Object.hasOwn(changes,'amount') && (!Number.isSafeInteger(changes.amount) || changes.amount<0 || changes.amount>1_000_000_000)) return send(400,{error:'Bestand muss eine ganze Zahl zwischen 0 und 1 Milliarde sein.'});
      if (Object.hasOwn(changes,'done') && typeof changes.done!=='boolean') return send(400,{error:'Ungültiges Häkchen.'});
      if (Object.hasOwn(changes,'note') && (typeof changes.note!=='string' || changes.note.length>240)) return send(400,{error:'Notiz darf höchstens 240 Zeichen haben.'});
      const result = await redis(['EVAL',UPDATE_SCRIPT,'1',key,`${scope}:${item}`,String(expectedVersion),mutation,JSON.stringify(changes),author.trim(),now()]);
      const outcome = typeof result==='string' ? JSON.parse(result) : result;
      if (!outcome || typeof outcome.ok!=='boolean' || !validRow(outcome.row)) throw Error('Invalid update');
      if (!outcome.ok) return send(409,{code:'ROW_CONFLICT',error:'Dieses Material wurde inzwischen geändert. Bitte den neuen Stand prüfen.',row:rowView(outcome.row)});
      return send(200,{row:rowView(outcome.row)});
    } catch {
      return send(503,{code:'STORE_UNAVAILABLE',error:'Die gemeinsame Liste ist gerade nicht erreichbar. Bitte erneut versuchen.'});
    }
  };
}
