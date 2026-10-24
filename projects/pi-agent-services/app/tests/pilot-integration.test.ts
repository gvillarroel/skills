// Run from this project: node --import tsx --test tests/pilot-integration.test.ts
// All model work is explicitly faux; no watcher command or notification reaches the host.
import test, { type TestContext } from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm } from 'node:fs/promises';
import { join, resolve, sep } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { AgentService } from '../src/server.js';
import { Catalog } from '../src/catalog.js';
import type { ServiceConfig } from '../src/config.js';
import type { LocalEvent } from '../src/local-events.js';
import type { Watchers } from '../src/watchers.js';

async function fixture(t: TestContext): Promise<ServiceConfig> {
  const cache = resolve('.cache', 'pilot-integration');
  await mkdir(cache, { recursive: true });
  const directory = await mkdtemp(join(cache, 'case-'));
  t.after(async () => {
    assert.ok(resolve(directory).startsWith(cache + sep));
    await rm(directory, { recursive: true, force: true });
  });
  return {
    version: 1, host: '127.0.0.1', port: 0, dataDir: directory,
    provider: { kind: 'faux' }, github: { mode: 'off', intervalMs: 1000, initialScan: 'baseline' },
    agents: [
      { id: 'repo-quality', name: 'Repository Quality', instructions: 'Summarize observed validator outcomes only.', repositories: [] },
      { id: 'delivery-watch', name: 'Delivery Watch', instructions: 'Summarize observed delivery status only.', repositories: ['owner/repo'] },
    ],
  };
}

function event(agentId: 'repo-quality' | 'delivery-watch', version = 'one', createdAt = new Date().toISOString()): LocalEvent {
  return {
    id: `local:${agentId}:${version}`, agentId,
    type: agentId === 'repo-quality' ? 'workspace.changed' : 'delivery.changed', createdAt,
    snapshot: { kind: 'integration-fixture', fingerprint: version, observedResult: 'Passing synthetic observation; no real repository work was performed.' },
  };
}

async function until(check: () => unknown | Promise<unknown>, timeoutMs = 10_000) {
  const deadline = Date.now() + timeoutMs;
  while (!await check()) {
    if (Date.now() >= deadline) throw new Error('Timed out waiting for the asserted pilot state.');
    await delay(10);
  }
}

