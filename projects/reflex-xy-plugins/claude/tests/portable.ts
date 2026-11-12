#!/usr/bin/env -S npx tsx
// Run: npm run test:portable -- [--plugin-root <built-plugin> --integration]
// Dependencies are declared in the parent package.json. This harness does not
// impersonate Claude's native test engine; native.test.ts covers that boundary.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { mkdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { register } from "../hooks/register.ts";
import { outputPath, parseRequest, parseResult, parseSavedImage, relativeFile, renderError, PNG_LIMIT, SVG_LIMIT } from "../hooks/helpers.ts";

type Element = { type: string; props: Record<string, any> };
type Handler = ($: any, e: any, next: any) => any;
const source = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const project = path.resolve(source, "..");
const argIndex = process.argv.indexOf("--plugin-root");
const pluginRoot = argIndex >= 0 ? path.resolve(process.argv[argIndex + 1]!) : source;
const integration = process.argv.includes("--integration");
const artifactRoot = path.join(project, "artifacts", "claude-portable");
const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420"><rect width="640" height="420" fill="#ffffff"/></svg>';
let assertions = 0;
let processCalls: { argv: string[]; init: any; spec?: any }[] = [];
let files: Record<string, string> = {};
let copied = "";
let requestFailure = false;
let oversized = false;
let real = false;
let renderGate: Promise<void> | null = null;
let modelCalls = 0;
let promptCalls = 0;

