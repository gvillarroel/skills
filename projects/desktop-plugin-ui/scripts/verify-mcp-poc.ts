#!/usr/bin/env node
// Run with Node 24 native TypeScript: node projects/desktop-plugin-ui/scripts/verify-mcp-poc.ts <package-review.json> <output-directory>
// Evaluator tooling dependencies: projects/desktop-plugin-ui/mcp-probe/package.json (locked MCP SDK 1.32.1 and Playwright 1.64.1).
// This evaluator is outside the shipped skill and never repairs generated files.
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createHash } from "node:crypto";

const [packageFile, outputArgument] = process.argv.slice(2);
if (!packageFile || !outputArgument) throw new Error("Usage: verify-mcp-poc.ts <package-review.json> <output-directory>");
const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const output = path.resolve(outputArgument);
if (!output.startsWith(path.join(repository, "projects/desktop-plugin-ui/artifacts") + path.sep)) throw new Error("Evaluator output must stay inside project artifacts");
await mkdir(path.dirname(output), { recursive: true });
await mkdir(output, { recursive: false });
const taskTemporary = path.join(output, "tmp");
await mkdir(taskTemporary, { recursive: true });
for (const name of ["TMP", "TEMP", "TMPDIR"]) process.env[name] = taskTemporary;
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(output, "browser-cache");
process.env.NODE_DISABLE_COMPILE_CACHE = "1";
const screenshots = path.join(repository, "projects/desktop-plugin-ui/artifacts/plugin-pocs/screenshots", path.basename(output));
await mkdir(screenshots, { recursive: true });
const packageReview = JSON.parse(await readFile(packageFile, "utf8"));
const dependencies = path.join(repository, "projects/desktop-plugin-ui/mcp-probe/node_modules");
const { Client } = await import(pathToFileURL(path.join(dependencies, "@modelcontextprotocol/sdk/dist/esm/client/index.js")).href);
const { StdioClientTransport } = await import(pathToFileURL(path.join(dependencies, "@modelcontextprotocol/sdk/dist/esm/client/stdio.js")).href);
const { chromium } = await import(pathToFileURL(path.join(dependencies, "playwright/index.mjs")).href);
const checks = [];
const observations = {};
function check(name, condition, detail = {}, layer = "protocol") { checks.push({ name, status: condition ? "pass" : "fail", layer, ...detail }); }
function skipped(name, reason, layer) { checks.push({ name, status: "untested", layer, reason }); }
async function attempt(name, operation, layer = "protocol") {
  try { const result = await operation(); check(name, true, {}, layer); return result; }
  catch (error) { check(name, false, { error: String(error) }, layer); return undefined; }
}
const expected = {
  all: [{ id: "T-104", status: "pending", priority: "high" }, { id: "T-105", status: "pending", priority: "normal" }, { id: "T-106", status: "closed", priority: "high" }],
  pending: [{ id: "T-104", status: "pending", priority: "high" }, { id: "T-105", status: "pending", priority: "normal" }],
  high: [{ id: "T-104", status: "pending", priority: "high" }, { id: "T-106", status: "closed", priority: "high" }],
};
function verifyResult(result, filter, prefix) {
  const data = result?.structuredContent;
  const actualRows = data?.rows?.map(row => ({ id: row.id, status: row.status, priority: row.priority })).sort((left, right) => left.id.localeCompare(right.id));
  check(`${prefix}:authoritative-rows`, !result?.isError && JSON.stringify(actualRows) === JSON.stringify(expected[filter]), { actual: actualRows, expected: expected[filter] });
  check(`${prefix}:filter-and-count`, data?.filter === filter && data?.count === expected[filter].length, { actual: data });
  const text = result?.content?.filter(item => item.type === "text").map(item => item.text).join("\n") ?? "";
  check(`${prefix}:plain-text-fallback`, expected[filter].every(row => text.includes(row.id) && text.includes(row.status) && text.includes(row.priority)), { actual: text });
}

