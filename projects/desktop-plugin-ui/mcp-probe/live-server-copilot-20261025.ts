// Run with the task package's tsx: node node_modules/tsx/dist/cli.mjs live-server-copilot-20261025.ts --stdio.
// Study-specific CS1 authored paint; preserves legacy tools/bridge behavior and user authority.
// Run with the task package's tsx: npx tsx live-server.ts [--stdio].
// Synthetic data only; exposes no filesystem, user account, secret, or command tools.
import {createServer} from 'node:http';
import {appendFile,mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {build} from 'esbuild';
import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {StreamableHTTPServerTransport} from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import {registerAppTool,registerAppResource,RESOURCE_MIME_TYPE} from '@modelcontextprotocol/ext-apps/server';
import {z} from 'zod';
const output=path.resolve(process.env.UI_PROBE_ARTIFACTS??path.resolve(import.meta.dirname,'../artifacts/capability-study-20261025/copilot/mcp-chat-live-v2'));await mkdir(output,{recursive:true});
const uri='ui://assistant-limits/probe-v1.html';
const bundle=await build({entryPoints:[path.resolve(import.meta.dirname,'live-widget.ts')],bundle:true,write:false,format:'esm',platform:'browser'});
const html=`<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>:root{color-scheme:light;--ui-background:#ffffff;--ui-ink:#333e48;--ui-primary:#9e1b32;--ui-primary-hover:#6d1222;--ui-soft:#e7e7e7;--ui-border:#696969;--ui-focus:#9e1b32}*{box-sizing:border-box}body{font:16px/1.5 'Open Sans',Arial,sans-serif;margin:0;padding:16px;background:var(--ui-background);color:var(--ui-ink)}main{max-width:880px;margin:0 auto;min-width:0}h1{font-size:22px;line-height:1.3;margin:0 0 8px}p{margin:8px 0}.hint{font-size:14px}.actions{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}button{font:inherit;min-height:44px;max-width:100%;padding:8px 12px;border:2px solid var(--ui-border);border-radius:4px;background:var(--ui-background);color:var(--ui-ink);cursor:pointer;overflow-wrap:anywhere}button[data-action=increment]{background:var(--ui-primary);border-color:var(--ui-primary);color:var(--ui-background);font-weight:700}button:not(:disabled):hover{border-color:var(--ui-primary-hover)}button[data-action=increment]:not(:disabled):hover{background:var(--ui-primary-hover);border-color:var(--ui-primary-hover)}button:disabled{background:var(--ui-soft);color:var(--ui-ink);border-color:var(--ui-border);border-style:dashed;cursor:default;opacity:1}button:focus-visible,summary:focus-visible{outline:3px solid var(--ui-focus);outline-offset:3px}#ready,#result{padding:10px;border:1px solid var(--ui-border);border-left:4px solid var(--ui-primary);border-radius:4px;background:var(--ui-soft);color:var(--ui-ink)}#result:empty{display:none}pre{font:13px/1.5 ui-monospace,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;max-height:240px;overflow:auto;padding:10px;border:1px solid var(--ui-border);border-radius:4px;background:var(--ui-soft);color:var(--ui-ink)}details{margin-top:16px}summary{min-height:44px;padding:8px 0;cursor:pointer;font-weight:700}@media(forced-colors:active){button,summary,#ready,#result,pre{forced-color-adjust:auto}button:focus-visible,summary:focus-visible{outline:3px solid Highlight}}</style></head><body><main><h1>Assistant UI limits probe</h1><p class="hint">These controls use synthetic data. Direct actions do not request a model reply. Unavailable host actions are disabled.</p><p id="ready" role="status">Waiting for host handshake</p><p>Value: <output id="value">0</output></p><section class="actions" aria-label="Probe actions"><button data-action="increment">Increment locally via tool</button><button data-action="invalid">Reject invalid input</button><button data-action="fullscreen">Fullscreen</button><button data-action="pip">Picture in picture</button><button data-action="context">Update model context only</button><button data-action="sandbox">Check sandbox</button><button data-action="download">Download synthetic text</button><button data-action="link">Open example.com</button></section><pre id="result" role="status" aria-live="polite"></pre><details><summary>Negotiated host capabilities</summary><pre id="caps"></pre><pre id="context"></pre></details></main><script type="module">${bundle.outputFiles[0].text.replace('Connected to actual host','Connected to host bridge').replace(/<\/script/gi,'<\\/script')}</script></body></html>`;
await writeFile(path.join(output,'view.html'),html);
const record=async(event:unknown)=>appendFile(path.join(output,'events.jsonl'),JSON.stringify({at:new Date().toISOString(),event})+'\n');
function makeServer(){
 const server=new McpServer({name:'assistant-ui-limits-probe',version:'1.0.0'});
 server.server.oninitialized=()=>void record({kind:'initialize',capabilities:server.server.getClientCapabilities(),client:server.server.getClientVersion()});
 registerAppResource(server,'assistant-ui-probe',uri,{},async()=>{await record({kind:'resource-read',uri});return {contents:[{uri,mimeType:RESOURCE_MIME_TYPE,text:html,_meta:{ui:{csp:{connectDomains:[],resourceDomains:[]},prefersBorder:true}}}]};});
 registerAppTool(server,'ui_limits_open',{title:'Open UI Limits Probe',description:'Show the synthetic interactive UI limits probe. No user data, account access, or side effects. Call once to open the UI.',inputSchema:{},annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},_meta:{ui:{resourceUri:uri}}},async()=>{await record({kind:'tool',name:'ui_limits_open'});return {structuredContent:{value:7,synthetic:true},content:[{type:'text',text:'Synthetic UI probe value: 7. The interactive view shows supported host controls.'}]};});
 registerAppTool(server,'ui_probe_increment',{description:'Increment the synthetic UI probe integer.',inputSchema:{value:z.number().int().min(0).max(99)},annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},_meta:{ui:{visibility:['app']}}},async({value})=>{await record({kind:'tool',name:'ui_probe_increment',value});return {structuredContent:{value:value+1,synthetic:true},content:[{type:'text',text:`Synthetic value: ${value+1}`}]};});
 return server;
}
if(process.argv.includes('--stdio')){const server=makeServer();await server.connect(new StdioServerTransport());}
else{
 const http=createServer(async(req,res)=>{
  if(req.url==='/health'){res.writeHead(200,{'content-type':'application/json'});res.end(JSON.stringify({service:'assistant-ui-limits-probe',synthetic:true}));return;}
  if(req.url!=='/mcp'){res.writeHead(404);res.end();return;}
  if(req.method!=='POST'){res.writeHead(405,{'Allow':'POST'});res.end();return;}
  const server=makeServer();const transport=new StreamableHTTPServerTransport({sessionIdGenerator:undefined,enableJsonResponse:true});
  try{const chunks:Buffer[]=[];for await(const chunk of req)chunks.push(Buffer.from(chunk));const body=JSON.parse(Buffer.concat(chunks).toString('utf8'));await record({kind:'rpc',method:body.method});await server.connect(transport);res.on('close',()=>{void transport.close();void server.close();});await transport.handleRequest(req,res,body);}
  catch(error){await record({kind:'server-error',message:String(error)});if(!res.headersSent)res.writeHead(500);res.end();}
 });http.listen(8796,'127.0.0.1',()=>{console.log('Synthetic UI probe: http://127.0.0.1:8796/mcp');});
}
