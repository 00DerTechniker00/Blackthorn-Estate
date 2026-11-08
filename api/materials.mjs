import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createHandler } from '../server/shared-materials.mjs';
const plan = JSON.parse(readFileSync(resolve(process.cwd(),'shared-plan.json'), 'utf8'));
export default createHandler({plan});
