#!/usr/bin/env node
// Node 24 native TypeScript: node projects/desktop-plugin-ui/scripts/verify-pi-import-rpc.ts <extension.ts> <installed-pi-dist/bundle/cli.js> [run-label] [--probe-stale-input]
// Actual offline Pi RPC checks; no new dependency or global installation.
import {spawn,spawnSync} from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {createHash} from "node:crypto";
const [extensionArgument,cliArgument,label="baseline",probe] = process.argv.slice(2);
if(!extensionArgument||!cliArgument||!/^[a-z0-9-]+$/.test(label)||(probe!==undefined&&probe!=="--probe-stale-input")) throw new Error("Usage: node verify-pi-import-rpc.ts <extension.ts> <installed-cli.js> [run-label] [--probe-stale-input]");
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
const extension=await fs.realpath(path.resolve(extensionArgument));
const cli=await fs.realpath(path.resolve(cliArgument));
if(!extension.startsWith(repo+path.sep)) throw new Error("Generated source must stay inside the repository.");
const output=path.join(repo,"projects/desktop-plugin-ui/artifacts/plugin-pocs/pi-rpc",label);
await fs.mkdir(output,{recursive:true});
const state=path.join(output,"agent-state");
await fs.mkdir(state,{recursive:true});
const env={...process.env,PI_CODING_AGENT_DIR:state};
const digest=(bytes:Uint8Array)=>createHash("sha256").update(bytes).digest("hex");
const before=digest(await fs.readFile(extension));
const version=spawnSync(process.execPath,[cli,"--offline","--version"],{cwd:output,env,encoding:"utf8",timeout:10000});
if(version.status!==0) throw new Error(`Pi version failed: ${version.stderr}`);
const args=[cli,"--offline","--mode","rpc","--no-session","--no-context-files","--no-extensions","--no-skills","--no-prompt-templates","--no-themes","--no-mcp","--no-tools","--no-approve","-e",extension];
const child=spawn(process.execPath,args,{cwd:output,env,stdio:["pipe","pipe","pipe"],windowsHide:true});
const records:any[]=[];const invalid:string[]=[];const checks:any[]=[];
let raw="",pending="",stderr="",spawnError="";let finished:any;
const closed=new Promise<void>(resolve=>child.once("close",(code,signal)=>{finished={code,signal};resolve();}));
child.once("error",error=>spawnError=String(error));
child.stdout.setEncoding("utf8");child.stderr.setEncoding("utf8");
child.stdout.on("data",chunk=>{raw+=chunk;pending+=chunk;let split:number;while((split=pending.indexOf("\n"))>=0){const line=pending.slice(0,split).replace(/\r$/,"");pending=pending.slice(split+1);if(!line.trim())continue;try{records.push(JSON.parse(line));}catch{invalid.push(line);}}});
child.stderr.on("data",chunk=>stderr+=chunk);
const check=(name:string,passed:unknown,detail:any=undefined)=>{checks.push({name,passed:Boolean(passed),...(detail===undefined?{}:{detail})});if(!passed)throw new Error(name);};
const send=(value:any)=>child.stdin.write(JSON.stringify(value)+"\n");
const wait=async(predicate:(record:any)=>boolean,start=0)=>{const deadline=Date.now()+15000;while(Date.now()<deadline){const result=records.slice(start).find(predicate);if(result)return result;if(invalid.length||finished||spawnError)throw new Error(`RPC exited or invalid: ${JSON.stringify(finished)} ${spawnError}`);await new Promise(resolve=>setTimeout(resolve,20));}throw new Error("Timed out waiting for actual Pi RPC response.");};
const rows=(value:any)=>Array.isArray(value)?value.map(row=>({id:row.id,name:row.name})).sort((a,b)=>a.id.localeCompare(b.id)):value;
const same=(a:any,b:any)=>JSON.stringify(a)===JSON.stringify(b);
let sequence=0;
type Answer={method:"select"|"input"|"confirm";value?:string|RegExp|boolean;cancel?:boolean;beforeReply?:()=>Promise<void>};
async function invoke(command:string,answers:Answer[]=[]){
  const start=records.length;const id=`operation-${++sequence}`;send({id,type:"prompt",message:`/import-review${command?" "+command:""}`});
  let scan=start;let answerIndex=0;
  for(;;){
    const event=await wait(record=>(record.type==="response"&&record.id===id)||record.type==="extension_ui_request"&&["select","input","confirm","editor"].includes(record.method),scan);
    scan=records.indexOf(event)+1;
    if(event.type==="response"){
      check(`${command||"menu"}: command handled`,event.success===true&&event.data?.disposition==="handled",event);
      const messages=records.slice(start).filter(record=>record.type==="message_end"&&record.message?.customType==="import-review");
      return {state:messages.at(-1)?.message?.details,messages,events:records.slice(start)};
    }
    const answer=answers[answerIndex++];
    check(`${command||"menu"}: expected native ${event.method}`,answer&&answer.method===event.method,{event,answer});
    if(answer.beforeReply)await answer.beforeReply();
    if(answer.cancel){send({type:"extension_ui_response",id:event.id,cancelled:true});continue;}
    if(event.method==="confirm"){send({type:"extension_ui_response",id:event.id,confirmed:answer.value===true});continue;}
    let value=answer.value;
    if(event.method==="select"){
      const option=event.options?.find((option:string)=>value instanceof RegExp?value.test(option):option===value);
      check("Semantic native option exists",typeof option==="string",{event,requested:String(value)});value=option;
    }
    send({type:"extension_ui_response",id:event.id,value});
  }
}
const expectedInitial=[{id:"I-11",name:"Atlas"},{id:"I-12",name:""},{id:"I-13",name:"Cedar"}];
let failure:string|undefined;let forced=false;
try{
  send({id:"commands",type:"get_commands"});const commands=await wait(record=>record.type==="response"&&record.id==="commands");
  check("Actual installed Pi discovers import-review",commands.success&&commands.data?.commands?.some(command=>command.name==="import-review"));
  const initial=(await invoke("status")).state;
  check("Initial exact draft and no committed rows",same(rows(initial?.draftRows),rows(expectedInitial))&&initial.committedRows.length===0,initial);
  await invoke(`commit ${initial.draftRevision}`);check("Missing review cannot commit",(await invoke("status")).state?.committedRows.length===0);
  const review=(await invoke("review")).state;
  check("Review contains only valid rows",same(rows(review?.reviewedRows),rows([expectedInitial[0],expectedInitial[2]])));
  const edited=(await invoke("edit I-12 Birch")).state;
  check("Editing invalidates prior review",edited?.draftRevision>initial.draftRevision&&edited.reviewRevision===null&&edited.reviewedRows.length===0);
  await invoke(`commit ${review.reviewRevision}`);check("Stale review cannot commit",(await invoke("status")).state?.committedRows.length===0);
  const fresh=(await invoke("review")).state;await invoke(`commit ${fresh.reviewRevision}`);
  const committed=(await invoke("status")).state;
  check("Exact current revision commits three rows",same(rows(committed.committedRows),rows(fresh.reviewedRows))&&committed.committedRows.length===3);
  await invoke(`commit ${fresh.reviewRevision}`);check("Repeated commit has no duplicate",same((await invoke("status")).state,committed));
  await invoke("edit I-12 Silver Birch");const beforeCancel=(await invoke("review")).state;
  await invoke("cancel");const afterCancel=(await invoke("status")).state;
  check("Explicit cancel preserves draft and committed state",afterCancel.reviewRevision===null&&afterCancel.reviewedRows.length===0&&same(rows(afterCancel.draftRows),rows(beforeCancel.draftRows))&&same(rows(afterCancel.committedRows),rows(beforeCancel.committedRows)));
  const beforeMenu=(await invoke("status")).state;
  await invoke("",[{method:"select",cancel:true}]);check("Native menu Escape makes no change",same((await invoke("status")).state,beforeMenu));
  const beforeConfirm=(await invoke("review")).state;
  await invoke("",[{method:"select",value:/\bcommit\b/i},{method:"confirm",value:false}]);
  check("Declined native commit keeps review for retry",same((await invoke("status")).state,beforeConfirm));
  await invoke("",[{method:"select",value:/\bcommit\b/i},{method:"confirm",value:true}]);
  const confirmed=(await invoke("status")).state;
  check("Accepted native commit uses exact reviewed rows",same(rows(confirmed.committedRows),rows(beforeConfirm.reviewedRows)));
  if(probe==="--probe-stale-input"){
    await invoke("",[{method:"select",value:/\bedit\b/i},{method:"select",value:/I-12/},{method:"input",value:"Birch",beforeReply:async()=>{await invoke("edit I-12 Newer Birch");}}]);
    const afterInterleaving=(await invoke("status")).state;
    check("Old native input cannot overwrite newer same-row value",afterInterleaving?.draftRows?.find(row=>row.id==="I-12")?.name==="Newer Birch",afterInterleaving);
  }
}catch(error){failure=String(error);}finally{
  child.stdin.end();let timeout:ReturnType<typeof setTimeout>|undefined;
  await Promise.race([closed,new Promise<void>(resolve=>{timeout=setTimeout(()=>{forced=true;child.kill();resolve();},5000);})]);if(timeout)clearTimeout(timeout);if(forced)await closed;
  checks.push({name:"Zero model agent/turn events",passed:!records.some(record=>["agent_start","agent_end","turn_start","turn_end"].includes(record.type))});
  checks.push({name:"Valid JSONL stdout",passed:invalid.length===0&&pending.trim()===""});
  checks.push({name:"Clean unforced exit",passed:!forced&&finished?.code===0&&finished.signal===null});
  checks.push({name:"Empty stderr and no spawn failure",passed:stderr.trim()===""&&spawnError===""});
  checks.push({name:"Generated source unchanged",passed:before===digest(await fs.readFile(extension))});
  const report={passed:!failure&&checks.every(item=>item.passed),host:{version:version.stdout.trim(),node:process.version},extension,sourceSha256:before,checks,failure:failure??null,finished,forced,
    boundary:"Actual installed offline RPC command/dialog transport. Native terminal paint, focus, resize, installation and user testing remain unverified."};
  await fs.writeFile(path.join(output,"events.jsonl"),raw);await fs.writeFile(path.join(output,"stderr.log"),stderr);await fs.writeFile(path.join(output,"result.json"),JSON.stringify(report,null,2)+"\n");
  console.log(JSON.stringify({passed:report.passed,checks:checks.length,failure,output}));process.exit(report.passed?0:1);
}
