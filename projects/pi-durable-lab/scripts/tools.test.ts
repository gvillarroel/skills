import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { deflateSync } from 'node:zlib';
import { resolve, join } from 'node:path';
import { BACKGROUND_CONTEXT as ctx } from '@earendil-works/chord/context';
import { Type } from '@earendil-works/pi-ai';
import { createModels } from '@earendil-works/pi-ai/models';
import { fauxProvider, fauxAssistantMessage as answer, fauxToolCall as call } from '@earendil-works/pi-ai/providers/faux';
import { Harness, MemoryStorage, createRegistry, defineExtension, defineTool, hook, section, ToolTask, wrapTool } from '@earendil-works/pi-durable';
import { createCodingTools, createPowerShellTool } from '@earendil-works/pi-durable/tools';
import { NodeExecutionEnv } from '@earendil-works/pi-durable/env/node';
import { getOrThrow } from '@earendil-works/pi-durable/env';
import { createToolSearchExtension } from '@earendil-works/pi-durable/tool-search';
import { createCodemodeExtension } from '@earendil-works/pi-durable/codemode';
import { CodemodeSandbox } from '@earendil-works/pi-codemode';

const outputRoot = resolve('artifacts/tools');
await mkdir(outputRoot, { recursive: true });
const reports: Record<string, unknown>[] = [];
const txt = (text: string) => [{ type: 'text' as const, text }];
const empty = Type.Object({});
const pause = (ms: number) => new Promise(r => setTimeout(r, ms));
async function fixture(extensions: any[], options: any = {}) {
  const faux = fauxProvider({ tokensPerSecond: 100000, models: [{ id: 'probe', input: ['text', 'image'] }] });
  const models = createModels();
  models.setProvider(faux.provider);
  const registry = createRegistry();
  for (const extension of extensions) registry.install(extension);
  const reported: string[] = [];
  const harness = await Harness.open(new MemoryStorage(), {
    models, registry, onReport: error => reported.push(String(error)), ...options,
  }, ctx);
  const root = await harness.root(ctx, { agent: { model: { provider: faux.getModel().provider, modelId: 'probe' }, cwd: outputRoot } });
  const toolOrder: string[] = [];
  async function run(calls: any[], check?: any) {
    toolOrder.push(...calls.map(call => call.id));
    faux.setResponses([answer(calls, { stopReason: 'toolUse' }), check ?? answer('completed')]);
    const settled = await (await root.submit({ type: 'input', content: 'Execute the deterministic probe.' }, ctx)).wait(ctx);
    assert.equal(settled.status, 'done');
    const view = await root.viewState(ctx);
    const entries = structuredClone(view.value.entries);
    view.dispose();
    const toolResults = entries.filter((e: any) => e.kind === 'pi.tool-result').sort((a: any, b: any) => toolOrder.indexOf(a.model[0].toolCallId) - toolOrder.indexOf(b.model[0].toolCallId));
    return { entries, toolResults };
  }
  return { faux, registry, harness, root, run, reported };
}

test('TypeBox validation, streamed output, details, errors and schema channels', { timeout: 20000 }, async () => {
  let executed = 0;
  const count = defineTool({ name: 'count', description: 'Count items', parameters: Type.Object({ n: Type.Number({ minimum: 1 }) }),
    execute: async ({ n }, api) => { executed++; for (let i = 1; i <= n; i++) api.output(`${i}\n`); await api.details({ n }, ctx); return {}; } });
  const broken = defineTool({ name: 'broken', description: 'Throw an execution error', parameters: empty,
    execute: async () => { throw new Error('intentional failure'); } });
  const f = await fixture([defineExtension({ name: 'custom', tools: [count, broken] })]);
  try {
    const { toolResults } = await f.run([call('count', { n: 3 }), call('count', { n: 'wrong' }), call('broken', {})]);
    assert.equal(executed, 1);
    assert.equal(toolResults.length, 3);
    const messages = toolResults.map((e: any) => e.model[0]);
    assert.match(JSON.stringify(messages[0]), /1\\n2\\n3/);
    assert.equal(messages[1].isError, true);
    assert.match(JSON.stringify(messages[1]), /invalid|validation/i);
    assert.equal(messages[2].isError, true);
    assert.match(JSON.stringify(messages[2]), /intentional failure/);
    assert.match(JSON.stringify(toolResults[0]), /"n":3/);
    reports.push({ test: 'custom-tools', executed, messages });
  } finally { await f.harness.close(ctx); }
});