let client, transport, initial, html, serverStderr = "";
const launch = packageReview.launch;
try {
  const review = JSON.parse(await readFile(path.join(packageReview.poc, "review.json"), "utf8"));
  const ids = Array.isArray(review.heuristics) ? review.heuristics.map(item => item.id) : Object.keys(review.heuristics ?? {});
  check("review-ten-heuristics", Array.from({ length: 10 }, (_, i) => `H${i + 1}`).every(id => ids.includes(id)), { actual: ids }, "artifact-inspection");
  check("review-no-unperformed-live-or-user-claim", review.host_acceptance_verified === false && review.user_testing_performed === false, {}, "artifact-inspection");
  check("review-default-palette", /colorset\s*1/i.test(JSON.stringify(review.palette)), { actual: review.palette }, "artifact-inspection");
} catch (error) { check("review-json", false, { error: String(error) }, "artifact-inspection"); }
try {
  if (!launch) throw new Error("No usable extracted launch declaration");
  const env = Object.fromEntries(Object.entries(process.env).filter(([key, value]) => typeof value === "string" && !/(API_KEY|ACCESS_TOKEN|SECRET|CREDENTIAL)/i.test(key)));
  delete env.NODE_PATH;
  delete env.NODE_OPTIONS;
  Object.assign(env, launch.env ?? {});
  transport = new StdioClientTransport({ command: process.execPath, args: launch.args, cwd: launch.cwd, env, stderr: "pipe" });
  transport.stderr?.on("data", data => { serverStderr += String(data); });
  client = new Client({ name: "independent-queue-poc-evaluator", version: "1.0.0" });
  await client.connect(transport);
  check("extracted-runtime-initializes", true, { version: client.getServerVersion() });
  const tools = await client.listTools();
  observations.tools = tools.tools;
  const opener = tools.tools.find(tool => tool.name === "queue_open");
  const filterTool = tools.tools.find(tool => tool.name === "queue_filter");
  check("required-tools-discovered", Boolean(opener && filterTool), { actual: tools.tools.map(tool => tool.name) });
  check("filter-app-only-metadata", JSON.stringify(filterTool?._meta?.ui?.visibility) === JSON.stringify(["app"]), { actual: filterTool?._meta });
  const uri = opener?._meta?.ui?.resourceUri;
  check("portable-resource-association", typeof uri === "string" && uri.startsWith("ui://"), { actual: uri });
  if (uri) {
    const resources = await client.listResources();
    check("resource-discovery", resources.resources.some(resource => resource.uri === uri), { actual: resources.resources });
    const resource = await client.readResource({ uri });
    const component = resource.contents.find(item => item.uri === uri) ?? resource.contents[0];
    html = component.text;
    observations.resource = { uri, mimeType: component.mimeType, meta: component._meta, bytes: Buffer.byteLength(html ?? "") };
    check("mcp-app-html-resource", component.mimeType === "text/html;profile=mcp-app" && typeof html === "string" && html.length > 100, observations.resource);
    const runtimeHtml = await readFile(path.join(packageReview.extracted, "dist/ui.html"), "utf8");
    check("resource-equals-packaged-ui", html === runtimeHtml, { sha256: createHash("sha256").update(html ?? "").digest("hex") });
    check("local-resource-no-foreign-host-domain", !component._meta?.ui?.domain, { actual: component._meta?.ui?.domain });
  }
  initial = await client.callTool({ name: "queue_open", arguments: {} });
  verifyResult(initial, "all", "open");
  for (const filter of ["all", "pending", "high"]) verifyResult(await client.callTool({ name: "queue_filter", arguments: { filter } }), filter, `filter-${filter}`);
  for (const [name, call] of [
    ["invalid-filter-rejected", { name: "queue_filter", arguments: { filter: "broken" } }],
    ["missing-filter-rejected", { name: "queue_filter", arguments: {} }],
    ["unknown-tool-rejected", { name: "unexpected_tool", arguments: {} }],
  ]) {
    try { const result = await client.callTool(call); check(name, result.isError === true, { actual: result }); }
    catch (error) { check(name, true, { refusal: String(error) }); }
  }
  const reopened = await client.callTool({ name: "queue_open", arguments: {} });
  verifyResult(reopened, "all", "reopen-default-not-mutated");
} catch (error) { check("extracted-runtime-protocol-flow", false, { error: String(error) }); }

