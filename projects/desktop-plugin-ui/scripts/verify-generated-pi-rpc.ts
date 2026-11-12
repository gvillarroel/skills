#!/usr/bin/env node
// Run with Node 24 native TypeScript support:
// node projects/desktop-plugin-ui/scripts/verify-generated-pi-rpc.ts <extension.ts> <installed-pi-dist/bundle/cli.js>
// Requires Node 24+ only. Tests the release-checks acceptance task in real Pi RPC;
// no model, TUI, installation, or global settings changes are needed.
import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

type RecordValue = Record<string, any>;
type Check = { name: string; passed: boolean; detail?: string };

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(projectRoot, "../..");
const output = path.join(projectRoot, "artifacts/generated-pi-rpc-20261025");
const state = path.join(output, "agent-state");
const [extensionArgument, cliArgument] = process.argv.slice(2);
if (!extensionArgument || !cliArgument) {
  console.error("Usage: node verify-generated-pi-rpc.ts <extension.ts> <installed-pi-dist/bundle/cli.js>");
  process.exit(2);
}
const extension = await fs.realpath(path.resolve(extensionArgument));
const cli = await fs.realpath(path.resolve(cliArgument));
const relativeExtension = path.relative(repoRoot, extension);
if (relativeExtension.startsWith("..") || path.isAbsolute(relativeExtension)) {
  throw new Error("The generated extension must remain inside this repository.");
}
await fs.mkdir(state, { recursive: true });
const hash = (bytes: Uint8Array) => createHash("sha256").update(bytes).digest("hex");
const before = hash(await fs.readFile(extension));
const env = { ...process.env, PI_CODING_AGENT_DIR: state };
const version = spawnSync(process.execPath, [cli, "--offline", "--version"], {
  cwd: output, env, encoding: "utf8", timeout: 10000,
});
if (version.status !== 0) throw new Error(`Pi version inspection failed: ${version.stderr}`);

const args = [cli, "--offline", "--mode", "rpc", "--no-session",
  "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates",
  "--no-themes", "--no-mcp", "--no-tools", "--no-approve", "-e", extension];
const child = spawn(process.execPath, args, {
  cwd: output, env, stdio: ["pipe", "pipe", "pipe"], windowsHide: true,
});
const records: RecordValue[] = [];
const invalidLines: string[] = [];
const checks: Check[] = [];
let stdout = "", stderr = "", pending = "";
let processError = "";
let finished: { code: number | null; signal: NodeJS.Signals | null } | undefined;
const closed = new Promise<void>(resolve => {
  child.once("close", (code, signal) => { finished = { code, signal }; resolve(); });
});
child.once("error", error => { processError = error.message; });
child.stdout.setEncoding("utf8");
child.stderr.setEncoding("utf8");
child.stdout.on("data", bytes => {
  const chunk = bytes.toString("utf8");
  stdout += chunk;
  pending += chunk;
  let split: number;
  while ((split = pending.indexOf("\n")) >= 0) {
    const line = pending.slice(0, split).replace(/\r$/, "");
    pending = pending.slice(split + 1);
    if (!line.trim()) continue;
    try { records.push(JSON.parse(line)); }
    catch { invalidLines.push(line); }
  }
});
child.stderr.on("data", bytes => { stderr += bytes.toString("utf8"); });

const check = (name: string, passed: boolean, detail?: string) => {
  checks.push({ name, passed, ...(detail ? { detail } : {}) });
  if (!passed) throw new Error(name + (detail ? `: ${detail}` : ""));
};
const send = (value: RecordValue) => child.stdin.write(JSON.stringify(value) + "\n");
const waitFor = async (predicate: (record: RecordValue) => boolean, start = 0): Promise<RecordValue> => {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    const record = records.slice(start).find(predicate);
    if (record) return record;
    if (invalidLines.length) throw new Error("Pi emitted invalid JSONL.");
    if (finished || processError) throw new Error(`Pi exited early: ${JSON.stringify(finished)} ${processError}`);
    await new Promise(resolve => setTimeout(resolve, 20));
  }
  throw new Error("Timed out waiting for a Pi RPC record.");
};
const resultsAfter = (start: number) => records.slice(start).filter(record =>
  record.type === "message_end" && record.message?.customType === "release-checks");
