// Run after npm run build. Uses the real Python renderer plus a protocol host
// fixture; it does not establish acceptance by the actual ChatGPT client.
import assert from "node:assert/strict";
import { once } from "node:events";
import { mkdir,readFile,writeFile } from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { CreateMessageRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { configFromEnv,HERE } from "../src/core.js";
import { startHttp,UI_URI,COMPACT_PREVIEW_SHIM } from "../src/server.js";

const desktop=process.argv.includes("--desktop");
const output=path.resolve(HERE,`../artifacts/chatgpt-${desktop?"desktop":"browser"}-v0.3.1`);await mkdir(output,{recursive:true});
const buildDir=path.resolve(process.env.XY_BUILD_DIR??path.join(HERE,"dist"));
const config=configFromEnv({...process.env,PORT:"0",XY_RUNTIME_DIR:path.join(output,"runtime")},{desktop});
const service=desktop?undefined:await startHttp(config);
const client=new Client({name:"xy-native-browser-test",version:"0.3.1"},{capabilities:{sampling:{}}});
let samplingCalls=0;client.setRequestHandler(CreateMessageRequestSchema,async()=>{samplingCalls++;return {role:"assistant",content:{type:"text",text:"Unexpected fixture sampling"},model:"fixture",stopReason:"endTurn"};});
const childEnv=Object.fromEntries(Object.entries(process.env).filter((x):x is [string,string]=>typeof x[1]==="string"));
Object.assign(childEnv,{HOST:"0.0.0.0",PORT:"invalid",XY_PUBLIC_BASE_URL:"https://unused.example/path",XY_MCP_BEARER_TOKEN:"inherited-unused-secret",XY_WIDGET_DOMAIN:"unused.example",XY_RUNTIME_DIR:config.runtimeDir});
for(const name of ["OPENAI_API_KEY","ANTHROPIC_API_KEY"])delete childEnv[name];
const desktopTransport=desktop?new StdioClientTransport({command:process.execPath,args:[path.join(buildDir,"server-bundled.js"),"--stdio","--desktop"],env:childEnv,stderr:"pipe"}):undefined;
const browser=await chromium.launch({headless:true,channel:process.env.PLAYWRIGHT_CHANNEL??"msedge"});
const page=await browser.newPage({viewport:{width:1040,height:1000}});
const errors:string[]=[];page.on("pageerror",error=>errors.push(error.message));
const consoleMessages:string[]=[];page.on("console",entry=>{if(entry.type()==="error"||entry.type()==="warning")consoleMessages.push(entry.text());});
const calls:{method:string;params:unknown}[]=[];
const blockedBrowserRequests:string[]=[],downloaded:Record<string,Buffer>={};let nextDownload:{name:string;blob:string}|undefined;
await page.route(/^https?:\/\//,async route=>{blockedBrowserRequests.push(route.request().url());await route.abort();});
let rejectNextPalette=true;
try {
  await client.connect(desktopTransport??new StreamableHTTPClientTransport(new URL(service!.url),config.bearer?{requestInit:{headers:{Authorization:`Bearer ${config.bearer}`}}}:{}));
  const explicit=await client.callTool({name:"xy_render_chart",arguments:{spec_json:JSON.stringify({preset:"line",colorset:"colorset2",title:"Explicit Colorset 2 before a new default chart"})}}) as CallToolResult;
  assert.ok(!explicit.isError,JSON.stringify(explicit));assert.equal(explicit.structuredContent?.palette,"colorset2");
  const initial=await client.callTool(desktop?{name:"xy_open_chart_app",arguments:{}}:{name:"xy_render_chart",arguments:{spec_json:JSON.stringify({version:1,factory:"chart",title:"Weekly activity",description:"Sample data",marks:[{kind:"line",args:[[1,2,3,4,5,6],[3,5,4,7,6,8]],kwargs:{color:"$ink",width:2}}],components:[{kind:"x_axis",kwargs:{label:"Week"}},{kind:"y_axis",kwargs:{label:"Completed tasks"}}]})}}) as CallToolResult;
  assert.ok(!initial.isError,JSON.stringify(initial));
  assert.equal(initial.structuredContent?.palette,"colorset1");
  if(desktop){const origin=String(initial._meta?.artifact_origin);assert.match(origin,/^http:\/\/127\.0\.0\.1:\d+$/);assert.equal((await fetch(origin+"/mcp",{method:"POST"})).status,404);const health=await (await fetch(origin)).json() as {mcp:unknown;transport:string};assert.equal(health.mcp,null);assert.equal(health.transport,"stdio");}
  const initialDownloads=initial.structuredContent?.downloads as {spec:string};const actualSpec=await (await fetch(initialDownloads.spec)).json() as {colorset:string};assert.equal(actualSpec.colorset,"colorset1");
  const tools=await client.listTools();const opener=tools.tools.find(t=>t.name==="xy_open_chart_app")!;assert.deepEqual((opener._meta?.ui as {visibility:string[]}).visibility,["app"]);assert.deepEqual((opener._meta?.["openai/ui"] as {entrypoints:unknown[]}).entrypoints,[{type:"global"},{type:"thread"}]);
  const resource=await client.readResource({uri:UI_URI});assert.ok('text' in resource.contents[0]);const html=resource.contents[0].text;assert.equal((resource.contents[0]._meta?.ui as {domain?:string}).domain,undefined);
  const paletteContract=JSON.parse(await readFile(path.join(config.skillDir,"assets/palettes/colorsets.json"),"utf8")) as {colorsets:{colorset1:{allowed:string[]}}};
  const css=/<style>([\s\S]*?)<\/style>/.exec(html)?.[1]??"";assert.ok(css.length>100);
  const authoredColors=[...new Set((css.match(/#[a-f0-9]{3,8}\b/gi)??[]).map(color=>color.toLowerCase()))].sort();
  for(const color of authoredColors)assert.ok(paletteContract.colorsets.colorset1.allowed.includes(color),`Widget fallback color ${color} is outside canonical Colorset 1.`);
  await page.exposeFunction("hostRpc",async(method:string,params:Record<string,unknown>)=>{
    calls.push({method,params});
    if(method==="ui/initialize")return {protocolVersion:params.protocolVersion,hostInfo:{name:"independent-protocol-fixture",version:"0.1.0"},hostCapabilities:{serverTools:{},downloadFile:{},openLinks:{}},hostContext:{theme:"light",displayMode:"inline",availableDisplayModes:["inline","fullscreen"],containerDimensions:{width:1000,maxHeight:2000}}};
    if(method==="tools/call") {if(params.name==="xy_recolor_chart"&&rejectNextPalette){rejectNextPalette=false;await new Promise(resolve=>setTimeout(resolve,500));return {isError:true,content:[{type:"text",text:"Intentional host fixture renderer failure."}]};}const response=await client.callTool(params as {name:string;arguments?:Record<string,unknown>});if(params.name==="xy_get_chart_artifact")nextDownload=response._meta?.artifact as {name:string;blob:string};return response;}
    if(method==="ui/download-file") {
      const item=(params.contents as {type:string;resource:{uri:string;blob:string;mimeType:string}}[])[0];assert.equal(item.type,"resource");assert.ok(nextDownload);assert.equal(item.resource.uri,`file:///${nextDownload.name}`);assert.equal(item.resource.blob,nextDownload.blob);const bytes=Buffer.from(item.resource.blob,"base64");assert.ok(bytes.length>0);downloaded[nextDownload.name]=bytes;if(nextDownload.name==="chart.png")assert.equal(bytes.subarray(0,8).toString("hex"),"89504e470d0a1a0a");return {};
    }
    if(method==="ui/open-link")return {};
    if(method==="ui/request-display-mode")return {mode:"fullscreen"};
    if(["ui/update-model-context","ui/message","sampling/createMessage"].includes(method))throw Error("A deterministic chart control attempted to contact the model.");
    return {};
  });
  await page.setContent('<!doctype html><html><body style="margin:0"><iframe id="hosted" title="MCP Apps protocol fixture" sandbox="allow-scripts allow-downloads" style="width:100%;height:1800px;border:0"></iframe></body></html>');
  await page.evaluate(({html,initial})=>{
    const hosted=document.getElementById("hosted") as HTMLIFrameElement;
    window.addEventListener("message",async event=>{
      if(event.source!==hosted.contentWindow||event.data?.jsonrpc!=="2.0")return;
      const msg=event.data;
      if(msg.method==="ui/notifications/size-changed" && typeof msg.params?.height==="number")hosted.style.height=`${Math.max(200,Math.min(1800,msg.params.height))}px`;
      if(msg.method==="ui/notifications/initialized") {hosted.contentWindow!.postMessage({jsonrpc:"2.0",method:"ui/notifications/tool-result",params:initial},"*");return;}
      if(msg.id!==undefined) {
        try{const result=await (window as unknown as {hostRpc:(method:string,params:unknown)=>Promise<unknown>}).hostRpc(msg.method,msg.params??{});hosted.contentWindow!.postMessage({jsonrpc:"2.0",id:msg.id,result},"*");}
        catch(error){hosted.contentWindow!.postMessage({jsonrpc:"2.0",id:msg.id,error:{code:-32603,message:String(error)}},"*");}
      } else if(msg.method)void (window as unknown as {hostRpc:(method:string,params:unknown)=>Promise<unknown>}).hostRpc(msg.method,msg.params??{});
    });hosted.srcdoc=html.replace("<head>",`<head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; connect-src 'none'; worker-src blob:; frame-src about:; base-uri 'none'; form-action 'none'">`);
  },{html,initial});
  const widget=page.frameLocator("#hosted");
  await widget.locator('#save-image:not([disabled])').waitFor({timeout:20000});
  assert.equal(await widget.locator("#palette-select").inputValue(),"colorset1");
  assert.equal(await widget.locator("#more-summary").getAttribute("aria-expanded"),"false");
  assert.equal(await widget.locator("#status").isVisible(),false);
  assert.equal(await widget.locator("#palette-select").isVisible(),false);
  const initialActions=await widget.locator("button:visible,summary:visible,select:visible,input:visible").evaluateAll(elements=>elements.map(e=>(e.textContent??"").trim()));
  assert.ok(initialActions.length<=3,JSON.stringify(initialActions));
  const chrome=await widget.locator("main").evaluate(()=>({
    background:getComputedStyle(document.documentElement).backgroundColor,
    foreground:getComputedStyle(document.documentElement).color,
    activeBackground:getComputedStyle(document.getElementById("save-image")!).backgroundColor,
    activeForeground:getComputedStyle(document.getElementById("save-image")!).color,
    border:getComputedStyle(document.getElementById("more-summary")!).borderTopColor,
  }));
  assert.deepEqual(chrome,{background:"rgb(247, 247, 247)",foreground:"rgb(51, 62, 72)",activeBackground:"rgb(158, 27, 50)",activeForeground:"rgb(255, 255, 255)",border:"rgb(130, 130, 130)"});
  await widget.locator("#chart").waitFor({state:"visible"});
  await widget.frameLocator("#chart").locator("canvas").first().waitFor({timeout:30000});
  const paints=await widget.frameLocator("#chart").locator("canvas").first().evaluate((canvas:HTMLCanvasElement)=>({width:canvas.width,height:canvas.height}));assert.ok(paints.width>200&&paints.height>100);
  await page.waitForTimeout(1000);
  assert.equal(await widget.locator("#chart").getAttribute("src"),null);
  const originalHtml=await (await fetch((initial.structuredContent?.downloads as {html:string}).html)).text();assert.doesNotMatch(originalHtml,/data-xy-compact-preview/);
  const compactHtml=(await widget.locator("#chart").getAttribute("srcdoc"))!;assert.match(compactHtml,/data-xy-compact-preview/);assert.equal(compactHtml.replace(COMPACT_PREVIEW_SHIM,""),originalHtml);
  await page.screenshot({path:path.join(output,"colorset1-desktop.png"),fullPage:true});
  await widget.locator("main").screenshot({path:path.join(output,"initial-desktop.png")});
  await widget.locator("#save-image").click();
  const triggerBefore=await widget.locator("#more-summary").boundingBox();await widget.locator("#more-summary").focus();await page.keyboard.press("Enter");assert.equal(await widget.locator("#more-summary").getAttribute("aria-expanded"),"true");assert.deepEqual(await widget.locator("#more-summary").boundingBox(),triggerBefore);await page.waitForTimeout(300);await page.screenshot({path:path.join(output,"colorset1-options-open-desktop.png"),fullPage:true});await widget.locator("main").screenshot({path:path.join(output,"expanded-desktop.png")});
  await page.keyboard.press("Escape");assert.equal(await widget.locator("#more-summary").getAttribute("aria-expanded"),"false");assert.equal(await widget.locator("#more-summary").evaluate(el=>el===document.activeElement),true);
  await page.keyboard.press("Space");assert.equal(await widget.locator("#palette-select").isVisible(),true);
  await widget.locator("#palette-select").focus();await widget.locator("#palette-select").selectOption("colorset2");
  assert.equal(await widget.locator("#save-image").isEnabled(),true);await widget.locator("#save-image").click();
  await widget.locator("#error").waitFor({state:"visible"});assert.match(await widget.locator("#error").innerText(),/Intentional host fixture/);assert.equal(await widget.locator("#palette-select").inputValue(),"colorset1");assert.equal(await widget.locator("#save-image").isEnabled(),true);assert.equal(await widget.locator("#save-image").evaluate(el=>el===document.activeElement),true);
  await widget.locator("#palette-select").focus();await widget.locator("#palette-select").selectOption("colorset2");
  await widget.locator("#palette-select").evaluate(async(el:HTMLSelectElement)=>{const end=Date.now()+100000;while(el.value!=="colorset2"){if(Date.now()>end)throw Error("Palette update timed out");await new Promise(resolve=>setTimeout(resolve,50));}});
  assert.equal(await widget.locator("#palette-select").evaluate(el=>el===document.activeElement),true);
  assert.equal(await widget.locator("#more-summary").getAttribute("aria-expanded"),"true");
  await widget.frameLocator("#chart").locator("canvas").first().waitFor({timeout:30000});
  await page.waitForTimeout(1000);await page.screenshot({path:path.join(output,"colorset2-desktop.png"),fullPage:true});
  const beforeToolsUrl=await widget.locator("#chart").getAttribute("srcdoc");
  await widget.frameLocator("#chart").locator("body").evaluate(()=>{(window as unknown as {noNavigationProbe:string}).noNavigationProbe="preserve-frame";});
  await widget.locator("#chart-tools").check();await page.waitForTimeout(100);assert.equal(await widget.locator("#chart").getAttribute("srcdoc"),beforeToolsUrl);
  assert.equal(await widget.frameLocator("#chart").locator("#xy-compact-preview-style").evaluate((el:HTMLStyleElement)=>el.disabled),true);
  assert.equal(await widget.frameLocator("#chart").locator("body").evaluate(()=>(window as unknown as {noNavigationProbe:string}).noNavigationProbe),"preserve-frame");await widget.locator("#chart-tools").uncheck();
  await page.waitForTimeout(100);assert.equal(await widget.frameLocator("#chart").locator("#xy-compact-preview-style").evaluate((el:HTMLStyleElement)=>el.disabled),false);
  await widget.locator("#view-select").selectOption("svg");await widget.locator("#preview").evaluate(async(img:HTMLImageElement)=>{if(img.complete){if(img.naturalWidth)return;throw Error("SVG failed to decode");}await new Promise<void>((resolve,reject)=>{const timer=setTimeout(()=>reject(Error("SVG loading timed out")),10000);img.onload=()=>{clearTimeout(timer);resolve();};img.onerror=()=>{clearTimeout(timer);reject(Error("SVG failed"));};});});
  for(const kind of ["svg","html","source","spec"]){await widget.locator("#export-format").selectOption(kind);await widget.locator("#download-format").click();}
  await page.waitForTimeout(200);
  await widget.locator("#view-select").selectOption("interactive");await widget.locator("#more-summary").focus();await page.keyboard.press("Escape");
  await page.setViewportSize({width:390,height:1000});
  await widget.frameLocator("#chart").locator("canvas").first().evaluate(async(canvas:HTMLCanvasElement)=>{
    const deadline=Date.now()+5000;while(canvas.getBoundingClientRect().width>window.innerWidth+1){if(Date.now()>deadline)throw Error("Native XY canvas did not adapt to the mobile frame");await new Promise(requestAnimationFrame);}
  });
  await page.waitForTimeout(1000);
  await page.screenshot({path:path.join(output,"colorset2-mobile.png"),fullPage:true});
  await widget.locator("#more-summary").focus();await page.keyboard.press("Enter");
  const touchTargets=await widget.locator("button:visible,summary:visible,select:visible,.check-label:visible").evaluateAll(elements=>elements.map(el=>({label:(el.textContent??"").trim(),height:el.getBoundingClientRect().height,width:el.getBoundingClientRect().width})));assert.ok(touchTargets.every(t=>t.height>=44&&t.width>=44),JSON.stringify(touchTargets));
  await widget.locator("#palette-select").selectOption("colorset1");await widget.locator("#palette-select").evaluate(async(el:HTMLSelectElement)=>{const end=Date.now()+100000;while(el.value!=="colorset1"){if(Date.now()>end)throw Error("Palette update timed out");await new Promise(resolve=>setTimeout(resolve,50));}});await widget.frameLocator("#chart").locator("canvas").first().waitFor({timeout:30000});await page.waitForTimeout(1000);await widget.locator("#more-summary").focus();await page.keyboard.press("Escape");await page.waitForTimeout(500);await page.screenshot({path:path.join(output,"colorset1-mobile.png"),fullPage:true});await widget.locator("main").screenshot({path:path.join(output,"initial-mobile.png")});
  const mobileGeometry=await widget.frameLocator("#chart").locator("body").evaluate(()=>({viewport:window.innerWidth,elements:[...document.querySelectorAll("body,#chart,.xy,canvas")].map(el=>({tag:el.tagName,id:el.id,className:el.className,width:el.getBoundingClientRect().width,style:el.getAttribute("style")}))}));
  const overflow=await widget.locator("main").evaluate(el=>({scroll:document.documentElement.scrollWidth,width:document.documentElement.clientWidth}));assert.ok(overflow.scroll<=overflow.width+1,JSON.stringify(overflow));
  await widget.locator("#more-summary").click();await widget.locator("#data-editor > summary").click();assert.match(await widget.locator("#data-help").innerText(),/sample data/);
  const previousSrc=await widget.locator("#chart").getAttribute("srcdoc"),beforeInvalidCalls=calls.filter(c=>c.method==="tools/call").length;
  await widget.locator("#spec-editor").fill("{");await widget.locator("#apply-data").click();await widget.locator("#error").waitFor({state:"visible"});assert.match(await widget.locator("#error").innerText(),/not valid JSON/);assert.equal(calls.filter(c=>c.method==="tools/call").length,beforeInvalidCalls);assert.equal(await widget.locator("#chart").getAttribute("srcdoc"),previousSrc);
  await widget.locator("#spec-editor").fill('{"version":1,"factory":"chart","marks":[{"kind":"no-such-mark","args":[],"kwargs":{}}]}');await widget.locator("#apply-data").click();await widget.locator("#apply-data:not([disabled])").waitFor({timeout:100000});await widget.locator("#error").waitFor({state:"visible"});assert.equal(await widget.locator("#chart").getAttribute("srcdoc"),previousSrc);assert.equal(await widget.locator("#save-image").isEnabled(),true);await widget.locator("#save-image").click();
  const edited={version:1,factory:"chart",title:"Updated activities",marks:[{kind:"line",args:[[2,4,6],[9,4,7]],kwargs:{color:"$ink"}}]};await widget.locator("#spec-editor").fill(JSON.stringify(edited));await widget.locator("#apply-data").click();await widget.locator("#title").evaluate(async(el:HTMLElement)=>{const deadline=Date.now()+100000;while(el.textContent!=="Updated activities"){if(Date.now()>deadline)throw Error("Editor update timed out");await new Promise(resolve=>setTimeout(resolve,50));}});
  assert.equal(await widget.locator("#palette-select").inputValue(),"colorset1");assert.equal(await widget.locator("#error").isVisible(),false);const editedSpec=JSON.parse(await widget.locator("#spec-editor").inputValue());assert.deepEqual(editedSpec.marks[0].args,edited.marks[0].args);assert.equal(editedSpec.colorset,"colorset1");
  assert.ok(calls.some(c=>c.method==="tools/call"&&(c.params as {name:string}).name==="xy_recolor_chart"));assert.ok(calls.some(c=>c.method==="ui/download-file"));assert.ok(calls.some(c=>c.method==="ui/notifications/size-changed"));
  const serverToolCalls=calls.filter(c=>c.method==="tools/call").map(c=>(c.params as {name:string}).name);assert.deepEqual(serverToolCalls.filter(name=>name!=="xy_get_chart_artifact"),["xy_recolor_chart","xy_recolor_chart","xy_recolor_chart","xy_render_chart","xy_render_chart"]);assert.equal(samplingCalls,0);assert.deepEqual(calls.filter(c=>["ui/message","ui/update-model-context","sampling/createMessage"].includes(c.method)),[]);
  assert.deepEqual(errors,[]);assert.deepEqual(blockedBrowserRequests,[]);assert.deepEqual(Object.keys(downloaded).sort(),["chart.html","chart.png","chart.py","chart.svg","spec.json"]);
  const result={pass:true,version:"0.3.1",transport:desktop?"desktop stdio with embedded previews and exports":"http",host:"MCP Apps protocol fixture (not actual ChatGPT)",renderer:"native XY",default_colorset:"colorset1",explicit_colorset2_then_new_omitted_colorset1:true,model_free_app_entrypoint:desktop,editor_preserves_exact_data:true,invalid_editor_keeps_previous_chart:true,model_messages:0,model_context_updates:0,sampling_requests:samplingCalls,server_tool_calls:serverToolCalls,initial_actions:initialActions,keyboard_disclosure:true,compact_preview_preserves_original:true,touch_targets:touchTargets,widget_authored_colors:authoredColors,widget_initial_computed_colors:chrome,palettes:["colorset1","colorset2"],viewports:["desktop","mobile"],no_browser_network:true,embedded_native_html:true,embedded_native_svg:true,native_downloads:["svg","png","html","python","json"],renderer_error_recovery:true,methods:calls.map(c=>c.method),canvas:paints,mobile_native_geometry:mobileGeometry,overflow,errors};
  await writeFile(path.join(output,"report.json"),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
} catch(error) {
  await page.screenshot({path:path.join(output,"failure.png"),fullPage:true});
  await writeFile(path.join(output,"failure.json"),JSON.stringify({error:String(error),errors,consoleMessages,calls},null,2));throw error;
} finally {await page.close();await browser.close();await client.close();await desktopTransport?.close();if(service){service.http.close();await once(service.http,"close");}}
