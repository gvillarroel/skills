#!/usr/bin/env node
// Run with Node 24 native TypeScript: node projects/desktop-plugin-ui/scripts/verify-pi-import-poc.ts <workspace> [result-name]
// Evaluator-owned state/interaction checks. Requires Node 24+ only.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { stripTypeScriptTypes } from "node:module";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

if (!vm.SourceTextModule) {
  const child = spawnSync(process.execPath, ["--experimental-vm-modules", fileURLToPath(import.meta.url), ...process.argv.slice(2)], { stdio: "inherit" });
  process.exit(child.status ?? 2);
}
const [workspaceArgument, resultName = "pi-import-independent"] = process.argv.slice(2);
if (!workspaceArgument || !/^[a-z0-9-]+$/.test(resultName)) {
  console.error("Usage: node verify-pi-import-poc.ts <workspace> [result-name]");
  process.exit(2);
}
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const workspace = path.resolve(workspaceArgument);
if (!workspace.startsWith(root + path.sep)) throw new Error("Workspace must remain inside this repository.");
const sourcePath = path.join(workspace, "poc/extension.ts");
const checks: any[] = [];
const transcripts: any[] = [];
const record = (name: string, passed: unknown, detail: unknown = undefined) => checks.push({ name, passed: Boolean(passed), ...(detail === undefined ? {} : { detail }) });
const clone = (value: any) => JSON.parse(JSON.stringify(value));
const rows = (value: any) => Array.isArray(value) ? value.map(item => ({ id: item.id, name: item.name })).sort((a,b) => String(a.id).localeCompare(String(b.id))) : value;
const same = (left: any, right: any) => JSON.stringify(left) === JSON.stringify(right);
const expectedInitial = [{ id:"I-11", name:"Atlas" }, { id:"I-12", name:"" }, { id:"I-13", name:"Cedar" }];
const expectedValid = [expectedInitial[0], expectedInitial[2]];
let source = "";
try {
  source = stripTypeScriptTypes(fs.readFileSync(sourcePath, "utf8"), { mode:"transform", sourceUrl:sourcePath });
  record("typescript-loadable", true);
} catch (error) { record("typescript-loadable", false, String(error)); }

