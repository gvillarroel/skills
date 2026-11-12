// Run with `claude plugin test <plugin-directory>`; no account or model calls.
import { expect, test } from "claude-code/testing";

const PANE = {
  component: "Pane" as const,
  requestId: "reflex-xy-chart",
  props: { title: "XY Charts", isFocused: true, bodyColumns: 80, placement: "dock" as const, scroll: { bodyRows: 50, offset: 0, contentRows: 50 }, view: {} },
};

test("empty pane starts simply and reveals optional controls on supported surfaces", async ($, on) => {
  on("session.id", () => ({ value: "native-empty" }));
  for (const surface of ["terminal", "desktop", "vscode"] as const) {
    const ui = await $.ui.mount({ plugin: "reflex-xy", surface, ...PANE });
    expect(await ui.find({ key: "palette" })).toBeUndefined();
    expect(await ui.find({ key: "preset" })).toBeUndefined();
    expect(await ui.find({ key: "reload" })).toBeUndefined();
    expect(await ui.find({ key: "create-chart" })).toBeDefined();
    expect(await ui.find({ key: "more-options" })).toBeDefined();
    expect(await ui.find({ type: "Text", text: /Python XY/ })).toBeUndefined();
    expect(await ui.find({ type: "Svg" })).toBeUndefined();
    expect(await ui.find({ type: "Image" })).toBeUndefined();
    await ui.press({ key: "more-options" });
    expect(await ui.find({ key: "palette" })).toBeDefined();
    expect(await ui.find({ key: "preset" })).toBeDefined();
    expect(await ui.find({ key: "reload" })).toBeDefined();
    await ui.press({ key: "more-options" });
    expect(await ui.find({ key: "palette" })).toBeUndefined();
    await ui.unmount();
  }
});