test('nested callers, modelTools, structured outputs and invalid schema results', { timeout: 20000 }, async () => {
  const received: any[] = [];
  const value = defineTool({ name: 'value', description: 'Program value', callers: ['tools'], parameters: empty,
    structuredOutputSchema: Type.Object({ count: Type.Number() }), execute: async () => ({ output: txt('model-only text'), structuredOutput: { count: 42 }, details: { internal: true } }) });
  const bad = defineTool({ name: 'bad', description: 'Invalid program value', callers: ['tools'], parameters: empty,
    structuredOutputSchema: Type.Object({ count: Type.Number() }), execute: async () => ({ output: txt('bad'), structuredOutput: { count: 'wrong' } }) });
  const modelOnly = defineTool({ name: 'model_only', description: 'Only model can call', callers: ['model'], parameters: empty, execute: async () => ({ output: txt('hello') }) });
  const plain = defineTool({ name: 'plain', description: 'Plain text', parameters: empty, execute: async () => ({ output: txt('plain text') }) });
  const bridge = defineTool({ name: 'bridge', description: 'Call all nested probes', parameters: empty, execute: async (_args, api, context) => {
    for (const name of ['value', 'bad', 'model_only', 'plain', 'missing']) received.push(await api.executeTool(name, {}, context, { key: `probe-${name}`, progress: false }));
    return { output: txt('bridge completed') };
  } });
  const f = await fixture([defineExtension({ name: 'nested', tools: [value, bad, modelOnly, plain, bridge] })]);
  try {
    await f.root.configure({ modelTools: [bridge] }, ctx);
    const agent = await f.root.agent(ctx);
    assert.deepEqual(agent.tools.map((t: any) => t.name), ['bridge']);
    assert(agent.callable.some((t: any) => t.name === 'value'));
    const { toolResults } = await f.run([call('bridge', {})]);
    assert.equal(toolResults.length, 1, 'nested calls do not enter transcript');
    assert.deepEqual(received[0].structuredOutput, { count: 42 });
    assert.equal(received[0].output, undefined);
    assert.equal(received[1].isError, true);
    assert(received[1].diagnostics.some((d: any) => d.code === 'invalid_structured_output'));
    assert.equal(received[2].isError, true);
    assert.equal(received[3].structuredOutput, 'plain text');
    assert.equal(received[4].isError, true);
    reports.push({ test: 'nested-and-callers', received });
  } finally { await f.harness.close(ctx); }
});

test('prepareArguments repairs input, output limits retain tail, terminate ends a run', { timeout: 20000 }, async () => {
  const bounded = defineTool({ name: 'bounded', description: 'Bounded streamed text', parameters: Type.Object({ n: Type.Number() }),
    prepareArguments: (args: any) => ({ n: Number(args.n) }),
    outputLimits: { maxBytes: 24, maxLines: 2, retain: 'tail' },
    execute: async ({ n }, api) => { assert.equal(n, 5); api.output('discarded line\n'); api.output('kept one\nkept two'); return { control: { terminate: true } }; } });
  const f = await fixture([defineExtension({ name: 'bounded', tools: [bounded] })]);
  try {
    f.faux.setResponses([answer([call('bounded', { n: '5' })], { stopReason: 'toolUse' })]);
    const settled = await (await f.root.submit({ type: 'input', content: 'Terminate after tool output.' }, ctx)).wait(ctx);
    assert.equal(settled.status, 'done');
    assert.equal(f.faux.state.callCount, 1);
    const view = await f.root.viewState(ctx);
    try {
      const tool = view.value.entries.find((e: any) => e.kind === 'pi.tool-result');
      assert.match(JSON.stringify(tool), /kept one/);
      assert.match(JSON.stringify(tool), /kept two/);
      assert(!JSON.stringify(tool.model[0].content[0]).includes('discarded line'));
      reports.push({ test: 'argument-repair-output-tail-terminate', settled, tool });
    } finally { view.dispose(); }
  } finally { await f.harness.close(ctx); }
});