function result(spec: any) {
  return { schema_version: 1, title: spec.title ?? "Portable chart", palette: spec.colorset ?? "colorset1", width: 640, height: 420, factory: "chart", files: { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" }, svg_bytes: oversized ? SVG_LIMIT + 1 : svg.length, png_bytes: oversized ? PNG_LIMIT + 1 : 512, svg_compat_repairs: 0, warnings: [], counts: { marks: 1, rows: 3 } };
}

async function execute(argv: string[], init: any): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  processCalls.push({ argv, init });
  if (argv[1] !== "run") return { exitCode: 0, stdout: argv[0] === "uname" ? "Darwin\n" : "", stderr: "" };
  const spec = JSON.parse(init.stdin);
  processCalls.at(-1)!.spec = spec;
  assert.equal(argv[2], "--script");
  const saveImage = argv[3] === `${pluginRoot}/scripts/save_image.py`;
  if (saveImage) {
    assert.equal(argv[4], "--project-dir");
    assert.equal(argv[5], init.cwd);
    assert.equal(argv[6], "--source-dir");
    assert.ok(argv[7]!.replaceAll("\\", "/").startsWith(init.cwd.replaceAll("\\", "/") + "/.xy-charts/"));
    if (!real) {
      assertions += 6;
      const name = "portable-chart-012345abcdef.png";
      return { exitCode: 0, stderr: "", stdout: JSON.stringify({ schema_version: 1, path: `${init.cwd}/.xy-charts/exports/${name}`, name, bytes: 512, sha256: "a".repeat(64) }) };
    }
  } else {
    assert.equal(argv[3], `${pluginRoot}/runtime/render.py`);
    assert.equal(argv[4], "--skill-dir");
    assert.equal(argv[5], `${pluginRoot}/skills/reflex-xy`);
    assert.equal(argv[6], "--output-dir");
  }
  assert.equal(argv.length, 8);
  assertions += 6;
  if (!real) {
    if (renderGate) await renderGate;
    if (requestFailure) return { exitCode: 2, stdout: "", stderr: '{"error":{"code":"invalid_spec","message":"A real validation error"}}' };
    return { exitCode: 0, stdout: JSON.stringify(result(spec)), stderr: "" };
  }
  return await new Promise((resolve, reject) => {
    const child = spawn(argv[0]!, argv.slice(1), { cwd: init.cwd, env: { ...process.env, ...init.env }, shell: false, windowsHide: true, stdio: ["pipe", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    const timeout = setTimeout(() => { child.kill(); reject(new Error("Renderer timeout")); }, 300_000);
    child.stdout.setEncoding("utf8").on("data", value => { stdout += value; });
    child.stderr.setEncoding("utf8").on("data", value => { stderr += value; });
    child.on("error", error => { clearTimeout(timeout); reject(error); });
    child.on("close", code => { clearTimeout(timeout); resolve({ exitCode: code ?? 1, stdout, stderr }); });
    child.stdin.end(init.stdin);
  });
}

const handlers: { event: string; matcher: Record<string, string>; fn: Handler }[] = [];
register(((event: string, matcherOrHandler: any, handler?: Handler) => {
  handlers.push({ event, matcher: handler ? matcherOrHandler : {}, fn: handler ?? matcherOrHandler });
  return { catch() {} };
}) as any, { uvExecutable: process.env.XY_UV_EXECUTABLE ?? "uv" });

function engine(id: string) {
  const cwd = path.join(artifactRoot, id);
  return {
    plugin: { root: pluginRoot },
    session: { id: async () => id, cwd: async () => cwd },
    clock: { now: async () => real ? Date.now() : 1234 },
    env: { get: async () => "Windows_NT" },
    fs: { read: async (file: string) => files[file] ?? (real ? await readFile(file, "utf8") : svg) },
    process: { run: execute },
    tool: { register: async () => {} },
    command: { register: async () => {} },
    model: { complete: async () => { modelCalls++; throw new Error("Unexpected model call"); } },
    prompt: { submit: async () => { promptCalls++; throw new Error("Unexpected submitted turn"); } },
    ui: {
      invalidate() {}, open: async () => {}, copy: async (value: { text: string }) => { copied = value.text; },
      resolve(event: any) {
        const names = ["Box", "Text", "Button", "Link"];
        if (event.surface !== "mobile") names.push("Select");
        if (event.surface === "terminal") names.push("Image");
        if (event.surface === "desktop" || event.surface === "vscode") names.push("Svg");
        return Object.fromEntries(names.map(type => [type, (props: any) => ({ type, props })]));
      },
    },
  };
}

async function dispatch($: any, event: string, fields: any) {
  const registered = handlers.find(hook => hook.event === event && Object.entries(hook.matcher).every(([key, value]) => fields[key] === value));
  assert.ok(registered, `No ${event} handler`);
  return await registered.fn($, fields, async () => ({ type: "fallback", props: {} }));
}

async function pane($: any, surface: string): Promise<Element> {
  return await dispatch($, "ui.render", { component: "Pane", requestId: "reflex-xy-chart", surface, props: { bodyColumns: 80 } });
}

function flatten(tree: Element): Element[] {
  return [tree, ...(Array.isArray(tree.props.children) ? tree.props.children.filter((child: unknown) => typeof child === "object").flatMap(flatten) : [])];
}

function check(value: unknown, message?: string) { assert.ok(value, message); assertions++; }
function rejectsPath(input: string) { assert.throws(() => relativeFile("/project", input)); assertions++; }

await mkdir(artifactRoot, { recursive: true });
for (const input of ["../outside", "/absolute", "C:/outside", "https://host/thing", "a//b", "a/./b", "a/../../b", "\\\\server\\file", "a\u0000b"]) rejectsPath(input);
check(relativeFile("C:\\Project Folder", "charts/request.json") === "C:\\Project Folder/charts/request.json");
check(outputPath("/work", "../secret", 42, 1) === "/work/.xy-charts/___secret-42-1");
check(parseRequest("colorset2 scatter").colorset === "colorset2");
check(parseRequest('{"preset":"bar","colorset":"colorset1"}').colorset === "colorset1");
check(renderError('{"error":{"message":"Invalid mark"}}', "fallback") === "Invalid mark");
assert.throws(() => parseResult(JSON.stringify({ ...result({}), files: { ...result({}).files, html: "../outside.html" } }), "/root")); assertions++;
assert.throws(() => parseSavedImage(JSON.stringify({ schema_version: 1, path: "/outside/chart-012345abcdef.png", name: "chart-012345abcdef.png", bytes: 512, sha256: "a".repeat(64) }), "/root")); assertions++;

const a = engine("session-a");
const b = engine("session-b");
await mkdir(await a.session.cwd(), { recursive: true });
await mkdir(await b.session.cwd(), { recursive: true });
const literalTitle = 'Revenue $(touch forbidden) `literal` <script>alert("x")</script>';
let rendered = await dispatch(a, "command.run", { command: "xy-chart", args: JSON.stringify({ preset: "line", colorset: "colorset2", title: literalTitle }) });
check(rendered.text.includes("XY chart created"));
check(processCalls.at(-1)!.spec.title === literalTitle);
check(!processCalls.at(-1)!.argv.some(arg => arg.includes(literalTitle)));
files[`${await a.session.cwd()}/omitted.json`] = '{"preset":"line"}';
files[`${await a.session.cwd()}/explicit.json`] = '{"preset":"line","colorset":"colorset2"}';
for (const omitted of ["", "bar", '{"preset":"scatter"}', "@omitted.json"]) {
  await dispatch(a, "command.run", { command: "xy-chart", args: "colorset2 line" });
  check(processCalls.at(-1)!.spec.colorset === "colorset2");
  const fresh = await dispatch(a, "command.run", { command: "xy-chart", args: omitted });
  check(fresh.text.includes("XY chart created"));
  check(processCalls.at(-1)!.spec.colorset === "colorset1", `Omitted palette must reset to Colorset 1 for ${omitted || "an empty command"}`);
}
await dispatch(a, "tool.call", { tool: "mcp__reflex-xy__render_chart", spec: { preset: "line", colorset: "colorset2" } });
check(processCalls.at(-1)!.spec.colorset === "colorset2");
await dispatch(a, "tool.call", { tool: "mcp__reflex-xy__render_chart", spec: { preset: "line" } });
check(processCalls.at(-1)!.spec.colorset === "colorset1");
await dispatch(a, "command.run", { command: "xy-chart", args: "@explicit.json" });
check(processCalls.at(-1)!.spec.colorset === "colorset2");
const simpleNodes = flatten(await pane(a, "desktop"));
check(simpleNodes.filter(node => node.type === "Button").length === 2, "The default chart view has one primary action and one options toggle");
check(simpleNodes.some(node => node.props.key === "save-image" && node.props.label === "Save image"));
check(!simpleNodes.some(node => node.props.key === "open-html"));
check(simpleNodes.some(node => node.props.key === "more-options" && node.props.label === "More options"));
check(!simpleNodes.some(node => node.type === "Text" && node.props.children === "Portable chart"), "The native image already contains the chart title");
check(!simpleNodes.some(node => node.props.autoFocus === true), "Rerenders must not request focus away from the user's current control");
check(!simpleNodes.some(node => node.type === "Select" || node.props.key === "copy-source" || node.props.key === "reload"));
check(!simpleNodes.some(node => typeof node.props.children === "string" && /Python XY|Artifact directory/.test(node.props.children)));
simpleNodes.find(node => node.props.key === "more-options")!.props.onPress();
check(!flatten(await pane(a, "desktop")).some(node => typeof node.props.children === "string" && /Python XY|640 × 420/.test(node.props.children)));
const presetControl = flatten(await pane(a, "desktop")).find(node => node.props.key === "preset")!;
check(presetControl.props.label.includes("replaces current data"));
await presetControl.props.onSelect("bar");
await new Promise(resolve => setTimeout(resolve, 5));
check(processCalls.at(-1)!.spec.colorset === "colorset2", "An explicit pane edit retains its selected palette");
for (const surface of ["terminal", "desktop", "vscode", "mobile"]) {
  const nodes = flatten(await pane(a, surface));
  check(nodes.some(node => node.props.key === "open-html"));
  check(nodes.some(node => node.props.key === "copy-source"));
  check(nodes.some(node => node.type === "Svg") === ["desktop", "vscode"].includes(surface));
  check(nodes.some(node => node.type === "Image") === (surface === "terminal"));
  check(nodes.some(node => node.type === "Select") === (surface !== "mobile"));
}
check(!flatten(await pane(b, "desktop")).some(node => node.type === "Svg"), "Other sessions must not see a prior chart");
check(!flatten(await pane(b, "desktop")).some(node => node.type === "Select"), "Other sessions must not inherit expanded options");
const copy = flatten(await pane(a, "desktop")).find(node => node.props.key === "copy-source")!;
const previousCalls = processCalls.length;
await copy.props.onPress();
check(copied.endsWith("/chart.py"));
check(processCalls.length === previousCalls, "Copying source must never execute or OS-open Python");
const beforeSave = processCalls.length;
const saveButton = flatten(await pane(a, "desktop")).find(node => node.props.key === "save-image")!;
await saveButton.props.onPress();
await new Promise(resolve => setTimeout(resolve, 5));
check(processCalls.length === beforeSave + 1);
check(processCalls.at(-1)!.argv[3] === `${pluginRoot}/scripts/save_image.py`);
check(flatten(await pane(a, "desktop")).some(node => node.type === "Text" && node.props.children === "Image saved."));
check(flatten(await pane(a, "desktop")).some(node => node.props.key === "copy-saved-image"));
check(modelCalls === 0 && promptCalls === 0);
const open = flatten(await pane(a, "desktop")).find(node => node.props.key === "open-html")!;
await open.props.onPress();
await new Promise(resolve => setTimeout(resolve, 5));
check(processCalls.at(-1)!.argv[0] === "explorer.exe");
check(processCalls.at(-1)!.argv.length === 2);
check(processCalls.at(-1)!.argv[1]!.endsWith("/chart.html"));

requestFailure = true;
rendered = await dispatch(a, "command.run", { command: "xy-chart", args: "bar" });
check(rendered.text.includes("A real validation error"));
check(flatten(await pane(a, "desktop")).some(node => node.type === "Svg"), "A failed render must retain the previous artifact");
requestFailure = false;
oversized = true;
await dispatch(b, "command.run", { command: "xy-chart", args: "colorset1 line" });
check(!flatten(await pane(b, "desktop")).some(node => node.type === "Svg"));
check(!flatten(await pane(b, "terminal")).some(node => node.type === "Image"));
oversized = false;
const reference = await dispatch(a, "tool.call", { tool: "mcp__reflex-xy__skill_reference", path: "../private" });
check(reference.isError === true);
const beforeInvalid = processCalls.length;
await dispatch(a, "command.run", { command: "xy-chart", args: "@../private.json" });
check(processCalls.length === beforeInvalid);
const refPath = `${pluginRoot}/skills/reflex-xy/references/colorsets.md`;
files[refPath] = "Exact palette guidance";
const guidance = await dispatch(a, "tool.call", { tool: "mcp__reflex-xy__skill_reference", path: "references/colorsets.md" });
check(guidance.result.text === "Exact palette guidance");

// Loading is a real intermediate state: the process promise remains pending.
const loadingHost = engine("loading-session");
await mkdir(await loadingHost.session.cwd(), { recursive: true });
let finishRender!: () => void;
renderGate = new Promise<void>(resolve => { finishRender = resolve; });
const pendingRender = dispatch(loadingHost, "command.run", { command: "xy-chart", args: "line" });
await new Promise(resolve => setTimeout(resolve, 5));
const loadingNodes = flatten(await pane(loadingHost, "desktop"));
check(loadingNodes.some(node => node.type === "Text" && node.props.children === "Creating your chart…"));
check(!loadingNodes.some(node => node.type === "Select" || node.props.key === "create-chart" || node.props.key === "reload"));
check(loadingNodes.filter(node => node.type === "Button").length === 1);
finishRender();
await pendingRender;
renderGate = null;
const readyNodes = flatten(await pane(loadingHost, "desktop"));
check(readyNodes.some(node => node.type === "Svg"));
check(readyNodes.filter(node => node.type === "Button").length === 2);

const failedHost = engine("failed-session");
requestFailure = true;
await dispatch(failedHost, "command.run", { command: "xy-chart", args: JSON.stringify({ preset: "line", title: "Preserved input", data: { x: [1, 2], y: [5, 8] } }) });
const failedNodes = flatten(await pane(failedHost, "desktop"));
check(failedNodes.some(node => node.type === "Text" && node.props.children === "A real validation error"));
const retry = failedNodes.find(node => node.props.key === "create-chart")!;
check(retry.props.label === "Try again");
requestFailure = false;
await retry.props.onPress();
await new Promise(resolve => setTimeout(resolve, 5));
check(processCalls.at(-1)!.spec.title === "Preserved input");
check(JSON.stringify(processCalls.at(-1)!.spec.data) === '{"x":[1,2],"y":[5,8]}');
check(!flatten(await pane(failedHost, "desktop")).some(node => node.type === "Text" && node.props.children === "A real validation error"));

let integrationArtifacts: string[] = [];
if (integration) {
  check(existsSync(path.join(pluginRoot, "runtime", "render.py")), "Build the plugin before running --integration");
  real = true;
  files = {};
  for (const palette of ["colorset1", "colorset2"]) {
    const host = engine(`real-${palette}`);
    await mkdir(await host.session.cwd(), { recursive: true });
    const answer = await dispatch(host, "tool.call", { tool: "mcp__reflex-xy__render_chart", spec: { preset: "line", colorset: palette, title: `Claude adapter ${palette}` } });
    check(!answer.isError, JSON.stringify(answer));
    check(answer.result.palette === palette);
    const artifacts = Object.values(answer.result.absolute_files) as string[];
    check(artifacts.length === 5);
    for (const artifact of artifacts) check(existsSync(artifact));
    const svgNodes = flatten(await pane(host, "desktop")).filter(node => node.type === "Svg");
    check(svgNodes.length === 1);
    check(svgNodes[0]!.props.source.startsWith("<svg") || svgNodes[0]!.props.source.startsWith("<?xml"));
    check(readFileSync(answer.result.absolute_files.html, "utf8").includes("<html"));
    const localSave = flatten(await pane(host, "desktop")).find(node => node.props.key === "save-image")!;
    await localSave.props.onPress();
    const deadline = Date.now() + 60_000;
    let savedNodes: Element[] = [];
    while (Date.now() < deadline) {
      savedNodes = flatten(await pane(host, "desktop"));
      if (savedNodes.some(node => node.type === "Text" && node.props.children === "Image saved.")) break;
      const error = savedNodes.find(node => node.type === "Text" && String(node.props.children).startsWith("Could not save the image:"));
      if (error) throw new Error(String(error.props.children));
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    check(savedNodes.some(node => node.type === "Text" && node.props.children === "Image saved."));
    savedNodes.find(node => node.props.key === "more-options")!.props.onPress();
    const savedCopy = flatten(await pane(host, "desktop")).find(node => node.props.key === "copy-saved-image")!;
    await savedCopy.props.onPress();
    await new Promise(resolve => setTimeout(resolve, 5));
    check(existsSync(copied));
    check(readFileSync(copied).equals(readFileSync(answer.result.absolute_files.png)), "Native Save image must preserve the actual XY PNG bytes");
    integrationArtifacts.push(answer.result.output_dir);
  }
}
check(modelCalls === 0 && promptCalls === 0);
console.log(JSON.stringify({ status: "passed", assertions, native_host: false, renderer_integration: integration, integration_artifacts: integrationArtifacts, subprocess_calls: processCalls.length, model_calls: modelCalls, submitted_turns: promptCalls }, null, 2));
