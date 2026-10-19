// Run from this project: node --import tsx --test scripts/storage-tasks.test.ts
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { performance } from 'node:perf_hooks';
import { BACKGROUND_CONTEXT as context } from '@earendil-works/chord/context';
import { fauxAssistantMessage } from '@earendil-works/pi-ai';
import { Harness, MemoryStorage, createRegistry, defineDoc, defineDocFamily, defineExtension, defineTask, ProviderDoc, SessionFailed } from '@earendil-works/pi-durable';
import { openNodeSqliteStorage } from '@earendil-works/pi-durable/storage/sqlite/node';
import { openNodeJsonlStorage } from '@earendil-works/pi-durable/storage/jsonl/node';
import { createStorageConformance } from '@earendil-works/pi-durable/testing';
import { offlineModels, recoveryRegistry } from './recovery-fixture.ts';

const base = resolve('artifacts/storage-tasks');
await mkdir(base, { recursive: true });
async function workspace(label: string) { return mkdtemp(join(base, label + '-')); }
const assertions = {
  ok: assert.ok, strictEqual: assert.strictEqual, deepEqual: assert.deepStrictEqual,
  partialDeepEqual: assert.partialDeepStrictEqual,
  greaterThan: (actual: number, expected: number) => assert.ok(actual > expected),
  rejects: async (operation: Promise<unknown>, message: string) => {
    await assert.rejects(operation, error => error instanceof Error && error.message.includes(message));
  },
};
for (const backend of ['memory', 'sqlite', 'jsonl'] as const) {
  const cases = createStorageConformance({ assertions, withStorage: async use => {
    const directory = await workspace('conformance-' + backend);
    const storage = backend === 'memory' ? new MemoryStorage() : backend === 'sqlite'
      ? await openNodeSqliteStorage(join(directory, 'session.sqlite'))
      : await openNodeJsonlStorage(directory, context, { fsync: true });
    try { await use(storage); } finally { await storage.close(context); }
  } });
  for (const item of cases) test(`storage-${backend}: ${item.name}`, { timeout: 15000 }, item.run);
}

for (const backend of ['sqlite', 'jsonl'] as const) {
  test(`${backend}: reopen preserves conversation, provider ID, answer and request deduplication`, { timeout: 15000 }, async () => {
    const directory = await workspace('reopen-' + backend);
    const open = () => backend === 'sqlite' ? openNodeSqliteStorage(join(directory, 'session.sqlite')) : openNodeJsonlStorage(directory, context, { fsync: true });
    const { models, faux, ref } = offlineModels();
    faux.setResponses([fauxAssistantMessage('persisted answer')]);
    let harness = await Harness.open(await open(), { models, registry: createRegistry() }, context);
    try {
      let root = await harness.root(context, { agent: { model: ref } });
      const submission = await root.submit({ type: 'input', content: 'persist', requestId: 'persist-1' }, context);
      const settled = await submission.wait(context);
      assert.equal(settled.status, 'done');
      const provider = await harness.snapshot(ProviderDoc, root.id, context);
      await harness.close(context);
      harness = await Harness.open(await open(), { models, registry: createRegistry() }, context);
      root = await harness.root(context);
      assert.deepEqual(await harness.snapshot(ProviderDoc, root.id, context), provider);
      const repeated = await root.submit({ type: 'input', content: 'persist', requestId: 'persist-1' }, context);
      assert.equal(repeated.id, submission.id);
      assert.deepEqual(await repeated.wait(context), settled);
      assert.equal(faux.state.callCount, 1);
    } finally { await harness.close(context); }
  });
}

