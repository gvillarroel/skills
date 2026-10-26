#!/usr/bin/env node
// Node 24: node --test projects/pi-custodian-evolution-10/scripts/test-harness.ts
import assert from 'node:assert/strict';
import test from 'node:test';
import { createHash } from 'node:crypto';
import { mkdir,mkdtemp,readFile,writeFile } from 'node:fs/promises';
import { resolve,join } from 'node:path';
import { decisionInput,loadManifest,publicResponse,requestText,validateSettings,verify } from './evolution-verifier.ts';

const hash=(value:Uint8Array|string)=>createHash('sha256').update(value).digest('hex');
const fixture={schemaVersion:1,cases:[{id:'case-one',input:{phase:'plan',observation:'No task result exists.'},expected:{hiddenAnswer:'NEVER-SEND-EXPECTED'}}],responseContract:{reasonCodes:['missing-evidence']}};
const settings={schemaVersion:1,kind:'custodian-evolution-evaluation',mode:'faux',model:{provider:'openai-codex',id:'gpt-6.1-sol',effort:'medium'},weights:{decisions:1,worker:0},timeoutMs:1000};
async function folder(){const parent=resolve('projects/pi-custodian-evolution-10/artifacts/harness-tests');await mkdir(parent,{recursive:true});return mkdtemp(join(parent,'case-'));}

test('model-visible input never receives expected answers; public vocabulary is provided',()=>{
  assert.deepEqual(decisionInput(fixture),[{id:'case-one',input:fixture.cases[0].input}]);
  const text=requestText(fixture);assert.ok(!text.includes('NEVER-SEND-EXPECTED'));assert.ok(text.includes('missing-evidence'));assert.ok(text.includes('no tools'));
});
test('real inference requires explicit authorization and exact Sol model/effort',()=>{
  assert.throws(()=>validateSettings({...settings,mode:'real',weights:{decisions:.5,worker:.5}}),/enabled/);
  assert.throws(()=>validateSettings({...settings,model:{...settings.model,id:'latest'}}),/exact Sol/);
  assert.throws(()=>validateSettings({...settings,model:{...settings.model,effort:'high'}}),/exact Sol/);
  assert.throws(()=>validateSettings({...settings,timeoutMs:180001}),/180 seconds/);
});
test('provider thinking is excluded and invalid public JSON remains a retained outcome',()=>{
  const response=publicResponse({provider:'openai-codex',model:'gpt-6.1-sol',content:[{type:'thinking',thinking:'NEVER-STORE-PRIVATE'},{type:'text',text:'invalid-json'}],usage:{input:3,output:4,totalTokens:7,reasoning:2},stopReason:'stop'});
  assert.equal(response.invalidJson,true);assert.equal(response.parsed,null);assert.ok(!JSON.stringify(response).includes('NEVER-STORE-PRIVATE'));assert.ok(!JSON.stringify(response).includes('reasoning'));
  assert.throws(()=>publicResponse({content:[{type:'toolCall',name:'no'}]}),/no-tool/);
});
test('manifest rejects altered bytes, ambiguous names and inputs outside its harness',async()=>{
  const root=await folder(),a=join(root,'a.json'),manifest=join(root,'fixtures.json');await writeFile(a,'{}');await writeFile(manifest,JSON.stringify([{path:a,sha256:hash('{}')}]))
  assert.equal((await loadManifest(manifest)).files.size,1);
  await writeFile(a,'{"changed":true}');await assert.rejects(loadManifest(manifest),/changed/);
  const outside=join(await folder(),'a.json');await writeFile(outside,'{}');await writeFile(manifest,JSON.stringify([{path:outside,sha256:hash('{}')}]))
  await assert.rejects(loadManifest(manifest),/escaped/);
  const sub=join(root,'sub');await mkdir(sub);const other=join(sub,'a.json');await writeFile(other,'{}');await writeFile(a,'{}');await writeFile(manifest,JSON.stringify([{path:a,sha256:hash('{}')},{path:other,sha256:hash('{}')}]))
  await assert.rejects(loadManifest(manifest),/unique/);
});
test('actual Pi SDK faux roundtrip retains public output without a model, service or source mutation',async()=>{
  const root=await folder(),project=resolve('C:/Users/villa/dev/.pi/durable/repo-custodian');
  const prompt=join(project,'prompts/repo-custodian.md'),config=join(project,'config.json'),before=[hash(await readFile(prompt)),hash(await readFile(config))];
  const response={cases:[{id:'case-one',action:'inspect',reasonCodes:['missing-evidence'],requiredChecks:[],missingChecks:[],missingEvidence:['result'],claimedOutcome:'unknown',nextAction:'Read a completed result.'}]};
  const files=[['evaluation-settings.json',{...settings,timeoutMs:10000,fauxResponse:response}],['decision-cases.json',fixture],['decision-grader.mjs',null]] as const;
  const entries=[];
  for(const [name,value] of files){const path=join(root,name),content=name.endsWith('.mjs')?"export function gradeDecisions(b,o){return {passed:o.cases[0].action==='inspect',score:0.75,cases:[{id:b.cases[0].id,passed:true,score:0.75}]};}\n":JSON.stringify(value);await writeFile(path,content);entries.push({path,sha256:hash(content)});}
  // Keep module selection explicitly frozen rather than assuming a .ts sibling.
  const settingsPath=join(root,'evaluation-settings.json');const changed=JSON.stringify({...settings,timeoutMs:10000,fauxResponse:response,decisionGrader:'decision-grader.mjs'});await writeFile(settingsPath,changed);entries[0].sha256=hash(changed);
  const manifest=join(root,'fixtures.json');await writeFile(manifest,JSON.stringify(entries));const outcome=await verify(project,manifest);
  assert.equal(outcome.passed,true);assert.equal(outcome.score,.75);assert.equal(outcome.mechanicsOnly,true);
  const receipt=JSON.parse(await readFile(join(root,'evaluation-artifacts/model-response.json'),'utf8'));assert.equal(receipt.noTools,true);assert.equal(receipt.oneFreshRequest,true);assert.equal(receipt.mechanicsOnly,true);assert.ok(!receipt.observed.model.startsWith('gpt-'));
  assert.deepEqual([hash(await readFile(prompt)),hash(await readFile(config))],before);
});
