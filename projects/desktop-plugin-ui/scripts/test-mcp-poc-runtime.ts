#!/usr/bin/env node
// Run with Node 24: node projects/desktop-plugin-ui/scripts/test-mcp-poc-runtime.ts <fresh-run-id>
// Uses the evaluator's locked MCP SDK/Playwright tooling, not the shipped skill.
import { mkdir, writeFile, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const runId = process.argv[2] ?? new Date().toISOString().replace(/[:.]/g, "-");
if (!/^[a-zA-Z0-9-]+$/.test(runId)) throw new Error("Use a simple fresh run ID");
const output = path.join(root, "projects/desktop-plugin-ui/artifacts/plugin-pocs/runtime-verifier-selftests", runId);
await mkdir(path.dirname(output), { recursive: true });
await mkdir(output, { recursive: false });
const rows = [{ id: "T-104", status: "pending", priority: "high" }, { id: "T-105", status: "pending", priority: "normal" }, { id: "T-106", status: "closed", priority: "high" }];
const css = "body{font:16px Arial;margin:16px;color:#333e48;background:#ffffff}select,button{font:inherit;color:#333e48;background:#ffffff;border:1px solid #696969;padding:8px}button{margin:4px}#apply{background:#9e1b32;color:#ffffff}button:focus-visible,select:focus-visible{outline:2px solid #000000;outline-offset:2px}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:6px;overflow-wrap:anywhere}#status{min-height:24px}button:disabled{opacity:.7}h1{font-size:24px}";
const appScript = String.raw`
let nextId=0;const pending=new Map();let committed='all';let current=[];
const view=document.querySelector('#view'),apply=document.querySelector('#apply'),cancel=document.querySelector('#cancel'),retry=document.querySelector('#retry'),status=document.querySelector('#status'),result=document.querySelector('#rows');
function rpc(method,params){return new Promise((resolve,reject)=>{const id=++nextId;pending.set(id,{resolve,reject});parent.postMessage({jsonrpc:'2.0',id,method,params},'*');});}
function render(data){committed=data.filter;current=data.rows;view.value=committed;result.innerHTML='';for(const row of current){const tr=document.createElement('tr');for(const key of ['id','status','priority']){const td=document.createElement('td');td.textContent=row[key];tr.append(td);}result.append(tr);}status.textContent='Ready';}
async function run(){apply.disabled=true;status.textContent='Loading selected view';retry.hidden=true;try{const response=await rpc('tools/call',{name:'queue_filter',arguments:{filter:view.value}});if(response.isError)throw Error(response.content[0].text);render(response.structuredContent);}catch(error){status.textContent='Error: '+String(error)+' Retry.';retry.hidden=false;}finally{apply.disabled=false;}}
apply.addEventListener('click',run);retry.addEventListener('click',run);cancel.addEventListener('click',()=>{view.value=committed;status.textContent='Cancelled; previous result preserved';});
window.addEventListener('message',event=>{const message=event.data;if(message?.jsonrpc!=='2.0')return;if(message.id!==undefined&&pending.has(message.id)){const callback=pending.get(message.id);pending.delete(message.id);message.error?callback.reject(Error(message.error.message)):callback.resolve(message.result);}if(message.method==='ui/notifications/tool-result')render(message.params.structuredContent);});
rpc('ui/initialize',{protocolVersion:'2026-01-26',appInfo:{name:'independent-valid-fixture',version:'1.0.0'},appCapabilities:{}}).then(()=>{parent.postMessage({jsonrpc:'2.0',method:'ui/notifications/initialized'},'*');}).catch(error=>{status.textContent='Host connection unavailable: '+String(error);apply.disabled=true;});
`;

const server = String.raw`
const readline=require('node:readline');const fs=require('node:fs');const path=require('node:path');
const rows=JSON.parse(fs.readFileSync(path.join(__dirname,'rows.json'),'utf8'));const uri='ui://fixture/queue.html';
function data(filter){return{filter,rows:rows.filter(row=>filter==='all'||(filter==='pending'?row.status==='pending':row.priority==='high')),count:rows.filter(row=>filter==='all'||(filter==='pending'?row.status==='pending':row.priority==='high')).length};}
function tool(filter){const value=data(filter);return{structuredContent:value,content:[{type:'text',text:value.rows.map(row=>row.id+' '+row.status+' '+row.priority).join('\n')}]};}
readline.createInterface({input:process.stdin}).on('line',line=>{let request;try{request=JSON.parse(line);}catch{return;}if(request.id===undefined)return;let result;switch(request.method){case'initialize':result={protocolVersion:request.params.protocolVersion,serverInfo:{name:'evaluator-fixture',version:'1.0.0'},capabilities:{tools:{},resources:{}}};break;case'tools/list':result={tools:[{name:'queue_open',description:'Open',inputSchema:{type:'object'},_meta:{ui:{resourceUri:uri}}},{name:'queue_filter',description:'Filter',inputSchema:{type:'object',properties:{filter:{type:'string',enum:['all','pending','high']}},required:['filter']},_meta:{ui:{visibility:['app']}}}]};break;case'resources/list':result={resources:[{uri,name:'Queue',mimeType:'text/html;profile=mcp-app'}]};break;case'resources/read':result={contents:[{uri,mimeType:'text/html;profile=mcp-app',text:fs.readFileSync(path.join(__dirname,'ui.html'),'utf8')}]};break;case'tools/call':if(request.params.name==='queue_open')result=tool('all');else if(request.params.name==='queue_filter'&&['all','pending','high'].includes(request.params.arguments?.filter))result=tool(request.params.arguments.filter);else result={isError:true,content:[{type:'text',text:'Invalid request'}]};break;default:result={};}process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:request.id,result})+'\n');});
`;
const cases = [];
for (const [name, cancelMutation, expectedAcceptance] of [["valid", false, true], ["cancel-sends-request", true, false]]) {
  const fixture = path.join(output, name); const dist = path.join(fixture, "dist");
  await mkdir(dist, { recursive: true });
  await writeFile(path.join(dist, "rows.json"), JSON.stringify(rows));
  await writeFile(path.join(dist, "server.cjs"), server.replaceAll("+'\\n'", "+String.fromCharCode(10)"));
  let script = appScript;
  if (cancelMutation) script = script.replace("view.value=committed;status.textContent='Cancelled; previous result preserved';", "view.value=committed;run();");
  const html = `<!doctype html><html lang="en"><head><style>${css}</style></head><body><h1>Queue review</h1><label for="view">View</label><select id="view"><option value="all">All tickets</option><option value="pending">Pending tickets</option><option value="high">High priority</option></select><div><button id="apply">Apply</button><button id="cancel">Cancel</button><button id="retry" hidden>Retry</button></div><p id="status" role="status">Connecting</p><table><thead><tr><th>ID</th><th>Status</th><th>Priority</th></tr></thead><tbody id="rows"></tbody></table><script>${script}</script></body></html>`;
  await writeFile(path.join(dist, "ui.html"), html);
  await writeFile(path.join(fixture, "review.json"), JSON.stringify({ heuristics: Array.from({ length: 10 }, (_, index) => ({ id: `H${index + 1}` })), host_acceptance_verified: false, user_testing_performed: false, palette: "colorset1" }));
  const packageReview = { launch: { command: "node", args: [path.join(dist, "server.cjs")], cwd: fixture }, extracted: fixture, poc: fixture };
  await writeFile(path.join(fixture, "package-review.json"), JSON.stringify(packageReview));
  const command = [path.join(root, "projects/desktop-plugin-ui/scripts/verify-mcp-poc.ts"), path.join(fixture, "package-review.json"), path.join(output, name + "-runtime")];
  const result = spawnSync(process.execPath, command, { cwd: root, encoding: "utf8", timeout: 90000 });
  const reportFile = path.join(output, name + "-runtime/runtime-review.json");
  let report;try { report = JSON.parse(await readFile(reportFile, "utf8")); } catch {}
  const accepted = result.status === 0 && report?.passed === true;
  cases.push({ name, passed: Boolean(report) && accepted === expectedAcceptance, expected_acceptance: expectedAcceptance, actual_acceptance: accepted, stdout: result.stdout, stderr: result.stderr, failed: report?.checks.filter(item => item.status !== "pass").map(item => item.name) });
}
const report = { passed: cases.every(item => item.passed), cases, scope: "Evaluator positive/negative protocol+browser fixtures only; no generated PoC or real host acceptance." };
await writeFile(path.join(output, "result.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report));
process.exitCode = report.passed ? 0 : 1;
