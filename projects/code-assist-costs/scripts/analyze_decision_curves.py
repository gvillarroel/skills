#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Export verified mathematical curves and exact crossings for the presentation."""
import csv
import hashlib
import itertools
import json
import math
import runpy
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT/'artifacts/decision-curves-v1'
STUDY=ROOT/'study'
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def csvrows(path):
    with path.open(encoding='utf-8-sig',newline='') as stream: return list(csv.DictReader(stream))
spec=load(STUDY/'experiment.json')
mapping=load(ROOT/'curve-map.json')
model=runpy.run_path(str(STUDY/'model.py'))
ledger=model['ledger']
base={p['name']:p['value'] for p in spec['scenarios'][0]['parameters']}
settings={d['designPointId']:{**base,**{p['name']:p['value'] for p in d['parameters']}} for d in spec['designPoints']}
runs={r['run_id']:r for r in csvrows(STUDY/'data/runs.csv')}
values={}
for row in csvrows(STUDY/'data/outcomes.csv'):
    run=runs[row['run_id']]
    values.setdefault((run['scenario_id'],run['design_point_id']),{})[row['outcome_name']]=float(row['value'])
curves={}
for (sid,work),out in values.items():
    family=mapping[sid]['family']
    curves.setdefault(f'{family}:{work}',[]).append({'x':mapping[sid]['x'],**out})
for rows in curves.values(): rows.sort(key=lambda r:r['x'])
checks=[]
def check(name,condition,detail=None):
    checks.append({'check':name,'pass':bool(condition),'detail':detail})
    if not condition: raise AssertionError(name)
def cost(work,**changes): return ledger({**settings[work],**changes})[1]
for work in settings:
    check(f'{work}-baseline-replay', abs(cost(work)['attempt_usd']-values[('baseline',work)]['attempt_usd'])<1e-12)
short=cost('short'); long=cost('long')
check('one-write-five-reads-system-oracle',abs(cost('short',system_tokens=5000)['attempt_usd']-short['attempt_usd']-.00035)<1e-12)
for (sid,work),out in values.items():
    check(f'finite-{sid}-{work}',all(math.isfinite(v) for v in out.values()) and 0<=out['completion']<=1)

def root(fn,lo,hi):
    a,b=fn(lo),fn(hi)
    if a*b>0: return None
    if abs(a)<1e-13:return lo
    if abs(b)<1e-13:return hi
    for _ in range(70):
        mid=(lo+hi)/2; c=fn(mid)
        if hi-lo<1e-11:break
        if a*c<=0:hi=mid
        else:lo=mid;a=c
    result=(lo+hi)/2
    check('root-residual',abs(fn(result))<1e-7,{'x':result,'residual':fn(result)})
    return result

free_quality=cost('long',rot_beta=.2,fidelity_link='critical')
froots={}
for mode in ['critical','average']:
    fn=lambda f:cost('long',compact_cap=180000,rot_beta=.2,fidelity_link=mode,summary_fidelity=f)['correct_usd']-free_quality['correct_usd']
    froots[mode]=root(fn,.9,1)
rotfn=lambda b:cost('long',compact_cap=180000,rot_beta=b,summary_fidelity=.99,fidelity_link='critical')['correct_usd']-cost('long',rot_beta=b,summary_fidelity=.99,fidelity_link='critical')['correct_usd']
rotroot=root(rotfn,0,1)
cachefn=lambda h:cost('long',compact_cap=180000,cache_hit=h)['attempt_usd']-cost('long',cache_hit=h)['attempt_usd']
cacheroot=root(cachefn,0,1)
for family,fn,found,lo,hi in [('fidelity-critical',lambda f:cost('long',compact_cap=180000,rot_beta=.2,fidelity_link='critical',summary_fidelity=f)['correct_usd']-free_quality['correct_usd'],froots['critical'],.9,1),('cache',cachefn,cacheroot,0,1),('rot',rotfn,rotroot,0,1)]:
    ys=[fn(lo+(hi-lo)*i/1000) for i in range(1001)]
    brackets=sum(a*b<0 for a,b in zip(ys,ys[1:]))
    check(f'{family}-crossing-scan',brackets==(0 if found is None else 1),{'sampled_brackets':brackets,'searched_range':[lo,hi]})

caps=curves['cap:long']
mincost=min(r['attempt_usd'] for r in caps)
mins=[r['x'] for r in caps if abs(r['attempt_usd']-mincost)<1e-10]
ranges=[]
for n in mins:
    if ranges and n==ranges[-1][1]+1000:ranges[-1][1]=n
    else:ranges.append([n,n])
fine=[(n,cost('long',compact_cap=n)['attempt_usd']) for n in range(50000,400001,500)]
fine_min=min(y for _,y in fine)
check('cap-500-token-grid-resolution',abs(mincost-fine_min)<1e-12,{'coarse_min':mincost,'fine_min':fine_min})
fine_min_caps=[n for n,c in fine if abs(c-fine_min)<1e-10]
trajectory={}
for cap,label in [(0,'free'),(180000,'compact')]:
    rows,out=ledger({**settings['long'],'compact_cap':cap})
    total=0; step=0; pending=False; points=[{'x':0,'cost':0,'context':31000,'compact':False}]
    for r in rows:
        total+=r['usd']
        if r['kind']=='compact':pending=True;continue
        step+=1
        points.append({'x':step,'cost':total,'context':r['input'],'compact':pending})
        pending=False
    check(f'{label}-trajectory-conservation',abs(total-out['attempt_usd'])<1e-12)
    trajectory[label]=points
