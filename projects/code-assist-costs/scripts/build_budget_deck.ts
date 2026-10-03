#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/code-assist-costs/scripts/build_budget_deck.ts
// Node built-ins only. Reuses the frozen data and local D3 7.9.0 runtime.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(project,'source/budget-deck');
const predecessor=path.join(project,'artifacts/decision-curves-v1');
const out=path.join(project,'artifacts/decision-budget-v2');
const read=(p:string)=>fs.readFileSync(p,'utf8');
const hash=(s:string|Buffer)=>crypto.createHash('sha256').update(s).digest('hex');
const dataRaw=read(path.join(predecessor,'presentation-data.json'));
const data=JSON.parse(dataRaw);
const math=read(path.join(source,'budget-math.js'));
const sandbox:any={};vm.runInNewContext(math,sandbox);
const m=sandbox.BudgetMath;
let checks=0;
const close=(a:number,b:number)=>{assert.ok(Math.abs(a-b)<=1e-9*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);checks++;};
const base=data.baselines.short.attempt_usd, budget=200;
const rows:any[]=[];
for(const [key,values] of Object.entries(data.curves) as [string,any[]][]){
 for(const r of values){
  const b=data.baselines[key.split(':')[1]].attempt_usd, p=m.planning(r.attempt_usd,b,budget);
  const successful=m.capacity(r.attempt_usd,budget,r.completion);
  close(p.runs*r.attempt_usd,budget);close(successful,budget/r.correct_usd);
  close(p.sameUseBalance+p.sameUseSpend,budget);
  assert.ok(p.whole*r.attempt_usd<=budget+1e-10);assert.ok((p.whole+1)*r.attempt_usd>budget-1e-10);checks+=2;
  rows.push({source_type:'simulated-mean-rate-transform',curve:key,parameter:r.x,budget_usd:budget,cost_usd:r.attempt_usd,success_probability:r.completion,runs_equivalent:p.runs,whole_run_plan:p.whole,expected_success_equivalent:successful,delta_whole_runs:p.delta,same_use_spend_usd:p.sameUseSpend,same_use_balance_usd:p.sameUseBalance});
 }
}
const find=(k:string,x:number)=>data.curves[k].find((r:any)=>Math.abs(r.x-x)<1e-8);
close(find('system:short',1000).attempt_usd-base,.00035);
const headline=[['baseline',base],['system-1000',find('system:short',1000).attempt_usd],['tools-4',find('tools:short',4).attempt_usd],['output-80pct',find('output:short',.8).attempt_usd],['cache-90pct',find('cache-free:short',.9).attempt_usd]].map(([id,cost])=>({id,...m.planning(cost,base)}));
assert.deepEqual(headline.map(x=>x.whole),[5449,5397,5597,6571,5215]);checks++;
close(m.capacity(2,0),0);close(m.capacity(2,200,0),0);close(m.capacity(2,200,1),100);
for(const args of [[0,200],[-1,200],[1,-1],[1,200,1.1],[1,200,-.1]]){assert.throws(()=>m.capacity(...args));checks++;}
close(m.reserve(40,base).usable,160);close(m.reserve(40,base).costHeadroom,.25);assert.equal(Math.floor(m.reserve(40,base).runs),4359);checks++;
assert.throws(()=>m.reserve(200,base));checks++;
for(const k of [1,2,3]) for(const r of data.retry[String(k)]){
 const got=m.retry(data.baselines.short.completion,base,k,r.x);close(got.success,r.y);close(got.spend,r.spend);close(got.successful,200/r.correct_usd);
}
const p=data.baselines.short.completion;
close(m.retry(p,base,3,0).successful,200*p/base);close(m.retry(p,base,3,1).success,p);close(m.retry(0,base,3,0).successful,0);close(m.retry(1,base,3,1).attempts,1);
for(const r of data.routing){const got=m.routing(data.profiles[0].pass1,data.profiles[0].cost_usd,data.profiles[3].cost_usd,r.x);close(got.success,r.y);close(got.spend,r.spend);}
const uncompressed=200/data.curves['quality-free:long'][0].correct_usd;
assert.ok(200/find('fidelity-critical:long',.95).correct_usd<uncompressed);assert.ok(200/find('fidelity-critical:long',.99).correct_usd>uncompressed);checks+=2;
const cap180=find('cap:long',180000).attempt_usd;
const calendar={tasks:150,with_summaries_balance:200-150*cap180,no_summaries_balance:200-150*data.baselines.long.attempt_usd,no_cap_exhaustion_day:200/(5*data.baselines.long.attempt_usd)};
assert.ok(calendar.with_summaries_balance>80&&calendar.with_summaries_balance<82);assert.ok(calendar.no_summaries_balance<0&&calendar.no_summaries_balance>-1);checks+=2;
data.budgetView={budgetUSD:200,method:read(path.join(project,'source/budget-view-method.md')),headlines:headline,calendar,interpretation:'Mean-rate planning equivalents, not subscription quotas or finite-budget stopping-time expectations.'};
data.inventory=data.inventory.map((v:any)=>({label:v.label,treatment:v.treatment,unit:v.unit,mechanism:v.mechanism,id:v.variable_id}));
for(const key of Object.keys(data.curves))data.curves[key]=data.curves[key].map((r:any)=>({x:r.x,attempt_usd:r.attempt_usd,correct_usd:r.correct_usd,completion:r.completion,compactions:r.compactions}));
const old=read(path.join(project,'source/decision-deck/app.js'));
let shared=old.slice(old.indexOf('function nearest('),old.indexOf('function setResult('));
assert.ok(shared.startsWith('function nearest(')&&shared.includes('function plot('));
shared=shared.replace('height=opts.height||(width<500?310:440)','height=opts.height||(width<500?310:Math.max(240,Math.min(360,innerHeight-465)))');
const app=read(path.join(source,'app.js')).replace('__PLOT__',()=>shared);
new vm.Script(app);new vm.Script(math);checks+=2;
let html=read(path.join(source,'index.html'));
for(const [key,val] of Object.entries({__STYLE__:read(path.join(source,'styles.css')),__D3__:read(path.join(predecessor,'deck/vendor/d3.min.js')),__DATA__:JSON.stringify(data).replaceAll('<','\\u003c'),__MATH__:math,__APP__:app}))html=html.replace(key,()=>val);
assert.ok(!html.includes('__PLOT__')&&!html.includes('__DATA__'));checks++;
for(const folder of ['deck','data','qa'])fs.mkdirSync(path.join(out,folder),{recursive:true});
fs.writeFileSync(path.join(out,'deck/index.html'),html);
fs.writeFileSync(path.join(out,'data/budget-view.json'),JSON.stringify(data));
const columns=Object.keys(rows[0]);
fs.writeFileSync(path.join(out,'data/budget-curves.csv'),columns.join(',')+'\n'+rows.map(r=>columns.map(k=>r[k]).join(',')).join('\n')+'\n');
fs.writeFileSync(path.join(out,'data/dictionary.json'),JSON.stringify({grain:'One retained source curve cell transformed to a $200 planning account',budget_usd:'USD available for metered token charges',runs_equivalent:'200 / cost, continuous mean-rate planning equivalent',whole_run_plan:'floor(runs_equivalent), not a guaranteed quota',expected_success_equivalent:'200 * success_probability / cost; expectation under fixed spending rate',delta_whole_runs:'whole plan minus same-workload baseline whole plan',same_use_spend_usd:'Cost at the whole baseline task count',same_use_balance_usd:'200 minus same_use_spend_usd',limitations:data.budgetView.interpretation},null,2));
const report={ok:true,checks,sourceCells:rows.length,targetExecutions:0,budgetUSD:200,sourceDataSha256:hash(dataRaw),htmlSha256:hash(html),headlines:headline,calendar,limitations:['Derived from frozen mathematical data, not new empirical evidence.','Uncertain costs require a separate stopping-process model for actual count distributions.','Quality and benchmark transfer remain assumptions.']};
fs.writeFileSync(path.join(out,'qa/arithmetic-report.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({output:path.join(out,'deck/index.html'),bytes:Buffer.byteLength(html),scenes:14,checks,sourceCells:rows.length,ok:true,headlines:headline.map(r=>({id:r.id,runs:r.whole,delta:r.delta,sameUseSpend:r.sameUseSpend})),calendar}));
