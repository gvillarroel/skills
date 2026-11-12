// Run from this package: npx --no-install tsx language-probe.ts
// Uses installed dependencies only. No provider, assistant host, or network call.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,readdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {build} from 'esbuild';
import {chromium, type Page} from 'playwright';

// Quoted Spanish messages are intentional foreign source/test data, not UI copy.
// They must remain in synthetic host replies and diagnostics, never recovery UI.
const foreignFixtures={
  initialize:'Error sintético de conexión del anfitrión.',
  invalid:'El valor sintético no es válido.',
  action:'La solicitud sintética fue rechazada.',
};
const packageRoot=import.meta.dirname;
const base=path.resolve(packageRoot,'../artifacts/component-language-20261025/live-browser');
await mkdir(base,{recursive:true});
const runName='run-'+String((await readdir(base)).filter(name=>/^run-\d+$/.test(name)).length+1).padStart(3,'0');
const output=path.join(base,runName);await mkdir(output,{recursive:true});
const checks:{id:string,passed:boolean,actual?:unknown}[]=[];
const states:unknown[]=[];
const consoleRecords:unknown[]=[];
const pageErrors:{scenario:string,message:string}[]=[];
const blockedRequests:{scenario:string,url:string}[]=[];
const caseErrors:{scenario:string,message:string}[]=[];
const pendingConsole:Promise<unknown>[]=[];
const rpcCalls:{scenario:string,method:string,params:unknown}[]=[];
function check(id:string,condition:unknown,actual?:unknown){
  checks.push({id,passed:Boolean(condition),...(actual===undefined?{}:{actual})});
  assert.ok(condition,id);
}
const hash=(text:string)=>createHash('sha256').update(text).digest('hex');
const sourceFiles=['widget.ts','live-widget.ts','probe.ts','live-server.ts'];
const sourceHashes=Object.fromEntries(await Promise.all(sourceFiles.map(async file=>[file,hash(await readFile(path.join(packageRoot,file),'utf8'))])));

async function actualTemplate(sourceFile:string,entry:string,format:'iife'|'esm'){
  const source=await readFile(path.join(packageRoot,sourceFile),'utf8');
  const opening='const html=`';const start=source.indexOf(opening)+opening.length;
  assert.ok(start>=opening.length,`HTML template absent: ${sourceFile}`);
  const end=source.indexOf('`;',start);assert.ok(end>start,`HTML template end absent: ${sourceFile}`);
  const template=source.slice(start,end);
  const marker=/\$\{bundle\.outputFiles\[0\]\.text\.replace\([\s\S]*?\)\}/g;
  assert.equal([...template.matchAll(marker)].length,1,`Expected one compiled-script slot: ${sourceFile}`);
  const bundle=await build({entryPoints:[path.join(packageRoot,entry)],bundle:true,write:false,format,platform:'browser'});
  const html=template.replace(marker,()=>bundle.outputFiles[0].text.replace(/<\/script/gi,'<\\/script'));
  assert.ok(!html.includes('${bundle.'),'Unexpanded source expression');
  await writeFile(path.join(output,`${entry.replace('.ts','')}.html`),html);
  return {html,source:sourceFile,entry,format,templateSha256:hash(template),htmlSha256:hash(html),
    method:'Actual authored HTML template extracted from source; only its existing compiled-script slot is substituted'};
}
const widget=await actualTemplate('probe.ts','widget.ts','iife');
const live=await actualTemplate('live-server.ts','live-widget.ts','esm');
const browser=await chromium.launch({headless:true,channel:'msedge'});
const browserVersion=browser.version();

