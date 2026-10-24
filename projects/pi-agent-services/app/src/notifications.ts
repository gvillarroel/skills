// Build with npm run build. Notifications contain fixed status text, never source logs.
import { DatabaseSync } from 'node:sqlite';
import { createHash } from 'node:crypto';
import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

export type NotificationType = 'job.started' | 'job.completed' | 'job.failed' | 'attention.required';
export type NotificationChannel = 'desktop' | 'telegram';
export type NotificationStatus = 'queued' | 'attempted' | 'provider_accepted' | 'failed';
export interface NotificationEvent { agentId: string; jobId: string; type: NotificationType }
export interface NotificationRow extends NotificationEvent {
  id: number; channel: NotificationChannel; title: string; message: string;
  status: NotificationStatus; attempts: number; nextAttemptAt: number;
  createdAt: number; updatedAt: number; errorCode?: string; providerMessageId?: string;
}
export interface DeliveryReceipt { providerMessageId?: string }
export type NotificationSender = (notification: Readonly<NotificationRow>) => Promise<DeliveryReceipt>;
export interface NotificationOptions {
  channels?: NotificationChannel[];
  sender?: NotificationSender;
  now?: () => number;
  maxAttempts?: number;
  retryBaseMs?: number;
}

const labels: Record<NotificationType, string> = {
  'job.started': 'Work started', 'job.completed': 'Work completed',
  'job.failed': 'Work failed; local details are available',
  'attention.required': 'Your attention is required; local details are available',
};
const allowedChannels = new Set<NotificationChannel>(['desktop', 'telegram']);
export class NotificationDeliveryError extends Error {
  constructor(readonly code: string, readonly retryable = true) { super(code); }
}

function row(value: Record<string, unknown>): NotificationRow {
  return {
    id: Number(value.id), agentId: String(value.agentId), jobId: String(value.jobId),
    type: value.type as NotificationType, channel: value.channel as NotificationChannel,
    title: String(value.title), message: String(value.message), status: value.status as NotificationStatus,
    attempts: Number(value.attempts), nextAttemptAt: Number(value.nextAttemptAt),
    createdAt: Number(value.createdAt), updatedAt: Number(value.updatedAt),
    ...(value.errorCode ? { errorCode: String(value.errorCode) } : {}),
    ...(value.providerMessageId ? { providerMessageId: String(value.providerMessageId) } : {}),
  };
}

