#!/usr/bin/env node
// Run with Node 24 native TypeScript support: node projects/desktop-plugin-ui/scripts/verify-build-interactions.ts <workspace> <contract|naturalistic>
// Requires Node 24+ only. This evaluator is not part of the shipped skill.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { stripTypeScriptTypes } from "node:module";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

if (!vm.SourceTextModule) {
  const child = spawnSync(process.execPath, ["--experimental-vm-modules", fileURLToPath(import.meta.url), ...process.argv.slice(2)], { stdio: "inherit" });
  process.exit(child.status ?? 2);
}

const [workspaceArgument, caseName] = process.argv.slice(2);
if (!workspaceArgument || !["contract", "naturalistic"].includes(caseName)) {
  console.error("Usage: node verify-build-interactions.ts <workspace> <contract|naturalistic>");
  process.exit(2);
}
const workspace = path.resolve(workspaceArgument);
const specification = caseName === "contract" ? {
  source: "plugin/queue.ts", command: "queue-view", json: "review/checks.json", review: "review/interaction-review.md",
  rows: [
    { id: "T-104", values: ["pending", "high"] },
    { id: "T-105", values: ["pending", "normal"] },
    { id: "T-106", values: ["closed", "high"] },
  ],
  filters: [
    { key: "all", pattern: /\ball\b/i, ids: ["T-104", "T-105", "T-106"] },
    { key: "pending", pattern: /\bpending\b/i, ids: ["T-104", "T-105"] },
    { key: "high", pattern: /\bhigh\b|\bpriority\b/i, ids: ["T-104", "T-106"] },
  ],
} : {
  source: "extension/releases.ts", command: "release-checks", json: "review/validation.json", review: "review/design.md",
  rows: [
    { id: "R-21", values: ["ready"] },
    { id: "R-22", values: ["blocked"] },
    { id: "R-23", values: ["ready"] },
  ],
  filters: [
    { key: "all", pattern: /\ball\b/i, ids: ["R-21", "R-22", "R-23"] },
    { key: "ready", pattern: /\bready\b/i, ids: ["R-21", "R-23"] },
    { key: "blocked", pattern: /\bblocked\b/i, ids: ["R-22"] },
  ],
};

const checks = [];
const record = (name, passed, detail = {}) => checks.push({ name, passed: Boolean(passed), ...detail });
const textOf = value => {
  if (typeof value === "string") return value;
  if (value === undefined || value === null) return "";
  if (Array.isArray(value)) return value.map(textOf).join("\n");
  if (typeof value === "object") {
    if ("content" in value) return textOf(value.content);
    if ("message" in value) return textOf(value.message);
    if (typeof value.text === "string") return value.text;
  }
  return JSON.stringify(value);
};
const allIds = specification.rows.map(row => row.id);
const timeout = (operation, milliseconds = 3000) => Promise.race([
  operation,
  new Promise((_, reject) => { const timer = setTimeout(() => reject(new Error("Evaluator invocation timeout")), milliseconds); timer.unref(); }),
]);

for (const relativePath of [specification.source, specification.json, specification.review]) {
  const file = path.join(workspace, relativePath);
  record(`artifact:${relativePath}`, fs.existsSync(file) && fs.statSync(file).isFile() && fs.statSync(file).size > 0);
}

let source;
try {
  source = stripTypeScriptTypes(fs.readFileSync(path.join(workspace, specification.source), "utf8"), { mode: "transform", sourceUrl: specification.source });
  record("typescript-transformation", true);
} catch (error) {
  record("typescript-transformation", false, { error: String(error) });
}

// These checks inspect required structure independently. Agent assertions never
// establish behavioral success; real handler invocations below supply that.
try {
  const declared = JSON.parse(fs.readFileSync(path.join(workspace, specification.json), "utf8"));
  const heuristics = declared.heuristics;
  const ids = Array.isArray(heuristics) ? heuristics.map(item => item.id) : [];
  record("json-heuristic-coverage", Array.from({ length: 10 }, (_, i) => `H${i + 1}`).every(id => ids.includes(id)) && new Set(ids).size === 10);
  record("json-check-results-present", Array.isArray(declared.checks) && declared.checks.length > 0 && declared.checks.every(item => ["name", "method", "expected", "actual", "status"].every(key => key in item)));
  record("json-complexity-fields-present", declared.complexity && ["visible_controls", "required_decisions", "primary_actions", "runtime_processes_added", "rationale"].every(key => key in declared.complexity));
  record("no-unperformed-host-or-user-study-claim", declared.host_paint_verified === false && declared.user_testing_performed === false);
} catch (error) {
  record("json-parse", false, { error: String(error) });
}