first_compaction=next(r['x'] for r in trajectory['compact'] if r['compact'])
first_payback=next(a['x'] for a,b in zip(trajectory['compact'],trajectory['free']) if a['x']>first_compaction and b['cost']-a['cost']>1e-12)
check('trajectory-payback-stays-positive',all(b['cost']-a['cost']>0 for a,b in zip(trajectory['compact'],trajectory['free']) if a['x']>=first_payback))

profiles=csvrows(PROJECT/'source/aa-profiles-20260906.csv')
for r in profiles:
    for k in ['pass1','answer_tokens','reasoning_tokens','output_tokens','cost_usd']:
        r[k]=float(r[k])
luna=profiles[0]; sol=profiles[3]
lossroot=(sol['cost_usd']-luna['cost_usd'])/(sol['pass1']-luna['pass1'])
loss={}
for label,m in [('Luna max',luna),('Sol xhigh',sol)]:
    loss[label]=[{'x':i/10,'y':m['cost_usd']+(1-m['pass1'])*i/10} for i in range(101)]
check('loss-crossing',abs(luna['cost_usd']+(1-luna['pass1'])*lossroot-sol['cost_usd']-(1-sol['pass1'])*lossroot)<1e-12)
p=luna['pass1']; retry={}
for k in [1,2,3]:
    retry[str(k)]=[]
    for i in range(101):
        rho=i/100;q,attempts=model['retry'](p,k,rho)
        retry[str(k)].append({'x':rho,'y':q,'spend':short['attempt_usd']*attempts,'correct_usd':short['attempt_usd']*attempts/q})
for pv,k,rho in itertools.product([0,.5,p,1],[1,2,3],[0,.5,1]):
    q=attempts=0
    for seq in itertools.product([0,1],repeat=k):
        weight=(1-rho)*math.prod(pv if x else 1-pv for x in seq)
        weight+=rho*(pv if all(seq) else 1-pv if not any(seq) else 0)
        q+=weight*any(seq)
        attempts+=weight*(seq.index(1)+1 if any(seq) else k)
    expect=model['retry'](pv,k,rho)
    check('retry-sequence-oracle',max(abs(q-expect[0]),abs(attempts-expect[1]))<1e-12)
ind=1-(1-p)**3
retryroot=(ind-.95)/(ind-p)
routingcost=luna['cost_usd']+(1-p)*sol['cost_usd']
routingroot=(.95-p)/(1-p)
routing=[{'x':i/100,'y':p+(1-p)*i/100,'spend':routingcost} for i in range(101)]
check('routing-95-percent-crossing',abs(p+(1-p)*routingroot-.95)<1e-12)
spread={}
for cv in [0,.3]:
    spread[str(cv)]=[]
    for i in range(121):
        n=1000*10**(3*i/120)
        sd=short['output_usd']*math.sqrt(1/n+cv**2+cv**2/n)/short['attempt_usd']
        spread[str(cv)].append({'x':n,'y':sd})
check('shared-shock-floor',spread['0.3'][-1]['y']>0.23)

inventory=csvrows(STUDY/'design/variable-inventory.csv')
package={'source_type':'simulated-except-explicit-AA-profiles','snapshot':'2026-09-06',
    'curves':curves,'baselines':{'short':short,'long':long},'settings':settings,
    'trajectory':trajectory,'trajectory_payback':{'first_compaction_call':first_compaction,'first_payback_call':first_payback},'profiles':profiles,'loss':loss,'retry':retry,'routing':routing,'spread':spread,
    'breakpoints':{'fidelity':froots,'rot':rotroot,'cache':cacheroot,'loss':lossroot,'retry':retryroot,'routing':routingroot,
        'cap_minimum':{'usd':mincost,'ranges':ranges,'grid_step':1000,'fine_grid_step':500,'fine_min_caps':fine_min_caps}},
    'inventory':inventory,
    'sources':[{'title':'Artificial Analysis Terminal-Bench v2.1','url':luna['source_url']},
        {'title':'GitHub Copilot model pricing','url':'https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing'},
        {'title':'Artificial Analysis Intelligence methodology','url':'https://artificialanalysis.ai/methodology/intelligence-benchmarking'}]}
(ROOT/'presentation-data.json').write_text(json.dumps(package,separators=(',',':')),encoding='utf-8')
out=ROOT/'data';out.mkdir(exist_ok=True)
with (out/'curves.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=['curve','x','attempt_usd','correct_usd','completion','compactions','source_type'])
    writer.writeheader()
    for key,rows in curves.items():
        for r in rows:writer.writerow({'curve':key,'x':r['x'],**{k:r[k] for k in ['attempt_usd','correct_usd','completion','compactions']},'source_type':'simulated'})
with (out/'analytic-curves.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=['family','series','x','y','x_unit','y_unit','source_type']);writer.writeheader()
    for family,series,xu,yu in [('failure-loss',loss,'USD/failure','USD/task'),('retries',retry,'1','probability'),('monthly-spread',spread,'task/month','relative-SD')]:
        for name,rows in series.items():
            for r in rows:writer.writerow({'family':family,'series':name,'x':r['x'],'y':r['y'],'x_unit':xu,'y_unit':yu,'source_type':'simulated'})
    for r in routing:writer.writerow({'family':'routing','series':'Luna-Sol','x':r['x'],'y':r['y'],'x_unit':'conditional-probability','y_unit':'probability','source_type':'simulated'})
(ROOT/'extension-audit.json').write_text(json.dumps({'ok':all(c['pass'] for c in checks),'checks':checks,'breakpoints':package['breakpoints'],
    'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'presentation-data.json',out/'curves.csv',out/'analytic-curves.csv']},
    'confidence_scope':'Exact arithmetic checks, not empirical validation. No Monte Carlo intervals for deterministic curves.'},indent=2),encoding='utf-8')
print(json.dumps({'checks':len(checks),'passed':all(c['pass'] for c in checks),'breakpoints':package['breakpoints']},indent=2))
