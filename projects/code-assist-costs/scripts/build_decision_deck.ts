#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/code-assist-costs/scripts/build_decision_deck.ts
// Only Node built-ins. Browser runtime: vendored D3 7.9.0, copied from the read-only blog dependency.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(project,'source/decision-deck');
const root=path.join(project,'artifacts/decision-curves-v1');
const data=JSON.parse(fs.readFileSync(path.join(root,'presentation-data.json'),'utf8'));
data.inventory=data.inventory.map(v=>({label:v.label,treatment:v.treatment,unit:v.unit,mechanism:v.mechanism,id:v.variable_id}));
for(const key of Object.keys(data.curves)) data.curves[key]=data.curves[key].map(r=>({x:r.x,attempt_usd:r.attempt_usd,correct_usd:r.correct_usd,completion:r.completion,compactions:r.compactions}));
const vendor=path.join(root,'deck/vendor/d3.min.js');
if(!fs.existsSync(vendor)) throw Error('Copy the verified installed D3 runtime into deck/vendor/d3.min.js first.');
let html=fs.readFileSync(path.join(source,'index.html'),'utf8');
const replacements={__STYLE__:fs.readFileSync(path.join(source,'styles.css'),'utf8'),__D3__:fs.readFileSync(vendor,'utf8'),__DATA__:JSON.stringify(data).replaceAll('<','\\u003c'),__APP__:fs.readFileSync(path.join(source,'app.js'),'utf8')};
for(const [key,val] of Object.entries(replacements)) html=html.replace(key,()=>val);
fs.writeFileSync(path.join(root,'deck/index.html'),html);
console.log(JSON.stringify({output:path.join(root,'deck/index.html'),bytes:Buffer.byteLength(html),scenes:15,offline:true}));
