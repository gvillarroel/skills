#!/usr/bin/env -S npx tsx
// Run with Node.js >=22 type stripping; standard library only. Reads published HTML, never inference.
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
const root = path.resolve('projects/code-assist-costs/artifacts/aa-ofat/source');
const all = {};
for (const stem of ['terminalbench', 'models']) {
  const file = path.join(root, stem+'.html');
  if (!fs.existsSync(file)) continue;
  const html = fs.readFileSync(file,'utf8');
  const datasets = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(m => JSON.parse(m[1])).filter(x=>x['@type']==='Dataset');
  all[stem] = {sha256:crypto.createHash('sha256').update(html).digest('hex'),retrieved:'2026-09-06',datasets};
  console.log(stem, datasets.map(x=>({name:x.name,n:x.data?.length,keys:Object.keys(x.data?.[0]||{})})));
}
fs.writeFileSync(path.join(root,'aa-datasets.json'),JSON.stringify(all,null,2));
const selected = /GPT-5.6 (Luna|Terra|Sol)|GPT-6 Astra/;
for (const [stem,v] of Object.entries(all)) for (const d of v.datasets) {
  console.log(stem,d.name,JSON.stringify(d.data?.filter(x=>selected.test(x.label))));
}
