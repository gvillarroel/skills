// Run from this package: node node_modules/tsx/dist/cli.mjs verify-live-copilot-20261025.ts
// Uses the package's pinned MCP SDK/Playwright dependencies. No assistant/model/account action.
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {chromium} from 'playwright';

const packageRoot=import.meta.dirname;
const project=path.resolve(packageRoot,'..');
const run=process.env.UI_COPILOT_VERIFY_RUN??'v1';
if(!/^v[1-9]\d*$/.test(run))throw new Error('Use a fresh versioned verification run ID, such as v2.');
const output=path.join(project,`artifacts/capability-study-20261025/copilot/cs1-fixture-verification-${run}`);
if(existsSync(path.join(output,'report.json')))throw new Error('Refusing to overwrite a completed verification receipt.');
await mkdir(output,{recursive:true});
const checks:{id:string,passed:boolean,actual?:unknown}[]=[];
const errors:string[]=[];
const pageErrors:string[]=[];
const requests:string[]=[];
const rpcCalls:{method:string,params:unknown}[]=[];
const states:unknown[]=[];
const check=(id:string,passed:unknown,actual?:unknown)=>checks.push({id,passed:Boolean(passed),...(actual===undefined?{}:{actual})});
const digest=(bytes:Uint8Array|string)=>createHash('sha256').update(bytes).digest('hex');
const legacy=path.join(packageRoot,'live-server.ts');
const clone=path.join(packageRoot,'live-server-copilot-20261025.ts');
const before={legacy:digest(await readFile(legacy)),clone:digest(await readFile(clone))};
const env:Record<string,string>={UI_PROBE_ARTIFACTS:path.join(output,'server')};
for(const key of ['PATH','SystemRoot','TEMP','TMP','PATHEXT','ComSpec'])if(process.env[key])env[key]=process.env[key]!;
const transport=new StdioClientTransport({command:process.execPath,args:[path.join(packageRoot,'node_modules/tsx/dist/cli.mjs'),clone,'--stdio'],env,stderr:'pipe'});
const stderr:string[]=[];
transport.stderr?.on('data',chunk=>stderr.push(String(chunk)));
const client=new Client({name:'CS1 synthetic verification',version:'1.0.0'});
let browser:Awaited<ReturnType<typeof chromium.launch>>|undefined;
try{
  await client.connect(transport);
  const tools=await client.listTools();
  check('exact-two-tools',tools.tools.map(t=>t.name).sort().join(',')==='ui_limits_open,ui_probe_increment');
  const opening=tools.tools.find(t=>t.name==='ui_limits_open')!;
  const increment=tools.tools.find(t=>t.name==='ui_probe_increment')!;
  check('same-resource-and-app-only-contract',(opening._meta?.ui as any)?.resourceUri==='ui://assistant-limits/probe-v1.html'&&(increment._meta?.ui as any)?.visibility?.join(',')==='app');
  const initial=await client.callTool({name:'ui_limits_open',arguments:{}});
  check('initial-synthetic-seven',initial.structuredContent?.value===7&&initial.structuredContent?.synthetic===true);
  const resource=await client.readResource({uri:'ui://assistant-limits/probe-v1.html'});
  const body=resource.contents[0];
  const html='text' in body?body.text:'';
  check('real-resource-mime',body.mimeType==='text/html;profile=mcp-app');
  check('compiled-html-english-and-cs1',html.includes('lang="en"')&&html.includes('--ui-primary:#9e1b32')&&!html.includes('var(--color-background-primary'));
  await writeFile(path.join(output,'served.html'),html);
  const direct=await client.callTool({name:'ui_probe_increment',arguments:{value:7}});
  const invalid=await client.callTool({name:'ui_probe_increment',arguments:{value:-1}});
  check('direct-valid-invalid-contract',direct.structuredContent?.value===8&&invalid.isError===true);
  const design=JSON.parse((await readFile(path.join(project,'artifacts/capability-study-20261025/copilot/config-snapshots/cs1-design-values-v1.json'),'utf8')).replace(/^\uFEFF/,''));
  check('seven-exact-helper-paths-and-pairs',design.passed===true&&design.resolved.length===7&&design.contrast.length===7);
  check('text-and-focus-thresholds',design.contrast.slice(0,4).every((p:any)=>p.requirements.ordinary_text.passes)&&design.contrast.slice(4).every((p:any)=>p.requirements.essential_non_text.passes));
  browser=await chromium.launch({headless:true,channel:'msedge'});
  const context=await browser.newContext({viewport:{width:900,height:1200},locale:'en-US',offline:true,serviceWorkers:'block'});
  await context.route('**/*',async route=>{requests.push(route.request().url());await route.abort();});
  const page=await context.newPage();page.setDefaultTimeout(8000);
  page.on('pageerror',error=>pageErrors.push(error.message));
  await page.exposeFunction('cs1HostRpc',async(method:string,params:any)=>{
    rpcCalls.push({method,params});
    if(method==='ui/initialize')return {protocolVersion:params.protocolVersion,hostInfo:{name:'Synthetic local CS1 fixture',version:'1.0.0'},hostCapabilities:{serverTools:{},updateModelContext:{}},hostContext:{theme:'dark',displayMode:'inline',availableDisplayModes:['inline'],containerDimensions:{width:900,maxHeight:1500}}};
    if(method==='tools/call')return client.callTool(params);
    if(method==='ui/update-model-context')return {};
    throw new Error(`Synthetic host does not support ${method}`);
  });
  await page.setContent('<!doctype html><html lang="en"><head><title>Synthetic CS1 fixture</title></head><body style="margin:0"><iframe id="app" title="Synthetic CS1 fixture" sandbox="allow-scripts" style="display:block;width:100%;height:1500px;border:0"></iframe></body></html>');
  await page.evaluate(({html,initial})=>{
    const frame=document.getElementById('app') as HTMLIFrameElement;
    window.addEventListener('message',async event=>{
      if(event.source!==frame.contentWindow||event.data?.jsonrpc!=='2.0')return;
      const message=event.data;
      if(message.method==='ui/notifications/initialized'){
        frame.contentWindow!.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:initial},'*');return;
      }
      if(message.id!==undefined){
        try{const result=await (window as any).cs1HostRpc(message.method,message.params??{});frame.contentWindow!.postMessage({jsonrpc:'2.0',id:message.id,result},'*');}
        catch(error){frame.contentWindow!.postMessage({jsonrpc:'2.0',id:message.id,error:{code:-32601,message:String(error)}},'*');}
      }
    });
    frame.srcdoc=html;
  },{html,initial});
  const frame=page.frameLocator('#app');
  await frame.locator('#ready').filter({hasText:'Connected to host bridge'}).waitFor();
  await frame.locator('#value').filter({hasText:'7'}).waitFor();
  check('browser-real-sdk-handshake',true);
  check('unsupported-controls-disabled',await frame.getByRole('button',{name:'Fullscreen',exact:true}).isDisabled()&&await frame.getByRole('button',{name:'Picture in picture',exact:true}).isDisabled()&&await frame.getByRole('button',{name:'Download synthetic text',exact:true}).isDisabled()&&await frame.getByRole('button',{name:'Open example.com',exact:true}).isDisabled());
  await frame.getByRole('button',{name:'Increment locally via tool',exact:true}).click();
  await frame.locator('#value').filter({hasText:'8'}).waitFor();check('browser-app-tool-roundtrip',true);
  await frame.getByRole('button',{name:'Reject invalid input',exact:true}).click();
  await frame.locator('#result').filter({hasText:'The input was rejected. Check the value and try again.'}).waitFor();
  check('english-rejection-preserves-eight',(await frame.locator('#result').innerText()).includes('"valuePreserved": 8')&&await frame.locator('#value').innerText()==='8');
  await frame.getByRole('button',{name:'Increment locally via tool',exact:true}).click();
  await frame.locator('#value').filter({hasText:'9'}).waitFor();check('recovery-after-rejection',true);
  await frame.getByRole('button',{name:'Check sandbox',exact:true}).click();
  await frame.locator('#result').filter({hasText:'SecurityError'}).waitFor();check('sandbox-parent-dom-denied',true);
  await frame.getByRole('button',{name:'Update model context only',exact:true}).click();
  await frame.locator('#result').filter({hasText:'"action": "context"'}).waitFor();
  check('context-without-followup-message',rpcCalls.some(c=>c.method==='ui/update-model-context')&&!rpcCalls.some(c=>c.method==='ui/message'));
  await frame.getByRole('button',{name:'Increment locally via tool',exact:true}).focus();
  await page.keyboard.press('Tab');await page.keyboard.press('Shift+Tab');
  const focus=await frame.getByRole('button',{name:'Increment locally via tool',exact:true}).evaluate(e=>({color:getComputedStyle(e).outlineColor,width:getComputedStyle(e).outlineWidth,offset:getComputedStyle(e).outlineOffset}));
  check('keyboard-focus-cs1-visible',focus.color==='rgb(158, 27, 50)'&&focus.width==='3px'&&focus.offset==='3px',focus);
  for(const width of [900,360,320]){
    await page.setViewportSize({width,height:1500});
    const layout=await frame.locator('body').evaluate(()=>({scroll:document.documentElement.scrollWidth,width:document.documentElement.clientWidth,language:document.documentElement.lang,background:getComputedStyle(document.body).backgroundColor,ink:getComputedStyle(document.body).color,targets:[...document.querySelectorAll('button,summary')].map(e=>e.getBoundingClientRect().height)}));
    check(`layout-${width}`,layout.scroll<=layout.width+1&&layout.targets.every(h=>h>=44),layout);
    check(`authored-paint-${width}`,layout.language==='en'&&layout.background==='rgb(255, 255, 255)'&&layout.ink==='rgb(51, 62, 72)',layout);
    const copy={width,text:await frame.locator('body').innerText(),accessible:await frame.locator('body').ariaSnapshot()};states.push(copy);
    await page.screenshot({path:path.join(output,`width-${width}.png`),fullPage:true});
  }
  check('no-page-errors-or-network',pageErrors.length===0&&requests.length===0,{pageErrors,requests});
  await context.close();
}catch(error){errors.push(String(error));}
finally{await browser?.close();await client.close();}
check('legacy-and-clone-unchanged',before.legacy===digest(await readFile(legacy))&&before.clone===digest(await readFile(clone)));
const report={passed:errors.length===0&&checks.every(c=>c.passed),timestamp_utc:new Date().toISOString(),layer:'real MCP stdio SDK plus offline synthetic sandboxed browser; not Copilot Chat',source_sha256:before,checks,errors,pageErrors,requests,rpcCalls,states,stderr,model_turns:0,provider_requests:0,assistant_host_acceptance_verified:false,limitations:['Synthetic protocol host only; no signed-in Copilot Chat acceptance.','No OS download, external navigation, device permission, screen-reader application or user study.','Forced-colors override is authored but not exercised in this fixture.']};
await writeFile(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,checks:checks.length,errors,output},null,2));
if(!report.passed)process.exitCode=1;
