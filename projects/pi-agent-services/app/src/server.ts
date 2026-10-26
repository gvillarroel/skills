// Build with npm run build. Loopback API for the service's own agent registry.
import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { randomBytes, timingSafeEqual } from 'node:crypto';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { Catalog, type Job, type ServiceEvent } from './catalog.js';
import { AgentRuntime } from './runtime.js';
import { loadServiceEnvironment, type ServiceConfig } from './config.js';
import { pollPullRequests, parseWebhook, GitHubEventError, type AgentEvent } from './github.js';
import { Watchers } from './watchers.js';
import { NotificationOutbox } from './notifications.js';

export class HttpError extends Error {constructor(readonly statusCode:number,message:string){super(message);}}
async function rawBody(request:IncomingMessage) {const chunks:Buffer[]=[];let bytes=0;for await(const chunk of request){bytes+=chunk.length;if(bytes>1024*1024)throw new HttpError(413,'Request body exceeds 1 MiB.');chunks.push(Buffer.from(chunk));}return Buffer.concat(chunks);}
function json(response:ServerResponse,value:unknown,status=200){response.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});response.end(JSON.stringify(value));}
export class AgentService {
  private runtimes=new Map<string,AgentRuntime>(); private running=new Map<string,Promise<void>>(); private stopping=false;
  private timer?:NodeJS.Timeout; private polling=false; private nextPoll=new Map<string,number>(); private pollAbort=new AbortController();
  private pilotTimer?:NodeJS.Timeout; private pilotPolling=false; private watchers?:Watchers; private notifications?:NotificationOutbox;
  private admissionsPaused=false;private admissionsInFlight=0;private shutdownOperation?:Promise<void>;private closePromise?:Promise<void>;
  private resolveClosed!:()=>void;private rejectClosed!:(error:unknown)=>void;
  readonly closed=new Promise<void>((resolve,reject)=>{this.resolveClosed=resolve;this.rejectClosed=reject;});
  private server=createServer((request,response)=>{void this.handle(request,response);});
  private constructor(readonly config:ServiceConfig,readonly catalog:Catalog,private token:string){void this.closed.catch(()=>{});}
  static async open(config:ServiceConfig) {
    await loadServiceEnvironment(config.dataDir);
    if(config.github.mode==='webhook' && !process.env.GITHUB_WEBHOOK_SECRET)throw new Error('GITHUB_WEBHOOK_SECRET is required for webhook mode.');
    const catalog=await Catalog.open(config.dataDir,config.agents);let service:AgentService|undefined;
    try {
      const path=join(config.dataDir,'console-token');let token:string;
      try{token=(await readFile(path,'utf8')).trim();if(!/^[a-f0-9]{64}$/.test(token))throw new Error('Invalid console-token file.');}
      catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;token=randomBytes(32).toString('hex');await writeFile(path,token+'\n',{flag:'wx',mode:0o600});}
      service=new AgentService(config,catalog,token);
      if(config.pilot){
        service.watchers=new Watchers({projectDir:config.pilot.repositoryRoot,stateDir:join(config.dataDir,'watchers'),repository:config.pilot.repository,stabilityMs:config.pilot.stabilityMs});
        const channels:Array<'desktop'|'telegram'>=[];
        if(config.pilot.desktopNotifications)channels.push('desktop');
        if(config.pilot.telegramNotifications===true)channels.push('telegram');
        if(channels.length)service.notifications=await NotificationOutbox.open(join(config.dataDir,'notifications'),{channels});
      }
      for(const agent of config.agents)service.runtimes.set(agent.id,await AgentRuntime.open(config,agent));
      await new Promise<void>((resolve,reject)=>{service!.server.once('error',reject);service!.server.listen(config.port,config.host,()=>{service!.server.off('error',reject);resolve();});});
      service.kick();
      if(config.github.mode==='poll'){service.timer=setInterval(()=>{void service!.poll();},1000);void service.poll();}
      if(config.pilot){service.pilotTimer=setInterval(()=>{void service!.pollPilot();},config.pilot.intervalMs);void service.pollPilot();}
      return service;
    }catch(error){if(service)await service.close();else catalog.close();throw error;}
  }
  get url(){const address=this.server.address();return `http://127.0.0.1:${typeof address==='object' && address ? address.port : this.config.port}`;}
  stats(){return Object.fromEntries([...this.runtimes].map(([id,runtime])=>[id,{providerCalls:runtime.calls}]));}
  admit(event:ServiceEvent){if(this.stopping||this.admissionsPaused)throw new HttpError(503,'Service admissions are paused for shutdown.');const ids=this.catalog.admit([event],this.config.agents);this.kick();return ids;}
  private async prepareShutdown(timeoutMs:number){
    if(this.stopping)return;if(this.shutdownOperation)return this.shutdownOperation;
    this.admissionsPaused=true;
    this.shutdownOperation=(async()=>{const deadline=Date.now()+timeoutMs;
      while(true){
        if(this.admissionsInFlight===0){
          const pending=this.catalog.agents().some(agent=>Number(agent.pending)>0);
          const idle=await Promise.all([...this.runtimes.values()].map(runtime=>runtime.quiescent()));
          if(!pending&&!this.running.size&&!this.polling&&!this.pilotPolling&&idle.every(Boolean))return;
        }
        if(Date.now()>=deadline)throw new HttpError(409,'Work is still running; shutdown did not cancel it and admissions have resumed.');
        await new Promise(resolve=>setTimeout(resolve,10));
      }
    })();
    try{await this.shutdownOperation;}catch(error){this.admissionsPaused=false;throw error;}finally{this.shutdownOperation=undefined;}
  }
  private kick(){if(this.stopping)return;for(const agent of this.config.agents){if(this.running.has(agent.id))continue;const work=Promise.resolve().then(()=>this.drain(agent.id)).finally(()=>{this.running.delete(agent.id);if(!this.stopping&&this.catalog.next(agent.id))this.kick();});this.running.set(agent.id,work);}}
  private async drain(agentId:string){const runtime=this.runtimes.get(agentId)!;while(!this.stopping){const job=this.catalog.next(agentId);if(!job)return;this.catalog.update(job.id,'running');
    this.notifications?.enqueue({agentId,jobId:job.id,type:'job.started'});
    const deadline=setTimeout(()=>{void runtime.abort(job.id).catch(()=>{});},8*60*1000);
    try{const result=await runtime.run(job,(conversationId,submissionId)=>this.catalog.update(job.id,'running',{conversationId,submissionId}));if(!this.stopping){this.catalog.update(job.id,result.status,result);this.notifications?.enqueue({agentId,jobId:job.id,type:result.status==='done'?'job.completed':'job.failed'});if(this.config.pilot){const directory=join(this.config.dataDir,'reports');await mkdir(directory,{recursive:true});const key=createHash('sha256').update(job.id).digest('hex').slice(0,20);await writeFile(join(directory,`${agentId}-${key}.md`),`# ${agentId}\n\nJob: ${job.id}\n\nStatus: ${result.status}\n\n${result.result??result.error??''}\n`,{mode:0o600});}}}
    catch(error){if(!this.stopping){this.catalog.update(job.id,'failed',{error:error instanceof Error?error.message:'Task execution failed'});this.notifications?.enqueue({agentId,jobId:job.id,type:'job.failed'});}}
    finally{clearTimeout(deadline);}
  }}
  async pollPilot(){if(this.pilotPolling||this.stopping||this.admissionsPaused||!this.watchers||!this.config.pilot)return;this.pilotPolling=true;
    try{for(const agentId of ['repo-quality','delivery-watch'] as const){
      if(this.stopping||this.admissionsPaused)break;
      if(!this.runtimes.has(agentId)||this.running.has(agentId)||this.catalog.next(agentId))continue;
      const jobs=this.catalog.jobs(agentId), last=jobs[0] as (Job&{admittedAt?:string})|undefined;
      if(this.catalog.admittedToday(agentId)>=this.config.pilot.maxJobsPerAgentPerDay)continue;
      if(last && Date.now()-Date.parse(last.admittedAt??last.event.createdAt)<this.config.pilot.minJobIntervalMs)continue;
      const event=await this.watchers.tick(agentId);if(this.stopping||this.admissionsPaused)break;
      if(event){this.admit(event);await this.watchers.ack(agentId,event.id);}
    }
    if(!this.stopping)await this.notifications?.flush({limit:4});
    }catch{console.error(JSON.stringify({type:'pilot-poll-error',message:'A bounded watcher or notification attempt failed; inspect local state.'}));}
    finally{this.pilotPolling=false;}
  }
  async poll(){if(this.polling||this.stopping||this.admissionsPaused)return;this.polling=true;
    try{for(const repository of [...new Set(this.config.agents.flatMap(a=>a.repositories))]){
      if(this.stopping||this.admissionsPaused||Date.now()<(this.nextPoll.get(repository)??0))continue;
      try{const result=await pollPullRequests({repository,token:process.env.GITHUB_TOKEN,state:this.catalog.state(repository),initialScan:this.config.github.initialScan,maxPages:this.config.github.maxPages,signal:this.pollAbort.signal});if(this.stopping||this.admissionsPaused)return;
        this.catalog.admit(result.events,this.config.agents,{repository,state:result.state});
        this.nextPoll.set(repository,Date.now()+Math.max(this.config.github.intervalMs,(result.state.minPollIntervalSeconds??0)*1000));this.kick();
      }catch(error){if(this.stopping)return;const backoff=error instanceof GitHubEventError && error.retryAt?Date.parse(error.retryAt):Date.now()+Math.max(this.config.github.intervalMs,60000);this.nextPoll.set(repository,Math.max(Date.now()+1000,backoff));console.error(JSON.stringify({type:'poll-error',repository,code:error instanceof GitHubEventError?error.code:'network_error',retryAt:new Date(this.nextPoll.get(repository)!).toISOString()}));}
    }}finally{this.polling=false;}
  }
  private async handle(request:IncomingMessage,response:ServerResponse){try{
    const url=new URL(request.url??'/',this.url);
    if(request.method==='GET' && url.pathname==='/health'){json(response,{service:'pi-durable-agent-service',version:1});return;}
    if(request.method==='POST' && url.pathname==='/webhooks/github'){
      if(this.config.github.mode!=='webhook')throw new HttpError(404,'Webhook mode is disabled.');
      const event=parseWebhook(await rawBody(request),{event:String(request.headers['x-github-event']??''),signature:String(request.headers['x-hub-signature-256']??''),delivery:String(request.headers['x-github-delivery']??'')},process.env.GITHUB_WEBHOOK_SECRET!);
      json(response,{accepted:true,jobs:event?this.admit(event):[]},202);return;
    }
    const provided=Buffer.from(request.headers.authorization??'');const expected=Buffer.from(`Bearer ${this.token}`);
    if(provided.length!==expected.length||!timingSafeEqual(provided,expected))throw new HttpError(401,'A local console bearer token is required.');
    if(request.headers.origin && request.headers.origin!==this.url)throw new HttpError(403,'Cross-origin requests are disabled.');
    if(request.method==='GET' && url.pathname==='/v1/agents'){json(response,{agents:this.catalog.agents(),mode:this.config.provider.kind});return;}
    if(request.method==='GET' && url.pathname==='/v1/status'){json(response,{pid:process.pid,provider:this.config.provider.kind,model:this.config.provider.model,admissionsPaused:this.admissionsPaused,stats:this.stats(),watching:!!this.watchers,budgets:this.config.pilot?Object.fromEntries(this.config.agents.map(a=>[a.id,{admittedToday:this.catalog.admittedToday(a.id),maximum:this.config.pilot!.maxJobsPerAgentPerDay}])):{},notifications:this.notifications?.list()??[]});return;}
    if(request.method==='POST' && url.pathname==='/v1/shutdown'){
      const value=JSON.parse((await rawBody(request)).toString('utf8')||'{}') as Record<string,unknown>;
      const timeoutMs=value?.timeoutMs??30000;if(!Number.isInteger(timeoutMs)||Number(timeoutMs)<0||Number(timeoutMs)>60000)throw new HttpError(400,'shutdown timeoutMs must be an integer from 0 to 60000.');
      await this.prepareShutdown(Number(timeoutMs));json(response,{stopping:true,drained:true});setImmediate(()=>{void this.close().catch(()=>{process.exitCode=1;});});return;
    }
    if(request.method==='POST' && url.pathname==='/v1/events'){
      const value=JSON.parse((await rawBody(request)).toString('utf8')) as AgentEvent;
      if(value.type!=='pull_request.opened'||!Number.isInteger(value.number)||value.number<1||!this.config.agents.some(a=>a.repositories.includes(String(value.repository).toLowerCase())))throw new HttpError(400,'Expected an allowlisted pull_request.opened event.');
      value.repository=value.repository.toLowerCase();value.id=`github:${value.repository}:pull_request:${value.number}:opened`;
      json(response,{jobs:this.admit(value)},202);return;
    }
    const match=/^\/v1\/agents\/([a-z][a-z0-9-]*)\/(jobs|chat|messages|evidence|feedback|submissions\/[0-9]+|abort)$/.exec(url.pathname);
    if(!match)throw new HttpError(404,'Unknown service route.');const runtime=this.runtimes.get(match[1]);if(!runtime)throw new HttpError(404,'Agent is not active in this configuration.');
    const jobId=url.searchParams.get('jobId')??undefined;
    if(jobId && !this.catalog.job(match[1],jobId))throw new HttpError(404,'Unknown job for this agent.');
    if(request.method==='GET'&&match[2]==='jobs'){json(response,{jobs:this.catalog.jobs(match[1])});return;}
    if(request.method==='GET'&&match[2]==='evidence'){const limit=Number(url.searchParams.get('limit')??100);if(!Number.isInteger(limit)||limit<1||limit>10000)throw new HttpError(400,'Evidence limit must be from 1 to 10000.');json(response,{records:runtime.evidence.list(match[1],limit)});return;}
    if(request.method==='POST'&&match[2]==='feedback'){
      const value=JSON.parse((await rawBody(request)).toString('utf8')) as Record<string,unknown>;
      if(typeof value.summary!=='string'||!value.summary.trim()||value.summary.length>4000||!Array.isArray(value.evidenceIds)||value.evidenceIds.length>30||value.evidenceIds.some(id=>typeof id!=='string'||!runtime.evidence.has(match[1],id)))throw new HttpError(400,'Feedback requires a bounded summary and existing evidence IDs for this agent.');
      const receipt=runtime.trace('feedback.recorded',{summary:value.summary,evidenceIds:value.evidenceIds,source:'authenticated-local-user'},jobId?{jobId}:{});json(response,{evidenceId:receipt.id},201);return;
    }
    if(request.method==='GET'&&match[2]==='chat'){json(response,await runtime.snapshot(jobId));return;}
    if(request.method==='GET'&&match[2].startsWith('submissions/')){const status=await runtime.status(Number(match[2].split('/')[1]));if(!status)throw new HttpError(404,'Unknown submission.');json(response,status);return;}
    if(request.method==='POST'&&match[2]==='messages'){
      if(this.stopping||this.admissionsPaused)throw new HttpError(503,'Service admissions are paused for shutdown.');
      const value=JSON.parse((await rawBody(request)).toString('utf8')) as Record<string,unknown>;
      if(typeof value.content!=='string'||!value.content.trim()||value.content.length>100000||typeof value.requestId!=='string'||!value.requestId||!['followUp','steer','reject'].includes(String(value.whenBusy??'followUp')))throw new HttpError(400,'content, stable requestId and a valid whenBusy mode are required.');
      if(this.stopping||this.admissionsPaused)throw new HttpError(503,'Service admissions are paused for shutdown.');
      this.admissionsInFlight++;let receipt;
      try{receipt=await runtime.submitHuman({content:value.content,requestId:value.requestId,whenBusy:(value.whenBusy??'followUp') as 'followUp'|'steer'|'reject'},jobId);}finally{this.admissionsInFlight--;}
      json(response,receipt,202);return;
    }
    if(request.method==='POST'&&match[2]==='abort'){await runtime.abort(jobId);json(response,{aborted:true});return;}
    throw new HttpError(405,'Method not allowed.');
  }catch(error){if(!response.headersSent)json(response,{error:error instanceof Error?error.message:'Request failed'},(error as {statusCode?:number}).statusCode??(error instanceof SyntaxError?400:500));else response.end();}}
  async close(){if(this.closePromise)return this.closePromise;this.stopping=true;if(this.timer)clearInterval(this.timer);if(this.pilotTimer)clearInterval(this.pilotTimer);this.watchers?.close();this.pollAbort.abort();
    this.closePromise=(async()=>{if(this.server.listening)await new Promise<void>((resolve,reject)=>this.server.close(error=>error?reject(error):resolve()));
      while(this.polling||this.pilotPolling)await new Promise(resolve=>setTimeout(resolve,10));await Promise.all([...this.runtimes.values()].map(runtime=>runtime.close()));await Promise.allSettled(this.running.values());this.notifications?.close();this.catalog.close();})();
    this.closePromise.then(this.resolveClosed,this.rejectClosed);return this.closePromise;
  }
}
