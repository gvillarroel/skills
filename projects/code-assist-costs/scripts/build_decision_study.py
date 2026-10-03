#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze a fresh exploratory curve study, without executing the modeled targets."""
import copy
import hashlib
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / 'artifacts/decision-curves-v1'
PARENT = PROJECT / 'artifacts/aa-ofat/study-v1'
study = ROOT / 'study'
if study.exists():
    raise SystemExit('Refusing to overwrite an existing study.')
spec = json.loads((PARENT / 'experiment.json').read_text(encoding='utf-8'))
spec['experimentId'] = 'decision-curves-20260906-v1'
spec['title'] = 'Exploratory cost and quality decision curves'
spec['description'] = 'Offline mathematical parameter sweeps. AA proxies do not validate production tasks.'
spec['phase'] = 'exploratory'
base = copy.deepcopy(spec['scenarios'][0])
families = {}
scenarios = []
def add(sid, family, x, changes):
    s = copy.deepcopy(base)
    s.update(scenarioId=sid, label=sid, description=f'{family}: one selected parameter within its fixed policy family')
    for p in s['parameters']:
        if p['name'] in changes:
            p['value'] = changes[p['name']]
    scenarios.append(s)
    families[sid] = dict(family=family, x=x, changes=changes)

add('baseline', 'baseline', 0, {})
for i in range(41):
    add(f'system-{i:03}', 'system', i*250, {'system_tokens':4000+i*250})
for i in range(11):
    add(f'tools-{i:03}', 'tools', i, {'tool_delta':i-5})
for i in range(51):
    add(f'output-{i:03}', 'output', .5+i*.02, {'output_factor':.5+i*.02})
for cap, suffix in [(0,'free'), (180000,'compact')]:
    for i in range(101):
        add(f'cache-{suffix}-{i:03}', f'cache-{suffix}', i/100, {'compact_cap':cap,'cache_hit':i/100})
for i in range(351):
    add(f'cap-{i:03}', 'cap', 50000+1000*i, {'compact_cap':50000+1000*i})
for mode in ['critical','average']:
    for i in range(101):
        f = .9+i*.001
        add(f'fidelity-{mode}-{i:03}', f'fidelity-{mode}', f,
            {'compact_cap':180000,'rot_beta':.2,'fidelity_link':mode,'summary_fidelity':f})
add('quality-free', 'quality-free', 1, {'rot_beta':.2,'fidelity_link':'critical'})
for cap, suffix in [(0,'free'), (180000,'compact')]:
    for i in range(101):
        add(f'rot-{suffix}-{i:03}', f'rot-{suffix}', i/100,
            {'compact_cap':cap,'rot_beta':i/100,'summary_fidelity':.99,'fidelity_link':'critical'})
spec['scenarios'] = scenarios
h = copy.deepcopy(spec['hypotheses'][0])
h.update(hypothesisId='h-system-plus1k', scenarioIds=['baseline','system-004'])
h['analysis']['comparisonScenarioId']='system-004'
spec['hypotheses']=[h]
review = spec['extensions']['simulation-data-lab']['variableReview']
review['scope'] = 'Exploratory decision curves using the parent ledger. Production optimality remains unidentifiable without task-specific quality, dependency and billing evidence.'
for v in review['variables']:
    names = v['parameterNames']
    values = {n: {str(next(p['value'] for p in s['parameters'] if p['name']==n)) for s in scenarios} for n in names if any(p['name']==n for p in base['parameters'])}
    if values:
        v['treatment']='modeled' if any(len(a)>1 for a in values.values()) else 'fixed'
review['openQuestions'].append('How much would imperfect validation or conditional fallback cost shift the displayed routing threshold?')
study.mkdir(parents=True)
(study/'experiment.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
(study/'model.py').write_bytes((PROJECT/'source/aa-ofat-model.py').read_bytes())
(ROOT/'curve-map.json').write_text(json.dumps(families,indent=2),encoding='utf-8')
manifest = {'phase':'exploratory','replications':1,'scenarios':len(scenarios),'planned_runs':len(scenarios)*2,
    'parent_spec_sha256':hashlib.sha256((PARENT/'experiment.json').read_bytes()).hexdigest(),
    'model_sha256':hashlib.sha256((study/'model.py').read_bytes()).hexdigest(),
    'method_sha256':hashlib.sha256((PROJECT/'source/decision-curves-method.md').read_bytes()).hexdigest(),
    'extension_plan':'source/decision-curves-method.md','target_executions':0}
(ROOT/'study-plan.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
