// Run: node projects/desktop-plugin-ui/capability-study-20261025/copilot/sdk-protocol.mjs
// Uses existing task-local official SDK/CLI. No send/sendAndWait/model prompt.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {CopilotClient,RuntimeConnection} from '../../artifacts/cross-assistant/copilot/package/dist/index.js';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const old=path.join(project,'artifacts/cross-assistant/copilot');
const artifacts=path.join(project,'artifacts/capability-study-20261025/copilot');
fs.mkdirSync(artifacts,{recursive:true});
const providerRequests=[];const callbacks=[];const rows=[];const sessions=[];
const server=http.createServer((request,response)=>{
  providerRequests.push({method:request.method,url:request.url});
  response.writeHead(503,{'content-type':'application/json'});
  response.end(JSON.stringify({error:'Inference is disabled for this synthetic capability study.'}));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const baseUrl=`http://127.0.0.1:${server.address().port}/v1`;
const env={...process.env,COPILOT_AUTO_UPDATE:'false',COPILOT_OFFLINE:'true',
  COPILOT_PROVIDER_BASE_URL:baseUrl,COPILOT_MODEL:'ui-study-no-inference',COPILOT_PROVIDER_MODEL_ID:'ui-study-no-inference'};
for(const key of ['GITHUB_TOKEN','GH_TOKEN','COPILOT_GITHUB_TOKEN','COPILOT_PROVIDER_API_KEY','COPILOT_PROVIDER_BEARER_TOKEN'])delete env[key];
const client=new CopilotClient({connection:RuntimeConnection.forStdio({path:path.join(old,'cli103/package/copilot.exe'),
  args:['--no-auto-update','--disable-client-telemetry','--disable-builtin-mcps']}),
  baseDirectory:path.join(artifacts,'sdk-profile'),workingDirectory:path.dirname(fileURLToPath(import.meta.url)),
  useLoggedInUser:false,env,logLevel:'error',mode:'empty'});
function record(id,expected,actual,layer='real-runtime-with-supplied-consumer-callback'){
  const passed=JSON.stringify(expected)===JSON.stringify(actual);rows.push({id,passed,expected,actual,layer});
}
try{
  await client.start();
  const status=await client.getStatus();
  rows.push({id:'runtime-build-status',passed:true,actual:{version:status.version,protocolVersion:status.protocolVersion},layer:'runtime-protocol'});
  const config={model:'ui-study-no-inference',availableTools:[],infiniteSessions:{enabled:false},
    provider:{type:'openai',baseUrl,wireApi:'completions'},enableConfigDiscovery:false,
    onPermissionRequest:()=>({kind:'denied-interactively-by-user'})};
  const bare=await client.createSession(config);sessions.push(bare);
  rows.push({id:'bare-consumer-capabilities',passed:true,actual:bare.capabilities,layer:'negotiation-not-paint'});
  let absentError='';try{await bare.ui.confirm('Synthetic bare consumer confirmation');}catch(error){absentError=String(error);}
  record('bare-consumer-confirm-refused',true,/not supported by the host/.test(absentError),'runtime-capability-gate');

  const responses=[
    {action:'accept',content:{confirmed:true}}, {action:'decline'}, {action:'cancel'},
    {action:'accept',content:{selection:'Beta'}}, {action:'cancel'},
    {action:'accept',content:{value:'synthetic'}}, {action:'decline'},
    {action:'accept',content:{value:true}},
  ];
  const host=await client.createSession({...config,onElicitationRequest:context=>{
    callbacks.push({message:context.message,mode:context.mode,requestedSchema:context.requestedSchema});
    return responses.shift();
  }});sessions.push(host);
  record('callback-advertises-elicitation',true,host.capabilities.ui?.elicitation,'negotiation-not-paint');
  record('confirm-accept',true,await host.ui.confirm('Synthetic confirmation acceptance'));
  record('confirm-decline',false,await host.ui.confirm('Synthetic confirmation decline'));
  record('confirm-cancel',false,await host.ui.confirm('Synthetic confirmation cancellation'));
  record('select-accept','Beta',await host.ui.select('Synthetic selection',['Alpha','Beta']));
  record('select-cancel',null,await host.ui.select('Synthetic selection cancellation',['Alpha','Beta']));
  record('input-accept','synthetic',await host.ui.input('Synthetic input',{title:'Value',description:'Synthetic text only',minLength:1,maxLength:12,default:'synthetic'}));
  record('input-decline',null,await host.ui.input('Synthetic input decline'));
  record('wrong-confirm-field-remains-false',false,await host.ui.confirm('Synthetic wrong response field'));
  record('all-callbacks-consumed',0,responses.length);
  record('input-schema-options-forwarded',12,callbacks[5].requestedSchema?.properties?.value?.maxLength,'runtime-schema-roundtrip');
}catch(error){rows.push({id:'probe-error',passed:false,error:String(error),layer:'probe-execution'});}
finally{
  for(const session of sessions){try{await session.destroy();}catch{}}
  await client.stop().catch(()=>{});await new Promise(resolve=>server.close(resolve));
  record('zero-provider-requests',0,providerRequests.length,'inference-guard');
  const report={timestampUtc:new Date().toISOString(),passed:rows.every(row=>row.passed),modelPrompts:0,
    sdkVersion:'1.0.26',cliVersion:'1.0.103',providerRequests,callbacks,rows,
    note:'Synthetic consumer callbacks are protocol tests. No terminal form, native canvas, MCP App, or Copilot chat paint is asserted.'};
  fs.writeFileSync(path.join(artifacts,'sdk-protocol.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({passed:report.passed,checks:rows.length,providerRequests:providerRequests.length,modelPrompts:0,rows},null,2));
  if(!report.passed)process.exitCode=1;
}