test('afterTool redacts both model output and schema value of nested calls', { timeout: 20000 }, async () => {
  let received: any;
  let nestedParent: any;
  const secret = defineTool({ name: 'secret', description: 'Return synthetic secret', parameters: empty, callers: ['tools'],
    structuredOutputSchema: Type.Object({ value: Type.String() }), execute: async () => ({ output: txt('synthetic-secret'), structuredOutput: { value: 'synthetic-secret' } }) });
  const bridge = defineTool({ name: 'redaction_probe', description: 'Call synthetic secret', parameters: empty, execute: async (_, api, context) => {
    received = await api.executeTool('secret', {}, context); return { output: txt(JSON.stringify(received.structuredOutput)) };
  } });
  const f = await fixture([defineExtension({ name: 'redaction', tools: [secret, bridge], hooks: [hook(ToolTask, {
    beforeTool: call => { if (call.name === 'secret') nestedParent = call.parent; },
    afterTool: (call, result) => call.name === 'secret' ? { ...result, output: txt('[REDACTED]'), structuredOutput: { value: '[REDACTED]' } } : undefined,
  })] })]);
  try {
    const result = await f.run([call('redaction_probe', {})]);
    assert(nestedParent.taskId);
    assert.deepEqual(received.structuredOutput, { value: '[REDACTED]' });
    assert(!JSON.stringify(result.toolResults).includes('synthetic-secret'));
    reports.push({ test: 'schema-redaction', received, nestedParent });
  } finally { await f.harness.close(ctx); }
});

test('deferred tool search loads matching tools for the next model request', { timeout: 20000 }, async () => {
  const special = defineTool({ name: 'inventory_lookup', description: 'Look up warehouse inventory stock', deferred: true, parameters: empty, execute: async () => ({ output: txt('stock=7') }) });
  const f = await fixture([defineExtension({ name: 'warehouse', tools: [special] }), createToolSearchExtension()]);
  try {
    assert(!(await f.root.agent(ctx)).tools.some(t => t.name === special.name));
    await f.run([call('tool_search', { query: 'inventory', limit: 1 })], (context: any) => {
      assert.match(JSON.stringify(context.messages.filter((m: any) => m.role === 'system')), /inventory_lookup/);
      return answer('loaded');
    });
    assert((await f.root.agent(ctx)).tools.some(t => t.name === special.name));
    reports.push({ test: 'deferred-tool-search', loaded: (await f.root.agent(ctx)).tools.map(t => t.name) });
  } finally { await f.harness.close(ctx); }
});

