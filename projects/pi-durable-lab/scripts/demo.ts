// Run: npm run demo -- <request-id>
// Uses the official offline provider. No credentials or model service are used.
import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { BACKGROUND_CONTEXT as context } from '@earendil-works/chord/context';
import { createModels, fauxProvider, fauxAssistantMessage, fauxToolCall, Type } from '@earendil-works/pi-ai';
import { Harness, AssistantEntry, createRegistry, defineExtension, defineTool } from '@earendil-works/pi-durable';
import { openNodeSqliteStorage } from '@earendil-works/pi-durable/storage/sqlite/node';

await mkdir('artifacts/demo', { recursive: true });
const count = defineTool({
  name: 'count', description: 'Count the supplied items',
  parameters: Type.Object({ items: Type.Array(Type.String()) }), replay: 'safe',
  execute: async ({ items }) => ({ output: [{ type: 'text', text: String(items.length) }] }),
});
const App = defineExtension({ name: 'demo', tools: [count] });
const registry = createRegistry(); registry.install(App);
const faux = fauxProvider({ tokensPerSecond: Infinity });
const models = createModels(); models.setProvider(faux.provider);
faux.setResponses([
  fauxAssistantMessage(fauxToolCall('count', { items: ['alpha', 'beta', 'gamma'] }), { stopReason: 'toolUse' }),
  fauxAssistantMessage('There are 3 items.'),
]);
const model = faux.getModel();
const harness = await Harness.open(await openNodeSqliteStorage(resolve('artifacts/demo/session.sqlite')), { models, registry }, context);
try {
  const root = await harness.root(context, { agent: { model: { provider: model.provider, modelId: model.id }, extensions: [App], tools: [count] } });
  const submission = await root.submit({ type: 'input', content: 'Count alpha, beta and gamma.', requestId: process.argv[2] ?? 'starter-1' }, context);
  const result = await submission.wait(context);
  if (result.status !== 'done' || result.type !== 'input') throw new Error(JSON.stringify(result));
  const answer = await root.commit(tx => tx.entry(AssistantEntry, result.answer), context);
  console.log(JSON.stringify({ submissionId: submission.id, answer: answer?.model, providerCallsThisProcess: faux.state.callCount }, null, 2));
} finally { await harness.close(context); }
