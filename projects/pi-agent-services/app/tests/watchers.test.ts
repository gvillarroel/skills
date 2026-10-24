import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, writeFile, readFile, rm } from 'node:fs/promises';
import { join, resolve, sep } from 'node:path';
import { Watchers, APPROVED_VALIDATORS, runReadOnlyCommand, type CommandResult, type CommandSpec } from '../src/watchers.js';

const okay = (stdout = ''): CommandResult => ({ code: 0, stdout, stderr: '', timedOut: false, truncated: false });
const initialHead = 'a'.repeat(40);
function sourceResult(spec: CommandSpec, head = initialHead): CommandResult {
  if (spec.command !== 'git') return okay('Passed');
  if (spec.args[0] === 'rev-parse') return okay(head);
  return okay(spec.args[0] === 'ls-files' ? 'skills/demo/SKILL.md\0projects/ignored.ts\0' : '');
}

async function fixture() {
  const cache = resolve('.cache', 'watcher-tests');
  await mkdir(cache, { recursive: true });
  const root = await mkdtemp(join(cache, 'case-'));
  await mkdir(join(root, 'skills', 'demo'), { recursive: true });
  await writeFile(join(root, 'skills', 'demo', 'SKILL.md'), 'first');
  const cleanup = async () => {
    assert.ok(root.startsWith(`${cache}${sep}`));
    await rm(root, { recursive: true, force: true });
  };
  return { root, cleanup };
}

test('repo watcher requires 30 seconds of stability, persists pending admission, and does not repeat identical input', async () => {
  const { root, cleanup } = await fixture();
  try {
    let now = 1000;
    const calls: CommandSpec[] = [];
    const runner = async (spec: CommandSpec) => {
      calls.push(spec);
      return sourceResult(spec);
    };
    const options = { projectDir: root, stateDir: join(root, 'state'), runner, now: () => now };
    const watchers = new Watchers(options);
    assert.equal(await watchers.tick('repo-quality'), undefined);
    now += 29_999;
    assert.equal(await watchers.tick('repo-quality'), undefined);
    assert.equal(calls.filter(call => call.command === 'uv').length, 0);
    now += 1;
    const event = await watchers.tick('repo-quality');
    assert.equal(event?.type, 'workspace.changed');
    assert.equal(event?.snapshot.kind, 'initial-readiness');
    assert.equal(event?.snapshot.fileCount, 1);
    assert.equal(event?.snapshot.dirtySourceCount, 1);
    assert.equal(event?.snapshot.head, initialHead);
    assert.equal(event?.snapshot.baseline, 'git-head-plus-dirty-sources');
    assert.ok(calls.filter(call => call.command === 'git').every(call => !call.args.includes('--cached')));
    assert.deepEqual(calls.filter(call => call.command === 'uv').map(call => call.args), APPROVED_VALIDATORS.map(script => ['run', '--script', script]));
    const restarted = new Watchers(options);
    assert.deepEqual(await restarted.tick('repo-quality'), event);
    await restarted.ack('repo-quality', event!.id);
    now += 60_000;
    assert.equal(await restarted.tick('repo-quality'), undefined);
    assert.equal(calls.filter(call => call.command === 'uv').length, 4);
  } finally { await cleanup(); }
});

test('untracked skill content changes trigger another debounced event, and reverting resets the stability clock', async () => {
  const { root, cleanup } = await fixture();
  try {
    let now = 0;
    const runner = async (spec: CommandSpec) => sourceResult(spec);
    const watcher = new Watchers({ projectDir: root, stateDir: join(root, 'state'), runner, now: () => now });
    await watcher.tick('repo-quality');
    now = 30_000;
    const first = (await watcher.tick('repo-quality'))!;
    await watcher.ack('repo-quality', first.id);
    await writeFile(join(root, 'skills', 'demo', 'SKILL.md'), 'second');
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now = 50_000;
    await writeFile(join(root, 'skills', 'demo', 'SKILL.md'), 'first');
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now = 60_000;
    await writeFile(join(root, 'skills', 'demo', 'SKILL.md'), 'second');
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now = 89_999;
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now = 90_000;
    const second = (await watcher.tick('repo-quality'))!;
    assert.notEqual(second.id, first.id);
    assert.deepEqual(second.snapshot.changedFiles, ['skills/demo/SKILL.md']);
    assert.equal(second.snapshot.kind, 'source-change');
    await watcher.ack('repo-quality', second.id);
    await writeFile(join(root, 'skills', 'demo', 'SKILL.md'), 'first');
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now += 30_000;
    const reverted = (await watcher.tick('repo-quality'))!;
    assert.equal(reverted.snapshot.fingerprint, first.snapshot.fingerprint);
    assert.notEqual(reverted.id, first.id);
  } finally { await cleanup(); }
});