test('sections, hook arguments/blocking/redaction, wrappers and registry replacement', { timeout: 20000 }, async () => {
  const observed: any[] = [];
  const echo = (version: string) => defineTool({ name: 'echo', description: 'Echo a value', parameters: Type.Object({ text: Type.String() }), execute: async ({ text }) => ({ output: txt(`${version}:${text}`) }) });
  const first = echo('v1');
  const policy = defineExtension({ name: 'policy', sections: [section('policy-note', () => 'Follow deterministic policy.')],
    wraps: [wrapTool(first, tool => ({ ...tool, execute: async (...args) => { observed.push('wrapper'); return tool.execute(...args); } }))],
    hooks: [hook(ToolTask, {
      beforeTool: call => { observed.push({ parent: call.parent, args: call.arguments }); if (call.arguments.text === 'block') return { block: 'blocked by probe' }; return { arguments: { text: String(call.arguments.text).toUpperCase() } }; },
      afterTool: (_call, result) => ({ ...result, output: result.output?.map((item: any) => item.type === 'text' ? { ...item, text: `${item.text}:redacted` } : item) }),
    })] });
  const f = await fixture([defineExtension({ name: 'echo-extension', tools: [first] }), policy]);
  try {
    const firstRun = await f.run([call('echo', { text: 'hello' }), call('echo', { text: 'block' })]);
    assert.match(JSON.stringify(firstRun.entries), /Follow deterministic policy/);
    assert.match(JSON.stringify(firstRun.toolResults[0]), /v1:HELLO:redacted/);
    assert.equal(firstRun.toolResults[1].model[0].isError, true);
    f.registry.install(defineExtension({ name: 'echo-extension', tools: [echo('v2')] }));
    const next = await f.run([call('echo', { text: 'next' })]);
    assert.match(JSON.stringify(next.toolResults.at(-1)), /v2:NEXT:redacted/);
    f.registry.uninstall(policy);
    const last = await f.run([call('echo', { text: 'last' })]);
    assert.match(JSON.stringify(last.toolResults.at(-1)), /v2:last/);
    assert.equal(observed.filter(x => x === 'wrapper').length, 2);
    reports.push({ test: 'extensions-hooks-wrappers-reload', observed });
  } finally { await f.harness.close(ctx); }
});

test('parallel settings overlap calls; sequential settings and override preserve ordering', { timeout: 20000 }, async () => {
  for (const [setting, override, expected] of [['parallel', undefined, 2], ['sequential', undefined, 1], ['parallel', 'sequential', 1]] as const) {
    let active = 0, peak = 0;
    const events: string[] = [];
    const delay = defineTool({ name: 'delay', description: 'Short local delay', parameters: Type.Object({ id: Type.Number() }), executionMode: override,
      execute: async ({ id }) => { events.push(`start-${id}`); active++; peak = Math.max(peak, active); await pause(80); active--; events.push(`end-${id}`); return { output: txt(`done ${id}`) }; } });
    const f = await fixture([defineExtension({ name: 'concurrency', tools: [delay] })], { settings: { toolExecution: setting } });
    try { await f.run([call('delay', { id: 1 }), call('delay', { id: 2 })]); assert.equal(peak, expected); reports.push({ test: 'concurrency', setting, override, peak, events }); }
    finally { await f.harness.close(ctx); }
  }
});

test('coding tools use NodeExecutionEnv for write, edit, read, bash and PowerShell', { timeout: 30000 }, async () => {
  const env = new NodeExecutionEnv({ cwd: outputRoot });
  const received: any[] = [];
  const bridge = defineTool({ name: 'coding_probe', description: 'Deterministic file and shell probe', parameters: empty,
    execute: async (_args, api, context) => {
      for (const [name, args] of [
        ['write', { path: 'probe.txt', content: 'alpha\nbeta\ngamma\n' }],
        ['edit', { path: 'probe.txt', edits: [{ oldText: 'beta', newText: 'BETA' }] }],
        ['read', { path: 'probe.txt', offset: 2, limit: 1 }],
        ['edit', { path: 'probe.txt', edits: [{ oldText: 'missing', newText: 'bad' }] }],
        ['bash', { command: 'printf "bash-ok\\n"', timeout: 5 }],
        ['powershell', { command: "[Console]::WriteLine('powershell-ok')", timeout: 5 }],
        ['powershell', { command: "[Console]::WriteLine('intentional exit'); exit 7", timeout: 5 }],
        ['powershell', { command: "[Console]::WriteLine('Unicode fixture: caf\u00e9 \u2713')", timeout: 5 }],
      ] as const) received.push({ name, result: await api.executeTool(name, args, context) });
      return { output: txt('coding completed') };
    } });
  const f = await fixture([createCodingTools(), defineExtension({ name: 'windows-and-probe', tools: [createPowerShellTool(), bridge] })], { env: () => env });
  try {
    await f.run([call('coding_probe', {})]);
    assert.equal(await readFile(join(outputRoot, 'probe.txt'), 'utf8'), 'alpha\nBETA\ngamma\n');
    assert.equal(received[0].result.isError, false);
    assert.equal(received[1].result.isError, false);
    assert.match(JSON.stringify(received[2]), /BETA/);
    assert.equal(received[3].result.isError, true);
    assert.equal(received[4].result.isError, false);
    assert.match(JSON.stringify(received[4]), /bash-ok/);
    assert.equal(received[5].result.isError, false);
    assert.equal(received[6].result.isError, true);
    assert.equal(received[6].result.structuredOutput.exitCode, 7);
    assert.equal(received[7].result.isError, false);
    assert.match(received[7].result.structuredOutput.output, /Unicode fixture: caf\u00e9 \u2713/);
    assert.equal(typeof (env as any).listFiles, 'undefined');
    const chunks: any[] = [];
    const exec = await env.exec([process.execPath, '-e', "process.stdout.write('argv-ok');process.stderr.write('stderr-ok')"], { onOutput: (text, _context, info) => chunks.push({ text, stream: info.stream }) }, ctx);
    assert.equal(exec.ok, true);
    assert(chunks.some(c => c.stream === 'stdout' && c.text.includes('argv-ok')));
    assert(chunks.some(c => c.stream === 'stderr' && c.text.includes('stderr-ok')));
    reports.push({ test: 'coding-and-shells', received, argvExec: exec, chunks });
  } finally { await f.harness.close(ctx); await env.cleanup(ctx); }
});