const Ledger = defineDoc<{ count: number }>({ kind: 'lab.ledger', version: 1, scope: 'conversation', history: 'rewindable', fork: 'asOf', initial: () => ({ count: 0 }) });
test('documents: entry and state atomicity, rollback, asOf fork and document family retirement', { timeout: 15000 }, async () => {
  const { models } = offlineModels();
  const harness = await Harness.open(new MemoryStorage(), { models, registry: createRegistry() }, context);
  try {
    const root = await harness.root(context);
    const entry = await root.commit(async tx => {
      (await tx.doc(Ledger, root.id)).count = 1;
      return tx.appendEntry(root.id, { kind: 'lab.note', data: 'first' });
    }, context);
    await root.commit(async tx => { (await tx.doc(Ledger, root.id)).count = 2; }, context);
    assert.equal((await harness.snapshotAsOf(Ledger, root.id, entry.id, context))?.count, 1);
    await assert.rejects(root.commit(async tx => {
      (await tx.doc(Ledger, root.id)).count = 999;
      await tx.appendEntry(root.id, { kind: 'lab.rolled-back', data: null });
      throw new Error('rollback probe');
    }, context), /rollback probe/);
    assert.equal((await harness.snapshot(Ledger, root.id, context))?.count, 2);
    assert.equal((await root.entries({}, 100, undefined, context)).items.some(x => x.kind === 'lab.rolled-back'), false);
    const fork = await root.fork(entry.id, { ownership: { kind: 'ownerless' } }, context);
    assert.equal((await harness.snapshot(Ledger, fork.id, context))?.count, 1);
    const Family = defineDocFamily<{ label: string }, string>({ kind: 'lab.family', version: 1, scope: 'session', family: true, initial: seed => ({ label: seed }) });
    await root.commit(async tx => { (await tx.doc(Family, 'a', 'seed')).label = 'changed'; }, context);
    assert.equal((await harness.snapshot(Family, 'a', context))?.label, 'changed');
    await root.commit(tx => tx.retireDoc(Family, 'a'), context);
    assert.equal(await harness.snapshot(Family, 'a', context), undefined);
  } finally { await harness.close(context); }
});

function terminal(runtime: any, ctx: any, outcome: any) { return runtime.commit(() => ({ status: 'terminal', outcome }), ctx); }
test('tasks: checkpoints, durable memo, owned children, allSettled, failFast, graph and faults', { timeout: 15000 }, async () => {
  const { models } = offlineModels();
  const reports: unknown[] = [];
  const Child = defineTask<{ fail: boolean }, { phase: 'run' }, string>({
    name: 'lab.child', version: 1, initial: () => ({ phase: 'run' }), phases: {
      run: async (task, runtime, ctx) => terminal(runtime, ctx, task.input.fail ? { status: 'failed', error: { message: 'declined' } } : { status: 'completed', result: 'ok' }),
    }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }),
  });
  const Parent = defineTask<{ policy: 'allSettled' | 'failFast' }, { phase: 'spawn' } | { phase: 'collect'; ids: any[] }, string[]>({
    name: 'lab.parent', version: 1, initial: () => ({ phase: 'spawn' }), phases: {
      spawn: async (task, runtime, ctx) => {
        assert.equal(await runtime.memo('decision', 'original', ctx), 'original');
        assert.equal(await runtime.memo('decision', 'replacement', ctx), 'original');
        await runtime.commit(async tx => {
          const ids = await Promise.all([false, true].map(fail => tx.createTask(Child, { fail }, { ownership: { kind: 'task', taskId: task.id } })));
          return { status: 'waiting', checkpoint: { phase: 'collect', ids }, on: ids, policy: task.input.policy };
        }, ctx);
      },
      collect: async (task, runtime, ctx) => {
        assert.equal(await runtime.memo('decision', ctx), 'original');
        const outcomes = await runtime.outcomes(task.state.checkpoint.ids, ctx);
        await terminal(runtime, ctx, { status: 'completed', result: outcomes.map(x => x.status) });
      },
    }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }),
  });
  const Fault = defineTask<null, { phase: 'run' }, null>({ name: 'lab.fault', version: 1, initial: () => ({ phase: 'run' }), phases: { run: async () => {} }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }) });
  const registry = createRegistry(); registry.install(defineExtension({ name: 'tasks', tasks: [Child, Parent, Fault] }));
  const harness = await Harness.open(new MemoryStorage(), { models, registry, onReport: error => reports.push(error) }, context);
  const graph = await harness.taskGraph(context);
  const observed: unknown[] = []; const off = graph.subscribe(value => observed.push(value));
  try {
    const root = await harness.root(context);
    for (const policy of ['allSettled', 'failFast'] as const) {
      const id = await root.commit(tx => tx.createTask(Parent, { policy }, { ownership: { kind: 'conversation' } }), context);
      const task = await harness.waitForTask(id, context);
      assert.equal(task.state.outcome.status, 'completed');
      assert.ok(task.state.outcome.result?.includes('failed'));
      if (policy === 'allSettled') assert.deepEqual(task.state.outcome.result, ['completed', 'failed']);
    }
    const fault = await root.commit(tx => tx.createTask(Fault, null, { ownership: { kind: 'conversation' } }), context);
    const faulted = (await harness.waitForTask(fault, context)).state.outcome;
    assert.equal(faulted.status, 'faulted');
    assert.match(faulted.error?.message ?? '', /progress|checkpoint/i);
    assert.ok(observed.length > 2);
    assert.deepEqual(graph.value.tasks, {});
  } finally { off(); graph.dispose(); await harness.close(context); }
});

