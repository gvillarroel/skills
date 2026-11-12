// Run: npm ci --ignore-scripts, then npm run probe. Dependencies are in package.json.
// This uses real MCP/App SDKs and a synthetic protocol host, not Claude Desktop.
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {build} from 'esbuild';
import {chromium} from 'playwright';
import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {InMemoryTransport} from '@modelcontextprotocol/sdk/inMemory.js';
import {registerAppTool,registerAppResource,RESOURCE_MIME_TYPE} from '@modelcontextprotocol/ext-apps/server';
import {z} from 'zod';

const output=path.resolve(process.env.UI_PROBE_ARTIFACTS??'../artifacts/mcp-probe'); await mkdir(output,{recursive:true});
const checks:{id:string,pass:boolean,layer:string}[]=[];
function check(id:string,condition:unknown,layer='browser-fixture'){assert.ok(condition,id);checks.push({id,pass:true,layer});}
const uri='ui://desktop-probe/v1.html';
const bundle=await build({entryPoints:['widget.ts'],bundle:true,write:false,format:'iife',platform:'browser'});
const html=`<!doctype html><html lang="en"><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'"><style>body{font:16px system-ui;margin:0;padding:16px;color:#222;background:#fff}button,input{min-height:44px;max-width:100%}main{max-width:100%}#options{padding-top:8px}[data-theme=dark] body{background:#222;color:#eee}</style></head><body><main><h1>Review result</h1><p>Value: <output id="value">0</output></p><button id="increment">Increment</button> <button id="details">More options</button><div id="options" hidden><label>Attach a file <input id="upload" type="file"></label></div><p id="error" role="status"></p><span id="ready" hidden>waiting</span></main><script>${bundle.outputFiles[0].text.replace(/<\/script/gi,'<\\/script')}</script></body></html>`;
const server=new McpServer({name:'desktop-ui-probe',version:'1.0.0'});
registerAppResource(server,'probe',uri,{},async()=>({contents:[{uri,mimeType:RESOURCE_MIME_TYPE,text:html,_meta:{ui:{csp:{connectDomains:[],resourceDomains:[]}}}}]}));
registerAppTool(server,'increment',{description:'Increment a review count',inputSchema:{value:z.number().int().nonnegative()},_meta:{ui:{resourceUri:uri}}},async({value})=>({structuredContent:{value:value+1},content:[{type:'text',text:`Count: ${value+1}`}]}));
const [clientTransport,serverTransport]=InMemoryTransport.createLinkedPair();
await server.connect(serverTransport);
const client=new Client({name:'probe-client',version:'1.0.0'});await client.connect(clientTransport);
try {
  const tools=await client.listTools();
  check('tool-resource-link',(tools.tools[0]._meta?.ui as any).resourceUri===uri,'real-mcp-sdk');
  const resource=await client.readResource({uri});
  check('resource-mime',resource.contents[0].mimeType==='text/html;profile=mcp-app','real-mcp-sdk');
  const initial=await client.callTool({name:'increment',arguments:{value:6}});
  check('headless-text-and-data',initial.structuredContent?.value===7&&initial.content.length===1,'real-mcp-sdk');
  const invalid=await client.callTool({name:'increment',arguments:{value:-1}});
  check('invalid-input-rejected',invalid.isError===true,'real-mcp-sdk');
  const hashes=['https://example.com/mcp','https://example.com/mcp/'].map(url=>createHash('sha256').update(url).digest('hex').slice(0,32)+'.claudemcpcontent.com');
  check('domain-exact-url-hash',hashes[0]==='c3d80a4ed901ee05b21755a88273b4a4.claudemcpcontent.com'&&hashes[0]!==hashes[1],'node-computation');
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  const browserVersion=browser.version();
  try {
    for(const capabilities of [true,false]) {
      const page=await browser.newPage({viewport:{width:900,height:650}});
      const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
      const calls:{method:string,params:any}[]=[];let rejectNext=false;
      await page.exposeFunction('hostRpc',async(method:string,params:any)=>{
        calls.push({method,params});
        if(method==='ui/initialize')return {protocolVersion:params.protocolVersion,hostInfo:{name:'research-fixture',version:'1.0.0'},hostCapabilities:{serverTools:{},updateModelContext:{},message:{},...(capabilities?{downloadFile:{},openLinks:{}}:{})},hostContext:{theme:'light',displayMode:'inline',availableDisplayModes:['inline','fullscreen'],containerDimensions:{width:860,maxHeight:1000}}};
        if(method==='tools/call') {
          if(rejectNext){rejectNext=false;return {isError:true,content:[{type:'text',text:'Controlled rejection'}]};}
          return client.callTool(params);
        }
        if(method==='ui/request-display-mode')return {mode:params.mode==='fullscreen'?'fullscreen':'inline'};
        if(['ui/download-file','ui/open-link'].includes(method)&&!capabilities)throw new Error('Host does not support this capability');
        if(['ui/download-file','ui/open-link','ui/message','ui/update-model-context'].includes(method))return {};
        throw new Error(`Unimplemented fixture method ${method}`);
      });
      await page.setContent('<!doctype html><html lang="en"><body style="margin:0"><p id="private">Host content</p><iframe id="app" title="Research protocol host" sandbox="allow-scripts" style="width:100%;height:500px;border:0"></iframe></body></html>');
      await page.evaluate(({html,initial})=>{
        const frame=document.getElementById('app') as HTMLIFrameElement;
        window.addEventListener('message',async event=>{
          if(event.source!==frame.contentWindow||event.data?.jsonrpc!=='2.0')return;
          const message=event.data;
          if(message.method==='ui/notifications/initialized') {
            frame.contentWindow!.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:initial},'*');return;
          }
          if(message.id!==undefined) {
            try {const result=await (window as any).hostRpc(message.method,message.params??{});frame.contentWindow!.postMessage({jsonrpc:'2.0',id:message.id,result},'*');}
            catch(error){frame.contentWindow!.postMessage({jsonrpc:'2.0',id:message.id,error:{code:-32601,message:String(error)}},'*');}
          }
        });frame.srcdoc=html;
      },{html,initial});
      const frame=page.frameLocator('#app');await frame.locator('#ready').waitFor({state:'attached'});
      await frame.locator('#value').filter({hasText:'7'}).waitFor();
      const run=async(operation:string)=>frame.locator('body').evaluate(async(_,op)=>{
        try{return {ok:true,value:await (window as any).probeRun(op)};}catch(error){return {ok:false,error:String(error)};}
      },operation);
      if(capabilities) {
        check('authored-document-language-en',await frame.locator('html').getAttribute('lang')==='en');
        check('handshake-result-delivery',await frame.locator('#value').innerText()==='7');
        await frame.locator('#increment').click();await frame.locator('#value').filter({hasText:'8'}).waitFor();
        check('interactive-server-tool',true);
        rejectNext=true;await frame.locator('#increment').click();await frame.locator('#error').filter({hasText:'Tool rejected'}).waitFor();
        check('error-preserves-result',await frame.locator('#value').innerText()==='8');
        check('model-context',(await run('context')).ok);
        check('followup-request',(await run('message')).ok);
        check('fullscreen-return',(await run('fullscreen')).value?.mode==='fullscreen');
        check('pip-denied-return-respected',(await run('pip')).value?.mode==='inline');
        check('host-open-link',(await run('link')).ok);
        check('host-download',(await run('download')).ok);
        const unknown=await run('unknown-tool');
        check('unknown-tool-rejected',!unknown.ok||unknown.value?.isError===true);
        check('parent-dom-blocked',(await run('parent-dom')).value==='SecurityError');
        check('file-path-injection-blocked',(await run('file-write')).value==='InvalidStateError');
        check('csp-network-blocked',(await run('fetch')).value==='blocked');
        await page.evaluate(()=>{(document.getElementById('app') as HTMLIFrameElement).contentWindow!.postMessage({jsonrpc:'2.0',method:'ui/notifications/host-context-changed',params:{theme:'dark'}},'*');});
        await frame.locator('html[data-theme="dark"]').waitFor();check('theme-update',true);
        await frame.locator('#details').focus();await page.keyboard.press('Enter');
        check('keyboard-disclosure',await frame.locator('#upload').isVisible());
        await writeFile(path.join(output,'authored-copy.json'),JSON.stringify({documentLanguage:await frame.locator('html').getAttribute('lang'),visibleText:await frame.locator('body').innerText(),accessibleTree:await frame.locator('body').ariaSnapshot(),scope:'Synthetic browser fixture; host and user source records are separate.'},null,2));
        await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
        await page.setViewportSize({width:360,height:650});
        const geometry=await frame.locator('body').evaluate(()=>({scroll:document.documentElement.scrollWidth,width:document.documentElement.clientWidth,targets:[...document.querySelectorAll('button')].map(x=>x.getBoundingClientRect().height)}));
        check('responsive-360',geometry.scroll<=geometry.width+1&&geometry.targets.every(h=>h>=44));
        await page.screenshot({path:path.join(output,'narrow.png'),fullPage:true});
      } else {
        const download=await run('download');check('absent-download-host-rejected',!download.ok&&/capab|support/i.test(download.error??''));
        check('sdk-method-existence-not-capability',calls.some(call=>call.method==='ui/download-file'));
      }
      check(`no-unhandled-errors-${capabilities}`,errors.length===0);
      await writeFile(path.join(output,`calls-${capabilities}.json`),JSON.stringify(calls,null,2));
      await page.close();
    }
  } finally {await browser.close();}
  await writeFile(path.join(output,'report.json'),JSON.stringify({timestampUtc:new Date().toISOString(),host:'Synthetic sandboxed protocol fixture; not Claude Desktop',browser:{channel:'msedge',version:browserVersion,playwright:'1.64.1'},node:process.version,sdk:{mcp:'1.32.1',apps:'1.7.5'},pass:true,count:checks.length,checks},null,2));
  console.log(JSON.stringify({pass:true,count:checks.length,output}));
} finally {await client.close();await server.close();}
