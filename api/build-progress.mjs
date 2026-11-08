import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {createBuildHandler} from '../server/build-progress.mjs';
const plan=JSON.parse(readFileSync(resolve(process.cwd(),'live-plan.json'),'utf8'));
export default createBuildHandler({plan});