test('tasks: missing definitions block until registry install, background idle and abandonOnRestart', { timeout: 15000 }, async () => {
  const { models } = offlineModels();
  const registry = createRegistry();
  const Task = defineTask<null, { phase: 'run' }, string>({ name: 'lab.blocked', version: 1, initial: () => ({ phase: 'run' }), phases: {
    run: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'completed', result: 'installed' }),
  }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }) });
  const harness = await Harness.open(new MemoryStorage(), { models, registry }, context);
  try {
    const root = await harness.root(context);
    const id = await root.commit(tx => tx.createTask(Task, null, { ownership: { kind: 'conversation' }, background: true }), context);
    harness.resume();
    await root.waitForIdle(context);
    const inspection = await harness.inspect(context);
    assert.ok(JSON.stringify(inspection).includes('lab.blocked'));
    assert.notEqual((await harness.getTask(id, context))?.state.status, 'terminal');
    registry.install(defineExtension({ name: 'unblock', tasks: [Task] }));
    assert.equal((await harness.waitForTask(id, context)).state.outcome.status, 'completed');
  } finally { await harness.close(context); }

  const directory = await workspace('abandon');
  const open = () => openNodeSqliteStorage(join(directory, 'session.sqlite'));
  let h = await Harness.open(await open(), { models, registry }, context);
  const root = await h.root(context);
  const id = await root.commit(tx => tx.createTask(Task, null, { ownership: { kind: 'conversation' }, abandonOnRestart: true }), context);
  await h.close(context); // no scheduler was started
  h = await Harness.open(await open(), { models, registry }, context);
  try { assert.equal((await h.waitForTask(id, context)).state.outcome.status, 'aborted'); }
  finally { await h.close(context); }
});