/** A durable, bounded, at-least-once outbox. Provider acceptance is not a read receipt. */
export class NotificationOutbox {
  private flushing = false;
  private readonly channels: NotificationChannel[];
  private readonly now: () => number;
  private readonly sender: NotificationSender;
  private readonly maxAttempts: number;
  private readonly retryBaseMs: number;
  private constructor(private db: DatabaseSync, options: NotificationOptions) {
    this.channels = [...new Set<NotificationChannel>(options.channels ?? ['desktop'])];
    if (!this.channels.length || this.channels.some(channel => !allowedChannels.has(channel))) throw new Error('Invalid notification channels.');
    this.maxAttempts = options.maxAttempts ?? 4;
    this.retryBaseMs = options.retryBaseMs ?? 60_000;
    if (!Number.isInteger(this.maxAttempts) || this.maxAttempts < 1 || this.maxAttempts > 6) throw new Error('Notification attempts must be between 1 and 6.');
    if (!Number.isSafeInteger(this.retryBaseMs) || this.retryBaseMs < 1 || this.retryBaseMs > 900_000) throw new Error('Invalid notification retry interval.');
    this.now = options.now ?? Date.now;
    this.sender = options.sender ?? createNotificationSender();
  }
  static async open(directory: string, options: NotificationOptions = {}): Promise<NotificationOutbox> {
    await mkdir(directory, { recursive: true });
    const db = new DatabaseSync(join(directory, 'notifications.sqlite'));
    try {
      db.exec(`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=3000;
        CREATE TABLE IF NOT EXISTS notifications (
          id INTEGER PRIMARY KEY, agentId TEXT NOT NULL, jobId TEXT NOT NULL, type TEXT NOT NULL,
          channel TEXT NOT NULL, title TEXT NOT NULL, message TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0,
          nextAttemptAt INTEGER NOT NULL, leaseUntil INTEGER NOT NULL DEFAULT 0,
          createdAt INTEGER NOT NULL, updatedAt INTEGER NOT NULL,
          errorCode TEXT, providerMessageId TEXT,
          UNIQUE(agentId, jobId, type, channel)
        );
        CREATE INDEX IF NOT EXISTS notifications_due ON notifications(status, nextAttemptAt);`);
      return new NotificationOutbox(db, options);
    } catch (error) { db.close(); throw error; }
  }
  enqueue(event: NotificationEvent): NotificationRow[] {
    if (!/^[a-z0-9][a-z0-9-]{0,63}$/.test(event.agentId)) throw new Error('Notification agent ID must be a slug.');
    if (typeof event.jobId !== 'string' || !event.jobId.length || event.jobId.length > 2048) throw new Error('Invalid notification job ID.');
    if (!Object.hasOwn(labels, event.type)) throw new Error('Invalid notification type.');
    const reference = createHash('sha256').update(`${event.agentId}\0${event.jobId}`).digest('hex').slice(0, 12);
    const title = `Pi agent: ${event.agentId}`;
    const message = `${labels[event.type]}. Reference ${reference}.`;
    const now = this.now();
    const result: NotificationRow[] = [];
    for (const channel of this.channels) {
      this.db.prepare(`INSERT OR IGNORE INTO notifications
        (agentId,jobId,type,channel,title,message,nextAttemptAt,createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?)`)
        .run(event.agentId, event.jobId, event.type, channel, title, message, now, now, now);
      result.push(row(this.db.prepare('SELECT * FROM notifications WHERE agentId=? AND jobId=? AND type=? AND channel=?')
        .get(event.agentId, event.jobId, event.type, channel)!));
    }
    return result;
  }
  list(limit = 100): NotificationRow[] {
    if (!Number.isInteger(limit) || limit < 1 || limit > 1000) throw new Error('Notification limit must be between 1 and 1000.');
    return this.db.prepare('SELECT * FROM notifications ORDER BY id DESC LIMIT ?').all(limit).map(row);
  }
  private claim(): NotificationRow | undefined {
    const now = this.now();
    this.db.exec('BEGIN IMMEDIATE');
    try {
      // A crash may happen after sending but before committing the receipt. Leases
      // recover the queue; external providers may receive a duplicate in that case.
      this.db.prepare(`UPDATE notifications SET status=CASE WHEN attempts>=? THEN 'failed' ELSE 'queued' END,
        leaseUntil=0,errorCode='interrupted_attempt',updatedAt=? WHERE status='attempted' AND leaseUntil<=?`)
        .run(this.maxAttempts, now, now);
      const next = this.db.prepare("SELECT * FROM notifications WHERE status='queued' AND nextAttemptAt<=? ORDER BY id LIMIT 1").get(now);
      if (!next) { this.db.exec('COMMIT'); return; }
      this.db.prepare("UPDATE notifications SET status='attempted',attempts=attempts+1,leaseUntil=?,updatedAt=? WHERE id=?")
        .run(now + 60_000, now, next.id!);
      const claimed = row(this.db.prepare('SELECT * FROM notifications WHERE id=?').get(next.id!)!);
      this.db.exec('COMMIT'); return claimed;
    } catch (error) { this.db.exec('ROLLBACK'); throw error; }
  }
  async flush(options: { limit?: number } = {}): Promise<NotificationRow[]> {
    const limit = options.limit ?? 4;
    if (!Number.isInteger(limit) || limit < 1 || limit > 20) throw new Error('Notification flush limit must be between 1 and 20.');
    if (this.flushing) return [];
    this.flushing = true;
    const results: NotificationRow[] = [];
    try {
      for (let i = 0; i < limit; i++) {
        const notification = this.claim();
        if (!notification) break;
        try {
          const receipt = await this.sender(Object.freeze(notification));
          const providerMessageId = receipt.providerMessageId;
          if (providerMessageId !== undefined && !/^[a-zA-Z0-9_.:-]{1,200}$/.test(providerMessageId)) throw new NotificationDeliveryError('invalid_provider_receipt', false);
          this.db.prepare("UPDATE notifications SET status='provider_accepted',leaseUntil=0,errorCode=NULL,providerMessageId=?,updatedAt=? WHERE id=? AND status='attempted' AND attempts=?")
            .run(providerMessageId ?? null, this.now(), notification.id, notification.attempts);
        } catch (error) {
          // Never persist raw exceptions: provider errors can contain request URLs or tokens.
          const failure = error instanceof NotificationDeliveryError ? error : new NotificationDeliveryError('delivery_failed');
          const code = /^[a-z_]{1,64}$/.test(failure.code) ? failure.code : 'delivery_failed';
          const retry = failure.retryable && notification.attempts < this.maxAttempts;
          const now = this.now();
          const backoff = Math.min(900_000, this.retryBaseMs * 2 ** (notification.attempts - 1));
          this.db.prepare('UPDATE notifications SET status=?,nextAttemptAt=?,leaseUntil=0,errorCode=?,updatedAt=? WHERE id=? AND status=\'attempted\' AND attempts=?')
            .run(retry ? 'queued' : 'failed', now + backoff, code, now, notification.id, notification.attempts);
        }
        results.push(row(this.db.prepare('SELECT * FROM notifications WHERE id=?').get(notification.id)!));
      }
      return results;
    } finally { this.flushing = false; }
  }
  close(): void {
    if (this.flushing) throw new Error('Wait for the notification flush before closing its outbox.');
    this.db.close();
  }
}

