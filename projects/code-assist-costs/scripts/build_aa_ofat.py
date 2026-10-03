#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze a new AA-anchored offline study; read published evidence, never targets."""
import csv
import json
import shutil
from pathlib import Path

ROOT=Path('projects/code-assist-costs')
OUT=ROOT/'artifacts/aa-ofat/study-v1'
AA=ROOT/'artifacts/aa-ofat/source/aa-datasets.json'
TEMPLATE=Path('.agents/skills/simulation-data-lab/assets/templates/experiment.json')
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')

def main():
    if OUT.exists(): raise SystemExit('A fresh study path is required.')
    aa=json.loads(AA.read_text(encoding='utf8'))
    datasets={d['name']:d['data'] for b in aa.values() for d in b['datasets']}
    chosen=['GPT-5.6 Luna (max)','GPT-5.6 Terra (max)','GPT-5.6 Sol (max)',
            'GPT-5.6 Sol (xhigh)','GPT-6 Astra (medium)','GPT-6 Astra (high)']
    profiles=[]
    def row(name,label): return next((r for r in datasets[name] if r['label']==label),None)
    for label in chosen:
        t=row('Terminal-Bench v2.1: Output Tokens per Task',label)
        c=row('Terminal-Bench v2.1: Cost per Task',label)
        a=row('Terminal-Bench v2.1: Score',label)
        idx=row('Output Tokens per Intelligence Index Task',label)
        cost=sum(c[x] for x in ['input','cacheHit','cacheWrite','answer','reasoning'])
        profiles.append(dict(model=label,benchmark='Terminal-Bench v2.1',tasks=89,repeats_per_task=3,
            pass1=a['Terminal-Bench v2.1'],answer_tokens=t['answer'],reasoning_tokens=t['reasoning'],
            output_tokens=t['answer']+t['reasoning'],cost_usd=cost,cost_per_success_proxy=cost/a['Terminal-Bench v2.1'],
            index_mean_tokens=None if idx is None else idx['answer']+idx['reasoning'],
            source_type='published-aa-aggregate',source_url='https://artificialanalysis.ai/evaluations/terminalbench-v2-1',
            variance_status='not-reported-in-retrieved-aggregate',transfer='not-validated-for-Pi-or-Copilot'))
    OUT.mkdir(parents=True)
    dump(OUT/'aa-profiles.json',profiles)
    with (OUT/'aa-profiles.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(profiles[0]));w.writeheader();w.writerows(profiles)
    luna=profiles[0]
    base=dict(system_tokens=4000,schema_tokens=2000,user_delta=0,tool_delta=0,batch_size=1,
        payload_factor=1,output_factor=1,reasoning_share=luna['reasoning_tokens']/luna['output_tokens'],
        cache_enabled=1,cache_hit=1,compact_cap=0,summary_tokens=20000,compactor_cache=0,retain_prefix=0,
        summary_fidelity=1,rot_onset=100000,rot_beta=0,quality_link='smooth',fidelity_link='average',critical_facts=10,
        success_probability=luna['pass1'],attempt_cap=1,failure_rho=0,failure_loss=0,tool_fee=0,
        input_price=.2,read_price=.02,write_price=.25,output_price=1.2,
        tier_threshold=200000,long_input_factor=2,long_output_factor=1.5)
    changes={
        'system-minus1k':('system_tokens',3000),'system-plus1k':('system_tokens',5000),'system-plus2k':('system_tokens',6000),
        'schema-plus1k':('schema_tokens',3000),'prompt-plus1k':('user_delta',1000),
        'tools-four':('tool_delta',-1),'tools-six':('tool_delta',1),'batch-two':('batch_size',2),'batch-five':('batch_size',5),
        'payload-half':('payload_factor',.5),'payload-double':('payload_factor',2),
        'output-half':('output_factor',.5),'output-minus20':('output_factor',.8),'output-plus20':('output_factor',1.2),'output-double':('output_factor',2),
        'cache-90':('cache_hit',.9),'cache-50':('cache_hit',.5),'cache-zero':('cache_hit',0),'cache-disabled':('cache_enabled',0),
        'cap-100k':('compact_cap',100000),'cap-180k':('compact_cap',180000),'cap-200k':('compact_cap',200000),
        'cap-272k':('compact_cap',272000),'cap-400k':('compact_cap',400000),
        'p-60':('success_probability',.6),'p-70':('success_probability',.7),'p-90':('success_probability',.9),'p-95':('success_probability',.95),
        'retry-two':('attempt_cap',2),'retry-three':('attempt_cap',3),
        'rot-mild':('rot_beta',.2),'rot-severe':('rot_beta',1),
        'direct-threshold':('tier_threshold',272000),'tool-fee-cent':('tool_fee',.01),
        'read-price-double':('read_price',.04),'write-price-double':('write_price',.5),'output-price-double':('output_price',2.4),
    }
    units={k:('token' if k in ['system_tokens','schema_tokens','user_delta','summary_tokens','rot_onset','compact_cap','tier_threshold']
        else 'USD/MTok' if k.endswith('_price') else 'USD/task' if k=='failure_loss' else 'USD/tool' if k=='tool_fee' else '1') for k in base}
    def param(k,v):return dict(name=k,value=v,unit=units.get(k,'token' if k in ['background_tokens','tool_payload','base_output'] else '1'),
        sourceType='literature' if k.endswith('_price') or k in ['success_probability','base_output','reasoning_share','tier_threshold','long_input_factor','long_output_factor'] else 'assumed',
        description='AA published aggregate used as an unvalidated task proxy.' if k in ['success_probability','base_output','reasoning_share'] else 'Frozen input; see source and scope notes.')
    scenarios=[dict(scenarioId='baseline',label='Baseline',description='Frozen reference',parameters=[param(k,v) for k,v in base.items()])]
    for sid,(key,value) in changes.items():
        p=base|{key:value};assert sum(p[k]!=base[k] for k in base)==1
        scenarios.append(dict(scenarioId=sid,label=sid,description=f'Only {key} changes; all other primitive parameters frozen. Derived ledger may change.',parameters=[param(k,v) for k,v in p.items()]))
    design=[dict(designPointId='short',description='Six calls / five tools, AA Luna output mean; hypothetical harness ledger.',parameters=[param(k,v) for k,v in dict(background_tokens=1000,base_tools=5,tool_payload=2000,base_output=luna['output_tokens']).items()]),
        dict(designPointId='long',description='Forty calls / 39 tools; hypothetical long workload, not an AA observation.',parameters=[param(k,v)|{'sourceType':'assumed'} for k,v in dict(background_tokens=25000,base_tools=39,tool_payload=20000,base_output=160000).items()])]
    spec=json.loads(TEMPLATE.read_text(encoding='utf8'))
    spec.update(experimentId='aa-ofat-20260906-v1',title='AA-anchored one-factor code-assist cost simulation',
        description='Exact mathematical ledgers, not target execution. AA aggregate output and success proxies are not production calibration.',
        phase='exploratory',paradigm='custom',rootSeed=20260906,uncertaintyMode='deterministic',seedPolicy='independent-by-run',replications=1,
        scenarios=scenarios,designPoints=design)
    outcomes=['attempt_usd','submitted_usd','completion','correct_usd','completion_defined','attempts','month_1k_usd','month_1m_usd','loss_usd','input_usd','output_usd','max_context','compactions','main_calls','exposure','fidelity','tool_calls']
    spec['outcomes']=[dict(name=k,unit='USD' if 'usd' in k else 'token' if k=='max_context' else '1',description=k.replace('_',' ')) for k in outcomes]
    spec['assumptions']=[dict(assumptionId='proxy',statement='AA pass@1 and mean output are task-distribution proxies, not validation of this synthetic harness. No empirical token SD is inferred.',sourceType='assumed'),
        dict(assumptionId='ledger',statement='Output total is frozen for tool-count and batching changes. Reasoning does not persist; answer tokens persist. New cacheable input is written once. No tool billing or quality effect unless varied.',sourceType='assumed'),
        dict(assumptionId='quality',statement='Success transfer, rotation onset/slope, summary fidelity, retry independence and losses are assumptions. Prices are GitHub token value, not an invoice.',sourceType='assumed')]
    spec['hypotheses']=[]
    for sid in ['system-plus1k','tools-four','payload-half','output-minus20','cache-90','cap-200k']:
        decrease=sid in ['tools-four','payload-half','output-minus20','cap-200k']
        spec['hypotheses'].append(dict(hypothesisId='h-'+sid,claim=f'{sid} changes attempt cost in the declared direction across both workloads.',claimScope='conditional-real-world',assumptionIds=['proxy','ledger','quality'],externalValidationRequired=True,
            outcome='attempt_usd',scenarioIds=['baseline',sid],estimand=f'{sid} minus baseline cost per attempt',
            analysis=dict(kind='scenario-contrast',estimator='mean-difference',baselineScenarioId='baseline',comparisonScenarioId=sid,primaryDesignPointIds=['short'],challengeDesignPointIds=['long'],pairing='deterministic',intervalMethod='none',intervalLevel=None,aggregationRule='all-design-points'),
            practicalThreshold=dict(value=0,unit='USD',operator='le' if decrease else 'ge'),decisionRule='Evaluate the exact signed contrast against zero at both design points; equality is allowed, not a meaningful saving.',falsificationRule='Long workloads and tier boundaries may reverse or saturate the short-workload effect.'))
    vr=spec['extensions']['simulation-data-lab']['variableReview']
    vr['scope']='One primitive intervention at a time. Baselines are hypothetical; wider omissions are visible, not claimed irrelevant.'
    vr['variables']=[]
    for k in list(base)+['background_tokens','base_tools','tool_payload','base_output']:
        vr['variables'].append(dict(variableId=k.replace('_','-'),label=k.replace('_',' ').title(),role='control',unit=units.get(k,'token' if k!='base_tools' else '1'),treatment='modeled',parameterNames=[k],affectsOutcomes=['attempt_usd','completion'],mechanism='Changes the request ledger, billing partition, or conditional completion mechanism as named.',evidence='GitHub rates and dated AA aggregates for literature inputs; other values are assumptions.',decisionImpact='high',reason='Explicit input in frozen scenario/design matrix.',nextCheck='Perturb this input in an active regime and compare the ledger or appropriate derived outcome.'))
    omitted=[('token-dispersion','Gamma CV 0.25/0.5/1 and lognormal rival in a separate extension; AA SD unidentified.'),
        ('task-selection','Difficulty, task family, language, repository size and benchmark transfer can change mean tokens and success.'),
        ('success-token-dependence','Failures may consume systematically more tokens; aggregate AA means do not identify the joint distribution.'),
        ('cache-lifecycle','TTL, pause duration, eviction, prefix ordering, version churn, minimum cache blocks and cross-session reuse feed cache-hit probability; not individually calibrated.'),
        ('tool-behavior','Errors, invalid arguments, retries, truncation, irrelevant results, deduplication and sequential dependencies may change both tokens and success.'),
        ('runtime-capacity','Concurrency, queues, TPM/RPM, TTFT, timeouts, sandbox minutes and human waiting cost require workload evidence.'),
        ('billing-contract','Seats, credits, legacy plans, discounts, taxes, FX, routing markups and batch discounts distinguish token value from invoice.'),
        ('validator-error','False acceptance and rejection change retry reach and escaped-failure losses; a perfect validator is only an extension assumption.'),
        ('context-structure','Fact position, distractors, instruction conflicts, retrieval, memory structure and summary criticality differ from raw context length.'),
        ('shared-shocks','Monthly task mix, correlated incidents, model/provider revisions and outages do not average away with volume.')]
    for k,why in omitted:
        vr['variables'].append(dict(variableId=k,label=k.replace('-',' ').title(),role='structural',unit='1',treatment='unresolved',parameterNames=[],affectsOutcomes=['attempt_usd','completion'],mechanism=why,evidence='No matching existing production trace; no live collection authorized.',decisionImpact='high',reason='Reported separately or explicitly outside the one-factor ledger.',nextCheck='Inspect existing evidence or a fresh labeled mathematical challenge; never launch the target.'))
    for v in vr['variables']:
        if v['parameterNames']: v['affectsOutcomes']=outcomes
    for arm in scenarios[1:]:
        key=changes[arm['scenarioId']][0]
        next(p for p in arm['parameters'] if p['name']==key)['sourceType']='assumed'
    vr['interactions']=[dict(interactionId='context-cache-tariff',variableIds=['system-tokens','compact-cap','cache-hit','tier-threshold'],treatment='modeled',decisionImpact='high',mechanism='Request length selects the tariff, affects replay, and triggers paid compaction.',reason='Derived consequences remain active even in OFAT.',nextCheck='Inspect long workload ledger and 200k boundary.')]
    dims=['outcome-backtrace','lifecycle','dependencies-and-feedback','heterogeneity-and-selection','time-and-scale','constraints-and-accounting','rival-mechanisms','evidence-gaps']
    vr['coverageChecks']=[dict(dimension=d,status='reviewed',variableIds=[v['variableId'] for v in vr['variables']],note='Inventory covers this dimension; unresolved variables restrict real-world inference. See method and extension tests.') for d in dims]
    vr['openQuestions']=['Which task distribution matches your workload?','What are model-specific token SD and success-token dependence?','What failure loss and quality floor should govern routing?']
    spec['extensions']['simulation-data-lab']['uncertaintyContract']=dict(systemVariability='Exact expected ledger core; separate Gamma/lognormal synthetic token extension.',simulationError='None in exact core; empirical MCSE in independently seeded extension.',parameterUncertainty='AA-to-task transfer, token CV, success and context-quality scenarios; not confidence intervals.',structuralUncertainty='Cache model, retry persistence, critical fact loss and common shocks remain conditional.',predictiveScope='Illustrative task/month cost, not an observed Pi/Copilot forecast.')
    spec['extensions']['aa-ofat']=dict(changes=changes,sourceHashes={k:v['sha256'] for k,v in aa.items()},
        extensionPlan=dict(tokenCV=[.25,.5,1],months=[1000,1000000],replications=20000,seeds=[20260906,20260907],
            successDelta=[-.2,-.1,0,.1],retryRho=[0,.5,1],recovery=[0,.2,.5,.8,.895131086142322],
            rotBeta=[0,.2,1],rotOnset=[0,100000,200000,1000000],fidelity=[1,.99,.95,.8],
            fidelityLinks=['average','critical'],qualityLinks=['smooth','cliff'],cap=[0,100000,180000,200000,272000,400000],
            compactorCache=[0,1],postPrefix=[0,1],loss=[0,.1,1,10],sharedCV=[0,.1,.3]))
    dump(OUT/'experiment.json',spec)
    shutil.copyfile(ROOT/'source/aa-ofat-model.py',OUT/'model.py')
    print(json.dumps(dict(bundle=str(OUT),profiles=len(profiles),scenarios=len(scenarios),designPoints=len(design),plannedRuns=len(scenarios)*len(design),candidateVariables=len(vr['variables']))))

if __name__=='__main__':main()
