#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Freeze a local Harbor study without moving artwork into any skill bundle."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil

REPO=Path(__file__).resolve().parents[3]
OLD=Path('C:/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1')
PRIVATE=Path(os.environ['LOCALAPPDATA'])/'FoxVectorBenchmark/private-v1'
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925'
NAME='svg-brief-design'
def sha(data):return hashlib.sha256(data).hexdigest()
def wsl(path):return '/mnt/c/'+str(path.resolve()).replace('\\','/')[3:]
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def files(root):return {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}

if STUDY.exists():raise SystemExit('Study already exists; preserve it.')
STUDY.mkdir(parents=True)
source=REPO/'skills'/NAME
assert all(p.suffix in ['.md','.yaml'] for p in source.rglob('*') if p.is_file())
for p in source.rglob('*'):
    if p.is_file():
        assert not re.search(r'<(?:svg|path|image)\b|data:image|base64,|vector-\d{3}|p\d{2}-s\d{3}|Fox Rockett',p.read_text(encoding='utf-8'),re.I),p
for candidate in ['baseline','visual-grammar']:
    shutil.copytree(source,STUDY/'candidates'/candidate/NAME)
baseline=STUDY/'candidates/baseline'/NAME/'SKILL.md'
frontmatter=baseline.read_text(encoding='utf-8').split('---',2)[1]
baseline.write_text('---'+frontmatter+'---\n\nFollow the user\'s request and delivery requirements.\n',encoding='utf-8',newline='\n')

original_config=json.loads((OLD/'configs/luna-pilot-v1.1.json').read_text())
development=original_config.copy()
development['job_name']='svg-brief-development'
development['jobs_dir']=wsl(STUDY/'native-jobs')
development['agents']=[{'import_path':'pi_svg_skill:PiSvgSkill','model_name':'openai-codex/gpt-6-luna','kwargs':{'version':'0.84.2'}}]
development['n_attempts']=1
write(STUDY/'jobs/development.json',development)

# Select two tasks per reserved family by predeclared hash, without emitting briefs.
records=json.loads((PRIVATE/'manifest-v1.1.private.json').read_text(encoding='utf-8'))
reserve=[r for r in records if r['split']!='development']
families=sorted(set(r['family'] for r in reserve))
selected=[]
for family in families:
    group=sorted((r for r in reserve if r['family']==family),key=lambda r:sha(('svg-skill-independent-20260925|'+r['id']).encode()))
    selected+=group[:2]
assert len(selected)==4 and len(families)==2
holdout=json.loads(json.dumps(development))
holdout['job_name']='svg-brief-independent-validation'
holdout['n_attempts']=3
holdout.pop('datasets')
holdout['tasks']=[{'path':wsl(Path(r['task_path']))} for r in selected]
write(STUDY/'jobs/holdout.json',holdout)

config={'schemaVersion':1,'search':{'id':'svg-brief-luna','baselineSkill':wsl(STUDY/'candidates/baseline'/NAME),'baselineCandidate':'baseline','outputDir':wsl(STUDY/'search'),'generation':0},'harbor':{'developmentJob':wsl(STUDY/'jobs/development.json'),'holdoutJob':wsl(STUDY/'jobs/holdout.json'),'rewardKey':'visual_similarity','passThreshold':1.0,'requiredRewards':{'artifact_valid':1.0},'requiredEnv':['FOX_PI_AUTH']},'candidates':[{'id':'baseline','skill':wsl(STUDY/'candidates/baseline'/NAME),'parents':[],'rationale':'Fresh control with identical skill plumbing and no additional design guidance.'},{'id':'visual-grammar','skill':wsl(STUDY/'candidates/visual-grammar'/NAME),'parents':['baseline'],'rationale':'Prior development outputs show muddied interior features, inconsistent line hierarchy, and decoration replacing composition. Add transferable planning and negative-space checks, without artwork or reference geometry.'}],'promotion':{'minimumMeanGain':0.015,'allowCaseRegressions':True,'requireNoErrors':True}}
write(STUDY/'generation-000.json',config)
task_dirs=[OLD/'datasets-v1.1/development'/n for n in development['datasets'][0]['task_names']]+[Path(r['task_path']) for r in selected]
protocol={'schema_version':1,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'study_id':'svg-brief-design-20260925','objective':'Improve original SVG design from general briefs without transferring purchased artwork into skills.','model':'openai-codex/gpt-6-luna','thinking':'medium','pi':'0.84.2','loading_policy':'Native Pi explicit --skill and /skill:svg-brief-design command expansion; no ambient skill discovery.','available_tools':['write'],'prior_exposure':'The curator authored the original 32 briefs and inspected source samples before this study. Only the six completed development trials and their visual/metric evidence inform candidate proposals; private outcomes remain unopened until one finalist is frozen. This is an internal transfer test, not independent external curation.','primary_reward':'visual_similarity','weights_frozen':'60% shape and 40% style; verifier 1.1.0 remains unchanged.','primary_threshold_note':'Continuous similarity has no calibrated pass threshold. passThreshold=1 is a reporter convention, not a visual acceptance claim.','qualification':{'artifact_valid':1,'execution_errors':0},'development_cases':6,'development_attempts':1,'private_cases':4,'private_families':2,'private_attempts':3,'remaining_reserved_cases':4,'finalist_rule':'Highest mean visual similarity among qualified development Pareto members with gain >= 0.015 over the fresh baseline; on an exact tie choose the smaller bundle. Keep per-case tradeoffs visible.','budget':{'maximum_design_candidates':3,'maximum_development_trials':24,'maximum_private_trials':24,'maximum_total_native_trials':48,'plateau':'Stop mutation after two consecutive candidate proposals fail to increase the best mean by 0.005, or after three design candidates.','native_retries':0},'private_gate':config['promotion'],'private_gate_policy':'Freeze one candidate digest before the one-way gate. No mutation or reselection from private scores. A failed gate does not authorize a fresh attempt on the same private cohort.','artwork_boundary':'Skill payload is Markdown/YAML guidance and official documentation links only. No SVG, path coordinates, images, encoded vectors, ground truth reconstructions, task IDs, or corpus references.','baseline_bundle_files':files(STUDY/'candidates/baseline'/NAME),'task_files':{wsl(t):files(t) for t in task_dirs},'job_config_sha256':{name:sha((STUDY/f'jobs/{name}.json').read_bytes()) for name in ['development','holdout']},'limitations':['One vendor; family grouping does not establish source independence.','Small descriptive sample and stochastic model; no broad causal or generalization claim.','The scalar similarity proxy may conflict with semantic quality; inspect artifacts and report regressions.']}
write(STUDY/'protocol.json',protocol)
shutil.copy2(OLD/'runtime/images.json',STUDY/'runtime-images.json')
print(json.dumps({'study':str(STUDY),'development_cases':6,'private_cases':4,'max_native_trials':48,'skill_payload_files':list(files(source))},indent=2))
