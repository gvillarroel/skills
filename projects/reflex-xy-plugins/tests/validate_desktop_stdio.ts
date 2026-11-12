#!/usr/bin/env -S npx tsx
// Run: npx tsx tests/validate_desktop_stdio.ts --root <extracted-mcpb>
//   --output-dir <artifacts> --sdk-root <@modelcontextprotocol/sdk/dist/esm>
// Add --default-sequence true to test fresh requests after explicit Colorset 2.
// Add --progressive-ui true for the versioned simple-first UI and interaction reference.
// Requires Node 22+ and the project's locked MCP SDK and tsx development tools.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

async function main() {
const options:Record<string,string>={};
for(let i=2;i<process.argv.length;i+=2) options[process.argv[i]!.replace(/^--/,"")]=process.argv[i+1]!;
for(const name of ["root","output-dir","sdk-root"]) assert.ok(options[name],`Missing --${name}`);
const root=path.resolve(options.root!);const output=path.resolve(options["output-dir"]!);await mkdir(output,{recursive:true});
const sdk=path.resolve(options["sdk-root"]!);
const {Client}=await import(pathToFileURL(path.join(sdk,"client/index.js")).href);
const {StdioClientTransport}=await import(pathToFileURL(path.join(sdk,"client/stdio.js")).href);
const manifest=JSON.parse(await readFile(path.join(root,"manifest.json"),"utf8"));
assert.equal(manifest.manifest_version,"0.3");assert.equal(manifest.server.type,"node");
const replacements:Record<string,string>={__dirname:root,"user_config.artifactDirectory":path.join(output,"runtime"),"user_config.uvExecutable":"uv"};
function substitute(value:string) {return value.replace(/\$\{([^}]+)\}/g,(_,key)=>{assert.ok(Object.hasOwn(replacements,key),`Unexpected manifest variable ${key}`);return replacements[key]!;});}
const env:Record<string,string>=Object.fromEntries(Object.entries(process.env).filter((entry):entry is [string,string]=>typeof entry[1]==="string"));
for(const [key,value]of Object.entries(manifest.server.mcp_config.env))env[key]=substitute(String(value));
env.UV_CACHE_DIR=path.join(output,"uv-cache");env.PYTHONDONTWRITEBYTECODE="1";env.PYTHONIOENCODING="utf-8";
// Deliberately do not provide XY_PYTHON: this validates the shipped uv entry.
delete env.XY_PYTHON;
const transport=new StdioClientTransport({command:manifest.server.mcp_config.command,args:manifest.server.mcp_config.args.map(substitute),env,cwd:root,stderr:"pipe"});
let diagnostics="";transport.stderr?.on("data",(chunk:Buffer)=>{diagnostics+=String(chunk);});
const client=new Client({name:"independent-desktop-acceptance",version:"0.1.0"});
const hash=async(file:string)=>createHash("sha256").update(await readFile(path.join(root,file))).digest("hex");
const report:Record<string,unknown>={passed:false,live_claude_desktop_installation:"not_tested",checks:[],palettes:[],
  extension_version:manifest.version,default_sequence:options["default-sequence"]==="true",
  subject:{manifest_sha256:await hash("manifest.json"),server_sha256:await hash(manifest.server.entry_point),renderer_sha256:await hash("runtime/render.py")}};
