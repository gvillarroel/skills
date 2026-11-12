import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp,mkdir,writeFile } from "node:fs/promises";
import path from "node:path";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { configFromEnv,FILES,HERE,RenderStore,type RenderMetadata } from "../src/core.js";
import { createMcpServer } from "../src/server.js";
import { COMPACT_PREVIEW_SHIM,embeddedPreviewHtml } from "../src/preview.js";

test("embedded preview adds a bridge without changing the original native export",()=>{
  const original='<!doctype html><html><head><title>Native XY</title></head><body></body></html>';
  assert.equal(embeddedPreviewHtml(original).replace(COMPACT_PREVIEW_SHIM,""),original);
  assert.throws(()=>embeddedPreviewHtml("<svg/>"),/document head/);
});

test("app-private previews and exports preserve original bytes with capability and size limits",async()=>{
  const root=path.resolve(HERE,"../artifacts/chatgpt-unit-v0.3.1");await mkdir(root,{recursive:true});const directory=await mkdtemp(path.join(root,"xy-"));
  const config=configFromEnv({XY_RUNTIME_DIR:root});const store=new RenderStore(config);
  const metadata:RenderMetadata={schema_version:1,title:"Native XY",palette:"colorset1",width:960,height:540,factory:"chart",warnings:[],counts:{rows:3,marks:1},svg_compat_repairs:0,svg_bytes:0,png_bytes:0,files:{html:"chart.html",svg:"chart.svg",png:"chart.png",source:"chart.py",spec:"spec.json"}};
  const record={id:"a".repeat(32),key:"K".repeat(43),directory,spec:{preset:"line",colorset:"colorset1"},created:Date.now(),bytes:0,metadata};store.records.set(record.id,record);
  const originals={"chart.html":Buffer.from('<!doctype html><html><head></head><body>Original native chart</body></html>'),"chart.svg":Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"/>'),"chart.png":Buffer.from("89504e470d0a1a0a","hex"),"chart.py":Buffer.from("print('Native XY')\n"),"spec.json":Buffer.from('{"colorset":"colorset1"}')};
  for(const [name,data] of Object.entries(originals))await writeFile(path.join(directory,name),data);
  // Substitute only the expensive renderer; exercise the real MCP result and
  // capability-protected file reader against known byte-identical fixtures.
  store.render=async()=>record;
  const server=await createMcpServer(store);const client=new Client({name:"xy-embedded-boundaries",version:"0.3.1"});const [clientTransport,serverTransport]=InMemoryTransport.createLinkedPair();
  try{
    await Promise.all([client.connect(clientTransport),server.connect(serverTransport)]);
    const chart=await client.callTool({name:"xy_open_chart_app",arguments:{}}) as CallToolResult;assert.ok(!chart.isError);
    const native=chart._meta?.native_preview as {html:string;svg:string};assert.equal(native.html,originals["chart.html"].toString());assert.equal(native.svg,originals["chart.svg"].toString());
    assert.equal(chart.structuredContent?.native_preview,undefined);assert.equal(chart.content[0].type,"text");assert.deepEqual(chart.content,[{type:"text",text:"The chart is ready."}]);
    for(const [format,name] of Object.entries({html:"chart.html",svg:"chart.svg",png:"chart.png",source:"chart.py",spec:"spec.json"}) as [string,keyof typeof originals][]){
      const result=await client.callTool({name:"xy_get_chart_artifact",arguments:{render_id:record.id,render_key:record.key,format}}) as CallToolResult;assert.ok(!result.isError);
      const artifact=result._meta?.artifact as {name:string;mime_type:string;blob:string};assert.equal(artifact.name,name);assert.equal(artifact.mime_type,FILES[name]);assert.deepEqual(Buffer.from(artifact.blob,"base64"),originals[name]);assert.equal(result.structuredContent?.bytes,originals[name].length);assert.equal(result.structuredContent?.blob,undefined);
    }
    const bad=await client.callTool({name:"xy_get_chart_artifact",arguments:{render_id:record.id,render_key:"X".repeat(43),format:"png"}});assert.equal(bad.isError,true);
    await writeFile(path.join(directory,"chart.png"),Buffer.alloc(16*1024*1024+1));const oversized=await client.callTool({name:"xy_get_chart_artifact",arguments:{render_id:record.id,render_key:record.key,format:"png"}});assert.equal(oversized.isError,true);assert.match(JSON.stringify(oversized.content),/16 MiB/);
    await writeFile(path.join(directory,"chart.html"),Buffer.alloc(8*1024*1024+1));const hugePreview=await client.callTool({name:"xy_open_chart_app",arguments:{}});assert.equal(hugePreview.isError,true);assert.match(JSON.stringify(hugePreview.content),/8 MiB/);
  }finally{await client.close();await server.close();}
});