test('tasks: failFast aborts an unfinished owned sibling before parent collect', { timeout: 15000 }, async () => {
  const { models } = offlineModels();
  let started!: () => void; const slowStarted = new Promise<void>(r => { started = r; });
  let aborts = 0;
  const Slow = defineTask<null, { phase: 'run' }, null>({ name: 'lab.slow', version: 1, initial: () => ({ phase: 'run' }), phases: {
    run: async (_task, runtime, ctx) => { started(); await runtime.sleep(runtime.now() + 60000, ctx); },
  }, abort: async (_task, runtime, ctx) => { aborts++; await terminal(runtime, ctx, { status: 'aborted' }); } });
  const Fail = defineTask<null, { phase: 'run' }, null>({ name: 'lab.decline', version: 1, initial: () => ({ phase: 'run' }), phases: {
    run: async (_task, runtime, ctx) => { await slowStarted; await terminal(runtime, ctx, { status: 'failed', error: { message: 'declined' } }); },
  }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }) });
  const Parent = defineTask<null, { phase: 'start' } | { phase: 'end'; ids: any[] }, string[]>({ name: 'lab.join', version: 1, initial: () => ({ phase: 'start' }), phases: {
    start: async (task, runtime, ctx) => runtime.commit(async tx => {
      const ids = [await tx.createTask(Slow, null, { ownership: { kind: 'task', taskId: task.id } }), await tx.createTask(Fail, null, { ownership: { kind: 'task', taskId: task.id } })];
      return { status: 'waiting', checkpoint: { phase: 'end', ids }, on: ids, policy: 'failFast' };
    }, ctx),
    end: async (task, runtime, ctx) => terminal(runtime, ctx, { status: 'completed', result: (await runtime.outcomes(task.state.checkpoint.ids, ctx)).map(x => x.status) }),
  }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }) });
  const registry = createRegistry(); registry.install(defineExtension({ name: 'fail-fast', tasks: [Slow, Fail, Parent] }));
  const harness = await Harness.open(new MemoryStorage(), { models, registry }, context);
  try {
    const root = await harness.root(context);
    const id = await root.commit(tx => tx.createTask(Parent, null, { ownership: { kind: 'conversation' } }), context);
    const outcome = (await harness.waitForTask(id, context)).state.outcome;
    assert.equal(outcome.status, 'completed');
    assert.deepEqual(outcome.result, ['aborted', 'failed']);
    assert.equal(aborts, 1);
  } finally { await harness.close(context); }
});

test('tasks: schema migration, task-scoped documents, background exclusion and inclusive abort', { timeout: 15000 }, async () => {
  const { models } = offlineModels(); const registry = createRegistry();
  const TaskDoc = defineDoc<{ visits: number }>({ kind: 'lab.task-state', version: 1, scope: 'task', initial: () => ({ visits: 0 }) });
  const Old = defineTask<{ value: number }, { phase: 'old' }, number>({ name: 'lab.upgrade', version: 1, initial: () => ({ phase: 'old' }), phases: {
    old: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'completed', result: -1 }),
  }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }) });
  const New = defineTask<{ value: number }, { phase: 'new' }, number>({ name: 'lab.upgrade', version: 2, initial: () => ({ phase: 'new' }),
    migrate: (input, checkpoint, version) => { assert.equal(version, 1); assert.deepEqual(checkpoint, { phase: 'old' }); return { input: input as { value: number }, checkpoint: { phase: 'new' } }; }, phases: {
      new: async (task, runtime, ctx) => { await runtime.commit(async tx => { (await tx.doc(TaskDoc, task.id)).visits++; }, ctx); await terminal(runtime, ctx, { status: 'completed', result: task.input.value + 1 }); },
    }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }),
  });
  const Long = defineTask<null, { phase: 'run' }, null>({ name: 'lab.background', version: 1, initial: () => ({ phase: 'run' }), phases: {
    run: async (_task, runtime, ctx) => { await runtime.sleep(runtime.now() + 60000, ctx); },
  }, abort: async (_task, runtime, ctx) => terminal(runtime, ctx, { status: 'aborted' }) });
  registry.install(defineExtension({ name: 'upgrades', tasks: [New, Long] }));
  const harness = await Harness.open(new MemoryStorage(), { models, registry }, context);
  try {
    const root = await harness.root(context);
    const id = await root.commit(tx => tx.createTask(Old, { value: 8 }, { ownership: { kind: 'conversation' } }), context);
    assert.equal((await harness.waitForTask(id, context)).state.outcome.result, 9);
    assert.equal(await harness.snapshot(TaskDoc, id, context), undefined);
    const bg = await root.commit(tx => tx.createTask(Long, null, { ownership: { kind: 'conversation' }, background: true }), context);
    harness.resume(); await root.waitForIdle(context); await root.abort(context);
    assert.notEqual((await harness.getTask(bg, context))?.state.status, 'terminal');
    await root.abort(context, { background: true });
    assert.equal((await harness.waitForTask(bg, context)).state.outcome.status, 'aborted');
  } finally { await harness.close(context); }
});

