// Run after building. This is a constrained protocol fixture, not an assistant
// client: block native child scripts and omit the downloadFile capability.
import assert from "node:assert/strict";
import { mkdir,readFile,writeFile } from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { HERE } from "../src/core.js";

const buildDir=path.resolve(process.env.XY_BUILD_DIR??path.join(HERE,"dist"));
const output=path.resolve(HERE,"../artifacts/chatgpt-fallbacks-v0.3.1");await mkdir(output,{recursive:true});
const env=Object.fromEntries(Object.entries(process.env).filter((value):value is [string,string]=>typeof value[1]==="string"));env.XY_RUNTIME_DIR=path.join(output,"runtime");delete env.OPENAI_API_KEY;delete env.ANTHROPIC_API_KEY;
const transport=new StdioClientTransport({command:process.execPath,args:[path.join(buildDir,"server-bundled.js"),"--stdio","--desktop"],env,stderr:"pipe"});
const client=new Client({name:"xy-host-fallback-fixture",version:"0.3.1"});
const browser=await chromium.launch({headless:true,channel:process.env.PLAYWRIGHT_CHANNEL??"msedge"});const page=await browser.newPage({viewport:{width:900,height:1000}});const calls:string[]=[],requests:string[]=[];
await page.route(/^https?:\/\//,async route=>{requests.push(route.request().url());await route.abort();});
try{
  await client.connect(transport);const initial=await client.callTool({name:"xy_open_chart_app",arguments:{}}) as CallToolResult;assert.ok(!initial.isError);
  let html=await readFile(path.join(buildDir,"widget.html"),"utf8");html=html.replace("<head>",`<head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-fixture'; style-src 'unsafe-inline'; img-src data:; frame-src about:; connect-src 'none'">`).replace("<script>",'<script nonce="fixture">');
  await page.exposeFunction("fallbackRpc",async(method:string,params:Record<string,unknown>)=>{calls.push(method);if(method==="ui/initialize")return {protocolVersion:params.protocolVersion,hostInfo:{name:"constrained-protocol-fixture",version:"0.3.1"},hostCapabilities:{serverTools:{}},hostContext:{theme:"light",displayMode:"inline",availableDisplayModes:["inline"]}};if(["tools/call","ui/download-file","ui/open-link","ui/message","ui/update-model-context","sampling/createMessage"].includes(method))throw Error(`Unexpected request: ${method}`);return {};});
  await page.setContent('<iframe id="hosted" sandbox="allow-scripts allow-downloads" style="width:100%;height:1800px;border:0"></iframe>');
  await page.evaluate(({html,initial})=>{const hosted=document.querySelector("iframe")!;window.addEventListener("message",async event=>{if(event.source!==hosted.contentWindow||event.data?.jsonrpc!=="2.0")return;const message=event.data;if(message.method==="ui/notifications/initialized"){hosted.contentWindow!.postMessage({jsonrpc:"2.0",method:"ui/notifications/tool-result",params:initial},"*");return;}if(message.id!==undefined){try{const result=await (window as unknown as {fallbackRpc:(method:string,params:unknown)=>Promise<unknown>}).fallbackRpc(message.method,message.params??{});hosted.contentWindow!.postMessage({jsonrpc:"2.0",id:message.id,result},"*");}catch(error){hosted.contentWindow!.postMessage({jsonrpc:"2.0",id:message.id,error:{code:-32603,message:String(error)}},"*");}}});hosted.srcdoc=html;},{html,initial});
  const widget=page.frameLocator("#hosted");await widget.locator("#save-image:not([disabled])").waitFor();assert.equal(await widget.locator("#expand").isVisible(),false);
  await widget.locator("#save-image").click();assert.match(await widget.locator("#error").innerText(),/does not support saving files/);assert.ok(!calls.includes("tools/call"));
  await widget.locator("#preview").waitFor({state:"visible",timeout:20000});assert.equal(await widget.locator("#view-select").inputValue(),"svg");assert.match(await widget.locator("#error").innerText(),/Interactive preview is unavailable.*Showing the chart image/);
  const image=await widget.locator("#preview").evaluate((value:HTMLImageElement)=>({width:value.naturalWidth,height:value.naturalHeight,source:value.src.slice(0,32)}));assert.ok(image.width>200&&image.height>100);assert.match(image.source,/^data:image\/svg\+xml/);assert.equal(await widget.locator("#save-image").isEnabled(),true);assert.deepEqual(requests,[]);
  await page.screenshot({path:path.join(output,"blocked-interaction-native-image.png"),fullPage:true});
  const report={pass:true,version:"0.3.1",evidence:"observed-working",scope:"constrained MCP Apps protocol fixture; actual assistant acceptance untested",blocked_child_scripts_show_original_svg:true,missing_download_capability_clear_error:true,no_export_tool_call_when_unsupported:true,no_browser_network:true,model_messages:0,model_context_updates:0,sampling_requests:0,image,methods:calls};await writeFile(path.join(output,"report.json"),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await page.close();await browser.close();await client.close();await transport.close();}