async function invoke(scenario) {
  const displays = [];
  const calls = [];
  const blocked = [];
  const commands = new Map();
  let selectionCount = 0;
  let cancellationDisplayBoundary = undefined;
  const forbidden = name => (...args) => {
    blocked.push({ name, arguments: args.map(textOf) });
    throw new Error(`Forbidden model, provider, process, or persistent action: ${name}`);
  };
  const emit = (method, value) => {
    calls.push({ method, value });
    displays.push(textOf(value));
  };
  const guardUI = method => {
    if (!scenario.hasUI) {
      blocked.push({ name: `headless-ui:${method}` });
      throw new Error(`No caller-visible native UI in headless mode: ${method}`);
    }
  };
  const ui = {
    async select(title, options) {
      guardUI("select");
      if (!Array.isArray(options) || options.some(option => typeof option !== "string")) throw new Error("Pi ui.select options must be strings");
      calls.push({ method: "ui.select", title, options: [...options] });
      displays.push(textOf(title), ...options);
      selectionCount++;
      if (scenario.cancel || selectionCount > 1) {
        cancellationDisplayBoundary ??= displays.length;
        return undefined;
      }
      const selected = options.find(option => scenario.filter.pattern.test(option));
      if (selected === undefined) throw new Error(`No native option matched required filter '${scenario.filter.key}'`);
      return selected;
    },
    async input(title, placeholder) {
      guardUI("input");
      calls.push({ method: "ui.input", title, placeholder });
      if (scenario.cancel) { cancellationDisplayBoundary ??= displays.length; return undefined; }
      return scenario.filter.key;
    },
    async confirm(title, message) {
      guardUI("confirm");
      calls.push({ method: "ui.confirm", title, message });
      displays.push(textOf(title), textOf(message));
      if (scenario.cancel) cancellationDisplayBoundary ??= displays.length;
      return !scenario.cancel;
    },
    async editor(title, prefill) {
      guardUI("editor");
      calls.push({ method: "ui.editor", title, prefill });
      if (scenario.cancel) { cancellationDisplayBoundary ??= displays.length; return undefined; }
      return scenario.filter.key;
    },
    notify(message, level) { guardUI("notify"); emit("ui.notify", { message, level }); },
    setWidget(key, content) { guardUI("setWidget"); emit("ui.setWidget", { key, content }); },
    setStatus(key, content) { guardUI("setStatus"); emit("ui.setStatus", { key, content }); },
    setTitle(title) { guardUI("setTitle"); emit("ui.setTitle", title); },
    theme: { fg: (_role, content) => content, bg: (_role, content) => content, bold: content => content, dim: content => content },
  };
  const pi = {
    registerCommand(name, command) {
      if (typeof name !== "string" || typeof command?.handler !== "function") throw new Error("Invalid Pi command registration");
      commands.set(name, command);
    },
    registerMessageRenderer() {},
    registerTool(tool) { calls.push({ method: "registerTool", name: tool?.name }); },
    on(event) { calls.push({ method: "on", event }); },
    sendMessage(message, options) {
      if (options?.triggerTurn === true) return forbidden("sendMessage.triggerTurn")(message, options);
      calls.push({ method: "sendMessage", message, options });
      if (message?.display !== false) displays.push(textOf(message?.content ?? message));
    },
    sendUserMessage: forbidden("sendUserMessage"),
    exec: forbidden("exec"),
    appendEntry: forbidden("appendEntry"),
    setModel: forbidden("setModel"),
    setThinkingLevel: forbidden("setThinkingLevel"),
    getModel: () => undefined,
    getAllTools: () => [],
  };
  const api = new Proxy(pi, { get(target, key) {
    if (key in target) return target[key];
    if (key === "then") return undefined;
    return forbidden(`pi.${String(key)}`);
  } });
  const context = {
    hasUI: scenario.hasUI,
    mode: scenario.hasUI ? "tui" : "print",
    cwd: workspace,
    ui: new Proxy(ui, { get(target, key) {
      if (key in target) return target[key];
      return forbidden(`unsupported-ui:${String(key)}`);
    } }),
    isIdle: () => true,
    sessionManager: { getSessionFile: () => undefined, getEntries: () => [], getBranch: () => [] },
    modelRegistry: new Proxy({}, { get: (_target, key) => forbidden(`modelRegistry.${String(key)}`) }),
    abort: () => {},
  };
  const sandbox = vm.createContext({
    console: { log: (...values) => emit("console.log", values), info: (...values) => emit("console.info", values), error: (...values) => emit("console.error", values) },
    fetch: forbidden("fetch"),
    process: new Proxy({}, { get: (_target, key) => forbidden(`process.${String(key)}`) }),
    setTimeout: forbidden("setTimeout"),
    setInterval: forbidden("setInterval"),
    URL,
    TextEncoder,
    TextDecoder,
  }, { codeGeneration: { strings: false, wasm: false } });
  let error;
  try {
    const module = new vm.SourceTextModule(source, {
      context: sandbox,
      identifier: specification.source,
      importModuleDynamically: async specifier => { blocked.push({ name: `dynamic-import:${specifier}` }); throw new Error(`Dynamic import unavailable in evaluator: ${specifier}`); },
    });
    await module.link(async specifier => {
      blocked.push({ name: `runtime-import:${specifier}`, classification: "evaluator-limitation-review-required" });
      throw new Error(`Runtime import requires independent evaluator support: ${specifier}`);
    });
    await module.evaluate({ timeout: 1000 });
    if (typeof module.namespace.default !== "function") throw new Error("Missing default extension initializer");
    await timeout(Promise.resolve(module.namespace.default(api)));
    const command = commands.get(specification.command);
    if (!command) throw new Error(`Required command '${specification.command}' was not registered`);
    await timeout(Promise.resolve(command.handler("", context)));
  } catch (caught) { error = String(caught); }
  return { scenario: scenario.name, commands: [...commands.keys()], calls, blocked, displays, cancellationDisplayBoundary, error };
}

