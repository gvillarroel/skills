#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Preserve the rejected preflight and freeze a corrected agent-loading profile."""
from pathlib import Path
import datetime,hashlib,json,shutil
REPO=Path(__file__).resolve().parents[3]
OLD=REPO/'evaluations/runs/svg-brief-design-20260925'
NEW=REPO/'evaluations/runs/svg-brief-design-20260925-r2'
def wsl(p):return '/mnt/c/'+str(p.resolve()).replace('\\','/')[3:]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
if NEW.exists():raise SystemExit('Successor already exists')
NEW.mkdir(parents=True)
shutil.copytree(OLD/'candidates',NEW/'candidates')
shutil.copy2(OLD/'runtime-images.json',NEW/'runtime-images.json')
for name in ['development','holdout']:
    data=json.loads((OLD/f'jobs/{name}.json').read_text())
    data['agents'][0].update(name='pi-svg-skill',import_path='pi_svg_skill_v2:PiSvgSkill')
    data['jobs_dir']=wsl(NEW/'native-jobs')
    write(NEW/f'jobs/{name}.json',data)
config=json.loads((OLD/'generation-000.json').read_text())
config=json.loads(json.dumps(config).replace(wsl(OLD),wsl(NEW)))
config['search']['id']='svg-brief-luna-r2'
write(NEW/'generation-000.json',config)
protocol=json.loads((OLD/'protocol.json').read_text())
protocol.update(study_id=NEW.name,created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),supersedes=OLD.name,supersession_reason='The first native control lacks a declared agent name needed by the strict analyzer; it also contains one agent-caused skill-integrity violation. Retain all six outputs. Correct the common loading contract and explicit agent identity, then start a fresh matched comparison. No private gate or treatment trial was executed.',loading_policy='Native Pi explicit skill command expansion plus an identical explicit read-only skill constraint for every control and treatment.',prior_model_trials=6)
protocol['job_config_sha256']={name:sha(NEW/f'jobs/{name}.json') for name in ['development','holdout']}
protocol['adapter_files']={p.name:sha(p) for p in [REPO/'projects/svg-brief-design/scripts/pi_svg_skill.py',REPO/'projects/svg-brief-design/scripts/pi_svg_skill_v2.py']}
write(NEW/'protocol.json',protocol)
receipt={'status':'ended-before-treatment','native_control_trials':6,'agent_integrity_failures':1,'strict_analysis_failure':'Configured import_path had no explicit name matching the observed agent identity.','private_gate_opened':False,'successor':NEW.name,'retained_all_evidence':True,'semantic_retry':False,'note':'A new common loading profile applies equally to both arms; this does not replace or erase the first control.'}
write(OLD/'preflight-closeout.json',receipt)
print(json.dumps({'successor':str(NEW),'prior_trials_retained':6,'private_gate_untouched':True}))