test("render command keeps JSON out of the shell and chooses native preview elements", async ($, on) => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420"><rect width="640" height="420" fill="#ffffff"/></svg>';
  const requests: unknown[] = [];
  let copied = "";
  on("session.cwd", () => ({ value: "/work/project" }));
  on("session.id", () => ({ value: "native-test" }));
  on("clock.now", () => ({ value: 1234 }));
  on("ui.open", () => ({ value: undefined }));
  on("process.run", ($, e) => {
    expect(e.argv[0]).toBe("uv");
    expect(e.argv[1]).toBe("run");
    expect(e.argv[2]).toBe("--script");
    expect(e.argv[e.argv.length - 2]).toBe("--output-dir");
    expect(e.argv[e.argv.length - 1]).toMatch(/^\/work\/project\/\.xy-charts\/native-test-/);
    const input = JSON.parse(e.init?.stdin ?? "{}");
    requests.push(input);
    expect(input.colorset).toBe("colorset2");
    return { value: { exitCode: 0, stderr: "", stdout: JSON.stringify({ schema_version: 1, title: "Test chart", palette: "colorset2", width: 640, height: 420, factory: "chart", files: { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" }, svg_bytes: svg.length, png_bytes: 512, svg_compat_repairs: 0, warnings: [], counts: { marks: 1, rows: 3 } }) } };
  });
  on("fs.read", () => ({ value: svg }));
  on("ui.copy", ($, e) => { copied = e.text; return { value: undefined }; });
  const rendered = await $.command.run({ command: "xy-chart", args: "colorset2 scatter" });
  expect(rendered.text).toMatch("XY chart created");
  expect(requests.length).toBe(1);
  for (const surface of ["terminal", "desktop", "vscode"] as const) {
    const ui = await $.ui.mount({ plugin: "reflex-xy", surface, ...PANE });
    if (surface === "terminal") {
      expect(await ui.find({ type: "Image" })).toBeDefined();
      expect(await ui.find({ type: "Svg" })).toBeUndefined();
    } else {
      expect(await ui.find({ type: "Svg" })).toBeDefined();
      expect(await ui.find({ type: "Image" })).toBeUndefined();
    }
    expect(await ui.find({ key: "save-image" })).toBeDefined();
    expect(await ui.find({ key: "open-html" })).toBeUndefined();
    expect(await ui.find({ key: "copy-source" })).toBeUndefined();
    expect(await ui.find({ key: "palette" })).toBeUndefined();
    expect(await ui.find({ type: "Text", text: /Python XY/ })).toBeUndefined();
    await ui.press({ key: "more-options" });
    expect(await ui.find({ key: "copy-source" })).toBeDefined();
    await ui.press({ key: "copy-source" });
    expect(copied).toMatch(/\/chart\.py$/);
    await ui.press({ key: "more-options" });
    await ui.unmount();
  }
});

test("chart tool returns engine validation errors as tool errors", async ($, on) => {
  on("session.id", () => ({ value: "native-tool-error" }));
  on("session.cwd", () => ({ value: "/work/project" }));
  on("clock.now", () => ({ value: 1234 }));
  on("process.run", () => ({ value: { exitCode: 2, stdout: "", stderr: '{"error":{"code":"invalid_spec","message":"Unknown chart mark"}}' } }));
  const answer = await $.tool.call({ tool: "mcp__reflex-xy__render_chart", spec: { version: 1, marks: [{ kind: "invalid" }] } });
  expect(answer.isError).toBe(true);
  expect(answer.result).toMatchObject({ error: "Unknown chart mark" });
});

test("skill reference tool only reads its bundled allowlist", async ($, on) => {
  const paths: string[] = [];
  on("fs.read", ($, e) => { paths.push(e.path); return { value: "Colorset guidance" }; });
  const allowed = await $.tool.call({ tool: "mcp__reflex-xy__skill_reference", path: "references/colorsets.md" });
  expect(allowed.result).toMatchObject({ text: "Colorset guidance" });
  expect(paths[0]).toMatch(/[\\/]skills[\\/]reflex-xy[\\/]references[\\/]colorsets\.md$/);
  const interaction = await $.tool.call({ tool: "mcp__reflex-xy__skill_reference", path: "references/interaction-design.md" });
  expect(interaction.result).toMatchObject({ text: "Colorset guidance" });
  expect(paths[1]).toMatch(/[\\/]skills[\\/]reflex-xy[\\/]references[\\/]interaction-design\.md$/);
  const denied = await $.tool.call({ tool: "mcp__reflex-xy__skill_reference", path: "../outside.md" });
  expect(denied.isError).toBe(true);
  expect(paths.length).toBe(2);
});

test("invalid input returns a helpful error without launching a process", async ($, on) => {
  on("session.id", () => ({ value: "native-invalid" }));
  on("ui.open", () => ({ value: undefined }));
  on("session.cwd", () => ({ value: "/work/project" }));
  const rendered = await $.command.run({ command: "xy-chart", args: "@../private.json" });
  expect(rendered.text).toMatch("File paths must not contain");
});

test("session activation loads the renderer preset catalog and registers both tools", async ($, on) => {
  const tools: string[] = [];
  on("session.id", () => ({ value: "native-catalog" }));
  on("session.cwd", () => ({ value: "/work/project" }));
  on("clock.now", () => ({ value: 1234 }));
  on("session.start", ($, e) => ({ cwd: e.cwd }));
  on("tool.register", ($, e) => { tools.push(e.name); return { value: { tool: e.name } }; });
  on("command.register", ($, e) => ({ value: { command: e.name } }));
  on("fs.read", ($, e) => ({ value: e.path.endsWith("contract.json") ? '{"presets":["line","heatmap","radar"]}' : '<svg xmlns="http://www.w3.org/2000/svg"/>' }));
  on("ui.open", () => ({ value: undefined }));
  on("process.run", ($, e) => {
    expect(JSON.parse(e.init?.stdin ?? "{}").preset).toBe("heatmap");
    return { value: { exitCode: 0, stderr: "", stdout: JSON.stringify({ schema_version: 1, title: "Heatmap", palette: "colorset1", width: 640, height: 420, factory: "chart", files: { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" }, svg_bytes: 40, png_bytes: 512, svg_compat_repairs: 0, warnings: [], counts: { marks: 1, rows: 3 } }) } };
  });
  await $.session.start({ cwd: "/work/project", surface: "terminal", isInteractive: true });
  expect(tools).toEqual(["render_chart", "skill_reference"]);
  const answer = await $.command.run({ command: "xy-chart", args: "heatmap" });
  expect(answer.text).toMatch("XY chart created: Heatmap");
});

test("new requests default to Colorset 1 after explicit Colorset 2 while pane choices stay explicit", async ($, on) => {
  const palettes: string[] = [];
  on("session.id", () => ({ value: "native-palette-default" }));
  on("session.cwd", () => ({ value: "/work/project" }));
  on("clock.now", () => ({ value: 1234 }));
  on("ui.open", () => ({ value: undefined }));
  on("fs.read", ($, e) => ({ value: e.path.endsWith("omitted.json") ? '{"preset":"line"}' : e.path.endsWith("explicit.json") ? '{"preset":"line","colorset":"colorset2"}' : '<svg xmlns="http://www.w3.org/2000/svg"/>' }));
  on("process.run", ($, e) => {
    const request = JSON.parse(e.init?.stdin ?? "{}");
    palettes.push(request.colorset);
    return { value: { exitCode: 0, stderr: "", stdout: JSON.stringify({ schema_version: 1, title: "Palette regression", palette: request.colorset, width: 640, height: 420, factory: "chart", files: { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" }, svg_bytes: 40, png_bytes: 512, svg_compat_repairs: 0, warnings: [], counts: { marks: 1, rows: 3 } }) } };
  });
  for (const omitted of ["", "bar", '{"preset":"scatter"}', "@omitted.json"]) {
    await $.command.run({ command: "xy-chart", args: "colorset2 line" });
    expect(palettes[palettes.length - 1]).toBe("colorset2");
    const answer = await $.command.run({ command: "xy-chart", args: omitted });
    expect(answer.text).toMatch("XY chart created");
    expect(palettes[palettes.length - 1]).toBe("colorset1");
  }
  await $.tool.call({ tool: "mcp__reflex-xy__render_chart", spec: { preset: "line", colorset: "colorset2" } });
  expect(palettes[palettes.length - 1]).toBe("colorset2");
  await $.tool.call({ tool: "mcp__reflex-xy__render_chart", spec: { preset: "line" } });
  expect(palettes[palettes.length - 1]).toBe("colorset1");
  await $.command.run({ command: "xy-chart", args: "@explicit.json" });
  expect(palettes[palettes.length - 1]).toBe("colorset2");
  const ui = await $.ui.mount({ plugin: "reflex-xy", surface: "desktop", ...PANE });
  await ui.press({ key: "more-options" });
  await ui.select({ key: "preset", value: "bar" });
  expect(palettes[palettes.length - 1]).toBe("colorset2");
  await ui.select({ key: "palette", value: "colorset1" });
  expect(palettes[palettes.length - 1]).toBe("colorset1");
  await ui.select({ key: "palette", value: "colorset2" });
  expect(palettes[palettes.length - 1]).toBe("colorset2");
  await ui.unmount();
});

test("optional palette edits preserve supplied data and technical details stay collapsed", async ($, on) => {
  const requests: Record<string, unknown>[] = [];
  let rejectNext = false;
  const data = { x: [1, 2, 3], y: [4, 8, 5] };
  const warning = "Export compatibility detail";
  on("session.id", () => ({ value: "native-progressive-options" }));
  on("session.cwd", () => ({ value: "/work/project" }));
  on("clock.now", () => ({ value: 1234 }));
  on("ui.open", () => ({ value: undefined }));
  on("fs.read", () => ({ value: '<svg xmlns="http://www.w3.org/2000/svg"/>' }));
  on("process.run", ($, e) => {
    const request = JSON.parse(e.init?.stdin ?? "{}");
    requests.push(request);
    if (rejectNext) return { value: { exitCode: 2, stdout: "", stderr: '{"error":{"message":"Could not create the new chart"}}' } };
    return { value: { exitCode: 0, stderr: "", stdout: JSON.stringify({ schema_version: 1, title: "Your measurements", palette: request.colorset, width: 640, height: 420, factory: "chart", files: { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" }, svg_bytes: 40, png_bytes: 512, svg_compat_repairs: 0, warnings: [warning, warning, "Standalone HTML is an interactive snapshot; Python callbacks and future updates need a live host."], counts: { marks: 1, rows: 3 } }) } };
  });
  await $.command.run({ command: "xy-chart", args: JSON.stringify({ preset: "line", title: "Your measurements", data }) });
  const ui = await $.ui.mount({ plugin: "reflex-xy", surface: "desktop", ...PANE });
  expect((await ui.findAll({ type: "Button" })).length).toBe(2);
  expect(await ui.find({ type: "Button", text: "Save image" })).toBeDefined();
  expect(await ui.find({ type: "Text", text: "Your measurements" })).toBeUndefined();
  expect(await ui.find({ type: "Text", text: warning })).toBeUndefined();
  expect(await ui.find({ type: "Text", text: /Artifact directory/ })).toBeUndefined();
  await ui.press({ key: "more-options" });
  expect(requests.length).toBe(1);
  expect((await ui.findAll({ type: "Text", text: warning })).length).toBe(1);
  expect(await ui.find({ type: "Text", text: /Python XY|640 × 420|interactive snapshot/ })).toBeUndefined();
  expect(await ui.find({ type: "Text", text: /Artifact directory/ })).toBeDefined();
  await ui.select({ key: "palette", value: "colorset2" });
  expect(requests[1]).toMatchObject({ preset: "line", title: "Your measurements", colorset: "colorset2", data });
  rejectNext = true;
  await $.command.run({ command: "xy-chart", args: JSON.stringify({ preset: "line", title: "Rejected request", data: { x: [99], y: [100] } }) });
  expect(await ui.find({ type: "Text", text: "Could not create the new chart" })).toBeDefined();
  rejectNext = false;
  await ui.select({ key: "palette", value: "colorset1" });
  expect(requests[3]).toMatchObject({ title: "Your measurements", colorset: "colorset1", data });
  await ui.press({ key: "more-options" });
  expect((await ui.findAll({ type: "Button" })).length).toBe(2);
  expect(await ui.find({ key: "palette" })).toBeUndefined();
  expect(await ui.find({ type: "Text", text: warning })).toBeUndefined();
  expect(requests.length).toBe(4);
  await ui.unmount();
});

test("native Save image uses only the local helper and browser export remains optional", async ($, on) => {
  const calls: string[][] = [];
  let modelCalls = 0;
  let promptCalls = 0;
  let saveFails = false;
  on("session.id", () => ({ value: "native-local-save" }));
  on("session.cwd", () => ({ value: "/work/project" }));
  on("clock.now", () => ({ value: 1234 }));
  on("ui.open", () => ({ value: undefined }));
  on("fs.read", () => ({ value: '<svg xmlns="http://www.w3.org/2000/svg"/>' }));
  on("model.complete", () => { modelCalls++; throw new Error("Local UI must not call a model."); });
  on("prompt.submit", () => { promptCalls++; throw new Error("Local UI must not submit a conversation turn."); });
  on("process.run", ($, e) => {
    calls.push([...e.argv]);
    if (e.argv[3]?.endsWith("/scripts/save_image.py")) {
      expect(e.argv[4]).toBe("--project-dir");
      expect(e.argv[5]).toBe("/work/project");
      expect(e.argv[6]).toBe("--source-dir");
      expect(e.argv[7]).toMatch(/^\/work\/project\/\.xy-charts\/native-local-save-/);
      expect(JSON.parse(e.init?.stdin ?? "{}")).toEqual({ title: "Native saved chart" });
      if (saveFails) return { value: { exitCode: 2, stdout: "", stderr: '{"error":{"message":"Export directory is read-only"}}' } };
      return { value: { exitCode: 0, stderr: "", stdout: JSON.stringify({ schema_version: 1, path: "/work/project/.xy-charts/exports/native-saved-chart-012345abcdef.png", name: "native-saved-chart-012345abcdef.png", bytes: 512, sha256: "a".repeat(64) }) } };
    }
    const request = JSON.parse(e.init?.stdin ?? "{}");
    return { value: { exitCode: 0, stderr: "", stdout: JSON.stringify({ schema_version: 1, title: "Native saved chart", palette: request.colorset, width: 640, height: 420, factory: "chart", files: { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" }, svg_bytes: 40, png_bytes: 512, svg_compat_repairs: 0, warnings: [], counts: { marks: 1, rows: 3 } }) } };
  });
  await $.command.run({ command: "xy-chart", args: "line" });
  const ui = await $.ui.mount({ plugin: "reflex-xy", surface: "desktop", ...PANE });
  expect((await ui.findAll({ type: "Button" })).length).toBe(2);
  expect(await ui.find({ key: "open-html" })).toBeUndefined();
  await ui.press({ key: "save-image" });
  expect(await ui.find({ type: "Text", text: "Image saved." })).toBeDefined();
  expect(calls.length).toBe(2);
  expect(calls.every(argv => argv[0] === "uv")).toBe(true);
  await ui.press({ key: "more-options" });
  expect(await ui.find({ key: "copy-saved-image" })).toBeDefined();
  expect(await ui.find({ key: "open-export-folder" })).toBeDefined();
  expect(await ui.find({ key: "open-html" })).toBeDefined();
  await ui.select({ key: "palette", value: "colorset2" });
  expect(await ui.find({ type: "Text", text: "Image saved." })).toBeUndefined();
  saveFails = true;
  await ui.press({ key: "save-image" });
  expect(await ui.find({ type: "Text", text: /Export directory is read-only/ })).toBeDefined();
  expect(await ui.find({ type: "Svg" })).toBeDefined();
  expect(await ui.find({ type: "Text", text: "Image saved." })).toBeUndefined();
  expect(modelCalls).toBe(0);
  expect(promptCalls).toBe(0);
  await ui.unmount();
});
