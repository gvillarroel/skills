#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.3,<3"]
# ///
"""Verify pure mathematics, then produce separate planned sensitivity extensions."""
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import sqlite3
import sys
from pathlib import Path
import numpy as np

ROOT=Path('projects/code-assist-costs/artifacts/aa-ofat/study-v1')
S=json.loads((ROOT/'experiment.json').read_text())
sp=importlib.util.spec_from_file_location('model',ROOT/'model.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
base={x['name']:x['value'] for x in S['scenarios'][0]['parameters']}
design={d['designPointId']:{x['name']:x['value'] for x in d['parameters']} for d in S['designPoints']}
profiles=json.loads((ROOT/'aa-profiles.json').read_text())
plan=S['extensions']['aa-ofat']['extensionPlan']
def save(name,rows):
    p=ROOT/'extension'/name;p.parent.mkdir(exist_ok=True)
    with p.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def writejson(name,data):(ROOT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')

def verify():
    tests=[]
    p=base|design['short']
    oracle=p|dict(system_tokens=1000,schema_tokens=0,background_tokens=0,base_tools=0,base_output=0)
    assert abs(M.ledger(oracle)[1]['attempt_usd']-.00025)<1e-12
    tests.append('one-write-hand-oracle')
    for q,k,rho in itertools.product([0,.2,.5,.9,1],[1,2,3],[0,.5,1]):
        expected_c=expected_n=0
        for seq in itertools.product([0,1],repeat=k):
            mass=(1-rho)*math.prod(q if bit else 1-q for bit in seq)
            if all(seq):mass+=rho*q
            if not any(seq):mass+=rho*(1-q)
            expected_c+=mass*int(any(seq));expected_n+=mass*(seq.index(1)+1 if any(seq) else k)
        c,n=M.retry(q,k,rho)
        assert abs(c-expected_c)<1e-12 and abs(n-expected_n)<1e-12
    tests.append('45-independent-binary-sequence-retry-oracles')
    delta=M.ledger(p|{'system_tokens':5000})[1]['attempt_usd']-M.ledger(p)[1]['attempt_usd']
    assert abs(delta-1000*(.25+5*.02)/1e6)<1e-12
    tests.append('system-prefix-marginal-oracle')
    active=base|design['long']|dict(compact_cap=180000,summary_fidelity=.95,rot_beta=.2,attempt_cap=3,failure_rho=.3)
    variants=dict(system_tokens=5000,schema_tokens=3000,user_delta=1000,tool_delta=-1,batch_size=2,payload_factor=.5,output_factor=.8,
        reasoning_share=.2,cache_enabled=0,cache_hit=.5,compact_cap=100000,summary_tokens=10000,compactor_cache=1,retain_prefix=1,
        summary_fidelity=.8,rot_onset=0,rot_beta=1,quality_link='cliff',fidelity_link='critical',critical_facts=15,
        success_probability=.6,attempt_cap=2,failure_rho=1,failure_loss=10,tool_fee=.01,input_price=.4,read_price=.04,
        write_price=.5,output_price=2.4,tier_threshold=100000,long_input_factor=3,long_output_factor=2,
        background_tokens=50000,base_tools=30,tool_payload=10000,base_output=80000)
    for key,value in variants.items():
        p0=active.copy()
        if key=='critical_facts':p0['fidelity_link']='critical'
        if key in ['long_input_factor','long_output_factor']:p0['compact_cap']=0
        a=M.ledger(p0)[1];b=M.ledger(p0|{key:value})[1]
        assert a!=b,key
    tests.append(f'{len(variants)}-active-parameter-perturbations')
    for d in design.values():
        for sc in S['scenarios']:
            p={x['name']:x['value'] for x in sc['parameters']}|d
            r=M.simulate({'parameters':p})
            assert all(x['status']=='pass' for x in r['diagnostics'])
    tests.append('76-preflight-ledger-invariants')
    writejson('preflight-tests.json',{'ok':True,'tests':tests,'target_executions':0})
    print(json.dumps({'preflight':'pass','tests':tests}))

def analyze():
    if (ROOT/'extension').exists():raise SystemExit('Fresh extension output required.')
    (ROOT/'extension').mkdir()
    # Every core scenario differs in exactly one primitive from its reference.
    core=[];ledgers=[]
    for d,dp in design.items():
        for sc in S['scenarios']:
            params={x['name']:x['value'] for x in sc['parameters']}
            changed=[k for k in base if params[k]!=base[k]]
            assert len(changed)==(sc['scenarioId']!='baseline')
            rows,o=M.ledger(params|dp)
            core.append(dict(scenario=sc['scenarioId'],workload=d,changed=','.join(changed),source_type='simulated',**o))
            ledgers.extend(dict(scenario=sc['scenarioId'],workload=d,request=i,source_type='simulated',**row) for i,row in enumerate(rows))
    save('ofat.csv',core);save('ledger.csv',ledgers)
    # Independently check persisted runner outcomes against analytical recalculation.
    runs={r['run_id']:r for r in csv.DictReader((ROOT/'data/runs.csv').open())}
    idx={(r['scenario'],r['workload']):r for r in core}
    for o in csv.DictReader((ROOT/'data/outcomes.csv').open()):
        r=runs[o['run_id']];expected=idx[r['scenario_id'],r['design_point_id']][o['outcome_name']]
        assert abs(float(o['value'])-expected)<1e-9
    short=idx['baseline','short'];long=idx['baseline','long']
    # CV changes only the final-output billing component. Input ledger and p remain frozen.
    # Gamma(shape=1/CV^2, scale=mean*CV^2) has exactly the specified mean and SD.
    spread=[];monthly=[];predictive=[];verification=[]
    for mi,model in enumerate(profiles):
        mu=model['output_tokens']
        for cv in plan['tokenCV']:
            for seed in plan['seeds']:
                rng=np.random.default_rng(np.random.SeedSequence([seed,mi,int(cv*100),'1'.__len__()]))
                x=rng.gamma(1/cv**2,mu*cv**2,plan['replications'])
                q=np.quantile(x,[.05,.5,.95])
                spread.append(dict(model=model['model'],cv=cv,seed=seed,n=len(x),mean_anchor=mu,assumed_sd=mu*cv,
                    sample_mean=float(x.mean()),mean_mcse=float(x.std(ddof=1)/math.sqrt(len(x))),p05=float(q[0]),p50=float(q[1]),p95=float(q[2]),source_type='simulated'))
                assert abs(x.mean()-mu)<6*x.std(ddof=1)/math.sqrt(len(x))
            # Rival family preserves mean and SD; its different tail is structural uncertainty.
            rng=np.random.default_rng(np.random.SeedSequence([20260906,mi,int(cv*100),2]))
            sigma=math.sqrt(math.log1p(cv*cv))
            x=rng.lognormal(math.log(mu)-sigma*sigma/2,sigma,plan['replications'])
            predictive.append(dict(model=model['model'],cv=cv,family='lognormal',n=len(x),assumed_mean=mu,assumed_sd=mu*cv,p95=float(np.quantile(x,.95)),source_type='simulated'))
    for cv,n,seed in itertools.product(plan['tokenCV'],plan['months'],plan['seeds']):
        rng=np.random.default_rng(np.random.SeedSequence([seed,int(cv*100),n,3]))
        tokens=rng.gamma(n/cv**2,profiles[0]['output_tokens']*cv**2,plan['replications'])
        dollars=n*short['input_usd']+tokens*base['output_price']/1e6
        q=np.quantile(dollars,[.05,.5,.95])
        monthly.append(dict(cv=cv,tasks=n,seed=seed,n_months=len(dollars),expected=n*short['attempt_usd'],sample_mean=float(dollars.mean()),
            mean_mcse=float(dollars.std(ddof=1)/math.sqrt(len(dollars))),p05=float(q[0]),p50=float(q[1]),p95=float(q[2]),source_type='simulated'))
    shared=[]
    for scv,n in itertools.product(plan['sharedCV'],plan['months']):
        rng=np.random.default_rng(np.random.SeedSequence([20260906,int(scv*100),n,4]))
        z=rng.lognormal(-math.log1p(scv*scv)/2,math.sqrt(math.log1p(scv*scv)),plan['replications']) if scv else np.ones(plan['replications'])
        x=n*(short['input_usd']+short['output_usd']*z)
        shared.append(dict(shared_cv=scv,tasks=n,p95=float(np.quantile(x,.95)),mean=float(x.mean()),source_type='simulated'))
    save('token-spread.csv',spread);save('rival-token-family.csv',predictive);save('monthly-spread.csv',monthly);save('shared-shock.csv',shared)
    quality=[]
    for beta,onset,f,flink,qlink,cap in itertools.product(plan['rotBeta'],plan['rotOnset'],plan['fidelity'],plan['fidelityLinks'],plan['qualityLinks'],plan['cap']):
        p=base|design['long']|dict(rot_beta=beta,rot_onset=onset,summary_fidelity=f,fidelity_link=flink,quality_link=qlink,compact_cap=cap)
        o=M.ledger(p)[1]
        quality.append(dict(beta=beta,onset=onset,summary_fidelity=f,fidelity_link=flink,quality_link=qlink,cap=cap,source_type='simulated',**o))
    save('context-quality.csv',quality)
    caching=[]
    for cap,comp,retain in itertools.product(plan['cap'],plan['compactorCache'],plan['postPrefix']):
        o=M.ledger(base|design['long']|dict(compact_cap=cap,compactor_cache=comp,retain_prefix=retain))[1]
        caching.append(dict(cap=cap,compactor_cache=comp,retain_prefix=retain,source_type='simulated',**o))
    save('compaction-cache.csv',caching)
    retries=[]
    for k,rho in itertools.product([1,2,3],plan['retryRho']):
        c,n=M.retry(base['success_probability'],k,rho)
        retries.append(dict(cap=k,rho=rho,completion=c,attempts=n,submitted_usd=short['attempt_usd']*n,
            correct_usd=short['attempt_usd']*n/c,source_type='simulated'))
    save('retry-persistence.csv',retries)
    # AA-native workload cost is kept separate from synthetic 6/40-call ledgers.
    # Recovery is explicitly conditional on Luna failing; do not infer independence from AA.
    routing=[];luna=profiles[0];sol=profiles[3]
    for recover in plan['recovery']:
        spend=luna['cost_usd']+(1-luna['pass1'])*sol['cost_usd']
        q=luna['pass1']+(1-luna['pass1'])*recover
        routing.append(dict(recovery= recover,spend=spend,success=q,cost_per_success=spend/q,
            month_1k=1000*spend,month_1m=1e6*spend,source_type='simulated-aa-proxy',validator='assumed-perfect'))
    save('routing.csv',routing)
    # Independent Bernoulli MC verification of retry expectation, not empirical evidence.
    rng=np.random.default_rng(20260906);x=rng.random((200000,3))<.5
    success=x.any(axis=1);attempts=np.where(success,x.argmax(axis=1)+1,3)
    for actual,expected in [(success.astype(float),.875),(attempts.astype(float),1.75)]:
        se=float(actual.std(ddof=1)/math.sqrt(len(actual)))
        assert abs(actual.mean()-expected)<6*se
        verification.append(dict(expected=expected,simulated_mean=float(actual.mean()),mcse=se,n=len(actual)))
    data=dict(profiles=profiles,core=core,spread=spread,monthly=monthly,shared=shared,routing=routing,retries=retries,
        quality=quality,caching=caching,token_rivals=predictive,verification=verification)
    writejson('extension/results.json',data)
    # Exact SQLite export and extension hash inventory for exploration.
    connection=sqlite3.connect(ROOT/'extension/exploration.sqlite')
    for file in sorted((ROOT/'extension').glob('*.csv')):
        rows=list(csv.DictReader(file.open(encoding='utf8')));table=file.stem.replace('-','_')
        numeric=lambda v: v!='' and _number(v)
        columns=list(rows[0]);types={c:'REAL' if all(numeric(r[c]) for r in rows) else 'TEXT' for c in columns}
        connection.execute(f'CREATE TABLE "{table}" ('+','.join(f'"{c}" {types[c]}' for c in columns)+')')
        connection.executemany(f'INSERT INTO "{table}" VALUES ('+','.join('?' for c in columns)+')',[[r[c] for c in columns] for r in rows])
        assert connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]==len(rows)
    connection.commit();connection.close()
    manifest={f.name:dict(sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size) for f in (ROOT/'extension').iterdir() if f.is_file()}
    writejson('extension/manifest.json',dict(ok=True,files=manifest,spec_sha256=hashlib.sha256((ROOT/'experiment.json').read_bytes()).hexdigest(),
        analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),numpy=np.__version__,scope='Mathematical verification only; not empirical validation.'))
    print(json.dumps(dict(core=len(core),quality_cases=len(quality),token_synthetic_draws=6*3*3*20000,monthly_draws=12*20000,
        short_baseline=short,long_baseline=long,profiles=profiles,routing=routing)))

def _number(x):
    try:return math.isfinite(float(x))
    except ValueError:return False
if __name__=='__main__':
    if '--verify-only' in sys.argv:verify()
    else:analyze()