test('documents: latest/current/initial forks, read migration, watches and creation callbacks', { timeout: 15000 }, async () => {
  const Current = defineDoc<{ count: number }>({ kind: 'lab.current', version: 1, scope: 'conversation', history: 'latest', fork: 'current', initial: () => ({ count: 0 }) });
  const Initial = defineDoc<{ count: number }>({ kind: 'lab.initial', version: 1, scope: 'conversation', history: 'latest', fork: 'initial', initial: () => ({ count: 0 }) });
  const Migrated = defineDoc<{ count: number; upgraded: boolean }>({ ...Current.definition, version: 2, initial: () => ({ count: 0, upgraded: true }), migrate: (value, from) => { assert.equal(from, 1); return { count: value.count as number, upgraded: true }; } });
  const { models } = offlineModels(); let creations = 0;
  const harness = await Harness.open(new MemoryStorage(), { models, registry: createRegistry(), conversationCreated: async (tx, conversation) => { creations++; await tx.doc(Initial, conversation.id); } }, context);
  try {
    const root = await harness.root(context);
    const entry = await root.commit(async tx => { (await tx.doc(Current, root.id)).count = 1; return tx.appendEntry(root.id, { kind: 'lab.cutoff', data: null }); }, context);
    const state = await harness.documentState(Current, root.id, context); assert.ok(state);
    const changes: unknown[] = []; const unsubscribe = state.subscribe(value => changes.push(value));
    const watch = await harness.watchDoc(Current, root.id, context); assert.ok(watch); const frames: unknown[] = []; watch.start(async (value) => { frames.push(value); });
    try {
      await root.commit(async tx => { (await tx.doc(Current, root.id)).count = 5; (await tx.doc(Initial, root.id)).count = 5; }, context);
      const fork = await root.fork(entry.id, { ownership: { kind: 'ownerless' } }, context);
      assert.equal((await harness.snapshot(Current, fork.id, context))?.count, 5);
      assert.equal((await harness.snapshot(Initial, fork.id, context))?.count, 0);
      assert.deepEqual(await harness.snapshot(Migrated, root.id, context), { count: 5, upgraded: true });
      await root.commit(async tx => { (await tx.doc(Migrated, root.id)).count = 6; }, context);
      assert.equal(creations, 2); assert.ok(changes.length >= 2);
      await watch.stop(); assert.ok(frames.length >= 1);
    } finally { unsubscribe(); state.dispose(); await watch.stop(); }
  } finally { await harness.close(context); }
});

