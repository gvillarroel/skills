#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Invoke the installed native Harbor Pareto workflow with frozen local images."""
from pathlib import Path
import json,os,subprocess,sys
REPO=Path(__file__).resolve().parents[3]
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925-r2'
env=os.environ.copy();env['PYTHONPATH']=str(Path(__file__).resolve().parent)+os.pathsep+env.get('PYTHONPATH','')
env['FOX_PI_AUTH']='/mnt/c/Users/villa/.pi/agent/auth.json'
for item in json.loads((STUDY/'runtime-images.json').read_text()).values():
    assert json.loads(subprocess.check_output(['docker','image','inspect',item['tag']]))[0]['Id']==item['image_id']
script='/mnt/c/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py'
config=sys.argv[1] if len(sys.argv)>1 else 'generation-000'
result=subprocess.run([sys.executable,script,str(STUDY/(config+'.json')),*sys.argv[2:]],env=env,check=False,capture_output=True,text=True)
suffix='-'.join(a.lstrip('-') for a in sys.argv[2:]) or 'development'
log=STUDY/f'{config}-{suffix}.json';log.write_text(result.stdout,encoding='utf-8')
if result.stderr:(STUDY/f'{config}-{suffix}.stderr.txt').write_text(result.stderr,encoding='utf-8')
if result.returncode:
    print(result.stderr[-5000:])
    raise SystemExit(result.returncode)
print(json.dumps({'completed':True,'output':str(log),'stderr_bytes':len(result.stderr)}))
