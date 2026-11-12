// Loaded by Claude Code directly; portable tests use `npx tsx tests/portable.ts`.
export type Palette = "colorset1" | "colorset2";
export type ChartRequest = Record<string, unknown>;

export const PRESETS = ["line", "scatter", "bar", "sankey"] as const;
export const SVG_LIMIT = 131_072;
export const PNG_LIMIT = 2 * 1024 * 1024;
export const REQUEST_LIMIT = 1_000_000;

export type RenderResult = {
  schema_version: 1;
  title: string;
  palette: Palette;
  width: number;
  height: number;
  factory: string;
  files: { html: string; svg: string; png: string; source: string; spec: string };
  svg_bytes: number;
  png_bytes: number;
  svg_compat_repairs: number;
  warnings: string[];
  counts: { marks: number; rows: number };
};

export type SavedImage = { schema_version: 1; path: string; name: string; bytes: number; sha256: string };

export function parseSavedImage(stdout: string, cwd: string): SavedImage {
  const result: unknown = JSON.parse(stdout);
  if (!isObject(result) || result.schema_version !== 1 || typeof result.path !== "string" || typeof result.name !== "string" || !/^[a-z0-9-]+-[a-f0-9]{12}\.png$/.test(result.name) || !Number.isSafeInteger(result.bytes) || (result.bytes as number) <= 0 || typeof result.sha256 !== "string" || !/^[a-f0-9]{64}$/.test(result.sha256)) {
    throw new Error("The image saver returned an invalid result.");
  }
  const expected = relativeFile(cwd, `.xy-charts/exports/${result.name}`).replaceAll("\\", "/");
  if (result.path.replaceAll("\\", "/") !== expected) throw new Error("The image saver returned a path outside this project's exports.");
  return result as SavedImage;
}

export function isObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

export function parseRequest(text: string, presets: readonly string[] = PRESETS): ChartRequest {
  if (text.length > REQUEST_LIMIT) throw new Error("Chart request exceeds 1,000,000 characters.");
  const input = text.trim();
  if (input.startsWith("{")) {
    const parsed: unknown = JSON.parse(input);
    if (!isObject(parsed)) throw new Error("Chart specification must be a JSON object.");
    return { colorset: "colorset1", ...parsed };
  }
  const words = input ? input.split(/\s+/) : [];
  let preset = "line";
  let selected: Palette = "colorset1";
  for (const word of words) {
    if (word === "colorset1" || word === "colorset2") selected = word;
    else if (presets.includes(word)) preset = word;
    else throw new Error("Use a supported preset, a colorset, @relative/spec.json, or a JSON object. The pane lists available demos.");
  }
  return { preset, colorset: selected };
}

export function relativeFile(root: string, relative: string): string {
  const path = relative.replaceAll("\\", "/");
  if (!path || /^[a-z][a-z0-9+.-]*:/i.test(path) || path.startsWith("/") || /[\x00-\x1f]/.test(path)) {
    throw new Error("Use a relative file path inside the current project.");
  }
  const parts = path.split("/");
  if (parts.some(part => !part || part === "." || part === "..")) {
    throw new Error("File paths must not contain empty, dot, or parent segments.");
  }
  return root.replace(/[\\/]+$/, "") + "/" + parts.join("/");
}

export function outputPath(cwd: string, session: string, now: number, serial: number): string {
  const safe = session.replace(/[^a-zA-Z0-9_-]/g, "_").slice(0, 48) || "session";
  return relativeFile(cwd, `.xy-charts/${safe}-${Math.trunc(now)}-${serial}`);
}

export function parseResult(stdout: string, output: string): RenderResult {
  const data: unknown = JSON.parse(stdout);
  if (!isObject(data) || data.schema_version !== 1 || typeof data.title !== "string" || !isObject(data.files)) {
    throw new Error("The chart engine returned an invalid response.");
  }
  const expectedFiles = { html: "chart.html", svg: "chart.svg", png: "chart.png", source: "chart.py", spec: "spec.json" };
  for (const [key, expected] of Object.entries(expectedFiles)) {
    const value = data.files[key];
    if (value !== expected) throw new Error(`The engine returned an unexpected ${key} artifact.`);
    relativeFile(output, value);
  }
  if (data.palette !== "colorset1" && data.palette !== "colorset2") throw new Error("The engine returned an invalid palette.");
  for (const key of ["width", "height", "svg_bytes", "png_bytes"]) {
    if (typeof data[key] !== "number" || !Number.isSafeInteger(data[key]) || data[key] <= 0) throw new Error(`The engine returned an invalid ${key}.`);
  }
  if ((data.width as number) < 320 || (data.width as number) > 2000 || (data.height as number) < 240 || (data.height as number) > 1400) throw new Error("The engine returned dimensions outside the chart contract.");
  if (typeof data.factory !== "string" || !/^[a-z][a-z0-9_]{0,63}$/.test(data.factory)) throw new Error("The engine returned an invalid factory.");
  if (!Number.isSafeInteger(data.svg_compat_repairs) || (data.svg_compat_repairs as number) < 0) throw new Error("The engine returned invalid SVG repair metadata.");
  if (!isObject(data.counts) || [data.counts.marks, data.counts.rows].some(value => !Number.isSafeInteger(value) || (value as number) < 0)) throw new Error("The engine returned invalid chart counts.");
  if (!Array.isArray(data.warnings) || data.warnings.some(value => typeof value !== "string")) throw new Error("The engine returned invalid warnings.");
  return data as RenderResult;
}

export function renderError(stderr: string, fallback: string): string {
  try {
    const parsed: unknown = JSON.parse(stderr);
    if (isObject(parsed) && isObject(parsed.error) && typeof parsed.error.message === "string") {
      return parsed.error.message.slice(0, 2_000);
    }
  } catch { /* A process startup failure is plain text, not engine JSON. */ }
  return (stderr.trim() || fallback).slice(0, 2_000);
}
