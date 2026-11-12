// Start the production server with no node_modules in its ancestry.
import assert from "node:assert/strict";
import { mkdir,copyFile,writeFile } from "node:fs/promises";
import path from "node:path";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { HERE } from "../src/core.js";
const output=path.resolve(HERE,"../artifacts/chatgpt-bundled-v0.3.1");const copied=path.join(output,"extracted/chatgpt/dist");await mkdir(copied,{recursive:true});
await copyFile(path.join(process.env.XY_BUILD_DIR??path.join(HERE,"dist"),"server-bundled.js"),path.join(copied,"server-bundled.js"));await copyFile(path.join(process.env.XY_BUILD_DIR??path.join(HERE,"dist"),"widget.html"),path.join(copied,"widget.html"));
await writeFile(path.join(copied,"../package.json"),'{"type":"module"}\n');
const env=Object.fromEntries(Object.entries(process.env).filter((x):x is [string,string]=>typeof x[1]==="string"));
Object.assign(env,{HOST:"0.0.0.0",PORT:"invalid",XY_PUBLIC_BASE_URL:"https://unused.example/path",XY_MCP_BEARER_TOKEN:"unused-secret",XY_WIDGET_DOMAIN:"unused.example",XY_RUNTIME_DIR:path.join(output,"runtime")});delete env.OPENAI_API_KEY;delete env.ANTHROPIC_API_KEY;
const transport=new StdioClientTransport({command:process.execPath,args:[path.join(copied,"server-bundled.js"),"--stdio","--desktop"],env,stderr:"pipe"});
const client=new Client({name:"xy-bundled-stdio-test",version:"0.1.0"});
try {
  await client.connect(transport);const tools=await client.listTools();assert.equal(tools.tools.length,6);
  const starter=await client.callTool({name:"xy_open_chart_app",arguments:{}});assert.ok(!starter.isError,JSON.stringify(starter));assert.equal((starter.structuredContent as {palette:string}).palette,"colorset1");
  const origin=String(starter._meta?.artifact_origin);assert.match(origin,/^http:\/\/127\.0\.0\.1:\d+$/);assert.equal((await fetch(origin+"/mcp",{method:"POST"})).status,404);
  const capabilities=await client.callTool({name:"xy_capabilities",arguments:{}});assert.ok(!capabilities.isError,JSON.stringify(capabilities));
  for(const colorset of ["colorset1","colorset2"]) {
    const result=await client.callTool({name:"xy_render_chart",arguments:{spec_json:JSON.stringify({preset:"scatter",colorset,title:"Bundled stdio chart"})}});
    assert.ok(!result.isError,JSON.stringify(result));const out=result.structuredContent as {palette:string;downloads:{svg:string;png:string;html:string}};assert.equal(out.palette,colorset);
    const svg=await fetch(out.downloads.svg);assert.equal(svg.status,200);assert.match(await svg.text(),/<svg/);
    const png=Buffer.from(await (await fetch(out.downloads.png)).arrayBuffer());assert.equal(png.subarray(0,8).toString("hex"),"89504e470d0a1a0a");
    const html=await (await fetch(out.downloads.html)).text();assert.match(html,/Bundled stdio chart/);
  }
  const defaultResult=await client.callTool({name:"xy_render_chart",arguments:{spec_json:'{"preset":"scatter","title":"Fresh default after explicit Colorset 2"}'}});
  assert.ok(!defaultResult.isError,JSON.stringify(defaultResult));const defaultOutput=defaultResult.structuredContent as {palette:string;downloads:{spec:string}};assert.equal(defaultOutput.palette,"colorset1");
  const defaultSpec=await (await fetch(defaultOutput.downloads.spec)).json() as {colorset:string};assert.equal(defaultSpec.colorset,"colorset1");
  const report={pass:true,version:"0.3.1",transport:"desktop stdio",http_mcp_endpoint:false,api_key_required:false,public_endpoint_required:false,production_bundle:"server-bundled.js",external_node_modules:false,default_colorset:"colorset1",explicit_colorset2_then_new_omitted_colorset1:true,palettes:["colorset1","colorset2"],native_formats:["html","svg","png"],tool_count:tools.tools.length};
  await writeFile(path.join(output,"report.json"),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {await client.close();await transport.close();}
