// Claude Code loads this TypeScript module without a separate build step.
import type { EngineInterface, Register, RenderElement } from "claude-code";
import { isObject, outputPath, parseRequest, parseResult, parseSavedImage, PRESETS, relativeFile, renderError, PNG_LIMIT, SVG_LIMIT, REQUEST_LIMIT } from "./helpers.ts";
import type { ChartRequest, Palette, RenderResult, SavedImage } from "./helpers.ts";

type Preview = { output: string; result: RenderResult; svg: string | null; request: ChartRequest };
type ViewState = { palette: Palette; preset: string; presets: string[]; request: ChartRequest; preview: Preview | null; busy: boolean; error: string | null; serial: number; optionsOpen: boolean; canRetry: boolean; saving: boolean; savedImage: SavedImage | null };

const PANE = "reflex-xy-chart";
const TOOL = "mcp__reflex-xy__render_chart";
const REFERENCE_TOOL = "mcp__reflex-xy__skill_reference";
const SNAPSHOT_WARNING = "Standalone HTML is an interactive snapshot; Python callbacks and future updates need a live host.";
const REFERENCES = ["SKILL.md", "references/advanced-charts.md", "references/chart-recipes.md", "references/colorsets.md", "references/interaction-design.md", "references/large-data-and-live.md", "references/outputs-and-validation.md", "references/pattern-recipes.md", "references/reflex-and-pyplot.md", "references/sources.md"];
const sessions = new Map<string, ViewState>();

async function sessionState($: EngineInterface): Promise<ViewState> {
  const id = await $.session.id();
  let state = sessions.get(id);
  if (!state) {
    state = { palette: "colorset1", preset: "line", presets: [...PRESETS], request: { preset: "line", colorset: "colorset1" }, preview: null, busy: false, error: null, serial: 0, optionsOpen: false, canRetry: false, saving: false, savedImage: null };
    sessions.set(id, state);
  }
  return state;
}

async function generate($: EngineInterface, request: ChartRequest, uv: string): Promise<Preview> {
  const state = await sessionState($);
  if (state.busy) throw new Error("A chart is already rendering. Wait for it to finish before trying again.");
  state.busy = true;
  state.error = null;
  state.request = request;
  state.canRetry = true;
  if (request.colorset === "colorset1" || request.colorset === "colorset2") state.palette = request.colorset;
  if (typeof request.preset === "string") state.preset = request.preset;
  $.ui.invalidate("ui.render");
  try {
    const cwd = await $.session.cwd();
    const session = await $.session.id();
    const output = outputPath(cwd, session, await $.clock.now(), ++state.serial);
    const encoded = JSON.stringify(request);
    if (encoded.length > REQUEST_LIMIT) throw new Error("Chart request exceeds 1,000,000 characters.");
    const process = await $.process.run([uv, "run", "--script", `${$.plugin.root}/runtime/render.py`, "--skill-dir", `${$.plugin.root}/skills/reflex-xy`, "--output-dir", output], {
      cwd,
      stdin: encoded,
      timeoutMs: 300_000,
      env: { PYTHONDONTWRITEBYTECODE: "1", PYTHONIOENCODING: "utf-8" },
    });
    if (process.exitCode !== 0) throw new Error(renderError(process.stderr, `Chart engine exited with status ${process.exitCode}.`));
    const result = parseResult(process.stdout, output);
    let svg: string | null = null;
    if (result.svg_bytes <= SVG_LIMIT) {
      const source = await $.fs.read(relativeFile(output, result.files.svg));
      if (source.length <= SVG_LIMIT) svg = source;
    }
    state.preview = { output, result, svg, request };
    state.savedImage = null;
    state.palette = result.palette;
    return state.preview;
  } catch (error) {
    state.error = String(error instanceof Error ? error.message : error).slice(0, 2_000);
    if (state.preview) state.palette = state.preview.result.palette;
    throw error;
  } finally {
    state.busy = false;
    $.ui.invalidate("ui.render");
  }
}

async function renderFromControl($: EngineInterface, request: ChartRequest, uv: string): Promise<void> {
  try { await generate($, request, uv); } catch { /* The pane displays the recorded error and keeps prior artifacts. */ }
}

