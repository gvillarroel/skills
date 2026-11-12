import { build } from "esbuild";
import { mkdir,readFile,writeFile } from "node:fs/promises";
import path from "node:path";
const outdir=path.resolve(process.env.XY_BUILD_DIR??"dist");
await mkdir(outdir,{recursive:true});
await build({entryPoints:["src/server.ts"],outfile:path.join(outdir,"server.js"),bundle:true,packages:"external",platform:"node",format:"esm",target:"node22"});
const serverBundle=await build({entryPoints:["src/server.ts"],outfile:path.join(outdir,"server-bundled.js"),bundle:true,platform:"node",format:"esm",target:"node22",metafile:true,banner:{js:'import { createRequire } from "node:module"; const require = createRequire(import.meta.url);'}});
const browser=await build({entryPoints:["web/widget.ts"],bundle:true,write:false,platform:"browser",format:"iife",target:"es2022",minify:true,metafile:true});
const template=await readFile("web/widget.html","utf8");
await writeFile(path.join(outdir,"widget.html"),template.replace("/*__WIDGET_BUNDLE__*/",()=>browser.outputFiles[0].text.replaceAll("</script","<\\/script")));
const packages=new Set();
for(const input of [...Object.keys(serverBundle.metafile.inputs),...Object.keys(browser.metafile.inputs)]) {
  const match=/node_modules\/(?:.*node_modules\/)?(@[^/]+\/[^/]+|[^/]+)\//.exec(input.replaceAll("\\","/"));if(match)packages.add(match[1]);
}
const notices=["THIRD-PARTY NOTICES\n\nNative XY MCP App server and widget bundles\n"];
for(const name of [...packages].sort()) {
  const folder=path.join("node_modules",name);const pkg=JSON.parse(await readFile(path.join(folder,"package.json"),"utf8"));
  notices.push(`\n${"=".repeat(72)}\n${name} ${pkg.version}\nLicense: ${pkg.license??"See package license"}\n`);
  let copied=false;
  for(const candidate of ["LICENSE","LICENSE.md","LICENSE.txt","license","license.md","license.txt","LICENCE","COPYING"]) {
    try {notices.push(await readFile(path.join(folder,candidate),"utf8"));copied=true;break;}catch{}
  }
  if(!copied)notices.push(`Package source: https://www.npmjs.com/package/${name}/v/${pkg.version}\n`);
}
await writeFile(path.join(outdir,"THIRD-PARTY-NOTICES.txt"),notices.join("\n"));
console.log("Built MCP server and self-contained MCP Apps widget.");