test('QuickJS code mode calls nested tools, stores values, introspects and rejects runtime failures', { timeout: 30000 }, async () => {
  const sandbox = new CodemodeSandbox({ memoryLimitBytes: 32 * 1024 * 1024 });
  const adder = defineTool({ name: 'add', description: 'Add two numbers', parameters: Type.Object({ a: Type.Number(), b: Type.Number() }), structuredOutputSchema: Type.Object({ sum: Type.Number() }),
    execute: async ({ a, b }) => ({ output: txt('sum hidden from model'), structuredOutput: { sum: a + b } }) });
  const f = await fixture([defineExtension({ name: 'math', tools: [adder] }), createCodemodeExtension({ sandbox, models: false })]);
  try {
    const first = await f.run([call('codemode', { code: "const values = await Promise.all([tools.add({a:2,b:3}),tools.add({a:5,b:8})]); store('total', values.reduce((n,v)=>n+v.sum,0)); text(values); text(describeTool('add'));" })]);
    assert.equal(first.toolResults[0].model[0].isError, false);
    assert.match(JSON.stringify(first.toolResults[0]), /sum/);
    const second = await f.run([call('codemode', { code: "text(load('total')); text(typeof process); text(searchTools('add'));" })]);
    assert.match(JSON.stringify(second.toolResults.at(-1)), /18/);
    assert.match(JSON.stringify(second.toolResults.at(-1)), /undefined/);
    const failed = await f.run([call('codemode', { code: "await tools.add({a:1,b:1}); throw new Error('intentional script failure');" })]);
    assert.equal(failed.toolResults.at(-1).model[0].isError, true);
    assert.match(JSON.stringify(failed.toolResults.at(-1)), /intentional script failure/);
    reports.push({ test: 'codemode', first: first.toolResults, second: second.toolResults.at(-1), failed: failed.toolResults.at(-1) });
  } finally { await f.harness.close(ctx); await sandbox.close(); }
});

test('code mode model catalog and wrong-type classifier/image calls stay local', { timeout: 30000 }, async () => {
  const sandbox = new CodemodeSandbox({ memoryLimitBytes: 32 * 1024 * 1024 });
  const f = await fixture([createCodemodeExtension({ sandbox })]);
  try {
    const provider = JSON.stringify(f.faux.getModel().provider);
    const result = await f.run([call('codemode', { code: `
      const modelsHere = await models.getModelsOfType('chat', ${provider});
      const available = await models.getAvailableOfType('chat', ${provider});
      const chat = await models.getModelOfType('chat', ${provider}, 'probe');
      text({catalog: modelsHere.length, available: available.length, id: chat.id});
      text(ALL_TOOLS.filter(t => t.name.startsWith('pi.codemode.')).length);
      for (const fn of ['classify', 'generateImages']) {
        try { await models[fn](chat, {}); } catch(error) { text(String(error)); }
      }
    ` })]);
    const tool = result.toolResults[0];
    assert.equal(tool.model[0].isError, false);
    assert.match(JSON.stringify(tool), /catalog/);
    assert.match(JSON.stringify(tool), /classifier model/);
    assert.match(JSON.stringify(tool), /image model/);
    reports.push({ test: 'codemode-model-catalog', tool, limitation: 'Real classifier and image providers were not invoked; wrong model types fail locally.' });
  } finally { await f.harness.close(ctx); await sandbox.close(); }
});

