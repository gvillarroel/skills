#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Run the final declared design candidate; never retry the unavailable sibling."""
from pathlib import Path
import asyncio,importlib.util,json,os
REPO=Path(__file__).resolve().parents[3]
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925-r2'
os.environ['FOX_PI_AUTH']='/mnt/c/Users/villa/.pi/agent/auth.json'
spec=importlib.util.spec_from_file_location('pareto','/mnt/c/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
if (STUDY/'search/holdout').exists():raise ValueError('Private gate already opened')
source=STUDY/'candidates/graphic-economy/svg-brief-design'
gen=STUDY/'search/development/generation-001'
staged,digest=module.stage_skill_for_evaluation(source,gen/'candidate-staging/graphic-economy','svg-brief-design')
config=json.loads((STUDY/'generation-001.json').read_text())
unavailable=[c for c in config['candidates'] if c['id']=='semantic-structure'][0]
config['candidates']=[c for c in config['candidates'] if c['id']!='semantic-structure']
job_name='svg-brief-luna-r2-g001-development-graphic-economy'
job_dir=gen/'harbor-jobs'/job_name
proposal=json.loads((STUDY/'graphic-economy-proposal.json').read_text())
config['candidates'].append({'id':'graphic-economy','skill':str(staged),'jobDirectory':str(job_dir),'parents':proposal['parents'],'rationale':proposal['mutation']})
path=STUDY/'generation-001-evaluable.json'
if path.exists():raise ValueError('Sibling configuration already exists')
path.write_text(json.dumps(config,indent=2))
module.normalize_config(path)
(gen/'unavailable-candidate.json').write_text(json.dumps({'candidate':unavailable,'fitness':None,'reason':'Five terminal Pi events report exact WebSocket closed 1011; no complete six-case evaluable vector. Original artifacts and the one valid case are preserved. No failed outcome is converted to zero fitness, and no trial is retried.','recovery_contract':'The stock recovery allowlist does not recognize message-only WebSocket 1011 evidence; it is not bypassed.','new_candidate_not_retry':'graphic-economy is a separately frozen prose organization hypothesis based only on complete generation-000 evidence.'},indent=2))
(gen/'graphic-economy-receipt.json').write_text(json.dumps({'source':str(source),'staged':str(staged),'digest':digest,'new_trials':6,'design_candidate_budget_used':3},indent=2))
asyncio.run(module.execute_job(STUDY/'jobs/development.json',staged,gen/'harbor-jobs',job_name))
print(json.dumps({'completed':True,'job':str(job_dir),'analysis_config':str(path)}))
