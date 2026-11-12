// Run: node projects/plugin-ui-rich-interfaces/scripts/review-generated.mjs [--run-id ID]
// Evaluator-owned checks; never edits evaluated workspaces or copied skills.
import fs from "node:fs/promises";
import path from "node:path";
import {createHash} from "node:crypto";
import {createRequire} from "node:module";
import {spawnSync} from "node:child_process";
import {fileURLToPath,pathToFileURL} from "node:url";
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const repo=path.resolve(project,"../..");
const output=path.join(project,"artifacts/reviews/generated");await fs.mkdir(output,{recursive:true});
let require=createRequire(path.join(project,"package.json"));try{require.resolve("playwright");}catch{require=createRequire(path.join(repo,"projects/desktop-plugin-ui/mcp-probe/package.json"));}
const {chromium}=require("playwright");
const browser=await chromium.launch({headless:true,channel:"msedge"});
const only=process.argv.includes("--run-id")?process.argv[process.argv.indexOf("--run-id")+1]:null;
const folders=(await fs.readdir(path.join(repo,"evaluations/runs"))).filter(n=>n.startsWith("20261112-rich-ui-")&&(!only||n===only));
const rows=[];
async function exists(file){try{return(await fs.stat(file)).isFile();}catch{return false;}}
for(const run of folders){
  const base=path.join(repo,"evaluations/runs",run),workspace=path.join(base,"workspace"),files=path.join(workspace,"deliverables");
  if(!await exists(path.join(base,"evaluation-result.json")))continue;
  const result=JSON.parse(await fs.readFile(path.join(base,"evaluation-result.json"),"utf8"));
  const skill=JSON.parse(await fs.readFile(path.join(base,"run-manifest.json"),"utf8")).skill.name;
  const id=createHash("sha256").update(run).digest("hex").slice(0,12),destination=path.join(output,id);await fs.mkdir(destination,{recursive:true});
  const row={run,strictPassed:result.passed,checks:[],errors:[],artifacts:[]};
  const check=(name,passed,detail)=>row.checks.push({name,passed:Boolean(passed),detail});
  try{
    if(await exists(path.join(files,"review.json"))){const review=JSON.parse(await fs.readFile(path.join(files,"review.json"),"utf8"));check("Review distinguishes alternatives and evidence",Array.isArray(review.alternatives)&&Array.isArray(review.testsPerformed)&&Array.isArray(review.untested));}
    if(run.includes("-contract-")){
      const design=JSON.parse(await fs.readFile(path.join(files,"design.json"),"utf8"));
      check("Palette result parses",typeof design==="object"&&design!==null);
      const text=await fs.readFile(path.join(files,"route.md"),"utf8");check("Route has concrete limits",text.length>200&&/graph|chart|Sankey/i.test(text));
    }else if(run.includes("-boundary-generalization-")){
      const plan=JSON.parse(await fs.readFile(path.join(files,"blueprint.json"),"utf8"));
      for(const key of ["host","primarySurface","graphPlan","chartPlan","statePlan","alternatives","testPlan","evidenceLimits"])check(`Plan includes ${key}`,Boolean(plan[key]));
      const text=JSON.stringify(plan);check("Plan covers bounded scope and recovery",/neighbo|bound|page|cluster/i.test(text)&&/cancel|epoch|request/i.test(text)&&/exact|raw|table/i.test(text));
      check("Plan records untested host evidence",/untested|not prove|not establish|does not|unverified|conditional/i.test(JSON.stringify(plan.evidenceLimits)));
    }else if(skill==="desktop-plugin-ui"&&run.includes("-naturalistic-")){
      const plan=JSON.parse(await fs.readFile(path.join(files,"blueprint.json"),"utf8"));check("Six concrete host adapters",Array.isArray(plan.hostAdapters)?plan.hostAdapters.length===6:Object.keys(plan.hostAdapters??{}).length===6);check("Shared data and layout alternatives",Boolean(plan.sharedData)&&Boolean(plan.layoutAlternatives));
    }else if(await exists(path.join(files,"workspace.html"))){
      const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:"reduce"});const errors=[],network=[];
      page.on("pageerror",error=>errors.push(error.message));await page.route(/^https?:\/\//,route=>{network.push(route.request().url());return route.abort();});
      await page.goto(pathToFileURL(path.join(files,"workspace.html")).href);
      check("Authored document uses English",await page.locator("html").getAttribute("lang")==="en");
      check("Graph and chart are present",await page.locator("svg,canvas").count()>=2);
      const text=await page.locator("body").innerText();check("Task data and units are visible",/enrich/i.test(text)&&/150/.test(text)&&/180/.test(text)&&/ms|millisecond/i.test(text));
      for(const width of [1280,320]){
        await page.setViewportSize({width,height:900});const file=path.join(destination,`initial-${width}.png`);await page.screenshot({path:file,fullPage:true});row.artifacts.push(path.relative(project,file));
      }
      await page.setViewportSize({width:1280,height:900});
      const store=page.getByRole("button",{name:/store/i}).first();
      if(await store.count()&&await store.isVisible()){
        const before=await page.locator("body").innerText();await store.click();
        check("Selecting another node changes the inspector",before!==await page.locator("body").innerText());
      }else check("Selecting another node has an accessible control",false);
      const search=page.locator('input[type="search"],input[placeholder*="ilter"],input[aria-label*="ilter"]').first();
      if(await search.count()){
        await search.fill("no-such-node-zz");check("Empty search has explicit feedback",/no .*match|0 of|0 visible|no nodes|no workflow/i.test(await page.locator("body").innerText()));await search.fill("");
      }else check("Requested filter is available",false);
      for(const width of [1280,320]){
        await page.setViewportSize({width,height:900});await page.evaluate(()=>window.scrollTo(0,0));
        const geometry=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight}));
        check(`Page fits ${width}px`,geometry.scroll<=width+1,geometry);
        const screenshot=path.join(destination,`web-${width}.png`);await page.screenshot({path:screenshot,fullPage:geometry.height<6500});row.artifacts.push(path.relative(project,screenshot));
      }
      check("No external dependencies or browser exceptions",!network.length&&!errors.length,{network,errors});await page.close();
    }else if(run.includes("-code-native-plugin-ui-naturalistic-")){
      const source=await fs.readFile(path.join(files,"view.ts"),"utf8");
      const stage=path.join(destination,"native");await fs.mkdir(path.join(stage,".claude-plugin"),{recursive:true});await fs.mkdir(path.join(stage,"hooks"),{recursive:true});await fs.mkdir(path.join(stage,"tests"),{recursive:true});
      await fs.copyFile(path.join(files,"view.ts"),path.join(stage,"view.ts"));
      await fs.writeFile(path.join(stage,".claude-plugin/plugin.json"),JSON.stringify({name:"workflow-view",version:"1.0.0",description:"Independent generated adapter validation"}));
      await fs.writeFile(path.join(stage,"package.json"),JSON.stringify({type:"module",private:true}));
      await fs.writeFile(path.join(stage,"hooks/hooks.json"),JSON.stringify({modules:["../view.ts"]}));
      const nodeKey=/key\s*:\s*["'](node|service|node-select|service-select)["']/.exec(source)?.[1]??"node";
      const viewKey=/key\s*:\s*["'](view|analysis-view|view-select)["']/.exec(source)?.[1]??"view";
      const test=`import {expect,test} from "claude-code/testing";
for(const surface of ["terminal","desktop"])for(const columns of [32,80])test(surface+columns,async($,on)=>{
let id;on("ui.open",($,event)=>{id=event.id;return {value:{isPlaced:true}};});
on("session.start",()=>({cwd:"/work"}));await $.session.start({surface,isInteractive:true,cwd:"/work"});
await $.command.run({command:"workflow-view",args:""});expect(typeof id).toBe("string");
const ui=await $.ui.mount({plugin:"workflow-view",component:"Pane",requestId:id,surface,viewport:{columns,rows:30},props:{title:"Workflow",isFocused:true,bodyColumns:columns,placement:"inline",scroll:{offset:0,bodyRows:20},view:{}}});
await ui.select({key:${JSON.stringify(nodeKey)},value:"enrich"});await ui.select({key:${JSON.stringify(viewKey)},value:"metrics"});
expect(await ui.find({type:"Text",text:/180/})).toBeDefined();expect(await ui.find({type:"Text",text:/150/})).toBeDefined();
await ui.select({key:${JSON.stringify(nodeKey)},value:"store"});expect(await ui.find({type:"Text",text:/not supplied|no latency|unavailable|not provided|missing/i})).toBeDefined();
await ui.unmount();});\n`;
      await fs.writeFile(path.join(stage,"tests/independent.test.ts"),test);
      const command=spawnSync("claude",["plugin","test","."],{cwd:stage,env:{...process.env,CLAUDE_CONFIG_DIR:path.join(destination,"claude-state")},encoding:"utf8",timeout:60000,windowsHide:true});
      await fs.writeFile(path.join(destination,"native-tests.txt"),command.stdout+command.stderr);
      check("Actual native engine selects metrics and preserves missing data",command.status===0,{exitCode:command.status,log:path.relative(project,path.join(destination,"native-tests.txt"))});
    }else if(run.includes("-pi-extension-ui-naturalistic-")){
      const source=await fs.readFile(path.join(files,"view.ts"),"utf8");
      check("No model-facing message request",!source.includes("sendUserMessage("));
      const cli="C:/Users/villa/AppData/Roaming/npm/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js";
      const printed=spawnSync(process.execPath,[cli,"--offline","--mode","json","--print","--no-session","--no-context-files","--no-extensions","--no-skills","--no-prompt-templates","--no-themes","--no-mcp","--no-tools","--no-approve","-e",path.join(files,"view.ts"),"/workflow-view"],{cwd:destination,env:{...process.env,PI_CODING_AGENT_DIR:path.join(destination,"pi-state")},encoding:"utf8",timeout:30000,windowsHide:true});
      await fs.writeFile(path.join(destination,"pi-print.jsonl"),printed.stdout);
      const events=[];let invalid=0;for(const line of printed.stdout.split(/\r?\n/).filter(Boolean)){try{events.push(JSON.parse(line));}catch{invalid++;}}
      check("Real Pi JSON print emits valid event JSON",printed.status===0&&invalid===0,{exitCode:printed.status,invalidLines:invalid});
      check("Real Pi print remains inference-free",!events.some(e=>["agent_start","turn_start"].includes(e.type)));
      check("Real Pi print returns useful workflow output",events.some(e=>e.message?.content&&/enrich/i.test(JSON.stringify(e.message.content))));
    }else if(run.includes("-gemini-enterprise-ui-naturalistic-")){
      const messages=JSON.parse(await fs.readFile(path.join(files,"interface.json"),"utf8"));
      check("A2UI stream is nonempty",Array.isArray(messages)&&messages.length>=3);
      check("Official catalog is selected",messages.some(m=>m.createSurface?.catalogId==="https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"));
      check("Native quantitative chart exists",messages.some(m=>m.updateComponents?.components.some(c=>c.component==="VegaChart")));
      const runCheck=spawnSync("uv",["run","--script",path.join(project,"scripts/validate-a2ui.py"),path.join(files,"interface.json"),"--label",`generated-${id}`],{cwd:repo,encoding:"utf8",timeout:60000,windowsHide:true});
      await fs.writeFile(path.join(destination,"a2ui-validation.txt"),runCheck.stdout+runCheck.stderr);check("Official envelope/catalog and Vega schema pass",runCheck.status===0,{exitCode:runCheck.status});
    }else if(run.includes("-reflex-xy-naturalistic-")){
      const flow=JSON.parse(await fs.readFile(path.join(files,"flow.json"),"utf8")),latency=JSON.parse(await fs.readFile(path.join(files,"latency.json"),"utf8"));
      check("Sankey identities are exact labels",flow.preset==="sankey"&&JSON.stringify(flow.data?.nodes)===JSON.stringify(["Queue","Worker A","Worker B","Archive"])&&JSON.stringify(flow.data?.links)===JSON.stringify([["Queue","Worker A",60],["Queue","Worker B",40],["Worker A","Archive",60],["Worker B","Archive",40]]));
      check("Latency spec keeps exact observations",latency.marks?.some(m=>JSON.stringify(m.args?.[0])==="[0,1,2,3]"&&JSON.stringify(m.args?.[1])==="[120,130,160,190]")||latency.preset==="line"&&JSON.stringify(latency.data?.x)==="[0,1,2,3]"&&JSON.stringify(latency.data?.y)==="[120,130,160,190]");
      for(const [label,spec]of [["flow",flow],["latency",latency]]){
        const checked=spawnSync("uv",["run","--script",path.join(repo,"skills/reflex-xy/scripts/check_connected_spec.py"),"--spec",path.join(files,label+".json"),"--report",path.join(destination,label+"-wire.json")],{cwd:repo,encoding:"utf8",timeout:30000,windowsHide:true});check(`Connected ${label} wire recipe passes`,checked.status===0);
      }
      check("Default palette is retained",[flow,latency].every(s=>!s.colorset||s.colorset==="colorset1"));
    }
  }catch(error){row.errors.push(String(error));}
  row.passed=!row.errors.length&&row.checks.length>0&&row.checks.every(c=>c.passed);
  await fs.writeFile(path.join(destination,"review.json"),JSON.stringify(row,null,2));rows.push(row);
}
await browser.close();
await fs.writeFile(path.join(output,only?`review-${only}.json`:"reviews.json"),JSON.stringify(rows,null,2));
console.log(JSON.stringify({reviewed:rows.length,artifactPassed:rows.filter(r=>r.passed).length,failed:rows.filter(r=>!r.passed).map(r=>({run:r.run,checks:r.checks.filter(c=>!c.passed),errors:r.errors}))}));
