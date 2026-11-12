#!/usr/bin/env node
// Run with Node 24: node projects/desktop-plugin-ui/scripts/test-browser-sdk-contract.ts <fresh-run-id>
// Reuses read-only installed project tooling and pins from earlier evaluator inputs.
import { mkdir, writeFile, readFile, symlink } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const runId = process.argv[2]; if (!runId || !/^[a-zA-Z0-9-]+$/.test(runId)) throw new Error("Provide a fresh simple run ID");
const output = path.join(root, "projects/desktop-plugin-ui/artifacts/plugin-pocs/browser-sdk-verifier-selftests", runId);
await mkdir(path.dirname(output), { recursive: true }); await mkdir(output);
const pocDependencies = path.join(root, "evaluations/runs/20261025-plugin-poc-v3-chatgpt-desktop-sol-1/workspace/poc/node_modules");
const evaluatorDependencies = path.join(root, "projects/desktop-plugin-ui/mcp-probe/node_modules");
const { build } = await import(pathToFileURL(path.join(evaluatorDependencies, "esbuild/lib/main.js")).href);
const source = String.raw`import {App} from '@modelcontextprotocol/ext-apps';
const app=new App({name:'sdk-contract-selftest',version:'1.0.0'},{});
const load=document.querySelector<HTMLButtonElement>('#load')!,disconnect=document.querySelector<HTMLButtonElement>('#disconnect')!,retry=document.querySelector<HTMLButtonElement>('#retry')!,status=document.querySelector('#status')!,count=document.querySelector('#count')!,list=document.querySelector('#items')!;
let connected=false,busy=false;
function controls(){load.disabled=!connected||busy;disconnect.disabled=!connected||busy;}
function render(value:unknown){const data=value as {count:number,items:{id:string,state:string}[]};count.textContent=String(data.count);list.replaceChildren(...data.items.map(row=>{const li=document.createElement('li');li.textContent=row.id+' '+row.state;return li;}));}
app.ontoolresult=result=>{if(connected)render(result.structuredContent);};
async function invoke(){if(!connected||busy)return;busy=true;controls();retry.hidden=true;status.textContent='Loading inventory';try{const result=await app.callServerTool({name:'inventory_ready',arguments:{scope:'ready'}},{timeout:10000});if(result.isError)throw Error('Tool refused');render(result.structuredContent);status.textContent='Ready';}catch{status.textContent='Error: retry the inventory';retry.hidden=false;}finally{busy=false;controls();}}
load.addEventListener('click',invoke);retry.addEventListener('click',invoke);
disconnect.addEventListener('click',async()=>{connected=false;await app.close();controls();status.textContent='Disconnected';});
async function connect(){try{await app.connect();connected=true;status.textContent='Ready';}catch{status.textContent='Host connection unavailable';}finally{controls();}}
void connect();
`;
const style = "body{margin:16px;background:#ffffff;color:#333e48;font:16px Arial}h1{font-size:24px}button{background:#ffffff;color:#333e48;border:1px solid #696969;padding:8px;margin:4px;font:inherit}#load{background:#9e1b32;color:#ffffff}button:focus-visible{outline:2px solid #000000;outline-offset:2px}li{margin:8px 0}";
const results = [];
for (const [name, fakeClose, expected] of [["valid", false, true], ["fake-close", true, false]]) {
  const fixture = path.join(output, name); await mkdir(path.join(fixture, "src"), { recursive: true }); await mkdir(path.join(fixture, "dist")); await mkdir(path.join(fixture, "tests")); await mkdir(path.join(fixture, "node_modules"));
  for (const packageName of ["@modelcontextprotocol/ext-apps", "@modelcontextprotocol/sdk", "typescript", "@types/node", "playwright", "esbuild"]) {
    const dependencies = ["playwright", "esbuild"].includes(packageName) ? evaluatorDependencies : pocDependencies;
    const target = path.join(dependencies, packageName), link = path.join(fixture, "node_modules", packageName);
    if (!target.startsWith(root + path.sep)) throw new Error("Read-only dependency must remain inside root");
    await mkdir(path.dirname(link), { recursive: true }); await symlink(target, link, "junction");
  }
  await writeFile(path.join(fixture, "package.json"), JSON.stringify({ private: true, type: "module" }));
  const appSource = fakeClose ? source.replace("await app.close();", "await ({close:async()=>{}}).close();") : source;
  await writeFile(path.join(fixture, "src/app.ts"), appSource);
  await writeFile(path.join(fixture, "tests/browser.ts"), "export const evaluatorOnlyFixture = true;\n");
  for (const [file, include, nodeTypes] of [["tsconfig.app.json", ["src/**/*.ts"], []], ["tsconfig.tests.json", ["tests/**/*.ts"], ["node"]]]) {
    await writeFile(path.join(fixture, file), JSON.stringify({ compilerOptions: { target: "ES2022", module: "ESNext", moduleResolution: "Bundler", lib: ["ES2022", "DOM", "DOM.Iterable"], types: nodeTypes, strict: true, skipLibCheck: true, noEmit: true }, include }));
  }
  const bundle = await build({ entryPoints: [path.join(fixture, "src/app.ts")], bundle: true, platform: "browser", format: "iife", write: false });
  const html = `<!doctype html><html lang="en"><head><style>${style}</style></head><body><h1>Inventory Review</h1><p id="status" role="status">Connecting</p><p>Count: <output id="count">0</output></p><button id="load" type="button">Load ready</button><button id="disconnect" type="button">Disconnect</button><button id="retry" type="button" hidden>Retry</button><ul id="items"></ul><script>${bundle.outputFiles[0].text.replace(/<\/script/gi,"<\\/script")}</script></body></html>`;
  await writeFile(path.join(fixture, "dist/ui.html"), html);
  const evaluation = path.join(output, name + "-review");
  const command = [path.join(root, "projects/desktop-plugin-ui/scripts/verify-browser-sdk-contract.ts"), fixture, evaluation];
  const result = spawnSync(process.execPath, command, { cwd: root, encoding: "utf8", timeout: 90000 });
  let report; try { report = JSON.parse(await readFile(path.join(evaluation, "independent-review.json"), "utf8")); } catch {}
  const actual = result.status === 0 && report?.passed === true;
  results.push({ name, passed: Boolean(report) && actual === expected, expected_acceptance: expected, actual_acceptance: actual, stdout: result.stdout, stderr: result.stderr, failed: report?.checks.filter(item => !item.passed).map(item => item.name) });
}
const report = { passed: results.every(item => item.passed), results, scope: "Evaluator selftests only; not generated-task acceptance or installed-host paint." };
await writeFile(path.join(output, "result.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report)); process.exitCode = report.passed ? 0 : 1;