async function hostPage(scenario:'widget-initialize-failure'|'live-actions',html:string){
  const context=await browser.newContext({viewport:{width:900,height:850},locale:'en-US',offline:true,serviceWorkers:'block'});
  await context.route('**/*',async route=>{blockedRequests.push({scenario,url:route.request().url()});await route.abort();});
  const page=await context.newPage();
  page.on('pageerror',error=>pageErrors.push({scenario,message:error.message}));
  page.on('console',message=>{
    pendingConsole.push((async()=>{
      const args=await Promise.all(message.args().map(arg=>arg.evaluate(value=>value instanceof Error
        ?{name:value.name,message:value.message}:value).catch(()=>'<unavailable diagnostic>')));
      const text=message.text();
      const expected=message.type()==='error'&&/^(Host connection failed|Probe input was rejected|UI probe action failed)/.test(text);
      consoleRecords.push({scenario,type:message.type(),text,args,expectedSyntheticDiagnostic:expected});
    })());
  });
  await page.exposeFunction('languageHostRpc',async(method:string,params:any)=>{
    rpcCalls.push({scenario,method,params});
    if(method==='ui/initialize'){
      if(scenario==='widget-initialize-failure')throw new Error(foreignFixtures.initialize);
      return {protocolVersion:params.protocolVersion,hostInfo:{name:'Local English language fixture',version:'1.0.0'},
        hostCapabilities:{serverTools:{},updateModelContext:{},message:{},downloadFile:{},openLinks:{}},
        hostContext:{theme:'light',displayMode:'inline',availableDisplayModes:['inline','fullscreen'],containerDimensions:{width:860,maxHeight:1200}}};
    }
    if(method==='tools/call'){
      if(params.arguments?.value===-1)return {isError:true,content:[{type:'text',text:foreignFixtures.invalid}]};
      return {structuredContent:{value:Number(params.arguments.value)+1,synthetic:true},content:[{type:'text',text:'Synthetic increment completed.'}]};
    }
    if(method==='ui/request-display-mode')throw new Error(foreignFixtures.action);
    if(['ui/update-model-context','ui/message','ui/open-link','ui/download-file'].includes(method))return {};
    throw new Error(`Unexpected local fixture method: ${method}`);
  });
  await page.setContent('<!doctype html><html lang="en"><head><title>Local language verification fixture</title></head><body style="margin:0"><iframe id="app" title="Local language verification fixture" sandbox="allow-scripts" style="display:block;width:100%;height:1200px;border:0"></iframe></body></html>');
  await page.evaluate(({html,initial})=>{
    const frame=document.getElementById('app') as HTMLIFrameElement;
    window.addEventListener('message',async event=>{
      if(event.source!==frame.contentWindow||event.data?.jsonrpc!=='2.0')return;
      const message=event.data;
      if(message.method==='ui/notifications/initialized'){
        if(initial)frame.contentWindow!.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:initial},'*');
        return;
      }
      if(message.id!==undefined){
        try{
          const result=await (window as any).languageHostRpc(message.method,message.params??{});
          frame.contentWindow!.postMessage({jsonrpc:'2.0',id:message.id,result},'*');
        }catch(error){
          frame.contentWindow!.postMessage({jsonrpc:'2.0',id:message.id,error:{code:-32603,message:(error as Error).message}},'*');
        }
      }
    });
    frame.srcdoc=html;
  },{html,initial:scenario==='live-actions'?{structuredContent:{value:7,synthetic:true},content:[{type:'text',text:'Synthetic initial value: 7.'}]}:null});
  return {page,context,frame:page.frameLocator('#app')};
}
async function snapshot(page:Page,name:string){
  const frame=page.frameLocator('#app');
  const text=await frame.locator('body').innerText();
  const accessible=await frame.locator('body').ariaSnapshot();
  const lang=await frame.locator('html').getAttribute('lang');
  const geometry=await frame.locator('body').evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth}));
  const leakage=Object.values(foreignFixtures).filter(value=>text.includes(value)||accessible.includes(value));
  states.push({name,lang,visibleText:text,accessibilitySnapshot:accessible,geometry,foreignPayloadLeakage:leakage});
  await writeFile(path.join(output,`${name}.txt`),text+'\n\nAccessibility snapshot:\n'+accessible+'\n');
  await page.screenshot({path:path.join(output,`${name}.png`),fullPage:true});
  check(`${name}:english-document-language`,lang==='en',lang);
  check(`${name}:foreign-source-not-visible-or-accessible`,leakage.length===0,leakage);
  return {text,accessible,geometry};
}