async function saveImage($: EngineInterface, preview: Preview, uv: string): Promise<void> {
  const state = await sessionState($);
  if (state.saving) return;
  state.saving = true;
  state.error = null;
  state.savedImage = null;
  $.ui.invalidate("ui.render");
  try {
    const cwd = await $.session.cwd();
    const saved = await $.process.run([uv, "run", "--script", `${$.plugin.root}/scripts/save_image.py`, "--project-dir", cwd, "--source-dir", preview.output], {
      cwd,
      stdin: JSON.stringify({ title: preview.result.title }),
      timeoutMs: 30_000,
      env: { PYTHONDONTWRITEBYTECODE: "1", PYTHONIOENCODING: "utf-8" },
    });
    if (saved.exitCode !== 0) throw new Error(renderError(saved.stderr, "Could not save the image."));
    const result = parseSavedImage(saved.stdout, cwd);
    if (state.preview?.output === preview.output) state.savedImage = result;
  } catch (error) {
    state.error = `Could not save the image: ${String(error instanceof Error ? error.message : error)}`;
  } finally {
    state.saving = false;
    $.ui.invalidate("ui.render");
  }
}

async function openArtifact($: EngineInterface, path: string): Promise<void> {
  try {
    const windows = await $.env.get("OS") === "Windows_NT";
    let executable = "explorer.exe";
    if (!windows) {
      const platform = await $.process.run(["uname", "-s"], { timeoutMs: 10_000 });
      executable = platform.stdout.trim() === "Darwin" ? "open" : "xdg-open";
    }
    const opened = await $.process.run([executable, path], { timeoutMs: 10_000 });
    // Explorer can report status 1 after successfully handing off a document.
    if (!windows && opened.exitCode !== 0) throw new Error(renderError(opened.stderr, "The host could not open this artifact."));
  } catch (error) {
    const state = await sessionState($);
    state.error = `Could not open the chart: ${String(error instanceof Error ? error.message : error)}. Use More options to copy its path.`;
    $.ui.invalidate("ui.render");
  }
}

async function copyPath($: EngineInterface, path: string): Promise<void> {
  try { await $.ui.copy({ text: path }); }
  catch (error) {
    const state = await sessionState($);
    state.error = `Could not copy the path: ${String(error instanceof Error ? error.message : error)}. Its directory is listed in More options.`;
    $.ui.invalidate("ui.render");
  }
}