for (const mode of ['safe', 'unsafe', 'checkpoint']) {
  test(`process-kill: ${mode} recovery uses committed state`, { timeout: 20000 }, async () => {
    const directory = await workspace('kill-' + mode);
    const child = spawn(process.execPath, ['--import', 'tsx', 'scripts/recovery-fixture.ts', directory, mode], { cwd: process.cwd(), stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
    let output = ''; let error = '';
    child.stderr.on('data', chunk => { error += chunk; });
    const ready = new Promise<void>((resolveReady, reject) => {
      const timeout = setTimeout(() => reject(new Error('worker did not reach checkpoint: ' + error)), 12000);
      child.stdout.on('data', chunk => { output += chunk; if (output.includes('READY')) { clearTimeout(timeout); resolveReady(); } });
      child.once('exit', () => { clearTimeout(timeout); if (!output.includes('READY')) reject(new Error('worker exited early: ' + error)); });
    });
    try { await ready; } finally {
      if (child.exitCode === null && child.signalCode === null) {
        const exited = once(child, 'exit'); child.kill('SIGKILL'); await exited;
      }
    }
    const { models, faux } = offlineModels();
    faux.setResponses([fauxAssistantMessage('recovery answer')]);
    const { registry } = recoveryRegistry(directory, mode, false);
    const harness = await Harness.open(await openNodeSqliteStorage(join(directory, 'session.sqlite')), { models, registry }, context);
    try {
      harness.resume(); await harness.waitForIdle(context);
      const effects = (await readFile(join(directory, 'effects.txt'), 'utf8')).trim().split('\n');
      if (mode === 'checkpoint') {
        assert.deepEqual(effects, ['first-phase']);
        const task = await harness.getTask(Number(await readFile(join(directory, 'task-id.txt'), 'utf8')) as any, context);
        assert.equal(task?.state.status, 'terminal');
        assert.equal((task?.state as any).outcome.result, 'checkpoint-resumed');
      } else {
        assert.equal(effects.length, mode === 'safe' ? 2 : 1);
        const root = await harness.root(context);
        const entries = (await root.entries({}, 100, undefined, context)).items;
        const result = entries.find(x => x.kind === 'pi.tool-result');
        assert.ok(result);
        assert.equal(JSON.stringify(result).includes('interrupted'), mode === 'unsafe');
        const repeated = await root.submit({ type: 'input', content: 'Run the replay probe', requestId: 'recovery-input' }, context);
        assert.equal((await repeated.wait(context)).status, 'done');
      }
    } finally { await harness.close(context); }
  });
}

test('errors: fatal storage failure closes Harness; reopening is required', { timeout: 15000 }, async () => {
  class FailingStorage extends MemoryStorage {
    fail = false;
    override async commit(...args: Parameters<MemoryStorage['commit']>) {
      if (this.fail) throw new Error('injected disk failure');
      return super.commit(...args);
    }
  }
  const storage = new FailingStorage(); const { models } = offlineModels(); const reports: unknown[] = [];
  const harness = await Harness.open(storage, { models, registry: createRegistry(), onReport: error => reports.push(error) }, context);
  const root = await harness.root(context);
  storage.fail = true;
  await assert.rejects(root.submit({ type: 'write', entry: { kind: 'lab.fail', data: null } }, context), /injected disk failure/);
  assert.equal((await harness.closed).reason, 'failed');
  await assert.rejects(harness.root(context), SessionFailed);
  assert.equal(reports.length, 1);
});

test('comparison: small sequential commit timing for memory, SQLite and JSONL fsync variants', { timeout: 30000 }, async () => {
  const measurements: unknown[] = [];
  for (const backend of ['memory', 'sqlite', 'jsonl', 'jsonl-fsync']) {
    const directory = await workspace('timing-' + backend); const { models } = offlineModels();
    const started = performance.now();
    const storage = backend === 'memory' ? new MemoryStorage() : backend === 'sqlite' ? await openNodeSqliteStorage(join(directory, 'session.sqlite')) : await openNodeJsonlStorage(directory, context, { fsync: backend === 'jsonl-fsync' });
    const harness = await Harness.open(storage, { models, registry: createRegistry() }, context);
    const openMs = performance.now() - started;
    try {
      const root = await harness.root(context); const samples: number[] = [];
      for (let i = 0; i < 30; i++) { const t = performance.now(); await root.submit({ type: 'write', entry: { kind: 'lab.measurement', data: { i } } }, context); samples.push(performance.now() - t); }
      samples.sort((a, b) => a - b);
      measurements.push({ backend, writes: 30, openMs, medianMs: samples[15], p95Ms: samples[28], totalMs: samples.reduce((a,b) => a+b, 0) });
    } finally { await harness.close(context); }
  }
  await writeFile(join(base, 'storage-timing.json'), JSON.stringify({ note: 'Small local smoke comparison, one process, 30 passive writes per backend, no remote model, not a throughput benchmark.', node: process.version, measurements }, null, 2));
});
