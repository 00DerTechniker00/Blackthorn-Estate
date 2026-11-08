"""Execute the actual Redis Lua update script in liblua, with in-memory Redis/JSON adapters."""
import ctypes,ctypes.util,re
from pathlib import Path
name=ctypes.util.find_library('lua5.4')
if not name:
    print('SKIP: liblua5.4 unavailable; Redis Lua runtime test requires a Lua library')
    raise SystemExit(77)
lib=ctypes.CDLL(name)
lib.luaL_newstate.restype=ctypes.c_void_p
lib.luaL_openlibs.argtypes=[ctypes.c_void_p]
lib.luaL_loadstring.argtypes=[ctypes.c_void_p,ctypes.c_char_p];lib.luaL_loadstring.restype=ctypes.c_int
lib.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_longlong,ctypes.c_void_p];lib.lua_pcallk.restype=ctypes.c_int
lib.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_size_t)];lib.lua_tolstring.restype=ctypes.c_char_p
lib.lua_close.argtypes=[ctypes.c_void_p]
script=re.search(r'export const UPDATE_SCRIPT = `([\s\S]*?)`;',Path('server/shared-materials.mjs').read_text())[1]
prelude='''
local function copy(x)
 if type(x)~='table' then return x end
 local t={} for k,v in pairs(x) do t[k]=copy(v) end return t
end
local jsonObjects={} local nextId=0
cjson={encode=function(v) nextId=nextId+1 local id='json'..nextId jsonObjects[id]=copy(v) return id end, decode=function(id) return copy(assert(jsonObjects[id])) end}
local hashes={}
redis={call=function(command,key,field,value)
 hashes[key]=hashes[key] or {}
 if command=='HGET' then return hashes[key][field] end
 assert(command=='HSET') hashes[key][field]=value return 1
end}
local function update()
'''
suffix='''
end
local function apply(field,version,id,patch)
 KEYS={'team'} ARGV={field,tostring(version),id,cjson.encode(patch),'Piet','time'}
 return cjson.decode(update())
end
local first=apply('house:stone',0,'one',{amount=7,done=true,note='A'})
assert(first.ok and first.row.version==1 and first.row.amount==7 and first.row.done)
local conflict=apply('house:stone',0,'two',{amount=99})
assert(not conflict.ok and conflict.row.amount==7 and conflict.row.version==1)
local duplicate=apply('house:stone',0,'one',{amount=7,done=true,note='A'})
assert(duplicate.ok and duplicate.row.version==1)
local clear=apply('house:stone',1,'three',{done=false,note=''})
assert(clear.ok and clear.row.done==false and clear.row.note=='' and clear.row.amount==7 and clear.row.version==2)
local other=apply('outdoor:stone',0,'four',{amount=2})
assert(other.ok and other.row.amount==2 and other.row.version==1)
print('PASS: actual Lua script syntax, CAS conflict, idempotency, false/empty updates and independent rows')
'''
state=lib.luaL_newstate()
try:
 lib.luaL_openlibs(state)
 code=lib.luaL_loadstring(state,(prelude+script+suffix).encode())
 if not code:code=lib.lua_pcallk(state,0,0,0,0,None)
 if code:raise RuntimeError(lib.lua_tolstring(state,-1,None).decode())
finally:lib.lua_close(state)