test('source changes during validators invalidate the report and begin a fresh stability interval', async () => {
  const { root, cleanup } = await fixture();
  try {
    let now = 0;
    let mutate = true;
    const runner = async (spec: CommandSpec) => {
      if (spec.command === 'git') return sourceResult(spec);
      if (mutate) { mutate = false; await writeFile(join(root, 'skills', 'demo', 'SKILL.md'), 'during-validation'); }
      return okay('Passed');
    };
    const watcher = new Watchers({ projectDir: root, stateDir: join(root, 'state'), runner, now: () => now });
    await watcher.tick('repo-quality');
    now = 30_000;
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now = 60_000;
    assert.equal((await watcher.tick('repo-quality'))?.snapshot.kind, 'initial-readiness');
  } finally { await cleanup(); }
});

test('a new committed HEAD triggers validation even when dirty source contents stay identical', async () => {
  const { root, cleanup } = await fixture();
  try {
    let now = 0;
    let head = initialHead;
    const calls: CommandSpec[] = [];
    const runner = async (spec: CommandSpec) => { calls.push(spec); return sourceResult(spec, head); };
    const watcher = new Watchers({ projectDir: root, stateDir: join(root, 'state'), runner, now: () => now });
    await watcher.tick('repo-quality');
    now = 30_000;
    const first = (await watcher.tick('repo-quality'))!;
    await watcher.ack('repo-quality', first.id);
    head = 'b'.repeat(40);
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now += 30_000;
    const committed = (await watcher.tick('repo-quality'))!;
    assert.notEqual(committed.snapshot.fingerprint, first.snapshot.fingerprint);
    assert.equal(committed.snapshot.headChanged, true);
    assert.equal(committed.snapshot.head, head);
    assert.equal(committed.snapshot.dirtySourceCount, 1);
    assert.ok(calls.some(call => call.args[0] === 'diff' && call.args[3] === head));
  } finally { await cleanup(); }
});

test('legacy full-inventory checkpoints migrate without reporting committed paths as deleted sources', async () => {
  const { root, cleanup } = await fixture();
  try {
    let now = 0;
    const stateDir = join(root, 'state');
    const checkpointPath = join(stateDir, 'watchers', 'repo-quality.json');
    await mkdir(join(stateDir, 'watchers'), { recursive: true });
    const publishedFiles = Object.fromEntries(Array.from({ length: 10_000 }, (_, index) => [`skills/retained-${index}/SKILL.md`, 'legacy-content-hash']));
    await writeFile(checkpointPath, JSON.stringify({ version: 1, publishedHash: 'legacy-full-inventory', publishedFiles, sequence: 7 }));
    const watcher = new Watchers({ projectDir: root, stateDir, runner: async spec => sourceResult(spec), now: () => now });
    assert.equal(await watcher.tick('repo-quality'), undefined);
    now = 30_000;
    const event = (await watcher.tick('repo-quality'))!;
    assert.equal(event.snapshot.kind, 'baseline-migration');
    assert.equal(event.snapshot.baselineChanged, true);
    assert.equal(event.snapshot.changedFileScope, 'current-dirty-sources');
    assert.equal(event.snapshot.changedFileCount, 1);
    assert.deepEqual(event.snapshot.changedFiles, ['skills/demo/SKILL.md']);
    const pendingCheckpoint = JSON.parse(await readFile(checkpointPath, 'utf8'));
    assert.equal(Object.keys(pendingCheckpoint.publishedFiles).length, 10_000);
    assert.equal(pendingCheckpoint.publishedHead, undefined);
    assert.equal(pendingCheckpoint.sequence, 7);
    const restarted = new Watchers({ projectDir: root, stateDir, runner: async spec => sourceResult(spec), now: () => now });
    assert.equal((await restarted.tick('repo-quality'))!.id, event.id);
    await restarted.ack('repo-quality', event.id);
    const admittedCheckpoint = JSON.parse(await readFile(checkpointPath, 'utf8'));
    assert.equal(admittedCheckpoint.publishedHead, initialHead);
    assert.equal(Object.keys(admittedCheckpoint.publishedFiles).length, 1);
    assert.equal(admittedCheckpoint.sequence, 8);
    assert.equal(await restarted.tick('repo-quality'), undefined);
  } finally { await cleanup(); }
});

