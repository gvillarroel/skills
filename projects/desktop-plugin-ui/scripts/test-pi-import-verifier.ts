#!/usr/bin/env node
// Node 24 native TypeScript: node projects/desktop-plugin-ui/scripts/test-pi-import-verifier.ts <passing-generated-workspace>
// Positive and injected-defect evaluator checks; requires Node 24+ only.
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {spawnSync} from "node:child_process";
import {createHash} from "node:crypto";
const sourceWorkspace=path.resolve(process.argv[2]??"");
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
if(!process.argv[2]||!sourceWorkspace.startsWith(repo+path.sep))throw new Error("A generated workspace inside this repository is required.");
const sourcePath=path.join(sourceWorkspace,"poc/extension.ts");
const bytes=fs.readFileSync(sourcePath);
const digest=(value:Uint8Array)=>createHash("sha256").update(value).digest("hex");
const source=bytes.toString("utf8").replace(/\r\n/g,"\n");
const fixtures=path.join(repo,"projects/desktop-plugin-ui/artifacts/plugin-pocs/pi-verifier-selftests");
const verifier=path.join(repo,"projects/desktop-plugin-ui/scripts/verify-pi-import-poc.ts");
const cases=[
  {name:"valid",accept:true},
  {name:"valid-local-helper",accept:true,prefix:'import { identity } from "./helper.ts";\nvoid identity;\n'},
  {name:"external-runtime-import",accept:false,prefix:'import fs from "node:fs";\nvoid fs;\n'},
  {name:"wrong-revision-accepted",accept:false,from:"if (revision !== reviewRevision)",to:"if (false)"},
  {name:"edit-keeps-stale-review",accept:false,from:"draftRevision++;\n    reviewRevision = null;\n    reviewed = [];",to:"draftRevision++;"},
  {name:"menu-escape-reviews",accept:false,from:"if (action === undefined) return;",to:"if (action === undefined) return review();"},
  {name:"whitespace-name-accepted",accept:false,from:"const value = name.trim();",to:"const value = name;"},
];
const results:any[]=[];
for(const item of cases){
  const workspace=path.join(fixtures,item.name);fs.mkdirSync(path.join(workspace,"poc"),{recursive:true});
  for(const relative of ["poc/package.json","poc/test-scenarios.json","poc/USAGE.md","poc/review.json"]){fs.copyFileSync(path.join(sourceWorkspace,relative),path.join(workspace,relative));}
  let candidate=source;
  if(item.prefix){candidate=item.prefix+candidate;}
  if(item.name==="valid-local-helper")fs.writeFileSync(path.join(workspace,"poc/helper.ts"),"export const identity = (value: unknown) => value;\n");
  if(item.from){if(source.split(item.from).length!==2)throw new Error(`Mutation ${item.name} needs exactly one source occurrence.`);candidate=source.replace(item.from,item.to!);}
  fs.writeFileSync(path.join(workspace,"poc/extension.ts"),candidate);
  const child=spawnSync(process.execPath,[verifier,workspace],{cwd:repo,encoding:"utf8",timeout:30000,windowsHide:true});
  let report:any;try{report=JSON.parse(fs.readFileSync(path.join(workspace,"evaluator-review/pi-import-independent.json"),"utf8"));}catch{}
  const accepted=child.status===0&&report?.passed===true;
  results.push({name:item.name,expectedAcceptance:item.accept,actualAcceptance:accepted,passed:accepted===item.accept,failedChecks:report?.checks?.filter(check=>!check.passed).map(check=>check.name),stdout:child.stdout,stderr:child.stderr});
}
const unchanged=digest(bytes)===digest(fs.readFileSync(sourcePath));
const report={passed:unchanged&&results.every(item=>item.passed),sourceUnchanged:unchanged,sourceSha256:digest(bytes),results};
fs.writeFileSync(path.join(fixtures,"result.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({passed:report.passed,cases:results.length,failed:results.filter(item=>!item.passed).map(item=>item.name)}));
process.exit(report.passed?0:1);
