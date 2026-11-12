#!/usr/bin/env node
// Run with Node 24: node projects/desktop-plugin-ui/scripts/verify-browser-sdk-contract.ts <generated-fixture-root> <fresh-project-artifact-output>
// Uses the fixture's real locked TypeScript/SDK/Playwright packages; no source repairs.
import { mkdir, readFile, writeFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";

const [fixtureArgument, outputArgument] = process.argv.slice(2);
if (!fixtureArgument || !outputArgument) throw new Error("Expected generated fixture root and fresh output directory");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const fixture = path.resolve(fixtureArgument), output = path.resolve(outputArgument);
if (!output.startsWith(path.join(root, "projects/desktop-plugin-ui/artifacts") + path.sep)) throw new Error("Output must stay inside project artifacts");
await mkdir(path.dirname(output), { recursive: true }); await mkdir(output);
const temporary = path.join(output, "tmp"); await mkdir(temporary);
for (const name of ["TMP", "TEMP", "TMPDIR"]) process.env[name] = temporary;
process.env.NODE_DISABLE_COMPILE_CACHE = "1";
const checks = [], observations = {};
function check(name, passed, detail = {}) { checks.push({ name, passed: Boolean(passed), ...detail }); }
const expectedPins = { "@modelcontextprotocol/ext-apps": "1.7.5", "@modelcontextprotocol/sdk": "1.32.2", typescript: "5.9.3", "@types/node": "24.10.1", playwright: "1.64.1", esbuild: "0.28.2" };
for (const [name, expected] of Object.entries(expectedPins)) {
  const actual = JSON.parse(await readFile(path.join(fixture, "node_modules", name, "package.json"), "utf8")).version;
  check("pinned-package:" + name, actual === expected, { actual, expected });
}
const typescriptModule = await import(pathToFileURL(path.join(fixture, "node_modules/typescript/lib/typescript.js")).href);
const ts = typescriptModule.default ?? typescriptModule;
const sdkModule = await import(pathToFileURL(path.join(fixture, "node_modules/@modelcontextprotocol/ext-apps/dist/src/app.js")).href);
const sdkApp = new sdkModule.App({ name: "independent-lifecycle-probe", version: "1.0.0" }, {});
check("real-sdk-inherited-close-exists", typeof sdkApp.close === "function");
try { await sdkApp.close(); check("real-sdk-inherited-close-resolves", true); } catch (error) { check("real-sdk-inherited-close-resolves", false, { error: String(error) }); }
for (const file of ["tsconfig.app.json", "tsconfig.tests.json"]) {
  const command = [path.join(fixture, "node_modules/typescript/bin/tsc"), "--project", path.join(fixture, file), "--noEmit", "--incremental", "false", "--pretty", "false"];
  const result = spawnSync(process.execPath, command, { cwd: fixture, encoding: "utf8", timeout: 30000 });
  await writeFile(path.join(output, file + ".stdout.txt"), result.stdout ?? "");
  await writeFile(path.join(output, file + ".stderr.txt"), result.stderr ?? "");
  check("independent-typecheck:" + file, result.status === 0, { exitCode: result.status, stdout: result.stdout, stderr: result.stderr });
}
try {
  const configPath = path.join(fixture, "tsconfig.app.json");
  const config = ts.readConfigFile(configPath, ts.sys.readFile);
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, fixture);
  const program = ts.createProgram({ rootNames: parsed.fileNames, options: { ...parsed.options, noEmit: true } });
  const checker = program.getTypeChecker();
  const source = program.getSourceFile(path.join(fixture, "src/app.ts"));
  const calls = [];
  function walk(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
      const name = node.expression.name.text;
      if (["connect", "callServerTool", "close"].includes(name)) {
        const receiver = checker.getNonNullableType(checker.getTypeAtLocation(node.expression.expression));
        const declaration = checker.getResolvedSignature(node)?.getDeclaration();
        calls.push({ name, receiver: checker.typeToString(receiver), receiverFlags: receiver.flags, declaration: declaration?.getSourceFile().fileName, sourceText: node.getText(source) });
      }
    }
    ts.forEachChild(node, walk);
  }
  walk(source); observations.resolvedSdkCalls = calls;
  for (const name of ["connect", "callServerTool", "close"]) {
    const genuine = calls.filter(call => call.name === name && call.receiver === "App" && call.declaration?.replaceAll("\\", "/").includes("/node_modules/@modelcontextprotocol/"));
    check("genuine-typed-sdk-call:" + name, genuine.length > 0, { calls: calls.filter(call => call.name === name) });
  }
} catch (error) { check("genuine-sdk-type-resolution", false, { error: String(error) }); }