let browser;
const bridgeCalls = [], browserRequests = [], browserErrors = [];
if (html && initial && client) {
  try {
    browser = await chromium.launch({ headless: true, channel: "msedge" });
    observations.browserVersion = browser.version();
    observations.browserTemporaryDirectory = taskTemporary;
    observations.browserTemporaryEntries = await readdir(taskTemporary);
    let failNext = false, holdNext = false, releaseHeld;
    const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
    page.on("pageerror", error => { browserErrors.push(error.message); });
    await page.route(/^https?:\/\//, async route => { browserRequests.push(route.request().url()); await route.abort(); });
    await page.exposeFunction("queueEvaluatorRpc", async (method, params) => {
      bridgeCalls.push({ method, params });
      if (method === "ui/initialize") return { protocolVersion: params.protocolVersion, hostInfo: { name: "independent-sandbox-fixture", version: "1.0.0" }, hostCapabilities: { serverTools: {} }, hostContext: { theme: "light", displayMode: "inline", availableDisplayModes: ["inline"], containerDimensions: { width: 900, maxHeight: 900 } } };
      if (method === "tools/call") {
        if (holdNext) { holdNext = false; await new Promise(resolve => { releaseHeld = resolve; }); }
        if (failNext) { failNext = false; return { isError: true, content: [{ type: "text", text: "Synthetic service error. Retry the selected view." }] }; }
        return client.callTool(params);
      }
      if (["ui/message", "sampling/createMessage"].includes(method)) throw new Error("Unexpected model work from deterministic control");
      if (method === "ui/update-model-context") return {};
      throw new Error(`Unsupported fixture request ${method}`);
    });
    await mount(page, html, initial);
    const frame = page.frameLocator("#queue-poc");
    await frame.getByLabel("View", { exact: true }).waitFor({ timeout: 15000 });
    await page.waitForTimeout(200);
    const view = frame.getByLabel("View", { exact: true });
    const apply = frame.getByRole("button", { name: "Apply", exact: true });
    const cancel = frame.getByRole("button", { name: "Cancel", exact: true });
    const toolCount = () => bridgeCalls.filter(call => call.method === "tools/call").length;
    const rowsVisible = async filter => {
      const text = await frame.locator("body").innerText();
      return ["T-104", "T-105", "T-106"].every(id => text.includes(id) === expected[filter].some(row => row.id === id));
    };
    check("browser-initial-all-rows", await rowsVisible("all"), {}, "browser-fixture");
    check("authored-language-en", (await frame.locator("html").getAttribute("lang")) === "en", {}, "browser-fixture");
    const beforeDraft = toolCount();
    await view.selectOption({ label: "Pending tickets" });
    check("draft-no-server-call", toolCount() === beforeDraft && await rowsVisible("all"), {}, "browser-fixture");
    await cancel.click();
    check("cancel-restores-committed-view-without-call", toolCount() === beforeDraft && (await view.locator("option:checked").innerText()) === "All tickets" && await rowsVisible("all"), {}, "browser-fixture");
    await view.selectOption({ label: "Pending tickets" });
    holdNext = true;
    await apply.click();
    for (let i = 0; i < 50 && !releaseHeld; i++) await page.waitForTimeout(20);
    const busyText = await frame.locator("body").innerText();
    check("busy-status-and-duplicate-submit-prevention", Boolean(releaseHeld) && await apply.isDisabled() && /(loading|applying|working|updating|busy)/i.test(busyText), { actual: busyText }, "browser-fixture");
    releaseHeld?.();
    for (let i = 0; i < 100 && !(await rowsVisible("pending")); i++) await page.waitForTimeout(20);
    check("apply-direct-tool-filter", toolCount() === beforeDraft + 1 && await rowsVisible("pending"), {}, "browser-fixture");
    await view.selectOption({ label: "High priority" });
    failNext = true;
    await apply.click();
    const retry = frame.getByRole("button", { name: "Retry", exact: true });
    await retry.waitFor({ timeout: 8000 });
    check("failure-preserves-prior-result-and-draft", await rowsVisible("pending") && (await view.locator("option:checked").innerText()) === "High priority", {}, "browser-fixture");
    const errorText = await frame.locator("[role=alert], [role=status]").allTextContents();
    check("useful-error-feedback", /error|retry|failed|could not|unable/i.test(errorText.join(" ")), { actual: errorText }, "browser-fixture");
    const errorContrast = await inspectContrast(frame);
    observations.errorContrast = errorContrast;
    check("visible-error-state-text-contrast", errorContrast.every(item => item.disabled || item.ratio >= (item.large ? 3 : 4.5)), { failing: errorContrast.filter(item => !item.disabled && item.ratio < (item.large ? 3 : 4.5)) }, "browser-fixture");
    await retry.click();
    for (let i = 0; i < 100 && !(await rowsVisible("high")); i++) await page.waitForTimeout(20);
    check("retry-direct-tool-success", await rowsVisible("high") && toolCount() === beforeDraft + 3, {}, "browser-fixture");
    await view.selectOption({ label: "All tickets" });
    await view.focus(); await view.press("Tab");
    const focus = await frame.locator("body").evaluate(() => {
      const active = document.activeElement; const style = active ? getComputedStyle(active) : null;
      const parse = value => { const match = value?.match(/rgba?\(([^)]+)\)/); return match ? match[1].split(",").map(Number) : null; };
      let background = [255,255,255], element = active?.parentElement;
      while(element) { const color = parse(getComputedStyle(element).backgroundColor); if(color && (color[3] ?? 1) === 1) { background = color.slice(0,3); break; } element = element.parentElement; }
      const foreground = parse(style?.outlineStyle !== "none" && parseFloat(style?.outlineWidth ?? "0") > 0 ? style?.outlineColor : style?.boxShadow);
      const linear = value => { value /= 255; return value <= .04045 ? value / 12.92 : Math.pow((value + .055) / 1.055, 2.4); };
      const luminance = rgb => .2126*linear(rgb[0])+.7152*linear(rgb[1])+.0722*linear(rgb[2]);
      const alpha = foreground?.[3] ?? 1; const composed = foreground?.slice(0,3).map((value,index)=>value*alpha+background[index]*(1-alpha));
      const ratio = composed ? (Math.max(luminance(composed),luminance(background))+.05)/(Math.min(luminance(composed),luminance(background))+.05) : 0;
      return { tag: active?.tagName, text: active?.textContent, outline: style?.outlineStyle, boxShadow: style?.boxShadow, foreground, background, ratio };
    });
    check("keyboard-reaches-action-with-focus-cue", focus.tag === "BUTTON" && (focus.outline !== "none" || focus.boxShadow !== "none"), { actual: focus }, "browser-fixture");
    check("computed-focus-indicator-contrast", focus.ratio >= 3, { actual: focus }, "browser-fixture");
    const beforeKeyboard = toolCount();
    await apply.press("Enter");
    for (let i = 0; i < 100 && !(await rowsVisible("all")); i++) await page.waitForTimeout(20);
    check("keyboard-enter-runs-primary-action-in-sandbox", toolCount() === beforeKeyboard + 1 && await rowsVisible("all"), {}, "browser-fixture");
    await view.selectOption({ label: "High priority" });
    await apply.focus(); const beforeSpace = toolCount(); await apply.press("Space");
    for (let i = 0; i < 100 && !(await rowsVisible("high")); i++) await page.waitForTimeout(20);
    check("keyboard-space-runs-primary-action-in-sandbox", toolCount() === beforeSpace + 1 && await rowsVisible("high"), {}, "browser-fixture");
    for (const width of [900, 320]) {
      await page.setViewportSize({ width, height: 900 });
      const dimensions = await frame.locator("html").evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
      check(`layout-no-horizontal-overflow-${width}`, dimensions.scroll <= dimensions.width + 1 && dimensions.body <= dimensions.width + 1, { actual: dimensions }, "browser-fixture");
      await page.screenshot({ path: path.join(screenshots, `queue-${width}.png`), fullPage: true });
    const colors = await inspectContrast(frame);
    observations.contrast ??= {};
    observations.contrast[width] = colors;
    check(`visible-text-contrast-${width}`, colors.every(item => item.disabled || item.ratio >= (item.large ? 3 : 4.5)), { failing: colors.filter(item => !item.disabled && item.ratio < (item.large ? 3 : 4.5)) }, "browser-fixture");
    }
    const paletteText = await readFile(path.join(repository, "skills/desktop-plugin-ui/assets/palettes/colorset1.yml"), "utf8");
    const paletteColors = new Set([...paletteText.matchAll(/value:\s*["'](#[a-f0-9]{6})["']/gi)].map(match => match[1].toLowerCase()));
    const styleText = [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map(match => match[1]).join("\n");
    const authoredHex = [...new Set([...styleText.matchAll(/#[a-f0-9]{3,8}\b/gi)].map(match => match[0].toLowerCase()).map(value => value.length === 4 ? "#" + [...value.slice(1)].map(character => character + character).join("") : value))];
    check("authored-css-hex-values-in-colorset1", authoredHex.every(value => paletteColors.has(value)), { authoredHex, unexpected: authoredHex.filter(value => !paletteColors.has(value)), limitation: "Literal CSS hex declarations only; host-owned/native theme paint and runtime variables require separate review." }, "artifact-inspection");
    check("no-browser-runtime-network", browserRequests.length === 0, { actual: browserRequests }, "browser-fixture");
    check("no-unhandled-browser-errors", browserErrors.length === 0, { actual: browserErrors }, "browser-fixture");
    check("no-deterministic-model-message-or-sampling", !bridgeCalls.some(call => ["ui/message", "sampling/createMessage"].includes(call.method)), {}, "browser-fixture");
    await page.close();

    const rejected = await browser.newPage({ viewport: { width: 900, height: 900 } });
    await rejected.exposeFunction("queueEvaluatorRpc", async method => { if (method === "ui/initialize") throw new Error("Synthetic host initialization unavailable"); return {}; });
    await mount(rejected, html, initial);
    await rejected.waitForTimeout(700);
    const rejectedText = await rejected.frameLocator("#queue-poc").locator("body").innerText();
    check("host-initialization-failure-visible", /(unavailable|failed|could not|unable|cannot|error|not connected)/i.test(rejectedText), { actual: rejectedText }, "browser-fixture");
    const rejectedContrast = await inspectContrast(rejected.frameLocator("#queue-poc"));
    observations.initializationFailureContrast = rejectedContrast;
    check("initialization-failure-text-contrast", rejectedContrast.every(item => item.disabled || item.ratio >= (item.large ? 3 : 4.5)), { failing: rejectedContrast.filter(item => !item.disabled && item.ratio < (item.large ? 3 : 4.5)) }, "browser-fixture");
    await rejected.screenshot({ path: path.join(screenshots, "initialization-failure.png"), fullPage: true });
    await rejected.close();
  } catch (error) { check("browser-interaction-flow", false, { error: String(error), methods: bridgeCalls }, "browser-fixture"); }
} else skipped("browser-interaction-flow", "Extracted protocol/resource initialization did not provide usable HTML and result", "browser-fixture");

await browser?.close();
await client?.close();
await transport?.close();
await writeFile(path.join(output, "server-stderr.txt"), serverStderr);
await writeFile(path.join(output, "bridge-calls.json"), JSON.stringify(bridgeCalls, null, 2));
const report = { passed: checks.length > 0 && checks.every(item => item.status === "pass"), checks, observations, browserRequests, browserErrors, host_acceptance_verified: false, user_testing_performed: false, scope: "Extracted actual stdio server + actual UI in sandboxed evaluator bridge/browser; real Desktop paint and installation remain untested." };
await writeFile(path.join(output, "runtime-review.json"), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ passed: report.passed, checks: checks.length, failed: checks.filter(item => item.status !== "pass").map(item => item.name), report: path.join(output, "runtime-review.json") }));
process.exitCode = report.passed ? 0 : 1;

async function mount(page, html, initial) {
  await page.setContent('<!doctype html><html lang="en"><body style="margin:0"><iframe id="queue-poc" title="Queue PoC protocol fixture" sandbox="allow-scripts" style="border:0;width:100%;height:850px"></iframe></body></html>');
  await page.evaluate(({ html, initial }) => {
    const frame = document.getElementById("queue-poc");
    window.addEventListener("message", async event => {
      if (event.source !== frame.contentWindow || event.data?.jsonrpc !== "2.0") return;
      const message = event.data;
      if (message.method === "ui/notifications/initialized") { frame.contentWindow.postMessage({ jsonrpc: "2.0", method: "ui/notifications/tool-result", params: initial }, "*"); return; }
      if (message.id !== undefined) {
        try { const result = await window.queueEvaluatorRpc(message.method, message.params ?? {}); frame.contentWindow.postMessage({ jsonrpc: "2.0", id: message.id, result }, "*"); }
        catch (error) { frame.contentWindow.postMessage({ jsonrpc: "2.0", id: message.id, error: { code: -32603, message: String(error) } }, "*"); }
      }
    });
    frame.srcdoc = html;
  }, { html, initial });
}

async function inspectContrast(frame) {
  return frame.locator("body").evaluate(() => {
    const parse = value => { const match = value.match(/^rgba?\(([^)]+)\)/); if (!match) return null; const values = match[1].split(",").map(Number); return { rgb: values.slice(0, 3), alpha: values[3] ?? 1 }; };
    const compose = (foreground, background, alpha) => foreground.map((value, index) => value * alpha + background[index] * (1 - alpha));
    const linear = value => { value /= 255; return value <= .04045 ? value / 12.92 : Math.pow((value + .055) / 1.055, 2.4); };
    const luminance = rgb => .2126 * linear(rgb[0]) + .7152 * linear(rgb[1]) + .0722 * linear(rgb[2]);
    return Array.from(document.querySelectorAll("h1,h2,p,label,button,td,th,li,output,[role=alert]")).filter(element => element.getBoundingClientRect().width > 0 && element.textContent?.trim()).map(element => {
      const style = getComputedStyle(element); let current = element; const layers = []; let opacity = 1;
      while (current) { const computed = getComputedStyle(current); const layer = parse(computed.backgroundColor); if (layer) layers.unshift(layer); opacity *= Number(computed.opacity); current = current.parentElement; }
      let background = [255,255,255]; for (const layer of layers) background = compose(layer.rgb, background, layer.alpha);
      const color = parse(style.color) ?? { rgb: [0,0,0], alpha: 1 }; const foreground = compose(color.rgb, background, color.alpha);
      const a = luminance(foreground), b = luminance(background); const ratio = (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
      const large = parseFloat(style.fontSize) >= 24 || (parseFloat(style.fontSize) >= 18.667 && Number(style.fontWeight) >= 700);
      return { tag: element.tagName, text: element.textContent?.trim().slice(0,80), foreground, background, ratio, large, disabled: element.hasAttribute("disabled"), fontSize: style.fontSize, opacity, limitation: opacity === 1 ? undefined : "Element opacity is recorded; complex group-opacity compositing requires separate review." };
    });
  });
}
