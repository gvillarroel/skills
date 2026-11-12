import test from "node:test";
import assert from "node:assert/strict";
import { once } from "node:events";
import { mkdtemp,writeFile,readFile,mkdir } from "node:fs/promises";
import path from "node:path";
import { tmpdir } from "node:os";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { configFromEnv,parseSpec,RenderStore,HERE } from "../src/core.js";
import { startHttp,UI_URI } from "../src/server.js";

const artifacts=path.resolve(HERE,"../artifacts/chatgpt-unit");
test("input boundary rejects unsupported size, depth, non-object and reserved keys",()=>{
  assert.deepEqual(parseSpec('{"preset":"line","colorset":"colorset2"}'),{preset:"line",colorset:"colorset2"});
  assert.deepEqual(parseSpec('{"preset":"line"}'),{preset:"line",colorset:"colorset1"});
  assert.equal(parseSpec('{"preset":"scatter","colorset":null}').colorset,null);
  for(const text of ['[]','null','[1,2]','{"__proto__":{"x":1}}','{"constructor":1}',JSON.stringify({title:"x".repeat(1025)}),JSON.stringify({data:Array(10001).fill(0)}),'{"x":1e999}'])assert.throws(()=>parseSpec(text));
  let obj:unknown=1;for(let i=0;i<14;i++)obj={x:obj};assert.throws(()=>parseSpec(JSON.stringify(obj)));
});
test("configuration requires intentional public exposure",()=>{
  assert.throws(()=>configFromEnv({HOST:"0.0.0.0"}));
  assert.throws(()=>configFromEnv({XY_PUBLIC_BASE_URL:"https://example.com/path"}));
  assert.throws(()=>configFromEnv({PORT:"not-a-number"}));
  assert.equal(configFromEnv({HOST:"0.0.0.0",XY_MCP_BEARER_TOKEN:"test-secret"}).bind,"0.0.0.0");
});
test("desktop configuration ignores inherited public hosting and keeps writable temp storage",()=>{
  const config=configFromEnv({HOST:"0.0.0.0",PORT:"invalid",XY_PUBLIC_BASE_URL:"https://invalid.example/path",XY_MCP_BEARER_TOKEN:"inherited-secret",XY_WIDGET_DOMAIN:"inherited.example"},{desktop:true});
  assert.equal(config.bind,"127.0.0.1");assert.equal(config.port,0);assert.equal(config.baseUrl,"http://127.0.0.1:0");
  assert.equal(config.bearer,undefined);assert.equal(config.widgetDomain,undefined);assert.equal(config.runtimeDir,path.resolve(tmpdir(),"reflex-xy"));
  assert.equal(configFromEnv({XY_RUNTIME_DIR:artifacts},{desktop:true}).runtimeDir,artifacts);
});
test("desktop asset listener has no HTTP MCP transport",async()=>{
  const service=await startHttp(configFromEnv({XY_RUNTIME_DIR:artifacts},{desktop:true}),{assetsOnly:true});
  try {
    const origin=service.store.config.baseUrl;
    const health=await (await fetch(origin)).json() as {mcp:unknown;transport:string;authentication:string};
    assert.equal(health.mcp,null);assert.equal(health.transport,"stdio");assert.equal(health.authentication,"none");
    for(const method of ["GET","POST"])assert.equal((await fetch(origin+"/mcp",{method})).status,404);
  } finally {service.http.close();await once(service.http,"close");}
});
test("MCP HTTP advertises UI, keeps capability tools app-visible and refuses public file access",async()=>{
  const config=configFromEnv({PORT:"0",XY_RUNTIME_DIR:artifacts,XY_MCP_BEARER_TOKEN:"test-secret"});
  const service=await startHttp(config);
  const client=new Client({name:"xy-boundary-test",version:"0.1.0"});
  try {
    assert.equal((await fetch(service.url,{method:"POST",headers:{"content-type":"application/json"},body:"{}"})).status,401);
    await client.connect(new StreamableHTTPClientTransport(new URL(service.url),{requestInit:{headers:{Authorization:"Bearer test-secret"}}}));
    const tools=await client.listTools();assert.equal(tools.tools.length,6);
    const render=tools.tools.find(t=>t.name==="xy_render_chart")!;assert.equal((render._meta?.ui as {resourceUri:string}).resourceUri,UI_URI);assert.equal(render.annotations?.readOnlyHint,true);assert.equal(render.annotations?.idempotentHint,false);
    const recolor=tools.tools.find(t=>t.name==="xy_recolor_chart")!;assert.deepEqual((recolor._meta?.ui as {visibility:string[]}).visibility,["app"]);
    const artifact=tools.tools.find(t=>t.name==="xy_get_chart_artifact")!;assert.deepEqual((artifact._meta?.ui as {visibility:string[]}).visibility,["app"]);
    const opener=tools.tools.find(t=>t.name==="xy_open_chart_app")!;assert.deepEqual((opener._meta?.ui as {visibility:string[]}).visibility,["app"]);assert.deepEqual(opener._meta?.["openai/ui"],{entrypoints:[{type:"global"},{type:"thread"}]});
    const resource=await client.readResource({uri:UI_URI});assert.ok('text' in resource.contents[0]);assert.match(resource.contents[0].text,/Save image/);assert.match(resource.contents[0].text,/More options/);assert.equal(resource.contents[0].mimeType,"text/html;profile=mcp-app");
    const csp=(resource.contents[0]._meta?.ui as {csp:{frameDomains:string[];resourceDomains:string[];connectDomains:string[]}}).csp;assert.deepEqual(csp.frameDomains,["about:"]);assert.deepEqual(csp.resourceDomains,[]);assert.deepEqual(csp.connectDomains,[]);
    const bad=await client.callTool({name:"xy_render_chart",arguments:{spec_json:'{"__proto__":1}'}});assert.equal(bad.isError,true);
    const unauthorized=await client.callTool({name:"xy_recolor_chart",arguments:{render_id:"0".repeat(32),render_key:"A".repeat(43),colorset:"colorset2"}});assert.equal(unauthorized.isError,true);
    const deniedExport=await client.callTool({name:"xy_get_chart_artifact",arguments:{render_id:"0".repeat(32),render_key:"A".repeat(43),format:"png"}});assert.equal(deniedExport.isError,true);
    for(const route of ["/artifacts/../../package.json","/artifacts/"+"0".repeat(32)+"/chart.html?token=no","/package.json","/.env"])assert.equal((await fetch(config.baseUrl+route)).status,404);
    const compressed=await fetch(service.url,{method:"POST",headers:{Authorization:"Bearer test-secret","content-type":"application/json","content-encoding":"gzip"},body:"{}"});assert.equal(compressed.status,400);
    const cross=await fetch(service.url,{method:"POST",headers:{Authorization:"Bearer test-secret","content-type":"application/json",Origin:"https://attacker.example"},body:"{}"});assert.equal(cross.status,403);
    const huge=await fetch(service.url,{method:"POST",headers:{Authorization:"Bearer test-secret","content-type":"application/json"},body:" ".repeat(262145)});assert.equal(huge.status,400);
  } finally {await client.close();service.http.close();await once(service.http,"close");}
});
test("artifact capabilities are isolated, expire, and cannot traverse",async()=>{
  await mkdir(artifacts,{recursive:true});const root=await mkdtemp(path.join(artifacts,"store-"));const dir=await mkdtemp(path.join(root,"xy-"));await writeFile(path.join(dir,"chart.svg"),"<svg/>");
  const config=configFromEnv({XY_RUNTIME_DIR:root});config.ttlMs=10000;
  const store=new RenderStore(config);const rec={id:"a".repeat(32),key:"K".repeat(43),directory:dir,spec:{preset:"line"},created:Date.now(),bytes:6,metadata:{} as never};store.records.set(rec.id,rec);
  assert.equal(await store.read(rec.id,"wrong","chart.svg"),undefined);assert.equal(await store.read(rec.id,rec.key,"../package.json"),undefined);
  assert.equal((await store.read(rec.id,rec.key,"chart.svg"))?.data.toString(),"<svg/>");
  rec.created=Date.now()-20000;assert.equal(store.get(rec.id,rec.key),undefined);await store.prune();assert.equal(store.records.size,0);await assert.rejects(readFile(path.join(dir,"chart.svg")));
});