const checks=report.checks as string[];
try {
  await client.connect(transport);
  const tools=await client.listTools();assert.ok(tools.tools.some((tool:{name:string})=>tool.name==="xy_render_chart"));
  checks.push("manifest_substitution_and_real_stdio_initialization");
  const capabilities=await client.callTool({name:"xy_capabilities",arguments:{}});assert.ok(!capabilities.isError);
  assert.equal(capabilities.structuredContent.capabilities.version,"0.0.8");
  assert.equal(capabilities.structuredContent.capabilities.presets.length,36);
  const reference=await client.callTool({name:"xy_get_reference",arguments:{topic:"workflow"}});assert.ok(!reference.isError);assert.match(reference.structuredContent.text,/name: reflex-xy/);
  if(options["default-sequence"]==="true"){
    assert.equal(capabilities.structuredContent.capabilities.default_colorset,"colorset1");
    assert.match(reference.structuredContent.text,/Default to `colorset1` for every new chart/);
  }
  checks.push("packaged_skill_and_capability_catalog");
  const renderTool=tools.tools.find((tool:{name:string})=>tool.name==="xy_render_chart");
  const uri=renderTool._meta.ui.resourceUri;
  if(options["progressive-ui"]==="true"){
    assert.equal(uri,"ui://reflex-xy/chart-v2.html");
    const interaction=await client.callTool({name:"xy_get_reference",arguments:{topic:"interaction"}});
    assert.ok(!interaction.isError);assert.match(interaction.structuredContent.text,/More options/);
    const progressive=await client.readResource({uri});
    const text=progressive.contents[0].text;
    assert.match(text,/id="save-image"/);assert.match(text,/id="advanced-panel"[^>]*hidden/);
    assert.match(text,/aria-controls="advanced-panel"/);
    report.widget_sha256=createHash("sha256").update(text).digest("hex");
    checks.push("versioned_progressive_ui_and_canonical_interaction_reference");
  }
  const generic={version:1,factory:"chart",title:"Independent Desktop default",data:{x:[0,2,5,9,14],y:[4,7,3,11,8]},marks:[{kind:"line",args:["x","y"],kwargs:{}},{kind:"scatter",args:["x","y"],kwargs:{}}]};
  const sequence=options["default-sequence"]==="true" ? [
    {name:"preset-explicit-cs2",palette:"colorset2",spec:{preset:"scatter",colorset:"colorset2"}},
    {name:"preset-omitted-after-cs2",palette:"colorset1",spec:{preset:"scatter"}},
    {name:"generic-explicit-cs2",palette:"colorset2",spec:{...generic,colorset:"colorset2"}},
    {name:"generic-omitted-after-cs2",palette:"colorset1",spec:generic},
  ] : ["colorset1","colorset2"].map(palette=>({name:palette,palette,spec:{preset:"scatter",colorset:palette,title:"Independent Desktop stdio"}}));
  for(const {name,palette,spec} of sequence){
    const response=await client.callTool({name:"xy_render_chart",arguments:{spec_json:JSON.stringify(spec)}},undefined,{timeout:180000});
    assert.ok(!response.isError,JSON.stringify(response));assert.equal(response.structuredContent.palette,palette);
    const dir=path.join(output,name);await mkdir(dir,{recursive:true});
    for(const [kind,url]of Object.entries(response.structuredContent.downloads)){
      const parsed=new URL(String(url));assert.equal(parsed.hostname,"127.0.0.1");assert.ok(parsed.searchParams.has("token"));
      const resource=await fetch(parsed);assert.equal(resource.status,200);assert.equal(resource.headers.get("cache-control"),"no-store");
      const ext=kind==="source"?"py":kind==="spec"?"json":kind;
      await writeFile(path.join(dir,`chart.${ext}`),Buffer.from(await resource.arrayBuffer()));
      const missing=new URL(parsed);missing.search="";assert.equal((await fetch(missing)).status,404);
    }
    const ui=await client.readResource({uri});assert.equal(ui.contents[0].mimeType,"text/html;profile=mcp-app");
    assert.equal(ui.contents[0]._meta.ui.domain,undefined,"Local Claude Desktop extension must omit ui.domain");
    assert.deepEqual(ui.contents[0]._meta.ui.csp.frameDomains,[response._meta.artifact_origin]);
    await writeFile(path.join(dir,"result.json"),JSON.stringify(response,null,2));
    const expectedInk=palette==="colorset1"?"#9e1b32":"#007298";
    const svg=await readFile(path.join(dir,"chart.svg"),"utf8");
    assert.match(svg,new RegExp(`<(?:circle|path|line|rect|polygon|polyline)\\b[^>]*(?:fill|stroke)=["']${expectedInk}["']`),"Native mark ink does not match the requested/default palette");
    const saved=JSON.parse(await readFile(path.join(dir,"chart.json"),"utf8"));assert.equal(saved.colorset,palette);
    (report.palettes as string[]).push(palette);
  }
  checks.push("uv_native_xy_both_palettes_and_capability_downloads","local_mcp_apps_resource_and_dynamic_origin_csp");
  if(options["default-sequence"]==="true")checks.push("fresh_preset_and_generic_default_cs1_after_explicit_cs2");
  report.passed=true;
}catch(error){report.failure=String(error);}finally{
  await client.close();report.stderr=diagnostics;
  await writeFile(path.join(output,"report.json"),JSON.stringify(report,null,2)+"\n");
}
console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
}
main().catch(error=>{console.error(String(error));process.exitCode=1;});