const usage = "Use /release-checks [all|ready|blocked]. Run /release-checks again to choose a view.";
const cases = [
  { value: "All checks", rows: ["R-21: ready", "R-22: blocked", "R-23: ready"] },
  { value: "Ready", rows: ["R-21: ready", "R-23: ready"] },
  { value: "Blocked", rows: ["R-22: blocked"] },
];
let failure: string | undefined;
let forcedTermination = false;
try {
  send({ id: "registered", type: "get_commands" });
  const registered = await waitFor(record => record.id === "registered" && record.type === "response");
  check("Installed Pi registers release-checks", registered.success === true &&
    registered.data?.commands?.some((command: RecordValue) => command.name === "release-checks"));
  for (const [index, item] of cases.entries()) {
    const start = records.length;
    const id = `select-${index}`;
    send({ id, type: "prompt", message: "/release-checks" });
    const selector = await waitFor(record => record.type === "extension_ui_request" && record.method === "select", start);
    check(`${item.value}: selector exposes exact values`,
      JSON.stringify(selector.options) === JSON.stringify(cases.map(value => value.value)) &&
      selector.title === "Release checks — choose a view (Esc to cancel)");
    send({ type: "extension_ui_response", id: selector.id, value: item.value });
    const response = await waitFor(record => record.type === "response" && record.id === id, start);
    check(`${item.value}: direct command handled`, response.success === true && response.data?.disposition === "handled");
    const expected = `Release checks — ${item.value} (${item.rows.length})\n${item.rows.join("\n")}\n${usage}`;
    const results = resultsAfter(start);
    check(`${item.value}: exactly one correct result`, results.length === 1 && results[0].message.content === expected);
  }
  const cancelStart = records.length;
  send({ id: "cancel", type: "prompt", message: "/release-checks" });
  const cancelledSelector = await waitFor(record => record.type === "extension_ui_request" && record.method === "select", cancelStart);
  send({ type: "extension_ui_response", id: cancelledSelector.id, cancelled: true });
  const cancelResponse = await waitFor(record => record.type === "response" && record.id === "cancel", cancelStart);
  check("Cancellation returns handled without starting work", cancelResponse.success === true && cancelResponse.data?.disposition === "handled");
  send({ id: "after-cancel", type: "get_state" });
  const afterCancel = await waitFor(record => record.type === "response" && record.id === "after-cancel", cancelStart);
  check("Cancellation emits no unintended result", afterCancel.success === true && resultsAfter(cancelStart).length === 0);
  check("All three selections retain exactly three results", resultsAfter(0).length === 3);
} catch (error) {
  failure = error instanceof Error ? error.message : String(error);
} finally {
  child.stdin.end();
  let shutdownTimer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<void>(resolve => {
    shutdownTimer = setTimeout(() => { forcedTermination = true; child.kill(); resolve(); }, 5000);
  });
  await Promise.race([closed, timeout]);
  if (shutdownTimer) clearTimeout(shutdownTimer);
  if (forcedTermination) await closed;
  const addFinal = (name: string, passed: boolean) => checks.push({ name, passed });
  addFinal("No model agent or turn events", !records.some(record =>
    ["agent_start", "agent_end", "turn_start", "turn_end"].includes(record.type)));
  addFinal("Every stdout record is valid JSONL", invalidLines.length === 0 && pending.trim() === "");
  addFinal("Process exits successfully without forced termination", !forcedTermination && finished?.code === 0 && finished.signal === null);
  addFinal("Process reports no stderr or spawn errors", stderr.trim() === "" && processError === "");
  addFinal("Generated extension stays byte-for-byte unchanged", before === hash(await fs.readFile(extension)));
  const report = {
    passed: !failure && checks.every(item => item.passed),
    checkedAt: new Date().toISOString(),
    host: { version: version.stdout.trim(), node: process.version, cli },
    extension, extensionSha256: before,
    command: { executable: process.execPath, args, cwd: output, state },
    checks, failure: failure ?? null, processExit: finished, forcedTermination,
    recordCount: records.length,
    resultCount: resultsAfter(0).length,
    boundaries: "Actual installed Pi RPC transport and command execution; TUI paint, focus, resize, installation, and third-party RPC client rendering are untested.",
  };
  await fs.writeFile(path.join(output, "events.jsonl"), stdout);
  await fs.writeFile(path.join(output, "stderr.log"), stderr);
  await fs.writeFile(path.join(output, "result.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify({ passed: report.passed, checks: checks.length,
    passedCount: checks.filter(item => item.passed).length, host: report.host.version,
    result: path.join(output, "result.json"), failure: report.failure }, null, 2));
  if (!report.passed) process.exitCode = 1;
}