type DialogScript = { selections?: Array<string|RegExp|undefined>; inputs?: Array<string|undefined>; confirms?: boolean[]; beforeInput?:()=>Promise<void>; beforeConfirm?:()=>Promise<void> };
async function createRuntime() {
  const commands = new Map<string, any>();
  const calls: any[] = [];
  const messages: any[] = [];
  const forbidden: any[] = [];
  let script: DialogScript = {};
  let hasUI = false;
  const reject = (method: string) => (...args:any[]) => { forbidden.push({ method, args:clone(args) }); throw new Error(`Forbidden action: ${method}`); };
  const guard = (method:string) => { if (!hasUI) return reject(`headless-ui:${method}`)(); };
  const ui = {
    select: async (title:string, options:string[]) => {
      guard("select");
      if (!Array.isArray(options) || options.some(item => typeof item !== "string")) throw new Error("Native selector options must be strings.");
      calls.push({ method:"select", title, options:clone(options) });
      const answer = script.selections?.shift();
      if (answer === undefined) return undefined;
      const selected = typeof answer === "string" ? options.find(item => item === answer) : options.find(item => answer.test(item));
      if (selected === undefined) throw new Error(`Evaluator could not find requested semantic option ${String(answer)} in ${JSON.stringify(options)}`);
      return selected;
    },
    input: async (title:string, placeholder?:string) => { guard("input"); calls.push({ method:"input", title, placeholder }); const answer=script.inputs?.shift();const before=script.beforeInput;script.beforeInput=undefined;if(before)await before();return answer; },
    confirm: async (title:string, message:string) => { guard("confirm"); calls.push({ method:"confirm", title, message }); const answer=script.confirms?.shift()??false;const before=script.beforeConfirm;script.beforeConfirm=undefined;if(before)await before();return answer; },
    editor: async (title:string, initial?:string) => { guard("editor"); calls.push({ method:"editor", title, initial }); return script.inputs?.shift(); },
    notify: (message:string, level?:string) => { guard("notify"); calls.push({ method:"notify", message, level }); },
    theme: { fg: (_role:string,text:string) => text, bg: (_role:string,text:string) => text, bold:(text:string)=>text },
  };
  const pi = new Proxy({
    registerCommand: (name:string, command:any) => { if (typeof command?.handler !== "function") throw new Error("Command requires handler."); commands.set(name,command); },
    sendMessage: (message:any, options:any) => {
      if (options?.triggerTurn === true) return reject("sendMessage.triggerTurn")(message,options);
      messages.push(clone(message)); calls.push({ method:"sendMessage", message:clone(message), options:clone(options ?? {}) });
    },
    registerMessageRenderer: (...args:any[]) => calls.push({ method:"registerMessageRenderer", argumentCount:args.length }),
    on: (event:string) => calls.push({ method:"on", event }),
  }, { get(target:any,key) { return key in target ? target[key] : key === "then" ? undefined : reject(`pi.${String(key)}`); } });
  const sandbox = vm.createContext({
    console: { log:(...args:any[])=>calls.push({method:"console.log",args}), error:(...args:any[])=>calls.push({method:"console.error",args}) },
    structuredClone, TextEncoder, TextDecoder, URL,
    fetch:reject("fetch"), process:new Proxy({}, {get:(_target,key)=>reject(`process.${String(key)}`)}),
  }, { codeGeneration:{strings:false,wasm:false} });
  if (!source) throw new Error("No transformed source to execute.");
  const moduleCache = new Map<string, any>();
  const pocRoot=path.join(workspace,"poc");
  const loadModule=(filename:string):any=>{
    const existing=moduleCache.get(filename);if(existing)return existing;
    let result:any;
    if(filename.endsWith(".json")){
      const value=JSON.parse(fs.readFileSync(filename,"utf8"));
      result=new vm.SyntheticModule(["default"],function(){this.setExport("default",value);},{context:sandbox,identifier:filename});
    }else{
      const code=filename===sourcePath?source:stripTypeScriptTypes(fs.readFileSync(filename,"utf8"),{mode:"transform",sourceUrl:filename});
      result=new vm.SourceTextModule(code,{context:sandbox,identifier:filename,
        importModuleDynamically:async specifier=>{throw new Error(`Dynamic import requires evaluator review: ${specifier}`);}});
    }
    moduleCache.set(filename,result);return result;
  };
  const module=loadModule(sourcePath);
  await module.link(async(specifier:string,referencing:any)=>{
    if(!specifier.startsWith("./")&&!specifier.startsWith("../"))throw new Error(`External runtime import forbidden: ${specifier}`);
    let target=path.resolve(path.dirname(referencing.identifier),specifier);
    if(!fs.existsSync(target))target=[target+".ts",target+".js",target+".mjs"].find(candidate=>fs.existsSync(candidate))??target;
    if(fs.lstatSync(target).isSymbolicLink())throw new Error(`Runtime module cannot be a symlink: ${specifier}`);
    target=fs.realpathSync(target);
    if(!target.startsWith(pocRoot+path.sep))throw new Error(`Runtime import escapes the generated PoC: ${specifier}`);
    return loadModule(target);
  });
  await module.evaluate({ timeout:1500 });
  if (typeof module.namespace.default !== "function") throw new Error("Missing default Pi extension initializer.");
  await module.namespace.default(pi);
  const command = commands.get("import-review");
  if (!command) throw new Error("import-review command is missing.");
  return {
    commands, calls, messages, forbidden,
    async invoke(args:string, interactive=false, nextScript:DialogScript={}) {
      hasUI=interactive; script={ selections:[...(nextScript.selections??[])],inputs:[...(nextScript.inputs??[])],confirms:[...(nextScript.confirms??[])],beforeInput:nextScript.beforeInput,beforeConfirm:nextScript.beforeConfirm };
      const start=messages.length; const callStart=calls.length;
      let error:string|undefined;
      try {
        await command.handler(args,{hasUI,mode:hasUI?"rpc":"print",cwd:workspace,ui,isIdle:()=>true,
          sessionManager:{getEntries:()=>[],getBranch:()=>[]},modelRegistry:new Proxy({}, {get:(_target,key)=>reject(`modelRegistry.${String(key)}`)})});
      } catch(caught) {error=String(caught);}
      const emitted=messages.slice(start);
      const last=emitted.filter(message=>message.customType==="import-review").at(-1);
      const result={args,interactive,emitted,calls:calls.slice(callStart),state:last?.details,error};
      transcripts.push(clone(result));
      return result;
    }
  };
}

