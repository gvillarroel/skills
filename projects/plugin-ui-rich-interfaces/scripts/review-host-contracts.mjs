// Run: node projects/plugin-ui-rich-interfaces/scripts/review-host-contracts.mjs
// Independently inspect the focused isolated contract artifacts; no host-paint claim.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const repo=path.resolve(root,'../..');
const runIds=['20261112-ui-short-terminal-contract-sol-1','20261112-ui-short-terminal-contract-sol-2','20261112-ui-allocated-panel-codex-sol-1','20261112-ui-allocated-panel-router-sol-1'];
const results=[];
for(const id of runIds){
  const folder=path.join(repo,'evaluations/runs',id),workspace=path.join(folder,'workspace');
  const strict=JSON.parse(await fs.readFile(path.join(folder,'evaluation-result.json'),'utf8'));
  const checks=[];
  try{
    if(id.includes('short-terminal')){
      const review=JSON.parse(await fs.readFile(path.join(workspace,'short-terminal-review.json'),'utf8'));
      for(const field of ['heightBudget','pageControls','resizePolicy','selectionPolicy','coverageCheck','evidenceBoundary'])assert.ok(typeof review[field]==='string'&&review[field].length>30,field);
      assert.ok(review.mode.startsWith('tui'));
      const {pageRows}=await import(pathToFileURL(path.join(workspace,'pager.mjs')));
      const records=Object.freeze(Array.from({length:24},(_,hour)=>Object.freeze({id:hour,hour:`${String(hour).padStart(2,'0')}:00`,value:hour*7+3})));
      for(const capacity of [1,3,7,8,24,40]){
        const pages=pageRows(records,0,capacity).pages,forward=[],backward=[];
        for(let page=0;page<pages;page++)forward.push(...pageRows(records,page,capacity).records);
        for(let page=pages-1;page>=0;page--)backward.unshift(...pageRows(records,page,capacity).records);
        assert.deepEqual(forward,records);assert.deepEqual(backward,records);
        assert.equal(pageRows(records,-50,capacity).page,0);assert.equal(pageRows(records,500,capacity).page,pages-1);
      }
      assert.deepEqual(pageRows([],8,8),{page:0,pages:1,records:[]});
      for(const capacity of [0,-1,1.5,NaN,Infinity])assert.throws(()=>pageRows(records,0,capacity));
      const copy=pageRows(records,0,8).records;copy.pop();assert.equal(records.length,24);
      checks.push('All exact records survive forward/backward traversal and capacity changes','Bounds, empty data, invalid capacities and independent page arrays');
    }else{
      const review=JSON.parse(await fs.readFile(path.join(workspace,'panel-review.json'),'utf8'));
      assert.equal(review.case,'allocated-panel-contract');assert.equal(review.presentation,'neighborhood-list');
      assert.equal(review.effectiveFontPx,7.65);
      for(const field of ['densityRule','preservedState','focusRepair','hostRoute','acceptance'])assert.ok(review[field]&&JSON.stringify(review[field]).length>30,field);
      checks.push('Exact allocated-width arithmetic and compact route','Required state, focus, host-route and acceptance fields');
    }
    results.push({runId:id,strictPassed:strict.passed,artifactPassed:true,checks});
  }catch(error){results.push({runId:id,strictPassed:strict.passed,artifactPassed:false,failure:String(error)});}
}
const output=path.join(root,'artifacts/reviews/target-hosts/contracts');await fs.mkdir(output,{recursive:true});
const report={passed:results.every(row=>row.artifactPassed),results,scope:'Independent focused artifact contracts and manual prose review; no new broad naturalistic cohort or host-paint certification.'};
await fs.writeFile(path.join(output,'review.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
