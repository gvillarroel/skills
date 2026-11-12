// Run: node projects/desktop-plugin-ui/cross-assistant/copilot/probe-sdk.mjs
// Uses the task-local official @github/copilot-sdk 1.0.26 installation.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {CopilotClient, RuntimeConnection} from '../../artifacts/cross-assistant/copilot/package/dist/index.js';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const artifacts = path.join(project, 'artifacts/cross-assistant/copilot');
const calls = [];
const server = http.createServer((request, response) => {
  calls.push({method:request.method, url:request.url});
  response.writeHead(503, {'content-type':'application/json'});
  response.end(JSON.stringify({error:'No inference provider is running: this is a no-inference UI protocol probe.'}));
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const baseUrl = `http://127.0.0.1:${server.address().port}/v1`;
const env = {...process.env, COPILOT_AUTO_UPDATE:'false', COPILOT_OFFLINE:'true', COPILOT_PROVIDER_BASE_URL:baseUrl,
  COPILOT_MODEL:'ui-evidence-no-inference',COPILOT_PROVIDER_MODEL_ID:'ui-evidence-no-inference'};
for(const key of ['GITHUB_TOKEN','GH_TOKEN','COPILOT_GITHUB_TOKEN','COPILOT_PROVIDER_API_KEY','COPILOT_PROVIDER_BEARER_TOKEN']) delete env[key];
const client = new CopilotClient({
  connection:RuntimeConnection.forStdio({path:path.join(artifacts,'cli103/package/copilot.exe'),args:['--no-auto-update','--disable-builtin-mcps']}),
  baseDirectory:path.join(artifacts,'sdk-home'),workingDirectory:path.dirname(fileURLToPath(import.meta.url)),
  useLoggedInUser:false,env,logLevel:'error',mode:'empty'
});
const rows=[];
const sessions=[];
const callbacks=[];
try {
  await client.start();
  const config={model:'ui-evidence-no-inference',availableTools:[],infiniteSessions:{enabled:false},
    provider:{type:'openai',baseUrl,wireApi:'completions'},enableConfigDiscovery:false};
  const session=await client.createSession({...config,onPermissionRequest:()=>({kind:'denied-interactively-by-user'})});
  sessions.push(session);
  rows.push({name:'runtime-session-capabilities-with-no-renderer',status:'observed-working',capabilities:session.capabilities});
  try { await session.ui.confirm('Synthetic capability check'); rows.push({name:'elicitation-without-host',status:'unexpected-success'}); }
  catch(error) { rows.push({name:'elicitation-without-host',status:'observed-failed',error:String(error)}); }
  const host=await client.createSession({...config,onPermissionRequest:()=>({kind:'denied-interactively-by-user'}),
    onElicitationRequest: context => { callbacks.push(context); return {action:'accept',content:{confirmed:true}}; }});
  sessions.push(host);
  const accepted=await host.ui.confirm('Synthetic confirm callback check');
  rows.push({name:'elicitation-with-explicit-consumer-callback',status:accepted?'observed-working':'observed-failed',
    capabilities:host.capabilities,accepted,callbacks});
} catch(error) { rows.push({name:'runtime-probe',status:'blocked',error:String(error)}); }
finally {
  for(const session of sessions) { try { await session.destroy(); } catch {} }
  await client.stop().catch(()=>{});
  await new Promise(resolve=>server.close(resolve));
  const report={timestampUtc:new Date().toISOString(),layer:'real-copilot-runtime-with-sdk-consumer-callback',
    sdkVersion:'1.0.26',cliVersion:'1.0.103',modelPrompts:0,providerRequests:calls,
    note:'No native TUI or Copilot-chat rendering is asserted; the consumer callback is deliberately supplied by this probe.',rows};
  fs.writeFileSync(path.join(artifacts,'copilot-sdk-no-inference.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
}
