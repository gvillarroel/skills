#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build and browser-audit both calibrated native mechanisms in both palettes."""
import json,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-composition/artifacts/hf-native';OUT.mkdir(parents=True,exist_ok=True)
commands=[];cases=[]
def run(cmd,report=None):
 if cmd[0]=='npm':cmd[0]=shutil.which('npm.cmd') or shutil.which('npm')
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');commands.append({'command':cmd,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(OUT/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8');assert r.returncode==0,(cmd,r.stderr)
 if report:assert json.loads(report.read_text(encoding='utf-8'))['ok'],report
for mode in ['colorset1','colorset2']:
 for kind in ['inlet','vehicle']:
  d=OUT/(mode+'-'+kind);d.mkdir(exist_ok=True)
  source,quantity,unit,qunit=('rate','volume','L/s','L') if kind=='inlet' else ('speed','distance','m/s','m')
  command=['uv','run','--script','skills/hyperframes-explainer/scripts/explainer.py','init','--brief',str(d/'model.json'),'--report',str(d/'init.json'),'--width','960','--height','540','--fps','12','--duration','8','--initial','2','--maximum','5','--target','5','--at','2','--ramp','2','--source',source,'--source-unit',unit,'--quantity',quantity,'--quantity-unit',qunit,'--palette',mode]
  if (d/'project/index.html').is_file():cases.append(d);continue
  run(command,d/'init.json')
  run(['uv','run','--script','skills/hyperframes-explainer/scripts/compose_mechanism.py','--brief',str(d/'model.json'),'--output',str(d/'scene.json'),'--svg',str(d/'mechanism.svg'),'--plan',str(d/'asset-plan.json'),'--kind',kind,'--report',str(d/'composition.json')],d/'composition.json')
  run(['uv','run','--script','skills/hyperframes-explainer/scripts/import_assets.py','--brief',str(d/'scene.json'),'--plan',str(d/'asset-plan.json'),'--output',str(d/'assembled.json'),'--report',str(d/'import.json')],d/'import.json')
  run(['uv','run','--script','skills/hyperframes-explainer/scripts/explainer.py','build','--brief',str(d/'assembled.json'),'--project',str(d/'project'),'--report',str(d/'build.json')],d/'build.json');cases.append(d)
shutil.copy2(cases[0]/'project/package.json',OUT/'package.json');run(['npm','install','--prefix',str(OUT),'--cache',str(OUT/'.cache/npm'),'--no-audit','--no-fund'])
for d in cases:
 run(['node',str(d/'project/scripts/audit.ts'),'--report',str(d/'audit.json'),'--screenshot',str(d/'preview.png')],d/'audit.json')
 r=json.loads((d/'audit.json').read_text());assert any(s['headCount'] for s in r['arrowStates']),d
(OUT/'summary.json').write_text(json.dumps({'passed':True,'cases':[{'id':d.name,'states':len(json.loads((d/'audit.json').read_text())['arrowStates'])} for d in cases]},indent=2)+'\n',encoding='utf-8');print((OUT/'summary.json').read_text())
