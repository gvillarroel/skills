// Run: node projects/plugin-ui-rich-interfaces/scripts/verify-pi.mjs
import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {spawn,spawnSync} from "node:child_process";
import {renderDashboard} from "../pi/observatory.ts";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const output=path.join(root,"artifacts/reviews/pi");await fs.mkdir(output,{recursive:true});
const probe=spawnSync("uv",["run","--script",path.join(root,"../../skills/pi-extension-ui/scripts/probe_runtime.py"),"--host","pi"],{encoding:"utf8",windowsHide:true});
if(probe.status!==0)throw new Error(probe.stderr);
const readiness=JSON.parse(probe.stdout),cli=readiness.checks.find(c=>c.name==="pi").command[1];
const extension=path.join(root,"pi/observatory.ts");
const args=[cli,"--offline","--mode","rpc","--no-session","--no-context-files","--no-extensions","--no-skills","--no-prompt-templates","--no-themes","--no-mcp","--no-tools","--no-approve","-e",extension];
const env={...process.env,PI_CODING_AGENT_DIR:path.join(root,"artifacts/pi-state")};
const child=spawn(process.execPath,args,{cwd:output,env,windowsHide:true,stdio:["pipe","pipe","pipe"]});
const events=[],checks=[];let pending="",raw="",stderr="",failure;
child.stdout.setEncoding("utf8");child.stderr.setEncoding("utf8");
child.stdout.on("data",chunk=>{raw+=chunk;pending+=chunk;let i;while((i=pending.indexOf("\n"))>=0){const line=pending.slice(0,i).trim();pending=pending.slice(i+1);if(line){try{events.push(JSON.parse(line));}catch{failure="Invalid RPC JSON";}}}});
child.stderr.on("data",chunk=>stderr+=chunk);child.on("error",error=>failure=String(error));
function check(name,passed,detail){checks.push({name,passed:Boolean(passed),detail});if(!passed)throw new Error(name);}
function send(value){child.stdin.write(JSON.stringify(value)+"\n");}
async function wait(predicate,start=0){const deadline=Date.now()+15000;while(Date.now()<deadline){if(failure)throw new Error(failure);const result=events.slice(start).find(predicate);if(result)return result;await new Promise(resolve=>setTimeout(resolve,10));}throw new Error("RPC response timeout");}
let sequence=0;
async function invoke(argument,answers=[]){
  const id=`invoke-${++sequence}`,start=events.length;send({id,type:"prompt",message:`/service-observatory${argument?" "+argument:""}`});
  let cursor=start;
  for(const answer of answers){const request=await wait(e=>e.type==="extension_ui_request"&&e.method==="select",cursor);cursor=events.indexOf(request)+1;send({type:"extension_ui_response",id:request.id,...(answer===null?{cancelled:true}:{value:answer})});}
  const response=await wait(e=>e.type==="response"&&e.id===id,start);
  check(`Real Pi handles command ${sequence}`,response.success&&response.data?.disposition==="handled",response);
  return events.slice(start);
}
try{
  send({id:"commands",type:"get_commands"});const registration=await wait(e=>e.type==="response"&&e.id==="commands");
  check("Extension is discovered by real Pi",registration.data.commands.some(c=>c.name==="service-observatory"));
  const result=await invoke("",["orders | Orders | watch","metrics"]);
  check("RPC native dialogs return exact selected metrics",result.some(e=>e.method==="notify"&&e.message.includes("Orders [WATCH]")&&e.message.includes("142")));
  const canceled=await invoke("",[null]);check("Cancel does not emit a success result",!canceled.some(e=>e.method==="notify"));
  const partial=await invoke("",["payments | Payments | degraded",null]);
  check("Second-dialog cancel does not publish partial choices",!partial.some(e=>e.method==="notify"));
  const selection=await invoke("",[null]);
  check("Second-dialog cancel preserves previous selected service",selection.some(e=>e.method==="select"&&e.title.includes("current: orders")));
  const direct=await invoke("payments dependencies");
  check("Direct arguments preserve relationships",direct.some(e=>e.method==="notify"&&e.message.includes("Orders -> Payments: 920 req/s")));
  const exact=await invoke("payments values");
  check("Exact-values route preserves all 24 hourly observations",exact.some(e=>e.method==="notify"&&(e.message.match(/\d\d:00/g)??[]).length===24&&e.message.includes("268 ms")));
  const invalid=await invoke("unrecognized");check("Unknown service gives usable recovery",invalid.some(e=>e.method==="notify"&&e.message.includes("/service-observatory payments metrics")));
  check("No inference starts in RPC",!events.some(e=>["agent_start","turn_start"].includes(e.type)));
  const printed=spawnSync(process.execPath,[cli,"--offline","--mode","json","--print","--no-session","--no-context-files","--no-extensions","--no-skills","--no-prompt-templates","--no-themes","--no-mcp","--no-tools","--no-approve","-e",extension,"/service-observatory payments metrics"],{cwd:output,env,encoding:"utf8",timeout:30000,windowsHide:true});
  await fs.writeFile(path.join(output,"print.jsonl"),printed.stdout);
  const lines=printed.stdout.split(/\r?\n/).filter(Boolean).map(line=>JSON.parse(line));
  check("JSON print returns useful exact text without inference",printed.status===0&&lines.some(e=>e.message?.customType==="service-observatory"&&e.message.content.includes("268"))&&!lines.some(e=>["agent_start","turn_start"].includes(e.type)),printed.stderr);
  for(const width of [60,80,120])for(const view of ["dependencies","metrics","values","records"]){
    const lines=renderDashboard("payments",view,width);
    check(`${view} fits ${width} terminal columns`,lines.every(line=>line.length+2<=width));
    await fs.writeFile(path.join(output,`${view}-${width}.txt`),lines.map(line=>"  "+line).join("\n")+"\n");
  }
}catch(error){failure=String(error);}finally{
  child.kill();await fs.writeFile(path.join(output,"rpc.jsonl"),raw);await fs.writeFile(path.join(output,"stderr.txt"),stderr);
  const report={passed:!failure&&checks.every(c=>c.passed),version:readiness.checks.find(c=>c.name==="pi").version,checks,failure,scope:"Real Pi RPC and print routes plus deterministic terminal geometry. Actual TUI keyboard/paint is a separate check."};
  await fs.writeFile(path.join(output,"review.json"),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
}
