import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { mkdir, readFile, writeFile, rename, lstat, readlink, realpath } from 'node:fs/promises';
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';

export type LocalEvent = {
  id: string;
  type: 'workspace.changed' | 'delivery.changed';
  agentId: string;
  createdAt: string;
  snapshot: Record<string, unknown>;
};

export type CommandSpec = {
  command: string;
  args: string[];
  cwd: string;
  timeoutMs: number;
  maxOutputBytes?: number;
  signal?: AbortSignal;
};

export type CommandResult = {
  code: number | null;
  stdout: string;
  stderr: string;
  timedOut: boolean;
  truncated: boolean;
  aborted?: boolean;
};

export const APPROVED_VALIDATORS = [
  'scripts/validate-pattern-ids.py',
  'scripts/validate-skills.py',
  'scripts/test-skill-independence.py',
  'scripts/check-repo-payload.py',
] as const;

/** Execute a fixed argv command without a shell and retain bounded output. */
export async function runReadOnlyCommand(spec: CommandSpec): Promise<CommandResult> {
  const maximum = Math.max(1024, Math.min(spec.maxOutputBytes ?? 16_384, 8 * 1024 * 1024));
  if (spec.signal?.aborted) return { code: null, stdout: '', stderr: 'Command cancelled.', timedOut: false, truncated: false, aborted: true };
  return new Promise(resolveResult => {
    const child = spawn(spec.command, spec.args, {
      cwd: spec.cwd, windowsHide: true, shell: false,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', UV_CACHE_DIR: join(spec.cwd, '.cache', 'pi-agent-uv') },
    });
    let stdout: Buffer = Buffer.alloc(0);
    let stderr: Buffer = Buffer.alloc(0);
    let timedOut = false;
    let aborted = false;
    let truncated = false;
    let settled = false;
    let forcedTimer: NodeJS.Timeout | undefined;
    const append = (current: Buffer, chunk: Buffer): Buffer => {
      if (current.length + chunk.length > maximum) truncated = true;
      return current.length >= maximum ? current : Buffer.concat([current, chunk.subarray(0, maximum - current.length)]);
    };
    child.stdout.on('data', (chunk: Buffer) => { stdout = append(stdout, chunk); });
    child.stderr.on('data', (chunk: Buffer) => { stderr = append(stderr, chunk); });
    const finish = (code: number | null) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (forcedTimer) clearTimeout(forcedTimer);
      spec.signal?.removeEventListener('abort', cancel);
      resolveResult({ code, stdout: stdout.toString('utf8'), stderr: stderr.toString('utf8'), timedOut, truncated, ...(aborted ? { aborted: true } : {}) });
    };
    const terminate = () => {
      if (settled || forcedTimer) return;
      if (process.platform === 'win32' && child.pid) {
        // Kill the entire uv/Python tree using a numeric process identifier.
        const killer = spawn('taskkill.exe', ['/pid', String(child.pid), '/T', '/F'], { windowsHide: true, shell: false, stdio: 'ignore' });
        killer.on('error', () => { child.kill(); });
        killer.on('close', code => { if (code !== 0) child.kill(); });
      } else child.kill('SIGKILL');
      // Keep the deadline bounded even if a descendant retains a pipe handle.
      forcedTimer = setTimeout(() => { child.kill(); child.stdout.destroy(); child.stderr.destroy(); finish(null); }, 1500);
      forcedTimer.unref();
    };
    const cancel = () => { aborted = true; terminate(); };
    const timer = setTimeout(() => {
      timedOut = true;
      terminate();
    }, Math.max(100, Math.min(spec.timeoutMs, 300_000)));
    spec.signal?.addEventListener('abort', cancel, { once: true });
    if (spec.signal?.aborted) cancel();
    child.on('error', error => { stderr = append(stderr, Buffer.from(error.message)); finish(null); });
    child.on('close', finish);
  });
}

type Checkpoint = {
  version: 1;
  publishedHash?: string;
  publishedFiles?: Record<string, string>;
  publishedHead?: string;
  candidateHash?: string;
  candidateSince?: number;
  pending?: LocalEvent;
  pendingHash?: string;
  pendingFiles?: Record<string, string>;
  pendingHead?: string;
  sequence?: number;
  pendingSequence?: number;
};

export type WatcherOptions = {
  projectDir: string;
  stateDir: string;
  repository?: string;
  stabilityMs?: number;
  commandTimeoutMs?: number;
  runner?: (command: CommandSpec) => Promise<CommandResult>;
  now?: () => number;
};