let failure:string|undefined;
let runtime:any;
const run = async(name:string, args:string, interactive=false, script:DialogScript={}) => {
  const result = await runtime.invoke(args,interactive,script);
  record(`${name}:executes`, !result.error, result.error);
  if (result.state) {
    record(`${name}:snapshot-contract`, Number.isInteger(result.state.draftRevision) &&
      (result.state.reviewRevision===null || Number.isInteger(result.state.reviewRevision)) &&
      ["draftRows","reviewedRows","committedRows"].every(field=>Array.isArray(result.state[field])) &&
      result.emitted.some((message:any)=>message.customType==="import-review" && typeof message.content==="string" && message.content.trim().length>0));
  }
  return result;
};
const status=async(name:string)=>{
  const result=await run(name,"status");
  if (!result.state) throw new Error(`${name}: no observable state snapshot`);
  return result.state;
};

try {
  runtime=await createRuntime();
  record("native-command-registered", runtime.commands.has("import-review"));
  let initial=await status("initial-status");
  record("initial-rows-exact",same(rows(initial.draftRows),rows(expectedInitial)),initial);
  record("initial-committed-empty",initial.committedRows.length===0);
  record("initial-review-empty",initial.reviewRevision===null && initial.reviewedRows.length===0);
  await run("missing-review-rejection",`commit ${initial.draftRevision}`);
  record("missing-review-preserves-empty-commit",(await status("after-missing-review")).committedRows.length===0);
  const firstReview=await run("review-valid-only","review");
  record("review-captures-current-revision",firstReview.state?.reviewRevision===initial.draftRevision);
  record("review-excludes-invalid-row",same(rows(firstReview.state?.reviewedRows),rows(expectedValid)),firstReview.state);
  const originalReviewRevision=firstReview.state?.reviewRevision;
  await run("wrong-current-revision-rejected",`commit ${originalReviewRevision+1}`);
  const afterWrongRevision=await status("after-wrong-revision");
  record("wrong-revision-preserves-current-review",afterWrongRevision.committedRows.length===0 && afterWrongRevision.reviewRevision===originalReviewRevision && same(rows(afterWrongRevision.reviewedRows),rows(expectedValid)));
  const edited=await run("edit-valid","edit I-12 Birch");
  record("edit-increments-revision",edited.state?.draftRevision>initial.draftRevision);
  record("edit-invalidates-review",edited.state?.reviewRevision===null && edited.state?.reviewedRows.length===0);
  record("edit-preserves-other-rows",same(rows(edited.state?.draftRows),rows([expectedInitial[0],{id:"I-12",name:"Birch"},expectedInitial[2]])));
  await run("stale-review-rejected",`commit ${originalReviewRevision}`);
  record("stale-commit-makes-no-change",(await status("after-stale-commit")).committedRows.length===0);
  const newReview=await run("fresh-review","review");
  const validRows=rows(newReview.state?.reviewedRows);
  const commit=await run("current-commit",`commit ${newReview.state?.reviewRevision}`);
  record("commit-exact-reviewed-data",same(rows(commit.state?.committedRows),validRows)&&commit.state?.committedRows.length===3,commit.state);
  await run("repeated-commit",`commit ${newReview.state?.reviewRevision}`);
  const afterRepeat=await status("after-repeat");
  record("repeat-no-duplicates",afterRepeat.committedRows.length===3 && new Set(afterRepeat.committedRows.map((row:any)=>row.id)).size===3 && same(rows(afterRepeat.committedRows),validRows));
  const preserved=clone(afterRepeat);
  for(const [label,args] of [["invalid-id","edit I-99 Maple"],["blank-name","edit I-12    "],["unknown-action","explode"]]) {
    await run(label,args);
    record(`${label}:state-preserved`,same(await status(`${label}-status`),preserved));
  }
  const spaceEdit=await run("space-name","edit I-12 Silver Birch");
  record("name-with-spaces-preserved",spaceEdit.state?.draftRows.find((row:any)=>row.id==="I-12")?.name==="Silver Birch");
  const reviewedAgain=await run("review-before-cancel","review");
  const cancel=await run("explicit-cancel","cancel");
  record("cancel-clears-review-only",cancel.state?.reviewRevision===null && cancel.state?.reviewedRows.length===0 &&
    same(rows(cancel.state?.draftRows),rows(reviewedAgain.state?.draftRows)) && same(rows(cancel.state?.committedRows),rows(reviewedAgain.state?.committedRows)));
  const headless=await run("no-ui-empty","");
  record("no-ui-shows-state-and-help",Boolean(headless.state) && headless.emitted.some((message:any)=>/import-review/.test(message.content)) && !headless.calls.some((call:any)=>["select","input","confirm"].includes(call.method)));

  runtime=await createRuntime();
  const beforeMenu=await status("ui-initial");
  await run("ui-blank-name","",true,{selections:[/\bedit\b/i,/I-12/],inputs:["   "]});
  record("ui-blank-name-preserves-state",same(await status("after-ui-blank-name"),beforeMenu));
  await run("menu-escape","",true,{selections:[undefined]});
  record("menu-escape-preserves-state",same(await status("after-menu-escape"),beforeMenu));
  await run("edit-input-escape","",true,{selections:[/\bedit\b/i,/I-12/],inputs:[undefined]});
  record("edit-input-escape-preserves-state",same(await status("after-edit-escape"),beforeMenu));
  await run("review-before-confirm","review");
  const beforeConfirm=await status("before-confirm");
  await run("declined-confirmation","",true,{selections:[/\bcommit\b/i],confirms:[false]});
  const afterConfirm=await status("after-confirm");
  record("decline-preserves-review-and-draft",same(beforeConfirm,afterConfirm));
  record("decline-does-not-commit",afterConfirm.committedRows.length===0);
  await run("accepted-confirmation","",true,{selections:[/\bcommit\b/i],confirms:[true]});
  const afterAccept=await status("after-accepted-confirmation");
  record("accepted-native-confirm-commits-reviewed-valid-rows",same(rows(afterAccept.committedRows),rows(expectedValid)),afterAccept);
  record("zero-forbidden-actions",runtime.forbidden.length===0,runtime.forbidden);

  runtime=await createRuntime();
  await run("async-review","review");
  await run("stale-native-confirmation","",true,{selections:[/\bcommit\b/i],confirms:[true],beforeConfirm:async()=>{await runtime.invoke("edit I-12 Birch");}});
  const afterStaleConfirm=await status("after-stale-native-confirm");
  record("async-confirm-cannot-commit-stale-review",afterStaleConfirm.committedRows.length===0 && afterStaleConfirm.reviewRevision===null && afterStaleConfirm.draftRows.find((row:any)=>row.id==="I-12")?.name==="Birch");
  runtime=await createRuntime();
  await run("stale-native-edit","",true,{selections:[/\bedit\b/i,/I-12/],inputs:["Birch"],beforeInput:async()=>{await runtime.invoke("edit I-12 Newer Birch");}});
  const afterStaleEdit=await status("after-stale-native-edit");
  record("async-input-cannot-overwrite-newer-row-value",afterStaleEdit.draftRows.find((row:any)=>row.id==="I-11")?.name==="Atlas" && afterStaleEdit.draftRows.find((row:any)=>row.id==="I-12")?.name==="Newer Birch");
} catch(error) { failure=String(error); record("evaluator-completed",false,failure); }