export const register: Register = (on, options) => {
  const uv = typeof options.uvExecutable === "string" && options.uvExecutable.trim() ? options.uvExecutable.trim() : "uv";

  on("session.start", async ($, e, next) => {
    const state = await sessionState($);
    try {
      const contract: unknown = JSON.parse(await $.fs.read(`${$.plugin.root}/runtime/contract.json`));
      if (isObject(contract) && Array.isArray(contract.presets) && contract.presets.length > 0 && contract.presets.length <= 64 && contract.presets.every(value => typeof value === "string" && /^[a-z][a-z0-9-]{0,63}$/.test(value))) {
        state.presets = [...new Set(contract.presets as string[])];
      }
    } catch { /* Four common demos remain available when packaging metadata is absent. */ }
    await $.tool.register({
      name: "render_chart",
      description: "Render an XY chart from a preset or declarative ChartSpec, using the bundled reflex-xy skill and Python XY 0.0.8. Return local interactive HTML, native SVG/PNG, editable Python and JSON paths. Use colorset1 by default or colorset2 when requested. No Python callbacks execute in the exported HTML. Pass data and whitelisted XY marks, not executable Python code or URLs.",
      inputSchema: { type: "object", properties: { spec: { type: "object", description: "A preset request {preset:string,colorset:'colorset1'|'colorset2',title?:string,data?:object}, or ChartSpec v1. Call skill_reference with path:'contract' for all supported preset names, marks, components and limits before using advanced options." } }, required: ["spec"], additionalProperties: false },
    });
    await $.tool.register({ name: "skill_reference", description: "Read one compact instruction or reference from the bundled reflex-xy skill before designing an advanced XY chart. Read runtime/contract.json through the contract option for ChartSpec and supported API names.", inputSchema: { type: "object", properties: { path: { type: "string", enum: [...REFERENCES, "contract"] } }, required: ["path"], additionalProperties: false } });
    await $.command.register({ name: "xy-chart", description: "Render an XY chart and open its chart pane", argumentHint: "[colorset1|colorset2] [preset] or @relative/spec.json" });
    return next(e);
  });

  on("session.end", async ($, e, next) => {
    sessions.delete(await $.session.id());
    return next(e);
  });

  on("tool.call", { tool: REFERENCE_TOOL }, async ($, e) => {
    if (typeof e.path !== "string" || (e.path !== "contract" && !REFERENCES.includes(e.path))) return { result: { error: "Choose a listed skill reference or contract." }, isError: true };
    const path = e.path === "contract" ? `${$.plugin.root}/runtime/contract.json` : relativeFile(`${$.plugin.root}/skills/reflex-xy`, e.path);
    const text = await $.fs.read(path);
    if (text.length > 50_000) return { result: { error: "This reference exceeds the 50,000-character response limit." }, isError: true };
    return { result: { path: e.path, text } };
  });

  on("command.run", { command: "xy-chart" }, async ($, e) => {
    const state = await sessionState($);
    await $.ui.open({ id: PANE, title: "XY Charts", focus: true });
    state.canRetry = false;
    try {
      const input = e.args.trim();
      const raw = input.startsWith("@") ? await $.fs.read(relativeFile(await $.session.cwd(), input.slice(1).trim())) : input;
      const preview = await generate($, parseRequest(raw, state.presets), uv);
      const html = relativeFile(preview.output, preview.result.files.html);
      return { text: `XY chart created: ${preview.result.title} (${preview.result.palette}).\nInteractive HTML: ${html}\nSVG and PNG previews, editable Python, and JSON are in ${preview.output}.` };
    } catch (error) {
      state.error = String(error instanceof Error ? error.message : error).slice(0, 2_000);
      $.ui.invalidate("ui.render");
      return { text: `XY chart failed: ${state.error}` };
    }
  });

  on("tool.call", { tool: TOOL }, async ($, e) => {
    if (!isObject(e.spec)) return { result: { error: "spec must be a JSON object." }, isError: true };
    try {
      const preview = await generate($, { colorset: "colorset1", ...e.spec }, uv);
      // Tool calls remain useful in headless sessions; opening a pane is a user command.
      return { result: { ...preview.result, output_dir: preview.output, absolute_files: Object.fromEntries(Object.entries(preview.result.files).map(([kind, path]) => [kind, relativeFile(preview.output, path)])), preview: "Run /xy-chart with the saved spec to open a pane; HTML retains browser interactions." } };
    } catch (error) {
      return { result: { error: String(error instanceof Error ? error.message : error) }, isError: true };
    }
  });

  on("ui.render", { component: "Pane" }, async ($, e, next) => {
    if (e.requestId !== PANE) return next(e);
    const state = await sessionState($);
    const { Box, Text, Button } = $.ui.resolve(e);
    const preview = state.preview;
    const hasNativePreview = !!preview && (((e.surface === "desktop" || e.surface === "vscode") && !!preview.svg) || (e.surface === "terminal" && preview.result.png_bytes <= PNG_LIMIT));
    const children: RenderElement[] = hasNativePreview ? [] : [Text({ bold: true, children: preview?.result.title ?? "Your chart" })];
    if (state.error) children.push(Text({ children: state.error.length > 240 ? `${state.error.slice(0, 237)}…` : state.error }));
    if (state.busy) children.push(Text({ children: preview ? "Updating your chart…" : "Creating your chart…" }));
    if (preview) {
      const result = preview.result;
      if (e.surface === "desktop" || e.surface === "vscode") {
        if (preview.svg) {
          const { Svg } = $.ui.resolve(e);
          children.push(Svg({ source: preview.svg, alt: result.title, width: Math.min(result.width, 960), height: Math.round(result.height * Math.min(1, 960 / result.width)) }));
        } else children.push(Text({ children: "The chart is ready. Save its image or use an export from More options." }));
      } else if (e.surface === "terminal") {
        if (result.png_bytes <= PNG_LIMIT) {
          const { Image } = $.ui.resolve(e);
          const columns = Math.max(1, Math.min(100, e.props.bodyColumns || 80));
          const rows = Math.max(1, Math.min(40, Math.round(columns * result.height / result.width / 2)));
          children.push(Image({ key: "chart-preview", source: { file: relativeFile(preview.output, result.files.png), format: "png" }, columns, rows, alt: `${result.title}; save the image if this terminal cannot display it.` }));
        } else children.push(Text({ children: "The chart is ready. Save its image or use an export from More options." }));
      } else children.push(Text({ children: "Open this chart on the computer where it was created." }));
      children.push(Button({ key: "save-image", label: state.saving ? "Saving image…" : "Save image", dimColor: state.saving, onPress: () => { void saveImage($, preview, uv); } }));
      if (state.savedImage) children.push(Text({ children: "Image saved." }));
    } else if (!state.busy) {
      children.push(Text({ children: state.error ? state.canRetry ? "Try the same request again, or ask Claude to adjust it." : "Ask Claude to fix the request, or create a sample to get started." : "Ask Claude to chart your data, or try a sample to get started." }));
      children.push(Button({ key: "create-chart", label: state.error && state.canRetry ? "Try again" : "Create a sample chart", onPress: () => {
        void renderFromControl($, state.error && state.canRetry ? state.request : { preset: "line", colorset: "colorset1" }, uv);
      } }));
    }
    children.push(Button({ key: "more-options", label: state.optionsOpen ? "Hide options" : "More options", onPress: () => {
      state.optionsOpen = !state.optionsOpen;
      $.ui.invalidate("ui.render");
    } }));
    if (state.optionsOpen) {
      const options: RenderElement[] = [Text({ bold: true, children: "Chart options" })];
      if (e.surface !== "mobile") {
        const { Select } = $.ui.resolve(e);
        options.push(Select({ key: "palette", label: "Palette", value: state.palette, options: [{ value: "colorset1", label: "Colorset 1" }, { value: "colorset2", label: "Colorset 2" }], onSelect: value => {
          if (!state.busy && (value === "colorset1" || value === "colorset2")) {
            state.palette = value;
            void renderFromControl($, { ...(preview?.request ?? state.request), colorset: value }, uv);
          }
        } }));
        options.push(Select({ key: "preset", label: "Sample chart (replaces current data)", value: state.preset, options: state.presets.map(value => ({ value, label: value[0]!.toUpperCase() + value.slice(1).replaceAll("-", " ") })), onSelect: value => {
          if (!state.busy) {
            state.preset = value;
            void renderFromControl($, { preset: value, colorset: state.palette }, uv);
          }
        } }));
      }
      options.push(Button({ key: "reload", label: state.busy ? "Updating chart…" : "Render this chart again", dimColor: state.busy, onPress: () => { if (!state.busy) void renderFromControl($, preview?.request ?? state.request, uv); } }));
      if (preview) {
        const result = preview.result;
        options.push(Text({ bold: true, children: "Save and edit" }));
        options.push(Button({ key: "open-html", label: "Open HTML export in browser", onPress: () => { void openArtifact($, relativeFile(preview.output, result.files.html)); } }));
        for (const [kind, label] of [["svg", "Open SVG image"], ["png", "Open PNG image"]] as const) {
          const path = relativeFile(preview.output, result.files[kind]);
          options.push(Button({ key: `open-${kind}`, label, onPress: () => { void openArtifact($, path); } }));
        }
        options.push(Button({ key: "copy-html", label: "Copy interactive chart path", onPress: () => { void copyPath($, relativeFile(preview.output, result.files.html)); } }));
        options.push(Button({ key: "copy-source", label: "Copy editable Python path", onPress: () => { void copyPath($, relativeFile(preview.output, result.files.source)); } }));
        options.push(Button({ key: "copy-spec", label: "Copy chart JSON path", onPress: () => { void copyPath($, relativeFile(preview.output, result.files.spec)); } }));
        options.push(Text({ bold: true, children: "Details" }));
        if (state.savedImage) {
          const savedImage = state.savedImage;
          options.push(Text({ children: `Saved image: ${savedImage.name}` }));
          options.push(Button({ key: "copy-saved-image", label: "Copy saved image path", onPress: () => { void copyPath($, savedImage.path); } }));
          options.push(Button({ key: "open-export-folder", label: "Open saved image folder", onPress: () => {
            const separator = Math.max(savedImage.path.lastIndexOf("/"), savedImage.path.lastIndexOf("\\"));
            void openArtifact($, savedImage.path.slice(0, separator));
          } }));
        }
        options.push(Text({ children: `Artifact directory: ${preview.output}` }));
        for (const warning of new Set(result.warnings)) {
          if (warning !== SNAPSHOT_WARNING) options.push(Text({ children: warning }));
        }
      }
      if (state.busy) options.push(Text({ children: "The first run may install the pinned Python environment." }));
      if (state.error && state.error.length > 240) options.push(Text({ children: `Full error: ${state.error}` }));
      children.push(Box({ flexDirection: "column", gap: 1, padding: 1, children: options }));
    }
    return Box({ flexDirection: "column", gap: 1, padding: 1, children });
  });
};
