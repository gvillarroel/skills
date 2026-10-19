// Run with: node --import tsx scripts/recovery-fixture.ts <directory> <safe|unsafe|checkpoint>
// This is a deliberately interrupted offline fixture, never a production worker.
import { appendFile } from 'node:fs/promises';
import { join } from 'node:path';
import { BACKGROUND_CONTEXT as context } from '@earendil-works/chord/context';
import { createModels, fauxProvider, fauxAssistantMessage, fauxToolCall, Type } from '@earendil-works/pi-ai';
import { Harness, createRegistry, defineExtension, defineTask, defineTool } from '@earendil-works/pi-durable';
import { openNodeSqliteStorage } from '@earendil-works/pi-durable/storage/sqlite/node';

export function recoveryRegistry(directory: string, mode: string, crashing: boolean) {
  const effects = join(directory, 'effects.txt');
  const tool = defineTool({
    name: 'effect', description: 'Offline replay probe', parameters: Type.Object({}),
    ...(mode === 'safe' ? { replay: 'safe' as const } : {}),
    execute: async (_args, api, ctx) => {
      await appendFile(effects, 'tool-effect\n');
      await api.details({ reached: 'external-effect' }, ctx);
      if (crashing) { process.stdout.write('READY\n'); await new Promise(() => {}); }
      return { output: [{ type: 'text' as const, text: 'recovered' }] };
    },
  });
  const checkpoint = defineTask<null, { phase: 'first' } | { phase: 'second' }, string>({
    name: 'lab.checkpoint', version: 1, initial: () => ({ phase: 'first' }),
    phases: {
      first: async (_task, runtime, ctx) => {
        await appendFile(effects, 'first-phase\n');
        await runtime.commit(() => ({ status: 'running', checkpoint: { phase: 'second' } }), ctx);
      },
      second: async (_task, runtime, ctx) => {
        if (crashing) { process.stdout.write('READY\n'); await new Promise(() => {}); }
        await runtime.commit(() => ({ status: 'terminal', outcome: { status: 'completed', result: 'checkpoint-resumed' } }), ctx);
      },
    },
    abort: async (_task, runtime, ctx) => {
      await runtime.commit(() => ({ status: 'terminal', outcome: { status: 'aborted' } }), ctx);
    },
  });
  const registry = createRegistry();
  registry.install(defineExtension({ name: 'recovery', tools: [tool], tasks: [checkpoint] }));
  return { registry, checkpoint };
}

export function offlineModels() {
  const faux = fauxProvider({ tokensPerSecond: Infinity });
  const models = createModels();
  models.setProvider(faux.provider);
  const model = faux.getModel();
  return { faux, models, ref: { provider: model.provider, modelId: model.id } };
}

async function main(directory: string, mode: string) {
  const { models, faux, ref } = offlineModels();
  const { registry, checkpoint } = recoveryRegistry(directory, mode, true);
  const harness = await Harness.open(await openNodeSqliteStorage(join(directory, 'session.sqlite')), { models, registry }, context);
  const root = await harness.root(context, { agent: { model: ref } });
  if (mode === 'checkpoint') {
    const id = await root.commit(tx => tx.createTask(checkpoint, null, { ownership: { kind: 'conversation' } }), context);
    await appendFile(join(directory, 'task-id.txt'), String(id));
    await harness.waitForTask(id, context);
  } else {
    faux.setResponses([fauxAssistantMessage(fauxToolCall('effect', {}), { stopReason: 'toolUse' }), fauxAssistantMessage('done')]);
    await (await root.submit({ type: 'input', content: 'Run the replay probe', requestId: 'recovery-input' }, context)).wait(context);
  }
  await harness.close(context);
}

if (process.argv[1]?.replaceAll('\\', '/').endsWith('/recovery-fixture.ts')) {
  main(process.argv[2], process.argv[3]).catch(error => { console.error(error); process.exitCode = 1; });
}
