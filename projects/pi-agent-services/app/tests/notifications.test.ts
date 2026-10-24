// Run with npm test. These notification probes are offline and inject every sender.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp } from 'node:fs/promises';
import { resolve } from 'node:path';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { NotificationOutbox, NotificationDeliveryError, createNotificationSender } from '../src/notifications.js';

await mkdir('../artifacts/notifications', { recursive: true });
const directory = () => mkdtemp(resolve('../artifacts/notifications/case-'));
const event = { agentId: 'skill-validator', jobId: 'private job path and source data', type: 'job.completed' as const };

test('outbox persists and deduplicates agent/job/type/channel while emitting only fixed metadata', async () => {
  const root = await directory(); let sent = 0;
  let outbox = await NotificationOutbox.open(root, { channels: ['desktop', 'telegram'], sender: async notification => {
    sent++; assert.doesNotMatch(notification.message, /private job|source data/); return { providerMessageId: `fixture:${sent}` };
  } });
  const first = outbox.enqueue(event); assert.equal(first.length, 2);
  assert.deepEqual(outbox.enqueue(event).map(item => item.id), first.map(item => item.id));
  assert.equal(outbox.list().length, 2);
  const delivered = await outbox.flush(); assert.equal(sent, 2);
  assert.ok(delivered.every(item => item.status === 'provider_accepted' && item.attempts === 1));
  outbox.close();
  outbox = await NotificationOutbox.open(root, { sender: async () => { throw new Error('must not resend accepted notifications'); } });
  try { assert.equal((await outbox.flush()).length, 0); assert.equal(outbox.enqueue(event)[0].status, 'provider_accepted'); }
  finally { outbox.close(); }
});

test('transient delivery retries with bounded exponential backoff and a terminal attempt cap', async () => {
  let time = 1000; let sent = 0;
  const outbox = await NotificationOutbox.open(await directory(), { now: () => time, retryBaseMs: 100, maxAttempts: 3,
    sender: async () => { sent++; throw new Error('secret-token in an untrusted provider failure'); } });
  try {
    outbox.enqueue(event);
    const first = (await outbox.flush())[0]; assert.equal(first.status, 'queued'); assert.equal(first.nextAttemptAt, 1100);
    assert.equal((await outbox.flush()).length, 0); assert.equal(sent, 1);
    time = 1100; const second = (await outbox.flush())[0]; assert.equal(second.nextAttemptAt, 1300);
    time = 1300; const third = (await outbox.flush())[0]; assert.equal(third.status, 'failed'); assert.equal(sent, 3);
    time = 1_000_000; assert.equal((await outbox.flush()).length, 0);
    assert.doesNotMatch(JSON.stringify(outbox.list()), /secret-token|untrusted provider/);
  } finally { outbox.close(); }
});

test('permanent rejection stops immediately and concurrent flush calls do not duplicate a send', async () => {
  let release!: () => void; let sent = 0;
  const waiting = new Promise<void>(resolve => { release = resolve; });
  const outbox = await NotificationOutbox.open(await directory(), { sender: async () => {
    sent++; await waiting; throw new NotificationDeliveryError('configuration_missing', false);
  } });
  try {
    outbox.enqueue(event); const active = outbox.flush();
    assert.equal(outbox.list()[0].status, 'attempted'); assert.equal((await outbox.flush()).length, 0);
    assert.throws(() => outbox.close(), /Wait for/); release();
    assert.equal((await active)[0].status, 'failed'); assert.equal(sent, 1);
    assert.equal((await outbox.flush()).length, 0);
  } finally { release(); outbox.close(); }
});

test('Telegram is disabled without explicit channel opt-in and never calls fetch', async () => {
  const sender = createNotificationSender({ PI_NOTIFY_TELEGRAM_TOKEN: '123456:fixtureTokenThatMustNotBeUsed', PI_NOTIFY_TELEGRAM_CHAT_ID: '123456' });
  const outbox = await NotificationOutbox.open(await directory(), { channels: ['telegram'], sender });
  try {
    outbox.enqueue(event); const result = (await outbox.flush())[0];
    assert.equal(result.status, 'failed'); assert.equal(result.errorCode, 'telegram_not_enabled');
  } finally { outbox.close(); }
});

test('notification validation rejects arbitrary text fields, invalid types and invalid limits', async () => {
  const outbox = await NotificationOutbox.open(await directory(), { sender: async () => ({}) });
  try {
    assert.throws(() => outbox.enqueue({ ...event, agentId: 'private raw logs\n' }), /slug/);
    assert.throws(() => outbox.enqueue({ ...event, type: 'constructor' as any }), /type/);
    assert.throws(() => outbox.list(1001), /limit/);
    await assert.rejects(outbox.flush({ limit: 21 }), /limit/);
  } finally { outbox.close(); }
});

test('expired attempt leases recover after restart without exceeding the retry budget', async () => {
  const root = await directory(); let sent = 0;
  let outbox = await NotificationOutbox.open(root, { now: () => 1000, maxAttempts: 2, sender: async () => ({}) });
  const queued = outbox.enqueue(event)[0]; outbox.close();
  const raw = new DatabaseSync(join(root, 'notifications.sqlite'));
  raw.prepare("UPDATE notifications SET status='attempted',attempts=1,leaseUntil=2000 WHERE id=?").run(queued.id); raw.close();
  let time = 1999;
  outbox = await NotificationOutbox.open(root, { now: () => time, maxAttempts: 2, sender: async () => { sent++; return {}; } });
  try {
    assert.equal((await outbox.flush()).length, 0); time = 2000;
    assert.equal((await outbox.flush())[0].status, 'provider_accepted'); assert.equal(sent, 1);
  } finally { outbox.close(); }
  const finalAttempt = new DatabaseSync(join(root, 'notifications.sqlite'));
  finalAttempt.prepare("UPDATE notifications SET status='attempted',leaseUntil=2001 WHERE id=?").run(queued.id); finalAttempt.close();
  outbox = await NotificationOutbox.open(root, { now: () => 2001, maxAttempts: 2, sender: async () => { sent++; return {}; } });
  try { assert.equal((await outbox.flush()).length, 0); assert.equal(outbox.list()[0].status, 'failed'); assert.equal(sent, 1); }
  finally { outbox.close(); }
});
