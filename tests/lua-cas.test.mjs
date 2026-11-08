import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
test('the actual Redis Lua script executes with compare-and-swap semantics',t=>{
  const result=spawnSync('python3',['tests/lua-cas.py'],{encoding:'utf8'});
  if(result.error?.code==='ENOENT'||result.status===77){t.skip('Python/liblua not installed; execute the live integration test instead');return;}
  assert.equal(result.status,0,result.stderr||result.stdout);assert.match(result.stdout,/PASS/);
});
