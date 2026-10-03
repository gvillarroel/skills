#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["scipy>=1.15,<2"]
# ///
"""Independent distribution-oracle and checksum audit of the simulation extension."""
import csv
import hashlib
import json
import math
from pathlib import Path
from scipy.stats import gamma, lognorm
import scipy

root=Path('projects/code-assist-costs/artifacts/aa-ofat/study-v1')
ext=root/'extension'
def rows(name):return list(csv.DictReader((ext/name).open(encoding='utf8')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ext/'manifest.json').read_text())
for filename,record in manifest['files'].items():assert sha(ext/filename)==record['sha256'],filename
assert sha(root/'experiment.json')==manifest['spec_sha256']
assert sha(Path('projects/code-assist-costs/scripts/analyze_aa_ofat.py'))==manifest['analysis_sha256']
data=json.loads((ext/'results.json').read_text())
baseline=next(r for r in data['core'] if r['scenario']=='baseline' and r['workload']=='short')
mu=data['profiles'][0]['output_tokens']
checks=[]
# Supplemental diagnostic, selected after generation: not a preregistered policy test.
# DKW + union bound across 66 distribution cells; finite-run quantile check only.
families=36+12+18
alpha=.01
for r in rows('token-spread.csv'):
    mean=float(r['mean_anchor']);cv=float(r['cv']);n=int(r['n'])
    dist=gamma(a=1/cv**2,scale=mean*cv**2)
    eps=math.sqrt(math.log(2*families/alpha)/(2*n))+1/n
    for q,k in [(.05,'p05'),(.5,'p50'),(.95,'p95')]:
        error=abs(float(dist.cdf(float(r[k])))-q)
        assert error<eps,(r['model'],cv,k,error,eps)
        checks.append(dict(table='token-spread',model=r['model'],cv=cv,quantile=q,cdf_error=error,tolerance=eps))
for r in rows('rival-token-family.csv'):
    mean=float(r['assumed_mean']);cv=float(r['cv']);n=int(r['n']);s=math.sqrt(math.log1p(cv*cv))
    error=abs(lognorm(s=s,scale=mean/math.sqrt(1+cv*cv)).cdf(float(r['p95']))-.95)
    eps=math.sqrt(math.log(2*families/alpha)/(2*n))+1/n
    assert error<eps
    checks.append(dict(table='rival-token-family',model=r['model'],cv=cv,quantile=.95,cdf_error=float(error),tolerance=eps))
for r in rows('monthly-spread.csv'):
    cv=float(r['cv']);tasks=int(r['tasks']);n=int(r['n_months'])
    assert abs(float(r['expected'])-tasks*baseline['attempt_usd'])<1e-8
    dist=gamma(a=tasks/cv**2,scale=mu*cv**2)
    eps=math.sqrt(math.log(2*families/alpha)/(2*n))+1/n
    for q,k in [(.05,'p05'),(.5,'p50'),(.95,'p95')]:
        tokens=(float(r[k])-tasks*baseline['input_usd'])/(1.2/1e6)
        error=abs(float(dist.cdf(tokens))-q)
        assert error<eps
        checks.append(dict(table='monthly-spread',model='Luna',cv=cv,quantile=q,cdf_error=error,tolerance=eps))
for r in rows('routing.csv'):
    q0=data['profiles'][0]['pass1'];recovery=float(r['recovery'])
    expected=q0+(1-q0)*recovery
    assert abs(float(r['success'])-expected)<1e-12
report=dict(ok=True,integrity=True,distribution_oracle='scipy '+scipy.__version__,checks=len(checks),
    maximum_cdf_error=max(x['cdf_error'] for x in checks),quantile_checks=checks,
    scope='Post-run computational diagnostic. DKW tolerance controls simulation CDF noise conditional on the assumed distributions; not confidence in AA transfer or production.',
    target_executions=0,files={p.name:sha(p) for p in ext.iterdir() if p.is_file() and p.name!='independent-audit.json'})
(ext/'independent-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['quantile_checks','files']}))