function child(executable: string, args: string[], env?: NodeJS.ProcessEnv): Promise<void> {
  return new Promise((resolve, reject) => {
    const process = spawn(executable, args, { windowsHide: true, shell: false, stdio: 'ignore', env });
    const timer = setTimeout(() => { process.kill(); reject(new NotificationDeliveryError('desktop_timeout')); }, 15_000);
    process.once('error', () => { clearTimeout(timer); reject(new NotificationDeliveryError('desktop_unavailable', false)); });
    process.once('exit', code => { clearTimeout(timer); code === 0 ? resolve() : reject(new NotificationDeliveryError('desktop_rejected')); });
  });
}

export async function sendDesktopNotification(notification: Pick<NotificationRow, 'title' | 'message'>): Promise<DeliveryReceipt> {
  if (process.platform === 'win32') {
    // Message values enter through child environment variables, never PowerShell code.
    const script = [
      '$ErrorActionPreference = "Stop"',
      'Add-Type -AssemblyName System.Windows.Forms',
      'Add-Type -AssemblyName System.Drawing',
      '$notice = New-Object System.Windows.Forms.NotifyIcon',
      '$notice.Icon = [System.Drawing.SystemIcons]::Information',
      '$notice.Visible = $true',
      'try {',
      '  $notice.ShowBalloonTip(10000, $env:PI_NOTICE_TITLE, $env:PI_NOTICE_MESSAGE, [System.Windows.Forms.ToolTipIcon]::Info)',
      '  $until = [DateTime]::UtcNow.AddSeconds(7)',
      '  while ([DateTime]::UtcNow -lt $until) { [System.Windows.Forms.Application]::DoEvents(); Start-Sleep -Milliseconds 50 }',
      '} finally { $notice.Visible = $false; $notice.Dispose() }',
    ].join('\n');
    await child('powershell.exe', ['-NoLogo', '-NoProfile', '-NonInteractive', '-WindowStyle', 'Hidden', '-EncodedCommand', Buffer.from(script, 'utf16le').toString('base64')],
      { ...process.env, PI_NOTICE_TITLE: notification.title, PI_NOTICE_MESSAGE: notification.message });
    return {};
  }
  if (process.platform === 'darwin') {
    // AppleScript reads arguments; strings are never interpolated into its source.
    await child('/usr/bin/osascript', ['-e', 'on run argv\ndisplay notification (item 2 of argv) with title (item 1 of argv)\nend run', notification.title, notification.message]);
    return {};
  }
  throw new NotificationDeliveryError('desktop_unsupported', false);
}

export function createNotificationSender(env: NodeJS.ProcessEnv = process.env): NotificationSender {
  return async notification => {
    if (notification.channel === 'desktop') return sendDesktopNotification(notification);
    if (env.PI_NOTIFY_TELEGRAM_ENABLED !== '1') throw new NotificationDeliveryError('telegram_not_enabled', false);
    const token = env.PI_NOTIFY_TELEGRAM_TOKEN ?? '';
    const chatId = env.PI_NOTIFY_TELEGRAM_CHAT_ID ?? '';
    if (!/^\d{3,20}:[a-zA-Z0-9_-]{20,200}$/.test(token) || !/^-?\d{1,20}$/.test(chatId)) throw new NotificationDeliveryError('telegram_configuration_missing', false);
    let response: Response;
    try {
      response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId, text: `${notification.title}\n${notification.message}`,
          link_preview_options: { is_disabled: true } }),
        signal: AbortSignal.timeout(10_000), redirect: 'error',
      });
    } catch { throw new NotificationDeliveryError('telegram_network_failed'); }
    if (!response.ok) {
      await response.body?.cancel();
      throw new NotificationDeliveryError('telegram_remote_rejected', response.status === 429 || response.status >= 500);
    }
    // A successful API response proves provider acceptance, not phone delivery or reading.
    let payload: any;
    try {
      const reader = response.body?.getReader();
      if (!reader) throw new Error('Missing response body.');
      const chunks: Uint8Array[] = []; let size = 0;
      while (true) {
        const item = await reader.read(); if (item.done) break;
        size += item.value.length;
        if (size > 16_384) { await reader.cancel(); throw new Error('Response exceeds limit.'); }
        chunks.push(item.value);
      }
      payload = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    } catch { throw new NotificationDeliveryError('telegram_invalid_response'); }
    if (payload?.ok !== true || !Number.isSafeInteger(payload?.result?.message_id)) throw new NotificationDeliveryError('telegram_invalid_response');
    return { providerMessageId: `telegram:${payload.result.message_id}` };
  };
}