const html = await readFile(path.join(fixture, "dist/ui.html"), "utf8");
observations.uiSha256 = createHash("sha256").update(html).digest("hex");
const { chromium } = await import(pathToFileURL(path.join(fixture, "node_modules/playwright/index.mjs")).href);
const wire = [], browserErrors = [], browserRequests = [];
let browser;
try {
  browser = await chromium.launch({ headless: true, channel: "msedge" });
  observations.browserVersion = browser.version(); observations.temporary = temporary; observations.temporaryEntries = await readdir(temporary);
  const page = await browser.newPage({ viewport: { width: 900, height: 850 } });
  page.on("pageerror", error => browserErrors.push(error.message));
  await page.route(/^https?:\/\//, async route => { browserRequests.push(route.request().url()); await route.abort(); });
  let hold = false, release, fail = false;
  await page.exposeFunction("contractRpc", async (method, params) => {
    wire.push({ method, params });
    if (method === "ui/initialize") return { protocolVersion: params.protocolVersion, hostInfo: { name: "independent-sdk-contract", version: "1.0.0" }, hostCapabilities: { serverTools: {} }, hostContext: { theme: "light", displayMode: "inline", availableDisplayModes: ["inline"] } };
    if (method === "tools/call") {
      if (params.name !== "inventory_ready" || params.arguments?.scope !== "ready") throw new Error("Unexpected business tool request");
      if (hold) { hold = false; await new Promise(resolve => { release = resolve; }); }
      if (fail) { fail = false; return { isError: true, content: [{ type: "text", text: "Synthetic tool failure; retry is available." }] }; }
      return { structuredContent: { count: 2, items: [{ id: "A-1", state: "ready" }, { id: "A-3", state: "ready" }] }, content: [{ type: "text", text: "2 ready items: A-1 and A-3" }] };
    }
    if (["ui/message", "sampling/createMessage"].includes(method)) throw new Error("Unexpected model work");
    throw new Error("Unexpected fixture request " + method);
  });
  await mount(page, html, { count: 0, items: [] });
  const frame = page.frameLocator("#component"), initialLoad = frame.getByRole("button", { name: "Load ready", exact: true }), disconnect = frame.getByRole("button", { name: "Disconnect", exact: true });
  await initialLoad.waitFor({ timeout: 15000 });
  const actionId = await initialLoad.getAttribute("id");
  const load = actionId ? frame.locator(`[id=${JSON.stringify(actionId)}]`) : initialLoad;
  observations.primaryActionId = actionId;
  for (let i = 0; i < 100 && await load.isDisabled(); i++) await page.waitForTimeout(20);
  const initialText = await frame.locator("body").innerText();
  check("actual-sdk-handshake-and-zero-opening", wire.some(call => call.method === "ui/initialize") && /\b0\b/.test(initialText) && !initialText.includes("A-1"), { actual: initialText });
  check("english-accessible-document", await frame.locator("html").getAttribute("lang") === "en");
  const countTools = () => wire.filter(call => call.method === "tools/call").length;
  const readyVisible = async () => { const text = await frame.locator("body").innerText(); return text.includes("A-1") && text.includes("A-3") && !text.includes("A-2") && /\b2\b/.test(text); };
  await load.focus(); await page.keyboard.press("Tab");
  const tabFocus = await frame.locator("body").evaluate(() => ({ tag: document.activeElement?.tagName, text: document.activeElement?.textContent }));
  check("native-tab-reaches-control", tabFocus.tag === "BUTTON", { actual: tabFocus });
  await load.focus(); hold = true; const beforeEnter = countTools(); await load.press("Enter");
  for (let i = 0; i < 100 && !release; i++) await page.waitForTimeout(20);
  const busyText = await frame.locator("body").innerText();
  check("real-busy-and-duplicate-guard", Boolean(release) && await load.isDisabled() && /loading|busy|working|fetching/i.test(busyText), { actual: busyText });
  await load.evaluate(button => button.click());
  check("no-second-dispatch-while-held", countTools() === beforeEnter + 1);
  release?.();
  for (let i = 0; i < 100 && !(await readyVisible()); i++) await page.waitForTimeout(20);
  check("enter-direct-call-authoritative-result", countTools() === beforeEnter + 1 && await readyVisible());
  const beforeSpace = countTools(); await load.focus(); await load.press("Space");
  for (let i = 0; i < 100 && countTools() === beforeSpace; i++) await page.waitForTimeout(20);
  check("space-one-direct-call", countTools() === beforeSpace + 1 && await readyVisible());
  fail = true; await load.click(); const retry = frame.getByRole("button", { name: "Retry", exact: true }); await retry.waitFor({ timeout: 8000 });
  check("failure-preserves-ready-data", await readyVisible());
  const beforeRetry = countTools(); await retry.click();
  for (let i = 0; i < 100 && await load.isDisabled(); i++) await page.waitForTimeout(20);
  check("retry-recovers-without-model", await readyVisible() && !await retry.isVisible() && !await load.isDisabled() && countTools() === beforeRetry + 1);
  const paint = [];
  for (const width of [900, 320]) {
    await page.setViewportSize({ width, height: 850 }); await load.focus();
    await load.press("Tab"); await page.keyboard.press("Shift+Tab");
    const measurement = await measure(frame);
    paint.push({ width, ...measurement });
    check("layout-and-text-contrast:" + width, measurement.scrollWidth <= measurement.width + 1 && measurement.colors.every(item => item.disabled || item.ratio >= (item.large ? 3 : 4.5)), { actual: measurement });
    check("focus-visible-contrast:" + width, measurement.focusRatio >= 3, { actual: measurement.focus });
    await page.screenshot({ path: path.join(output, "inventory-" + width + ".png"), fullPage: true });
  }
  observations.paint = paint;
  await disconnect.click(); await page.waitForTimeout(100);
  const afterDisconnect = await frame.locator("body").innerText();
  check("disconnect-disabled-state", await load.isDisabled() && /disconnect/i.test(afterDisconnect), { actual: afterDisconnect });
  await page.evaluate(() => document.querySelector("iframe").contentWindow.postMessage({ jsonrpc: "2.0", method: "ui/notifications/tool-result", params: { structuredContent: { count: 99, items: [{ id: "LATE-99", state: "ready" }] }, content: [] } }, "*"));
  await page.waitForTimeout(150);
  check("late-result-ignored-after-close", await frame.locator("body").innerText() === afterDisconnect);
  await page.close();
  const rejected = await browser.newPage({ viewport: { width: 900, height: 850 } });
  await rejected.exposeFunction("contractRpc", async method => { if (method === "ui/initialize") throw new Error("Synthetic initialization denial"); return {}; });
  await mount(rejected, html, { count: 0, items: [] }); await rejected.waitForTimeout(500);
  const rejectedText = await rejected.frameLocator("#component").locator("body").innerText();
  check("initialization-failure-visible", /unavailable|failed|could not|unable|error|not connected/i.test(rejectedText), { actual: rejectedText });
  await rejected.screenshot({ path: path.join(output, "initialization-failure.png"), fullPage: true });
  await rejected.close();
  check("no-browser-network-or-page-errors", browserRequests.length === 0 && browserErrors.length === 0, { browserRequests, browserErrors });
  check("no-model-message-or-sampling", !wire.some(call => ["ui/message", "sampling/createMessage"].includes(call.method)));
} catch (error) { check("independent-browser-sequence", false, { error: String(error), wire }); }
await browser?.close();
const report = { passed: checks.length > 0 && checks.every(item => item.passed), checks, observations, wire, browserRequests, browserErrors, host_acceptance_verified: false, user_testing_performed: false };
await writeFile(path.join(output, "independent-review.json"), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ passed: report.passed, checks: checks.length, failed: checks.filter(item => !item.passed).map(item => item.name), report: path.join(output, "independent-review.json") }));
process.exitCode = report.passed ? 0 : 1;