test('NodeExecutionEnv binary reads, directory pages, file errors and default watcher', { timeout: 20000 }, async () => {
  const env = new NodeExecutionEnv({ cwd: outputRoot });
  await writeFile(join(outputRoot, 'watch.txt'), 'first\nsecond\n');
  const changes: any[] = [];
  const watcher = getOrThrow(await env.watch([{ path: 'watch.txt' }], change => changes.push(change), ctx));
  try {
    const binary = getOrThrow(await env.openBinaryReader('watch.txt', undefined, ctx));
    try {
      assert.equal(new TextDecoder().decode(getOrThrow(await binary.read(6, 6, ctx))), 'second');
      const scan = getOrThrow(await binary.scanLines({ startLine: 1, endLine: 2 }, ctx));
      assert.equal(scan.newlines, 2);
      assert.equal(scan.selectedBytes, 6);
    } finally { await binary.close(ctx); }
    const dir = getOrThrow(await env.openDirReader('.', ctx));
    try { assert.equal(getOrThrow(await dir.next(1, ctx)).entries.length, 1); } finally { await dir.close(ctx); }
    const missing = await env.readTextFile('does-not-exist.txt', ctx);
    assert.equal(missing.ok, false);
    if (!missing.ok) assert.equal(missing.error.code, 'not_found');
    await writeFile(join(outputRoot, 'watch.txt'), 'changed\n');
    for (let i = 0; changes.length === 0 && i < 100; i++) await pause(50);
    assert(changes.length > 0);
    reports.push({ test: 'node-environment', watcherMode: watcher.mode, changes, missing: missing.ok ? undefined : missing.error.code });
  } finally { await watcher.close(ctx); await env.cleanup(ctx); }
});

function pngFixture(): Buffer {
  const crc32 = (bytes: Buffer) => {
    let crc = 0xffffffff;
    for (const byte of bytes) { crc ^= byte; for (let i = 0; i < 8; i++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0); }
    return (crc ^ 0xffffffff) >>> 0;
  };
  const chunk = (name: string, data: Buffer) => {
    const type = Buffer.from(name); const header = Buffer.alloc(4); header.writeUInt32BE(data.length);
    const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([type, data])));
    return Buffer.concat([header, type, data, crc]);
  };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(1, 0); ihdr.writeUInt32BE(1, 4); ihdr[8] = 8; ihdr[9] = 6;
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(Buffer.from([0,255,0,0,255]))), chunk('IEND', Buffer.alloc(0))]);
}
const PNG = pngFixture().toString('base64');
test('image passthrough works without Photon and rejects dimensions beyond limits', { timeout: 20000 }, async () => {
  const png = Buffer.from(PNG, 'base64');
  await writeFile(join(outputRoot, 'pixel.png'), png);
  // Header-only bound check occurs before a decoder is needed. The oversized fixture is not sent to a provider.
  const oversized = Buffer.from(png); oversized.writeUInt32BE(3000, 16);
  await writeFile(join(outputRoot, 'oversized.png'), oversized);
  const env = new NodeExecutionEnv({ cwd: outputRoot });
  const f = await fixture([createCodingTools()], { env: () => env });
  try {
    const result = await f.run([call('read', { path: 'pixel.png' }), call('read', { path: 'oversized.png' })]);
    const image = result.toolResults[0].model[0];
    assert.equal(image.isError, false);
    assert(image.content.some((item: any) => item.type === 'image'));
    assert.equal(result.toolResults[1].model[0].isError, true);
    assert(result.toolResults[1].data.diagnostics.some((d: any) => d.code === 'unsupported_image'));
    reports.push({ test: 'image-passthrough', imageBlocks: image.content.filter((item: any) => item.type === 'image').length, oversizedDiagnostics: result.toolResults[1].data.diagnostics });
  } finally { await f.harness.close(ctx); await env.cleanup(ctx); }
});

