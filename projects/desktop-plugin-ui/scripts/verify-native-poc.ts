#!/usr/bin/env node
// Run with Node 24 native TypeScript: node projects/desktop-plugin-ui/scripts/verify-native-poc.ts <workspace/poc> <label>
// No packages required. Evaluator-only: runs installed Claude's account-free native test engine.
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";

const [input, label] = process.argv.slice(2);
if (!input || !label || !/^[a-z0-9-]+$/.test(label)) {
  console.error("Usage: node verify-native-poc.ts <workspace/poc> <label>");
  process.exit(2);
}
const root = process.cwd();
const source = path.resolve(input);
const artifactRoot = path.resolve(root, "projects/desktop-plugin-ui/artifacts/plugin-pocs", `native-${label}`);
for (const item of [source, artifactRoot]) {
  if (!item.startsWith(root + path.sep)) throw new Error("Evaluation paths must stay inside the repository");
}
if (fs.existsSync(artifactRoot)) throw new Error("Refusing to overwrite retained native evaluation evidence; choose a fresh label");
fs.mkdirSync(artifactRoot, { recursive: true });
const target = path.join(artifactRoot, "independent-plugin");
const required = [".claude-plugin/plugin.json", "hooks/hooks.json", "hooks/register.ts", "package.json", "tests/native.test.ts", "USAGE.md", "review.json"];
const checks = [];
const record = (name, passed, details = {}) => checks.push({ name, passed: Boolean(passed), ...details });
const digest = file => createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const snapshot = directory => {
  const result = {};
  const visit = current => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (["node_modules", ".host-state", ".claude-state", "logs", "cache"].includes(entry.name)) continue;
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) visit(full);
      else if (entry.isFile()) result[path.relative(directory, full).replaceAll("\\", "/")] = digest(full);
    }
  };
  visit(directory);
  return result;
};
for (const relative of required) {
  const full = path.join(source, relative);
  record(`artifact:${relative}`, fs.existsSync(full) && fs.statSync(full).isFile() && fs.statSync(full).size > 0);
}
const before = snapshot(source);
fs.cpSync(source, target, {
  recursive: true,
  filter: full => !["node_modules", ".host-state", ".claude-state", "logs", "cache"].some(part => path.relative(source, full).split(path.sep).includes(part)) && !/\.test\.tsx?$/.test(full),
});
const environment = { ...process.env, CLAUDE_CONFIG_DIR: path.join(artifactRoot, "host-state"), CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1" };
for (const key of ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY"]) delete environment[key];
fs.mkdirSync(environment.CLAUDE_CONFIG_DIR, { recursive: true });
function execute(name, args) {
  const started = Date.now();
  const result = spawnSync("claude", args, { cwd: root, env: environment, encoding: "utf8", timeout: 60000, windowsHide: true });
  fs.writeFileSync(path.join(artifactRoot, `${name}.stdout.txt`), result.stdout || "");
  fs.writeFileSync(path.join(artifactRoot, `${name}.stderr.txt`), result.stderr || "");
  const summary = { command: ["claude", ...args], exitCode: result.status, error: result.error ? String(result.error) : null, durationMs: Date.now() - started };
  record(name, result.status === 0 && !result.error, summary);
  return result;
}
const strict = execute("strict-validation", ["plugin", "validate", source, "--strict", "--json"]);
execute("forward-native-tests", ["plugin", "test", source]);
let manifest;
try {
  manifest = JSON.parse(fs.readFileSync(path.join(source, ".claude-plugin/plugin.json"), "utf8"));
  record("manifest-name", manifest.name === "release-review");
} catch (error) { record("manifest-json", false, { error: String(error) }); }
try {
  const review = JSON.parse(fs.readFileSync(path.join(source, "review.json"), "utf8"));
  record("review-honest-live-flags", review.host_paint_verified === false && review.user_testing_performed === false);
  // The prompt requires H1-H10 findings, but does not prescribe an array
  // instead of a keyed object. Validate either faithful serialization.
  const heuristics = review.heuristics || {};
  const entries = Array.isArray(heuristics) ? heuristics.map(item => [item.id, item]) : Object.entries(heuristics);
  const ids = new Set(entries.map(([id]) => id));
  record("review-h1-h10", ids.size === 10 && Array.from({ length: 10 }, (_, i) => `H${i + 1}`).every(id => ids.has(id)) && entries.every(([, item]) => ["interaction", "finding", "evidence"].every(key => key in item)));
} catch (error) { record("review-json", false, { error: String(error) }); }

const suite = String.raw`import { expect, test } from "claude-code/testing";
const PANE = { plugin: "release-review", component: "Pane", requestId: "release-review", viewport: { columns: 100, rows: 30 }, props: { title: "Release review", isFocused: true, bodyColumns: 60, placement: "inline", scroll: { offset: 0, bodyRows: 15 }, view: {} } } as const;
const IDS = ["R-71", "R-72", "R-73"];
function guards(on) {
  const rejected = [];
  for (const event of ["model.complete", "process.run", "fs.write", "store.set"]) on(event, () => { rejected.push(event); return { deny: "Unexpected inference, process or persistence in this read-only PoC" }; });
  on("ui.render", () => ({ type: "Text", props: {}, children: ["HOST-FALLBACK"] }));
  on("ui.toast", () => ({ value: undefined }));
  return rejected;
}
async function runText($, args) { return String((await $.command.run({ command: "release-review", args })).text || ""); }
function verifyRows(text, expected) {
  for (const id of IDS) {
    if (expected.includes(id)) expect(text).toContain(id);
    else expect(text).not.toContain(id);
  }
  for (const id of expected) {
    const state = id === "R-72" ? "blocked" : "ready";
    const sameLine = text.split(/\r?\n/).find(line => line.includes(id)) || "";
    const followingBlock = new RegExp(id + "(?:(?!R-7[123])[\\s\\S])*?\\b" + state + "\\b", "i");
    expect(new RegExp("\\b" + state + "\\b", "i").test(sameLine) || followingBlock.test(text)).toBe(true);
  }
}
test("independent: session.start actually registers the public command", async ($, on) => {
  const forbidden = guards(on);
  const registrations = [];
  on("command.register", ($, e) => { registrations.push(e); return { value: undefined }; });
  on("session.start", () => ({ cwd: "/work" }));
  await $.session.start({ surface: "terminal", isInteractive: true, cwd: "/work" });
  expect(registrations.some(item => item.name === "release-review")).toBe(true);
  expect(forbidden).toEqual([]);
});
for (const [argument, expected] of [["all", IDS], ["ready", ["R-71", "R-73"]], ["blocked", ["R-72"]]]) test("independent: direct " + argument + " is exact and never opens UI", async ($, on) => {
  const forbidden = guards(on); let opened = 0;
  on("ui.open", () => { opened++; return { value: { isPlaced: true } }; });
  verifyRows(await runText($, argument), expected);
  expect(opened).toBe(0); expect(forbidden).toEqual([]);
});
test("independent: invalid arguments give actionable recovery without pane", async ($, on) => {
  const forbidden = guards(on); let opened = 0;
  on("ui.open", () => { opened++; return { value: { isPlaced: true } }; });
  const text = await runText($, "nonsense");
  expect(text).toMatch(/release-review/); expect(text).toMatch(/help|all|ready|blocked/i);
  expect(opened).toBe(0); expect(forbidden).toEqual([]);
});
test("independent: missing placement returns all rows and text recovery", async ($, on) => {
  const forbidden = guards(on);
  on("ui.open", () => ({ value: { isPlaced: false } }));
  const text = await runText($, ""); verifyRows(text, IDS);
  expect(text).toMatch(/release-review/); expect(forbidden).toEqual([]);
});
for (const surface of ["terminal", "desktop"]) test("independent: native " + surface + " selector filters and Cancel closes without changing records", async ($, on) => {
  const forbidden = guards(on); let closed = 0; let opened = 0;
  on("ui.open", () => { opened++; return { value: { isPlaced: true } }; });
  on("ui.close", () => { closed++; return { value: undefined }; });
  await runText($, "");
  const ui = await $.ui.mount({ ...PANE, surface });
  const select = await ui.find({ type: "Select", key: "view" });
  expect(select).toBeDefined();
  const options = select.props.options;
  for (const [label, expected] of [["All checks", IDS], ["Ready", ["R-71", "R-73"]], ["Blocked", ["R-72"]]]) {
    const semantic = label === "All checks" ? /\ball\b/i : label === "Ready" ? /\bready\b/i : /\bblocked\b/i;
    const option = options.find(item => semantic.test(String(item.label)));
    expect(option).toBeDefined();
    await ui.select({ key: "view", value: option.value });
    for (const id of IDS) {
      const found = await ui.find({ type: "Text", text: new RegExp(id) });
      if (expected.includes(id)) expect(found).toBeDefined(); else expect(found).toBeUndefined();
    }
  }
  await ui.press({ key: "cancel" }); expect(closed).toBe(1);
  verifyRows(await runText($, "all"), IDS);
  await runText($, ""); expect(opened).toBe(2);
  await ui.unmount(); expect(forbidden).toEqual([]);
});
test("independent: another pane retains its host drawing", async ($, on) => {
  const forbidden = guards(on);
  const ui = await $.ui.mount({ ...PANE, surface: "desktop", requestId: "unrelated-pane" });
  expect(await ui.find({ type: "Text", text: "HOST-FALLBACK" })).toBeDefined();
  await ui.unmount(); expect(forbidden).toEqual([]);
});
`;
fs.mkdirSync(path.join(target, "evaluator-tests"), { recursive: true });
fs.writeFileSync(path.join(target, "evaluator-tests/acceptance.test.ts"), suite);
const independent = execute("independent-native-tests", ["plugin", "test", target]);
let commandProbe = { attempted: false, status: "untested", reason: "Native validation and independent tests must pass before a real command probe." };
if (strict.status === 0 && independent.status === 0) {
  const args = ["-p", "/release-review ready", "--plugin-dir", target, "--output-format", "json", "--no-session-persistence"];
  const probe = spawnSync("claude", args, { cwd: root, env: environment, encoding: "utf8", timeout: 45000, windowsHide: true });
  fs.writeFileSync(path.join(artifactRoot, "headless-command.stdout.txt"), probe.stdout || "");
  fs.writeFileSync(path.join(artifactRoot, "headless-command.stderr.txt"), probe.stderr || "");
  let receipt;
  try { receipt = JSON.parse(probe.stdout); } catch { receipt = null; }
  const success = probe.status === 0 && receipt && receipt.is_error === false && receipt.num_turns === 0 && receipt.duration_api_ms === 0 && receipt.total_cost_usd === 0 && /R-71/.test(receipt.result) && /R-73/.test(receipt.result) && !/R-72/.test(receipt.result);
  commandProbe = { attempted: true, status: success ? "observed-working" : "observed-failed", command: ["claude", ...args], exitCode: probe.status, zeroTurns: receipt?.num_turns === 0, apiMilliseconds: receipt?.duration_api_ms, costUsd: receipt?.total_cost_usd, result: receipt?.result, error: probe.error ? String(probe.error) : null, scope: "Installed headless native command with empty task-local Claude state; not terminal or Desktop paint. A blocked account/trust/host gate is separate from native engine acceptance." };
}
record("generated-source-unchanged", JSON.stringify(before) === JSON.stringify(snapshot(source)));
const result = { passed: checks.every(item => item.passed), source, artifactRoot, checks, commandProbe, limits: "Actual installed native engine and manifest checks; no installed terminal/Desktop paint, focus, resize or sign-in proof. Any actual command/inference receipt is separately scoped in commandProbe." };
fs.writeFileSync(path.join(artifactRoot, "result.json"), JSON.stringify(result, null, 2) + "\n");
console.log(JSON.stringify({ passed: result.passed, checks: checks.length, failed: checks.filter(item => !item.passed), evidence: path.join(artifactRoot, "result.json") }));
process.exit(result.passed ? 0 : 1);