try{
  try{
    const {page,context,frame}=await hostPage('widget-initialize-failure',widget.html);
    try{
      await frame.getByText('Unable to connect to the host. Please retry.',{exact:true}).waitFor();
      check('widget:english-connection-recovery',await frame.locator('#error').innerText()==='Unable to connect to the host. Please retry.');
      await frame.getByRole('button',{name:'More options',exact:true}).click();
      check('widget:expanded-file-label',await frame.getByText('Attach a file',{exact:false}).isVisible());
      await page.setViewportSize({width:360,height:850});
      const state=await snapshot(page,'widget-failed-connection-expanded-narrow');
      check('widget:narrow-no-horizontal-overflow',state.geometry.scrollWidth<=state.geometry.clientWidth+1,state.geometry);
      check('widget:accessible-english-buttons',state.accessible.includes('Increment')&&state.accessible.includes('More options')&&state.accessible.includes('Attach a file'));
    }finally{await Promise.all(pendingConsole);await context.close();}
  }catch(error){caseErrors.push({scenario:'widget-initialize-failure',message:String(error)});}

  try{
    const {page,context,frame}=await hostPage('live-actions',live.html);
    try{
      await frame.getByText('Connected to actual host',{exact:true}).waitFor();
      await frame.locator('#value').filter({hasText:'7'}).waitFor();
      check('live:initial-value-seven',await frame.locator('#value').innerText()==='7');
      await snapshot(page,'live-initial-seven');
      await frame.getByRole('button',{name:'Increment locally via tool',exact:true}).click();
      await frame.locator('#value').filter({hasText:'8'}).waitFor();
      check('live:increment-seven-to-eight',await frame.locator('#value').innerText()==='8');
      await snapshot(page,'live-increment-eight');
      await frame.getByRole('button',{name:'Reject invalid input',exact:true}).click();
      await frame.locator('#result').filter({hasText:'The input was rejected. Check the value and try again.'}).waitFor();
      check('live:invalid-input-english-recovery-and-value',await frame.locator('#value').innerText()==='8'&&(await frame.locator('#result').innerText()).includes('"valuePreserved": 8'));
      await snapshot(page,'live-invalid-result-english-recovery');
      await frame.getByRole('button',{name:'Fullscreen',exact:true}).click();
      await frame.locator('#result').filter({hasText:'The requested action failed. Please retry.'}).waitFor();
      check('live:thrown-request-english-recovery-and-value',await frame.locator('#value').innerText()==='8'&&(await frame.locator('#result').innerText()).includes('"valuePreserved": 8'));
      await snapshot(page,'live-thrown-request-english-recovery');
      await frame.getByText('Negotiated host capabilities',{exact:true}).click();
      check('live:expanded-capabilities-visible',await frame.locator('#caps').isVisible()&&await frame.locator('#context').isVisible());
      await page.setViewportSize({width:360,height:850});
      const state=await snapshot(page,'live-expanded-capabilities-narrow');
      check('live:narrow-no-horizontal-overflow',state.geometry.scrollWidth<=state.geometry.clientWidth+1,state.geometry);
      check('live:accessible-english-controls-and-help',state.accessible.includes('Reject invalid input')&&state.accessible.includes('Negotiated host capabilities')&&state.accessible.includes('Download synthetic text'));
    }finally{await Promise.all(pendingConsole);await context.close();}
  }catch(error){caseErrors.push({scenario:'live-actions',message:String(error)});}
}finally{await browser.close();}

await Promise.all(pendingConsole);
const sourceAfter=Object.fromEntries(await Promise.all(sourceFiles.map(async file=>[file,hash(await readFile(path.join(packageRoot,file),'utf8'))])));
checks.push({id:'source-files-unchanged',passed:JSON.stringify(sourceHashes)===JSON.stringify(sourceAfter)});
checks.push({id:'no-unhandled-page-errors',passed:pageErrors.length===0,actual:pageErrors});
const expectedConsole=(consoleRecords as any[]).filter(row=>row.expectedSyntheticDiagnostic);
const unexpectedConsole=(consoleRecords as any[]).filter(row=>row.type==='error'&&!row.expectedSyntheticDiagnostic);
checks.push({id:'three-expected-synthetic-console-diagnostics',passed:expectedConsole.length===3,actual:expectedConsole.length});
checks.push({id:'no-unexpected-console-errors',passed:unexpectedConsole.length===0,actual:unexpectedConsole});
const report={passed:caseErrors.length===0&&checks.every(row=>row.passed),timestampUtc:new Date().toISOString(),
  layer:'real-browser-with-local-synthetic-MCP-Apps-host',browser:{channel:'msedge',version:browserVersion},
  dependencies:{playwright:'1.64.1',esbuild:'0.28.2'},network:'Browser context offline; all page network requests intercepted and aborted',
  providerRequests:0,assistantHostTestPerformed:false,sourceHashes,sourceAfter,
  templates:[{...widget,html:undefined},{...live,html:undefined}],quotedForeignSourceFixtures:foreignFixtures,
  checks,caseErrors,pageErrors,consoleRecords,blockedRequests,rpcCalls,states,
  limits:['Local synthetic host and browser only; no Claude, ChatGPT, Copilot or Codex assistant paint acceptance.',
    'English recovery strings, document language, accessible/visible copy and narrow layouts checked for these states only.',
    'Raw user data, protocol identifiers, external host locale, console diagnostics and historical evidence are not translated.',
    'No real consent, download delivery, external link navigation, screen-reader application, or representative user test.']};
await writeFile(path.join(output,'report.json'),JSON.stringify(report,null,2));
await writeFile(path.join(base,'latest.json'),JSON.stringify({run:runName,report:path.relative(base,path.join(output,'report.json')),passed:report.passed},null,2));
console.log(JSON.stringify({passed:report.passed,count:checks.length,caseErrors,pageErrors,expectedConsoleDiagnostics:expectedConsole.length,unexpectedConsoleErrors:unexpectedConsole.length,output},null,2));
if(!report.passed)process.exitCode=1;
