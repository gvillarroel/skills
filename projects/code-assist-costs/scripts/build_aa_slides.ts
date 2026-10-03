#!/usr/bin/env -S npx tsx
// Node.js >=22; native Slides request generator, standard library only. No target executions.
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve('projects/code-assist-costs/artifacts/aa-ofat');
const input=JSON.parse(fs.readFileSync(path.join(root,'source/deck-input.json'),'utf8'));
const data=JSON.parse(fs.readFileSync(path.join(root,'study-v1/extension/results.json'),'utf8'));
const c=(id,w='short')=>data.core.find(x=>x.scenario===id&&x.workload===w);
const usd=(n,d=2)=>'$'+Number(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const num=(n,d=0)=>Number(n).toLocaleString('en-US',{maximumFractionDigits:d});
const pct=(n,d=1)=>(100*n).toFixed(d)+'%';
const short=c('baseline'),long=c('baseline','long');
const aaURL='https://artificialanalysis.ai/evaluations/terminalbench-v2-1';
const priceURL='https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing';
const notes='Source date: 2026-09-06. Mathematical simulation only; no Pi, Copilot, inference API, or actual modeled tool executions. USD is token usage value before subscription allowances, taxes and human work. Data: projects/code-assist-costs/artifacts/aa-ofat/study-v1/extension/ . Artificial Analysis aggregates: '+aaURL+' . Price schedule: '+priceURL+' . AA pass@1 is not a calibrated production success probability. Mean output is not per-call output. Token SD is not available in the retrieved aggregate; assumed CV scenarios are not empirical confidence intervals.';
const slides=[];
function table(title,subtitle,rows,footer='Inventory: 36 implemented primitive inputs plus 10 unresolved mechanism groups. Not exhaustive.') {slides.push({type:'table',exemplar:'p3',title,subtitle,rows,footer});}
function plain(title,subtitle,leftTitle,left,rightTitle,right,bottom,footer='Published evidence and simulation assumptions are kept separate.'){slides.push({type:'plain',exemplar:'p16',title,subtitle,leftTitle,left,rightTitle,right,bottom,footer});}
function plot(title,subtitle,bars,unit,callout,body,small,footer,extra={}) {slides.push({type:'plot',exemplar:'p4',title,subtitle,bars,unit,callout,body,small,footer,...extra});}
slides.push({type:'cover',exemplar:'p1',title:'What changes the cost\nof code assistance?',subtitle:'A parameter-by-parameter simulation',body:'Frozen baselines, model-specific tokens and success',footer:'Evidence and prices: 6 September 2026\nMathematical models only. No live Pi, Copilot or model runs.'});
table('Parameters first: prompts, tools and cache','Each named intervention gets its own comparison; derived accounting still propagates.',[
['Parameter family','Inputs considered and treatment'],['Prompts','System size; user/background size; tool-schema size. Varied separately.'],['Tool workflow','Call count; batch size; result size; per-tool fee. Task output frozen.'],['Model output','Total tokens; reasoning/answer share; retention. Mean anchored to AA.'],['Cache reuse','Enabled and hit fraction varied; input/read/write prices explicit.'],['Cache lifecycle','TTL, pauses, eviction, prefix order and version churn: folded into hit rate.']]);
table('Parameters first: context, quality and recovery','Do not hide a quality change inside a claimed token saving.',[
['Parameter family','Inputs considered and treatment'],['Context','Initial size; growth; compaction cap; pricing threshold; summary length.'],['Compaction','Summary-call cache; retained prefix; summary fidelity; critical facts.'],['Task success','Per-model pass@1 proxy; task difficulty; domain transfer and task mix.'],['Context rot','Onset; slope; smooth vs cliff link; average vs critical-fact retention.'],['Recovery','Attempt cap; persistent failure; conditional fallback recovery; error loss.']]);
table('Parameters first: price, volume and uncertainty','Reviewed omissions remain visible; more simulations do not remove these gaps.',[
['Parameter family','Inputs considered and treatment'],['Pricing','Input/read/write/output rates; long-tier factors; provider vs harness route.'],['Scale','1,000 and 1,000,000 tasks/month; independent variability; shared shocks.'],['Dispersion','Token CV 0.25 / 0.50 / 1.00; Gamma and lognormal alternatives. Assumed.'],['Cash and capacity','Seats, credits, tax, FX, quotas, latency and infrastructure: not in token ledger.'],['Unresolved quality','Validator errors, tool failures, dependency limits and success-token correlation.']]);
plain('What Artificial Analysis does—and does not—tell us','Terminal-Bench v2.1: 89 tasks, three repeats per task, Terminus 2 harness.',
    'Published aggregates','Pass@1 for a named model and effort\nMean answer + reasoning tokens per task\nMean task cost with input/cache/output split',
    'Not identified here','Production success in Pi or Copilot\nTask-level token SD or token/success covariance\nAn empirical context-rot onset for these models',
    'Use benchmark-specific tokens and success together. The Intelligence Index score is not a success probability.', 'Source: Artificial Analysis Terminal-Bench v2.1 and methodology; retrieved 6 Sep 2026.');
plot('Models do not use the same tokens per task','Published Terminal-Bench output tokens; row labels include pass@1.',data.profiles.map(x=>({label:x.model.replace('GPT-5.6 ','').replace('GPT-6 ','')+' | '+pct(x.pass1),value:x.output_tokens})),
    'Output tokens per benchmark task','6.7× tokens','Luna max uses 24,120 tokens; Astra medium uses 3,617. Prices differ too.',
    'Answer + reasoning. These are whole-task means, not per-call budgets.','Source: AA Terminal-Bench v2.1. Scores are point estimates; small differences are not proved significant.',{format:'number'});
table('Which average should anchor the simulation?','The benchmark mixture changes the mean. Do not treat these columns as interchangeable.',[
['Model / effort','Index weighted mean → Terminal-Bench mean'],...data.profiles.slice(0,3).map(x=>[x.model,num(x.index_mean_tokens)+' → '+num(x.output_tokens)+' output tokens/task']),
['Sol xhigh','10,783 Terminal-Bench tokens/task; no Index mean used here.'],['Choice for this study','Anchor the short case to Luna max Terminal-Bench: 24,120 output tokens.']],
    'Source: AA /models and Terminal-Bench. No total-token / guessed-task-count division was used.');
table('Freeze the baseline before changing anything','The synthetic short ledger is not an attempt to reproduce the AA harness.',[
['Frozen input','Short-workload reference'],['Model and prices','Luna: $0.20 input / $0.02 read / $0.25 write / $1.20 output per 1M tokens.'],['Input structure','4,000 system + 2,000 schema + 1,000 user/background tokens.'],['Tools and output','5 tools × 2,000 result tokens; 6 model calls; 24,120 output tokens total.'],['Cache and quality','First prefix write, subsequent reuse; no compaction; p = 80.90%; 1 attempt.'],['Reference cost',usd(short.attempt_usd,5)+'/attempt = '+usd(short.month_1k_usd)+'/1k tasks = '+usd(short.month_1m_usd,0)+'/1M tasks.']],
    'All workload structure is assumed. Output mean/p are AA proxies. Prices: GitHub Copilot token billing.');
plain('Read every scenario the same way','One changed primitive; the same workload, prices and quality unless explicitly named.',
    'Accounting experiment','Cost = uncached + cache-read + cache-write + output\nEach input token occupies exactly one billing bucket.',
    'Quality-adjusted experiment','Cost per correct task = cohort spend / expected correct completions\nAll failed attempts remain in the numerator.',
    'Output reductions and omitted tools do not automatically preserve quality. Those slides report conditional savings.',
    'Monthly scaling is algebraic. One million tasks is a volume assumption, not one million live executions.');
function coreplot(title,subtitle,ids,labels,callout,body,small,footer,work='short',outcome='attempt_usd',scale=1000,delta=false){
    const b=c('baseline',work)[outcome];
    plot(title,subtitle,ids.map((id,i)=>({label:labels[i],value:(c(id,work)[outcome]-(delta?b:0))*scale})),
        (delta?'Change in ':'')+'USD / '+(scale===1e6?'1M':'1k')+(outcome==='correct_usd'?' correct tasks':' tasks'),callout,body,small,footer,{format:'usd'});
}
coreplot('01 | Add 1,000 system-prompt tokens','Changed: system size only. Frozen: six calls, output, tools, cache and quality.',
    ['system-minus1k','baseline','system-plus1k','system-plus2k'],['3,000 system','4,000 baseline','5,000 system','6,000 system'],
    '+$350 / 1M','One extra 1k prefix block: one write + five reads = $0.00035/task.',
    '+$0.35 per 1k tasks. Local cost elasticity: 0.038.',
    'Short case. Stable prefix, no tier crossing. Quality held fixed; changing instruction content may violate that assumption.','short','attempt_usd',1e6,true);
coreplot('02 | Add 1,000 tool-schema tokens','Changed: tool definitions grow from 2k to 3k. Frozen: number of tools and all calls.',
    ['baseline','schema-plus1k'],['2,000 schema','3,000 schema'],
    '+$350 / 1M','Unused definitions still travel in the prefix. Here they have the same marginal bill as system tokens.',
    'Discovery can reduce schema size, but its own extra calls must be counted.',
    'Short case; stable schema and full reuse. This does not simulate executing any tool.','short','attempt_usd',1e6,true);
coreplot('03 | Add 1,000 user/background tokens','Changed: one initial user/background block. Frozen: all other inputs.',
    ['baseline','prompt-plus1k'],['1,000 background','2,000 background'],
    '+$350 / 1M','The block is introduced once and retained. It is not 1,000 new tokens on every turn.',
    'Token placement and repetition matter more than the field name.',
    'Short case; no assumed semantic benefit or quality penalty.','short','attempt_usd',1e6,true);
coreplot('04 | Use four tools instead of five','Changed: tool count only. Frozen: 24,120 total output tokens, result size, prices and p.',
    ['tools-four','baseline','tools-six'],['4 tools / 5 calls','5 tools / 6 calls','6 tools / 7 calls'],
    '−$976 / 1M','Removing one round saves $0.98 per 1k tasks through less input and replay.',
    'Same-quality savings require the removed operation to be unnecessary.',
    'Output is redistributed across remaining calls. If every operation is required, this is not a valid policy saving.');
coreplot('05 | Halve the size of each tool result','Changed: result payload from 2,000 to 1,000 tokens. Frozen: five tools and total output.',
    ['payload-half','baseline','payload-double'],['1k per tool','2k baseline','4k per tool'],
    '−$1,450 / 1M','Shorter tool results reduce new writes and repeated context reads.',
    'Filtering must preserve the facts needed for success.',
    'Conditional accounting only: p is frozen, so this does not estimate the quality cost of losing evidence.');
coreplot('06 | Batch independent tools into one round','Changed: batch size only. Frozen: all five operations, all results, task output and p.',
    ['baseline','batch-two','batch-five'],['1 per round','2 per round','5 in one round'],
    '−$2,123 / 1M','Five tools in one batch reduce six model calls to two. All five operations remain.',
    'Only applicable when those operations are independent.',
    'Total output is frozen; reductions come from request replay. Latency benefits and orchestration overhead are excluded.');
coreplot('07 | Change cache-hit fraction, nothing else','Changed: reusable-prefix hit fraction. Frozen: token ledger, prices, output and p.',
    ['baseline','cache-90','cache-50','cache-zero'],['100% hits','90% hits','50% hits','0% hits; write'],
    '+$1,647 / 1M','A fall from 100% to 90% raises the short-case bill by 4.49%.',
    'Misses are modeled as writes. Disabling caching entirely is a different policy.',
    'Expected token buckets, not sampled cache events. TTL and prefix churn are mechanisms behind this assumed hit fraction.');
coreplot('08 | Reduce required model output by 20%','Changed: total output requirement. Frozen: p, tools, reasoning share, cache and prices.',
    ['output-half','output-minus20','baseline','output-plus20','output-double'],['50% of mean','80% of mean','100% baseline','120% of mean','200% of mean'],
    '−$6,271 / 1M','20% fewer output tokens save 17.08% of the baseline cost, including answer replay.',
    'Cost elasticity to output requirement is about 0.85 here.',
    'This is a hypothetical efficiency gain at fixed p, not proof that setting a lower max-token cap preserves success.');
coreplot('09 | Change success probability, not token use','Changed: p only. Frozen: cost per attempt, output, cache, workload and one attempt.',
    ['p-60','p-70','baseline','p-90','p-95'],['p = 60%','p = 70%','p = 80.90%','p = 90%','p = 95%'],
    '$61 → $39','Spend per 1k correct tasks falls as p increases from 60% to 95%.',
    'Cost per submitted task stays $36.70 / 1k throughout.',
    'C/p has elasticity −1 with respect to p when C is fixed. A real intelligence change can also alter tokens and prices.','short','correct_usd');
const spread=data.spread.filter(x=>x.model===data.profiles[0].model&&x.seed===20260906);
plot('10 | Change token dispersion, not the mean','Changed: assumed CV = SD / mean. Frozen: Luna mean 24,120 tokens, p and input ledger.',
    spread.map(x=>({label:'CV '+x.cv.toFixed(2)+' | SD '+num(x.assumed_sd),value:x.p95})),
    'Simulated task output P95, tokens','SD is assumed','The same mean supports many different spreads. We test CV 0.25, 0.50 and 1.00.',
    'Gamma is positive and skewed; lognormal is a tested rival.',
    '20,000 draws per cell, two seeds. P95 is a conditional predictive quantile—not a confidence interval on AA. ',{format:'number'});
const month=data.monthly.filter(x=>x.tasks===1000&&x.seed===20260906);
plot('11 | More token variance widens the budget margin','Changed: token CV only. Frozen: 1k tasks, mean tokens, p and all input billing.',
    month.map(x=>({label:'CV '+x.cv.toFixed(2),value:x.p95})),
    'Monthly P95 USD; mean is $36.70','P95 $37–38','Mean stays $36.70. CV 0.25 → 1.00 raises P95 from $37.08 to $38.23.',
    'IID averaging is optimistic when an entire month becomes harder.',
    'Only output billing varies in this extension; input replay, context thresholds and success are deliberately frozen.');
coreplot('12 | Change the maximum number of attempts','Changed: attempt cap only. Frozen: per-attempt p and cost; independent failures.',
    ['baseline','retry-two','retry-three'],['1 attempt','Up to 2','Up to 3'],
    '80.9% → 99.3%','More attempts improve completion and increase spend per submitted task.',
    'Under IID retries at equal cost, cohort cost per correct task stays C/p.',
    'Retries stop after the first success. A retry rebuilds the same costed attempt; validator assumed perfect.','short','submitted_usd');
plot('13 | Change retry persistence, not the retry cap','Changed: failure correlation mixture. Frozen: three attempts, marginal p and per-attempt cost.',
    data.retries.filter(x=>x.cap===3).map(x=>({label:'Persistence '+x.rho+' | '+pct(x.completion)+' success',value:1000*x.correct_usd})),
    'USD per 1k correct tasks','Retries can fail','Perfect persistence returns completion to 80.9%, while repeated failures still cost money.',
    'Repeated attempts are not automatically independent evidence.',
    'Exact persistent-failure mixture, not a measured correlation. Binary-sequence oracles and Bernoulli MC checked.');
coreplot('14 | Change only the long-session compaction cap','Long case: 39 tools × 20k results; 40 calls; 160k output. Quality frozen.',
    ['baseline','cap-100k','cap-180k','cap-200k','cap-272k','cap-400k'],['No cap: 875k peak','100k cap','180k cap','200k cap','272k cap','400k cap'],
    '−40.7% at 180k','1k long tasks cost $1,338 without a cap, $793 at 180k and $973 at 200k.',
    'A 200k trigger can make the summary call itself cross the 200k tariff.',
    '20k-token summary; cold summarizer and rebuild; unchanged total main output. This is not a universal optimal cap.','long');
const cache=data.caching.filter(x=>x.cap===200000&&x.retain_prefix===0);
plot('15 | Change only the summarizer’s cache access','Frozen: long case, 200k cap, 20k summary, cold rebuilt context and perfect fidelity.',
    cache.map(x=>({label:x.compactor_cache?'Reuse eligible prefix':'Cold summary input',value:x.attempt_usd*1000})),
    'USD per 1k long tasks',pct(1-cache[1].attempt_usd/cache[0].attempt_usd)+' less',
    'The summarization request is a paid call. Its own input-cache behavior can change the result.',
    'Post-compaction prefix retention is tested separately in the data.',
    'Only summarizer cache access changes here. No blanket claim that compaction always destroys every cache segment.');
plot('16 | Change context-rot severity, not the ledger','Changed: assumed decay slope. Frozen: no cap, 100k onset, p0 and identical long-task spend.',
    ['baseline','rot-mild','rot-severe'].map((id,i)=>({label:['No decay','Mild slope 0.2','Severe slope 1.0'][i],value:100*c(id,'long').completion})),
    'Task completion probability, %','$1,338 fixed','The same 1k-task bill yields 80.9%, 67.5% or 10.7% completion under these assumptions.',
    'The slope is not fitted to AA. No universal failure-onset claim.',
    'Log-odds hinge with average excess context exposure. Cliff and alternative onset mechanisms are separate challenges.',{format:'percent100'});
const qf=data.quality.filter(x=>x.onset===100000&&x.beta===.2&&x.quality_link==='smooth'&&x.fidelity_link==='critical'&&x.cap===180000);
plot('17 | Change summary fidelity, not the cap','Changed: fact-retention probability. Frozen: 180k cap, five compactions, ten critical facts.',
    qf.slice(0,3).map(x=>({label:'Fact retention '+pct(x.summary_fidelity),value:100*x.completion})),
    'Task completion probability, %','80.2% → 23.8%',
    'At 95% per-fact retention, repeated summaries can erase the quality-adjusted cost advantage.',
    'All-critical-facts survival is a structural challenge, not measured behavior.',
    'Fixed mild rot. Ten facts × five compactions feed an odds penalty. Average-fidelity link is a separate rival.',{format:'percent100'});
plot('18 | Change the reasoning-effort configuration','Published Sol configurations: price family fixed; output and success may both change.',
    [data.profiles[2],data.profiles[3]].map(x=>({label:x.model.replace('GPT-5.6 ','')+' | '+pct(x.pass1),value:x.cost_usd*1000})),
    'AA USD per 1k benchmark tasks','xhigh: −29.7%',
    'Sol xhigh: 10,783 output tokens and 89.51% pass@1. Max: 14,684 tokens and 88.01%.',
    'This is a bundled configuration comparison—not a pure causal token test.',
    'Source: AA Terminal-Bench. The 1.50 percentage-point score gap has no paired significance claim.');
plot('19 | Compare complete model profiles','Each profile carries its own observed mean output, task cost and pass@1 proxy.',
    data.profiles.map(x=>({label:x.model.replace('GPT-5.6 ','').replace('GPT-6 ','')+' | '+pct(x.pass1),value:x.cost_per_success_proxy*1000})),
    'AA-derived USD per 1k correct tasks','Luna: $65.42',
    'Luna is cheapest here, but its 80.9% pass@1 fails an assumed 85% or 95% single-attempt floor.',
    'At an 85% floor, Sol xhigh is cheapest among these six point estimates.',
    'Cohort ratio = published average task cost / pass@1. Not a measured production invoice or causal model ranking.');
plot('20 | Change only fallback recovery probability','Frozen: Luna first, Sol xhigh after detected failure; same costs and perfect validation.',
    data.routing.map(x=>({label:'Recovery '+pct(x.recovery),value:100*x.success})),
    'Combined task success, %','Need ≥73.8%',
    'For 95% overall success, Sol must recover at least 73.8% of Luna failures. AA does not report that conditional rate.',
    'Spend stays $125.91 / 1k tasks in this proxy model.',
    'Recovery is conditional on first-model failure. Do not substitute Sol’s marginal benchmark score without labeling the assumption.',{format:'percent100'});
plot('Local savings: same baseline, different levers','Summary of independent interventions—not a combined savings claim.',
    [['Output −20%','output-minus20'],['Five-tool batch','batch-five'],['Tool results −50%','payload-half'],['One fewer tool','tools-four'],['System −1k','system-minus1k']].map(([label,id])=>({label,value:(short.attempt_usd-c(id).attempt_usd)*1e6})),
    'USD saved per 1M short tasks','Quality is frozen',
    'Output economy dominates this short ledger. Cache and context control become much larger in long sessions.',
    'Effects interact; do not add these savings without a new joint scenario.',
    'One-factor local contrasts. Global optimality and operational task equivalence are not established.');
plain('Choose parameters against a quality requirement','There is no universally cheapest configuration once failure has a cost.',
    'Low-risk, high-volume work','Start with the cheapest adequate model profile.\nReduce irrelevant output and tool payload.\nKeep stable prefixes; batch independent work.',
    'Hard or long-running work','Select against a minimum completion rate.\nTest caps with paid compaction and fact loss.\nUse conditional recovery, not marginal scores.',
    'Next evidence that matters: task-level tokens + success, cache traces and recovery on failed tasks—from existing data only.',
    '76 exact OFAT cells, 1,152 context-quality challenge cells; 36 active-input tests; uncertainty remains conditional.');
plain('Sources, reproducibility and limits','Updated study: AA-anchored OFAT, 6 September 2026.',
    'Published evidence','Artificial Analysis: Terminal-Bench v2.1\nArtificial Analysis: model and Index token means\nGitHub: Copilot token rates and thresholds',
    'Reproducible simulation','CSV: per-scenario costs and request ledgers\nSQLite: quality, retries and token uncertainty\nSeeded Gamma/lognormal and exact audit reports',
    'No empirical SD was manufactured. No actual harness, model or modeled tool was executed. Unknown factors may remain.',
    'Source URLs and detailed assumptions are in speaker notes. Core audit passed with zero failed or invalid runs.');

// Native template following: duplicate rich exemplars, keep all text/table objects,
// explicitly replace the p4 chart image with editable native chart shapes.
const requests=[];const mapping=[];let current=[];
const rgb=h=>({red:parseInt(h.slice(1,3),16)/255,green:parseInt(h.slice(3,5),16)/255,blue:parseInt(h.slice(5,7),16)/255});
const colors={navy:'#112D3B',teal:'#087F8C',amber:'#B65B19',gray:'#536774',light:'#DDE7E9'};
function replace(id,text,source,cell){
  const cellLocation=cell?{rowIndex:cell[0],columnIndex:cell[1]}:undefined;
  current.push({deleteText:{objectId:id,textRange:{type:'ALL'},...(cell?{cellLocation}:{})}},
    {insertText:{objectId:id,text,insertionIndex:0,...(cell?{cellLocation}:{})}});
  const elements=source?.textElements||source?.shape?.text?.textElements||[];
  const styles=elements.filter(x=>x.textRun&&x.textRun.content.trim()).map(x=>x.textRun.style);
  const style=styles[0]||{fontFamily:'Arial',fontSize:{magnitude:18.75,unit:'PT'},foregroundColor:{opaqueColor:{rgbColor:rgb(colors.navy)}}};
  let start=0;
  text.split('\n').forEach((para,i)=>{
    if(para.length)current.push({updateTextStyle:{objectId:id,textRange:{type:'FIXED_RANGE',startIndex:start,endIndex:start+para.length},style:styles[i]||style,fields:Object.keys(styles[i]||style).join(','),...(cell?{cellLocation}:{})}});
    start+=para.length+1;
  });
}
let newCounter=0;
function shape(slide,x,y,w,h,text='',size=15,color=colors.navy,fill=null,bold=false){
  const id=slide+'_chart_'+newCounter++;
  current.push({createShape:{objectId:id,shapeType:fill?'RECTANGLE':'TEXT_BOX',elementProperties:{pageObjectId:slide,size:{width:{magnitude:w,unit:'PT'},height:{magnitude:h,unit:'PT'}},transform:{scaleX:1,scaleY:1,translateX:x,translateY:y,unit:'PT'}}}});
  current.push({updateShapeProperties:{objectId:id,shapeProperties:{outline:{propertyState:'NOT_RENDERED'},...(fill?{shapeBackgroundFill:{solidFill:{color:{rgbColor:rgb(fill)},alpha:1}}}:{}),contentAlignment:'MIDDLE'},fields:fill?'outline,shapeBackgroundFill,contentAlignment':'outline,contentAlignment'}});
  if(text){current.push({insertText:{objectId:id,text,insertionIndex:0}},{updateTextStyle:{objectId:id,textRange:{type:'ALL'},style:{fontFamily:'Arial',fontSize:{magnitude:size,unit:'PT'},foregroundColor:{opaqueColor:{rgbColor:rgb(color)}},bold},fields:'fontFamily,fontSize,foregroundColor,bold'}},{updateParagraphStyle:{objectId:id,textRange:{type:'ALL'},style:{spaceAbove:{magnitude:0,unit:'PT'},spaceBelow:{magnitude:0,unit:'PT'},lineSpacing:100},fields:'spaceAbove,spaceBelow,lineSpacing'}});}
  return id;
}
function bars(slide,s){
  const min=Math.min(0,...s.bars.map(x=>x.value)),max=Math.max(1e-9,...s.bars.map(x=>x.value));
  const left=225,right=605,width=right-left,top=209,bottom=452;
  const scale=x=>left+(x-min)/(max-min)*width;
  shape(slide,48,168,620,28,s.unit,15,colors.gray);
  for(let i=0;i<=4;i++){
    const value=min+(max-min)*i/4,x=scale(value);
    shape(slide,x,205,.6,249,'',12,colors.gray,colors.light);
    const label=s.format==='percent100'?value.toFixed(0)+'%':s.format==='number'?num(value):usd(value,Math.abs(max)<100?0:0);
    shape(slide,x-25,459,80,20,label,11.5,colors.gray);
  }
  const step=(bottom-top)/s.bars.length;
  for(const [i,b] of s.bars.entries()){
    const y=top+i*step+5;
    const labelId=shape(slide,48,y-4,170,step-2,b.label,14.25,colors.navy);
    current.push({updateShapeProperties:{objectId:labelId,shapeProperties:{contentAlignment:'TOP'},fields:'contentAlignment'}});
    const zero=scale(0),x=scale(b.value);
    if(Math.abs(b.value)>1e-9)shape(slide,Math.min(x,zero),y+4,Math.max(.5,Math.abs(x-zero)),Math.min(22,step-12),'',12,colors.gray,b.value<0?colors.amber:colors.teal);
    const label=s.format==='percent100'?b.value.toFixed(1)+'%':s.format==='number'?num(b.value):usd(b.value,Math.abs(max)<100?2:0);
    shape(slide,610,y-1,82,28,label,14.25,colors.navy,null,true);
  }
}
for(const [i,s] of slides.entries()){
  current=[];const sid='aa_'+String(i+1).padStart(2,'0');
  const original=input.slides.find(x=>x.objectId===s.exemplar);
  const ids={[original.objectId]:sid};for(const [ei,e]of original.pageElements.entries())ids[e.objectId]=sid+'_e'+ei;
  current.push({duplicateObject:{objectId:original.objectId,objectIds:ids}});
  const textEls=original.pageElements.filter(e=>e.shape);
  const mapText=(old,text)=>replace(ids[old.objectId],text,old);
  if(s.type==='cover')textEls.forEach((e,j)=>mapText(e,[s.title,s.subtitle,s.body,s.footer][j]));
  else{
    for(const [j,value]of [s.title,s.subtitle,s.footer,String(i+1).padStart(2,'0')].entries())mapText(textEls[j],value);
    if(s.type==='table'){
      const table=original.pageElements.find(e=>e.table);
      for(let r=0;r<6;r++)for(let col=0;col<2;col++)replace(ids[table.objectId],s.rows[r][col],table.table.tableRows[r].tableCells[col].text,[r,col]);
    } else if(s.type==='plain'){
      [s.leftTitle,s.left,s.rightTitle,s.right,s.bottom].forEach((value,j)=>mapText(textEls[j+4],value));
    } else {
      [s.callout,s.body,s.small].forEach((value,j)=>mapText(textEls[j+4],value));
      const img=original.pageElements.find(e=>e.image);
      current.push({deleteObject:{objectId:ids[img.objectId]}});
      bars(sid,s);
    }
  }
  mapping.push({slideId:sid,narrativeRole:s.type,exemplar:s.exemplar,method:'duplicate-and-populate',media:s.type==='plot'?'Delete mapped chart image; replace with native editable data bars.':'No media left unmapped.',title:s.title,notes:notes+'\n\n'+s.title+'\n'+s.subtitle+'\n'+(s.footer||'')});
  requests.push({slideId:sid,requests:current});
}
fs.mkdirSync(path.join(root,'slides'),{recursive:true});
fs.writeFileSync(path.join(root,'slides/build-requests.json'),JSON.stringify(requests));
fs.writeFileSync(path.join(root,'slides/narrative-map.json'),JSON.stringify(mapping,null,2));
fs.writeFileSync(path.join(root,'slides/content.json'),JSON.stringify(slides,null,2));
console.log(JSON.stringify({slides:slides.length,requests:requests.reduce((a,b)=>a+b.requests.length,0),ids:mapping.map(x=>x.slideId)}));
