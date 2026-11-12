#!/usr/bin/env node
// Run with Node 24 native TypeScript: node projects/plugin-ui-host-split/scripts/verify_pi_starter.ts
import fs from "node:fs/promises";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";

const root = process.cwd();
const label = process.argv[2] ?? "pi-starter-v2";
if (!/^[a-z0-9-]+$/.test(label)) throw new Error("Use a lowercase task-local run label.");
const output = path.resolve(root, "projects/plugin-ui-host-split/artifacts", label);
await fs.mkdir(output, { recursive: true });
const extension = path.resolve(root, "skills/pi-extension-ui/assets/templates/pi-command/view-mode.ts");
const probe = spawnSync("python", ["skills/pi-extension-ui/scripts/probe_runtime.py", "--host", "pi"], { cwd: root, encoding: "utf8", windowsHide: true });
if (probe.status !== 0) throw new Error(probe.stderr);
const readiness = JSON.parse(probe.stdout);
if (!readiness.passed) throw new Error("Pi readiness failed.");
const cli = readiness.checks.find((check: any) => check.name === "pi").command[1];
const hash = (bytes: Uint8Array) => createHash("sha256").update(bytes).digest("hex");
const before = hash(await fs.readFile(extension));
const args = [cli, "--offline", "--mode", "rpc", "--no-session", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-mcp", "--no-tools", "--no-approve", "-e", extension];
const env = { ...process.env, PI_CODING_AGENT_DIR: path.join(output, "state") };
const child = spawn(process.execPath, args, { cwd: output, env, stdio: ["pipe", "pipe", "pipe"], windowsHide: true });
const events: any[] = [];
const checks: any[] = [];
let pending = "", raw = "", stderr = "", error: string | undefined;
child.stdout.setEncoding("utf8");
child.stderr.setEncoding("utf8");
child.stdout.on("data", chunk => {
  raw += chunk; pending += chunk;
  let split: number;
  while ((split = pending.indexOf("\n")) >= 0) {
    const line = pending.slice(0, split).trim(); pending = pending.slice(split + 1);
    if (line) { try { events.push(JSON.parse(line)); } catch { error = `Invalid RPC JSON: ${line}`; } }
  }
});
child.stderr.on("data", chunk => { stderr += chunk; });
child.on("error", reason => { error = String(reason); });
function check(name: string, passed: unknown, detail?: unknown) {
  checks.push({ name, passed: Boolean(passed), detail });
  if (!passed) throw new Error(name);
}
function send(message: object) { child.stdin.write(JSON.stringify(message) + "\n"); }
async function wait(predicate: (event: any) => boolean, start = 0) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    if (error) throw new Error(error);
    const found = events.slice(start).find(predicate);
    if (found) return found;
    await new Promise(resolve => setTimeout(resolve, 20));
  }
  throw new Error("RPC response timeout.");
}
let sequence = 0;
async function invoke(argument: string, answer?: string | null, expectedTitle?: string) {
  const start = events.length, id = `command-${++sequence}`;
  send({ id, type: "prompt", message: `/view-mode${argument ? " " + argument : ""}` });
  if (answer !== undefined) {
    const request = await wait(event => event.type === "extension_ui_request" && event.method === "select", start);
    if (expectedTitle) check(`Selector shows ${expectedTitle}`, request.title === expectedTitle, request);
    send({ type: "extension_ui_response", id: request.id, ...(answer === null ? { cancelled: true } : { value: answer }) });
  }
  const response = await wait(event => event.type === "response" && event.id === id, start);
  check(`Command ${id} was handled`, response.success && response.data?.disposition === "handled", response);
  return events.slice(start);
}
try {
  send({ id: "commands", type: "get_commands" });
  const commands = await wait(event => event.type === "response" && event.id === "commands");
  check("Real Pi discovers view-mode", commands.success && commands.data.commands.some((command: any) => command.name === "view-mode"));
  let result = await invoke("", "detailed", "Output: compact");
  check("Selection reports detailed", result.some(event => event.method === "notify" && event.message === "Output mode: detailed"));
  result = await invoke("", null, "Output: detailed");
  check("Cancel has no success notification", !result.some(event => event.method === "notify"));
  await invoke("", null, "Output: detailed");
  result = await invoke("broken");
  check("Invalid argument provides usable command", result.some(event => event.method === "notify" && event.message === "Use /view-mode compact or /view-mode detailed."));
  result = await invoke("compact");
  check("Explicit argument bypasses selector", !result.some(event => event.method === "select") && result.some(event => event.message === "Output mode: compact"));
  check("RPC commands use no model turn", !events.some(event => ["agent_start", "turn_start"].includes(event.type)));
  const printed = spawnSync(process.execPath, [cli, "--offline", "--mode", "json", "--print", "--no-session", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-mcp", "--no-tools", "--no-approve", "-e", extension, "/view-mode compact"], { cwd: output, env, encoding: "utf8", timeout: 30000, windowsHide: true });
  await fs.writeFile(path.join(output, "print.jsonl"), printed.stdout);
  const printEvents = printed.stdout.split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
  check("JSON print returns exact custom result without inference", printed.status === 0 && printEvents.some(event => event.message?.customType === "view-mode" && event.message?.content === "Output mode: compact") && !printEvents.some(event => ["agent_start", "turn_start"].includes(event.type)), printed.stderr);
  check("Skill template is unchanged", hash(await fs.readFile(extension)) === before);
} catch (reason) {
  error = String(reason);
} finally {
  child.kill();
  await fs.writeFile(path.join(output, "rpc.jsonl"), raw);
  await fs.writeFile(path.join(output, "stderr.txt"), stderr);
  const report = { passed: !error && checks.every(check => check.passed), version: readiness.checks.find((check: any) => check.name === "pi").version, checks, error, scope: "Real Pi RPC and JSON-print command behavior; visible TUI remains untested." };
  await fs.writeFile(path.join(output, "review.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  if (!report.passed) process.exitCode = 1;
}
