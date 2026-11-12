#!/usr/bin/env node
// Run with Node 24 native TypeScript support: node projects/desktop-plugin-ui/scripts/test-build-interactions-verifier.ts
// Requires Node 24+ only. Generated fixtures stay in the owning project's artifacts.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fixtureRoot = path.join(projectRoot, "artifacts", "verifier-selftest");
const verifier = path.join(projectRoot, "scripts", "verify-build-interactions.ts");
const source = `export default function(pi: any) {
  const rows = [
    { id: "T-104", status: "pending", priority: "high" },
    { id: "T-105", status: "pending", priority: "normal" },
    { id: "T-106", status: "closed", priority: "high" }
  ];
  pi.registerCommand("queue-view", { description: "View queue", async handler(_args: string, ctx: any) {
    const display = (items: any[]) => items.map(row => row.id + " | " + row.status + " | " + row.priority).join("\\n");
    if (!ctx.hasUI) {
      pi.sendMessage({customType:"queue-view",content:display(rows)+"\\nRun pi -e ./plugin/queue.ts in an interactive terminal, then /queue-view.",display:true}, {triggerTurn:false});
      return;
    }
    const choice = await ctx.ui.select("View queue", ["All tickets", "Pending tickets", "High priority"]);
    if (choice === undefined) { ctx.ui.notify("Cancelled.", "info"); return; }
    const selected = choice === "Pending tickets" ? rows.filter(row => row.status === "pending") : choice === "High priority" ? rows.filter(row => row.priority === "high") : rows;
    ctx.ui.notify(display(selected), "info");
  }});
}`;
const releaseSource = `export default function(pi: any) {
  const rows = [{id:"R-21",state:"ready"},{id:"R-22",state:"blocked"},{id:"R-23",state:"ready"}];
  pi.registerCommand("release-checks", { description: "View release checks", async handler(_args: string, ctx: any) {
    const display = (items: any[]) => items.map(row => row.id + " | " + row.state).join("\\n");
    if (!ctx.hasUI) { pi.sendMessage({customType:"release-checks",content:display(rows)+"\\nRun pi -e ./extension/releases.ts in an interactive terminal, then /release-checks.",display:true}); return; }
    const choice = await ctx.ui.select("Release checks", ["All checks", "Ready", "Blocked"]);
    if (choice === undefined) return;
    const selected = choice === "Ready" ? rows.filter(row => row.state === "ready") : choice === "Blocked" ? rows.filter(row => row.state === "blocked") : rows;
    ctx.ui.notify(display(selected), "info");
  }});
}`;
const cases = [
  { name: "valid-contract", expected: true, source },
  { name: "implicit-cancel-default", expected: false, source: source.replace('if (choice === undefined) { ctx.ui.notify("Cancelled.", "info"); return; }', "") },
  { name: "filter-ignored", expected: false, source: source.replace('ctx.ui.notify(display(selected), "info")', 'ctx.ui.notify(display(rows), "info")') },
  { name: "wrong-priority", expected: false, source: source.replace('{ id: "T-104", status: "pending", priority: "high" }', '{ id: "T-104", status: "pending", priority: "normal" }') },
  { name: "headless-ui-no-op", expected: false, source: source.replace('pi.sendMessage({customType:"queue-view",content:display(rows)+"\\nRun pi -e ./plugin/queue.ts in an interactive terminal, then /queue-view.",display:true}, {triggerTurn:false});', 'ctx.ui.notify(display(rows), "info");') },
  { name: "unexpected-model-turn", expected: false, source: source.replace('ctx.ui.notify(display(selected), "info");', 'pi.sendUserMessage("Explain selected rows"); ctx.ui.notify(display(selected), "info");') },
  { name: "valid-naturalistic", case: "naturalistic", expected: true, source: releaseSource },
  { name: "wrong-release-state", case: "naturalistic", expected: false, source: releaseSource.replace('{id:"R-22",state:"blocked"}', '{id:"R-22",state:"ready"}') },
];
const results = [];
for (const test of cases) {
  const workspace = path.join(fixtureRoot, test.name);
  const naturalistic = test.case === "naturalistic";
  const sourceDirectory = naturalistic ? "extension" : "plugin";
  fs.mkdirSync(path.join(workspace, sourceDirectory), { recursive: true });
  fs.mkdirSync(path.join(workspace, "review"), { recursive: true });
  fs.writeFileSync(path.join(workspace, sourceDirectory, naturalistic ? "releases.ts" : "queue.ts"), test.source);
  fs.writeFileSync(path.join(workspace, "review", naturalistic ? "design.md" : "interaction-review.md"), "Evaluator fixture; not a model result.\n");
  fs.writeFileSync(path.join(workspace, "review", naturalistic ? "validation.json" : "checks.json"), JSON.stringify({
    checks: [{ name: "fixture", method: "independent test", expected: "fixture", actual: "fixture", status: "pass" }],
    heuristics: Array.from({ length: 10 }, (_, index) => ({ id: `H${index + 1}` })),
    complexity: { visible_controls: 1, required_decisions: 1, primary_actions: 1, runtime_processes_added: 0, rationale: "fixture" },
    host_paint_verified: false,
    user_testing_performed: false,
  }));
  const invocation = spawnSync(process.execPath, [verifier, workspace, test.case ?? "contract"], { encoding: "utf8", timeout: 15000 });
  const actual = invocation.status === 0;
  results.push({ name: test.name, passed: actual === test.expected, expected_acceptance: test.expected, actual_acceptance: actual, stdout: invocation.stdout.trim(), stderr: invocation.stderr.trim() });
}
const result = { passed: results.every(item => item.passed), results };
fs.writeFileSync(path.join(fixtureRoot, "results.json"), JSON.stringify(result, null, 2) + "\n");
console.log(JSON.stringify(result));
process.exitCode = result.passed ? 0 : 1;
