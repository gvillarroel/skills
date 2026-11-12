#!/usr/bin/env node
// Run with Node 24: node projects/desktop-plugin-ui/scripts/probe-mcp-sdk-lifecycle.ts <generated-poc-root> <fresh-project-artifact-output>
// Uses the PoC's declared, already installed TypeScript and SDK files read-only.
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const [pocArgument, outputArgument] = process.argv.slice(2);
if (!pocArgument || !outputArgument) throw new Error("Expected PoC root and fresh output");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const poc = path.resolve(pocArgument), output = path.resolve(outputArgument);
if (!output.startsWith(path.join(root, "projects/desktop-plugin-ui/artifacts") + path.sep)) throw new Error("Output must stay in project artifacts");
await mkdir(path.dirname(output), { recursive: true }); await mkdir(output);
await writeFile(path.join(output, "package.json"), JSON.stringify({ private: true, type: "module" }));
const packageRoot = path.join(poc, "node_modules/@modelcontextprotocol/ext-apps");
const version = JSON.parse(await readFile(path.join(packageRoot, "package.json"), "utf8")).version;
const compilerVersion = JSON.parse(await readFile(path.join(poc, "node_modules/typescript/package.json"), "utf8")).version;
const nodeTypeVersion = JSON.parse(await readFile(path.join(poc, "node_modules/@types/node/package.json"), "utf8")).version;
const sdkVersion = JSON.parse(await readFile(path.join(poc, "node_modules/@modelcontextprotocol/sdk/package.json"), "utf8")).version;
const source = `import { App } from "@modelcontextprotocol/ext-apps";\nconst app = new App({name:"lifecycle-probe",version:"1.0.0"}, {});\nconst closeResult: Promise<void> = app.close();\nconst connectResult: Promise<void> = app.connect();\nconst toolResult = app.callServerTool({name:"selected_filter",arguments:{filter:"all"}}, {timeout:10000});\nvoid closeResult;void connectResult;void toolResult;\n`;
await writeFile(path.join(output, "lifecycle.ts"), source);
const results = [];
for (const mode of ["NodeNext", "Bundler"]) {
  const config = { compilerOptions: { target: "ES2022", module: mode === "NodeNext" ? "NodeNext" : "ESNext", moduleResolution: mode, lib: ["ES2022", "DOM", "DOM.Iterable"], types: [], strict: true, skipLibCheck: true, noEmit: true, paths: { "@modelcontextprotocol/ext-apps": [path.join(packageRoot, "dist/src/app.d.ts")] } }, files: ["lifecycle.ts"] };
  const configFile = path.join(output, `tsconfig-${mode}.json`);
  await writeFile(configFile, JSON.stringify(config, null, 2));
  const command = [path.join(poc, "node_modules/typescript/bin/tsc"), "--project", configFile];
  const result = spawnSync(process.execPath, command, { encoding: "utf8", cwd: output, timeout: 30000 });
  await writeFile(path.join(output, `${mode}-stdout.txt`), result.stdout ?? "");
  await writeFile(path.join(output, `${mode}-stderr.txt`), result.stderr ?? "");
  results.push({ mode, exitCode: result.status, error: result.error ? String(result.error) : undefined, stdout: result.stdout, stderr: result.stderr });
}
const { App } = await import(pathToFileURL(path.join(packageRoot, "dist/src/app.js")).href);
const app = new App({ name: "lifecycle-runtime-probe", version: "1.0.0" }, {});
const runtimeClose = typeof app.close;
let runtimeCloseResult;
try { await app.close(); runtimeCloseResult = "resolved"; } catch (error) { runtimeCloseResult = String(error); }
const report = { version, compilerVersion, nodeTypeVersion, sdkVersion, results, runtimeClose, runtimeCloseResult, observed: "Actual pinned declaration-chain compilation under two module resolvers and real inherited-method invocation; no network, host connection or model request." };
await writeFile(path.join(output, "result.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report));