for(const artifact of ["poc/package.json","poc/test-scenarios.json","poc/USAGE.md","poc/review.json"]){
  const target=path.join(workspace,artifact); record(`artifact:${artifact}`,fs.existsSync(target)&&fs.statSync(target).size>0);
}
try {
  const metadata=JSON.parse(fs.readFileSync(path.join(workspace,"poc/package.json"),"utf8"));
  record("package-entry-exists",Array.isArray(metadata.pi?.extensions)&&metadata.pi.extensions.some((entry:string)=>path.resolve(workspace,"poc",entry)===sourcePath));
  const review=JSON.parse(fs.readFileSync(path.join(workspace,"poc/review.json"),"utf8"));
  record("no-false-host-user-acceptance",review.host_paint_verified===false && review.user_testing_performed===false);
} catch(error) {record("metadata-review-parse",false,String(error));}
const outputDirectory=path.join(workspace,"evaluator-review");
fs.mkdirSync(outputDirectory,{recursive:true});
const output=path.join(outputDirectory,`${resultName}.json`);
const report={passed:checks.length>0&&checks.every(item=>item.passed),checks,transcripts,failure:failure??null,
  boundary:"Evaluator-owned exported-handler VM checks; actual Pi RPC is a separate layer. TUI paint and user testing are unverified."};
fs.writeFileSync(output,JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({passed:report.passed,checked:checks.length,failed:checks.filter(item=>!item.passed).map(item=>item.name),output}));
process.exit(report.passed?0:1);
