import { spawn } from "node:child_process";
import { createHash, randomBytes, timingSafeEqual } from "node:crypto";
import { mkdir, mkdtemp, readFile, realpath, rm, stat } from "node:fs/promises";
import path from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { z } from "zod";

export const HERE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const FILES = {
  "chart.html": "text/html; charset=utf-8",
  "chart.svg": "image/svg+xml",
  "chart.png": "image/png",
  "chart.py": "text/plain; charset=utf-8",
  "spec.json": "application/json; charset=utf-8",
} as const;
export type ArtifactName = keyof typeof FILES;
export type Colorset = "colorset1" | "colorset2";
const safeText = z.string().max(1024);
const EngineResult = z.object({
  schema_version: z.literal(1), title: safeText, palette: z.enum(["colorset1", "colorset2"]),
  width: z.number().int().min(320).max(2000), height: z.number().int().min(240).max(1400),
  factory: safeText, files: z.object({ html: z.literal("chart.html"), svg: z.literal("chart.svg"), png: z.literal("chart.png"), source: z.literal("chart.py"), spec: z.literal("spec.json") }),
  svg_bytes: z.number().int().nonnegative(), png_bytes: z.number().int().nonnegative(),
  svg_compat_repairs: z.number().int().nonnegative(), warnings: z.array(safeText).max(50),
  counts: z.object({marks:z.number().int().nonnegative(),rows:z.number().int().nonnegative()}),
}).passthrough();
export type RenderMetadata = z.infer<typeof EngineResult>;
export interface RenderRecord { id: string; key: string; directory: string; spec: Record<string, unknown>; metadata: RenderMetadata; created: number; bytes: number; }
export interface ServerConfig {
  baseUrl: string; runtimeDir: string; renderScript: string; skillDir: string;
  uv: string; python?: string; renderTimeoutMs: number; ttlMs: number;
  maxRecords: number; maxBytes: number; maxConcurrent: number; maxSessions: number;
  bearer?: string; widgetDomain?:string; bind: string; port: number;
}
export function configFromEnv(env = process.env, options: {desktop?: boolean} = {}): ServerConfig {
  // A desktop plugin is a local child process, regardless of inherited hosting settings.
  if(options.desktop)env={...env,HOST:"127.0.0.1",PORT:"0",XY_PUBLIC_BASE_URL:"http://127.0.0.1:0",XY_MCP_BEARER_TOKEN:undefined,XY_WIDGET_DOMAIN:undefined,XY_RUNTIME_DIR:env.XY_RUNTIME_DIR??path.join(tmpdir(),"reflex-xy")};
  const port = Number(env.PORT ?? 8787);
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error("PORT must be between 0 and 65535.");
  const base = new URL(env.XY_PUBLIC_BASE_URL ?? `http://127.0.0.1:${port}`);
  if (!["http:","https:"].includes(base.protocol) || base.username || base.password || base.search || base.hash || base.pathname !== "/") throw new Error("XY_PUBLIC_BASE_URL must be an HTTP(S) origin without a path.");
  const bind = env.HOST ?? "127.0.0.1";
  if (!['127.0.0.1','localhost','::1'].includes(bind) && !env.XY_MCP_BEARER_TOKEN && env.XY_ALLOW_PUBLIC_NOAUTH !== "1") throw new Error("Public binding requires XY_MCP_BEARER_TOKEN or explicit XY_ALLOW_PUBLIC_NOAUTH=1 for non-sensitive development data.");
  return {
    baseUrl: base.origin, runtimeDir: path.resolve(env.XY_RUNTIME_DIR ?? path.join(HERE,".runtime")),
    renderScript: path.resolve(env.XY_RENDER_SCRIPT ?? path.join(HERE,"../runtime/render.py")),
    skillDir: path.resolve(env.XY_SKILL_DIR ?? path.join(HERE,"../runtime/skill/reflex-xy")),
    uv: env.XY_UV_BINARY ?? "uv", python: env.XY_PYTHON, renderTimeoutMs: 90000,
    ttlMs: 20*60*1000, maxRecords: 40, maxBytes: 256*1024*1024, maxConcurrent: 2,
    maxSessions: 100, bearer: env.XY_MCP_BEARER_TOKEN, widgetDomain:env.XY_WIDGET_DOMAIN, bind, port,
  };
}
export function parseSpec(text: string): Record<string, unknown> {
  if (Buffer.byteLength(text,"utf8") > 196608) throw new Error("Chart input exceeds 192 KiB.");
  let value: unknown;
  try { value=JSON.parse(text); } catch { throw new Error("spec_json must be a valid JSON object."); }
  let nodes=0;
  function walk(node: unknown, depth: number) {
    if (++nodes > 30000 || depth > 12) throw new Error("Chart input is too complex.");
    if (typeof node === "number" && !Number.isFinite(node)) throw new Error("Use finite numbers or null for missing values.");
    if (typeof node === "string" && node.length > 1024) throw new Error("A chart string exceeds 1024 characters.");
    if (Array.isArray(node)) { if (node.length > 10000) throw new Error("An input array exceeds 10000 elements."); for(const item of node) walk(item,depth+1); }
    else if(node && typeof node === "object") {
      if(Object.keys(node).length>128) throw new Error("An input object has too many fields.");
      for(const [key,item] of Object.entries(node)) {
        if (["__proto__","prototype","constructor"].includes(key)) throw new Error("Reserved object key.");
        walk(item,depth+1);
      }
    }
  }
  walk(value,0);
  if(!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Chart input must be an object.");
  const spec=value as Record<string, unknown>;
  // Every request starts with the same default. Never inherit a previous
  // widget's explicit palette choice into a new specification.
  if(!Object.hasOwn(spec,"colorset"))spec.colorset="colorset1";
  return spec;
}
function sameSecret(a: string,b: string): boolean {
  const one=createHash("sha256").update(a).digest(); const two=createHash("sha256").update(b).digest();
  return timingSafeEqual(one,two);
}
export class RenderStore {
  readonly records=new Map<string,RenderRecord>();
  private running=0;
  private sessions=0;
  constructor(readonly config: ServerConfig) {}
  private async discard(record: RenderRecord) {
    this.records.delete(record.id);
    const target=path.resolve(record.directory); const root=path.resolve(this.config.runtimeDir);
    if (!target.startsWith(root+path.sep) || path.dirname(target)!==root || !path.basename(target).startsWith("xy-")) throw new Error("Refusing to clean a directory outside the runtime root.");
    await rm(target,{recursive:true,force:true});
  }
  async prune() {
    const now=Date.now();
    for(const record of [...this.records.values()]) if(now-record.created>=this.config.ttlMs) await this.discard(record);
    let bytes=[...this.records.values()].reduce((sum,r)=>sum+r.bytes,0);
    for(const record of [...this.records.values()]) {
      if(this.records.size<this.config.maxRecords && bytes<this.config.maxBytes) break;
      bytes-=record.bytes; await this.discard(record);
    }
  }
  private async admit(record:RenderRecord) {
    if(record.bytes>this.config.maxBytes)throw new Error("Chart exceeds the configured cache capacity.");
    let bytes=[...this.records.values()].reduce((sum,r)=>sum+r.bytes,0);
    const evicted:RenderRecord[]=[];
    // Choose admission and mutate the index synchronously so concurrent renders
    // cannot each reserve the same remaining cache capacity.
    for(const existing of this.records.values()) {
      if(this.records.size<this.config.maxRecords && bytes+record.bytes<=this.config.maxBytes)break;
      bytes-=existing.bytes;this.records.delete(existing.id);evicted.push(existing);
    }
    this.records.set(record.id,record);
    for(const existing of evicted)await this.discard(existing);
  }
  acquireSession() { if(this.sessions>=this.config.maxSessions) throw new Error("Too many active MCP sessions."); ++this.sessions; return ()=>--this.sessions; }
  get(id: string,key: string): RenderRecord | undefined {
    const record=this.records.get(id);
    if(!record || Date.now()-record.created>=this.config.ttlMs || !sameSecret(record.key,key)) return undefined;
    return record;
  }
  async read(id: string,key: string,name: string): Promise<{data:Buffer;type:string}|undefined> {
    const record=this.get(id,key);
    if(!record || !Object.hasOwn(FILES,name)) return undefined;
    const filename=path.join(record.directory,name);
    const actual=await realpath(filename);
    if(path.dirname(actual)!==await realpath(record.directory)) throw new Error("Artifact symlinks are not permitted.");
    return {data:await readFile(actual),type:FILES[name as ArtifactName]};
  }
  artifactUrl(record: RenderRecord,name: ArtifactName) {
    return `${this.config.baseUrl}/artifacts/${record.id}/${name}?token=${record.key}`;
  }
  async render(spec: Record<string,unknown>): Promise<RenderRecord> {
    if(this.running>=this.config.maxConcurrent) throw new Error("Renderer is busy. Retry after the current chart finishes.");
    ++this.running;
    let directory: string|undefined;
    try {
      await this.prune();
      await mkdir(this.config.runtimeDir,{recursive:true});
      directory=await mkdtemp(path.join(this.config.runtimeDir,"xy-"));
      const argv=this.config.python
        ? [this.config.renderScript,"--output-dir",directory]
        : ["run","--script",this.config.renderScript,"--output-dir",directory];
      const stdout=await new Promise<string>((resolve,reject)=>{
        const child=spawn(this.config.python ?? this.config.uv,argv,{
          shell:false,windowsHide:true,detached:process.platform!=="win32",cwd:path.dirname(this.config.renderScript),
          env:{...process.env, PYTHONIOENCODING:"utf-8",PYTHONDONTWRITEBYTECODE:"1",XY_SKILL_DIR:this.config.skillDir},stdio:["pipe","pipe","pipe"],
        });
        let out="",err="",done=false;
        const terminate=()=>{
          if(child.pid && process.platform==="win32") {
            const killer=spawn("taskkill",["/PID",String(child.pid),"/T","/F"],{shell:false,windowsHide:true,stdio:"ignore"});killer.on("error",()=>child.kill());
          } else if(child.pid) {try{process.kill(-child.pid,"SIGKILL");}catch{child.kill();}}
          else child.kill();
        };
        const finish=(error?:Error)=>{if(done)return;done=true;clearTimeout(timer);if(error){terminate();reject(error);}else resolve(out);};
        const timer=setTimeout(()=>finish(new Error("XY render timed out. Reduce the chart size or data.")),this.config.renderTimeoutMs);
        child.on("error",()=>finish(new Error("Cannot start the configured Python/uv renderer. Check installation and XY_RENDER_SCRIPT.")));
        child.stdout.on("data",chunk=>{out+=String(chunk);if(Buffer.byteLength(out)>262144)finish(new Error("Renderer output exceeded the limit."));});
        child.stderr.on("data",chunk=>{err+=String(chunk);if(Buffer.byteLength(err)>65536)finish(new Error("Renderer diagnostic output exceeded the limit."));});
        child.stdin.on("error",()=>{});
        child.on("close",code=>{
          if(code!==0) {
            let message="XY could not render this specification. Check the supported fields and chart arguments.";
            try{const parsed=JSON.parse(err.trim()); if(typeof parsed?.error?.message==="string")message=parsed.error.message.slice(0,1024);}catch{}
            finish(new Error(message));
          } else finish();
        });
        child.stdin.end(JSON.stringify(spec));
      });
      const metadata=EngineResult.parse(JSON.parse(stdout.trim()));
      let bytes=0;
      for(const name of Object.keys(FILES)) {
        const filename=path.join(directory,name); const actual=await realpath(filename);
        if(path.dirname(actual)!==await realpath(directory)) throw new Error("Renderer returned an unsafe artifact path.");
        const info=await stat(actual); if(!info.isFile() || info.size>32*1024*1024) throw new Error("A generated artifact exceeds 32 MiB."); bytes+=info.size;
      }
      if(bytes>64*1024*1024)throw new Error("Chart artifact bundle exceeds 64 MiB.");
      const record={id:randomBytes(16).toString("hex"),key:randomBytes(32).toString("base64url"),directory,spec,metadata,created:Date.now(),bytes};
      await this.admit(record); return record;
    } catch(error) {
      if(directory) await this.discard({id:"uncommitted",directory} as RenderRecord);
      throw error;
    } finally {--this.running;}
  }
}
