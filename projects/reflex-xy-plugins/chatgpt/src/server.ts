import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerAppResource, registerAppTool, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import { z } from "zod";
import { configFromEnv, FILES, HERE, parseSpec, RenderStore, type RenderRecord, type ServerConfig } from "./core.js";
import { embeddedPreviewHtml } from "./preview.js";
export { COMPACT_PREVIEW_SHIM } from "./preview.js";

export const UI_URI="ui://reflex-xy/chart-v4.html";
export const STARTER_SPEC={version:1,title:"Weekly activity",description:"Sample data",colorset:"colorset1",factory:"chart",marks:[{kind:"line",args:[[1,2,3,4,5,6],[3,5,4,7,6,8]],kwargs:{color:"$ink",width:2}}],components:[{kind:"x_axis",kwargs:{label:"Week"}},{kind:"y_axis",kwargs:{label:"Completed tasks"}}]};
const palette=z.enum(["colorset1","colorset2"]);
const outputSchema=z.object({
  render_id:z.string(),title:z.string(),palette,width:z.number(),height:z.number(),factory:z.string(),
  rows:z.number(),marks:z.number(),warnings:z.array(z.string()),expires_at:z.string(),
  downloads:z.object({html:z.string().url(),svg:z.string().url(),png:z.string().url(),source:z.string().url(),spec:z.string().url()}),
});
const readOnly={readOnlyHint:true,destructiveHint:false,openWorldHint:false,idempotentHint:true};
const referenceFiles={
  workflow:"SKILL.md",colorsets:"references/colorsets.md",recipes:"references/chart-recipes.md",
  advanced:"references/advanced-charts.md",exports:"references/outputs-and-validation.md",live:"references/large-data-and-live.md",interaction:"references/interaction-design.md",
} as const;
function toolError(error:unknown) {return {isError:true as const,content:[{type:"text" as const,text:error instanceof Error ? error.message : "XY request failed."}]};}
async function chartResult(store:RenderStore,record:RenderRecord) {
  const m=record.metadata;
  const [html,svg]=await Promise.all([store.read(record.id,record.key,"chart.html"),store.read(record.id,record.key,"chart.svg")]);
  if(!html||!svg)throw new Error("Chart preview expired or unavailable.");
  if(html.data.length+svg.data.length>8*1024*1024)throw new Error("The embedded chart preview exceeds 8 MiB. Reduce the chart data or SVG detail.");
  const downloads={html:store.artifactUrl(record,"chart.html"),svg:store.artifactUrl(record,"chart.svg"),png:store.artifactUrl(record,"chart.png"),source:store.artifactUrl(record,"chart.py"),spec:store.artifactUrl(record,"spec.json")};
  return {
    content:[{type:"text" as const,text:"The chart is ready."}],
    structuredContent:{render_id:record.id,title:m.title,palette:m.palette,width:m.width,height:m.height,factory:m.factory,rows:m.counts.rows,marks:m.counts.marks,warnings:m.warnings,expires_at:new Date(record.created+store.config.ttlMs).toISOString(),downloads},
    _meta:{render_key:record.key,artifact_origin:store.config.baseUrl,svg_compat_repairs:m.svg_compat_repairs,spec_json:JSON.stringify(record.spec),native_preview:{html:html.data.toString("utf8"),svg:svg.data.toString("utf8")}},
  };
}
export async function createMcpServer(store:RenderStore,widgetPath=path.join(process.env.XY_BUILD_DIR??path.join(HERE,"dist"),"widget.html")) {
  const server=new McpServer({name:"reflex-xy",version:"0.3.1"},{instructions:"Render familiar XY requests directly with xy_render_chart; no preflight tool calls are required. Known sample presets: line, scatter, bar, sankey. Minimal spec_json: {\"preset\":\"line\",\"title\":\"Sample trend\"}. For supplied numeric x/y data, use {\"version\":1,\"factory\":\"chart\",\"marks\":[{\"kind\":\"line\",\"args\":[[1,2],[3,5]],\"kwargs\":{\"color\":\"$ink\"}}]}; replace the sample arrays with the exact supplied data. Read xy_capabilities or one focused xy_get_reference topic only for an unfamiliar contract. Preset defaults are synthetic samples. Every new chart defaults to Colorset 1; Colorset 2 requires explicit user opt-in for that chart, and never affects later defaults. Keep responses concise: the inline component supplies Save image and More options. Its palette, view and export controls run without a model turn. Do not duplicate their UI or narrate engine counts/expiry. Standalone HTML is an interactive data snapshot; Python callbacks require a live backend."});
  registerAppResource(server,"XY chart",UI_URI,{description:"A chart with Save image and optional display/export controls."},async()=>({
    contents:[{uri:UI_URI,mimeType:RESOURCE_MIME_TYPE,text:await readFile(widgetPath,"utf8"),_meta:{
      ui:{prefersBorder:true,...(store.config.widgetDomain?{domain:store.config.widgetDomain}:{}),csp:{connectDomains:[],resourceDomains:[],frameDomains:["about:"]}},
      "openai/widgetDescription":"Chart preview with Save image. More options contains palette, view and export choices.",
      "openai/ui":{availableDisplayModes:["inline","fullscreen"]},
      "openai/widgetCSP":{redirect_domains:[]},
    }}],
  }));
  registerAppTool(server,"xy_open_chart_app",{
    title:"XY charts",description:"Open the chart app with a clearly labeled Colorset 1 sample. Edit chart data in More options; all controls run without a model turn.",
    inputSchema:{},outputSchema,annotations:{...readOnly,idempotentHint:false},
    _meta:{ui:{resourceUri:UI_URI,visibility:["app"]},"openai/ui":{entrypoints:[{type:"global"},{type:"thread"}]}},
  },async()=>{try{return chartResult(store,await store.render(STARTER_SPEC));}catch(error){return toolError(error);}});
  registerAppTool(server,"xy_render_chart",{
    title:"Render native XY chart",description:"Render directly to an inline interactive XY chart and native HTML/SVG/PNG/Python exports. Known sample presets: line, scatter, bar, sankey. Minimal spec_json: {\"preset\":\"line\",\"title\":\"Sample trend\"}. Preserve exact supplied data through the generic version:1 contract. Query xy_capabilities only for unfamiliar chart types. New charts always default to Colorset 1; colorset2 requires explicit opt-in for this chart. Never pass code, URLs or filesystem paths. UI palette/view/export controls require no model turn.",
    inputSchema:{spec_json:z.string().min(2).max(196608).describe("JSON object: {preset,colorset?,title?,data?} or the generic version:1 chart specification documented by xy_capabilities. Missing colorset always becomes colorset1. colorset2 requires explicit user opt-in.")},outputSchema,
    annotations:{...readOnly,idempotentHint:false},_meta:{ui:{resourceUri:UI_URI,visibility:["model","app"]},"openai/toolInvocation/invoking":"Rendering XY chart…","openai/toolInvocation/invoked":"XY chart ready"},
  },async({spec_json})=>{try{return chartResult(store,await store.render(parseSpec(spec_json)));}catch(error){return toolError(error);}});
  registerAppTool(server,"xy_recolor_chart",{
    title:"Change XY palette",description:"Regenerate this existing native XY chart after the user explicitly chooses a palette. Colorset 2 is opt-in for this chart only and never changes the default of a new chart. The UI must supply its opaque render capability.",
    inputSchema:{render_id:z.string().regex(/^[a-f0-9]{32}$/),render_key:z.string().regex(/^[A-Za-z0-9_-]{43}$/),colorset:palette},outputSchema,
    annotations:{...readOnly,idempotentHint:false},_meta:{ui:{visibility:["app"]}},
  },async({render_id,render_key,colorset})=>{
    try {const record=store.get(render_id,render_key);if(!record)throw new Error("Chart expired or unavailable. Ask the assistant to render it again.");return chartResult(store,await store.render({...record.spec,colorset}));}
    catch(error){return toolError(error);}
  });
  registerAppTool(server,"xy_get_chart_artifact",{
    title:"Get native XY export",description:"Read one original chart export through its opaque widget capability. Returns embedded bytes to the app without navigating to a local HTTP URL.",
    inputSchema:{render_id:z.string().regex(/^[a-f0-9]{32}$/),render_key:z.string().regex(/^[A-Za-z0-9_-]{43}$/),format:z.enum(["html","svg","png","source","spec"])},
    outputSchema:{name:z.string(),mime_type:z.string(),bytes:z.number().int().nonnegative()},annotations:readOnly,_meta:{ui:{visibility:["app"]}},
  },async({render_id,render_key,format})=>{
    try{
      const name=({html:"chart.html",svg:"chart.svg",png:"chart.png",source:"chart.py",spec:"spec.json"} as const)[format];
      const file=await store.read(render_id,render_key,name);if(!file)throw new Error("Chart expired or unavailable. Render a fresh chart.");
      if(file.data.length>16*1024*1024)throw new Error("The embedded export exceeds 16 MiB. Reduce the chart data before downloading.");
      return {content:[{type:"text" as const,text:"File ready."}],structuredContent:{name,mime_type:FILES[name],bytes:file.data.length},_meta:{artifact:{name,mime_type:FILES[name],blob:file.data.toString("base64")}}};
    }catch(error){return toolError(error);}
  });
  server.registerTool("xy_get_reference",{
    title:"Read bundled XY skill guidance",description:"Read one focused, canonical skill reference when the requested chart needs unfamiliar styling, interaction, export or advanced behavior. Familiar chart requests can render directly without reading references.",
    inputSchema:{topic:z.enum(["workflow","colorsets","recipes","advanced","exports","live","interaction"])},
    outputSchema:{topic:z.string(),text:z.string()},annotations:readOnly,
  },async({topic})=>{try{const text=await readFile(path.join(store.config.skillDir,referenceFiles[topic]),"utf8");if(Buffer.byteLength(text)>32768)throw new Error("Reference exceeds the configured limit.");return {content:[{type:"text",text}],structuredContent:{topic,text}};}catch{return toolError(new Error("Bundled skill reference is unavailable. Run the project packaging/bootstrap step."));}});
  server.registerTool("xy_capabilities",{
    title:"Inspect supported XY chart contract",description:"List the authoritative, allowlisted native XY factories, marks, components and presets supported by this deterministic adapter, plus input limits and boundaries. This adapter deliberately does not execute arbitrary Python.",
    inputSchema:{},outputSchema:{capabilities:z.record(z.string(),z.unknown())},annotations:readOnly,
  },async()=>{try {
    const text=await readFile(path.join(path.dirname(store.config.renderScript),"capabilities.json"),"utf8");
    const capabilities=JSON.parse(text);
    return {content:[{type:"text",text:JSON.stringify(capabilities)}],structuredContent:{capabilities}};
  }catch{return toolError(new Error("Runtime capability manifest is unavailable. Run the project bootstrap step."));}});
  return server;
}
async function bodyJson(req:IncomingMessage) {
  if(req.headers["content-encoding"] && req.headers["content-encoding"]!=="identity")throw new Error("Compressed requests are unsupported.");
  if(!String(req.headers["content-type"]??"").toLowerCase().startsWith("application/json"))throw new Error("Use application/json.");
  let size=0;const chunks:Buffer[]=[];
  for await(const chunk of req) {const b=Buffer.from(chunk);size+=b.length;if(size>262144)throw new Error("MCP request exceeds 256 KiB.");chunks.push(b);}
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}
export async function startHttp(config:ServerConfig, options: {assetsOnly?: boolean} = {}) {
  const store=new RenderStore(config);
  const http=createServer(async(req,res)=>{
    const url=new URL(req.url??"/",config.baseUrl);
    res.setHeader("X-Content-Type-Options","nosniff");res.setHeader("Referrer-Policy","no-referrer");res.setHeader("Cache-Control","no-store");
    try {
      if(req.method==="GET" && url.pathname==="/") {res.writeHead(200,{"Content-Type":"application/json"}).end(JSON.stringify({name:"reflex-xy",version:"0.3.1",mcp:options.assetsOnly?null:"/mcp",transport:options.assetsOnly?"stdio":"http",authentication:config.bearer?"bearer":"none",status:"ready",default_colorset:"colorset1"}));return;}
      if(req.method==="GET" && url.pathname.startsWith("/artifacts/")) {
        const match=/^\/artifacts\/([a-f0-9]{32})\/(chart\.(?:html|svg|png|py)|spec\.json)$/.exec(url.pathname);
        if(!match){res.writeHead(404).end("Artifact not found.");return;}
        const artifact=await store.read(match[1],url.searchParams.get("token")??"",match[2]);
        if(!artifact){res.writeHead(404).end("Artifact expired or unavailable.");return;}
        res.setHeader("Content-Type",artifact.type);
        res.setHeader("Content-Disposition",`${url.searchParams.get("download")==="1" ? "attachment":"inline"}; filename="${match[2]}"`);
        if(match[2]==="chart.html")res.setHeader("Content-Security-Policy","default-src 'none'; script-src 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; connect-src 'none'; worker-src blob:; base-uri 'none'; form-action 'none'; frame-src 'none'");
        if(match[2]==="chart.html"&&url.searchParams.get("preview")==="compact") {
          // Only the embedded preview hides native toolbar chrome. The original
          // standalone HTML file and every download remain byte-for-byte intact.
          const compact=embeddedPreviewHtml(artifact.data.toString("utf8"));
          res.end(compact);
        } else res.end(artifact.data);
        return;
      }
      if(options.assetsOnly||url.pathname!=="/mcp"){res.writeHead(404).end("Not found.");return;}
      if(req.headers.origin) {
        const origin=new URL(req.headers.origin);
        if(origin.origin!==config.baseUrl){res.writeHead(403).end("Direct cross-origin MCP requests are disabled; use the host MCP bridge.");return;}
      }
      if(config.bearer && req.headers.authorization!==`Bearer ${config.bearer}`) {res.writeHead(401,{"WWW-Authenticate":"Bearer"}).end("Unauthorized.");return;}
      const hostname=new URL(`http://${req.headers.host??""}`).hostname.toLowerCase();
      const allowed=new Set([new URL(config.baseUrl).hostname,"localhost","127.0.0.1","[::1]"]);
      if(!allowed.has(hostname)){res.writeHead(403).end("Unexpected host.");return;}
      if(req.method!=="POST"){res.writeHead(405,{Allow:"POST"}).end("Use stateless Streamable HTTP POST.");return;}
      const parsed=await bodyJson(req);
      const release=store.acquireSession();
      const server=await createMcpServer(store);
      const transport=new StreamableHTTPServerTransport({sessionIdGenerator:undefined,enableJsonResponse:true});
      res.on("close",()=>{release();void transport.close();void server.close();});
      await server.connect(transport);
      await transport.handleRequest(req,res,parsed);
    } catch(error) {
      if(!res.headersSent)res.writeHead(400,{"Content-Type":"application/json"}).end(JSON.stringify({error:error instanceof Error?error.message:"Invalid request."}));else res.end();
    }
  });
  http.requestTimeout=100000;http.headersTimeout=10000;
  await new Promise<void>((resolve,reject)=>{http.once("error",reject);http.listen(config.port,config.bind,()=>resolve());});
  const address=http.address();
  if(typeof address==="object" && address && config.port===0) {config.port=address.port;config.baseUrl=`http://127.0.0.1:${address.port}`;}
  return {http,store,url:`${config.baseUrl}/mcp`};
}
async function main() {
  const stdio=process.argv.includes("--stdio"),desktop=process.argv.includes("--desktop");
  if(desktop&&!stdio)throw new Error("--desktop requires --stdio.");
  const config=configFromEnv(process.env,{desktop});
  if(stdio) {
    // The small HTTP listener serves capability-protected assets for UI/download links.
    const service=await startHttp(config,{assetsOnly:desktop});const server=await createMcpServer(service.store);await server.connect(new StdioServerTransport());
    process.stderr.write(`XY MCP stdio ready; artifacts at ${config.baseUrl}\n`);
  } else {const service=await startHttp(config);process.stderr.write(`XY MCP server ready at ${service.url}\n`);}
}
if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(error=>{process.stderr.write(`${error instanceof Error?error.message:"Startup failed."}\n`);process.exitCode=1;});
