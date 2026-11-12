#!/usr/bin/env node
// Node 24 native TypeScript: node projects/desktop-plugin-ui/scripts/test-pi-guarded-intent.ts
// Requires Node 24+ only; tests the canonical dependency-free guard template.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {runGuardedIntent} from "../../../skills/desktop-plugin-ui/assets/templates/pi-stateful/guarded-intent.ts";

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
const output=path.join(repo,"projects/desktop-plugin-ui/artifacts/plugin-pocs/pi-guard-helper");
fs.mkdirSync(output,{recursive:true});
const checks:any[]=[];
const check=async(name:string,action:()=>Promise<void>)=>{try{await action();checks.push({name,passed:true});}catch(error){checks.push({name,passed:false,error:String(error)});}};
const deferred=<T>()=>{let resolve!:(value:T)=>void;const promise=new Promise<T>(done=>resolve=done);return{promise,resolve};};

await check("unchanged version applies once after collection",async()=>{
  let version=0,value="old",applies=0;const order:string[]=[];
  const result=await runGuardedIntent({getRevision:()=>{order.push("version");return version;},collect:async()=>{order.push("collect");return "new";},apply:intent=>{order.push("apply");value=intent;version++;applies++;return undefined;}});
  assert.equal(result,"applied");assert.equal(value,"new");assert.equal(applies,1);assert.deepEqual(order,["version","collect","version","apply"]);
});
await check("dismissal never applies",async()=>{
  let applies=0;const result=await runGuardedIntent({getRevision:()=>0,collect:async()=>undefined,apply:()=>{applies++;return undefined;}});
  assert.equal(result,"cancelled");assert.equal(applies,0);
});
await check("falsy intents remain distinct from cancellation",async()=>{
  for(const intent of [false,0,""]){let received:any="unset";const result=await runGuardedIntent({getRevision:()=>0,collect:async()=>intent,apply:value=>{received=value;return undefined;}});assert.equal(result,"applied");assert.equal(received,intent);}
});
await check("old same-record input cannot overwrite newer value",async()=>{
  let version=0,value="old",applies=0;const input=deferred<string>();
  const pending=runGuardedIntent({getRevision:()=>version,collect:()=>input.promise,apply:intent=>{value=intent;applies++;return undefined;}});
  value="newer";version++;input.resolve("stale");assert.equal(await pending,"stale");assert.equal(value,"newer");assert.equal(applies,0);
});
await check("deferred confirmation cannot commit invalidated review",async()=>{
  let version=0,committed="unchanged";const confirm=deferred<boolean>();
  const pending=runGuardedIntent({getRevision:()=>version,collect:async()=>(await confirm.promise)?"reviewed":undefined,apply:intent=>{committed=intent;return undefined;}});
  version++;confirm.resolve(true);assert.equal(await pending,"stale");assert.equal(committed,"unchanged");
});
await check("declined confirmation preserves a valid review",async()=>{
  const review={version:0,data:"reviewed"};let committed="unchanged";
  const result=await runGuardedIntent({getRevision:()=>review.version,collect:async()=>false?review.data:undefined,apply:intent=>{committed=intent;return undefined;}});
  assert.equal(result,"cancelled");assert.equal(committed,"unchanged");assert.deepEqual(review,{version:0,data:"reviewed"});
});
await check("domain validation rejects before writing and allows fresh retry",async()=>{
  let version=0,value="old";
  await assert.rejects(runGuardedIntent({getRevision:()=>version,collect:async()=>"   ",apply:intent=>{if(!intent.trim())throw new Error("Enter a name");value=intent;return undefined;}}),/Enter a name/);
  assert.equal(value,"old");version++;
  const result=await runGuardedIntent({getRevision:()=>version,collect:async()=>"valid",apply:intent=>{value=intent;version++;return undefined;}});
  assert.equal(result,"applied");assert.equal(value,"valid");
});
await check("directly async apply is rejected before collection",async()=>{
  let collected=false,applied=false;
  await assert.rejects(runGuardedIntent({getRevision:()=>0,collect:async()=>{collected=true;return "value";},apply:(async()=>{applied=true;}) as any}),/synchronous/);
  assert.equal(collected,false);assert.equal(applied,false);
});
await check("promise-returning ordinary apply is detected",async()=>{
  await assert.rejects(runGuardedIntent({getRevision:()=>0,collect:async()=>"value",apply:(()=>Promise.resolve()) as any}),/must return undefined/);
});
await check("collection failure propagates without applying",async()=>{
  let applied=false;await assert.rejects(runGuardedIntent({getRevision:()=>0,collect:async()=>{throw new Error("Dialog failed");},apply:()=>{applied=true;return undefined;}}),/Dialog failed/);assert.equal(applied,false);
});
const report={passed:checks.every(item=>item.passed),checks,boundary:"Generic local version guard tests; no Pi runtime, host painting or user testing claim."};
fs.writeFileSync(path.join(output,"result.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({passed:report.passed,checks:checks.length,failed:checks.filter(item=>!item.passed).map(item=>item.name),output}));
process.exit(report.passed?0:1);
