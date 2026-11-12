// Run: node projects/plugin-ui-rich-interfaces/scripts/build.mjs
// Dependencies: esbuild and the MCP SDK packages declared in ../package.json.
import fs from "node:fs/promises";
import path from "node:path";
import {createRequire} from "node:module";
import {fileURLToPath} from "node:url";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
let require=createRequire(path.join(root,"package.json"));
try{require.resolve("esbuild");}catch{
  // Reuse the pinned project development installation on this workstation.
  require=createRequire(path.resolve(root,"../desktop-plugin-ui/mcp-probe/package.json"));
}
const {build}=require("esbuild");
async function dependencyVersion(entry,name){
  let directory=path.dirname(require.resolve(entry));
  while(directory!==path.dirname(directory)){
    try{const value=JSON.parse(await fs.readFile(path.join(directory,"package.json"),"utf8"));if(value.name===name&&value.version)return value.version;}catch{}
    directory=path.dirname(directory);
  }
  throw new Error(`Dependency version not found: ${name}`);
}
const nodePaths=[path.dirname(path.dirname(require.resolve("esbuild/package.json")))];
const output=path.join(root,"artifacts/packages/service-observatory");
await fs.mkdir(output,{recursive:true});
const read=relative=>fs.readFile(path.join(root,relative),"utf8");
const escapeScript=value=>value.replace(/<\/script/gi,"<\\/script");
const bundle=await build({entryPoints:[path.join(root,"web/bridge.js")],bundle:true,write:false,format:"iife",platform:"browser",nodePaths,minify:true});
let html=await read("web/index.html");
const css=await read("web/styles.css"),d3=await read("web/vendor/d3.min.js"),data=await read("web/data.js"),application=await read("web/app.js");
html=html.replace('<link rel="stylesheet" href="styles.css">',()=>`<style>${css}</style>`)
  .replace('<script src="vendor/d3.min.js"></script>',()=>`<script>${escapeScript(d3)}</script>`)
  .replace('<script src="data.js"></script>',()=>`<script>${escapeScript(data)}</script>`)
  .replace('<script src="app.js" defer></script>',"")
  .replace("</body>",()=>`<script>${escapeScript(application)}</script></body>`);
const standalone=html;
await fs.writeFile(path.join(output,"standalone.html"),standalone);
await fs.writeFile(path.join(output,"workspace.html"),html.replace("</body>",()=>`<script>${escapeScript(bundle.outputFiles[0].text)}</script></body>`));
await fs.copyFile(path.join(root,"data/observatory.json"),path.join(output,"observatory.json"));
await build({entryPoints:[path.join(root,"server.mjs")],outfile:path.join(output,"server.mjs"),bundle:true,platform:"node",format:"esm",nodePaths,banner:{js:"import { createRequire as __createRequire } from 'node:module'; const require = __createRequire(import.meta.url);"}});
await fs.writeFile(path.join(output,"package.json"),JSON.stringify({name:"service-observatory",version:"1.0.0",type:"module",private:true},null,2));
await fs.writeFile(path.join(output,"mcp.json"),JSON.stringify({$schema:"https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",mcpServers:{"service-observatory":{type:"stdio",command:"node",args:["${PLUGIN_ROOT}/server.mjs"],cwd:"${PLUGIN_ROOT}"}}},null,2));
await fs.writeFile(path.join(output,"plugin.json"),JSON.stringify({$schema:"https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",name:"service-observatory",version:"1.0.0",description:"Read-only service dependencies, metrics and inspection."},null,2));
await fs.writeFile(path.join(output,"build-evidence.json"),JSON.stringify({sdk:await dependencyVersion("@modelcontextprotocol/sdk/server/mcp.js","@modelcontextprotocol/sdk"),apps:await dependencyVersion("@modelcontextprotocol/ext-apps","@modelcontextprotocol/ext-apps"),esbuild:require("esbuild/package.json").version,htmlBytes:Buffer.byteLength(html),scope:"One portable stdio MCP App. Host loaders and paint require separate verification."},null,2));
console.log(JSON.stringify({output,htmlBytes:Buffer.byteLength(html),selfContained:true}));
