import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {createPlanHandler} from '../server/build-plan.mjs';
const plan=JSON.parse(readFileSync(resolve(process.cwd(),'live-plan.json'),'utf8'));
const bytes=readFileSync(resolve(process.cwd(),'live-server-plan.tsv.gz'));
export default createPlanHandler({plan,bytes});
