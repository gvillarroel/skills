#!/usr/bin/env node
// Build with npm run build. Run node dist/src/verify-live.js <output.json> [baseline.json].
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadConfig } from './config.js';
import { pilotConfigPath } from './pilot-config.js';
type Receipt={provider:string;model:string;pid:number;agents:Array<{agentId:string;jobId:string;conversationId:number;submissionId:number;providerRequests:number;responses:number;decisions:number;currentProcessRequests:number}>;notifications:Array<{channel:string;status:string;type:string}>};
async function main(){
  const project=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
  const output=resolve(process.argv[2]??'../artifacts/manifests/live.json');
  const config=await loadConfig(pilotConfigPath(project));
  const token=(await readFile(resolve(config.dataDir,'console-token'),'utf8')).trim();
  const base=`http://127.0.0.1:${config.port}`;
  async function get(path:string){const response=await fetch(base+path,{headers:{Authorization:`Bearer ${token}`},signal:AbortSignal.timeout(10000)});assert.equal(response.status,200);return response.json() as Promise<any>;}
  assert.equal((await fetch(base+'/v1/status')).status,401);
  const status=await get('/v1/status');assert.equal(status.provider,'openai-codex');
  const receipt:Receipt={provider:status.provider,model:status.model,pid:status.pid,agents:[],notifications:status.notifications.map((n:any)=>({channel:n.channel,status:n.status,type:n.type}))};
  for(const agentId of ['repo-quality','delivery-watch']){
    const jobs=(await get(`/v1/agents/${agentId}/jobs`)).jobs;
    const job=jobs.find((j:any)=>j.status==='done');assert.ok(job,`${agentId} needs a real completed job.`);
    const snapshot=await get(`/v1/agents/${agentId}/chat?jobId=${encodeURIComponent(job.id)}`);assert.equal(snapshot.conversation.id,job.conversationId);
    const records=(await get(`/v1/agents/${agentId}/evidence?limit=1000`)).records;
    const responses=records.filter((e:any)=>e.kind==='model.response'&&e.conversationId===job.conversationId);
    assert.ok(responses.length>0);assert.ok(responses.every((e:any)=>e.details.model.provider==='openai-codex'&&e.details.model.model===config.provider.model));
    const decisions=records.filter((e:any)=>e.kind==='decision.recorded'&&e.conversationId===job.conversationId);assert.ok(decisions.length>0);
    receipt.agents.push({agentId,jobId:job.id,conversationId:job.conversationId,submissionId:job.submissionId,providerRequests:records.filter((e:any)=>e.kind==='model.request').length,responses:responses.length,decisions:decisions.length,currentProcessRequests:status.stats[agentId].providerCalls});
  }
  if(process.argv[3]){const baseline=JSON.parse(await readFile(resolve(process.argv[3]),'utf8')) as Receipt;assert.notEqual(receipt.pid,baseline.pid);for(const current of receipt.agents){const previous=baseline.agents.find(a=>a.agentId===current.agentId)!;assert.equal(current.jobId,previous.jobId);assert.equal(current.conversationId,previous.conversationId);assert.equal(current.submissionId,previous.submissionId);assert.equal(current.providerRequests,previous.providerRequests);assert.equal(current.currentProcessRequests,0);}}
  await mkdir(dirname(output),{recursive:true});await writeFile(output,JSON.stringify({...receipt,checkedAt:new Date().toISOString()},null,2)+'\n',{mode:0o600});
  console.log(JSON.stringify({verified:true,provider:receipt.provider,agents:receipt.agents,notifications:receipt.notifications},null,2));
}
main().catch(error=>{console.error(error instanceof Error?error.message:'Live verification failed.');process.exitCode=1;});