test('Photon image processing and coding read image blocks', { timeout: 20000 }, async (t) => {
  // A complete 1x1 RGBA PNG; Photon decodes the image instead of trusting its header.
  const png = Buffer.from(PNG, 'base64');
  let images;
  try {
    const { createNodePhotonImages } = await import('@earendil-works/pi-durable/images/node');
    images = await createNodePhotonImages({ worker: false });
  } catch (error) {
    if (!(error instanceof SyntaxError && error.message.includes('@silvia-odwyer/photon/photon_rs.js') && error.message.includes("does not provide an export named 'PhotonImage'"))) throw error;
    reports.push({ test: 'photon-and-read-images', status: 'blocked-integration', error: String(error), stack: error instanceof Error ? error.stack : undefined });
    t.skip(`Installed Photon export prevents loading image processor: ${error}`);
    return;
  }
  const prepared = await images.prepare(png, 'image/png', { maxWidth: 10, maxHeight: 10, maxBytes: 10000 });
  assert(prepared);
  assert.match(prepared.mimeType, /^image\//);
  await writeFile(join(outputRoot, 'pixel.png'), png);
  const env = new NodeExecutionEnv({ cwd: outputRoot });
  const f = await fixture([createCodingTools({ images })], { env: () => env });
  try {
    const result = await f.run([call('read', { path: 'pixel.png' })]);
    const message = result.toolResults[0].model[0];
    assert.equal(message.isError, false);
    assert(message.content.some((item: any) => item.type === 'image'));
    reports.push({ test: 'photon-and-read-images', mimeType: prepared.mimeType, imageBlocks: message.content.filter((item: any) => item.type === 'image').length });
  } finally { await f.harness.close(ctx); await env.cleanup(ctx); }
});

test('portable Photon processor works when the dependency is bundled as ESM', { timeout: 30000 }, async () => {
  const require = createRequire(import.meta.url);
  const { build } = await import('esbuild');
  const bundlePath = join(outputRoot, 'photon-portable.mjs');
  await build({ entryPoints: [require.resolve('@earendil-works/pi-durable/images')], outfile: bundlePath, bundle: true, format: 'esm', platform: 'node', logLevel: 'silent' });
  const { createPhotonImages } = await import(pathToFileURL(bundlePath).href);
  const wasm = await readFile(require.resolve('@silvia-odwyer/photon/photon_rs_bg.wasm'));
  const images = createPhotonImages(wasm);
  const prepared = await images.prepare(Buffer.from(PNG, 'base64'), 'image/png', { maxWidth: 10, maxHeight: 10, maxBytes: 10000 });
  assert(prepared);
  await writeFile(join(outputRoot, 'pixel.png'), Buffer.from(PNG, 'base64'));
  const env = new NodeExecutionEnv({ cwd: outputRoot });
  const f = await fixture([createCodingTools({ images })], { env: () => env });
  try {
    const result = await f.run([call('read', { path: 'pixel.png' })]);
    assert.equal(result.toolResults[0].model[0].isError, false);
    assert(result.toolResults[0].model[0].content.some((item: any) => item.type === 'image'));
    reports.push({ test: 'photon-bundled-esm-workaround', status: 'passed', mimeType: prepared.mimeType, wasmBytes: wasm.length });
  } finally { await f.harness.close(ctx); await env.cleanup(ctx); }
});

test.after(async () => { await writeFile(join(outputRoot, 'probe-results.json'), JSON.stringify({ version: '1.3.0', node: process.version, platform: process.platform, reports }, null, 2)); });
