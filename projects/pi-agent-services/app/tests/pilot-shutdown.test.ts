// npm run build; node --import tsx --test tests/pilot-shutdown.test.ts
// These are real local Harness/HTTP/process tests with faux generation only.
import assert from 'node:assert/strict';
import test from 'node:test';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { DatabaseSync } from 'node:sqlite';
import { mkdir,mkdtemp,readFile,writeFile } from 'node:fs/promises';
import { join,resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { BACKGROUND_CONTEXT as context } from '@earendil-works/chord/context';
import { defineTask } from '@earendil-works/pi-durable';
import { AgentService } from '../src/server.js';
import { AgentRuntime } from '../src/runtime.js';
import type { ServiceConfig } from '../src/config.js';

async function fixture(delayMs=0):Promise<ServiceConfig>{await mkdir('artifacts',{recursive:true});return {version:1,host:'127.0.0.1',port:0,dataDir:await mkdtemp(resolve('artifacts/shutdown-')),provider:{kind:'faux',delayMs},github:{mode:'off',intervalMs:1000,initialScan:'baseline'},agents:[{id:'reader',name:'Reader',instructions:'Report only the supplied offline marker.',repositories:['owner/repo']}]};}
const event=(number:number)=>({id:`github:owner/repo:pull_request:${number}:opened`,type:'pull_request.opened',repository:'owner/repo',number,title:'Offline fixture',url:`https://github.com/owner/repo/pull/${number}`,headSha:'a'.repeat(40),createdAt:'2026-10-25T00:00:00Z'});
async function until(check:()=>unknown|Promise<unknown>,timeoutMs=10000){const end=Date.now()+timeoutMs;while(!await check()){if(Date.now()>=end)throw new Error('Timed out waiting for the asserted owner state.');await delay(10);}}
async function client(url:string,dataDir:string){const token=(await readFile(join(dataDir,'console-token'),'utf8')).trim();return async(path:string,body?:unknown)=>{const response=await fetch(url+path,{method:body===undefined?'GET':'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},...(body===undefined?{}:{body:JSON.stringify(body)})});return {status:response.status,value:await response.json() as any};};}
const runtime=(service:AgentService)=>(service as unknown as {runtimes:Map<string,AgentRuntime>}).runtimes.get('reader')!;

test('actual standalone owner drains queued jobs and control work and exits despite an idle handle',{timeout:20000},async()=>{
  const cfg=await fixture(200),file=join(cfg.dataDir,'config.json');await writeFile(file,JSON.stringify(cfg));
  const child=spawn(process.execPath,['--import','data:text/javascript,setInterval(()=>{},1000)','dist/src/cli.js','serve','--config',file],{cwd:process.cwd(),windowsHide:true,stdio:['ignore','pipe','pipe']});
  let output='',errors='';child.stdout.on('data',value=>{output+=value;});child.stderr.on('data',value=>{errors+=value;});const exited=once(child,'exit');
  try{
    await until(()=>{if(child.exitCode!==null)throw new Error(errors);return output.includes('listening');});const address=JSON.parse(output.trim().split('\n')[0]);const call=await client(address.url,cfg.dataDir);
    assert.equal((await fetch(address.url+'/v1/shutdown',{method:'POST',body:'{}'})).status,401);
    for(const n of [1,2])assert.equal((await call('/v1/events',event(n))).status,202);
    const control=await call('/v1/agents/reader/messages',{content:'CONTROL-DRAIN-MARKER',requestId:'control-drain-one'});assert.equal(control.status,202);
    const response=await call('/v1/shutdown',{timeoutMs:5000});assert.equal(response.status,200);assert.equal(response.value.drained,true);
    await until(()=>child.exitCode!==null);const [code,signal]=await exited;assert.equal(code,0,errors);assert.equal(signal,null);
    const db=new DatabaseSync(join(cfg.dataDir,'catalog.sqlite'),{readOnly:true});try{const jobs=db.prepare('SELECT status,conversationId,submissionId,result FROM jobs').all();assert.equal(jobs.length,2);assert.ok(jobs.every(job=>job.status==='done'&&job.conversationId&&job.submissionId&&String(job.result).includes('OFFLINE DEMO')));}finally{db.close();}
    const evidence=new DatabaseSync(join(cfg.dataDir,'evidence.sqlite'),{readOnly:true});try{assert.equal(Number(evidence.prepare("SELECT count(*) AS n FROM evidence WHERE kind='model.request'").get()!.n),3);assert.equal(Number(evidence.prepare("SELECT count(*) AS n FROM evidence WHERE kind='runtime.closed'").get()!.n),1);}finally{evidence.close();}
    const owner=new DatabaseSync(join(cfg.dataDir,'owner.sqlite'));try{owner.exec('PRAGMA busy_timeout=0; BEGIN EXCLUSIVE; ROLLBACK');}finally{owner.close();}
    const reopened=await AgentService.open({...cfg,provider:{kind:'faux'}});try{const again=await client(reopened.url,cfg.dataDir);assert.equal((await again(`/v1/agents/reader/submissions/${control.value.submissionId}`)).value.status,'done');assert.equal(reopened.catalog.jobs('reader').length,2);assert.equal(reopened.stats().reader.providerCalls,0);}finally{await reopened.close();}
  }finally{if(child.exitCode===null&&child.signalCode===null){child.kill('SIGKILL');await exited;}}
});

test('busy timeout preserves work and resumes admission; a real drain refuses new messages',{timeout:15000},async()=>{
  const service=await AgentService.open(await fixture(500)),call=await client(service.url,service.config.dataDir);
  try{
    const first=(await call('/v1/agents/reader/messages',{content:'KEEP-WORK',requestId:'busy-first'})).value;
    const busy=await call('/v1/shutdown',{timeoutMs:0});assert.equal(busy.status,409);assert.match(busy.value.error,/did not cancel/);assert.equal((await call('/v1/status')).value.admissionsPaused,false);
    const second=await call('/v1/agents/reader/messages',{content:'SECOND-WORK',requestId:'busy-second'});assert.equal(second.status,202);
    const shutdown=call('/v1/shutdown',{timeoutMs:5000});await until(async()=>(await call('/v1/status')).value.admissionsPaused);
    assert.equal((await call('/v1/agents/reader/messages',{content:'REFUSE-NEW',requestId:'busy-third'})).status,503);
    assert.equal((await call('/v1/events',event(9))).status,503);
    assert.equal((await shutdown).status,200);await service.closed;
    const reopen=await AgentService.open({...service.config,provider:{kind:'faux'}});try{const again=await client(reopen.url,reopen.config.dataDir);for(const id of [first.submissionId,second.value.submissionId])assert.equal((await again(`/v1/agents/reader/submissions/${id}`)).value.status,'done');assert.equal(reopen.stats().reader.providerCalls,0);}finally{await reopen.close();}
  }finally{await service.close();}
});

test('blocked background work prevents shutdown even when no job or generation is running',{timeout:10000},async()=>{
  const service=await AgentService.open(await fixture()),call=await client(service.url,service.config.dataDir),owner=runtime(service);
  const held=defineTask({name:'fixture.pilot-held-background',version:1,initial:()=>({phase:'hold' as const}),phases:{hold:async()=>{}},abort:async()=>{}});
  try{
    await owner.harness.commit(tx=>tx.createTask(held,{}, {conversationId:owner.root.id,ownership:{kind:'conversation'},background:true}),context);
    assert.equal((await call('/v1/shutdown',{timeoutMs:0})).status,409);assert.equal(await owner.quiescent(),false);assert.equal(service.stats().reader.providerCalls,0);
    await owner.root.abort(context,{background:true});await until(()=>owner.quiescent());assert.equal((await call('/v1/shutdown',{timeoutMs:1000})).status,200);await service.closed;
  }finally{await service.close();}
});

test('an accepted message still entering the Harness cannot slip past the drain',{timeout:10000},async()=>{
  const service=await AgentService.open(await fixture()),call=await client(service.url,service.config.dataDir),owner=runtime(service);
  let entering=false,release!:()=>void;const gate=new Promise<void>(resolve=>{release=resolve;}),original=owner.submitHuman.bind(owner);
  owner.submitHuman=async(...args)=>{entering=true;await gate;return original(...args);};
  try{
    const message=call('/v1/agents/reader/messages',{content:'IN-FLIGHT-ADMISSION',requestId:'admission-race'});await until(()=>entering);
    assert.equal((await call('/v1/shutdown',{timeoutMs:0})).status,409);release();assert.equal((await message).status,202);
    assert.equal((await call('/v1/shutdown',{timeoutMs:3000})).status,200);await service.closed;
  }finally{release();await service.close();}
});

test('a watcher finishing during shutdown neither admits nor acknowledges the pending event',{timeout:10000},async()=>{
  const cfg=await fixture();cfg.agents[0].id='repo-quality';const service=await AgentService.open(cfg),call=await client(service.url,cfg.dataDir);
  let entered=false,release!:(value:any)=>void,acknowledged=0;const gate=new Promise<any>(resolve=>{release=resolve;});
  cfg.pilot={repositoryRoot:resolve('.'),repository:'owner/repo',intervalMs:10000,stabilityMs:30000,minJobIntervalMs:60000,maxJobsPerAgentPerDay:1,desktopNotifications:false};
  (service as any).watchers={tick:async()=>{entered=true;return gate;},ack:async()=>{acknowledged++;},close:()=>{}};
  try{
    const polling=service.pollPilot();await until(()=>entered);const shutdown=call('/v1/shutdown',{timeoutMs:3000});await until(async()=>(await call('/v1/status')).value.admissionsPaused);
    release({id:'local:repo-quality:late',agentId:'repo-quality',type:'workspace.changed',createdAt:new Date().toISOString(),snapshot:{kind:'synthetic-late-capture'}});await polling;
    assert.equal((await shutdown).status,200);await service.closed;assert.equal(acknowledged,0);assert.equal(service.stats()['repo-quality'].providerCalls,0);
    const db=new DatabaseSync(join(cfg.dataDir,'catalog.sqlite'),{readOnly:true});try{assert.equal(Number(db.prepare('SELECT count(*) AS n FROM jobs').get()!.n),0);}finally{db.close();}
  }finally{release(undefined);await service.close();}
});