function stable(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => `${JSON.stringify(key)}:${stable(item)}`).join(',')}}`;
  return JSON.stringify(value) ?? 'null';
}

function digest(value: unknown): string { return createHash('sha256').update(stable(value)).digest('hex'); }

function relevant(path: string): boolean {
  const normalized = path.replaceAll('\\', '/');
  if (normalized.split('/').some(part => ['.git', 'node_modules', 'artifacts', '.cache', 'dist', 'state', '__pycache__'].includes(part))) return false;
  if (/^(?:projects|evaluations|output|\.agents)\//.test(normalized)) return false;
  if (/^(?:skills|scripts|docs|\.github)\//.test(normalized)) {
    return /\.(?:md|py|ts|tsx|js|mjs|cjs|json|ya?ml|toml|txt|html|css|vue|svg|xml|lock)$/.test(normalized);
  }
  return /^(?:AGENTS\.md|SKILLS\.md|README\.md|package(?:-lock)?\.json|pyproject\.toml|uv\.lock|\.gitattributes|\.gitignore)$/.test(normalized);
}

function concise(result: CommandResult): Record<string, unknown> {
  return { exitCode: result.code, timedOut: result.timedOut, truncated: result.truncated, stdout: result.stdout.trim(), stderr: result.stderr.trim() };
}

export class Watchers {
  private readonly projectDir: string;
  private readonly stateDir: string;
  private readonly repository: string;
  private readonly stabilityMs: number;
  private readonly timeoutMs: number;
  private readonly runner: (command: CommandSpec) => Promise<CommandResult>;
  private readonly now: () => number;
  private readonly locks = new Map<string, Promise<LocalEvent | undefined>>();
  private readonly cancellation = new AbortController();

  constructor(options: WatcherOptions) {
    this.projectDir = resolve(options.projectDir);
    this.stateDir = resolve(options.stateDir);
    this.repository = options.repository ?? 'gvillarroel/skills';
    if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(this.repository)) throw new Error('Expected repository in owner/name form.');
    this.stabilityMs = Math.max(30_000, options.stabilityMs ?? 30_000);
    this.timeoutMs = Math.max(100, Math.min(options.commandTimeoutMs ?? 120_000, 300_000));
    this.runner = options.runner ?? runReadOnlyCommand;
    this.now = options.now ?? Date.now;
  }

  tick(agentId: 'repo-quality' | 'delivery-watch'): Promise<LocalEvent | undefined> {
    if (this.cancellation.signal.aborted) return Promise.resolve(undefined);
    const active = this.locks.get(agentId);
    if (active) return active;
    const operation = this.capture(agentId).catch(error => {
      if (this.cancellation.signal.aborted) return undefined;
      throw error;
    }).finally(() => this.locks.delete(agentId));
    this.locks.set(agentId, operation);
    return operation;
  }

  /** Abort an in-flight command tree before waiting for host shutdown. */
  close(): void { this.cancellation.abort(); }

  private assertOpen(): void {
    if (this.cancellation.signal.aborted) throw new Error('Watcher stopped.');
  }

  /** Acknowledge only after durable catalog admission, including duplicate admission. */
  async ack(agentId: string, eventId: string): Promise<void> {
    const checkpoint = await this.load(agentId);
    if (checkpoint.pending?.id !== eventId) return;
    checkpoint.publishedHash = checkpoint.pendingHash;
    checkpoint.sequence = checkpoint.pendingSequence ?? (checkpoint.sequence ?? 0) + 1;
    if (checkpoint.pendingFiles) checkpoint.publishedFiles = checkpoint.pendingFiles;
    if (checkpoint.pendingHead) checkpoint.publishedHead = checkpoint.pendingHead;
    delete checkpoint.pending;
    delete checkpoint.pendingHash;
    delete checkpoint.pendingFiles;
    delete checkpoint.pendingHead;
    delete checkpoint.pendingSequence;
    await this.save(agentId, checkpoint);
  }

  private path(agentId: string): string {
    if (!['repo-quality', 'delivery-watch'].includes(agentId)) throw new Error('Unknown watcher agent.');
    return join(this.stateDir, 'watchers', `${agentId}.json`);
  }

  private async load(agentId: string): Promise<Checkpoint> {
    try {
      const data = JSON.parse(await readFile(this.path(agentId), 'utf8')) as Checkpoint;
      if (data.version !== 1) throw new Error('Unsupported watcher checkpoint version.');
      return data;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') return { version: 1 };
      throw error;
    }
  }

  private async save(agentId: string, checkpoint: Checkpoint): Promise<void> {
    const path = this.path(agentId);
    await mkdir(dirname(path), { recursive: true });
    const temporary = `${path}.${process.pid}.tmp`;
    await writeFile(temporary, JSON.stringify(checkpoint), { encoding: 'utf8', mode: 0o600 });
    await rename(temporary, path);
  }

  private async command(command: string, args: string[], maxOutputBytes?: number): Promise<CommandResult> {
    this.assertOpen();
    const result = await this.runner({ command, args, cwd: this.projectDir, timeoutMs: this.timeoutMs, maxOutputBytes, signal: this.cancellation.signal });
    this.assertOpen();
    return result;
  }

  private async sourceFiles(): Promise<{ head: string; files: Record<string, string> }> {
    const actualRoot = await realpath(this.projectDir);
    const [revision, untracked] = await Promise.all([
      this.command('git', ['rev-parse', 'HEAD']),
      this.command('git', ['ls-files', '--others', '--exclude-standard', '-z'], 8 * 1024 * 1024),
    ]);
    const head = revision.stdout.trim();
    if (revision.code !== 0 || revision.timedOut || revision.truncated || !/^[a-f0-9]{40,64}$/i.test(head)) throw new Error('Cannot capture a valid repository HEAD.');
    // HEAD anchors committed content. Hash only paths whose working-tree content
    // differs from that exact revision, plus untracked source files.
    const dirty = await this.command('git', ['diff', '--name-only', '-z', head, '--'], 8 * 1024 * 1024);
    for (const listing of [untracked, dirty]) {
      if (listing.code !== 0 || listing.timedOut || listing.truncated) throw new Error(`Cannot capture complete dirty-source inventory: ${listing.stderr.slice(0, 1000)}`);
    }
    const paths = [...new Set(`${dirty.stdout}\0${untracked.stdout}`.split('\0').filter(path => path && relevant(path)))].sort();
    if (paths.length > 50_000) throw new Error('Dirty-source inventory exceeds the 50,000-file watcher limit.');
    const files: Record<string, string> = {};
    let totalBytes = 0;
    for (const path of paths) {
      this.assertOpen();
      const absolute = resolve(this.projectDir, path);
      const relativePath = relative(this.projectDir, absolute);
      if (isAbsolute(relativePath) || relativePath === '..' || relativePath.startsWith(`..${sep}`)) throw new Error('Source inventory contains a path outside the project.');
      try {
        const info = await lstat(absolute);
        if (info.isSymbolicLink()) { files[path] = `symlink:${digest(await readlink(absolute))}`; continue; }
        if (!info.isFile()) continue;
        const actualRelative = relative(actualRoot, await realpath(absolute));
        if (isAbsolute(actualRelative) || actualRelative === '..' || actualRelative.startsWith(`..${sep}`)) throw new Error('Source inventory resolves outside the project.');
        totalBytes += info.size;
        if (totalBytes > 512 * 1024 * 1024) throw new Error('Source inventory exceeds the 512 MiB watcher limit.');
        const hash = createHash('sha256');
        for await (const chunk of createReadStream(absolute)) { this.assertOpen(); hash.update(chunk); }
        files[path] = hash.digest('hex');
      } catch (error) {
        if ((error as NodeJS.ErrnoException).code === 'ENOENT') files[path] = 'deleted';
        else throw error;
      }
    }
    return { head, files };
  }

  private async capture(agentId: 'repo-quality' | 'delivery-watch'): Promise<LocalEvent | undefined> {
    const checkpoint = await this.load(agentId);
    if (checkpoint.pending) return checkpoint.pending;
    if (agentId === 'delivery-watch') return this.captureDelivery(checkpoint);
    const inventory = await this.sourceFiles();
    const { files, head } = inventory;
    const fingerprint = digest(inventory);
    if (fingerprint === checkpoint.publishedHash) {
      if (checkpoint.candidateHash !== fingerprint) {
        checkpoint.candidateHash = fingerprint;
        checkpoint.candidateSince = this.now();
        await this.save(agentId, checkpoint);
      }
      return undefined;
    }
    if (fingerprint !== checkpoint.candidateHash) {
      checkpoint.candidateHash = fingerprint;
      checkpoint.candidateSince = this.now();
      await this.save(agentId, checkpoint);
      return undefined;
    }
    if (this.now() - (checkpoint.candidateSince ?? this.now()) < this.stabilityMs) return undefined;
    const validations = [];
    for (const script of APPROVED_VALIDATORS) {
      const result = await this.command('uv', ['run', '--script', script]);
      validations.push({ script, ...concise(result) });
    }
    // A validation report must identify the exact inventory it observed.
    const after = await this.sourceFiles();
    if (digest(after) !== fingerprint) {
      checkpoint.candidateHash = digest(after);
      checkpoint.candidateSince = this.now();
      await this.save(agentId, checkpoint);
      return undefined;
    }
    // A legacy full-source inventory cannot be compared with dirty-source paths.
    // Keep the old checkpoint intact until this new baseline is acknowledged.
    const baselineChanged = Boolean(checkpoint.publishedHash && !checkpoint.publishedHead);
    const previous = checkpoint.publishedHead ? checkpoint.publishedFiles ?? {} : {};
    const changed = [...new Set([...Object.keys(files), ...Object.keys(previous)])].filter(path => files[path] !== previous[path]).sort();
    return this.pending(agentId, checkpoint, fingerprint, {
      kind: baselineChanged ? 'baseline-migration' : checkpoint.publishedHash ? 'source-change' : 'initial-readiness',
      repository: this.repository, fingerprint, baseline: 'git-head-plus-dirty-sources', head,
      baselineChanged, changedFileScope: checkpoint.publishedHead ? 'dirty-source-delta' : 'current-dirty-sources',
      headChanged: Boolean(checkpoint.publishedHead && checkpoint.publishedHead !== head),
      dirtySourceCount: Object.keys(files).length, fileCount: Object.keys(files).length,
      changedFileCount: changed.length, changedFiles: changed.slice(0, 100), omittedChangedFiles: Math.max(0, changed.length - 100),
      validators: validations,
    }, files, head);
  }

  private async captureDelivery(checkpoint: Checkpoint): Promise<LocalEvent | undefined> {
    const commands = [
      ['head', 'git', ['rev-parse', 'HEAD']],
      ['status', 'git', ['status', '--porcelain=v1', '-z', '--untracked-files=normal']],
      ['pullRequests', 'gh', ['pr', 'list', '--repo', this.repository, '--state', 'open', '--limit', '20', '--json', 'number,title,url,headRefOid,baseRefName,headRefName,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup']],
      ['workflowRuns', 'gh', ['run', 'list', '--repo', this.repository, '--limit', '20', '--json', 'databaseId,workflowName,headSha,event,status,conclusion,url,number,displayTitle']],
    ] as const;
    const commandStatus:Record<string,unknown> = {};
    const observations: Record<string, unknown> = { commandStatus };
    for (const [key, command, args] of commands) {
      const result = await this.command(command, [...args], key === 'pullRequests' ? 128_000 : 64_000);
      commandStatus[key] = { exitCode:result.code, timedOut:result.timedOut, truncated:result.truncated };
      if (result.code !== 0 || result.timedOut || result.truncated) { observations[key] = { error: concise(result) }; continue; }
      if (key === 'head') observations[key] = result.stdout.trim();
      else if (key === 'status') {
        observations[key] = result.stdout.split('\0').filter(item => item.length > 3 && relevant(item.slice(3))).sort();
      } else {
        try {
          const parsed = JSON.parse(result.stdout) as Record<string, unknown>[];
          if (!Array.isArray(parsed)) throw new Error('Expected a JSON list.');
          if (key === 'pullRequests') {
            observations[key] = parsed.map((pr): Record<string, unknown> => ({
              ...pr,
              statusCheckRollup: Array.isArray(pr.statusCheckRollup) ? pr.statusCheckRollup.map((check: Record<string, unknown>) => ({
                name: check.name ?? check.context, status: check.status ?? check.state, conclusion: check.conclusion,
              })).sort((a, b) => stable(a).localeCompare(stable(b))) : [],
            })).sort((a, b) => Number(a.number) - Number(b.number));
          } else observations[key] = parsed.sort((a, b) => Number(a.databaseId) - Number(b.databaseId));
        } catch { observations[key] = { error: 'The read-only GitHub command returned invalid JSON.' }; }
      }
    }
    const fingerprint = digest(observations);
    if (fingerprint === checkpoint.publishedHash) return undefined;
    return this.pending('delivery-watch', checkpoint, fingerprint, {
      kind: checkpoint.publishedHash ? 'delivery-change' : 'initial-readiness', repository: this.repository, fingerprint, ...observations,
    });
  }

  private async pending(agentId: string, checkpoint: Checkpoint, fingerprint: string, snapshot: Record<string, unknown>, files?: Record<string, string>, head?: string): Promise<LocalEvent> {
    this.assertOpen();
    const sequence = (checkpoint.sequence ?? 0) + 1;
    const event: LocalEvent = {
      id: `local:${agentId}:${fingerprint}:${sequence}`,
      type: agentId === 'repo-quality' ? 'workspace.changed' : 'delivery.changed',
      agentId, createdAt: new Date(this.now()).toISOString(), snapshot,
    };
    checkpoint.pending = event;
    checkpoint.pendingHash = fingerprint;
    checkpoint.pendingSequence = sequence;
    if (files) checkpoint.pendingFiles = files;
    if (head) checkpoint.pendingHead = head;
    await this.save(agentId, checkpoint);
    return event;
  }
}