function verifyRowValues(scenarioName, displays, rows) {
  const displayedText = displays.join("\n");
  for (const row of rows) {
    // Inspect the same bounded row, not an unrelated status elsewhere.
    const rowLines = displayedText.split(/\r?\n|\\n/).filter(line => line.includes(row.id));
    const rowValuesMatch = rowLines.some(line => {
      const position = line.indexOf(row.id);
      const nextId = line.slice(position + row.id.length).search(caseName === "contract" ? /\bT-\d+\b/ : /\bR-\d+\b/);
      const neighborhood = line.slice(position, nextId < 0 ? undefined : position + row.id.length + nextId);
      return row.values.every(value => new RegExp(`\\b${value}\\b`, "i").test(neighborhood));
    });
    record(`${scenarioName}:values:${row.id}`, rowValuesMatch, { expected: row.values, inspected_lines: rowLines });
  }
}

const scenarios = [];
if (source !== undefined) {
  for (const filter of specification.filters) {
    const result = await invoke({ name: `ui-${filter.key}`, hasUI: true, filter });
    scenarios.push(result);
    record(`${result.scenario}:execution`, !result.error, { error: result.error, blocked: result.blocked });
    const displayedText = result.displays.join("\n");
    const actualIds = [...new Set(displayedText.match(caseName === "contract" ? /\bT-\d+\b/g : /\bR-\d+\b/g) ?? [])].sort();
    record(`${result.scenario}:matching-rows`, JSON.stringify(actualIds) === JSON.stringify([...filter.ids].sort()), { expected: filter.ids, actual: actualIds });
    verifyRowValues(result.scenario, result.displays, specification.rows.filter(row => filter.ids.includes(row.id)));
    record(`${result.scenario}:deterministic`, result.blocked.length === 0);
  }
  const cancelled = await invoke({ name: "cancel", hasUI: true, cancel: true, filter: specification.filters[0] });
  scenarios.push(cancelled);
  record("cancel:execution", !cancelled.error, { error: cancelled.error });
  const postCancelDisplays = cancelled.displays.slice(cancelled.cancellationDisplayBoundary ?? 0);
  record("cancel:no-implicit-selection", cancelled.cancellationDisplayBoundary !== undefined && !allIds.some(id => postCancelDisplays.some(value => value.includes(id))), { displays_after_cancel: postCancelDisplays });
  record("cancel:deterministic", cancelled.blocked.length === 0, { blocked: cancelled.blocked });
  const headless = await invoke({ name: "no-ui", hasUI: false, filter: specification.filters[0] });
  scenarios.push(headless);
  const headlessText = headless.displays.join("\n");
  record("no-ui:execution", !headless.error, { error: headless.error });
  record("no-ui:all-rows-visible", allIds.every(id => headlessText.includes(id)), { displays: headless.displays });
  verifyRowValues("no-ui", headless.displays, specification.rows);
  const recoveryMatches = caseName === "contract"
    ? /interactive|\bTUI\b|\bterminal\b/i.test(headlessText) && /\bpi\b|\/queue-view/i.test(headlessText)
    : /\/release-checks\b/i.test(headlessText);
  record("no-ui:recovery", recoveryMatches, { displays: headless.displays, criterion: caseName === "contract" ? "Interactive route, explicitly requested by contract prompt" : "Actionable command recovery; naturalistic prompt does not require an interactive-mode keyword" });
  record("no-ui:no-dialog-or-external-action", headless.blocked.length === 0, { blocked: headless.blocked });
}

const result = {
  schema_version: 1,
  evaluator: "verify-build-interactions.ts",
  case: caseName,
  workspace,
  passed: checks.length > 0 && checks.every(check => check.passed),
  checks,
  scenarios,
  limitations: [
    "VM and API stubs execute handlers; they do not establish native Pi paint, complete accessibility, or user testing.",
    "Unsupported runtime imports require evaluator review; they are not evidence that the real host rejects the extension.",
    "Semantic English, Nielsen findings, complexity counts, sources, and real-host load commands still require direct review.",
  ],
};
const resultDirectory = path.join(workspace, "evaluator-review");
fs.mkdirSync(resultDirectory, { recursive: true });
const output = path.join(resultDirectory, "build-interactions.json");
fs.writeFileSync(output, JSON.stringify(result, null, 2) + "\n");
console.log(JSON.stringify({ passed: result.passed, checked: checks.length, failed: checks.filter(check => !check.passed).map(check => check.name), output }));
process.exitCode = result.passed ? 0 : 1;
