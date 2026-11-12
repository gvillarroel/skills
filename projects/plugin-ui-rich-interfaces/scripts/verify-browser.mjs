// Run: node projects/plugin-ui-rich-interfaces/scripts/verify-browser.mjs
// Uses the pinned MCP SDK and Playwright dependencies from ../package.json.
import fs from "node:fs/promises";
import path from "node:path";
import {createRequire} from "node:module";
import {fileURLToPath,pathToFileURL} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
let require=createRequire(path.join(root,"package.json"));
try{require.resolve("playwright");}catch{require=createRequire(path.resolve(root,"../desktop-plugin-ui/mcp-probe/package.json"));}
const {chromium}=require("playwright");
const {Client}=await import(pathToFileURL(require.resolve("@modelcontextprotocol/sdk/client/index.js")));
const {StdioClientTransport}=await import(pathToFileURL(require.resolve("@modelcontextprotocol/sdk/client/stdio.js")));
const output=path.join(root,"artifacts/reviews/browser");await fs.mkdir(output,{recursive:true});
const packageRoot=path.join(root,"artifacts/packages/service-observatory");
const transport=new StdioClientTransport({command:process.execPath,args:[path.join(packageRoot,"server.mjs")],cwd:packageRoot,stderr:"pipe"});
const client=new Client({name:"rich-interface-independent-check",version:"1.0.0"});
const checks=[],errors=[],calls=[];
function check(name,passed,detail){checks.push({name,passed:Boolean(passed),detail});if(!passed)throw new Error(name);}
let browser,failure;
try{
  await client.connect(transport);
  const tools=await client.listTools();
  check("Real stdio tool discovery",tools.tools.some(t=>t.name==="open_observatory")&&tools.tools.some(t=>t.name==="refresh_observatory"));
  const initial=await client.callTool({name:"open_observatory",arguments:{}});
  check("Text-only clients receive useful results",initial.content.some(c=>c.type==="text"&&c.text.includes("268 ms")));
  check("Shared exact dataset",initial.structuredContent.snapshot.services.length===12&&initial.structuredContent.snapshot.edges.length===13);
  const resource=await client.readResource({uri:"ui://service-observatory/workspace.html"});
  const entry=resource.contents[0],html=entry.text;
  check("MCP App resource MIME",entry.mimeType==="text/html;profile=mcp-app");
  check("Bundled network-free resource",!/<script[^>]+src=|<link[^>]+href=/i.test(html));
  await fs.writeFile(path.join(output,"resource.html"),html);
  browser=await chromium.launch({headless:true,channel:"msedge"});
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:"reduce"});
  page.on("pageerror",error=>errors.push(error.message));
  let rejectNext=false,delayNext=false,denyMode=false,releaseDelayed,delayedComplete,serverToolsEnabled=true;
  await page.exposeFunction("hostRpc",async(method,params)=>{
    calls.push({method,params});
    if(method==="ui/initialize")return {protocolVersion:params.protocolVersion,hostInfo:{name:"Local protocol fixture",version:"1.0.0"},hostCapabilities:serverToolsEnabled?{serverTools:{}}:{},hostContext:{theme:"light",displayMode:"inline",availableDisplayModes:["inline","fullscreen"],containerDimensions:{width:1440,maxHeight:1800}}};
    if(method==="tools/call"){
      const delayed=delayNext;
      if(delayed){delayNext=false;delayedComplete=false;await new Promise(resolve=>{releaseDelayed=resolve;});}
      if(rejectNext){rejectNext=false;return {isError:true,content:[{type:"text",text:"Controlled refresh rejection"}]};}
      const result=await client.callTool(params);if(delayed)delayedComplete=true;return result;
    }
    if(method==="ui/request-display-mode")return {mode:denyMode?"inline":params.mode};
    throw new Error(`Unsupported fixture request: ${method}`);
  });
  const shell='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0"><iframe id="app" title="Service Observatory — local protocol fixture" sandbox="allow-scripts" style="width:100%;height:1800px;border:0;display:block"></iframe></body></html>';
  await page.setContent(shell);
  await page.evaluate(({html,initial})=>{
    const element=document.getElementById("app");
    window.addEventListener("message",async event=>{
      if(event.source!==element.contentWindow||event.data?.jsonrpc!=="2.0")return;
      const request=event.data;
      if(request.method==="ui/notifications/initialized"){
        element.contentWindow.postMessage({jsonrpc:"2.0",method:"ui/notifications/tool-result",params:initial},"*");return;
      }
      if(request.id!==undefined){
        try{const result=await window.hostRpc(request.method,request.params??{});element.contentWindow.postMessage({jsonrpc:"2.0",id:request.id,result},"*");}
        catch(error){element.contentWindow.postMessage({jsonrpc:"2.0",id:request.id,error:{code:-32601,message:String(error)}},"*");}
      }
    });
    element.srcdoc=html.replace("<head>",'<head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data:; connect-src \'none\'">');
  },{html,initial});
  const frame=page.frameLocator("#app");
  await frame.locator('body[data-bridge="ready"]').waitFor();
  check("Real App SDK handshake and result delivery",await frame.locator("#selected-name").innerText()==="Payments");
  check("Visible map has all nodes",await frame.locator("g.graph-node").count()===12);
  const original=await frame.locator("body").evaluate(()=>window.ServiceObservatory.getData());
  await frame.locator("body").evaluate(()=>{const data=window.ServiceObservatory.getData(),service=data.services.find(s=>s.id==="payments");service.name="Payments operation with a very long documented service name";service.p95=345;service.history[23].p95=345;window.ServiceObservatory.setData(data);});
  check("Long graph label stays within the node",await frame.getByRole("button",{name:/Payments operation with a very long/}).locator(".node-label").evaluate(node=>node.getComputedTextLength()<=102));
  check("Summary metrics derive from the same snapshot",(await frame.locator("#kpi-latency").innerText()).includes("345")&&(await frame.locator("#selected-latency").innerText()).includes("345"));
  await frame.locator("body").evaluate((_,data)=>window.ServiceObservatory.setData(data),original);
  await frame.getByRole("button",{name:"Orders, watch, 142 milliseconds",exact:true}).click();
  check("Graph selection updates inspector",await frame.locator("#selected-name").innerText()==="Orders");
  await frame.locator("#show-metrics").click();
  check("Selection survives view change",(await frame.locator("#chart-heading").innerText()).startsWith("Orders"));
  await frame.locator("#metrics-panel details").evaluate(el=>el.open=true);
  check("Exact hourly data provided",await frame.locator("#values-body tr").count()===24);
  await frame.locator("#metric").selectOption("error");
  check("Metric units update",(await frame.locator("#value-unit").innerText()).includes("%"));
  check("No stale point titles after redraw",await frame.locator("circle.observation title").count()===24);
  await frame.locator("#search").fill("Payments");
  check("Filtered-out selection remains explicit",await frame.locator("#outside-filter").isVisible()&&await frame.locator("#selected-name").innerText()==="Orders");
  await frame.locator("#search").fill("does-not-exist");
  await frame.locator("#tab-dependencies").click();
  check("Empty filter has recovery",await frame.locator("#empty").isVisible()&&await frame.locator("#clear-filters").isVisible());
  await frame.locator("#clear-filters").click();
  await frame.locator("#options-toggle").click();await frame.locator("#layout").focus();await page.keyboard.press("Escape");
  check("Escape closes only focused options and returns focus",!(await frame.locator("#options").isVisible())&&await frame.locator("#options-toggle").evaluate(el=>el===document.activeElement));
  await frame.locator("g.graph-node[tabindex='0']").focus();await page.keyboard.press("ArrowRight");
  check("Graph roving keyboard selection",await frame.locator("g.graph-node[tabindex='0']").count()===1&&await frame.locator("g.graph-node[tabindex='0']").evaluate(el=>el===document.activeElement));
  const before=await frame.locator("body").evaluate(()=>window.ServiceObservatory.getState());
  rejectNext=true;await frame.locator("#refresh").click();await frame.locator("#error").waitFor();
  check("Error preserves selected identity",(await frame.locator("body").evaluate(()=>window.ServiceObservatory.getState())).selected===before.selected);
  await frame.locator("#retry").click();await frame.locator("#refresh-status").filter({hasText:"Snapshot refreshed"}).waitFor();
  check("Retry recovers with actual server tool",!await frame.locator("#error").isVisible()&&calls.some(c=>c.method==="tools/call"&&c.params.name==="refresh_observatory"));
  const revision=await frame.locator("body").evaluate(()=>window.ServiceObservatory.getData().revision);
  delayNext=true;await frame.locator("#refresh").click();await frame.locator("#cancel-refresh").click();
  check("Cancel occurs before delayed response",typeof releaseDelayed==="function"&&(await frame.locator("#refresh-status").innerText()).includes("canceled"));
  releaseDelayed();for(let i=0;i<100&&!delayedComplete;i++)await new Promise(resolve=>setTimeout(resolve,10));
  check("Canceled server request actually completes",delayedComplete);await page.waitForTimeout(100);
  const afterCancel=await frame.locator("body").evaluate(()=>({revision:window.ServiceObservatory.getData().revision,state:window.ServiceObservatory.getState()}));
  check("Late canceled response cannot overwrite snapshot",afterCancel.revision===revision,{before:revision,after:afterCancel});
  denyMode=true;await frame.locator("#expand-workspace").click();await frame.locator("#connection").filter({hasText:"inline view retained"}).waitFor();
  check("Fullscreen refusal respects returned mode",true);
  await frame.locator("#options-toggle").click();await frame.locator("#export").click();
  check("Data view works without sandbox downloads",await frame.locator("#export-data pre").isVisible());
  await frame.locator("#export-data").evaluate(el=>el.remove());
  await frame.locator("#options-toggle").click();
  await frame.locator("body").evaluate(()=>window.ServiceObservatory.select("payments"));
  for(const width of [1440,1280,1024,768,542,390,320]){
    await page.setViewportSize({width,height:1000});
    const geometry=await frame.locator("html").evaluate(el=>({width:el.clientWidth,scroll:el.scrollWidth}));
    check(`No page overflow at ${width}px`,geometry.scroll<=geometry.width+1,geometry);
    check(`Inspector visible at ${width}px`,await frame.locator("#selected-name").isVisible());
    if(width<=1024){
      check(`Readable dependency list at ${width}px`,await frame.locator("#adjacency").isVisible()&&!await frame.locator("#network").isVisible());
      check(`Mobile graph starts with the direct neighborhood at ${width}px`,await frame.locator("#adjacency button").count()===3);
      await frame.locator("#mobile-scope").click();check(`Full topology remains available at ${width}px`,await frame.locator("#adjacency button").count()===12);await frame.locator("#mobile-scope").click();
    }
    if(width<=390){
      const targets=await frame.locator("button,select,summary").evaluateAll(nodes=>nodes.filter(node=>node.getClientRects().length&&node.getBoundingClientRect().width>0&&node.getBoundingClientRect().height>0).map(node=>({name:node.textContent.trim().slice(0,40),height:node.getBoundingClientRect().height,width:node.getBoundingClientRect().width})));
      check(`Visible mobile controls meet the 44px target at ${width}px`,targets.every(target=>target.height>=44&&target.width>=44),targets.filter(target=>target.height<44||target.width<44));
    }
    if(width>1024){
      const font=await frame.locator("#network .node-label").first().evaluate(node=>parseFloat(getComputedStyle(node).fontSize)*document.getElementById("network").getBoundingClientRect().width/840);
      check(`Primary graph labels remain at least 12 physical CSS pixels at ${width}px`,font>=12,{font});
    }
    if(width===542){
      await frame.locator("#adjacency button").filter({hasText:"Orders"}).first().focus();await page.keyboard.press("Enter");
      const focus=await frame.locator("body").evaluate(()=>({selected:document.getElementById("selected-name").textContent,activeTag:document.activeElement.tagName,activeText:document.activeElement.textContent.slice(0,80),scope:document.activeElement.closest("#adjacency")?.id,keys:[...document.querySelectorAll("#adjacency button")].map(node=>node.getAttribute("data-focus-key"))}));
      check("Keyboard selection preserves focus on the rebuilt compact-list control",focus.selected==="Orders"&&focus.scope==="adjacency"&&focus.activeText.startsWith("Orders"),focus);
      await frame.locator("#related button").first().focus();await page.keyboard.press("Enter");
      check("A removed relationship trigger moves focus to the selected-service heading",await frame.locator("#selected-name").evaluate(node=>node===document.activeElement));
      await frame.locator("body").evaluate(()=>window.ServiceObservatory.select("payments"));
    }
    await page.evaluate(()=>window.scrollTo(0,0));
    await frame.locator("html").evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:path.join(output,`bridge-${width}.png`)});
  }
  await page.setViewportSize({width:1440,height:1000});
  await frame.locator("#options-toggle").click();await frame.locator("#layout").selectOption("overview");await frame.locator("#options-toggle").click();
  check("Overview alternative retains same selected data",await frame.locator("#metrics-panel").isVisible()&&await frame.locator("#records-panel").isVisible()&&await frame.locator("#selected-name").innerText()==="Payments");
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,"bridge-overview-1440.png")});
  check("No unhandled browser exceptions",errors.length===0,errors);
  check("No assistant messages requested by inspection controls",!calls.some(c=>c.method==="ui/message"));
  serverToolsEnabled=false;
  await page.evaluate(html=>{document.getElementById("app").srcdoc=html;},html);
  await frame.locator('body[data-bridge="ready"]').waitFor();
  check("Absent server-tool capability hides refresh",!await frame.locator("#refresh").isVisible());
  await frame.locator("#search").fill("Orders");check("Local inspection remains available without server actions",await frame.locator("g.graph-node").count()===1);
  await frame.locator("#options-toggle").click();await frame.locator("#export").click();check("Data access remains available without optional host file APIs",await frame.locator("#export-data pre").isVisible());
  const filteredExport=JSON.parse(await frame.locator("#export-data pre").innerText());check("Export declares and preserves the visible filter scope",filteredExport.services.length===1&&filteredExport.services[0].id==="orders"&&filteredExport.scope.query==="Orders"&&filteredExport.selectionOutsideFilter===true);
  await fs.writeFile(path.join(output,"host-calls.json"),JSON.stringify(calls,null,2));
  await page.close();
  // Capture the same authored UI without iframe compositor/scroll ambiguity.
  const visual=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:"reduce"});
  visual.on("pageerror",error=>errors.push(error.message));
  const standalone=pathToFileURL(path.join(packageRoot,"standalone.html")).href;
  for(const width of [1440,1280,1024,768,542,390,320]){
    await visual.setViewportSize({width,height:1000});await visual.goto(standalone);
    await visual.locator("g.graph-node").first().waitFor({state:"attached"});
    await visual.screenshot({path:path.join(output,`focused-${width}.png`),fullPage:true});
    check(`Standalone page paints at ${width}px`,await visual.locator("h1").isVisible());
  }
  await visual.setViewportSize({width:1440,height:1000});await visual.goto(standalone+"?layout=overview");
  await visual.screenshot({path:path.join(output,"overview-1440.png"),fullPage:true});
  await visual.goto(standalone);await visual.locator("#tab-metrics").click();
  await visual.screenshot({path:path.join(output,"metrics-1440.png"),fullPage:true});
  await visual.setViewportSize({width:320,height:1000});await visual.screenshot({path:path.join(output,"metrics-320.png"),fullPage:true});
  await visual.close();
}catch(error){failure=String(error);}finally{
  if(browser)await browser.close();await client.close();
  const report={passed:!failure&&checks.every(c=>c.passed),checks,failure,errors,scope:"Actual stdio MCP server and real App SDK in a sandboxed browser fixture. This is not signed-in host acceptance."};
  await fs.writeFile(path.join(output,"review.json"),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
}