test('delivery watcher omits check timestamps from deduplication and reacts to meaningful status transitions', async () => {
  const { root, cleanup } = await fixture();
  try {
    let conclusion = 'SUCCESS';
    let timestamp = 'earlier';
    const runner = async (spec: CommandSpec) => {
      if (spec.command === 'git') return okay(spec.args[0] === 'rev-parse' ? 'abc123\n' : ' M skills/demo/SKILL.md\0?? projects/private/\0');
      if (spec.args[0] === 'pr') return okay(JSON.stringify([{ number: 12, title: 'PR fixture', statusCheckRollup: [{ name: 'test', status: 'COMPLETED', conclusion, startedAt: timestamp }] }]));
      return okay('[]');
    };
    const watcher = new Watchers({ projectDir: root, stateDir: join(root, 'state'), runner });
    const event = (await watcher.tick('delivery-watch'))!;
    assert.equal(event.snapshot.kind, 'initial-readiness');
    assert.deepEqual(event.snapshot.status, [' M skills/demo/SKILL.md']);
    await watcher.ack('delivery-watch', event.id);
    timestamp = 'later';
    assert.equal(await watcher.tick('delivery-watch'), undefined);
    conclusion = 'FAILURE';
    const changed = (await watcher.tick('delivery-watch'))!;
    assert.notEqual(changed.id, event.id);
    assert.equal(changed.snapshot.kind, 'delivery-change');
    await watcher.ack('delivery-watch', changed.id);
    conclusion = 'SUCCESS';
    const recovered = (await watcher.tick('delivery-watch'))!;
    assert.equal(recovered.snapshot.fingerprint, event.snapshot.fingerprint);
    assert.notEqual(recovered.id, event.id);
    const restarted = new Watchers({ projectDir: root, stateDir: join(root, 'state'), runner });
    assert.equal((await restarted.tick('delivery-watch'))!.id, recovered.id);
    await restarted.ack('delivery-watch', recovered.id);
    assert.equal(await restarted.tick('delivery-watch'), undefined);
  } finally { await cleanup(); }
});

test('delivery command failures remain explicit observations rather than invented PR data', async () => {
  const { root, cleanup } = await fixture();
  try {
    const runner = async (spec: CommandSpec) => spec.command === 'gh' ? { ...okay(), code: 1, stderr: 'Authentication required' } : okay('abc123');
    const watcher = new Watchers({ projectDir: root, stateDir: join(root, 'state'), runner });
    const event = (await watcher.tick('delivery-watch'))!;
    const error = event.snapshot.pullRequests as { error: { exitCode: number; stderr: string } };
    assert.equal(error.error.exitCode, 1);
    assert.equal(error.error.stderr, 'Authentication required');
  } finally { await cleanup(); }
});

test('command runner bounds retained output and terminates an over-deadline process', async () => {
  const output = await runReadOnlyCommand({ command: process.execPath, args: ['-e', 'process.stdout.write("x".repeat(10000))'], cwd: process.cwd(), timeoutMs: 2000, maxOutputBytes: 1024 });
  assert.equal(output.code, 0);
  assert.equal(output.stdout.length, 1024);
  assert.equal(output.truncated, true);
  const started = Date.now();
  const timeout = await runReadOnlyCommand({ command: process.execPath, args: ['-e', 'setInterval(()=>{},1000)'], cwd: process.cwd(), timeoutMs: 100 });
  assert.equal(timeout.timedOut, true);
  assert.ok(Date.now() - started < 5000);
});

test('watcher shutdown aborts in-flight work and does not publish a failure snapshot', async () => {
  const { root, cleanup } = await fixture();
  try {
    let entered: () => void;
    const started = new Promise<void>(resolveStarted => { entered = resolveStarted; });
    const runner = (spec: CommandSpec): Promise<CommandResult> => new Promise(resolveResult => {
      entered();
      spec.signal!.addEventListener('abort', () => resolveResult({ ...okay(), code: null, aborted: true }), { once: true });
    });
    const watcher = new Watchers({ projectDir: root, stateDir: join(root, 'state'), runner });
    const inFlight = watcher.tick('delivery-watch');
    await started;
    watcher.close();
    assert.equal(await inFlight, undefined);
    assert.equal(await watcher.tick('delivery-watch'), undefined);
  } finally { await cleanup(); }
});

test('command cancellation terminates an active process without reporting a timeout', async () => {
  const controller = new AbortController();
  const result = runReadOnlyCommand({ command: process.execPath, args: ['-e', 'setInterval(()=>{},1000)'], cwd: process.cwd(), timeoutMs: 10000, signal: controller.signal });
  setTimeout(() => controller.abort(), 100);
  const observed = await result;
  assert.equal(observed.aborted, true);
  assert.equal(observed.timedOut, false);
});
