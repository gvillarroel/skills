#!/usr/bin/env node
// Build with npm run build. Run node dist/src/manage.js <start|status|stop|jobs|chat>.
import { spawn } from 'node:child_process';
import { openSync, closeSync } from 'node:fs';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadConfig } from './config.js';
import { pilotConfigPath } from './pilot-config.js';

const project=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const cli=join(project,'dist/src/cli.js');
async function main(){
  const [action='status',...args]=process.argv.slice(2);
  const configPath=pilotConfigPath(project), config=await loadConfig(configPath);
  if(action==='start'){
    try{const response=await fetch(`http://127.0.0.1:${config.port}/health`,{signal:AbortSignal.timeout(2000)});if(response.ok)throw new Error('A service already answers on the configured port. Use status to verify ownership.');}catch(error){if(error instanceof Error&&error.message.startsWith('A service already'))throw error;}
    const logs=join(config.dataDir,'logs');await mkdir(logs,{recursive:true});
    const output=openSync(join(logs,'host.stdout.log'),'a'),error=openSync(join(logs,'host.stderr.log'),'a');
    let child;
    try{child=spawn(process.execPath,[cli,'serve','--config',configPath],{cwd:project,windowsHide:true,detached:true,stdio:['ignore',output,error]});await new Promise<void>((accept,reject)=>{child!.once('spawn',accept);child!.once('error',reject);});}
    finally{closeSync(output);closeSync(error);}
    child.unref();
    await writeFile(join(config.dataDir,'process.json'),JSON.stringify({pid:child.pid,node:process.execPath,config:configPath,startedAt:new Date().toISOString()},null,2)+'\n',{mode:0o600});
    let ready=false;
    for(let attempt=0;attempt<30;attempt++){
      try{const token=(await readFile(join(config.dataDir,'console-token'),'utf8')).trim();const response=await fetch(`http://127.0.0.1:${config.port}/v1/status`,{headers:{Authorization:`Bearer ${token}`},signal:AbortSignal.timeout(1000)});if(response.ok){const status=await response.json() as {pid:number};if(status.pid!==child.pid)throw new Error('Unexpected owner on service port.');ready=true;break;}}catch{}
      await new Promise(accept=>setTimeout(accept,500));
    }
    if(!ready)throw new Error('The service did not become ready; inspect project-local host logs.');
    console.log(JSON.stringify({status:'running',pid:child.pid,url:`http://127.0.0.1:${config.port}`,agents:config.agents.map(a=>a.id),autoStartAtLogin:false},null,2));return;
  }
  if(!['status','stop','jobs','chat','traces','abort','list'].includes(action))throw new Error('Use start, status, stop, list, jobs <agent>, chat <agent>, traces <agent>, or abort <agent>.');
  const child=spawn(process.execPath,[cli,action,...args,'--config',configPath],{cwd:project,stdio:'inherit',windowsHide:true});
  process.exitCode=await new Promise<number>(accept=>{child.once('exit',code=>accept(code??1));child.once('error',()=>accept(1));});
}
main().catch(()=>{console.error('Pilot operation failed. Check the command, local service status, and project-local logs.');process.exitCode=1;});
