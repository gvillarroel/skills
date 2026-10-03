#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Run only a new native candidate; retain previous jobs for Pareto analysis."""
from pathlib import Path
import asyncio,importlib.util,json,os,sys
REPO=Path(__file__).resolve().parents[3]
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925-r2'
generation=int(sys.argv[1]);candidate_id=sys.argv[2]
if generation<1 or generation>2:raise ValueError('Declared development generation budget exceeded')
if (STUDY/'search/holdout').exists():raise ValueError('Private gate opened; no further development')
os.environ['FOX_PI_AUTH']='/mnt/c/Users/villa/.pi/agent/auth.json'
spec=importlib.util.spec_from_file_location('pareto','/mnt/c/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
previous=STUDY/f'search/development/generation-{generation-1:03d}/pareto-archive.json'
archive=json.loads(previous.read_text());module.validate_archive_seal(archive,'previous')
gen_dir=STUDY/f'search/development/generation-{generation:03d}'
source=STUDY/'candidates'/candidate_id/'svg-brief-design'
staged,digest=module.stage_skill_for_evaluation(source,gen_dir/'candidate-staging'/candidate_id,'svg-brief-design')
config=json.loads((STUDY/'generation-000.json').read_text())
config['search'].update(generation=generation,previousGenerationLog=str(previous))
config['candidates']=[]
for record in archive['candidateResults']:
    config['candidates'].append({'id':record['candidateId'],'skill':record['evaluatedSkill'],'jobDirectory':record['jobDirectory'],'parents':record['parents'],'rationale':record['rationale']})
baseline=next(c for c in config['candidates'] if c['id']=='baseline')
config['search']['baselineSkill']=baseline['skill']
proposal=json.loads((STUDY/(candidate_id+'-proposal.json')).read_text())
job_name=f"svg-brief-luna-r2-g{generation:03d}-development-{candidate_id}"
job_dir=gen_dir/'harbor-jobs'/job_name
config['candidates'].append({'id':candidate_id,'skill':str(staged),'jobDirectory':str(job_dir),'parents':proposal['parents'],'rationale':proposal['mutation']})
config_path=STUDY/f'generation-{generation:03d}.json'
if config_path.exists():raise ValueError('Generation configuration already exists')
config_path.write_text(json.dumps(config,indent=2))
module.normalize_config(config_path)
(gen_dir/'new-candidate-receipt.json').write_text(json.dumps({'candidate':candidate_id,'source':str(source),'staged':str(staged),'digest':digest,'reused_prior_jobs':len(archive['candidateResults']),'new_trials':6},indent=2))
asyncio.run(module.execute_job(STUDY/'jobs/development.json',staged,gen_dir/'harbor-jobs',job_name))
print(json.dumps({'completed':True,'job':str(job_dir),'next_action':'Analyze the new generation with --analyze-only; do not rerun prior candidates.'}))