async function client(service: AgentService) {
  const token = (await readFile(join(service.config.dataDir, 'console-token'), 'utf8')).trim();
  return async (path: string, body?: unknown) => {
    const response = await fetch(service.url + path, {
      method: body === undefined ? 'GET' : 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    return { status: response.status, value: await response.json() as any };
  };
}

test('two targeted local events create independent durable jobs; duplicate admission stays idle', { timeout: 20_000 }, async t => {
  const config = await fixture(t);
  const service = await AgentService.open(config);
  try {
    await delay(30);
    assert.deepEqual(service.stats(), { 'repo-quality': { providerCalls: 0 }, 'delivery-watch': { providerCalls: 0 } });
    const qualityIds = service.admit(event('repo-quality'));
    const deliveryIds = service.admit(event('delivery-watch'));
    assert.equal(qualityIds.length, 1);
    assert.equal(deliveryIds.length, 1);
    assert.deepEqual(service.admit(event('repo-quality')), []);
    assert.deepEqual(service.admit(event('delivery-watch')), []);
    await until(() => config.agents.every(agent => service.catalog.jobs(agent.id)[0]?.status === 'done'));
    for (const agent of config.agents) {
      const jobs = service.catalog.jobs(agent.id);
      assert.equal(jobs.length, 1);
      assert.equal((jobs[0].event as LocalEvent).agentId, agent.id);
      assert.ok(jobs[0].conversationId);
      assert.match(jobs[0].result ?? '', /OFFLINE DEMO/u);
      assert.equal(service.stats()[agent.id].providerCalls, 1);
      assert.ok((await readFile(join(config.dataDir, 'agents', agent.id, 'harness.sqlite'))).length > 0);
    }
    await delay(50);
    assert.deepEqual(service.stats(), { 'repo-quality': { providerCalls: 1 }, 'delivery-watch': { providerCalls: 1 } });
  } finally { await service.close(); }
});

test('reopen reconnects the same job conversations and does not generate while reading status, evidence, or chat', { timeout: 20_000 }, async t => {
  const config = await fixture(t);
  let service = await AgentService.open(config);
  const ids = config.agents.flatMap(agent => service.admit(event(agent.id as 'repo-quality' | 'delivery-watch')));
  await until(() => config.agents.every(agent => service.catalog.jobs(agent.id)[0]?.status === 'done'));
  const prior = config.agents.map(agent => service.catalog.jobs(agent.id)[0]);
  await service.close();
  service = await AgentService.open(config);
  try {
    const call = await client(service);
    for (const job of prior) {
      const thread = await call(`/v1/agents/${job.agentId}/chat?jobId=${encodeURIComponent(job.id)}`);
      assert.equal(thread.value.conversation.id, job.conversationId);
      const evidence = await call(`/v1/agents/${job.agentId}/evidence`);
      assert.ok(evidence.value.records.some((record: any) => record.kind === 'model.response'));
      assert.deepEqual(service.admit(job.event), []);
    }
    assert.equal((await call('/v1/status')).status, 200);
    assert.equal(ids.length, 2);
    await delay(100);
    assert.deepEqual(service.stats(), { 'repo-quality': { providerCalls: 0 }, 'delivery-watch': { providerCalls: 0 } });
  } finally { await service.close(); }
});

test('status and shutdown require local auth; authenticated shutdown closes the owner', { timeout: 20_000 }, async t => {
  const config = await fixture(t);
  const service = await AgentService.open(config);
  try {
    assert.equal((await fetch(service.url + '/health')).status, 200);
    assert.equal((await fetch(service.url + '/v1/status')).status, 401);
    assert.equal((await fetch(service.url + '/v1/shutdown', { method: 'POST' })).status, 401);
    assert.equal((await fetch(service.url + '/health')).status, 200);
    const call = await client(service);
    const status = await call('/v1/status');
    assert.equal(status.status, 200);
    assert.equal(status.value.provider, 'faux');
    assert.deepEqual(status.value.notifications, []);
    assert.doesNotMatch(JSON.stringify(status.value), /console-token|Bearer|credential|auth\.json/u);
    assert.equal((await call('/v1/shutdown', {})).status, 200);
    await until(() => { try { service.catalog.agents(); return false; } catch { return true; } });
    const again = await Catalog.open(config.dataDir, config.agents);
    again.close();
  } finally { await service.close(); }
});

test('local watcher daily cap persists across restart and prevents a second capture or model job', { timeout: 20_000 }, async t => {
  const config = await fixture(t);
  const attach = (service: AgentService, captures: string[]) => {
    // Attach after open to isolate cap mechanics from OS commands and timers.
    config.pilot = { repositoryRoot: resolve('.'), repository: 'owner/repo', intervalMs: 10_000, stabilityMs: 30_000,
      minJobIntervalMs: 0, maxJobsPerAgentPerDay: 1, desktopNotifications: false };
    (service as unknown as { watchers: Pick<Watchers, 'tick' | 'ack' | 'close'> }).watchers = {
      async tick(agentId) { captures.push(agentId); return event(agentId, `capture-${captures.length}`); },
      async ack() {},
      close() {},
    };
  };
  let service = await AgentService.open(config);
  try {
    await delay(30);
    const captures: string[] = [];
    attach(service, captures);
    await until(async () => {
      await service.pollPilot();
      return config.agents.every(agent => service.catalog.jobs(agent.id)[0]?.status === 'done');
    });
    await delay(30);
    assert.equal(captures.length, 2);
    await service.pollPilot();
    assert.equal(captures.length, 2);
    assert.equal(service.catalog.admittedToday('repo-quality'), 1);
    assert.equal(service.catalog.admittedToday('delivery-watch'), 1);
    await service.close();
    delete config.pilot;
    service = await AgentService.open(config);
    await delay(30);
    const restartedCaptures: string[] = [];
    attach(service, restartedCaptures);
    await service.pollPilot();
    assert.deepEqual(restartedCaptures, []);
    assert.deepEqual(service.stats(), { 'repo-quality': { providerCalls: 0 }, 'delivery-watch': { providerCalls: 0 } });
  } finally { await service.close(); }
});

test('an old pending event counts against the day it is actually admitted', async t => {
  const config = await fixture(t);
  const priorDay = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  let catalog = await Catalog.open(config.dataDir, config.agents);
  const oldEvent = event('repo-quality', 'prior-day-pending', priorDay);
  try {
    assert.equal(catalog.admit([oldEvent], config.agents).length, 1);
    assert.equal(catalog.admittedToday('repo-quality'), 1);
    assert.equal(catalog.admittedToday('delivery-watch'), 0);
    assert.deepEqual(catalog.admit([oldEvent], config.agents), []);
    assert.equal(catalog.admittedToday('repo-quality'), 1);
    catalog.close();
    catalog = await Catalog.open(config.dataDir, config.agents);
    assert.equal(catalog.admittedToday('repo-quality'), 1);
  } finally { catalog.close(); }
});

test('shutdown interrupts active generation and reopening recovers the admitted thread', { timeout: 20_000 }, async t => {
  const config = await fixture(t);
  config.provider.delayMs = 2000;
  let service = await AgentService.open(config);
  try {
    const id = service.admit(event('repo-quality', 'interrupted'))[0];
    await until(() => service.catalog.job('repo-quality', id)?.submissionId);
    const admitted = service.catalog.job('repo-quality', id)!;
    const started = Date.now();
    await service.close();
    assert.ok(Date.now() - started < 3000);
    config.provider.delayMs = 0;
    service = await AgentService.open(config);
    await until(() => service.catalog.job('repo-quality', id)?.status === 'done');
    const recovered = service.catalog.job('repo-quality', id)!;
    assert.equal(recovered.conversationId, admitted.conversationId);
    assert.equal(recovered.submissionId, admitted.submissionId);
    assert.equal(service.catalog.jobs('repo-quality').length, 1);
  } finally { await service.close(); }
});