async function mount(page, html, data) {
  await page.setContent('<!doctype html><html lang="en"><body style="margin:0"><iframe id="component" title="Inventory SDK fixture" sandbox="allow-scripts" style="width:100%;height:800px;border:0"></iframe></body></html>');
  await page.evaluate(({ html, data }) => {
    const frame = document.querySelector("iframe");
    window.addEventListener("message", async event => {
      if (event.source !== frame.contentWindow || event.data?.jsonrpc !== "2.0") return;
      const message = event.data;
      if (message.method === "ui/notifications/initialized") { frame.contentWindow.postMessage({ jsonrpc: "2.0", method: "ui/notifications/tool-result", params: { structuredContent: data, content: [{ type: "text", text: "Inventory initial result" }] } }, "*"); return; }
      if (message.id === undefined) return;
      try { const result = await window.contractRpc(message.method, message.params ?? {}); frame.contentWindow.postMessage({ jsonrpc: "2.0", id: message.id, result }, "*"); }
      catch (error) { frame.contentWindow.postMessage({ jsonrpc: "2.0", id: message.id, error: { code: -32603, message: String(error) } }, "*"); }
    });
    frame.srcdoc = html;
  }, { html, data });
}

async function measure(frame) {
  return frame.locator("body").evaluate(() => {
    const parse = value => { const match = value?.match(/rgba?\(([^)]+)\)/); if (!match) return null; const values = match[1].split(",").map(Number); return { rgb: values.slice(0,3), alpha: values[3] ?? 1 }; };
    const compose = (foreground, background, alpha) => foreground.map((value,index)=>value*alpha+background[index]*(1-alpha));
    const lum = rgb => rgb.map(value=>{ value/=255; return value<=.04045?value/12.92:Math.pow((value+.055)/1.055,2.4); }).reduce((sum,value,index)=>sum+value*[.2126,.7152,.0722][index],0);
    const ratio = (foreground,background) => (Math.max(lum(foreground),lum(background))+.05)/(Math.min(lum(foreground),lum(background))+.05);
    const background = element => { const layers=[];while(element){const color=parse(getComputedStyle(element).backgroundColor);if(color)layers.unshift(color);element=element.parentElement;}return layers.reduce((base,layer)=>compose(layer.rgb,base,layer.alpha),[255,255,255]); };
    const colors=Array.from(document.querySelectorAll('h1,h2,p,label,button,li,output,[role=status],[role=alert]')).filter(element=>element.getBoundingClientRect().width>0&&element.textContent?.trim()).map(element=>{const style=getComputedStyle(element),bg=background(element),fg=parse(style.color)??{rgb:[0,0,0],alpha:1},large=parseFloat(style.fontSize)>=24||(parseFloat(style.fontSize)>=18.667&&Number(style.fontWeight)>=700);return{text:element.textContent?.trim().slice(0,80),ratio:ratio(compose(fg.rgb,bg,fg.alpha),bg),large,disabled:element.hasAttribute('disabled')};});
    const active=document.activeElement,style=getComputedStyle(active),bg=background(active.parentElement),outline=parse(style.outlineStyle!=='none'&&parseFloat(style.outlineWidth)>0?style.outlineColor:style.boxShadow);
    return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,colors,focus:{tag:active.tagName,text:active.textContent,outline:style.outline,shadow:style.boxShadow},focusRatio:outline?ratio(compose(outline.rgb,bg,outline.alpha),bg):0};
  });
}
