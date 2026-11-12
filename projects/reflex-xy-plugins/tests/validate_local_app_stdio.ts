#!/usr/bin/env -S npx tsx
// Run with the project's locked tsx: node chatgpt/node_modules/tsx/dist/cli.mjs
// tests/validate_local_app_stdio.ts --root <extracted-plugin> --kind portable|mcpb
// --output-dir <project-artifacts> --sdk-root <@modelcontextprotocol/sdk/dist/esm>
// Requires Node 22+, uv, and the project's locked MCP SDK and tsx tooling.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

async function main() {
  const options: Record<string, string> = {};
  for (let i = 2; i < process.argv.length; i += 2) options[process.argv[i]!.replace(/^--/, "")] = process.argv[i + 1]!;
  for (const key of ["root", "kind", "output-dir", "sdk-root"]) assert.ok(options[key], `Missing --${key}`);
  assert.ok(["portable", "mcpb"].includes(options.kind!));
  const root = path.resolve(options.root!);
  const output = path.resolve(options["output-dir"]!);
  try { await readFile(path.join(output, "report.json")); throw new Error("Preserve prior evidence; choose a new output directory."); }
  catch (error: any) { if (error.code !== "ENOENT") throw error; }
  await mkdir(output, { recursive: true });
  const { Client } = await import(pathToFileURL(path.join(options["sdk-root"]!, "client/index.js")).href);
  const { StdioClientTransport } = await import(pathToFileURL(path.join(options["sdk-root"]!, "client/stdio.js")).href);
  const manifestFile = options.kind === "portable" ? "mcp.json" : "manifest.json";
  const manifest = JSON.parse(await readFile(path.join(root, manifestFile), "utf8"));
  const declared = options.kind === "portable" ? manifest.mcpServers.xy : manifest.server.mcp_config;
  if (options.kind === "portable") assert.ok(!JSON.stringify(declared).includes("${PLUGIN_ROOT}"), "The observed Codex 0.145 loader leaves this placeholder literal.");
  const substitutions: Record<string, string> = { PLUGIN_ROOT: root, __dirname: root, "user_config.uvExecutable": "uv", "user_config.artifactDirectory": path.join(output, "runtime") };
  const substitute = (value: string) => value.replace(/\$\{([^}]+)\}/g, (_, key) => { assert.ok(Object.hasOwn(substitutions, key), `Unknown placeholder: ${key}`); return substitutions[key]!; });
  const env: Record<string, string> = Object.fromEntries(Object.entries(process.env).filter((x): x is [string, string] => typeof x[1] === "string"));
  for (const name of ["XY_PYTHON", "XY_PUBLIC_BASE_URL", "XY_WIDGET_DOMAIN", "XY_MCP_BEARER_TOKEN"]) delete env[name];
  for (const [key, value] of Object.entries(declared.env ?? {})) env[key] = substitute(String(value));
  env.XY_RUNTIME_DIR = path.join(output, "runtime");
  env.UV_CACHE_DIR = path.join(output, "uv-cache");
  env.PYTHONDONTWRITEBYTECODE = "1";
  env.PYTHONIOENCODING = "utf-8";
  const command = substitute(declared.command);
  const args = declared.args.map(substitute);
  const cwd = path.resolve(root, substitute(declared.cwd ?? "${PLUGIN_ROOT}"));
  assert.ok(args.includes("--stdio") && args.includes("--desktop"));
  const transport = new StdioClientTransport({ command, args, env, cwd, stderr: "pipe" });
  let diagnostics = "";
  transport.stderr?.on("data", (value: Buffer) => { diagnostics += String(value); });
  const client = new Client({ name: "independent-local-app-acceptance", version: "0.3.1" });
  const report: Record<string, unknown> = { passed: false, package_kind: options.kind, model_or_api_calls: false, app_installation: "untested", subject: { manifest_sha256: createHash("sha256").update(await readFile(path.join(root, manifestFile))).digest("hex"), server_sha256: createHash("sha256").update(await readFile(path.resolve(cwd, args[0]))).digest("hex") }, checks: [], sequence: [] };
  const checks = report.checks as string[];
  const artifactNames: Record<string, string> = { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" };
  async function originalDirectory(html: string) {
    const matches: string[] = [];
    for (const entry of await readdir(env.XY_RUNTIME_DIR, { withFileTypes: true })) {
      if (!entry.isDirectory() || !entry.name.startsWith("xy-")) continue;
      const directory = path.join(env.XY_RUNTIME_DIR, entry.name);
      if ((await readFile(path.join(directory, "chart.html"), "utf8")) === html) matches.push(directory);
    }
    assert.equal(matches.length, 1, "The embedded preview must match exactly one real Python output.");
    return matches[0]!;
  }
  async function saveAndCheck(result: any, palette: string, name: string) {
    assert.ok(!result.isError, JSON.stringify(result));
    assert.equal(result.structuredContent.palette, palette);
    const dir = path.join(output, name); await mkdir(dir, { recursive: true });
    assert.equal(typeof result._meta.native_preview.html, "string");
    assert.equal(typeof result._meta.native_preview.svg, "string");
    const nativeDirectory = await originalDirectory(result._meta.native_preview.html);
    assert.equal(result._meta.native_preview.svg, await readFile(path.join(nativeDirectory, "chart.svg"), "utf8"));
    assert.match(result._meta.native_preview.html, /<!doctype html>/i);
    assert.doesNotMatch(result._meta.native_preview.html, /data-xy-compact-preview/);
    assert.equal(new URL(result._meta.artifact_origin).hostname, "127.0.0.1");
    const health = await (await fetch(result._meta.artifact_origin)).json() as any;
    assert.equal(health.transport, "stdio"); assert.equal(health.mcp, null);
    assert.equal((await fetch(result._meta.artifact_origin + "/mcp")).status, 404);
    assert.equal((await fetch(result._meta.artifact_origin + "/mcp", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" })).status, 404);
    assert.deepEqual(Object.keys(result.structuredContent.downloads).sort(), ["html", "png", "source", "spec", "svg"]);
    const exportEvidence: Record<string, unknown> = {};
    for (const [kind, value] of Object.entries(result.structuredContent.downloads)) {
      const url = new URL(String(value)); assert.equal(url.origin, result._meta.artifact_origin); assert.ok(url.searchParams.has("token"));
      const response = await fetch(url); assert.equal(response.status, 200); assert.equal(response.headers.get("cache-control"), "no-store");
      const data = Buffer.from(await response.arrayBuffer()); assert.ok(data.length > 10);
      const original = await readFile(path.join(nativeDirectory, artifactNames[kind]!));
      assert.deepEqual(data, original, `${kind} HTTP download must retain the original Python bytes.`);
      const exported: any = await client.callTool({ name: "xy_get_chart_artifact", arguments: { render_id: result.structuredContent.render_id, render_key: result._meta.render_key, format: kind } });
      assert.ok(!exported.isError, JSON.stringify(exported));
      assert.equal(exported.structuredContent.name, artifactNames[kind]);
      assert.equal(exported.structuredContent.bytes, original.length);
      assert.equal(exported._meta.artifact.name, artifactNames[kind]);
      assert.equal(exported._meta.artifact.mime_type, exported.structuredContent.mime_type);
      assert.equal(exported.structuredContent.blob, undefined);
      assert.deepEqual(Buffer.from(exported._meta.artifact.blob, "base64"), original, `${kind} MCP export must retain the original Python bytes.`);
      exportEvidence[kind] = { bytes: original.length, sha256: createHash("sha256").update(original).digest("hex"), http_and_mcp_equal_original: true };
      const ext = kind === "source" ? "py" : kind === "spec" ? "json" : kind;
      await writeFile(path.join(dir, `chart.${ext}`), data);
      const missing = new URL(url); missing.search = ""; assert.equal((await fetch(missing)).status, 404);
    }
    const spec = JSON.parse(await readFile(path.join(dir, "chart.json"), "utf8")); assert.equal(spec.colorset, palette);
    const svg = await readFile(path.join(dir, "chart.svg"), "utf8");
    assert.match(svg, new RegExp(`<(?:circle|path|line|rect|polygon|polyline)\\b[^>]*(?:fill|stroke)=["']${palette === "colorset1" ? "#9e1b32" : "#007298"}["']`));
    await writeFile(path.join(dir, "result.json"), JSON.stringify(result, null, 2));
    await writeFile(path.join(dir, "export-evidence.json"), JSON.stringify(exportEvidence, null, 2));
    (report.sequence as unknown[]).push({ name, palette, native_mark_ink: true, five_downloads: true, embedded_preview_equals_original: true, mcp_exports_equal_original: true, loopback_assets_optional: true });
  }
  try {
    await client.connect(transport);
    const list = await client.listTools();
    const names = list.tools.map((tool: any) => tool.name).sort();
    assert.deepEqual(names, ["xy_capabilities", "xy_get_chart_artifact", "xy_get_reference", "xy_open_chart_app", "xy_recolor_chart", "xy_render_chart"]);
    if (options.kind === "mcpb") assert.deepEqual(manifest.tools.map((tool: any) => tool.name).sort(), names);
    const opener = list.tools.find((tool: any) => tool.name === "xy_open_chart_app");
    assert.deepEqual(opener._meta.ui.visibility, ["app"]);
    assert.deepEqual(opener._meta["openai/ui"].entrypoints, [{ type: "global" }, { type: "thread" }]);
    assert.equal(opener._meta.ui.resourceUri, "ui://reflex-xy/chart-v4.html");
    assert.deepEqual(list.tools.find((tool: any) => tool.name === "xy_recolor_chart")._meta.ui.visibility, ["app"]);
    assert.deepEqual(list.tools.find((tool: any) => tool.name === "xy_get_chart_artifact")._meta.ui.visibility, ["app"]);
    assert.equal(client.getServerVersion()?.version, "0.3.1");
    checks.push("exact_six_tools_and_app_only_entrypoints_exports");
    const resource = await client.readResource({ uri: opener._meta.ui.resourceUri });
    const component = resource.contents[0]; assert.equal(component.mimeType, "text/html;profile=mcp-app"); assert.equal(component._meta.ui.domain, undefined);
    const widgetHash = createHash("sha256").update(component.text).digest("hex");
    const packagedWidget = await readFile(path.join(path.dirname(path.resolve(cwd, args[0])), "widget.html"));
    assert.equal(widgetHash, createHash("sha256").update(packagedWidget).digest("hex"));
    assert.deepEqual(component._meta.ui.csp, { connectDomains: [], resourceDomains: [], frameDomains: ["about:"] });
    report.widget_sha256 = widgetHash;
    const opened: any = await client.callTool({ name: "xy_open_chart_app", arguments: {} }, undefined, { timeout: 180000 });
    await saveAndCheck(opened, "colorset1", "entrypoint-default-cs1");
    assert.match(opened._meta.spec_json, /Sample data/);
    const liveResource = await client.readResource({ uri: opener._meta.ui.resourceUri });
    assert.deepEqual(liveResource.contents[0]._meta.ui.csp, { connectDomains: [], resourceDomains: [], frameDomains: ["about:"] });
    const badKey = (opened._meta.render_key[0] === "A" ? "B" : "A") + opened._meta.render_key.slice(1);
    const denied: any = await client.callTool({ name: "xy_get_chart_artifact", arguments: { render_id: opened.structuredContent.render_id, render_key: badKey, format: "png" } });
    assert.equal(denied.isError, true);
    assert.equal(denied._meta?.artifact, undefined);
    checks.push("bad_artifact_capability_rejected_without_bytes");
    const recolored: any = await client.callTool({ name: "xy_recolor_chart", arguments: { render_id: opened.structuredContent.render_id, render_key: opened._meta.render_key, colorset: "colorset2" } }, undefined, { timeout: 180000 });
    await saveAndCheck(recolored, "colorset2", "app-palette-cs2");
    const fresh: any = await client.callTool({ name: "xy_render_chart", arguments: { spec_json: JSON.stringify({ preset: "line", title: "Independent default after palette selection" }) } }, undefined, { timeout: 180000 });
    await saveAndCheck(fresh, "colorset1", "new-render-default-cs1");
    checks.push("empty_entrypoint_renders_native_cs1_sample", "app_recolor_cs2_does_not_change_new_chart_default", "preview_and_all_five_http_mcp_exports_equal_original_python_bytes", "native_palette_mark_ink", "loopback_assets_optional_and_http_mcp_404", "v4_component_matches_packaged_widget_and_about_only_frame_csp");
    report.passed = true;
  } catch (error) { report.failure = String(error); }
  finally { await client.close(); report.stderr = diagnostics; await writeFile(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n"); }
  console.log(JSON.stringify({ passed: report.passed, kind: options.kind, checks, sequence: report.sequence, failure: report.failure, report: path.join(output, "report.json") }));
  if (!report.passed) process.exitCode = 1;
}
main().catch(error => { console.error(String(error)); process.exitCode = 1; });
